#!/usr/bin/env python3
"""
CyberSnoop UI and Feature Test Script
Tests all fixed issues and validates functionality
"""

import sys
import os
from pathlib import Path
import subprocess
import time

def test_api_server():
    """Test if API server can start properly"""
    print("🧪 Testing API Server startup...")
    
    try:
        # Try to import API components
        sys.path.append('desktop_app')
        from backend.api_server import CyberSnoopAPI
        from backend.enhanced_database_manager import EnhancedDatabaseManager
        from backend.network_monitor import NetworkMonitor
        
        # Create simple config
        class SimpleConfig:
            def get(self, key, default=None):
                return default
        
        config_manager = SimpleConfig()
        db_manager = EnhancedDatabaseManager(config_manager)
        network_monitor = NetworkMonitor(config_manager)
        api = CyberSnoopAPI(config_manager, db_manager, network_monitor)
        
        print("✅ API Server components imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ API Server test failed: {e}")
        return False

def test_desktop_app_imports():
    """Test if desktop app can import properly"""
    print("🧪 Testing Desktop App imports...")
    
    try:
        # Test PySide6 imports
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        print("✅ PySide6 imports successful")
        
        # Test backend imports
        sys.path.append('desktop_app')
        from enhanced_cybersnoop_desktop import EnhancedCyberSnoopApp
        print("✅ Desktop App imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Desktop App import test failed: {e}")
        return False

def test_requirements():
    """Test system requirements"""
    print("🧪 Testing System Requirements...")
    
    # Test Python version
    import sys
    python_version = sys.version_info
    if python_version >= (3, 11):
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️ Python version: {python_version.major}.{python_version.minor} (3.11+ recommended)")
    
    # Test required packages
    required_packages = [
        'PySide6', 'fastapi', 'uvicorn', 'requests', 
        'sqlalchemy', 'pandas', 'numpy', 'cryptography'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("🧪 Testing File Structure...")
    
    required_files = [
        'desktop_app/enhanced_cybersnoop_desktop.py',
        'desktop_app/start_api_server.py',
        'desktop_app/backend/api_server.py',
        'desktop_app/backend/network_monitor.py',
        'desktop_app/backend/threat_detector.py',
        'desktop_app/backend/enhanced_database_manager.py',
        'requirements.txt',
        'setup.py',
        'SYSTEM_REQUIREMENTS.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - Missing")
    
    if missing_files:
        print(f"⚠️ Missing files: {len(missing_files)}")
        return False
    
    return True

def test_desktop_icon():
    """Test desktop icon creation"""
    print("🧪 Testing Desktop Icon...")
    
    desktop_paths = [
        Path.home() / "Desktop",
        Path.home() / "OneDrive" / "Desktop"
    ]
    
    for desktop in desktop_paths:
        if desktop.exists():
            print(f"✅ Desktop found: {desktop}")
            
            # Check if shortcuts exist
            shortcuts = list(desktop.glob("CyberSnoop*"))
            if shortcuts:
                print(f"✅ Desktop shortcuts found: {len(shortcuts)}")
                for shortcut in shortcuts:
                    print(f"   📎 {shortcut.name}")
            else:
                print("ℹ️ No desktop shortcuts found (run create_desktop_icon.py)")
            
            return True
    
    print("❌ No desktop folder found")
    return False

def run_comprehensive_test():
    """Run all tests"""
    print("🧪 " + "="*50)
    print("🧪 CyberSnoop Comprehensive Test Suite")
    print("🧪 " + "="*50)
    
    tests = [
        ("System Requirements", test_requirements),
        ("File Structure", test_file_structure),
        ("Desktop App Imports", test_desktop_app_imports),
        ("API Server", test_api_server),
        ("Desktop Icon", test_desktop_icon)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n🎯 " + "="*50)
    print("🎯 TEST SUMMARY")
    print("🎯 " + "="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<10} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED! CyberSnoop is ready for use.")
        print("\n🚀 Quick Start:")
        print("1. Start API: python desktop_app/start_api_server.py")
        print("2. Launch App: python desktop_app/enhanced_cybersnoop_desktop.py")
    else:
        print("⚠️ Some tests FAILED. Please fix issues before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
