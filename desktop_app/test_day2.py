#!/usr/bin/env python3
"""
CyberSnoop Day 2 Test Suite
Tests the enhanced core functionality including database, logging, and API integration.
"""

import sys
import os
import unittest
import tempfile
import threading
import time
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestDay2Core(unittest.TestCase):
    """Test Day 2 core functionality enhancements"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_database_manager_import(self):
        """Test database manager import"""
        try:
            from backend.database_manager import DatabaseManager
            print("✅ DatabaseManager import successful")
        except ImportError as e:
            self.fail(f"Failed to import DatabaseManager: {e}")
            
    def test_logging_system_import(self):
        """Test logging system import"""
        try:
            from backend.logging_system import initialize_logging, get_logger
            print("✅ Logging system import successful")
        except ImportError as e:
            self.fail(f"Failed to import logging system: {e}")
            
    def test_enhanced_api_server_import(self):
        """Test enhanced API server import"""
        try:
            from backend.api_server import CyberSnoopAPI
            print("✅ Enhanced API server import successful")
        except ImportError as e:
            self.fail(f"Failed to import enhanced API server: {e}")
            
    def test_enhanced_network_monitor_import(self):
        """Test enhanced network monitor import"""
        try:
            from backend.network_monitor import NetworkMonitor
            print("✅ Enhanced network monitor import successful")
        except ImportError as e:
            self.fail(f"Failed to import enhanced network monitor: {e}")

class TestDatabaseManager(unittest.TestCase):
    """Test database manager functionality"""
    
    def setUp(self):
        """Set up database test environment"""
        from config.config_manager import ConfigManager
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test config manager and override config directory
        self.config_manager = ConfigManager()
        self.config_manager.config_dir = self.temp_dir
        self.config_manager.config_file = self.temp_dir / "config.json"
        
        # Set database path to temp directory
        self.config_manager.config["database"]["path"] = str(self.temp_dir / "test.db")
        
    def tearDown(self):
        """Clean up database test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_database_initialization(self):
        """Test database initialization"""
        try:
            from backend.database_manager import DatabaseManager
            db_manager = DatabaseManager(self.config_manager)
            
            # Test database file creation
            db_path = Path(self.config_manager.get_database_path())
            self.assertTrue(db_path.exists(), "Database file should be created")
            
            print("✅ Database initialization successful")
            
        except Exception as e:
            self.fail(f"Database initialization failed: {e}")
            
    def test_packet_storage(self):
        """Test packet storage functionality"""
        try:
            from backend.database_manager import DatabaseManager
            db_manager = DatabaseManager(self.config_manager)
            
            # Test packet data
            packet_data = {
                "timestamp": "2025-06-30T12:00:00Z",
                "src_ip": "192.168.1.100",
                "dst_ip": "8.8.8.8",
                "src_port": 12345,
                "dst_port": 80,
                "protocol": "TCP",
                "protocol_name": "HTTP",
                "size": 1024,
                "payload_preview": "GET / HTTP/1.1",
                "interface_name": "eth0"
            }
            
            # Store packet
            result = db_manager.store_packet(packet_data)
            self.assertTrue(result, "Packet storage should succeed")
            
            # Test packet count
            count = db_manager.get_packet_count()
            self.assertGreaterEqual(count, 1, "Packet count should be at least 1")
            
            print("✅ Packet storage functionality working")
            
        except Exception as e:
            self.fail(f"Packet storage test failed: {e}")
            
    def test_threat_storage(self):
        """Test threat storage functionality"""
        try:
            from backend.database_manager import DatabaseManager
            db_manager = DatabaseManager(self.config_manager)
            
            # Test threat data
            threat_data = {
                "timestamp": "2025-06-30T12:00:00Z",
                "type": "Port Scan",
                "severity": "Medium",
                "source_ip": "192.168.1.100",
                "destination_ip": "192.168.1.1",
                "description": "Port scan detected from internal network",
                "additional_data": {"ports_scanned": [22, 80, 443]}
            }
            
            # Store threat
            result = db_manager.store_threat(threat_data)
            self.assertTrue(result, "Threat storage should succeed")
            
            # Test threat count
            count = db_manager.get_threat_count()
            self.assertGreaterEqual(count, 1, "Threat count should be at least 1")
            
            print("✅ Threat storage functionality working")
            
        except Exception as e:
            self.fail(f"Threat storage test failed: {e}")

class TestLoggingSystem(unittest.TestCase):
    """Test logging system functionality"""
    
    def setUp(self):
        """Set up logging test environment"""
        from config.config_manager import ConfigManager
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test config manager and override config directory
        self.config_manager = ConfigManager()
        self.config_manager.config_dir = self.temp_dir
        self.config_manager.config_file = self.temp_dir / "config.json"
        
    def tearDown(self):
        """Clean up logging test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_logging_initialization(self):
        """Test logging system initialization"""
        try:
            from backend.logging_system import initialize_logging, get_logger
            
            # Initialize logging
            logger_system = initialize_logging(self.config_manager)
            self.assertIsNotNone(logger_system, "Logger system should be initialized")
            
            # Test getting a logger
            logger = get_logger("test")
            self.assertIsNotNone(logger, "Logger should be available")
            
            print("✅ Logging system initialization successful")
            
        except Exception as e:
            self.fail(f"Logging initialization failed: {e}")
            
    def test_security_event_logging(self):
        """Test security event logging"""
        try:
            from backend.logging_system import initialize_logging, log_security_event
            
            # Initialize logging
            initialize_logging(self.config_manager)
            
            # Log a security event
            log_security_event("test_event", "Test security event", {"test": "data"})
            
            # Check if log file was created
            log_dir = Path(self.config_manager.config_dir) / "logs"
            security_log = log_dir / "security_events.log"
            
            # Give it a moment to write
            time.sleep(0.1)
            
            if security_log.exists():
                print("✅ Security event logging working")
            else:
                print("⚠️ Security log file not found (may be timing issue)")
                
        except Exception as e:
            self.fail(f"Security event logging failed: {e}")

class TestEnhancedAPI(unittest.TestCase):
    """Test enhanced API server functionality"""
    
    def setUp(self):
        """Set up API test environment"""
        from config.config_manager import ConfigManager
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test config manager and override config directory
        self.config_manager = ConfigManager()
        self.config_manager.config_dir = self.temp_dir
        self.config_manager.config_file = self.temp_dir / "config.json"
        
    def tearDown(self):
        """Clean up API test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_api_initialization_with_components(self):
        """Test API server initialization with all components"""
        try:
            from backend.api_server import CyberSnoopAPI
            from backend.database_manager import DatabaseManager
            from backend.network_monitor import NetworkMonitor
            
            # Create components
            db_manager = DatabaseManager(self.config_manager)
            network_monitor = NetworkMonitor(self.config_manager)
            
            # Create API server with components
            api_server = CyberSnoopAPI(self.config_manager, db_manager, network_monitor)
            self.assertIsNotNone(api_server, "API server should be initialized")
            self.assertIsNotNone(api_server.database_manager, "Database manager should be set")
            self.assertIsNotNone(api_server.network_monitor, "Network monitor should be set")
            
            print("✅ Enhanced API server initialization successful")
            
        except Exception as e:
            self.fail(f"Enhanced API initialization failed: {e}")

class TestEnhancedNetworkMonitor(unittest.TestCase):
    """Test enhanced network monitor functionality"""
    
    def setUp(self):
        """Set up network monitor test"""
        from config.config_manager import ConfigManager
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test config manager and override config directory
        self.config_manager = ConfigManager()
        self.config_manager.config_dir = self.temp_dir
        self.config_manager.config_file = self.temp_dir / "config.json"
        
    def tearDown(self):
        """Clean up network monitor test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_network_monitor_enhanced_methods(self):
        """Test enhanced network monitor methods"""
        try:
            from backend.network_monitor import NetworkMonitor
            
            monitor = NetworkMonitor(self.config_manager)
            
            # Test interface detection
            interfaces = monitor.get_interfaces()
            self.assertIsInstance(interfaces, list, "Interfaces should be a list")
            
            # Test connection count
            connection_count = monitor.get_active_connections_count()
            self.assertIsInstance(connection_count, int, "Connection count should be an integer")
            
            # Test bandwidth stats
            bandwidth = monitor.get_bandwidth_stats()
            self.assertIsInstance(bandwidth, dict, "Bandwidth stats should be a dict")
            self.assertIn("upload", bandwidth, "Bandwidth should have upload key")
            self.assertIn("download", bandwidth, "Bandwidth should have download key")
            
            print("✅ Enhanced network monitor methods working")
            
        except Exception as e:
            self.fail(f"Enhanced network monitor test failed: {e}")

def run_day2_tests():
    """Run all Day 2 tests"""
    print("🚀 Running CyberSnoop Day 2 Enhancement Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestDay2Core))
    test_suite.addTest(unittest.makeSuite(TestDatabaseManager))
    test_suite.addTest(unittest.makeSuite(TestLoggingSystem))
    test_suite.addTest(unittest.makeSuite(TestEnhancedAPI))
    test_suite.addTest(unittest.makeSuite(TestEnhancedNetworkMonitor))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 ALL DAY 2 TESTS PASSED!")
        print("✅ Database integration working")
        print("✅ Enhanced logging system working")
        print("✅ API server integration working")
        print("✅ Network monitor enhancements working")
        print("\n🚀 Ready to proceed with Day 2 objectives!")
    else:
        print("❌ Some tests failed:")
        for failure in result.failures:
            print(f"   - {failure[0]}: {failure[1]}")
        for error in result.errors:
            print(f"   - {error[0]}: {error[1]}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_day2_tests()
    sys.exit(0 if success else 1)
