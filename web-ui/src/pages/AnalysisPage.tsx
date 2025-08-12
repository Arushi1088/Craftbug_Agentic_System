import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, Settings, Play } from 'lucide-react';
import { useAnalysis } from '../hooks/useAPI';
import { apiClient } from '../services/api';

type AnalysisConfig = {
  app: string;
  scenarioFile: string;
  mode: 'mock-scenario';
  enablePerformance: boolean;
  enableAccessibility: boolean;
  enableKeyboard: boolean;
  enableUxHeuristics: boolean;
  enableBestPractices: boolean;
  enableHealthAlerts: boolean;
  enableFunctional: boolean;
};

interface ScenarioDTO {
  id: string;
  name: string;
  description?: string;
  app_type: string;
}

export function AnalysisPage() {
  const navigate = useNavigate();
  const { isAnalyzing, currentAnalysis, error, progress, startMockScenario, resetAnalysis } = useAnalysis();
  
  const [selectedApp, setSelectedApp] = useState<string>('');
  const [scenarios, setScenarios] = useState<ScenarioDTO[]>([]);
  const [loading, setLoading] = useState(false);
  
  const [config, setConfig] = useState<AnalysisConfig>({
    app: '',
    scenarioFile: '',
    mode: 'mock-scenario',
    enablePerformance: true,
    enableAccessibility: true,
    enableKeyboard: true,
    enableUxHeuristics: true,
    enableBestPractices: true,
    enableHealthAlerts: true,
    enableFunctional: true,
  });

  const loadScenarios = useCallback(async (appType: string) => {
    if (!appType) return;
    
    setLoading(true);
    try {
      console.log(`🔍 Loading scenarios for app: ${appType}`);
      const data = await apiClient.getScenarios();
      const filtered = data?.filter((s: ScenarioDTO) => s.app_type === appType) || [];
      console.log(`✅ Found ${filtered.length} scenarios for ${appType}:`, filtered);
      setScenarios(filtered);
    } catch (error) {
      console.error('❌ Failed to load scenarios:', error);
      setScenarios([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleAppSelection = (app: string) => {
    console.log(`📱 App selected: ${app}`);
    setSelectedApp(app);
    
    // Update config and reset scenario selection
    setConfig(prev => {
      const next: AnalysisConfig = { ...prev, app: app, scenarioFile: '' };
      console.log('🔧 Updated config:', next);
      return next;
    });
    
    // Load scenarios for the selected app
    loadScenarios(app);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedApp || !config.scenarioFile) {
      console.warn('⚠️ Missing required fields');
      return;
    }

    console.log('🚀 Starting analysis with config:', { selectedApp, config });
    
    try {
      const result = await startMockScenario(selectedApp, config.scenarioFile, config);
      if (result?.analysis_id) {
        console.log('✅ Analysis started, navigating to:', result.analysis_id);
        navigate(`/analysis/${result.analysis_id}`);
      }
    } catch (error) {
      console.error('❌ Analysis failed:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">UX Analysis</h1>
        <p className="text-lg text-gray-600">Configure your analysis settings and choose what to evaluate</p>
        <div className="flex items-center justify-center mt-4 space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-sm text-green-600 font-medium">Connected to API</span>
        </div>
      </div>

      {/* Progress */}
      {isAnalyzing && (
        <div className="bg-white rounded-xl shadow p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="font-semibold">Analysis in Progress</div>
            <div className="text-blue-600">{progress}%</div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
          </div>
          {currentAnalysis?.message && <div className="text-sm text-gray-600 mt-2">{currentAnalysis.message}</div>}
        </div>
      )}

      {/* Errors */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5" />
            <span className="font-medium">Analysis Error:</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Target App Selection */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Select Target Application
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {['word', 'excel', 'powerpoint'].map((app) => (
              <button
                key={app}
                type="button"
                onClick={() => handleAppSelection(app)}
                className={`p-4 border-2 rounded-lg transition-all ${
                  selectedApp === app 
                    ? 'border-blue-500 bg-blue-50 text-blue-700' 
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                }`}
                disabled={isAnalyzing}
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">
                    {app === 'word' ? '📄' : app === 'excel' ? '📊' : '📽️'}
                  </div>
                  <div className="font-medium">
                    {app === 'word' ? 'Word' : app === 'excel' ? 'Excel' : 'PowerPoint'}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {app === 'word' ? 'Microsoft Word' : app === 'excel' ? 'Microsoft Excel' : 'Microsoft PowerPoint'}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Scenario Selection */}
        {selectedApp && (
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-2">
              Select Scenario for {selectedApp === 'word' ? 'Microsoft Word' : selectedApp === 'excel' ? 'Microsoft Excel' : 'Microsoft PowerPoint'}
            </h2>

            <div>
              <label className="block text-sm font-medium mb-1">Scenario</label>
              <select
                className="w-full p-3 border rounded-lg"
                value={config.scenarioFile || ''}
                onChange={(e) => setConfig(p => ({ ...p, scenarioFile: e.target.value }))}
                required
                disabled={isAnalyzing || scenarios.length === 0}
              >
                <option value="">Choose a scenario...</option>
                {scenarios.map(s => (
                  <option key={s.id} value={s.id} title={s.description || ''}>
                    {s.name}
                  </option>
                ))}
              </select>
              {scenarios.length > 0 && (
                <p className="text-sm text-green-600 mt-1">✅ {scenarios.length} {selectedApp} scenarios loaded</p>
              )}
              {scenarios.length === 0 && !loading && selectedApp && (
                <p className="text-sm text-gray-500 mt-1">No scenarios available for {selectedApp}</p>
              )}
            </div>
          </div>
        )}

        {/* Analysis Modules */}
        {selectedApp && config.scenarioFile && (
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Analysis Modules</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { key: 'enablePerformance', label: 'Performance Analysis', desc: 'Core Web Vitals and loading metrics' },
                { key: 'enableAccessibility', label: 'Accessibility Audit', desc: 'WCAG 2.1 compliance testing' },
                { key: 'enableKeyboard', label: 'Keyboard Navigation', desc: 'Keyboard accessibility testing' },
                { key: 'enableUxHeuristics', label: 'UX Heuristics', desc: 'Nielsen\'s usability principles' },
                { key: 'enableBestPractices', label: 'Best Practices', desc: 'Industry standard compliance' },
                { key: 'enableHealthAlerts', label: 'Health Alerts', desc: 'Critical issue detection' },
                { key: 'enableFunctional', label: 'Functional Testing', desc: 'Feature workflow validation' },
              ].map(module => (
                <label key={module.key} className="flex items-start space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={config[module.key as keyof AnalysisConfig] as boolean}
                    onChange={(e) => setConfig(p => ({ ...p, [module.key]: e.target.checked }))}
                    className="mt-1"
                    disabled={isAnalyzing}
                  />
                  <div>
                    <div className="font-medium">{module.label}</div>
                    <div className="text-sm text-gray-600">{module.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Submit Button */}
        {selectedApp && config.scenarioFile && (
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={isAnalyzing || !selectedApp || !config.scenarioFile}
              className="inline-flex items-center px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="w-5 h-5 mr-2" />
              {isAnalyzing ? 'Running Analysis...' : 'Start Analysis'}
            </button>
          </div>
        )}
      </form>
    </div>
  );
}
