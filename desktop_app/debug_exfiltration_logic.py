#!/usr/bin/env python3
"""Debug data exfiltration step by step"""

import sys
import os
import time
from datetime import datetime
from unittest.mock import Mock

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from advanced_threat_detector import AdvancedThreatDetector

def debug_data_exfiltration_logic():
    print("=== Debug Data Exfiltration Logic ===")
    
    # Create mock config
    mock_config = Mock()
    mock_config.get = Mock(side_effect=lambda key, default=None: {
        "threats.exfiltration.size_threshold_mb": 1,
        "threats.exfiltration.upload_ratio_threshold": 2.0,
        "threats.exfiltration.time_window": 15
    }.get(key, default))
    
    # Create detector
    detector = AdvancedThreatDetector(mock_config)
    
    print(f"Thresholds: {detector.thresholds['exfiltration']}")
    
    # Create test packet  
    packet = {
        'timestamp': time.time(),
        'src_ip': "192.168.1.100",  # Internal
        'dst_ip': "8.8.8.8",        # External  
        'size': 2048 * 1024,        # 2MB
        'direction': 'outbound'
    }
    
    print(f"Processing packet: size={packet['size']} bytes ({packet['size']/1024/1024:.2f} MB)")
    
    # Process packet
    threats = detector.detect_data_exfiltration([packet])
    
    # Check connection state
    key = f"{packet['src_ip']}:{packet['dst_ip']}"
    if key in detector.connection_states:
        state = detector.connection_states[key]
        upload_mb = state["upload_bytes"] / (1024 * 1024)
        download_mb = state["download_bytes"] / (1024 * 1024)
        upload_ratio = upload_mb / max(download_mb, 1)
        
        print(f"Connection state:")
        print(f"  Upload: {upload_mb:.2f} MB")
        print(f"  Download: {download_mb:.2f} MB") 
        print(f"  Ratio: {upload_ratio:.2f}")
        print(f"  Start time: {state['start_time']}")
        print(f"  Last activity: {state['last_activity']}")
        
        # Check time window
        current_time = datetime.fromtimestamp(packet['timestamp'])
        time_elapsed_minutes = (current_time - state["start_time"]).seconds / 60
        print(f"  Time elapsed: {time_elapsed_minutes:.2f} minutes")
        
        # Check thresholds
        size_check = upload_mb >= detector.thresholds["exfiltration"]["size_threshold_mb"]
        ratio_check = upload_ratio >= detector.thresholds["exfiltration"]["upload_ratio_threshold"]
        time_check = time_elapsed_minutes >= detector.thresholds["exfiltration"]["time_window"]
        size_trigger = state["upload_bytes"] >= detector.thresholds["exfiltration"]["size_threshold_mb"] * 1024 * 1024
        
        print(f"Checks:")
        print(f"  Size >= {detector.thresholds['exfiltration']['size_threshold_mb']} MB: {size_check}")
        print(f"  Ratio >= {detector.thresholds['exfiltration']['upload_ratio_threshold']}: {ratio_check}")
        print(f"  Time >= {detector.thresholds['exfiltration']['time_window']} min: {time_check}")
        print(f"  Size trigger: {size_trigger}")
        print(f"  Should check: {time_check or size_trigger}")
        
        if size_check and ratio_check and (time_check or size_trigger):
            print("❌ All conditions met but no threat detected - bug in logic!")
        else:
            print("ℹ️  Conditions not met, no detection expected")
    
    print(f"Threats detected: {len(threats)}")

if __name__ == "__main__":
    debug_data_exfiltration_logic()
