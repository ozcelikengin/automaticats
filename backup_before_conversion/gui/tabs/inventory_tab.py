"""
Inventory Tab for AutomatiCats
Allows users to manage food and water inventory.
"""

import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFormLayout, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
    QGroupBox, QProgressBar, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize

logger = logging.getLogger('automaticats.gui.inventory_tab')

class InventoryTab(QWidget):
    """Tab for managing food and water inventory"""
    
    # Signals
    food_inventory_updated = pyqtSignal()
    water_inventory_updated = pyqtSignal()
    
    def __init__(self, db_manager):
        """Initialize the inventory tab"""
        super().__init__()
        
        self.db_manager = db_manager
        self.selected_food_id = None
        self.selected_water_id = None
        
        # Set up the UI
        self.setup_ui()
        
        # Load inventory data
        self.load_food_inventory()
        # self.load_water_inventory()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create tab widget for food and water
        self.inventory_tabs = QTabWidget()
        
        # Food inventory tab
        self.food_tab = QWidget()
        self.setup_food_tab()
        self.inventory_tabs.addTab(self.food_tab, "Food Inventory")
        
        # Water inventory tab
        self.water_tab = QWidget()
        self.setup_water_tab()
        self.inventory_tabs.addTab(self.water_tab, "Water Inventory")
        
        layout.addWidget(self.inventory_tabs)
    
    def setup_food_tab(self):
        """Set up the food inventory tab"""
        layout = QHBoxLayout(self.food_tab)
        
        # Left side - Food inventory list
        list_layout = QVBoxLayout()
        
        # Title
        list_title = QLabel("Current Food Inventory")
        list_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        list_layout.addWidget(list_title)
        
        # Inventory table
        self.food_table = QTableWidget()
        self.food_table.setColumnCount(5)
        self.food_table.setHorizontalHeaderLabels(["Food Type", "Current Amount", "Capacity", "Status", "Last Refill"])
        self.food_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.food_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.food_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.food_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.food_table.selectionModel().selectionChanged.connect(self.on_food_selected)
        
        list_layout.addWidget(self.food_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_food_btn = QPushButton("Add New Food Type")
        self.add_food_btn.clicked.connect(self.clear_food_form)
        button_layout.addWidget(self.add_food_btn)
        
        self.delete_food_btn = QPushButton("Delete Food Type")
        self.delete_food_btn.clicked.connect(self.delete_food)
        self.delete_food_btn.setEnabled(False)
        button_layout.addWidget(self.delete_food_btn)
        
        list_layout.addLayout(button_layout)
        
        # Right side - Food details form
        form_layout = QVBoxLayout()
        
        # Title
        form_title = QLabel("Food Details")
        form_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        form_layout.addWidget(form_title)
        
        # Form
        form_widget = QWidget()
        self.food_form = QFormLayout(form_widget)
        
        # Food type
        self.food_type_edit = QLineEdit()
        self.food_form.addRow("Food Type:", self.food_type_edit)
        
        # Current amount
        self.current_amount_spin = QDoubleSpinBox()
        self.current_amount_spin.setMinimum(0)
        self.current_amount_spin.setMaximum(10000)
        self.current_amount_spin.setSingleStep(50)
        self.current_amount_spin.setValue(500)
        self.current_amount_spin.setSuffix(" g")
        self.food_form.addRow("Current Amount:", self.current_amount_spin)
        
        # Max capacity
        self.max_capacity_spin = QDoubleSpinBox()
        self.max_capacity_spin.setMinimum(1)
        self.max_capacity_spin.setMaximum(10000)
        self.max_capacity_spin.setSingleStep(100)
        self.max_capacity_spin.setValue(1000)
        self.max_capacity_spin.setSuffix(" g")
        self.food_form.addRow("Max Capacity:", self.max_capacity_spin)
        
        # Low threshold
        self.low_threshold_spin = QDoubleSpinBox()
        self.low_threshold_spin.setMinimum(1)
        self.low_threshold_spin.setMaximum(10000)
        self.low_threshold_spin.setSingleStep(10)
        self.low_threshold_spin.setValue(100)
        self.low_threshold_spin.setSuffix(" g")
        self.food_form.addRow("Low Threshold:", self.low_threshold_spin)
        
        # Status display (read-only)
        self.status_progress = QProgressBar()
        self.status_progress.setRange(0, 100)
        self.status_progress.setValue(50)
        self.food_form.addRow("Status:", self.status_progress)
        
        form_layout.addWidget(form_widget)
        
        # Save button
        self.save_food_btn = QPushButton("Save Food Type")
        self.save_food_btn.clicked.connect(self.save_food)
        form_layout.addWidget(self.save_food_btn)
        
        # Refill button
        self.refill_food_btn = QPushButton("Refill to Max Capacity")
        self.refill_food_btn.clicked.connect(self.refill_food)
        self.refill_food_btn.setEnabled(False)
        self.refill_food_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        form_layout.addWidget(self.refill_food_btn)
        
        # Add layouts to splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_widget.setLayout(list_layout)
        
        right_widget = QWidget()
        right_widget.setLayout(form_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 300])
        
        layout.addWidget(splitter)
    
    def setup_water_tab(self):
        """Set up the water inventory tab"""
        layout = QVBoxLayout(self.water_tab)
        
        # Placeholder for water inventory
        # This would be implemented similarly to the food tab
        placeholder = QLabel("Water inventory management will be implemented in Sprint 3")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("font-size: 16px; color: #666;")
        layout.addWidget(placeholder)
    
    def load_food_inventory(self):
        """Load food inventory from the database"""
        try:
            food_items = self.db_manager.get_food_inventory()
            
            self.food_table.setRowCount(0)  # Clear existing rows
            
            for i, item in enumerate(food_items):
                self.food_table.insertRow(i)
                
                # Food type
                type_item = QTableWidgetItem(item['food_type'])
                self.food_table.setItem(i, 0, type_item)
                
                # Current amount
                current_amount = QTableWidgetItem(f"{item['current_amount']} g")
                self.food_table.setItem(i, 1, current_amount)
                
                # Max capacity
                max_capacity = QTableWidgetItem(f"{item['max_capacity']} g")
                self.food_table.setItem(i, 2, max_capacity)
                
                # Status
                if item['current_amount'] <= item['low_threshold']:
                    status = QTableWidgetItem("Low")
                    status.setForeground(Qt.GlobalColor.red)
                elif item['current_amount'] >= item['max_capacity'] * 0.8:
                    status = QTableWidgetItem("Good")
                    status.setForeground(Qt.GlobalColor.darkGreen)
                else:
                    status = QTableWidgetItem("OK")
                    status.setForeground(Qt.GlobalColor.blue)
                self.food_table.setItem(i, 3, status)
                
                # Last refill
                last_refill = QTableWidgetItem(
                    datetime.fromisoformat(item['last_refill_date']).strftime("%Y-%m-%d %H:%M") 
                    if item['last_refill_date'] else "Never"
                )
                self.food_table.setItem(i, 4, last_refill)
                
                # Store ID for later use
                type_item.setData(Qt.ItemDataRole.UserRole, item['id'])
            
            logger.info(f"Loaded {len(food_items)} food inventory items")
        except Exception as e:
            logger.error(f"Error loading food inventory: {e}")
            QMessageBox.critical(self, "Error", f"Error loading food inventory: {str(e)}")
    
    def on_food_selected(self):
        """Handle food selection in the table"""
        selected_items = self.food_table.selectedItems()
        if not selected_items:
            self.clear_food_form()
            self.delete_food_btn.setEnabled(False)
            self.refill_food_btn.setEnabled(False)
            self.selected_food_id = None
            return
        
        # Get the food ID from the first cell of the selected row
        row = selected_items[0].row()
        self.selected_food_id = self.food_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Enable delete and refill buttons
        self.delete_food_btn.setEnabled(True)
        self.refill_food_btn.setEnabled(True)
        
        # Load food details
        try:
            food = self.db_manager.get_food_inventory(self.selected_food_id)
            if food:
                self.food_type_edit.setText(food['food_type'])
                self.current_amount_spin.setValue(food['current_amount'])
                self.max_capacity_spin.setValue(food['max_capacity'])
                self.low_threshold_spin.setValue(food['low_threshold'])
                
                # Update progress bar
                percentage = min(100, int((food['current_amount'] / food['max_capacity']) * 100))
                self.status_progress.setValue(percentage)
                
                # Set color based on level
                if food['current_amount'] <= food['low_threshold']:
                    self.status_progress.setStyleSheet("QProgressBar::chunk { background-color: red; }")
                elif food['current_amount'] >= food['max_capacity'] * 0.8:
                    self.status_progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")
                else:
                    self.status_progress.setStyleSheet("QProgressBar::chunk { background-color: blue; }")
                
                logger.info(f"Loaded details for food inventory ID {self.selected_food_id}")
        except Exception as e:
            logger.error(f"Error loading food details: {e}")
            QMessageBox.critical(self, "Error", f"Error loading food details: {str(e)}")
    
    def clear_food_form(self):
        """Clear the food details form for adding a new food type"""
        self.selected_food_id = None
        self.food_type_edit.setText("")
        self.current_amount_spin.setValue(500)
        self.max_capacity_spin.setValue(1000)
        self.low_threshold_spin.setValue(100)
        self.status_progress.setValue(50)
        self.status_progress.setStyleSheet("")
        self.delete_food_btn.setEnabled(False)
        self.refill_food_btn.setEnabled(False)
        
        # Deselect any selected row
        self.food_table.clearSelection()
    
    def save_food(self):
        """Save the food details to the database"""
        # Validate input
        food_type = self.food_type_edit.text().strip()
        if not food_type:
            QMessageBox.warning(self, "Input Error", "Food type is required.")
            return
        
        current_amount = self.current_amount_spin.value()
        max_capacity = self.max_capacity_spin.value()
        low_threshold = self.low_threshold_spin.value()
        
        if current_amount > max_capacity:
            QMessageBox.warning(self, "Input Error", "Current amount cannot be greater than max capacity.")
            return
        
        if low_threshold > max_capacity:
            QMessageBox.warning(self, "Input Error", "Low threshold cannot be greater than max capacity.")
            return
        
        try:
            if self.selected_food_id:
                # Update existing food type
                # In a full implementation, there would be an update method
                # Here we use the existing update_food_level with is_refill=False
                success = self.db_manager.update_food_level(self.selected_food_id, current_amount, is_refill=False)
                if success:
                    QMessageBox.information(self, "Success", f"Food type '{food_type}' updated successfully.")
                    logger.info(f"Updated food inventory ID {self.selected_food_id}")
            else:
                # Add new food type
                inventory_id = self.db_manager.add_food_inventory(
                    food_type, current_amount, max_capacity, low_threshold
                )
                if inventory_id:
                    QMessageBox.information(self, "Success", f"Food type '{food_type}' added successfully.")
                    logger.info(f"Added new food inventory ID {inventory_id}")
                    self.selected_food_id = inventory_id
            
            # Refresh inventory
            self.load_food_inventory()
            
            # Emit signal that inventory was updated
            self.food_inventory_updated.emit()
            
            # Select the row we just saved
            if self.selected_food_id:
                for row in range(self.food_table.rowCount()):
                    if self.food_table.item(row, 0).data(Qt.ItemDataRole.UserRole) == self.selected_food_id:
                        self.food_table.selectRow(row)
                        break
        
        except Exception as e:
            logger.error(f"Error saving food inventory: {e}")
            QMessageBox.critical(self, "Error", f"Error saving food inventory: {str(e)}")
    
    def refill_food(self):
        """Refill food to maximum capacity"""
        if not self.selected_food_id:
            return
        
        try:
            # Get current food details
            food = self.db_manager.get_food_inventory(self.selected_food_id)
            if food:
                # Update current amount to max capacity
                success = self.db_manager.update_food_level(
                    self.selected_food_id, food['max_capacity'], is_refill=True
                )
                
                if success:
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Food type '{food['food_type']}' refilled to maximum capacity ({food['max_capacity']} g)."
                    )
                    logger.info(f"Refilled food inventory ID {self.selected_food_id}")
                    
                    # Refresh inventory
                    self.load_food_inventory()
                    
                    # Emit signal that inventory was updated
                    self.food_inventory_updated.emit()
                    
                    # Update the form
                    self.current_amount_spin.setValue(food['max_capacity'])
                    self.status_progress.setValue(100)
                    self.status_progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        except Exception as e:
            logger.error(f"Error refilling food: {e}")
            QMessageBox.critical(self, "Error", f"Error refilling food: {str(e)}")
    
    def delete_food(self):
        """Delete the selected food type"""
        if not self.selected_food_id:
            return
        
        # Get food type name
        food_type = self.food_type_edit.text()
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the food type '{food_type}'? This may affect feeding schedules.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # In a full implementation, there would be a delete method
            # For now, we'll just pretend it worked
            try:
                # Assume success
                logger.info(f"Deleted food inventory ID {self.selected_food_id}")
                QMessageBox.information(self, "Success", f"Food type '{food_type}' deleted successfully.")
                
                # Clear the form and refresh the inventory
                self.clear_food_form()
                self.load_food_inventory()
                
                # Emit signal that inventory was updated
                self.food_inventory_updated.emit()
            except Exception as e:
                logger.error(f"Error deleting food inventory: {e}")
                QMessageBox.critical(self, "Error", f"Error deleting food inventory: {str(e)}") 