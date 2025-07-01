# 🖥️ CyberSnoop Desktop Application - Installation & Usage Guide

[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Framework: PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython/)

> **🎯 Complete guide for installing, configuring, and using the CyberSnoop desktop application**

---

## 📋 **System Requirements**

### **Hardware Requirements**

#### **Minimum Configuration** ⚡
- **CPU**: Intel Core i3-8100 / AMD Ryzen 3 2200G or equivalent
- **RAM**: 8 GB DDR4 (CyberSnoop uses 200-800 MB)
- **Storage**: 2 GB free disk space (SSD recommended)
- **Network**: Ethernet/Wi-Fi adapter with administrator privileges
- **Display**: 1366x768 resolution (1920x1080 recommended)

#### **Recommended Configuration** 🚀
- **CPU**: Intel Core i5-10400 / AMD Ryzen 5 3600 or better
- **RAM**: 16 GB DDR4 or higher
- **Storage**: 5 GB free SSD space
- **Network**: Gigabit Ethernet adapter
- **Display**: 1920x1080 or higher (dual monitor setup ideal)

#### **High-Performance Configuration** 💪
- **CPU**: Intel Core i7-11700K / AMD Ryzen 7 5800X or better
- **RAM**: 32 GB DDR4 or higher
- **Storage**: 10 GB free NVMe SSD space
- **Network**: Multiple network adapters (for advanced monitoring)
- **Display**: 2560x1440 or 4K display

### **Operating System Requirements**
- ✅ **Windows 10** (64-bit) - Version 1903 or later
- ✅ **Windows 11** (64-bit) - All versions fully supported
- ✅ **Windows Server 2019/2022** - Supported for business environments

### **Software Dependencies**
- **Python**: 3.11 or higher (3.12 recommended)
- **Node.js**: 18.x or higher (optional, for web dashboard)
- **NPM**: 8.x or higher (optional, for web dashboard)
- **Git**: Latest version (for updates and source installation)

### **Network Requirements**
- **Administrator Privileges**: Required for packet capture
- **Windows Firewall**: CyberSnoop may request network access
- **Antivirus Exclusions**: Recommended to prevent interference
- **Network Adapters**: Any Windows-compatible Ethernet/Wi-Fi adapter

---

## ⚡ **Quick Installation (Recommended)**

### **Method 1: One-Command Installation**
```powershell
# Open PowerShell as Administrator
# Clone and install CyberSnoop
git clone https://github.com/srivathsavsree/CyberSnoop.git
cd CyberSnoop
python setup.py install
```

### **Method 2: Manual Step-by-Step**
```powershell
# 1. Clone repository
git clone https://github.com/srivathsavsree/CyberSnoop.git
cd CyberSnoop

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Test installation
python setup.py --version

# 4. Launch desktop app
python desktop_app/enhanced_cybersnoop_desktop.py
```

### **Method 3: Python Environment Setup**
```powershell
# 1. Create virtual environment (optional but recommended)
python -m venv cybersnoop_env
cybersnoop_env\\Scripts\\activate

# 2. Install CyberSnoop
git clone https://github.com/srivathsavsree/CyberSnoop.git
cd CyberSnoop
pip install -r requirements.txt

# 3. Launch
python desktop_app/enhanced_cybersnoop_desktop.py
```

---

## 🔧 **Detailed Installation Process**

### **Step 1: Prerequisites**
1. **Install Python 3.11+**
   - Download from [python.org](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation
   - ✅ Check "Install pip" option

2. **Install Git (if not present)**
   - Download from [git-scm.com](https://git-scm.com/downloads)
   - Use default installation options

3. **Verify Installation**
   ```powershell
   python --version    # Should show 3.11.x or higher
   pip --version       # Should show pip version
   git --version       # Should show git version
   ```

### **Step 2: Download CyberSnoop**
```powershell
# Create project directory
mkdir C:\\Tools\\CyberSnoop
cd C:\\Tools\\CyberSnoop

# Clone repository
git clone https://github.com/srivathsavsree/CyberSnoop.git .
```

### **Step 3: Install Dependencies**
```powershell
# Install all required Python packages (40+ security libraries)
pip install -r requirements.txt

# This installs:
# - PySide6 (GUI framework)
# - FastAPI (API server)
# - Scapy (packet analysis)
# - SQLAlchemy (database)
# - And 40+ other security libraries
```

### **Step 4: Verify Installation**
```powershell
# Test CyberSnoop installation
python setup.py --version

# Expected output:
# CyberSnoop v1.0 - Network Security Monitor
# Installation: Complete
# Features: All Enabled
# Status: Ready
```

### **Step 5: Create Desktop Shortcut (Optional)**
```powershell
# Run the desktop shortcut creator
python create_desktop_icon.py

# This creates:
# - Desktop shortcut to CyberSnoop
# - Start Menu entry
# - Windows integration
```

---

## 🚀 **Launching CyberSnoop**

### **Method 1: Command Line**
```powershell
cd C:\\Tools\\CyberSnoop
python desktop_app/enhanced_cybersnoop_desktop.py
```

### **Method 2: Desktop Shortcut**
- Double-click the **CyberSnoop** icon on your desktop
- Or find it in Start Menu under "CyberSnoop"

### **Method 3: System Path (Advanced)**
```powershell
# Add to system PATH for global access
python setup.py --add-to-path
cybersnoop  # Now works from any directory
```

---

## 🖥️ **Desktop Application Interface**

### **Main Window Features**
```
┌─────────────────────────────────────────────────────────────┐
│  🛡️ CyberSnoop - Network Security Monitor                    │
├─────────────────────────────────────────────────────────────┤
│  📊 Dashboard  |  🚨 Alerts  |  🔍 Analysis  |  ⚙️ Settings  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🌐 Network Interfaces:          📈 Live Statistics:        │
│  • Ethernet (192.168.1.100)      • Packets/sec: 1,247      │
│  • Wi-Fi (192.168.1.101)         • Threats: 3              │
│                                   • Bandwidth: 45.2 Mbps   │
│  🔴 Start Monitoring              • Uptime: 02:34:15        │
│                                                             │
│  📋 Recent Activity:                                        │
│  • 14:23:15 - Port scan detected from 192.168.1.200       │
│  • 14:22:48 - High bandwidth usage on port 443            │
│  • 14:21:33 - New device connected: iPhone                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Key Interface Elements**

#### **🌐 Network Interface Selection**
- **Auto-Detection**: CyberSnoop automatically finds all network adapters
- **Interface Details**: IP address, MAC address, connection status
- **Multi-Interface**: Monitor multiple adapters simultaneously
- **Status Indicators**: Green (active), Yellow (monitoring), Red (error)

#### **📊 Real-Time Dashboard**
- **Live Metrics**: Packets per second, bandwidth usage, threat count
- **Interactive Charts**: Network traffic, threat timeline, device activity
- **Customizable Widgets**: Drag and drop dashboard components
- **Export Data**: Save metrics as CSV/JSON for analysis

#### **🚨 Alert System**
- **Real-Time Notifications**: Instant threat detection alerts
- **Severity Levels**: Critical, High, Medium, Low, Info
- **Alert Details**: Timestamp, source, destination, threat type
- **Action Buttons**: Block IP, investigate, mark as false positive

#### **🔍 Analysis Tools**
- **Packet Inspector**: Deep packet analysis with protocol decoding  
- **Traffic Analyzer**: Bandwidth usage by application and device
- **Threat Investigation**: Detailed forensics for security incidents
- **Historical Data**: Search and analyze past network activity

### **System Tray Integration**
- **Background Operation**: Runs silently with minimal resource usage
- **Quick Access**: Right-click tray icon for instant controls
- **Status Indicators**: Color-coded icon shows monitoring status
- **Notifications**: Windows toast notifications for important alerts

---

## ⚙️ **Configuration & Settings**

### **First-Time Setup Wizard**

#### **Step 1: Network Configuration**
1. **Select Network Interfaces**
   - Choose which adapters to monitor
   - Configure IP range filters
   - Set bandwidth thresholds

2. **Security Settings**
   - Enable/disable specific threat detection algorithms
   - Configure alert sensitivity levels
   - Set up notification preferences

3. **Performance Tuning**
   - Optimize for your hardware (8GB RAM, i3 CPU settings included)
   - Configure packet buffer sizes
   - Set monitoring intervals

#### **Step 2: Dashboard Preferences**
1. **Layout Configuration**
   - Choose dashboard widgets
   - Set refresh intervals
   - Configure chart types

2. **Data Retention**
   - Set how long to keep historical data
   - Configure automatic cleanup
   - Database optimization settings

### **Advanced Configuration File**
```python
# Located at: config/cybersnoop_config.json
{
    \"monitoring\": {
        \"interfaces\": [\"auto\"],           # Auto-detect all interfaces
        \"packet_buffer_size\": 1000,        # Optimized for 8GB RAM
        \"monitoring_interval\": 2.0,        # Check every 2 seconds
        \"max_concurrent_connections\": 100   # Reasonable limit
    },
    \"performance\": {
        \"cpu_cores\": 2,                    # Match your i3 processor
        \"memory_limit_mb\": 800,            # Maximum RAM usage
        \"background_processing\": true,      # Use background threads
        \"log_retention_days\": 7            # Keep 1 week of logs
    },
    \"threats\": {
        \"port_scan_detection\": true,
        \"brute_force_detection\": true,
        \"malware_detection\": true,
        \"anomaly_detection\": true,
        \"ddos_detection\": true,
        \"insider_threat_detection\": true
    },
    \"alerts\": {
        \"desktop_notifications\": true,
        \"sound_alerts\": false,
        \"email_notifications\": false,
        \"syslog_integration\": false
    }
}
```

---

## 🛠️ **Usage Guide**

### **Starting Network Monitoring**

#### **Quick Start (30 seconds)**
1. **Launch CyberSnoop**
   - Double-click desktop icon or run from command line

2. **Grant Administrator Access**
   - Click "Yes" when Windows UAC prompt appears
   - Required for packet capture functionality

3. **Select Network Interface**
   - CyberSnoop auto-detects available adapters
   - Choose your primary internet connection (usually auto-selected)

4. **Start Monitoring**
   - Click the green "Start Monitoring" button
   - Status changes to "Active" with real-time metrics

5. **View Live Dashboard**
   - Monitor real-time network activity
   - Watch for security alerts and threats

#### **Advanced Setup (5 minutes)**
1. **Configure Multiple Interfaces**
   ```
   Settings → Network → Interface Configuration
   ✅ Ethernet Adapter (Primary)
   ✅ Wi-Fi Adapter (Secondary)
   ✅ VPN Adapter (Optional)
   ```

2. **Customize Threat Detection**
   ```
   Settings → Security → Threat Detection
   🚨 Port Scan Detection: Enabled (High Sensitivity)
   🚨 Brute Force Detection: Enabled (Medium Sensitivity)  
   🚨 Malware Detection: Enabled (High Sensitivity)
   🚨 Anomaly Detection: Enabled (Medium Sensitivity)
   🚨 DDoS Detection: Enabled (Low Sensitivity)
   ```

3. **Set Performance Options**
   ```
   Settings → Performance → Hardware Optimization
   💻 Hardware Profile: Intel i3 + 8GB RAM (Detected)
   ⚡ Performance Mode: Balanced
   📊 Monitoring Frequency: Every 2 seconds
   💾 Memory Usage Limit: 800 MB
   ```

### **Understanding the Dashboard**

#### **📊 Main Metrics Panel**
- **Packets/Second**: Real-time network activity (target: 1,000-5,000 for your system)
- **Bandwidth Usage**: Current network utilization (Mbps in/out)
- **Active Connections**: Number of concurrent network connections
- **Threat Level**: Current security status (Green/Yellow/Orange/Red)

#### **🌐 Network Map**
- **Device Discovery**: All devices on your network
- **Traffic Flow**: Visual representation of data movement
- **Connection Status**: Active, idle, suspicious connections
- **Geolocation**: Source/destination countries for external traffic

#### **🚨 Alert Timeline**
- **Real-Time Alerts**: Latest security events and threats
- **Alert Severity**: Color-coded by importance (Red=Critical, Yellow=Warning)
- **Quick Actions**: Block, investigate, or dismiss alerts
- **Historical View**: Browse past alerts and incidents

#### **📈 Analytics Charts**
- **Traffic Over Time**: Bandwidth usage patterns
- **Threat Detection Rate**: Security events per hour/day
- **Protocol Distribution**: HTTP, HTTPS, DNS, P2P breakdown
- **Device Activity**: Most active devices on network

### **Web Dashboard Integration (Optional)**

#### **Launching the Web Dashboard**
```powershell
# Navigate to dashboard directory
cd cybersnoop-dashboard

# Install web dependencies (one-time setup)
npm install --legacy-peer-deps

# Start web server
npm run dev

# Access dashboard at: http://localhost:3000
```

#### **Web Dashboard Features**
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **🎨 Modern UI**: Beautiful charts, tables, and visualizations
- **⚡ Real-Time Updates**: Live data streaming from desktop app
- **📊 Advanced Analytics**: Detailed reports and trend analysis
- **🔍 Search & Filter**: Find specific events and data points
- **📤 Export Data**: Download reports in PDF, CSV, JSON formats

---

## 🔧 **Troubleshooting Guide**

### **Common Issues & Solutions**

#### **❌ "Access Denied" Error**
```
Problem: CyberSnoop cannot start packet capture
Solution: Run as Administrator
- Right-click CyberSnoop shortcut
- Select "Run as administrator"
- Click "Yes" on UAC prompt
```

#### **❌ "No Network Interfaces Found"**
```
Problem: Network adapters not detected
Solutions:
1. Check Windows network settings
2. Ensure adapters are enabled
3. Restart network services:
   - Open Command Prompt as admin
   - Run: netsh winsock reset
   - Restart computer
```

#### **❌ "Python Module Not Found"**
```
Problem: Missing Python dependencies
Solution: Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### **❌ High CPU Usage**
```
Problem: CyberSnoop using too much CPU on your i3 system
Solutions:
1. Reduce monitoring frequency:
   Settings → Performance → Monitoring Interval: 3-5 seconds
2. Lower packet buffer size:
   Settings → Performance → Buffer Size: 500-1000
3. Disable unused threat detection:
   Settings → Security → Disable less critical algorithms
```

#### **❌ High Memory Usage**
```
Problem: Memory usage over 800MB on 8GB system
Solutions:
1. Enable memory optimization:
   Settings → Performance → Memory Limit: 600MB
2. Reduce log retention:
   Settings → Data → Retention: 3-5 days
3. Clear historical data:
   Settings → Data → Clear Old Data
```

#### **❌ Dashboard Won't Load**
```
Problem: Web dashboard shows errors
Solutions:
1. Check if API server is running:
   python desktop_app/start_api_server.py
2. Verify dashboard dependencies:
   cd cybersnoop-dashboard
   npm install --legacy-peer-deps
3. Clear browser cache and reload
```

### **Performance Optimization for Your Hardware**

#### **Intel i3-1005G1 + 8GB RAM Configuration**
```python
# Optimal settings for your specific system
RECOMMENDED_SETTINGS = {
    \"packet_buffer_size\": 1000,      # Moderate buffer
    \"monitoring_interval\": 2.0,      # Every 2 seconds
    \"max_concurrent_connections\": 100,  # Reasonable limit
    \"memory_limit_mb\": 600,          # Conservative memory use
    \"cpu_usage_limit\": 50,           # Max 50% CPU usage
    \"background_threads\": 2,         # Match CPU cores
    \"log_retention_days\": 5          # Keep 5 days of logs
}
```

#### **Expected Performance**
```
✅ Monitoring Capacity:
   • Network Speed: Up to 100 Mbps
   • Packets/Second: 1,000-3,000
   • Concurrent Analysis: 50-100 threats
   • Memory Usage: 300-600 MB

✅ CPU Usage:
   • Idle Monitoring: 3-8% CPU
   • Active Analysis: 15-30% CPU
   • Peak Load: 40-60% CPU (short bursts)

✅ Response Times:
   • Alert Generation: <2 seconds
   • Dashboard Updates: <1 second
   • Database Queries: <500ms
```

### **Log Files & Debugging**

#### **Log File Locations**
```
📁 C:\\Tools\\CyberSnoop\\logs\\
├── cybersnoop_main.log          # Main application logs
├── network_monitor.log          # Network monitoring events
├── threat_detection.log         # Security alerts and analysis
├── api_server.log              # API server requests/responses
└── dashboard.log               # Web dashboard activity
```

#### **Enable Debug Mode**
```powershell
# Run with verbose logging
python desktop_app/enhanced_cybersnoop_desktop.py --debug

# Or set environment variable
set CYBERSNOOP_DEBUG=1
python desktop_app/enhanced_cybersnoop_desktop.py
```

---

## 🛡️ **Security Best Practices**

### **Network Security**
- **Firewall Configuration**: Allow CyberSnoop through Windows Firewall
- **Antivirus Exclusions**: Add CyberSnoop directory to antivirus exclusions
- **Network Isolation**: Monitor from a dedicated network segment if possible
- **Access Control**: Limit who can run CyberSnoop with administrator privileges

### **Data Protection**
- **Local Storage**: All data stored locally, never sent to external servers
- **Database Encryption**: Enable SQLite encryption for sensitive data
- **Log Rotation**: Automatic cleanup of old logs to prevent disk filling
- **Backup Strategy**: Regular backups of configuration and historical data

### **Operational Security**
- **Regular Updates**: Check GitHub for new releases and security updates
- **Configuration Backup**: Save your settings before major changes
- **Incident Response**: Have a plan for handling critical security alerts
- **Documentation**: Keep notes on custom configurations and tuning

---

## 🔄 **Updates & Maintenance**

### **Checking for Updates**
```powershell
# Check current version
python setup.py --version

# Update from GitHub
git pull origin main
pip install -r requirements.txt --upgrade

# Verify update
python setup.py --version
```

### **Automatic Updates (Planned)**
- **Background Checks**: CyberSnoop will check for updates weekly
- **Notification System**: Alert when new versions are available
- **One-Click Updates**: Simple update process through GUI
- **Rollback Support**: Easy way to revert to previous version

### **Database Maintenance**
```powershell
# Clean old data (keeps last 30 days)
python tools/cleanup_database.py --days 30

# Optimize database performance
python tools/optimize_database.py

# Backup current data
python tools/backup_database.py --output backup_YYYYMMDD.db
```

### **System Health Checks**
```powershell
# Run comprehensive system check
python tools/system_check.py

# Expected output:
✅ Python Environment: OK
✅ Dependencies: All installed
✅ Network Interfaces: 2 detected
✅ Database: Healthy
✅ Disk Space: 15.2 GB available
✅ Memory: 7.1 GB available
✅ Performance: Optimal
```

---

## 🎯 **Advanced Usage Tips**

### **Power User Features**

#### **Custom Threat Rules**
```python
# Create custom threat detection rules
# File: config/custom_rules.py

def detect_custom_threat(packet_data):
    \"\"\"
    Custom threat detection logic
    Return: (is_threat, severity, description)
    \"\"\"
    # Example: Detect unusual DNS queries
    if packet_data.get('protocol') == 'DNS':
        query = packet_data.get('dns_query', '')
        if len(query) > 100:  # Unusually long DNS query
            return (True, 'Medium', f'Suspicious DNS query: {query[:50]}...')
    
    return (False, None, None)
```

#### **API Integration**
```python
# Integrate with external security tools
import requests

# Send alerts to external SIEM
def send_to_siem(alert_data):
    siem_endpoint = \"http://your-siem-server:8080/alerts\"
    response = requests.post(siem_endpoint, json=alert_data)
    return response.status_code == 200

# Export data to external systems
def export_to_splunk(data):
    splunk_hec = \"https://your-splunk:8088/services/collector\"
    headers = {\"Authorization\": \"Splunk YOUR-HEC-TOKEN\"}
    requests.post(splunk_hec, json=data, headers=headers)
```

#### **Scheduled Reports**
```powershell
# Set up automated daily reports
python tools/generate_report.py --schedule daily --email admin@company.com

# Weekly security summary
python tools/generate_report.py --schedule weekly --format pdf --output weekly_report.pdf
```

### **Integration Examples**

#### **Splunk Integration**
```bash
# Forward CyberSnoop logs to Splunk
# Configure Universal Forwarder to monitor:
C:\\Tools\\CyberSnoop\\logs\\*.log

# Splunk search examples:
index=cybersnoop source=\"*threat_detection.log\" severity=High
index=cybersnoop source=\"*network_monitor.log\" | stats count by src_ip
```

#### **Elasticsearch Integration**
```python
# Send data to Elasticsearch/ELK stack
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

def send_to_elk(threat_data):
    es.index(
        index=\"cybersnoop-threats\",
        body=threat_data
    )
```

---

## 🤝 **Getting Help & Support**

### **Free Community Support**
- **📋 GitHub Issues**: [Report bugs and get help](https://github.com/srivathsavsree/CyberSnoop/issues)
- **💬 Discussions**: [Community Q&A and tips](https://github.com/srivathsavsree/CyberSnoop/discussions)
- **📖 Documentation**: This guide and additional resources in the repo
- **🔍 Search First**: Check existing issues before creating new ones

### **Self-Help Resources**
1. **📚 Documentation**: Read this guide thoroughly
2. **🔍 Error Messages**: Copy exact error text when seeking help
3. **📋 System Info**: Include your OS, Python version, and hardware specs
4. **🔧 Configuration**: Share relevant config files (remove sensitive data)

### **Contributing Back**
- **🐛 Bug Reports**: Help improve stability for everyone
- **✨ Feature Suggestions**: Propose new security monitoring capabilities
- **📝 Documentation**: Improve guides and tutorials
- **🧪 Testing**: Help test new features and releases

---

**🎯 Ready to start monitoring? Launch CyberSnoop and secure your network today!**

*For questions about this guide, create an issue on GitHub with the label \"documentation\".*
