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
    logger.info("Training time prediction model...")
    
    # Prepare features and target
    X = data[['cat_id', 'day_of_week', 'hour']]
    y = data['hour']  # Predict the hour of feeding
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"Time prediction model trained with accuracy: {accuracy:.4f}")
    
    # Get feature importance
    feature_importance = dict(zip(X.columns, model.feature_importances_))
    
    return {
        'model_type': 'time_prediction',
        'model': model,
        'accuracy': accuracy,
        'feature_importance': feature_importance,
        'scaler': scaler
    }

def train_portion_model(data):
    """Train a model to recommend portion sizes."""
    logger.info("Training portion size prediction model...")
    
    # Prepare features and target
    X = data[['cat_id', 'day_of_week', 'hour']]
    y = data['amount']  # Predict the portion size
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    logger.info(f"Portion size model trained with RMSE: {rmse:.4f}")
    
    # Get feature importance
    feature_importance = dict(zip(X.columns, model.feature_importances_))
    
    return {
        'model_type': 'portion_prediction',
        'model': model,
        'rmse': rmse,
        'feature_importance': feature_importance,
        'scaler': scaler
    }

def train_food_preference_model(data):
    """Train models to predict food preferences."""
    logger.info("Training food preference prediction models...")
    
    # Prepare features
    X = data[['cat_id', 'day_of_week', 'hour']]
    
    # Scale features once for all models
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train a model for each food type
    food_types = ['Dry Food', 'Wet Food', 'Treats']
    models = {}
    
    for food_type in food_types:
        # Create binary target: 1 if this food type was chosen, 0 otherwise
        y = (data['food_type'] == food_type).astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Food preference model for {food_type} trained with accuracy: {accuracy:.4f}")
        
        # Get feature importance
        feature_importance = dict(zip(X.columns, model.feature_importances_))
        
        # Store model info
        models[food_type] = {
            'model': model,
            'accuracy': accuracy,
            'feature_importance': feature_importance
        }
    
    return {
        'model_type': 'food_preference',
        'models': models,
        'scaler': scaler
    }

def save_models(db_manager, models_dir, models, debug_mode=False, sample_size=200):
    """Save trained models to disk and record in database."""
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    cursor = db_manager.conn.cursor()
    feeding_logs = []  # Default empty list
    
    try:
        # Check if ml_models table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ml_models'")
        if not cursor.fetchone():
            logger.warning("ml_models table does not exist, creating it...")
            # Create the table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_models (
                    model_id INTEGER PRIMARY KEY,
                    model_type TEXT NOT NULL,
                    model_path TEXT NOT NULL,
                    accuracy_metric TEXT,
                    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    feature_importance TEXT,
                    additional_info TEXT
                )
            ''')
        
        # Save each model
        for model_info in models:
            model_type = model_info['model_type']
            
            if model_type == 'time_prediction' or model_type == 'portion_prediction':
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
        
        # Save the scaler
        if 'scaler' in model_info:
            scaler = model_info['scaler']
            scaler_path = os.path.join(models_dir, 'scaler.pkl')
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            logger.info(f"Saved feature scaler to {scaler_path}")
        
        # Record training session
        cursor.execute('''
            INSERT INTO ml_training_sessions (
                started_at, completed_at, status, data_points_used
            ) VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'completed',
            sample_size if debug_mode else len(feeding_logs)
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
    """Main function to train ML models."""
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
            sample_size = 200
            logger.info(f"Generated sample data with {len(df)} records")
        else:
            df = get_training_data(db_manager)
            sample_size = len(df) if df is not None else 0
        
        if df is None or len(df) < 10:
            logger.warning("Insufficient data for training models")
            if args.debug:
                logger.info("Using sample data instead")
                df = generate_sample_data(size=200)
                sample_size = 200
            else:
                db_manager.close()
                return
        
        # Train models directly with the dataframe
        time_model = train_time_model(df)
        portion_model = train_portion_model(df)
        food_model = train_food_preference_model(df)
        
        # Save models
        models_dir = os.path.join(project_root, 'data', 'models')
        save_models(db_manager, models_dir, [time_model, portion_model, food_model], args.debug, sample_size)
        
        logger.info("ML model training completed successfully")
    
    except Exception as e:
        logger.error(f"Error in ML model training: {e}")
    
    finally:
        db_manager.close()

if __name__ == "__main__":
    main() 