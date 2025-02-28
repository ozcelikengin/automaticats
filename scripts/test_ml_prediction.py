#!/usr/bin/env python3
"""
Test ML Prediction Script for AutomatiCats

This script loads the trained ML models and makes predictions
to verify that the ML functionality is working correctly.
"""

import os
import sys
import glob
import pickle
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Add the parent directory to sys.path to import project modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ml_prediction_test')

def load_latest_model(model_type, models_dir):
    """Load the latest model of the specified type."""
    try:
        # Find all models of the specified type
        pattern = os.path.join(models_dir, f"{model_type}_*.pkl")
        model_files = glob.glob(pattern)
        
        if not model_files:
            logger.warning(f"No {model_type} models found in {models_dir}")
            return None
        
        # Sort by modification time (newest first)
        latest_model_file = max(model_files, key=os.path.getmtime)
        
        # Load the model
        with open(latest_model_file, 'rb') as f:
            model = pickle.load(f)
        
        logger.info(f"Loaded {model_type} model from {latest_model_file}")
        return model
    
    except Exception as e:
        logger.error(f"Error loading {model_type} model: {e}")
        return None

def create_test_input():
    """Create a test input for prediction."""
    # Create a sample input for a cat
    cat_id = 1
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()
    
    # Create a DataFrame with one-hot encoded features
    # This should match the format used during training
    data = {
        'hour': current_hour,  # Not one-hot encoded
        'day_of_week': current_day,
        'cat_id_1': 1,  # One-hot encoded cat_id
        'cat_id_2': 0,
        'cat_id_3': 0,
        'food_type_Dry Food': 1,
        'food_type_Wet Food': 0,
        'food_type_Treats': 0,
        'amount': 50.0,
        'meal_duration_minutes': 10.0,
        'consumption_rate_grams_per_minute': 5.0,
        'leftover_amount_grams': 5.0
    }
    
    # Create a DataFrame
    df = pd.DataFrame([data])
    
    return df

def predict_feeding_time(model, input_data):
    """Predict the optimal feeding time."""
    if model is None:
        return None
    
    try:
        # Select features for time prediction
        # Use the exact feature names from the model
        if hasattr(model, 'feature_names_in_'):
            features = [f for f in model.feature_names_in_ if f in input_data.columns]
            X = input_data[features]
        else:
            # Fallback to using all cat_id columns and hour/day_of_week
            features = [col for col in input_data.columns if col.startswith('cat_id_') or 
                       col == 'hour' or col == 'day_of_week']
            X = input_data[features]
        
        # Make prediction
        predicted_hour = model.predict(X)[0]
        
        # Get probabilities for all hours
        probabilities = model.predict_proba(X)[0]
        
        # Get top 3 hours with highest probabilities
        top_hours_indices = np.argsort(probabilities)[-3:][::-1]
        top_hours = [(int(model.classes_[idx]), float(probabilities[idx])) for idx in top_hours_indices]
        
        return {
            'predicted_hour': int(predicted_hour),
            'top_hours': top_hours
        }
    
    except Exception as e:
        logger.error(f"Error predicting feeding time: {e}")
        return None

def predict_portion_size(model, input_data):
    """Predict the optimal portion size."""
    if model is None:
        return None
    
    try:
        # Select features for portion prediction
        portion_features = [col for col in input_data.columns if col.startswith('cat_id_') or 
                           col.startswith('food_type_') or 
                           col in ['consumption_rate_grams_per_minute', 'leftover_amount_grams']]
        
        X = input_data[portion_features]
        
        # Make prediction
        predicted_amount = model.predict(X)[0]
        
        return {
            'predicted_amount': float(predicted_amount),
            'confidence': 0.85  # Placeholder for confidence
        }
    
    except Exception as e:
        logger.error(f"Error predicting portion size: {e}")
        return None

def main():
    """Main function to test ML predictions."""
    logger.info("Starting ML prediction test")
    
    # Path to models directory
    models_dir = os.path.join(project_root, 'data', 'models')
    
    # Load models
    time_model = load_latest_model('time_prediction', models_dir)
    portion_model = load_latest_model('portion_prediction', models_dir)
    
    if not time_model and not portion_model:
        logger.error("No models available for testing")
        return
    
    # Create test input
    test_input = create_test_input()
    logger.info("Created test input for predictions")
    
    # Make predictions
    if time_model:
        time_prediction = predict_feeding_time(time_model, test_input)
        if time_prediction:
            logger.info(f"Time prediction: {time_prediction['predicted_hour']}:00")
            logger.info(f"Top feeding hours: {time_prediction['top_hours']}")
    
    if portion_model:
        portion_prediction = predict_portion_size(portion_model, test_input)
        if portion_prediction:
            logger.info(f"Portion size prediction: {portion_prediction['predicted_amount']:.2f} grams")
            logger.info(f"Confidence: {portion_prediction['confidence']:.2f}")
    
    logger.info("ML prediction test completed")

if __name__ == "__main__":
    main() 