-- Schema update for ML features in AutomatiCats
-- Sprint 5: Adding ML-related tables and columns

-- Add columns to feeding_logs for ML metrics
ALTER TABLE feeding_logs ADD COLUMN meal_duration_minutes REAL;
ALTER TABLE feeding_logs ADD COLUMN consumption_rate_grams_per_minute REAL;
ALTER TABLE feeding_logs ADD COLUMN leftover_amount_grams REAL;

-- Create table for storing ML models
CREATE TABLE ml_models (
    model_id INTEGER PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_type TEXT NOT NULL,
    model_file_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accuracy_metric REAL,
    version TEXT,
    is_active INTEGER DEFAULT 1
);

-- Create table for feeding recommendations
CREATE TABLE feeding_recommendations (
    recommendation_id INTEGER PRIMARY KEY,
    cat_id INTEGER NOT NULL,
    model_id INTEGER,
    recommendation_type TEXT NOT NULL, -- 'feeding_time', 'portion_size', 'food_type'
    recommended_value TEXT NOT NULL,
    confidence_score REAL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_viewed INTEGER DEFAULT 0,
    is_applied INTEGER DEFAULT 0,
    feedback_rating INTEGER, -- 1-5 scale or NULL if not rated
    FOREIGN KEY (cat_id) REFERENCES cats(cat_id),
    FOREIGN KEY (model_id) REFERENCES ml_models(model_id)
);

-- Create table for feature importance tracking
CREATE TABLE ml_feature_importance (
    feature_id INTEGER PRIMARY KEY,
    model_id INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    importance_score REAL NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES ml_models(model_id)
);

-- Create table for ML training sessions
CREATE TABLE ml_training_sessions (
    session_id INTEGER PRIMARY KEY,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT, -- 'in_progress', 'completed', 'failed'
    error_message TEXT,
    cat_id INTEGER, -- NULL if trained on all cats
    data_points_used INTEGER,
    training_duration_seconds REAL,
    FOREIGN KEY (cat_id) REFERENCES cats(cat_id)
);

-- Create table for feeding patterns
CREATE TABLE feeding_patterns (
    pattern_id INTEGER PRIMARY KEY,
    cat_id INTEGER NOT NULL,
    pattern_type TEXT NOT NULL, -- 'time_preference', 'portion_preference', 'food_preference'
    pattern_data TEXT NOT NULL, -- JSON string with pattern details
    confidence_score REAL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (cat_id) REFERENCES cats(cat_id)
);

-- Create index for efficient recommendation queries
CREATE INDEX idx_recommendations_cat ON feeding_recommendations(cat_id, recommendation_type, generated_at);

-- Create index for pattern queries
CREATE INDEX idx_patterns_cat ON feeding_patterns(cat_id, pattern_type, detected_at); 