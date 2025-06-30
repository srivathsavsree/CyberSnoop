#!/usr/bin/env python3
"""
Day 4 Test Suite for CyberSnoop (Windows Compatible)
Tests for advanced packet filtering, categorization, and performance optimization.
"""

import unittest
import sys
import os
import time
import threading
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestDay4Basic(unittest.TestCase):
    """Basic test cases for Day 4 functionality"""
    
    def setUp(self):
        """Set up test environment"""
        from config.config_manager import ConfigManager
        self.config = ConfigManager()
        
    def test_packet_filter_import(self):
        """Test packet filter module import"""
        try:
            from backend.packet_filter import AdvancedPacketFilter, PacketCategory, PacketPriority
            print("PASS: Packet filter module imported successfully")
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import packet filter: {e}")
    
    def test_network_monitor_import(self):
        """Test enhanced network monitor import"""
        try:
            from backend.network_monitor import NetworkMonitor
            monitor = NetworkMonitor(self.config)
            print("PASS: Enhanced network monitor imported successfully")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Enhanced network monitor import failed: {e}")
    
    def test_packet_buffer_basic(self):
        """Test basic packet buffer functionality"""
        try:
            from backend.packet_filter import PacketBuffer
            
            buffer = PacketBuffer(max_size=10)
            packet = {"id": 1, "src_ip": "192.168.1.1", "dst_ip": "192.168.1.2"}
            result = buffer.add_packet(packet)
            self.assertTrue(result)
            
            packets = buffer.get_packets(count=1)
            self.assertEqual(len(packets), 1)
            print("PASS: Packet buffer basic functionality working")
        except Exception as e:
            self.fail(f"Packet buffer test failed: {e}")
    
    def test_packet_categorization_basic(self):
        """Test basic packet categorization"""
        try:
            from backend.packet_filter import AdvancedPacketFilter
            
            filter_system = AdvancedPacketFilter(self.config)
            
            # Test web traffic
            web_packet = {
                "src_ip": "192.168.1.100",
                "dst_ip": "142.250.191.14",
                "dst_port": 443,
                "protocol_name": "TCP",
                "size": 1024
            }
            
            result = filter_system.filter_and_categorize_packet(web_packet)
            self.assertEqual(result["category"], "web_traffic")
            print("PASS: Packet categorization working")
        except Exception as e:
            self.fail(f"Packet categorization failed: {e}")
    
    def test_performance_stats(self):
        """Test performance statistics collection"""
        try:
            from backend.network_monitor import NetworkMonitor
            monitor = NetworkMonitor(self.config)
            
            # Check performance stats
            self.assertIn("cpu_usage", monitor.performance_stats)
            self.assertIn("memory_usage", monitor.performance_stats)
            print("PASS: Performance statistics working")
        except Exception as e:
            self.fail(f"Performance stats test failed: {e}")

def run_basic_tests():
    """Run basic Day 4 tests"""
    print("Starting CyberSnoop Day 4 Basic Test Suite")
    print("=" * 50)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDay4Basic)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    total_tests = result.testsRun
    total_passed = total_tests - len(result.failures) - len(result.errors)
    total_failed = len(result.failures) + len(result.errors)
    
    print("\n" + "=" * 50)
    print("DAY 4 BASIC TEST RESULTS")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")
    
    if total_failed == 0:
        print("\nALL BASIC TESTS PASSED!")
        print("Day 4 core functionality is working correctly")
        return True
    else:
        print(f"\n{total_failed} tests failed.")
        return False

if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)
