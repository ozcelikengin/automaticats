"""
Machine Learning Engine for AutomatiCats

This module handles pattern recognition and recommendations
for cat feeding schedules and portions based on historical data.
"""

import os
import logging
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score

# Configure logging
logger = logging.getLogger('automaticats.ml_engine')

class MLEngine:
    """Machine Learning engine for feeding pattern analysis and recommendations"""
    
    def __init__(self, db_manager, models_dir='data/models'):
        """Initialize the ML engine with database access"""
        self.db_manager = db_manager
        self.models_dir = models_dir
        self.time_model = None
        self.portion_model = None
        self.food_preference_model = None
        self.scaler = None
        
        # Create models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Try to load existing models
        self._load_models()
    
    def _load_models(self):
        """Load trained models if they exist"""
        try:
            # Get the most recent models from the database
            cursor = self.db_manager.conn.cursor()
            
            # Time prediction model
            cursor.execute('''
                SELECT model_path FROM ml_models 
                WHERE model_type LIKE 'time_prediction%' AND is_active = 1
                ORDER BY training_date DESC LIMIT 1
            ''')
            time_model_row = cursor.fetchone()
            
            if time_model_row and os.path.exists(time_model_row[0]):
                time_model_path = time_model_row[0]
                with open(time_model_path, 'rb') as f:
                    self.time_model = pickle.load(f)
                logger.info(f"Loaded time prediction model from {time_model_path}")
            else:
                # Fallback to direct file search
                time_model_files = [f for f in os.listdir(self.models_dir) if f.startswith('time_prediction_')]
                if time_model_files:
                    # Get the most recent model by sorting filenames (which contain timestamps)
                    latest_time_model = sorted(time_model_files)[-1]
                    time_model_path = os.path.join(self.models_dir, latest_time_model)
                    with open(time_model_path, 'rb') as f:
                        self.time_model = pickle.load(f)
                    logger.info(f"Loaded time prediction model from {time_model_path}")
            
            # Portion recommendation model
            cursor.execute('''
                SELECT model_path FROM ml_models 
                WHERE model_type LIKE 'portion_prediction%' AND is_active = 1
                ORDER BY training_date DESC LIMIT 1
            ''')
            portion_model_row = cursor.fetchone()
            
            if portion_model_row and os.path.exists(portion_model_row[0]):
                portion_model_path = portion_model_row[0]
                with open(portion_model_path, 'rb') as f:
                    self.portion_model = pickle.load(f)
                logger.info(f"Loaded portion recommendation model from {portion_model_path}")
            else:
                # Fallback to direct file search
                portion_model_files = [f for f in os.listdir(self.models_dir) if f.startswith('portion_prediction_')]
                if portion_model_files:
                    # Get the most recent model
                    latest_portion_model = sorted(portion_model_files)[-1]
                    portion_model_path = os.path.join(self.models_dir, latest_portion_model)
                    with open(portion_model_path, 'rb') as f:
                        self.portion_model = pickle.load(f)
                    logger.info(f"Loaded portion recommendation model from {portion_model_path}")
            
            # Food preference models (multiple models, one per food type)
            cursor.execute('''
                SELECT model_path FROM ml_models 
                WHERE model_type LIKE 'food_preference_%' AND is_active = 1
                ORDER BY training_date DESC
            ''')
            food_model_rows = cursor.fetchall()
            
            if food_model_rows:
                # For simplicity, just use the first food preference model
                # In a real implementation, we would load all food preference models
                food_model_path = food_model_rows[0][0]
                if os.path.exists(food_model_path):
                    with open(food_model_path, 'rb') as f:
                        self.food_preference_model = pickle.load(f)
                    logger.info(f"Loaded food preference model from {food_model_path}")
            else:
                # Fallback to direct file search
                food_model_files = [f for f in os.listdir(self.models_dir) if f.startswith('food_preference_')]
                if food_model_files:
                    # Get the most recent model
                    latest_food_model = sorted(food_model_files)[-1]
                    food_model_path = os.path.join(self.models_dir, latest_food_model)
                    with open(food_model_path, 'rb') as f:
                        self.food_preference_model = pickle.load(f)
                    logger.info(f"Loaded food preference model from {food_model_path}")
            
            # Feature scaler - we don't have this in the database, so just use the old approach
            scaler_path = os.path.join(self.models_dir, 'scaler.pkl')
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("Loaded feature scaler")
            else:
                # If no scaler is found, create a default one
                self.scaler = StandardScaler()
                logger.info("Created default feature scaler")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            # Reset models if loading fails
            self.time_model = None
            self.portion_model = None
            self.food_preference_model = None
            self.scaler = None
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            # Time prediction model
            if self.time_model:
                with open(os.path.join(self.models_dir, 'time_model.pkl'), 'wb') as f:
                    pickle.dump(self.time_model, f)
            
            # Portion recommendation model
            if self.portion_model:
                with open(os.path.join(self.models_dir, 'portion_model.pkl'), 'wb') as f:
                    pickle.dump(self.portion_model, f)
            
            # Food preference model
            if self.food_preference_model:
                with open(os.path.join(self.models_dir, 'preference_model.pkl'), 'wb') as f:
                    pickle.dump(self.food_preference_model, f)
            
            # Feature scaler
            if self.scaler:
                with open(os.path.join(self.models_dir, 'scaler.pkl'), 'wb') as f:
                    pickle.dump(self.scaler, f)
                    
            logger.info("Saved ML models to disk")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def get_feeding_data(self, cat_id=None, days=30):
        """Get feeding data for training from database"""
        # This would be implemented to extract data from the database
        # For now, we'll return a placeholder dataframe
        
        # In a real implementation, we would:
        # 1. Query feeding_logs table for historical data
        # 2. Join with feeding_metrics for additional features
        # 3. Process and format the data for ML
        
        # Placeholder data
        dates = pd.date_range(end=datetime.now(), periods=100, freq='6H')
        
        if cat_id:
            # Generate data for a specific cat
            data = {
                'cat_id': [cat_id] * len(dates),
                'timestamp': dates,
                'hour_of_day': [d.hour for d in dates],
                'day_of_week': [d.dayofweek for d in dates],
                'portion_size': np.random.normal(30, 5, len(dates)),
                'consumed_percent': np.random.normal(90, 10, len(dates)),
                'consumption_rate': np.random.normal(2, 0.5, len(dates)),  # grams per minute
                'meal_duration': np.random.normal(10, 3, len(dates)),  # minutes
                'food_type_id': np.random.choice([1, 2, 3], len(dates)),
                'leftover_amount': np.random.normal(3, 2, len(dates))
            }
        else:
            # Generate data for all cats (example with 3 cats)
            data = {
                'cat_id': np.random.choice([1, 2, 3], len(dates)),
                'timestamp': dates,
                'hour_of_day': [d.hour for d in dates],
                'day_of_week': [d.dayofweek for d in dates],
                'portion_size': np.random.normal(30, 5, len(dates)),
                'consumed_percent': np.random.normal(90, 10, len(dates)),
                'consumption_rate': np.random.normal(2, 0.5, len(dates)),
                'meal_duration': np.random.normal(10, 3, len(dates)),
                'food_type_id': np.random.choice([1, 2, 3], len(dates)),
                'leftover_amount': np.random.normal(3, 2, len(dates))
            }
        
        return pd.DataFrame(data)
    
    def train_models(self, cat_id=None):
        """Train ML models on feeding history data"""
        try:
            # Get training data
            data = self.get_feeding_data(cat_id)
            
            if len(data) < 10:
                logger.warning("Insufficient data for training models")
                return False
            
            # Prepare features for time prediction model
            X_time = data[['cat_id', 'day_of_week', 'consumed_percent', 
                          'consumption_rate', 'meal_duration', 'food_type_id']]
            y_time = data['hour_of_day']
            
            # Train time prediction model
            X_train, X_test, y_train, y_test = train_test_split(X_time, y_time, test_size=0.2)
            
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            self.time_model = RandomForestRegressor(n_estimators=100)
            self.time_model.fit(X_train_scaled, y_train)
            
            # Evaluate time model
            y_pred_time = self.time_model.predict(X_test_scaled)
            time_error = mean_absolute_error(y_test, y_pred_time)
            logger.info(f"Time prediction model MAE: {time_error}")
            
            # Prepare features for portion recommendation model
            X_portion = data[['cat_id', 'hour_of_day', 'day_of_week', 
                             'consumption_rate', 'consumed_percent', 'food_type_id']]
            y_portion = data['portion_size']
            
            # Train portion recommendation model
            X_train, X_test, y_train, y_test = train_test_split(X_portion, y_portion, test_size=0.2)
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            self.portion_model = RandomForestRegressor(n_estimators=100)
            self.portion_model.fit(X_train_scaled, y_train)
            
            # Evaluate portion model
            y_pred_portion = self.portion_model.predict(X_test_scaled)
            portion_error = mean_absolute_error(y_test, y_pred_portion)
            logger.info(f"Portion recommendation model MAE: {portion_error}")
            
            # Prepare features for food preference model
            X_food = data[['cat_id', 'hour_of_day', 'day_of_week', 'consumed_percent']]
            y_food = data['food_type_id']
            
            # Train food preference model
            X_train, X_test, y_train, y_test = train_test_split(X_food, y_food, test_size=0.2)
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            self.food_preference_model = RandomForestClassifier(n_estimators=100)
            self.food_preference_model.fit(X_train_scaled, y_train)
            
            # Evaluate food preference model
            y_pred_food = self.food_preference_model.predict(X_test_scaled)
            food_accuracy = accuracy_score(y_test, y_pred_food)
            logger.info(f"Food preference model accuracy: {food_accuracy}")
            
            # Save models
            self._save_models()
            
            return True
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return False
    
    def predict_optimal_feeding_time(self, cat_id, day_of_week):
        """Predict the optimal feeding time for a cat on a specific day"""
        if not self.time_model or not self.scaler:
            logger.warning("Time prediction model not available")
            return None, 0.0
        
        try:
            # Create a feature vector for prediction
            # Use the same structure as in training: cat_id, day_of_week, hour
            # For hour, we'll use the current hour as a placeholder
            current_hour = datetime.now().hour
            features = np.array([[cat_id, day_of_week, current_hour]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            hour_prediction = self.time_model.predict(features_scaled)[0]
            
            # Get confidence (use feature importance and prediction variance as proxy)
            confidence = 0.75  # Placeholder, would calculate from model internals
            
            # Convert hour to time format
            hour = int(hour_prediction)
            minute = 0  # We're predicting the hour, not minutes
            predicted_time = f"{hour:02d}:{minute:02d}"
            
            return predicted_time, confidence
            
        except Exception as e:
            logger.error(f"Error predicting feeding time: {e}")
            return None, 0.0
    
    def recommend_portion_size(self, cat_id, hour_of_day, day_of_week, food_type_id=1):
        """Recommend an optimal portion size for a feeding"""
        if not self.portion_model or not self.scaler:
            logger.warning("Portion recommendation model not available")
            return None, 0.0
        
        try:
            # Create a feature vector for prediction
            # Use the same structure as in training: cat_id, day_of_week, hour
            features = np.array([[cat_id, day_of_week, hour_of_day]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            portion_prediction = self.portion_model.predict(features_scaled)[0]
            
            # Get confidence
            confidence = 0.80  # Placeholder, would calculate from model internals
            
            return round(portion_prediction, 1), confidence
            
        except Exception as e:
            logger.error(f"Error recommending portion size: {e}")
            return None, 0.0
    
    def suggest_food_type(self, cat_id, hour_of_day, day_of_week):
        """Suggest a food type based on cat preferences"""
        if not self.food_preference_model or not self.scaler:
            logger.warning("Food preference model not available")
            return None, 0.0
        
        try:
            # Create a feature vector for prediction
            # Use the same structure as in training: cat_id, day_of_week, hour
            features = np.array([[cat_id, day_of_week, hour_of_day]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            food_type_prediction = self.food_preference_model.predict(features_scaled)[0]
            
            # Get prediction probabilities
            proba = self.food_preference_model.predict_proba(features_scaled)[0]
            confidence = max(proba)
            
            # Convert binary prediction to food type
            # Since we're using a binary classifier for each food type,
            # a prediction of 1 means the food type is recommended
            if food_type_prediction == 1:
                # Extract food type from model name in database
                cursor = self.db_manager.conn.cursor()
                cursor.execute('''
                    SELECT additional_info FROM ml_models 
                    WHERE model_path = ? LIMIT 1
                ''', (os.path.abspath(self.db_manager.conn.execute(
                    "SELECT model_path FROM ml_models WHERE model_type LIKE 'food_preference_%' LIMIT 1"
                ).fetchone()[0]),))
                
                food_type_row = cursor.fetchone()
                if food_type_row:
                    food_name = food_type_row[0]
                else:
                    # Fallback to a default food type
                    food_name = "Recommended Food"
            else:
                # If prediction is 0, suggest a default food type
                food_name = "Standard Food"
            
            return food_name, confidence
            
        except Exception as e:
            logger.error(f"Error suggesting food type: {e}")
            return None, 0.0
    
    def get_recommendations(self, cat_id):
        """Get a full set of feeding recommendations for a cat"""
        recommendations = []
        
        # Get cat info
        cat_name = f"Cat {cat_id}"  # Placeholder, would get from database
        
        # Current time info
        now = datetime.now()
        today_dow = now.weekday()
        
        # Get time recommendation for today
        optimal_time, time_confidence = self.predict_optimal_feeding_time(cat_id, today_dow)
        if optimal_time and time_confidence > 0.7:
            # Only include high confidence recommendations
            time_rec = {
                "type": "feeding_time",
                "cat_id": cat_id,
                "cat_name": cat_name,
                "value": optimal_time,
                "confidence": time_confidence,
                "message": f"{cat_name} might prefer eating at {optimal_time}"
            }
            recommendations.append(time_rec)
        
        # Current hour (for portion and food recommendations)
        current_hour = now.hour
        
        # Get portion recommendation
        portion_size, portion_confidence = self.recommend_portion_size(cat_id, current_hour, today_dow)
        if portion_size and portion_confidence > 0.7:
            portion_rec = {
                "type": "portion_size",
                "cat_id": cat_id,
                "cat_name": cat_name,
                "value": portion_size,
                "confidence": portion_confidence,
                "message": f"Consider a {portion_size}g portion for {cat_name}'s next meal"
            }
            recommendations.append(portion_rec)
        
        # Get food type suggestion
        food_type, food_confidence = self.suggest_food_type(cat_id, current_hour, today_dow)
        if food_type and food_confidence > 0.7:
            food_rec = {
                "type": "food_type",
                "cat_id": cat_id,
                "cat_name": cat_name,
                "value": food_type,
                "confidence": food_confidence,
                "message": f"Try feeding {cat_name} with {food_type}"
            }
            recommendations.append(food_rec)
        
        return recommendations
    
    def record_feedback(self, recommendation_id, accepted, actual_value=None):
        """Record user feedback on a recommendation"""
        # In a real implementation, this would:
        # 1. Update the database with the feedback
        # 2. Use this data for future model training
        
        logger.info(f"Recorded feedback for recommendation {recommendation_id}: accepted={accepted}")
        return True
    
    def generate_pattern_analysis(self, cat_id, days=30):
        """Generate data for feeding pattern visualization"""
        # Get feeding data
        data = self.get_feeding_data(cat_id, days)
        
        # Process for visualization
        # This would return data suitable for plotting
        # For example, time of day vs consumption
        
        hours = list(range(24))
        avg_consumption = []
        
        for hour in hours:
            hour_data = data[data['hour_of_day'] == hour]
            if len(hour_data) > 0:
                avg = hour_data['consumed_percent'].mean()
            else:
                avg = 0
            avg_consumption.append(avg)
        
        return {
            'hours': hours,
            'consumption': avg_consumption,
            'cat_id': cat_id
        } 