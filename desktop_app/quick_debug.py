#!/usr/bin/env python3
"""Quick debug for remaining test failures"""

import sys
import os
import time
from unittest.mock import Mock

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from advanced_threat_detector import AdvancedThreatDetector

def test_data_exfiltration_simple():
    print("=== Quick Data Exfiltration Test ===")
    
    # Create mock config
    mock_config = Mock()
    mock_config.get = Mock(side_effect=lambda key, default=None: {
        "threats.exfiltration.size_threshold_mb": 1,
        "threats.exfiltration.upload_ratio_threshold": 5.0,
        "threats.exfiltration.time_window": 15
    }.get(key, default))
    
    # Create detector
    detector = AdvancedThreatDetector(mock_config)
    
    # Create simple test case - single large packet
    packet = {
        'timestamp': time.time(),
        'src_ip': "192.168.1.100",  # Internal
        'dst_ip': "8.8.8.8",        # External  
        'size': 2048 * 1024,        # 2MB - well above threshold
        'direction': 'outbound'
    }
    
    print(f"Testing with single 2MB packet...")
    threats = detector.detect_data_exfiltration([packet])
    print(f"Threats detected: {len(threats)}")
    
    if threats:
        print(f"Threat: {threats[0]}")
    else:
        print("No threats detected")
        # Check connection state
        for key, state in detector.connection_states.items():
            print(f"Connection {key}: {state}")

def test_port_scan_simple():
    print("\n=== Quick Port Scan Test ===")
    
    # Create mock config  
    mock_config = Mock()
    mock_config.get = Mock(side_effect=lambda key, default=None: {
        "threats.port_scan.min_ports": 5,
        "threats.port_scan.time_window_minutes": 5
    }.get(key, default))
    
    # Create detector
    detector = AdvancedThreatDetector(mock_config)
    
    # Create port scan packets
    packets = []
    for port in range(20, 30):  # 10 ports
        packet = {
            'timestamp': time.time(),
            'src_ip': "203.0.113.200",
            'dst_ip': "198.51.100.10", 
            'src_port': 45000,
            'dst_port': port,
            'protocol': 'TCP',
            'flags': 'SYN'
        }
        packets.append(packet)
    
    print(f"Testing port scan with {len(packets)} packets...")
    threats = detector.detect_port_scan(packets)
    print(f"Threats detected: {len(threats)}")
    
    if threats:
        print(f"Threat: {threats[0]}")

if __name__ == "__main__":
    test_data_exfiltration_simple()
    test_port_scan_simple()
