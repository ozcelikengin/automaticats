#!/usr/bin/env python3
"""
AutomatiCats Dependency Installer

This script attempts to install the dependencies required by AutomatiCats
while working around common installation issues.
"""

import subprocess
import sys
import os

def main():
    """Install dependencies with appropriate options"""
    print("AutomatiCats Dependency Installer")
    print("=================================")
    
    # Check if running on Windows
    is_windows = os.name == 'nt'
    
    print("Attempting to install dependencies...")
    
    try:
        # On Windows, we need to handle long path issues
        if is_windows:
            print("Installing PyQt6 with options to handle long paths...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "PyQt6>=6.5.0", 
                "--no-cache-dir", 
                "--disable-pip-version-check"
            ])
        else:
            # On other platforms, just install from requirements.txt
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            
        print("\nDependencies installed successfully!")
        print("\nYou can now run the application with:")
        print("python run.py")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError installing dependencies: {e}")
        print("\nAlternative solutions:")
        
        if is_windows:
            print("\n1. Enable long paths in Windows:")
            print("   - Run regedit.exe as administrator")
            print("   - Navigate to HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\FileSystem")
            print("   - Set the value of LongPathsEnabled to 1")
            print("   - Restart your computer")
            print("\n2. Try using a virtual environment in a shorter path:")
            print("   python -m venv C:\\venv\\automaticats")
            print("   C:\\venv\\automaticats\\Scripts\\activate")
            print("   pip install PyQt6>=6.5.0")
            print("\n3. Consider using PySide6 as an alternative to PyQt6:")
            print("   - Edit requirements.txt to replace PyQt6 with PySide6")
            print("   - Replace 'PyQt6' imports with 'PySide6' in the code")
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 