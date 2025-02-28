#!/usr/bin/env python3
"""
PyQt6 to PySide6 Converter

This script scans all Python files in the project and converts PyQt6 imports to PySide6.
This is useful if you're having issues with PyQt6 installation on Windows due to long path names.
"""

import os
import re
import sys
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file before modifying it"""
    backup_dir = "backup_before_conversion"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create relative path structure
    rel_path = os.path.relpath(file_path)
    backup_path = os.path.join(backup_dir, rel_path)
    
    # Create necessary directories
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    
    # Copy the file
    shutil.copy2(file_path, backup_path)
    return backup_path

def convert_file(file_path):
    """Convert PyQt6 imports to PySide6 in a single file"""
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file contains PyQt6 imports
    if 'PyQt6' not in content:
        print(f"  No PyQt6 imports found. Skipping.")
        return False
    
    # Backup the file
    backup_path = backup_file(file_path)
    print(f"  Created backup: {backup_path}")
    
    # Replace imports
    new_content = re.sub(r'from PyQt6\.', 'from PySide6.', content)
    new_content = re.sub(r'import PyQt6\.', 'import PySide6.', new_content)
    
    # Handle specific API differences
    
    # Signal -> Signal
    new_content = re.sub(r'Signal', 'Signal', new_content)
    
    # exec() -> exec_()
    if '.exec()' in new_content:
        print(f"  Note: Found .exec() method - PySide6 may use .exec_() instead")
    
    # Fix specific Qt constants
    if 'Qt.ItemDataRole' in new_content:
        print(f"  Note: Found Qt.ItemDataRole which might need manual fixing in PySide6")
    
    if 'Qt.AlignmentFlag' in new_content:
        print(f"  Note: Found Qt.AlignmentFlag which might need manual fixing in PySide6")
    
    # Write the modified content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  Converted PyQt6 imports to PySide6")
    return True

def convert_directory(directory='.'):
    """Convert all Python files in the directory and its subdirectories"""
    converted_count = 0
    skipped_count = 0
    
    for root, dirs, files in os.walk(directory):
        # Skip the backup directory and virtual environments
        if ('backup_before_conversion' in root or 
            'venv' in root or 
            '.git' in root or
            'env' in root or
            '__pycache__' in root):
            continue
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if convert_file(file_path):
                    converted_count += 1
                else:
                    skipped_count += 1
    
    return converted_count, skipped_count

def main():
    """Main function to run the converter"""
    print("PyQt6 to PySide6 Converter")
    print("=========================")
    print("This script will convert PyQt6 imports to PySide6 in all Python files.")
    print("Backups will be created in the 'backup_before_conversion' directory.")
    print()
    
    response = input("Do you want to proceed? (y/n): ").strip().lower()
    if response != 'y':
        print("Conversion cancelled.")
        return
    
    print("\nStarting conversion...\n")
    start_time = datetime.now()
    
    try:
        converted, skipped = convert_directory()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\nConversion completed!")
        print(f"Converted {converted} files, skipped {skipped} files in {duration:.2f} seconds.")
        print("\nNOTE: Some manual adjustments may still be needed for API differences.")
        print("Known differences between PyQt6 and PySide6:")
        print("  - PyQt6 uses Signal, PySide6 uses Signal")
        print("  - PyQt6 uses exec(), PySide6 may use exec_()")
        print("  - Some enum values are accessed differently")
        print("\nYou can now run the application with:")
        print("  python run.py")
        
    except Exception as e:
        print(f"\nError during conversion: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 