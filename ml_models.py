"""
Advanced Machine Learning Models for MLB Analytics
Predictive modeling, feature engineering, and model validation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import joblib
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Machine Learning imports
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_regression
import xgboost as xgb
import lightgbm as lgb

# Local imports
from user_settings import MLBUserSettings
from error_handler import MLBErrorHandler, log_operation


class MLBFeatureEngineering:
    """
    Advanced feature engineering for MLB data.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
    
    def create_batting_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced batting features."""
        features = df.copy()
        
        # Basic rate stats
        features['avg'] = features['hits'] / features['at_bats'].replace(0, np.nan)
        features['obp'] = (features['hits'] + features['walks'] + features['hbp']) / (features['at_bats'] + features['walks'] + features['hbp'] + features['sf']).replace(0, np.nan)
        features['slg'] = features['total_bases'] / features['at_bats'].replace(0, np.nan)
        features['ops'] = features['obp'] + features['slg']
        
        # Advanced metrics
        features['iso'] = features['slg'] - features['avg']
        features['babip'] = (features['hits'] - features['home_runs']) / (features['at_bats'] - features['strikeouts'] - features['home_runs'] + features['sf']).replace(0, np.nan)
        features['k_rate'] = features['strikeouts'] / features['at_bats'].replace(0, np.nan)
        features['bb_rate'] = features['walks'] / features['at_bats'].replace(0, np.nan)
        
        # wOBA calculation (simplified)
        woba_weights = {'bb': 0.69, 'hbp': 0.72, '1b': 0.89, '2b': 1.27, '3b': 1.62, 'hr': 2.10}
        singles = features['hits'] - features['doubles'] - features['triples'] - features['home_runs']
        features['woba'] = (
            woba_weights['bb'] * features['walks'] +
            woba_weights['hbp'] * features['hbp'] +
            woba_weights['1b'] * singles +
            woba_weights['2b'] * features['doubles'] +
            woba_weights['3b'] * features['triples'] +
            woba_weights['hr'] * features['home_runs']
        ) / (features['at_bats'] + features['walks'] + features['sf'] + features['hbp']).replace(0, np.nan)
        
        # Rolling averages (last 10 games)
        for stat in ['avg', 'obp', 'slg', 'ops', 'woba']:
            features[f'{stat}_l10'] = features.groupby('player_id')[stat].rolling(10, min_periods=3).mean().reset_index(0, drop=True)
        
        # Situational features
        features['clutch_avg'] = features['risp_hits'] / features['risp_at_bats'].replace(0, np.nan)
        features['vs_lhp_avg'] = features['vs_lhp_hits'] / features['vs_lhp_at_bats'].replace(0, np.nan)
        features['vs_rhp_avg'] = features['vs_rhp_hits'] / features['vs_rhp_at_bats'].replace(0, np.nan)
        
        return features
    
    def create_pitching_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced pitching features."""
        features = df.copy()
        
        # Basic rate stats
        features['era'] = (features['earned_runs'] * 9) / features['innings_pitched'].replace(0, np.nan)
        features['whip'] = (features['walks'] + features['hits']) / features['innings_pitched'].replace(0, np.nan)
        features['k_per_9'] = (features['strikeouts'] * 9) / features['innings_pitched'].replace(0, np.nan)
        features['bb_per_9'] = (features['walks'] * 9) / features['innings_pitched'].replace(0, np.nan)
        features['hr_per_9'] = (features['home_runs'] * 9) / features['innings_pitched'].replace(0, np.nan)
        
        # Advanced metrics
        features['k_rate'] = features['strikeouts'] / features['batters_faced'].replace(0, np.nan)
        features['bb_rate'] = features['walks'] / features['batters_faced'].replace(0, np.nan)
        features['hr_rate'] = features['home_runs'] / features['batters_faced'].replace(0, np.nan)
        features['lob_rate'] = features['left_on_base'] / (features['hits'] + features['walks'] + features['hbp'] - features['home_runs']).replace(0, np.nan)
        
        # FIP calculation
        fip_constant = 3.10  # League average
        features['fip'] = ((13 * features['home_runs'] + 3 * features['walks'] - 2 * features['strikeouts']) / features['innings_pitched']) + fip_constant
        
        # xFIP (using league average HR/FB rate)
        league_hr_fb_rate = 0.11
        fb_estimated = features['fly_balls'] if 'fly_balls' in features.columns else features['batters_faced'] * 0.35
        features['xfip'] = ((13 * fb_estimated * league_hr_fb_rate + 3 * features['walks'] - 2 * features['strikeouts']) / features['innings_pitched']) + fip_constant
        
        # Rolling averages
        for stat in ['era', 'whip', 'k_per_9', 'fip']:
            features[f'{stat}_l5'] = features.groupby('player_id')[stat].rolling(5, min_periods=2).mean().reset_index(0, drop=True)
        
        return features
    
    def create_team_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create team-level features."""
        features = df.copy()
        
        # Team performance metrics
        features['runs_per_game'] = features['runs_scored'] / features['games_played']
        features['runs_allowed_per_game'] = features['runs_allowed'] / features['games_played']
        features['run_differential'] = features['runs_scored'] - features['runs_allowed']
        features['win_percentage'] = features['wins'] / features['games_played']
        
        # Recent form (last 10 games)
        features['l10_win_pct'] = features['l10_wins'] / 10
        features['l10_run_diff'] = features['l10_runs_scored'] - features['l10_runs_allowed']
        
        # Home/Away splits
        features['home_win_pct'] = features['home_wins'] / features['home_games']
        features['away_win_pct'] = features['away_wins'] / features['away_games']
        
        # Strength metrics
        features['strength_of_schedule'] = features['opp_win_pct']
        features['pythagorean_wins'] = (features['runs_scored'] ** 2) / (features['runs_scored'] ** 2 + features['runs_allowed'] ** 2) * features['games_played']
        features['luck_factor'] = features['wins'] - features['pythagorean_wins']
        
        return features
    
    def create_matchup_features(self, home_df: pd.DataFrame, away_df: pd.DataFrame, 
                              pitcher_home: pd.DataFrame, pitcher_away: pd.DataFrame) -> pd.DataFrame:
        """Create matchup-specific features."""
        matchup_features = pd.DataFrame()
        
        # Team strength differential
        matchup_features['win_pct_diff'] = home_df['win_percentage'] - away_df['win_percentage']
        matchup_features['run_diff_advantage'] = home_df['run_differential'] - away_df['run_differential']
        matchup_features['home_field_advantage'] = 0.54  # Historical home field advantage
        
        # Pitching matchup
        matchup_features['pitcher_era_diff'] = pitcher_away['era'] - pitcher_home['era']  # Negative favors home
        matchup_features['pitcher_fip_diff'] = pitcher_away['fip'] - pitcher_home['fip']
        matchup_features['pitcher_k_rate_diff'] = pitcher_home['k_rate'] - pitcher_away['k_rate']
        
        # Recent form
        matchup_features['l10_form_diff'] = home_df['l10_win_pct'] - away_df['l10_win_pct']
        
        # Offensive vs pitching matchups
        matchup_features['home_off_vs_away_pitch'] = home_df['runs_per_game'] / (pitcher_away['era'] / 4.5)  # Normalized
        matchup_features['away_off_vs_home_pitch'] = away_df['runs_per_game'] / (pitcher_home['era'] / 4.5)
        
        return matchup_features
    
    def add_weather_features(self, df: pd.DataFrame, weather_data: pd.DataFrame) -> pd.DataFrame:
        """Add weather-based features."""
        if weather_data.empty:
            # Add default weather features
            df['temperature'] = 72  # Default temperature
            df['wind_speed'] = 5    # Default wind speed
            df['humidity'] = 50     # Default humidity
            df['is_dome'] = 0       # Most games are outdoor
        else:
            df = df.merge(weather_data, on=['game_id', 'date'], how='left')
        
        # Weather impact features
        df['hitting_weather'] = ((df['temperature'] > 75) & (df['wind_speed'] < 15) & (df['humidity'] < 70)).astype(int)
        df['pitching_weather'] = ((df['temperature'] < 70) | (df['wind_speed'] > 20) | (df['humidity'] > 80)).astype(int)
        
        return df
    
    def engineer_features(self, game_data: pd.DataFrame, batting_data: pd.DataFrame, 
                         pitching_data: pd.DataFrame, weather_data: pd.DataFrame = None) -> pd.DataFrame:
        """Main feature engineering pipeline."""
        
        # Create individual feature sets
        batting_features = self.create_batting_features(batting_data)
        pitching_features = self.create_pitching_features(pitching_data)
        
        # Aggregate team features
        team_batting = batting_features.groupby(['team_id', 'date']).agg({
            'runs': 'sum', 'hits': 'sum', 'home_runs': 'sum',
            'avg': 'mean', 'obp': 'mean', 'slg': 'mean', 'ops': 'mean',
            'woba': 'mean', 'iso': 'mean', 'babip': 'mean'
        }).reset_index()
        
        team_pitching = pitching_features.groupby(['team_id', 'date']).agg({
            'era': 'mean', 'whip': 'mean', 'fip': 'mean',
            'k_rate': 'mean', 'bb_rate': 'mean', 'hr_rate': 'mean'
        }).reset_index()
        
        # Merge with game data
        features = game_data.merge(team_batting.add_suffix('_home'), 
                                 left_on=['home_team_id', 'date'], 
                                 right_on=['team_id_home', 'date'], how='left')
        
        features = features.merge(team_batting.add_suffix('_away'), 
                                left_on=['away_team_id', 'date'], 
                                right_on=['team_id_away', 'date'], how='left')
        
        # Add weather features
        if weather_data is not None:
            features = self.add_weather_features(features, weather_data)
        
        # Create derived features
        features['total_implied_runs'] = features['home_team_implied_runs'] + features['away_team_implied_runs']
        features['run_total_over_under'] = features['total_implied_runs'] - features['betting_total']
        
        # Store feature names
        self.feature_names = [col for col in features.columns if col not in ['game_id', 'date', 'home_score', 'away_score', 'total_score']]
        
        return features


class MLBPredictiveModels:
    """
    Machine learning models for MLB game prediction.
    """
    
    def __init__(self, settings: MLBUserSettings):
        self.settings = settings
        self.error_handler = MLBErrorHandler()
        self.feature_engineer = MLBFeatureEngineering()
        
        # Model storage
        self.models = {}
        self.model_metrics = {}
        self.feature_importance = {}
        
        # Model configurations
        self.model_configs = {
            'random_forest': {
                'model': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
                'params': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 15, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
            },
            'gradient_boosting': {
                'model': GradientBoostingRegressor(random_state=42),
                'params': {
                    'n_estimators': [100, 200],
                    'learning_rate': [0.05, 0.1, 0.15],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9, 1.0]
                }
            },
            'xgboost': {
                'model': xgb.XGBRegressor(random_state=42, n_jobs=-1),
                'params': {
                    'n_estimators': [100, 200],
                    'learning_rate': [0.05, 0.1, 0.15],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9],
                    'colsample_bytree': [0.8, 0.9, 1.0]
                }
            },
            'lightgbm': {
                'model': lgb.LGBMRegressor(random_state=42, n_jobs=-1, verbose=-1),
                'params': {
                    'n_estimators': [100, 200],
                    'learning_rate': [0.05, 0.1, 0.15],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9],
                    'colsample_bytree': [0.8, 0.9, 1.0]
                }
            }
        }
    
    @log_operation("Model Training")
    def train_models(self, X: pd.DataFrame, y: pd.Series, target_type: str = "total_runs") -> Dict:
        """Train multiple models and select the best performer."""
        
        # Split data chronologically for time series
        split_date = X['date'].quantile(0.8) if 'date' in X.columns else len(X) * 0.8
        
        if 'date' in X.columns:
            train_mask = X['date'] <= split_date
            X_train, X_test = X[train_mask], X[~train_mask]
            y_train, y_test = y[train_mask], y[~train_mask]
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Remove non-feature columns
        feature_cols = [col for col in X_train.columns if col not in ['game_id', 'date']]
        X_train_features = X_train[feature_cols]
        X_test_features = X_test[feature_cols]
        
        results = {}
        
        for model_name, config in self.model_configs.items():
            try:
                print(f"Training {model_name}...")
                
                # Grid search for best parameters
                grid_search = GridSearchCV(
                    config['model'], 
                    config['params'], 
                    cv=TimeSeriesSplit(n_splits=3),
                    scoring='neg_mean_squared_error',
                    n_jobs=-1
                )
                
                grid_search.fit(X_train_features, y_train)
                best_model = grid_search.best_estimator_
                
                # Evaluate model
                train_pred = best_model.predict(X_train_features)
                test_pred = best_model.predict(X_test_features)
                
                metrics = {
                    'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
                    'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
                    'train_mae': mean_absolute_error(y_train, train_pred),
                    'test_mae': mean_absolute_error(y_test, test_pred),
                    'train_r2': r2_score(y_train, train_pred),
                    'test_r2': r2_score(y_test, test_pred),
                    'best_params': grid_search.best_params_
                }
                
                # Feature importance
                if hasattr(best_model, 'feature_importances_'):
                    importance_df = pd.DataFrame({
                        'feature': feature_cols,
                        'importance': best_model.feature_importances_
                    }).sort_values('importance', ascending=False)
                    
                    self.feature_importance[f"{model_name}_{target_type}"] = importance_df
                
                # Store model and metrics
                self.models[f"{model_name}_{target_type}"] = best_model
                self.model_metrics[f"{model_name}_{target_type}"] = metrics
                results[model_name] = metrics
                
                print(f"✅ {model_name} - Test RMSE: {metrics['test_rmse']:.3f}, R²: {metrics['test_r2']:.3f}")
                
            except Exception as e:
                self.error_handler.handle_error(e, f"Training {model_name}", target_type)
                print(f"❌ {model_name} training failed: {e}")
        
        # Create ensemble model
        if len(results) > 1:
            self._create_ensemble_model(X_train_features, y_train, X_test_features, y_test, target_type)
        
        return results
    
    def _create_ensemble_model(self, X_train: pd.DataFrame, y_train: pd.Series, 
                             X_test: pd.DataFrame, y_test: pd.Series, target_type: str):
        """Create ensemble model from trained models."""
        try:
            # Get best performing models
            model_keys = [key for key in self.models.keys() if target_type in key and 'ensemble' not in key]
            
            if len(model_keys) >= 2:
                # Select top 3 models by test R²
                top_models = sorted(model_keys, 
                                  key=lambda x: self.model_metrics[x]['test_r2'], 
                                  reverse=True)[:3]
                
                estimators = [(name.split('_')[0], self.models[name]) for name in top_models]
                
                ensemble = VotingRegressor(estimators=estimators)
                ensemble.fit(X_train, y_train)
                
                # Evaluate ensemble
                train_pred = ensemble.predict(X_train)
                test_pred = ensemble.predict(X_test)
                
                metrics = {
                    'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
                    'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
                    'train_r2': r2_score(y_train, train_pred),
                    'test_r2': r2_score(y_test, test_pred),
                    'component_models': [name.split('_')[0] for name in top_models]
                }
                
                self.models[f"ensemble_{target_type}"] = ensemble
                self.model_metrics[f"ensemble_{target_type}"] = metrics
                
                print(f"✅ Ensemble - Test RMSE: {metrics['test_rmse']:.3f}, R²: {metrics['test_r2']:.3f}")
                
        except Exception as e:
            self.error_handler.handle_error(e, "Ensemble Creation", target_type)
    
    @log_operation("Model Prediction")
    def predict_game(self, game_features: pd.DataFrame, target_type: str = "total_runs") -> Dict:
        """Make predictions for a single game."""
        predictions = {}
        
        # Prepare features
        feature_cols = [col for col in game_features.columns if col not in ['game_id', 'date']]
        X = game_features[feature_cols]
        
        # Get predictions from all models
        for model_name, model in self.models.items():
            if target_type in model_name:
                try:
                    pred = model.predict(X)[0]
                    predictions[model_name.replace(f"_{target_type}", "")] = pred
                except Exception as e:
                    self.error_handler.handle_error(e, f"Prediction {model_name}", "single_game")
        
        # Calculate confidence based on model agreement
        if len(predictions) > 1:
            pred_values = list(predictions.values())
            mean_pred = np.mean(pred_values)
            std_pred = np.std(pred_values)
            confidence = max(0, 1 - (std_pred / mean_pred)) if mean_pred > 0 else 0
            
            predictions['mean'] = mean_pred
            predictions['std'] = std_pred
            predictions['confidence'] = confidence
        
        return predictions
    
    def save_models(self, model_dir: str = "models"):
        """Save trained models to disk."""
        model_path = Path(model_dir)
        model_path.mkdir(exist_ok=True)
        
        for model_name, model in self.models.items():
            try:
                joblib.dump(model, model_path / f"{model_name}.pkl")
                print(f"✅ Saved {model_name}")
            except Exception as e:
                self.error_handler.handle_error(e, f"Saving {model_name}", "model_persistence")
        
        # Save metrics and feature importance
        with open(model_path / "model_metrics.json", 'w') as f:
            import json
            json.dump(self.model_metrics, f, indent=2, default=str)
        
        print(f"📁 Models saved to {model_path}")
    
    def load_models(self, model_dir: str = "models"):
        """Load trained models from disk."""
        model_path = Path(model_dir)
        
        if not model_path.exists():
            print(f"❌ Model directory {model_dir} not found")
            return
        
        for model_file in model_path.glob("*.pkl"):
            try:
                model_name = model_file.stem
                self.models[model_name] = joblib.load(model_file)
                print(f"✅ Loaded {model_name}")
            except Exception as e:
                self.error_handler.handle_error(e, f"Loading {model_name}", "model_persistence")
        
        # Load metrics
        metrics_file = model_path / "model_metrics.json"
        if metrics_file.exists():
            try:
                import json
                with open(metrics_file, 'r') as f:
                    self.model_metrics = json.load(f)
            except Exception as e:
                self.error_handler.handle_error(e, "Loading metrics", "model_persistence")
        
        print(f"📁 Models loaded from {model_path}")
    
    def get_model_summary(self) -> pd.DataFrame:
        """Get summary of model performance."""
        summary_data = []
        
        for model_name, metrics in self.model_metrics.items():
            summary_data.append({
                'Model': model_name,
                'Test RMSE': metrics.get('test_rmse', 0),
                'Test R²': metrics.get('test_r2', 0),
                'Test MAE': metrics.get('test_mae', 0),
                'Overfitting': metrics.get('train_r2', 0) - metrics.get('test_r2', 0)
            })
        
        return pd.DataFrame(summary_data).sort_values('Test R²', ascending=False)


def main():
    """Test the machine learning system."""
    print("🤖 MLB Machine Learning System")
    print("=" * 35)
    
    # Initialize components
    settings = MLBUserSettings()
    ml_system = MLBPredictiveModels(settings)
    
    # Create sample data for testing
    np.random.seed(42)
    n_games = 1000
    
    sample_data = pd.DataFrame({
        'game_id': range(n_games),
        'date': pd.date_range('2023-01-01', periods=n_games),
        'home_team_runs_avg': np.random.normal(4.5, 1.0, n_games),
        'away_team_runs_avg': np.random.normal(4.3, 1.0, n_games),
        'home_era': np.random.normal(4.2, 0.8, n_games),
        'away_era': np.random.normal(4.3, 0.8, n_games),
        'total_runs': np.random.poisson(8.8, n_games)  # Target variable
    })
    
    # Feature engineering
    features = sample_data.drop(['total_runs'], axis=1)
    target = sample_data['total_runs']
    
    # Train models
    print("Training models...")
    results = ml_system.train_models(features, target, "total_runs")
    
    # Show model summary
    print("\nModel Performance Summary:")
    summary = ml_system.get_model_summary()
    print(summary.to_string(index=False))
    
    # Test prediction
    print("\nTesting single game prediction...")
    test_game = features.iloc[[0]]
    predictions = ml_system.predict_game(test_game, "total_runs")
    print(f"Predictions: {predictions}")
    
    # Save models
    ml_system.save_models()
    
    print("\n✅ Machine learning system test completed!")


if __name__ == "__main__":
    main()
