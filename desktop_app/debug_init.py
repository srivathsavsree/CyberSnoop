#!/usr/bin/env python3
"""Debug initialization issues"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.advanced_threat_detector import AdvancedThreatDetector
import inspect

# Check the constructor signature
print("AdvancedThreatDetector constructor signature:")
sig = inspect.signature(AdvancedThreatDetector.__init__)
print(f"Signature: {sig}")
print(f"Parameters: {list(sig.parameters.keys())}")

# Test basic initialization
class MockConfig:
    def get(self, key, default=None):
        return default

try:
    mock_config = MockConfig()
    detector = AdvancedThreatDetector(mock_config)
    print("✓ Single argument initialization works")
except Exception as e:
    print(f"✗ Single argument initialization failed: {e}")

try:
    mock_config = MockConfig()
    detector = AdvancedThreatDetector(mock_config, None)
    print("✓ Two argument initialization works")
except Exception as e:
    print(f"✗ Two argument initialization failed: {e}")
