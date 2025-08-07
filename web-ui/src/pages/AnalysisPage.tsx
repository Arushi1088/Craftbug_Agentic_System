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
  Zap,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { useAnalysis, useConnectionStatus } from '../hooks/useAPI';
import apiClient from '../services/api';

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

interface AnalysisModule {
  key: string;
  name: string;
  description: string;
  enabled: boolean;
}

export function AnalysisPage() {
  const navigate = useNavigate();
  const { 
    isAnalyzing, 
    currentAnalysis, 
    error, 
    progress,
    startUrlAnalysis, 
    startScreenshotAnalysis, 
    startScenarioAnalysis,
    resetAnalysis 
  } = useAnalysis();
  const { isConnected } = useConnectionStatus();
  
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [modules, setModules] = useState<AnalysisModule[]>([]);
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

  // Load available scenarios and modules on component mount
  useEffect(() => {
    const defaultScenarios = [
      { name: 'Basic Navigation', filename: 'basic_navigation.yaml', path: 'scenarios/basic_navigation.yaml', description: 'Test basic page navigation and menu interactions' },
      { name: 'Login Flow', filename: 'login_flow.yaml', path: 'scenarios/login_flow.yaml', description: 'Test user authentication and login process' },
      { name: 'Office Tests', filename: 'office_tests.yaml', path: 'scenarios/office_tests.yaml', description: 'Comprehensive Office application testing scenarios' }
    ];

    const defaultModules = [
      { key: 'performance', name: 'Performance Analysis', description: 'Core Web Vitals and loading metrics', enabled: true },
      { key: 'accessibility', name: 'Accessibility Audit', description: 'WCAG 2.1 compliance testing', enabled: true },
      { key: 'keyboard', name: 'Keyboard Navigation', description: 'Keyboard accessibility evaluation', enabled: true },
      { key: 'ux_heuristics', name: 'UX Heuristics', description: 'Nielsen\'s usability principles', enabled: true },
      { key: 'best_practices', name: 'Best Practices', description: 'Modern web development standards', enabled: true },
      { key: 'health_alerts', name: 'Health Alerts', description: 'Critical issues detection', enabled: true },
      { key: 'functional', name: 'Functional Testing', description: 'User journey validation', enabled: false }
    ];

    const loadScenariosAndModules = async () => {
      try {
        // Load scenarios
        const scenarioList = await apiClient.getScenarios();
        setScenarios(scenarioList.map((scenario) => ({
          name: scenario.name || scenario.filename.replace(/\.yaml$/, '').replace(/_/g, ' '),
          filename: scenario.filename,
          path: scenario.path,
          description: scenario.description || `Test scenario: ${scenario.name || scenario.filename.replace(/\.yaml$/, '').replace(/_/g, ' ')}`
        })));

        // Load modules
        const moduleList = await apiClient.getModules();
        setModules(moduleList);
        
        // Initialize config with default module states
        const initialModuleConfig = moduleList.reduce((acc, module) => ({
          ...acc,
          [`enable${module.key.charAt(0).toUpperCase() + module.key.slice(1).replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())}`]: module.enabled
        }), {});
        
        setConfig(prev => ({ ...prev, ...initialModuleConfig }));

      } catch (error) {
        console.error('Failed to load scenarios and modules, using defaults:', error);
        setScenarios(defaultScenarios);
        setModules(defaultModules);
      }
    };

    loadScenariosAndModules();
  }, []);

  // Handle analysis completion
  useEffect(() => {
    if (currentAnalysis && currentAnalysis.status === 'completed') {
      // Navigate to results page after a short delay
      setTimeout(() => {
        navigate(`/report/${currentAnalysis.analysis_id}`);
      }, 2000);
    }
  }, [currentAnalysis, navigate]);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      resetAnalysis();
      
      if (config.mode === 'url' && config.url) {
        await startUrlAnalysis(config.url, config.scenarioFile);
      } else if (config.mode === 'screenshot' && config.screenshot) {
        const screenshotConfig = {
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
        await startScreenshotAnalysis(config.screenshot, screenshotConfig);
      } else if (config.mode === 'url-scenario' && config.url && config.scenarioFile) {
        // Create scenario file from selected path
        const scenarioBlob = new Blob([`# Auto-generated scenario for ${config.url}`], { type: 'text/yaml' });
        const scenarioFile = new File([scenarioBlob], 'auto-scenario.yaml', { type: 'text/yaml' });
        await startScenarioAnalysis(scenarioFile, config.url);
      } else if (config.mode === 'mock-scenario' && config.mockAppPath && config.scenarioFile) {
        // For mock scenarios, create a simple scenario file
        const scenarioBlob = new Blob([`# Mock app scenario for ${config.mockAppPath}`], { type: 'text/yaml' });
        const scenarioFile = new File([scenarioBlob], 'mock-scenario.yaml', { type: 'text/yaml' });
        await startScenarioAnalysis(scenarioFile, config.mockAppPath);
      } else {
        throw new Error('Please fill in all required fields');
      }
    } catch (error) {
      console.error('Analysis error:', error);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setConfig(prev => ({ ...prev, screenshot: file }));
    }
  };

  // Connection status indicator
  const ConnectionStatus = () => (
    <div className={`flex items-center space-x-2 text-sm ${
      isConnected ? 'text-green-600' : 'text-red-600'
    }`}>
      {isConnected ? (
        <CheckCircle className="w-4 h-4" />
      ) : (
        <AlertCircle className="w-4 h-4" />
      )}
      <span>{isConnected ? 'Connected to API' : 'API Connection Lost'}</span>
    </div>
  );

  // Progress indicator
  const ProgressIndicator = () => {
    if (!isAnalyzing) return null;
    
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Analysis in Progress</h3>
          <span className="text-blue-600 font-medium">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>
            {currentAnalysis ? currentAnalysis.message : 'Preparing analysis...'}
          </span>
        </div>
        {currentAnalysis?.estimated_duration_minutes && (
          <p className="text-xs text-gray-500 mt-2">
            Estimated time: {currentAnalysis.estimated_duration_minutes} minutes
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Start UX Analysis
        </h1>
        <p className="text-gray-600 mb-4">
          Configure your analysis settings and choose what to evaluate
        </p>
        <ConnectionStatus />
      </div>

      {/* Show progress if analysis is running */}
      <ProgressIndicator />

      {/* Show error if any */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5" />
            <span className="font-medium">Analysis Error:</span>
          </div>
          <p className="mt-2">{error}</p>
        </div>
      )}

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
                  disabled={isAnalyzing}
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
              disabled={isAnalyzing}
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
                disabled={isAnalyzing}
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
                  disabled={isAnalyzing}
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
                    disabled={isAnalyzing}
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
                  disabled={isAnalyzing}
                  title={scenarios.find(s => s.path === config.scenarioFile)?.description || 'Select a scenario to see description'}
                >
                  <option value="">Choose a scenario...</option>
                  {scenarios.map((scenario) => (
                    <option key={scenario.filename} value={scenario.path} title={scenario.description}>
                      {scenario.name} - {scenario.description}
                    </option>
                  ))}
                </select>
                {scenarios.length === 0 && (
                  <p className="text-sm text-gray-500 mt-2 flex items-center">
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Loading scenarios from backend...
                  </p>
                )}
                {scenarios.length > 0 && (
                  <p className="text-sm text-green-600 mt-2 flex items-center">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    {scenarios.length} scenarios loaded from API
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
            {modules.map((module) => {
              const configKey = `enable${module.key.charAt(0).toUpperCase() + module.key.slice(1).replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())}` as keyof AnalysisConfig;
              return (
                <label
                  key={module.key}
                  className="flex items-start space-x-3 cursor-pointer p-3 rounded-lg hover:bg-gray-50"
                >
                  <input
                    type="checkbox"
                    checked={config[configKey] as boolean}
                    onChange={(e) => setConfig(prev => ({ 
                      ...prev, 
                      [configKey]: e.target.checked 
                    }))}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    disabled={isAnalyzing}
                  />
                  <div>
                    <h3 className="font-medium text-gray-900">{module.name}</h3>
                    <p className="text-sm text-gray-600">{module.description}</p>
                  </div>
                </label>
              );
            })}
            {modules.length === 0 && (
              <p className="text-sm text-gray-500 col-span-2 text-center">
                Loading analysis modules...
              </p>
            )}
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
                  disabled={isAnalyzing}
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
            disabled={isAnalyzing || !isConnected}
            className="inline-flex items-center px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isAnalyzing ? (
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
          {!isConnected && (
            <p className="text-sm text-red-600 mt-2">
              Cannot start analysis: API connection lost
            </p>
          )}
        </div>
      </form>
    </div>
  );
}
