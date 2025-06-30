#!/usr/bin/env python3
"""
Debug script for Day 6 advanced threat detection
"""

import sys
import os
import tempfile
from unittest.mock import Mock

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from enhanced_database_manager import EnhancedDatabaseManager
from advanced_threat_detector import AdvancedThreatDetector

def debug_port_scan():
    """Debug port scan detection"""
    print("=== Debugging Port Scan Detection ===")
    
    # Create temporary database and mock config
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    mock_config = Mock()
    mock_config.get = Mock(side_effect=lambda key, default=None: {
        "database.path": temp_db.name,
        "threats.port_scan.min_ports": 5,  # Lower threshold for testing
        "threats.port_scan.time_window_minutes": 5,
        "threats.port_scan.max_targets": 10
    }.get(key, default))
    
    # Initialize components
    db_manager = EnhancedDatabaseManager(mock_config, temp_db.name)
    detector = AdvancedThreatDetector(mock_config, db_manager)
    
    print(f"Detector initialized: {detector}")
    print(f"Port scan threshold: {detector.thresholds['port_scan']}")
    
    # Create test packets - use external IPs to avoid internal traffic filter
    test_packets = []
    scanner_ip = "203.0.113.100"  # External IP
    target_ip = "198.51.100.1"   # External IP
    
    for port in range(20, 30):  # 10 ports
        packet = {
            'timestamp': 1234567890,
            'src_ip': scanner_ip,
            'dst_ip': target_ip,
            'src_port': 45000,
            'dst_port': port,
            'protocol': 'TCP',
            'packet_size': 64,
            'flags': 'SYN'
        }
        test_packets.append(packet)
        print(f"Created packet: {scanner_ip}:{45000} -> {target_ip}:{port}")
    
    # Test detection
    print(f"Testing with {len(test_packets)} packets")
    threats = detector.detect_port_scan(test_packets)
    print(f"Detected threats: {len(threats)}")
    
    for threat in threats:
        print(f"Threat: {threat}")
    
    # Debug: Check internal state
    print(f"Port scan tracking keys: {list(detector.port_scan_tracking.keys())}")
    for ip, data in detector.port_scan_tracking.items():
        print(f"  {ip}: ports={len(data['ports'])}, timestamps={len(data['timestamps'])}")
    
    # Cleanup
    db_manager.close()
    os.unlink(temp_db.name)

if __name__ == '__main__':
    debug_port_scan()
