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
  Eye,
  Keyboard,
  Zap,
  Brain,
  ShieldCheck,
  PlayCircle,
  Loader2,
  Settings,
  ExternalLink
} from 'lucide-react';
import { useReports, useFixManager } from '../hooks/useAPI';
import { AnalysisReport, UXIssue } from '../services/api';

// Interface for module findings from real backend data
interface ModuleFinding {
  type: string;
  message: string;
  severity: string;
  element?: string;
  recommendation: string;
  fixed?: boolean;
  fix_timestamp?: string;
}

// Interface for scenario step data
interface ScenarioStep {
  action: string;
  status: string;
  duration_ms: number;
  screenshot?: string;
  selector?: string;
  url?: string;
  errors?: string[];
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

// Fix Now Button Component for Legacy Issues
interface FixNowButtonProps {
  issue: UXIssue;
  reportId: string;
  onFixApplied: () => void;
}

function FixNowButton({ issue, reportId, onFixApplied }: FixNowButtonProps) {
  const { applyFix, isFixing, getFixResult } = useFixManager();
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleFix = async () => {
    try {
      await applyFix(issue.issue_id, reportId, issue.type);
      onFixApplied();
      setShowSuggestions(true);
    } catch (error) {
      console.error('Fix failed:', error);
    }
  };

  const fixResult = getFixResult(issue.issue_id);
  const fixing = isFixing(issue.issue_id);

  return (
    <div className="mt-2">
      <button
        onClick={handleFix}
        disabled={fixing || issue.fix_applied}
        className={`inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
          issue.fix_applied
            ? 'bg-green-100 text-green-800 cursor-not-allowed'
            : fixing
            ? 'bg-gray-100 text-gray-600 cursor-not-allowed'
            : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
        }`}
      >
        {fixing ? (
          <>
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            Fixing...
          </>
        ) : issue.fix_applied ? (
          <>
            <CheckCircle className="w-3 h-3 mr-1" />
            Fix Applied
          </>
        ) : (
          <>
            <Settings className="w-3 h-3 mr-1" />
            Fix Now
          </>
        )}
      </button>

      {/* Show fix suggestions after applying */}
      {showSuggestions && fixResult && (
        <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-md">
          <h5 className="font-medium text-green-800 mb-2">Fix Suggestions Applied:</h5>
          <ul className="text-sm text-green-700 space-y-1">
            {fixResult.fix_suggestions.map((suggestion: string, index: number) => (
              <li key={index} className="flex items-start">
                <span className="mr-2">•</span>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// Fix Now Button Component for Module Findings (New Backend Format)
interface ModuleFixNowButtonProps {
  finding: ModuleFinding;
  moduleKey: string;
  findingIndex: number;
  reportId: string;
  onFixApplied: () => void;
}

function ModuleFixNowButton({ moduleKey, findingIndex, reportId, onFixApplied }: ModuleFixNowButtonProps) {
  const { applyFix, isFixing, getFixResult } = useFixManager();
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Generate unique issue ID from module and finding index
  const issueId = `${moduleKey}-${findingIndex}`;

  const handleFix = async () => {
    try {
      // Use real backend API with constructed issue ID
      await applyFix(issueId, reportId, moduleKey);
      onFixApplied();
      setShowSuggestions(true);
    } catch (error) {
      console.error('Fix failed:', error);
    }
  };

  const fixResult = getFixResult(issueId);
  const fixing = isFixing(issueId);

  return (
    <div className="mt-2">
      <button
        onClick={handleFix}
        disabled={fixing}
        className={`inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
          fixing
            ? 'bg-gray-100 text-gray-600 cursor-not-allowed'
            : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
        }`}
      >
        {fixing ? (
          <>
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            Fixing...
          </>
        ) : (
          <>
            <Settings className="w-3 h-3 mr-1" />
            Fix Now
          </>
        )}
      </button>

      {/* Show fix suggestions after applying */}
      {showSuggestions && fixResult && (
        <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-md">
          <h5 className="font-medium text-green-800 mb-2">Fix Suggestions Applied:</h5>
          <ul className="text-sm text-green-700 space-y-1">
            {fixResult.fix_suggestions.map((suggestion: string, index: number) => (
              <li key={index} className="flex items-start">
                <span className="mr-2">•</span>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export function ReportPage() {
  const { reportId } = useParams<{ reportId: string }>();
  const { fetchReport, downloadReport, loading, error } = useReports();
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [hideFixed, setHideFixed] = useState(false);

  useEffect(() => {
    if (reportId) {
      loadReport(reportId);
    }
  }, [reportId]);

  const loadReport = async (id: string) => {
    try {
      const reportData = await fetchReport(id);
      setReport(reportData);
      
      // Determine active tab based on available data
      if (reportData.module_results && Object.keys(reportData.module_results).length > 0) {
        // Use first module from backend data
        const moduleKeys = Object.keys(reportData.module_results);
        setActiveTab(moduleKeys[0]);
      } else if (reportData.ux_issues && reportData.ux_issues.length > 0) {
        // Fallback to legacy format
        const issueTypes = [...new Set(reportData.ux_issues.map(issue => issue.type))];
        setActiveTab(issueTypes[0] || 'overview');
      } else {
        setActiveTab('overview');
      }
    } catch (err) {
      console.error('Failed to load report:', err);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const handleDownload = async () => {
    if (!reportId) return;
    try {
      await downloadReport(reportId);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const shareReport = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    alert('Report URL copied to clipboard!');
  };

  const onFixApplied = () => {
    // Refresh the report to show updated fix status
    if (reportId) {
      loadReport(reportId);
    }
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

  // Group issues by type for tab navigation - handle both legacy and new format
  const issuesByType = report.ux_issues?.reduce((acc, issue) => {
    if (!acc[issue.type]) acc[issue.type] = [];
    acc[issue.type].push(issue);
    return acc;
  }, {} as Record<string, UXIssue[]>) || {};

  // Extract data from new backend format
  const moduleResults = report.module_results || {};
  const scenarioResults = report.scenario_results || [];
  
  // Calculate metrics from available data
  const totalIssues = report.total_issues || 
    report.ux_issues?.length || 
    Object.values(moduleResults).reduce((sum, module) => sum + (module.findings?.length || 0), 0);
    
  const criticalIssues = report.ux_issues?.filter(issue => 
    issue.severity === 'critical' || issue.severity === 'high'
  ).length || 
  Object.values(moduleResults).reduce((sum, module) => 
    sum + (module.findings?.filter(f => f.severity === 'critical' || f.severity === 'high').length || 0), 0
  );

  const overallScore = report.overall_score || 
    (Object.keys(moduleResults).length > 0 
      ? Math.round(Object.values(moduleResults).reduce((sum, m) => sum + m.score, 0) / Object.keys(moduleResults).length)
      : 75);

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
              onClick={() => handleDownload()}
              className="inline-flex items-center px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
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
                className="ml-2 text-blue-600 hover:underline flex items-center"
              >
                {new URL(report.url).hostname}
                <ExternalLink className="w-3 h-3 ml-1" />
              </a>
            </span>
          )}
          <span className="flex items-center">
            <Clock className="w-4 h-4 mr-1" />
            {new Date(report.timestamp).toLocaleString()}
          </span>
          <span className="flex items-center">
            <span className="font-medium">App Type:</span>
            <span className="ml-2 capitalize">{report.app_type}</span>
          </span>
        </div>
      </div>

      {/* Score Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Overall Score</h3>
              <p className="text-sm text-gray-600">Composite UX rating</p>
            </div>
            <div className={`text-3xl font-bold ${getScoreColor(overallScore)}`}>
              {overallScore}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Total Issues</h3>
              <p className="text-sm text-gray-600">UX problems found</p>
            </div>
            <div className="text-3xl font-bold text-blue-600">
              {totalIssues}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Critical Issues</h3>
              <p className="text-sm text-gray-600">High priority problems</p>
            </div>
            <div className="text-3xl font-bold text-red-600">
              {criticalIssues}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Performance</h3>
              <p className="text-sm text-gray-600">Core Web Vitals</p>
            </div>
            <div className={`text-3xl font-bold ${getScoreColor(report.performance_metrics?.load_time ? 100 - (report.performance_metrics.load_time * 10) : 75)}`}>
              {report.performance_metrics?.load_time ? `${report.performance_metrics.load_time}s` : 'Good'}
            </div>
          </div>
        </div>
      </div>

      {/* Issues Analysis */}
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
            {/* Module tabs from backend data */}
            {Object.keys(moduleResults).map((moduleKey) => (
              <button
                key={moduleKey}
                onClick={() => setActiveTab(moduleKey)}
                className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === moduleKey
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {moduleIcons[moduleKey] || <AlertTriangle className="w-5 h-5" />}
                <span className="ml-2 capitalize">{moduleNames[moduleKey] || moduleKey.replace('_', ' ')}</span>
                <span className="ml-2 bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
                  {moduleResults[moduleKey].findings?.length || 0}
                </span>
              </button>
            ))}
            
            {/* Legacy issue type tabs */}
            {Object.keys(issuesByType).map((type) => (
              <button
                key={type}
                onClick={() => setActiveTab(type)}
                className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === type
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {moduleIcons[type] || <AlertTriangle className="w-5 h-5" />}
                <span className="ml-2 capitalize">{type.replace('_', ' ')}</span>
                <span className="ml-2 bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
                  {issuesByType[type].length}
                </span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Toggle for hiding/showing fixed issues in overview */}
              {(Object.values(moduleResults).some(module => 
                module.findings?.some((f: any) => f.fixed)
              ) || report.ux_issues?.some(issue => issue.fix_applied)) && (
                <div className="flex justify-end">
                  <button
                    onClick={() => setHideFixed(!hideFixed)}
                    className="text-sm px-3 py-1.5 rounded bg-gray-200 hover:bg-gray-300 transition-colors"
                  >
                    {hideFixed ? "Show All Issues" : "Hide Fixed Issues"}
                  </button>
                </div>
              )}
              
              {/* Issues Summary Chart */}
              {(Object.keys(moduleResults).length > 0 || Object.keys(issuesByType).length > 0) && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Issues by Category
                  </h3>
                  <Plot
                    data={[
                      {
                        x: Object.keys(moduleResults).length > 0 
                          ? Object.keys(moduleResults).map(key => moduleNames[key] || key.replace('_', ' '))
                          : Object.keys(issuesByType).map(type => type.replace('_', ' ')),
                        y: Object.keys(moduleResults).length > 0
                          ? Object.values(moduleResults).map(module => module.findings?.length || 0)
                          : Object.values(issuesByType).map(issues => issues.length),
                        type: 'bar',
                        marker: {
                          color: Object.keys(moduleResults).length > 0
                            ? Object.values(moduleResults).map(module => {
                                const criticalCount = module.findings?.filter(f => f.severity === 'critical' || f.severity === 'high').length || 0;
                                return criticalCount > 0 ? '#ef4444' : '#3b82f6';
                              })
                            : Object.values(issuesByType).map(issues => {
                                const criticalCount = issues.filter(i => i.severity === 'critical' || i.severity === 'high').length;
                                return criticalCount > 0 ? '#ef4444' : '#3b82f6';
                              })
                        }
                      }
                    ]}
                    layout={{
                      title: { text: 'UX Issues Distribution' },
                      xaxis: { title: { text: 'Issue Category' } },
                      yaxis: { title: { text: 'Number of Issues' } },
                      showlegend: false,
                      height: 300
                    }}
                    config={{ displayModeBar: false }}
                    className="w-full"
                  />
                </div>
              )}

              {/* Scenario Results Overview */}
              {scenarioResults.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Scenario Test Results
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                    {scenarioResults.map((scenario, index) => (
                      <div key={index} className="bg-white border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900 truncate">{scenario.name}</h4>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            scenario.status === 'completed' || scenario.status === 'passed' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {scenario.status}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <div className="flex justify-between">
                            <span>Score:</span>
                            <span className={`font-medium ${getScoreColor(scenario.score)}`}>
                              {scenario.score}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Duration:</span>
                            <span>{scenario.duration_ms}ms</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Steps:</span>
                            <span>{scenario.steps?.length || 0}</span>
                          </div>
                          {/* Show if screenshots are available */}
                          {report.has_screenshots && (
                            <div className="flex justify-between">
                              <span>Screenshots:</span>
                              <span className="text-green-600 text-xs font-medium">✓ Available</span>
                            </div>
                          )}
                        </div>
                        
                        {/* Step Details with Screenshots */}
                        {scenario.steps && scenario.steps.length > 0 && (
                          <div className="mt-3 border-t pt-3">
                            <h5 className="text-sm font-medium text-gray-700 mb-2">Step Details:</h5>
                            <div className="space-y-2 max-h-60 overflow-y-auto">
                              {scenario.steps.map((step: ScenarioStep, stepIndex: number) => (
                                <div key={stepIndex} className="text-xs border rounded p-2 bg-gray-50">
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="font-medium text-gray-700 capitalize">
                                      {step.action.replace('_', ' ')}
                                    </span>
                                    <span className={`px-1.5 py-0.5 rounded text-xs ${
                                      step.status === 'success' ? 'bg-green-100 text-green-700' :
                                      step.status === 'failed' ? 'bg-red-100 text-red-700' :
                                      'bg-yellow-100 text-yellow-700'
                                    }`}>
                                      {step.status}
                                    </span>
                                  </div>
                                  
                                  {step.url && (
                                    <div className="text-gray-600 truncate mb-1">
                                      URL: {step.url}
                                    </div>
                                  )}
                                  
                                  {step.selector && (
                                    <div className="text-gray-600 truncate mb-1">
                                      Selector: {step.selector}
                                    </div>
                                  )}
                                  
                                  <div className="text-gray-500">
                                    Duration: {step.duration_ms}ms
                                  </div>
                                  
                                  {step.errors && step.errors.length > 0 && (
                                    <div className="text-red-600 text-xs mt-1">
                                      Error: {step.errors[0]}
                                    </div>
                                  )}
                                  
                                  {/* 🖼️ Screenshot Display */}
                                  {step.screenshot && (
                                    <div className="mt-2">
                                      <img
                                        src={`http://localhost:8000/reports/${step.screenshot}`}
                                        alt={`Screenshot for ${step.action} step`}
                                        className="w-full border rounded shadow-sm cursor-pointer hover:shadow-md transition-shadow"
                                        onClick={() => window.open(`http://localhost:8000/reports/${step.screenshot}`, '_blank')}
                                        onError={(e) => {
                                          console.error('Failed to load screenshot:', step.screenshot);
                                          (e.target as HTMLImageElement).style.display = 'none';
                                        }}
                                      />
                                      <div className="text-xs text-gray-500 mt-1 text-center">
                                        Click to view full size
                                      </div>
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recent Issues */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Recent Issues Found
                </h3>
                <div className="space-y-3">
                  {/* Show issues from module results if available */}
                  {Object.keys(moduleResults).length > 0 ? (
                    Object.entries(moduleResults).slice(0, 5).flatMap(([moduleKey, module]) => 
                      module.findings?.slice(0, 2).map((finding, index) => {
                        // Filter out fixed issues if toggle is enabled
                        if (hideFixed && (finding as any).fixed) return null;
                        
                        return (
                          <div
                            key={`${moduleKey}-${index}`}
                            className={`p-4 rounded-lg border ${getSeverityColor(finding.severity)} ${
                              (finding as any).fixed ? 'opacity-50 border-gray-300' : ''
                            }`}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center justify-between">
                                  <h4 className="font-medium text-gray-900">
                                    [{moduleNames[moduleKey] || moduleKey}] {finding.type}
                                  </h4>
                                  {(finding as any).fixed && (
                                    <span className="text-green-600 text-sm font-semibold ml-2">✅ Fixed</span>
                                  )}
                                </div>
                                <p className="text-sm text-gray-600 mt-1">{finding.message}</p>
                                {finding.element && (
                                  <p className="text-xs text-gray-500 mt-1">Element: {finding.element}</p>
                                )}
                                {(finding as any).fixed && (finding as any).fix_timestamp && (
                                  <div className="text-xs text-gray-500 mt-1">
                                    Fixed on: {new Date((finding as any).fix_timestamp).toLocaleString()}
                                  </div>
                                )}
                              </div>
                              <div className="ml-4 text-right">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(finding.severity)}`}>
                                  {finding.severity}
                                </span>
                                {!(finding as any).fixed && (
                                  <ModuleFixNowButton 
                                    finding={finding}
                                    moduleKey={moduleKey}
                                    findingIndex={index}
                                    reportId={reportId!}
                                    onFixApplied={onFixApplied}
                                  />
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      }).filter(Boolean) || []
                    )
                  ) : (
                    /* Fallback to legacy format */
                    report.ux_issues?.slice(0, 5).map((issue) => {
                      // Filter out fixed issues if toggle is enabled
                      if (hideFixed && issue.fix_applied) return null;
                      
                      return (
                        <div
                          key={issue.issue_id}
                          className={`p-4 rounded-lg border ${getSeverityColor(issue.severity)} ${
                            issue.fix_applied ? 'opacity-50 border-gray-300' : ''
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center justify-between">
                                <h4 className="font-medium text-gray-900">{issue.title}</h4>
                                {issue.fix_applied && (
                                  <span className="text-green-600 text-sm font-semibold ml-2">✅ Fixed</span>
                                )}
                              </div>
                              <p className="text-sm text-gray-600 mt-1">{issue.description}</p>
                              {issue.location && (
                                <p className="text-xs text-gray-500 mt-1">Location: {issue.location}</p>
                              )}
                              {issue.fix_applied && issue.fix_timestamp && (
                                <div className="text-xs text-gray-500 mt-1">
                                  Fixed on: {new Date(issue.fix_timestamp).toLocaleString()}
                                </div>
                              )}
                            </div>
                            <div className="ml-4 text-right">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(issue.severity)}`}>
                                {issue.severity}
                              </span>
                              {!issue.fix_applied && (
                                <FixNowButton 
                                  issue={issue} 
                                  reportId={reportId!} 
                                  onFixApplied={onFixApplied}
                                />
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    }).filter(Boolean) || []
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Module results view (new backend format) */}
          {activeTab !== 'overview' && moduleResults[activeTab] && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  {moduleNames[activeTab] || activeTab.replace('_', ' ')} Analysis 
                  ({moduleResults[activeTab].findings?.length || 0} findings)
                </h3>
                <div className="text-sm text-gray-600 flex items-center space-x-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    moduleResults[activeTab].score >= 80 ? 'bg-green-100 text-green-800' :
                    moduleResults[activeTab].score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    Score: {moduleResults[activeTab].score}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    moduleResults[activeTab].threshold_met ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {moduleResults[activeTab].threshold_met ? 'Threshold Met' : 'Below Threshold'}
                  </span>
                  {moduleResults[activeTab].analytics_enabled && (
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Analytics Enabled
                    </span>
                  )}
                </div>
              </div>

              {/* Module Findings */}
              <div className="space-y-4">
                {/* Toggle for hiding/showing fixed issues */}
                {moduleResults[activeTab].findings && moduleResults[activeTab].findings.some((f: any) => f.fixed) && (
                  <button
                    onClick={() => setHideFixed(!hideFixed)}
                    className="text-sm px-3 py-1.5 rounded bg-gray-200 hover:bg-gray-300 mb-4 transition-colors"
                  >
                    {hideFixed ? "Show All Issues" : "Hide Fixed Issues"}
                  </button>
                )}
                
                {moduleResults[activeTab].findings?.map((finding, index) => {
                  // Filter out fixed issues if toggle is enabled
                  if (hideFixed && (finding as any).fixed) return null;
                  
                  return (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border ${getSeverityColor(finding.severity)} ${
                        (finding as any).fixed ? 'opacity-50 border-gray-300' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h4 className="font-medium text-gray-900">{finding.type}</h4>
                            {(finding as any).fixed && (
                              <span className="text-green-600 text-sm font-semibold ml-2">✅ Fixed</span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mt-1">{finding.message}</p>
                          {finding.element && (
                            <p className="text-xs text-gray-500 mt-1">
                              <span className="font-medium">Element:</span> {finding.element}
                            </p>
                          )}
                          <div className="mt-2">
                            <p className="text-xs font-medium text-gray-700 mb-1">Recommendation:</p>
                            <p className="text-xs text-gray-600">{finding.recommendation}</p>
                          </div>
                          {/* Show fix timestamp if available */}
                          {(finding as any).fixed && (finding as any).fix_timestamp && (
                            <div className="text-xs text-gray-500 mt-2">
                              Fixed on: {new Date((finding as any).fix_timestamp).toLocaleString()}
                            </div>
                          )}
                        </div>
                        <div className="ml-4 text-right">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(finding.severity)}`}>
                            {finding.severity}
                          </span>
                          {/* Only show Fix Now button if not already fixed */}
                          {!(finding as any).fixed && (
                            <ModuleFixNowButton 
                              finding={finding}
                              moduleKey={activeTab}
                              findingIndex={index}
                              reportId={reportId!}
                              onFixApplied={onFixApplied}
                            />
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Module Recommendations */}
              {moduleResults[activeTab].recommendations && moduleResults[activeTab].recommendations.length > 0 && (
                <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Module Recommendations:</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    {moduleResults[activeTab].recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start">
                        <span className="mr-2">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Legacy issues view */}
          {activeTab !== 'overview' && issuesByType[activeTab] && !moduleResults[activeTab] && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  {activeTab.replace('_', ' ')} Issues ({issuesByType[activeTab].length})
                </h3>
                <div className="text-sm text-gray-600">
                  {issuesByType[activeTab].filter(i => i.severity === 'critical' || i.severity === 'high').length} critical/high priority
                </div>
              </div>

              {/* Toggle for hiding/showing fixed issues */}
              {issuesByType[activeTab].some(issue => issue.fix_applied) && (
                <button
                  onClick={() => setHideFixed(!hideFixed)}
                  className="text-sm px-3 py-1.5 rounded bg-gray-200 hover:bg-gray-300 mb-4 transition-colors"
                >
                  {hideFixed ? "Show All Issues" : "Hide Fixed Issues"}
                </button>
              )}

              <div className="space-y-4">
                {issuesByType[activeTab].map((issue) => {
                  // Filter out fixed issues if toggle is enabled
                  if (hideFixed && issue.fix_applied) return null;
                  
                  return (
                    <div
                      key={issue.issue_id}
                      className={`p-4 rounded-lg border ${getSeverityColor(issue.severity)} ${
                        issue.fix_applied ? 'opacity-50 border-gray-300' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h4 className="font-medium text-gray-900">{issue.title}</h4>
                            {issue.fix_applied && (
                              <span className="text-green-600 text-sm font-semibold ml-2">✅ Fixed</span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mt-1">{issue.description}</p>
                          {issue.location && (
                            <p className="text-xs text-gray-500 mt-1">
                              <span className="font-medium">Location:</span> {issue.location}
                            </p>
                          )}
                          {issue.suggestions && issue.suggestions.length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs font-medium text-gray-700 mb-1">Suggestions:</p>
                              <ul className="text-xs text-gray-600 space-y-1">
                                {issue.suggestions.map((suggestion, idx) => (
                                  <li key={idx} className="flex items-start">
                                    <span className="mr-2">•</span>
                                    {suggestion}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {issue.fix_applied && issue.fix_timestamp && (
                            <div className="text-xs text-gray-500 mt-2">
                              Fixed on: {new Date(issue.fix_timestamp).toLocaleString()}
                            </div>
                          )}
                        </div>
                        <div className="ml-4 text-right">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(issue.severity)}`}>
                            {issue.severity}
                          </span>
                          {!issue.fix_applied && (
                            <FixNowButton 
                              issue={issue} 
                              reportId={reportId!} 
                              onFixApplied={onFixApplied}
                            />
                          )}
                        </div>
                      </div>
                    </div>
                  );
                }).filter(Boolean)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
