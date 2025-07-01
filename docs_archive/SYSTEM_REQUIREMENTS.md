# 🖥️ CyberSnoop - System Requirements & Specifications

## 📋 **Minimum System Requirements**

### **Operating System**
- ✅ **Windows 10** (64-bit) - Version 1903 or later
- ✅ **Windows 11** (64-bit) - All versions supported
- ⚠️ **Windows Server 2019/2022** - Supported (business use)

### **Hardware Requirements**

#### **Minimum Configuration**
- **CPU**: Intel Core i3-8100 / AMD Ryzen 3 2200G or equivalent
- **RAM**: 8 GB DDR4
- **Storage**: 2 GB free disk space (SSD recommended)
- **Network**: Ethernet/Wi-Fi adapter with admin privileges
- **Display**: 1366x768 resolution (1920x1080 recommended)

#### **Recommended Configuration**
- **CPU**: Intel Core i5-10400 / AMD Ryzen 5 3600 or better
- **RAM**: 16 GB DDR4 or higher
- **Storage**: 5 GB free SSD space
- **Network**: Gigabit Ethernet adapter
- **Display**: 1920x1080 or higher (dual monitor setup recommended)

#### **High-Performance Configuration**
- **CPU**: Intel Core i7-11700K / AMD Ryzen 7 5800X or better
- **RAM**: 32 GB DDR4 or higher
- **Storage**: 10 GB free NVMe SSD space
- **Network**: Multiple network adapters (for advanced monitoring)
- **Display**: 2560x1440 or 4K display

## 🔧 **Software Dependencies**

### **Required Software**
- **Python**: 3.11 or higher (3.12 recommended)
- **Node.js**: 18.x or higher (for web dashboard)
- **NPM**: 8.x or higher
- **Git**: Latest version (for updates)

### **Python Packages** (Auto-installed)
- **PySide6**: 6.6.0+ (GUI framework)
- **FastAPI**: 0.104.0+ (API server)
- **Uvicorn**: 0.24.0+ (ASGI server)
- **Scapy**: 2.5.0+ (packet analysis)
- **SQLAlchemy**: 2.0.23+ (database)
- **Requests**: 2.31.0+ (HTTP client)
- **And 40+ other security libraries**

## 🌐 **Network Requirements**

### **Permissions**
- **Administrator Rights**: Required for packet capture
- **Firewall Access**: Allow CyberSnoop through Windows Firewall
- **Network Interface**: Raw socket access for deep packet inspection

### **Ports Used**
- **8889**: API Server (localhost only)
- **3000/3001**: Web Dashboard (localhost only)
- **Custom**: Configurable monitoring ports

## 💾 **Storage Requirements**

### **Installation**
- **Base Installation**: ~500 MB
- **Python Dependencies**: ~300 MB
- **Node.js Dependencies**: ~200 MB
- **Total Initial**: ~1 GB

### **Runtime Data**
- **Packet Logs**: 100 MB - 10 GB (configurable retention)
- **Threat Database**: 50-500 MB (grows with detections)
- **Reports/Exports**: 10-100 MB (user generated)

## 🔒 **Security Requirements**

### **User Permissions**
- **Run as Administrator**: Required for network monitoring
- **UAC**: May prompt for elevation during startup
- **Antivirus**: Add CyberSnoop to exclusion list (prevents interference)

### **Network Access**
- **Promiscuous Mode**: Required for full packet capture
- **Raw Sockets**: Required for deep packet inspection
- **WinPcap/Npcap**: Auto-installed with Scapy

## 🚀 **Performance Optimization**

### **For Standard Use** (Home/Small Office)
```
CPU: 4+ cores, 2.5+ GHz
RAM: 8-16 GB
Network: 100 Mbps monitoring capability
```

### **For Enterprise Use** (Large Networks)
```
CPU: 8+ cores, 3.0+ GHz
RAM: 32-64 GB
Network: 1+ Gbps monitoring capability
Storage: High-speed SSD with 100+ GB free
```

### **For Security Operations Center (SOC)**
```
CPU: 16+ cores, 3.5+ GHz
RAM: 64-128 GB
Network: 10+ Gbps monitoring capability
Storage: Enterprise SSD with 500+ GB free
Multiple monitors: 3x 1920x1080 or 2x 4K displays
```

## ⚡ **Expected Performance**

### **Packet Processing**
- **Standard**: 1,000-10,000 packets/second
- **High-Performance**: 10,000-100,000 packets/second
- **Enterprise**: 100,000+ packets/second

### **Memory Usage**
- **Idle**: 200-500 MB RAM
- **Active Monitoring**: 500 MB - 2 GB RAM
- **Heavy Load**: 2-8 GB RAM (with large packet buffers)

### **CPU Usage**
- **Idle**: 1-5% CPU
- **Active Monitoring**: 10-30% CPU
- **Heavy Analysis**: 30-70% CPU

## 🎯 **Use Case Recommendations**

### **Home Users**
- Minimum requirements sufficient
- Focus on malware detection and basic monitoring

### **Small Business (1-50 devices)**
- Recommended configuration
- SIEM integration and compliance reporting

### **Enterprise (50+ devices)**
- High-performance configuration
- Full SOC integration with advanced analytics

### **Security Professionals**
- Maximum configuration
- Real-time threat hunting and forensics

## 🔧 **Installation Notes**

### **Fresh Installation**
1. Ensure Python 3.11+ is installed
2. Run `python setup.py install`
3. First launch may take 2-3 minutes (dependency verification)

### **Network Setup**
1. Run as Administrator for full functionality
2. Allow through Windows Firewall when prompted
3. Configure network interfaces in Settings

### **Troubleshooting**
- **Slow Performance**: Increase RAM or reduce monitoring scope
- **High CPU**: Adjust packet buffer sizes in settings
- **Connection Issues**: Check firewall and antivirus settings

---

**💡 Pro Tip**: For optimal performance, dedicate a machine specifically to CyberSnoop in production environments. Virtual machines are supported but may have reduced packet capture capabilities.

**🆓 Best Part**: All these enterprise-grade features are completely FREE! No licensing costs, no user limits, no feature restrictions.**
