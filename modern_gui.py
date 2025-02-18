import customtkinter as ctk
from core import CatFeederCore
import atexit
from datetime import datetime
import json

class ModernCatFeederApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("AutomatiCats")
        self.app.geometry("1100x800")
        
        # Set the theme and color scheme
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # Initialize core functionality
        self.core = CatFeederCore()
        atexit.register(self.cleanup)
        
        # Create main container with padding
        self.main_container = ctk.CTkFrame(self.app)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create left and right panels
        self.left_panel = ctk.CTkFrame(self.main_container, width=300)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        
        self.right_panel = ctk.CTkFrame(self.main_container)
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        self.setup_left_panel()
        self.setup_right_panel()
        
        # Load existing cats
        self.load_cats()
        
        # Start automatic updates
        self.update_stats()
        self.update_monitoring()

    def setup_left_panel(self):
        # Cat Management Section
        cat_section = ctk.CTkFrame(self.left_panel)
        cat_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(cat_section, text="Add New Cat", font=("SF Pro", 16, "bold")).pack(pady=5)
        
        self.cat_name_var = ctk.StringVar()
        name_entry = ctk.CTkEntry(cat_section, placeholder_text="Cat Name", textvariable=self.cat_name_var)
        name_entry.pack(fill="x", padx=10, pady=5)
        
        add_button = ctk.CTkButton(cat_section, text="Add Cat", command=self.add_cat)
        add_button.pack(fill="x", padx=10, pady=5)
        
        # Cat Selection Section
        select_section = ctk.CTkFrame(self.left_panel)
        select_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(select_section, text="Select Cat", font=("SF Pro", 16, "bold")).pack(pady=5)
        
        self.selected_cat = ctk.StringVar()
        self.cat_menu = ctk.CTkOptionMenu(select_section, variable=self.selected_cat)
        self.cat_menu.pack(fill="x", padx=10, pady=5)
        
        # Quick Actions Section
        actions_section = ctk.CTkFrame(self.left_panel)
        actions_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(actions_section, text="Quick Actions", font=("SF Pro", 16, "bold")).pack(pady=5)
        
        feed_button = ctk.CTkButton(actions_section, text="Dispense Food (50g)", command=self.trigger_feeding)
        feed_button.pack(fill="x", padx=10, pady=5)
        
        identify_button = ctk.CTkButton(actions_section, text="Identify Cat", command=self.identify_cat)
        identify_button.pack(fill="x", padx=10, pady=5)

    def setup_right_panel(self):
        # Create tabs
        self.tabview = ctk.CTkTabview(self.right_panel)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tabview.add("Feeding Log")
        self.tabview.add("Statistics")
        self.tabview.add("Monitoring")
        
        # Setup Feeding Log tab
        self.setup_feeding_log_tab()
        
        # Setup Statistics tab
        self.setup_statistics_tab()
        
        # Setup Monitoring tab
        self.setup_monitoring_tab()

    def setup_feeding_log_tab(self):
        tab = self.tabview.tab("Feeding Log")
        
        # Create input frame
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # Amount input
        amount_frame = ctk.CTkFrame(input_frame)
        amount_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(amount_frame, text="Amount (g):").pack(side="left", padx=5)
        self.amount_var = ctk.StringVar()
        amount_entry = ctk.CTkEntry(amount_frame, textvariable=self.amount_var, width=100)
        amount_entry.pack(side="left", padx=5)
        
        # Food type input
        type_frame = ctk.CTkFrame(input_frame)
        type_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(type_frame, text="Food Type:").pack(side="left", padx=5)
        self.food_type_var = ctk.StringVar(value="Dry Food")
        type_entry = ctk.CTkEntry(type_frame, textvariable=self.food_type_var, width=200)
        type_entry.pack(side="left", padx=5)
        
        # Log button
        log_button = ctk.CTkButton(input_frame, text="Log Feeding", command=self.log_feeding)
        log_button.pack(pady=10)
        
        # Create textbox for feeding history
        self.feeding_history = ctk.CTkTextbox(tab, height=400)
        self.feeding_history.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_statistics_tab(self):
        tab = self.tabview.tab("Statistics")
        
        # Create stats display
        self.stats_text = ctk.CTkTextbox(tab)
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_monitoring_tab(self):
        tab = self.tabview.tab("Monitoring")
        
        # Status Frame
        status_frame = ctk.CTkFrame(tab)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        # Food Weight
        weight_frame = ctk.CTkFrame(status_frame)
        weight_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(weight_frame, text="Current Food Weight:").pack(side="left", padx=5)
        self.weight_label = ctk.CTkLabel(weight_frame, text="N/A")
        self.weight_label.pack(side="left", padx=5)
        
        # Water Level
        water_frame = ctk.CTkFrame(status_frame)
        water_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(water_frame, text="Water Level:").pack(side="left", padx=5)
        self.water_label = ctk.CTkLabel(water_frame, text="N/A")
        self.water_label.pack(side="left", padx=5)
        
        # Simulation Mode Label
        if not self.core.has_hardware:
            ctk.CTkLabel(
                status_frame,
                text="Running in simulation mode",
                text_color="orange"
            ).pack(pady=10)

    def add_cat(self):
        name = self.cat_name_var.get().strip()
        if not name:
            self.show_error("Please enter a cat name")
            return
        
        result = self.core.add_cat(name)
        if result['success']:
            self.cat_name_var.set("")
            self.load_cats()
            self.show_info("Success", result['message'])
        else:
            self.show_error(result['message'])

    def load_cats(self):
        cats = self.core.get_cats()
        cat_names = [cat['name'] for cat in cats]
        if cat_names:
            self.cat_menu.configure(values=cat_names)
            self.cat_menu.set(cat_names[0])
        else:
            self.cat_menu.configure(values=["No cats added"])
            self.cat_menu.set("No cats added")

    def log_feeding(self):
        cat_name = self.selected_cat.get()
        if cat_name == "No cats added":
            self.show_error("Please add a cat first")
            return
            
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            self.show_error("Please enter a valid amount")
            return
        
        cats = self.core.get_cats()
        cat_id = next((cat['id'] for cat in cats if cat['name'] == cat_name), None)
        if cat_id is None:
            self.show_error("Selected cat not found")
            return
        
        result = self.core.log_feeding(
            cat_id,
            amount,
            self.food_type_var.get()
        )
        
        if result['success']:
            self.amount_var.set("")
            self.update_stats()
            self.show_info("Success", result['message'])
        else:
            self.show_error(result['message'])

    def update_stats(self):
        stats = self.core.get_feeding_stats()
        
        self.stats_text.delete("0.0", "end")
        self.stats_text.insert("0.0", "Feeding Statistics:\n\n")
        
        for stat in stats:
            self.stats_text.insert("end",
                f"🐱 {stat['name']}\n"
                f"   • Total Feedings: {stat['feeding_count']}\n"
                f"   • Total Amount: {stat['total_amount']:.1f}g\n"
                f"   • Last Feeding: {stat['last_feeding']}\n\n")
        
        self.app.after(5000, self.update_stats)

    def update_monitoring(self):
        status = self.core.get_hardware_status()
        self.weight_label.configure(text=f"{status['food_weight']:.1f}g")
        self.water_label.configure(text=f"{status['water_level']:.1f}%")
        self.app.after(1000, self.update_monitoring)

    def trigger_feeding(self):
        result = self.core.trigger_feeding(50.0)  # 50g default portion
        if result['success']:
            self.show_info("Success", "Feeding triggered successfully")
        else:
            self.show_error(result['message'])

    def identify_cat(self):
        result = self.core.identify_cat()
        if result['success']:
            self.show_info(
                "Cat Identified",
                f"Detected cat: {result['cat_name']}\n"
                f"Confidence: {result['confidence']:.1%}"
            )
        else:
            self.show_error(result['message'])

    def show_error(self, message):
        dialog = ctk.CTkInputDialog(
            text=message,
            title="Error",
            button_text="OK"
        )
        dialog.get_input()

    def show_info(self, title, message):
        dialog = ctk.CTkInputDialog(
            text=message,
            title=title,
            button_text="OK"
        )
        dialog.get_input()

    def cleanup(self):
        """Clean up resources when the application closes."""
        self.core.cleanup()

    def run(self):
        self.app.mainloop()

def main():
    app = ModernCatFeederApp()
    app.run()

if __name__ == "__main__":
    main()