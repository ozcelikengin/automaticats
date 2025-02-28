#!/usr/bin/env python3
"""
Inspect ML Model Script for AutomatiCats

This script loads the trained ML models and inspects their structure
to understand the features used during training.
"""

import os
import sys
import glob
import pickle
import logging
import pandas as pd
import numpy as np

# Add the parent directory to sys.path to import project modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ml_model_inspector')

def load_latest_model(model_type, models_dir):
    """Load the latest model of the specified type."""
    try:
        # Find all models of the specified type
        pattern = os.path.join(models_dir, f"{model_type}_*.pkl")
        model_files = glob.glob(pattern)
        
        if not model_files:
            logger.warning(f"No {model_type} models found in {models_dir}")
            return None, None
        
        # Sort by modification time (newest first)
        latest_model_file = max(model_files, key=os.path.getmtime)
        
        # Load the model
        with open(latest_model_file, 'rb') as f:
            model = pickle.load(f)
        
        logger.info(f"Loaded {model_type} model from {latest_model_file}")
        return model, latest_model_file
    
    except Exception as e:
        logger.error(f"Error loading {model_type} model: {e}")
        return None, None

def inspect_model(model, model_path):
    """Inspect the model structure."""
    if model is None:
        return
    
    logger.info(f"Inspecting model: {os.path.basename(model_path)}")
    
    # Print model type
    logger.info(f"Model type: {type(model).__name__}")
    
    # Print model parameters
    logger.info(f"Model parameters: {model.get_params()}")
    
    # Print feature names if available
    if hasattr(model, 'feature_names_in_'):
        logger.info(f"Feature names used during training:")
        for i, feature in enumerate(model.feature_names_in_):
            logger.info(f"  {i+1}. {feature}")
    
    # Print target classes if available (for classification)
    if hasattr(model, 'classes_'):
        logger.info(f"Target classes: {model.classes_}")
    
    # Print feature importances if available
    if hasattr(model, 'feature_importances_'):
        logger.info("Feature importances:")
        if hasattr(model, 'feature_names_in_'):
            # Sort features by importance
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1]
            
            for i in range(min(10, len(indices))):  # Print top 10
                idx = indices[i]
                logger.info(f"  {model.feature_names_in_[idx]}: {importances[idx]:.4f}")
        else:
            logger.info(f"  {model.feature_importances_}")
    
    # Print estimators if it's an ensemble
    if hasattr(model, 'estimators_'):
        logger.info(f"Number of estimators: {len(model.estimators_)}")
        
        # Print first estimator details
        if len(model.estimators_) > 0:
            logger.info(f"First estimator type: {type(model.estimators_[0]).__name__}")
    
    logger.info("Model inspection completed")

def main():
    """Main function to inspect ML models."""
    logger.info("Starting ML model inspection")
    
    # Path to models directory
    models_dir = os.path.join(project_root, 'data', 'models')
    
    # Load time prediction model
    result = load_latest_model('time_prediction', models_dir)
    if result[0]:
        time_model, time_model_path = result
        inspect_model(time_model, time_model_path)
    
    # Load portion prediction model
    result = load_latest_model('portion_prediction', models_dir)
    if result[0]:
        portion_model, portion_model_path = result
        inspect_model(portion_model, portion_model_path)
    
    # Load food preference models
    result = load_latest_model('food_preference', models_dir)
    if result[0]:
        food_model, food_model_path = result
        inspect_model(food_model, food_model_path)
    
    logger.info("ML model inspection completed")

if __name__ == "__main__":
    main() 