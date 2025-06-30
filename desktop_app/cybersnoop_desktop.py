#!/usr/bin/env python3
"""
CyberSnoop Desktop Application
Professional Network Security Monitor

Main application entry point with embedded React dashboard.
"""

import sys
import os
import logging
import asyncio
import threading
import time
from pathlib import Path
from typing import Optional

# Qt imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLabel, QSystemTrayIcon, QMenu, QMessageBox,
    QSplashScreen, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, QThread, pyqtSignal, QUrl, Signal
from PySide6.QtGui import QIcon, QPixmap, QAction, QFont
from PySide6.QtWebEngineWidgets import QWebEngineView

# Application imports
from backend.api_server import CyberSnoopAPI
from backend.network_monitor import NetworkMonitor
from backend.enhanced_database_manager import EnhancedDatabaseManager as DatabaseManager
from backend.logging_system import initialize_logging, get_logger
from config.config_manager import ConfigManager
from config.settings_dialog import SettingsDialog

# Constants
APP_NAME = "CyberSnoop"
APP_VERSION = "1.0.0"
APP_AUTHOR = "CyberSnoop Security"
DASHBOARD_PORT = 8888
DASHBOARD_URL = f"http://localhost:{DASHBOARD_PORT}"

class SplashScreen(QSplashScreen):
    """Professional splash screen with loading progress"""
    
    def __init__(self):
        # Create a simple splash screen pixmap
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.darkBlue)
        super().__init__(pixmap)
        
        # Add progress bar
        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 250, 300, 20)
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        # Add title
        self.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        
    def update_progress(self, value: int, message: str):
        """Update progress bar and message"""
        self.progress.setValue(value)
        self.showMessage(f"{message}...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        QApplication.processEvents()

class APIServerThread(QThread):
    """Thread to run the FastAPI server"""
    
    server_started = Signal(bool)
    
    def __init__(self, config_manager, database_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.database_manager = database_manager
        self.api_server = None
        
    def run(self):
        """Run the API server in a separate thread"""
        try:
            # Create network monitor for API integration
            network_monitor = NetworkMonitor(self.config_manager)
            
            # Initialize API server with all components
            self.api_server = CyberSnoopAPI(
                self.config_manager, 
                self.database_manager, 
                network_monitor
            )
            self.api_server.start_server(port=DASHBOARD_PORT)
            self.server_started.emit(True)
        except Exception as e:
            logger = get_logger("main")
            logger.error(f"Failed to start API server: {e}")
            self.server_started.emit(False)

class NetworkMonitorThread(QThread):
    """Thread to run network monitoring"""
    
    threat_detected = Signal(dict)
    statistics_updated = Signal(dict)
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.network_monitor = None
        self.running = False
        
    def run(self):
        """Run network monitoring in a separate thread"""
        try:
            self.network_monitor = NetworkMonitor(self.config_manager)
            self.network_monitor.threat_callback = self.on_threat_detected
            self.network_monitor.stats_callback = self.on_statistics_updated
            
            self.running = True
            self.network_monitor.start_monitoring()
            
        except Exception as e:
            logging.error(f"Network monitoring error: {e}")
            
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.running = False
        if self.network_monitor:
            self.network_monitor.stop_monitoring()
            
    def on_threat_detected(self, threat_data):
        """Handle threat detection"""
        self.threat_detected.emit(threat_data)
        
    def on_statistics_updated(self, stats_data):
        """Handle statistics update"""
        self.statistics_updated.emit(stats_data)

class CyberSnoopMainWindow(QMainWindow):
    """Main application window with embedded dashboard"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.database_manager = None
        self.api_thread = None
        self.monitor_thread = None
        self.tray_icon = None
        self.logger = get_logger("main")
        
        # Initialize database
        self.database_manager = DatabaseManager(config_manager)
        
        self.init_ui()
        self.setup_system_tray()
        self.setup_threads()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"{APP_NAME} - Network Security Monitor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set application icon (placeholder for now)
        # self.setWindowIcon(QIcon("assets/cybersnoop.ico"))
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        toolbar_layout = QHBoxLayout()
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: blue; font-weight: bold; padding: 5px;")
        toolbar_layout.addWidget(self.status_label)
        
        toolbar_layout.addStretch()
        
        # Settings button (placeholder)
        # settings_btn = QPushButton("Settings")
        # settings_btn.clicked.connect(self.show_settings)
        # toolbar_layout.addWidget(settings_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Create web view for dashboard
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl("about:blank"))  # Start with blank page
        layout.addWidget(self.web_view)
        
        # Status bar
        self.statusBar().showMessage("Ready to start monitoring...")
        
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(self, APP_NAME, "System tray is not available on this system.")
            return
            
        # Create tray icon (using default icon for now)
        self.tray_icon = QSystemTrayIcon(self)
        # self.tray_icon.setIcon(QIcon("assets/cybersnoop_tray.ico"))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show Dashboard", self)
        show_action.triggered.connect(self.show_dashboard)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        start_action = QAction("Start Monitoring", self)
        start_action.triggered.connect(self.start_monitoring)
        tray_menu.addAction(start_action)
        
        stop_action = QAction("Stop Monitoring", self)
        stop_action.triggered.connect(self.stop_monitoring)
        tray_menu.addAction(stop_action)
        
        tray_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        
    def setup_threads(self):
        """Setup background threads for API server and monitoring"""
        # API Server Thread with database integration
        self.api_thread = APIServerThread(self.config_manager, self.database_manager)
        self.api_thread.server_started.connect(self.on_api_server_started)
        
        # Network Monitor Thread with database integration
        self.monitor_thread = NetworkMonitorThread(self.config_manager, self.database_manager)
        self.monitor_thread.threat_detected.connect(self.on_threat_detected)
        self.monitor_thread.statistics_updated.connect(self.on_statistics_updated)
        
    def start_api_server(self):
        """Start the API server"""
        self.status_label.setText("Starting API server...")
        self.api_thread.start()
        
    def on_api_server_started(self, success):
        """Handle API server startup result"""
        if success:
            self.status_label.setText("API server running")
            # Load the dashboard
            self.web_view.setUrl(QUrl(DASHBOARD_URL))
            self.statusBar().showMessage("Dashboard loaded successfully")
        else:
            self.status_label.setText("API server failed to start")
            self.statusBar().showMessage("Failed to start API server")
            
    def start_monitoring(self):
        """Start network monitoring"""
        if not self.monitor_thread.running:
            self.status_label.setText("Starting network monitoring...")
            self.monitor_thread.start()
            self.statusBar().showMessage("Network monitoring started")
            
    def stop_monitoring(self):
        """Stop network monitoring"""
        if self.monitor_thread.running:
            self.status_label.setText("Stopping network monitoring...")
            self.monitor_thread.stop_monitoring()
            self.statusBar().showMessage("Network monitoring stopped")
            
    def on_threat_detected(self, threat_data):
        """Handle threat detection notification"""
        threat_type = threat_data.get('type', 'Unknown')
        source_ip = threat_data.get('source_ip', 'Unknown')
        
        # Show system tray notification
        if self.tray_icon:
            self.tray_icon.showMessage(
                "Security Threat Detected!",
                f"{threat_type} from {source_ip}",
                QSystemTrayIcon.Warning,
                5000
            )
            
    def on_statistics_updated(self, stats_data):
        """Handle statistics update"""
        packet_count = stats_data.get('packet_count', 0)
        threat_count = stats_data.get('threat_count', 0)
        
        self.statusBar().showMessage(
            f"Packets: {packet_count:,} | Threats: {threat_count} | Monitoring..."
        )
        
    def show_dashboard(self):
        """Show the main dashboard window"""
        self.show()
        self.raise_()
        self.activateWindow()
        
    def show_settings(self):
        """Show settings dialog"""
        settings_dialog = SettingsDialog(self.config_manager, self)
        settings_dialog.exec()
        
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_dashboard()
            
    def closeEvent(self, event):
        """Handle window close event"""
        if self.tray_icon.isVisible():
            # Minimize to tray instead of closing
            self.hide()
            event.ignore()
            
            # Show notification about minimizing to tray
            self.tray_icon.showMessage(
                APP_NAME,
                "Application minimized to system tray",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            event.accept()
            
    def quit_application(self):
        """Quit the application completely"""
        # Stop monitoring
        if self.monitor_thread and self.monitor_thread.running:
            self.monitor_thread.stop_monitoring()
            self.monitor_thread.wait(3000)  # Wait up to 3 seconds
            
        # Stop API server
        if self.api_thread and self.api_thread.isRunning():
            self.api_thread.quit()
            self.api_thread.wait(3000)  # Wait up to 3 seconds
            
        QApplication.quit()

class CyberSnoopApplication:
    """Main application class"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.config_manager = None
        self.splash = None
        
    def check_privileges(self):
        """Check if running with administrator privileges"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def request_admin_privileges(self):
        """Request administrator privileges"""
        if not self.check_privileges():
            reply = QMessageBox.question(
                None,
                "Administrator Privileges Required",
                "CyberSnoop requires administrator privileges for network packet capture.\n\n"
                "Would you like to restart the application as administrator?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                try:
                    import ctypes
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", sys.executable, " ".join(sys.argv), None, 1
                    )
                except Exception as e:
                    QMessageBox.critical(
                        None,
                        "Error",
                        f"Failed to restart as administrator: {e}"
                    )
                return False
            else:
                return False
        return True
        
    def initialize_logging(self):
        """Initialize application logging"""
        # Use the new centralized logging system
        try:
            initialize_logging(self.config_manager)
            logger = get_logger("main")
            logger.info("CyberSnoop enhanced logging system initialized")
        except Exception as e:
            # Fallback to basic logging
            log_dir = Path.home() / "AppData" / "Local" / APP_NAME / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / "cybersnoop.log"
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            logging.error(f"Failed to initialize enhanced logging, using fallback: {e}")
        
        logging.info(f"Starting {APP_NAME} v{APP_VERSION}")
        
    def run(self):
        """Run the application"""
        # Initialize Qt Application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)
        self.app.setOrganizationName(APP_AUTHOR)
        
        # Initialize logging
        self.initialize_logging()
        
        # Show splash screen
        self.splash = SplashScreen()
        self.splash.show()
        self.splash.update_progress(10, "Checking privileges")
        
        # Check administrator privileges
        if not self.request_admin_privileges():
            sys.exit(1)
            
        self.splash.update_progress(30, "Loading configuration")
        
        # Initialize configuration manager
        try:
            self.config_manager = ConfigManager()
        except Exception as e:
            logging.error(f"Failed to initialize configuration: {e}")
            QMessageBox.critical(None, "Configuration Error", f"Failed to load configuration: {e}")
            sys.exit(1)
            
        self.splash.update_progress(50, "Initializing main window")
        
        # Create main window
        self.main_window = CyberSnoopMainWindow(self.config_manager)
        
        self.splash.update_progress(70, "Starting API server")
        
        # Start API server
        self.main_window.start_api_server()
        
        self.splash.update_progress(90, "Finalizing startup")
        
        # Small delay for splash screen visibility
        time.sleep(1)
        
        self.splash.update_progress(100, "Ready")
        
        # Close splash screen and show main window
        self.splash.finish(self.main_window)
        self.main_window.show()
        
        logging.info("Application startup complete")
        
        # Run the application
        return self.app.exec()

def main():
    """Main entry point"""
    try:
        app = CyberSnoopApplication()
        return app.run()
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
        return 0
    except Exception as e:
        logging.error(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
