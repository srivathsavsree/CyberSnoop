"""
💼 CyberSnoop Customer Portal & Billing Integration
Web-based customer management and billing system

This module provides:
- Customer self-service portal
- License management
- Billing & subscription management
- Support ticket system
- Usage analytics dashboard
- Download center
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import stripe
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customer_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure Stripe (replace with your keys)
stripe.api_key = 'sk_test_your_stripe_secret_key'  # Replace with actual key

# Database Models
class Customer(UserMixin, db.Model):
    """Customer account model"""
    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    company_name = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    
    # License information
    license_type = db.Column(db.String(20), default='trial')  # starter, professional, enterprise
    license_key = db.Column(db.String(30), unique=True)
    license_status = db.Column(db.String(20), default='trial')  # active, trial, expired, suspended
    
    # Subscription information
    stripe_customer_id = db.Column(db.String(50))
    stripe_subscription_id = db.Column(db.String(50))
    subscription_status = db.Column(db.String(20))  # active, past_due, canceled, etc.
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trial_ends_at = db.Column(db.DateTime)
    subscription_current_period_end = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    
    # Usage limits
    max_users = db.Column(db.Integer, default=5)
    current_users = db.Column(db.Integer, default=0)
    
    # Relationships
    support_tickets = db.relationship('SupportTicket', backref='customer', lazy=True)
    usage_records = db.relationship('UsageRecord', backref='customer', lazy=True)

class SupportTicket(db.Model):
    """Support ticket model"""
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customer.id'), nullable=False)
    
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, critical
    category = db.Column(db.String(20), default='technical')  # technical, billing, feature_request
    status = db.Column(db.String(20), default='open')  # open, in_progress, waiting_customer, resolved, closed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Admin fields
    assigned_to = db.Column(db.String(50))
    resolution = db.Column(db.Text)

class UsageRecord(db.Model):
    """Customer usage tracking"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('customer.id'), nullable=False)
    
    feature_used = db.Column(db.String(50), nullable=False)
    usage_count = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    metadata = db.Column(db.Text)  # JSON metadata

class DownloadLog(db.Model):
    """Track customer downloads"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('customer.id'), nullable=False)
    
    filename = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20))
    platform = db.Column(db.String(20))  # windows, mac, linux
    download_url = db.Column(db.String(200))
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))

@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(user_id)

# Utility Functions
def generate_license_key():
    """Generate a unique license key"""
    import secrets
    import string
    
    chars = string.ascii_uppercase + string.digits
    groups = []
    for _ in range(5):
        group = ''.join(secrets.choice(chars) for _ in range(5))
        groups.append(group)
    
    return '-'.join(groups)

def generate_ticket_id():
    """Generate a unique support ticket ID"""
    import uuid
    timestamp = int(datetime.utcnow().timestamp())
    short_uuid = str(uuid.uuid4())[:8]
    return f"CS-{timestamp}-{short_uuid}"

# Stripe Integration
class BillingManager:
    """Handles Stripe billing operations"""
    
    PRICING_PLANS = {
        'starter': {
            'name': 'Starter Plan',
            'price': 9900,  # $99 in cents
            'stripe_price_id': 'price_starter_monthly',  # Replace with actual Stripe price ID
            'max_users': 5,
            'features': ['Network Monitoring', 'Threat Detection', 'Basic Reports']
        },
        'professional': {
            'name': 'Professional Plan',
            'price': 29900,  # $299 in cents
            'stripe_price_id': 'price_professional_monthly',
            'max_users': 50,
            'features': ['All Starter Features', 'Advanced Analytics', 'API Access', 'Priority Support']
        },
        'enterprise': {
            'name': 'Enterprise Plan',
            'price': 99900,  # $999 in cents
            'stripe_price_id': 'price_enterprise_monthly',
            'max_users': 1000,
            'features': ['All Professional Features', 'SIEM Integration', 'Custom Reports', 'Dedicated Support']
        }
    }
    
    @staticmethod
    def create_customer(email: str, name: str) -> str:
        """Create Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            return customer.id
        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise
    
    @staticmethod
    def create_subscription(customer_id: str, plan: str) -> Dict[str, Any]:
        """Create Stripe subscription"""
        try:
            plan_info = BillingManager.PRICING_PLANS.get(plan)
            if not plan_info:
                raise ValueError(f"Invalid plan: {plan}")
            
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    'price': plan_info['stripe_price_id']
                }],
                trial_period_days=14
            )
            
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end),
                'trial_end': datetime.fromtimestamp(subscription.trial_end) if subscription.trial_end else None
            }
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            raise
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> bool:
        """Cancel Stripe subscription"""
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False

# Routes
@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('pricing.html', plans=BillingManager.PRICING_PLANS)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration"""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            
            # Validate input
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            company_name = data.get('company_name', '').strip()
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            plan = data.get('plan', 'starter')
            
            if not all([email, password, company_name]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Check if customer already exists
            if Customer.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already registered'}), 400
            
            # Create Stripe customer
            stripe_customer_id = BillingManager.create_customer(
                email=email,
                name=f"{first_name} {last_name}".strip()
            )
            
            # Generate license key
            license_key = generate_license_key()
            
            # Create customer record
            import uuid
            customer = Customer(
                id=str(uuid.uuid4()),
                email=email,
                password_hash=generate_password_hash(password),
                company_name=company_name,
                first_name=first_name,
                last_name=last_name,
                license_type=plan,
                license_key=license_key,
                license_status='trial',
                stripe_customer_id=stripe_customer_id,
                trial_ends_at=datetime.utcnow() + timedelta(days=14),
                max_users=BillingManager.PRICING_PLANS[plan]['max_users']
            )
            
            db.session.add(customer)
            db.session.commit()
            
            # Log in the user
            login_user(customer)
            
            return jsonify({
                'success': True,
                'message': 'Account created successfully',
                'license_key': license_key,
                'redirect': url_for('dashboard')
            })
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return jsonify({'error': 'Registration failed'}), 500
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login"""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            customer = Customer.query.filter_by(email=email).first()
            
            if customer and check_password_hash(customer.password_hash, password):
                login_user(customer)
                customer.last_login = datetime.utcnow()
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'redirect': url_for('dashboard')
                })
            else:
                return jsonify({'error': 'Invalid email or password'}), 401
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return jsonify({'error': 'Login failed'}), 500
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Customer logout"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Customer dashboard"""
    # Get usage statistics
    usage_stats = db.session.query(
        UsageRecord.feature_used,
        db.func.sum(UsageRecord.usage_count).label('total_usage')
    ).filter_by(customer_id=current_user.id)\
     .group_by(UsageRecord.feature_used)\
     .all()
    
    # Get recent support tickets
    recent_tickets = SupportTicket.query.filter_by(customer_id=current_user.id)\
                                       .order_by(SupportTicket.created_at.desc())\
                                       .limit(5).all()
    
    return render_template('dashboard.html', 
                         customer=current_user, 
                         usage_stats=usage_stats,
                         recent_tickets=recent_tickets)

@app.route('/billing')
@login_required
def billing():
    """Billing and subscription management"""
    try:
        # Get Stripe customer info
        stripe_customer = None
        if current_user.stripe_customer_id:
            stripe_customer = stripe.Customer.retrieve(current_user.stripe_customer_id)
        
        # Get subscription info
        subscription = None
        if current_user.stripe_subscription_id:
            subscription = stripe.Subscription.retrieve(current_user.stripe_subscription_id)
        
        return render_template('billing.html', 
                             customer=current_user,
                             stripe_customer=stripe_customer,
                             subscription=subscription,
                             plans=BillingManager.PRICING_PLANS)
        
    except Exception as e:
        logger.error(f"Billing page error: {e}")
        flash('Error loading billing information', 'error')
        return redirect(url_for('dashboard'))

@app.route('/support')
@login_required
def support():
    """Support tickets page"""
    tickets = SupportTicket.query.filter_by(customer_id=current_user.id)\
                                .order_by(SupportTicket.created_at.desc())\
                                .all()
    
    return render_template('support.html', tickets=tickets)

@app.route('/support/create', methods=['POST'])
@login_required
def create_support_ticket():
    """Create new support ticket"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        subject = data.get('subject', '').strip()
        description = data.get('description', '').strip()
        priority = data.get('priority', 'medium')
        category = data.get('category', 'technical')
        
        if not all([subject, description]):
            return jsonify({'error': 'Subject and description are required'}), 400
        
        ticket = SupportTicket(
            ticket_id=generate_ticket_id(),
            customer_id=current_user.id,
            subject=subject,
            description=description,
            priority=priority,
            category=category
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'ticket_id': ticket.ticket_id,
            'message': 'Support ticket created successfully'
        })
        
    except Exception as e:
        logger.error(f"Support ticket creation error: {e}")
        return jsonify({'error': 'Failed to create support ticket'}), 500

@app.route('/downloads')
@login_required
def downloads():
    """Download center"""
    # Available downloads based on license type
    available_downloads = {
        'starter': [
            {'name': 'CyberSnoop Desktop', 'version': '3.0.0', 'platform': 'windows', 'filename': 'cybersnoop-desktop-3.0.0-win.exe'},
            {'name': 'CyberSnoop Desktop', 'version': '3.0.0', 'platform': 'mac', 'filename': 'cybersnoop-desktop-3.0.0-mac.dmg'},
            {'name': 'CyberSnoop Desktop', 'version': '3.0.0', 'platform': 'linux', 'filename': 'cybersnoop-desktop-3.0.0-linux.AppImage'},
        ],
        'professional': [
            {'name': 'CyberSnoop Desktop Pro', 'version': '3.0.0', 'platform': 'windows', 'filename': 'cybersnoop-pro-3.0.0-win.exe'},
            {'name': 'CyberSnoop Desktop Pro', 'version': '3.0.0', 'platform': 'mac', 'filename': 'cybersnoop-pro-3.0.0-mac.dmg'},
            {'name': 'CyberSnoop Desktop Pro', 'version': '3.0.0', 'platform': 'linux', 'filename': 'cybersnoop-pro-3.0.0-linux.AppImage'},
            {'name': 'API Documentation', 'version': '3.0.0', 'platform': 'pdf', 'filename': 'cybersnoop-api-docs-3.0.0.pdf'},
        ],
        'enterprise': [
            {'name': 'CyberSnoop Enterprise', 'version': '3.0.0', 'platform': 'windows', 'filename': 'cybersnoop-enterprise-3.0.0-win.exe'},
            {'name': 'CyberSnoop Enterprise', 'version': '3.0.0', 'platform': 'mac', 'filename': 'cybersnoop-enterprise-3.0.0-mac.dmg'},
            {'name': 'CyberSnoop Enterprise', 'version': '3.0.0', 'platform': 'linux', 'filename': 'cybersnoop-enterprise-3.0.0-linux.AppImage'},
            {'name': 'Enterprise Setup Guide', 'version': '3.0.0', 'platform': 'pdf', 'filename': 'cybersnoop-enterprise-setup-3.0.0.pdf'},
            {'name': 'SIEM Integration Kit', 'version': '3.0.0', 'platform': 'zip', 'filename': 'cybersnoop-siem-integration-3.0.0.zip'},
        ]
    }
    
    # Get download history
    download_history = DownloadLog.query.filter_by(customer_id=current_user.id)\
                                       .order_by(DownloadLog.downloaded_at.desc())\
                                       .limit(10).all()
    
    downloads = available_downloads.get(current_user.license_type, available_downloads['starter'])
    
    return render_template('downloads.html', 
                         downloads=downloads,
                         download_history=download_history)

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    """Handle file downloads"""
    try:
        # Log the download
        download_log = DownloadLog(
            customer_id=current_user.id,
            filename=filename,
            ip_address=request.remote_addr
        )
        db.session.add(download_log)
        db.session.commit()
        
        # In production, this would serve files from a secure location
        # For now, return a download URL
        download_url = f"https://downloads.cybersnoop.com/{filename}"
        
        return jsonify({
            'success': True,
            'download_url': download_url,
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': 'Download failed'}), 500

# API Endpoints
@app.route('/api/license/validate', methods=['POST'])
def validate_license_api():
    """API endpoint for license validation"""
    try:
        data = request.get_json()
        license_key = data.get('license_key')
        
        if not license_key:
            return jsonify({'valid': False, 'error': 'License key required'}), 400
        
        customer = Customer.query.filter_by(license_key=license_key).first()
        
        if not customer:
            return jsonify({'valid': False, 'error': 'Invalid license key'}), 404
        
        # Check license status
        if customer.license_status == 'expired':
            return jsonify({'valid': False, 'error': 'License expired'}), 403
        
        if customer.license_status == 'suspended':
            return jsonify({'valid': False, 'error': 'License suspended'}), 403
        
        # Check trial expiry
        if customer.license_status == 'trial' and customer.trial_ends_at < datetime.utcnow():
            customer.license_status = 'expired'
            db.session.commit()
            return jsonify({'valid': False, 'error': 'Trial expired'}), 403
        
        return jsonify({
            'valid': True,
            'customer_id': customer.id,
            'license_type': customer.license_type,
            'max_users': customer.max_users,
            'current_users': customer.current_users,
            'expires_at': customer.trial_ends_at.isoformat() if customer.trial_ends_at else None
        })
        
    except Exception as e:
        logger.error(f"License validation error: {e}")
        return jsonify({'valid': False, 'error': 'Validation failed'}), 500

@app.route('/api/usage/track', methods=['POST'])
def track_usage_api():
    """API endpoint for tracking feature usage"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        feature_used = data.get('feature_used')
        usage_count = data.get('usage_count', 1)
        metadata = data.get('metadata')
        
        if not all([customer_id, feature_used]):
            return jsonify({'error': 'Customer ID and feature are required'}), 400
        
        # Verify customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Invalid customer ID'}), 404
        
        # Record usage
        usage_record = UsageRecord(
            customer_id=customer_id,
            feature_used=feature_used,
            usage_count=usage_count,
            metadata=json.dumps(metadata) if metadata else None
        )
        
        db.session.add(usage_record)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Usage tracked'})
        
    except Exception as e:
        logger.error(f"Usage tracking error: {e}")
        return jsonify({'error': 'Usage tracking failed'}), 500

# Initialize database
@app.before_first_request
def create_tables():
    """Create database tables"""
    db.create_all()

if __name__ == '__main__':
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Run development server
    app.run(debug=True, host='0.0.0.0', port=5000)
