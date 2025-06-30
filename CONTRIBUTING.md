# Contributing to CyberSnoop

First off, thank you for considering contributing to CyberSnoop! 🎉

CyberSnoop is an open source project and we love to receive contributions from our community. There are many ways to contribute, from writing tutorials or blog posts, improving the documentation, submitting bug reports and feature requests or writing code which can be incorporated into CyberSnoop itself.

## 🚀 Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a new branch** for your feature/fix
4. **Make your changes** with tests
5. **Submit a pull request**

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🏁 Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for dashboard development)
- Git
- Windows 10/11 (for testing desktop features)

### Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/cybersnoop.git
cd cybersnoop

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/macOS

# 3. Install development dependencies
cd desktop_app
pip install -r requirements.txt
pip install -r ../enterprise_requirements.txt

# 4. Install pre-commit hooks
pip install pre-commit
pre-commit install

# 5. Set up the dashboard
cd ../cybersnoop-dashboard
npm install
npm run build

# 6. Run tests to verify setup
cd ../desktop_app
python test_phase3_comprehensive.py
```

## 🤝 How to Contribute

### 🐛 Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include:

- **Clear description** of the problem
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Screenshots** if applicable
- **Environment details** (OS, Python version, etc.)
- **Log files** if relevant

Use our [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md).

### ✨ Suggesting Features

Feature requests are welcome! Please provide:

- **Clear description** of the feature
- **Use case** - why would this be useful?
- **Possible implementation** approach
- **Alternative solutions** you've considered

Use our [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md).

### 💻 Code Contributions

#### Types of Contributions Welcome:

1. **🔧 Core Features**
   - Network monitoring improvements
   - Threat detection enhancements
   - Performance optimizations

2. **🎨 UI/UX Improvements**
   - Dashboard enhancements
   - Desktop application improvements
   - Accessibility features

3. **🏢 Enterprise Features**
   - SIEM integrations
   - Compliance reporting
   - API enhancements

4. **📱 Platform Support**
   - Linux compatibility
   - macOS support
   - Mobile companion apps

5. **🧪 Testing & Quality**
   - Unit tests
   - Integration tests
   - Performance testing

6. **📚 Documentation**
   - User guides
   - API documentation
   - Code comments

## 🔄 Pull Request Process

### Before You Start

1. **Check existing issues** - your feature might already be in progress
2. **Create an issue** to discuss major changes
3. **Fork the repository** and create a feature branch
4. **Keep changes focused** - one feature per PR

### Pull Request Guidelines

1. **Branch naming**: Use descriptive names
   ```
   feature/siem-integration
   bugfix/dashboard-memory-leak
   docs/api-reference-update
   ```

2. **Commit messages**: Follow conventional commits
   ```
   feat: add Splunk SIEM integration
   fix: resolve dashboard memory leak
   docs: update API reference documentation
   test: add unit tests for threat detector
   ```

3. **Code quality**:
   - ✅ All tests must pass
   - ✅ Code follows PEP 8 style guide
   - ✅ Type hints included
   - ✅ Documentation updated
   - ✅ No security vulnerabilities

4. **Pull request template**:
   - Description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if UI changes)
   - Breaking changes (if any)

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by maintainers
3. **Testing** on multiple environments
4. **Documentation** review
5. **Security review** (for security-related changes)

## 🎯 Coding Standards

### Python Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specifics:

```python
# Line length: 88 characters (Black formatter)
# String quotes: Double quotes preferred
# Import order: isort configuration

# Example function with proper docstring
def detect_port_scan(packets: List[Packet], threshold: int = 100) -> List[ThreatAlert]:
    """
    Detect port scanning attacks in network traffic.
    
    Args:
        packets: List of network packets to analyze
        threshold: Minimum number of ports to trigger alert
        
    Returns:
        List of threat alerts for detected port scans
        
    Raises:
        ValueError: If threshold is negative
    """
    if threshold < 0:
        raise ValueError("Threshold must be non-negative")
    
    # Implementation here
    return alerts
```

### TypeScript/React Style

```typescript
// Use TypeScript strict mode
// Prefer functional components with hooks
// Use descriptive prop interfaces

interface ThreatAlertProps {
  alert: ThreatAlert;
  onDismiss: (alertId: string) => void;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

const ThreatAlertComponent: React.FC<ThreatAlertProps> = ({
  alert,
  onDismiss,
  severity
}) => {
  // Component implementation
};
```

### Code Organization

```
desktop_app/
├── backend/                 # Core business logic
│   ├── __init__.py
│   ├── network_monitor.py   # Network monitoring
│   ├── threat_detector.py   # Threat detection
│   └── database_manager.py  # Data persistence
├── config/                  # Configuration management
├── ui/                      # User interface components
├── tests/                   # Test suites
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/               # End-to-end tests
└── utils/                  # Utility functions
```

## 🧪 Testing Guidelines

### Test Types

1. **Unit Tests** - Test individual components
   ```python
   def test_port_scan_detection():
       detector = ThreatDetector()
       packets = create_port_scan_packets()
       alerts = detector.detect_port_scan(packets)
       assert len(alerts) == 1
       assert alerts[0].threat_type == "PORT_SCAN"
   ```

2. **Integration Tests** - Test component interactions
   ```python
   def test_database_threat_storage():
       db = DatabaseManager()
       detector = ThreatDetector()
       threat = detector.analyze_packet(malicious_packet)
       db.store_threat(threat)
       retrieved = db.get_threats(limit=1)
       assert retrieved[0].id == threat.id
   ```

3. **Performance Tests** - Verify performance requirements
   ```python
   def test_packet_processing_performance():
       monitor = NetworkMonitor()
       start_time = time.time()
       monitor.process_packets(large_packet_set)
       duration = time.time() - start_time
       assert duration < 1.0  # Must process in under 1 second
   ```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test files
python test_phase3_comprehensive.py

# Run with coverage
python -m pytest --cov=backend --cov-report=html

# Run performance tests
python -m pytest tests/performance/
```

### Test Coverage Requirements

- **Minimum 80%** code coverage for new features
- **90%+ coverage** for critical security components
- **100% coverage** for utility functions

## 📚 Documentation

### Code Documentation

- **Docstrings** for all public functions and classes
- **Type hints** for function parameters and return values
- **Inline comments** for complex logic
- **README files** for each major component

### User Documentation

- **Getting Started** guides for new users
- **Configuration** examples with explanations
- **Troubleshooting** guides for common issues
- **API Reference** with complete examples

### Documentation Standards

```python
class ThreatDetector:
    """
    Advanced threat detection engine for network security monitoring.
    
    This class implements multiple detection algorithms to identify
    various types of network threats including port scans, DDoS attacks,
    and malware communication patterns.
    
    Attributes:
        config: Configuration manager instance
        algorithms: List of enabled detection algorithms
        
    Example:
        detector = ThreatDetector(config_manager)
        threats = detector.analyze_packets(packet_list)
        for threat in threats:
            print(f"Detected: {threat.threat_type}")
    """
```

## 🌍 Community

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and ideas
- **Discord** - Real-time chat with community
- **Email** - security@cybersnoop.com for security issues

### Community Guidelines

1. **Be respectful** and inclusive
2. **Help others** learn and grow
3. **Share knowledge** and experiences
4. **Give constructive feedback**
5. **Follow the code of conduct**

### Recognition

Contributors are recognized in several ways:

- **Contributors page** on our website
- **GitHub contributors graph**
- **Release notes** acknowledgments
- **Swag and stickers** for significant contributions
- **Speaking opportunities** at conferences

## 🏆 Contribution Levels

### 🥉 Bronze Contributors
- First-time contributors
- Bug fixes and small improvements
- Documentation updates

### 🥈 Silver Contributors  
- Multiple contributions
- Feature implementations
- Code reviews

### 🥇 Gold Contributors
- Major feature development
- Architecture improvements
- Community leadership

### 💎 Core Contributors
- Long-term commitment
- Major decision making
- Release management

## 📝 License

By contributing to CyberSnoop, you agree that your contributions will be licensed under the MIT License for the open source components and appropriate commercial licenses for enterprise features.

## ❓ Questions?

Don't hesitate to ask questions! You can:

- **Create a discussion** on GitHub
- **Join our Discord** server
- **Email us** at contribute@cybersnoop.com
- **Attend** our monthly contributor meetings

## 🎉 Thank You!

Every contribution, no matter how small, makes CyberSnoop better for everyone. Thank you for being part of our community!

---

**Happy Contributing! 🚀**

*CyberSnoop Community Team*
