"""
Statistics Tab for AutomatiCats
Provides analytics and charts for cat feeding and water consumption.
"""

import logging
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QDateEdit, QGroupBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot, QDate

logger = logging.getLogger('automaticats.gui.statistics_tab')

class StatisticsTab(QWidget):
    """Tab for displaying statistics and analytics"""
    
    def __init__(self, db_manager):
        """Initialize the statistics tab"""
        super().__init__()
        
        self.db_manager = db_manager
        self.selected_cat_id = None
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Controls section
        controls_layout = QHBoxLayout()
        
        # Cat selector
        controls_layout.addWidget(QLabel("Cat:"))
        self.cat_selector = QComboBox()
        self.cat_selector.currentIndexChanged.connect(self.on_cat_changed)
        controls_layout.addWidget(self.cat_selector)
        
        # Date range selector
        controls_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        controls_layout.addWidget(self.start_date)
        
        controls_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        controls_layout.addWidget(self.end_date)
        
        # Apply filter button
        self.apply_filter_btn = QPushButton("Apply Filter")
        self.apply_filter_btn.clicked.connect(self.load_statistics)
        controls_layout.addWidget(self.apply_filter_btn)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Stats tabs
        self.stats_tabs = QTabWidget()
        
        # Feeding stats tab
        self.feeding_stats_tab = QWidget()
        self.setup_feeding_stats_tab()
        self.stats_tabs.addTab(self.feeding_stats_tab, "Feeding Statistics")
        
        # Water stats tab
        self.water_stats_tab = QWidget()
        self.setup_water_stats_tab()
        self.stats_tabs.addTab(self.water_stats_tab, "Water Statistics")
        
        layout.addWidget(self.stats_tabs)
        
        # Load cats
        self.load_cats()
    
    def setup_feeding_stats_tab(self):
        """Set up the feeding statistics tab"""
        layout = QVBoxLayout(self.feeding_stats_tab)
        
        # Summary section
        summary_group = QGroupBox("Feeding Summary")
        summary_layout = QHBoxLayout(summary_group)
        
        # Total food consumed
        self.total_food_label = QLabel("Total Food: 0g")
        self.total_food_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        summary_layout.addWidget(self.total_food_label)
        
        # Average daily consumption
        self.avg_daily_food_label = QLabel("Average Daily: 0g")
        self.avg_daily_food_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        summary_layout.addWidget(self.avg_daily_food_label)
        
        # Most common food type
        self.common_food_label = QLabel("Most Common Food: None")
        self.common_food_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        summary_layout.addWidget(self.common_food_label)
        
        layout.addWidget(summary_group)
        
        # Feeding logs table
        table_group = QGroupBox("Feeding Logs")
        table_layout = QVBoxLayout(table_group)
        
        self.feeding_table = QTableWidget()
        self.feeding_table.setColumnCount(5)
        self.feeding_table.setHorizontalHeaderLabels(["Date & Time", "Food Type", "Amount", "Schedule", "Notes"])
        self.feeding_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.feeding_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        table_layout.addWidget(self.feeding_table)
        
        layout.addWidget(table_group)
        
        # Placeholder for future charts
        chart_placeholder = QLabel("Charts and graphs will be implemented in Sprint 3")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("font-size: 14px; color: #666; margin: 20px;")
        layout.addWidget(chart_placeholder)
    
    def setup_water_stats_tab(self):
        """Set up the water statistics tab"""
        layout = QVBoxLayout(self.water_stats_tab)
        
        # Coming soon message
        coming_soon = QLabel("Water Statistics will be implemented in Sprint 3")
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coming_soon.setStyleSheet("font-size: 18px; color: #666; margin: 20px;")
        layout.addWidget(coming_soon)
        
        layout.addStretch()
    
    def load_cats(self):
        """Load cats from the database into the combo box"""
        try:
            cats = self.db_manager.get_all_cats()
            
            # Store current selection
            current_cat_id = self.selected_cat_id
            
            # Clear and repopulate
            self.cat_selector.clear()
            self.cat_selector.addItem("All Cats", None)
            
            for cat in cats:
                self.cat_selector.addItem(cat['name'], cat['id'])
            
            # Restore selection if possible
            if current_cat_id:
                for i in range(self.cat_selector.count()):
                    if self.cat_selector.itemData(i) == current_cat_id:
                        self.cat_selector.setCurrentIndex(i)
                        break
            
            logger.info(f"Loaded {len(cats)} cats for statistics selector")
        except Exception as e:
            logger.error(f"Error loading cats for statistics selector: {e}")
            QMessageBox.critical(self, "Error", f"Error loading cats: {str(e)}")
    
    def on_cat_changed(self, index):
        """Handle cat selection change in combo box"""
        self.selected_cat_id = self.cat_selector.itemData(index)
        self.load_statistics()
    
    @pyqtSlot(int)
    def set_selected_cat(self, cat_id):
        """Set the selected cat ID from external signal"""
        self.selected_cat_id = cat_id
        
        # Update the cat selector
        for i in range(self.cat_selector.count()):
            if self.cat_selector.itemData(i) == cat_id:
                self.cat_selector.setCurrentIndex(i)
                break
        
        # Load statistics
        self.load_statistics()
    
    def load_statistics(self):
        """Load statistics based on selected cat and date range"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Load feeding statistics
        self.load_feeding_statistics(start_date, end_date)
        
        # Future: Load water statistics
    
    def load_feeding_statistics(self, start_date, end_date):
        """Load feeding statistics for the selected cat and date range"""
        try:
            # Get feeding logs
            logs = self.db_manager.get_feeding_logs(self.selected_cat_id, start_date, end_date)
            
            # Update table
            self.feeding_table.setRowCount(0)
            
            total_food = 0
            food_types = {}
            
            for i, log in enumerate(logs):
                self.feeding_table.insertRow(i)
                
                # Date & Time
                timestamp = datetime.fromisoformat(log['timestamp'])
                time_str = timestamp.strftime("%Y-%m-%d %H:%M")
                self.feeding_table.setItem(i, 0, QTableWidgetItem(time_str))
                
                # Food Type
                food_type = log['food_type']
                self.feeding_table.setItem(i, 1, QTableWidgetItem(food_type))
                
                # Track food types for most common calculation
                if food_type in food_types:
                    food_types[food_type] += 1
                else:
                    food_types[food_type] = 1
                
                # Amount
                amount = log['amount']
                total_food += amount
                self.feeding_table.setItem(i, 2, QTableWidgetItem(f"{amount} g"))
                
                # Schedule
                is_manual = log['is_manual']
                self.feeding_table.setItem(i, 3, QTableWidgetItem("Manual" if is_manual else "Scheduled"))
                
                # Notes
                notes = log['notes'] if log['notes'] else ""
                self.feeding_table.setItem(i, 4, QTableWidgetItem(notes))
            
            # Update summary
            self.total_food_label.setText(f"Total Food: {total_food}g")
            
            # Calculate days in range for average
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end - start).days + 1
            avg_daily = total_food / max(1, days)
            
            self.avg_daily_food_label.setText(f"Average Daily: {avg_daily:.1f}g")
            
            # Find most common food type
            most_common_food = max(food_types.items(), key=lambda x: x[1])[0] if food_types else "None"
            self.common_food_label.setText(f"Most Common Food: {most_common_food}")
            
            logger.info(f"Loaded {len(logs)} feeding logs for statistics")
        except Exception as e:
            logger.error(f"Error loading feeding statistics: {e}")
            QMessageBox.critical(self, "Error", f"Error loading feeding statistics: {str(e)}") 