#!/usr/bin/env python3
"""
CyberSnoop - Free & Open Source Network Security Monitor
Simple setup script for all features (no restrictions)
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print the CyberSnoop setup banner"""
    print("🛡️" + "="*60)
    print("   CyberSnoop - Free Network Security Monitor")
    print("   100% Free & Open Source - All Features Included")
    print("="*62)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ is required")
        print(f"   Current version: {version.major}.{version.minor}")
        print("   Please upgrade Python and try again")
        return False
    print(f"✅ Python {version.major}.{version.minor} - Compatible")
    return True

def check_os():
    """Check if OS is supported"""
    os_name = platform.system()
    if os_name != "Windows":
        print(f"⚠️  CyberSnoop is optimized for Windows")
        print(f"   Current OS: {os_name}")
        print("   Some features may not work as expected")
        return True
    print(f"✅ {os_name} - Fully supported")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def setup_config():
    """Create default configuration"""
    print("\n⚙️  Setting up configuration...")
    
    config_dir = Path("desktop_app/config")
    config_dir.mkdir(exist_ok=True)
    
    # Create a simple config file
    config_content = """{
    "app_name": "CyberSnoop",
    "version": "1.0.0",
    "free_version": true,
    "all_features_enabled": true,
    "network_monitoring": {
        "enabled": true,
        "interfaces": "auto-detect"
    },
    "threat_detection": {
        "ai_ml_enabled": true,
        "behavioral_analysis": true,
        "anomaly_detection": true
    },
    "integrations": {
        "siem_enabled": true,
        "cloud_monitoring": true,
        "compliance_reporting": true
    },
    "ui": {
        "dashboard_enabled": true,
        "system_tray": true,
        "notifications": true
    }
}"""
    
    config_file = config_dir / "app_config.json"
    config_file.write_text(config_content)
    print("✅ Configuration created - All features enabled")
    return True

def create_shortcuts():
    """Create desktop shortcuts"""
    print("\n🔗 Creating shortcuts...")
    
    # For now, just create a simple batch file
    desktop = Path.home() / "Desktop"
    if desktop.exists():
        shortcut_content = f"""@echo off
cd /d "{Path.cwd().absolute()}"
python desktop_app\\enhanced_cybersnoop_desktop.py
pause
"""
        shortcut_file = desktop / "CyberSnoop.bat"
        shortcut_file.write_text(shortcut_content)
        print(f"✅ Desktop shortcut created: {shortcut_file}")
    
    return True

def main():
    """Main setup function"""
    print_banner()
    
    # Check system requirements
    if not check_python_version():
        return False
    
    if not check_os():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Setup configuration
    if not setup_config():
        return False
    
    # Create shortcuts
    if not create_shortcuts():
        return False
    
    print("\n🎉 CyberSnoop setup completed successfully!")
    print("\n🚀 To start CyberSnoop:")
    print("   1. Double-click the desktop shortcut, OR")
    print("   2. Run: python desktop_app\\enhanced_cybersnoop_desktop.py")
    print("\n💡 All features are free and enabled by default!")
    print("   - AI/ML Threat Detection ✅")
    print("   - SIEM Integrations ✅") 
    print("   - Cloud Monitoring ✅")
    print("   - Compliance Reporting ✅")
    print("   - Advanced Analytics ✅")
    print("\n🤝 Need help? Visit: https://github.com/your-username/cybersnoop/issues")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
