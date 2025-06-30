#!/usr/bin/env python3
"""
Day 5 Testing Suite for CyberSnoop Desktop Application
Testing enhanced database integration with SQLAlchemy ORM

This test suite validates:
1. Enhanced database manager initialization
2. SQLAlchemy ORM integration
3. Advanced packet and threat storage
4. Data retention and cleanup
5. Performance monitoring
6. Migration system (placeholder)
7. Database statistics and analytics
"""

import unittest
import sys
import os
import tempfile
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config.config_manager import ConfigManager
    from backend.enhanced_database_manager import EnhancedDatabaseManager, SQLALCHEMY_AVAILABLE
    from backend.enhanced_database_manager import PacketRecord, ThreatRecord, NetworkInterface, SystemMetrics
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class TestDay5EnhancedDatabase(unittest.TestCase):
    """Test suite for Day 5 enhanced database functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_cybersnoop.db")
        
        # Create a test config manager
        self.config = ConfigManager()
        self.config.set("database.path", self.db_path)
        self.config.set("database.retention_days", 7)
        self.config.set("database.cleanup_interval_hours", 1)
        
        # Create enhanced database manager
        self.db_manager = EnhancedDatabaseManager(self.config, self.db_path)
        
        print(f"Test database: {self.db_path}")
        print(f"SQLAlchemy available: {SQLALCHEMY_AVAILABLE}")
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_01_database_initialization(self):
        """Test database initialization with both SQLAlchemy and basic SQLite"""
        print("\n🧪 Testing database initialization...")
        
        # Check database file exists
        self.assertTrue(os.path.exists(self.db_path))
        
        # Check database info
        db_info = self.db_manager.get_database_info()
        self.assertIn("database_path", db_info)
        self.assertIn("engine_type", db_info)
        self.assertIn("retention_days", db_info)
        self.assertIn("query_stats", db_info)
        
        self.assertEqual(db_info["database_path"], self.db_path)
        self.assertEqual(db_info["retention_days"], 7)
        
        print(f"✅ Database initialized: {db_info['engine_type']}")
    
    def test_02_packet_storage_sqlalchemy(self):
        """Test packet storage using SQLAlchemy (if available)"""
        print("\n🧪 Testing packet storage with SQLAlchemy...")
        
        if not SQLALCHEMY_AVAILABLE:
            print("⚠️ SQLAlchemy not available, skipping SQLAlchemy-specific tests")
            return
        
        # Test packet data
        packet_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "src_ip": "192.168.1.100",
            "dst_ip": "8.8.8.8",
            "src_port": 52341,
            "dst_port": 443,
            "protocol_name": "TCP",
            "size": 1024,
            "category": "web_traffic",
            "priority": 1,
            "threat_indicators": ["encrypted", "https"],
            "additional_data": {"user_agent": "Mozilla/5.0"}
        }
        
        # Store packet
        result = self.db_manager.store_packet(packet_data)
        self.assertTrue(result)
        
        # Verify storage using SQLAlchemy session
        session = self.db_manager.get_session()
        try:
            packet = session.query(PacketRecord).filter_by(src_ip="192.168.1.100").first()
            self.assertIsNotNone(packet)
            self.assertEqual(packet.dst_ip, "8.8.8.8")
            self.assertEqual(packet.src_port, 52341)
            self.assertEqual(packet.dst_port, 443)
            self.assertEqual(packet.protocol, "TCP")
            self.assertEqual(packet.category, "web_traffic")
            self.assertEqual(packet.priority, 1)
        finally:
            session.close()
        
        print("✅ Packet storage with SQLAlchemy successful")
    
    def test_03_threat_storage_sqlalchemy(self):
        """Test threat storage using SQLAlchemy (if available)"""
        print("\n🧪 Testing threat storage with SQLAlchemy...")
        
        if not SQLALCHEMY_AVAILABLE:
            print("⚠️ SQLAlchemy not available, skipping SQLAlchemy-specific tests")
            return
        
        # Test threat data
        threat_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "port_scan",
            "severity": "high",
            "source_ip": "192.168.1.200",
            "destination_ip": "192.168.1.1",
            "description": "Suspicious port scanning activity detected",
            "indicators": ["multiple_ports", "rapid_connections"]
        }
        
        # Store threat
        result = self.db_manager.store_threat(threat_data)
        self.assertTrue(result)
        
        # Verify storage using SQLAlchemy session
        session = self.db_manager.get_session()
        try:
            threat = session.query(ThreatRecord).filter_by(source_ip="192.168.1.200").first()
            self.assertIsNotNone(threat)
            self.assertEqual(threat.threat_type, "port_scan")
            self.assertEqual(threat.severity, "high")
            self.assertEqual(threat.description, "Suspicious port scanning activity detected")
        finally:
            session.close()
        
        print("✅ Threat storage with SQLAlchemy successful")
    
    def test_04_basic_sqlite_fallback(self):
        """Test basic SQLite fallback functionality"""
        print("\n🧪 Testing basic SQLite fallback...")
        
        # Create a new database manager without SQLAlchemy
        original_available = SQLALCHEMY_AVAILABLE
        
        try:
            # Simulate SQLAlchemy not available
            import backend.enhanced_database_manager as edb
            edb.SQLALCHEMY_AVAILABLE = False
            
            # Create new database manager
            fallback_db_path = os.path.join(self.test_dir, "fallback_test.db")
            fallback_db = EnhancedDatabaseManager(self.config, fallback_db_path)
            
            # Test packet storage
            packet_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "src_ip": "10.0.0.1",
                "dst_ip": "10.0.0.2",
                "src_port": 80,
                "dst_port": 8080,
                "protocol_name": "HTTP",
                "size": 512,
                "category": "web_traffic",
                "priority": 2
            }
            
            result = fallback_db.store_packet(packet_data)
            self.assertTrue(result)
            
            # Test threat storage
            threat_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "malware",
                "severity": "critical",
                "source_ip": "10.0.0.3",
                "description": "Malware detected in network traffic"
            }
            
            result = fallback_db.store_threat(threat_data)
            self.assertTrue(result)
            
            # Clean up
            fallback_db.close()
            
        finally:
            # Restore original SQLAlchemy availability
            edb.SQLALCHEMY_AVAILABLE = original_available
        
        print("✅ Basic SQLite fallback working correctly")
    
    def test_05_packet_statistics(self):
        """Test packet statistics functionality"""
        print("\n🧪 Testing packet statistics...")
        
        # Store multiple packets with different categories
        test_packets = [
            {"src_ip": "192.168.1.10", "dst_ip": "8.8.8.8", "category": "dns", "priority": 1},
            {"src_ip": "192.168.1.11", "dst_ip": "1.1.1.1", "category": "dns", "priority": 1},
            {"src_ip": "192.168.1.12", "dst_ip": "google.com", "category": "web_traffic", "priority": 2},
            {"src_ip": "192.168.1.13", "dst_ip": "facebook.com", "category": "social_media", "priority": 3},
            {"src_ip": "192.168.1.14", "dst_ip": "suspicious.com", "category": "malware", "priority": 5}
        ]
        
        for packet in test_packets:
            packet["timestamp"] = datetime.utcnow().isoformat()
            packet["protocol_name"] = "TCP"
            packet["size"] = 1024
            result = self.db_manager.store_packet(packet)
            self.assertTrue(result)
        
        # Get statistics
        stats = self.db_manager.get_packet_statistics(hours=24)
        
        self.assertIn("total_packets", stats)
        self.assertIn("category_breakdown", stats)
        self.assertIn("time_period_hours", stats)
        
        # Verify statistics
        self.assertGreaterEqual(stats["total_packets"], 5)
        self.assertEqual(stats["time_period_hours"], 24)
        
        # Check category breakdown
        category_breakdown = stats["category_breakdown"]
        self.assertIn("dns", category_breakdown)
        self.assertIn("web_traffic", category_breakdown)
        self.assertEqual(category_breakdown["dns"], 2)
        self.assertEqual(category_breakdown["web_traffic"], 1)
        
        print("✅ Packet statistics working correctly")
    
    def test_06_data_retention_cleanup(self):
        """Test data retention and cleanup functionality"""
        print("\n🧪 Testing data retention and cleanup...")
        
        # Store old packets (simulate old data)
        old_timestamp = (datetime.utcnow() - timedelta(days=10)).isoformat()
        recent_timestamp = datetime.utcnow().isoformat()
        
        # Store old packet
        old_packet = {
            "timestamp": old_timestamp,
            "src_ip": "192.168.1.100",
            "dst_ip": "old.example.com",
            "protocol_name": "TCP",
            "category": "old_traffic",
            "priority": 1,
            "size": 512
        }
        
        # Store recent packet
        recent_packet = {
            "timestamp": recent_timestamp,
            "src_ip": "192.168.1.101",
            "dst_ip": "recent.example.com",
            "protocol_name": "TCP",
            "category": "recent_traffic",
            "priority": 1,
            "size": 512
        }
        
        self.assertTrue(self.db_manager.store_packet(old_packet))
        self.assertTrue(self.db_manager.store_packet(recent_packet))
        
        # Run cleanup (should remove old data)
        deleted_counts = self.db_manager.cleanup_old_data()
        
        self.assertIn("packets", deleted_counts)
        self.assertIn("threats", deleted_counts)
        self.assertGreaterEqual(deleted_counts["packets"], 1)
        
        print(f"✅ Data cleanup successful: {deleted_counts}")
    
    def test_07_performance_monitoring(self):
        """Test performance monitoring and query statistics"""
        print("\n🧪 Testing performance monitoring...")
        
        # Perform several operations to generate statistics
        for i in range(10):
            packet_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "src_ip": f"192.168.1.{i}",
                "dst_ip": "8.8.8.8",
                "protocol_name": "TCP",
                "category": "test_traffic",
                "priority": 1,
                "size": 1024
            }
            self.db_manager.store_packet(packet_data)
        
        # Get database info with performance stats
        db_info = self.db_manager.get_database_info()
        query_stats = db_info["query_stats"]
        
        self.assertIn("total_queries", query_stats)
        self.assertIn("avg_query_time", query_stats)
        self.assertIn("slow_queries", query_stats)
        
        self.assertGreater(query_stats["total_queries"], 0)
        self.assertGreaterEqual(query_stats["avg_query_time"], 0)
        self.assertGreaterEqual(query_stats["slow_queries"], 0)
        
        print(f"✅ Performance monitoring working: {query_stats}")
    
    def test_08_advanced_orm_features(self):
        """Test advanced ORM features (if SQLAlchemy available)"""
        print("\n🧪 Testing advanced ORM features...")
        
        if not SQLALCHEMY_AVAILABLE:
            print("⚠️ SQLAlchemy not available, skipping ORM-specific tests")
            return
        
        session = self.db_manager.get_session()
        
        try:
            # Test relationships between packets and threats
            packet = PacketRecord(
                timestamp=datetime.utcnow(),
                src_ip="192.168.1.50",
                dst_ip="malicious.com",
                protocol="TCP",
                category="malware",
                priority=5
            )
            
            session.add(packet)
            session.commit()
            
            # Add related threat
            threat = ThreatRecord(
                timestamp=datetime.utcnow(),
                threat_type="malware_communication",
                severity="critical",
                source_ip="192.168.1.50",
                description="Communication with known malicious domain",
                packet_id=packet.id
            )
            
            session.add(threat)
            session.commit()
            
            # Test relationship
            retrieved_packet = session.query(PacketRecord).filter_by(src_ip="192.168.1.50").first()
            self.assertIsNotNone(retrieved_packet)
            self.assertEqual(len(retrieved_packet.threats), 1)
            self.assertEqual(retrieved_packet.threats[0].threat_type, "malware_communication")
            
            # Test reverse relationship
            retrieved_threat = session.query(ThreatRecord).filter_by(threat_type="malware_communication").first()
            self.assertIsNotNone(retrieved_threat)
            self.assertIsNotNone(retrieved_threat.packet)
            self.assertEqual(retrieved_threat.packet.src_ip, "192.168.1.50")
            
        finally:
            session.close()
        
        print("✅ Advanced ORM features working correctly")
    
    def test_09_network_interface_tracking(self):
        """Test network interface tracking (if SQLAlchemy available)"""
        print("\n🧪 Testing network interface tracking...")
        
        if not SQLALCHEMY_AVAILABLE:
            print("⚠️ SQLAlchemy not available, skipping interface tracking tests")
            return
        
        session = self.db_manager.get_session()
        
        try:
            # Add network interface
            interface = NetworkInterface(
                name="Ethernet0",
                description="Intel Ethernet Connection",
                ip_address="192.168.1.100",
                mac_address="00:11:22:33:44:55",
                status="active",
                speed="1000 Mbps",
                media_type="Ethernet"
            )
            
            session.add(interface)
            session.commit()
            
            # Retrieve and verify
            retrieved_interface = session.query(NetworkInterface).filter_by(name="Ethernet0").first()
            self.assertIsNotNone(retrieved_interface)
            self.assertEqual(retrieved_interface.ip_address, "192.168.1.100")
            self.assertEqual(retrieved_interface.mac_address, "00:11:22:33:44:55")
            self.assertEqual(retrieved_interface.status, "active")
            
        finally:
            session.close()
        
        print("✅ Network interface tracking working correctly")
    
    def test_10_system_metrics_storage(self):
        """Test system metrics storage (if SQLAlchemy available)"""
        print("\n🧪 Testing system metrics storage...")
        
        if not SQLALCHEMY_AVAILABLE:
            print("⚠️ SQLAlchemy not available, skipping metrics storage tests")
            return
        
        session = self.db_manager.get_session()
        
        try:
            # Add system metrics
            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=45.2,
                memory_usage=68.7,
                packet_processing_rate=1500.0,
                avg_processing_time=0.002,
                active_connections=25,
                bytes_sent=1024000,
                bytes_received=2048000
            )
            
            session.add(metrics)
            session.commit()
            
            # Retrieve and verify
            retrieved_metrics = session.query(SystemMetrics).order_by(
                SystemMetrics.timestamp.desc()
            ).first()
            
            self.assertIsNotNone(retrieved_metrics)
            self.assertEqual(retrieved_metrics.cpu_usage, 45.2)
            self.assertEqual(retrieved_metrics.memory_usage, 68.7)
            self.assertEqual(retrieved_metrics.packet_processing_rate, 1500.0)
            self.assertEqual(retrieved_metrics.active_connections, 25)
            
        finally:
            session.close()
        
        print("✅ System metrics storage working correctly")

def run_day5_tests():
    """Run all Day 5 tests"""
    print("=" * 80)
    print("🚀 CYBERSNOOP DAY 5 TESTING SUITE")
    print("Testing Enhanced Database Integration with SQLAlchemy ORM")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDay5EnhancedDatabase)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True
    )
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print("🎉 ALL DAY 5 TESTS PASSED!")
        print(f"✅ {result.testsRun} tests completed successfully")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"Failed: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    print("=" * 80)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_day5_tests()
    sys.exit(0 if success else 1)
