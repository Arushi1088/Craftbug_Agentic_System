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
  BarChart3
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
    }
  ];

  const analysisTypes = [
    {
      icon: <Globe className="w-8 h-8" />,
      title: "URL Analysis",
      description: "Analyze live websites and web applications with comprehensive UX auditing",
      features: ["Performance metrics", "Accessibility audit", "Best practices check"]
    },
    {
      icon: <FileText className="w-8 h-8" />,
      title: "Scenario Testing", 
      description: "Test user journeys with predefined YAML scenarios for consistent evaluation",
      features: ["Office integration tests", "Login workflows", "Navigation scenarios"]
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Advanced Reports",
      description: "Visual and JSON reports with interactive charts and detailed insights",
      features: ["Interactive charts", "JSON view", "Downloadable reports"]
    }
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          Comprehensive UX Analysis Platform
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Analyze websites and applications with our unified platform combining performance 
          monitoring, accessibility auditing, UX heuristics evaluation, and functional testing.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/analyze"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Start Analysis
            <ArrowRight className="w-4 h-4 ml-2" />
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
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
              <p className="text-gray-600">
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
                <Brain className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Mock App Testing</h4>
                <p className="text-gray-600 text-sm">
                  Test prototypes and development builds with comprehensive UX evaluation.
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
              className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow border border-gray-100"
            >
              <div className="text-blue-600 mb-4">
                {type.icon}
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {type.title}
              </h3>
              <p className="text-gray-600 mb-4">
                {type.description}
              </p>
              <ul className="space-y-2">
                {type.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center text-sm text-gray-600">
                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-2"></div>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Call to Action */}
      <div className="text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl text-white p-8">
        <h2 className="text-2xl font-bold mb-4">
          Ready to Improve Your User Experience?
        </h2>
        <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
          Get started with our comprehensive UX analysis platform and discover 
          actionable insights to enhance your website's usability and performance.
        </p>
        <Link
          to="/analyze"
          className="inline-flex items-center px-6 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors"
        >
          Start Your First Analysis
          <ArrowRight className="w-4 h-4 ml-2" />
        </Link>
      </div>
    </div>
  );
}
