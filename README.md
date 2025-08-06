# 🔍 UX Analyzer - Complete UX Audit Platform

A comprehensive UX analysis platform combining automated auditing, scenario-based testing, and interactive reporting. Analyze websites, mobile apps, and design mockups with AI-powered insights and visual reporting.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18%2B-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Platform Overview

### Complete Analysis Suite
- **🌐 Website Auditing**: Live URL analysis with accessibility, performance, and design evaluation
- **📱 Mobile App Testing**: iOS/Android app analysis with UI/UX scoring
- **🎨 Design Mockup Review**: Visual analysis of prototypes and design files
- **📋 Scenario Testing**: YAML-based user journey validation and testing

### Multi-Interface Access
- **🖥️ Command Line Interface**: Powerful CLI for automated workflows and CI/CD integration
- **🔌 REST API**: FastAPI server for programmatic access and third-party integrations
- **🌐 Web Interface**: Modern React application for intuitive visual analysis

### Advanced Reporting
- **📊 Interactive Dashboards**: Plotly.js charts with score breakdowns and trends
- **📈 Visual Analytics**: Comprehensive UX metrics and accessibility scoring
- **💾 Multiple Formats**: JSON, HTML, and PDF report exports
- **🔄 Real-time Results**: Live analysis progress and instant feedback

## 🚀 Quick Start

### 1. Backend Setup (Python/FastAPI)
```bash
# Clone repository
git clone <repository-url>
cd uiux-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start API server
uvicorn src.main:app --reload --port 8000
```

### 2. Web Interface Setup (React/Vite)
```bash
# Navigate to web interface
cd web-ui

# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

### 3. CLI Usage
```bash
# Basic website analysis
python src/main.py --mode url --input https://example.com

# Scenario-based testing
python src/main.py --mode url-scenario --url https://example.com --scenario ecommerce-checkout

# Mobile app analysis
python src/main.py --mode mock --input /path/to/app --scenario mobile-navigation
```

## 📋 Analysis Capabilities

### Core Analysis Modes

#### 🌐 URL Analysis
```bash
python src/main.py --mode url --input https://example.com --output-format html
```
- **Accessibility Audit**: WCAG compliance and screen reader compatibility
- **Performance Metrics**: Load times, Core Web Vitals, optimization opportunities
- **Design Evaluation**: Visual hierarchy, color contrast, typography assessment
- **Mobile Responsiveness**: Cross-device compatibility and touch interactions

#### 🎨 Screenshot Analysis
```bash
python src/main.py --mode screenshot --input design-mockup.png --modules ui,accessibility
```
- **Visual Design Review**: Layout, typography, color scheme evaluation
- **UI Component Analysis**: Button design, form layouts, navigation patterns
- **Accessibility Check**: Color contrast, text readability, icon clarity
- **Brand Consistency**: Design system adherence and visual coherence

#### 📋 Scenario-Based Testing
```bash
python src/main.py --mode url-scenario --url https://shop.com --scenario ecommerce-checkout
```
- **User Journey Validation**: End-to-end workflow testing
- **Interaction Testing**: Form submissions, navigation flows, error handling
- **Multi-device Testing**: Responsive design across screen sizes
- **Performance Under Load**: User experience during typical usage patterns

### Advanced Features

#### 🧪 Custom Scenarios (YAML)
```yaml
name: "E-commerce Checkout Flow"
description: "Complete purchase workflow validation"
steps:
  - action: "navigate"
    target: "/products"
    validate: "Product listing displays correctly"
  - action: "click"
    target: ".add-to-cart"
    validate: "Item added to cart successfully"
  - action: "navigate"
    target: "/checkout"
    validate: "Checkout process initiates"
```

#### 📊 Module System
- **UI Analysis**: Layout, typography, color, spacing evaluation
- **Accessibility**: WCAG compliance, keyboard navigation, screen reader support
- **Performance**: Load times, resource optimization, Core Web Vitals
- **Security**: HTTPS usage, secure forms, data protection measures
- **SEO**: Meta tags, structured data, search engine optimization

## 🎯 Use Cases

### 👨‍💻 Developers
- **Pre-deployment Testing**: Catch UX issues before production
- **CI/CD Integration**: Automated UX testing in build pipelines
- **Performance Monitoring**: Regular audits and optimization tracking
- **Accessibility Compliance**: WCAG validation and remediation guidance

### 🎨 Designers
- **Design Validation**: Mockup analysis and accessibility review
- **Prototype Testing**: Early-stage UX evaluation and feedback
- **Design System Audits**: Consistency and pattern validation
- **Cross-platform Analysis**: Multi-device design verification

### 📊 Product Managers
- **Competitive Analysis**: Benchmark against industry standards
- **User Experience Metrics**: Quantifiable UX scoring and trends
- **Feature Impact Assessment**: Pre/post-launch UX comparison
- **Stakeholder Reporting**: Visual dashboards and executive summaries

### 🔍 QA Engineers
- **Automated UX Testing**: Comprehensive quality assurance workflows
- **Regression Testing**: Continuous UX monitoring and validation
- **Cross-browser Testing**: Multi-platform compatibility verification
- **Performance Regression**: UX impact of code changes

## 🗂️ Project Structure

```
uiux-analyzer/
├── 📁 src/                          # Core Python application
│   ├── 📄 main.py                   # CLI entry point and FastAPI server
│   ├── 📁 analyzers/                # Analysis engine modules
│   │   ├── 📄 ui_analyzer.py        # UI/Visual analysis
│   │   ├── 📄 accessibility_analyzer.py # A11y compliance
│   │   ├── 📄 performance_analyzer.py   # Performance metrics
│   │   └── 📄 security_analyzer.py      # Security assessment
│   ├── 📁 scenarios/                # YAML scenario engine
│   │   ├── 📄 scenario_manager.py   # Scenario loading and execution
│   │   └── 📄 yaml_scenarios/       # Predefined test scenarios
│   ├── 📁 utils/                    # Utility functions
│   │   ├── 📄 screenshot.py         # Screenshot capture utilities
│   │   ├── 📄 report_generator.py   # Multi-format report generation
│   │   └── 📄 file_utils.py         # File handling and validation
│   └── 📁 api/                      # FastAPI routes and models
│       ├── 📄 routes.py             # API endpoint definitions
│       └── 📄 models.py             # Request/response models
├── 📁 web-ui/                       # React web interface
│   ├── 📁 src/                      # React application source
│   │   ├── 📁 components/           # Reusable UI components
│   │   ├── 📁 pages/                # Application pages/routes
│   │   └── 📄 App.tsx               # Main application component
│   ├── 📄 package.json              # Node.js dependencies
│   └── 📄 vite.config.ts            # Vite build configuration
├── 📁 scenarios/                    # YAML test scenarios
│   ├── 📄 ecommerce-checkout.yaml   # E-commerce workflow
│   ├── 📄 mobile-navigation.yaml    # Mobile app navigation
│   └── 📄 accessibility-audit.yaml  # Accessibility testing
├── 📁 docs/                         # Documentation and guides
│   ├── 📄 API.md                    # API documentation
│   ├── 📄 SCENARIOS.md              # Scenario creation guide
│   ├── 📄 DEPLOYMENT.md             # Deployment instructions
│   ├── 📄 demo.sh                   # Comprehensive demo script
│   └── 📄 STEP_9_WEB_FRONTEND.md    # Web interface documentation
├── 📁 tests/                        # Test suite
│   ├── 📁 unit/                     # Unit tests
│   ├── 📁 integration/              # Integration tests
│   └── 📁 golden_files/             # Reference test outputs
├── 📄 requirements.txt              # Python dependencies
├── 📄 docker-compose.yml            # Multi-service deployment
└── 📄 README.md                     # This file
```

## 🔧 Configuration

### Environment Variables
```bash
# .env
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
ENABLE_CORS=true
SCENARIO_DIR=./scenarios
OUTPUT_DIR=./outputs
LOG_LEVEL=INFO
```

### Configuration Files
```yaml
# config/default.yaml
analysis:
  timeout: 30
  modules:
    - ui
    - accessibility
    - performance
    - security
  output_formats:
    - json
    - html
    - pdf
```

## 📊 Sample Outputs

### CLI Analysis Result
```json
{
  "analysis_id": "analysis_20241201_143022",
  "timestamp": "2024-12-01T14:30:22Z",
  "input": {
    "mode": "url",
    "target": "https://example.com",
    "scenario": null
  },
  "results": {
    "overall_score": 85,
    "module_scores": {
      "ui": 88,
      "accessibility": 82,
      "performance": 87,
      "security": 83
    },
    "findings": [
      {
        "category": "accessibility",
        "severity": "medium",
        "message": "Missing alt text for 3 images",
        "recommendation": "Add descriptive alt attributes"
      }
    ]
  },
  "metadata": {
    "execution_time": 12.4,
    "modules_used": ["ui", "accessibility", "performance", "security"],
    "scenario_steps": null
  }
}
```

### Web Interface Dashboard
- **📈 Score Overview**: Visual gauge charts for each analysis module
- **🔍 Detailed Findings**: Expandable cards with recommendations
- **📊 Historical Trends**: Performance over time with comparative analysis
- **💾 Export Options**: JSON, HTML, and PDF report downloads

## 🧪 Testing

### Running Tests
```bash
# Unit tests
python -m pytest tests/unit/ -v

# Integration tests  
python -m pytest tests/integration/ -v

# Golden file validation
python -m pytest tests/golden_files/ -v

# All tests with coverage
python -m pytest --cov=src --cov-report=html
```

### Test Scenarios
- **URL Analysis**: Live website auditing with known results
- **Screenshot Processing**: Image analysis with expected outputs
- **Scenario Execution**: YAML workflow validation
- **API Integration**: FastAPI endpoint testing
- **Web Interface**: React component and integration testing

## 🚀 Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up --build

# Backend only
docker-compose up backend

# Frontend only  
docker-compose up frontend
```

### Production Setup
```bash
# Backend production server
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend production build
cd web-ui && npm run build && npm run preview
```

### Cloud Deployment
- **AWS**: ECS/Fargate containers with Application Load Balancer
- **Google Cloud**: Cloud Run with Cloud Build for CI/CD
- **Azure**: Container Instances with Front Door for global distribution
- **Kubernetes**: Helm charts for scalable orchestration

## 📈 Performance & Scaling

### Optimization Features
- **Caching**: Redis-based result caching for faster repeated analysis
- **Async Processing**: Celery task queue for long-running analysis
- **CDN Integration**: Static asset delivery optimization
- **Database Optimization**: PostgreSQL with indexed queries

### Monitoring & Analytics
- **Application Metrics**: Prometheus and Grafana dashboards
- **Error Tracking**: Sentry integration for error monitoring
- **Performance Monitoring**: New Relic APM integration
- **User Analytics**: Usage patterns and feature adoption tracking

## 🔒 Security

### Security Features
- **Input Validation**: Comprehensive sanitization and validation
- **Rate Limiting**: API endpoint protection against abuse
- **Authentication**: JWT-based user authentication (configurable)
- **HTTPS Enforcement**: TLS encryption for all communications

### Privacy & Compliance
- **Data Protection**: Secure handling of analysis data
- **GDPR Compliance**: Data retention and deletion policies
- **Audit Logging**: Comprehensive activity tracking
- **Access Control**: Role-based permissions (enterprise features)

## 🤝 Contributing

### Development Setup
1. **Fork Repository**: Create your fork on GitHub
2. **Clone Locally**: `git clone <your-fork-url>`
3. **Install Dependencies**: Backend and frontend setup
4. **Run Tests**: Ensure all tests pass
5. **Create Feature Branch**: `git checkout -b feature/your-feature`
6. **Submit Pull Request**: Detailed description and testing evidence

### Code Standards
- **Python**: PEP 8 compliance with Black formatting
- **TypeScript**: Strict typing with ESLint enforcement
- **Testing**: 80%+ code coverage required
- **Documentation**: Comprehensive docstrings and comments

## 📚 Documentation

### Complete Documentation Set
- **[API Documentation](docs/API.md)**: REST API endpoints and models
- **[Scenario Guide](docs/SCENARIOS.md)**: YAML scenario creation and management
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Production deployment instructions
- **[Web Frontend](docs/STEP_9_WEB_FRONTEND.md)**: React application architecture
- **[Demo Script](docs/demo.sh)**: Comprehensive platform demonstration

### Learning Resources
- **Getting Started**: Step-by-step setup and first analysis
- **Advanced Usage**: Custom scenarios and CI/CD integration
- **Best Practices**: Optimization tips and common patterns
- **Troubleshooting**: Common issues and solutions

## 🎯 Roadmap

### Version 2.0 Features
- **🤖 AI-Powered Insights**: Machine learning recommendations
- **🔄 Continuous Monitoring**: Scheduled analysis and alerts
- **👥 Team Collaboration**: Multi-user workspaces and sharing
- **📱 Mobile App**: Native iOS/Android analysis applications

### Enterprise Features
- **🏢 SSO Integration**: Enterprise authentication providers
- **📊 Advanced Analytics**: Custom dashboards and reporting
- **🔌 API Extensions**: Custom analysis modules and plugins
- **☁️ Cloud Platform**: Hosted SaaS solution with enterprise support

---

## 📞 Support

### Community Support
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community Q&A and best practices
- **Documentation**: Comprehensive guides and API reference
- **Demo**: Live demonstration at [demo.ux-analyzer.com](https://demo.ux-analyzer.com)

### Professional Support
- **Enterprise Licenses**: Commercial support and SLA
- **Custom Development**: Tailored features and integrations
- **Training**: Team onboarding and advanced usage
- **Consulting**: UX optimization strategies and implementation

---

**Ready to revolutionize your UX analysis workflow?** 🚀

Start with our [Quick Start Guide](#-quick-start) or try the [Live Demo](docs/demo.sh)!
