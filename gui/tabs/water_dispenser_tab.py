"""
Water Dispenser Tab for AutomatiCats
Allows users to manage water dispensers and track water consumption.
"""

import logging
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFormLayout, QTabWidget, QMessageBox, QComboBox, 
    QSpinBox, QDoubleSpinBox, QGroupBox, QProgressBar, QSlider
)
from PySide6.QtCore import Qt, Slot, QDate

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
        
        # Coming soon message (with updated message)
        coming_soon = QLabel("Water Dispenser functionality is in development (Sprint 3)")
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coming_soon.setStyleSheet("font-size: 18px; color: #666; margin: 20px;")
        layout.addWidget(coming_soon)
        
        # Create tabs for water dispenser controls
        tab_widget = QTabWidget()
        
        # Add tabs
        tab_widget.addTab(self._create_status_tab(), "Status")
        tab_widget.addTab(self._create_settings_tab(), "Settings")
        tab_widget.addTab(self._create_history_tab(), "History")
        
        layout.addWidget(tab_widget)
    
    def _create_status_tab(self):
        """Create the status tab showing current water dispenser status"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Status group
        status_group = QGroupBox("Current Status")
        status_layout = QFormLayout(status_group)
        
        # Water level
        level_layout = QHBoxLayout()
        water_level = QProgressBar()
        water_level.setValue(75)  # Sample value
        water_level.setStyleSheet("QProgressBar { height: 20px; }")
        level_layout.addWidget(water_level)
        
        refill_button = QPushButton("Refill")
        refill_button.clicked.connect(self._on_refill_clicked)
        level_layout.addWidget(refill_button)
        
        status_layout.addRow("Water Level:", level_layout)
        
        # Last dispense
        status_layout.addRow("Last Dispense:", QLabel("Today 10:45 AM (Whiskers)"))
        
        # Last refill
        status_layout.addRow("Last Refill:", QLabel("2023-06-01 08:30 AM"))
        
        # Water quality
        quality_label = QLabel("Excellent")
        quality_label.setStyleSheet("color: green; font-weight: bold;")
        status_layout.addRow("Water Quality:", quality_label)
        
        # Water temperature
        status_layout.addRow("Water Temperature:", QLabel("20°C (68°F)"))
        
        layout.addWidget(status_group)
        
        # Manual dispense group
        dispense_group = QGroupBox("Manual Dispense")
        dispense_layout = QVBoxLayout(dispense_group)
        
        # Cat selection
        cat_layout = QHBoxLayout()
        cat_combo = QComboBox()
        cat_combo.addItem("Select a cat...")
        cat_combo.addItem("All Cats")
        # In a real implementation, we would populate this from the database
        cat_layout.addWidget(cat_combo, 1)
        dispense_layout.addLayout(cat_layout)
        
        # Amount selection
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Amount:"))
        
        amount_slider = QSlider(Qt.Orientation.Horizontal)
        amount_slider.setMinimum(10)
        amount_slider.setMaximum(100)
        amount_slider.setValue(30)
        amount_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        amount_slider.setTickInterval(10)
        amount_layout.addWidget(amount_slider, 1)
        
        amount_spin = QSpinBox()
        amount_spin.setMinimum(10)
        amount_spin.setMaximum(100)
        amount_spin.setValue(30)
        amount_spin.setSuffix(" ml")
        amount_layout.addWidget(amount_spin)
        
        # Connect slider and spin box
        amount_slider.valueChanged.connect(amount_spin.setValue)
        amount_spin.valueChanged.connect(amount_slider.setValue)
        
        dispense_layout.addLayout(amount_layout)
        
        # Dispense button
        dispense_button = QPushButton("Dispense Water")
        dispense_button.clicked.connect(self._on_dispense_clicked)
        dispense_button.setStyleSheet("font-weight: bold; padding: 8px;")
        dispense_layout.addWidget(dispense_button)
        
        layout.addWidget(dispense_group)
        layout.addStretch()
        
        return tab
    
    def _create_settings_tab(self):
        """Create the settings tab for water dispenser configuration"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Automatic dispensing
        auto_combo = QComboBox()
        auto_combo.addItems(["Disabled", "Scheduled", "On Demand", "Smart (AI)"])
        layout.addRow("Dispensing Mode:", auto_combo)
        
        # Default amount
        default_amount = QSpinBox()
        default_amount.setMinimum(10)
        default_amount.setMaximum(200)
        default_amount.setValue(30)
        default_amount.setSuffix(" ml")
        layout.addRow("Default Amount:", default_amount)
        
        # Water temperature
        temp_combo = QComboBox()
        temp_combo.addItems(["Room Temperature", "Cool", "Cold"])
        layout.addRow("Water Temperature:", temp_combo)
        
        # Filter settings
        filter_group = QGroupBox("Filter Settings")
        filter_layout = QFormLayout(filter_group)
        
        filter_combo = QComboBox()
        filter_combo.addItems(["Standard", "Carbon", "Advanced"])
        filter_layout.addRow("Filter Type:", filter_combo)
        
        filter_date = QLabel("2023-05-01")
        filter_layout.addRow("Last Replacement:", filter_date)
        
        replace_button = QPushButton("Replace Filter")
        replace_button.clicked.connect(self._on_replace_filter_clicked)
        filter_layout.addRow("", replace_button)
        
        layout.addRow("", filter_group)
        
        # Apply button
        apply_button = QPushButton("Apply Settings")
        apply_button.clicked.connect(self._on_apply_settings_clicked)
        layout.addRow("", apply_button)
        
        return tab
    
    def _create_history_tab(self):
        """Create the history tab showing water consumption data"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Placeholder for history chart
        chart_placeholder = QLabel("Water Consumption Chart Placeholder")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("background-color: #f0f0f0; padding: 40px; margin: 10px;")
        layout.addWidget(chart_placeholder)
        
        # Period selection
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Period:"))
        
        period_combo = QComboBox()
        period_combo.addItems(["Today", "Last 7 Days", "Last 30 Days", "Custom"])
        period_layout.addWidget(period_combo)
        period_layout.addStretch()
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._on_refresh_clicked)
        period_layout.addWidget(refresh_button)
        
        layout.addLayout(period_layout)
        
        # Cats to include
        cats_layout = QHBoxLayout()
        cats_layout.addWidget(QLabel("Cats to include:"))
        
        # In a real implementation, this would be populated from the database
        # and would use checkboxes for multiple selection
        cats_combo = QComboBox()
        cats_combo.addItem("All Cats")
        cats_combo.addItem("Whiskers")
        cats_combo.addItem("Mittens")
        cats_layout.addWidget(cats_combo, 1)
        
        layout.addLayout(cats_layout)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout(stats_group)
        
        stats_layout.addRow("Daily Average:", QLabel("120 ml"))
        stats_layout.addRow("Peak Time:", QLabel("Morning (6-9 AM)"))
        stats_layout.addRow("Monthly Trend:", QLabel("↑ 5% increase"))
        
        layout.addWidget(stats_group)
        layout.addStretch()
        
        return tab
    
    # Event handlers (non-functional placeholders)
    def _on_refill_clicked(self):
        QMessageBox.information(self, "Water Dispenser", 
                               "Water refill function will be implemented in the next sprint.")
    
    def _on_dispense_clicked(self):
        QMessageBox.information(self, "Water Dispenser", 
                               "Manual water dispensing will be implemented in the next sprint.")
    
    def _on_replace_filter_clicked(self):
        QMessageBox.information(self, "Water Dispenser", 
                               "Filter replacement tracking will be implemented in the next sprint.")
    
    def _on_apply_settings_clicked(self):
        QMessageBox.information(self, "Water Dispenser", 
                               "Settings saved (placeholder - will be functional in the next sprint).")
    
    def _on_refresh_clicked(self):
        QMessageBox.information(self, "Water Dispenser", 
                               "Data refresh and visualization will be implemented in the next sprint.")
    
    @Slot(int)
    def set_selected_cat(self, cat_id):
        """Set the selected cat ID from external signal"""
        self.selected_cat_id = cat_id
    
    @Slot()
    def refresh_water_inventory(self):
        """Refresh water inventory data (will be implemented in Sprint 3)"""
        pass 