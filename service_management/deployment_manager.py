"""
🚀 CyberSnoop Deployment & Operations Automation
Handles all deployment, monitoring, and operational tasks

This script automates:
- Production deployment
- Service monitoring
- Database management
- Backup & recovery
- Performance optimization
- Security updates
"""

import os
import sys
import json
import time
import subprocess
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import psutil
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeploymentManager:
    """
    🚀 Automated Deployment & Operations Manager
    
    Handles:
    - Production deployments
    - Service monitoring
    - Database management
    - Backup operations
    - Performance monitoring
    - Security updates
    """
    
    def __init__(self, config_path: str = "deployment_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.project_root = Path(__file__).parent.parent
        logger.info("Deployment Manager initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        default_config = {
            "environment": "production",
            "server_config": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4,
                "max_requests": 1000
            },
            "database_config": {
                "backup_interval": 3600,  # 1 hour
                "backup_retention_days": 30,
                "backup_location": "/backups"
            },
            "monitoring_config": {
                "check_interval": 300,  # 5 minutes
                "services": [
                    {"name": "api_server", "url": "http://localhost:8000/health"},
                    {"name": "dashboard", "url": "http://localhost:3000"},
                    {"name": "database", "url": "sqlite:///cybersnoop.db"}
                ]
            },
            "deployment_config": {
                "strategy": "rolling",  # rolling, blue_green, canary
                "health_check_timeout": 300,
                "rollback_on_failure": True
            },
            "security_config": {
                "update_check_interval": 86400,  # 24 hours
                "auto_security_updates": True,
                "vulnerability_scanning": True
            },
            "notification_config": {
                "email_alerts": True,
                "slack_webhook": "",
                "alert_thresholds": {
                    "cpu_usage": 80,
                    "memory_usage": 85,
                    "disk_usage": 90,
                    "response_time": 2000
                }
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    # 🚀 DEPLOYMENT OPERATIONS
    def deploy_application(self, version: str = None) -> Dict[str, Any]:
        """Deploy the application to production"""
        deployment_id = f"deploy-{int(time.time())}"
        logger.info(f"Starting deployment {deployment_id}")
        
        try:
            # 1. Pre-deployment checks
            logger.info("Running pre-deployment checks...")
            if not self._pre_deployment_checks():
                raise Exception("Pre-deployment checks failed")
            
            # 2. Backup current version
            logger.info("Creating backup...")
            backup_path = self._create_backup()
            
            # 3. Deploy new version
            logger.info("Deploying new version...")
            if not self._deploy_version(version):
                raise Exception("Deployment failed")
            
            # 4. Run post-deployment tests
            logger.info("Running post-deployment tests...")
            if not self._post_deployment_tests():
                logger.error("Post-deployment tests failed, rolling back...")
                self._rollback_deployment(backup_path)
                raise Exception("Post-deployment tests failed")
            
            # 5. Update configuration
            self._update_deployment_config(deployment_id, version)
            
            logger.info(f"Deployment {deployment_id} completed successfully")
            return {
                "status": "success",
                "deployment_id": deployment_id,
                "version": version,
                "deployed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Deployment {deployment_id} failed: {e}")
            return {
                "status": "failed",
                "deployment_id": deployment_id,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }
    
    def _pre_deployment_checks(self) -> bool:
        """Run pre-deployment validation checks"""
        checks = [
            self._check_system_resources,
            self._check_dependencies,
            self._check_database_connection,
            self._check_external_services
        ]
        
        for check in checks:
            try:
                if not check():
                    return False
            except Exception as e:
                logger.error(f"Pre-deployment check failed: {e}")
                return False
        
        return True
    
    def _check_system_resources(self) -> bool:
        """Check system resources availability"""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        thresholds = self.config['notification_config']['alert_thresholds']
        
        if cpu_usage > thresholds['cpu_usage']:
            logger.error(f"CPU usage too high: {cpu_usage}%")
            return False
        
        if memory.percent > thresholds['memory_usage']:
            logger.error(f"Memory usage too high: {memory.percent}%")
            return False
        
        if disk.percent > thresholds['disk_usage']:
            logger.error(f"Disk usage too high: {disk.percent}%")
            return False
        
        logger.info("System resources check passed")
        return True
    
    def _check_dependencies(self) -> bool:
        """Check if all dependencies are available"""
        try:
            # Check Python dependencies
            result = subprocess.run([
                sys.executable, '-c', 
                'import flask, sqlite3, requests, psutil, schedule'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Python dependencies check failed: {result.stderr}")
                return False
            
            # Check Node.js dependencies (for dashboard)
            dashboard_path = self.project_root / 'cybersnoop-dashboard'
            if dashboard_path.exists():
                result = subprocess.run([
                    'npm', 'list', '--depth=0'
                ], cwd=dashboard_path, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Node.js dependencies check failed: {result.stderr}")
                    return False
            
            logger.info("Dependencies check passed")
            return True
            
        except Exception as e:
            logger.error(f"Dependencies check failed: {e}")
            return False
    
    def _check_database_connection(self) -> bool:
        """Check database connectivity"""
        try:
            import sqlite3
            db_path = self.project_root / 'desktop_app' / 'data' / 'cybersnoop.db'
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            
            logger.info("Database connection check passed")
            return True
            
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    def _check_external_services(self) -> bool:
        """Check external service dependencies"""
        services = self.config['monitoring_config']['services']
        
        for service in services:
            if 'url' in service and service['url'].startswith('http'):
                try:
                    response = requests.get(service['url'], timeout=10)
                    if response.status_code != 200:
                        logger.error(f"Service {service['name']} health check failed")
                        return False
                except Exception as e:
                    logger.error(f"Service {service['name']} unreachable: {e}")
                    return False
        
        logger.info("External services check passed")
        return True
    
    def _create_backup(self) -> str:
        """Create backup of current deployment"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(self.config['database_config']['backup_location'])
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        try:
            # Backup database
            db_path = self.project_root / 'desktop_app' / 'data' / 'cybersnoop.db'
            if db_path.exists():
                import shutil
                shutil.copy2(db_path, backup_path / 'cybersnoop.db')
            
            # Backup configuration files
            config_files = [
                'service_config.json',
                'deployment_config.json',
                'desktop_app/config/config.json'
            ]
            
            for config_file in config_files:
                config_path = self.project_root / config_file
                if config_path.exists():
                    shutil.copy2(config_path, backup_path / config_path.name)
            
            logger.info(f"Backup created at {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise
    
    def _deploy_version(self, version: str = None) -> bool:
        """Deploy specific version"""
        try:
            # In a real deployment, this would:
            # 1. Pull code from git repository
            # 2. Install dependencies
            # 3. Run database migrations
            # 4. Update configuration
            # 5. Restart services
            
            # For now, simulate deployment
            logger.info(f"Deploying version {version or 'latest'}")
            
            # Install/update Python dependencies
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 
                str(self.project_root / 'requirements.txt')
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Python dependencies installation failed: {result.stderr}")
                return False
            
            # Install/update Node.js dependencies
            dashboard_path = self.project_root / 'cybersnoop-dashboard'
            if dashboard_path.exists():
                result = subprocess.run([
                    'npm', 'install'
                ], cwd=dashboard_path, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Node.js dependencies installation failed: {result.stderr}")
                    return False
                
                # Build dashboard
                result = subprocess.run([
                    'npm', 'run', 'build'
                ], cwd=dashboard_path, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Dashboard build failed: {result.stderr}")
                    return False
            
            logger.info("Version deployment completed")
            return True
            
        except Exception as e:
            logger.error(f"Version deployment failed: {e}")
            return False
    
    def _post_deployment_tests(self) -> bool:
        """Run post-deployment validation tests"""
        try:
            # Run comprehensive tests
            test_script = self.project_root / 'desktop_app' / 'test_phase3_comprehensive.py'
            if test_script.exists():
                result = subprocess.run([
                    sys.executable, str(test_script)
                ], capture_output=True, text=True, cwd=self.project_root / 'desktop_app')
                
                if result.returncode != 0:
                    logger.error(f"Post-deployment tests failed: {result.stderr}")
                    return False
            
            # Test API endpoints
            services = self.config['monitoring_config']['services']
            for service in services:
                if 'url' in service and service['url'].startswith('http'):
                    try:
                        response = requests.get(service['url'], timeout=30)
                        if response.status_code != 200:
                            logger.error(f"Service {service['name']} post-deployment test failed")
                            return False
                    except Exception as e:
                        logger.error(f"Service {service['name']} post-deployment test error: {e}")
                        return False
            
            logger.info("Post-deployment tests passed")
            return True
            
        except Exception as e:
            logger.error(f"Post-deployment tests failed: {e}")
            return False
    
    def _rollback_deployment(self, backup_path: str):
        """Rollback to previous deployment"""
        try:
            logger.info(f"Rolling back deployment from backup: {backup_path}")
            
            backup_dir = Path(backup_path)
            
            # Restore database
            backup_db = backup_dir / 'cybersnoop.db'
            if backup_db.exists():
                import shutil
                target_db = self.project_root / 'desktop_app' / 'data' / 'cybersnoop.db'
                shutil.copy2(backup_db, target_db)
            
            # Restore configuration files
            for config_file in backup_dir.glob('*.json'):
                if config_file.name in ['config.json', 'service_config.json', 'deployment_config.json']:
                    target_path = self.project_root / config_file.name
                    import shutil
                    shutil.copy2(config_file, target_path)
            
            logger.info("Rollback completed")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise
    
    def _update_deployment_config(self, deployment_id: str, version: str):
        """Update deployment configuration"""
        config_update = {
            "last_deployment": {
                "id": deployment_id,
                "version": version,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        }
        
        self.config.update(config_update)
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    # 📊 MONITORING OPERATIONS
    def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info("Starting continuous monitoring...")
        
        # Schedule monitoring tasks
        schedule.every(5).minutes.do(self._monitor_services)
        schedule.every(1).hours.do(self._monitor_system_health)
        schedule.every(1).hours.do(self._backup_database)
        schedule.every(24).hours.do(self._check_security_updates)
        schedule.every(7).days.do(self._cleanup_old_backups)
        
        # Run monitoring loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)
    
    def _monitor_services(self):
        """Monitor service health"""
        services = self.config['monitoring_config']['services']
        
        for service in services:
            try:
                if 'url' in service and service['url'].startswith('http'):
                    start_time = time.time()
                    response = requests.get(service['url'], timeout=10)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code != 200:
                        self._send_alert(
                            f"Service {service['name']} is down",
                            f"HTTP {response.status_code} - {service['url']}"
                        )
                    elif response_time > self.config['notification_config']['alert_thresholds']['response_time']:
                        self._send_alert(
                            f"Service {service['name']} slow response",
                            f"Response time: {response_time:.2f}ms"
                        )
                    
            except Exception as e:
                self._send_alert(
                    f"Service {service['name']} monitoring failed",
                    str(e)
                )
    
    def _monitor_system_health(self):
        """Monitor system health metrics"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            thresholds = self.config['notification_config']['alert_thresholds']
            
            if cpu_usage > thresholds['cpu_usage']:
                self._send_alert("High CPU Usage", f"CPU usage: {cpu_usage}%")
            
            if memory.percent > thresholds['memory_usage']:
                self._send_alert("High Memory Usage", f"Memory usage: {memory.percent}%")
            
            if disk.percent > thresholds['disk_usage']:
                self._send_alert("High Disk Usage", f"Disk usage: {disk.percent}%")
            
        except Exception as e:
            logger.error(f"System health monitoring failed: {e}")
    
    def _backup_database(self):
        """Automated database backup"""
        try:
            backup_path = self._create_backup()
            logger.info(f"Automated backup created: {backup_path}")
        except Exception as e:
            logger.error(f"Automated backup failed: {e}")
            self._send_alert("Database Backup Failed", str(e))
    
    def _check_security_updates(self):
        """Check for security updates"""
        try:
            # Check Python package updates
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'list', '--outdated'
            ], capture_output=True, text=True)
            
            if result.stdout:
                outdated_packages = result.stdout.split('\n')
                security_packages = [pkg for pkg in outdated_packages if any(
                    sec_pkg in pkg.lower() for sec_pkg in ['security', 'crypto', 'ssl', 'auth']
                )]
                
                if security_packages:
                    self._send_alert(
                        "Security Updates Available",
                        f"Outdated security-related packages: {len(security_packages)}"
                    )
            
        except Exception as e:
            logger.error(f"Security update check failed: {e}")
    
    def _cleanup_old_backups(self):
        """Clean up old backup files"""
        try:
            backup_dir = Path(self.config['database_config']['backup_location'])
            if not backup_dir.exists():
                return
            
            retention_days = self.config['database_config']['backup_retention_days']
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            removed_count = 0
            for backup_path in backup_dir.glob('backup_*'):
                if backup_path.is_dir():
                    # Parse timestamp from directory name
                    try:
                        timestamp_str = backup_path.name.split('_', 1)[1]
                        backup_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        
                        if backup_date < cutoff_date:
                            import shutil
                            shutil.rmtree(backup_path)
                            removed_count += 1
                    except:
                        continue
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old backups")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def _send_alert(self, title: str, message: str):
        """Send alert notification"""
        logger.warning(f"ALERT: {title} - {message}")
        
        # Here you would integrate with:
        # - Email notifications
        # - Slack webhooks
        # - PagerDuty
        # - SMS alerts
        
        # For now, just log the alert
        alert_data = {
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "severity": "warning"
        }
        
        # Save alert to file for later processing
        alerts_file = Path('alerts.json')
        alerts = []
        
        if alerts_file.exists():
            try:
                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)
            except:
                pass
        
        alerts.append(alert_data)
        
        # Keep only last 100 alerts
        alerts = alerts[-100:]
        
        with open(alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)

# 🎯 Deployment CLI Interface
class DeploymentCLI:
    """Command-line interface for deployment operations"""
    
    def __init__(self):
        self.deployment_manager = DeploymentManager()
    
    def run(self):
        """Run the deployment CLI"""
        print("🚀 CyberSnoop Deployment & Operations Console")
        print("=" * 55)
        
        while True:
            print("\n📋 Available Commands:")
            print("1. Deploy Application")
            print("2. Start Monitoring")
            print("3. Create Backup")
            print("4. System Health Check")
            print("5. View Recent Alerts")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            try:
                if choice == '1':
                    self._deploy_interactive()
                elif choice == '2':
                    self._start_monitoring()
                elif choice == '3':
                    self._create_backup()
                elif choice == '4':
                    self._health_check()
                elif choice == '5':
                    self._view_alerts()
                elif choice == '6':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _deploy_interactive(self):
        """Interactive deployment"""
        print("\n🚀 Deploy Application")
        version = input("Version (leave empty for latest): ").strip() or None
        
        print("Starting deployment...")
        result = self.deployment_manager.deploy_application(version)
        
        if result['status'] == 'success':
            print(f"✅ Deployment successful!")
            print(f"Deployment ID: {result['deployment_id']}")
            print(f"Version: {result.get('version', 'latest')}")
        else:
            print(f"❌ Deployment failed: {result['error']}")
    
    def _start_monitoring(self):
        """Start monitoring services"""
        print("\n📊 Starting Service Monitoring...")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            self.deployment_manager.start_monitoring()
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped")
    
    def _create_backup(self):
        """Create manual backup"""
        print("\n💾 Creating Backup...")
        try:
            backup_path = self.deployment_manager._create_backup()
            print(f"✅ Backup created: {backup_path}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
    
    def _health_check(self):
        """Run system health check"""
        print("\n🏥 System Health Check")
        
        # System resources
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"CPU Usage: {cpu_usage:.1f}%")
        print(f"Memory Usage: {memory.percent:.1f}%")
        print(f"Disk Usage: {disk.percent:.1f}%")
        
        # Service health
        services = self.deployment_manager.config['monitoring_config']['services']
        print("\nService Status:")
        
        for service in services:
            if 'url' in service and service['url'].startswith('http'):
                try:
                    response = requests.get(service['url'], timeout=5)
                    status = "✅ Online" if response.status_code == 200 else f"❌ Error {response.status_code}"
                except:
                    status = "❌ Offline"
                
                print(f"  {service['name']}: {status}")
    
    def _view_alerts(self):
        """View recent alerts"""
        print("\n🚨 Recent Alerts")
        
        alerts_file = Path('alerts.json')
        if not alerts_file.exists():
            print("No alerts found")
            return
        
        try:
            with open(alerts_file, 'r') as f:
                alerts = json.load(f)
            
            if not alerts:
                print("No alerts found")
                return
            
            # Show last 10 alerts
            recent_alerts = alerts[-10:]
            
            for alert in reversed(recent_alerts):
                timestamp = datetime.fromisoformat(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                print(f"🚨 {timestamp} - {alert['title']}")
                print(f"   {alert['message']}")
                print()
        
        except Exception as e:
            print(f"❌ Error reading alerts: {e}")

if __name__ == "__main__":
    # Run the deployment CLI
    cli = DeploymentCLI()
    cli.run()
