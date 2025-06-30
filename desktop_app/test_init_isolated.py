#!/usr/bin/env python3
"""Isolate the initialization issue"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Fix import issue by ensuring backend directory is accessible
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from enhanced_database_manager import EnhancedDatabaseManager
from advanced_threat_detector import AdvancedThreatDetector
from threat_detector import ThreatDetector

class MockConfig:
    def get(self, key, default=None):
        return {
            "threats.port_scan_threshold": 5,
            "threats.brute_force_threshold": 3,
            "threats.ddos_packet_threshold": 50,
            "threats.time_window_minutes": 1,
            "threats.data_upload_threshold_mb": 1,
            "threats.anomaly.detection_enabled": True,
            "threats.anomaly.sensitivity": 0.8,
            "threats.anomaly.baseline_window_minutes": 60,
            "threats.anomaly.deviation_threshold": 3.0,
            "threats.anomaly.min_samples": 30,
            "threats.malware.domain_blacklist_enabled": True,
            "threats.exfiltration.data_size_threshold_mb": 10,
            "threats.exfiltration.time_window_minutes": 15,
            "threats.exfiltration.size_threshold_mb": 1,    
            "threats.exfiltration.upload_ratio_threshold": 5.0  
        }.get(key, default)

print("Testing initialization...")

# Test 1: Advanced detector directly
try:
    config = MockConfig()
    print("Creating advanced detector...")
    advanced_detector = AdvancedThreatDetector(config)
    print("✓ Advanced detector created successfully")
except Exception as e:
    print(f"✗ Advanced detector creation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: With database manager
try:
    import tempfile
    config = MockConfig()
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    print("Creating database manager...")
    db_manager = EnhancedDatabaseManager(config, temp_db.name)
    print("✓ Database manager created")
    
    print("Creating advanced detector with database...")
    advanced_detector = AdvancedThreatDetector(config, db_manager)
    print("✓ Advanced detector with database created successfully")
    
    os.unlink(temp_db.name)
except Exception as e:
    print(f"✗ Advanced detector with database creation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Unified detector
try:
    config = MockConfig()
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    print("Creating unified detector...")
    db_manager = EnhancedDatabaseManager(config, temp_db.name)
    unified_detector = ThreatDetector(config, db_manager)
    print("✓ Unified detector created successfully")
    print(f"Advanced detector available: {unified_detector.use_advanced}")
    print(f"Advanced detector object: {unified_detector.advanced_detector}")
    
    os.unlink(temp_db.name)
except Exception as e:
    print(f"✗ Unified detector creation failed: {e}")
    import traceback
    traceback.print_exc()
