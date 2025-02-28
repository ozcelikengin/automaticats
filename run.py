#!/usr/bin/env python3
"""
AutomatiCats Launcher

This script launches the AutomatiCats application.
"""

import sys
import os
import platform
import subprocess
import importlib.util
import traceback

def setup_environment():
    """Set up the environment for the application"""
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/photos', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Set platform-specific configurations
    if platform.system() == 'Windows':
        # Windows-specific setup
        pass
    elif platform.system() == 'Darwin':
        # macOS-specific setup
        pass
    else:
        # Linux/Unix-specific setup
        pass

def check_dependencies():
    """Check if necessary dependencies are installed"""
    # First try importing PySide6 (our preferred alternative)
    if importlib.util.find_spec("PySide6") is not None:
        print("PySide6 is installed. Will use it instead of PyQt6.")
        return True
        
    # Then check for PyQt6
    if importlib.util.find_spec("PyQt6") is not None:
        print("PyQt6 is installed.")
        return True
    
    # If neither is installed, ask to install PySide6
    print("Neither PySide6 nor PyQt6 is installed.")
    print("Would you like to install PySide6? (recommended) (y/n)")
    choice = input().strip().lower()
    if choice == 'y':
        try:
            print("Installing PySide6...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "PySide6",
                "--no-cache-dir", "--disable-pip-version-check"
            ])
            print("PySide6 installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing PySide6: {e}")
            print("Please install dependencies manually by running:")
            print("  pip install PySide6")
            return False
    else:
        print("Please install either PySide6 or PyQt6 manually:")
        print("  pip install PySide6")
        print("  or")
        print("  pip install PyQt6")
        return False

def main():
    """Main function to launch the application"""
    print("Starting AutomatiCats...")
    
    try:
        # Set up environment
        setup_environment()
        
        # Check dependencies
        if not check_dependencies():
            print("Missing dependencies. Please install them and try again.")
            return 1
        
        # Import and run the main application
        try:
            # Make sure the current directory is in the path
            if os.getcwd() not in sys.path:
                sys.path.insert(0, os.getcwd())
                
            # Try to import the main module
            from main import main as run_app
            return run_app()
            
        except ImportError as e:
            print(f"Error importing application: {e}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Python path: {sys.path}")
            print("\nTraceback:")
            traceback.print_exc()
            
            print("\nPlease check that all files are in the correct location.")
            return 1
            
        except Exception as e:
            print(f"Error running application: {e}")
            print("\nTraceback:")
            traceback.print_exc()
            return 1
            
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        return 0
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 