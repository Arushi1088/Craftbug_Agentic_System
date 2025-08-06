import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Plot from 'react-plotly.js';
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
  Loader2
} from 'lucide-react';

interface ReportData {
  analysis_id: string;
  timestamp: string;
  url?: string;
  mode: string;
  overall_score: number;
  modules: {
    [key: string]: {
      score: number;
      findings: Array<{
        type: 'error' | 'warning' | 'info';
        message: string;
        severity: 'high' | 'medium' | 'low';
      }>;
      recommendations: string[];
      metrics?: { [key: string]: any };
    };
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

export function ReportPage() {
  const { reportId } = useParams<{ reportId: string }>();
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');

  useEffect(() => {
    if (reportId) {
      fetchReport(reportId);
    }
  }, [reportId]);

  const fetchReport = async (id: string) => {
    try {
      const response = await fetch(`/api/reports/${id}`);
      if (response.ok) {
        const data = await response.json();
        setReport(data);
        setActiveTab(Object.keys(data.modules)[0] || 'overview');
      } else {
        setError('Report not found');
      }
    } catch (err) {
      setError('Failed to load report');
    } finally {
      setLoading(false);
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

  const downloadReport = (format: 'html' | 'json' | 'pdf') => {
    if (!reportId) return;
    window.open(`/api/reports/${reportId}/download?format=${format}`, '_blank');
  };

  const shareReport = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    alert('Report URL copied to clipboard!');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading report...</span>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Report Not Found</h2>
        <p className="text-gray-600 mb-6">{error || 'The requested report could not be found.'}</p>
        <Link
          to="/analyze"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Start New Analysis
        </Link>
      </div>
    );
  }

  const moduleEntries = Object.entries(report.modules);

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <Link
            to="/analyze"
            className="inline-flex items-center text-blue-600 hover:text-blue-700"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Start New Analysis
          </Link>
          <div className="flex space-x-2">
            <button
              onClick={() => downloadReport('html')}
              className="inline-flex items-center px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              <Download className="w-4 h-4 mr-2" />
              HTML
            </button>
            <button
              onClick={() => downloadReport('json')}
              className="inline-flex items-center px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              <Download className="w-4 h-4 mr-2" />
              JSON
            </button>
            <button
              onClick={shareReport}
              className="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Share2 className="w-4 h-4 mr-2" />
              Share
            </button>
          </div>
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          UX Analysis Report
        </h1>
        <div className="flex items-center space-x-4 text-gray-600">
          {report.url && (
            <span className="flex items-center">
              <span className="font-medium">URL:</span>
              <a
                href={report.url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-blue-600 hover:underline"
              >
                {report.url}
              </a>
            </span>
          )}
          <span className="flex items-center">
            <Clock className="w-4 h-4 mr-1" />
            {new Date(report.timestamp).toLocaleString()}
          </span>
          <span className="flex items-center">
            <span className="font-medium">Mode:</span>
            <span className="ml-2 capitalize">{report.mode}</span>
          </span>
        </div>
      </div>

      {/* Overall Score */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Overall UX Score
            </h2>
            <p className="text-gray-600">
              Composite score across all analysis modules
            </p>
          </div>
          <div className={`text-right ${getScoreColor(report.overall_score)}`}>
            <div className="text-4xl font-bold">{report.overall_score}</div>
            <div className="text-sm">out of 100</div>
          </div>
        </div>
        
        {/* Score Breakdown */}
        <div className="mt-6">
          <h3 className="font-medium text-gray-900 mb-3">Module Scores</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            {moduleEntries.map(([moduleKey, moduleData]) => (
              <div
                key={moduleKey}
                className={`p-3 rounded-lg ${getScoreBgColor(moduleData.score)}`}
              >
                <div className="flex items-center mb-2">
                  {moduleIcons[moduleKey]}
                  <span className="ml-2 text-sm font-medium text-gray-900">
                    {moduleNames[moduleKey]}
                  </span>
                </div>
                <div className={`text-lg font-bold ${getScoreColor(moduleData.score)}`}>
                  {moduleData.score}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Module Navigation */}
      <div className="bg-white rounded-xl shadow-lg mb-8">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Overview
            </button>
            {moduleEntries.map(([moduleKey]) => (
              <button
                key={moduleKey}
                onClick={() => setActiveTab(moduleKey)}
                className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === moduleKey
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {moduleIcons[moduleKey]}
                <span className="ml-2">{moduleNames[moduleKey]}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Score Chart */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Score Distribution
                </h3>
                <Plot
                  data={[
                    {
                      x: moduleEntries.map(([key]) => moduleNames[key]),
                      y: moduleEntries.map(([, data]) => data.score),
                      type: 'bar',
                      marker: {
                        color: moduleEntries.map(([, data]) => 
                          data.score >= 80 ? '#10b981' : 
                          data.score >= 60 ? '#f59e0b' : '#ef4444'
                        )
                      }
                    }
                  ]}
                  layout={{
                    title: 'Module Scores',
                    xaxis: { title: 'Modules' },
                    yaxis: { title: 'Score', range: [0, 100] },
                    showlegend: false,
                    height: 300
                  }}
                  config={{ displayModeBar: false }}
                  className="w-full"
                />
              </div>

              {/* Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center mb-2">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                    <span className="font-medium text-green-800">Strengths</span>
                  </div>
                  <p className="text-green-700 text-sm">
                    {moduleEntries.filter(([, data]) => data.score >= 80).length} modules performing well
                  </p>
                </div>
                
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <div className="flex items-center mb-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
                    <span className="font-medium text-yellow-800">Areas for Improvement</span>
                  </div>
                  <p className="text-yellow-700 text-sm">
                    {moduleEntries.filter(([, data]) => data.score < 80 && data.score >= 60).length} modules need attention
                  </p>
                </div>
                
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="flex items-center mb-2">
                    <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
                    <span className="font-medium text-red-800">Critical Issues</span>
                  </div>
                  <p className="text-red-700 text-sm">
                    {moduleEntries.filter(([, data]) => data.score < 60).length} modules require immediate attention
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab !== 'overview' && report.modules[activeTab] && (
            <div className="space-y-6">
              {/* Module Score */}
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  {moduleNames[activeTab]} Analysis
                </h3>
                <div className={`text-2xl font-bold ${getScoreColor(report.modules[activeTab].score)}`}>
                  {report.modules[activeTab].score}/100
                </div>
              </div>

              {/* Findings */}
              {report.modules[activeTab].findings.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Findings</h4>
                  <div className="space-y-2">
                    {report.modules[activeTab].findings.map((finding, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg border-l-4 ${
                          finding.type === 'error'
                            ? 'bg-red-50 border-red-500'
                            : finding.type === 'warning'
                            ? 'bg-yellow-50 border-yellow-500'
                            : 'bg-blue-50 border-blue-500'
                        }`}
                      >
                        <div className="flex items-start">
                          <div className={`mt-0.5 mr-3 ${
                            finding.type === 'error'
                              ? 'text-red-600'
                              : finding.type === 'warning'
                              ? 'text-yellow-600'
                              : 'text-blue-600'
                          }`}>
                            <AlertTriangle className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="text-gray-900">{finding.message}</p>
                            <span className={`text-xs font-medium px-2 py-1 rounded mt-1 inline-block ${
                              finding.severity === 'high'
                                ? 'bg-red-100 text-red-800'
                                : finding.severity === 'medium'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-blue-100 text-blue-800'
                            }`}>
                              {finding.severity} severity
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {report.modules[activeTab].recommendations.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Recommendations</h4>
                  <ul className="space-y-2">
                    {report.modules[activeTab].recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start">
                        <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
                        <span className="text-gray-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Metrics Chart (if available) */}
              {report.modules[activeTab].metrics && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Metrics</h4>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <pre className="text-sm text-gray-700 overflow-x-auto">
                      {JSON.stringify(report.modules[activeTab].metrics, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
