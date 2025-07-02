# 🧪 CyberSnoop Testing Instructions

> **For External Testers - Please Follow These Steps**

## 📋 System Requirements to Verify

### **Minimum Requirements** (Must Work)
- **CPU**: Intel Core i5 (4th generation) or AMD Ryzen 5 equivalent
- **RAM**: 8 GB DDR4
- **Storage**: 2 GB free disk space
- **OS**: Windows 10 (64-bit) or Windows 11
- **Network**: Ethernet or Wi-Fi adapter with driver support
- **Privileges**: Administrator access for installation

### **Recommended Configuration** (Best Performance)
- **CPU**: Intel Core i7 (8th generation or newer) or AMD Ryzen 7 equivalent
- **RAM**: 16 GB DDR4 or higher
- **Storage**: 5 GB free SSD space
- **OS**: Windows 11 (64-bit) with latest updates
- **Network**: Gigabit Ethernet for high-traffic monitoring

---

## 🚀 Testing Steps

### **Step 1: Download**
1. Download `CyberSnoop-Setup.exe` from the GitHub repository
2. File size should be approximately 15 MB (contains all dependencies)

### **Step 2: Installation**
1. **Right-click** on `CyberSnoop-Setup.exe` → **"Run as administrator"**
2. Click "Yes" when Windows UAC prompts
3. In the installer:
   - ✅ Ensure "Create Desktop Shortcut" is checked
   - Click "Install CyberSnoop"
   - Wait for installation to complete

### **Step 3: Verify Installation**
1. **Check installed files**:
   - Location: `C:\Program Files\CyberSnoop\`
   - Should contain:
     - `desktop_app\` folder with Python files
     - `requirements.txt`
     - `README.md`
     - `LICENSE.md`
     - `CyberSnoop.bat` (launcher)
     - `cybersnoop.ico` (icon file)

2. **Check desktop shortcut**:
   - Should appear on desktop as "CyberSnoop.lnk"
   - Should have custom icon (shield with "S")
   - Should point to the correct installation directory

### **Step 4: Launch Application**
1. **Method 1**: Double-click desktop shortcut
2. **Method 2**: Navigate to `C:\Program Files\CyberSnoop\` and run `CyberSnoop.bat`

### **Step 5: Test Core Functions**
1. **Application startup**:
   - Should launch without errors
   - PySide6 GUI should appear
   - Network monitoring should initialize

2. **Basic functionality**:
   - Try starting/stopping network monitoring
   - Check if interface detects network adapters
   - Verify dashboard displays correctly

---

## 🐛 What to Report

### **Critical Issues** (Must Fix)
- ❌ Installation fails or crashes
- ❌ Desktop shortcut not created or doesn't work
- ❌ Application won't launch
- ❌ Missing files after installation
- ❌ Python dependency errors

### **Performance Issues** (System Requirements)
- ⚠️ Slow performance on minimum requirements
- ⚠️ High CPU/RAM usage beyond expected
- ⚠️ Network monitoring drops packets
- ⚠️ Dashboard lag or freezing

### **Minor Issues** (Nice to Fix)
- 💡 UI/UX improvements
- 💡 Feature requests
- 💡 Documentation clarifications

---

## 📊 Testing Report Template

```
**Test Environment:**
- OS: Windows [10/11] [version]
- CPU: [Model and generation]
- RAM: [Amount] GB
- Storage: [Type and available space]
- Network: [Ethernet/Wi-Fi]

**Installation Test:**
- ✅/❌ Downloaded installer successfully
- ✅/❌ Ran as administrator without issues
- ✅/❌ Installation completed successfully
- ✅/❌ Desktop shortcut created
- ✅/❌ All files installed correctly

**Application Test:**
- ✅/❌ Application launches from shortcut
- ✅/❌ Application launches from .bat file
- ✅/❌ Network monitoring starts
- ✅/❌ Dashboard displays correctly
- ✅/❌ No crashes or errors

**Performance Test:**
- CPU usage: [%] during idle/monitoring
- RAM usage: [MB] during idle/monitoring
- Network monitoring: [packets/sec] handled
- Dashboard responsiveness: [Good/Slow/Laggy]

**Issues Found:**
[List any problems or suggestions]

**Overall Rating:**
[1-5 stars] - [Brief summary]
```

---

## 🔧 Troubleshooting

### **Common Issues**
1. **"Windows protected your PC"**: Click "More info" → "Run anyway"
2. **Python not found**: Installer should handle this automatically
3. **Permission denied**: Ensure running as administrator
4. **Desktop shortcut missing**: Manually create from `C:\Program Files\CyberSnoop\CyberSnoop.bat`

### **If Installation Fails**
1. Check Windows version (must be 64-bit)
2. Ensure administrator privileges
3. Temporarily disable antivirus
4. Check available disk space (2+ GB required)
5. Restart computer and try again

---

## 📧 Contact

- **GitHub Issues**: https://github.com/srivathsavsree/CyberSnoop/issues
- **Email**: [Your email for direct feedback]
- **Priority**: Critical bugs first, then performance, then features

---

**Thank you for testing CyberSnoop! Your feedback helps make it better for everyone.** 🙏
