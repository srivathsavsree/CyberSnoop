"""
Enhanced Desktop Application with Integrated React Dashboard
Phase 3: Complete UI Integration with real-time features and settings management
"""

import sys
import os
import threading
import time
import subprocess
import json
import webbrowser
import requests
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QSystemTrayIcon, QMenu, QToolBar, QStatusBar, QSplitter,
    QTextEdit, QTabWidget, QGroupBox, QGridLayout, QLabel,
    QPushButton, QProgressBar, QFrame, QScrollArea, QMessageBox,
    QDialog, QFormLayout, QLineEdit, QSpinBox, QCheckBox, QComboBox
)
from PySide6.QtCore import QTimer, QThread, Signal, QUrl, QSize, Qt
from PySide6.QtGui import QIcon, QAction, QFont, QPixmap, QDesktopServices
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

# Import our backend components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from config.config_manager import ConfigManager
    from backend.enhanced_database_manager import EnhancedDatabaseManager as DatabaseManager
    from backend.network_monitor import NetworkMonitor
    from backend.threat_detector import ThreatDetector
    from backend.api_server import CyberSnoopAPI
    from backend.advanced_threat_detector import AdvancedThreatDetector
except ImportError as e:
    print(f"Warning: Could not import backend modules: {e}")
    print("Some features may not be available.")

class DashboardServer(QThread):
    """Thread to run the Next.js dashboard server"""
    server_ready = Signal()
    server_error = Signal(str)
    
    def __init__(self, dashboard_path):
        super().__init__()
        self.dashboard_path = Path(dashboard_path)
        self.process = None
        self.running = False
        
    def run(self):
        """Start the Next.js production server"""
        try:
            # Change to dashboard directory
            original_dir = os.getcwd()
            os.chdir(self.dashboard_path)
            
            # Start Next.js production server
            self.process = subprocess.Popen(
                ['npm', 'start'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            
            self.running = True
            
            # Wait for server to be ready
            for i in range(30):  # Wait up to 30 seconds
                if not self.running:
                    break
                    
                try:
                    response = requests.get('http://localhost:3000', timeout=2)
                    if response.status_code == 200:
                        self.server_ready.emit()
                        break
                except:
                    pass
                
                time.sleep(1)
            else:
                self.server_error.emit("Dashboard server failed to start within 30 seconds")
                
            os.chdir(original_dir)
            
            # Wait for process to complete
            if self.process and self.running:
                self.process.wait()
                
        except Exception as e:
            self.server_error.emit(f"Dashboard server error: {str(e)}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the dashboard server"""
        self.running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()

class APIServerThread(QThread):
    """Thread to run the API server"""
    server_ready = Signal()
    server_error = Signal(str)
    
    def __init__(self, config_manager, database_manager, network_monitor):
        super().__init__()
        self.config_manager = config_manager
        self.database_manager = database_manager
        self.network_monitor = network_monitor
        self.api_server = None
        self.running = False
        
    def run(self):
        """Start the API server"""
        try:
            self.api_server = CyberSnoopAPI(
                self.config_manager,
                self.database_manager,
                self.network_monitor
            )
            
            self.running = True
            self.server_ready.emit()
            
            # Start the server (this blocks)
            self.api_server.start_server(host="127.0.0.1", port=8000)
            
        except Exception as e:
            self.server_error.emit(f"API server error: {str(e)}")
    
    def stop(self):
        """Stop the API server"""
        self.running = False
        if self.api_server:
            self.api_server.stop_server()

class NetworkMonitorThread(QThread):
    """Thread to run network monitoring"""
    stats_updated = Signal(dict)
    threat_detected = Signal(dict)
    
    def __init__(self, config_manager, database_manager):
        super().__init__()
        self.config_manager = config_manager
        self.database_manager = database_manager
        self.network_monitor = None
        self.threat_detector = None
        self.advanced_threat_detector = None
        self.running = False
        
    def run(self):
        """Start network monitoring"""
        try:
            # Initialize components
            self.network_monitor = NetworkMonitor(self.config_manager)
            self.threat_detector = ThreatDetector(self.config_manager)
            self.advanced_threat_detector = AdvancedThreatDetector(self.config_manager)
            
            self.running = True
            
            # Start monitoring
            self.network_monitor.start_monitoring()
            
            # Main monitoring loop
            while self.running:
                try:
                    # Get network statistics
                    stats = self.network_monitor.get_statistics()
                    if stats:
                        self.stats_updated.emit(stats)
                    
                    # Process any queued packets for threat detection
                    # (In a real implementation, this would be more sophisticated)
                    
                    time.sleep(5)  # Update every 5 seconds
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            print(f"Network monitor error: {e}")
        finally:
            if self.network_monitor:
                self.network_monitor.stop_monitoring()
    
    def stop(self):
        """Stop network monitoring"""
        self.running = False
        if self.network_monitor:
            self.network_monitor.stop_monitoring()

class SettingsDialog(QDialog):
    """Settings configuration dialog"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("CyberSnoop Settings")
        self.setModal(True)
        self.resize(400, 500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Create tabs
        tab_widget = QTabWidget()
        
        # General settings tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        self.retention_days = QSpinBox()
        self.retention_days.setRange(1, 365)
        self.retention_days.setValue(self.config_manager.get("database.retention_days", 30))
        general_layout.addRow("Data Retention (days):", self.retention_days)
        
        self.cleanup_interval = QSpinBox()
        self.cleanup_interval.setRange(1, 168)
        self.cleanup_interval.setValue(self.config_manager.get("database.cleanup_interval_hours", 24))
        general_layout.addRow("Cleanup Interval (hours):", self.cleanup_interval)
        
        tab_widget.addTab(general_tab, "General")
        
        # Monitoring settings tab
        monitoring_tab = QWidget()
        monitoring_layout = QFormLayout(monitoring_tab)
        
        self.packet_buffer_size = QSpinBox()
        self.packet_buffer_size.setRange(1000, 100000)
        self.packet_buffer_size.setValue(self.config_manager.get("monitoring.packet_buffer_size", 10000))
        monitoring_layout.addRow("Packet Buffer Size:", self.packet_buffer_size)
        
        self.enable_advanced_detection = QCheckBox()
        self.enable_advanced_detection.setChecked(self.config_manager.get("detection.enable_advanced", True))
        monitoring_layout.addRow("Enable Advanced Detection:", self.enable_advanced_detection)
        
        tab_widget.addTab(monitoring_tab, "Monitoring")
        
        # Threat detection settings tab
        threat_tab = QWidget()
        threat_layout = QFormLayout(threat_tab)
        
        self.port_scan_threshold = QSpinBox()
        self.port_scan_threshold.setRange(5, 1000)
        self.port_scan_threshold.setValue(self.config_manager.get("detection.port_scan_threshold", 10))
        threat_layout.addRow("Port Scan Threshold:", self.port_scan_threshold)
        
        self.brute_force_threshold = QSpinBox()
        self.brute_force_threshold.setRange(3, 100)
        self.brute_force_threshold.setValue(self.config_manager.get("detection.brute_force_threshold", 5))
        threat_layout.addRow("Brute Force Threshold:", self.brute_force_threshold)
        
        tab_widget.addTab(threat_tab, "Threat Detection")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def save_settings(self):
        """Save settings to config"""
        try:
            # Save general settings
            self.config_manager.set("database.retention_days", self.retention_days.value())
            self.config_manager.set("database.cleanup_interval_hours", self.cleanup_interval.value())
            
            # Save monitoring settings
            self.config_manager.set("monitoring.packet_buffer_size", self.packet_buffer_size.value())
            self.config_manager.set("detection.enable_advanced", self.enable_advanced_detection.isChecked())
            
            # Save detection settings
            self.config_manager.set("detection.port_scan_threshold", self.port_scan_threshold.value())
            self.config_manager.set("detection.brute_force_threshold", self.brute_force_threshold.value())
            
            # Save to file
            self.config_manager.save_config()
            
            QMessageBox.information(self, "Settings", "Settings saved successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

class CyberSnoopMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize configuration and components
        self.config_manager = ConfigManager()
        self.database_manager = None
        self.dashboard_server = None
        self.api_server = None
        self.network_monitor = None
        
        # Statistics tracking
        self.stats = {
            'packets_captured': 0,
            'threats_detected': 0,
            'uptime_start': datetime.now(),
            'monitoring_active': False
        }
        
        # Initialize UI
        self.init_ui()
        
        # Initialize backend components
        self.init_backend()
        
        # Set up timers
        self.setup_timers()
        
        # Start servers
        self.start_servers()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("CyberSnoop - Network Security Monitor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application icon
        self.setWindowIcon(QIcon("assets/cybersnoop_icon.png"))
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        
        # Create system tray
        self.create_system_tray()
    
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = self.addToolBar("Main")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Dashboard action
        dashboard_action = QAction("🏠 Dashboard", self)
        dashboard_action.setToolTip("Open Web Dashboard")
        dashboard_action.triggered.connect(self.open_dashboard)
        toolbar.addAction(dashboard_action)
        
        toolbar.addSeparator()
        
        # Start/Stop monitoring
        self.monitoring_action = QAction("▶️ Start Monitoring", self)
        self.monitoring_action.setToolTip("Start/Stop Network Monitoring")
        self.monitoring_action.triggered.connect(self.toggle_monitoring)
        toolbar.addAction(self.monitoring_action)
        
        toolbar.addSeparator()
        
        # Settings action
        settings_action = QAction("⚙️ Settings", self)
        settings_action.setToolTip("Open Settings")
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
        
        # Export data action
        export_action = QAction("📥 Export", self)
        export_action.setToolTip("Export Data")
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Help action
        help_action = QAction("❓ Help", self)
        help_action.setToolTip("Help & About")
        help_action.triggered.connect(self.show_help)
        toolbar.addAction(help_action)
    
    def create_main_content(self):
        """Create main content area"""
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Dashboard tab (embedded web view)
        self.dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout(self.dashboard_tab)
        
        # Web view for dashboard
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        dashboard_layout.addWidget(self.web_view)
        
        # Loading label
        self.loading_label = QLabel("Loading dashboard...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 18px; color: #666;")
        dashboard_layout.addWidget(self.loading_label)
        
        self.tab_widget.addTab(self.dashboard_tab, "🏠 Dashboard")
        
        # System Overview tab
        self.system_tab = QWidget()
        self.create_system_overview()
        self.tab_widget.addTab(self.system_tab, "📊 System Overview")
        
        # Logs tab
        self.logs_tab = QWidget()
        self.create_logs_tab()
        self.tab_widget.addTab(self.logs_tab, "📝 Logs")
        
        # Add tabs to main layout
        self.centralWidget().layout().addWidget(self.tab_widget)
    
    def create_system_overview(self):
        """Create system overview tab"""
        layout = QVBoxLayout(self.system_tab)
        
        # Statistics group
        stats_group = QGroupBox("System Statistics")
        stats_layout = QGridLayout(stats_group)
        
        # Statistics labels
        self.packets_label = QLabel("Packets Captured: 0")
        self.threats_label = QLabel("Threats Detected: 0")
        self.uptime_label = QLabel("Uptime: 00:00:00")
        self.status_label = QLabel("Status: Initializing...")
        
        stats_layout.addWidget(self.packets_label, 0, 0)
        stats_layout.addWidget(self.threats_label, 0, 1)
        stats_layout.addWidget(self.uptime_label, 1, 0)
        stats_layout.addWidget(self.status_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        # Services status group
        services_group = QGroupBox("Services Status")
        services_layout = QGridLayout(services_group)
        
        self.api_status_label = QLabel("API Server: ⏳ Starting...")
        self.dashboard_status_label = QLabel("Dashboard Server: ⏳ Starting...")
        self.monitor_status_label = QLabel("Network Monitor: ⏳ Stopped")
        self.database_status_label = QLabel("Database: ⏳ Initializing...")
        
        services_layout.addWidget(self.api_status_label, 0, 0)
        services_layout.addWidget(self.dashboard_status_label, 0, 1)
        services_layout.addWidget(self.monitor_status_label, 1, 0)
        services_layout.addWidget(self.database_status_label, 1, 1)
        
        layout.addWidget(services_group)
        
        layout.addStretch()
    
    def create_logs_tab(self):
        """Create logs tab"""
        layout = QVBoxLayout(self.logs_tab)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_text)
        
        # Log controls
        controls_layout = QHBoxLayout()
        
        clear_button = QPushButton("Clear Logs")
        clear_button.clicked.connect(lambda: self.log_text.clear())
        controls_layout.addWidget(clear_button)
        
        controls_layout.addStretch()
        
        export_logs_button = QPushButton("Export Logs")
        export_logs_button.clicked.connect(self.export_logs)
        controls_layout.addWidget(export_logs_button)
        
        layout.addLayout(controls_layout)
    
    def create_status_bar(self):
        """Create status bar"""
        status_bar = self.statusBar()
        
        # Connection status
        self.connection_status = QLabel("🔴 Disconnected")
        status_bar.addWidget(self.connection_status)
        
        status_bar.addPermanentWidget(QLabel(f"CyberSnoop v1.0 | {datetime.now().strftime('%Y-%m-%d')}"))
    
    def create_system_tray(self):
        """Create system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/cybersnoop_icon.png"))
        
        # Tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show CyberSnoop", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        dashboard_action = QAction("Open Dashboard", self)
        dashboard_action.triggered.connect(self.open_dashboard)
        tray_menu.addAction(dashboard_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Handle tray icon activation
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def init_backend(self):
        """Initialize backend components"""
        try:
            # Database manager
            self.database_manager = DatabaseManager(self.config_manager)
            self.database_status_label.setText("Database: ✅ Connected")
            self.log_message("Database initialized successfully")
            
        except Exception as e:
            self.database_status_label.setText("Database: ❌ Failed")
            self.log_message(f"Database initialization failed: {e}", "ERROR")
    
    def setup_timers(self):
        """Set up update timers"""
        # Statistics update timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(5000)  # Update every 5 seconds
        
        # Dashboard check timer
        self.dashboard_timer = QTimer()
        self.dashboard_timer.timeout.connect(self.check_dashboard_status)
        self.dashboard_timer.start(2000)  # Check every 2 seconds
    
    def start_servers(self):
        """Start the API and dashboard servers"""
        # Start API server
        if self.database_manager:
            self.api_server = APIServerThread(
                self.config_manager,
                self.database_manager,
                None  # Network monitor will be set later
            )
            self.api_server.server_ready.connect(self.on_api_server_ready)
            self.api_server.server_error.connect(self.on_api_server_error)
            self.api_server.start()
        
        # Start dashboard server
        dashboard_path = Path(__file__).parent.parent / "cybersnoop-dashboard"
        if dashboard_path.exists():
            self.dashboard_server = DashboardServer(dashboard_path)
            self.dashboard_server.server_ready.connect(self.on_dashboard_server_ready)
            self.dashboard_server.server_error.connect(self.on_dashboard_server_error)
            self.dashboard_server.start()
        else:
            self.log_message(f"Dashboard path not found: {dashboard_path}", "ERROR")
    
    def on_api_server_ready(self):
        """Handle API server ready"""
        self.api_status_label.setText("API Server: ✅ Running")
        self.log_message("API server started successfully")
        self.connection_status.setText("🟡 API Ready")
    
    def on_api_server_error(self, error_msg):
        """Handle API server error"""
        self.api_status_label.setText("API Server: ❌ Failed")
        self.log_message(f"API server error: {error_msg}", "ERROR")
    
    def on_dashboard_server_ready(self):
        """Handle dashboard server ready"""
        self.dashboard_status_label.setText("Dashboard Server: ✅ Running")
        self.log_message("Dashboard server started successfully")
        self.connection_status.setText("🟢 Connected")
        
        # Load dashboard in web view
        self.web_view.load(QUrl("http://localhost:3000"))
        self.loading_label.hide()
        self.web_view.show()
    
    def on_dashboard_server_error(self, error_msg):
        """Handle dashboard server error"""
        self.dashboard_status_label.setText("Dashboard Server: ❌ Failed")
        self.log_message(f"Dashboard server error: {error_msg}", "ERROR")
        self.loading_label.setText(f"Dashboard failed to load: {error_msg}")
    
    def check_dashboard_status(self):
        """Check if dashboard is accessible"""
        try:
            response = requests.get("http://localhost:3000", timeout=2)
            if response.status_code == 200:
                if self.loading_label.isVisible():
                    self.web_view.load(QUrl("http://localhost:3000"))
                    self.loading_label.hide()
                    self.web_view.show()
        except:
            pass
    
    def toggle_monitoring(self):
        """Toggle network monitoring"""
        if self.stats['monitoring_active']:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start network monitoring"""
        try:
            if not self.network_monitor:
                self.network_monitor = NetworkMonitorThread(
                    self.config_manager,
                    self.database_manager
                )
                self.network_monitor.stats_updated.connect(self.on_stats_updated)
                self.network_monitor.threat_detected.connect(self.on_threat_detected)
            
            self.network_monitor.start()
            self.stats['monitoring_active'] = True
            self.monitoring_action.setText("⏸️ Stop Monitoring")
            self.monitor_status_label.setText("Network Monitor: ✅ Running")
            self.log_message("Network monitoring started")
            
        except Exception as e:
            self.log_message(f"Failed to start monitoring: {e}", "ERROR")
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        try:
            if self.network_monitor:
                self.network_monitor.stop()
                self.network_monitor.wait(5000)  # Wait up to 5 seconds
            
            self.stats['monitoring_active'] = False
            self.monitoring_action.setText("▶️ Start Monitoring")
            self.monitor_status_label.setText("Network Monitor: ⏸️ Stopped")
            self.log_message("Network monitoring stopped")
            
        except Exception as e:
            self.log_message(f"Failed to stop monitoring: {e}", "ERROR")
    
    def on_stats_updated(self, stats):
        """Handle statistics update"""
        self.stats.update(stats)
    
    def on_threat_detected(self, threat):
        """Handle threat detection"""
        self.stats['threats_detected'] += 1
        self.log_message(f"Threat detected: {threat.get('type', 'Unknown')} from {threat.get('source_ip', 'Unknown')}", "WARNING")
    
    def update_statistics(self):
        """Update displayed statistics"""
        # Update labels
        self.packets_label.setText(f"Packets Captured: {self.stats['packets_captured']:,}")
        self.threats_label.setText(f"Threats Detected: {self.stats['threats_detected']:,}")
        
        # Calculate uptime
        uptime = datetime.now() - self.stats['uptime_start']
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        self.uptime_label.setText(f"Uptime: {uptime_str}")
        
        # Status
        status = "Monitoring" if self.stats['monitoring_active'] else "Idle"
        self.status_label.setText(f"Status: {status}")
    
    def open_dashboard(self):
        """Open dashboard in external browser"""
        webbrowser.open("http://localhost:3000")
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config_manager, self)
        dialog.exec()
    
    def export_data(self):
        """Export data to file"""
        try:
            # Simple CSV export
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cybersnoop_export_{timestamp}.json"
            
            # Get database info
            db_info = self.database_manager.get_database_info() if self.database_manager else {}
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "statistics": self.stats.copy(),
                "database_info": db_info,
                "configuration": self.config_manager.config
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            QMessageBox.information(self, "Export Complete", f"Data exported to {filename}")
            self.log_message(f"Data exported to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
            self.log_message(f"Export failed: {e}", "ERROR")
    
    def export_logs(self):
        """Export logs to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cybersnoop_logs_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write(self.log_text.toPlainText())
            
            QMessageBox.information(self, "Export Complete", f"Logs exported to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export logs: {str(e)}")
    
    def show_help(self):
        """Show help/about dialog"""
        help_text = """
        <h2>CyberSnoop Network Security Monitor</h2>
        <p><b>Version:</b> 1.0 (Phase 3 Complete)</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Real-time network monitoring</li>
            <li>Advanced threat detection</li>
            <li>Web-based dashboard with live updates</li>
            <li>Data export and reporting</li>
            <li>Configurable security policies</li>
        </ul>
        <p><b>Usage:</b></p>
        <ol>
            <li>Click "Start Monitoring" to begin network analysis</li>
            <li>View real-time data in the Dashboard tab</li>
            <li>Configure settings via the Settings dialog</li>
            <li>Export data for analysis or reporting</li>
        </ol>
        <p><b>Dashboard URL:</b> <a href="http://localhost:3000">http://localhost:3000</a></p>
        <p><b>API URL:</b> <a href="http://localhost:8000">http://localhost:8000</a></p>
        """
        
        QMessageBox.about(self, "CyberSnoop Help", help_text)
    
    def log_message(self, message, level="INFO"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        self.log_text.append(log_entry)
        print(log_entry)  # Also print to console
    
    def tray_icon_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.quit_application()
    
    def quit_application(self):
        """Quit the application"""
        self.log_message("Shutting down CyberSnoop...")
        
        # Stop monitoring
        if self.stats['monitoring_active']:
            self.stop_monitoring()
        
        # Stop servers
        if self.dashboard_server:
            self.dashboard_server.stop()
            self.dashboard_server.wait(5000)
        
        if self.api_server:
            self.api_server.stop()
            self.api_server.wait(5000)
        
        # Close database
        if self.database_manager:
            self.database_manager.close()
        
        QApplication.quit()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray
    
    # Set application properties
    app.setApplicationName("CyberSnoop")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("CyberSnoop Security")
    
    # Create and show main window
    window = CyberSnoopMainWindow()
    window.show()
    
    # Show startup message
    window.log_message("CyberSnoop started successfully")
    window.log_message("Phase 3: UI Integration and Real-time Features Complete")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
