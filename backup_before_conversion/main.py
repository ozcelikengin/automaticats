#!/usr/bin/env python3
"""
AutomatiCats Application

Main entry point for the AutomatiCats application.
"""

import sys
import os
import logging
from datetime import datetime

# Use PySide6 instead of PyQt6 to avoid installation issues
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox
from PySide6.QtCore import Qt

def setup_logging():
    """Set up logging for the application"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Set up logging to file and console
    log_file = f'logs/automaticats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # Configure root logger
    logger = logging.getLogger('automaticats')
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class SimplePlaceholderWindow(QMainWindow):
    """A simple window to show when the main UI can't be loaded"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutomatiCats")
        self.setMinimumSize(600, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Welcome to AutomatiCats!")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Message
        message = QLabel(
            "This is a temporary interface.\n\n"
            "The full application requires converting the UI from PyQt6 to PySide6\n"
            "or fixing the PyQt6 installation issues."
        )
        message.setStyleSheet("font-size: 14px;")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        
        # Add some instruction text
        instructions = QLabel(
            "\nTo fix this issue, you have two options:\n\n"
            "1. Convert all PyQt6 imports to PySide6 in the GUI files\n"
            "2. Fix the PyQt6 installation (see Windows long path issues)\n\n"
            "This placeholder window is using PySide6, which was successfully installed."
        )
        instructions.setStyleSheet("font-size: 12px; color: #555;")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)
        
        # Add spacer
        layout.addStretch()
        
        # Button
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        exit_btn.setMaximumWidth(200)
        layout.addWidget(exit_btn, 0, Qt.AlignCenter)
        layout.addStretch()

def main():
    """Main function to run the application"""
    # Set up logging
    logger = setup_logging()
    logger.info("Starting AutomatiCats application")
    
    try:
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("AutomatiCats")
        app.setOrganizationName("AutomatiCats")
        
        try:
            # Try to import the main window from gui
            from gui.main_window import MainWindow
            main_window = MainWindow()
        except ImportError as e:
            # If import fails (likely due to PyQt6/PySide6 mismatch), show simple window
            logger.warning(f"Could not import MainWindow: {e}. Using simple placeholder.")
            QMessageBox.warning(
                None, 
                "UI Import Error",
                f"Could not load the full UI: {e}\n\nShowing simplified interface."
            )
            main_window = SimplePlaceholderWindow()
        
        main_window.show()
        logger.info("Application initialized successfully")
        
        # Execute application
        return app.exec()
    
    except Exception as e:
        logger.error(f"Error starting application: {e}", exc_info=True)
        return 1
    finally:
        logger.info("Application exiting")

if __name__ == "__main__":
    sys.exit(main()) 