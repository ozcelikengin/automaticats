"""
Unit tests for the ML Engine
"""

import os
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd

from core.ml_engine import MLEngine

class TestMLEngine(unittest.TestCase):
    """Test case for the MLEngine class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for models
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock database manager
        self.mock_db = MagicMock()
        
        # Sample cat data
        self.mock_db.get_cats.return_value = [
            {'cat_id': 1, 'name': 'Whiskers', 'age': 3},
            {'cat_id': 2, 'name': 'Mittens', 'age': 5}
        ]
        
        # Initialize MLEngine with mock db and temp directory
        self.ml_engine = MLEngine(self.mock_db, models_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test MLEngine initialization"""
        self.assertEqual(self.ml_engine.db_manager, self.mock_db)
        self.assertEqual(self.ml_engine.models_dir, self.temp_dir)
        self.assertTrue(os.path.exists(self.temp_dir))
        
        # Ensure models are initially None
        self.assertIsNone(self.ml_engine.time_model)
        self.assertIsNone(self.ml_engine.portion_model)
        self.assertIsNone(self.ml_engine.food_preference_model)
    
    def test_get_feeding_data(self):
        """Test get_feeding_data method"""
        # Test with no cat_id
        data = self.ml_engine.get_feeding_data()
        self.assertIsInstance(data, pd.DataFrame)
        self.assertGreater(len(data), 0)
        
        # Test with specific cat_id
        cat_data = self.ml_engine.get_feeding_data(cat_id=1)
        self.assertIsInstance(cat_data, pd.DataFrame)
        self.assertGreater(len(cat_data), 0)
        self.assertTrue(all(cat_data['cat_id'] == 1))
    
    def test_train_models(self):
        """Test train_models method"""
        # Train models
        result = self.ml_engine.train_models()
        
        # Check result
        self.assertTrue(result)
        
        # Check if models were created
        self.assertIsNotNone(self.ml_engine.time_model)
        self.assertIsNotNone(self.ml_engine.portion_model)
        self.assertIsNotNone(self.ml_engine.food_preference_model)
        
        # Check if model files were saved
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'time_model.pkl')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'portion_model.pkl')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'preference_model.pkl')))
    
    def test_predict_optimal_feeding_time(self):
        """Test predict_optimal_feeding_time method"""
        # First train the models
        self.ml_engine.train_models()
        
        # Make a prediction
        time, confidence = self.ml_engine.predict_optimal_feeding_time(1, 3)  # Cat 1, Wednesday
        
        # Check results
        self.assertIsNotNone(time)
        self.assertIsInstance(time, str)
        self.assertRegex(time, r'^\d{2}:\d{2}$')  # Format should be HH:MM
        
        self.assertIsNotNone(confidence)
        self.assertIsInstance(confidence, float)
        self.assertTrue(0 <= confidence <= 1)
    
    def test_recommend_portion_size(self):
        """Test recommend_portion_size method"""
        # First train the models
        self.ml_engine.train_models()
        
        # Make a recommendation
        portion, confidence = self.ml_engine.recommend_portion_size(1, 8, 2)  # Cat 1, 8am, Tuesday
        
        # Check results
        self.assertIsNotNone(portion)
        self.assertIsInstance(portion, float)
        self.assertTrue(10 <= portion <= 100)  # Reasonable portion size
        
        self.assertIsNotNone(confidence)
        self.assertIsInstance(confidence, float)
        self.assertTrue(0 <= confidence <= 1)
    
    def test_suggest_food_type(self):
        """Test suggest_food_type method"""
        # First train the models
        self.ml_engine.train_models()
        
        # Make a suggestion
        food_type, confidence = self.ml_engine.suggest_food_type(1, 18, 4)  # Cat 1, 6pm, Thursday
        
        # Check results
        self.assertIsNotNone(food_type)
        self.assertIsInstance(food_type, str)
        
        self.assertIsNotNone(confidence)
        self.assertIsInstance(confidence, float)
        self.assertTrue(0 <= confidence <= 1)
    
    def test_get_recommendations(self):
        """Test get_recommendations method"""
        # First train the models
        self.ml_engine.train_models()
        
        # Get recommendations
        recommendations = self.ml_engine.get_recommendations(1)
        
        # Check results
        self.assertIsNotNone(recommendations)
        self.assertIsInstance(recommendations, list)
        
        # Check individual recommendations
        for rec in recommendations:
            self.assertIsInstance(rec, dict)
            self.assertIn('type', rec)
            self.assertIn('value', rec)
            self.assertIn('confidence', rec)
            self.assertIn('message', rec)
    
    def test_record_feedback(self):
        """Test record_feedback method"""
        # Record feedback
        result = self.ml_engine.record_feedback(123, True, 30)
        
        # Check result
        self.assertTrue(result)
    
    def test_generate_pattern_analysis(self):
        """Test generate_pattern_analysis method"""
        # Generate pattern analysis
        pattern_data = self.ml_engine.generate_pattern_analysis(1)
        
        # Check results
        self.assertIsNotNone(pattern_data)
        self.assertIsInstance(pattern_data, dict)
        self.assertIn('hours', pattern_data)
        self.assertIn('consumption', pattern_data)
        self.assertIn('cat_id', pattern_data)
        self.assertEqual(pattern_data['cat_id'], 1)
        self.assertEqual(len(pattern_data['hours']), 24)
        self.assertEqual(len(pattern_data['consumption']), 24)


if __name__ == '__main__':
    unittest.main() 