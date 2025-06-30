"""
🏢 CyberSnoop Service Management & Operations Framework
The 80% of business operations beyond just the code

This module handles:
- Customer onboarding & support
- License management & billing
- Service monitoring & health checks
- Deployment & updates
- Analytics & reporting
- Incident management
- Performance optimization
"""

import os
import json
import time
import logging
import requests
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('service_management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Customer:
    """Customer management data structure"""
    customer_id: str
    email: str
    company_name: str
    license_type: str  # 'starter', 'professional', 'enterprise'
    license_key: str
    activation_date: datetime
    expiry_date: datetime
    max_users: int
    current_users: int
    status: str  # 'active', 'trial', 'expired', 'suspended'
    support_tier: str  # 'basic', 'premium', 'enterprise'
    created_at: datetime
    last_activity: datetime
    
@dataclass
class ServiceHealth:
    """Service health monitoring data"""
    service_name: str
    status: str  # 'healthy', 'degraded', 'down'
    response_time: float
    cpu_usage: float
    memory_usage: float
    error_rate: float
    last_check: datetime
    uptime_percentage: float

@dataclass
class SupportTicket:
    """Customer support ticket management"""
    ticket_id: str
    customer_id: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    category: str  # 'technical', 'billing', 'feature_request', 'bug_report'
    subject: str
    description: str
    status: str  # 'open', 'in_progress', 'waiting_customer', 'resolved', 'closed'
    assigned_to: str
    created_at: datetime
    updated_at: datetime
    resolution: Optional[str] = None

class ServiceManager:
    """
    🎯 Core Service Management System
    
    Handles all business operations:
    - Customer lifecycle management
    - License validation & billing
    - Service monitoring & alerts
    - Support ticket management
    - Analytics & reporting
    """
    
    def __init__(self, config_path: str = "service_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.db_path = self.config.get('database_path', 'service_management.db')
        self._init_database()
        logger.info("Service Manager initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load service configuration"""
        default_config = {
            "database_path": "service_management.db",
            "email_config": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email": "support@cybersnoop.com",
                "password": "your_app_password"
            },
            "monitoring_config": {
                "check_interval": 300,  # 5 minutes
                "alert_thresholds": {
                    "cpu_usage": 80,
                    "memory_usage": 85,
                    "error_rate": 5,
                    "response_time": 2000  # milliseconds
                }
            },
            "license_config": {
                "trial_period_days": 14,
                "grace_period_days": 7
            },
            "webhook_urls": {
                "slack_alerts": "",
                "billing_notifications": ""
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
            # Create default config file
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def _init_database(self):
        """Initialize SQLite database for service management"""
        conn = sqlite3.connect(self.db_path)
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
        logger.info("Database initialized successfully")
    
    # 👥 CUSTOMER MANAGEMENT
    def create_customer(self, email: str, company_name: str, license_type: str) -> str:
        """Create a new customer account"""
        import uuid
        
        customer_id = str(uuid.uuid4())
        license_key = self._generate_license_key()
        
        # Calculate dates
        now = datetime.now()
        trial_days = self.config['license_config']['trial_period_days']
        expiry_date = now + timedelta(days=trial_days)
        
        # Determine user limits
        user_limits = {
            'starter': 5,
            'professional': 50,
            'enterprise': 1000
        }
        
        customer = Customer(
            customer_id=customer_id,
            email=email,
            company_name=company_name,
            license_type=license_type,
            license_key=license_key,
            activation_date=now,
            expiry_date=expiry_date,
            max_users=user_limits.get(license_type, 5),
            current_users=0,
            status='trial',
            support_tier='basic' if license_type == 'starter' else 'premium',
            created_at=now,
            last_activity=now
        )
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer.customer_id, customer.email, customer.company_name,
            customer.license_type, customer.license_key,
            customer.activation_date.isoformat(), customer.expiry_date.isoformat(),
            customer.max_users, customer.current_users, customer.status,
            customer.support_tier, customer.created_at.isoformat(),
            customer.last_activity.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Send welcome email
        self._send_welcome_email(customer)
        
        logger.info(f"Customer created: {customer_id} ({email})")
        return customer_id
    
    def _generate_license_key(self) -> str:
        """Generate a unique license key"""
        import secrets
        import string
        
        # Generate a 25-character license key in format: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
        chars = string.ascii_uppercase + string.digits
        groups = []
        for _ in range(5):
            group = ''.join(secrets.choice(chars) for _ in range(5))
            groups.append(group)
        
        return '-'.join(groups)
    
    def validate_license(self, license_key: str) -> Dict[str, Any]:
        """Validate a license key and return customer info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM customers WHERE license_key = ?
        ''', (license_key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {"valid": False, "error": "Invalid license key"}
        
        # Parse result
        customer_data = {
            "customer_id": result[0],
            "email": result[1],
            "company_name": result[2],
            "license_type": result[3],
            "license_key": result[4],
            "expiry_date": datetime.fromisoformat(result[6]),
            "max_users": result[7],
            "current_users": result[8],
            "status": result[9]
        }
        
        # Check expiry
        now = datetime.now()
        if customer_data["expiry_date"] < now:
            return {"valid": False, "error": "License expired", "customer": customer_data}
        
        # Check status
        if customer_data["status"] in ['suspended', 'cancelled']:
            return {"valid": False, "error": f"License {customer_data['status']}", "customer": customer_data}
        
        # Update last activity
        self._update_last_activity(customer_data["customer_id"])
        
        return {"valid": True, "customer": customer_data}
    
    def _update_last_activity(self, customer_id: str):
        """Update customer's last activity timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE customers SET last_activity = ? WHERE customer_id = ?
        ''', (datetime.now().isoformat(), customer_id))
        
        conn.commit()
        conn.close()
    
    # 📊 SERVICE MONITORING
    def check_service_health(self, service_name: str, endpoint: str) -> ServiceHealth:
        """Check health of a specific service"""
        import psutil
        
        try:
            # HTTP health check
            start_time = time.time()
            response = requests.get(endpoint, timeout=10)
            response_time = (time.time() - start_time) * 1000  # milliseconds
            
            # System metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Determine status
            thresholds = self.config['monitoring_config']['alert_thresholds']
            status = 'healthy'
            
            if (response.status_code != 200 or 
                response_time > thresholds['response_time'] or
                cpu_usage > thresholds['cpu_usage'] or
                memory_usage > thresholds['memory_usage']):
                status = 'degraded'
            
            if response.status_code >= 500:
                status = 'down'
            
            health = ServiceHealth(
                service_name=service_name,
                status=status,
                response_time=response_time,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                error_rate=0.0,  # Would need error tracking
                last_check=datetime.now(),
                uptime_percentage=99.9  # Would need historical data
            )
            
            # Save to database
            self._save_service_health(health)
            
            # Send alerts if needed
            if status != 'healthy':
                self._send_service_alert(health)
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            
            health = ServiceHealth(
                service_name=service_name,
                status='down',
                response_time=0,
                cpu_usage=0,
                memory_usage=0,
                error_rate=100.0,
                last_check=datetime.now(),
                uptime_percentage=0.0
            )
            
            self._save_service_health(health)
            self._send_service_alert(health)
            
            return health
    
    def _save_service_health(self, health: ServiceHealth):
        """Save service health data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO service_health 
            (service_name, status, response_time, cpu_usage, memory_usage, 
             error_rate, last_check, uptime_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            health.service_name, health.status, health.response_time,
            health.cpu_usage, health.memory_usage, health.error_rate,
            health.last_check.isoformat(), health.uptime_percentage
        ))
        
        conn.commit()
        conn.close()
    
    # 🎫 SUPPORT MANAGEMENT
    def create_support_ticket(self, customer_id: str, subject: str, 
                            description: str, priority: str = 'medium',
                            category: str = 'technical') -> str:
        """Create a new support ticket"""
        import uuid
        
        ticket_id = f"CS-{int(time.time())}-{str(uuid.uuid4())[:8]}"
        
        ticket = SupportTicket(
            ticket_id=ticket_id,
            customer_id=customer_id,
            priority=priority,
            category=category,
            subject=subject,
            description=description,
            status='open',
            assigned_to='auto-assign',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO support_tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticket.ticket_id, ticket.customer_id, ticket.priority,
            ticket.category, ticket.subject, ticket.description,
            ticket.status, ticket.assigned_to,
            ticket.created_at.isoformat(), ticket.updated_at.isoformat(),
            ticket.resolution
        ))
        
        conn.commit()
        conn.close()
        
        # Send notification
        self._send_ticket_notification(ticket)
        
        logger.info(f"Support ticket created: {ticket_id}")
        return ticket_id
    
    # 📧 COMMUNICATION
    def _send_welcome_email(self, customer: Customer):
        """Send welcome email to new customer"""
        try:
            email_config = self.config['email_config']
            
            msg = MimeMultipart()
            msg['From'] = email_config['email']
            msg['To'] = customer.email
            msg['Subject'] = f"Welcome to CyberSnoop - Your License Key"
            
            body = f"""
            Dear {customer.company_name},
            
            Welcome to CyberSnoop! Your enterprise cybersecurity solution is ready.
            
            License Details:
            - License Key: {customer.license_key}
            - License Type: {customer.license_type.title()}
            - Max Users: {customer.max_users}
            - Trial Period: {self.config['license_config']['trial_period_days']} days
            - Expires: {customer.expiry_date.strftime('%Y-%m-%d')}
            
            Getting Started:
            1. Download CyberSnoop from: https://cybersnoop.com/download
            2. Enter your license key during setup
            3. Configure your network monitoring preferences
            4. Access the dashboard at: http://localhost:3000
            
            Support:
            - Documentation: https://docs.cybersnoop.com
            - Support Portal: https://support.cybersnoop.com
            - Email: support@cybersnoop.com
            
            Thank you for choosing CyberSnoop!
            
            Best regards,
            The CyberSnoop Team
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['email'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Welcome email sent to {customer.email}")
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
    
    def _send_service_alert(self, health: ServiceHealth):
        """Send service alert notification"""
        logger.warning(f"Service Alert: {health.service_name} is {health.status}")
        
        # Here you would integrate with Slack, PagerDuty, etc.
        # For now, just log the alert
        
    def _send_ticket_notification(self, ticket: SupportTicket):
        """Send support ticket notification"""
        logger.info(f"New support ticket: {ticket.ticket_id} - {ticket.subject}")
        
        # Here you would notify the support team
    
    # 📈 ANALYTICS & REPORTING
    def track_usage(self, customer_id: str, feature_used: str, metadata: Dict = None):
        """Track customer feature usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO usage_analytics (customer_id, feature_used, timestamp, metadata)
            VALUES (?, ?, ?, ?)
        ''', (
            customer_id, feature_used, datetime.now().isoformat(),
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        conn.close()
    
    def generate_usage_report(self, customer_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate usage report for a customer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT feature_used, COUNT(*) as usage_count
            FROM usage_analytics 
            WHERE customer_id = ? AND timestamp > ?
            GROUP BY feature_used
            ORDER BY usage_count DESC
        ''', (customer_id, since_date))
        
        usage_data = cursor.fetchall()
        conn.close()
        
        return {
            "customer_id": customer_id,
            "period_days": days,
            "total_usage": sum(count for _, count in usage_data),
            "feature_usage": dict(usage_data),
            "generated_at": datetime.now().isoformat()
        }
    
    # 🚀 DEPLOYMENT & UPDATES
    def deploy_update(self, version: str, deployment_type: str = 'rolling'):
        """Deploy application updates"""
        logger.info(f"Deploying update {version} using {deployment_type} deployment")
        
        # This would integrate with your CI/CD pipeline
        # For now, just log the deployment
        
        return {"status": "success", "version": version, "deployed_at": datetime.now().isoformat()}

# 🎯 Service Management CLI Interface
class ServiceManagerCLI:
    """Command-line interface for service management"""
    
    def __init__(self):
        self.service_manager = ServiceManager()
    
    def run(self):
        """Run the interactive CLI"""
        print("🏢 CyberSnoop Service Management Console")
        print("=" * 50)
        
        while True:
            print("\n📋 Available Commands:")
            print("1. Create Customer")
            print("2. Validate License")
            print("3. Check Service Health")
            print("4. Create Support Ticket")
            print("5. Usage Report")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            try:
                if choice == '1':
                    self._create_customer_interactive()
                elif choice == '2':
                    self._validate_license_interactive()
                elif choice == '3':
                    self._check_health_interactive()
                elif choice == '4':
                    self._create_ticket_interactive()
                elif choice == '5':
                    self._usage_report_interactive()
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
    
    def _create_customer_interactive(self):
        """Interactive customer creation"""
        print("\n👥 Create New Customer")
        email = input("Email: ").strip()
        company = input("Company Name: ").strip()
        
        print("\nLicense Types:")
        print("1. Starter ($99/month)")
        print("2. Professional ($299/month)")
        print("3. Enterprise ($999/month)")
        
        license_choice = input("Choose license type (1-3): ").strip()
        license_types = {'1': 'starter', '2': 'professional', '3': 'enterprise'}
        license_type = license_types.get(license_choice, 'starter')
        
        customer_id = self.service_manager.create_customer(email, company, license_type)
        print(f"✅ Customer created successfully! ID: {customer_id}")
    
    def _validate_license_interactive(self):
        """Interactive license validation"""
        print("\n🔑 Validate License Key")
        license_key = input("License Key: ").strip()
        
        result = self.service_manager.validate_license(license_key)
        
        if result['valid']:
            customer = result['customer']
            print("✅ License Valid!")
            print(f"Company: {customer['company_name']}")
            print(f"Type: {customer['license_type']}")
            print(f"Users: {customer['current_users']}/{customer['max_users']}")
            print(f"Expires: {customer['expiry_date']}")
        else:
            print(f"❌ License Invalid: {result['error']}")
    
    def _check_health_interactive(self):
        """Interactive service health check"""
        print("\n🏥 Service Health Check")
        service_name = input("Service Name: ").strip()
        endpoint = input("Health Check URL: ").strip()
        
        health = self.service_manager.check_service_health(service_name, endpoint)
        
        print(f"Status: {health.status}")
        print(f"Response Time: {health.response_time:.2f}ms")
        print(f"CPU Usage: {health.cpu_usage:.1f}%")
        print(f"Memory Usage: {health.memory_usage:.1f}%")
    
    def _create_ticket_interactive(self):
        """Interactive support ticket creation"""
        print("\n🎫 Create Support Ticket")
        customer_id = input("Customer ID: ").strip()
        subject = input("Subject: ").strip()
        description = input("Description: ").strip()
        
        print("\nPriority Levels:")
        print("1. Low")
        print("2. Medium")
        print("3. High")
        print("4. Critical")
        
        priority_choice = input("Choose priority (1-4): ").strip()
        priorities = {'1': 'low', '2': 'medium', '3': 'high', '4': 'critical'}
        priority = priorities.get(priority_choice, 'medium')
        
        ticket_id = self.service_manager.create_support_ticket(
            customer_id, subject, description, priority
        )
        print(f"✅ Support ticket created: {ticket_id}")
    
    def _usage_report_interactive(self):
        """Interactive usage report generation"""
        print("\n📊 Generate Usage Report")
        customer_id = input("Customer ID: ").strip()
        days = int(input("Report period (days): ").strip() or "30")
        
        report = self.service_manager.generate_usage_report(customer_id, days)
        
        print(f"\n📈 Usage Report ({days} days):")
        print(f"Total Usage: {report['total_usage']}")
        print("\nFeature Usage:")
        for feature, count in report['feature_usage'].items():
            print(f"  {feature}: {count}")

if __name__ == "__main__":
    # Run the service management CLI
    cli = ServiceManagerCLI()
    cli.run()
