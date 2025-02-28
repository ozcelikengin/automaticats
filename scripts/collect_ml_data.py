#!/usr/bin/env python3
"""
ML Data Collection Script for AutomatiCats

This script collects data from feeding logs and generates ML metrics
for feeding pattern recognition and smart recommendations.
"""

import os
import sys
import argparse
import logging
import sqlite3
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

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
logger = logging.getLogger('ml_data_collection')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Collect ML training data from feeding logs')
    parser.add_argument('--days', type=int, default=30, help='Number of days of data to process')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with random data generation')
    return parser.parse_args()

def collect_feeding_logs(db_manager, days=30, debug=False):
    """Collect feeding logs from the database for the specified number of days."""
    try:
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d 00:00:00')
        
        cursor = db_manager.conn.cursor()
        query = '''
            SELECT fl.*, c.name as cat_name
            FROM feeding_logs fl
            JOIN cats c ON fl.cat_id = c.id
            WHERE fl.timestamp >= ?
            ORDER BY fl.timestamp
        '''
        cursor.execute(query, (start_date,))
        logs = cursor.fetchall()
        
        logger.info(f"Retrieved {len(logs)} feeding logs for the past {days} days")
        
        if not logs and debug:
            # Generate sample data in debug mode
            logger.info("Generating sample feeding logs for debug mode")
            sample_logs = generate_sample_logs(db_manager, days)
            return sample_logs
        
        return logs
    except Exception as e:
        logger.error(f"Error collecting feeding logs: {e}")
        return []

def generate_sample_logs(db_manager, days=30):
    """Generate sample feeding logs for debug mode."""
    try:
        # Get cats from database or create sample cats if none exist
        cursor = db_manager.conn.cursor()
        cursor.execute('SELECT * FROM cats')
        cats = cursor.fetchall()
        
        if not cats:
            # Add sample cats if none exist
            cat_ids = []
            for name in ['Whiskers', 'Mittens', 'Luna']:
                cursor.execute('''
                    INSERT INTO cats (name, age, weight)
                    VALUES (?, ?, ?)
                ''', (name, random.uniform(1, 15), random.uniform(2.5, 6.5)))
                cat_ids.append(cursor.lastrowid)
            db_manager.conn.commit()
        else:
            cat_ids = [cat['id'] for cat in cats]
        
        # Generate sample logs
        sample_logs = []
        food_types = ['Dry', 'Wet', 'Treats']
        now = datetime.now()
        
        for day in range(days):
            for cat_id in cat_ids:
                # 2-3 feedings per day
                for _ in range(random.randint(2, 3)):
                    timestamp = now - timedelta(days=day, 
                                               hours=random.randint(0, 23),
                                               minutes=random.randint(0, 59))
                    food_type = random.choice(food_types)
                    amount = random.uniform(20, 100) if food_type == 'Dry' else random.uniform(50, 150)
                    
                    # Insert the log
                    cursor.execute('''
                        INSERT INTO feeding_logs (cat_id, food_type, amount, timestamp, is_manual)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (cat_id, food_type, amount, timestamp, random.choice([0, 1])))
                    
                    # Create a sample log dict for immediate use
                    log = {
                        'id': cursor.lastrowid,
                        'cat_id': cat_id,
                        'food_type': food_type,
                        'amount': amount,
                        'timestamp': timestamp,
                        'is_manual': random.choice([0, 1])
                    }
                    sample_logs.append(log)
        
        db_manager.conn.commit()
        logger.info(f"Generated {len(sample_logs)} sample feeding logs")
        
        # Retrieve the actual logs from the database
        cursor.execute('''
            SELECT fl.*, c.name as cat_name
            FROM feeding_logs fl
            JOIN cats c ON fl.cat_id = c.id
            ORDER BY fl.timestamp
        ''')
        return cursor.fetchall()
    
    except Exception as e:
        logger.error(f"Error generating sample logs: {e}")
        return []

def generate_ml_metrics(feeding_logs):
    """Generate ML metrics from feeding logs."""
    if not feeding_logs:
        logger.warning("No feeding logs to generate metrics from")
        return []
    
    logger.info(f"Generating ML metrics from {len(feeding_logs)} feeding logs")
    
    # Convert logs to DataFrame for easier analysis
    df = pd.DataFrame([dict(row) for row in feeding_logs])
    
    # Ensure timestamp is datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Add additional ML metrics
    metrics = []
    
    for _, log in df.iterrows():
        # Calculate meal duration (random for now, would be actual duration in real system)
        meal_duration = random.uniform(2, 15)  # minutes
        
        # Calculate consumption rate
        consumption_rate = log['amount'] / meal_duration if meal_duration > 0 else 0
        
        # Calculate leftover food (random for demonstration)
        leftover = random.uniform(0, log['amount'] * 0.3)
        
        # Create metrics dict
        metric = {
            'log_id': log['id'],
            'cat_id': log['cat_id'],
            'meal_duration': meal_duration,
            'consumption_rate': consumption_rate,
            'leftover_food': leftover,
            'time_of_day': log['timestamp'].hour
        }
        metrics.append(metric)
    
    logger.info(f"Generated {len(metrics)} ML metrics")
    return metrics

def update_feeding_logs(db_manager, metrics):
    """Update feeding logs with ML metrics."""
    if not metrics:
        logger.warning("No metrics to update")
        return
    
    try:
        cursor = db_manager.conn.cursor()
        
        # Check if ML metrics columns exist, add them if not
        cursor.execute("PRAGMA table_info(feeding_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        column_mapping = {
            'meal_duration': 'meal_duration_minutes',
            'consumption_rate': 'consumption_rate_grams_per_minute',
            'leftover_food': 'leftover_amount_grams'
        }
        
        # Update logs with metrics
        for metric in metrics:
            cursor.execute('''
                UPDATE feeding_logs
                SET meal_duration_minutes = ?,
                    consumption_rate_grams_per_minute = ?,
                    leftover_amount_grams = ?
                WHERE id = ?
            ''', (
                metric['meal_duration'],
                metric['consumption_rate'],
                metric['leftover_food'],
                metric['log_id']
            ))
        
        db_manager.conn.commit()
        logger.info(f"Updated {len(metrics)} feeding logs with ML metrics")
    except Exception as e:
        logger.error(f"Error updating feeding logs with metrics: {e}")
        db_manager.conn.rollback()

def analyze_time_preference(db_manager, cat_id):
    """Analyze feeding time preference for a cat."""
    try:
        cursor = db_manager.conn.cursor()
        cursor.execute('''
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as frequency
            FROM feeding_logs
            WHERE cat_id = ?
            GROUP BY hour
            ORDER BY frequency DESC
        ''', (cat_id,))
        results = cursor.fetchall()
        
        # Get the preferred time periods
        morning_count = 0
        afternoon_count = 0
        evening_count = 0
        night_count = 0
        
        for result in results:
            hour = int(result['hour'])
            freq = result['frequency']
            
            if 5 <= hour < 12:
                morning_count += freq
            elif 12 <= hour < 17:
                afternoon_count += freq
            elif 17 <= hour < 22:
                evening_count += freq
            else:
                night_count += freq
        
        # Determine preferred time
        periods = {
            'Morning (5am-12pm)': morning_count,
            'Afternoon (12pm-5pm)': afternoon_count,
            'Evening (5pm-10pm)': evening_count,
            'Night (10pm-5am)': night_count
        }
        
        preferred_time = max(periods, key=periods.get)
        confidence = periods[preferred_time] / sum(periods.values()) if sum(periods.values()) > 0 else 0
        
        return {
            'preferred_time': preferred_time,
            'confidence': confidence,
            'time_distribution': periods
        }
    except Exception as e:
        logger.error(f"Error analyzing time preference: {e}")
        return None

def analyze_food_preference(db_manager, cat_id):
    """Analyze food type preference for a cat."""
    try:
        cursor = db_manager.conn.cursor()
        cursor.execute('''
            SELECT 
                food_type,
                COUNT(*) as frequency,
                AVG(amount) as avg_amount,
                AVG(COALESCE(leftover_amount_grams, 0)) as avg_leftover
            FROM feeding_logs
            WHERE cat_id = ?
            GROUP BY food_type
            ORDER BY frequency DESC
        ''', (cat_id,))
        results = cursor.fetchall()
        
        if not results:
            return None
        
        # Calculate preference based on frequency and leftover
        preferences = {}
        for result in results:
            food_type = result['food_type']
            frequency = result['frequency']
            avg_leftover_ratio = result['avg_leftover'] / result['avg_amount'] if result['avg_amount'] > 0 else 0
            
            # Higher score = more preferred (more frequency, less leftover)
            preference_score = frequency * (1 - avg_leftover_ratio)
            preferences[food_type] = preference_score
        
        # Get preferred food type
        preferred_food = max(preferences, key=preferences.get)
        total_score = sum(preferences.values())
        confidence = preferences[preferred_food] / total_score if total_score > 0 else 0
        
        return {
            'preferred_food': preferred_food,
            'confidence': confidence,
            'food_distribution': preferences
        }
    except Exception as e:
        logger.error(f"Error analyzing food preference: {e}")
        return None

def analyze_consumption_pattern(db_manager, cat_id):
    """Analyze consumption patterns for a cat."""
    try:
        cursor = db_manager.conn.cursor()
        cursor.execute('''
            SELECT 
                AVG(amount) as avg_amount,
                AVG(COALESCE(meal_duration_minutes, 0)) as avg_duration,
                AVG(COALESCE(consumption_rate_grams_per_minute, 0)) as avg_rate,
                food_type
            FROM feeding_logs
            WHERE cat_id = ?
            GROUP BY food_type
        ''', (cat_id,))
        results = cursor.fetchall()
        
        if not results:
            return None
        
        consumption_patterns = {}
        for result in results:
            food_type = result['food_type']
            consumption_patterns[food_type] = {
                'avg_amount': result['avg_amount'],
                'avg_duration': result['avg_duration'],
                'avg_rate': result['avg_rate']
            }
        
        return {
            'consumption_patterns': consumption_patterns
        }
    except Exception as e:
        logger.error(f"Error analyzing consumption pattern: {e}")
        return None

def analyze_patterns(db_manager):
    """Analyze feeding patterns for all cats."""
    try:
        # Get all cats
        cursor = db_manager.conn.cursor()
        cursor.execute('SELECT * FROM cats')
        cats = cursor.fetchall()
        
        if not cats:
            logger.warning("No cats found in database")
            return
        
        patterns = []
        for cat in cats:
            cat_id = cat['id']
            cat_name = cat['name']
            
            logger.info(f"Analyzing patterns for cat: {cat_name}")
            
            # Analyze different aspects of feeding behavior
            time_pref = analyze_time_preference(db_manager, cat_id)
            food_pref = analyze_food_preference(db_manager, cat_id)
            consumption = analyze_consumption_pattern(db_manager, cat_id)
            
            # Skip if no meaningful data
            if not time_pref or not food_pref or not consumption:
                logger.warning(f"Insufficient data for cat {cat_name}")
                continue
            
            # Create pattern entry
            pattern = {
                'cat_id': cat_id,
                'cat_name': cat_name,
                'timestamp': datetime.now(),
                'time_preference': time_pref['preferred_time'],
                'time_confidence': time_pref['confidence'],
                'food_preference': food_pref['preferred_food'],
                'food_confidence': food_pref['confidence'],
                'avg_consumption_rate': next(iter(consumption['consumption_patterns'].values()))['avg_rate'],
                'pattern_data': {
                    'time': time_pref,
                    'food': food_pref,
                    'consumption': consumption
                }
            }
            
            patterns.append(pattern)
            
            # Save the pattern
            save_pattern(db_manager, pattern)
        
        logger.info(f"Analyzed patterns for {len(patterns)} cats")
    except Exception as e:
        logger.error(f"Error analyzing patterns: {e}")

def save_pattern(db_manager, pattern):
    """Save the analyzed pattern to the database."""
    try:
        cursor = db_manager.conn.cursor()
        
        # Convert pattern_data to JSON
        import json
        
        # Save time preference pattern
        time_pattern_data = {
            'preferred_time': pattern['time_preference'],
            'confidence': pattern['time_confidence'],
            'distribution': pattern['pattern_data']['time']['time_distribution']
        }
        
        cursor.execute('''
            INSERT INTO feeding_patterns (
                cat_id, pattern_type, pattern_data, confidence_score
            ) VALUES (?, ?, ?, ?)
        ''', (
            pattern['cat_id'],
            'time_preference',
            json.dumps(time_pattern_data),
            pattern['time_confidence']
        ))
        
        # Save food preference pattern
        food_pattern_data = {
            'preferred_food': pattern['food_preference'],
            'confidence': pattern['food_confidence'],
            'distribution': pattern['pattern_data']['food']['food_distribution']
        }
        
        cursor.execute('''
            INSERT INTO feeding_patterns (
                cat_id, pattern_type, pattern_data, confidence_score
            ) VALUES (?, ?, ?, ?)
        ''', (
            pattern['cat_id'],
            'food_preference',
            json.dumps(food_pattern_data),
            pattern['food_confidence']
        ))
        
        # Save consumption pattern
        consumption_pattern_data = {
            'avg_consumption_rate': pattern['avg_consumption_rate'],
            'patterns': pattern['pattern_data']['consumption']['consumption_patterns']
        }
        
        cursor.execute('''
            INSERT INTO feeding_patterns (
                cat_id, pattern_type, pattern_data, confidence_score
            ) VALUES (?, ?, ?, ?)
        ''', (
            pattern['cat_id'],
            'consumption_pattern',
            json.dumps(consumption_pattern_data),
            0.75  # Default confidence for consumption patterns
        ))
        
        db_manager.conn.commit()
        logger.info(f"Saved feeding patterns for cat ID {pattern['cat_id']}")
    except Exception as e:
        logger.error(f"Error saving pattern: {e}")
        db_manager.conn.rollback()

def main():
    """Main function to run the ML data collection script."""
    args = parse_arguments()
    
    logger.info("Starting ML data collection")
    logger.info(f"Processing {args.days} days of data")
    
    if args.debug:
        logger.info("Debug mode enabled - will generate random metrics")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    try:
        # Collect feeding logs
        logger.info(f"Collecting feeding logs for the past {args.days} days")
        feeding_logs = collect_feeding_logs(db_manager, args.days, args.debug)
        
        if not feeding_logs:
            logger.warning("No feeding logs found, exiting")
            db_manager.close()
            return
        
        # Generate ML metrics
        metrics = generate_ml_metrics(feeding_logs)
        
        # Update feeding logs with metrics
        update_feeding_logs(db_manager, metrics)
        
        # Analyze feeding patterns
        analyze_patterns(db_manager)
        
        logger.info("ML data collection completed successfully")
    except Exception as e:
        logger.error(f"Error in ML data collection: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    main() 