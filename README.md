# CyberSnoop - Professional Network Security Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Development Status](https://img.shields.io/badge/status-Active%20Development-green.svg)](https://github.com/your-username/cybersnoop)

## 🛡️ Overview

CyberSnoop is a professional Windows desktop application for real-time network security monitoring and threat detection. Built with PySide6 and featuring an integrated React dashboard, it provides enterprise-grade network monitoring capabilities in an easy-to-use package.

### 🌟 Key Features

- **Advanced Packet Filtering** - Real-time categorization into 12+ categories (web, DNS, P2P, gaming, etc.)
- **Smart Threat Detection** - Multi-algorithm detection for port scans, brute force, malware communication
- **Performance Optimization** - Memory management, rate limiting, and automatic resource optimization
- **Professional Windows Integration** - UAC handling, privilege detection, system tray integration
- **Interactive Dashboard** - Real-time visualization with embedded React interface
- **Priority-based Processing** - Critical, High, Normal, Low priority packet handling
- **Comprehensive Statistics** - Live performance metrics with CPU/memory monitoring
- **Export & Analysis** - JSON export with comprehensive metadata and filtering
- **Network Interface Management** - Detailed Windows adapter detection and configuration
- **Enterprise-ready Architecture** - Thread-safe operations, error handling, and scalability

### 🏗️ Architecture

```
CyberSnoop/
├── desktop_app/           # Main application
│   ├── cybersnoop_desktop.py    # Main entry point
│   ├── backend/                 # Core functionality
│   │   ├── network_monitor.py   # Network monitoring engine
│   │   ├── threat_detector.py   # Advanced threat detection
│   │   ├── database_manager.py  # Data persistence
│   │   ├── api_server.py        # FastAPI backend
│   │   ├── privilege_manager.py # Windows UAC handling
│   │   └── logging_system.py    # Centralized logging
│   └── config/                  # Configuration management
│       ├── config_manager.py    # Settings persistence
│       └── settings_dialog.py   # UI configuration
└── cybersnoop-dashboard/  # React frontend
    └── [React components]
```

## 🚀 Quick Start

### Prerequisites

- **Windows 10/11** (Administrator privileges recommended)
- **Python 3.11+**
- **Git** for cloning the repository

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/cybersnoop.git
   cd cybersnoop
   ```

2. **Install Python dependencies**
   ```bash
   cd desktop_app
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python cybersnoop_desktop.py
   ```

### First Run

1. The application will request administrator privileges for network packet capture
2. Select your network interface in Settings → Network tab
3. Start monitoring from the main dashboard
4. View real-time network statistics and threat alerts

## 📊 Screenshots

### Main Dashboard
![Dashboard](docs/screenshots/dashboard.png)
*Real-time network monitoring with threat detection*

### Network Interface Selection
![Interface Selection](docs/screenshots/interfaces.png)
*Professional network adapter detection and configuration*

### Threat Detection
![Threat Detection](docs/screenshots/threats.png)
*Advanced threat detection with detailed analysis*

## 🔧 Development

### Running Tests

```bash
# Test Day 1 components (basic framework)
python test_day1.py

# Test Day 2 components (database and API)
python test_day2.py

# Test Day 3 components (advanced features)
python test_day3.py

# Test Day 4 components (packet filtering & performance)
python test_day4_basic.py
```

### Project Structure

- **Day 1**: Basic application framework, system tray, configuration
- **Day 2**: Database integration, enhanced API, comprehensive logging
- **Day 3**: Windows integration, advanced threat detection, enhanced UI

### Development Progress

Track detailed development progress in [DEVELOPMENT_PROGRESS.md](DEVELOPMENT_PROGRESS.md)

## 🛠️ Technology Stack

### Backend
- **Python 3.11+** - Core application language
- **PySide6** - Desktop application framework
- **FastAPI** - REST API backend
- **SQLite** - Local database storage
- **Scapy** - Network packet capture and analysis

### Frontend
- **React** - Dashboard user interface
- **TypeScript** - Type-safe frontend development
- **Tailwind CSS** - Modern styling framework
- **Chart.js** - Real-time data visualization

### Windows Integration
- **PowerShell** - Network adapter detection
- **WMI** - System information gathering
- **UAC** - Privilege elevation handling

## 🔐 Security Features

### Threat Detection
- **Port Scan Detection** - Identifies reconnaissance attempts
- **DDoS Attack Detection** - Monitors traffic volume patterns
- **Brute Force Detection** - Tracks authentication failures
- **Malware Communication** - Detects suspicious network patterns
- **Anomaly Detection** - Statistical analysis of traffic patterns

### Data Protection
- **Local Storage** - All data remains on your system
- **Encrypted Logs** - Security events with proper formatting
- **Data Retention** - Configurable cleanup policies
- **Privacy First** - No data transmitted externally

## 📈 Performance

- **Real-time Processing** - Minimal latency network monitoring
- **Memory Efficient** - Optimized packet buffer management
- **Scalable Architecture** - Handles high-traffic networks
- **Background Operation** - System tray integration

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

### Code Quality

- Follow PEP 8 style guidelines
- Include comprehensive tests
- Update documentation
- Add type hints where appropriate

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](https://github.com/your-username/cybersnoop/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-username/cybersnoop/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/cybersnoop/discussions)

## 🗺️ Roadmap

### Phase 1: Foundation (Days 1-3) ✅ COMPLETE
- [x] Desktop application framework
- [x] Database integration and logging
- [x] Windows integration and advanced threat detection

### Phase 2: Core Features (Days 4-7) 🚧 IN PROGRESS
- [ ] Real-time packet capture engine
- [ ] Advanced threat detection algorithms
- [ ] API server and dashboard integration

### Phase 3: Polish & Distribution (Days 8-16)
- [ ] React dashboard integration
- [ ] Professional installer creation
- [ ] Performance optimization and testing

## 🙏 Acknowledgments

- **Scapy** - Powerful packet manipulation library
- **PySide6** - Excellent Python Qt bindings
- **FastAPI** - Modern, fast web framework
- **React** - Powerful frontend framework

---

**CyberSnoop** - Professional Network Security Monitoring Made Simple

*Built with ❤️ for network security professionals and enthusiasts*
