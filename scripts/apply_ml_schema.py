#!/usr/bin/env python3
"""
Apply ML schema updates to the AutomatiCats database.
This script reads the schema_update_ml.sql file and applies it to the database.
"""

import os
import sqlite3
import sys
import re

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
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # First, check if we need to drop and recreate ml_models
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ml_models'")
        if cursor.fetchone():
            print("Found existing ml_models table. Dropping for schema compatibility.")
            cursor.execute("DROP TABLE IF EXISTS ml_models")
            conn.commit()
            print("Successfully dropped ml_models table.")

        # Extract and execute CREATE TABLE statement for ml_models directly
        ml_models_create = None
        for statement in schema_sql.split(';'):
            if 'CREATE TABLE ml_models' in statement:
                ml_models_create = statement.strip()
                break
        
        if ml_models_create:
            print(f"Executing ml_models create statement: {ml_models_create}")
            cursor.execute(ml_models_create)
            conn.commit()
            print("Successfully created ml_models table.")
        else:
            print("ERROR: Could not find CREATE TABLE statement for ml_models in schema file.")
        
        # Split the SQL into individual statements
        sql_statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        # Process each statement
        for statement in sql_statements:
            try:
                # Skip comments
                if statement.strip().startswith('--'):
                    continue
                
                # Skip ml_models creation as we already did it
                if 'CREATE TABLE ml_models' in statement:
                    print("Skipping ml_models creation - already done.")
                    continue
                
                # Handle ALTER TABLE statements to add columns
                if statement.strip().upper().startswith('ALTER TABLE') and 'ADD COLUMN' in statement.upper():
                    # Extract table name
                    table_match = re.search(r'ALTER TABLE\s+(\w+)', statement, re.IGNORECASE)
                    if table_match:
                        table_name = table_match.group(1)
                        
                        # Extract column name
                        column_match = re.search(r'ADD COLUMN\s+(\w+)', statement, re.IGNORECASE)
                        if column_match:
                            column_name = column_match.group(1)
                            
                            # Check if column already exists
                            cursor.execute(f"PRAGMA table_info({table_name})")
                            columns = [col['name'] for col in cursor.fetchall()]
                            
                            if column_name in columns:
                                print(f"Column {column_name} already exists in table {table_name}, skipping...")
                                continue
                
                # Handle CREATE TABLE statements
                elif statement.strip().upper().startswith('CREATE TABLE'):
                    # Extract table name
                    table_match = re.search(r'CREATE TABLE\s+(\w+)', statement, re.IGNORECASE)
                    if table_match:
                        table_name = table_match.group(1)
                        
                        # Skip check for ml_models since we deliberately dropped it
                        if table_name == 'ml_models':
                            continue  # Skip as we already created it
                            
                        # Check if table already exists
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                        if cursor.fetchone():
                            print(f"Table {table_name} already exists, skipping creation...")
                            continue
                
                # Execute the statement
                cursor.execute(statement)
                print(f"Executed: {statement[:50]}{'...' if len(statement) > 50 else ''}")
            
            except sqlite3.Error as e:
                print(f"Error executing statement: {e}")
                print(f"Statement: {statement}")
                # Continue with other statements
        
        # Verify the ml_models table was created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ml_models'")
        if cursor.fetchone():
            print("Verification: ml_models table exists after schema update.")
            
            # Check columns
            cursor.execute("PRAGMA table_info(ml_models)")
            columns = cursor.fetchall()
            print("ml_models columns:")
            for col in columns:
                print(f"  {col['name']} ({col['type']})")
        else:
            print("ERROR: ml_models table was not created!")
        
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