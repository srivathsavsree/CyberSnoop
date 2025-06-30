"""
Enhanced Desktop Application with Integrated React Dashboard
Day 8-10: Complete UI Integration with real-time features
"""

import sys
import os
import threading
import time
import subprocess
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QSystemTrayIcon, QMenu, QToolBar, QStatusBar, QSplitter,
    QTextEdit, QTabWidget, QGroupBox, QGridLayout, QLabel,
    QPushButton, QProgressBar, QFrame, QScrollArea
)
from PySide6.QtCore import QTimer, QThread, Signal, QUrl, QSize
from PySide6.QtGui import QIcon, QAction, QFont, QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

# Import our backend components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.config_manager import ConfigManager
from backend.enhanced_database_manager import EnhancedDatabaseManager as DatabaseManager
from backend.network_monitor import NetworkMonitor
from backend.threat_detector import ThreatDetector
from backend.api_server import CyberSnoopAPI
from backend.advanced_threat_detector import AdvancedThreatDetector

# All features are now included and free - no enterprise restrictions
# Import all advanced features directly
try:
    from enterprise_compatibility import EnterpriseEnhancedCyberSnoop
    ENTERPRISE_FEATURES_AVAILABLE = True
except ImportError:
    ENTERPRISE_FEATURES_AVAILABLE = False
    print("Advanced features module not found - using built-in capabilities")

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
            for _ in range(30):  # Wait up to 30 seconds
                if not self.running:
                    break
                    
                try:
                    import requests
                    response = requests.get('http://localhost:3000', timeout=2)
                    if response.status_code == 200:
                        self.server_ready.emit()
                        break
                except:
                    pass
                
                time.sleep(1)
            else:
                self.server_error.emit("Dashboard server failed to start")
            
            # Wait for process to complete
            if self.process:
                self.process.wait()
                
        except Exception as e:
            self.server_error.emit(f"Dashboard server error: {str(e)}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the dashboard server"""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process.terminate()
            self.process.wait()

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
        
    def run(self):
        """Start the API server"""
        try:
            self.api_server = CyberSnoopAPI(
                self.config_manager,
                self.database_manager,
                self.network_monitor
            )
            
            self.server_ready.emit()
            
            # Start the server (this blocks)
            self.api_server.start_server(host="127.0.0.1", port=8888)
            
        except Exception as e:
            self.server_error.emit(f"API server error: {str(e)}")

class NetworkMonitorThread(QThread):
    """Thread for network monitoring"""
    packet_captured = Signal(dict)
    threat_detected = Signal(dict)
    stats_updated = Signal(dict)
    
    def __init__(self, network_monitor, threat_detector):
        super().__init__()
        self.network_monitor = network_monitor
        self.threat_detector = threat_detector
        self.running = False
        
    def run(self):
        """Run network monitoring"""
        self.running = True
        
        # Start network monitoring
        if hasattr(self.network_monitor, 'start_monitoring'):
            self.network_monitor.start_monitoring()
        
        while self.running:
            try:
                # Get network statistics
                stats = self.network_monitor.get_network_stats()
                if stats:
                    self.stats_updated.emit(stats)
                
                # Small delay
                time.sleep(2)
                
            except Exception as e:
                print(f"Network monitoring error: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop network monitoring"""
        self.running = False
        if hasattr(self.network_monitor, 'stop_monitoring'):
            self.network_monitor.stop_monitoring()

class EnhancedCyberSnoopApp(QMainWindow):
    """Enhanced CyberSnoop Desktop Application with integrated React dashboard"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize configuration and components
        self.config_manager = ConfigManager()
        self.database_manager = DatabaseManager(self.config_manager)
        self.network_monitor = NetworkMonitor(self.config_manager)
        self.threat_detector = ThreatDetector(self.config_manager, self.database_manager)
        self.advanced_threat_detector = AdvancedThreatDetector(self.config_manager)
        
        # Initialize enterprise components if available
        self.enterprise = None
        if ENTERPRISE_FEATURES_AVAILABLE:
            try:
                self.enterprise = EnterpriseEnhancedCyberSnoop(
                    self.config_manager, 
                    self.database_manager
                )
                print("✅ Enterprise features initialized successfully")
            except Exception as e:
                print(f"⚠️ Enterprise features failed to initialize: {e}")
                self.enterprise = None
        
        # Server threads
        self.api_server_thread = None
        self.dashboard_server_thread = None
        self.network_monitor_thread = None
        
        # Dashboard integration
        self.dashboard_url = "http://localhost:3000"
        self.api_url = "http://127.0.0.1:8888"
        
        # UI components
        self.web_view = None
        self.system_tray = None
        self.status_bar = None
        
        # Statistics
        self.stats = {
            'packets_captured': 0,
            'threats_detected': 0,
            'monitoring_status': False,
            'uptime': 0
        }
        
        self.setup_ui()
        self.setup_system_tray()
        self.start_backend_services()
        self.setup_timers()
        
    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("CyberSnoop - Network Security Monitor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application icon
        # self.setWindowIcon(QIcon("assets/cybersnoop-icon.png"))
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter()
        main_layout.addWidget(splitter)
        
        # Left panel for system info and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel for dashboard
        right_panel = self.create_dashboard_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (20% left, 80% right)
        splitter.setSizes([280, 1120])
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.create_status_bar()
        
    def create_left_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        panel.setMaximumWidth(300)
        panel.setMinimumWidth(250)
        
        layout = QVBoxLayout(panel)
        
        # System Status Group
        status_group = QGroupBox("System Status")
        status_layout = QGridLayout(status_group)
        
        self.status_label = QLabel("⏸️ Monitoring Stopped")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        status_layout.addWidget(QLabel("Status:"), 0, 0)
        status_layout.addWidget(self.status_label, 0, 1)
        
        self.uptime_label = QLabel("00:00:00")
        status_layout.addWidget(QLabel("Uptime:"), 1, 0)
        status_layout.addWidget(self.uptime_label, 1, 1)
        
        layout.addWidget(status_group)
        
        # Statistics Group
        stats_group = QGroupBox("Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.packets_label = QLabel("0")
        self.packets_label.setStyleSheet("color: #3b82f6; font-weight: bold; font-size: 14px;")
        stats_layout.addWidget(QLabel("Packets:"), 0, 0)
        stats_layout.addWidget(self.packets_label, 0, 1)
        
        self.threats_label = QLabel("0")
        self.threats_label.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 14px;")
        stats_layout.addWidget(QLabel("Threats:"), 1, 0)
        stats_layout.addWidget(self.threats_label, 1, 1)
        
        self.connections_label = QLabel("0")
        stats_layout.addWidget(QLabel("Connections:"), 2, 0)
        stats_layout.addWidget(self.connections_label, 2, 1)
        
        layout.addWidget(stats_group)
        
        # Controls Group
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        self.start_button = QPushButton("▶️ Start Monitoring")
        self.start_button.clicked.connect(self.toggle_monitoring)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        controls_layout.addWidget(self.start_button)
        
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.clicked.connect(self.open_settings)
        controls_layout.addWidget(self.settings_button)
        
        self.export_button = QPushButton("📊 Export Data")
        self.export_button.clicked.connect(self.export_data)
        controls_layout.addWidget(self.export_button)
        
        layout.addWidget(controls_group)
        
        # Server Status Group
        server_group = QGroupBox("Services")
        server_layout = QGridLayout(server_group)
        
        self.api_status = QLabel("🔴 Stopped")
        server_layout.addWidget(QLabel("API Server:"), 0, 0)
        server_layout.addWidget(self.api_status, 0, 1)
        
        self.dashboard_status = QLabel("🔴 Stopped")
        server_layout.addWidget(QLabel("Dashboard:"), 1, 0)
        server_layout.addWidget(self.dashboard_status, 1, 1)
        
        layout.addWidget(server_group)
        
        # Enterprise Features Group (if available)
        if self.enterprise:
            enterprise_group = QGroupBox("Enterprise Features")
            enterprise_layout = QGridLayout(enterprise_group)
            
            # SIEM Integration Status
            siem_enabled = self.enterprise.enterprise_features.get('siem_integration', False)
            self.siem_status = QLabel("🟢 Enabled" if siem_enabled else "🔴 Disabled")
            enterprise_layout.addWidget(QLabel("SIEM:"), 0, 0)
            enterprise_layout.addWidget(self.siem_status, 0, 1)
            
            # AI Detection Status
            ai_enabled = self.enterprise.enterprise_features.get('ai_detection', False)
            self.ai_status = QLabel("🟢 Enabled" if ai_enabled else "🔴 Disabled")
            enterprise_layout.addWidget(QLabel("AI Detection:"), 1, 0)
            enterprise_layout.addWidget(self.ai_status, 1, 1)
            
            # Compliance Reporting Status
            compliance_enabled = self.enterprise.enterprise_features.get('compliance_reporting', False)
            self.compliance_status = QLabel("🟢 Enabled" if compliance_enabled else "🔴 Disabled")
            enterprise_layout.addWidget(QLabel("Compliance:"), 2, 0)
            enterprise_layout.addWidget(self.compliance_status, 2, 1)
            
            # Enterprise Actions
            self.ml_analysis_button = QPushButton("🤖 Run ML Analysis")
            self.ml_analysis_button.clicked.connect(self.run_ml_analysis)
            enterprise_layout.addWidget(self.ml_analysis_button, 3, 0, 1, 2)
            
            self.compliance_report_button = QPushButton("📋 Generate Reports")
            self.compliance_report_button.clicked.connect(self.generate_compliance_reports)
            enterprise_layout.addWidget(self.compliance_report_button, 4, 0, 1, 2)
            
            layout.addWidget(enterprise_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return panel
        
    def create_dashboard_panel(self):
        """Create the dashboard web view panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Create web view for dashboard
        self.web_view = QWebEngineView()
        
        # Configure web engine settings
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        
        # Initially load a loading page
        self.web_view.setHtml(self.get_loading_html())
        
        layout.addWidget(self.web_view)
        
        return panel
        
    def get_loading_html(self):
        """Get loading HTML while services start"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CyberSnoop Loading</title>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: linear-gradient(135deg, #1e293b, #334155);
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    text-align: center;
                }
                .loading-container {
                    max-width: 400px;
                    padding: 40px;
                }
                .logo {
                    font-size: 3em;
                    margin-bottom: 20px;
                }
                .spinner {
                    border: 4px solid #334155;
                    border-left: 4px solid #3b82f6;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 20px auto;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .status {
                    margin-top: 20px;
                    color: #94a3b8;
                }
            </style>
        </head>
        <body>
            <div class="loading-container">
                <div class="logo">🛡️</div>
                <h1>CyberSnoop</h1>
                <p>Network Security Monitor</p>
                <div class="spinner"></div>
                <div class="status" id="status">Starting services...</div>
            </div>
            
            <script>
                let dots = 0;
                setInterval(() => {
                    dots = (dots + 1) % 4;
                    document.getElementById('status').textContent = 'Starting services' + '.'.repeat(dots);
                }, 500);
            </script>
        </body>
        </html>
        """
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        export_action = QAction('Export Data', self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create the application toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Start/Stop action
        self.monitor_action = QAction('▶️ Start', self)
        self.monitor_action.triggered.connect(self.toggle_monitoring)
        toolbar.addAction(self.monitor_action)
        
        toolbar.addSeparator()
        
        # Settings action
        settings_action = QAction('⚙️ Settings', self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
        
        # Refresh action
        refresh_action = QAction('🔄 Refresh', self)
        refresh_action.triggered.connect(self.refresh_dashboard)
        toolbar.addAction(refresh_action)
        
    def create_status_bar(self):
        """Create the application status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets to status bar
        self.connection_status = QLabel("🔴 Disconnected")
        self.status_bar.addPermanentWidget(self.connection_status)
        
        self.status_bar.showMessage("Ready")
        
    def setup_system_tray(self):
        """Setup system tray integration"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        self.system_tray = QSystemTrayIcon(self)
        # self.system_tray.setIcon(QIcon("assets/cybersnoop-icon.png"))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show CyberSnoop", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        toggle_action = QAction("Start Monitoring", self)
        toggle_action.triggered.connect(self.toggle_monitoring)
        tray_menu.addAction(toggle_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.system_tray.setContextMenu(tray_menu)
        self.system_tray.show()
        
        # Handle tray icon activation
        self.system_tray.activated.connect(self.on_tray_activated)
        
    def start_backend_services(self):
        """Start all backend services"""
        # Start API server
        self.start_api_server()
        
        # Start dashboard server
        self.start_dashboard_server()
        
    def start_api_server(self):
        """Start the API server"""
        if self.api_server_thread and self.api_server_thread.isRunning():
            return
            
        self.api_server_thread = APIServerThread(
            self.config_manager,
            self.database_manager,
            self.network_monitor
        )
        
        self.api_server_thread.server_ready.connect(self.on_api_server_ready)
        self.api_server_thread.server_error.connect(self.on_api_server_error)
        
        self.api_server_thread.start()
        
    def start_dashboard_server(self):
        """Start the dashboard server"""
        dashboard_path = Path(__file__).parent.parent / "cybersnoop-dashboard"
        
        if not dashboard_path.exists():
            print(f"Dashboard path not found: {dashboard_path}")
            return
            
        if self.dashboard_server_thread and self.dashboard_server_thread.isRunning():
            return
            
        self.dashboard_server_thread = DashboardServer(dashboard_path)
        self.dashboard_server_thread.server_ready.connect(self.on_dashboard_server_ready)
        self.dashboard_server_thread.server_error.connect(self.on_dashboard_server_error)
        
        self.dashboard_server_thread.start()
        
    def setup_timers(self):
        """Setup update timers"""
        # Stats update timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(5000)  # Update every 5 seconds
        
        # Uptime timer
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        self.uptime_timer.start(1000)  # Update every second
        
    def on_api_server_ready(self):
        """Handle API server ready signal"""
        self.api_status.setText("🟢 Running")
        self.connection_status.setText("🟢 API Connected")
        self.status_bar.showMessage("API Server started successfully")
        
    def on_api_server_error(self, error):
        """Handle API server error signal"""
        self.api_status.setText("🔴 Error")
        self.status_bar.showMessage(f"API Server error: {error}")
        
    def on_dashboard_server_ready(self):
        """Handle dashboard server ready signal"""
        self.dashboard_status.setText("🟢 Running")
        
        # Wait a moment for server to fully initialize
        QTimer.singleShot(3000, self.load_dashboard)
        
    def on_dashboard_server_error(self, error):
        """Handle dashboard server error signal"""
        self.dashboard_status.setText("🔴 Error")
        self.status_bar.showMessage(f"Dashboard error: {error}")
        
    def load_dashboard(self):
        """Load the React dashboard in the web view"""
        if self.web_view:
            self.web_view.load(QUrl(self.dashboard_url))
            self.status_bar.showMessage("Dashboard loaded successfully")
            
    def refresh_dashboard(self):
        """Refresh the dashboard"""
        if self.web_view:
            self.web_view.reload()
            
    def toggle_monitoring(self):
        """Toggle network monitoring"""
        if self.stats['monitoring_status']:
            self.stop_monitoring()
        else:
            self.start_monitoring()
            
    def start_monitoring(self):
        """Start network monitoring"""
        if not self.network_monitor_thread or not self.network_monitor_thread.isRunning():
            self.network_monitor_thread = NetworkMonitorThread(
                self.network_monitor,
                self.threat_detector
            )
            
            self.network_monitor_thread.stats_updated.connect(self.on_stats_updated)
            self.network_monitor_thread.packet_captured.connect(self.on_packet_captured)
            self.network_monitor_thread.threat_detected.connect(self.on_threat_detected)
            
            self.network_monitor_thread.start()
            
        self.stats['monitoring_status'] = True
        self.update_monitoring_ui()
        
    def stop_monitoring(self):
        """Stop network monitoring"""
        if self.network_monitor_thread and self.network_monitor_thread.isRunning():
            self.network_monitor_thread.stop()
            self.network_monitor_thread.wait()
            
        self.stats['monitoring_status'] = False
        self.update_monitoring_ui()
        
    def update_monitoring_ui(self):
        """Update UI elements based on monitoring status"""
        if self.stats['monitoring_status']:
            self.status_label.setText("▶️ Monitoring Active")
            self.status_label.setStyleSheet("color: #22c55e; font-weight: bold;")
            self.start_button.setText("⏸️ Stop Monitoring")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            self.monitor_action.setText("⏸️ Stop")
        else:
            self.status_label.setText("⏸️ Monitoring Stopped")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
            self.start_button.setText("▶️ Start Monitoring")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #22c55e;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #16a34a;
                }
            """)
            self.monitor_action.setText("▶️ Start")
            
    def on_stats_updated(self, stats):
        """Handle updated network statistics"""
        if 'packets_captured' in stats:
            self.stats['packets_captured'] = stats['packets_captured']
        if 'threats_detected' in stats:
            self.stats['threats_detected'] = stats['threats_detected']
        if 'active_connections' in stats:
            self.stats['active_connections'] = stats['active_connections']
            
        self.update_stats_display()
        
    def on_packet_captured(self, packet_data):
        """Handle packet captured event"""
        self.stats['packets_captured'] += 1
        self.update_stats_display()
        
    def on_threat_detected(self, threat_data):
        """Handle threat detected event"""
        self.stats['threats_detected'] += 1
        self.update_stats_display()
        
        # Process with enterprise features if available
        if self.enterprise:
            try:
                # Run in background to avoid blocking UI
                import asyncio
                asyncio.create_task(self.enterprise.process_enterprise_threat(threat_data))
            except Exception as e:
                print(f"Enterprise threat processing error: {e}")
        
        # Show system tray notification
        if self.system_tray:
            self.system_tray.showMessage(
                "CyberSnoop Alert",
                f"Threat detected: {threat_data.get('type', 'Unknown')}",
                QSystemTrayIcon.MessageIcon.Warning,
                5000
            )
            
    def update_stats_display(self):
        """Update the statistics display"""
        self.packets_label.setText(f"{self.stats['packets_captured']:,}")
        self.threats_label.setText(f"{self.stats['threats_detected']:,}")
        self.connections_label.setText(f"{self.stats.get('active_connections', 0):,}")
        
    def update_stats(self):
        """Update statistics from database"""
        try:
            # Get packet count from database
            packet_count = self.database_manager.get_packet_count()
            threat_count = self.database_manager.get_threat_count()
            
            self.stats['packets_captured'] = packet_count
            self.stats['threats_detected'] = threat_count
            
            self.update_stats_display()
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            
    def update_uptime(self):
        """Update uptime display"""
        if self.stats['monitoring_status']:
            self.stats['uptime'] += 1
            
        hours = self.stats['uptime'] // 3600
        minutes = (self.stats['uptime'] % 3600) // 60
        seconds = self.stats['uptime'] % 60
        
        uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.uptime_label.setText(uptime_str)
        
    def open_settings(self):
        """Open settings dialog"""
        from config.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(self.config_manager, self)
        dialog.exec()
        
    def export_data(self):
        """Export captured data"""
        # Implementation for data export
        self.status_bar.showMessage("Data export feature coming soon...")
        
    def show_about(self):
        """Show about dialog"""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.about(self, "About CyberSnoop", 
            "CyberSnoop v1.0\n\n"
            "Advanced Network Security Monitor\n"
            "Real-time threat detection and analysis\n\n"
            "Developed with ❤️ for network security")
            
    def on_tray_activated(self, reason):
        """Handle system tray activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
                
    def closeEvent(self, event):
        """Handle close event"""
        if self.system_tray and self.system_tray.isVisible():
            self.hide()
            event.ignore()
        else:
            self.quit_application()
            
    def quit_application(self):
        """Quit the application"""
        # Stop all services
        self.stop_monitoring()
        
        if self.api_server_thread and self.api_server_thread.isRunning():
            self.api_server_thread.terminate()
            self.api_server_thread.wait()
            
        if self.dashboard_server_thread and self.dashboard_server_thread.isRunning():
            self.dashboard_server_thread.stop()
            self.dashboard_server_thread.wait()
            
        # Close database connections
        if self.database_manager:
            self.database_manager.close()
            
        QApplication.quit()

    def run_ml_analysis(self):
        """Run machine learning analysis on recent packets"""
        if not self.enterprise:
            self.status_bar.showMessage("Enterprise features not available")
            return
        
        try:
            # Get recent packets from database
            recent_packets = self.database_manager.get_recent_packets(limit=1000)
            
            if recent_packets:
                # Run ML analysis in background
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                anomalies = loop.run_until_complete(
                    self.enterprise.run_ml_analysis(recent_packets)
                )
                
                if anomalies:
                    message = f"ML Analysis complete: {len(anomalies)} anomalies detected"
                    self.status_bar.showMessage(message)
                    
                    # Show notification
                    if self.system_tray:
                        self.system_tray.showMessage(
                            "CyberSnoop ML Analysis",
                            message,
                            QSystemTrayIcon.MessageIcon.Information,
                            3000
                        )
                else:
                    self.status_bar.showMessage("ML Analysis complete: No anomalies detected")
            else:
                self.status_bar.showMessage("No packet data available for analysis")
                
        except Exception as e:
            error_msg = f"ML Analysis error: {str(e)}"
            self.status_bar.showMessage(error_msg)
            print(error_msg)
    
    def generate_compliance_reports(self):
        """Generate compliance reports"""
        if not self.enterprise:
            self.status_bar.showMessage("Enterprise features not available")
            return
        
        try:
            reports = self.enterprise.generate_compliance_reports()
            
            if reports:
                # Save reports to files
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                for report_type, report_data in reports.items():
                    filename = f"compliance_report_{report_type}_{timestamp}.json"
                    filepath = Path(__file__).parent / "reports" / filename
                    
                    # Create reports directory if it doesn't exist
                    filepath.parent.mkdir(exist_ok=True)
                    
                    with open(filepath, 'w') as f:
                        json.dump(report_data, f, indent=2)
                
                message = f"Generated {len(reports)} compliance reports"
                self.status_bar.showMessage(message)
                
                # Show notification
                if self.system_tray:
                    self.system_tray.showMessage(
                        "CyberSnoop Reports",
                        message,
                        QSystemTrayIcon.MessageIcon.Information,
                        3000
                    )
            else:
                self.status_bar.showMessage("No compliance reports generated")
                
        except Exception as e:
            error_msg = f"Report generation error: {str(e)}"
            self.status_bar.showMessage(error_msg)
            print(error_msg)

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep app running when window is closed
    
    # Set application properties
    app.setApplicationName("CyberSnoop")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("CyberSnoop Security")
    
    # Create and show main window
    window = EnhancedCyberSnoopApp()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
