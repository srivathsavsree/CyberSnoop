"""
Advanced Threat Detection Algorithms for CyberSnoop
Implements sophisticated threat detection including port scans, DDoS attacks, 
brute force attempts, and anomaly detection.
"""

import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
import statistics

class ThreatSeverity(Enum):
    """Threat severity levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class ThreatType(Enum):
    """Types of threats that can be detected"""
    PORT_SCAN = "Port Scan"
    DDoS_ATTACK = "DDoS Attack"
    BRUTE_FORCE = "Brute Force Attack"
    SUSPICIOUS_TRAFFIC = "Suspicious Traffic"
    ANOMALY = "Network Anomaly"
    MALWARE_COMMUNICATION = "Malware Communication"
    DATA_EXFILTRATION = "Data Exfiltration"

@dataclass
class ThreatEvent:
    """Represents a detected threat event"""
    threat_type: ThreatType
    severity: ThreatSeverity
    source_ip: str
    destination_ip: str
    timestamp: datetime
    description: str
    confidence: float  # 0.0 to 1.0
    additional_data: Dict[str, Any]

class ConnectionTracker:
    """Tracks network connections for analysis"""
    
    def __init__(self, max_age_minutes: int = 30):
        self.connections = defaultdict(lambda: defaultdict(set))
        self.connection_times = defaultdict(list)
        self.max_age = timedelta(minutes=max_age_minutes)
        self.lock = threading.Lock()
    
    def add_connection(self, src_ip: str, dst_ip: str, dst_port: int):
        """Add a new connection attempt"""
        with self.lock:
            current_time = datetime.now()
            
            # Clean old connections
            self._clean_old_connections(current_time)
            
            # Track the connection
            self.connections[src_ip][dst_ip].add(dst_port)
            self.connection_times[src_ip].append(current_time)
    
    def _clean_old_connections(self, current_time: datetime):
        """Remove old connection records"""
        cutoff_time = current_time - self.max_age
        
        # Clean connection times
        for src_ip in list(self.connection_times.keys()):
            self.connection_times[src_ip] = [
                t for t in self.connection_times[src_ip] if t > cutoff_time
            ]
            if not self.connection_times[src_ip]:
                del self.connection_times[src_ip]
        
        # Clean connections
        for src_ip in list(self.connections.keys()):
            if src_ip not in self.connection_times:
                del self.connections[src_ip]
    
    def get_port_scan_score(self, src_ip: str) -> Tuple[int, int, float]:
        """
        Get port scan score for a source IP
        Returns: (unique_targets, unique_ports, scan_rate)
        """
        with self.lock:
            if src_ip not in self.connections:
                return 0, 0, 0.0
            
            unique_targets = len(self.connections[src_ip])
            unique_ports = sum(len(ports) for ports in self.connections[src_ip].values())
            
            # Calculate scan rate (connections per minute)
            if src_ip in self.connection_times:
                recent_connections = len(self.connection_times[src_ip])
                time_span = (datetime.now() - min(self.connection_times[src_ip])).total_seconds() / 60
                scan_rate = recent_connections / max(time_span, 1)
            else:
                scan_rate = 0.0
            
            return unique_targets, unique_ports, scan_rate

class TrafficAnalyzer:
    """Analyzes network traffic patterns for anomalies"""
    
    def __init__(self, window_size: int = 100):
        self.packet_rates = deque(maxlen=window_size)
        self.byte_rates = deque(maxlen=window_size)
        self.protocol_stats = defaultdict(int)
        self.port_stats = defaultdict(int)
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def add_packet(self, packet_info: Dict[str, Any]):
        """Add packet information for analysis"""
        with self.lock:
            current_time = time.time()
            
            # Update rates
            if current_time - self.last_update >= 1.0:  # Every second
                self.packet_rates.append(len(self.protocol_stats))
                total_bytes = sum(self.byte_rates) if self.byte_rates else 0
                self.byte_rates.append(total_bytes)
                self.last_update = current_time
            
            # Update protocol stats
            protocol = packet_info.get('protocol_name', 'Unknown')
            self.protocol_stats[protocol] += 1
            
            # Update port stats
            dst_port = packet_info.get('dst_port', 0)
            if dst_port:
                self.port_stats[dst_port] += 1
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect traffic anomalies"""
        anomalies = []
        
        with self.lock:
            # Check for traffic spikes
            if len(self.packet_rates) >= 10:
                recent_avg = statistics.mean(list(self.packet_rates)[-5:])
                historical_avg = statistics.mean(list(self.packet_rates)[:-5])
                
                if recent_avg > historical_avg * 3:  # 3x increase
                    anomalies.append({
                        'type': 'traffic_spike',
                        'severity': 'medium',
                        'description': f'Traffic spike detected: {recent_avg:.1f} vs {historical_avg:.1f} packets/sec'
                    })
            
            # Check for unusual protocols
            total_packets = sum(self.protocol_stats.values())
            if total_packets > 100:
                for protocol, count in self.protocol_stats.items():
                    percentage = (count / total_packets) * 100
                    if percentage > 90 and protocol not in ['TCP', 'UDP', 'ICMP']:
                        anomalies.append({
                            'type': 'unusual_protocol',
                            'severity': 'low',
                            'description': f'Unusual protocol dominance: {protocol} ({percentage:.1f}%)'
                        })
        
        return anomalies

class AdvancedThreatDetector:
    """Advanced threat detection engine with multiple algorithms"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.connection_tracker = ConnectionTracker()
        self.traffic_analyzer = TrafficAnalyzer()
        self.failed_logins = defaultdict(list)
        self.suspicious_ips = set()
        self.known_malware_ports = {1337, 31337, 12345, 54321, 9999}
        self.detected_threats = []
        self.threat_callbacks = []
        
        # Load configuration
        self.port_scan_threshold = self.config.get("threat_detection.port_scan_threshold", 10)
        self.brute_force_threshold = self.config.get("threat_detection.brute_force_threshold", 5)
        self.ddos_threshold = self.config.get("threat_detection.ddos_threshold", 1000)
        
        logging.info("Advanced threat detector initialized")
    
    def add_threat_callback(self, callback):
        """Add callback for threat notifications"""
        self.threat_callbacks.append(callback)
    
    def analyze_packet(self, packet_info: Dict[str, Any]) -> Optional[ThreatEvent]:
        """Analyze a packet for potential threats"""
        try:
            src_ip = packet_info.get('src_ip', '')
            dst_ip = packet_info.get('dst_ip', '')
            dst_port = packet_info.get('dst_port', 0)
            protocol = packet_info.get('protocol', '')
            
            # Skip internal traffic analysis
            if self._is_internal_traffic(src_ip, dst_ip):
                return None
            
            # Add to traffic analyzer
            self.traffic_analyzer.add_packet(packet_info)
            
            # Track connections
            if dst_port:
                self.connection_tracker.add_connection(src_ip, dst_ip, dst_port)
            
            # Check for various threats
            threat = None
            
            # Port scan detection
            threat = threat or self._detect_port_scan(src_ip)
            
            # Suspicious ports
            threat = threat or self._detect_suspicious_ports(src_ip, dst_ip, dst_port)
            
            # Brute force detection
            threat = threat or self._detect_brute_force(src_ip, dst_ip, dst_port)
            
            # DDoS detection
            threat = threat or self._detect_ddos(dst_ip)
            
            # Malware communication
            threat = threat or self._detect_malware_communication(src_ip, dst_ip, dst_port)
            
            if threat:
                self._handle_threat(threat)
            
            return threat
            
        except Exception as e:
            logging.error(f"Error analyzing packet for threats: {e}")
            return None
    
    def _is_internal_traffic(self, src_ip: str, dst_ip: str) -> bool:
        """Check if traffic is internal/local"""
        internal_ranges = [
            '127.', '10.', '192.168.', '172.16.', '172.17.', '172.18.',
            '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
            '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
            '172.29.', '172.30.', '172.31.'
        ]
        
        return any(src_ip.startswith(r) and dst_ip.startswith(r) for r in internal_ranges)
    
    def _detect_port_scan(self, src_ip: str) -> Optional[ThreatEvent]:
        """Detect port scanning attempts"""
        targets, ports, rate = self.connection_tracker.get_port_scan_score(src_ip)
        
        if ports > self.port_scan_threshold or rate > 50:  # 50 connections/minute
            severity = ThreatSeverity.HIGH if ports > 50 else ThreatSeverity.MEDIUM
            confidence = min(1.0, (ports / 100.0) + (rate / 100.0))
            
            return ThreatEvent(
                threat_type=ThreatType.PORT_SCAN,
                severity=severity,
                source_ip=src_ip,
                destination_ip="multiple",
                timestamp=datetime.now(),
                description=f"Port scan detected: {ports} ports, {targets} targets, {rate:.1f} conn/min",
                confidence=confidence,
                additional_data={
                    'ports_scanned': ports,
                    'targets': targets,
                    'scan_rate': rate
                }
            )
        
        return None
    
    def _detect_suspicious_ports(self, src_ip: str, dst_ip: str, dst_port: int) -> Optional[ThreatEvent]:
        """Detect connections to suspicious ports"""
        if dst_port in self.known_malware_ports:
            return ThreatEvent(
                threat_type=ThreatType.MALWARE_COMMUNICATION,
                severity=ThreatSeverity.HIGH,
                source_ip=src_ip,
                destination_ip=dst_ip,
                timestamp=datetime.now(),
                description=f"Connection to known malware port {dst_port}",
                confidence=0.8,
                additional_data={'port': dst_port}
            )
        
        return None
    
    def _detect_brute_force(self, src_ip: str, dst_ip: str, dst_port: int) -> Optional[ThreatEvent]:
        """Detect brute force attacks"""
        # Common brute force ports
        brute_force_ports = {22, 23, 21, 25, 110, 143, 993, 995, 3389, 5900}
        
        if dst_port in brute_force_ports:
            # Track failed attempts (simplified - in real implementation, 
            # this would analyze actual authentication failures)
            now = datetime.now()
            self.failed_logins[src_ip].append(now)
            
            # Clean old attempts
            cutoff = now - timedelta(minutes=10)
            self.failed_logins[src_ip] = [
                t for t in self.failed_logins[src_ip] if t > cutoff
            ]
            
            if len(self.failed_logins[src_ip]) > self.brute_force_threshold:
                return ThreatEvent(
                    threat_type=ThreatType.BRUTE_FORCE,
                    severity=ThreatSeverity.HIGH,
                    source_ip=src_ip,
                    destination_ip=dst_ip,
                    timestamp=now,
                    description=f"Brute force attack detected on port {dst_port}",
                    confidence=0.9,
                    additional_data={
                        'port': dst_port,
                        'attempts': len(self.failed_logins[src_ip])
                    }
                )
        
        return None
    
    def _detect_ddos(self, dst_ip: str) -> Optional[ThreatEvent]:
        """Detect DDoS attacks"""
        # This is a simplified DDoS detection
        # In practice, this would analyze traffic patterns more thoroughly
        if len(self.traffic_analyzer.packet_rates) > 0:
            current_rate = self.traffic_analyzer.packet_rates[-1]
            if current_rate > self.ddos_threshold:
                return ThreatEvent(
                    threat_type=ThreatType.DDoS_ATTACK,
                    severity=ThreatSeverity.CRITICAL,
                    source_ip="multiple",
                    destination_ip=dst_ip,
                    timestamp=datetime.now(),
                    description=f"DDoS attack detected: {current_rate} packets/sec",
                    confidence=0.7,
                    additional_data={'packet_rate': current_rate}
                )
        
        return None
    
    def _detect_malware_communication(self, src_ip: str, dst_ip: str, dst_port: int) -> Optional[ThreatEvent]:
        """Detect potential malware communication patterns"""
        # Check for communication with known bad IPs (simplified)
        suspicious_patterns = [
            dst_port in range(6660, 6670),  # IRC bot networks
            dst_port == 6667,  # IRC
            dst_port in {4444, 5555, 7777, 8888, 9999}  # Common backdoor ports
        ]
        
        if any(suspicious_patterns):
            return ThreatEvent(
                threat_type=ThreatType.MALWARE_COMMUNICATION,
                severity=ThreatSeverity.MEDIUM,
                source_ip=src_ip,
                destination_ip=dst_ip,
                timestamp=datetime.now(),
                description=f"Suspicious communication pattern detected on port {dst_port}",
                confidence=0.6,
                additional_data={'port': dst_port}
            )
        
        return None
    
    def _handle_threat(self, threat: ThreatEvent):
        """Handle detected threat"""
        self.detected_threats.append(threat)
        
        # Log the threat
        logging.warning(f"THREAT DETECTED: {threat.threat_type.value} - {threat.description}")
        
        # Notify callbacks
        for callback in self.threat_callbacks:
            try:
                callback(threat)
            except Exception as e:
                logging.error(f"Error in threat callback: {e}")
    
    def get_threat_summary(self) -> Dict[str, Any]:
        """Get summary of detected threats"""
        if not self.detected_threats:
            return {"total": 0, "by_type": {}, "by_severity": {}}
        
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        
        for threat in self.detected_threats:
            by_type[threat.threat_type.value] += 1
            by_severity[threat.severity.value] += 1
        
        return {
            "total": len(self.detected_threats),
            "by_type": dict(by_type),
            "by_severity": dict(by_severity),
            "latest": self.detected_threats[-10:]  # Latest 10 threats
        }
    
    def clear_old_threats(self, hours: int = 24):
        """Clear threats older than specified hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        self.detected_threats = [
            t for t in self.detected_threats if t.timestamp > cutoff
        ]

if __name__ == "__main__":
    # Test the threat detection system
    print("Testing Advanced Threat Detection System")
    print("=" * 50)
    
    # Mock config manager
    class MockConfig:
        def get(self, key, default):
            return default
    
    detector = AdvancedThreatDetector(MockConfig())
    
    # Test packet
    test_packet = {
        'src_ip': '192.168.1.100',
        'dst_ip': '8.8.8.8',
        'dst_port': 80,
        'protocol': 'TCP',
        'protocol_name': 'HTTP'
    }
    
    threat = detector.analyze_packet(test_packet)
    print(f"Test packet analysis: {threat}")
    
    # Test port scan
    for port in range(20, 30):
        scan_packet = {
            'src_ip': '192.168.1.200',
            'dst_ip': '192.168.1.1',
            'dst_port': port,
            'protocol': 'TCP',
            'protocol_name': 'TCP'
        }
        detector.analyze_packet(scan_packet)
    
    summary = detector.get_threat_summary()
    print(f"Threat summary: {summary}")
