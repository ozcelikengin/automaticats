#!/usr/bin/env python3
"""
Apply ML schema updates to the AutomatiCats database.
This script reads the schema_update_ml.sql file and applies it to the database.
"""

import os
import sqlite3
import sys

def apply_schema_updates():
    """Apply the ML schema updates to the database."""
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Paths to the database and schema files
    db_path = os.path.join(project_root, 'data', 'automaticats.db')
    schema_path = os.path.join(project_root, 'database', 'schema_update_ml.sql')
    
    # Check if files exist
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False
    
    if not os.path.exists(schema_path):
        print(f"Error: Schema update file not found at {schema_path}")
        return False
    
    # Read the schema update SQL
    try:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
    except Exception as e:
        print(f"Error reading schema file: {e}")
        return False
    
    # Apply the schema updates
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Split the SQL into individual statements and execute them
        sql_statements = schema_sql.split(';')
        for statement in sql_statements:
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        conn.close()
        print(f"Schema updates successfully applied to {db_path}")
        return True
    except Exception as e:
        print(f"Error applying schema updates: {e}")
        return False

if __name__ == "__main__":
    success = apply_schema_updates()
    sys.exit(0 if success else 1) 