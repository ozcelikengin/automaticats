"""
Machine Learning Recommendations Tab for AutomatiCats

This tab displays ML-based recommendations and insights for cat feeding patterns.
"""

import logging
import json
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QPushButton, QGroupBox, QTabWidget, QScrollArea, QFrame,
                             QSizePolicy, QSpacerItem, QProgressBar, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QPalette, QFont

from core.ml_engine import MLEngine

# Configure logging
logger = logging.getLogger('automaticats.gui.ml_recommendations_tab')

class RecommendationWidget(QFrame):
    """Widget to display a single ML recommendation with accept/reject options"""
    
    feedback_given = Signal(int, bool, object)  # recommendation_id, accepted, value
    
    def __init__(self, recommendation, parent=None):
        super().__init__(parent)
        self.recommendation = recommendation
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components for this recommendation widget"""
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            RecommendationWidget {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #f9f9f9;
                margin: 5px;
                padding: 10px;
            }
            QLabel.title {
                font-weight: bold;
                font-size: 14px;
                color: #333333;
            }
            QLabel.confidence {
                font-style: italic;
                color: #666666;
            }
            QPushButton.accept {
                background-color: #4CAF50;
                color: white;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton.reject {
                background-color: #f44336;
                color: white;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Recommendation type
        rec_type = self.recommendation['type'].replace('_', ' ').title()
        type_label = QLabel(f"{rec_type}")
        type_label.setProperty("class", "title")
        layout.addWidget(type_label)
        
        # Recommendation message
        message_label = QLabel(self.recommendation['message'])
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Confidence score
        confidence = int(self.recommendation['confidence'] * 100)
        confidence_label = QLabel(f"Confidence: {confidence}%")
        confidence_label.setProperty("class", "confidence")
        layout.addWidget(confidence_label)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Accept button
        accept_button = QPushButton("Apply")
        accept_button.setProperty("class", "accept")
        accept_button.clicked.connect(self.on_accept)
        button_layout.addWidget(accept_button)
        
        # Reject button
        reject_button = QPushButton("Ignore")
        reject_button.setProperty("class", "reject")
        reject_button.clicked.connect(self.on_reject)
        button_layout.addWidget(reject_button)
        
        layout.addLayout(button_layout)
        
    def on_accept(self):
        """Handle acceptance of recommendation"""
        logger.info(f"Accepted recommendation: {self.recommendation['type']}")
        self.feedback_given.emit(
            id(self.recommendation), True, self.recommendation['value']
        )
        self.setVisible(False)
        
    def on_reject(self):
        """Handle rejection of recommendation"""
        logger.info(f"Rejected recommendation: {self.recommendation['type']}")
        self.feedback_given.emit(
            id(self.recommendation), False, None
        )
        self.setVisible(False)


class PatternChart(QFrame):
    """Simple visualization of feeding patterns"""
    
    def __init__(self, pattern_data, title="Feeding Pattern", parent=None):
        super().__init__(parent)
        self.pattern_data = pattern_data
        self.title = title
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components for this pattern visualization"""
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(200)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        # Pattern visualization - simplified version using progress bars
        # In a real app, this would use matplotlib or another charting library
        self.chart_widget = QWidget()
        chart_layout = QHBoxLayout()
        self.chart_widget.setLayout(chart_layout)
        
        # For our example, we'll visualize hourly consumption
        hours = self.pattern_data.get('hours', list(range(24)))
        consumption = self.pattern_data.get('consumption', [0] * 24)
        
        # Group into 4-hour blocks for simplicity
        blocks = 6
        block_values = []
        
        for i in range(blocks):
            start_hour = i * (24 // blocks)
            end_hour = (i + 1) * (24 // blocks) - 1
            block_consumption = sum(consumption[start_hour:end_hour+1]) / (24 // blocks)
            block_values.append((f"{start_hour:02d}-{end_hour:02d}", block_consumption))
        
        # Create the bar chart
        for label, value in block_values:
            bar_layout = QVBoxLayout()
            
            # Progress bar as our bar
            bar = QProgressBar()
            bar.setOrientation(Qt.Vertical)
            bar.setMaximum(100)
            bar.setValue(min(int(value), 100))
            bar.setTextVisible(False)
            bar.setFixedWidth(30)
            bar.setMinimumHeight(100)
            
            # Time label
            time_label = QLabel(label)
            time_label.setAlignment(Qt.AlignCenter)
            
            bar_layout.addWidget(bar, 1)
            bar_layout.addWidget(time_label)
            bar_layout.setAlignment(Qt.AlignBottom)
            
            chart_layout.addLayout(bar_layout)
        
        layout.addWidget(self.chart_widget)


class MLRecommendationsTab(QWidget):
    """Tab displaying machine learning recommendations and insights"""
    
    # Signals
    recommendations_updated = Signal()
    feedback_submitted = Signal(int, bool, object)  # recommendation_id, accepted, value
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.ml_engine = MLEngine(db_manager)
        self.selected_cat_id = None
        self.recommendations = []
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components for the ML Recommendations tab"""
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header with title and cat selector
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Smart Feeding Insights")
        title_label.setFont(QFont("", 14, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Cat selector
        cat_label = QLabel("Select Cat:")
        header_layout.addWidget(cat_label)
        
        self.cat_combo = QComboBox()
        self.cat_combo.setMinimumWidth(150)
        self.cat_combo.currentIndexChanged.connect(self.on_cat_selected)
        header_layout.addWidget(self.cat_combo)
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_recommendations)
        header_layout.addWidget(refresh_button)
        
        # Train model button
        train_button = QPushButton("Train Model")
        train_button.clicked.connect(self.train_models)
        header_layout.addWidget(train_button)
        
        layout.addLayout(header_layout)
        
        # Tab widget for different insights
        self.insights_tabs = QTabWidget()
        
        # Recommendations tab
        self.recommendations_tab = QWidget()
        self.recommendations_layout = QVBoxLayout()
        self.recommendations_tab.setLayout(self.recommendations_layout)
        
        # Scroll area for recommendations
        recommendations_scroll = QScrollArea()
        recommendations_scroll.setWidgetResizable(True)
        
        self.recommendations_container = QWidget()
        self.recommendations_container_layout = QVBoxLayout()
        self.recommendations_container.setLayout(self.recommendations_container_layout)
        
        recommendations_scroll.setWidget(self.recommendations_container)
        self.recommendations_layout.addWidget(recommendations_scroll)
        
        # Patterns tab
        self.patterns_tab = QWidget()
        self.patterns_layout = QVBoxLayout()
        self.patterns_tab.setLayout(self.patterns_layout)
        
        # Stats tab
        self.stats_tab = QWidget()
        self.stats_layout = QVBoxLayout()
        self.stats_tab.setLayout(self.stats_layout)
        
        # Add tabs
        self.insights_tabs.addTab(self.recommendations_tab, "Recommendations")
        self.insights_tabs.addTab(self.patterns_tab, "Feeding Patterns")
        self.insights_tabs.addTab(self.stats_tab, "ML Stats")
        
        layout.addWidget(self.insights_tabs)
        
        # Populate cat combo box
        self.populate_cats()
        
        # Populate patterns tab with placeholder
        self.populate_patterns_tab()
        
        # Populate stats tab with placeholder
        self.populate_stats_tab()
    
    def populate_cats(self):
        """Populate the cat selector combo box"""
        try:
            # Clear existing items
            self.cat_combo.clear()
            
            # Add 'All Cats' option
            self.cat_combo.addItem("All Cats", -1)
            
            # Get cats from database
            cats = self.db_manager.get_cats()
            
            # Add cats to combo box
            for cat in cats:
                self.cat_combo.addItem(cat['name'], cat['cat_id'])
                
        except Exception as e:
            logger.error(f"Error populating cats: {e}")
    
    @Slot(int)
    def on_cat_selected(self, index):
        """Handle cat selection"""
        cat_id = self.cat_combo.itemData(index)
        self.selected_cat_id = None if cat_id == -1 else cat_id
        self.refresh_recommendations()
    
    def refresh_recommendations(self):
        """Refresh recommendations based on selected cat"""
        # Clear existing recommendations
        self.clear_recommendations()
        
        try:
            # If no cat is selected or 'All Cats' is selected
            if self.selected_cat_id is None or self.selected_cat_id == -1:
                # Get recommendations for all cats
                cats = self.db_manager.get_cats()
                for cat in cats:
                    cat_recommendations = self.ml_engine.get_recommendations(cat['cat_id'])
                    self.recommendations.extend(cat_recommendations)
            else:
                # Get recommendations for selected cat
                self.recommendations = self.ml_engine.get_recommendations(self.selected_cat_id)
            
            # Display recommendations
            self.display_recommendations()
            
        except Exception as e:
            logger.error(f"Error refreshing recommendations: {e}")
            # Add error message to UI
            error_label = QLabel(f"Error loading recommendations: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.recommendations_container_layout.addWidget(error_label)
    
    def clear_recommendations(self):
        """Clear all recommendation widgets"""
        # Clear the layout
        while self.recommendations_container_layout.count():
            item = self.recommendations_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def display_recommendations(self):
        """Display recommendations in the UI"""
        # If no recommendations, show message
        if not self.recommendations:
            no_rec_label = QLabel("No recommendations available. You may need to train the model first.")
            no_rec_label.setAlignment(Qt.AlignCenter)
            no_rec_label.setStyleSheet("color: #666; font-style: italic;")
            self.recommendations_container_layout.addWidget(no_rec_label)
            return
        
        # Add each recommendation
        for rec in self.recommendations:
            rec_widget = RecommendationWidget(rec)
            rec_widget.feedback_given.connect(self.on_feedback_given)
            self.recommendations_container_layout.addWidget(rec_widget)
        
        # Add stretch to push recommendations to the top
        self.recommendations_container_layout.addStretch()
    
    @Slot(int, bool, object)
    def on_feedback_given(self, rec_id, accepted, value):
        """Handle feedback on a recommendation"""
        try:
            # Record feedback
            self.ml_engine.record_feedback(rec_id, accepted, value)
            
            # Emit signal for other components
            self.feedback_submitted.emit(rec_id, accepted, value)
            
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
    
    def train_models(self):
        """Train ML models for the selected cat"""
        try:
            # Train the models
            success = self.ml_engine.train_models(self.selected_cat_id)
            
            # Show result
            if success:
                label = QLabel("Models trained successfully!")
                label.setStyleSheet("color: green; font-weight: bold;")
            else:
                label = QLabel("Model training failed. Check logs for details.")
                label.setStyleSheet("color: red;")
            
            # Add to layout with a brief timeout
            self.recommendations_layout.addWidget(label)
            
            # Refresh recommendations
            self.refresh_recommendations()
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            label = QLabel(f"Error training models: {str(e)}")
            label.setStyleSheet("color: red;")
            self.recommendations_layout.addWidget(label)
    
    def populate_patterns_tab(self):
        """Populate the patterns tab with visualizations"""
        # Clear existing content
        while self.patterns_layout.count():
            item = self.patterns_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # If no cat is selected, show message
        if not self.selected_cat_id or self.selected_cat_id == -1:
            no_cat_label = QLabel("Please select a cat to view feeding patterns")
            no_cat_label.setAlignment(Qt.AlignCenter)
            no_cat_label.setStyleSheet("color: #666; font-style: italic;")
            self.patterns_layout.addWidget(no_cat_label)
            return
        
        try:
            # Generate pattern data for the selected cat
            pattern_data = self.ml_engine.generate_pattern_analysis(self.selected_cat_id)
            
            # Add pattern chart
            feeding_chart = PatternChart(pattern_data, "Feeding Activity by Time of Day")
            self.patterns_layout.addWidget(feeding_chart)
            
            # Additional pattern information
            info_box = QGroupBox("Pattern Insights")
            info_layout = QVBoxLayout()
            info_box.setLayout(info_layout)
            
            # Sample insights - in a real app, these would be generated from analysis
            insights = [
                "Peak feeding times are between 6-10am and 6-10pm",
                "Monday and Thursday show higher consumption rates",
                "Consumption rate decreases by 15% during weekends",
                "Food Type 2 is consumed 30% faster than other types"
            ]
            
            for insight in insights:
                label = QLabel(f"• {insight}")
                info_layout.addWidget(label)
            
            self.patterns_layout.addWidget(info_box)
            
            # Add stretch to push content to the top
            self.patterns_layout.addStretch()
            
        except Exception as e:
            logger.error(f"Error populating patterns tab: {e}")
            error_label = QLabel(f"Error loading patterns: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.patterns_layout.addWidget(error_label)
    
    def populate_stats_tab(self):
        """Populate the ML stats tab"""
        # Clear existing content
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        try:
            # Create table for model statistics
            stats_table = QTableWidget()
            stats_table.setColumnCount(5)
            stats_table.setHorizontalHeaderLabels([
                "Model Type", "Last Updated", "Accuracy", "Data Points", "Status"
            ])
            
            # Sample model stats - in a real app, these would come from the database
            model_stats = [
                {
                    "type": "Feeding Time Prediction",
                    "updated": "2023-04-18 14:32",
                    "accuracy": "82.5%",
                    "data_points": "128",
                    "status": "Active"
                },
                {
                    "type": "Portion Recommendation",
                    "updated": "2023-04-18 14:32",
                    "accuracy": "78.3%",
                    "data_points": "128",
                    "status": "Active"
                },
                {
                    "type": "Food Preference",
                    "updated": "2023-04-18 14:32",
                    "accuracy": "91.2%",
                    "data_points": "128",
                    "status": "Active"
                }
            ]
            
            # Populate table
            stats_table.setRowCount(len(model_stats))
            for row, stat in enumerate(model_stats):
                stats_table.setItem(row, 0, QTableWidgetItem(stat["type"]))
                stats_table.setItem(row, 1, QTableWidgetItem(stat["updated"]))
                stats_table.setItem(row, 2, QTableWidgetItem(stat["accuracy"]))
                stats_table.setItem(row, 3, QTableWidgetItem(stat["data_points"]))
                stats_table.setItem(row, 4, QTableWidgetItem(stat["status"]))
            
            # Resize columns to content
            stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Add to layout
            self.stats_layout.addWidget(QLabel("ML Model Statistics"))
            self.stats_layout.addWidget(stats_table)
            
            # Feature importance section
            importance_box = QGroupBox("Feature Importance")
            importance_layout = QVBoxLayout()
            importance_box.setLayout(importance_layout)
            
            # Sample feature importance data
            importance_data = [
                {"feature": "Day of Week", "importance": 0.35},
                {"feature": "Previous Consumption", "importance": 0.25},
                {"feature": "Time of Day", "importance": 0.20},
                {"feature": "Food Type", "importance": 0.15},
                {"feature": "Cat Age", "importance": 0.05}
            ]
            
            # Create layout for feature importance bars
            for feat in importance_data:
                feat_layout = QHBoxLayout()
                
                # Feature name
                name_label = QLabel(feat["feature"])
                name_label.setFixedWidth(150)
                feat_layout.addWidget(name_label)
                
                # Importance bar
                bar = QProgressBar()
                bar.setMaximum(100)
                bar.setValue(int(feat["importance"] * 100))
                bar.setTextVisible(True)
                bar.setFormat(f"{int(feat['importance'] * 100)}%")
                feat_layout.addWidget(bar)
                
                importance_layout.addLayout(feat_layout)
            
            self.stats_layout.addWidget(importance_box)
            
            # Add ML performance over time section (placeholder)
            time_box = QGroupBox("Model Performance Over Time")
            time_layout = QVBoxLayout()
            time_box.setLayout(time_layout)
            
            time_label = QLabel("Historical performance data visualization would appear here")
            time_label.setAlignment(Qt.AlignCenter)
            time_layout.addWidget(time_label)
            
            self.stats_layout.addWidget(time_box)
            
            # Add stretch to push content to the top
            self.stats_layout.addStretch()
            
        except Exception as e:
            logger.error(f"Error populating stats tab: {e}")
            error_label = QLabel(f"Error loading ML stats: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.stats_layout.addWidget(error_label)
    
    @Slot()
    def on_refresh(self):
        """Refresh all tab content"""
        self.refresh_recommendations()
        self.populate_patterns_tab()
        self.populate_stats_tab()
    
    def closeEvent(self, event):
        """Handle tab closing"""
        # Any cleanup needed before closing the tab
        event.accept() 