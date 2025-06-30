#!/usr/bin/env python3
"""
CyberSnoop Enterprise Setup Script
Configures enterprise features and integrations
"""

import sys
import os
import json
import subprocess
from pathlib import Path

def install_enterprise_dependencies():
    """Install enterprise dependencies"""
    print("🔧 Installing enterprise dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "enterprise_requirements.txt"
        ])
        print("✅ Enterprise dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_enterprise_config():
    """Setup enterprise configuration"""
    print("⚙️ Setting up enterprise configuration...")
    
    config_path = Path("desktop_app/config/enterprise_config.json")
    
    if config_path.exists():
        print("📄 Enterprise configuration already exists")
        
        # Ask if user wants to reconfigure
        response = input("Do you want to reconfigure? (y/N): ").lower()
        if response != 'y':
            return True
    
    # Interactive configuration
    print("\n🔧 Enterprise Configuration Setup")
    print("=" * 40)
    
    config = {
        "enterprise": {
            "enabled": True,
            "features": {},
            "siem": {},
            "ai": {},
            "compliance": {},
            "cloud": {}
        }
    }
    
    # SIEM Integration
    print("\n📊 SIEM Integration:")
    siem_enabled = input("Enable SIEM integration? (y/N): ").lower() == 'y'
    config["enterprise"]["features"]["siem_integration"] = siem_enabled
    
    if siem_enabled:
        siem_type = input("SIEM type (splunk/elastic/qradar): ").lower()
        config["enterprise"]["siem"]["type"] = siem_type
        
        if siem_type == "splunk":
            host = input("Splunk host (localhost): ") or "localhost"
            port = input("Splunk HEC port (8088): ") or "8088"
            token = input("Splunk HEC token: ")
            
            config["enterprise"]["siem"]["splunk"] = {
                "host": host,
                "port": int(port),
                "token": token,
                "index": "cybersnoop"
            }
    
    # AI/ML Features
    print("\n🤖 AI/ML Features:")
    ai_enabled = input("Enable AI/ML threat detection? (y/N): ").lower() == 'y'
    config["enterprise"]["features"]["ai_detection"] = ai_enabled
    
    # Compliance Reporting
    print("\n📋 Compliance Reporting:")
    compliance_enabled = input("Enable compliance reporting? (y/N): ").lower() == 'y'
    config["enterprise"]["features"]["compliance_reporting"] = compliance_enabled
    
    if compliance_enabled:
        print("Select compliance frameworks:")
        frameworks = []
        if input("  PCI DSS? (y/N): ").lower() == 'y':
            frameworks.append("pci_dss")
        if input("  HIPAA? (y/N): ").lower() == 'y':
            frameworks.append("hipaa")
        if input("  GDPR? (y/N): ").lower() == 'y':
            frameworks.append("gdpr")
        
        config["enterprise"]["compliance"]["reports"] = frameworks
    
    # Cloud Monitoring
    print("\n☁️ Cloud Monitoring:")
    cloud_enabled = input("Enable cloud monitoring? (y/N): ").lower() == 'y'
    config["enterprise"]["features"]["cloud_monitoring"] = cloud_enabled
    
    # Save configuration
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved to {config_path}")
    return True

def test_enterprise_features():
    """Test enterprise features"""
    print("🧪 Testing enterprise features...")
    
    try:
        # Test import
        sys.path.append(str(Path("desktop_app").absolute()))
        from enterprise_compatibility import EnterpriseEnhancedCyberSnoop
        
        print("✅ Enterprise module imports successfully")
        
        # Test basic initialization
        from config.config_manager import ConfigManager
        from backend.enhanced_database_manager import EnhancedDatabaseManager
        
        config = ConfigManager()
        db = EnhancedDatabaseManager(config)
        
        enterprise = EnterpriseEnhancedCyberSnoop(config, db)
        print("✅ Enterprise components initialize successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("🚀 CyberSnoop Enterprise Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("desktop_app").exists():
        print("❌ Please run this script from the CyberSnoop root directory")
        sys.exit(1)
    
    # Step 1: Install dependencies
    if not install_enterprise_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Step 2: Setup configuration
    if not setup_enterprise_config():
        print("❌ Setup failed during configuration")
        sys.exit(1)
    
    # Step 3: Test features
    if not test_enterprise_features():
        print("❌ Setup failed during testing")
        print("Enterprise features may not work correctly")
    
    print("\n" + "=" * 50)
    print("🎉 Enterprise Setup Complete!")
    print("=" * 50)
    print("Next steps:")
    print("1. Review the configuration in desktop_app/config/enterprise_config.json")
    print("2. Configure your SIEM credentials if enabled")
    print("3. Run the enhanced desktop application")
    print("4. Test enterprise features from the UI")
    print("\nTo start CyberSnoop with enterprise features:")
    print("  cd desktop_app")
    print("  python enhanced_cybersnoop_desktop.py")

if __name__ == "__main__":
    main()
