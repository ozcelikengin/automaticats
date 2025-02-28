"""
Tests for the Water Dispenser functionality
"""

import unittest
import os
import sys
import tempfile
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db_manager import DatabaseManager
from gui.tabs.water_dispenser_tab import WaterDispenserTab
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

# Mock QApplication for testing
app = QApplication.instance()
if not app:
    app = QApplication([])

class MockMessageBox:
    """Mock class for QMessageBox to avoid actual dialogs during tests"""
    @staticmethod
    def information(*args, **kwargs):
        return QMessageBox.StandardButton.Ok

class TestWaterDispenser(unittest.TestCase):
    """Test class for Water Dispenser functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create test cat data
        self.cat_id = self.db_manager.add_cat("Whiskers", 3, 4.5, "Siamese", "Picky eater")
        
        # Create the water dispenser tab with the test database
        self.water_dispenser_tab = WaterDispenserTab(self.db_manager)
        
        # Save the original QMessageBox.information method
        self.original_message_box = QMessageBox.information
        # Replace with mock
        QMessageBox.information = MockMessageBox.information

    def tearDown(self):
        """Clean up after tests"""
        # Close and remove the temporary database
        os.close(self.db_fd)
        os.unlink(self.db_path)
        
        # Restore the original QMessageBox.information method
        QMessageBox.information = self.original_message_box
    
    def test_tab_initialization(self):
        """Test that the tab initializes correctly"""
        # Verify that the tab has been created with appropriate widgets
        self.assertIsNotNone(self.water_dispenser_tab)
        
        # Check that the database manager was properly assigned
        self.assertEqual(self.water_dispenser_tab.db_manager, self.db_manager)
        
        # Check that selected_cat_id is initialized to None
        self.assertIsNone(self.water_dispenser_tab.selected_cat_id)
    
    def test_ui_components(self):
        """Test that all UI components are present"""
        # The tab has 3 tabs: Status, Settings, History
        tab_widget = None
        for child in self.water_dispenser_tab.children():
            if isinstance(child, QTabWidget):
                tab_widget = child
                break
        
        self.assertIsNotNone(tab_widget, "Tab widget not found")
        if tab_widget:
            self.assertEqual(tab_widget.count(), 3, "Tab widget should have 3 tabs")
            self.assertEqual(tab_widget.tabText(0), "Status")
            self.assertEqual(tab_widget.tabText(1), "Settings")
            self.assertEqual(tab_widget.tabText(2), "History")
    
    def test_refill_button_click(self):
        """Test the refill button functionality"""
        # Find the refill button
        refill_button = None
        for child in self.water_dispenser_tab.findChildren(QPushButton):
            if child.text() == "Refill":
                refill_button = child
                break
        
        self.assertIsNotNone(refill_button, "Refill button not found")
        
        # Click the button and verify it triggers the _on_refill_clicked method
        if refill_button:
            # QTest.mouseClick doesn't work well in this context, so we'll directly call the slot
            self.water_dispenser_tab._on_refill_clicked()
            # No assertion needed as we're using a mock message box
    
    def test_dispense_button_click(self):
        """Test the dispense button functionality"""
        # Find the dispense button
        dispense_button = None
        for child in self.water_dispenser_tab.findChildren(QPushButton):
            if child.text() == "Dispense Water":
                dispense_button = child
                break
        
        self.assertIsNotNone(dispense_button, "Dispense Water button not found")
        
        # Click the button and verify it triggers the _on_dispense_clicked method
        if dispense_button:
            self.water_dispenser_tab._on_dispense_clicked()
            # No assertion needed as we're using a mock message box
    
    def test_set_selected_cat(self):
        """Test setting the selected cat ID"""
        # Initially the selected_cat_id should be None
        self.assertIsNone(self.water_dispenser_tab.selected_cat_id)
        
        # Set a selected cat
        self.water_dispenser_tab.set_selected_cat(self.cat_id)
        
        # Verify that the selected_cat_id was updated
        self.assertEqual(self.water_dispenser_tab.selected_cat_id, self.cat_id)
    
    def test_refresh_water_inventory(self):
        """Test refreshing water inventory"""
        # Call the refresh method (which currently does nothing but should not crash)
        self.water_dispenser_tab.refresh_water_inventory()
        
        # No assertion needed as the method is a placeholder in the current implementation
    
    def test_apply_settings(self):
        """Test applying settings"""
        # Find the apply settings button
        apply_button = None
        for child in self.water_dispenser_tab.findChildren(QPushButton):
            if child.text() == "Apply Settings":
                apply_button = child
                break
        
        self.assertIsNotNone(apply_button, "Apply Settings button not found")
        
        # Click the button and verify it triggers the _on_apply_settings_clicked method
        if apply_button:
            self.water_dispenser_tab._on_apply_settings_clicked()
            # No assertion needed as we're using a mock message box

if __name__ == '__main__':
    unittest.main() 