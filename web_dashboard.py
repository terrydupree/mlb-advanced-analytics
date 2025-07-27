"""
Interactive Web Dashboard for MLB Analytics
Flask-based web interface with real-time data visualization.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.utils
from pathlib import Path

# Local imports
from modules.data_fetch import get_games_today, get_park_factors
from modules.analytics import run_ev_poisson_analysis
from user_settings import MLBUserSettings
from ml_models import MLBPredictiveModels
from error_handler import MLBErrorHandler


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'mlb-analytics-secret-key')

# Initialize components
settings = MLBUserSettings()
ml_models = MLBPredictiveModels(settings)
error_handler = MLBErrorHandler()

# Load models if available
if Path("models").exists():
    ml_models.load_models()


@app.route('/')
def dashboard():
    """Main dashboard view."""
    try:
        # Get today's games
        games = get_games_today()
        park_factors = get_park_factors("data/park_factors.csv")
        
        # Run analysis
        analysis = run_ev_poisson_analysis(games, [], park_factors)
        
        # Get system status
        system_health = error_handler.get_system_health()
        
        # Prepare data for charts
        chart_data = _prepare_dashboard_charts(analysis, games)
        
        return render_template('dashboard.html', 
                             games=games[:10],  # Limit to first 10 games
                             analysis=analysis.get('game_analyzer', [])[:10],
                             chart_data=chart_data,
                             system_health=system_health,
                             total_games=len(games))
    
    except Exception as e:
        error_handler.handle_error(e, "Dashboard", "main_view")
        return render_template('error.html', error=str(e))


@app.route('/games')
def games_view():
    """Detailed games analysis view."""
    try:
        games = get_games_today()
        park_factors = get_park_factors("data/park_factors.csv")
        analysis = run_ev_poisson_analysis(games, [], park_factors)
        
        # Add ML predictions if models are available
        if ml_models.models:
            for i, game in enumerate(games):
                try:
                    # Create feature vector for game
                    game_features = _create_game_features(game, park_factors)
                    predictions = ml_models.predict_game(game_features, "total_runs")
                    games[i]['ml_predictions'] = predictions
                except Exception as e:
                    games[i]['ml_predictions'] = {'error': str(e)}
        
        return render_template('games.html', 
                             games=games,
                             analysis=analysis.get('game_analyzer', []))
    
    except Exception as e:
        error_handler.handle_error(e, "Games View", "detailed_analysis")
        return render_template('error.html', error=str(e))


@app.route('/analytics')
def analytics_view():
    """Advanced analytics and model performance view."""
    try:
        # Model performance metrics
        model_summary = ml_models.get_model_summary() if ml_models.models else pd.DataFrame()
        
        # Feature importance data
        feature_importance = ml_models.feature_importance if hasattr(ml_models, 'feature_importance') else {}
        
        # Historical performance (mock data for demo)
        historical_data = _get_historical_performance()
        
        return render_template('analytics.html',
                             model_summary=model_summary.to_dict('records') if not model_summary.empty else [],
                             feature_importance=feature_importance,
                             historical_data=historical_data)
    
    except Exception as e:
        error_handler.handle_error(e, "Analytics View", "model_performance")
        return render_template('error.html', error=str(e))


@app.route('/settings')
def settings_view():
    """User settings configuration view."""
    try:
        return render_template('settings.html', 
                             stat_weights=settings.stat_weights.__dict__,
                             confidence=settings.confidence.__dict__,
                             analysis=settings.analysis.__dict__)
    
    except Exception as e:
        error_handler.handle_error(e, "Settings View", "configuration")
        return render_template('error.html', error=str(e))


@app.route('/api/games')
def api_games():
    """API endpoint for games data."""
    try:
        games = get_games_today()
        return jsonify({
            'success': True,
            'games': games,
            'count': len(games),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        error_handler.handle_error(e, "API Games", "data_fetch")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for ML predictions."""
    try:
        game_data = request.json
        
        if not ml_models.models:
            return jsonify({
                'success': False,
                'error': 'No trained models available'
            })
        
        # Create features from game data
        features = pd.DataFrame([game_data])
        predictions = ml_models.predict_game(features, "total_runs")
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        error_handler.handle_error(e, "API Predict", "ml_inference")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })


@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """API endpoint for settings management."""
    try:
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'settings': {
                    'stat_weights': settings.stat_weights.__dict__,
                    'confidence': settings.confidence.__dict__,
                    'analysis': settings.analysis.__dict__
                }
            })
        
        elif request.method == 'POST':
            new_settings = request.json
            
            # Update settings
            if 'stat_weights' in new_settings:
                settings.update_stat_weights(**new_settings['stat_weights'])
            if 'confidence' in new_settings:
                settings.update_confidence_settings(**new_settings['confidence'])
            if 'analysis' in new_settings:
                settings.update_analysis_settings(**new_settings['analysis'])
            
            return jsonify({
                'success': True,
                'message': 'Settings updated successfully'
            })
    
    except Exception as e:
        error_handler.handle_error(e, "API Settings", "configuration_update")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/health')
def api_health():
    """API endpoint for system health check."""
    try:
        health = error_handler.get_system_health()
        return jsonify({
            'success': True,
            'health': health,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })


def _prepare_dashboard_charts(analysis: dict, games: list) -> dict:
    """Prepare data for dashboard charts."""
    try:
        chart_data = {}
        
        # Games by statistical edge
        if 'game_analyzer' in analysis:
            game_data = analysis['game_analyzer']
            edges = [float(row[9]) if row[9] != 'No edge' else 0 for row in game_data]
            
            # Edge distribution chart
            edge_chart = go.Figure(data=[
                go.Histogram(x=edges, nbinsx=20, name='Statistical Edge Distribution')
            ])
            edge_chart.update_layout(
                title='Distribution of Statistical Edges',
                xaxis_title='Statistical Edge',
                yaxis_title='Number of Games'
            )
            chart_data['edge_distribution'] = json.dumps(edge_chart, cls=plotly.utils.PlotlyJSONEncoder)
            
            # Win probability comparison
            if len(game_data) > 0:
                home_probs = [float(row[7]) for row in game_data if row[7] != 'N/A']
                away_probs = [float(row[8]) for row in game_data if row[8] != 'N/A']
                
                prob_chart = go.Figure()
                prob_chart.add_trace(go.Scatter(
                    y=list(range(len(home_probs))),
                    x=home_probs,
                    mode='markers',
                    name='Home Win Probability'
                ))
                prob_chart.add_trace(go.Scatter(
                    y=list(range(len(away_probs))),
                    x=away_probs,
                    mode='markers',
                    name='Away Win Probability'
                ))
                prob_chart.update_layout(
                    title='Win Probability Comparison',
                    xaxis_title='Win Probability',
                    yaxis_title='Game Number'
                )
                chart_data['win_probabilities'] = json.dumps(prob_chart, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Model performance chart (if models exist)
        if ml_models.models:
            model_summary = ml_models.get_model_summary()
            if not model_summary.empty:
                perf_chart = go.Figure(data=[
                    go.Bar(
                        x=model_summary['Model'],
                        y=model_summary['Test R²'],
                        name='Model Performance (R²)'
                    )
                ])
                perf_chart.update_layout(
                    title='Model Performance Comparison',
                    xaxis_title='Model',
                    yaxis_title='R² Score'
                )
                chart_data['model_performance'] = json.dumps(perf_chart, cls=plotly.utils.PlotlyJSONEncoder)
        
        return chart_data
        
    except Exception as e:
        error_handler.handle_error(e, "Chart Preparation", "data_visualization")
        return {}


def _create_game_features(game: dict, park_factors: dict) -> pd.DataFrame:
    """Create feature vector for a single game."""
    try:
        features = pd.DataFrame([{
            'home_team_runs_avg': game.get('home_team_stats', {}).get('runs_per_game', 4.5),
            'away_team_runs_avg': game.get('away_team_stats', {}).get('runs_per_game', 4.3),
            'home_era': game.get('home_pitcher_stats', {}).get('era', 4.2),
            'away_era': game.get('away_pitcher_stats', {}).get('era', 4.3),
            'park_factor': park_factors.get(game.get('venue', ''), 1.0),
            'game_id': game.get('game_id', 0),
            'date': datetime.now()
        }])
        
        return features
        
    except Exception as e:
        error_handler.handle_error(e, "Feature Creation", "single_game")
        return pd.DataFrame()


def _get_historical_performance() -> dict:
    """Get historical model performance data."""
    # This would typically come from a database
    # For demo purposes, generating mock data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    return {
        'dates': [d.strftime('%Y-%m-%d') for d in dates[-30:]],  # Last 30 days
        'accuracy': np.random.normal(0.75, 0.05, 30).tolist(),
        'profit_loss': np.cumsum(np.random.normal(2, 10, 30)).tolist()
    }


# Create HTML templates directory and files
def create_templates():
    """Create HTML templates for the web interface."""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Base template
    base_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}MLB Analytics Dashboard{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        .navbar-brand { font-weight: bold; }
        .card-header { background-color: #f8f9fa; font-weight: bold; }
        .system-healthy { color: #28a745; }
        .system-degraded { color: #ffc107; }
        .system-critical { color: #dc3545; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">⚾ MLB Analytics</a>
            <div class="navbar-nav">
                <a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a>
                <a class="nav-link" href="{{ url_for('games_view') }}">Games</a>
                <a class="nav-link" href="{{ url_for('analytics_view') }}">Analytics</a>
                <a class="nav-link" href="{{ url_for('settings_view') }}">Settings</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""
    
    # Dashboard template
    dashboard_template = """
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5>Today's Games Analysis</h5>
            </div>
            <div class="card-body">
                {% if games %}
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Matchup</th>
                                <th>Statistical Edge</th>
                                <th>Confidence</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for i in range(analysis|length) %}
                            <tr>
                                <td>{{ games[i].get('time', 'TBD') }}</td>
                                <td>{{ analysis[i][1] }} @ {{ analysis[i][0] }}</td>
                                <td>
                                    {% if analysis[i][9] != 'No edge' %}
                                        <span class="badge bg-success">{{ "%.2f"|format(analysis[i][9]|float) }}%</span>
                                    {% else %}
                                        <span class="badge bg-secondary">No edge</span>
                                    {% endif %}
                                </td>
                                <td>
                                    <span class="badge bg-info">{{ analysis[i][10] }}</span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted">No games found for today.</p>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card mb-3">
            <div class="card-header">
                <h6>System Status</h6>
            </div>
            <div class="card-body">
                <p>Status: <span class="system-{{ system_health.status }}">{{ system_health.status.title() }}</span></p>
                <p>Total Games: {{ total_games }}</p>
                <p>Last Check: {{ system_health.last_check[:16] }}</p>
            </div>
        </div>
        
        {% if chart_data.get('edge_distribution') %}
        <div class="card">
            <div class="card-header">
                <h6>Statistical Edge Distribution</h6>
            </div>
            <div class="card-body">
                <div id="edge-chart"></div>
            </div>
        </div>
        {% endif %}
    </div>
</div>

{% if chart_data.get('model_performance') %}
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5>Model Performance</h5>
            </div>
            <div class="card-body">
                <div id="model-chart"></div>
            </div>
        </div>
    </div>
</div>
{% endif %}
{% endblock %}

{% block scripts %}
{% if chart_data.get('edge_distribution') %}
<script>
    var edgeData = {{ chart_data.edge_distribution|safe }};
    Plotly.newPlot('edge-chart', edgeData.data, edgeData.layout, {responsive: true});
</script>
{% endif %}

{% if chart_data.get('model_performance') %}
<script>
    var modelData = {{ chart_data.model_performance|safe }};
    Plotly.newPlot('model-chart', modelData.data, modelData.layout, {responsive: true});
</script>
{% endif %}
{% endblock %}
"""
    
    # Error template
    error_template = """
{% extends "base.html" %}

{% block content %}
<div class="alert alert-danger" role="alert">
    <h4 class="alert-heading">Error!</h4>
    <p>{{ error }}</p>
    <hr>
    <p class="mb-0"><a href="{{ url_for('dashboard') }}" class="btn btn-primary">Return to Dashboard</a></p>
</div>
{% endblock %}
"""
    
    # Write templates
    with open(templates_dir / "base.html", 'w') as f:
        f.write(base_template)
    
    with open(templates_dir / "dashboard.html", 'w') as f:
        f.write(dashboard_template)
    
    with open(templates_dir / "error.html", 'w') as f:
        f.write(error_template)
    
    print("✅ HTML templates created")


def main():
    """Run the Flask web application."""
    print("🌐 Starting MLB Analytics Web Dashboard")
    print("=" * 40)
    
    # Create templates
    create_templates()
    
    # Configure Flask app
    app.config['DEBUG'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    print("🚀 Dashboard starting at http://localhost:5000")
    print("📊 Available endpoints:")
    print("   • /          - Main dashboard")
    print("   • /games     - Detailed games analysis") 
    print("   • /analytics - Model performance")
    print("   • /settings  - Configuration")
    print("   • /api/*     - REST API endpoints")
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == "__main__":
    main()
