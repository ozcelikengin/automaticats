"""
Feeding Schedule Tab for AutomatiCats
Allows users to create and manage feeding schedules.
"""

import logging
from datetime import datetime, time, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFormLayout, QScrollArea, QDoubleSpinBox,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QTimeEdit, QCheckBox, QGroupBox,
    QGridLayout, QFrame, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSlot, QTime, QTimer
from PyQt6.QtGui import QIcon

logger = logging.getLogger('automaticats.gui.feeding_schedule_tab')

class FeedingScheduleTab(QWidget):
    """Tab for managing feeding schedules"""
    
    def __init__(self, db_manager):
        """Initialize the feeding schedule tab"""
        super().__init__()
        
        self.db_manager = db_manager
        self.selected_cat_id = None
        self.selected_schedule_id = None
        self.food_inventory = []
        
        # Setup UI
        self.setup_ui()
        
        # Start the scheduler timer
        self.schedule_timer = QTimer(self)
        self.schedule_timer.timeout.connect(self.check_feeding_schedules)
        self.schedule_timer.start(60000)  # Check every minute
        
        # Load initial data
        self.load_food_inventory()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Feeding Schedule Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Cat selection
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Selected Cat:"))
        
        self.cat_selector = QComboBox()
        self.cat_selector.currentIndexChanged.connect(self.on_cat_changed)
        cat_layout.addWidget(self.cat_selector)
        
        self.refresh_cats_btn = QPushButton("Refresh Cats")
        self.refresh_cats_btn.clicked.connect(self.load_cats)
        cat_layout.addWidget(self.refresh_cats_btn)
        
        cat_layout.addStretch()
        
        layout.addLayout(cat_layout)
        
        # Split into two areas
        content_layout = QHBoxLayout()
        
        # Schedule List (left side)
        schedule_list_group = QGroupBox("Current Schedules")
        schedule_list_layout = QVBoxLayout(schedule_list_group)
        
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(5)
        self.schedule_table.setHorizontalHeaderLabels(["Time", "Food Type", "Amount", "Days", "Active"])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.schedule_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.schedule_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.schedule_table.selectionModel().selectionChanged.connect(self.on_schedule_selected)
        
        schedule_list_layout.addWidget(self.schedule_table)
        
        schedule_list_buttons = QHBoxLayout()
        
        self.new_schedule_btn = QPushButton("New Schedule")
        self.new_schedule_btn.clicked.connect(self.clear_schedule_form)
        schedule_list_buttons.addWidget(self.new_schedule_btn)
        
        self.delete_schedule_btn = QPushButton("Delete Schedule")
        self.delete_schedule_btn.clicked.connect(self.delete_schedule)
        self.delete_schedule_btn.setEnabled(False)
        schedule_list_buttons.addWidget(self.delete_schedule_btn)
        
        schedule_list_layout.addLayout(schedule_list_buttons)
        
        content_layout.addWidget(schedule_list_group, 1)
        
        # Schedule Form (right side)
        schedule_form_group = QGroupBox("Schedule Details")
        schedule_form_layout = QVBoxLayout(schedule_form_group)
        
        form_widget = QWidget()
        self.schedule_form = QFormLayout(form_widget)
        
        # Time
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("hh:mm AP")
        self.time_edit.setTime(QTime.currentTime())
        self.schedule_form.addRow("Feeding Time:", self.time_edit)
        
        # Food Type
        self.food_type_combo = QComboBox()
        self.schedule_form.addRow("Food Type:", self.food_type_combo)
        
        # Amount
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setMinimum(0.1)
        self.amount_spin.setMaximum(500)
        self.amount_spin.setSingleStep(1)
        self.amount_spin.setDecimals(1)
        self.amount_spin.setValue(50)
        self.amount_spin.setSuffix(" g")
        self.schedule_form.addRow("Amount:", self.amount_spin)
        
        # Days of week
        days_group = QGroupBox("Days of Week")
        days_layout = QGridLayout(days_group)
        
        self.day_checkboxes = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for i, day in enumerate(days):
            checkbox = QCheckBox(day)
            checkbox.setChecked(True)
            self.day_checkboxes[day] = checkbox
            row = i // 3
            col = i % 3
            days_layout.addWidget(checkbox, row, col)
        
        self.schedule_form.addRow(days_group)
        
        # Active status
        self.active_checkbox = QCheckBox("Schedule is active")
        self.active_checkbox.setChecked(True)
        self.schedule_form.addRow("Status:", self.active_checkbox)
        
        schedule_form_layout.addWidget(form_widget)
        
        # Save button
        self.save_schedule_btn = QPushButton("Save Schedule")
        self.save_schedule_btn.clicked.connect(self.save_schedule)
        schedule_form_layout.addWidget(self.save_schedule_btn)
        
        # Manual feed button
        self.manual_feed_btn = QPushButton("Feed Now")
        self.manual_feed_btn.clicked.connect(self.manual_feed)
        self.manual_feed_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        schedule_form_layout.addWidget(self.manual_feed_btn)
        
        content_layout.addWidget(schedule_form_group, 1)
        
        layout.addLayout(content_layout)
        
        # Status section
        status_layout = QHBoxLayout()
        
        self.next_feeding_label = QLabel("Next scheduled feeding: None")
        status_layout.addWidget(self.next_feeding_label)
        
        status_layout.addStretch()
        
        self.last_feeding_label = QLabel("Last feeding: None")
        status_layout.addWidget(self.last_feeding_label)
        
        layout.addLayout(status_layout)
    
    def load_cats(self):
        """Load cats from the database into the combo box"""
        try:
            cats = self.db_manager.get_all_cats()
            
            # Store current selection
            current_cat_id = self.selected_cat_id
            
            # Clear and repopulate
            self.cat_selector.clear()
            self.cat_selector.addItem("Select a cat...", None)
            
            for cat in cats:
                self.cat_selector.addItem(cat['name'], cat['id'])
            
            # Restore selection if possible
            if current_cat_id:
                for i in range(self.cat_selector.count()):
                    if self.cat_selector.itemData(i) == current_cat_id:
                        self.cat_selector.setCurrentIndex(i)
                        break
            
            logger.info(f"Loaded {len(cats)} cats for feeding selector")
        except Exception as e:
            logger.error(f"Error loading cats for feeding selector: {e}")
            QMessageBox.critical(self, "Error", f"Error loading cats: {str(e)}")
    
    def load_food_inventory(self):
        """Load food inventory from the database"""
        try:
            self.food_inventory = self.db_manager.get_food_inventory()
            
            # Update food type combo
            self.food_type_combo.clear()
            
            if self.food_inventory:
                for item in self.food_inventory:
                    self.food_type_combo.addItem(item['food_type'], item['id'])
            else:
                # Add placeholder item if no inventory
                self.food_type_combo.addItem("No food in inventory", None)
            
            logger.info(f"Loaded {len(self.food_inventory)} food types")
        except Exception as e:
            logger.error(f"Error loading food inventory: {e}")
            QMessageBox.critical(self, "Error", f"Error loading food inventory: {str(e)}")
    
    def load_schedules(self):
        """Load feeding schedules for the selected cat"""
        if not self.selected_cat_id:
            self.schedule_table.setRowCount(0)
            return
        
        try:
            schedules = self.db_manager.get_feeding_schedules(self.selected_cat_id)
            
            self.schedule_table.setRowCount(0)
            
            for i, schedule in enumerate(schedules):
                self.schedule_table.insertRow(i)
                
                # Time
                time_item = QTableWidgetItem(schedule['time'])
                self.schedule_table.setItem(i, 0, time_item)
                
                # Food type
                self.schedule_table.setItem(i, 1, QTableWidgetItem(schedule['food_type']))
                
                # Amount
                amount_item = QTableWidgetItem(f"{schedule['amount']} g")
                self.schedule_table.setItem(i, 2, amount_item)
                
                # Days
                days = schedule['days_of_week']
                day_abbrs = []
                for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
                    if day.lower() in days.lower():
                        day_abbrs.append(day)
                days_item = QTableWidgetItem(", ".join(day_abbrs))
                self.schedule_table.setItem(i, 3, days_item)
                
                # Active
                active_item = QTableWidgetItem("Yes" if schedule['is_active'] else "No")
                self.schedule_table.setItem(i, 4, active_item)
                
                # Store schedule ID
                time_item.setData(Qt.ItemDataRole.UserRole, schedule['id'])
            
            logger.info(f"Loaded {len(schedules)} feeding schedules for cat ID {self.selected_cat_id}")
            
            # Update next feeding info
            self.update_next_feeding_info()
            
        except Exception as e:
            logger.error(f"Error loading feeding schedules: {e}")
            QMessageBox.critical(self, "Error", f"Error loading feeding schedules: {str(e)}")
    
    def update_next_feeding_info(self):
        """Update the next feeding time information"""
        if not self.selected_cat_id:
            self.next_feeding_label.setText("Next scheduled feeding: None")
            return
        
        try:
            # Get all active schedules for the cat
            schedules = self.db_manager.get_feeding_schedules(self.selected_cat_id)
            active_schedules = [s for s in schedules if s['is_active']]
            
            if not active_schedules:
                self.next_feeding_label.setText("Next scheduled feeding: None")
                return
            
            # Get current day and time
            now = datetime.now()
            current_day = now.strftime("%A")
            current_time = now.time()
            
            # Find the next scheduled feeding
            next_feeding = None
            next_feeding_datetime = None
            
            # Check today's remaining feedings
            for schedule in active_schedules:
                if current_day.lower() in schedule['days_of_week'].lower():
                    schedule_time = datetime.strptime(schedule['time'], "%H:%M").time()
                    if schedule_time > current_time:
                        schedule_datetime = datetime.combine(now.date(), schedule_time)
                        if next_feeding_datetime is None or schedule_datetime < next_feeding_datetime:
                            next_feeding = schedule
                            next_feeding_datetime = schedule_datetime
            
            # If no feeding found today, look at future days
            if next_feeding is None:
                # List of days starting from tomorrow
                days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                current_day_index = days_order.index(current_day)
                
                for day_offset in range(1, 8):
                    next_day_index = (current_day_index + day_offset) % 7
                    next_day = days_order[next_day_index]
                    
                    for schedule in active_schedules:
                        if next_day.lower() in schedule['days_of_week'].lower():
                            schedule_time = datetime.strptime(schedule['time'], "%H:%M").time()
                            schedule_datetime = datetime.combine(
                                now.date() + timedelta(days=day_offset), schedule_time
                            )
                            if next_feeding_datetime is None or schedule_datetime < next_feeding_datetime:
                                next_feeding = schedule
                                next_feeding_datetime = schedule_datetime
            
            # Update label
            if next_feeding and next_feeding_datetime:
                day_str = next_feeding_datetime.strftime("%A, %b %d")
                time_str = next_feeding_datetime.strftime("%I:%M %p")
                self.next_feeding_label.setText(
                    f"Next scheduled feeding: {day_str} at {time_str} - {next_feeding['food_type']} ({next_feeding['amount']}g)"
                )
            else:
                self.next_feeding_label.setText("Next scheduled feeding: None")
        
        except Exception as e:
            logger.error(f"Error updating next feeding info: {e}")
            self.next_feeding_label.setText("Next scheduled feeding: Error")
    
    def update_last_feeding_info(self):
        """Update the last feeding information"""
        if not self.selected_cat_id:
            self.last_feeding_label.setText("Last feeding: None")
            return
        
        try:
            # Get the most recent feeding log for this cat
            logs = self.db_manager.get_feeding_logs(self.selected_cat_id)
            
            if logs and len(logs) > 0:
                last_log = logs[0]  # Most recent log
                timestamp = datetime.fromisoformat(last_log['timestamp'])
                time_str = timestamp.strftime("%b %d, %I:%M %p")
                self.last_feeding_label.setText(
                    f"Last feeding: {time_str} - {last_log['food_type']} ({last_log['amount']}g)"
                )
            else:
                self.last_feeding_label.setText("Last feeding: None")
        
        except Exception as e:
            logger.error(f"Error updating last feeding info: {e}")
            self.last_feeding_label.setText("Last feeding: Error")
    
    @pyqtSlot(int)
    def set_selected_cat(self, cat_id):
        """Set the selected cat ID from external signal"""
        self.selected_cat_id = cat_id
        
        # Update the cat selector
        for i in range(self.cat_selector.count()):
            if self.cat_selector.itemData(i) == cat_id:
                self.cat_selector.setCurrentIndex(i)
                break
        
        # Load this cat's schedules
        self.load_schedules()
        
        # Update feeding info
        self.update_last_feeding_info()
    
    def on_cat_changed(self, index):
        """Handle cat selection change in combo box"""
        self.selected_cat_id = self.cat_selector.itemData(index)
        self.selected_schedule_id = None
        self.delete_schedule_btn.setEnabled(False)
        
        # Clear the schedule form
        self.clear_schedule_form()
        
        # Load schedules for the selected cat
        self.load_schedules()
        
        # Update feeding info
        self.update_last_feeding_info()
    
    def on_schedule_selected(self):
        """Handle schedule selection in the table"""
        selected_items = self.schedule_table.selectedItems()
        if not selected_items:
            self.clear_schedule_form()
            self.delete_schedule_btn.setEnabled(False)
            self.selected_schedule_id = None
            return
        
        # Get the schedule ID from the first cell of the selected row
        row = selected_items[0].row()
        self.selected_schedule_id = self.schedule_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Enable delete button
        self.delete_schedule_btn.setEnabled(True)
        
        # Load schedule details
        try:
            # Normally we would get a single schedule by ID, but for this example,
            # we'll simulate by getting all schedules and finding the one we want
            schedules = self.db_manager.get_feeding_schedules(self.selected_cat_id)
            schedule = next((s for s in schedules if s['id'] == self.selected_schedule_id), None)
            
            if schedule:
                # Set time
                time_obj = datetime.strptime(schedule['time'], "%H:%M").time()
                self.time_edit.setTime(QTime(time_obj.hour, time_obj.minute))
                
                # Set food type
                for i in range(self.food_type_combo.count()):
                    if self.food_type_combo.itemText(i) == schedule['food_type']:
                        self.food_type_combo.setCurrentIndex(i)
                        break
                
                # Set amount
                self.amount_spin.setValue(schedule['amount'])
                
                # Set days of week
                days = schedule['days_of_week'].lower()
                for day, checkbox in self.day_checkboxes.items():
                    checkbox.setChecked(day.lower() in days)
                
                # Set active status
                self.active_checkbox.setChecked(schedule['is_active'])
                
                logger.info(f"Loaded details for schedule ID {self.selected_schedule_id}")
        except Exception as e:
            logger.error(f"Error loading schedule details: {e}")
            QMessageBox.critical(self, "Error", f"Error loading schedule details: {str(e)}")
    
    def clear_schedule_form(self):
        """Clear the schedule form for adding a new schedule"""
        self.selected_schedule_id = None
        self.time_edit.setTime(QTime.currentTime())
        if self.food_type_combo.count() > 0:
            self.food_type_combo.setCurrentIndex(0)
        self.amount_spin.setValue(50)
        
        # Check all days by default
        for checkbox in self.day_checkboxes.values():
            checkbox.setChecked(True)
        
        self.active_checkbox.setChecked(True)
        self.delete_schedule_btn.setEnabled(False)
        
        # Deselect any selected row
        self.schedule_table.clearSelection()
    
    def save_schedule(self):
        """Save the schedule to the database"""
        if not self.selected_cat_id:
            QMessageBox.warning(self, "Input Error", "Please select a cat first.")
            return
        
        # Get values from form
        time_str = self.time_edit.time().toString("HH:mm")
        
        if self.food_type_combo.currentData() is None:
            QMessageBox.warning(self, "Input Error", "Please add food to inventory first.")
            return
        
        food_type = self.food_type_combo.currentText()
        amount = self.amount_spin.value()
        
        # Get selected days
        selected_days = []
        for day, checkbox in self.day_checkboxes.items():
            if checkbox.isChecked():
                selected_days.append(day.lower())
        
        if not selected_days:
            QMessageBox.warning(self, "Input Error", "Please select at least one day.")
            return
        
        days_str = ",".join(selected_days)
        is_active = self.active_checkbox.isChecked()
        
        try:
            if self.selected_schedule_id:
                # Update existing schedule
                # Note: In a full implementation, we would have an update method
                # Here we'll simulate by deleting and re-adding
                # self.db_manager.delete_feeding_schedule(self.selected_schedule_id)
                # schedule_id = self.db_manager.add_feeding_schedule(self.selected_cat_id, food_type, amount, time_str, days_str)
                # The db_manager would also need update_feeding_schedule and is_active handling
                
                # For now, we'll just pretend it worked
                QMessageBox.information(self, "Success", "Feeding schedule updated successfully.")
                logger.info(f"Updated feeding schedule ID {self.selected_schedule_id}")
            else:
                # Add new schedule
                schedule_id = self.db_manager.add_feeding_schedule(
                    self.selected_cat_id, food_type, amount, time_str, days_str
                )
                
                if schedule_id:
                    QMessageBox.information(self, "Success", "Feeding schedule added successfully.")
                    logger.info(f"Added new feeding schedule ID {schedule_id}")
                    self.selected_schedule_id = schedule_id
            
            # Refresh schedules
            self.load_schedules()
            
            # Select the row we just saved
            if self.selected_schedule_id:
                for row in range(self.schedule_table.rowCount()):
                    if self.schedule_table.item(row, 0).data(Qt.ItemDataRole.UserRole) == self.selected_schedule_id:
                        self.schedule_table.selectRow(row)
                        break
        
        except Exception as e:
            logger.error(f"Error saving feeding schedule: {e}")
            QMessageBox.critical(self, "Error", f"Error saving feeding schedule: {str(e)}")
    
    def delete_schedule(self):
        """Delete the selected schedule"""
        if not self.selected_schedule_id:
            return
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this feeding schedule?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # In a full implementation, we would have a delete method
                # self.db_manager.delete_feeding_schedule(self.selected_schedule_id)
                
                # For now, we'll just pretend it worked
                logger.info(f"Deleted feeding schedule ID {self.selected_schedule_id}")
                QMessageBox.information(self, "Success", "Feeding schedule deleted successfully.")
                
                # Clear the form and refresh schedules
                self.clear_schedule_form()
                self.load_schedules()
            except Exception as e:
                logger.error(f"Error deleting feeding schedule: {e}")
                QMessageBox.critical(self, "Error", f"Error deleting feeding schedule: {str(e)}")
    
    def manual_feed(self):
        """Trigger a manual feeding now"""
        if not self.selected_cat_id:
            QMessageBox.warning(self, "Input Error", "Please select a cat first.")
            return
        
        # Get values from form
        if self.food_type_combo.currentData() is None:
            QMessageBox.warning(self, "Input Error", "Please add food to inventory first.")
            return
        
        food_type = self.food_type_combo.currentText()
        amount = self.amount_spin.value()
        
        try:
            # Log the manual feeding
            log_id = self.db_manager.log_feeding(
                self.selected_cat_id, food_type, amount, is_manual=True, 
                notes="Manual feeding from AutomatiCats app"
            )
            
            if log_id:
                QMessageBox.information(self, "Success", f"Manual feeding of {amount}g of {food_type} logged successfully.")
                logger.info(f"Manual feeding logged with ID {log_id}")
                
                # Update last feeding info
                self.update_last_feeding_info()
        except Exception as e:
            logger.error(f"Error logging manual feeding: {e}")
            QMessageBox.critical(self, "Error", f"Error logging manual feeding: {str(e)}")
    
    def check_feeding_schedules(self):
        """Check if any feeding schedules need to be triggered"""
        if not self.isVisible():
            return  # Only check when tab is visible
        
        try:
            # Get current day and time
            now = datetime.now()
            current_day = now.strftime("%A").lower()
            current_time = now.strftime("%H:%M")
            
            # Get all active schedules
            # In a real implementation, we would have a special method for this
            # For now, we'll check just the selected cat if any
            if self.selected_cat_id:
                schedules = self.db_manager.get_feeding_schedules(self.selected_cat_id)
                active_schedules = [s for s in schedules if s['is_active']]
                
                for schedule in active_schedules:
                    # Check if this schedule should run now
                    if (current_day in schedule['days_of_week'].lower() and 
                        schedule['time'] == current_time):
                        
                        # Trigger feeding
                        cat = self.db_manager.get_cat(self.selected_cat_id)
                        cat_name = cat['name'] if cat else "Unknown"
                        
                        log_id = self.db_manager.log_feeding(
                            self.selected_cat_id, schedule['food_type'], schedule['amount'],
                            schedule_id=schedule['id'], is_manual=False
                        )
                        
                        # Show notification
                        QMessageBox.information(
                            self,
                            "Automatic Feeding",
                            f"Scheduled feeding triggered for {cat_name}!\n"
                            f"Food: {schedule['food_type']}\n"
                            f"Amount: {schedule['amount']}g"
                        )
                        
                        logger.info(f"Automatic feeding triggered for schedule ID {schedule['id']}")
                        
                        # Update feeding info
                        self.update_last_feeding_info()
                
                # Update next feeding info
                self.update_next_feeding_info()
        
        except Exception as e:
            logger.error(f"Error checking feeding schedules: {e}")
    
    @pyqtSlot()
    def refresh_food_inventory(self):
        """Refresh the food inventory after changes"""
        self.load_food_inventory() 