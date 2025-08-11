// Dashboard component with ADO integration and analytics
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Plot from 'react-plotly.js';
import {
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Eye,
  TrendingUp,
  TrendingDown,
  ExternalLink,
  RefreshCw,
  Filter,
  Download,
  Settings
} from 'lucide-react';
import { useDashboard, useReports, useConnectionStatus } from '../hooks/useAPI';

// ADO SDK types (if needed in iframe context)
declare global {
  interface Window {
    AzureDevOpsSDK?: any;
  }
}

// ADO Work Item Card Component
interface WorkItemCardProps {
  workItem: {
    id: string;
    title: string;
    type: string;
    state: string;
    priority: string;
    url: string;
    created_date: string;
    source_issue_id: string;
  };
}

function WorkItemCard({ workItem }: WorkItemCardProps) {
  const getStateColor = (state: string) => {
    switch (state.toLowerCase()) {
      case 'new': return 'bg-blue-100 text-blue-800';
      case 'active': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      case 'closed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case '1': return 'bg-red-100 text-red-800 border-red-200';
      case '2': return 'bg-orange-100 text-orange-800 border-orange-200';
      case '3': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case '4': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h4 className="font-medium text-gray-900 mb-1">{workItem.title}</h4>
          <p className="text-sm text-gray-600">Issue ID: {workItem.source_issue_id}</p>
        </div>
        <a
          href={workItem.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStateColor(workItem.state)}`}>
            {workItem.state}
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded border ${getPriorityColor(workItem.priority)}`}>
            P{workItem.priority}
          </span>
        </div>
        <span className="text-xs text-gray-500">
          {new Date(workItem.created_date).toLocaleDateString()}
        </span>
      </div>
    </div>
  );
}

// Main Dashboard Component
export function DashboardPage() {
  const { 
    analytics, 
    alerts, 
    loading, 
    error, 
    autoRefresh, 
    fetchDashboardData, 
    createADOTickets,
    toggleAutoRefresh 
  } = useDashboard();
  
  const { reports, fetchReports } = useReports();
  const { isConnected } = useConnectionStatus();
  
  // Guarded ADO SDK loading - only load when running inside Azure DevOps iframe
  useEffect(() => {
    const inAdoIframe = window.self !== window.top; // simple heuristic to detect iframe
    if (!inAdoIframe) {
      console.log('Running in standalone mode - Azure DevOps SDK not loaded');
      return;
    }

    (async () => {
      try {
        // Dynamically import only when embedded in ADO iframe
        console.log('Loading Azure DevOps SDK...');
        const SDK = await import('azure-devops-extension-sdk');
        await SDK.init();
        await SDK.ready();
        console.log('Azure DevOps SDK initialized successfully');
        // Store SDK reference globally if needed by other components
        window.AzureDevOpsSDK = SDK;
      } catch (error) {
        console.warn('Failed to initialize Azure DevOps SDK:', error);
        // Don't show error to user as this is expected in standalone mode
      }
    })();
  }, []);
  
  // Helper function to safely create absolute URLs
  const toAbsoluteUrl = (u?: string) => {
    if (!u) return undefined;
    try { 
      return new URL(u, window.location.origin).toString(); 
    } catch (e) {
      console.warn('Bad URL in report:', u, e);
      return undefined;
    }
  };

  // Helper function to safely get hostname from URL
  const getHostname = (url?: string) => {
    const absoluteUrl = toAbsoluteUrl(url);
    if (absoluteUrl) {
      try {
        return new URL(absoluteUrl).hostname;
      } catch {
        return url || 'Unknown';
      }
    }
    return url || 'Unknown';
  };
  
  const [selectedReport, setSelectedReport] = useState<string>('');
  const [creatingTickets, setCreatingTickets] = useState(false);
  const [demoMode, setDemoMode] = useState(true);
  const [activeFilter, setActiveFilter] = useState<'all' | 'critical' | 'recent'>('all');

  // Fetch reports on component mount
  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  // Also refresh reports when component becomes visible again (e.g., user navigates back)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        fetchReports();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', fetchReports);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', fetchReports);
    };
  }, [fetchReports]);

  const handleCreateADOTickets = async () => {
    if (!selectedReport) {
      alert('Please select a report first');
      return;
    }

    try {
      setCreatingTickets(true);
      await createADOTickets();
      alert(`Created work items in ADO ${demoMode ? '(Demo Mode)' : ''}`);
    } catch (error) {
      alert('Failed to create ADO tickets');
    } finally {
      setCreatingTickets(false);
    }
  };

  const filteredReports = reports.filter(report => {
    switch (activeFilter) {
      case 'critical':
        return report.ux_issues?.some(issue => issue.severity === 'critical' || issue.severity === 'high');
      case 'recent':
        const dayAgo = new Date();
        dayAgo.setDate(dayAgo.getDate() - 1);
        return new Date(report.timestamp) > dayAgo;
      default:
        return true;
    }
  });

  // Debug logging
  console.log('📊 Dashboard Debug:', {
    totalReports: reports.length,
    filteredReports: filteredReports.length,
    activeFilter,
    reports: reports.slice(0, 3) // Show first 3 for debugging
  });

  const filteredAlerts = alerts.filter(alert => !alert.acknowledged);

  if (loading && !analytics) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">UX Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Real-time insights and Azure DevOps integration
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-2 text-sm ${
            isConnected ? 'text-green-600' : 'text-red-600'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <button
            onClick={toggleAutoRefresh}
            className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
              autoRefresh 
                ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
          </button>
          <button
            onClick={fetchDashboardData}
            className="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          <button
            onClick={() => {
              fetchReports();
              fetchDashboardData();
            }}
            className="inline-flex items-center px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh All
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5" />
            <span className="font-medium">Dashboard Error:</span>
          </div>
          <p className="mt-2">{error}</p>
        </div>
      )}

      {/* Alerts Section */}
      {filteredAlerts.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-800 mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2" />
            Active Alerts ({filteredAlerts.length})
          </h2>
          <div className="space-y-3">
            {filteredAlerts.slice(0, 3).map((alert) => (
              <div key={alert.alert_id} className="bg-white rounded-lg p-3 border border-red-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">{alert.message}</h4>
                    <p className="text-sm text-gray-600">{alert.type.replace('_', ' ')}</p>
                  </div>
                  <div className="text-right">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      alert.severity === 'high' ? 'bg-red-100 text-red-800' :
                      alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {alert.severity}
                    </span>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stats Overview */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Total Analyses</h3>
                <p className="text-3xl font-bold text-blue-600">{analytics.total_analyses}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-500" />
            </div>
            <p className="text-sm text-gray-600 mt-2">
              +{analytics.recent_analyses?.length || 0} this week
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Total Issues</h3>
                <p className="text-3xl font-bold text-red-600">{analytics.total_issues}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Avg {analytics.avg_issues_per_analysis?.toFixed(1) || '0.0'} per analysis
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Most Common</h3>
                <p className="text-xl font-bold text-yellow-600 capitalize">
                  {analytics.most_common_issue_type?.replace('_', ' ') || 'N/A'}
                </p>
              </div>
              <Eye className="w-8 h-8 text-yellow-500" />
            </div>
            <p className="text-sm text-gray-600 mt-2">Issue category</p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Performance</h3>
                <p className="text-3xl font-bold text-green-600">Good</p>
              </div>
              <Zap className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-sm text-gray-600 mt-2">System health</p>
          </div>
        </div>
      )}

      {/* Charts */}
      {analytics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Issue Severity Distribution */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Issue Severity Distribution</h3>
            <Plot
              data={[
                {
                  values: Object.values(analytics.issue_severity_distribution || {}),
                  labels: Object.keys(analytics.issue_severity_distribution || {}),
                  type: 'pie',
                  marker: {
                    colors: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981']
                  }
                }
              ]}
              layout={{
                height: 300,
                showlegend: true,
                legend: { orientation: 'h', y: -0.1 }
              }}
              config={{ displayModeBar: false }}
              className="w-full"
            />
          </div>

          {/* Issue Type Distribution */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Issue Types</h3>
            <Plot
              data={[
                {
                  x: Object.keys(analytics.issue_type_distribution || {}).map(type => type.replace('_', ' ')),
                  y: Object.values(analytics.issue_type_distribution || {}) as number[],
                  type: 'bar',
                  marker: { color: '#3b82f6' }
                }
              ]}
              layout={{
                height: 300,
                xaxis: { title: { text: 'Issue Type' } },
                yaxis: { title: { text: 'Count' } }
              }}
              config={{ displayModeBar: false }}
              className="w-full"
            />
          </div>
        </div>
      )}

      {/* ADO Integration Section */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Azure DevOps Integration
          </h2>
          <div className="flex items-center space-x-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={demoMode}
                onChange={(e) => setDemoMode(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="text-sm text-gray-700">Demo Mode</span>
            </label>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Report Selection */}
          <div>
            <h3 className="font-medium text-gray-900 mb-3">Create Work Items from Report</h3>
            <div className="space-y-3">
              <select
                value={selectedReport}
                onChange={(e) => setSelectedReport(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select a report...</option>
                {filteredReports.map((report) => (
                  <option key={report.analysis_id} value={report.analysis_id}>
                    {getHostname(report.url)} - {report.total_issues} issues - {new Date(report.timestamp).toLocaleDateString()}
                  </option>
                ))}
              </select>
              
              <button
                onClick={handleCreateADOTickets}
                disabled={!selectedReport || creatingTickets}
                className="w-full inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {creatingTickets ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Creating Work Items...
                  </>
                ) : (
                  'Create ADO Work Items'
                )}
              </button>
            </div>
          </div>

          {/* Recent Work Items (Mock Data) */}
          <div>
            <h3 className="font-medium text-gray-900 mb-3">Recent Work Items</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {/* Mock work items for demo */}
              <WorkItemCard
                workItem={{
                  id: 'WI-001',
                  title: 'Fix accessibility issues on homepage',
                  type: 'Bug',
                  state: 'Active',
                  priority: '2',
                  url: '#',
                  created_date: new Date().toISOString(),
                  source_issue_id: 'UX-001'
                }}
              />
              <WorkItemCard
                workItem={{
                  id: 'WI-002',
                  title: 'Improve button contrast ratio',
                  type: 'Task',
                  state: 'New',
                  priority: '3',
                  url: '#',
                  created_date: new Date().toISOString(),
                  source_issue_id: 'UX-002'
                }}
              />
              <WorkItemCard
                workItem={{
                  id: 'WI-003',
                  title: 'Optimize page load performance',
                  type: 'Bug',
                  state: 'Resolved',
                  priority: '1',
                  url: '#',
                  created_date: new Date().toISOString(),
                  source_issue_id: 'UX-003'
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Reports Filter & List */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            Recent Reports ({filteredReports.length} total)
          </h2>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={activeFilter}
              onChange={(e) => setActiveFilter(e.target.value as 'all' | 'critical' | 'recent')}
              className="border border-gray-300 rounded-lg px-3 py-1 text-sm"
            >
              <option value="all">All Reports</option>
              <option value="critical">Critical Issues</option>
              <option value="recent">Last 24 Hours</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredReports.slice(0, 6).map((report) => (
            <Link
              key={report.analysis_id}
              to={`/reports/${report.analysis_id}`}
              className="block p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900 truncate">
                  {getHostname(report.url)}
                </h4>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  (report.total_issues || 0) > 10 ? 'bg-red-100 text-red-800' :
                  (report.total_issues || 0) > 5 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {report.total_issues} issues
                </span>
              </div>
              <p className="text-sm text-gray-600">
                {new Date(report.timestamp).toLocaleString()}
              </p>
              {report.overall_score && (
                <div className="mt-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">UX Score</span>
                    <span className={`font-medium ${
                      report.overall_score >= 80 ? 'text-green-600' :
                      report.overall_score >= 60 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {report.overall_score}/100
                    </span>
                  </div>
                </div>
              )}
            </Link>
          ))}
        </div>

        {filteredReports.length === 0 && (
          <div className="text-center py-8">
            <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No reports found</h3>
            <p className="text-gray-600 mb-4">
              {activeFilter === 'all' 
                ? 'Start your first analysis to see reports here' 
                : 'No reports match the current filter'}
            </p>
            <Link
              to="/analyze"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Start Analysis
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
