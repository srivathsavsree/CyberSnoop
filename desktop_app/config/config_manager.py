"""
Configuration Manager for CyberSnoop Desktop Application
Handles application settings, user preferences, and configuration persistence.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class ConfigManager:
    """Manages application configuration and settings"""
    
    DEFAULT_CONFIG = {
        "application": {
            "name": "CyberSnoop",
            "version": "1.0.0",
            "auto_start": False,
            "minimize_to_tray": True,
            "check_updates": True
        },
        "network": {
            "interface": "auto",
            "capture_filter": "",
            "packet_buffer_size": 1000000,
            "max_packet_storage": 100000
        },
        "threat_detection": {
            "sensitivity": "medium",
            "port_scan_threshold": 10,
            "brute_force_threshold": 5,
            "ddos_threshold": 1000,
            "anomaly_detection": True
        },
        "database": {
            "path": "cybersnoop.db",
            "max_size_mb": 500,
            "retention_days": 30,
            "auto_cleanup": True
        },
        "api": {
            "port": 8888,
            "host": "localhost",
            "cors_enabled": False,
            "rate_limiting": True
        },
        "logging": {
            "level": "INFO",
            "max_file_size_mb": 10,
            "backup_count": 5,
            "console_output": True
        },
        "alerts": {
            "show_notifications": True,
            "sound_enabled": False,
            "email_notifications": False,
            "email_smtp_server": "",
            "email_username": "",
            "email_password": ""
        },
        "ui": {
            "theme": "dark",
            "auto_refresh_interval": 5,
            "show_welcome": True,
            "dashboard_layout": "default"
        }
    }
    
    def __init__(self):
        self.config_dir = Path.home() / "AppData" / "Local" / "CyberSnoop"
        self.config_file = self.config_dir / "config.json"
        self.config = {}
        
        self._ensure_config_directory()
        self._load_config()
        
    def _ensure_config_directory(self):
        """Ensure configuration directory exists"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Configuration directory: {self.config_dir}")
        except Exception as e:
            logging.error(f"Failed to create config directory: {e}")
            raise
            
    def _load_config(self):
        """Load configuration from file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    
                # Merge with defaults for any missing keys
                self.config = self._merge_with_defaults(self.config)
                logging.info("Configuration loaded successfully")
            else:
                # Create default configuration
                self.config = self.DEFAULT_CONFIG.copy()
                self._save_config()
                logging.info("Default configuration created")
                
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            self.config = self.DEFAULT_CONFIG.copy()
            
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults to ensure all keys exist"""
        result = self.DEFAULT_CONFIG.copy()
        
        def deep_merge(default_dict, user_dict):
            for key, value in user_dict.items():
                if key in default_dict:
                    if isinstance(value, dict) and isinstance(default_dict[key], dict):
                        default_dict[key] = deep_merge(default_dict[key], value)
                    else:
                        default_dict[key] = value
            return default_dict
            
        return deep_merge(result, config)
        
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logging.info("Configuration saved successfully")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: get("network.interface") returns config["network"]["interface"]
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation
        Example: set("network.interface", "eth0")
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        # Set the value
        config[keys[-1]] = value
        self._save_config()
        
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {})
        
    def set_section(self, section: str, values: Dict[str, Any]):
        """Set entire configuration section"""
        self.config[section] = values
        self._save_config()
        
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self._save_config()
        logging.info("Configuration reset to defaults")
        
    def get_database_path(self) -> Path:
        """Get full path to database file"""
        db_filename = self.get("database.path", "cybersnoop.db")
        return self.config_dir / db_filename
        
    def get_log_directory(self) -> Path:
        """Get log directory path"""
        log_dir = self.config_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        return log_dir
        
    def export_config(self, file_path: str):
        """Export configuration to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logging.info(f"Configuration exported to {file_path}")
        except Exception as e:
            logging.error(f"Failed to export configuration: {e}")
            raise
            
    def import_config(self, file_path: str):
        """Import configuration from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                
            # Validate and merge with defaults
            self.config = self._merge_with_defaults(imported_config)
            self._save_config()
            logging.info(f"Configuration imported from {file_path}")
        except Exception as e:
            logging.error(f"Failed to import configuration: {e}")
            raise
            
    def validate_config(self) -> Dict[str, str]:
        """Validate configuration and return any errors"""
        errors = {}
        
        # Validate network settings
        if not isinstance(self.get("network.packet_buffer_size"), int):
            errors["network.packet_buffer_size"] = "Must be an integer"
            
        if not isinstance(self.get("network.max_packet_storage"), int):
            errors["network.max_packet_storage"] = "Must be an integer"
            
        # Validate threshold settings
        thresholds = [
            "threat_detection.port_scan_threshold",
            "threat_detection.brute_force_threshold",
            "threat_detection.ddos_threshold"
        ]
        
        for threshold in thresholds:
            value = self.get(threshold)
            if not isinstance(value, int) or value <= 0:
                errors[threshold] = "Must be a positive integer"
                
        # Validate database settings
        max_size = self.get("database.max_size_mb")
        if not isinstance(max_size, int) or max_size <= 0:
            errors["database.max_size_mb"] = "Must be a positive integer"
            
        retention_days = self.get("database.retention_days")
        if not isinstance(retention_days, int) or retention_days <= 0:
            errors["database.retention_days"] = "Must be a positive integer"
            
        # Validate API settings
        api_port = self.get("api.port")
        if not isinstance(api_port, int) or not (1024 <= api_port <= 65535):
            errors["api.port"] = "Must be an integer between 1024 and 65535"
            
        return errors
        
    def __str__(self):
        """String representation of configuration"""
        return f"ConfigManager(config_file={self.config_file})"
        
    def __repr__(self):
        return self.__str__()
