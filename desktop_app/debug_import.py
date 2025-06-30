#!/usr/bin/env python3
"""Debug import issue"""

import sys
import os
import inspect

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

print("=== Testing imports ===")

# Import directly
try:
    from advanced_threat_detector import AdvancedThreatDetector as DirectAdvanced
    print("✓ Direct import successful")
    print(f"Direct class: {DirectAdvanced}")
    print(f"Direct __init__ signature: {inspect.signature(DirectAdvanced.__init__)}")
except Exception as e:
    print(f"✗ Direct import failed: {e}")

# Import through threat_detector
try:
    from threat_detector import ThreatDetector
    print("✓ ThreatDetector import successful")
    
    # Check what AdvancedThreatDetector is being imported
    import threat_detector
    if hasattr(threat_detector, 'AdvancedThreatDetector'):
        ImportedAdvanced = threat_detector.AdvancedThreatDetector
        print(f"Imported class: {ImportedAdvanced}")
        print(f"Imported __init__ signature: {inspect.signature(ImportedAdvanced.__init__)}")
        print(f"Same class? {DirectAdvanced is ImportedAdvanced}")
    else:
        print("AdvancedThreatDetector not found in threat_detector module")
        
except Exception as e:
    print(f"✗ ThreatDetector import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Checking for any __new__ methods ===")
try:
    if hasattr(DirectAdvanced, '__new__'):
        print(f"DirectAdvanced.__new__ signature: {inspect.signature(DirectAdvanced.__new__)}")
    else:
        print("No __new__ method found")
except Exception as e:
    print(f"Error checking __new__: {e}")
