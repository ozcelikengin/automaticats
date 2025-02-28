"""
Cat Management Tab for AutomatiCats
Allows users to add, edit, and delete cats.
"""

import os
import logging
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFormLayout, QScrollArea, QDoubleSpinBox,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QFrame, QGridLayout, QSplitter
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon

logger = logging.getLogger('automaticats.gui.cat_management_tab')

class CatManagementTab(QWidget):
    """Tab for managing cats in the system"""
    
    # Signals
    cat_selected = Signal(int)  # Signal emitted when a cat is selected (passes cat_id)
    
    def __init__(self, db_manager):
        """Initialize the cat management tab"""
        super().__init__()
        
        self.db_manager = db_manager
        self.selected_cat_id = None
        self.photo_path = None
        
        # Set up the UI
        self.setup_ui()
        
        # Load cats from database
        self.load_cats()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        layout = QHBoxLayout(self)
        
        # Left side - Cat list
        cat_list_layout = QVBoxLayout()
        
        # Title
        cat_list_title = QLabel("Your Cats")
        cat_list_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        cat_list_layout.addWidget(cat_list_title)
        
        # Cat list table
        self.cat_table = QTableWidget()
        self.cat_table.setColumnCount(3)
        self.cat_table.setHorizontalHeaderLabels(["Name", "Age", "Weight"])
        self.cat_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.cat_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cat_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.cat_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cat_table.selectionModel().selectionChanged.connect(self.on_cat_selected)
        
        cat_list_layout.addWidget(self.cat_table)
        
        # Buttons for cat list
        button_layout = QHBoxLayout()
        
        self.add_cat_btn = QPushButton("Add Cat")
        self.add_cat_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.add_cat_btn)
        
        self.delete_cat_btn = QPushButton("Delete Cat")
        self.delete_cat_btn.clicked.connect(self.delete_cat)
        self.delete_cat_btn.setEnabled(False)
        button_layout.addWidget(self.delete_cat_btn)
        
        cat_list_layout.addLayout(button_layout)
        
        # Right side - Cat details form
        form_layout = QVBoxLayout()
        
        # Title
        form_title = QLabel("Cat Details")
        form_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        form_layout.addWidget(form_title)
        
        # Form container
        form_container = QWidget()
        self.detail_form = QFormLayout(form_container)
        
        # Cat photo
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(150, 150)
        self.photo_label.setFrameShape(QFrame.Shape.Box)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setText("No Photo")
        
        photo_layout.addWidget(self.photo_label)
        
        photo_btn_layout = QVBoxLayout()
        self.upload_photo_btn = QPushButton("Upload Photo")
        self.upload_photo_btn.clicked.connect(self.upload_photo)
        photo_btn_layout.addWidget(self.upload_photo_btn)
        photo_btn_layout.addStretch()
        
        photo_layout.addLayout(photo_btn_layout)
        photo_layout.addStretch()
        
        self.detail_form.addRow(photo_layout)
        
        # Name
        self.name_edit = QLineEdit()
        self.detail_form.addRow("Name:", self.name_edit)
        
        # Age
        self.age_edit = QDoubleSpinBox()
        self.age_edit.setMinimum(0)
        self.age_edit.setMaximum(30)
        self.age_edit.setSingleStep(0.1)
        self.age_edit.setDecimals(1)
        self.detail_form.addRow("Age (years):", self.age_edit)
        
        # Weight
        self.weight_edit = QDoubleSpinBox()
        self.weight_edit.setMinimum(0)
        self.weight_edit.setMaximum(30)
        self.weight_edit.setSingleStep(0.1)
        self.weight_edit.setDecimals(1)
        self.detail_form.addRow("Weight (kg):", self.weight_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        self.detail_form.addRow("Notes:", self.notes_edit)
        
        # Add the form to the layout
        form_layout.addWidget(form_container)
        
        # Save button
        self.save_btn = QPushButton("Save Cat")
        self.save_btn.clicked.connect(self.save_cat)
        form_layout.addWidget(self.save_btn)
        
        # Add layouts to main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create widgets for each side
        left_widget = QWidget()
        left_widget.setLayout(cat_list_layout)
        
        right_widget = QWidget()
        right_widget.setLayout(form_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 400])  # Set initial sizes
        
        layout.addWidget(splitter)
    
    def load_cats(self):
        """Load cats from the database into the table"""
        try:
            cats = self.db_manager.get_all_cats()
            
            self.cat_table.setRowCount(0)  # Clear existing rows
            
            for i, cat in enumerate(cats):
                self.cat_table.insertRow(i)
                self.cat_table.setItem(i, 0, QTableWidgetItem(cat['name']))
                
                # Age (may be None)
                age_item = QTableWidgetItem()
                if cat['age'] is not None:
                    age_item.setText(str(cat['age']))
                    age_item.setData(Qt.ItemDataRole.DisplayRole, cat['age'])
                self.cat_table.setItem(i, 1, age_item)
                
                # Weight (may be None)
                weight_item = QTableWidgetItem()
                if cat['weight'] is not None:
                    weight_item.setText(str(cat['weight']))
                    weight_item.setData(Qt.ItemDataRole.DisplayRole, cat['weight'])
                self.cat_table.setItem(i, 2, weight_item)
                
                # Store cat_id as item data
                self.cat_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, cat['id'])
            
            logger.info(f"Loaded {len(cats)} cats from database")
        except Exception as e:
            logger.error(f"Error loading cats: {e}")
            QMessageBox.critical(self, "Error", f"Error loading cats: {str(e)}")
    
    def on_cat_selected(self):
        """Handle cat selection in the table"""
        selected_rows = self.cat_table.selectedItems()
        if not selected_rows:
            self.clear_form()
            self.delete_cat_btn.setEnabled(False)
            self.selected_cat_id = None
            return
        
        # Get the cat ID from the first cell of the selected row
        row = selected_rows[0].row()
        self.selected_cat_id = self.cat_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Enable delete button
        self.delete_cat_btn.setEnabled(True)
        
        # Load cat details
        try:
            cat = self.db_manager.get_cat(self.selected_cat_id)
            if cat:
                self.name_edit.setText(cat['name'])
                
                if cat['age'] is not None:
                    self.age_edit.setValue(cat['age'])
                else:
                    self.age_edit.setValue(0)
                
                if cat['weight'] is not None:
                    self.weight_edit.setValue(cat['weight'])
                else:
                    self.weight_edit.setValue(0)
                
                if cat['notes']:
                    self.notes_edit.setText(cat['notes'])
                else:
                    self.notes_edit.setText("")
                
                # Load photo if available
                self.photo_path = cat['photo_path']
                if self.photo_path and os.path.exists(self.photo_path):
                    pixmap = QPixmap(self.photo_path)
                    self.photo_label.setPixmap(pixmap.scaled(
                        self.photo_label.width(), 
                        self.photo_label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio
                    ))
                else:
                    self.photo_label.setText("No Photo")
                    self.photo_label.setPixmap(QPixmap())
                
                # Emit signal that a cat was selected
                self.cat_selected.emit(self.selected_cat_id)
                
                logger.info(f"Loaded details for cat ID {self.selected_cat_id}")
        except Exception as e:
            logger.error(f"Error loading cat details: {e}")
            QMessageBox.critical(self, "Error", f"Error loading cat details: {str(e)}")
    
    def clear_form(self):
        """Clear the cat details form for adding a new cat"""
        self.selected_cat_id = None
        self.name_edit.setText("")
        self.age_edit.setValue(0)
        self.weight_edit.setValue(0)
        self.notes_edit.setText("")
        self.photo_path = None
        self.photo_label.setText("No Photo")
        self.photo_label.setPixmap(QPixmap())
        self.delete_cat_btn.setEnabled(False)
        
        # Deselect any selected row
        self.cat_table.clearSelection()
    
    def upload_photo(self):
        """Upload a photo for the cat"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Cat Photo",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            # Create photos directory if it doesn't exist
            os.makedirs("data/photos", exist_ok=True)
            
            # Generate a new filename based on timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = os.path.splitext(file_path)[1]
            new_filename = f"data/photos/cat_{timestamp}{extension}"
            
            # Copy the file to our photos directory
            import shutil
            try:
                shutil.copy(file_path, new_filename)
                self.photo_path = new_filename
                
                # Display the photo
                pixmap = QPixmap(self.photo_path)
                self.photo_label.setPixmap(pixmap.scaled(
                    self.photo_label.width(), 
                    self.photo_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio
                ))
                
                logger.info(f"Uploaded photo: {self.photo_path}")
            except Exception as e:
                logger.error(f"Error copying photo: {e}")
                QMessageBox.critical(self, "Error", f"Error saving photo: {str(e)}")
    
    def save_cat(self):
        """Save the cat details to the database"""
        # Validate input
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Cat name is required.")
            return
        
        age = self.age_edit.value() if self.age_edit.value() > 0 else None
        weight = self.weight_edit.value() if self.weight_edit.value() > 0 else None
        notes = self.notes_edit.toPlainText().strip() if self.notes_edit.toPlainText().strip() else None
        
        try:
            if self.selected_cat_id:
                # Update existing cat
                success = self.db_manager.update_cat(
                    self.selected_cat_id, name, age, weight, self.photo_path, notes
                )
                if success:
                    logger.info(f"Updated cat ID {self.selected_cat_id}")
                    QMessageBox.information(self, "Success", f"Cat '{name}' updated successfully.")
            else:
                # Add new cat
                cat_id = self.db_manager.add_cat(name, age, weight, self.photo_path, notes)
                if cat_id:
                    logger.info(f"Added new cat ID {cat_id}")
                    QMessageBox.information(self, "Success", f"Cat '{name}' added successfully.")
                    self.selected_cat_id = cat_id
            
            # Refresh the cat list
            self.load_cats()
            
            # Select the row for the cat we just saved
            if self.selected_cat_id:
                for row in range(self.cat_table.rowCount()):
                    if self.cat_table.item(row, 0).data(Qt.ItemDataRole.UserRole) == self.selected_cat_id:
                        self.cat_table.selectRow(row)
                        break
        
        except Exception as e:
            logger.error(f"Error saving cat: {e}")
            QMessageBox.critical(self, "Error", f"Error saving cat: {str(e)}")
    
    def delete_cat(self):
        """Delete the selected cat from the database"""
        if not self.selected_cat_id:
            return
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete this cat? This will also delete all feeding and water logs for this cat.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                success = self.db_manager.delete_cat(self.selected_cat_id)
                if success:
                    logger.info(f"Deleted cat ID {self.selected_cat_id}")
                    QMessageBox.information(self, "Success", "Cat deleted successfully.")
                    
                    # Clear the form and refresh the list
                    self.clear_form()
                    self.load_cats()
            except Exception as e:
                logger.error(f"Error deleting cat: {e}")
                QMessageBox.critical(self, "Error", f"Error deleting cat: {str(e)}") 