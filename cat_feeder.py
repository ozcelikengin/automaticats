import tkinter as tk
from tkinter import ttk, messagebox
from core import CatFeederCore
import atexit

class AutomaticMonitoringFrame(ttk.LabelFrame):
    def __init__(self, parent, core):
        super().__init__(parent, text="Automatic Monitoring", padding="5")
        self.core = core
        
        # Status labels
        ttk.Label(self, text="Current Food Weight:").grid(row=0, column=0, padx=5)
        self.weight_label = ttk.Label(self, text="N/A")
        self.weight_label.grid(row=0, column=1, padx=5)
        
        ttk.Label(self, text="Water Level:").grid(row=1, column=0, padx=5)
        self.water_label = ttk.Label(self, text="N/A")
        self.water_label.grid(row=1, column=1, padx=5)
        
        # Control buttons
        self.feed_button = ttk.Button(
            self, text="Dispense Food (50g)",
            command=self.trigger_feeding
        )
        self.feed_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Cat identification
        self.identify_button = ttk.Button(
            self, text="Identify Cat",
            command=self.identify_cat
        )
        self.identify_button.grid(row=3, column=0, columnspan=2, pady=5)
        
        if not core.has_hardware:
            ttk.Label(
                self, text="Running in simulation mode",
                foreground="orange"
            ).grid(row=4, column=0, columnspan=2)
            
            # Disable hardware buttons
            self.feed_button['state'] = 'disabled'
            self.identify_button['state'] = 'disabled'
        
        self.update_status()
    
    def trigger_feeding(self):
        result = self.core.trigger_feeding(50.0)  # 50g default portion
        if result['success']:
            messagebox.showinfo("Success", "Feeding triggered successfully")
        else:
            messagebox.showerror("Error", result['message'])
    
    def identify_cat(self):
        result = self.core.identify_cat()
        if result['success']:
            messagebox.showinfo(
                "Cat Identified",
                f"Detected cat: {result['cat_name']}\n"
                f"Confidence: {result['confidence']:.1%}"
            )
        else:
            messagebox.showerror("Error", result['message'])
    
    def update_status(self):
        status = self.core.get_hardware_status()
        self.weight_label.config(
            text=f"{status['food_weight']:.1f}g"
        )
        self.water_label.config(
            text=f"{status['water_level']:.1f}%"
        )
        self.after(1000, self.update_status)

class CatFeederApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutomatiCats Feeder")
        
        # Initialize core functionality
        self.core = CatFeederCore()
        atexit.register(self.cleanup)
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cat management section
        self.create_cat_management()
        
        # Feeding log section
        self.create_feeding_log()
        
        # Stats section
        self.create_stats_section()
        
        # Hardware monitoring section
        self.monitoring_frame = AutomaticMonitoringFrame(
            self.main_frame, self.core
        )
        self.monitoring_frame.grid(
            row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        
        # Load existing cats
        self.load_cats()
    
    def cleanup(self):
        """Clean up resources when the application closes."""
        self.core.cleanup()

    def create_cat_management(self):
        # Cat Management Frame
        cat_frame = ttk.LabelFrame(self.main_frame, text="Cat Management", padding="5")
        cat_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Add new cat
        ttk.Label(cat_frame, text="Cat Name:").grid(row=0, column=0, padx=5)
        self.cat_name_var = tk.StringVar()
        self.cat_entry = ttk.Entry(cat_frame, textvariable=self.cat_name_var)
        self.cat_entry.grid(row=0, column=1, padx=5)
        
        ttk.Button(cat_frame, text="Add Cat", command=self.add_cat).grid(row=0, column=2, padx=5)

    def create_feeding_log(self):
        # Feeding Log Frame
        log_frame = ttk.LabelFrame(self.main_frame, text="Log Feeding", padding="5")
        log_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Cat selection
        ttk.Label(log_frame, text="Select Cat:").grid(row=0, column=0, padx=5)
        self.selected_cat = tk.StringVar()
        self.cat_combo = ttk.Combobox(log_frame, textvariable=self.selected_cat)
        self.cat_combo.grid(row=0, column=1, padx=5)
        
        # Amount
        ttk.Label(log_frame, text="Amount (g):").grid(row=1, column=0, padx=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(log_frame, textvariable=self.amount_var).grid(row=1, column=1, padx=5)
        
        # Food type
        ttk.Label(log_frame, text="Food Type:").grid(row=2, column=0, padx=5)
        self.food_type_var = tk.StringVar(value="Dry Food")
        ttk.Entry(log_frame, textvariable=self.food_type_var).grid(row=2, column=1, padx=5)
        
        # Log button
        ttk.Button(log_frame, text="Log Feeding", command=self.log_feeding).grid(row=3, column=0, columnspan=2, pady=5)

    def create_stats_section(self):
        # Stats Frame
        stats_frame = ttk.LabelFrame(self.main_frame, text="Feeding Stats", padding="5")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Stats display
        self.stats_text = tk.Text(stats_frame, height=10, width=50)
        self.stats_text.grid(row=0, column=0, padx=5, pady=5)
        
        # Refresh button
        ttk.Button(stats_frame, text="Refresh Stats", command=self.update_stats).grid(row=1, column=0, pady=5)

    def add_cat(self):
        name = self.cat_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a cat name")
            return
        
        result = self.core.add_cat(name)
        if result['success']:
            self.cat_name_var.set("")
            self.load_cats()
            messagebox.showinfo("Success", result['message'])
        else:
            messagebox.showerror("Error", result['message'])

    def load_cats(self):
        cats = self.core.get_cats()
        self.cat_combo['values'] = [cat['name'] for cat in cats]
        self.update_stats()

    def log_feeding(self):
        cat_name = self.selected_cat.get()
        if not cat_name:
            messagebox.showerror("Error", "Please select a cat")
            return
            
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            return
        
        # Find cat ID
        cats = self.core.get_cats()
        cat_id = next((cat['id'] for cat in cats if cat['name'] == cat_name), None)
        if cat_id is None:
            messagebox.showerror("Error", "Selected cat not found")
            return
        
        result = self.core.log_feeding(
            cat_id,
            amount,
            self.food_type_var.get()
        )
        
        if result['success']:
            self.amount_var.set("")
            self.update_stats()
            messagebox.showinfo("Success", result['message'])
        else:
            messagebox.showerror("Error", result['message'])

    def update_stats(self):
        stats = self.core.get_feeding_stats()
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "Feeding Statistics:\n\n")
        
        for stat in stats:
            self.stats_text.insert(tk.END,
                f"Cat: {stat['name']}\n"
                f"Total Feedings: {stat['feeding_count']}\n"
                f"Total Amount: {stat['total_amount']:.1f}g\n"
                f"Last Feeding: {stat['last_feeding']}\n\n")

def main():
    root = tk.Tk()
    app = CatFeederApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

class AutomaticMonitoringFrame(ttk.LabelFrame):
    def __init__(self, parent, hardware_monitor):
        super().__init__(parent, text="Automatic Monitoring", padding="5")
        self.hardware_monitor = hardware_monitor
        
        # Status labels
        ttk.Label(self, text="Current Food Weight:").grid(row=0, column=0, padx=5)
        self.weight_label = ttk.Label(self, text="N/A")
        self.weight_label.grid(row=0, column=1, padx=5)
        
        ttk.Label(self, text="Water Level:").grid(row=1, column=0, padx=5)
        self.water_label = ttk.Label(self, text="N/A")
        self.water_label.grid(row=1, column=1, padx=5)
        
        # Control buttons
        self.monitor_var = tk.BooleanVar(value=False)
        self.toggle_button = ttk.Checkbutton(
            self, text="Enable Automatic Monitoring",
            variable=self.monitor_var, command=self.toggle_monitoring
        )
        self.toggle_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        if not hardware_monitor.HARDWARE_AVAILABLE:
            ttk.Label(
                self, text="Running in simulation mode",
                foreground="orange"
            ).grid(row=3, column=0, columnspan=2)
        
        self.update_status()
    
    def toggle_monitoring(self):
        if self.monitor_var.get():
            self.hardware_monitor.start()
        else:
            self.hardware_monitor.stop()
    
    def update_status(self):
        if self.monitor_var.get():
            status = self.hardware_monitor.get_current_status()
            self.weight_label.config(
                text=f"{status['food_weight']:.1f}g"
            )
            self.water_label.config(
                text=f"{status['water_level']:.1f}%"
            )
        self.after(1000, self.update_status)

class CatFeederApp:
    def __init__(self, root, hardware_monitor=None):
        self.root = root
        self.root.title("AutomatiCats Feeder")
        
        # Initialize database
        self.init_database()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cat management section
        self.create_cat_management()
        
        # Feeding log section
        self.create_feeding_log()
        
        # Stats section
        self.create_stats_section()
        
        # Hardware monitoring section (if available)
        if hardware_monitor:
            self.monitoring_frame = AutomaticMonitoringFrame(
                self.main_frame, hardware_monitor
            )
            self.monitoring_frame.grid(
                row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5
            )
        
        # Load existing cats
        self.load_cats()

def main():
    try:
        from hardware_monitor import HardwareMonitor
        hardware_monitor = HardwareMonitor()
    except ImportError:
        print("Hardware monitoring not available")
        hardware_monitor = None
    
    root = tk.Tk()
    app = CatFeederApp(root, hardware_monitor)
    root.mainloop()
    
    if hardware_monitor:
        hardware_monitor.stop()

if __name__ == "__main__":
    main()