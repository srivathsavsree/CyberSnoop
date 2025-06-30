#!/usr/bin/env python3
"""Run just test 7 to debug data exfiltration"""

import unittest
import sys
import os
import time
import tempfile
from unittest.mock import Mock

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from advanced_threat_detector import AdvancedThreatDetector
from enhanced_database_manager import EnhancedDatabaseManager

class TestDataExfiltration(unittest.TestCase):
    
    def setUp(self):
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create mock config manager with the same settings as the main test
        self.mock_config = Mock()
        self.mock_config.get = Mock(side_effect=lambda key, default=None: {
            "threats.exfiltration.size_threshold_mb": 1,
            "threats.exfiltration.upload_ratio_threshold": 2.0,  # Same as updated test
            "threats.exfiltration.time_window": 15
        }.get(key, default))
        
        # Initialize database manager and detector
        self.db_manager = EnhancedDatabaseManager(self.mock_config, self.temp_db.name)
        self.advanced_detector = AdvancedThreatDetector(self.mock_config, self.db_manager)
    
    def tearDown(self):
        try:
            self.db_manager.close()
            os.unlink(self.temp_db.name)
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def test_data_exfiltration_detection(self):
        """Test data exfiltration detection - exact copy from main test"""
        print("\n=== Test 7: Data Exfiltration Detection (Isolated) ===")
        
        # Simulate large outbound data transfer (exact copy from test)
        test_packets = []
        internal_ip = "192.168.1.100"  # Clearly internal IP
        external_ip = "8.8.8.8"       # Clearly external IP (Google DNS)
        
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
                'packet_size': 60000,  # Larger packets to exceed 1MB threshold
                'size': 60000,  # Add size field for data exfiltration detection
                'flags': 'PSH,ACK',
                'direction': 'outbound'
            }
            test_packets.append(packet)
        
        print(f"Created {len(test_packets)} packets")
        print(f"Total size: {sum(p['size'] for p in test_packets) / 1024 / 1024:.2f} MB")
        print(f"Time span: {(test_packets[-1]['timestamp'] - test_packets[0]['timestamp']) / 60:.1f} minutes")
        
        # Test detection
        threats = self.advanced_detector.detect_data_exfiltration(test_packets)
        
        print(f"Threats detected: {len(threats)}")
        if threats:
            for i, threat in enumerate(threats):
                print(f"  Threat {i+1}: {threat}")
        
        # Check connection states for debug
        for key, state in self.advanced_detector.connection_states.items():
            upload_mb = state["upload_bytes"] / (1024 * 1024)
            download_mb = state["download_bytes"] / (1024 * 1024)
            print(f"Connection {key}: {upload_mb:.2f}MB up, {download_mb:.2f}MB down")
        
        self.assertGreater(len(threats), 0, "Data exfiltration should be detected")

if __name__ == '__main__':
    unittest.main(verbosity=2)
