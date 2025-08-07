import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Globe, 
  Image, 
  Settings,
  Upload,
  ArrowRight,
  Loader2,
  FileText,
  Zap
} from 'lucide-react';

type AnalysisMode = 'url' | 'screenshot' | 'url-scenario' | 'mock-scenario';

interface AnalysisConfig {
  mode: AnalysisMode;
  url?: string;
  screenshot?: File;
  scenario?: string;
  scenarioFile?: string;
  mockAppPath?: string;
  enablePerformance: boolean;
  enableAccessibility: boolean;
  enableKeyboard: boolean;
  enableUxHeuristics: boolean;
  enableBestPractices: boolean;
  enableHealthAlerts: boolean;
  enableFunctional: boolean;
  outputFormat: 'html' | 'json' | 'text';
}

interface Scenario {
  name: string;
  filename: string;
  path: string;
  description: string;
}

export function AnalysisPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [config, setConfig] = useState<AnalysisConfig>({
    mode: 'url',
    enablePerformance: true,
    enableAccessibility: true,
    enableKeyboard: true,
    enableUxHeuristics: true,
    enableBestPractices: true,
    enableHealthAlerts: true,
    enableFunctional: false,
    outputFormat: 'html'
  });

  // Mock app options
  const mockApps = [
    { id: 'word', name: 'Microsoft Word (Mock)', path: 'mocks/word.html' },
    { id: 'excel', name: 'Microsoft Excel (Mock)', path: 'mocks/excel.html' },
    { id: 'powerpoint', name: 'Microsoft PowerPoint (Mock)', path: 'mocks/powerpoint.html' },
    { id: 'integration', name: 'Integration Hub (Mock)', path: 'mocks/integration.html' }
  ];

  // Load available scenarios on component mount
  useEffect(() => {
    // Load scenarios directly (fallback if API fails)
    const defaultScenarios = [
      { name: 'Basic Navigation', filename: 'basic_navigation.yaml', path: 'scenarios/basic_navigation.yaml', description: 'Test basic page navigation and menu interactions' },
      { name: 'Login Flow', filename: 'login_flow.yaml', path: 'scenarios/login_flow.yaml', description: 'Test user authentication and login process' },
      { name: 'Office Tests', filename: 'office_tests.yaml', path: 'scenarios/office_tests.yaml', description: 'Comprehensive Office application testing scenarios' }
    ];

    const loadScenarios = async () => {
      try {
        const response = await fetch('/api/scenarios');
        if (response.ok) {
          const data = await response.json();
          setScenarios(data.scenarios || defaultScenarios);
        } else {
          // Use default scenarios if API fails
          setScenarios(defaultScenarios);
        }
      } catch (error) {
        console.error('Failed to load scenarios, using defaults:', error);
        setScenarios(defaultScenarios);
      }
    };

    loadScenarios();
  }, []);

  const analysisTypes = [
    {
      id: 'url' as AnalysisMode,
      icon: <Globe className="w-6 h-6" />,
      title: 'URL Analysis',
      description: 'Analyze a live website or web application',
      placeholder: 'https://example.com'
    },
    {
      id: 'screenshot' as AnalysisMode,
      icon: <Image className="w-6 h-6" />,
      title: 'Screenshot Analysis',
      description: 'Upload an image for visual UX analysis',
      placeholder: 'Upload image file...'
    },
    {
      id: 'url-scenario' as AnalysisMode,
      icon: <Zap className="w-6 h-6" />,
      title: 'URL + Scenario Testing',
      description: 'Test live websites with predefined scenarios',
      placeholder: 'https://example.com'
    },
    {
      id: 'mock-scenario' as AnalysisMode,
      icon: <FileText className="w-6 h-6" />,
      title: 'Mock App + Scenario',
      description: 'Test prototypes with predefined user journeys',
      placeholder: '/path/to/mock-app.json'
    }
  ];

  const analysisModules = [
    { key: 'enablePerformance', label: 'Performance Analysis', description: 'Core Web Vitals and loading metrics' },
    { key: 'enableAccessibility', label: 'Accessibility Audit', description: 'WCAG 2.1 compliance testing' },
    { key: 'enableKeyboard', label: 'Keyboard Navigation', description: 'Keyboard accessibility evaluation' },
    { key: 'enableUxHeuristics', label: 'UX Heuristics', description: 'Nielsen\'s usability principles' },
    { key: 'enableBestPractices', label: 'Best Practices', description: 'Modern web development standards' },
    { key: 'enableHealthAlerts', label: 'Health Alerts', description: 'Critical issues detection' },
    { key: 'enableFunctional', label: 'Functional Testing', description: 'User journey validation' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      let endpoint = '/api/analyze';
      let body: any = {
        modules: {
          performance: config.enablePerformance,
          accessibility: config.enableAccessibility,
          keyboard: config.enableKeyboard,
          ux_heuristics: config.enableUxHeuristics,
          best_practices: config.enableBestPractices,
          health_alerts: config.enableHealthAlerts,
          functional: config.enableFunctional
        },
        output_format: config.outputFormat
      };

      if (config.mode === 'url' && config.url) {
        body.url = config.url;
      } else if (config.mode === 'screenshot' && config.screenshot) {
        const formData = new FormData();
        formData.append('screenshot', config.screenshot);
        formData.append('config', JSON.stringify(body));
        endpoint = '/api/analyze/screenshot';
        body = formData; // Use FormData for file upload
      } else if (config.mode === 'url-scenario' && config.url && config.scenarioFile) {
        endpoint = '/api/analyze/url-scenario';
        body.url = config.url;
        body.scenario_path = config.scenarioFile;
      } else if (config.mode === 'mock-scenario' && config.mockAppPath && config.scenarioFile) {
        endpoint = '/api/analyze/mock-scenario';
        body.app_path = config.mockAppPath;
        body.scenario_path = config.scenarioFile;
      } else {
        throw new Error('Please fill in all required fields');
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: config.mode !== 'screenshot' ? {
          'Content-Type': 'application/json',
        } : undefined,
        body: config.mode === 'screenshot' ? body : JSON.stringify(body),
      });

      if (response.ok) {
        const result = await response.json();
        navigate(`/analysis/${result.analysis_id}`);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        const errorMessage = errorData.detail || errorData.error || 'Analysis failed';
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('Analysis error:', error);
      alert(`Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setConfig(prev => ({ ...prev, screenshot: file }));
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Start UX Analysis
        </h1>
        <p className="text-gray-600">
          Configure your analysis settings and choose what to evaluate
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Analysis Type Selection */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Analysis Type
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analysisTypes.map((type) => (
              <label
                key={type.id}
                className={`cursor-pointer border-2 rounded-lg p-4 transition-colors ${
                  config.mode === type.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="mode"
                  value={type.id}
                  checked={config.mode === type.id}
                  onChange={(e) => setConfig(prev => ({ ...prev, mode: e.target.value as AnalysisMode }))}
                  className="sr-only"
                />
                <div className="flex items-start space-x-3">
                  <div className={`p-2 rounded-lg ${
                    config.mode === type.id ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {type.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{type.title}</h3>
                    <p className="text-sm text-gray-600">{type.description}</p>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {analysisTypes.find(t => t.id === config.mode)?.title} Input
          </h2>
          
          {config.mode === 'url' && (
            <input
              type="url"
              value={config.url || ''}
              onChange={(e) => setConfig(prev => ({ ...prev, url: e.target.value }))}
              placeholder="https://example.com"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          )}

          {config.mode === 'screenshot' && (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600 mb-2">Upload an image file for analysis</p>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                required
              />
              {config.screenshot && (
                <p className="text-sm text-green-600 mt-2">
                  Selected: {config.screenshot.name}
                </p>
              )}
            </div>
          )}

          {(config.mode === 'url-scenario' || config.mode === 'mock-scenario') && (
            <div className="space-y-4">
              {config.mode === 'url-scenario' && (
                <input
                  type="url"
                  value={config.url || ''}
                  onChange={(e) => setConfig(prev => ({ ...prev, url: e.target.value }))}
                  placeholder="https://example.com"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              )}
              
              {config.mode === 'mock-scenario' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Mock App
                  </label>
                  <select
                    value={config.mockAppPath || ''}
                    onChange={(e) => setConfig(prev => ({ ...prev, mockAppPath: e.target.value }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Choose a mock app...</option>
                    {mockApps.map((app) => (
                      <option key={app.id} value={app.path}>
                        {app.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Scenario
                </label>
                <select
                  value={config.scenarioFile || ''}
                  onChange={(e) => setConfig(prev => ({ ...prev, scenarioFile: e.target.value }))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Choose a scenario...</option>
                  {scenarios.map((scenario) => (
                    <option key={scenario.filename} value={scenario.path}>
                      {scenario.name} - {scenario.description}
                    </option>
                  ))}
                </select>
                {scenarios.length === 0 && (
                  <p className="text-sm text-gray-500 mt-2">
                    Loading scenarios...
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Analysis Modules */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Analysis Modules
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analysisModules.map((module) => (
              <label
                key={module.key}
                className="flex items-start space-x-3 cursor-pointer p-3 rounded-lg hover:bg-gray-50"
              >
                <input
                  type="checkbox"
                  checked={config[module.key as keyof AnalysisConfig] as boolean}
                  onChange={(e) => setConfig(prev => ({ 
                    ...prev, 
                    [module.key]: e.target.checked 
                  }))}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div>
                  <h3 className="font-medium text-gray-900">{module.label}</h3>
                  <p className="text-sm text-gray-600">{module.description}</p>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Output Format */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Output Format
          </h2>
          <div className="flex space-x-4">
            {['html', 'json', 'text'].map((format) => (
              <label key={format} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="radio"
                  name="outputFormat"
                  value={format}
                  checked={config.outputFormat === format}
                  onChange={(e) => setConfig(prev => ({ 
                    ...prev, 
                    outputFormat: e.target.value as 'html' | 'json' | 'text'
                  }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="text-gray-700 capitalize">{format}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <div className="text-center">
          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Running Analysis...
              </>
            ) : (
              <>
                Start Analysis
                <ArrowRight className="w-5 h-5 ml-2" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
