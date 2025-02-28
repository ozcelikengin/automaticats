"""
Main Window for AutomatiCats application
"""

import sys
import os
import logging
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QLabel, QMessageBox,
    QApplication, QStatusBar
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon, QPixmap

# Import tab widgets
from gui.tabs.cat_management_tab import CatManagementTab
from gui.tabs.feeding_schedule_tab import FeedingScheduleTab
from gui.tabs.water_dispenser_tab import WaterDispenserTab
from gui.tabs.inventory_tab import InventoryTab
from gui.tabs.statistics_tab import StatisticsTab
from gui.tabs.ml_recommendations_tab import MLRecommendationsTab

# Import database manager
from core.db_manager import DatabaseManager

logger = logging.getLogger('automaticats.main_window')

class MainWindow(QMainWindow):
    """Main window for the AutomatiCats application"""
    
    def __init__(self):
        """Initialize the main window"""
        super().__init__()
        
        # Initialize the database
        self.db_manager = DatabaseManager()
        
        # Set up the UI
        self.setup_ui()
        
        # Set up notification timer
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.check_inventory_levels)
        self.notification_timer.start(60000)  # Check every minute
        
        # Initial inventory check
        QTimer.singleShot(1000, self.check_inventory_levels)
        
    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle("AutomatiCats - Cat Feeder & Water Dispenser")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create header with logo and title
        header_layout = QHBoxLayout()
        
        # Logo placeholder (replace with actual logo path)
        logo_label = QLabel()
        # logo_pixmap = QPixmap("assets/logo.png")
        # logo_label.setPixmap(logo_pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
        logo_label.setText("🐱")  # Temporary placeholder
        logo_label.setStyleSheet("font-size: 40px;")
        header_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("AutomatiCats")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel("System Status: OK")
        self.status_indicator.setStyleSheet("color: green;")
        header_layout.addWidget(self.status_indicator)
        
        main_layout.addLayout(header_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Create tabs
        self.cat_tab = CatManagementTab(self.db_manager)
        self.feeding_tab = FeedingScheduleTab(self.db_manager)
        self.water_tab = WaterDispenserTab(self.db_manager)
        self.inventory_tab = InventoryTab(self.db_manager)
        self.stats_tab = StatisticsTab(self.db_manager)
        self.ml_tab = MLRecommendationsTab(self.db_manager)
        
        # Add tabs to widget
        self.tab_widget.addTab(self.cat_tab, "Cat Management")
        self.tab_widget.addTab(self.feeding_tab, "Feeding Schedule")
        self.tab_widget.addTab(self.water_tab, "Water Dispenser")
        self.tab_widget.addTab(self.inventory_tab, "Inventory")
        self.tab_widget.addTab(self.stats_tab, "Statistics")
        self.tab_widget.addTab(self.ml_tab, "Smart Insights")
        
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Connect signals between tabs
        self.connect_signals()
    
    def connect_signals(self):
        """Connect signals between tabs for communication"""
        # Connect cat selection in cat tab to feeding and water tabs
        self.cat_tab.cat_selected.connect(self.feeding_tab.set_selected_cat)
        self.cat_tab.cat_selected.connect(self.water_tab.set_selected_cat)
        self.cat_tab.cat_selected.connect(self.stats_tab.set_selected_cat)
        
        # Connect inventory updates to relevant tabs
        self.inventory_tab.food_inventory_updated.connect(self.feeding_tab.refresh_food_inventory)
        self.inventory_tab.water_inventory_updated.connect(self.water_tab.refresh_water_inventory)
        
        # Connect ML tab signals
        self.cat_tab.cat_selected.connect(lambda cat_id: self.ml_tab.cat_combo.setCurrentIndex(
            self.ml_tab.cat_combo.findData(cat_id)
        ))
        self.ml_tab.feedback_submitted.connect(self.handle_ml_feedback)
    
    def handle_ml_feedback(self, rec_id, accepted, value):
        """Handle feedback from ML recommendations"""
        if accepted:
            self.statusBar.showMessage(f"Recommendation applied: {value}")
        else:
            self.statusBar.showMessage("Recommendation ignored")
    
    def check_inventory_levels(self):
        """Check inventory levels and show notifications if low"""
        try:
            # Check food inventory
            low_food = self.db_manager.get_low_food_inventory()
            
            # TODO: Implement water inventory check
            # low_water = self.db_manager.get_low_water_inventory()
            
            if low_food:
                food_types = ", ".join([item['food_type'] for item in low_food])
                self.statusBar.showMessage(f"Low food inventory: {food_types}")
                self.status_indicator.setText("System Status: Warning")
                self.status_indicator.setStyleSheet("color: orange;")
                
                # Show notification if not already shown
                if not hasattr(self, '_shown_food_notification') or not self._shown_food_notification:
                    QMessageBox.warning(
                        self, 
                        "Low Food Inventory", 
                        f"The following food types are running low: {food_types}. Please refill soon.",
                        QMessageBox.StandardButton.Ok
                    )
                    self._shown_food_notification = True
            else:
                self._shown_food_notification = False
                
            # TODO: Handle water inventory notifications
            
        except Exception as e:
            logger.error(f"Error checking inventory levels: {e}")
            self.statusBar.showMessage(f"Error checking inventory: {str(e)}")
            self.status_indicator.setText("System Status: Error")
            self.status_indicator.setStyleSheet("color: red;")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Close database connection
        self.db_manager.close()
        
        # Accept the event and close the window
        event.accept() 