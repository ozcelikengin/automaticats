"""
Tests for the DatabaseManager class
"""

import os
import sys
import unittest
import tempfile
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager"""

    def setUp(self):
        """Set up a test database in a temporary file"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_manager = DatabaseManager(self.db_path)
    
    def tearDown(self):
        """Clean up after tests"""
        self.db_manager.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_add_and_get_cat(self):
        """Test adding and retrieving a cat"""
        # Add a cat
        cat_id = self.db_manager.add_cat(
            name="Whiskers",
            age=3.5,
            weight=4.2
        )
        
        # Verify cat_id is returned
        self.assertIsNotNone(cat_id)
        
        # Get the cat and verify details
        cat = self.db_manager.get_cat(cat_id)
        self.assertIsNotNone(cat)
        self.assertEqual(cat['name'], "Whiskers")
        self.assertEqual(cat['age'], 3.5)
        self.assertEqual(cat['weight'], 4.2)
    
    def test_get_all_cats(self):
        """Test retrieving all cats"""
        # Add multiple cats
        cat1_id = self.db_manager.add_cat(name="Whiskers")
        cat2_id = self.db_manager.add_cat(name="Mittens")
        cat3_id = self.db_manager.add_cat(name="Felix")
        
        # Get all cats
        cats = self.db_manager.get_all_cats()
        
        # Verify count
        self.assertEqual(len(cats), 3)
        
        # Verify cat names
        cat_names = [cat['name'] for cat in cats]
        self.assertIn("Whiskers", cat_names)
        self.assertIn("Mittens", cat_names)
        self.assertIn("Felix", cat_names)
    
    def test_update_cat(self):
        """Test updating a cat"""
        # Add a cat
        cat_id = self.db_manager.add_cat(
            name="Whiskers",
            age=3.5,
            weight=4.2
        )
        
        # Update the cat
        success = self.db_manager.update_cat(
            cat_id,
            name="Whiskers Jr.",
            age=4.0,
            weight=4.5
        )
        
        # Verify update was successful
        self.assertTrue(success)
        
        # Get the updated cat
        cat = self.db_manager.get_cat(cat_id)
        
        # Verify updated details
        self.assertEqual(cat['name'], "Whiskers Jr.")
        self.assertEqual(cat['age'], 4.0)
        self.assertEqual(cat['weight'], 4.5)
    
    def test_delete_cat(self):
        """Test deleting a cat"""
        # Add a cat
        cat_id = self.db_manager.add_cat(name="Whiskers")
        
        # Delete the cat
        success = self.db_manager.delete_cat(cat_id)
        
        # Verify deletion was successful
        self.assertTrue(success)
        
        # Try to get the deleted cat
        cat = self.db_manager.get_cat(cat_id)
        
        # Verify cat is None
        self.assertIsNone(cat)
    
    def test_food_inventory(self):
        """Test food inventory operations"""
        # Add food inventory
        food_id = self.db_manager.add_food_inventory(
            food_type="Dry Kibble",
            current_amount=500.0,
            max_capacity=1000.0,
            low_threshold=100.0
        )
        
        # Verify food_id is returned
        self.assertIsNotNone(food_id)
        
        # Get the food inventory
        food = self.db_manager.get_food_inventory(food_id)
        
        # Verify details
        self.assertEqual(food['food_type'], "Dry Kibble")
        self.assertEqual(food['current_amount'], 500.0)
        self.assertEqual(food['max_capacity'], 1000.0)
        self.assertEqual(food['low_threshold'], 100.0)
        
        # Update food level
        success = self.db_manager.update_food_level(
            food_id,
            current_amount=300.0
        )
        
        # Verify update was successful
        self.assertTrue(success)
        
        # Get updated food inventory
        food = self.db_manager.get_food_inventory(food_id)
        
        # Verify updated amount
        self.assertEqual(food['current_amount'], 300.0)
        
        # Add more food items
        self.db_manager.add_food_inventory(
            food_type="Wet Food",
            current_amount=50.0,
            max_capacity=200.0,
            low_threshold=30.0
        )
        
        # Get all food inventory
        foods = self.db_manager.get_food_inventory()
        
        # Verify count
        self.assertEqual(len(foods), 2)
    
    def test_feeding_schedule(self):
        """Test feeding schedule operations"""
        # Add a cat
        cat_id = self.db_manager.add_cat(name="Whiskers")
        
        # Add a feeding schedule
        schedule_id = self.db_manager.add_feeding_schedule(
            cat_id=cat_id,
            food_type="Dry Kibble",
            amount=50.0,
            time="08:00",
            days_of_week="monday,wednesday,friday"
        )
        
        # Verify schedule_id is returned
        self.assertIsNotNone(schedule_id)
        
        # Get feeding schedules for the cat
        schedules = self.db_manager.get_feeding_schedules(cat_id)
        
        # Verify schedule was added
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0]['food_type'], "Dry Kibble")
        self.assertEqual(schedules[0]['amount'], 50.0)
        self.assertEqual(schedules[0]['time'], "08:00")
        self.assertEqual(schedules[0]['days_of_week'], "monday,wednesday,friday")
    
    def test_feeding_log(self):
        """Test feeding log operations"""
        # Add a cat
        cat_id = self.db_manager.add_cat(name="Whiskers")
        
        # Add a feeding schedule
        schedule_id = self.db_manager.add_feeding_schedule(
            cat_id=cat_id,
            food_type="Dry Kibble",
            amount=50.0,
            time="08:00",
            days_of_week="monday,wednesday,friday"
        )
        
        # Add food inventory
        food_id = self.db_manager.add_food_inventory(
            food_type="Dry Kibble",
            current_amount=500.0,
            max_capacity=1000.0,
            low_threshold=100.0
        )
        
        # Log a feeding
        log_id = self.db_manager.log_feeding(
            cat_id=cat_id,
            food_type="Dry Kibble",
            amount=50.0,
            schedule_id=schedule_id,
            is_manual=False
        )
        
        # Verify log_id is returned
        self.assertIsNotNone(log_id)
        
        # Get feeding logs for the cat
        logs = self.db_manager.get_feeding_logs(cat_id)
        
        # Verify log was added
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['cat_id'], cat_id)
        self.assertEqual(logs[0]['food_type'], "Dry Kibble")
        self.assertEqual(logs[0]['amount'], 50.0)
        self.assertEqual(logs[0]['is_manual'], 0)  # SQLite stores booleans as 0/1
        
        # Verify food inventory was updated
        food = self.db_manager.get_food_inventory(food_id)
        self.assertEqual(food['current_amount'], 450.0)  # 500 - 50

if __name__ == '__main__':
    unittest.main()