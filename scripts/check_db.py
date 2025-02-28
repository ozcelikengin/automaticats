#!/usr/bin/env python3
"""
Simple script to check database tables and contents
"""

import sqlite3
import os
import sys
from pprint import pprint

def main():
    # Connect to the database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'automaticats.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check the tables in the database
    print("Tables in the database:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table['name']}")
    
    print("\n")
    
    # Check the cats table
    print("Cats in the database:")
    cursor.execute("SELECT * FROM cats")
    cats = cursor.fetchall()
    for cat in cats:
        print(f"Cat ID: {cat['id']}, Name: {cat['name']}, Age: {cat['age']}, Weight: {cat['weight']}")
    
    print("\n")
    
    # Check the feeding_logs table
    print("Feeding logs in the database:")
    cursor.execute("SELECT * FROM feeding_logs")
    logs = cursor.fetchall()
    for log in logs:
        log_dict = dict(log)
        pprint(log_dict)
        print("-" * 40)
    
    print("\n")
    
    # Close the connection
    conn.close()

if __name__ == "__main__":
    main() 