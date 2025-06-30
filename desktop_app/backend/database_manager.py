"""
Database Manager for CyberSnoop
Handles packet storage, threat logging, and data persistence using SQLite.
"""

import sqlite3
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import threading

class DatabaseManager:
    """Manages SQLite database for packet storage and threat logging"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.db_path = config_manager.get_database_path()
        self.connection_lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create packets table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS packets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        src_ip TEXT,
                        dst_ip TEXT,
                        src_port INTEGER,
                        dst_port INTEGER,
                        protocol TEXT,
                        protocol_name TEXT,
                        packet_size INTEGER,
                        payload_preview TEXT,
                        interface_name TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create threats table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS threats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        threat_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        source_ip TEXT,
                        destination_ip TEXT,
                        description TEXT,
                        additional_data TEXT,
                        resolved BOOLEAN DEFAULT FALSE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create network_stats table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS network_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        packet_count INTEGER,
                        threat_count INTEGER,
                        bytes_sent INTEGER,
                        bytes_received INTEGER,
                        active_connections INTEGER,
                        interface_name TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create interfaces table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS interfaces (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        ip_address TEXT,
                        status TEXT,
                        interface_type TEXT,
                        first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_packets_timestamp ON packets(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_packets_src_ip ON packets(src_ip)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_threats_timestamp ON threats(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_threats_type ON threats(threat_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_stats_timestamp ON network_stats(timestamp)")
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            raise
            
    def store_packet(self, packet_data: Dict[str, Any]) -> bool:
        """Store packet information in database"""
        try:
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO packets (
                            timestamp, src_ip, dst_ip, src_port, dst_port,
                            protocol, protocol_name, packet_size, payload_preview, interface_name
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        packet_data.get("timestamp"),
                        packet_data.get("src_ip"),
                        packet_data.get("dst_ip"),
                        packet_data.get("src_port"),
                        packet_data.get("dst_port"),
                        packet_data.get("protocol"),
                        packet_data.get("protocol_name"),
                        packet_data.get("size"),
                        packet_data.get("payload_preview", "")[:1000],  # Limit payload preview
                        packet_data.get("interface_name")
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logging.error(f"Failed to store packet: {e}")
            return False
            
    def store_threat(self, threat_data: Dict[str, Any]) -> bool:
        """Store threat information in database"""
        try:
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Convert additional data to JSON string
                    additional_data = json.dumps(threat_data.get("additional_data", {}))
                    
                    cursor.execute("""
                        INSERT INTO threats (
                            timestamp, threat_type, severity, source_ip, destination_ip,
                            description, additional_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        threat_data.get("timestamp"),
                        threat_data.get("type"),
                        threat_data.get("severity"),
                        threat_data.get("source_ip"),
                        threat_data.get("destination_ip"),
                        threat_data.get("description"),
                        additional_data
                    ))
                    
                    conn.commit()
                    logging.info(f"Stored threat: {threat_data.get('type')} from {threat_data.get('source_ip')}")
                    return True
                    
        except Exception as e:
            logging.error(f"Failed to store threat: {e}")
            return False
            
    def store_network_stats(self, stats_data: Dict[str, Any]) -> bool:
        """Store network statistics in database"""
        try:
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO network_stats (
                            timestamp, packet_count, threat_count, bytes_sent, bytes_received,
                            active_connections, interface_name
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        stats_data.get("timestamp"),
                        stats_data.get("packet_count"),
                        stats_data.get("threat_count"),
                        stats_data.get("bytes_sent"),
                        stats_data.get("bytes_received"),
                        stats_data.get("connection_count"),
                        stats_data.get("selected_interface")
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logging.error(f"Failed to store network stats: {e}")
            return False
            
    def get_recent_threats(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent threats from database"""
        try:
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Calculate cutoff time
                    cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
                    
                    cursor.execute("""
                        SELECT * FROM threats 
                        WHERE timestamp > ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (cutoff_time, limit))
                    
                    columns = [description[0] for description in cursor.description]
                    threats = []
                    
                    for row in cursor.fetchall():
                        threat = dict(zip(columns, row))
                        # Parse additional_data JSON
                        if threat.get("additional_data"):
                            try:
                                threat["additional_data"] = json.loads(threat["additional_data"])
                            except:
                                threat["additional_data"] = {}
                        threats.append(threat)
                        
                    return threats
                    
        except Exception as e:
            logging.error(f"Failed to get recent threats: {e}")
            return []
            
    def get_packet_count(self, hours: int = 24) -> int:
        """Get total packet count within specified hours"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) FROM packets 
                        WHERE timestamp > ?
                    """, (cutoff_time,))
                    
                    return cursor.fetchone()[0]
                    
        except Exception as e:
            logging.error(f"Failed to get packet count: {e}")
            return 0

    def get_threat_count(self, hours: int = 24) -> int:
        """Get total threat count within specified hours"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) FROM threats 
                        WHERE timestamp > ?
                    """, (cutoff_time,))
                    
                    return cursor.fetchone()[0]
                    
        except Exception as e:
            logging.error(f"Failed to get threat count: {e}")
            return 0

    def get_recent_packets(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent packets"""
        try:
            packets = []
            
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT timestamp, src_ip, dst_ip, src_port, dst_port, 
                               protocol_name, packet_size, interface_name
                        FROM packets 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (limit,))
                    
                    for row in cursor.fetchall():
                        packets.append({
                            "timestamp": row[0],
                            "src_ip": row[1],
                            "dst_ip": row[2],
                            "src_port": row[3],
                            "dst_port": row[4],
                            "protocol": row[5],
                            "size": row[6],
                            "interface": row[7]
                        })
                    
                    return packets
                    
        except Exception as e:
            logging.error(f"Failed to get recent packets: {e}")
            return []

    def get_recent_threats(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent threats"""
        try:
            threats = []
            
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT timestamp, threat_type, severity, source_ip, 
                               destination_ip, description, additional_data
                        FROM threats 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (limit,))
                    
                    for row in cursor.fetchall():
                        additional_data = {}
                        try:
                            if row[6]:
                                additional_data = json.loads(row[6])
                        except:
                            pass
                            
                        threats.append({
                            "timestamp": row[0],
                            "type": row[1],
                            "severity": row[2],
                            "source_ip": row[3],
                            "destination_ip": row[4],
                            "description": row[5],
                            "additional_data": additional_data
                        })
                    
                    return threats
                    
        except Exception as e:
            logging.error(f"Failed to get recent threats: {e}")
            return []

    def get_network_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get network statistics summary"""
        try:
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
                    
                    # Get packet statistics
                    cursor.execute("""
                        SELECT COUNT(*) as total_packets,
                               COUNT(DISTINCT src_ip) as unique_sources,
                               COUNT(DISTINCT dst_ip) as unique_destinations
                        FROM packets 
                        WHERE timestamp > ?
                    """, (cutoff_time,))
                    
                    packet_stats = cursor.fetchone()
                    
                    # Get threat statistics
                    cursor.execute("""
                        SELECT threat_type, COUNT(*) as count
                        FROM threats 
                        WHERE timestamp > ?
                        GROUP BY threat_type
                    """, (cutoff_time,))
                    
                    threat_stats = {row[0]: row[1] for row in cursor.fetchall()}
                    
                    # Get top source IPs
                    cursor.execute("""
                        SELECT src_ip, COUNT(*) as count
                        FROM packets 
                        WHERE timestamp > ? AND src_ip IS NOT NULL
                        GROUP BY src_ip
                        ORDER BY count DESC
                        LIMIT 10
                    """, (cutoff_time,))
                    
                    top_sources = [{"ip": row[0], "count": row[1]} for row in cursor.fetchall()]
                    
                    return {
                        "total_packets": packet_stats[0] if packet_stats else 0,
                        "unique_sources": packet_stats[1] if packet_stats else 0,
                        "unique_destinations": packet_stats[2] if packet_stats else 0,
                        "threat_breakdown": threat_stats,
                        "top_source_ips": top_sources,
                        "period_hours": hours
                    }
                    
        except Exception as e:
            logging.error(f"Failed to get network statistics: {e}")
            return {}
            
    def update_interface(self, interface_data: Dict[str, Any]) -> bool:
        """Update or insert interface information"""
        try:
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO interfaces (
                            name, ip_address, status, interface_type, last_seen
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        interface_data.get("name"),
                        interface_data.get("ip"),
                        interface_data.get("status"),
                        interface_data.get("type"),
                        datetime.now().isoformat()
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logging.error(f"Failed to update interface: {e}")
            return False
            
    def cleanup_old_data(self) -> bool:
        """Clean up old data based on retention policy"""
        try:
            retention_days = self.config_manager.get("database.retention_days", 30)
            cutoff_time = (datetime.now() - timedelta(days=retention_days)).isoformat()
            
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Clean up old packets
                    cursor.execute("DELETE FROM packets WHERE timestamp < ?", (cutoff_time,))
                    packets_deleted = cursor.rowcount
                    
                    # Clean up old stats (keep more stats than packets)
                    stats_cutoff = (datetime.now() - timedelta(days=retention_days * 2)).isoformat()
                    cursor.execute("DELETE FROM network_stats WHERE timestamp < ?", (stats_cutoff,))
                    stats_deleted = cursor.rowcount
                    
                    # Don't delete threats - keep for historical analysis
                    
                    conn.commit()
                    
                    logging.info(f"Cleanup completed: {packets_deleted} packets, {stats_deleted} stats deleted")
                    return True
                    
        except Exception as e:
            logging.error(f"Failed to cleanup old data: {e}")
            return False
            
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        try:
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get table sizes
                    cursor.execute("SELECT COUNT(*) FROM packets")
                    packet_count = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM threats")
                    threat_count = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM network_stats")
                    stats_count = cursor.fetchone()[0]
                    
                    # Get database file size
                    db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                    
                    return {
                        "database_path": str(self.db_path),
                        "database_size_bytes": db_size,
                        "database_size_mb": round(db_size / (1024 * 1024), 2),
                        "packet_count": packet_count,
                        "threat_count": threat_count,
                        "stats_count": stats_count,
                        "max_size_mb": self.config_manager.get("database.max_size_mb", 500),
                        "retention_days": self.config_manager.get("database.retention_days", 30)
                    }
                    
        except Exception as e:
            logging.error(f"Failed to get database info: {e}")
            return {}
            
    def export_data(self, output_file: str, table: str = "threats", hours: int = 24) -> bool:
        """Export data to CSV file"""
        try:
            import csv
            
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            with self.connection_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    if table == "threats":
                        cursor.execute("""
                            SELECT timestamp, threat_type, severity, source_ip, destination_ip, description
                            FROM threats 
                            WHERE timestamp > ?
                            ORDER BY timestamp DESC
                        """, (cutoff_time,))
                    elif table == "packets":
                        cursor.execute("""
                            SELECT timestamp, src_ip, dst_ip, src_port, dst_port, protocol_name
                            FROM packets 
                            WHERE timestamp > ?
                            ORDER BY timestamp DESC
                        """, (cutoff_time,))
                    else:
                        logging.error(f"Unknown table for export: {table}")
                        return False
                        
                    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        
                        # Write header
                        columns = [description[0] for description in cursor.description]
                        writer.writerow(columns)
                        
                        # Write data
                        writer.writerows(cursor.fetchall())
                        
                    logging.info(f"Data exported to {output_file}")
                    return True
                    
        except Exception as e:
            logging.error(f"Failed to export data: {e}")
            return False
