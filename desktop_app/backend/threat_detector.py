"""
Enhanced Threat Detection Integration for CyberSnoop
Integrates both basic and advanced threat detection algorithms.
This module serves as the main interface for threat detection functionality.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
import threading
import statistics
import time

# Import the advanced threat detector
try:
    from .advanced_threat_detector import (
        AdvancedThreatDetector, 
        ThreatAlert, 
        ThreatSeverity as AdvancedThreatSeverity, 
        ThreatType as AdvancedThreatType
    )
    ADVANCED_DETECTOR_AVAILABLE = True
except ImportError:
    try:
        from advanced_threat_detector import (
            AdvancedThreatDetector, 
            ThreatAlert, 
            ThreatSeverity as AdvancedThreatSeverity, 
            ThreatType as AdvancedThreatType
        )
        ADVANCED_DETECTOR_AVAILABLE = True
    except ImportError:
        logging.warning("Advanced threat detector not available: import failed")
        ADVANCED_DETECTOR_AVAILABLE = False
    logging.info("Advanced threat detector available")
except ImportError as e:
    ADVANCED_DETECTOR_AVAILABLE = False
    logging.warning(f"Advanced threat detector not available: {e}")

# Legacy compatibility classes
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

class EnhancedThreatDetector:
    """Enhanced threat detector that combines basic and advanced detection"""
    
    def __init__(self, config_manager, database_manager=None):
        self.config = config_manager
        self.database = database_manager
        self.lock = threading.RLock()
        
        # Initialize advanced detector if available
        if ADVANCED_DETECTOR_AVAILABLE:
            try:
                self.advanced_detector = AdvancedThreatDetector(config_manager, database_manager)
                self.use_advanced = True
                logging.info("Using advanced threat detection engine")
            except Exception as e:
                logging.error(f"Failed to initialize advanced detector: {e}")
                self.advanced_detector = None
                self.use_advanced = False
        else:
            self.advanced_detector = None
            self.use_advanced = False
        
        # Initialize basic detection components
        self._init_basic_detection()
        
        logging.info("Enhanced Threat Detector initialized")
    
    def _init_basic_detection(self):
        """Initialize basic threat detection components"""
        # Connection tracking for basic detection
        self.connection_tracker = defaultdict(lambda: defaultdict(set))
        self.port_scan_tracking = defaultdict(lambda: {"ports": set(), "first_seen": None, "last_seen": None})
        self.brute_force_tracking = defaultdict(lambda: {"attempts": deque(), "target_ports": set()})
        self.traffic_volume = defaultdict(lambda: {"packets": deque(), "bytes": deque()})
        
        # Threat thresholds
        self.port_scan_threshold = self.config.get("threats.port_scan_threshold", 10)
        self.brute_force_threshold = self.config.get("threats.brute_force_threshold", 5)
        self.ddos_packet_threshold = self.config.get("threats.ddos_packet_threshold", 1000)
        self.time_window = self.config.get("threats.time_window_minutes", 5)
        
        # Suspicious ports
        self.suspicious_ports = {1337, 31337, 12345, 54321, 9999}
        
        # Recent threats (for deduplication)
        self.recent_threats = deque(maxlen=1000)
        self.threat_callbacks = []
    
    def analyze_packet(self, packet_info: Dict[str, Any]) -> List[Any]:
        """Analyze a packet for threats using both basic and advanced detection"""
        threats = []
        
        try:
            # Use advanced detector if available
            if self.use_advanced and self.advanced_detector:
                advanced_alerts = self.advanced_detector.analyze_packet(packet_info)
                
                # Convert advanced alerts to legacy format if needed
                for alert in advanced_alerts:
                    legacy_threat = self._convert_alert_to_legacy(alert)
                    if legacy_threat:
                        threats.append(legacy_threat)
            
            # Also run basic detection as fallback or supplementary
            basic_threat = self._analyze_packet_basic(packet_info)
            if basic_threat:
                threats.append(basic_threat)
        
        except Exception as e:
            logging.error(f"Error in threat analysis: {e}")
        
        return threats
    
    def _analyze_packet_basic(self, packet_info: Dict[str, Any]) -> Optional[ThreatEvent]:
        """Basic packet analysis for threats"""
        try:
            src_ip = packet_info.get("src_ip")
            dst_ip = packet_info.get("dst_ip")
            dst_port = packet_info.get("dst_port")
            
            if not all([src_ip, dst_ip]):
                return None
            
            # Update connection tracking
            self._update_tracking(src_ip, dst_ip, dst_port, packet_info)
            
            # Check for various threat types
            threat = None
            
            # Port scan detection
            if not threat:
                threat = self._detect_port_scan_basic(src_ip)
            
            # Suspicious port detection
            if not threat and dst_port:
                threat = self._detect_suspicious_ports_basic(src_ip, dst_ip, dst_port)
            
            # Brute force detection
            if not threat and dst_port:
                threat = self._detect_brute_force_basic(src_ip, dst_ip, dst_port)
            
            # DDoS detection
            if not threat:
                threat = self._detect_ddos_basic(dst_ip)
            
            if threat:
                self._handle_threat_basic(threat)
            
            return threat
            
        except Exception as e:
            logging.error(f"Error in basic packet analysis: {e}")
            return None
    
    def _update_tracking(self, src_ip: str, dst_ip: str, dst_port: Optional[int], packet_info: Dict[str, Any]):
        """Update tracking data structures"""
        current_time = datetime.utcnow()
        
        # Update connection tracking
        if dst_port:
            self.connection_tracker[src_ip][dst_ip].add(dst_port)
            
            # Update port scan tracking
            scan_data = self.port_scan_tracking[src_ip]
            scan_data["ports"].add((dst_ip, dst_port))
            if not scan_data["first_seen"]:
                scan_data["first_seen"] = current_time
            scan_data["last_seen"] = current_time
            
            # Update brute force tracking for common services
            if dst_port in [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389]:
                bf_key = f"{src_ip}:{dst_ip}:{dst_port}"
                self.brute_force_tracking[bf_key]["attempts"].append(current_time)
                self.brute_force_tracking[bf_key]["target_ports"].add(dst_port)
        
        # Update traffic volume tracking
        packet_size = packet_info.get("size", 0)
        self.traffic_volume[dst_ip]["packets"].append(current_time)
        self.traffic_volume[dst_ip]["bytes"].append(packet_size)
        
        # Clean old tracking data
        self._cleanup_old_tracking_data(current_time)
    
    def _detect_port_scan_basic(self, src_ip: str) -> Optional[ThreatEvent]:
        """Basic port scan detection"""
        scan_data = self.port_scan_tracking[src_ip]
        unique_ports = len(scan_data["ports"])
        
        if unique_ports >= self.port_scan_threshold:
            unique_targets = len(set(ip for ip, port in scan_data["ports"]))
            
            return ThreatEvent(
                threat_type=ThreatType.PORT_SCAN,
                severity=ThreatSeverity.HIGH if unique_ports > 50 else ThreatSeverity.MEDIUM,
                source_ip=src_ip,
                destination_ip="multiple" if unique_targets > 1 else list(scan_data["ports"])[0][0],
                timestamp=datetime.utcnow(),
                description=f"Port scan detected: {unique_ports} ports scanned on {unique_targets} targets",
                confidence=0.8 if unique_ports > 30 else 0.6,
                additional_data={
                    "scanned_ports": unique_ports,
                    "target_count": unique_targets,
                    "scan_duration": (scan_data["last_seen"] - scan_data["first_seen"]).seconds if scan_data["first_seen"] else 0
                }
            )
        
        return None
    
    def _detect_suspicious_ports_basic(self, src_ip: str, dst_ip: str, dst_port: int) -> Optional[ThreatEvent]:
        """Basic suspicious port detection"""
        if dst_port in self.suspicious_ports:
            return ThreatEvent(
                threat_type=ThreatType.SUSPICIOUS_TRAFFIC,
                severity=ThreatSeverity.MEDIUM,
                source_ip=src_ip,
                destination_ip=dst_ip,
                timestamp=datetime.utcnow(),
                description=f"Connection to suspicious port {dst_port}",
                confidence=0.7,
                additional_data={"suspicious_port": dst_port}
            )
        
        return None
    
    def _detect_brute_force_basic(self, src_ip: str, dst_ip: str, dst_port: int) -> Optional[ThreatEvent]:
        """Basic brute force detection"""
        bf_key = f"{src_ip}:{dst_ip}:{dst_port}"
        bf_data = self.brute_force_tracking[bf_key]
        
        # Clean old attempts
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(minutes=self.time_window)
        while bf_data["attempts"] and bf_data["attempts"][0] < cutoff_time:
            bf_data["attempts"].popleft()
        
        if len(bf_data["attempts"]) >= self.brute_force_threshold:
            service_name = self._get_service_name_basic(dst_port)
            
            return ThreatEvent(
                threat_type=ThreatType.BRUTE_FORCE,
                severity=ThreatSeverity.HIGH,
                source_ip=src_ip,
                destination_ip=dst_ip,
                timestamp=current_time,
                description=f"Brute force attack detected on {service_name} (port {dst_port})",
                confidence=0.9,
                additional_data={
                    "service": service_name,
                    "attempt_count": len(bf_data["attempts"]),
                    "target_port": dst_port
                }
            )
        
        return None
    
    def _detect_ddos_basic(self, dst_ip: str) -> Optional[ThreatEvent]:
        """Basic DDoS detection"""
        traffic_data = self.traffic_volume[dst_ip]
        
        # Clean old data
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(minutes=1)  # 1-minute window for DDoS
        
        while traffic_data["packets"] and traffic_data["packets"][0] < cutoff_time:
            traffic_data["packets"].popleft()
            traffic_data["bytes"].popleft()
        
        packet_count = len(traffic_data["packets"])
        
        if packet_count >= self.ddos_packet_threshold:
            total_bytes = sum(traffic_data["bytes"])
            
            return ThreatEvent(
                threat_type=ThreatType.DDoS_ATTACK,
                severity=ThreatSeverity.CRITICAL,
                source_ip="multiple",
                destination_ip=dst_ip,
                timestamp=current_time,
                description=f"DDoS attack detected: {packet_count} packets ({total_bytes} bytes) in 1 minute",
                confidence=0.85,
                additional_data={
                    "packet_count": packet_count,
                    "total_bytes": total_bytes,
                    "time_window": "1 minute"
                }
            )
        
        return None
    
    def _get_service_name_basic(self, port: int) -> str:
        """Get service name for a port"""
        common_ports = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
            443: "HTTPS", 993: "IMAPS", 995: "POP3S", 3389: "RDP"
        }
        return common_ports.get(port, f"Port {port}")
    
    def _cleanup_old_tracking_data(self, current_time: datetime):
        """Clean up old tracking data"""
        cutoff_time = current_time - timedelta(minutes=30)
        
        # Clean port scan tracking
        for src_ip in list(self.port_scan_tracking.keys()):
            scan_data = self.port_scan_tracking[src_ip]
            if scan_data["last_seen"] and scan_data["last_seen"] < cutoff_time:
                del self.port_scan_tracking[src_ip]
        
        # Clean brute force tracking
        for key in list(self.brute_force_tracking.keys()):
            bf_data = self.brute_force_tracking[key]
            while bf_data["attempts"] and bf_data["attempts"][0] < cutoff_time:
                bf_data["attempts"].popleft()
            if not bf_data["attempts"]:
                del self.brute_force_tracking[key]
    
    def _handle_threat_basic(self, threat: ThreatEvent):
        """Handle a detected threat"""
        try:
            # Add to recent threats
            self.recent_threats.append(threat)
            
            # Store in database if available
            if self.database:
                threat_data = {
                    "timestamp": threat.timestamp.isoformat(),
                    "type": threat.threat_type.value,
                    "severity": threat.severity.value,
                    "source_ip": threat.source_ip,
                    "destination_ip": threat.destination_ip,
                    "description": threat.description,
                    "confidence": threat.confidence,
                    "additional_data": threat.additional_data
                }
                self.database.store_threat(threat_data)
            
            # Trigger callbacks
            for callback in self.threat_callbacks:
                try:
                    callback(threat)
                except Exception as e:
                    logging.error(f"Error in threat callback: {e}")
            
            logging.warning(f"Threat detected: {threat.description}")
            
        except Exception as e:
            logging.error(f"Error handling threat: {e}")
    
    def _convert_alert_to_legacy(self, alert: 'ThreatAlert') -> Optional[ThreatEvent]:
        """Convert advanced threat alert to legacy threat event"""
        try:
            # Map advanced severity to legacy severity
            severity_map = {
                AdvancedThreatSeverity.LOW: ThreatSeverity.LOW,
                AdvancedThreatSeverity.MEDIUM: ThreatSeverity.MEDIUM,
                AdvancedThreatSeverity.HIGH: ThreatSeverity.HIGH,
                AdvancedThreatSeverity.CRITICAL: ThreatSeverity.CRITICAL
            }
            
            # Map advanced threat type to legacy threat type
            type_map = {
                AdvancedThreatType.PORT_SCAN: ThreatType.PORT_SCAN,
                AdvancedThreatType.BRUTE_FORCE: ThreatType.BRUTE_FORCE,
                AdvancedThreatType.DDOS: ThreatType.DDoS_ATTACK,
                AdvancedThreatType.MALWARE_COMMUNICATION: ThreatType.MALWARE_COMMUNICATION,
                AdvancedThreatType.DATA_EXFILTRATION: ThreatType.DATA_EXFILTRATION,
                AdvancedThreatType.ANOMALY: ThreatType.ANOMALY,
                AdvancedThreatType.SUSPICIOUS_DNS: ThreatType.SUSPICIOUS_TRAFFIC,
                AdvancedThreatType.INTRUSION_ATTEMPT: ThreatType.SUSPICIOUS_TRAFFIC
            }
            
            return ThreatEvent(
                threat_type=type_map.get(alert.threat_type, ThreatType.SUSPICIOUS_TRAFFIC),
                severity=severity_map.get(alert.severity, ThreatSeverity.MEDIUM),
                source_ip=alert.source_ip,
                destination_ip=alert.destination_ip or "unknown",
                timestamp=alert.timestamp,
                description=alert.description,
                confidence=alert.confidence,
                additional_data=alert.raw_data or {}
            )
            
        except Exception as e:
            logging.error(f"Error converting alert to legacy format: {e}")
            return None
    
    def add_threat_callback(self, callback):
        """Add callback for threat notifications"""
        self.threat_callbacks.append(callback)
        
        # Also add to advanced detector if available
        if self.advanced_detector:
            try:
                self.advanced_detector.add_alert_callback(lambda alert: callback(self._convert_alert_to_legacy(alert)))
            except Exception as e:
                logging.error(f"Error adding callback to advanced detector: {e}")
    
    def get_recent_threats(self, limit: int = 50) -> List[ThreatEvent]:
        """Get recent threats"""
        threats = list(self.recent_threats)[-limit:]
        
        # Also get from advanced detector if available
        if self.advanced_detector:
            try:
                advanced_alerts = self.advanced_detector.get_recent_alerts(limit)
                for alert in advanced_alerts:
                    legacy_threat = self._convert_alert_to_legacy(alert)
                    if legacy_threat:
                        threats.append(legacy_threat)
            except Exception as e:
                logging.error(f"Error getting advanced threats: {e}")
        
        # Sort by timestamp and return latest
        threats.sort(key=lambda t: t.timestamp, reverse=True)
        return threats[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get threat detection statistics"""
        stats = {
            "basic_threats_detected": len(self.recent_threats),
            "advanced_detector_available": ADVANCED_DETECTOR_AVAILABLE,
            "using_advanced_detection": self.use_advanced
        }
        
        if self.advanced_detector:
            try:
                advanced_stats = self.advanced_detector.get_detection_statistics()
                stats["advanced_stats"] = advanced_stats
            except Exception as e:
                logging.error(f"Error getting advanced stats: {e}")
        
        return stats
    
    def update_configuration(self, new_config: Dict[str, Any]):
        """Update threat detection configuration"""
        try:
            # Update basic thresholds
            if "port_scan_threshold" in new_config:
                self.port_scan_threshold = new_config["port_scan_threshold"]
            if "brute_force_threshold" in new_config:
                self.brute_force_threshold = new_config["brute_force_threshold"]
            if "ddos_packet_threshold" in new_config:
                self.ddos_packet_threshold = new_config["ddos_packet_threshold"]
            
            # Update advanced detector configuration
            if self.advanced_detector and "advanced_thresholds" in new_config:
                self.advanced_detector.update_thresholds(new_config["advanced_thresholds"])
            
            logging.info("Threat detection configuration updated")
            
        except Exception as e:
            logging.error(f"Error updating threat detection configuration: {e}")
    
    def close(self):
        """Clean up resources"""
        try:
            if self.advanced_detector:
                self.advanced_detector.close()
            logging.info("Enhanced Threat Detector closed")
        except Exception as e:
            logging.error(f"Error closing threat detector: {e}")

# Compatibility alias
ThreatDetector = EnhancedThreatDetector

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
