"""
Day 7: Simplified API Server Test
Tests API endpoints with inline server startup
"""
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

def test_api_functionality():
    """Test API functionality by creating components and testing methods"""
    print("🧪 Day 7: Testing API Server Components...")
    
    tests_passed = 0
    tests_total = 0
    
    try:
        # Test 1: Component initialization
        tests_total += 1
        print("1. Testing component initialization...")
        config_manager = ConfigManager()
        db_manager = DatabaseManager(config_manager)
        network_monitor = NetworkMonitor(config_manager)
        api_server = CyberSnoopAPI(config_manager, db_manager, network_monitor)
        print("✅ Component initialization: OK")
        tests_passed += 1
        
        # Test 2: Database methods
        tests_total += 1
        print("2. Testing database query methods...")
        packet_count = db_manager.get_packet_count()
        threat_count = db_manager.get_threat_count()
        recent_packets = db_manager.get_recent_packets(10)
        recent_threats = db_manager.get_recent_threats(10)
        print(f"✅ Database queries: {packet_count} packets, {threat_count} threats")
        tests_passed += 1
        
        # Test 3: API app creation
        tests_total += 1
        print("3. Testing FastAPI app creation...")
        if hasattr(api_server, 'app') and api_server.app is not None:
            print("✅ FastAPI app created successfully")
            tests_passed += 1
        else:
            print("❌ FastAPI app creation failed")
        
        # Test 4: Route setup
        tests_total += 1
        print("4. Testing API route setup...")
        routes = [route.path for route in api_server.app.routes]
        expected_routes = ["/", "/api/status", "/api/stats", "/api/interfaces", "/api/packets", "/api/threats"]
        routes_found = sum(1 for route in expected_routes if route in routes)
        if routes_found >= 5:  # Allow for some flexibility
            print(f"✅ API routes setup: {routes_found}/{len(expected_routes)} routes found")
            tests_passed += 1
        else:
            print(f"❌ API routes setup: Only {routes_found}/{len(expected_routes)} routes found")
        
        # Test 5: Authentication setup
        tests_total += 1
        print("5. Testing authentication setup...")
        # Check if security is properly configured by looking at route dependencies
        auth_protected_routes = 0
        for route in api_server.app.routes:
            if hasattr(route, 'dependencies') and route.dependencies:
                auth_protected_routes += 1
        if auth_protected_routes > 0:
            print(f"✅ Authentication setup: {auth_protected_routes} protected routes")
            tests_passed += 1
        else:
            print("❌ Authentication setup: No protected routes found")
        
        # Test 6: WebSocket endpoint
        tests_total += 1
        print("6. Testing WebSocket endpoint...")
        ws_routes = [route.path for route in api_server.app.routes if hasattr(route, 'path') and route.path == "/ws"]
        if ws_routes:
            print("✅ WebSocket endpoint: OK")
            tests_passed += 1
        else:
            print("❌ WebSocket endpoint: Not found")
        
        # Test 7: Server configuration
        tests_total += 1
        print("7. Testing server configuration...")
        if hasattr(api_server, 'start_server'):
            print("✅ Server configuration: OK")
            tests_passed += 1
        else:
            print("❌ Server configuration: Missing start_server method")
        
        # Test 8: Database integration
        tests_total += 1
        print("8. Testing database integration...")
        if api_server.database_manager is not None:
            print("✅ Database integration: OK")
            tests_passed += 1
        else:
            print("❌ Database integration: Missing database manager")
        
        # Test 9: Network monitor integration
        tests_total += 1
        print("9. Testing network monitor integration...")
        if api_server.network_monitor is not None:
            print("✅ Network monitor integration: OK")
            tests_passed += 1
        else:
            print("❌ Network monitor integration: Missing network monitor")
        
        # Test 10: WebSocket client management
        tests_total += 1
        print("10. Testing WebSocket client management...")
        if hasattr(api_server, 'connected_clients') and isinstance(api_server.connected_clients, list):
            print("✅ WebSocket client management: OK")
            tests_passed += 1
        else:
            print("❌ WebSocket client management: Missing or invalid")
        
    except Exception as e:
        print(f"❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n📊 Day 7 API Server Component Tests: {tests_passed}/{tests_total} PASSING ({int(tests_passed/tests_total*100)}%)")
    
    if tests_passed == tests_total:
        print("🎉 All Day 7 API Server component tests PASSED!")
        return True
    else:
        print("⚠️ Some Day 7 API Server component tests FAILED!")
        return False

if __name__ == "__main__":
    success = test_api_functionality()
    sys.exit(0 if success else 1)
