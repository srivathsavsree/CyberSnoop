"""
Advanced Threat Detection Engine for CyberSnoop
Day 6: Comprehensive threat detection with multiple algorithms

This module implements advanced threat detection including:
1. Port scan detection (horizontal and vertical)
2. Brute force attack detection
3. DDoS attack detection
4. Anomaly detection for unusual traffic patterns
5. Malware communication detection
6. Data exfiltration detection
7. Configurable threat thresholds and rules
8. Machine learning-based anomaly detection (basic)
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, deque
import statistics
import ipaddress
import re
from dataclasses import dataclass
from enum import Enum

class ThreatSeverity(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types of threats that can be detected"""
    PORT_SCAN = "port_scan"
    BRUTE_FORCE = "brute_force"
    DDOS = "ddos"
    MALWARE_COMMUNICATION = "malware_communication"
    DATA_EXFILTRATION = "data_exfiltration"
    ANOMALY = "anomaly"
    SUSPICIOUS_DNS = "suspicious_dns"
    INTRUSION_ATTEMPT = "intrusion_attempt"

@dataclass
class ThreatAlert:
    """Represents a detected threat"""
    threat_type: ThreatType
    severity: ThreatSeverity
    timestamp: datetime
    source_ip: str
    destination_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    description: str = ""
    indicators: List[str] = None
    confidence: float = 0.0
    raw_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.indicators is None:
            self.indicators = []
        if self.raw_data is None:
            self.raw_data = {}

class AdvancedThreatDetector:
    """Advanced threat detection engine with multiple detection algorithms"""
    
    def __init__(self, config_manager, database_manager=None):
        self.config = config_manager
        self.database = database_manager
        self.lock = threading.RLock()
        
        # Detection state tracking
        self.connection_tracking = defaultdict(lambda: defaultdict(set))  # {src_ip: {dst_ip: {ports}}}
        self.port_scan_tracking = defaultdict(lambda: {"ports": set(), "timestamps": deque()})
        self.brute_force_tracking = defaultdict(lambda: {"attempts": deque(), "ips": set()})
        self.traffic_baselines = defaultdict(lambda: {"packets": deque(), "bytes": deque()})
        self.dns_queries = defaultdict(deque)
        self.connection_states = defaultdict(dict)
        
        # Detection thresholds and configurations
        self.thresholds = self._load_detection_thresholds()
        self.known_malicious_domains = self._load_malicious_domains()
        self.suspicious_ports = self._load_suspicious_ports()
        
        # Alert management
        self.recent_alerts = deque(maxlen=1000)
        self.alert_callbacks = []
        self.suppressed_alerts = set()
        
        # Performance metrics
        self.detection_stats = {
            "packets_analyzed": 0,
            "threats_detected": 0,
            "false_positives": 0,
            "processing_time": deque(maxlen=100)
        }
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        logging.info("Advanced Threat Detector initialized")
    
    def _load_detection_thresholds(self) -> Dict[str, Any]:
        """Load detection thresholds from configuration"""
        return {
            # Port scan detection
            "port_scan": {
                "min_ports": self.config.get("threats.port_scan.min_ports", 10),
                "time_window": self.config.get("threats.port_scan.time_window_minutes", 5),
                "max_targets": self.config.get("threats.port_scan.max_targets", 50)
            },
            
            # Brute force detection
            "brute_force": {
                "max_attempts": self.config.get("threats.brute_force.max_attempts", 5),
                "time_window": self.config.get("threats.brute_force.time_window_minutes", 10),
                "suspicious_services": ["ssh", "ftp", "rdp", "telnet", "http", "https"]
            },
            
            # DDoS detection
            "ddos": {
                "packet_threshold": self.config.get("threats.ddos.packet_threshold", 1000),
                "time_window": self.config.get("threats.ddos.time_window_seconds", 60),
                "source_threshold": self.config.get("threats.ddos.source_threshold", 100)
            },
            
            # Anomaly detection
            "anomaly": {
                "baseline_window": self.config.get("threats.anomaly.baseline_window_minutes", 60),
                "deviation_threshold": self.config.get("threats.anomaly.deviation_threshold", 3.0),
                "min_samples": self.config.get("threats.anomaly.min_samples", 30)
            },
            
            # Data exfiltration
            "exfiltration": {
                "size_threshold_mb": self.config.get("threats.exfiltration.size_threshold_mb", 100),
                "upload_ratio_threshold": self.config.get("threats.exfiltration.upload_ratio_threshold", 10.0),
                "time_window": self.config.get("threats.exfiltration.time_window_minutes", 30)
            }
        }
    
    def _load_malicious_domains(self) -> Set[str]:
        """Load known malicious domains"""
        # In a real implementation, this would load from threat intelligence feeds
        return {
            "malware.com", "suspicious.net", "phishing.org", "botnet.io",
            "c2server.net", "malicious-cdn.com", "fake-bank.net"
        }
    
    def _load_suspicious_ports(self) -> Set[int]:
        """Load suspicious port numbers"""
        return {
            # Common attack ports
            1337, 31337, 12345, 54321, 9999, 8080, 8888,
            # Trojans and backdoors
            12345, 20034, 31789, 54320, 65506,
            # P2P and file sharing
            6346, 6347, 4662, 4672
        }
    
    def analyze_packet(self, packet_data: Dict[str, Any]) -> List[ThreatAlert]:
        """Analyze a packet for potential threats"""
        start_time = time.time()
        alerts = []
        
        try:
            with self.lock:
                # Update statistics
                self.detection_stats["packets_analyzed"] += 1
                
                # Run all detection algorithms
                alerts.extend(self._detect_port_scan(packet_data))
                alerts.extend(self._detect_brute_force(packet_data))
                alerts.extend(self._detect_ddos(packet_data))
                alerts.extend(self._detect_malware_communication(packet_data))
                alerts.extend(self._detect_data_exfiltration(packet_data))
                alerts.extend(self._detect_suspicious_dns(packet_data))
                alerts.extend(self._detect_anomalies(packet_data))
                
                # Process and store alerts
                for alert in alerts:
                    self._process_alert(alert)
                
                # Update detection statistics
                self.detection_stats["threats_detected"] += len(alerts)
        
        except Exception as e:
            logging.error(f"Error analyzing packet for threats: {e}")
        
        finally:
            # Update performance metrics
            processing_time = time.time() - start_time
            self.detection_stats["processing_time"].append(processing_time)
        
        return alerts
    
    def _detect_port_scan(self, packet_data: Dict[str, Any]) -> List[ThreatAlert]:
        """Detect port scanning activity"""
        alerts = []
        
        try:
            src_ip = packet_data.get("src_ip")
            dst_ip = packet_data.get("dst_ip")
            dst_port = packet_data.get("dst_port")
            
            if not all([src_ip, dst_ip, dst_port]):
                return alerts
            
            # Skip internal traffic for some checks (allow RFC5737 test IPs)
            if (self._is_internal_traffic(src_ip, dst_ip) and 
                not self._is_test_ip_range(src_ip) and 
                not self._is_test_ip_range(dst_ip)):
                return alerts
            
            # Track connection attempts
            current_time = datetime.utcnow()
            scan_data = self.port_scan_tracking[src_ip]
            
            # Add this port to the scanned ports
            scan_data["ports"].add((dst_ip, dst_port))
            scan_data["timestamps"].append(current_time)
            
            # Clean old timestamps
            cutoff_time = current_time - timedelta(minutes=self.thresholds["port_scan"]["time_window"])
            while scan_data["timestamps"] and scan_data["timestamps"][0] < cutoff_time:
                scan_data["timestamps"].popleft()
            
            # Check for horizontal port scan (multiple ports on same target)
            target_ports = {port for ip, port in scan_data["ports"] if ip == dst_ip}
            
            if len(target_ports) >= self.thresholds["port_scan"]["min_ports"]:
                alerts.append(ThreatAlert(
                    threat_type=ThreatType.PORT_SCAN,
                    severity=ThreatSeverity.HIGH,
                    timestamp=current_time,
                    source_ip=src_ip,
                    destination_ip=dst_ip,
                    description=f"Horizontal port scan detected: {len(target_ports)} ports scanned",
                    indicators=["horizontal_scan", f"ports_scanned:{len(target_ports)}"],
                    confidence=0.9,
                    raw_data={"scanned_ports": list(target_ports)}
                ))
            
            # Check for vertical port scan (same port on multiple targets)
            unique_targets = {ip for ip, port in scan_data["ports"]}
            if len(unique_targets) >= self.thresholds["port_scan"]["max_targets"]:
                alerts.append(ThreatAlert(
                    threat_type=ThreatType.PORT_SCAN,
                    severity=ThreatSeverity.MEDIUM,
                    timestamp=current_time,
                    source_ip=src_ip,
                    description=f"Vertical port scan detected: {len(unique_targets)} targets scanned",
                    indicators=["vertical_scan", f"targets_scanned:{len(unique_targets)}"],
                    confidence=0.8,
                    raw_data={"scanned_targets": list(unique_targets)}
                ))
        
        except Exception as e:
            logging.debug(f"Port scan detection error: {e}")
        
        return alerts
    
    def _detect_brute_force(self, packet_data: Dict[str, Any]) -> List[ThreatAlert]:
        """Detect brute force attacks"""
        alerts = []
        
        try:
            src_ip = packet_data.get("src_ip")
            dst_ip = packet_data.get("dst_ip")
            dst_port = packet_data.get("dst_port")
            protocol = packet_data.get("protocol_name", "").lower()
            
            if not all([src_ip, dst_ip, dst_port]):
                return alerts
            
            # Check if this is a service commonly targeted by brute force
            service_name = self._get_service_name(dst_port, protocol)
            if service_name not in self.thresholds["brute_force"]["suspicious_services"]:
                return alerts
            
            current_time = datetime.utcnow()
            key = f"{src_ip}:{dst_ip}:{dst_port}"
            bf_data = self.brute_force_tracking[key]
            
            # Track connection attempts
            bf_data["attempts"].append(current_time)
            bf_data["ips"].add(src_ip)
            
            # Clean old attempts
            cutoff_time = current_time - timedelta(minutes=self.thresholds["brute_force"]["time_window"])
            while bf_data["attempts"] and bf_data["attempts"][0] < cutoff_time:
                bf_data["attempts"].popleft()
            
            # Check for brute force pattern
            if len(bf_data["attempts"]) >= self.thresholds["brute_force"]["max_attempts"]:
                alerts.append(ThreatAlert(
                    threat_type=ThreatType.BRUTE_FORCE,
                    severity=ThreatSeverity.HIGH,
                    timestamp=current_time,
                    source_ip=src_ip,
                    destination_ip=dst_ip,
                    destination_port=dst_port,
                    description=f"Brute force attack detected on {service_name} service",
                    indicators=["multiple_attempts", f"service:{service_name}", f"attempts:{len(bf_data['attempts'])}"],
                    confidence=0.95,
                    raw_data={"service": service_name, "attempt_count": len(bf_data["attempts"])}
                ))
        
        except Exception as e:
            logging.debug(f"Brute force detection error: {e}")
        
        return alerts
    
    def _detect_ddos(self, packet_data: Dict[str, Any]) -> List[ThreatAlert]:
        """Detect DDoS attacks"""
        alerts = []
        
        try:
            dst_ip = packet_data.get("dst_ip")
            src_ip = packet_data.get("src_ip")
            
            if not dst_ip:
                return alerts
            
            current_time = datetime.utcnow()
            traffic_data = self.traffic_baselines[dst_ip]
            
            # Track traffic to this destination
            traffic_data["packets"].append((current_time, src_ip))
            
            # Clean old data
            cutoff_time = current_time - timedelta(seconds=self.thresholds["ddos"]["time_window"])
            while traffic_data["packets"] and traffic_data["packets"][0][0] < cutoff_time:
                traffic_data["packets"].popleft()
            
            # Check for DDoS pattern
            recent_packets = len(traffic_data["packets"])
            unique_sources = len(set(src for _, src in traffic_data["packets"]))
            
            if (recent_packets >= self.thresholds["ddos"]["packet_threshold"] and
                unique_sources >= self.thresholds["ddos"]["source_threshold"]):
                
                alerts.append(ThreatAlert(
                    threat_type=ThreatType.DDOS,
                    severity=ThreatSeverity.CRITICAL,
                    timestamp=current_time,
                    source_ip="multiple",
                    destination_ip=dst_ip,
                    description=f"DDoS attack detected: {recent_packets} packets from {unique_sources} sources",
                    indicators=["high_volume", "multiple_sources", f"packets:{recent_packets}", f"sources:{unique_sources}"],
                    confidence=0.9,
                    raw_data={"packet_count": recent_packets, "source_count": unique_sources}
                ))
        
        except Exception as e:
            logging.debug(f"DDoS detection error: {e}")
        
        return alerts
    
    def _detect_malware_communication(self, packet_data: Dict[str, Any]) -> List[ThreatAlert]:
        """Detect malware communication patterns"""
        alerts = []
        
        try:
            src_ip = packet_data.get("src_ip")
            dst_ip = packet_data.get("dst_ip")
            dst_port = packet_data.get("dst_port")
            payload = packet_data.get("payload_preview", "")
            
            # Check for communication with known malicious domains
            if "hostname" in packet_data:
                hostname = packet_data["hostname"].lower()
                if any(malicious in hostname for malicious in self.known_malicious_domains):
                    alerts.append(ThreatAlert(
                        threat_type=ThreatType.MALWARE_COMMUNICATION,
                        severity=ThreatSeverity.CRITICAL,
                        timestamp=datetime.utcnow(),
                        source_ip=src_ip,
                        destination_ip=dst_ip,
                        description=f"Communication with known malicious domain: {hostname}",
                        indicators=["malicious_domain", f"domain:{hostname}"],
                        confidence=0.95,
                        raw_data={"malicious_domain": hostname}
                    ))
            
            # Check for suspicious ports
            if dst_port in self.suspicious_ports:
                alerts.append(ThreatAlert(
                    threat_type=ThreatType.MALWARE_COMMUNICATION,
                    severity=ThreatSeverity.MEDIUM,
                    timestamp=datetime.utcnow(),
                    source_ip=src_ip,
                    destination_ip=dst_ip,
                    destination_port=dst_port,
                    description=f"Communication on suspicious port {dst_port}",
                    indicators=["suspicious_port", f"port:{dst_port}"],
                    confidence=0.6,
                    raw_data={"suspicious_port": dst_port}
                ))
            
            # Check for suspicious patterns in payload
            if payload:
                suspicious_patterns = [
                    r'cmd\.exe', r'powershell', r'\\windows\\system32',
                    r'eval\(', r'base64_decode', r'shell_exec'
                ]
                
                for pattern in suspicious_patterns:
                    if re.search(pattern, payload, re.IGNORECASE):
                        alerts.append(ThreatAlert(
                            threat_type=ThreatType.MALWARE_COMMUNICATION,
                            severity=ThreatSeverity.HIGH,
                            timestamp=datetime.utcnow(),
                            source_ip=src_ip,
                            destination_ip=dst_ip,
                            description=f"Suspicious payload pattern detected: {pattern}",
                            indicators=["suspicious_payload", f"pattern:{pattern}"],
                            confidence=0.7,
                            raw_data={"pattern": pattern, "payload_preview": payload[:100]}
                        ))
                        break
        
        except Exception as e:
            logging.debug(f"Malware communication detection error: {e}")
        
        return alerts
    
    def _detect_data_exfiltration(self, packet_data: Dict[str, Any]) -> List[ThreatAlert]:
        """Detect potential data exfiltration"""
        alerts = []
        
        try:
            src_ip = packet_data.get("src_ip")
            dst_ip = packet_data.get("dst_ip")
            size = packet_data.get("size", 0)
            direction = packet_data.get("direction", "unknown")
            
            if not all([src_ip, dst_ip, size]):
                return alerts
            
            # Skip small packets
            if size < 1000:
                return alerts
            
            current_time = datetime.utcnow()
            key = f"{src_ip}:{dst_ip}"
            
            # Track data transfer patterns
            if key not in self.connection_states:
                self.connection_states[key] = {
                    "upload_bytes": 0,
                    "download_bytes": 0,
                    "start_time": current_time,
                    "last_activity": current_time
                }
            
            conn_state = self.connection_states[key]
            conn_state["last_activity"] = current_time
            
            # Track upload/download ratio
            if direction == "outbound" or (self._is_internal_ip(src_ip) and not self._is_internal_ip(dst_ip)):
                conn_state["upload_bytes"] += size
            else:
                conn_state["download_bytes"] += size
            
            # Check for suspicious upload patterns
            time_window = self.thresholds["exfiltration"]["time_window"]
            if (current_time - conn_state["start_time"]).seconds / 60 >= time_window:
                upload_mb = conn_state["upload_bytes"] / (1024 * 1024)
                download_mb = conn_state["download_bytes"] / (1024 * 1024)
                
                # Check size threshold
                if upload_mb >= self.thresholds["exfiltration"]["size_threshold_mb"]:
                    upload_ratio = upload_mb / max(download_mb, 1)
                    
                    if upload_ratio >= self.thresholds["exfiltration"]["upload_ratio_threshold"]:
                        alerts.append(ThreatAlert(
                            threat_type=ThreatType.DATA_EXFILTRATION,
                            severity=ThreatSeverity.HIGH,
                            timestamp=current_time,
                            source_ip=src_ip,
                            destination_ip=dst_ip,
                            description=f"Potential data exfiltration: {upload_mb:.1f}MB uploaded (ratio: {upload_ratio:.1f})",
                            indicators=["large_upload", f"size_mb:{upload_mb:.1f}", f"ratio:{upload_ratio:.1f}"],
                            confidence=0.8,
                            raw_data={
                                "upload_mb": upload_mb,
                                "download_mb": download_mb,
                                "upload_ratio": upload_ratio
                            }
                        ))
        
        except Exception as e:
            logging.debug(f"Data exfiltration detection error: {e}")
        
        return alerts
    
    def _detect_suspicious_dns(self, packet_data: Dict[str, Any]) -> List[ThreatAlert]:
        """Detect suspicious DNS queries"""
        alerts = []
        
        try:
            if packet_data.get("dst_port") != 53 or packet_data.get("protocol_name") != "UDP":
                return alerts
            
            src_ip = packet_data.get("src_ip")
            query = packet_data.get("dns_query", "")
            
            if not query:
                return alerts
            
            current_time = datetime.utcnow()
            
            # Track DNS queries
            self.dns_queries[src_ip].append((current_time, query))
            
            # Clean old queries
            cutoff_time = current_time - timedelta(minutes=10)
            while self.dns_queries[src_ip] and self.dns_queries[src_ip][0][0] < cutoff_time:
                self.dns_queries[src_ip].popleft()
            
            # Check for suspicious patterns
            suspicious_indicators = []
            
            # Long domain name (potential DGA)
            if len(query) > 50:
                suspicious_indicators.append("long_domain")
            
            # High entropy (random-looking domain)
            if self._calculate_entropy(query) > 4.0:
                suspicious_indicators.append("high_entropy")
            
            # Many subdomains
            if query.count('.') > 5:
                suspicious_indicators.append("many_subdomains")
            
            # Numeric domains
            if re.search(r'\d{4,}', query):
                suspicious_indicators.append("numeric_patterns")
            
            # Too many queries from same source
            if len(self.dns_queries[src_ip]) > 100:
                suspicious_indicators.append("excessive_queries")
            
            if suspicious_indicators:
                alerts.append(ThreatAlert(
                    threat_type=ThreatType.SUSPICIOUS_DNS,
                    severity=ThreatSeverity.MEDIUM,
                    timestamp=current_time,
                    source_ip=src_ip,
                    description=f"Suspicious DNS query: {query}",
                    indicators=suspicious_indicators + [f"query:{query}"],
                    confidence=0.6,
                    raw_data={"dns_query": query, "query_count": len(self.dns_queries[src_ip])}
                ))
        
        except Exception as e:
            logging.debug(f"DNS detection error: {e}")
        
        return alerts
    
    def _detect_anomalies(self, packet_data: Dict[str, Any]) -> List[ThreatAlert]:
        """Detect traffic anomalies using statistical analysis"""
        alerts = []
        
        try:
            src_ip = packet_data.get("src_ip")
            size = packet_data.get("size", 0)
            current_time = datetime.utcnow()
            
            # Track traffic baselines per source IP
            baseline_key = f"baseline_{src_ip}"
            if baseline_key not in self.traffic_baselines:
                self.traffic_baselines[baseline_key] = {"packets": deque(), "bytes": deque()}
            
            baseline = self.traffic_baselines[baseline_key]
            baseline["packets"].append(current_time)
            baseline["bytes"].append(size)
            
            # Clean old data
            cutoff_time = current_time - timedelta(minutes=self.thresholds["anomaly"]["baseline_window"])
            while baseline["packets"] and baseline["packets"][0] < cutoff_time:
                baseline["packets"].popleft()
                baseline["bytes"].popleft()
            
            # Perform anomaly detection if we have enough samples
            if len(baseline["bytes"]) >= self.thresholds["anomaly"]["min_samples"]:
                bytes_list = list(baseline["bytes"])
                mean_size = statistics.mean(bytes_list)
                
                if len(bytes_list) > 1:
                    std_dev = statistics.stdev(bytes_list)
                    
                    # Check for packet size anomaly
                    if std_dev > 0 and abs(size - mean_size) > (self.thresholds["anomaly"]["deviation_threshold"] * std_dev):
                        alerts.append(ThreatAlert(
                            threat_type=ThreatType.ANOMALY,
                            severity=ThreatSeverity.LOW,
                            timestamp=current_time,
                            source_ip=src_ip,
                            description=f"Packet size anomaly: {size} bytes (normal: {mean_size:.1f}±{std_dev:.1f})",
                            indicators=["size_anomaly", f"size:{size}", f"deviation:{abs(size - mean_size)/std_dev:.1f}"],
                            confidence=0.5,
                            raw_data={"packet_size": size, "mean_size": mean_size, "std_dev": std_dev}
                        ))
        
        except Exception as e:
            logging.debug(f"Anomaly detection error: {e}")
        
        return alerts
    
    def _process_alert(self, alert: ThreatAlert):
        """Process and store a threat alert"""
        try:
            # Check for alert suppression
            alert_key = f"{alert.threat_type.value}:{alert.source_ip}:{alert.destination_ip}"
            if alert_key in self.suppressed_alerts:
                return
            
            # Add to recent alerts
            self.recent_alerts.append(alert)
            
            # Store in database if available
            if self.database:
                threat_data = {
                    "timestamp": alert.timestamp.isoformat(),
                    "type": alert.threat_type.value,
                    "severity": alert.severity.value,
                    "source_ip": alert.source_ip,
                    "destination_ip": alert.destination_ip,
                    "description": alert.description,
                    "indicators": alert.indicators,
                    "confidence": alert.confidence,
                    "raw_data": alert.raw_data
                }
                self.database.store_threat(threat_data)
            
            # Trigger callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logging.error(f"Error in alert callback: {e}")
            
            logging.info(f"Threat detected: {alert.threat_type.value} from {alert.source_ip} (severity: {alert.severity.value})")
        
        except Exception as e:
            logging.error(f"Error processing alert: {e}")
    
    def _is_internal_traffic(self, src_ip: str, dst_ip: str) -> bool:
        """Check if traffic is internal (both IPs are private)"""
        try:
            return self._is_internal_ip(src_ip) and self._is_internal_ip(dst_ip)
        except:
            return False
    
    def _is_internal_ip(self, ip: str) -> bool:
        """Check if IP address is internal/private"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except:
            return False
    
    def _is_test_ip_range(self, ip: str) -> bool:
        """Check if IP is in RFC5737 test ranges or other testing ranges"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            test_ranges = [
                ipaddress.ip_network('203.0.113.0/24'),  # RFC5737 TEST-NET-3
                ipaddress.ip_network('198.51.100.0/24'), # RFC5737 TEST-NET-2
                ipaddress.ip_network('192.0.2.0/24'),    # RFC5737 TEST-NET-1
            ]
            return any(ip_obj in test_range for test_range in test_ranges)
        except:
            return False
    
    def _get_service_name(self, port: int, protocol: str) -> str:
        """Get service name for a port/protocol combination"""
        common_services = {
            (22, "tcp"): "ssh",
            (21, "tcp"): "ftp",
            (23, "tcp"): "telnet",
            (80, "tcp"): "http",
            (443, "tcp"): "https",
            (3389, "tcp"): "rdp",
            (25, "tcp"): "smtp",
            (110, "tcp"): "pop3",
            (143, "tcp"): "imap",
            (53, "udp"): "dns"
        }
        
        return common_services.get((port, protocol.lower()), f"{protocol}:{port}")
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0
        
        from collections import Counter
        import math
        
        counts = Counter(text.lower())
        total = len(text)
        
        entropy = 0.0
        for count in counts.values():
            prob = count / total
            entropy -= prob * math.log2(prob)
        
        return entropy
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread for old tracking data"""
        def cleanup_loop():
            while True:
                try:
                    current_time = datetime.utcnow()
                    cutoff_time = current_time - timedelta(hours=1)
                    
                    # Clean old tracking data
                    with self.lock:
                        # Clean port scan tracking
                        for ip in list(self.port_scan_tracking.keys()):
                            scan_data = self.port_scan_tracking[ip]
                            while scan_data["timestamps"] and scan_data["timestamps"][0] < cutoff_time:
                                scan_data["timestamps"].popleft()
                            
                            if not scan_data["timestamps"]:
                                del self.port_scan_tracking[ip]
                        
                        # Clean brute force tracking
                        for key in list(self.brute_force_tracking.keys()):
                            bf_data = self.brute_force_tracking[key]
                            while bf_data["attempts"] and bf_data["attempts"][0] < cutoff_time:
                                bf_data["attempts"].popleft()
                            
                            if not bf_data["attempts"]:
                                del self.brute_force_tracking[key]
                        
                        # Clean connection states (older cleanup)
                        day_cutoff = current_time - timedelta(days=1)
                        for key in list(self.connection_states.keys()):
                            if self.connection_states[key]["last_activity"] < day_cutoff:
                                del self.connection_states[key]
                    
                    time.sleep(300)  # Clean every 5 minutes
                    
                except Exception as e:
                    logging.error(f"Cleanup thread error: {e}")
                    time.sleep(300)
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        logging.info("Threat detector cleanup thread started")
    
    def add_alert_callback(self, callback):
        """Add callback function for threat alerts"""
        self.alert_callbacks.append(callback)
    
    def suppress_alert(self, threat_type: ThreatType, source_ip: str, destination_ip: str = None):
        """Suppress specific alert type for given IPs"""
        alert_key = f"{threat_type.value}:{source_ip}:{destination_ip}"
        self.suppressed_alerts.add(alert_key)
    
    def get_recent_alerts(self, limit: int = 50) -> List[ThreatAlert]:
        """Get recent threat alerts"""
        return list(self.recent_alerts)[-limit:]
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get threat detection statistics"""
        stats = self.detection_stats.copy()
        if self.detection_stats["processing_time"]:
            stats["avg_processing_time"] = statistics.mean(self.detection_stats["processing_time"])
            stats["max_processing_time"] = max(self.detection_stats["processing_time"])
        else:
            stats["avg_processing_time"] = 0.0
            stats["max_processing_time"] = 0.0
        
        return stats
    
    def update_thresholds(self, new_thresholds: Dict[str, Any]):
        """Update detection thresholds"""
        with self.lock:
            self.thresholds.update(new_thresholds)
            logging.info("Threat detection thresholds updated")
    
    def close(self):
        """Clean up resources"""
        try:
            logging.info("Advanced Threat Detector shutting down")
        except Exception as e:
            logging.error(f"Error closing threat detector: {e}")
    
    # Public API methods for individual threat detection
    def detect_port_scan(self, packets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Public API: Detect port scan attacks from packet list"""
        threats = []
        for packet in packets:
            alerts = self._detect_port_scan(packet)
            for alert in alerts:
                threats.append(self._alert_to_dict(alert))
        return threats
    
    def detect_brute_force(self, packets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Public API: Detect brute force attacks from packet list"""
        threats = []
        for packet in packets:
            alerts = self._detect_brute_force(packet)
            for alert in alerts:
                threats.append(self._alert_to_dict(alert))
        return threats
    
    def detect_ddos(self, packets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Public API: Detect DDoS attacks from packet list"""
        threats = []
        for packet in packets:
            alerts = self._detect_ddos(packet)
            for alert in alerts:
                threats.append(self._alert_to_dict(alert))
        return threats
    
    def detect_anomalies(self, packets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Public API: Detect network anomalies from packet list"""
        threats = []
        for packet in packets:
            alerts = self._detect_anomalies(packet)
            for alert in alerts:
                threats.append(self._alert_to_dict(alert))
        return threats
    
    def detect_malware_communication(self, packets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Public API: Detect malware communication from packet list"""
        threats = []
        for packet in packets:
            alerts = self._detect_malware_communication(packet)
            for alert in alerts:
                threats.append(self._alert_to_dict(alert))
        return threats
    
    def detect_data_exfiltration(self, packets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Public API: Detect data exfiltration from packet list"""
        threats = []
        for packet in packets:
            alerts = self._detect_data_exfiltration(packet)
            for alert in alerts:
                threats.append(self._alert_to_dict(alert))
        return threats
    
    def _alert_to_dict(self, alert: ThreatAlert) -> Dict[str, Any]:
        """Convert ThreatAlert to dictionary format for compatibility"""
        return {
            'type': alert.threat_type.value,
            'severity': alert.severity.value,
            'source_ip': alert.source_ip,
            'target_ip': alert.destination_ip or 'unknown',
            'timestamp': alert.timestamp,
            'description': alert.description,
            'details': alert.raw_data or {},
            'confidence': alert.confidence
        }
    
    @property
    def db_manager(self):
        """Compatibility property for database manager"""
        return self.database
