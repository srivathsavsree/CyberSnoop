"""
Settings Dialog for CyberSnoop Desktop Application
Provides user interface for configuring application settings.
"""

import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QSpinBox, QCheckBox, QComboBox,
    QPushButton, QLabel, QGroupBox, QSlider, QTextEdit,
    QDialogButtonBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class SettingsDialog(QDialog):
    """Settings dialog for CyberSnoop configuration"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("CyberSnoop Settings")
        self.setGeometry(200, 200, 600, 500)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_general_tab()
        self.create_network_tab()
        self.create_detection_tab()
        self.create_alerts_tab()
        self.create_advanced_tab()
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        
        layout.addWidget(button_box)
        
    def create_general_tab(self):
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Application settings group
        app_group = QGroupBox("Application Settings")
        app_layout = QFormLayout(app_group)
        
        self.auto_start_check = QCheckBox("Start with Windows")
        app_layout.addRow("Startup:", self.auto_start_check)
        
        self.minimize_tray_check = QCheckBox("Minimize to system tray")
        app_layout.addRow("Minimize:", self.minimize_tray_check)
        
        self.check_updates_check = QCheckBox("Check for updates automatically")
        app_layout.addRow("Updates:", self.check_updates_check)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        app_layout.addRow("Theme:", self.theme_combo)
        
        layout.addWidget(app_group)
        
        # UI settings group
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(1, 60)
        self.refresh_interval_spin.setSuffix(" seconds")
        ui_layout.addRow("Refresh Interval:", self.refresh_interval_spin)
        
        self.show_welcome_check = QCheckBox("Show welcome screen")
        ui_layout.addRow("Welcome:", self.show_welcome_check)
        
        layout.addWidget(ui_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "General")
        
    def create_network_tab(self):
        """Create enhanced network settings tab with real interface detection"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Network interface group
        interface_group = QGroupBox("Network Interface Selection")
        interface_layout = QVBoxLayout(interface_group)
        
        # Interface selection with details
        interface_selection_layout = QHBoxLayout()
        
        interface_label = QLabel("Active Interface:")
        self.interface_combo = QComboBox()
        self.interface_combo.setMinimumWidth(300)
        self.refresh_interfaces_btn = QPushButton("🔄 Refresh")
        self.refresh_interfaces_btn.clicked.connect(self.refresh_network_interfaces)
        
        interface_selection_layout.addWidget(interface_label)
        interface_selection_layout.addWidget(self.interface_combo)
        interface_selection_layout.addWidget(self.refresh_interfaces_btn)
        interface_selection_layout.addStretch()
        
        interface_layout.addLayout(interface_selection_layout)
        
        # Interface details display
        self.interface_details = QTextEdit()
        self.interface_details.setMaximumHeight(100)
        self.interface_details.setReadOnly(True)
        self.interface_details.setPlaceholderText("Select an interface to view details...")
        interface_layout.addWidget(QLabel("Interface Details:"))
        interface_layout.addWidget(self.interface_details)
        
        # Privilege status
        self.privilege_status = QLabel("Checking privileges...")
        self.privilege_status.setStyleSheet("color: orange; font-weight: bold;")
        interface_layout.addWidget(self.privilege_status)
        
        # Advanced settings
        advanced_layout = QFormLayout()
        
        self.capture_filter_edit = QLineEdit()
        self.capture_filter_edit.setPlaceholderText("e.g., tcp port 80 or host 192.168.1.1")
        advanced_layout.addRow("Capture Filter:", self.capture_filter_edit)
        
        self.promiscuous_mode_check = QCheckBox("Enable promiscuous mode")
        self.promiscuous_mode_check.setToolTip("Capture all network traffic (requires admin privileges)")
        advanced_layout.addRow("Promiscuous Mode:", self.promiscuous_mode_check)
        
        interface_layout.addLayout(advanced_layout)
        
        layout.addWidget(interface_group)
        
        # Performance group
        performance_group = QGroupBox("Performance Settings")
        performance_layout = QFormLayout(performance_group)
        
        self.buffer_size_spin = QSpinBox()
        self.buffer_size_spin.setRange(100000, 10000000)
        self.buffer_size_spin.setValue(1000000)
        self.buffer_size_spin.setToolTip("Packet capture buffer size in bytes")
        performance_layout.addRow("Buffer Size:", self.buffer_size_spin)
        
        self.max_packets_spin = QSpinBox()
        self.max_packets_spin.setRange(10000, 1000000)
        self.max_packets_spin.setValue(100000)
        self.max_packets_spin.setToolTip("Maximum number of packets to store in database")
        performance_layout.addRow("Max Stored Packets:", self.max_packets_spin)
        
        self.capture_timeout_spin = QSpinBox()
        self.capture_timeout_spin.setRange(1, 3600)
        self.capture_timeout_spin.setValue(30)
        self.capture_timeout_spin.setSuffix(" seconds")
        self.capture_timeout_spin.setToolTip("Timeout for packet capture operations")
        performance_layout.addRow("Capture Timeout:", self.capture_timeout_spin)
        
        layout.addWidget(performance_group)
        
        # Initialize interface detection
        self.refresh_network_interfaces()
        self.check_privileges()
        
        # Connect interface selection change
        self.interface_combo.currentTextChanged.connect(self.on_interface_selected)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Network")
        
    def refresh_network_interfaces(self):
        """Refresh the list of available network interfaces"""
        try:
            from backend.network_monitor import NetworkMonitor
            
            # Create a temporary network monitor to get interfaces
            temp_monitor = NetworkMonitor(self.config_manager)
            interfaces = temp_monitor.get_interfaces()
            
            # Clear existing items
            self.interface_combo.clear()
            
            # Add auto-detect option
            self.interface_combo.addItem("Auto-detect", {"type": "auto"})
            
            # Add detected interfaces
            for interface in interfaces:
                display_name = f"{interface['name']} ({interface['ip']})"
                if interface.get('description'):
                    display_name = f"{interface['description']} - {interface['ip']}"
                
                self.interface_combo.addItem(display_name, interface)
            
            # Add simulation mode option
            self.interface_combo.addItem("Simulation Mode (No Admin Required)", {"type": "simulation"})
            
            logging.info(f"Loaded {len(interfaces)} network interfaces")
            
        except Exception as e:
            logging.error(f"Failed to refresh network interfaces: {e}")
            self.interface_combo.clear()
            self.interface_combo.addItem("Error loading interfaces", {"type": "error"})
    
    def on_interface_selected(self):
        """Handle interface selection change"""
        try:
            current_data = self.interface_combo.currentData()
            if not current_data:
                return
            
            if current_data.get("type") == "auto":
                self.interface_details.setText("Automatic interface detection will be used.")
            elif current_data.get("type") == "simulation":
                self.interface_details.setText("Simulation mode - generates fake network data for testing.")
            elif current_data.get("type") == "error":
                self.interface_details.setText("Failed to detect network interfaces.")
            else:
                # Display interface details
                details = []
                details.append(f"Name: {current_data.get('name', 'Unknown')}")
                details.append(f"IP Address: {current_data.get('ip', 'Unknown')}")
                
                if current_data.get('description'):
                    details.append(f"Description: {current_data.get('description')}")
                
                if current_data.get('mac'):
                    details.append(f"MAC Address: {current_data.get('mac')}")
                
                if current_data.get('speed'):
                    details.append(f"Speed: {current_data.get('speed')}")
                
                if current_data.get('media_type'):
                    details.append(f"Media Type: {current_data.get('media_type')}")
                
                details.append(f"Status: {current_data.get('status', 'Unknown')}")
                details.append(f"Detection Method: {current_data.get('type', 'Unknown')}")
                
                self.interface_details.setText("\n".join(details))
                
        except Exception as e:
            logging.error(f"Error updating interface details: {e}")
            self.interface_details.setText("Error loading interface details.")
    
    def check_privileges(self):
        """Check and display current privilege status"""
        try:
            from backend.privilege_manager import get_privilege_level, check_network_capture_privileges
            
            privilege_level = get_privilege_level()
            has_capture, capture_reason = check_network_capture_privileges()
            
            if has_capture:
                self.privilege_status.setText(f"✅ {privilege_level} - Network capture available")
                self.privilege_status.setStyleSheet("color: green; font-weight: bold;")
                self.promiscuous_mode_check.setEnabled(True)
            else:
                self.privilege_status.setText(f"⚠️ {privilege_level} - Limited capture mode")
                self.privilege_status.setStyleSheet("color: orange; font-weight: bold;")
                self.promiscuous_mode_check.setEnabled(False)
                self.promiscuous_mode_check.setChecked(False)
                
        except Exception as e:
            logging.error(f"Error checking privileges: {e}")
            self.privilege_status.setText("❌ Error checking privileges")
            self.privilege_status.setStyleSheet("color: red; font-weight: bold;")
        
    def create_detection_tab(self):
        """Create threat detection settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Detection sensitivity group
        sensitivity_group = QGroupBox("Detection Sensitivity")
        sensitivity_layout = QFormLayout(sensitivity_group)
        
        self.sensitivity_combo = QComboBox()
        self.sensitivity_combo.addItems(["Low", "Medium", "High", "Custom"])
        sensitivity_layout.addRow("Overall Sensitivity:", self.sensitivity_combo)
        
        self.anomaly_detection_check = QCheckBox("Enable anomaly detection")
        sensitivity_layout.addRow("Anomaly Detection:", self.anomaly_detection_check)
        
        layout.addWidget(sensitivity_group)
        
        # Threat thresholds group
        thresholds_group = QGroupBox("Threat Thresholds")
        thresholds_layout = QFormLayout(thresholds_group)
        
        self.port_scan_spin = QSpinBox()
        self.port_scan_spin.setRange(1, 100)
        self.port_scan_spin.setValue(10)
        thresholds_layout.addRow("Port Scan Threshold:", self.port_scan_spin)
        
        self.brute_force_spin = QSpinBox()
        self.brute_force_spin.setRange(1, 50)
        self.brute_force_spin.setValue(5)
        thresholds_layout.addRow("Brute Force Threshold:", self.brute_force_spin)
        
        self.ddos_spin = QSpinBox()
        self.ddos_spin.setRange(100, 10000)
        self.ddos_spin.setValue(1000)
        thresholds_layout.addRow("DDoS Threshold:", self.ddos_spin)
        
        layout.addWidget(thresholds_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Detection")
        
    def create_alerts_tab(self):
        """Create alerts settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Notification settings group
        notification_group = QGroupBox("Notifications")
        notification_layout = QFormLayout(notification_group)
        
        self.show_notifications_check = QCheckBox("Show desktop notifications")
        notification_layout.addRow("Desktop Alerts:", self.show_notifications_check)
        
        self.sound_enabled_check = QCheckBox("Play sound for alerts")
        notification_layout.addRow("Sound Alerts:", self.sound_enabled_check)
        
        layout.addWidget(notification_group)
        
        # Email settings group
        email_group = QGroupBox("Email Notifications")
        email_layout = QFormLayout(email_group)
        
        self.email_notifications_check = QCheckBox("Enable email notifications")
        email_layout.addRow("Email Alerts:", self.email_notifications_check)
        
        self.smtp_server_edit = QLineEdit()
        self.smtp_server_edit.setPlaceholderText("smtp.gmail.com:587")
        email_layout.addRow("SMTP Server:", self.smtp_server_edit)
        
        self.email_username_edit = QLineEdit()
        email_layout.addRow("Username:", self.email_username_edit)
        
        self.email_password_edit = QLineEdit()
        self.email_password_edit.setEchoMode(QLineEdit.Password)
        email_layout.addRow("Password:", self.email_password_edit)
        
        layout.addWidget(email_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Alerts")
        
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Database settings group
        database_group = QGroupBox("Database Settings")
        database_layout = QFormLayout(database_group)
        
        self.max_db_size_spin = QSpinBox()
        self.max_db_size_spin.setRange(10, 10000)
        self.max_db_size_spin.setValue(500)
        self.max_db_size_spin.setSuffix(" MB")
        database_layout.addRow("Max Database Size:", self.max_db_size_spin)
        
        self.retention_days_spin = QSpinBox()
        self.retention_days_spin.setRange(1, 365)
        self.retention_days_spin.setValue(30)
        self.retention_days_spin.setSuffix(" days")
        database_layout.addRow("Data Retention:", self.retention_days_spin)
        
        self.auto_cleanup_check = QCheckBox("Auto cleanup old data")
        database_layout.addRow("Auto Cleanup:", self.auto_cleanup_check)
        
        layout.addWidget(database_group)
        
        # Logging settings group
        logging_group = QGroupBox("Logging Settings")
        logging_layout = QFormLayout(logging_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        logging_layout.addRow("Log Level:", self.log_level_combo)
        
        self.console_output_check = QCheckBox("Show console output")
        logging_layout.addRow("Console Output:", self.console_output_check)
        
        layout.addWidget(logging_group)
        
        # Configuration management
        config_group = QGroupBox("Configuration Management")
        config_layout = QVBoxLayout(config_group)
        
        config_buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export Settings")
        export_btn.clicked.connect(self.export_config)
        config_buttons_layout.addWidget(export_btn)
        
        import_btn = QPushButton("Import Settings")
        import_btn.clicked.connect(self.import_config)
        config_buttons_layout.addWidget(import_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        config_buttons_layout.addWidget(reset_btn)
        
        config_layout.addLayout(config_buttons_layout)
        layout.addWidget(config_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Advanced")
        
    def load_settings(self):
        """Load settings from configuration manager"""
        # General settings
        self.auto_start_check.setChecked(self.config_manager.get("application.auto_start", False))
        self.minimize_tray_check.setChecked(self.config_manager.get("application.minimize_to_tray", True))
        self.check_updates_check.setChecked(self.config_manager.get("application.check_updates", True))
        
        theme = self.config_manager.get("ui.theme", "dark")
        theme_index = {"light": 0, "dark": 1, "auto": 2}.get(theme.lower(), 1)
        self.theme_combo.setCurrentIndex(theme_index)
        
        self.refresh_interval_spin.setValue(self.config_manager.get("ui.auto_refresh_interval", 5))
        self.show_welcome_check.setChecked(self.config_manager.get("ui.show_welcome", True))
        
        # Network settings
        self.capture_filter_edit.setText(self.config_manager.get("network.capture_filter", ""))
        self.buffer_size_spin.setValue(self.config_manager.get("network.packet_buffer_size", 1000000))
        self.max_packets_spin.setValue(self.config_manager.get("network.max_packet_storage", 100000))
        
        # Detection settings
        sensitivity = self.config_manager.get("threat_detection.sensitivity", "medium")
        sensitivity_index = {"low": 0, "medium": 1, "high": 2, "custom": 3}.get(sensitivity.lower(), 1)
        self.sensitivity_combo.setCurrentIndex(sensitivity_index)
        
        self.anomaly_detection_check.setChecked(self.config_manager.get("threat_detection.anomaly_detection", True))
        self.port_scan_spin.setValue(self.config_manager.get("threat_detection.port_scan_threshold", 10))
        self.brute_force_spin.setValue(self.config_manager.get("threat_detection.brute_force_threshold", 5))
        self.ddos_spin.setValue(self.config_manager.get("threat_detection.ddos_threshold", 1000))
        
        # Alert settings
        self.show_notifications_check.setChecked(self.config_manager.get("alerts.show_notifications", True))
        self.sound_enabled_check.setChecked(self.config_manager.get("alerts.sound_enabled", False))
        self.email_notifications_check.setChecked(self.config_manager.get("alerts.email_notifications", False))
        self.smtp_server_edit.setText(self.config_manager.get("alerts.email_smtp_server", ""))
        self.email_username_edit.setText(self.config_manager.get("alerts.email_username", ""))
        self.email_password_edit.setText(self.config_manager.get("alerts.email_password", ""))
        
        # Advanced settings
        self.max_db_size_spin.setValue(self.config_manager.get("database.max_size_mb", 500))
        self.retention_days_spin.setValue(self.config_manager.get("database.retention_days", 30))
        self.auto_cleanup_check.setChecked(self.config_manager.get("database.auto_cleanup", True))
        
        log_level = self.config_manager.get("logging.level", "INFO")
        log_level_index = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}.get(log_level, 1)
        self.log_level_combo.setCurrentIndex(log_level_index)
        
        self.console_output_check.setChecked(self.config_manager.get("logging.console_output", True))
        
    def apply_settings(self):
        """Apply settings to configuration manager"""
        # General settings
        self.config_manager.set("application.auto_start", self.auto_start_check.isChecked())
        self.config_manager.set("application.minimize_to_tray", self.minimize_tray_check.isChecked())
        self.config_manager.set("application.check_updates", self.check_updates_check.isChecked())
        
        themes = ["light", "dark", "auto"]
        self.config_manager.set("ui.theme", themes[self.theme_combo.currentIndex()])
        
        self.config_manager.set("ui.auto_refresh_interval", self.refresh_interval_spin.value())
        self.config_manager.set("ui.show_welcome", self.show_welcome_check.isChecked())
        
        # Network settings
        self.config_manager.set("network.capture_filter", self.capture_filter_edit.text())
        self.config_manager.set("network.packet_buffer_size", self.buffer_size_spin.value())
        self.config_manager.set("network.max_packet_storage", self.max_packets_spin.value())
        
        # Detection settings
        sensitivities = ["low", "medium", "high", "custom"]
        self.config_manager.set("threat_detection.sensitivity", sensitivities[self.sensitivity_combo.currentIndex()])
        
        self.config_manager.set("threat_detection.anomaly_detection", self.anomaly_detection_check.isChecked())
        self.config_manager.set("threat_detection.port_scan_threshold", self.port_scan_spin.value())
        self.config_manager.set("threat_detection.brute_force_threshold", self.brute_force_spin.value())
        self.config_manager.set("threat_detection.ddos_threshold", self.ddos_spin.value())
        
        # Alert settings
        self.config_manager.set("alerts.show_notifications", self.show_notifications_check.isChecked())
        self.config_manager.set("alerts.sound_enabled", self.sound_enabled_check.isChecked())
        self.config_manager.set("alerts.email_notifications", self.email_notifications_check.isChecked())
        self.config_manager.set("alerts.email_smtp_server", self.smtp_server_edit.text())
        self.config_manager.set("alerts.email_username", self.email_username_edit.text())
        self.config_manager.set("alerts.email_password", self.email_password_edit.text())
        
        # Advanced settings
        self.config_manager.set("database.max_size_mb", self.max_db_size_spin.value())
        self.config_manager.set("database.retention_days", self.retention_days_spin.value())
        self.config_manager.set("database.auto_cleanup", self.auto_cleanup_check.isChecked())
        
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        self.config_manager.set("logging.level", log_levels[self.log_level_combo.currentIndex()])
        
        self.config_manager.set("logging.console_output", self.console_output_check.isChecked())
        
    def accept_settings(self):
        """Accept and apply settings"""
        self.apply_settings()
        self.accept()
        
    def export_config(self):
        """Export configuration to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Configuration", "cybersnoop_config.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.config_manager.export_config(file_path)
                QMessageBox.information(self, "Export Successful", f"Configuration exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export configuration: {e}")
                
    def import_config(self):
        """Import configuration from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Configuration", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.config_manager.import_config(file_path)
                self.load_settings()  # Reload UI with imported settings
                QMessageBox.information(self, "Import Successful", f"Configuration imported from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", f"Failed to import configuration: {e}")
                
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self, "Reset to Defaults",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config_manager.reset_to_defaults()
            self.load_settings()  # Reload UI with default settings
            QMessageBox.information(self, "Reset Complete", "All settings have been reset to defaults.")
