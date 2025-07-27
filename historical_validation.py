"""
Historical Data Expansion and Model Validation System
Store game results, odds, predictions for comprehensive model validation.
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Local imports
from error_handler import MLBErrorHandler, log_operation
from user_settings import MLBUserSettings


class MLBHistoricalDatabase:
    """
    Database management for historical MLB data storage and retrieval.
    """
    
    def __init__(self, db_path: str = "data/mlb_historical.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.error_handler = MLBErrorHandler()
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Games table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS games (
                        game_id TEXT PRIMARY KEY,
                        date DATE NOT NULL,
                        home_team TEXT NOT NULL,
                        away_team TEXT NOT NULL,
                        home_score INTEGER,
                        away_score INTEGER,
                        total_score INTEGER,
                        winner TEXT,
                        venue TEXT,
                        attendance INTEGER,
                        weather_temp REAL,
                        weather_wind REAL,
                        weather_humidity REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Predictions table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id TEXT NOT NULL,
                        model_name TEXT NOT NULL,
                        prediction_type TEXT NOT NULL, -- 'total_runs', 'winner', 'spread'
                        predicted_value REAL NOT NULL,
                        confidence REAL,
                        actual_value REAL,
                        prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (game_id) REFERENCES games (game_id)
                    )
                """)
                
                # Odds table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS odds (
                        odds_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id TEXT NOT NULL,
                        sportsbook TEXT NOT NULL,
                        bet_type TEXT NOT NULL, -- 'moneyline', 'total', 'spread'
                        home_odds REAL,
                        away_odds REAL,
                        total_line REAL,
                        over_odds REAL,
                        under_odds REAL,
                        spread_line REAL,
                        spread_home_odds REAL,
                        spread_away_odds REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (game_id) REFERENCES games (game_id)
                    )
                """)
                
                # Player stats table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS player_stats (
                        stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id TEXT NOT NULL,
                        player_id TEXT NOT NULL,
                        player_name TEXT NOT NULL,
                        team TEXT NOT NULL,
                        position TEXT,
                        at_bats INTEGER DEFAULT 0,
                        hits INTEGER DEFAULT 0,
                        runs INTEGER DEFAULT 0,
                        rbis INTEGER DEFAULT 0,
                        home_runs INTEGER DEFAULT 0,
                        walks INTEGER DEFAULT 0,
                        strikeouts INTEGER DEFAULT 0,
                        stolen_bases INTEGER DEFAULT 0,
                        -- Pitching stats
                        innings_pitched REAL DEFAULT 0,
                        earned_runs INTEGER DEFAULT 0,
                        pitch_count INTEGER DEFAULT 0,
                        FOREIGN KEY (game_id) REFERENCES games (game_id)
                    )
                """)
                
                # Model performance tracking
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS model_performance (
                        performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT NOT NULL,
                        prediction_type TEXT NOT NULL,
                        date DATE NOT NULL,
                        accuracy REAL,
                        mse REAL,
                        mae REAL,
                        r_squared REAL,
                        profit_loss REAL,
                        num_predictions INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_games_date ON games(date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_game_id ON predictions(game_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_odds_game_id ON odds(game_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_player_stats_game_id ON player_stats(game_id)")
                
                print("✅ Database initialized successfully")
                
        except Exception as e:
            self.error_handler.handle_error(e, "Database Initialization", "schema_creation")
    
    @log_operation("Store Game Data")
    def store_game(self, game_data: Dict) -> bool:
        """Store a single game's data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO games 
                    (game_id, date, home_team, away_team, home_score, away_score, 
                     total_score, winner, venue, attendance, weather_temp, weather_wind, weather_humidity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    game_data['game_id'],
                    game_data['date'],
                    game_data['home_team'],
                    game_data['away_team'],
                    game_data.get('home_score'),
                    game_data.get('away_score'),
                    game_data.get('total_score'),
                    game_data.get('winner'),
                    game_data.get('venue'),
                    game_data.get('attendance'),
                    game_data.get('weather_temp'),
                    game_data.get('weather_wind'),
                    game_data.get('weather_humidity')
                ))
                
            return True
            
        except Exception as e:
            self.error_handler.handle_error(e, "Store Game", f"game_id: {game_data.get('game_id')}")
            return False
    
    @log_operation("Store Prediction")
    def store_prediction(self, game_id: str, model_name: str, prediction_type: str, 
                        predicted_value: float, confidence: float = None) -> bool:
        """Store a model prediction."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO predictions 
                    (game_id, model_name, prediction_type, predicted_value, confidence)
                    VALUES (?, ?, ?, ?, ?)
                """, (game_id, model_name, prediction_type, predicted_value, confidence))
                
            return True
            
        except Exception as e:
            self.error_handler.handle_error(e, "Store Prediction", f"{model_name} - {game_id}")
            return False
    
    @log_operation("Update Prediction Results")
    def update_prediction_results(self, game_id: str, actual_results: Dict) -> bool:
        """Update predictions with actual results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for prediction_type, actual_value in actual_results.items():
                    conn.execute("""
                        UPDATE predictions 
                        SET actual_value = ?
                        WHERE game_id = ? AND prediction_type = ?
                    """, (actual_value, game_id, prediction_type))
                
            return True
            
        except Exception as e:
            self.error_handler.handle_error(e, "Update Results", f"game_id: {game_id}")
            return False
    
    def get_prediction_accuracy(self, model_name: str, prediction_type: str, 
                               days_back: int = 30) -> Dict:
        """Get prediction accuracy for a model."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query("""
                    SELECT predicted_value, actual_value, confidence
                    FROM predictions p
                    JOIN games g ON p.game_id = g.game_id
                    WHERE p.model_name = ? AND p.prediction_type = ?
                    AND p.actual_value IS NOT NULL
                    AND g.date >= date('now', '-{} days')
                    ORDER BY g.date DESC
                """.format(days_back), conn, params=(model_name, prediction_type))
                
            if df.empty:
                return {'error': 'No data available'}
            
            # Calculate metrics
            mae = np.mean(np.abs(df['predicted_value'] - df['actual_value']))
            mse = np.mean((df['predicted_value'] - df['actual_value']) ** 2)
            rmse = np.sqrt(mse)
            
            # R-squared
            ss_res = np.sum((df['actual_value'] - df['predicted_value']) ** 2)
            ss_tot = np.sum((df['actual_value'] - np.mean(df['actual_value'])) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Accuracy (within 1 unit for totals, exact for winners)
            if prediction_type == 'total_runs':
                accuracy = np.mean(np.abs(df['predicted_value'] - df['actual_value']) <= 1)
            else:
                accuracy = np.mean(df['predicted_value'] == df['actual_value'])
            
            return {
                'model_name': model_name,
                'prediction_type': prediction_type,
                'num_predictions': len(df),
                'accuracy': accuracy,
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'r_squared': r_squared,
                'avg_confidence': df['confidence'].mean() if df['confidence'].notna().any() else None
            }
            
        except Exception as e:
            self.error_handler.handle_error(e, "Get Accuracy", f"{model_name} - {prediction_type}")
            return {'error': str(e)}
    
    def get_historical_games(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get historical games data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query("""
                    SELECT * FROM games
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC
                """, conn, params=(start_date, end_date))
                
            return df
            
        except Exception as e:
            self.error_handler.handle_error(e, "Get Historical Games", f"{start_date} to {end_date}")
            return pd.DataFrame()


class ModelValidationSystem:
    """
    Comprehensive model validation and performance tracking.
    """
    
    def __init__(self, db: MLBHistoricalDatabase, settings: MLBUserSettings):
        self.db = db
        self.settings = settings
        self.error_handler = MLBErrorHandler()
    
    @log_operation("Validate Model Performance")
    def validate_model_performance(self, model_name: str, days_back: int = 30) -> Dict:
        """Comprehensive model validation."""
        try:
            results = {}
            
            # Get accuracy for different prediction types
            prediction_types = ['total_runs', 'winner', 'home_score', 'away_score']
            
            for pred_type in prediction_types:
                accuracy = self.db.get_prediction_accuracy(model_name, pred_type, days_back)
                if 'error' not in accuracy:
                    results[pred_type] = accuracy
            
            # Calculate overall performance score
            if results:
                overall_accuracy = np.mean([r['accuracy'] for r in results.values()])
                overall_rmse = np.mean([r['rmse'] for r in results.values()])
                
                results['overall'] = {
                    'accuracy': overall_accuracy,
                    'rmse': overall_rmse,
                    'performance_score': self._calculate_performance_score(results)
                }
            
            return results
            
        except Exception as e:
            self.error_handler.handle_error(e, "Model Validation", model_name)
            return {'error': str(e)}
    
    def _calculate_performance_score(self, results: Dict) -> float:
        """Calculate composite performance score."""
        try:
            weights = {
                'total_runs': 0.4,  # Most important for betting
                'winner': 0.3,
                'home_score': 0.15,
                'away_score': 0.15
            }
            
            weighted_score = 0
            total_weight = 0
            
            for pred_type, weight in weights.items():
                if pred_type in results:
                    # Combine accuracy and R-squared
                    type_score = (results[pred_type]['accuracy'] * 0.6 + 
                                 max(0, results[pred_type]['r_squared']) * 0.4)
                    weighted_score += type_score * weight
                    total_weight += weight
            
            return weighted_score / total_weight if total_weight > 0 else 0
            
        except Exception as e:
            self.error_handler.handle_error(e, "Performance Score", "calculation")
            return 0
    
    @log_operation("Generate Validation Report")
    def generate_validation_report(self, models: List[str], days_back: int = 30) -> Dict:
        """Generate comprehensive validation report."""
        try:
            report = {
                'report_date': datetime.now().isoformat(),
                'validation_period': f"{days_back} days",
                'models': {}
            }
            
            for model_name in models:
                model_results = self.validate_model_performance(model_name, days_back)
                if 'error' not in model_results:
                    report['models'][model_name] = model_results
            
            # Model comparison
            if len(report['models']) > 1:
                report['comparison'] = self._compare_models(report['models'])
            
            # Recommendations
            report['recommendations'] = self._generate_recommendations(report['models'])
            
            return report
            
        except Exception as e:
            self.error_handler.handle_error(e, "Validation Report", f"{len(models)} models")
            return {'error': str(e)}
    
    def _compare_models(self, models: Dict) -> Dict:
        """Compare model performances."""
        try:
            comparison = {}
            
            # Overall performance ranking
            model_scores = {
                name: results.get('overall', {}).get('performance_score', 0)
                for name, results in models.items()
            }
            
            sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
            comparison['ranking'] = [{'model': name, 'score': score} for name, score in sorted_models]
            
            # Best model by prediction type
            prediction_types = ['total_runs', 'winner', 'home_score', 'away_score']
            comparison['best_by_type'] = {}
            
            for pred_type in prediction_types:
                best_accuracy = 0
                best_model = None
                
                for model_name, results in models.items():
                    if pred_type in results:
                        accuracy = results[pred_type]['accuracy']
                        if accuracy > best_accuracy:
                            best_accuracy = accuracy
                            best_model = model_name
                
                if best_model:
                    comparison['best_by_type'][pred_type] = {
                        'model': best_model,
                        'accuracy': best_accuracy
                    }
            
            return comparison
            
        except Exception as e:
            self.error_handler.handle_error(e, "Model Comparison", "analysis")
            return {}
    
    def _generate_recommendations(self, models: Dict) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        try:
            for model_name, results in models.items():
                if 'overall' in results:
                    performance = results['overall']['performance_score']
                    
                    if performance < 0.6:
                        recommendations.append(f"⚠️ {model_name}: Low performance ({performance:.2f}). Consider retraining with more data.")
                    elif performance < 0.7:
                        recommendations.append(f"🔄 {model_name}: Moderate performance ({performance:.2f}). Review feature engineering.")
                    else:
                        recommendations.append(f"✅ {model_name}: Good performance ({performance:.2f}). Monitor for consistency.")
                
                # Check individual prediction types
                for pred_type in ['total_runs', 'winner']:
                    if pred_type in results:
                        accuracy = results[pred_type]['accuracy']
                        if accuracy < 0.55:
                            recommendations.append(f"📉 {model_name}: Low {pred_type} accuracy ({accuracy:.2f}). Focus on {pred_type} features.")
            
            # General recommendations
            if len(models) == 1:
                recommendations.append("💡 Consider training ensemble models for better performance.")
            
            if not recommendations:
                recommendations.append("🎯 All models performing well. Continue monitoring.")
            
            return recommendations
            
        except Exception as e:
            self.error_handler.handle_error(e, "Generate Recommendations", "analysis")
            return ["⚠️ Error generating recommendations"]
    
    def plot_model_performance(self, model_name: str, days_back: int = 30) -> str:
        """Create performance visualization plots."""
        try:
            # Get prediction data
            with sqlite3.connect(self.db.db_path) as conn:
                df = pd.read_sql_query("""
                    SELECT p.prediction_type, p.predicted_value, p.actual_value, 
                           p.confidence, g.date
                    FROM predictions p
                    JOIN games g ON p.game_id = g.game_id
                    WHERE p.model_name = ? AND p.actual_value IS NOT NULL
                    AND g.date >= date('now', '-{} days')
                    ORDER BY g.date
                """.format(days_back), conn, params=(model_name,))
            
            if df.empty:
                return None
            
            # Create plots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Model Performance: {model_name}', fontsize=16)
            
            # Plot 1: Prediction vs Actual scatter
            for i, pred_type in enumerate(['total_runs', 'winner']):
                if pred_type in df['prediction_type'].values:
                    type_data = df[df['prediction_type'] == pred_type]
                    
                    axes[0, i].scatter(type_data['actual_value'], type_data['predicted_value'], alpha=0.6)
                    axes[0, i].plot([type_data['actual_value'].min(), type_data['actual_value'].max()],
                                   [type_data['actual_value'].min(), type_data['actual_value'].max()], 'r--')
                    axes[0, i].set_xlabel('Actual Value')
                    axes[0, i].set_ylabel('Predicted Value')
                    axes[0, i].set_title(f'{pred_type.replace("_", " ").title()}')
            
            # Plot 3: Residuals over time
            total_runs_data = df[df['prediction_type'] == 'total_runs']
            if not total_runs_data.empty:
                residuals = total_runs_data['predicted_value'] - total_runs_data['actual_value']
                axes[1, 0].plot(pd.to_datetime(total_runs_data['date']), residuals, 'o-', alpha=0.7)
                axes[1, 0].axhline(y=0, color='r', linestyle='--')
                axes[1, 0].set_xlabel('Date')
                axes[1, 0].set_ylabel('Residuals')
                axes[1, 0].set_title('Residuals Over Time')
                axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Plot 4: Confidence distribution
            conf_data = df[df['confidence'].notna()]
            if not conf_data.empty:
                axes[1, 1].hist(conf_data['confidence'], bins=20, alpha=0.7, edgecolor='black')
                axes[1, 1].set_xlabel('Confidence Score')
                axes[1, 1].set_ylabel('Frequency')
                axes[1, 1].set_title('Confidence Score Distribution')
            
            plt.tight_layout()
            
            # Save plot
            plot_path = Path("reports") / f"{model_name}_performance_{datetime.now().strftime('%Y%m%d')}.png"
            plot_path.parent.mkdir(exist_ok=True)
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(plot_path)
            
        except Exception as e:
            self.error_handler.handle_error(e, "Plot Performance", model_name)
            return None


def main():
    """Test the historical data and validation system."""
    print("📚 MLB Historical Data & Validation System")
    print("=" * 45)
    
    # Initialize components
    db = MLBHistoricalDatabase()
    settings = MLBUserSettings()
    validator = ModelValidationSystem(db, settings)
    
    # Test data storage
    print("Testing data storage...")
    sample_game = {
        'game_id': 'test_game_001',
        'date': '2024-07-27',
        'home_team': 'NYY',
        'away_team': 'BOS',
        'home_score': 7,
        'away_score': 4,
        'total_score': 11,
        'winner': 'NYY',
        'venue': 'Yankee Stadium',
        'attendance': 45000
    }
    
    success = db.store_game(sample_game)
    print(f"Game storage: {'✅ Success' if success else '❌ Failed'}")
    
    # Test prediction storage
    print("Testing prediction storage...")
    success = db.store_prediction('test_game_001', 'test_model', 'total_runs', 10.5, 0.75)
    print(f"Prediction storage: {'✅ Success' if success else '❌ Failed'}")
    
    # Update with actual results
    db.update_prediction_results('test_game_001', {'total_runs': 11})
    
    # Test accuracy calculation
    print("Testing accuracy calculation...")
    accuracy = db.get_prediction_accuracy('test_model', 'total_runs', 30)
    if 'error' not in accuracy:
        print(f"✅ Accuracy calculated: {accuracy['accuracy']:.3f}")
    else:
        print(f"❌ Accuracy calculation failed: {accuracy['error']}")
    
    # Test validation
    print("Testing model validation...")
    validation = validator.validate_model_performance('test_model', 30)
    if 'error' not in validation:
        print("✅ Model validation completed")
    else:
        print(f"❌ Validation failed: {validation['error']}")
    
    print("\n📊 Historical data system ready for production!")


if __name__ == "__main__":
    main()
