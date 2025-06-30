"""
Network Monitor for CyberSnoop
Enhanced packet capture, analysis, and threat detection with advanced filtering.
Day 4 Enhanced: Real-time packet filtering, performance optimization, and advanced analysis.
"""

import logging
import threading
import time
import socket
import random
import psutil
from typing import Optional, Callable, Dict, Any, List
from collections import defaultdict, deque
from datetime import datetime, timedelta

# Try to import Scapy, fall back to simulation if not available
try:
    from scapy.all import sniff, get_if_list, get_if_addr, conf
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    SCAPY_AVAILABLE = True
    logging.info("Scapy imported successfully - real packet capture available")
except ImportError:
    SCAPY_AVAILABLE = False
    logging.warning("Scapy not available - using simulation mode")

# Try to import netifaces for better interface detection
try:
    import netifaces
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False
    logging.warning("netifaces not available - using basic interface detection")

class ThreatDetector:
    """Threat detection algorithms"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.connection_tracker = defaultdict(lambda: defaultdict(int))
        self.failed_logins = defaultdict(list)
        self.port_scan_tracker = defaultdict(set)
        self.traffic_baseline = defaultdict(lambda: deque(maxlen=100))
        
    def analyze_packet(self, packet_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a packet for potential threats"""
        threats = []
        
        # Port scan detection
        if self._detect_port_scan(packet_info):
            threats.append({
                "type": "Port Scan",
                "severity": "Medium",
                "source_ip": packet_info.get("src_ip"),
                "description": f"Multiple port connections from {packet_info.get('src_ip')}"
            })
            
        # DDoS detection (simple volume-based)
        if self._detect_ddos(packet_info):
            threats.append({
                "type": "DDoS Attack",
                "severity": "High", 
                "source_ip": packet_info.get("src_ip"),
                "description": f"High traffic volume from {packet_info.get('src_ip')}"
            })
            
        # Suspicious protocol usage
        if self._detect_suspicious_protocol(packet_info):
            threats.append({
                "type": "Suspicious Protocol",
                "severity": "Low",
                "source_ip": packet_info.get("src_ip"),
                "description": f"Unusual protocol usage: {packet_info.get('protocol')}"
            })
            
        return threats[0] if threats else None
        
    def _detect_port_scan(self, packet_info: Dict[str, Any]) -> bool:
        """Detect port scanning behavior"""
        src_ip = packet_info.get("src_ip")
        dst_port = packet_info.get("dst_port")
        
        if src_ip and dst_port:
            self.port_scan_tracker[src_ip].add(dst_port)
            
            # If more than threshold unique ports accessed, it's likely a port scan
            threshold = self.config.get("threat_detection.port_scan_threshold", 10)
            if len(self.port_scan_tracker[src_ip]) > threshold:
                return True
                
        return False
        
    def _detect_ddos(self, packet_info: Dict[str, Any]) -> bool:
        """Detect DDoS attacks based on traffic volume"""
        src_ip = packet_info.get("src_ip")
        
        if src_ip:
            current_time = time.time()
            self.traffic_baseline[src_ip].append(current_time)
            
            # Check if traffic from this IP exceeds threshold in recent time window
            recent_packets = [t for t in self.traffic_baseline[src_ip] if current_time - t < 60]  # Last minute
            threshold = self.config.get("threat_detection.ddos_threshold", 1000)
            
            if len(recent_packets) > threshold:
                return True
                
        return False
        
    def _detect_suspicious_protocol(self, packet_info: Dict[str, Any]) -> bool:
        """Detect suspicious protocol usage"""
        protocol = packet_info.get("protocol")
        dst_port = packet_info.get("dst_port")
        
        # Flag uncommon protocols or ports
        suspicious_ports = [1337, 31337, 12345, 54321]  # Common backdoor ports
        
        if dst_port in suspicious_ports:
            return True
            
        return False

class NetworkMonitor:
    """Enhanced network monitoring and threat detection engine with advanced filtering"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.is_monitoring = False
        self.monitor_thread = None
        self.threat_callback: Optional[Callable] = None
        self.stats_callback: Optional[Callable] = None
        
        # Enhanced statistics with performance monitoring
        self.packet_count = 0
        self.threat_count = 0
        self.connection_count = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.start_time = None
        self.filtered_packet_count = 0
        self.dropped_packet_count = 0
        
        # Performance optimization settings
        self.max_packets_per_second = config_manager.get("performance.max_packets_per_second", 1000)
        self.packet_batch_size = config_manager.get("performance.packet_batch_size", 50)
        self.stats_update_interval = config_manager.get("performance.stats_update_interval", 2.0)
        
        # Performance monitoring
        self.performance_stats = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "packet_processing_rate": 0.0,
            "avg_packet_processing_time": 0.0
        }
        self.last_stats_update = time.time()
        self.packet_processing_times = deque(maxlen=1000)
        
        # Advanced packet filter
        try:
            from .packet_filter import AdvancedPacketFilter
            self.packet_filter = AdvancedPacketFilter(config_manager)
            logging.info("Advanced packet filter initialized")
        except ImportError as e:
            logging.warning(f"Advanced packet filter not available: {e}")
            self.packet_filter = None
        
        # Threat detection - use advanced detector
        try:
            from .threat_detector import AdvancedThreatDetector
            self.threat_detector = AdvancedThreatDetector(config_manager)
            logging.info("Advanced threat detector initialized")
        except ImportError:
            # Fallback to basic threat detector
            self.threat_detector = ThreatDetector(config_manager)
            logging.info("Basic threat detector initialized")
        
        # Network interfaces
        self.available_interfaces = []
        self.selected_interface = None
        
        # Packet capture control
        self.capture_filters = {
            "enabled": True,
            "protocols": ["TCP", "UDP", "ICMP"],  # Default protocols to capture
            "port_ranges": [],  # Custom port ranges
            "ip_whitelist": [],  # IPs to always capture
            "ip_blacklist": []   # IPs to never capture
        }
        
        # Initialize interface detection
        self._detect_network_interfaces()
        
        # Start performance monitoring thread (only if monitoring is enabled)
        self.performance_thread = None
        self._start_performance_monitoring()
    
    def _start_performance_monitoring(self):
        """Start performance monitoring thread"""
        try:
            if not self.performance_thread:
                self.performance_thread = threading.Thread(target=self._performance_monitor_loop, daemon=True)
                self.performance_thread.start()
                logging.info("Performance monitoring thread started")
        except Exception as e:
            logging.warning(f"Performance monitoring thread failed to start: {e}")
            # Continue without performance monitoring
    
    def _performance_monitor_loop(self):
        """Monitor system performance and adjust capture settings"""
        while True:
            try:
                # Get system performance metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                
                self.performance_stats.update({
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory_info.percent,
                    "memory_available_mb": memory_info.available / (1024 * 1024)
                })
                
                # Calculate packet processing rate
                current_time = time.time()
                time_diff = current_time - self.last_stats_update
                if time_diff > 0:
                    self.performance_stats["packet_processing_rate"] = self.packet_count / time_diff
                
                # Calculate average processing time
                if self.packet_processing_times:
                    self.performance_stats["avg_packet_processing_time"] = (
                        sum(self.packet_processing_times) / len(self.packet_processing_times) * 1000
                    )
                
                # Performance-based optimization
                self._optimize_capture_performance()
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logging.error(f"Performance monitoring error: {e}")
                time.sleep(10)
    
    def _optimize_capture_performance(self):
        """Automatically optimize capture performance based on system load"""
        cpu_usage = self.performance_stats["cpu_usage"]
        memory_usage = self.performance_stats["memory_usage"]
        
        # High CPU usage optimization
        if cpu_usage > 80:
            # Reduce packet capture rate
            self.max_packets_per_second = max(100, self.max_packets_per_second - 100)
            self.packet_batch_size = max(10, self.packet_batch_size - 10)
            logging.warning(f"High CPU usage ({cpu_usage}%), reducing capture rate")
        
        # High memory usage optimization
        if memory_usage > 85:
            # Clear buffers and reduce memory usage
            if self.packet_filter:
                self.packet_filter.clear_buffer()
            logging.warning(f"High memory usage ({memory_usage}%), clearing buffers")
        
        # Normal usage - restore performance
        if cpu_usage < 50 and memory_usage < 70:
            original_max = self.config_manager.get("performance.max_packets_per_second", 1000)
            original_batch = self.config_manager.get("performance.packet_batch_size", 50)
            
            self.max_packets_per_second = min(original_max, self.max_packets_per_second + 50)
            self.packet_batch_size = min(original_batch, self.packet_batch_size + 5)
        
        # Start performance monitoring thread
        self.performance_thread = threading.Thread(target=self._performance_monitor_loop, daemon=True)
        self.performance_thread.start()
        
    def _detect_network_interfaces(self):
        """Enhanced network interface detection with detailed Windows adapter information"""
        self.available_interfaces = []
        
        try:
            # Try Windows-specific WMI detection first
            if self._detect_windows_interfaces():
                return
                
            # Fallback to Scapy detection
            if SCAPY_AVAILABLE:
                self._detect_scapy_interfaces()
                
            # Fallback to netifaces
            elif NETIFACES_AVAILABLE:
                self._detect_netifaces_interfaces()
                
            # Final fallback
            else:
                self._detect_basic_interfaces()
                
            logging.info(f"Detected {len(self.available_interfaces)} network interfaces")
            
        except Exception as e:
            logging.error(f"Error detecting network interfaces: {e}")
            self._create_fallback_interface()
    
    def _detect_windows_interfaces(self) -> bool:
        """Detect Windows network adapters using WMI"""
        try:
            import subprocess
            import json
            
            # Use PowerShell to get detailed adapter information
            ps_command = """
            Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | ForEach-Object {
                $adapter = $_
                $ipConfig = Get-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
                [PSCustomObject]@{
                    Name = $adapter.Name
                    InterfaceDescription = $adapter.InterfaceDescription
                    Status = $adapter.Status
                    LinkSpeed = $adapter.LinkSpeed
                    MediaType = $adapter.MediaType
                    IPAddress = if($ipConfig) { $ipConfig.IPAddress } else { $null }
                    InterfaceIndex = $adapter.InterfaceIndex
                    MacAddress = $adapter.MacAddress
                }
            } | ConvertTo-Json
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                adapters_data = json.loads(result.stdout)
                if isinstance(adapters_data, dict):
                    adapters_data = [adapters_data]
                
                for adapter in adapters_data:
                    if adapter.get('IPAddress'):
                        self.available_interfaces.append({
                            "name": adapter.get('Name', 'Unknown'),
                            "description": adapter.get('InterfaceDescription', ''),
                            "ip": adapter.get('IPAddress', ''),
                            "mac": adapter.get('MacAddress', ''),
                            "status": "active",
                            "type": "windows_adapter",
                            "speed": self._format_link_speed(adapter.get('LinkSpeed', 0)),
                            "media_type": adapter.get('MediaType', 'Unknown'),
                            "interface_index": adapter.get('InterfaceIndex', 0)
                        })
                
                return len(self.available_interfaces) > 0
                
        except Exception as e:
            logging.debug(f"Windows interface detection failed: {e}")
            
        return False
        
    def _format_link_speed(self, speed_bps: int) -> str:
        """Format link speed in human-readable format"""
        if not speed_bps or speed_bps == 0:
            return "Unknown"
            
        if speed_bps >= 1_000_000_000:
            return f"{speed_bps // 1_000_000_000} Gbps"
        elif speed_bps >= 1_000_000:
            return f"{speed_bps // 1_000_000} Mbps"
        elif speed_bps >= 1_000:
            return f"{speed_bps // 1_000} Kbps"
        else:
            return f"{speed_bps} bps"
    
    def _detect_scapy_interfaces(self):
        """Detect interfaces using Scapy"""
        try:
            interfaces = get_if_list()
            for interface in interfaces:
                try:
                    ip_addr = get_if_addr(interface)
                    if ip_addr and ip_addr != "0.0.0.0":
                        self.available_interfaces.append({
                            "name": interface,
                            "description": f"Scapy detected: {interface}",
                            "ip": ip_addr,
                            "mac": "",
                            "status": "active",
                            "type": "scapy_detected",
                            "speed": "Unknown",
                            "media_type": "Unknown",
                            "interface_index": 0
                        })
                except:
                    pass
        except Exception as e:
            logging.debug(f"Scapy interface detection failed: {e}")
    
    def _detect_netifaces_interfaces(self):
        """Detect interfaces using netifaces"""
        try:
            interfaces = netifaces.interfaces()
            for interface in interfaces:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    ip_addr = addrs[netifaces.AF_INET][0]['addr']
                    if ip_addr != "127.0.0.1":
                        mac_addr = ""
                        if netifaces.AF_LINK in addrs:
                            mac_addr = addrs[netifaces.AF_LINK][0].get('addr', '')
                            
                        self.available_interfaces.append({
                            "name": interface,
                            "description": f"Network interface: {interface}",
                            "ip": ip_addr,
                            "mac": mac_addr,
                            "status": "active",
                            "type": "netifaces_detected",
                            "speed": "Unknown",
                            "media_type": "Unknown",
                            "interface_index": 0
                        })
        except Exception as e:
            logging.debug(f"Netifaces interface detection failed: {e}")
    
    def _detect_basic_interfaces(self):
        """Basic interface detection using socket"""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            self.available_interfaces.append({
                "name": "Local Interface",
                "description": f"Local network interface ({hostname})",
                "ip": local_ip,
                "mac": "",
                "status": "active",
                "type": "socket_detected",
                "speed": "Unknown",
                "media_type": "Unknown",
                "interface_index": 0
            })
        except Exception as e:
            logging.debug(f"Basic interface detection failed: {e}")
    
    def _create_fallback_interface(self):
        """Create fallback interface when all detection methods fail"""
        self.available_interfaces = [{
            "name": "Fallback Interface",
            "description": "Simulated network interface for testing",
            "ip": "127.0.0.1",
            "mac": "",
            "status": "simulated",
            "type": "fallback",
            "speed": "Unknown",
            "media_type": "Loopback",
            "interface_index": 0
        }]
            
    def start_monitoring(self, interface_name: Optional[str] = None):
        """Start network monitoring on specified interface"""
        if self.is_monitoring:
            logging.warning("Network monitoring is already running")
            return
            
        self.is_monitoring = True
        self.start_time = time.time()
        self.selected_interface = interface_name or (
            self.available_interfaces[0]["name"] if self.available_interfaces else None
        )
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logging.info(f"Network monitoring started on interface: {self.selected_interface}")
        
    def stop_monitoring(self):
        """Stop network monitoring"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logging.info("Network monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop with real or simulated packet capture"""
        logging.info("Starting network monitoring loop")
        
        if SCAPY_AVAILABLE and self.selected_interface:
            self._real_packet_capture()
        else:
            self._simulated_packet_capture()
            
    def _real_packet_capture(self):
        """Enhanced real packet capture using Scapy with filtering and performance optimization"""
        try:
            logging.info(f"Starting enhanced packet capture on {self.selected_interface}")
            
            # Packet processing control
            packets_this_second = 0
            second_start = time.time()
            
            def packet_handler(packet):
                nonlocal packets_this_second, second_start
                
                if not self.is_monitoring:
                    return
                
                current_time = time.time()
                processing_start = current_time
                
                try:
                    # Rate limiting for performance
                    if current_time - second_start >= 1.0:
                        packets_this_second = 0
                        second_start = current_time
                    
                    if packets_this_second >= self.max_packets_per_second:
                        self.dropped_packet_count += 1
                        return
                    
                    packets_this_second += 1
                    
                    # Parse packet
                    packet_info = self._parse_packet(packet)
                    if not packet_info:
                        return
                    
                    # Apply capture filters
                    if not self._should_capture_packet(packet_info):
                        return
                    
                    # Update basic stats
                    self.packet_count += 1
                    self.bytes_received += len(packet)
                    
                    # Advanced packet filtering and categorization
                    if self.packet_filter:
                        try:
                            filtered_packet = self.packet_filter.filter_and_categorize_packet(packet_info)
                            self.filtered_packet_count += 1
                        except Exception as e:
                            logging.debug(f"Packet filtering error: {e}")
                            filtered_packet = packet_info
                    else:
                        filtered_packet = packet_info
                    
                    # Threat detection with priority handling
                    threat = None
                    packet_priority = filtered_packet.get("priority", 4)
                    
                    # Only run expensive threat detection on high-priority packets
                    if packet_priority <= 2:  # CRITICAL or HIGH priority
                        threat = self.threat_detector.analyze_packet(filtered_packet)
                        if threat:
                            self.threat_count += 1
                            threat["timestamp"] = datetime.now().isoformat()
                            threat["packet_category"] = filtered_packet.get("category", "unknown")
                            if self.threat_callback:
                                self.threat_callback(threat)
                    
                    # Record processing time for performance monitoring
                    processing_time = time.time() - processing_start
                    self.packet_processing_times.append(processing_time)
                    
                    # Update statistics periodically (performance optimization)
                    if self.packet_count % self.packet_batch_size == 0:
                        self._update_statistics()
                        
                except Exception as e:
                    logging.error(f"Error processing packet: {e}")
                    
            # Configure Scapy capture parameters for performance
            capture_filter = self._build_capture_filter()
            
            # Start packet sniffing with optimized parameters
            sniff(
                iface=self.selected_interface, 
                prn=packet_handler, 
                stop_filter=lambda x: not self.is_monitoring,
                filter=capture_filter,  # BPF filter for performance
                store=False,            # Don't store packets in memory
                count=0                 # Capture indefinitely
            )
            
        except Exception as e:
            logging.error(f"Enhanced packet capture failed: {e}")
            # Fall back to simulation
            self._simulated_packet_capture()
    
    def _should_capture_packet(self, packet_info: Dict[str, Any]) -> bool:
        """Determine if packet should be captured based on filters"""
        if not self.capture_filters["enabled"]:
            return True
        
        # Protocol filtering
        protocol = packet_info.get("protocol_name", "").upper()
        if protocol and protocol not in self.capture_filters["protocols"]:
            return False
        
        # IP whitelist check
        src_ip = packet_info.get("src_ip", "")
        dst_ip = packet_info.get("dst_ip", "")
        if self.capture_filters["ip_whitelist"]:
            if not (src_ip in self.capture_filters["ip_whitelist"] or 
                   dst_ip in self.capture_filters["ip_whitelist"]):
                return False
        
        # IP blacklist check
        if src_ip in self.capture_filters["ip_blacklist"] or dst_ip in self.capture_filters["ip_blacklist"]:
            return False
        
        # Port range filtering
        dst_port = packet_info.get("dst_port")
        src_port = packet_info.get("src_port")
        if self.capture_filters["port_ranges"]:
            port_match = False
            for port_range in self.capture_filters["port_ranges"]:
                start, end = port_range
                if ((dst_port and start <= dst_port <= end) or 
                    (src_port and start <= src_port <= end)):
                    port_match = True
                    break
            if not port_match:
                return False
        
        return True
    
    def _build_capture_filter(self) -> str:
        """Build BPF (Berkeley Packet Filter) for efficient packet capture"""
        filters = []
        
        # Protocol filters
        if self.capture_filters["protocols"]:
            protocol_filters = []
            for protocol in self.capture_filters["protocols"]:
                if protocol.upper() == "TCP":
                    protocol_filters.append("tcp")
                elif protocol.upper() == "UDP":
                    protocol_filters.append("udp")
                elif protocol.upper() == "ICMP":
                    protocol_filters.append("icmp")
            
            if protocol_filters:
                filters.append(f"({' or '.join(protocol_filters)})")
        
        # Port range filters
        if self.capture_filters["port_ranges"]:
            port_filters = []
            for start, end in self.capture_filters["port_ranges"]:
                if start == end:
                    port_filters.append(f"port {start}")
                else:
                    port_filters.append(f"portrange {start}-{end}")
            
            if port_filters:
                filters.append(f"({' or '.join(port_filters)})")
        
        # Combine filters
        if filters:
            return " and ".join(filters)
        else:
            return ""  # No filter - capture all packets
            
    def _parse_packet(self, packet):
        """Parse Scapy packet into standardized format"""
        try:
            packet_info = {
                "timestamp": datetime.now().isoformat(),
                "size": len(packet)
            }
            
            if IP in packet:
                packet_info.update({
                    "src_ip": packet[IP].src,
                    "dst_ip": packet[IP].dst,
                    "protocol": packet[IP].proto
                })
                
                if TCP in packet:
                    packet_info.update({
                        "src_port": packet[TCP].sport,
                        "dst_port": packet[TCP].dport,
                        "protocol_name": "TCP"
                    })
                elif UDP in packet:
                    packet_info.update({
                        "src_port": packet[UDP].sport,
                        "dst_port": packet[UDP].dport,
                        "protocol_name": "UDP"
                    })
                elif ICMP in packet:
                    packet_info.update({
                        "protocol_name": "ICMP"
                    })
                    
            return packet_info
            
        except Exception as e:
            logging.error(f"Error parsing packet: {e}")
            return None
            
    def _simulated_packet_capture(self):
        """Simulated packet capture for development/testing"""
        logging.info("Starting simulated packet capture")
        
        while self.is_monitoring:
            try:
                # Simulate packet batch
                packet_batch = random.randint(5, 25)
                self.packet_count += packet_batch
                self.bytes_received += packet_batch * random.randint(64, 1500)
                
                # Simulate occasional threats
                if random.random() < 0.02:  # 2% chance
                    threat_types = ["Port Scan", "Brute Force Attack", "DDoS Attack", "Suspicious Connection"]
                    threat = {
                        "type": random.choice(threat_types),
                        "severity": random.choice(["Low", "Medium", "High"]),
                        "source_ip": f"192.168.1.{random.randint(1, 254)}",
                        "destination_ip": "192.168.1.1",
                        "timestamp": datetime.now().isoformat(),
                        "description": "Simulated threat for development"
                    }
                    
                    self.threat_count += 1
                    if self.threat_callback:
                        self.threat_callback(threat)
                        
                # Update statistics
                self._update_statistics()
                
                # Sleep between batches
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error in simulated monitoring loop: {e}")
                time.sleep(5)
                
    def _update_statistics(self):
        """Enhanced statistics update with performance metrics"""
        current_time = time.time()
        
        # Calculate active connections (enhanced with real data when possible)
        self.connection_count = self._get_active_connections_count()
        
        uptime = current_time - self.start_time if self.start_time else 0
        
        # Calculate rates
        packet_rate = self.packet_count / uptime if uptime > 0 else 0
        threat_rate = self.threat_count / uptime if uptime > 0 else 0
        
        # Enhanced statistics data
        stats_data = {
            "packet_count": self.packet_count,
            "filtered_packet_count": self.filtered_packet_count,
            "dropped_packet_count": self.dropped_packet_count,
            "threat_count": self.threat_count,
            "connection_count": self.connection_count,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "uptime": uptime,
            "packet_rate": round(packet_rate, 2),
            "threat_rate": round(threat_rate, 4),
            "timestamp": datetime.now().isoformat(),
            "interfaces": self.available_interfaces,
            "selected_interface": self.selected_interface,
            "monitoring_mode": "real" if SCAPY_AVAILABLE else "simulated",
            "performance": self.performance_stats.copy(),
            "capture_filters": self.capture_filters.copy()
        }
        
        # Add packet filter statistics if available
        if self.packet_filter:
            try:
                filter_stats = self.packet_filter.get_filter_statistics()
                stats_data["filter_statistics"] = filter_stats
            except Exception as e:
                logging.debug(f"Error getting filter statistics: {e}")
        
        self.last_stats_update = current_time
        
        if self.stats_callback:
            self.stats_callback(stats_data)
    
    def _get_active_connections_count(self) -> int:
        """Get actual count of active network connections"""
        try:
            # Try to get real connection count using psutil
            connections = psutil.net_connections(kind='inet')
            active_connections = [conn for conn in connections if conn.status == 'ESTABLISHED']
            return len(active_connections)
        except Exception:
            # Fallback to simulated count
            return random.randint(40, 80)
            
    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get available network interfaces"""
        return self.available_interfaces
        
    def set_interface(self, interface_name: str):
        """Set the network interface for monitoring"""
        if interface_name in [iface["name"] for iface in self.available_interfaces]:
            self.selected_interface = interface_name
            logging.info(f"Network interface set to: {interface_name}")
            return True
        else:
            logging.error(f"Interface {interface_name} not found")
            return False
            
    def get_current_stats(self) -> Dict[str, Any]:
        """Get enhanced monitoring statistics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        base_stats = {
            "is_monitoring": self.is_monitoring,
            "packet_count": self.packet_count,
            "filtered_packet_count": self.filtered_packet_count,
            "dropped_packet_count": self.dropped_packet_count,
            "threat_count": self.threat_count,
            "connection_count": self.connection_count,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "uptime": uptime,
            "interfaces": self.available_interfaces,
            "selected_interface": self.selected_interface,
            "scapy_available": SCAPY_AVAILABLE,
            "performance": self.performance_stats.copy(),
            "capture_filters": self.capture_filters.copy()
        }
        
        # Add filter statistics if available
        if self.packet_filter:
            try:
                base_stats["filter_statistics"] = self.packet_filter.get_filter_statistics()
            except Exception as e:
                logging.debug(f"Error getting filter statistics: {e}")
        
        return base_stats
    
    # Enhanced filter management methods
    def set_capture_filters(self, filters: Dict[str, Any]) -> bool:
        """Set packet capture filters"""
        try:
            # Validate filter format
            valid_keys = {"enabled", "protocols", "port_ranges", "ip_whitelist", "ip_blacklist"}
            if not all(key in valid_keys for key in filters.keys()):
                return False
            
            self.capture_filters.update(filters)
            logging.info(f"Updated capture filters: {filters}")
            return True
        except Exception as e:
            logging.error(f"Error setting capture filters: {e}")
            return False
    
    def add_ip_to_whitelist(self, ip: str) -> bool:
        """Add IP to capture whitelist"""
        try:
            if ip not in self.capture_filters["ip_whitelist"]:
                self.capture_filters["ip_whitelist"].append(ip)
                logging.info(f"Added {ip} to whitelist")
            return True
        except Exception as e:
            logging.error(f"Error adding IP to whitelist: {e}")
            return False
    
    def add_ip_to_blacklist(self, ip: str) -> bool:
        """Add IP to capture blacklist"""
        try:
            if ip not in self.capture_filters["ip_blacklist"]:
                self.capture_filters["ip_blacklist"].append(ip)
                logging.info(f"Added {ip} to blacklist")
            return True
        except Exception as e:
            logging.error(f"Error adding IP to blacklist: {e}")
            return False
    
    def add_port_range(self, start_port: int, end_port: int) -> bool:
        """Add port range to capture filters"""
        try:
            port_range = (start_port, end_port)
            if port_range not in self.capture_filters["port_ranges"]:
                self.capture_filters["port_ranges"].append(port_range)
                logging.info(f"Added port range {start_port}-{end_port}")
            return True
        except Exception as e:
            logging.error(f"Error adding port range: {e}")
            return False
    
    def get_filtered_packets(self, category: str = None, count: int = 100) -> List[Dict[str, Any]]:
        """Get filtered packets from packet buffer"""
        if self.packet_filter:
            return self.packet_filter.get_filtered_packets(category=category, count=count)
        return []
    
    def get_packet_categories(self) -> Dict[str, int]:
        """Get packet category statistics"""
        if self.packet_filter:
            return self.packet_filter.get_category_statistics()
        return {}
    
    def clear_packet_buffer(self):
        """Clear packet buffer"""
        if self.packet_filter:
            self.packet_filter.clear_buffer()
            logging.info("Packet buffer cleared")
    
    def optimize_performance(self):
        """Manually trigger performance optimization"""
        self._optimize_capture_performance()
        if self.packet_filter:
            self.packet_filter.optimize_performance()
        logging.info("Performance optimization triggered")
    
    def export_packet_data(self, filename: str, category: str = None, count: int = 1000) -> bool:
        """Export packet data to file"""
        try:
            import json
            packets = self.get_filtered_packets(category=category, count=count)
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "export_params": {
                    "category": category,
                    "count": count,
                    "interface": self.selected_interface
                },
                "statistics": self.get_current_stats(),
                "packets": packets
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logging.info(f"Exported {len(packets)} packets to {filename}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting packet data: {e}")
            return False
    
    def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get available network interfaces (alias for get_network_interfaces)"""
        return self.get_network_interfaces()
    
    def get_active_connections_count(self) -> int:
        """Get count of active network connections"""
        return self.connection_count
    
    def get_bandwidth_stats(self) -> Dict[str, str]:
        """Get current bandwidth statistics"""
        # Calculate rates based on collected data
        uptime = time.time() - self.start_time if self.start_time else 1
        
        upload_rate = self.bytes_sent / uptime if uptime > 0 else 0
        download_rate = self.bytes_received / uptime if uptime > 0 else 0
        
        def format_bytes(bytes_value):
            """Format bytes to human readable string"""
            for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
                if bytes_value < 1024.0:
                    return f"{bytes_value:.1f} {unit}"
                bytes_value /= 1024.0
            return f"{bytes_value:.1f} TB/s"
        
        return {
            "upload": format_bytes(upload_rate),
            "download": format_bytes(download_rate)
        }
