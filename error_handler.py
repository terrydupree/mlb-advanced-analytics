"""
Comprehensive Error Handling and Logging System for MLB Analytics
Handles scraping failures, API errors, quota limits, and system monitoring.
"""

import logging
import traceback
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from pathlib import Path
import smtplib
from email.mime.text import MimeType
from email.mime.multipart import MimeMultipart
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MLBErrorHandler:
    """
    Comprehensive error handling system for MLB analytics.
    """
    
    def __init__(self, config_file: str = "error_config.json"):
        self.config = self._load_error_config(config_file)
        self.error_counts = {}
        self.last_errors = {}
        self.system_status = {"status": "healthy", "last_check": datetime.now()}
        
        # Setup logging
        self._setup_comprehensive_logging()
        
        # Setup session with retry strategy
        self.session = self._setup_robust_session()
    
    def _load_error_config(self, config_file: str) -> Dict:
        """Load error handling configuration."""
        default_config = {
            "retry_settings": {
                "max_retries": 3,
                "backoff_factor": 2,
                "retry_delays": [1, 5, 15],  # Progressive delays in seconds
                "retry_on_status": [429, 500, 502, 503, 504]
            },
            "rate_limiting": {
                "fangraphs_delay": 2.0,
                "bref_delay": 3.0,
                "mlb_api_delay": 1.0,
                "max_requests_per_minute": 20
            },
            "error_thresholds": {
                "max_consecutive_failures": 5,
                "error_rate_threshold": 0.1,  # 10% error rate
                "circuit_breaker_threshold": 10
            },
            "notifications": {
                "email_alerts": False,
                "slack_webhook": None,
                "critical_errors_only": True
            },
            "logging": {
                "log_level": "INFO",
                "max_log_size_mb": 100,
                "backup_count": 5,
                "include_traceback": True
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception:
                return default_config
        else:
            self._save_config(config_file, default_config)
            return default_config
    
    def _save_config(self, config_file: str, config: Dict):
        """Save configuration to file."""
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save error config: {e}")
    
    def _setup_comprehensive_logging(self):
        """Setup comprehensive logging system."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create multiple log files for different purposes
        log_files = {
            "main": "mlb_analytics.log",
            "errors": "errors.log",
            "api": "api_calls.log",
            "performance": "performance.log"
        }
        
        # Setup rotating file handlers
        from logging.handlers import RotatingFileHandler
        
        self.loggers = {}
        for log_type, filename in log_files.items():
            logger = logging.getLogger(f"MLB_{log_type}")
            logger.setLevel(getattr(logging, self.config["logging"]["log_level"]))
            
            # File handler with rotation
            file_handler = RotatingFileHandler(
                log_dir / filename,
                maxBytes=self.config["logging"]["max_log_size_mb"] * 1024 * 1024,
                backupCount=self.config["logging"]["backup_count"]
            )
            
            # Console handler for critical errors
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            self.loggers[log_type] = logger
        
        # Main logger
        self.logger = self.loggers["main"]
    
    def _setup_robust_session(self) -> requests.Session:
        """Setup requests session with retry strategy."""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=self.config["retry_settings"]["max_retries"],
            backoff_factor=self.config["retry_settings"]["backoff_factor"],
            status_forcelist=self.config["retry_settings"]["retry_on_status"],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Default headers
        session.headers.update({
            'User-Agent': 'MLB-Analytics-Bot/1.0 (Educational Purpose)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        return session
    
    def handle_error(self, error: Exception, context: str = "", operation: str = ""):
        """Comprehensive error handling with context."""
        error_key = f"{context}_{type(error).__name__}"
        current_time = datetime.now()
        
        # Track error frequency
        if error_key not in self.error_counts:
            self.error_counts[error_key] = {"count": 0, "first_seen": current_time, "last_seen": current_time}
        
        self.error_counts[error_key]["count"] += 1
        self.error_counts[error_key]["last_seen"] = current_time
        self.last_errors[error_key] = str(error)
        
        # Log error with full context
        error_msg = f"Error in {context} - {operation}: {str(error)}"
        if self.config["logging"]["include_traceback"]:
            error_msg += f"\nTraceback: {traceback.format_exc()}"
        
        self.loggers["errors"].error(error_msg)
        
        # Check for critical error patterns
        if self._is_critical_error(error, error_key):
            self._handle_critical_error(error, context, operation)
        
        # Update system status
        self._update_system_status(error_key)
        
        return self._get_error_response(error, context)
    
    def _is_critical_error(self, error: Exception, error_key: str) -> bool:
        """Determine if error is critical."""
        critical_conditions = [
            # Too many consecutive failures
            self.error_counts[error_key]["count"] > self.config["error_thresholds"]["max_consecutive_failures"],
            
            # Authentication/Authorization errors
            "401" in str(error) or "403" in str(error),
            
            # Service unavailable
            "503" in str(error) or "502" in str(error),
            
            # Database/file system errors
            isinstance(error, (IOError, OSError, FileNotFoundError)),
            
            # Memory/system errors
            isinstance(error, (MemoryError, SystemError))
        ]
        
        return any(critical_conditions)
    
    def _handle_critical_error(self, error: Exception, context: str, operation: str):
        """Handle critical errors with notifications."""
        critical_msg = f"🚨 CRITICAL ERROR in {context} - {operation}: {str(error)}"
        
        self.loggers["errors"].critical(critical_msg)
        
        # Send notifications if configured
        if self.config["notifications"]["email_alerts"]:
            self._send_email_alert(critical_msg)
        
        if self.config["notifications"]["slack_webhook"]:
            self._send_slack_alert(critical_msg)
        
        # Update system status to degraded
        self.system_status["status"] = "critical"
        self.system_status["last_critical"] = datetime.now()
    
    def _update_system_status(self, error_key: str):
        """Update overall system health status."""
        total_errors = sum(info["count"] for info in self.error_counts.values())
        recent_errors = sum(
            1 for info in self.error_counts.values()
            if (datetime.now() - info["last_seen"]).seconds < 3600  # Last hour
        )
        
        if recent_errors > self.config["error_thresholds"]["circuit_breaker_threshold"]:
            self.system_status["status"] = "degraded"
        elif recent_errors == 0:
            self.system_status["status"] = "healthy"
        
        self.system_status["last_check"] = datetime.now()
        self.system_status["total_errors"] = total_errors
        self.system_status["recent_errors"] = recent_errors
    
    def _get_error_response(self, error: Exception, context: str) -> Dict:
        """Generate standardized error response."""
        return {
            "error": True,
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "retry_recommended": self._should_retry(error)
        }
    
    def _should_retry(self, error: Exception) -> bool:
        """Determine if operation should be retried."""
        retry_conditions = [
            "timeout" in str(error).lower(),
            "connection" in str(error).lower(),
            "429" in str(error),  # Rate limit
            "500" in str(error),  # Server error
            "502" in str(error),  # Bad gateway
            "503" in str(error),  # Service unavailable
        ]
        
        return any(retry_conditions)
    
    def _send_email_alert(self, message: str):
        """Send email alert for critical errors."""
        try:
            # Email configuration would be loaded from environment variables
            # This is a placeholder implementation
            self.logger.info(f"Email alert would be sent: {message}")
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def _send_slack_alert(self, message: str):
        """Send Slack alert for critical errors."""
        try:
            webhook_url = self.config["notifications"]["slack_webhook"]
            if webhook_url:
                payload = {"text": message}
                response = self.session.post(webhook_url, json=payload, timeout=10)
                response.raise_for_status()
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")
    
    def safe_request(self, url: str, source: str = "generic", **kwargs) -> Optional[requests.Response]:
        """Make a safe HTTP request with rate limiting and error handling."""
        # Apply rate limiting
        delay = self.config["rate_limiting"].get(f"{source}_delay", 2.0)
        time.sleep(delay)
        
        # Log API call
        self.loggers["api"].info(f"API call to {source}: {url}")
        
        try:
            response = self.session.get(url, timeout=30, **kwargs)
            
            # Check for rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                self.logger.warning(f"Rate limited by {source}. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self.safe_request(url, source, **kwargs)  # Retry
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            self.handle_error(e, f"{source}_api", f"GET {url}")
            return None
    
    def get_system_health(self) -> Dict:
        """Get current system health status."""
        return {
            "status": self.system_status["status"],
            "last_check": self.system_status["last_check"].isoformat(),
            "total_errors": self.system_status.get("total_errors", 0),
            "recent_errors": self.system_status.get("recent_errors", 0),
            "error_summary": {
                key: {
                    "count": info["count"],
                    "last_seen": info["last_seen"].isoformat(),
                    "last_error": self.last_errors.get(key, "")
                }
                for key, info in self.error_counts.items()
            }
        }
    
    def reset_error_counts(self):
        """Reset error tracking (useful for testing or after fixes)."""
        self.error_counts.clear()
        self.last_errors.clear()
        self.system_status["status"] = "healthy"
        self.logger.info("Error counts reset")


def log_operation(operation_name: str):
    """Decorator for logging and error handling of operations."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            error_handler = getattr(args[0], 'error_handler', MLBErrorHandler()) if args else MLBErrorHandler()
            start_time = time.time()
            
            try:
                # Log operation start
                error_handler.loggers["performance"].info(f"Starting {operation_name}")
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Log successful completion
                duration = time.time() - start_time
                error_handler.loggers["performance"].info(
                    f"Completed {operation_name} in {duration:.2f} seconds"
                )
                
                return result
                
            except Exception as e:
                # Handle error
                duration = time.time() - start_time
                error_response = error_handler.handle_error(e, operation_name, func.__name__)
                
                error_handler.loggers["performance"].error(
                    f"Failed {operation_name} after {duration:.2f} seconds: {str(e)}"
                )
                
                # Re-raise exception or return error response based on configuration
                if error_handler.config.get("raise_exceptions", True):
                    raise
                else:
                    return error_response
        
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for automatic retry on failure."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            error_handler = getattr(args[0], 'error_handler', MLBErrorHandler()) if args else MLBErrorHandler()
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        # Final attempt failed
                        error_handler.handle_error(e, func.__name__, f"Final attempt {attempt + 1}")
                        raise
                    
                    # Log retry attempt
                    wait_time = delay * (backoff ** attempt)
                    error_handler.logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {wait_time:.1f} seconds..."
                    )
                    
                    time.sleep(wait_time)
            
        return wrapper
    return decorator


# Rate limiting decorator
class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self):
        self.call_times = {}
    
    def limit(self, source: str, max_calls: int = 60, window: int = 60):
        """Rate limiting decorator."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                now = time.time()
                
                # Clean old entries
                if source in self.call_times:
                    self.call_times[source] = [
                        call_time for call_time in self.call_times[source]
                        if now - call_time < window
                    ]
                else:
                    self.call_times[source] = []
                
                # Check rate limit
                if len(self.call_times[source]) >= max_calls:
                    wait_time = window - (now - self.call_times[source][0])
                    if wait_time > 0:
                        time.sleep(wait_time)
                
                # Record this call
                self.call_times[source].append(now)
                
                return func(*args, **kwargs)
            
            return wrapper
        return decorator


# Global rate limiter instance
rate_limiter = RateLimiter()


def main():
    """Test the error handling system."""
    handler = MLBErrorHandler()
    
    print("🛡️ Testing MLB Error Handling System")
    print("=" * 40)
    
    # Test error handling
    try:
        raise ConnectionError("Test connection error")
    except Exception as e:
        handler.handle_error(e, "test_context", "test_operation")
    
    # Test system health
    health = handler.get_system_health()
    print("System Health:")
    print(json.dumps(health, indent=2))
    
    # Test safe request
    response = handler.safe_request("https://httpbin.org/status/200", "test")
    print(f"Safe request test: {'Success' if response else 'Failed'}")


if __name__ == "__main__":
    main()
