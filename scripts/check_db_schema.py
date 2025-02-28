#!/usr/bin/env python3
"""
Check the database schema for AutomatiCats
"""

import os
import sqlite3
import sys

def check_schema():
    """Check the schema of the database tables"""
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Path to the database
    db_path = os.path.join(project_root, 'data', 'automaticats.db')
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables in the database:")
        for table in tables:
            table_name = table['name']
            print(f"\n===== TABLE: {table_name} =====")
            
            # Get the table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                print(f"  {col['name']} ({col['type']}){' PRIMARY KEY' if col['pk'] else ''}")
        
        # Close the connection
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error checking database schema: {e}")
        return False

if __name__ == "__main__":
    success = check_schema()
    sys.exit(0 if success else 1) 