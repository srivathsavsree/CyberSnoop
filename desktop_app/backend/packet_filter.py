"""
Advanced Packet Filter and Categorization System for CyberSnoop
Real-time packet filtering, categorization, and analysis with performance optimization
"""

import logging
import threading
import time
from typing import Dict, Any, List, Optional, Set, Callable
from collections import defaultdict, deque
from datetime import datetime, timedelta
from enum import Enum
import re

# Try to import Scapy for advanced packet analysis
try:
    from scapy.all import IP, TCP, UDP, ICMP, ARP, DNS, HTTP
    from scapy.layers.dhcp import DHCP
    from scapy.layers.tls import TLS
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logging.warning("Scapy not available for advanced packet filtering")

class PacketCategory(Enum):
    """Packet categories for classification"""
    WEB_TRAFFIC = "web_traffic"
    SYSTEM_TRAFFIC = "system_traffic"
    P2P_TRAFFIC = "p2p_traffic"
    STREAMING = "streaming"
    GAMING = "gaming"
    EMAIL = "email"
    FTP = "ftp"
    DNS = "dns"
    DHCP = "dhcp"
    VPN = "vpn"
    SECURITY = "security"
    MALWARE = "malware"
    UNKNOWN = "unknown"

class PacketPriority(Enum):
    """Packet priority levels for processing"""
    CRITICAL = 1    # Security threats, malware
    HIGH = 2        # System traffic, DNS
    NORMAL = 3      # Web, email
    LOW = 4         # P2P, streaming

class PacketBuffer:
    """Thread-safe circular buffer for packet storage with memory management"""
    
    def __init__(self, max_size: int = 10000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.buffer = deque(maxlen=max_size)
        self.memory_usage = 0
        self.lock = threading.RLock()
        self.stats = {
            "total_packets": 0,
            "dropped_packets": 0,
            "memory_cleanups": 0
        }
    
    def add_packet(self, packet_data: Dict[str, Any]) -> bool:
        """Add packet to buffer with memory management"""
        with self.lock:
            packet_size = self._estimate_packet_size(packet_data)
            
            # Check memory limits
            if self.memory_usage + packet_size > self.max_memory_bytes:
                self._cleanup_memory()
                
            # Add packet if there's space
            if len(self.buffer) < self.max_size:
                self.buffer.append(packet_data)
                self.memory_usage += packet_size
                self.stats["total_packets"] += 1
                return True
            else:
                # Buffer full, drop packet
                self.stats["dropped_packets"] += 1
                return False
    
    def get_packets(self, count: int = None, category: str = None) -> List[Dict[str, Any]]:
        """Get packets from buffer with optional filtering"""
        with self.lock:
            packets = list(self.buffer)
            
            # Filter by category if specified
            if category:
                packets = [p for p in packets if p.get("category") == category]
            
            # Limit count if specified
            if count:
                packets = packets[-count:]
                
            return packets
    
    def clear(self):
        """Clear buffer and reset stats"""
        with self.lock:
            self.buffer.clear()
            self.memory_usage = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics"""
        with self.lock:
            return {
                "buffer_size": len(self.buffer),
                "max_size": self.max_size,
                "memory_usage_mb": self.memory_usage / (1024 * 1024),
                "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
                **self.stats
            }
    
    def _estimate_packet_size(self, packet_data: Dict[str, Any]) -> int:
        """Estimate memory size of packet data"""
        # Rough estimation based on data types and content
        size = 0
        for key, value in packet_data.items():
            size += len(str(key)) + len(str(value))
        return size + 100  # Base overhead
    
    def _cleanup_memory(self):
        """Clean up memory by removing old packets"""
        if len(self.buffer) > 0:
            # Remove 25% of oldest packets
            cleanup_count = max(1, len(self.buffer) // 4)
            for _ in range(cleanup_count):
                if self.buffer:
                    removed = self.buffer.popleft()
                    self.memory_usage -= self._estimate_packet_size(removed)
            
            self.stats["memory_cleanups"] += 1

class AdvancedPacketFilter:
    """Advanced packet filtering and categorization system"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.packet_buffer = PacketBuffer(
            max_size=self.config.get("packet_filter.buffer_size", 10000),
            max_memory_mb=self.config.get("packet_filter.max_memory_mb", 100)
        )
        
        # Protocol port mappings for categorization
        self.port_categories = {
            # Web traffic
            80: PacketCategory.WEB_TRAFFIC,
            443: PacketCategory.WEB_TRAFFIC,
            8080: PacketCategory.WEB_TRAFFIC,
            8443: PacketCategory.WEB_TRAFFIC,
            
            # Email
            25: PacketCategory.EMAIL,    # SMTP
            110: PacketCategory.EMAIL,   # POP3
            143: PacketCategory.EMAIL,   # IMAP
            993: PacketCategory.EMAIL,   # IMAPS
            995: PacketCategory.EMAIL,   # POP3S
            
            # System services
            53: PacketCategory.DNS,      # DNS
            67: PacketCategory.DHCP,     # DHCP Server
            68: PacketCategory.DHCP,     # DHCP Client
            
            # FTP
            20: PacketCategory.FTP,      # FTP Data
            21: PacketCategory.FTP,      # FTP Control
            
            # VPN
            1194: PacketCategory.VPN,    # OpenVPN
            1723: PacketCategory.VPN,    # PPTP
            
            # P2P
            6881: PacketCategory.P2P_TRAFFIC,  # BitTorrent
            6969: PacketCategory.P2P_TRAFFIC,  # BitTorrent tracker
        }
        
        # Suspicious ports for security categorization
        self.suspicious_ports = {
            1337, 31337, 12345, 54321, 666, 1234, 4444, 5555, 6666, 9999
        }
        
        # Gaming ports
        self.gaming_ports = {
            3724, 6112, 6113, 6114, 27015, 27016, 28910
        }
        
        # Streaming ports
        self.streaming_ports = {
            1935,  # RTMP
            5004,  # RTP
            5005   # RTCP
        }
        
        # Statistics
        self.filter_stats = defaultdict(int)
        self.category_stats = defaultdict(int)
        self.priority_stats = defaultdict(int)
        
        # Performance monitoring
        self.processing_times = deque(maxlen=1000)
        self.lock = threading.RLock()
        
    def filter_and_categorize_packet(self, packet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main filtering and categorization function"""
        start_time = time.time()
        
        try:
            # Enhance packet data with categorization
            enhanced_packet = packet_data.copy()
            
            # Categorize packet
            category = self._categorize_packet(packet_data)
            enhanced_packet["category"] = category.value
            
            # Assign priority
            priority = self._assign_priority(category, packet_data)
            enhanced_packet["priority"] = priority.value
            
            # Add filtering metadata
            enhanced_packet["filtered_at"] = datetime.now().isoformat()
            enhanced_packet["filter_version"] = "1.0"
            
            # Perform advanced analysis if packet is high priority
            if priority in [PacketPriority.CRITICAL, PacketPriority.HIGH]:
                enhanced_packet = self._advanced_analysis(enhanced_packet)
            
            # Add to buffer
            self.packet_buffer.add_packet(enhanced_packet)
            
            # Update statistics
            with self.lock:
                self.filter_stats["total_filtered"] += 1
                self.category_stats[category.value] += 1
                self.priority_stats[priority.value] += 1
            
            # Record processing time
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            
            return enhanced_packet
            
        except Exception as e:
            logging.error(f"Error in packet filtering: {e}")
            self.filter_stats["errors"] += 1
            return packet_data
    
    def _categorize_packet(self, packet_data: Dict[str, Any]) -> PacketCategory:
        """Categorize packet based on ports, protocols, and content"""
        
        dst_port = packet_data.get("dst_port")
        src_port = packet_data.get("src_port")
        protocol = packet_data.get("protocol_name", "").upper()
        src_ip = packet_data.get("src_ip", "")
        dst_ip = packet_data.get("dst_ip", "")
        
        # Check for suspicious ports first (security priority)
        if dst_port in self.suspicious_ports or src_port in self.suspicious_ports:
            return PacketCategory.SECURITY
        
        # Check for malware communication patterns
        if self._is_malware_communication(packet_data):
            return PacketCategory.MALWARE
        
        # Check known port categories
        if dst_port in self.port_categories:
            return self.port_categories[dst_port]
        if src_port in self.port_categories:
            return self.port_categories[src_port]
        
        # Gaming traffic detection
        if dst_port in self.gaming_ports or src_port in self.gaming_ports:
            return PacketCategory.GAMING
        
        # Streaming traffic detection
        if dst_port in self.streaming_ports or src_port in self.streaming_ports:
            return PacketCategory.STREAMING
        
        # High port ranges often indicate P2P
        if (dst_port and dst_port > 50000) or (src_port and src_port > 50000):
            return PacketCategory.P2P_TRAFFIC
        
        # Protocol-based categorization
        if protocol == "ICMP":
            return PacketCategory.SYSTEM_TRAFFIC
        
        # Default categorization
        return PacketCategory.UNKNOWN
    
    def _assign_priority(self, category: PacketCategory, packet_data: Dict[str, Any]) -> PacketPriority:
        """Assign processing priority to packet"""
        
        if category in [PacketCategory.MALWARE, PacketCategory.SECURITY]:
            return PacketPriority.CRITICAL
        
        if category in [PacketCategory.SYSTEM_TRAFFIC, PacketCategory.DNS, PacketCategory.DHCP]:
            return PacketPriority.HIGH
        
        if category in [PacketCategory.WEB_TRAFFIC, PacketCategory.EMAIL]:
            return PacketPriority.NORMAL
        
        # P2P, streaming, gaming get lower priority
        return PacketPriority.LOW
    
    def _is_malware_communication(self, packet_data: Dict[str, Any]) -> bool:
        """Detect potential malware communication patterns"""
        
        dst_port = packet_data.get("dst_port")
        src_ip = packet_data.get("src_ip", "")
        dst_ip = packet_data.get("dst_ip", "")
        
        # Known malware ports
        malware_ports = {
            6667, 6668, 6669,  # IRC (often used by botnets)
            4444,               # Metasploit default
            5554,               # Sasser worm
            9999,               # Various malware
            31337               # Back Orifice
        }
        
        if dst_port in malware_ports:
            return True
        
        # Check for suspicious IP patterns
        if self._is_suspicious_ip(dst_ip):
            return True
        
        return False
    
    def _is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP address looks suspicious"""
        
        # Known bad IP ranges or patterns
        suspicious_patterns = [
            r"^0\.",          # Invalid range
            r"^127\.",        # Loopback (suspicious if external)
            r"^169\.254\.",   # Link-local
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, ip):
                return True
        
        return False
    
    def _advanced_analysis(self, packet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced analysis on high-priority packets"""
        
        enhanced = packet_data.copy()
        
        # Add threat indicators
        threat_indicators = []
        
        # Check for port scanning patterns
        if self._is_potential_port_scan(packet_data):
            threat_indicators.append("potential_port_scan")
        
        # Check for brute force patterns
        if self._is_potential_brute_force(packet_data):
            threat_indicators.append("potential_brute_force")
        
        # Check for data exfiltration patterns
        if self._is_potential_data_exfiltration(packet_data):
            threat_indicators.append("potential_data_exfiltration")
        
        enhanced["threat_indicators"] = threat_indicators
        enhanced["advanced_analysis"] = True
        
        return enhanced
    
    def _is_potential_port_scan(self, packet_data: Dict[str, Any]) -> bool:
        """Detect potential port scanning behavior"""
        # This would integrate with the threat detector for more sophisticated detection
        dst_port = packet_data.get("dst_port")
        return dst_port and dst_port < 1024  # Scanning common ports
    
    def _is_potential_brute_force(self, packet_data: Dict[str, Any]) -> bool:
        """Detect potential brute force attack patterns"""
        dst_port = packet_data.get("dst_port")
        # Common brute force targets
        brute_force_ports = {22, 23, 21, 25, 53, 80, 110, 143, 443, 993, 995, 3389}
        return dst_port in brute_force_ports
    
    def _is_potential_data_exfiltration(self, packet_data: Dict[str, Any]) -> bool:
        """Detect potential data exfiltration patterns"""
        size = packet_data.get("size", 0)
        # Large outbound packets might indicate data exfiltration
        return size > 10000  # Large packet threshold
    
    def get_filtered_packets(self, category: str = None, count: int = 100) -> List[Dict[str, Any]]:
        """Get filtered packets from buffer"""
        return self.packet_buffer.get_packets(count=count, category=category)
    
    def get_category_statistics(self) -> Dict[str, int]:
        """Get packet category statistics"""
        with self.lock:
            return dict(self.category_stats)
    
    def get_filter_statistics(self) -> Dict[str, Any]:
        """Get comprehensive filter statistics"""
        with self.lock:
            avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
            
            return {
                "filter_stats": dict(self.filter_stats),
                "category_stats": dict(self.category_stats),
                "priority_stats": dict(self.priority_stats),
                "buffer_stats": self.packet_buffer.get_stats(),
                "performance": {
                    "avg_processing_time_ms": avg_processing_time * 1000,
                    "max_processing_time_ms": max(self.processing_times) * 1000 if self.processing_times else 0,
                    "min_processing_time_ms": min(self.processing_times) * 1000 if self.processing_times else 0
                }
            }
    
    def create_filter_rule(self, name: str, conditions: Dict[str, Any], action: str = "allow"):
        """Create custom filter rule (placeholder for future enhancement)"""
        # This would allow users to create custom filtering rules
        pass
    
    def clear_buffer(self):
        """Clear packet buffer"""
        self.packet_buffer.clear()
    
    def optimize_performance(self):
        """Optimize filter performance"""
        # Clean up old statistics
        current_time = time.time()
        
        # Reset statistics if they're getting too large
        with self.lock:
            if sum(self.category_stats.values()) > 100000:
                logging.info("Resetting filter statistics for performance")
                self.category_stats.clear()
                self.priority_stats.clear()
                self.filter_stats["total_filtered"] = 0
        
        # Clean buffer if needed
        if self.packet_buffer.memory_usage > self.packet_buffer.max_memory_bytes * 0.8:
            self.packet_buffer._cleanup_memory()
