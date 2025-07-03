# 🚀 CyberSnoop Installation Guide

[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Version: 2.0](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/srivathsavsree/CyberSnoop)
[![Installation: One-Click](https://img.shields.io/badge/installation-One--Click-green.svg)](https://github.com/srivathsavsree/CyberSnoop)

> **💾 Easy one-click installation for CyberSnoop Network Security Monitor**

---

## 📋 Before You Install

### **System Requirements Check**

#### **✅ Minimum Requirements**
- **OS**: Windows 10 (64-bit) or Windows 11
- **CPU**: Intel Core i5 (4th generation) or AMD Ryzen 5 equivalent
- **RAM**: 8 GB DDR4
- **Storage**: 2 GB free disk space
- **Network**: Ethernet or Wi-Fi adapter with driver support
- **Privileges**: Administrator access for installation

#### **🚀 Recommended for Best Performance**
- **OS**: Windows 11 (64-bit) with latest updates
- **CPU**: Intel Core i7 (8th generation or newer) or AMD Ryzen 7 equivalent
- **RAM**: 16 GB DDR4 or higher
- **Storage**: 5 GB free SSD space
- **Network**: Gigabit Ethernet for high-traffic monitoring
- **GPU**: Dedicated graphics card for enhanced dashboard performance

---

## 📦 Installation Methods

### **Method 1: One-Click Installer (Recommended)**

1. **Download the Installer**
   ```
   Download: CyberSnoop-Setup.exe
   Size: ~15 MB (includes all dependencies)
   ```

2. **Run as Administrator**
   - Right-click on `CyberSnoop-Setup.exe`
   - Select "Run as administrator"
   - Click "Yes" when prompted by Windows UAC

3. **Follow Installation Wizard**
   - ✅ Check "Create Desktop Shortcut" (recommended)
   - Click "Install CyberSnoop"
   - Wait for installation to complete (~2-3 minutes)

4. **Launch CyberSnoop**
   - Double-click the desktop shortcut, or
   - Navigate to `C:\Program Files\CyberSnoop\` and run `CyberSnoop.bat`

### **Method 2: Manual Installation**

```bash
# Clone the repository
git clone https://github.com/srivathsavsree/CyberSnoop.git
cd CyberSnoop

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python desktop_app/enhanced_cybersnoop_desktop.py
```

---

## 🔧 Post-Installation Setup

### **1. Network Adapter Configuration**
- CyberSnoop will automatically detect your network adapters
- Grant administrator privileges when prompted
- Select your primary network interface from the dropdown

### **2. First-Time Launch**
- The application will initialize the database
- Default dashboard will load with real-time monitoring
- Allow Windows Firewall access when prompted

### **3. Performance Optimization**
- For high-traffic networks (>1000 packets/sec), consider:
  - Increasing packet buffer size in settings
  - Using SSD storage for better database performance
  - Closing unnecessary applications during monitoring

---

## 🛠️ Troubleshooting

### **Common Installation Issues**

#### **"Installation failed: Python executable not found"**
- **Solution**: The installer will automatically handle Python installation
- **Alternative**: Install Python 3.11+ manually from python.org

#### **"Failed to create desktop shortcut"**
- **Solution**: Run installer as Administrator
- **Alternative**: Manually create shortcut to `C:\Program Files\CyberSnoop\CyberSnoop.bat`

#### **"Permission denied" errors**
- **Solution**: Ensure you're running as Administrator
- **Check**: Antivirus software isn't blocking the installation

### **Application Launch Issues**

#### **"No network adapters found"**
- **Solution**: Run CyberSnoop as Administrator
- **Check**: Network adapter drivers are properly installed

#### **"Database initialization failed"**
- **Solution**: Ensure you have write permissions to installation directory
- **Alternative**: Temporarily disable antivirus during first launch

#### **Performance Issues**
- **Close unnecessary applications** to free up system resources
- **Use Task Manager** to verify CyberSnoop isn't using excessive CPU/RAM
- **Check network traffic volume** - high traffic may require performance adjustments

---

## 📁 Installation Locations

### **Default Installation Paths**
```
Application Files: C:\Program Files\CyberSnoop\
Desktop Shortcut: %USERPROFILE%\Desktop\CyberSnoop.lnk
Database: C:\Program Files\CyberSnoop\cybersnoop.db
Logs: C:\Program Files\CyberSnoop\logs\
Configuration: C:\Program Files\CyberSnoop\config\
```

### **What Gets Installed**
- ✅ **CyberSnoop Desktop Application** (enhanced_cybersnoop_desktop.py)
- ✅ **All Python Dependencies** (automatically via pip)
- ✅ **Database Engine** (SQLite for packet storage)
- ✅ **Web Dashboard** (React-based UI components)
- ✅ **Configuration Files** (default settings)
- ✅ **Documentation** (README, LICENSE)
- ✅ **Desktop Shortcut** (for easy access)

---

## 🔄 Updating CyberSnoop

### **Automatic Updates**
- Future versions will include automatic update checking
- Updates will be downloaded and installed seamlessly

### **Manual Updates**
1. Download the latest `CyberSnoop-Setup.exe`
2. Run the new installer (it will update existing installation)
3. Your settings and data will be preserved

---

## 🗑️ Uninstallation

### **Clean Removal**
```bash
# Stop CyberSnoop if running
# Delete installation directory
rmdir /s "C:\Program Files\CyberSnoop"

# Remove desktop shortcut
del "%USERPROFILE%\Desktop\CyberSnoop.lnk"
```

### **Registry Cleanup**
- CyberSnoop doesn't modify Windows registry
- No additional cleanup required

---

## 📞 Installation Support

### **Need Help?**
- 📧 **Email**: support@cybersnoop.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/srivathsavsree/CyberSnoop/issues)
- 📖 **Documentation**: [Full Documentation](https://github.com/srivathsavsree/CyberSnoop/wiki)
- 💬 **Community**: [Discord Server](https://discord.gg/cybersnoop)

### **Before Reporting Issues**
1. ✅ Check system requirements are met
2. ✅ Run installer as Administrator
3. ✅ Temporarily disable antivirus
4. ✅ Check Windows Event Viewer for error details
5. ✅ Include error messages and system info in bug reports

---

**🎉 Congratulations! You're ready to secure your network with CyberSnoop!**
