import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

class CatFeederApp:
    def __init__(self, root):
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
        
        # Load existing cats
        self.load_cats()

    def init_database(self):
        with sqlite3.connect('cat_feeder.db') as conn:
            c = conn.cursor()
            # Create cats table
            c.execute('''CREATE TABLE IF NOT EXISTS cats
                        (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
            
            # Create feeding_logs table
            c.execute('''CREATE TABLE IF NOT EXISTS feeding_logs
                        (id INTEGER PRIMARY KEY,
                         cat_id INTEGER,
                         timestamp DATETIME,
                         amount REAL,
                         food_type TEXT,
                         FOREIGN KEY (cat_id) REFERENCES cats(id))''')
            conn.commit()

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
            
        try:
            with sqlite3.connect('cat_feeder.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO cats (name) VALUES (?)", (name,))
                conn.commit()
                
            self.cat_name_var.set("")
            self.load_cats()
            messagebox.showinfo("Success", f"Cat {name} added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Cat {name} already exists!")

    def load_cats(self):
        with sqlite3.connect('cat_feeder.db') as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM cats")
            cats = [row[0] for row in c.fetchall()]
            self.cat_combo['values'] = cats
            
        self.update_stats()

    def log_feeding(self):
        cat = self.selected_cat.get()
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            return
            
        food_type = self.food_type_var.get()
        
        if not cat:
            messagebox.showerror("Error", "Please select a cat")
            return
            
        with sqlite3.connect('cat_feeder.db') as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM cats WHERE name=?", (cat,))
            cat_id = c.fetchone()[0]
            
            c.execute("""INSERT INTO feeding_logs 
                        (cat_id, timestamp, amount, food_type)
                        VALUES (?, ?, ?, ?)""",
                     (cat_id, datetime.now(), amount, food_type))
            conn.commit()
            
        self.amount_var.set("")
        self.update_stats()
        messagebox.showinfo("Success", "Feeding logged successfully!")

    def update_stats(self):
        with sqlite3.connect('cat_feeder.db') as conn:
            c = conn.cursor()
            c.execute("""
                SELECT c.name,
                       COUNT(*) as feeding_count,
                       SUM(amount) as total_amount,
                       MAX(timestamp) as last_feeding
                FROM cats c
                LEFT JOIN feeding_logs fl ON c.id = fl.cat_id
                GROUP BY c.name
            """)
            stats = c.fetchall()
            
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "Feeding Statistics:\n\n")
        
        for name, count, total, last in stats:
            count = count if count else 0
            total = total if total else 0
            last = last if last else "Never"
            self.stats_text.insert(tk.END, 
                f"Cat: {name}\n"
                f"Total Feedings: {count}\n"
                f"Total Amount: {total:.1f}g\n"
                f"Last Feeding: {last}\n\n")

def main():
    root = tk.Tk()
    app = CatFeederApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()