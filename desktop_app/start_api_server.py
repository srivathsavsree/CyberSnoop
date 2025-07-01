#!/usr/bin/env python3
"""
Quick API Server for CyberSnoop Testing
"""

import sys
import os
from pathlib import Path

# Add the desktop_app directory to Python path
desktop_app_dir = Path(__file__).parent
sys.path.insert(0, str(desktop_app_dir))

try:
    from backend.api_server import CyberSnoopAPI
    from backend.enhanced_database_manager import EnhancedDatabaseManager
    from backend.network_monitor import NetworkMonitor
    import uvicorn
    
    print("🔧 Setting up CyberSnoop API server...")
    
    # Create a simple config manager
    class SimpleConfig:
        def get(self, key, default=None):
            return default
    
    # Initialize components
    config_manager = SimpleConfig()
    db_manager = EnhancedDatabaseManager(config_manager)
    network_monitor = NetworkMonitor(config_manager)
    
    # Create API server
    api = CyberSnoopAPI(config_manager, db_manager, network_monitor)
    
    print("🚀 Starting CyberSnoop API server...")
    print("📍 Server will be available at: http://127.0.0.1:8889")
    print("🌐 Dashboard: http://127.0.0.1:8889")
    print("📊 API Docs: http://127.0.0.1:8889/docs")
    print("\n✅ Ready! Now try clicking 'Retry' in your desktop app.")
    
    # Start the server
    api.start_server(host="127.0.0.1", port=8889)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Trying alternative startup method...")
    
    # Fallback: Simple FastAPI server
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="CyberSnoop API", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {
            "message": "CyberSnoop API is running!",
            "status": "online",
            "version": "1.0.0"
        }
    
    @app.get("/api/status")
    async def api_status():
        return {
            "api_server": "running",
            "dashboard": "running",
            "monitoring": "stopped",
            "timestamp": "2025-06-30T23:10:00Z"
        }
    
    @app.get("/api/stats")
    async def get_stats():
        return {
            "packets": 0,
            "threats": 0,
            "connections": 0,
            "uptime": "00:00:15"
        }
    
    print("🚀 Starting basic CyberSnoop API server...")
    print("📍 Server: http://127.0.0.1:8889")
    print("✅ Ready! Try clicking 'Retry' in your desktop app.")
    
    uvicorn.run(app, host="127.0.0.1", port=8889, log_level="info")

except Exception as e:
    print(f"❌ Error starting server: {e}")
    print("🔧 Please check your installation and try again.")
