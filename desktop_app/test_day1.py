"""
CyberSnoop Day 1 Test Script
Quick test to verify the basic desktop application framework is working.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        from PySide6.QtWidgets import QApplication
        print("✅ PySide6 import successful")
    except ImportError as e:
        print(f"❌ PySide6 import failed: {e}")
        return False
        
    try:
        from config.config_manager import ConfigManager
        print("✅ ConfigManager import successful")
    except ImportError as e:
        print(f"❌ ConfigManager import failed: {e}")
        return False
        
    try:
        from backend.api_server import CyberSnoopAPI
        print("✅ API Server import successful")
    except ImportError as e:
        print(f"❌ API Server import failed: {e}")
        return False
        
    try:
        from backend.network_monitor import NetworkMonitor
        print("✅ Network Monitor import successful")
    except ImportError as e:
        print(f"❌ Network Monitor import failed: {e}")
        return False
        
    return True

def test_config_manager():
    """Test configuration manager functionality"""
    print("\nTesting Configuration Manager...")
    
    try:
        from config.config_manager import ConfigManager
        config = ConfigManager()
        
        # Test basic get/set
        test_value = config.get("application.name")
        print(f"✅ Config get works: {test_value}")
        
        config.set("test.value", "test123")
        retrieved = config.get("test.value")
        
        if retrieved == "test123":
            print("✅ Config set/get works correctly")
        else:
            print(f"❌ Config set/get failed: expected 'test123', got '{retrieved}'")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration Manager test failed: {e}")
        return False

def test_api_server():
    """Test API server initialization"""
    print("\nTesting API Server...")
    
    try:
        from config.config_manager import ConfigManager
        from backend.api_server import CyberSnoopAPI
        config = ConfigManager()
        api = CyberSnoopAPI(config)
        print("✅ API Server initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ API Server test failed: {e}")
        return False

def test_network_monitor():
    """Test network monitor initialization"""
    print("\nTesting Network Monitor...")
    
    try:
        from config.config_manager import ConfigManager
        from backend.network_monitor import NetworkMonitor
        config = ConfigManager()
        monitor = NetworkMonitor(config)
        
        # Test getting current stats
        stats = monitor.get_current_stats()
        print(f"✅ Network Monitor stats: {stats}")
        return True
        
    except Exception as e:
        print(f"❌ Network Monitor test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("CyberSnoop Day 1 - Component Testing")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_manager,
        test_api_server,
        test_network_monitor
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("❌ Test failed!")
            
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All tests passed! Day 1 implementation is working correctly.")
        print("\nTo run the full application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run application: python cybersnoop_desktop.py")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
