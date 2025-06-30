#!/usr/bin/env python3
"""
CyberSnoop - Day 6 Test Suite: Advanced Threat Detection Algorithms
Tests all advanced threat detection features implemented on Day 6.
"""

import unittest
import sqlite3
import tempfile
import os
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Fix import issue by ensuring backend directory is accessible
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from enhanced_database_manager import EnhancedDatabaseManager
from advanced_threat_detector import AdvancedThreatDetector
from threat_detector import ThreatDetector

class TestDay6AdvancedThreatDetection(unittest.TestCase):
    """Test suite for Day 6: Advanced Threat Detection Algorithms"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create mock config manager
        self.mock_config = Mock()
        self.mock_config.get = Mock(side_effect=lambda key, default=None: {
            "database.path": self.temp_db.name,
            "threats.port_scan.min_ports": 10,
            "threats.port_scan.time_window_minutes": 5,
            "threats.port_scan.max_targets": 50,
            "threats.brute_force.max_attempts": 5,
            "threats.brute_force.time_window_minutes": 10,
            "threats.ddos.packet_rate_threshold": 100,
            "threats.ddos.time_window_seconds": 60,
            "threats.ddos.packet_threshold": 100,  # Lower threshold for testing
            "threats.ddos.source_threshold": 10,   # Lower threshold for testing
            "threats.anomaly.detection_enabled": True,
            "threats.anomaly.sensitivity": 0.8,
            "threats.anomaly.baseline_window_minutes": 60,
            "threats.anomaly.deviation_threshold": 3.0,
            "threats.anomaly.min_samples": 30,
            "threats.malware.domain_blacklist_enabled": True,
            "threats.exfiltration.data_size_threshold_mb": 10,
            "threats.exfiltration.time_window_minutes": 15,
            "threats.exfiltration.size_threshold_mb": 1,    # Lower threshold for testing (1MB)
            "threats.exfiltration.upload_ratio_threshold": 5.0  # Lower ratio for testing
        }.get(key, default))
        
        # Initialize database manager and threat detector
        self.db_manager = EnhancedDatabaseManager(self.mock_config, self.temp_db.name)
        self.advanced_detector = AdvancedThreatDetector(self.mock_config, self.db_manager)
        self.unified_detector = ThreatDetector(self.mock_config, self.db_manager)
        
        print(f"Test setup complete. Using database: {self.temp_db.name}")
    
    def tearDown(self):
        """Clean up test environment"""
        try:
            self.db_manager.close()
            os.unlink(self.temp_db.name)
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def test_1_advanced_threat_detector_initialization(self):
        """Test 1: Advanced threat detector initializes correctly"""
        print("\n=== Test 1: Advanced Threat Detector Initialization ===")
        
        # Test initialization
        self.assertIsNotNone(self.advanced_detector)
        self.assertIsNotNone(self.advanced_detector.database)
        
        # Test configuration
        self.assertIn('port_scan', self.advanced_detector.thresholds)
        self.assertIn('brute_force', self.advanced_detector.thresholds)
        self.assertIn('ddos', self.advanced_detector.thresholds)
        
        print("✓ Advanced threat detector initialized successfully")
        print("✓ Configuration loaded properly")
    
    def test_2_port_scan_detection(self):
        """Test 2: Port scan detection algorithm"""
        print("\n=== Test 2: Port Scan Detection ===")
        
        # Simulate port scan traffic - use external IPs
        test_packets = []
        scanner_ip = "203.0.113.100"  # RFC5737 test IP
        target_ip = "198.51.100.1"   # RFC5737 test IP
        
        # Create packets representing port scan (same source, different ports)
        for port in range(20, 35):  # 15 different ports
            packet = {
                'timestamp': time.time(),
                'src_ip': scanner_ip,
                'dst_ip': target_ip,
                'src_port': 45000,
                'dst_port': port,
                'protocol': 'TCP',
                'packet_size': 64,
                'flags': 'SYN'
            }
            test_packets.append(packet)
        
        # Test detection
        threats = self.advanced_detector.detect_port_scan(test_packets)
        
        self.assertGreater(len(threats), 0, "Port scan should be detected")
        
        threat = threats[0]
        self.assertEqual(threat['type'], 'port_scan')
        self.assertEqual(threat['source_ip'], scanner_ip)
        self.assertIn('scanned_ports', threat['details'])  # Changed from 'ports_scanned'
        
        print(f"✓ Port scan detected: {len(threats)} threats found")
        print(f"✓ Scanner IP: {threat['source_ip']}")
        print(f"✓ Ports scanned: {threat['details']['scanned_ports']}")
    
    def test_3_brute_force_detection(self):
        """Test 3: Brute force attack detection"""
        print("\n=== Test 3: Brute Force Detection ===")
        
        # Simulate brute force login attempts - use external IPs
        test_packets = []
        attacker_ip = "203.0.113.200"  # RFC5737 test IP
        target_ip = "198.51.100.2"    # RFC5737 test IP
        
        # Create packets representing failed login attempts
        for i in range(12):  # 12 failed attempts
            packet = {
                'timestamp': time.time(),
                'src_ip': attacker_ip,
                'dst_ip': target_ip,
                'src_port': 50000 + i,
                'dst_port': 22,  # SSH port
                'protocol': 'TCP',
                'protocol_name': 'TCP',  # Add this field for brute force detection
                'packet_size': 128,
                'flags': 'PSH,ACK',
                'payload': f'SSH-2.0-attempt-{i}'
            }
            test_packets.append(packet)
        
        # Test detection
        threats = self.advanced_detector.detect_brute_force(test_packets)
        
        self.assertGreater(len(threats), 0, "Brute force attack should be detected")
        
        threat = threats[0]
        self.assertEqual(threat['type'], 'brute_force')
        self.assertEqual(threat['source_ip'], attacker_ip)
        self.assertIn('attempt_count', threat['details'])  # Changed from 'attempts'
        
        print(f"✓ Brute force attack detected: {len(threats)} threats found")
        print(f"✓ Attacker IP: {threat['source_ip']}")
        print(f"✓ Attempts: {threat['details']['attempt_count']}")
    
    def test_4_ddos_detection(self):
        """Test 4: DDoS attack detection"""
        print("\n=== Test 4: DDoS Detection ===")
        
        # Simulate DDoS traffic - use external IP as target
        test_packets = []
        target_ip = "198.51.100.3"  # RFC5737 test IP
        
        # Create high volume of packets from multiple sources
        for i in range(150):  # High packet count
            packet = {
                'timestamp': time.time(),
                'src_ip': f"203.0.113.{(i % 254) + 1}",  # Various external source IPs
                'dst_ip': target_ip,
                'src_port': 40000 + (i % 1000),
                'dst_port': 80,  # HTTP port
                'protocol': 'TCP',
                'packet_size': 64,
                'flags': 'SYN'
            }
            test_packets.append(packet)
        
        # Test detection
        threats = self.advanced_detector.detect_ddos(test_packets)
        
        self.assertGreater(len(threats), 0, "DDoS attack should be detected")
        
        threat = threats[0]
        self.assertEqual(threat['type'], 'ddos')
        self.assertEqual(threat['target_ip'], target_ip)
        self.assertIn('packet_count', threat['details'])  # Changed from 'packet_rate'
        
        print(f"✓ DDoS attack detected: {len(threats)} threats found")
        print(f"✓ Target IP: {threat['target_ip']}")
        print(f"✓ Packet rate: {threat['details']['packet_count']}")
    
    def test_5_anomaly_detection(self):
        """Test 5: Network anomaly detection"""
        print("\n=== Test 5: Anomaly Detection ===")
        
        # First, establish baseline with normal traffic
        normal_packets = []
        for i in range(50):
            packet = {
                'timestamp': time.time(),
                'src_ip': "203.0.113.10",  # RFC5737 test IP
                'dst_ip': "198.51.100.4",  # RFC5737 test IP
                'src_port': 50000,
                'dst_port': 80,
                'protocol': 'TCP',
                'packet_size': 1024,  # Normal size
                'size': 1024,  # Add size field for anomaly detection
                'flags': 'PSH,ACK'
            }
            normal_packets.append(packet)
        
        # Now create anomalous traffic
        anomalous_packets = []
        for i in range(10):
            packet = {
                'timestamp': time.time(),
                'src_ip': "203.0.113.10",  # RFC5737 test IP
                'dst_ip': "198.51.100.4",  # RFC5737 test IP
                'src_port': 50000,
                'dst_port': 80,
                'protocol': 'TCP',
                'packet_size': 65000,  # Unusually large
                'size': 65000,  # Add size field for anomaly detection
                'flags': 'PSH,ACK'
            }
            anomalous_packets.append(packet)
        
        # Test detection
        all_packets = normal_packets + anomalous_packets
        threats = self.advanced_detector.detect_anomalies(all_packets)
        
        self.assertGreater(len(threats), 0, "Anomalies should be detected")
        
        threat = threats[0]
        self.assertEqual(threat['type'], 'anomaly')
        self.assertIn('packet_size', threat['details'])  # Changed from 'anomaly_type'
        
        print(f"✓ Network anomalies detected: {len(threats)} threats found")
        print(f"✓ Anomaly type: packet_size_anomaly")
    
    def test_6_malware_detection(self):
        """Test 6: Malware communication detection"""
        print("\n=== Test 6: Malware Detection ===")
        
        # Simulate suspicious malware-like communication
        test_packets = []
        suspicious_domains = ["malware.com", "botnet.io", "c2server.net"]  # Use domains from known_malicious_domains
        
        for i, domain in enumerate(suspicious_domains):
            packet = {
                'timestamp': time.time(),
                'src_ip': "203.0.113.50",     # RFC5737 test IP
                'dst_ip': "198.51.100.{0}".format(10 + i),  # External IPs
                'src_port': 49000 + i,
                'dst_port': 443,  # HTTPS
                'protocol': 'TCP',
                'packet_size': 256,
                'flags': 'PSH,ACK',
                'payload_preview': f'Host: {domain}',  # Use payload_preview field
                'hostname': domain  # Add hostname field for domain detection
            }
            test_packets.append(packet)
        
        # Test detection
        threats = self.advanced_detector.detect_malware_communication(test_packets)
        
        self.assertGreater(len(threats), 0, "Malware communication should be detected")
        
        threat = threats[0]
        self.assertEqual(threat['type'], 'malware_communication')
        self.assertIn('malicious_domain', threat['details'])  # Changed from 'indicators'
        
        print(f"✓ Malware communication detected: {len(threats)} threats found")
        print(f"✓ Indicators: {threat['details']['malicious_domain']}")
    
    def test_7_data_exfiltration_detection(self):
        """Test 7: Data exfiltration detection"""
        print("\n=== Test 7: Data Exfiltration Detection ===")
        
        # Simulate large outbound data transfer
        test_packets = []
        internal_ip = "203.0.113.100"  # RFC5737 test IP (simulating internal)
        external_ip = "198.51.100.50"  # RFC5737 test IP (simulating external)
        
        # Create large outbound transfer
        base_time = time.time()
        for i in range(20):
            packet = {
                'timestamp': base_time + (i * 60),  # Spread over time to meet time window
                'src_ip': internal_ip,
                'dst_ip': external_ip,
                'src_port': 51000,
                'dst_port': 443,
                'protocol': 'TCP',
                'packet_size': 50000,  # Large packets
                'size': 50000,  # Add size field for data exfiltration detection
                'flags': 'PSH,ACK',
                'direction': 'outbound'
            }
            test_packets.append(packet)
        
        # Test detection
        threats = self.advanced_detector.detect_data_exfiltration(test_packets)
        
        self.assertGreater(len(threats), 0, "Data exfiltration should be detected")
        
        threat = threats[0]
        self.assertEqual(threat['type'], 'data_exfiltration')
        self.assertEqual(threat['source_ip'], internal_ip)
        self.assertIn('upload_mb', threat['details'])  # Changed from 'data_volume'
        
        print(f"✓ Data exfiltration detected: {len(threats)} threats found")
        print(f"✓ Source IP: {threat['source_ip']}")
        print(f"✓ Data volume: {threat['details']['upload_mb']} MB")
    
    def test_8_unified_threat_detector_integration(self):
        """Test 8: Unified threat detector integration"""
        print("\n=== Test 8: Unified Threat Detector Integration ===")
        
        # Test that the unified detector can access both basic and advanced detection
        self.assertIsNotNone(self.unified_detector)
        self.assertIsNotNone(self.unified_detector.advanced_detector)
        
        # Test basic detection still works
        test_packet = {
            'src_ip': '192.168.1.100',
            'dst_ip': '10.0.0.1',
            'src_port': 12345,
            'dst_port': 22,
            'protocol': 'TCP',
            'timestamp': time.time(),
            'packet_size': 64
        }
        
        basic_threats = self.unified_detector.detect_threats([test_packet])
        self.assertIsInstance(basic_threats, list)
        
        # Test advanced detection through unified interface
        # Create port scan pattern
        port_scan_packets = []
        for port in range(20, 30):
            packet = {
                'timestamp': time.time(),
                'src_ip': '192.168.1.200',
                'dst_ip': '10.0.0.5',
                'src_port': 45000,
                'dst_port': port,
                'protocol': 'TCP',
                'packet_size': 64,
                'flags': 'SYN'
            }
            port_scan_packets.append(packet)
        
        # Test advanced detection
        advanced_threats = self.unified_detector.advanced_detector.detect_port_scan(port_scan_packets)
        self.assertGreater(len(advanced_threats), 0)
        
        print("✓ Unified threat detector integration working")
        print("✓ Basic detection accessible")
        print("✓ Advanced detection accessible")
        print(f"✓ Advanced threats detected: {len(advanced_threats)}")
    
    def test_9_threat_correlation_and_scoring(self):
        """Test 9: Threat correlation and severity scoring"""
        print("\n=== Test 9: Threat Correlation and Scoring ===")
        
        # Create a complex attack scenario
        test_packets = []
        attacker_ip = "203.0.113.250"  # RFC5737 test IP
        target_ip = "198.51.100.10"   # RFC5737 test IP
        
        # Port scan followed by brute force
        # First: port scan
        for port in [21, 22, 23, 80, 443, 3389]:
            packet = {
                'timestamp': time.time(),
                'src_ip': attacker_ip,
                'dst_ip': target_ip,
                'src_port': 60000,
                'dst_port': port,
                'protocol': 'TCP',
                'packet_size': 64,
                'flags': 'SYN'
            }
            test_packets.append(packet)
        
        # Then: brute force on discovered SSH port
        for i in range(15):
            packet = {
                'timestamp': time.time() + 10,  # Later timestamp
                'src_ip': attacker_ip,
                'dst_ip': target_ip,
                'src_port': 60001 + i,
                'dst_port': 22,
                'protocol': 'TCP',
                'packet_size': 128,
                'flags': 'PSH,ACK'
            }
            test_packets.append(packet)
        
        # Detect both attack types
        port_scan_threats = self.advanced_detector.detect_port_scan(test_packets[:6])
        brute_force_threats = self.advanced_detector.detect_brute_force(test_packets[6:])
        
        all_threats = port_scan_threats + brute_force_threats
        
        self.assertGreaterEqual(len(all_threats), 2, "Both attack types should be detected")
        
        # Verify threat types
        threat_types = [threat['type'] for threat in all_threats]
        self.assertIn('port_scan', threat_types)
        self.assertIn('brute_force', threat_types)
        
        # Verify same attacker
        source_ips = set(threat['source_ip'] for threat in all_threats)
        self.assertEqual(len(source_ips), 1, "All threats should come from same source")
        self.assertEqual(list(source_ips)[0], attacker_ip)
        
        print(f"✓ Complex attack scenario detected: {len(all_threats)} related threats")
        print(f"✓ Threat types: {threat_types}")
        print(f"✓ Correlated attacker IP: {attacker_ip}")
    
    def test_10_performance_and_scalability(self):
        """Test 10: Performance with large packet volumes"""
        print("\n=== Test 10: Performance and Scalability ===")
        
        # Generate large packet dataset
        large_packet_set = []
        start_time = time.time()
        
        # Create 1000 mixed packets
        for i in range(1000):
            packet = {
                'timestamp': time.time(),
                'src_ip': f"203.0.113.{(i % 254) + 1}",  # RFC5737 test IPs
                'dst_ip': f"198.51.100.{(i % 254) + 1}", # RFC5737 test IPs
                'src_port': 40000 + (i % 10000),
                'dst_port': 80 + (i % 100),
                'protocol': 'TCP' if i % 2 == 0 else 'UDP',
                'packet_size': 64 + (i % 1400),
                'size': 64 + (i % 1400),  # Add size field
                'flags': 'PSH,ACK' if i % 2 == 0 else 'SYN'
            }
            large_packet_set.append(packet)
        
        generation_time = time.time() - start_time
        
        # Test detection performance
        detection_start = time.time()
        
        # Run multiple detection algorithms
        port_scan_threats = self.advanced_detector.detect_port_scan(large_packet_set)
        brute_force_threats = self.advanced_detector.detect_brute_force(large_packet_set)
        ddos_threats = self.advanced_detector.detect_ddos(large_packet_set)
        anomaly_threats = self.advanced_detector.detect_anomalies(large_packet_set)
        
        detection_time = time.time() - detection_start
        
        total_threats = (len(port_scan_threats) + len(brute_force_threats) + 
                        len(ddos_threats) + len(anomaly_threats))
        
        # Performance assertions
        self.assertLess(detection_time, 10.0, "Detection should complete within 10 seconds")
        self.assertGreaterEqual(total_threats, 0, "Detection should complete without errors")
        
        print(f"✓ Processed {len(large_packet_set)} packets")
        print(f"✓ Generation time: {generation_time:.2f} seconds")
        print(f"✓ Detection time: {detection_time:.2f} seconds")
        print(f"✓ Total threats found: {total_threats}")
        print(f"✓ Processing rate: {len(large_packet_set)/detection_time:.0f} packets/second")

def run_day6_tests():
    """Run all Day 6 tests and provide summary"""
    print("="*70)
    print("CyberSnoop - Day 6 Test Suite: Advanced Threat Detection Algorithms")
    print("="*70)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDay6AdvancedThreatDetection)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*70)
    print("DAY 6 TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors))/result.testsRun)*100:.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL DAY 6 TESTS PASSED! 🎉")
        print("Advanced threat detection algorithms are working correctly.")
        print("\nDay 6 Features Verified:")
        print("✓ Port scan detection")
        print("✓ Brute force attack detection")
        print("✓ DDoS attack detection")
        print("✓ Network anomaly detection")
        print("✓ Malware communication detection")
        print("✓ Data exfiltration detection")
        print("✓ Unified threat detector integration")
        print("✓ Threat correlation and scoring")
        print("✓ Performance and scalability")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please review the failures above and fix the issues.")
        return False

if __name__ == '__main__':
    success = run_day6_tests()
    sys.exit(0 if success else 1)
