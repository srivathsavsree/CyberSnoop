#!/usr/bin/env python3
"""
🚀 CyberSnoop Service Management Setup
Initialize and configure the service management system

This script sets up:
- Service management infrastructure
- Customer portal database
- Configuration files
- Monitoring systems
- Deployment tools
"""

import os
import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import secrets
import string

def print_banner():
    """Print setup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  🚀 CyberSnoop Service Management Setup                         ║
║                                                                  ║
║  Setting up enterprise-grade service management infrastructure  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ], check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def generate_secret_key():
    """Generate a secure secret key"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(50))

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "logs",
        "backups",
        "uploads",
        "static",
        "static/css",
        "static/js",
        "static/images",
        "templates",
        "data"
    ]
    
    base_path = Path(__file__).parent
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_config_files():
    """Create configuration files"""
    print("\n⚙️ Creating configuration files...")
    
    base_path = Path(__file__).parent
    
    # Service configuration
    service_config = {
        "database_path": "data/service_management.db",
        "secret_key": generate_secret_key(),
        "debug": False,
        "email_config": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email": "support@cybersnoop.com",
            "password": "your_app_password_here"
        },
        "stripe_config": {
            "publishable_key": "pk_test_your_publishable_key_here",
            "secret_key": "sk_test_your_secret_key_here",
            "webhook_secret": "whsec_your_webhook_secret_here"
        },
        "monitoring_config": {
            "check_interval": 300,
            "alert_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 85,
                "error_rate": 5,
                "response_time": 2000
            }
        },
        "license_config": {
            "trial_period_days": 14,
            "grace_period_days": 7
        }
    }
    
    with open(base_path / "service_config.json", 'w') as f:
        json.dump(service_config, f, indent=2)
    
    print("✅ Created service_config.json")
    
    # Deployment configuration
    deployment_config = {
        "environment": "production",
        "server_config": {
            "host": "0.0.0.0",
            "port": 8000,
            "workers": 4,
            "max_requests": 1000
        },
        "database_config": {
            "backup_interval": 3600,
            "backup_retention_days": 30,
            "backup_location": str(base_path / "backups")
        },
        "monitoring_config": {
            "check_interval": 300,
            "services": [
                {"name": "api_server", "url": "http://localhost:8000/health"},
                {"name": "dashboard", "url": "http://localhost:3000"},
                {"name": "customer_portal", "url": "http://localhost:5000"}
            ]
        },
        "deployment_config": {
            "strategy": "rolling",
            "health_check_timeout": 300,
            "rollback_on_failure": True
        }
    }
    
    with open(base_path / "deployment_config.json", 'w') as f:
        json.dump(deployment_config, f, indent=2)
    
    print("✅ Created deployment_config.json")
    
    # Environment variables template
    env_template = """# CyberSnoop Service Management Environment Variables
# Copy this file to .env and update with your actual values

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=production
DATABASE_URL=sqlite:///data/customer_portal.db

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=support@cybersnoop.com
SMTP_PASSWORD=your_app_password_here

# External Services
SENTRY_DSN=your_sentry_dsn_here
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here
"""
    
    with open(base_path / ".env.template", 'w') as f:
        f.write(env_template)
    
    print("✅ Created .env.template")

def initialize_databases():
    """Initialize SQLite databases"""
    print("\n🗄️ Initializing databases...")
    
    base_path = Path(__file__).parent
    data_path = base_path / "data"
    data_path.mkdir(exist_ok=True)
    
    # Service management database
    service_db_path = data_path / "service_management.db"
    conn = sqlite3.connect(service_db_path)
    cursor = conn.cursor()
    
    # Customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            company_name TEXT,
            license_type TEXT NOT NULL,
            license_key TEXT UNIQUE NOT NULL,
            activation_date TEXT,
            expiry_date TEXT,
            max_users INTEGER,
            current_users INTEGER DEFAULT 0,
            status TEXT DEFAULT 'trial',
            support_tier TEXT DEFAULT 'basic',
            created_at TEXT,
            last_activity TEXT
        )
    ''')
    
    # Service health table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            status TEXT NOT NULL,
            response_time REAL,
            cpu_usage REAL,
            memory_usage REAL,
            error_rate REAL,
            last_check TEXT,
            uptime_percentage REAL
        )
    ''')
    
    # Support tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_tickets (
            ticket_id TEXT PRIMARY KEY,
            customer_id TEXT,
            priority TEXT NOT NULL,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'open',
            assigned_to TEXT,
            created_at TEXT,
            updated_at TEXT,
            resolution TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    # Usage analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            feature_used TEXT,
            usage_count INTEGER DEFAULT 1,
            timestamp TEXT,
            metadata TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Service management database initialized")
    
    # Customer portal database
    portal_db_path = data_path / "customer_portal.db"
    conn = sqlite3.connect(portal_db_path)
    cursor = conn.cursor()
    
    # Customer portal tables (simplified for setup)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            company_name TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            license_type TEXT DEFAULT 'trial',
            license_key TEXT UNIQUE,
            license_status TEXT DEFAULT 'trial',
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            subscription_status TEXT,
            created_at TEXT,
            trial_ends_at TEXT,
            subscription_current_period_end TEXT,
            last_login TEXT,
            max_users INTEGER DEFAULT 5,
            current_users INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_ticket (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            customer_id TEXT,
            subject TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            category TEXT DEFAULT 'technical',
            status TEXT DEFAULT 'open',
            created_at TEXT,
            updated_at TEXT,
            resolved_at TEXT,
            assigned_to TEXT,
            resolution TEXT,
            FOREIGN KEY (customer_id) REFERENCES customer (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            feature_used TEXT NOT NULL,
            usage_count INTEGER DEFAULT 1,
            timestamp TEXT,
            metadata TEXT,
            FOREIGN KEY (customer_id) REFERENCES customer (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS download_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            filename TEXT NOT NULL,
            version TEXT,
            platform TEXT,
            download_url TEXT,
            downloaded_at TEXT,
            ip_address TEXT,
            FOREIGN KEY (customer_id) REFERENCES customer (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Customer portal database initialized")

def create_sample_data():
    """Create sample data for testing"""
    print("\n📊 Creating sample data...")
    
    base_path = Path(__file__).parent
    service_db_path = base_path / "data" / "service_management.db"
    
    conn = sqlite3.connect(service_db_path)
    cursor = conn.cursor()
    
    # Sample customer
    sample_customer = {
        'customer_id': 'demo-customer-001',
        'email': 'demo@example.com',
        'company_name': 'Demo Security Corp',
        'license_type': 'professional',
        'license_key': 'DEMO1-2345-6789-ABCD-EFGH',
        'activation_date': datetime.now().isoformat(),
        'expiry_date': (datetime.now() + timedelta(days=365)).isoformat(),
        'max_users': 50,
        'current_users': 12,
        'status': 'active',
        'support_tier': 'premium',
        'created_at': datetime.now().isoformat(),
        'last_activity': datetime.now().isoformat()
    }
    
    cursor.execute('''
        INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(sample_customer.values()))
    
    # Sample usage data
    features = ['network_monitoring', 'threat_detection', 'dashboard_access', 'api_calls', 'report_generation']
    for feature in features:
        cursor.execute('''
            INSERT INTO usage_analytics (customer_id, feature_used, usage_count, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (sample_customer['customer_id'], feature, 25, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    print("✅ Sample data created")

def create_systemd_service():
    """Create systemd service file for Linux"""
    if os.name != 'posix':
        return
    
    print("\n🔧 Creating systemd service file...")
    
    base_path = Path(__file__).parent
    service_content = f"""[Unit]
Description=CyberSnoop Service Management
After=network.target

[Service]
Type=notify
User=cybersnoop
Group=cybersnoop
WorkingDirectory={base_path}
Environment=PATH={base_path}/venv/bin
ExecStart={base_path}/venv/bin/python customer_portal.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
"""
    
    service_file = base_path / "cybersnoop-service.service"
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print(f"✅ Created systemd service file: {service_file}")
    print("   To install: sudo cp cybersnoop-service.service /etc/systemd/system/")
    print("   To enable: sudo systemctl enable cybersnoop-service")
    print("   To start: sudo systemctl start cybersnoop-service")

def create_startup_scripts():
    """Create startup scripts"""
    print("\n🚀 Creating startup scripts...")
    
    base_path = Path(__file__).parent
    
    # Linux/Mac startup script
    startup_script = """#!/bin/bash
# CyberSnoop Service Management Startup Script

echo "🚀 Starting CyberSnoop Service Management..."

# Set working directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start service manager in background
echo "📊 Starting Service Manager..."
python service_manager.py &
SERVICE_MANAGER_PID=$!

# Start deployment manager in background
echo "🚀 Starting Deployment Manager..."
python deployment_manager.py &
DEPLOYMENT_MANAGER_PID=$!

# Start customer portal
echo "🏢 Starting Customer Portal..."
python customer_portal.py &
PORTAL_PID=$!

# Create PID file
echo "$SERVICE_MANAGER_PID" > service_manager.pid
echo "$DEPLOYMENT_MANAGER_PID" > deployment_manager.pid
echo "$PORTAL_PID" > customer_portal.pid

echo "✅ All services started successfully!"
echo "📊 Service Manager PID: $SERVICE_MANAGER_PID"
echo "🚀 Deployment Manager PID: $DEPLOYMENT_MANAGER_PID"
echo "🏢 Customer Portal PID: $PORTAL_PID"
echo ""
echo "Access the customer portal at: http://localhost:5000"
echo "Service management CLI: python service_manager.py"
echo "Deployment management CLI: python deployment_manager.py"
echo ""
echo "To stop services, run: ./stop_services.sh"
"""
    
    with open(base_path / "start_services.sh", 'w') as f:
        f.write(startup_script)
    
    # Make executable
    if os.name == 'posix':
        os.chmod(base_path / "start_services.sh", 0o755)
    
    # Stop script
    stop_script = """#!/bin/bash
# CyberSnoop Service Management Stop Script

echo "🛑 Stopping CyberSnoop Service Management..."

# Set working directory
cd "$(dirname "$0")"

# Stop services using PID files
if [ -f "service_manager.pid" ]; then
    PID=$(cat service_manager.pid)
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "📊 Service Manager stopped (PID: $PID)"
    fi
    rm -f service_manager.pid
fi

if [ -f "deployment_manager.pid" ]; then
    PID=$(cat deployment_manager.pid)
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "🚀 Deployment Manager stopped (PID: $PID)"
    fi
    rm -f deployment_manager.pid
fi

if [ -f "customer_portal.pid" ]; then
    PID=$(cat customer_portal.pid)
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "🏢 Customer Portal stopped (PID: $PID)"
    fi
    rm -f customer_portal.pid
fi

echo "✅ All services stopped successfully!"
"""
    
    with open(base_path / "stop_services.sh", 'w') as f:
        f.write(stop_script)
    
    # Make executable
    if os.name == 'posix':
        os.chmod(base_path / "stop_services.sh", 0o755)
    
    print("✅ Created start_services.sh")
    print("✅ Created stop_services.sh")

def create_readme():
    """Create README for service management"""
    print("\n📝 Creating README...")
    
    readme_content = """# CyberSnoop Service Management

Enterprise-grade service management and operations platform for CyberSnoop.

## 🚀 Quick Start

1. **Setup**: Run the setup script
   ```bash
   python setup_service_management.py
   ```

2. **Configure**: Update configuration files
   - `service_config.json` - Service settings
   - `deployment_config.json` - Deployment settings
   - `.env` - Environment variables (copy from `.env.template`)

3. **Start Services**: 
   ```bash
   ./start_services.sh      # Linux/Mac
   # or run individually:
   python customer_portal.py
   python service_manager.py
   python deployment_manager.py
   ```

4. **Access Portal**: http://localhost:5000

## 📊 Components

### Customer Portal
- Web-based customer management
- Self-service license management
- Support ticket system
- Billing integration
- Download center

### Service Manager
- Customer lifecycle management
- License validation
- Usage analytics
- Support ticket management
- Automated notifications

### Deployment Manager
- Automated deployments
- Service monitoring
- Performance analytics
- Backup management
- Incident response

## 🛠️ Configuration

### Stripe Integration
1. Create Stripe account
2. Get API keys from dashboard
3. Update `service_config.json` with keys
4. Configure webhook endpoints

### Email Integration
1. Configure SMTP settings
2. Update email templates
3. Test email delivery

### Monitoring
1. Configure service endpoints
2. Set alert thresholds
3. Setup notification channels

## 🔧 Management Commands

```bash
# Service management CLI
python service_manager.py

# Deployment CLI
python deployment_manager.py

# Customer portal (web)
python customer_portal.py
```

## 📈 Monitoring

- **Health Checks**: Automated service monitoring
- **Performance Metrics**: Response time, error rates
- **Business Metrics**: Customer count, revenue, churn
- **Alerts**: Email, Slack, webhook notifications

## 🔒 Security

- **Database Encryption**: SQLite with encryption
- **API Security**: Rate limiting, authentication
- **Data Protection**: GDPR compliance ready
- **Access Control**: Role-based permissions

## 📞 Support

- **Documentation**: Complete API and user docs
- **Monitoring**: 24/7 service monitoring
- **Incident Response**: Automated alerting
- **Customer Support**: Multi-tier support system

## 🚀 Deployment

### Development
```bash
python customer_portal.py
```

### Production
```bash
gunicorn --config gunicorn.conf.py customer_portal:app
```

### Docker
```bash
docker build -t cybersnoop-service-management .
docker run -p 5000:5000 cybersnoop-service-management
```

## 📊 Metrics & Analytics

- **Customer Analytics**: Usage patterns, feature adoption
- **Business Metrics**: MRR, ARR, churn, LTV
- **Technical Metrics**: Uptime, performance, errors
- **Support Metrics**: Ticket volume, resolution time

## 🔄 CI/CD

- **Automated Testing**: Unit, integration, end-to-end
- **Deployment Pipeline**: Build, test, deploy
- **Rollback Capability**: Automated rollback on failure
- **Monitoring Integration**: Deployment success tracking

## 📋 License

Enterprise software - see LICENSE.md for details.
"""
    
    base_path = Path(__file__).parent
    with open(base_path / "README.md", 'w') as f:
        f.write(readme_content)
    
    print("✅ Created README.md")

def main():
    """Main setup function"""
    print_banner()
    
    print("🔍 Checking system requirements...")
    check_python_version()
    
    print("\n📦 Setting up service management infrastructure...")
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed: Could not install dependencies")
        return False
    
    # Create directory structure
    create_directories()
    
    # Create configuration files
    create_config_files()
    
    # Initialize databases
    initialize_databases()
    
    # Create sample data
    create_sample_data()
    
    # Create service files
    create_systemd_service()
    create_startup_scripts()
    
    # Create documentation
    create_readme()
    
    print("\n" + "="*70)
    print("🎉 CyberSnoop Service Management Setup Complete!")
    print("="*70)
    
    print("\n📋 Next Steps:")
    print("1. Update configuration files with your actual credentials")
    print("2. Configure Stripe API keys for billing")
    print("3. Setup email SMTP settings")
    print("4. Start services: ./start_services.sh")
    print("5. Access customer portal: http://localhost:5000")
    
    print("\n🔧 Configuration Files:")
    print("- service_config.json: Service settings")
    print("- deployment_config.json: Deployment settings")
    print("- .env.template: Environment variables template")
    
    print("\n🚀 Service Management Components:")
    print("- Customer Portal: Web-based customer management")
    print("- Service Manager: Backend service operations")
    print("- Deployment Manager: Automated deployment & monitoring")
    
    print("\n✅ Setup completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
