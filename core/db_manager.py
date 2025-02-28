"""
Database Manager for AutomatiCats
Handles all database operations for storing and retrieving cat data,
feeding schedules, consumption logs, and water dispenser data.
"""

import os
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger('automaticats.db_manager')

class DatabaseManager:
    """Manages all database operations for the AutomatiCats application"""
    
    def __init__(self, db_path='data/automaticats.db'):
        """Initialize the database manager and create tables if they don't exist"""
        self.db_path = db_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connect to database and create tables if they don't exist
        self.conn = self._get_connection()
        self._create_tables()
        logger.info(f"Database initialized at {db_path}")
    
    def _get_connection(self):
        """Create and return a database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.conn.cursor()
            
            # Cats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age REAL,
                    weight REAL,
                    photo_path TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Food inventory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS food_inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    food_type TEXT NOT NULL,
                    current_amount REAL NOT NULL,
                    max_capacity REAL NOT NULL,
                    low_threshold REAL NOT NULL,
                    last_refill_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Water inventory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS water_inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dispenser_name TEXT NOT NULL,
                    current_amount REAL NOT NULL,
                    max_capacity REAL NOT NULL,
                    low_threshold REAL NOT NULL,
                    last_refill_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Feeding schedules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feeding_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cat_id INTEGER NOT NULL,
                    food_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    time TEXT NOT NULL,
                    days_of_week TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cat_id) REFERENCES cats (id) ON DELETE CASCADE
                )
            ''')
            
            # Feeding logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feeding_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cat_id INTEGER NOT NULL,
                    schedule_id INTEGER,
                    food_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_manual BOOLEAN NOT NULL DEFAULT 0,
                    notes TEXT,
                    FOREIGN KEY (cat_id) REFERENCES cats (id) ON DELETE CASCADE,
                    FOREIGN KEY (schedule_id) REFERENCES feeding_schedules (id) ON DELETE SET NULL
                )
            ''')
            
            # Water dispenser logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS water_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cat_id INTEGER NOT NULL,
                    dispenser_id INTEGER,
                    amount REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_manual BOOLEAN NOT NULL DEFAULT 0,
                    notes TEXT,
                    FOREIGN KEY (cat_id) REFERENCES cats (id) ON DELETE CASCADE,
                    FOREIGN KEY (dispenser_id) REFERENCES water_inventory (id) ON DELETE SET NULL
                )
            ''')
            
            self.conn.commit()
            logger.info("Database tables created successfully")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            self.conn.rollback()
            raise
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    # Cat-related methods
    def add_cat(self, name, age=None, weight=None, photo_path=None, notes=None):
        """Add a new cat to the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO cats (name, age, weight, photo_path, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, age, weight, photo_path, notes))
            self.conn.commit()
            cat_id = cursor.lastrowid
            logger.info(f"Added cat '{name}' with ID {cat_id}")
            return cat_id
        except sqlite3.Error as e:
            logger.error(f"Error adding cat: {e}")
            self.conn.rollback()
            raise
    
    def get_all_cats(self):
        """Get all cats from the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM cats ORDER BY name')
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error getting cats: {e}")
            raise
    
    def get_cat(self, cat_id):
        """Get a specific cat by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM cats WHERE id = ?', (cat_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Error getting cat ID {cat_id}: {e}")
            raise
    
    def update_cat(self, cat_id, name, age=None, weight=None, photo_path=None, notes=None):
        """Update cat information"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE cats 
                SET name = ?, age = ?, weight = ?, photo_path = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (name, age, weight, photo_path, notes, cat_id))
            self.conn.commit()
            logger.info(f"Updated cat ID {cat_id}")
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error updating cat ID {cat_id}: {e}")
            self.conn.rollback()
            raise
    
    def delete_cat(self, cat_id):
        """Delete a cat from the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM cats WHERE id = ?', (cat_id,))
            self.conn.commit()
            logger.info(f"Deleted cat ID {cat_id}")
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting cat ID {cat_id}: {e}")
            self.conn.rollback()
            raise
    
    # Food inventory methods
    def add_food_inventory(self, food_type, current_amount, max_capacity, low_threshold):
        """Add a new food inventory item"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO food_inventory (food_type, current_amount, max_capacity, low_threshold, last_refill_date)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (food_type, current_amount, max_capacity, low_threshold))
            self.conn.commit()
            inventory_id = cursor.lastrowid
            logger.info(f"Added food inventory for '{food_type}' with ID {inventory_id}")
            return inventory_id
        except sqlite3.Error as e:
            logger.error(f"Error adding food inventory: {e}")
            self.conn.rollback()
            raise
    
    def update_food_level(self, inventory_id, current_amount, is_refill=False):
        """Update food inventory level"""
        try:
            cursor = self.conn.cursor()
            if is_refill:
                cursor.execute('''
                    UPDATE food_inventory 
                    SET current_amount = ?, last_refill_date = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (current_amount, inventory_id))
            else:
                cursor.execute('''
                    UPDATE food_inventory 
                    SET current_amount = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (current_amount, inventory_id))
            self.conn.commit()
            logger.info(f"Updated food inventory ID {inventory_id} to {current_amount}")
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error updating food inventory ID {inventory_id}: {e}")
            self.conn.rollback()
            raise
    
    def get_food_inventory(self, inventory_id=None):
        """Get food inventory. If no ID provided, get all inventory items"""
        try:
            cursor = self.conn.cursor()
            if inventory_id:
                cursor.execute('SELECT * FROM food_inventory WHERE id = ?', (inventory_id,))
                return cursor.fetchone()
            else:
                cursor.execute('SELECT * FROM food_inventory ORDER BY food_type')
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error getting food inventory: {e}")
            raise
    
    def get_low_food_inventory(self):
        """Get all food inventory items below their low threshold"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM food_inventory 
                WHERE current_amount <= low_threshold
                ORDER BY food_type
            ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error getting low food inventory: {e}")
            raise
    
    # Similar methods for water inventory, feeding schedules, and logs...
    # (To be implemented)

    def add_feeding_schedule(self, cat_id, food_type, amount, time, days_of_week):
        """Add a new feeding schedule"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO feeding_schedules (cat_id, food_type, amount, time, days_of_week)
                VALUES (?, ?, ?, ?, ?)
            ''', (cat_id, food_type, amount, time, days_of_week))
            self.conn.commit()
            schedule_id = cursor.lastrowid
            logger.info(f"Added feeding schedule for cat ID {cat_id} at {time}")
            return schedule_id
        except sqlite3.Error as e:
            logger.error(f"Error adding feeding schedule: {e}")
            self.conn.rollback()
            raise
    
    def get_feeding_schedules(self, cat_id=None):
        """Get feeding schedules. If cat_id is provided, get only that cat's schedules"""
        try:
            cursor = self.conn.cursor()
            if cat_id:
                cursor.execute('''
                    SELECT fs.*, c.name as cat_name
                    FROM feeding_schedules fs
                    JOIN cats c ON fs.cat_id = c.id
                    WHERE fs.cat_id = ?
                    ORDER BY fs.time
                ''', (cat_id,))
            else:
                cursor.execute('''
                    SELECT fs.*, c.name as cat_name
                    FROM feeding_schedules fs
                    JOIN cats c ON fs.cat_id = c.id
                    ORDER BY fs.time
                ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error getting feeding schedules: {e}")
            raise
    
    def log_feeding(self, cat_id, food_type, amount, schedule_id=None, is_manual=False, notes=None):
        """Log a feeding event"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO feeding_logs (cat_id, schedule_id, food_type, amount, is_manual, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cat_id, schedule_id, food_type, amount, is_manual, notes))
            self.conn.commit()
            log_id = cursor.lastrowid
            
            # Update food inventory
            self._update_food_inventory_after_feeding(food_type, amount)
            
            logger.info(f"Logged feeding for cat ID {cat_id}, amount: {amount}")
            return log_id
        except sqlite3.Error as e:
            logger.error(f"Error logging feeding: {e}")
            self.conn.rollback()
            raise
    
    def _update_food_inventory_after_feeding(self, food_type, amount_used):
        """Update food inventory after a feeding event"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE food_inventory
                SET current_amount = MAX(0, current_amount - ?), 
                    updated_at = CURRENT_TIMESTAMP
                WHERE food_type = ?
            ''', (amount_used, food_type))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating food inventory after feeding: {e}")
            self.conn.rollback()
            raise
    
    def get_feeding_logs(self, cat_id=None, start_date=None, end_date=None):
        """Get feeding logs with optional filters"""
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT fl.*, c.name as cat_name
                FROM feeding_logs fl
                JOIN cats c ON fl.cat_id = c.id
            '''
            params = []
            
            # Add filters
            where_clauses = []
            if cat_id:
                where_clauses.append("fl.cat_id = ?")
                params.append(cat_id)
            if start_date:
                where_clauses.append("fl.timestamp >= ?")
                params.append(start_date)
            if end_date:
                where_clauses.append("fl.timestamp <= ?")
                params.append(end_date)
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += " ORDER BY fl.timestamp DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error getting feeding logs: {e}")
            raise 