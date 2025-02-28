#!/usr/bin/env python3
"""
Test ML Predictions for AutomatiCats

This script tests the ML models by loading them and making predictions
on sample data.
"""

import os
import sys
import logging
import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the parent directory to sys.path to import project modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from core.db_manager import DatabaseManager
from core.ml_engine import MLEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ml_prediction_test')

def create_test_input():
    """Create a sample input for testing predictions."""
    # Create a sample cat with feeding history
    cat_id = 1
    cat_name = "TestCat"
    
    # Current time info
    now = datetime.now()
    day_of_week = now.weekday()
    hour_of_day = now.hour
    
    return {
        'cat_id': cat_id,
        'day_of_week': day_of_week,
        'hour_of_day': hour_of_day
    }

def test_time_prediction(ml_engine, features):
    """Test the time prediction model."""
    try:
        # Get prediction for next feeding time
        cat_id = features['cat_id']
        day_of_week = features['day_of_week']
        
        prediction, confidence = ml_engine.predict_optimal_feeding_time(cat_id, day_of_week)
        
        if prediction is not None:
            logger.info(f"Time prediction: {prediction} (confidence: {confidence:.2f})")
            return True
        else:
            logger.error("Failed to get time prediction")
            return False
    except Exception as e:
        logger.error(f"Error in time prediction test: {e}")
        return False

def test_portion_prediction(ml_engine, features):
    """Test the portion prediction model."""
    try:
        # Get prediction for portion size
        cat_id = features['cat_id']
        hour_of_day = features['hour_of_day']
        day_of_week = features['day_of_week']
        
        prediction, confidence = ml_engine.recommend_portion_size(cat_id, hour_of_day, day_of_week)
        
        if prediction is not None:
            logger.info(f"Portion prediction: {prediction:.2f} grams (confidence: {confidence:.2f})")
            return True
        else:
            logger.error("Failed to get portion prediction")
            return False
    except Exception as e:
        logger.error(f"Error in portion prediction test: {e}")
        return False

def test_food_preference(ml_engine, features):
    """Test the food preference model."""
    try:
        # Get prediction for food preference
        cat_id = features['cat_id']
        hour_of_day = features['hour_of_day']
        day_of_week = features['day_of_week']
        
        prediction, confidence = ml_engine.suggest_food_type(cat_id, hour_of_day, day_of_week)
        
        if prediction is not None:
            logger.info(f"Food preference prediction: {prediction} (confidence: {confidence:.2f})")
            return True
        else:
            logger.error("Failed to get food preference prediction")
            return False
    except Exception as e:
        logger.error(f"Error in food preference test: {e}")
        return False

def test_recommendations(ml_engine, features):
    """Test getting all recommendations."""
    try:
        cat_id = features['cat_id']
        recommendations = ml_engine.get_recommendations(cat_id)
        
        if recommendations:
            logger.info(f"Got {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"  {i}. {rec['type']}: {rec['value']} (confidence: {rec['confidence']:.2f})")
            return True
        else:
            logger.warning("No recommendations available")
            return False
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return False

def main():
    """Main function to test ML predictions."""
    logger.info("Starting ML prediction test")
    
    # Initialize database manager and ML engine
    db_manager = DatabaseManager()
    ml_engine = MLEngine(db_manager)
    
    try:
        # Create test input
        features = create_test_input()
        logger.info(f"Created test input: {features}")
        
        # Test time prediction
        time_success = test_time_prediction(ml_engine, features)
        
        # Test portion prediction
        portion_success = test_portion_prediction(ml_engine, features)
        
        # Test food preference
        food_success = test_food_preference(ml_engine, features)
        
        # Test getting all recommendations
        rec_success = test_recommendations(ml_engine, features)
        
        if time_success and portion_success and food_success and rec_success:
            logger.info("All ML prediction tests completed successfully")
        else:
            logger.warning("Some ML prediction tests failed")
    
    except Exception as e:
        logger.error(f"Error in ML prediction test: {e}")
    
    finally:
        db_manager.close()

if __name__ == "__main__":
    main() 