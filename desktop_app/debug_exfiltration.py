#!/usr/bin/env python3
"""Debug data exfiltration detection"""

import sys
import os
import time
import logging
from unittest.mock import Mock

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from advanced_threat_detector import AdvancedThreatDetector

def debug_exfiltration():
    print("=== Debug Data Exfiltration Detection ===")
    
    # Create mock config
    mock_config = Mock()
    mock_config.get = Mock(side_effect=lambda key, default=None: {
        "threats.exfiltration.data_size_threshold_mb": 10,
        "threats.exfiltration.time_window_minutes": 15,
        "threats.exfiltration.size_threshold_mb": 1,    # Lower threshold for testing (1MB)
        "threats.exfiltration.upload_ratio_threshold": 5.0  # Lower ratio for testing
    }.get(key, default))
    
    # Create detector
    detector = AdvancedThreatDetector(mock_config)
    
    # Simulate packets exactly like the test
    test_packets = []
    internal_ip = "192.168.1.100"  # Clearly internal IP
    external_ip = "8.8.8.8"       # Clearly external IP (Google DNS)
    
    # Create large outbound transfer
    base_time = time.time()
    total_size = 0
    for i in range(20):
        packet_time = base_time + (i * 60)  # Spread over 19 minutes
        packet = {
            'timestamp': packet_time,  # Use current time for each packet
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
        total_size += 50000
        
        # Process packet immediately to build state
        print(f"Processing packet {i+1} at time {packet_time}...")
        threats = detector.detect_data_exfiltration([packet])
        if threats:
            print(f"  -> Threat detected: {threats}")
        else:
            print(f"  -> No threat detected yet")
    
    return  # Don't run the batch detection
    
    print(f"Test setup:")
    print(f"- Total packets: {len(test_packets)}")
    print(f"- Total size: {total_size/1024/1024:.2f} MB")
    print(f"- Time span: {(test_packets[-1]['timestamp'] - test_packets[0]['timestamp'])/60:.1f} minutes")
    print(f"- Source IP: {internal_ip}")
    print(f"- Destination IP: {external_ip}")
    
    # Check thresholds
    print(f"\nThresholds:")
    for key in ['exfiltration']:
        if key in detector.thresholds:
            print(f"- {key}: {detector.thresholds[key]}")
    
    # Test detection
    print(f"\nRunning detection...")
    threats = detector.detect_data_exfiltration(test_packets)
    
    print(f"Results:")
    print(f"- Threats detected: {len(threats)}")
    for i, threat in enumerate(threats):
        print(f"  Threat {i+1}: {threat}")
    
    # Test internal IP detection
    print(f"\nIP classification:")
    print(f"- Is {internal_ip} internal? {detector._is_internal_ip(internal_ip)}")
    print(f"- Is {external_ip} internal? {detector._is_internal_ip(external_ip)}")
    
    # Check connection states
    print(f"\nConnection states:")
    for key, state in detector.connection_states.items():
        print(f"- {key}: {state}")

if __name__ == "__main__":
    debug_exfiltration()
