import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Play, 
  StopCircle, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Download,
  RefreshCw,
  AlertTriangle,
  Shield,
  Bot,
  Database
} from 'lucide-react';

interface ExcelTestResult {
  scenario_name: string;
  success: boolean;
  steps_completed: number;
  total_steps: number;
  execution_time: number;
  screenshots: string[];
  errors: string[];
  performance_metrics: any;
  ux_analysis?: {
    ux_score: number;
    craft_bugs_found: number;
    recommendations: string[];
  };
}

export function ExcelTestingPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [currentTest, setCurrentTest] = useState<ExcelTestResult | null>(null);
  const [testHistory, setTestHistory] = useState<ExcelTestResult[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [progress, setProgress] = useState(0);
  const [selectedScenario, setSelectedScenario] = useState('basic');

  const API_BASE = 'http://localhost:8000';

  const addLog = (message: string, type: 'info' | 'success' | 'error' | 'warning' = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] ${message}`;
    setLogs(prev => [...prev, logEntry]);
  };

  const checkStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/excel-web/status`);
      const result = await response.json();
      
      if (result.available) {
        setIsAuthenticated(true);
        addLog('Excel Web integration is available and ready', 'success');
      } else {
        setIsAuthenticated(false);
        addLog('Excel Web integration is not available', 'error');
      }
    } catch (error) {
      addLog(`Status check error: ${error}`, 'error');
    }
  };

  const authenticate = async () => {
    try {
      setIsRunning(true);
      addLog('Starting Excel Web authentication...', 'info');
      
      const response = await fetch(`${API_BASE}/api/excel-web/authenticate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        setIsAuthenticated(true);
        addLog('Authentication completed successfully', 'success');
      } else {
        addLog(`Authentication failed: ${result.message}`, 'error');
      }
    } catch (error) {
      addLog(`Authentication error: ${error}`, 'error');
    } finally {
      setIsRunning(false);
    }
  };

  const runSelectedScenario = async () => {
    try {
      setIsRunning(true);
      setProgress(0);
      
      if (selectedScenario === 'copilot') {
        addLog('Starting Copilot Chart Generation scenario with AI-specific UX Analysis...', 'info');
        addLog('🤖 This scenario tests AI trust, conversation flow, and chart generation integration', 'info');
      } else {
        addLog('Starting Excel Document Creation scenario with UX Analysis...', 'info');
      }
      
      // Step 1: Execute the scenario with UX analysis
      setProgress(20);
      addLog('Executing scenario with enhanced UX analysis...', 'info');
      
      const response = await fetch(`${API_BASE}/api/excel-web/ux-report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          variant: selectedScenario
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        
        if (result.status === 'success') {
          // Step 2: Automatically navigate to the report URL
          setProgress(80);
          addLog('Generating comprehensive UX analysis report...', 'info');
          
          const reportUrl = `${API_BASE}${result.report_url}`;
          addLog(`📊 Report generated: ${result.report_filename}`, 'success');
          
          if (selectedScenario === 'copilot') {
            addLog('🤖 AI Trust Score: ' + (result.ai_trust_score || 'N/A'), 'info');
            addLog('😤 AI Frustration Score: ' + (result.ai_frustration_score || 'N/A'), 'info');
            addLog('🎯 Copilot Effectiveness: ' + (result.copilot_effectiveness || 'N/A') + '%', 'info');
          }
          
          // Navigate to the report URL
          const newWindow = window.open(reportUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
          
          if (newWindow) {
            addLog('✅ UX Analysis Report opened automatically in new window', 'success');
            addLog('🎨 Report contains enhanced Craft bug analysis and UX recommendations', 'success');
            addLog(`🔗 Report URL: ${reportUrl}`, 'info');
          } else {
            // Fallback: navigate in current window
            window.location.href = reportUrl;
            addLog('✅ Navigating to UX Analysis Report in current window', 'success');
          }
          
          setProgress(100);
          addLog('🎉 Scenario execution and UX analysis completed!', 'success');
          addLog('📊 Report shows enhanced Craft bugs detected during interaction', 'info');
        } else {
          addLog(`❌ Report generation failed: ${result.message || 'Unknown error'}`, 'error');
        }
      } else {
        const errorData = await response.json();
        addLog(`❌ UX Report generation failed: ${errorData.detail || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      addLog(`❌ Scenario error: ${error}`, 'error');
    } finally {
      setIsRunning(false);
    }
  };

  const runDocumentCreationTest = async () => {
    // Legacy function - now handled by runSelectedScenario
    setSelectedScenario('basic');
    await runSelectedScenario();
  };

  const stopTest = () => {
    setIsRunning(false);
    addLog('Test execution stopped by user', 'warning');
  };

  const clearLogs = () => {
    setLogs([]);
    addLog('Logs cleared', 'info');
  };

  const downloadLogs = () => {
    const logText = logs.join('\n');
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `excel-automation-log-${new Date().toISOString().slice(0, 19)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };



  useEffect(() => {
    checkStatus();
    addLog('Excel Web Testing Dashboard loaded', 'info');
  }, []);

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
                <div className="mb-8">
            <div className="flex items-center mb-4">
              <div className="bg-green-100 text-green-600 p-3 rounded-lg mr-4">
                <Table className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Excel Web UX Analysis</h1>
                <p className="text-gray-600">Execute real Excel scenarios and automatically generate UX analysis reports with Craft bug detection</p>
              </div>
            </div>
          </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Testing Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Authentication Status */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Authentication Status</h2>
              <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                isAuthenticated 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {isAuthenticated ? (
                  <>
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Authenticated
                  </>
                ) : (
                  <>
                    <XCircle className="w-4 h-4 mr-1" />
                    Not Authenticated
                  </>
                )}
              </div>
            </div>
            
            <div className="flex gap-4">
              <button
                onClick={authenticate}
                disabled={isRunning}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Shield className="w-4 h-4 mr-2" />
                Authenticate to Excel Web
              </button>
              <button
                onClick={checkStatus}
                className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Check Status
              </button>
            </div>
          </div>

          {/* Test Execution */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Test Execution</h2>
            
            <div className="space-y-4">
              {/* Scenario Selection */}
              <div className="flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700">Select Test Scenario:</label>
                <select 
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  onChange={(e) => setSelectedScenario(e.target.value)}
                  value={selectedScenario}
                >
                  <option value="basic">📄 Document Creation & Save</option>
                  <option value="copilot">🤖 Copilot Chart Generation</option>
                </select>
              </div>
              
              <div className="flex gap-4">
                <button
                  onClick={runSelectedScenario}
                  disabled={!isAuthenticated || isRunning}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Run {selectedScenario === 'copilot' ? 'Copilot' : 'Excel'} Scenario & Generate UX Report
                </button>
                {isRunning && (
                  <button
                    onClick={stopTest}
                    className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    <StopCircle className="w-4 h-4 mr-2" />
                    Stop Test
                  </button>
                )}
              </div>

              {/* Progress Bar */}
              {isRunning && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
              )}
            </div>
          </div>

          {/* Current Test Results */}
          {currentTest && (
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Latest Test Results</h2>
              
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{currentTest.steps_completed}/{currentTest.total_steps}</div>
                  <div className="text-sm text-gray-600">Steps Completed</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{currentTest.execution_time.toFixed(1)}s</div>
                  <div className="text-sm text-gray-600">Execution Time</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{currentTest.screenshots.length}</div>
                  <div className="text-sm text-gray-600">Screenshots</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{currentTest.errors.length}</div>
                  <div className="text-sm text-gray-600">Errors</div>
                </div>
                {currentTest.ux_analysis && (
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">{currentTest.ux_analysis.ux_score}/100</div>
                    <div className="text-sm text-gray-600">UX Score</div>
                  </div>
                )}
              </div>

              <div className="flex items-center mb-4">
                <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  currentTest.success 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {currentTest.success ? (
                    <>
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Test Passed
                    </>
                  ) : (
                    <>
                      <XCircle className="w-4 h-4 mr-1" />
                      Test Failed
                    </>
                  )}
                </div>
              </div>

              {currentTest.errors.length > 0 && (
                <div className="mb-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Errors:</h3>
                  <div className="space-y-1">
                    {currentTest.errors.map((error, index) => (
                      <div key={index} className="text-sm text-red-600 bg-red-50 p-2 rounded">
                        {error}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Execution Logs */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Execution Logs</h2>
              <div className="flex gap-2">
                <button
                  onClick={clearLogs}
                  className="flex items-center px-3 py-1 text-sm border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
                >
                  Clear
                </button>
                <button
                  onClick={downloadLogs}
                  className="flex items-center px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  <Download className="w-4 h-4 mr-1" />
                  Download
                </button>
              </div>
            </div>
            
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-64 overflow-y-auto">
              {logs.length === 0 ? (
                <div className="text-gray-500">No logs yet. Start a test to see execution logs.</div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="mb-1">
                    {log}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Features */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Features</h2>
            
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="bg-green-100 text-green-600 p-2 rounded-lg">
                  <Bot className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Automated Testing</h3>
                  <p className="text-sm text-gray-600">Run predefined scenarios for document creation and data entry</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="bg-blue-100 text-blue-600 p-2 rounded-lg">
                  <Shield className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Biometric Auth</h3>
                  <p className="text-sm text-gray-600">Secure authentication with fingerprint and passkey support</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="bg-purple-100 text-purple-600 p-2 rounded-lg">
                  <Database className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Bug Detection</h3>
                  <p className="text-sm text-gray-600">Identify issues and report to Azure DevOps automatically</p>
                </div>
              </div>
            </div>
          </div>

          {/* Test History */}
          {testHistory.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Test History</h2>
              
              <div className="space-y-3">
                {testHistory.slice(0, 5).map((test, index) => (
                  <div key={index} className="p-3 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-sm">{test.scenario_name}</span>
                      <div className={`flex items-center px-2 py-1 rounded-full text-xs ${
                        test.success 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {test.success ? 'Passed' : 'Failed'}
                      </div>
                    </div>
                    <div className="text-xs text-gray-600">
                      {test.steps_completed}/{test.total_steps} steps • {test.execution_time.toFixed(1)}s
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
