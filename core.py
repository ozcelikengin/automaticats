import sqlite3
from datetime import datetime
import logging
from typing import Optional, Dict, Any, List
import json

class CatFeederCore:
    def __init__(self, db_path: str = 'cat_feeder.db'):
        self.db_path = db_path
        self.setup_logging()
        self.init_database()
        
        # Try to import hardware support
        try:
            from hardware_monitor import HardwareMonitor
            self.hardware = HardwareMonitor(db_path)
            self.hardware.start()
            self.has_hardware = True
        except ImportError:
            self.hardware = None
            self.has_hardware = False
            self.logger.info("Running without hardware support")
    
    def setup_logging(self):
        self.logger = logging.getLogger('CatFeederCore')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('cat_feeder.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
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
    
    def add_cat(self, name: str) -> Dict[str, Any]:
        """Add a new cat to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO cats (name) VALUES (?)", (name,))
                conn.commit()
                return {
                    'success': True,
                    'message': f"Cat {name} added successfully!",
                    'cat_id': c.lastrowid
                }
        except sqlite3.IntegrityError:
            return {
                'success': False,
                'message': f"Cat {name} already exists!"
            }
        except Exception as e:
            self.logger.error(f"Error adding cat: {e}")
            return {
                'success': False,
                'message': f"Error adding cat: {str(e)}"
            }
    
    def get_cats(self) -> List[Dict[str, Any]]:
        """Get list of all cats."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT id, name FROM cats ORDER BY name")
                return [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
        except Exception as e:
            self.logger.error(f"Error getting cats: {e}")
            return []
    
    def log_feeding(self, cat_id: int, amount: float, food_type: str = "Dry Food") -> Dict[str, Any]:
        """Log a feeding event."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("""INSERT INTO feeding_logs 
                            (cat_id, timestamp, amount, food_type)
                            VALUES (?, ?, ?, ?)""",
                         (cat_id, datetime.now(), amount, food_type))
                conn.commit()
                return {
                    'success': True,
                    'message': "Feeding logged successfully!"
                }
        except Exception as e:
            self.logger.error(f"Error logging feeding: {e}")
            return {
                'success': False,
                'message': f"Error logging feeding: {str(e)}"
            }
    
    def get_feeding_stats(self) -> List[Dict[str, Any]]:
        """Get feeding statistics for all cats."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT c.name,
                           COUNT(*) as feeding_count,
                           SUM(amount) as total_amount,
                           MAX(timestamp) as last_feeding
                    FROM cats c
                    LEFT JOIN feeding_logs fl ON c.id = fl.cat_id
                    GROUP BY c.name
                    ORDER BY c.name
                """)
                return [{
                    'name': row[0],
                    'feeding_count': row[1] or 0,
                    'total_amount': row[2] or 0,
                    'last_feeding': row[3] or "Never"
                } for row in c.fetchall()]
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return []
    
    def get_recent_feedings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent feeding events."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT c.name, fl.timestamp, fl.amount, fl.food_type
                    FROM feeding_logs fl
                    JOIN cats c ON fl.cat_id = c.id
                    ORDER BY fl.timestamp DESC
                    LIMIT ?
                """, (limit,))
                return [{
                    'cat_name': row[0],
                    'timestamp': row[1],
                    'amount': row[2],
                    'food_type': row[3]
                } for row in c.fetchall()]
        except Exception as e:
            self.logger.error(f"Error getting recent feedings: {e}")
            return []
    
    def get_hardware_status(self) -> Dict[str, Any]:
        """Get current hardware status."""
        if not self.has_hardware:
            return {
                'hardware_available': False,
                'food_weight': 0.0,
                'water_level': 0.0,
                'timestamp': datetime.now().isoformat()
            }
        
        return self.hardware.get_current_status()
    
    def trigger_feeding(self, amount: float) -> Dict[str, Any]:
        """Trigger automatic feeding."""
        if not self.has_hardware:
            return {
                'success': False,
                'message': "Hardware not available"
            }
        
        return {
            'success': self.hardware.trigger_feeding(amount),
            'message': "Feeding triggered successfully"
        }
    
    def identify_cat(self) -> Dict[str, Any]:
        """Identify cat using camera."""
        if not self.has_hardware:
            return {
                'success': False,
                'message': "Hardware not available"
            }
        
        return self.hardware.identify_cat()
    
    def cleanup(self):
        """Clean up resources."""
        if self.has_hardware:
            self.hardware.stop()