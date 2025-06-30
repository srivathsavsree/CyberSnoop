"""
Enhanced Database Manager with SQLAlchemy ORM for CyberSnoop
Day 5: Advanced database integration, migrations, and performance optimization
"""

import logging
import threading
import time
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

# SQLAlchemy imports
try:
    from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, Index
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session, relationship
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.sql import func
    SQLALCHEMY_AVAILABLE = True
    logging.info("SQLAlchemy available - using ORM database integration")
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logging.warning("SQLAlchemy not available - falling back to basic SQLite")

# Fallback to basic sqlite3
import sqlite3
import json

# Base for SQLAlchemy models
Base = declarative_base()

class PacketRecord(Base):
    """SQLAlchemy model for packet records"""
    __tablename__ = 'packets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    src_ip = Column(String(45), index=True)  # IPv6 support
    dst_ip = Column(String(45), index=True)
    src_port = Column(Integer, index=True)
    dst_port = Column(Integer, index=True)
    protocol = Column(String(10), index=True)
    size = Column(Integer)
    category = Column(String(50), index=True)
    priority = Column(Integer, index=True)
    threat_indicators = Column(Text)  # JSON string
    raw_data = Column(Text)  # JSON string of full packet data
    processed = Column(Boolean, default=False, index=True)
    
    # Relationships
    threats = relationship("ThreatRecord", back_populates="packet")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_packet_lookup', 'timestamp', 'src_ip', 'dst_ip'),
        Index('idx_packet_category', 'category', 'priority'),
        Index('idx_packet_threat', 'timestamp', 'category', 'priority'),
    )

class ThreatRecord(Base):
    """SQLAlchemy model for threat records"""
    __tablename__ = 'threats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    threat_type = Column(String(100), index=True)
    severity = Column(String(20), index=True)
    source_ip = Column(String(45), index=True)
    destination_ip = Column(String(45))
    description = Column(Text)
    indicators = Column(Text)  # JSON string
    packet_id = Column(Integer, ForeignKey('packets.id'))
    resolved = Column(Boolean, default=False, index=True)
    false_positive = Column(Boolean, default=False)
    
    # Relationships
    packet = relationship("PacketRecord", back_populates="threats")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_threat_lookup', 'timestamp', 'threat_type', 'severity'),
        Index('idx_threat_status', 'resolved', 'false_positive'),
    )

class NetworkInterface(Base):
    """SQLAlchemy model for network interfaces"""
    __tablename__ = 'network_interfaces'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    ip_address = Column(String(45))
    mac_address = Column(String(17))
    status = Column(String(20))
    speed = Column(String(20))
    media_type = Column(String(50))
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class SystemMetrics(Base):
    """SQLAlchemy model for system performance metrics"""
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    packet_processing_rate = Column(Float)
    avg_processing_time = Column(Float)
    active_connections = Column(Integer)
    bytes_sent = Column(Integer)
    bytes_received = Column(Integer)
    
    # Index for time-series queries
    __table_args__ = (
        Index('idx_metrics_time', 'timestamp'),
    )

class EnhancedDatabaseManager:
    """Enhanced database manager with SQLAlchemy ORM and advanced features"""
    
    def __init__(self, config_manager, db_path: str = None):
        self.config = config_manager
        self.db_path = db_path or self.config.get("database.path", "cybersnoop.db")
        self.engine = None
        self.session_factory = None
        self.current_session = None
        self.lock = threading.RLock()
        
        # Migration tracking
        self.current_version = 1
        self.migration_history = []
        
        # Performance monitoring
        self.query_stats = {
            "total_queries": 0,
            "avg_query_time": 0.0,
            "slow_queries": 0
        }
        
        # Data retention settings
        self.retention_days = self.config.get("database.retention_days", 30)
        self.cleanup_interval = self.config.get("database.cleanup_interval_hours", 24)
        self.last_cleanup = None
        
        # Initialize database
        self._initialize_database()
        
        # Start background maintenance
        self._start_maintenance_thread()
    
    def _initialize_database(self):
        """Initialize database with SQLAlchemy or fallback to basic SQLite"""
        try:
            if SQLALCHEMY_AVAILABLE:
                self._initialize_sqlalchemy()
            else:
                self._initialize_basic_sqlite()
            
            # Run migrations if needed
            self._check_and_run_migrations()
            
            logging.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            raise
    
    def _initialize_sqlalchemy(self):
        """Initialize SQLAlchemy engine and session factory"""
        # Create database directory if it doesn't exist
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Create engine with optimized settings
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
                "timeout": 30,
                "isolation_level": None  # Autocommit mode
            },
            echo=self.config.get("database.debug", False)
        )
        
        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine)
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        
        logging.info("SQLAlchemy database initialized successfully")
    
    def _initialize_basic_sqlite(self):
        """Fallback to basic SQLite initialization"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic tables
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic packet table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                src_ip TEXT,
                dst_ip TEXT,
                src_port INTEGER,
                dst_port INTEGER,
                protocol TEXT,
                size INTEGER,
                category TEXT,
                priority INTEGER,
                raw_data TEXT
            )
        ''')
        
        # Basic threat table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                threat_type TEXT,
                severity TEXT,
                source_ip TEXT,
                description TEXT,
                packet_id INTEGER,
                FOREIGN KEY (packet_id) REFERENCES packets (id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_packets_timestamp ON packets(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_threats_timestamp ON threats(timestamp)')
        
        conn.commit()
        conn.close()
        
        logging.info("Basic SQLite database initialized successfully")
    
    def get_session(self) -> Session:
        """Get a database session (SQLAlchemy only)"""
        if not SQLALCHEMY_AVAILABLE or not self.session_factory:
            raise RuntimeError("SQLAlchemy not available")
        
        return self.session_factory()
    
    def store_packet(self, packet_data: Dict[str, Any]) -> bool:
        """Store packet data in database"""
        start_time = time.time()
        
        try:
            with self.lock:
                if SQLALCHEMY_AVAILABLE:
                    return self._store_packet_sqlalchemy(packet_data)
                else:
                    return self._store_packet_basic(packet_data)
        
        except Exception as e:
            logging.error(f"Error storing packet: {e}")
            return False
        
        finally:
            # Update query statistics
            query_time = time.time() - start_time
            self._update_query_stats(query_time)
    
    def _store_packet_sqlalchemy(self, packet_data: Dict[str, Any]) -> bool:
        """Store packet using SQLAlchemy ORM"""
        session = self.get_session()
        
        try:
            packet = PacketRecord(
                timestamp=datetime.fromisoformat(packet_data.get("timestamp", datetime.utcnow().isoformat())),
                src_ip=packet_data.get("src_ip"),
                dst_ip=packet_data.get("dst_ip"),
                src_port=packet_data.get("src_port"),
                dst_port=packet_data.get("dst_port"),
                protocol=packet_data.get("protocol_name"),
                size=packet_data.get("size", 0),
                category=packet_data.get("category"),
                priority=packet_data.get("priority"),
                threat_indicators=json.dumps(packet_data.get("threat_indicators", [])),
                raw_data=json.dumps(packet_data)
            )
            
            session.add(packet)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logging.error(f"SQLAlchemy packet storage error: {e}")
            return False
        
        finally:
            session.close()
    
    def _store_packet_basic(self, packet_data: Dict[str, Any]) -> bool:
        """Store packet using basic SQLite"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO packets (timestamp, src_ip, dst_ip, src_port, dst_port, 
                                   protocol, size, category, priority, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                packet_data.get("timestamp", datetime.utcnow().isoformat()),
                packet_data.get("src_ip"),
                packet_data.get("dst_ip"),
                packet_data.get("src_port"),
                packet_data.get("dst_port"),
                packet_data.get("protocol_name"),
                packet_data.get("size", 0),
                packet_data.get("category"),
                packet_data.get("priority"),
                json.dumps(packet_data)
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Basic SQLite packet storage error: {e}")
            return False
        
        finally:
            conn.close()
    
    def store_threat(self, threat_data: Dict[str, Any], packet_id: int = None) -> bool:
        """Store threat data in database"""
        start_time = time.time()
        
        try:
            with self.lock:
                if SQLALCHEMY_AVAILABLE:
                    return self._store_threat_sqlalchemy(threat_data, packet_id)
                else:
                    return self._store_threat_basic(threat_data, packet_id)
        
        except Exception as e:
            logging.error(f"Error storing threat: {e}")
            return False
        
        finally:
            query_time = time.time() - start_time
            self._update_query_stats(query_time)
    
    def _store_threat_sqlalchemy(self, threat_data: Dict[str, Any], packet_id: int = None) -> bool:
        """Store threat using SQLAlchemy ORM"""
        session = self.get_session()
        
        try:
            threat = ThreatRecord(
                timestamp=datetime.fromisoformat(threat_data.get("timestamp", datetime.utcnow().isoformat())),
                threat_type=threat_data.get("type"),
                severity=threat_data.get("severity"),
                source_ip=threat_data.get("source_ip"),
                destination_ip=threat_data.get("destination_ip"),
                description=threat_data.get("description"),
                indicators=json.dumps(threat_data.get("indicators", [])),
                packet_id=packet_id
            )
            
            session.add(threat)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logging.error(f"SQLAlchemy threat storage error: {e}")
            return False
        
        finally:
            session.close()
    
    def _store_threat_basic(self, threat_data: Dict[str, Any], packet_id: int = None) -> bool:
        """Store threat using basic SQLite"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO threats (timestamp, threat_type, severity, source_ip, 
                                   description, packet_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                threat_data.get("timestamp", datetime.utcnow().isoformat()),
                threat_data.get("type"),
                threat_data.get("severity"),
                threat_data.get("source_ip"),
                threat_data.get("description"),
                packet_id
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Basic SQLite threat storage error: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_packet_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get packet statistics for the specified time period"""
        start_time = time.time()
        
        try:
            if SQLALCHEMY_AVAILABLE:
                return self._get_packet_statistics_sqlalchemy(hours)
            else:
                return self._get_packet_statistics_basic(hours)
        
        finally:
            query_time = time.time() - start_time
            self._update_query_stats(query_time)
    
    def _get_packet_statistics_sqlalchemy(self, hours: int) -> Dict[str, Any]:
        """Get packet statistics using SQLAlchemy"""
        session = self.get_session()
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Total packets
            total_packets = session.query(PacketRecord).filter(
                PacketRecord.timestamp >= cutoff_time
            ).count()
            
            # Category breakdown
            category_stats = session.query(
                PacketRecord.category,
                func.count(PacketRecord.id).label('count')
            ).filter(
                PacketRecord.timestamp >= cutoff_time
            ).group_by(PacketRecord.category).all()
            
            # Priority breakdown
            priority_stats = session.query(
                PacketRecord.priority,
                func.count(PacketRecord.id).label('count')
            ).filter(
                PacketRecord.timestamp >= cutoff_time
            ).group_by(PacketRecord.priority).all()
            
            return {
                "total_packets": total_packets,
                "category_breakdown": {cat: count for cat, count in category_stats},
                "priority_breakdown": {str(pri): count for pri, count in priority_stats},
                "time_period_hours": hours
            }
            
        finally:
            session.close()
    
    def _get_packet_statistics_basic(self, hours: int) -> Dict[str, Any]:
        """Get packet statistics using basic SQLite"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        
        try:
            cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            # Total packets
            cursor.execute(
                "SELECT COUNT(*) FROM packets WHERE timestamp >= ?",
                (cutoff_time,)
            )
            total_packets = cursor.fetchone()[0]
            
            # Category breakdown
            cursor.execute(
                "SELECT category, COUNT(*) FROM packets WHERE timestamp >= ? GROUP BY category",
                (cutoff_time,)
            )
            category_stats = dict(cursor.fetchall())
            
            return {
                "total_packets": total_packets,
                "category_breakdown": category_stats,
                "time_period_hours": hours
            }
            
        finally:
            conn.close()
    
    def cleanup_old_data(self) -> Dict[str, int]:
        """Clean up old data based on retention policy"""
        start_time = time.time()
        deleted_counts = {"packets": 0, "threats": 0}
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=self.retention_days)
            
            with self.lock:
                if SQLALCHEMY_AVAILABLE:
                    deleted_counts = self._cleanup_old_data_sqlalchemy(cutoff_time)
                else:
                    deleted_counts = self._cleanup_old_data_basic(cutoff_time)
            
            self.last_cleanup = datetime.utcnow()
            logging.info(f"Data cleanup completed: {deleted_counts}")
            
        except Exception as e:
            logging.error(f"Data cleanup failed: {e}")
        
        finally:
            query_time = time.time() - start_time
            self._update_query_stats(query_time)
        
        return deleted_counts
    
    def _cleanup_old_data_sqlalchemy(self, cutoff_time: datetime) -> Dict[str, int]:
        """Clean up old data using SQLAlchemy"""
        session = self.get_session()
        deleted_counts = {"packets": 0, "threats": 0}
        
        try:
            # Delete old threats first (foreign key constraint)
            deleted_threats = session.query(ThreatRecord).filter(
                ThreatRecord.timestamp < cutoff_time
            ).delete()
            
            # Delete old packets
            deleted_packets = session.query(PacketRecord).filter(
                PacketRecord.timestamp < cutoff_time
            ).delete()
            
            session.commit()
            
            deleted_counts["packets"] = deleted_packets
            deleted_counts["threats"] = deleted_threats
            
        except Exception as e:
            session.rollback()
            logging.error(f"SQLAlchemy cleanup error: {e}")
        
        finally:
            session.close()
        
        return deleted_counts
    
    def _cleanup_old_data_basic(self, cutoff_time: datetime) -> Dict[str, int]:
        """Clean up old data using basic SQLite"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        deleted_counts = {"packets": 0, "threats": 0}
        
        try:
            cutoff_str = cutoff_time.isoformat()
            
            # Delete old threats first
            cursor.execute("DELETE FROM threats WHERE timestamp < ?", (cutoff_str,))
            deleted_counts["threats"] = cursor.rowcount
            
            # Delete old packets
            cursor.execute("DELETE FROM packets WHERE timestamp < ?", (cutoff_str,))
            deleted_counts["packets"] = cursor.rowcount
            
            # Vacuum to reclaim space
            cursor.execute("VACUUM")
            
            conn.commit()
            
        except Exception as e:
            logging.error(f"Basic SQLite cleanup error: {e}")
        
        finally:
            conn.close()
        
        return deleted_counts
    
    def _update_query_stats(self, query_time: float):
        """Update query performance statistics"""
        self.query_stats["total_queries"] += 1
        
        # Update average query time
        total_time = self.query_stats["avg_query_time"] * (self.query_stats["total_queries"] - 1)
        self.query_stats["avg_query_time"] = (total_time + query_time) / self.query_stats["total_queries"]
        
        # Track slow queries (> 1 second)
        if query_time > 1.0:
            self.query_stats["slow_queries"] += 1
    
    def _check_and_run_migrations(self):
        """Check and run database migrations if needed"""
        # This is a placeholder for future migration system
        # In a real implementation, you would check current DB version
        # and run appropriate migration scripts
        pass
    
    def _start_maintenance_thread(self):
        """Start background maintenance thread"""
        def maintenance_loop():
            while True:
                try:
                    # Check if cleanup is needed
                    if (self.last_cleanup is None or 
                        datetime.utcnow() - self.last_cleanup > timedelta(hours=self.cleanup_interval)):
                        self.cleanup_old_data()
                    
                    # Sleep for 1 hour before next check
                    time.sleep(3600)
                    
                except Exception as e:
                    logging.error(f"Maintenance thread error: {e}")
                    time.sleep(3600)  # Continue despite errors
        
        maintenance_thread = threading.Thread(target=maintenance_loop, daemon=True)
        maintenance_thread.start()
        logging.info("Database maintenance thread started")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        info = {
            "database_path": self.db_path,
            "engine_type": "SQLAlchemy" if SQLALCHEMY_AVAILABLE else "Basic SQLite",
            "retention_days": self.retention_days,
            "last_cleanup": self.last_cleanup.isoformat() if self.last_cleanup else None,
            "query_stats": self.query_stats.copy()
        }
        
        # Add table counts if possible
        try:
            if SQLALCHEMY_AVAILABLE:
                session = self.get_session()
                try:
                    info["packet_count"] = session.query(PacketRecord).count()
                    info["threat_count"] = session.query(ThreatRecord).count()
                finally:
                    session.close()
            else:
                conn = sqlite3.connect(self.db_path, timeout=30)
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT COUNT(*) FROM packets")
                    info["packet_count"] = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM threats")
                    info["threat_count"] = cursor.fetchone()[0]
                finally:
                    conn.close()
        except Exception as e:
            logging.debug(f"Could not get table counts: {e}")
        
        return info
    
    def close(self):
        """Close database connections"""
        try:
            if SQLALCHEMY_AVAILABLE and self.engine:
                self.engine.dispose()
            logging.info("Database connections closed")
        except Exception as e:
            logging.error(f"Error closing database: {e}")
    
    def get_packet_count(self) -> int:
        """Get total number of packets stored"""
        try:
            if SQLALCHEMY_AVAILABLE:
                with self.get_session() as session:
                    count = session.query(PacketRecord).count()
                    return count
            else:
                cursor = sqlite3.connect(self.db_path).cursor()
                cursor.execute("SELECT COUNT(*) FROM packets")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logging.error(f"Error getting packet count: {e}")
            return 0

    def get_threat_count(self) -> int:
        """Get total number of threats detected"""
        try:
            if SQLALCHEMY_AVAILABLE:
                with self.get_session() as session:
                    count = session.query(ThreatRecord).count()
                    return count
            else:
                cursor = sqlite3.connect(self.db_path).cursor()
                cursor.execute("SELECT COUNT(*) FROM threats")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logging.error(f"Error getting threat count: {e}")
            return 0

    def get_recent_packets(self, limit: int = 100, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent packets from the database"""
        try:
            if SQLALCHEMY_AVAILABLE:
                with self.get_session() as session:
                    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                    packets = session.query(PacketRecord)\
                        .filter(PacketRecord.timestamp >= cutoff_time)\
                        .order_by(PacketRecord.timestamp.desc())\
                        .limit(limit)\
                        .all()
                    
                    return [{
                        'id': packet.id,
                        'timestamp': packet.timestamp.isoformat() if packet.timestamp else '',
                        'src_ip': packet.src_ip,
                        'dst_ip': packet.dst_ip,
                        'src_port': packet.src_port,
                        'dst_port': packet.dst_port,
                        'protocol': packet.protocol,
                        'size': packet.size,
                        'category': packet.category,
                        'priority': packet.priority
                    } for packet in packets]
            else:
                cursor = sqlite3.connect(self.db_path).cursor()
                cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
                cursor.execute("""
                    SELECT id, timestamp, src_ip, dst_ip, src_port, dst_port, 
                           protocol, size, category, priority 
                    FROM packets 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (cutoff_time, limit))
                
                results = cursor.fetchall()
                return [{
                    'id': row[0],
                    'timestamp': row[1],
                    'src_ip': row[2],
                    'dst_ip': row[3],
                    'src_port': row[4],
                    'dst_port': row[5],
                    'protocol': row[6],
                    'size': row[7],
                    'category': row[8],
                    'priority': row[9]
                } for row in results]
        except Exception as e:
            logging.error(f"Error getting recent packets: {e}")
            return []

    def get_recent_threats(self, limit: int = 50, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent threats from the database"""
        try:
            if SQLALCHEMY_AVAILABLE:
                with self.get_session() as session:
                    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                    threats = session.query(ThreatRecord)\
                        .filter(ThreatRecord.timestamp >= cutoff_time)\
                        .order_by(ThreatRecord.timestamp.desc())\
                        .limit(limit)\
                        .all()
                    
                    return [{
                        'id': threat.id,
                        'timestamp': threat.timestamp.isoformat() if threat.timestamp else '',
                        'threat_type': threat.threat_type,
                        'severity': threat.severity,
                        'source_ip': threat.source_ip,
                        'target_ip': threat.target_ip,
                        'description': threat.description,
                        'indicators': threat.indicators,
                        'confidence': threat.confidence,
                        'resolved': threat.resolved
                    } for threat in threats]
            else:
                cursor = sqlite3.connect(self.db_path).cursor()
                cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
                cursor.execute("""
                    SELECT id, timestamp, threat_type, severity, source_ip, 
                           target_ip, description, indicators, confidence, resolved 
                    FROM threats 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (cutoff_time, limit))
                
                results = cursor.fetchall()
                return [{
                    'id': row[0],
                    'timestamp': row[1],
                    'threat_type': row[2],
                    'severity': row[3],
                    'source_ip': row[4],
                    'target_ip': row[5],
                    'description': row[6],
                    'indicators': row[7],
                    'confidence': row[8],
                    'resolved': row[9]
                } for row in results]
        except Exception as e:
            logging.error(f"Error getting recent threats: {e}")
            return []

    def get_threat_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get threat statistics for the specified time period"""
        try:
            if SQLALCHEMY_AVAILABLE:
                with self.get_session() as session:
                    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                    
                    total_threats = session.query(ThreatRecord)\
                        .filter(ThreatRecord.timestamp >= cutoff_time)\
                        .count()
                    
                    high_severity = session.query(ThreatRecord)\
                        .filter(ThreatRecord.timestamp >= cutoff_time)\
                        .filter(ThreatRecord.severity == 'high')\
                        .count()
                    
                    threat_types = session.query(ThreatRecord.threat_type, 
                                                func.count(ThreatRecord.threat_type))\
                        .filter(ThreatRecord.timestamp >= cutoff_time)\
                        .group_by(ThreatRecord.threat_type)\
                        .all()
                    
                    return {
                        'total_threats': total_threats,
                        'high_severity': high_severity,
                        'threat_types': dict(threat_types),
                        'time_period_hours': hours
                    }
            else:
                cursor = sqlite3.connect(self.db_path).cursor()
                cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
                
                cursor.execute("SELECT COUNT(*) FROM threats WHERE timestamp >= ?", (cutoff_time,))
                total_threats = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM threats WHERE timestamp >= ? AND severity = 'high'", (cutoff_time,))
                high_severity = cursor.fetchone()[0]
                
                cursor.execute("SELECT threat_type, COUNT(*) FROM threats WHERE timestamp >= ? GROUP BY threat_type", (cutoff_time,))
                threat_types = dict(cursor.fetchall())
                
                return {
                    'total_threats': total_threats,
                    'high_severity': high_severity,
                    'threat_types': threat_types,
                    'time_period_hours': hours
                }
        except Exception as e:
            logging.error(f"Error getting threat statistics: {e}")
            return {
                'total_threats': 0,
                'high_severity': 0,
                'threat_types': {},
                'time_period_hours': hours
            }

# Compatibility alias for existing code
DatabaseManager = EnhancedDatabaseManager
