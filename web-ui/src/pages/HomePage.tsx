import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Zap, 
  Eye, 
  Keyboard, 
  Brain, 
  ShieldCheck, 
  AlertTriangle, 
  PlayCircle,
  ArrowRight,
  Globe,
  FileText,
  BarChart3,
  Table,
  Database,
  Bot
} from 'lucide-react';

export function HomePage() {
  const features = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Performance Analysis",
      description: "Core Web Vitals and loading performance metrics"
    },
    {
      icon: <Eye className="w-6 h-6" />,
      title: "Accessibility Audit",
      description: "WCAG 2.1 compliance and inclusive design assessment"
    },
    {
      icon: <Keyboard className="w-6 h-6" />,
      title: "Keyboard Navigation",
      description: "Keyboard accessibility and navigation flow analysis"
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: "UX Heuristics",
      description: "Nielsen's 10 usability principles evaluation"
    },
    {
      icon: <ShieldCheck className="w-6 h-6" />,
      title: "Best Practices",
      description: "Modern web development standards and conventions"
    },
    {
      icon: <AlertTriangle className="w-6 h-6" />,
      title: "Health Alerts",
      description: "Critical issues and system health indicators"
    },
    {
      icon: <PlayCircle className="w-6 h-6" />,
      title: "Scenario Testing",
      description: "YAML-based user journey validation and workflow testing"
    },
    {
      icon: <Table className="w-6 h-6" />,
      title: "Excel Web Automation",
      description: "Automated testing and bug detection for Excel Web applications"
    }
  ];

  const analysisTypes = [
    {
      icon: <Globe className="w-8 h-8" />,
      title: "URL Analysis",
      description: "Analyze live websites and web applications with comprehensive UX auditing",
      features: ["Performance metrics", "Accessibility audit", "Best practices check"],
      link: "/analyze"
    },
    {
      icon: <Table className="w-8 h-8" />,
      title: "Excel Web Testing", 
      description: "Automated testing and bug detection for Excel Web with biometric authentication",
      features: ["Document creation", "Data entry workflows", "Save operations"],
      link: "/excel-testing"
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Advanced Reports",
      description: "Visual and JSON reports with interactive charts and detailed insights",
      features: ["Interactive charts", "JSON view", "Downloadable reports"],
      link: "/reports"
    }
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          Enhanced UX Analysis Platform
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Comprehensive platform for analyzing websites, applications, and Excel Web automation 
          with performance monitoring, accessibility auditing, and automated testing capabilities.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/analyze"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Start Analysis
            <ArrowRight className="w-4 h-4 ml-2" />
          </Link>
          <Link
            to="/excel-testing"
            className="inline-flex items-center px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
          >
            Excel Web Testing
            <Table className="w-4 h-4 ml-2" />
          </Link>
          <a
            href="/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
          >
            API Documentation
          </a>
        </div>
      </div>

      {/* Features Grid */}
      <div className="mb-16">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
          Comprehensive Analysis Suite
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow border border-gray-100"
            >
              <div className="flex items-center mb-4">
                <div className="bg-blue-100 text-blue-600 p-2 rounded-lg mr-4">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {feature.title}
                </h3>
              </div>
              <p className="text-gray-600 text-sm">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Analysis Modes */}
      <div className="bg-white rounded-xl shadow-lg p-8 mb-16">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">
          Multiple Analysis Modes
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="bg-green-100 text-green-600 p-2 rounded-lg">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">URL Analysis</h4>
                <p className="text-gray-600 text-sm">
                  Comprehensive analysis of live websites with performance and accessibility auditing.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="bg-purple-100 text-purple-600 p-2 rounded-lg">
                <Eye className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Screenshot Analysis</h4>
                <p className="text-gray-600 text-sm">
                  Visual analysis of design mockups and static images for UX patterns.
                </p>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="bg-orange-100 text-orange-600 p-2 rounded-lg">
                <PlayCircle className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Scenario Testing</h4>
                <p className="text-gray-600 text-sm">
                  Functional testing with user journey validation and interaction scenarios.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="bg-teal-100 text-teal-600 p-2 rounded-lg">
                <Table className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Excel Web Automation</h4>
                <p className="text-gray-600 text-sm">
                  Automated testing and bug detection for Excel Web with biometric authentication.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Types */}
      <div className="mb-16">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
          Powerful Analysis Capabilities
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {analysisTypes.map((type, index) => (
            <div
              key={index}
              className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow border border-gray-100"
            >
              <div className="flex items-center mb-4">
                <div className="bg-blue-100 text-blue-600 p-3 rounded-lg mr-4">
                  {type.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900">
                  {type.title}
                </h3>
              </div>
              <p className="text-gray-600 mb-4">
                {type.description}
              </p>
              <ul className="space-y-2 mb-6">
                {type.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center text-sm text-gray-600">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-2"></div>
                    {feature}
                  </li>
                ))}
              </ul>
              <Link
                to={type.link}
                className="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium"
              >
                Get Started
                <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
          ))}
        </div>
      </div>

      {/* Excel Web Highlight Section */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-8 mb-16 border border-green-200">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 text-green-600 rounded-full mb-4">
            <Table className="w-8 h-8" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Excel Web Automation
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Test Excel Web applications with automated scenarios, biometric authentication, 
            and comprehensive bug detection. Perfect for enterprise Excel workflows.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="text-center">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <Bot className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <h3 className="font-semibold text-gray-900">Automated Testing</h3>
              <p className="text-sm text-gray-600">Run predefined scenarios for document creation and data entry</p>
            </div>
          </div>
          <div className="text-center">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <ShieldCheck className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <h3 className="font-semibold text-gray-900">Biometric Auth</h3>
              <p className="text-sm text-gray-600">Secure authentication with fingerprint and passkey support</p>
            </div>
          </div>
          <div className="text-center">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <Database className="w-8 h-8 text-purple-600 mx-auto mb-2" />
              <h3 className="font-semibold text-gray-900">Bug Detection</h3>
              <p className="text-sm text-gray-600">Identify issues and report to Azure DevOps automatically</p>
            </div>
          </div>
        </div>
        
        <div className="text-center">
          <Link
            to="/excel-testing"
            className="inline-flex items-center px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
          >
            Start Excel Testing
            <ArrowRight className="w-4 h-4 ml-2" />
          </Link>
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Ready to Get Started?
        </h2>
        <p className="text-lg text-gray-600 mb-8">
          Choose your analysis type and start uncovering insights about your applications.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/analyze"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Analyze Website
            <Globe className="w-4 h-4 ml-2" />
          </Link>
          <Link
            to="/excel-testing"
            className="inline-flex items-center px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
          >
            Test Excel Web
            <Table className="w-4 h-4 ml-2" />
          </Link>
          <Link
            to="/reports"
            className="inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
          >
            View Reports
            <BarChart3 className="w-4 h-4 ml-2" />
          </Link>
        </div>
      </div>
    </div>
  );
}
