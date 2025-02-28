#!/usr/bin/env python3
"""
ML Model Training Script for AutomatiCats

This script trains machine learning models based on the collected feeding data
and saves the models for use in the application.
"""

import os
import sys
import argparse
import logging
import json
import pickle
import sqlite3
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Add the parent directory to sys.path to import project modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from core.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ml_model_training')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Train ML models for AutomatiCats')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with sample data')
    parser.add_argument('--force', action='store_true', help='Force retraining even if recent models exist')
    return parser.parse_args()

def get_training_data(db_manager):
    """Get training data from the database."""
    try:
        cursor = db_manager.conn.cursor()
        
        # Get feeding logs with ML metrics
        cursor.execute('''
            SELECT fl.*, c.name as cat_name
            FROM feeding_logs fl
            JOIN cats c ON fl.cat_id = c.id
            WHERE fl.meal_duration_minutes IS NOT NULL
              AND fl.consumption_rate_grams_per_minute IS NOT NULL
              AND fl.leftover_amount_grams IS NOT NULL
            ORDER BY fl.timestamp
        ''')
        logs = cursor.fetchall()
        
        if not logs:
            logger.warning("No feeding logs with ML metrics found")
            return None
        
        logger.info(f"Retrieved {len(logs)} feeding logs for training")
        
        # Convert to DataFrame
        df = pd.DataFrame([dict(row) for row in logs])
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Extract time features
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['is_weekend'] = df['timestamp'].dt.dayofweek >= 5
        
        return df
    
    except Exception as e:
        logger.error(f"Error getting training data: {e}")
        return None

def preprocess_data(df):
    """Preprocess the data for training."""
    try:
        # Handle categorical features
        cat_features = ['food_type', 'cat_id']
        num_features = ['amount', 'hour', 'day_of_week']
        
        # One-hot encode categorical features
        df_encoded = pd.get_dummies(df, columns=cat_features, drop_first=False)
        
        # Select features for different models
        time_features = [col for col in df_encoded.columns if col.startswith('hour') or 
                         col.startswith('day_of_week') or col.startswith('cat_id')]
        
        portion_features = [col for col in df_encoded.columns if col.startswith('cat_id') or 
                           col.startswith('food_type') or 'amount' in col or 
                           'consumption_rate' in col or 'leftover' in col]
        
        food_features = [col for col in df_encoded.columns if col.startswith('cat_id') or 
                        'amount' in col or 'leftover' in col or 'meal_duration' in col]
        
        return {
            'full_data': df_encoded,
            'time_features': time_features,
            'portion_features': portion_features,
            'food_features': food_features
        }
    
    except Exception as e:
        logger.error(f"Error preprocessing data: {e}")
        return None

def train_time_model(data):
    """Train a model to predict optimal feeding times."""
    try:
        df = data['full_data']
        features = data['time_features']
        
        # Target: hour of day (classification problem)
        X = df[features]
        y = df['hour']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Get feature importance
        feature_importance = dict(zip(features, model.feature_importances_))
        
        logger.info(f"Time prediction model trained with accuracy: {accuracy:.4f}")
        
        return {
            'model': model,
            'accuracy': accuracy,
            'feature_importance': feature_importance,
            'model_type': 'time_prediction'
        }
    
    except Exception as e:
        logger.error(f"Error training time model: {e}")
        return None

def train_portion_model(data):
    """Train a model to predict optimal portion sizes."""
    try:
        df = data['full_data']
        features = data['portion_features']
        
        # Target: amount (regression problem)
        X = df[features]
        y = df['amount']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # Get feature importance
        feature_importance = dict(zip(features, model.feature_importances_))
        
        logger.info(f"Portion size model trained with RMSE: {rmse:.4f}")
        
        return {
            'model': model,
            'rmse': rmse,
            'feature_importance': feature_importance,
            'model_type': 'portion_prediction'
        }
    
    except Exception as e:
        logger.error(f"Error training portion model: {e}")
        return None

def train_food_preference_model(data):
    """Train a model to predict food preferences."""
    try:
        df = data['full_data']
        features = data['food_features']
        
        # Target: food_type (already one-hot encoded)
        food_type_cols = [col for col in df.columns if col.startswith('food_type_')]
        
        if not food_type_cols:
            logger.warning("No food type columns found after encoding")
            return None
        
        # For each food type, train a binary classifier
        models = {}
        
        for food_col in food_type_cols:
            food_name = food_col.replace('food_type_', '')
            
            X = df[features]
            y = df[food_col]
            
            # Skip if all values are the same
            if y.nunique() <= 1:
                continue
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            # Get feature importance
            feature_importance = dict(zip(features, model.feature_importances_))
            
            models[food_name] = {
                'model': model,
                'accuracy': accuracy,
                'f1_score': f1,
                'feature_importance': feature_importance
            }
            
            logger.info(f"Food preference model for {food_name} trained with accuracy: {accuracy:.4f}")
        
        return {
            'models': models,
            'model_type': 'food_preference'
        }
    
    except Exception as e:
        logger.error(f"Error training food preference model: {e}")
        return None

def save_models(db_manager, models_dir, models):
    """Save trained models to disk and record in database."""
    try:
        # Ensure models directory exists
        os.makedirs(models_dir, exist_ok=True)
        
        cursor = db_manager.conn.cursor()
        
        # Check if ml_models table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ml_models'")
        if not cursor.fetchone():
            logger.warning("ml_models table not found, skipping database recording")
            return
        
        for model_info in models:
            if not model_info:
                continue
                
            model_type = model_info['model_type']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if model_type == 'time_prediction' or model_type == 'portion_prediction':
                # Save single model
                model = model_info['model']
                model_path = os.path.join(models_dir, f"{model_type}_{timestamp}.pkl")
                
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                
                # Record in database
                metrics = json.dumps({
                    'accuracy': model_info.get('accuracy', 0),
                    'rmse': model_info.get('rmse', 0)
                })
                
                cursor.execute('''
                    INSERT INTO ml_models (
                        model_type, model_path, accuracy_metric, 
                        training_date, is_active, feature_importance
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    model_type,
                    model_path,
                    metrics,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    1,  # Active
                    json.dumps(model_info['feature_importance'])
                ))
                
                logger.info(f"Saved {model_type} model to {model_path}")
                
            elif model_type == 'food_preference':
                # Save multiple models
                models_dict = model_info['models']
                
                for food_name, food_model_info in models_dict.items():
                    model = food_model_info['model']
                    model_path = os.path.join(models_dir, f"{model_type}_{food_name}_{timestamp}.pkl")
                    
                    with open(model_path, 'wb') as f:
                        pickle.dump(model, f)
                    
                    # Record in database
                    metrics = json.dumps({
                        'accuracy': food_model_info.get('accuracy', 0),
                        'f1_score': food_model_info.get('f1_score', 0)
                    })
                    
                    cursor.execute('''
                        INSERT INTO ml_models (
                            model_type, model_path, accuracy_metric, 
                            training_date, is_active, feature_importance, 
                            additional_info
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        f"{model_type}_{food_name}",
                        model_path,
                        metrics,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        1,  # Active
                        json.dumps(food_model_info['feature_importance']),
                        food_name
                    ))
                    
                    logger.info(f"Saved {model_type} model for {food_name} to {model_path}")
        
        # Record training session
        cursor.execute('''
            INSERT INTO ml_training_sessions (
                timestamp, models_trained, success
            ) VALUES (?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            len(models),
            1
        ))
        
        db_manager.conn.commit()
        logger.info(f"Recorded model information in database")
        
    except Exception as e:
        logger.error(f"Error saving models: {e}")
        db_manager.conn.rollback()

def generate_sample_data(size=100):
    """Generate sample data for debug mode."""
    np.random.seed(42)
    
    # Generate cat IDs
    cat_ids = np.random.choice([1, 2, 3], size=size)
    
    # Generate food types
    food_types = np.random.choice(['Dry Food', 'Wet Food', 'Treats'], size=size)
    
    # Generate timestamps
    base_date = pd.Timestamp('2025-01-01')
    timestamps = [base_date + pd.Timedelta(days=np.random.randint(0, 30), 
                                          hours=np.random.randint(0, 24)) 
                 for _ in range(size)]
    
    # Generate amounts
    amounts = np.random.uniform(20, 100, size=size)
    
    # Generate ML metrics
    meal_durations = np.random.uniform(2, 15, size=size)
    consumption_rates = amounts / meal_durations
    leftover_amounts = np.random.uniform(0, 0.3, size=size) * amounts
    
    # Create DataFrame
    df = pd.DataFrame({
        'cat_id': cat_ids,
        'food_type': food_types,
        'timestamp': timestamps,
        'amount': amounts,
        'meal_duration_minutes': meal_durations,
        'consumption_rate_grams_per_minute': consumption_rates,
        'leftover_amount_grams': leftover_amounts,
        'hour': [ts.hour for ts in timestamps],
        'day_of_week': [ts.dayofweek for ts in timestamps],
        'is_weekend': [ts.dayofweek >= 5 for ts in timestamps]
    })
    
    return df

def main():
    """Main function to run the ML model training script."""
    args = parse_arguments()
    
    logger.info("Starting ML model training")
    
    if args.debug:
        logger.info("Debug mode enabled - will use sample data")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    try:
        # Get training data
        if args.debug:
            df = generate_sample_data(size=200)
            logger.info(f"Generated sample data with {len(df)} records")
        else:
            df = get_training_data(db_manager)
        
        if df is None or len(df) < 10:
            logger.warning("Insufficient data for training models")
            if args.debug:
                logger.info("Using sample data instead")
                df = generate_sample_data(size=200)
            else:
                db_manager.close()
                return
        
        # Preprocess data
        processed_data = preprocess_data(df)
        if not processed_data:
            logger.error("Failed to preprocess data")
            db_manager.close()
            return
        
        # Train models
        time_model = train_time_model(processed_data)
        portion_model = train_portion_model(processed_data)
        food_model = train_food_preference_model(processed_data)
        
        # Save models
        models_dir = os.path.join(project_root, 'data', 'models')
        save_models(db_manager, models_dir, [time_model, portion_model, food_model])
        
        logger.info("ML model training completed successfully")
    
    except Exception as e:
        logger.error(f"Error in ML model training: {e}")
    
    finally:
        db_manager.close()

if __name__ == "__main__":
    main() 