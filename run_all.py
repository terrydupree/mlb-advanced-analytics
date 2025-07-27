import os
from dotenv import load_dotenv
from modules.data_fetch import get_games_today, get_odds, get_park_factors
from modules.analytics import run_ev_poisson_analysis
from modules.sheet_manager import connect_sheet, update_sheets

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get Google Sheet ID from environment variable or use default
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "1EZjH0UllYLvHp4Qq6VnmomtBqNSYZZCYGYEV7ErMgtQ")
    print(f"🔗 Connecting to Google Sheet: {sheet_id}")
    gs = connect_sheet(sheet_id)

    """
MLB Advanced Analytics Platform - Main Runner
Coordinates all system components for optimal performance.
"""

import os
import sys
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Import core modules
from google_sheets_connect import MLBSheetsConnector
from historical_data import MLBDataCollector
from automation_scheduler import MLBAutomationScheduler
from error_handler import MLBErrorHandler
from user_settings import MLBSettingsManager
from ml_models import MLBPredictiveModels
from web_dashboard import create_app
from historical_validation import MLBHistoricalDatabase

class MLBSystemOrchestrator:
    """
    Central coordinator for the MLB analytics platform.
    Manages all components and ensures optimal system operation.
    """
    
    def __init__(self):
        """Initialize the system orchestrator."""
        self.logger = self._setup_logging()
        self.error_handler = MLBErrorHandler()
        self.settings_manager = MLBSettingsManager()
        self.running = False
        self.components = {}
        
        # Load configuration
        self.config = self._load_configuration()
        
        # Initialize components
        self._initialize_components()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up centralized logging."""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE', 'logs/mlb_system.log')
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        return logging.getLogger(__name__)
    
    def _load_configuration(self) -> Dict:
        """Load system configuration from environment and settings."""
        config = {
            'auto_scheduling': os.getenv('AUTO_SCHEDULING_ENABLED', 'true').lower() == 'true',
            'ml_predictions': os.getenv('ML_PREDICTIONS_ENABLED', 'true').lower() == 'true',
            'web_dashboard': os.getenv('WEB_DASHBOARD_ENABLED', 'true').lower() == 'true',
            'dashboard_port': int(os.getenv('DASHBOARD_PORT', 5000)),
            'dashboard_host': os.getenv('DASHBOARD_HOST', 'localhost'),
            'live_updates': os.getenv('LIVE_UPDATES_ENABLED', 'true').lower() == 'true',
            'performance_monitoring': os.getenv('PERFORMANCE_MONITORING', 'true').lower() == 'true'
        }
        
        return config
    
    def _initialize_components(self):
        """Initialize all system components."""
        try:
            self.logger.info("Initializing MLB Analytics Platform components...")
            
            # Core data components
            self.components['sheets_connector'] = MLBSheetsConnector()
            self.components['data_collector'] = MLBDataCollector()
            self.components['historical_db'] = MLBHistoricalDatabase()
            
            # Advanced components
            if self.config['auto_scheduling']:
                self.components['scheduler'] = MLBAutomationScheduler()
            
            if self.config['ml_predictions']:
                self.components['ml_models'] = MLBPredictiveModels()
            
            # Web dashboard
            if self.config['web_dashboard']:
                self.components['flask_app'] = create_app()
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            self.error_handler.handle_error(e, "component_initialization")
            raise
    
    def start_system(self, mode: str = "full"):
        """
        Start the MLB analytics system.
        
        Args:
            mode: System mode - 'full', 'automation_only', 'dashboard_only', 'data_only'
        """
        try:
            self.logger.info(f"Starting MLB Analytics Platform in {mode} mode...")
            self.running = True
            
            if mode in ['full', 'automation_only']:
                self._start_automation()
            
            if mode in ['full', 'data_only']:
                self._start_data_collection()
            
            if mode in ['full', 'dashboard_only']:
                self._start_dashboard()
            
            if mode == 'full':
                self._start_monitoring()
            
            self.logger.info("MLB Analytics Platform started successfully!")
            
            # Keep the main thread alive
            if mode == 'full':
                self._run_main_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            self.error_handler.handle_error(e, "system_startup")
            self.stop_system()
    
    def _start_automation(self):
        """Start the automation scheduler."""
        if 'scheduler' in self.components:
            scheduler_thread = threading.Thread(
                target=self.components['scheduler'].start_automation,
                daemon=True
            )
            scheduler_thread.start()
            self.logger.info("Automation scheduler started")
    
    def _start_data_collection(self):
        """Start initial data collection."""
        try:
            # Perform initial data sync
            data_thread = threading.Thread(
                target=self._initial_data_sync,
                daemon=True
            )
            data_thread.start()
            self.logger.info("Data collection initiated")
            
        except Exception as e:
            self.logger.error(f"Failed to start data collection: {e}")
    
    def _start_dashboard(self):
        """Start the web dashboard."""
        if 'flask_app' in self.components:
            dashboard_thread = threading.Thread(
                target=self._run_dashboard,
                daemon=True
            )
            dashboard_thread.start()
            self.logger.info(f"Web dashboard starting on {self.config['dashboard_host']}:{self.config['dashboard_port']}")
    
    def _run_dashboard(self):
        """Run the Flask dashboard."""
        try:
            self.components['flask_app'].run(
                host=self.config['dashboard_host'],
                port=self.config['dashboard_port'],
                debug=False,
                threaded=True
            )
        except Exception as e:
            self.logger.error(f"Dashboard error: {e}")
            self.error_handler.handle_error(e, "dashboard_runtime")
    
    def _start_monitoring(self):
        """Start system monitoring."""
        if self.config['performance_monitoring']:
            monitor_thread = threading.Thread(
                target=self._monitor_system_health,
                daemon=True
            )
            monitor_thread.start()
            self.logger.info("System monitoring started")
    
    def _initial_data_sync(self):
        """Perform initial data synchronization."""
        try:
            self.logger.info("Starting initial data synchronization...")
            
            # Collect today's games
            collector = self.components['data_collector']
            today_games = collector.get_todays_games()
            
            if today_games:
                # Update sheets
                sheets = self.components['sheets_connector']
                sheets.update_games_data(today_games)
                
                # Store in database
                if 'historical_db' in self.components:
                    db = self.components['historical_db']
                    for game in today_games:
                        db.store_game(game)
                
                self.logger.info(f"Synchronized {len(today_games)} games")
            
            # Train ML models if enabled
            if 'ml_models' in self.components:
                ml_models = self.components['ml_models']
                ml_models.train_models()
                self.logger.info("ML models training initiated")
            
        except Exception as e:
            self.logger.error(f"Initial data sync failed: {e}")
            self.error_handler.handle_error(e, "initial_sync")
    
    def _monitor_system_health(self):
        """Monitor system health and performance."""
        while self.running:
            try:
                # Check component health
                health_status = self._check_component_health()
                
                # Log system metrics
                self._log_system_metrics()
                
                # Send alerts if needed
                if not all(health_status.values()):
                    self._send_health_alert(health_status)
                
                # Sleep for monitoring interval
                time.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                time.sleep(60)  # Retry after 1 minute
    
    def _check_component_health(self) -> Dict[str, bool]:
        """Check the health of all components."""
        health = {}
        
        for name, component in self.components.items():
            try:
                if hasattr(component, 'health_check'):
                    health[name] = component.health_check()
                else:
                    health[name] = True  # Assume healthy if no health check
            except Exception:
                health[name] = False
        
        return health
    
    def _log_system_metrics(self):
        """Log system performance metrics."""
        import psutil
        
        # CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        self.logger.info(
            f"System metrics - CPU: {cpu_percent}%, "
            f"Memory: {memory.percent}% ({memory.used // 1024 // 1024} MB used)"
        )
    
    def _send_health_alert(self, health_status: Dict[str, bool]):
        """Send health alerts for unhealthy components."""
        unhealthy = [name for name, status in health_status.items() if not status]
        
        alert_message = f"MLB Analytics Platform Alert: Unhealthy components detected: {', '.join(unhealthy)}"
        
        # Send notification
        self.error_handler.send_notification(
            message=alert_message,
            alert_type="system_health",
            severity="warning"
        )
    
    def _run_main_loop(self):
        """Main system loop."""
        try:
            while self.running:
                # Perform periodic maintenance
                self._periodic_maintenance()
                
                # Sleep for main loop interval
                time.sleep(3600)  # 1 hour
                
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
            self.stop_system()
        except Exception as e:
            self.logger.error(f"Main loop error: {e}")
            self.error_handler.handle_error(e, "main_loop")
    
    def _periodic_maintenance(self):
        """Perform periodic system maintenance."""
        try:
            # Clean up old logs
            self._cleanup_old_logs()
            
            # Backup critical data
            self._backup_data()
            
            # Update system configuration
            self._update_configuration()
            
        except Exception as e:
            self.logger.error(f"Maintenance error: {e}")
    
    def _cleanup_old_logs(self):
        """Clean up old log files."""
        try:
            log_dir = "logs"
            if os.path.exists(log_dir):
                cutoff_date = datetime.now() - timedelta(days=7)
                
                for filename in os.listdir(log_dir):
                    filepath = os.path.join(log_dir, filename)
                    if os.path.isfile(filepath):
                        file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                        if file_time < cutoff_date:
                            os.remove(filepath)
                            self.logger.info(f"Cleaned up old log file: {filename}")
        except Exception as e:
            self.logger.error(f"Log cleanup error: {e}")
    
    def _backup_data(self):
        """Backup critical system data."""
        try:
            if 'historical_db' in self.components:
                db = self.components['historical_db']
                backup_path = f"backups/mlb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                
                # Create backup directory
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                
                # Copy database file
                import shutil
                shutil.copy2(db.db_path, backup_path)
                
                self.logger.info(f"Database backup created: {backup_path}")
        except Exception as e:
            self.logger.error(f"Backup error: {e}")
    
    def _update_configuration(self):
        """Update system configuration from settings."""
        try:
            # Reload settings
            new_settings = self.settings_manager.load_settings()
            
            # Update configuration if needed
            # This allows for dynamic configuration updates
            
        except Exception as e:
            self.logger.error(f"Configuration update error: {e}")
    
    def stop_system(self):
        """Stop the MLB analytics system."""
        try:
            self.logger.info("Stopping MLB Analytics Platform...")
            self.running = False
            
            # Stop scheduler if running
            if 'scheduler' in self.components:
                scheduler = self.components['scheduler']
                if hasattr(scheduler, 'stop_automation'):
                    scheduler.stop_automation()
            
            self.logger.info("MLB Analytics Platform stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping system: {e}")
    
    def get_system_status(self) -> Dict:
        """Get current system status."""
        return {
            'running': self.running,
            'components': list(self.components.keys()),
            'config': self.config,
            'health': self._check_component_health() if self.running else {}
        }


def main():
    """Main entry point for the MLB analytics system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='MLB Advanced Analytics Platform')
    parser.add_argument(
        '--mode', 
        choices=['full', 'automation_only', 'dashboard_only', 'data_only'],
        default='full',
        help='System operation mode'
    )
    parser.add_argument(
        '--config-gui',
        action='store_true',
        help='Open configuration GUI'
    )
    
    args = parser.parse_args()
    
    if args.config_gui:
        # Open settings GUI
        from user_settings import SettingsGUI
        gui = SettingsGUI()
        gui.run()
        return
    
    # Initialize and start the system
    orchestrator = MLBSystemOrchestrator()
    
    try:
        orchestrator.start_system(mode=args.mode)
    except KeyboardInterrupt:
        print("
Shutdown requested by user")
    except Exception as e:
        print(f"System error: {e}")
    finally:
        orchestrator.stop_system()


if __name__ == "__main__":
    main()
    print("💡 Enhanced with Chadwick Tools for historical data processing")
    
    games = get_games_today()
    # odds = get_odds()  # Odds disabled - focusing on pure analytics
    parks = get_park_factors("data/park_factors.csv")

    print("🔬 Running statistical analysis...")
    analysis = run_ev_poisson_analysis(games, [], parks)  # Empty odds array
    
    print("📋 Updating Google Sheets with analysis...")
    update_sheets(gs, analysis)
    
    print("\n🎯 Advanced Features Available:")
    print("   📊 Chadwick Tools integration: python chadwick_integration.py")
    print("   📈 Enhanced data processing: python enhanced_data_processing.py")
    print("   🔍 Historical analysis with Retrosheet data")
    print("   📋 Multi-year statistical trends")
    
    print("\n✅ Analysis complete! Check your Google Sheet for results.")

if __name__ == "__main__":
    main()