import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Plot from 'react-plotly.js';
import ReactJsonView from 'react-json-view';
import { 
  Download, 
  Share2, 
  ArrowLeft,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Eye,
  Keyboard,
  Zap,
  Brain,
  ShieldCheck,
  PlayCircle,
  Loader2,
  FileText,
  Code,
  BarChart3,
  ChevronRight,
  AlertCircle,
  Info
} from 'lucide-react';

interface ReportData {
  analysis_id: string;
  timestamp: string;
  url?: string;
  type?: string;
  mode?: string;
  overall_score: number;
  scenario_results?: Array<{
    name: string;
    score: number;
    status: string;
    duration_ms: number;
    steps: Array<{
      action: string;
      status: string;
      duration_ms: number;
      selector?: string;
    }>;
  }>;
  module_results?: {
    [key: string]: {
      score: number;
      threshold_met: boolean;
      analytics_enabled: boolean;
    };
  };
  modules?: {
    [key: string]: {
      score: number;
      findings: Array<{
        type: 'error' | 'warning' | 'info';
        message: string;
        severity: 'high' | 'medium' | 'low';
        element?: string;
        line?: number;
      }>;
      recommendations: string[];
      metrics?: { [key: string]: any };
    };
  };
  metadata?: {
    [key: string]: any;
  };
}

const moduleIcons: { [key: string]: React.ReactNode } = {
  performance: <Zap className="w-5 h-5" />,
  accessibility: <Eye className="w-5 h-5" />,
  keyboard: <Keyboard className="w-5 h-5" />,
  ux_heuristics: <Brain className="w-5 h-5" />,
  best_practices: <ShieldCheck className="w-5 h-5" />,
  health_alerts: <AlertTriangle className="w-5 h-5" />,
  functional: <PlayCircle className="w-5 h-5" />
};

const moduleNames: { [key: string]: string } = {
  performance: 'Performance',
  accessibility: 'Accessibility',
  keyboard: 'Keyboard Navigation',
  ux_heuristics: 'UX Heuristics',
  best_practices: 'Best Practices',
  health_alerts: 'Health Alerts',
  functional: 'Functional Testing'
};

export function EnhancedReportPage() {
  const { reportId } = useParams<{ reportId: string }>();
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [viewMode, setViewMode] = useState<'visual' | 'json'>('visual');

  useEffect(() => {
    if (reportId) {
      fetchReport(reportId);
    }
  }, [reportId]);

  const fetchReport = async (id: string) => {
    try {
      console.log('Fetching report for ID:', id);
      const response = await fetch(`/api/reports/${id}`);
      console.log('Report response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Report data received:', data);
        setReport(data);
        
        // Set default active tab based on report type
        if (data.scenario_results && data.scenario_results.length > 0) {
          setActiveTab('scenarios');
        } else if (data.modules && Object.keys(data.modules).length > 0) {
          setActiveTab(Object.keys(data.modules)[0]);
        } else {
          setActiveTab('overview');
        }
      } else {
        console.error('Report fetch failed with status:', response.status);
        setError('Report not found');
      }
    } catch (err) {
      console.error('Error fetching report:', err);
      setError('Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async (format: 'json' | 'html') => {
    try {
      const response = await fetch(`/api/reports/${reportId}/download?format=${format}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `report_${reportId}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Download failed');
      }
    } catch (error) {
      console.error('Download error:', error);
      alert('Download failed');
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading report...</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Report Not Found</h2>
          <p className="text-gray-600 mb-4">{error || 'The requested report could not be found.'}</p>
          <Link
            to="/analyze"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Start New Analysis
          </Link>
        </div>
      </div>
    );
  }

  // Prepare chart data for scenario results
  const scenarioChartData = report.scenario_results ? {
    x: report.scenario_results.map(s => s.name),
    y: report.scenario_results.map(s => s.score),
    type: 'bar' as const,
    marker: {
      color: report.scenario_results.map(s => 
        s.score >= 80 ? '#10B981' : s.score >= 60 ? '#F59E0B' : '#EF4444'
      )
    },
    text: report.scenario_results.map(s => `${s.score}/100`),
    textposition: 'auto' as const,
  } : null;

  // Prepare chart data for module results
  const moduleChartData = report.module_results ? {
    labels: Object.keys(report.module_results).map(key => moduleNames[key] || key),
    datasets: [{
      data: Object.values(report.module_results).map(m => m.score),
      backgroundColor: Object.values(report.module_results).map(m => 
        m.score >= 80 ? '#10B981' : m.score >= 60 ? '#F59E0B' : '#EF4444'
      ),
    }]
  } : null;

  const isScenarioReport = report.scenario_results && report.scenario_results.length > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Link
                to="/analyze"
                className="inline-flex items-center text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Analysis
              </Link>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* View Mode Toggle */}
              <div className="flex bg-gray-100 rounded-lg">
                <button
                  onClick={() => setViewMode('visual')}
                  className={`px-3 py-1 rounded-lg text-sm ${
                    viewMode === 'visual' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <BarChart3 className="w-4 h-4 inline mr-1" />
                  Visual
                </button>
                <button
                  onClick={() => setViewMode('json')}
                  className={`px-3 py-1 rounded-lg text-sm ${
                    viewMode === 'json' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Code className="w-4 h-4 inline mr-1" />
                  JSON
                </button>
              </div>

              {/* Download Buttons */}
              <button
                onClick={() => downloadReport('json')}
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 bg-white hover:bg-gray-50"
              >
                <Download className="w-4 h-4 mr-2" />
                JSON
              </button>
              <button
                onClick={() => downloadReport('html')}
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 bg-white hover:bg-gray-50"
              >
                <Download className="w-4 h-4 mr-2" />
                HTML
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* JSON View */}
      {viewMode === 'json' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Raw JSON Data</h2>
            <ReactJsonView
              src={report}
              theme="rjv-default"
              collapsed={2}
              displayDataTypes={false}
              displayObjectSize={false}
              enableClipboard={true}
              style={{ backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px' }}
            />
          </div>
        </div>
      )}

      {/* Visual View */}
      {viewMode === 'visual' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Report Header */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  {isScenarioReport ? 'Scenario Analysis Report' : 'UX Analysis Report'}
                </h1>
                <p className="text-gray-600">Report ID: {report.analysis_id}</p>
                {report.url && (
                  <p className="text-gray-600">URL: {report.url}</p>
                )}
              </div>
              <div className={`text-right ${getScoreColor(report.overall_score)}`}>
                <div className="text-4xl font-bold">{report.overall_score}</div>
                <div className="text-sm">Overall Score</div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className={`p-4 rounded-lg ${getScoreBgColor(report.overall_score)}`}>
                <div className={`text-2xl font-bold ${getScoreColor(report.overall_score)}`}>
                  {report.overall_score}/100
                </div>
                <div className="text-sm text-gray-600">Overall Score</div>
              </div>
              
              {isScenarioReport && (
                <div className="p-4 rounded-lg bg-blue-100">
                  <div className="text-2xl font-bold text-blue-600">
                    {report.scenario_results?.length || 0}
                  </div>
                  <div className="text-sm text-gray-600">Scenarios</div>
                </div>
              )}
              
              <div className="p-4 rounded-lg bg-purple-100">
                <div className="text-2xl font-bold text-purple-600">
                  {Object.keys(report.module_results || report.modules || {}).length}
                </div>
                <div className="text-sm text-gray-600">Modules</div>
              </div>
              
              <div className="p-4 rounded-lg bg-gray-100">
                <div className="text-2xl font-bold text-gray-600">
                  {new Date(report.timestamp).toLocaleDateString()}
                </div>
                <div className="text-sm text-gray-600">Generated</div>
              </div>
            </div>
          </div>

          {/* Scenario Results (for scenario reports) */}
          {isScenarioReport && scenarioChartData && (
            <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
              <h2 className="text-xl font-semibold mb-4">Scenario Results</h2>
              
              {/* Scenario Chart */}
              <div className="mb-6">
                <Plot
                  data={[scenarioChartData]}
                  layout={{
                    title: { text: 'Scenario Scores' },
                    xaxis: { title: 'Scenarios' },
                    yaxis: { title: 'Score (0-100)', range: [0, 100] },
                    height: 400,
                  }}
                  style={{ width: '100%' }}
                  config={{ responsive: true }}
                />
              </div>

              {/* Scenario Details */}
              <div className="space-y-4">
                {report.scenario_results?.map((scenario, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold">{scenario.name}</h3>
                      <div className="flex items-center space-x-4">
                        <span className={`font-bold ${getScoreColor(scenario.score)}`}>
                          {scenario.score}/100
                        </span>
                        <span className={`px-2 py-1 rounded text-xs ${
                          scenario.status === 'success' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {scenario.status}
                        </span>
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">
                      Duration: {scenario.duration_ms}ms
                    </p>
                    
                    <div className="space-y-2">
                      <h4 className="font-medium">Steps:</h4>
                      {scenario.steps.map((step, stepIndex) => (
                        <div 
                          key={stepIndex} 
                          className={`p-2 rounded text-sm ${
                            step.status === 'success' 
                              ? 'bg-green-50 border-l-4 border-green-400' 
                              : 'bg-red-50 border-l-4 border-red-400'
                          }`}
                        >
                          <div className="font-medium">{step.action}</div>
                          <div className="text-gray-600">
                            {step.duration_ms}ms {step.selector && `| ${step.selector}`}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Module Results */}
          {(report.module_results || report.modules) && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Module Analysis</h2>
              
              {/* Module Chart */}
              {moduleChartData && (
                <div className="mb-6">
                  <Plot
                    data={[{
                      values: Object.values(report.module_results || {}).map(m => m.score),
                      labels: Object.keys(report.module_results || {}).map(key => moduleNames[key] || key),
                      type: 'pie' as const,
                      marker: {
                        colors: Object.values(report.module_results || {}).map(m => 
                          m.score >= 80 ? '#10B981' : m.score >= 60 ? '#F59E0B' : '#EF4444'
                        )
                      }
                    }]}
                    layout={{
                      title: { text: 'Module Scores Distribution' },
                      height: 400,
                    }}
                    style={{ width: '100%' }}
                    config={{ responsive: true }}
                  />
                </div>
              )}

              {/* Module Detailed Analysis */}
              <div className="space-y-6">
                {Object.entries(report.modules || report.module_results || {}).map(([key, results]) => {
                  const moduleData = report.modules?.[key] || results;
                  const isExpanded = activeTab === key || activeTab === 'overview';
                  
                  return (
                    <div key={key} className="border rounded-lg">
                      <button
                        onClick={() => setActiveTab(activeTab === key ? 'overview' : key)}
                        className="w-full px-6 py-4 text-left hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            {moduleIcons[key]}
                            <span className="ml-3 text-lg font-medium">{moduleNames[key] || key}</span>
                            <span className={`ml-4 px-3 py-1 rounded-full text-sm font-medium ${
                              getScoreBgColor(moduleData.score)
                            } ${getScoreColor(moduleData.score)}`}>
                              {moduleData.score}/100
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            {moduleData.findings && moduleData.findings.length > 0 && (
                              <span className="text-sm text-gray-500">
                                {moduleData.findings.length} issue{moduleData.findings.length !== 1 ? 's' : ''}
                              </span>
                            )}
                            <ChevronRight className={`w-5 h-5 transform transition-transform ${
                              isExpanded ? 'rotate-90' : ''
                            }`} />
                          </div>
                        </div>
                      </button>
                      
                      {isExpanded && (
                        <div className="px-6 pb-6 border-t bg-gray-50">
                          {/* Module Score and Status */}
                          <div className="py-4">
                            <div className="flex items-center justify-between mb-4">
                              <h3 className="text-lg font-semibold">Analysis Results</h3>
                              {'threshold_met' in moduleData && (
                                <div className="flex items-center space-x-4">
                                  <span className={`px-2 py-1 rounded text-xs ${
                                    moduleData.threshold_met ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                  }`}>
                                    {moduleData.threshold_met ? 'Threshold Met' : 'Below Threshold'}
                                  </span>
                                  {'analytics_enabled' in moduleData && (
                                    <span className={`px-2 py-1 rounded text-xs ${
                                      moduleData.analytics_enabled ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                                    }`}>
                                      {moduleData.analytics_enabled ? 'Analytics Enabled' : 'Basic Analysis'}
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Findings/Issues */}
                          {moduleData.findings && moduleData.findings.length > 0 && (
                            <div className="mb-6">
                              <h4 className="font-semibold mb-3 flex items-center">
                                <AlertTriangle className="w-4 h-4 mr-2 text-orange-500" />
                                Issues Found ({moduleData.findings.length})
                              </h4>
                              <div className="space-y-3">
                                {moduleData.findings.map((finding: any, index: number) => (
                                  <div 
                                    key={index}
                                    className={`p-4 rounded-lg border-l-4 ${
                                      finding.type === 'error' 
                                        ? 'bg-red-50 border-red-400 text-red-800'
                                        : finding.type === 'warning' 
                                        ? 'bg-yellow-50 border-yellow-400 text-yellow-800'
                                        : 'bg-blue-50 border-blue-400 text-blue-800'
                                    }`}
                                  >
                                    <div className="flex items-start justify-between">
                                      <div className="flex-1">
                                        <div className="flex items-center mb-1">
                                          {finding.type === 'error' && <AlertCircle className="w-4 h-4 mr-2" />}
                                          {finding.type === 'warning' && <AlertTriangle className="w-4 h-4 mr-2" />}
                                          {finding.type === 'info' && <Info className="w-4 h-4 mr-2" />}
                                          <span className="font-medium">{finding.message}</span>
                                        </div>
                                        {finding.element && (
                                          <code className="text-xs bg-white bg-opacity-50 px-2 py-1 rounded">
                                            {finding.element}
                                          </code>
                                        )}
                                        {finding.line && (
                                          <div className="text-xs mt-1 opacity-75">
                                            Line {finding.line}
                                          </div>
                                        )}
                                      </div>
                                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                                        finding.severity === 'high' 
                                          ? 'bg-red-100 border border-red-300 text-red-800'
                                          : finding.severity === 'medium' 
                                          ? 'bg-orange-100 border border-orange-300 text-orange-800'
                                          : 'bg-green-100 border border-green-300 text-green-800'
                                      }`}>
                                        {finding.severity}
                                      </span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Recommendations */}
                          {moduleData.recommendations && moduleData.recommendations.length > 0 && (
                            <div className="mb-6">
                              <h4 className="font-semibold mb-3 flex items-center">
                                <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                                Recommendations ({moduleData.recommendations.length})
                              </h4>
                              <div className="space-y-2">
                                {moduleData.recommendations.map((rec: string, index: number) => (
                                  <div key={index} className="flex items-start p-3 bg-green-50 rounded-lg">
                                    <CheckCircle className="w-4 h-4 mr-3 mt-0.5 text-green-500 flex-shrink-0" />
                                    <span className="text-green-800">{rec}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Metrics */}
                          {moduleData.metrics && (
                            <div>
                              <h4 className="font-semibold mb-3 flex items-center">
                                <BarChart3 className="w-4 h-4 mr-2 text-blue-500" />
                                Performance Metrics
                              </h4>
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {Object.entries(moduleData.metrics).map(([metricKey, metricValue]) => (
                                  <div key={metricKey} className="bg-white p-3 rounded-lg border">
                                    <div className="text-sm font-medium text-gray-600 mb-1">
                                      {metricKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                    </div>
                                    <div className="text-lg font-semibold">
                                      {typeof metricValue === 'object' && metricValue !== null ? (
                                        <div className="text-sm space-y-1">
                                          {Object.entries(metricValue as Record<string, any>).map(([subKey, subValue]) => (
                                            <div key={subKey} className="flex justify-between">
                                              <span className="text-gray-600">{subKey}:</span>
                                              <span>{String(subValue)}</span>
                                            </div>
                                          ))}
                                        </div>
                                      ) : (
                                        String(metricValue)
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Metadata */}
          {report.metadata && Object.keys(report.metadata).length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6 mt-8">
              <h2 className="text-xl font-semibold mb-4">Analysis Metadata</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(report.metadata).map(([key, value]) => (
                  key !== 'analytics_features' && (
                    <div key={key} className="flex justify-between">
                      <span className="font-medium">{key.replace(/_/g, ' ').toUpperCase()}:</span>
                      <span className="text-gray-600">{String(value)}</span>
                    </div>
                  )
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
