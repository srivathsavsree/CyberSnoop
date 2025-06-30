"""
CyberSnoop API Server
FastAPI backend for serving the React dashboard and providing network monitoring data.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import json
from pathlib import Path
from .enhanced_database_manager import EnhancedDatabaseManager as DatabaseManager
from .network_monitor import NetworkMonitor

class CyberSnoopAPI:
    """FastAPI server for CyberSnoop dashboard"""
    
    def __init__(self, config_manager, database_manager: Optional[DatabaseManager] = None, network_monitor: Optional[NetworkMonitor] = None):
        self.config_manager = config_manager
        self.database_manager = database_manager
        self.network_monitor = network_monitor
        self.app = FastAPI(title="CyberSnoop API", version="1.0.0")
        self.connected_clients = []
        self.setup_routes()
        
    def setup_routes(self):
        """Setup API routes and endpoints"""
        
        @self.app.get("/")
        async def dashboard():
            """Serve the main dashboard"""
            return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>CyberSnoop Dashboard</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: white; }
                    .header { text-align: center; margin-bottom: 40px; }
                    .status { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
                    .stat-card { background: #2d2d2d; padding: 20px; border-radius: 8px; text-align: center; }
                    .stat-value { font-size: 2em; font-weight: bold; color: #4CAF50; }
                    .loading { text-align: center; margin: 40px; }
                    .threat { background: #d32f2f; padding: 10px; margin: 5px 0; border-radius: 4px; }
                    .safe { background: #388e3c; padding: 10px; margin: 5px 0; border-radius: 4px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🛡️ CyberSnoop Network Security Monitor</h1>
                    <p>Real-time network monitoring and threat detection</p>
                </div>
                
                <div class="status">
                    <h2>System Status</h2>
                    <p id="status">✅ Initializing network monitoring...</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value" id="packets">0</div>
                        <div>Packets Captured</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="threats">0</div>
                        <div>Threats Detected</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="connections">0</div>
                        <div>Active Connections</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="interfaces">1</div>
                        <div>Network Interfaces</div>
                    </div>
                </div>
                
                <div class="loading">
                    <p>🔄 Real-time dashboard will be integrated in next development phase</p>
                    <p>Current Status: Desktop Application Framework Complete</p>
                </div>
                
                <script>
                    // Placeholder for real-time updates
                    let packetCount = 0;
                    setInterval(() => {
                        packetCount += Math.floor(Math.random() * 10) + 1;
                        document.getElementById('packets').textContent = packetCount.toLocaleString();
                        document.getElementById('status').textContent = '✅ Network monitoring active - ' + new Date().toLocaleTimeString();
                    }, 2000);
                </script>
            </body>
            </html>
            """)
            
        @self.app.get("/api/status")
        async def get_status():
            """Get system status"""
            try:
                monitoring_status = False
                interface_count = 0
                
                if self.network_monitor:
                    monitoring_status = self.network_monitor.is_monitoring
                    interface_count = len(self.network_monitor.get_interfaces())
                
                return {
                    "status": "online",
                    "version": "1.0.0",
                    "uptime": self._get_uptime(),
                    "monitoring": monitoring_status,
                    "interfaces": interface_count
                }
            except Exception as e:
                logging.error(f"Error getting status: {e}")
                return {"status": "error", "message": str(e)}
            
        @self.app.get("/api/stats")
        async def get_stats():
            """Get network statistics"""
            try:
                stats = {
                    "packets_captured": 0,
                    "threats_detected": 0,
                    "active_connections": 0,
                    "network_interfaces": 0,
                    "bandwidth_usage": {
                        "upload": "0 B/s",
                        "download": "0 B/s"
                    }
                }
                
                if self.database_manager:
                    # Get packet count from database
                    stats["packets_captured"] = self.database_manager.get_packet_count()
                    stats["threats_detected"] = self.database_manager.get_threat_count()
                
                if self.network_monitor:
                    stats["network_interfaces"] = len(self.network_monitor.get_interfaces())
                    stats["active_connections"] = self.network_monitor.get_active_connections_count()
                    bandwidth = self.network_monitor.get_bandwidth_stats()
                    if bandwidth:
                        stats["bandwidth_usage"] = bandwidth
                
                return stats
            except Exception as e:
                logging.error(f"Error getting stats: {e}")
                return {"error": str(e)}

        @self.app.get("/api/interfaces")
        async def get_interfaces():
            """Get available network interfaces"""
            try:
                if self.network_monitor:
                    interfaces = self.network_monitor.get_interfaces()
                    return {"interfaces": interfaces}
                return {"interfaces": []}
            except Exception as e:
                logging.error(f"Error getting interfaces: {e}")
                return {"error": str(e)}

        @self.app.get("/api/packets")
        async def get_recent_packets(limit: int = 100):
            """Get recent captured packets"""
            try:
                if self.database_manager:
                    packets = self.database_manager.get_recent_packets(limit)
                    return {"packets": packets}
                return {"packets": []}
            except Exception as e:
                logging.error(f"Error getting packets: {e}")
                return {"error": str(e)}

        @self.app.get("/api/threats")
        async def get_recent_threats(limit: int = 50):
            """Get recent detected threats"""
            try:
                if self.database_manager:
                    threats = self.database_manager.get_recent_threats(limit)
                    return {"threats": threats}
                return {"threats": []}
            except Exception as e:
                logging.error(f"Error getting threats: {e}")
                return {"error": str(e)}

        @self.app.post("/api/monitoring/start")
        async def start_monitoring():
            """Start network monitoring"""
            try:
                if self.network_monitor:
                    self.network_monitor.start_monitoring()
                    return {"status": "monitoring_started"}
                return {"error": "Network monitor not available"}
            except Exception as e:
                logging.error(f"Error starting monitoring: {e}")
                return {"error": str(e)}

        @self.app.post("/api/monitoring/stop")
        async def stop_monitoring():
            """Stop network monitoring"""
            try:
                if self.network_monitor:
                    self.network_monitor.stop_monitoring()
                    return {"status": "monitoring_stopped"}
                return {"error": "Network monitor not available"}
            except Exception as e:
                logging.error(f"Error stopping monitoring: {e}")
                return {"error": str(e)}
            
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            self.connected_clients.append(websocket)
            
            try:
                while True:
                    # Send real-time updates every 5 seconds
                    await asyncio.sleep(5)
                    
                    # Get current stats
                    stats_data = {
                        "timestamp": datetime.now().isoformat(),
                        "packets": 0,
                        "threats": 0,
                        "monitoring": False
                    }
                    
                    if self.database_manager:
                        stats_data["packets"] = self.database_manager.get_packet_count()
                        stats_data["threats"] = self.database_manager.get_threat_count()
                    
                    if self.network_monitor:
                        stats_data["monitoring"] = self.network_monitor.is_monitoring
                    
                    await websocket.send_text(json.dumps({
                        "type": "stats_update",
                        "data": stats_data
                    }))
            except WebSocketDisconnect:
                if websocket in self.connected_clients:
                    self.connected_clients.remove(websocket)
            except Exception as e:
                logging.error(f"WebSocket error: {e}")
                if websocket in self.connected_clients:
                    self.connected_clients.remove(websocket)

    def _get_uptime(self) -> str:
        """Get system uptime formatted as string"""
        # This is a placeholder - in real implementation, track start time
        return "00:05:30"

    async def broadcast_update(self, message: dict):
        """Broadcast real-time updates to all connected clients"""
        if not self.connected_clients:
            return
        
        disconnect_clients = []
        for client in self.connected_clients:
            try:
                await client.send_text(json.dumps(message))
            except Exception as e:
                logging.warning(f"Failed to send to client: {e}")
                disconnect_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnect_clients:
            self.connected_clients.remove(client)
                
    def start_server(self, host="127.0.0.1", port=8888):
        """Start the FastAPI server"""
        try:
            logging.info(f"Starting CyberSnoop API server on {host}:{port}")
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                log_level="info",
                access_log=False
            )
        except Exception as e:
            logging.error(f"Failed to start API server: {e}")
            raise
