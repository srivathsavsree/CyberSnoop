"""
Day 7: API Server Test Runner
Starts the API server and runs comprehensive endpoint tests
"""
import asyncio
import threading
import time
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_app.backend.api_server import CyberSnoopAPI
from desktop_app.config.config_manager import ConfigManager
from desktop_app.backend.enhanced_database_manager import EnhancedDatabaseManager as DatabaseManager
from desktop_app.backend.network_monitor import NetworkMonitor

def start_test_server():
    """Start API server for testing"""
    print("🚀 Starting CyberSnoop API server for Day 7 testing...")
    
    # Initialize components
    config_manager = ConfigManager()
    db_manager = DatabaseManager(config_manager)
    network_monitor = NetworkMonitor(config_manager)
    
    # Create API server
    api_server = CyberSnoopAPI(config_manager, db_manager, network_monitor)
    
    # Start server
    api_server.start_server(host="127.0.0.1", port=8888)

def run_manual_tests():
    """Run manual API endpoint tests"""
    import requests
    from requests.auth import HTTPBasicAuth
    
    BASE_URL = "http://127.0.0.1:8888"
    AUTH = HTTPBasicAuth("admin", "cybersnoop2025")
    
    print("🧪 Running Day 7 API Server Manual Tests...")
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    tests_passed = 0
    tests_total = 0
    
    # Test endpoints
    endpoints = [
        ("/api/status", "System Status"),
        ("/api/stats", "Network Statistics"),
        ("/api/interfaces", "Network Interfaces"),
        ("/api/packets", "Recent Packets"),
        ("/api/threats", "Recent Threats")
    ]
    
    for endpoint, description in endpoints:
        tests_total += 1
        try:
            response = requests.get(BASE_URL + endpoint, auth=AUTH, timeout=5)
            if response.status_code == 200:
                print(f"✅ {description} ({endpoint}): OK")
                tests_passed += 1
            else:
                print(f"❌ {description} ({endpoint}): HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {description} ({endpoint}): {str(e)}")
    
    # Test monitoring control
    control_endpoints = [
        ("/api/monitoring/start", "POST", "Start Monitoring"),
        ("/api/monitoring/stop", "POST", "Stop Monitoring")
    ]
    
    for endpoint, method, description in control_endpoints:
        tests_total += 1
        try:
            if method == "POST":
                response = requests.post(BASE_URL + endpoint, auth=AUTH, timeout=5)
            else:
                response = requests.get(BASE_URL + endpoint, auth=AUTH, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {description} ({endpoint}): OK")
                tests_passed += 1
            else:
                print(f"❌ {description} ({endpoint}): HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {description} ({endpoint}): {str(e)}")
    
    # Test authentication
    tests_total += 1
    try:
        response = requests.get(BASE_URL + "/api/status", timeout=5)  # No auth
        if response.status_code == 401:
            print("✅ Authentication Required: OK")
            tests_passed += 1
        else:
            print(f"❌ Authentication Required: Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Authentication Required: {str(e)}")
    
    # Test input validation
    tests_total += 1
    try:
        response = requests.get(BASE_URL + "/api/packets?limit=0", auth=AUTH, timeout=5)
        if response.status_code == 400:
            print("✅ Input Validation: OK")
            tests_passed += 1
        else:
            print(f"❌ Input Validation: Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Input Validation: {str(e)}")
    
    print(f"\n📊 Day 7 API Server Test Results: {tests_passed}/{tests_total} PASSING ({int(tests_passed/tests_total*100)}%)")
    
    if tests_passed == tests_total:
        print("🎉 All Day 7 API Server tests PASSED!")
        return True
    else:
        print("⚠️ Some Day 7 API Server tests FAILED!")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run tests (server should already be running)
        success = run_manual_tests()
        sys.exit(0 if success else 1)
    else:
        # Start server
        start_test_server()
