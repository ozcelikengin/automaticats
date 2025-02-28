# AutomatiCats Machine Learning Integration

This document provides an overview of the machine learning components added to the AutomatiCats project during Sprint 5. The ML functionality focuses on feeding pattern recognition and generating smart recommendations to optimize cat nutrition and wellbeing.

## Table of Contents
1. [Overview](#overview)
2. [Components](#components)
3. [Data Collection](#data-collection)
4. [ML Models](#ml-models)
5. [Database Schema](#database-schema)
6. [User Interface](#user-interface)
7. [Getting Started](#getting-started)
8. [Running Tests](#running-tests)
9. [Future Enhancements](#future-enhancements)

## Overview

The machine learning system in AutomatiCats analyzes historical feeding data to identify patterns and provide personalized recommendations. The implementation includes:

- **Pattern Recognition**: Identifying when cats prefer to eat, which foods they prefer, and how their consumption varies over time.
- **Smart Recommendations**: Suggesting optimal feeding times, portion sizes, and food types based on learned patterns.
- **Visualization**: Visual presentation of feeding patterns and insights.
- **Feedback Loop**: Collection of user feedback to improve future recommendations.

## Components

The ML implementation consists of the following key components:

```
core/
  ├── ml_engine.py           # Core ML functionality and prediction models
database/
  ├── schema_update_ml.sql   # Database schema updates for ML features
gui/tabs/
  ├── ml_recommendations_tab.py  # UI tab for ML recommendations
scripts/
  ├── collect_ml_data.py     # Script for collecting and processing ML training data
tests/
  ├── test_ml_engine.py      # Unit tests for ML functionality
```

## Data Collection

The `collect_ml_data.py` script prepares data for machine learning by:

1. Retrieving historical feeding logs from the database
2. Calculating additional metrics needed for ML:
   - Meal duration
   - Consumption rate (grams per minute)
   - Leftover food amounts
3. Analyzing patterns in feeding behavior
4. Storing the derived metrics and patterns back in the database

To run the data collection script:

```
python scripts/collect_ml_data.py --days 30
```

Use the `--debug` flag to generate random data for testing:

```
python scripts/collect_ml_data.py --days 30 --debug
```

## ML Models

The system implements three core prediction models:

1. **Feeding Time Prediction**: Predicts when a cat prefers to eat based on historical patterns.
2. **Portion Size Recommendation**: Suggests optimal portion sizes based on cat-specific factors.
3. **Food Preference Prediction**: Recommends food types that a cat is likely to prefer.

All models use RandomForest algorithms, which provide robust performance even with limited data. The models automatically improve over time as more feeding data is collected.

## Database Schema

The ML functionality is supported by the following database tables:

- `ml_models`: Stores information about trained models
- `feeding_recommendations`: Records recommendations and user feedback
- `ml_feature_importance`: Tracks which features influence predictions most
- `ml_training_sessions`: Logs model training history
- `feeding_patterns`: Stores detected feeding patterns

Additional columns were added to the `feeding_logs` table to support ML metrics.

## User Interface

The ML functionality is presented through a new "Smart Insights" tab in the main application, which includes:

- **Recommendations Panel**: Shows actionable recommendations with confidence scores
- **Feeding Patterns**: Visualizes patterns in feeding behavior
- **ML Stats**: Displays model performance metrics and feature importance

Each recommendation includes:
- A clear explanation of what is being recommended
- The confidence level of the recommendation
- Options to apply or ignore the recommendation

## Getting Started

To use the ML features in AutomatiCats:

1. Ensure you have the required dependencies installed:
   ```
   pip install scikit-learn numpy pandas matplotlib
   ```

2. Run the data collection script to prepare initial data:
   ```
   python scripts/collect_ml_data.py --days 30
   ```

3. Launch the application and navigate to the "Smart Insights" tab:
   ```
   python main.py
   ```

4. Click the "Train Model" button to train the initial ML models

## Running Tests

To run tests for the ML components:

```
python -m unittest tests/test_ml_engine.py
```

Or run all tests with pytest:

```
pytest
```

## Future Enhancements

Planned improvements for future sprints:

1. **Advanced Time-Series Analysis**: Implementing more sophisticated algorithms for temporal pattern detection
2. **Anomaly Detection**: Identifying unusual feeding patterns that may indicate health issues
3. **Multi-Cat Comparative Analysis**: Comparing patterns across multiple cats
4. **Environmental Factors**: Integrating weather, season, and other environmental data into predictions
5. **Interactive Visualizations**: Adding more detailed and interactive charts
6. **Reinforcement Learning**: Enhancing the feedback loop to improve recommendation quality over time 