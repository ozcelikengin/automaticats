"""
Water Dispenser Tab for AutomatiCats
Allows users to manage water dispensers and track water consumption.
"""

import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFormLayout, QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot

logger = logging.getLogger('automaticats.gui.water_dispenser_tab')

class WaterDispenserTab(QWidget):
    """Tab for managing water dispensers and consumption"""
    
    def __init__(self, db_manager):
        """Initialize the water dispenser tab"""
        super().__init__()
        
        self.db_manager = db_manager
        self.selected_cat_id = None
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Coming soon message
        coming_soon = QLabel("Water Dispenser functionality will be implemented in Sprint 3")
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coming_soon.setStyleSheet("font-size: 18px; color: #666; margin: 20px;")
        layout.addWidget(coming_soon)
        
        # Features preview
        features_widget = QWidget()
        features_layout = QVBoxLayout(features_widget)
        
        features_title = QLabel("Planned Features:")
        features_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        features_layout.addWidget(features_title)
        
        features = [
            "• Real-time water level monitoring",
            "• Automated refill scheduling",
            "• Individual cat water consumption tracking",
            "• Water quality monitoring",
            "• Low water alerts"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("font-size: 14px; margin-left: 20px;")
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_widget)
        layout.addStretch()
    
    @pyqtSlot(int)
    def set_selected_cat(self, cat_id):
        """Set the selected cat ID from external signal"""
        self.selected_cat_id = cat_id
    
    @pyqtSlot()
    def refresh_water_inventory(self):
        """Refresh water inventory data (will be implemented in Sprint 3)"""
        pass 