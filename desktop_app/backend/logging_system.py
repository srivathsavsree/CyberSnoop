"""
Logging System for CyberSnoop
Centralized logging with file rotation, levels, and real-time monitoring.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional, Dict, Any, List
import json

class CyberSnoopLogger:
    """Enhanced logging system for CyberSnoop"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.loggers = {}
        self.log_dir = Path(config_manager.config_dir) / "logs"
        
        # Ensure log directory exists
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize main loggers
        self._setup_main_logger()
        self._setup_security_logger()
        self._setup_network_logger()
        self._setup_api_logger()
        
    def _setup_main_logger(self):
        """Setup main application logger"""
        logger = logging.getLogger("cybersnoop.main")
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            self.log_dir / "cybersnoop_main.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        self.loggers["main"] = logger
        
    def _setup_security_logger(self):
        """Setup security events logger"""
        logger = logging.getLogger("cybersnoop.security")
        logger.setLevel(logging.INFO)
        
        # Separate file for security events
        security_handler = TimedRotatingFileHandler(
            self.log_dir / "security_events.log",
            when="midnight",
            interval=1,
            backupCount=30  # Keep 30 days
        )
        security_handler.setLevel(logging.INFO)
        
        # JSON format for security events
        class SecurityFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                    "level": record.levelname,
                    "event_type": getattr(record, 'event_type', 'unknown'),
                    "message": record.getMessage(),
                    "source": record.name,
                    "details": getattr(record, 'details', {})
                }
                return json.dumps(log_entry)
        
        security_handler.setFormatter(SecurityFormatter())
        logger.addHandler(security_handler)
        
        self.loggers["security"] = logger
        
    def _setup_network_logger(self):
        """Setup network monitoring logger"""
        logger = logging.getLogger("cybersnoop.network")
        logger.setLevel(logging.DEBUG)
        
        # Network events file
        network_handler = RotatingFileHandler(
            self.log_dir / "network_monitoring.log",
            maxBytes=50*1024*1024,  # 50MB (network logs can be large)
            backupCount=3
        )
        network_handler.setLevel(logging.DEBUG)
        network_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        network_handler.setFormatter(network_formatter)
        
        logger.addHandler(network_handler)
        self.loggers["network"] = logger
        
    def _setup_api_logger(self):
        """Setup API server logger"""
        logger = logging.getLogger("cybersnoop.api")
        logger.setLevel(logging.INFO)
        
        # API access log
        api_handler = TimedRotatingFileHandler(
            self.log_dir / "api_access.log",
            when="midnight",
            interval=1,
            backupCount=7  # Keep 7 days
        )
        api_handler.setLevel(logging.INFO)
        api_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        api_handler.setFormatter(api_formatter)
        
        logger.addHandler(api_handler)
        self.loggers["api"] = logger
        
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger by name"""
        return self.loggers.get(name, self.loggers["main"])
        
    def log_security_event(self, event_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log a security event"""
        logger = self.loggers["security"]
        
        # Create log record with extra attributes
        record = logger.makeRecord(
            logger.name, logging.WARNING, "", 0, message, (), None
        )
        record.event_type = event_type
        record.details = details or {}
        
        logger.handle(record)
        
    def log_threat_detected(self, threat_info: Dict[str, Any]):
        """Log a detected threat"""
        self.log_security_event(
            "threat_detected",
            f"Threat detected: {threat_info.get('type', 'Unknown')}",
            threat_info
        )
        
    def log_network_event(self, event_type: str, message: str, packet_info: Optional[Dict[str, Any]] = None):
        """Log a network monitoring event"""
        logger = self.loggers["network"]
        
        if packet_info:
            full_message = f"[{event_type}] {message} | Packet: {packet_info}"
        else:
            full_message = f"[{event_type}] {message}"
            
        logger.info(full_message)
        
    def log_api_request(self, method: str, endpoint: str, client_ip: str, status_code: int):
        """Log API request"""
        logger = self.loggers["api"]
        logger.info(f"{client_ip} - {method} {endpoint} - {status_code}")
        
    def get_recent_logs(self, log_type: str = "main", lines: int = 100) -> List[str]:
        """Get recent log entries"""
        try:
            log_files = {
                "main": "cybersnoop_main.log",
                "security": "security_events.log", 
                "network": "network_monitoring.log",
                "api": "api_access.log"
            }
            
            log_file = self.log_dir / log_files.get(log_type, "cybersnoop_main.log")
            
            if not log_file.exists():
                return []
                
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return [line.strip() for line in all_lines[-lines:]]
                
        except Exception as e:
            print(f"Error reading logs: {e}")
            return []
            
    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        stats = {
            "log_directory": str(self.log_dir),
            "log_files": [],
            "total_size": 0
        }
        
        try:
            for log_file in self.log_dir.glob("*.log"):
                file_stats = log_file.stat()
                stats["log_files"].append({
                    "name": log_file.name,
                    "size": file_stats.st_size,
                    "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                })
                stats["total_size"] += file_stats.st_size
                
        except Exception as e:
            self.loggers["main"].error(f"Error getting log stats: {e}")
            
        return stats
        
    def cleanup_old_logs(self, days: int = 30):
        """Clean up log files older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.loggers["main"].info(f"Cleaned up old log file: {log_file.name}")
                    
        except Exception as e:
            self.loggers["main"].error(f"Error cleaning up logs: {e}")

# Global logger instance
_logger_instance: Optional[CyberSnoopLogger] = None

def initialize_logging(config_manager) -> CyberSnoopLogger:
    """Initialize the global logging system"""
    global _logger_instance
    _logger_instance = CyberSnoopLogger(config_manager)
    return _logger_instance

def get_logger(name: str = "main") -> logging.Logger:
    """Get a logger instance"""
    if _logger_instance is None:
        # Fallback to basic logging if not initialized
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(f"cybersnoop.{name}")
    
    return _logger_instance.get_logger(name)

def log_security_event(event_type: str, message: str, details: Optional[Dict[str, Any]] = None):
    """Convenience function for logging security events"""
    if _logger_instance:
        _logger_instance.log_security_event(event_type, message, details)

def log_threat_detected(threat_info: Dict[str, Any]):
    """Convenience function for logging threats"""
    if _logger_instance:
        _logger_instance.log_threat_detected(threat_info)
