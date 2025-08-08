import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Filter,
  ExternalLink,
  RefreshCw,
  Eye,
  TrendingUp
} from 'lucide-react';
import { useReportsSummary, useConnectionStatus } from '../hooks/useAPI';

// Color scheme for charts
const COLORS = {
  primary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#6366f1',
  gray: '#6b7280'
};

const CHART_COLORS = [COLORS.primary, COLORS.success, COLORS.warning, COLORS.danger, COLORS.info];

// Utility function for safe numeric operations in charts
const safeNum = (value: any): number => {
  const num = typeof value === 'number' ? value : parseFloat(value) || 0;
  return isNaN(num) || !isFinite(num) ? 0 : num;
};

// Check if data is valid for chart rendering
const hasValidData = (data: any[]): boolean => {
  return Array.isArray(data) && data.length > 0 && data.some(item => 
    item && typeof item === 'object' && Object.keys(item).length > 0
  );
};

// Issue Status Component with ADO integration
interface IssueStatusProps {
  issue: {
    issue_id: string;
    title: string;
    severity: string;
    ado_work_item_id?: string;
    ado_status?: string;
    ado_url?: string;
    fixed?: boolean;
    fix_timestamp?: string;
  };
}

function IssueStatus({ issue }: IssueStatusProps) {
  const getStatusColor = (status?: string) => {
    switch (status?.toLowerCase()) {
      case 'new': return 'bg-blue-100 text-blue-800';
      case 'active': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      case 'closed': return 'bg-gray-100 text-gray-800';
      default: return issue.fixed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex-1">
        <h4 className="font-medium text-gray-900 mb-1">{issue.title}</h4>
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 text-xs font-medium rounded border ${getSeverityColor(issue.severity)}`}>
            {issue.severity}
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(issue.ado_status)}`}>
            {issue.ado_status || (issue.fixed ? 'Fixed' : 'Open')}
          </span>
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        {issue.ado_work_item_id && issue.ado_url && (
          <a
            href={issue.ado_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 flex items-center text-sm"
          >
            ADO #{issue.ado_work_item_id}
            <ExternalLink className="w-3 h-3 ml-1" />
          </a>
        )}
        {issue.fix_timestamp && (
          <span className="text-xs text-gray-500">
            Fixed {new Date(issue.fix_timestamp).toLocaleDateString()}
          </span>
        )}
      </div>
    </div>
  );
}

// Fix Timeline Component
interface TimelineEntry {
  timestamp: string;
  action: string;
  details: string;
  user?: string;
}

interface FixTimelineProps {
  entries: TimelineEntry[];
}

function FixTimeline({ entries }: FixTimelineProps) {
  return (
    <div className="space-y-3">
      {entries.map((entry, index) => (
        <div key={index} className="flex items-start space-x-3">
          <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-900">{entry.action}</p>
              <span className="text-xs text-gray-500">
                {new Date(entry.timestamp).toLocaleDateString()}
              </span>
            </div>
            <p className="text-sm text-gray-600">{entry.details}</p>
            {entry.user && (
              <p className="text-xs text-gray-500">by {entry.user}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// Main Enhanced Dashboard Page
export function EnhancedDashboardPage() {
  const { summary, loading, error, filters, setFilters, availableFilters, fetchSummary } = useReportsSummary();
  const { isConnected } = useConnectionStatus();
  
  const [showIssueDetails, setShowIssueDetails] = useState(false);

  // Prepare chart data
  const fixRateChartData = useMemo(() => {
    if (!summary?.reports) return [];
    
    return summary.reports
      .slice(0, 10) // Show last 10 reports
      .map(report => ({
        name: report.report_name.length > 20 ? `${report.report_name.substring(0, 20)}...` : report.report_name,
        fixRate: report.fix_rate,
        totalIssues: report.total_issues,
        fixedIssues: report.fixed_issues,
        fullName: report.report_name
      }));
  }, [summary]);

  const appTypeDistribution = useMemo(() => {
    if (!summary?.reports) return [];
    
    const distribution: Record<string, number> = {};
    summary.reports.forEach(report => {
      distribution[report.app_type] = (distribution[report.app_type] || 0) + 1;
    });
    
    return Object.entries(distribution).map(([app, count]) => ({
      name: app,
      value: count
    }));
  }, [summary]);

  const moduleIssuesDistribution = useMemo(() => {
    if (!summary?.reports) return [];
    
    const distribution: Record<string, number> = {};
    summary.reports.forEach(report => {
      report.modules.forEach(module => {
        distribution[module] = (distribution[module] || 0) + report.total_issues;
      });
    });
    
    return Object.entries(distribution)
      .map(([module, issues]) => ({
        name: module.charAt(0).toUpperCase() + module.slice(1),
        issues
      }))
      .sort((a, b) => b.issues - a.issues)
      .slice(0, 6);
  }, [summary]);

  // Mock data for issue timeline
  const mockTimelineData = [
    { timestamp: new Date(Date.now() - 86400000).toISOString(), action: 'Issue Fixed', details: 'Accessibility contrast issue resolved', user: 'John Doe' },
    { timestamp: new Date(Date.now() - 172800000).toISOString(), action: 'Issue Created', details: 'Low contrast ratio detected in navigation', user: 'System' },
    { timestamp: new Date(Date.now() - 259200000).toISOString(), action: 'ADO Work Item Created', details: 'Work item #12345 created in Azure DevOps', user: 'UX Analyzer' }
  ];

  if (loading && !summary) {
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
          <h1 className="text-3xl font-bold text-gray-900">ADO Dashboard</h1>
          <p className="text-gray-600 mt-1">Issue triage, fix history, and resolution status</p>
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
            onClick={fetchSummary}
            className="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
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

      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Total Reports</h3>
                <p className="text-3xl font-bold text-blue-600">{summary.summary.total_reports}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-500" />
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Analysis reports tracked
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Total Issues</h3>
                <p className="text-3xl font-bold text-red-600">{summary.summary.total_issues}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Issues identified
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Issues Fixed</h3>
                <p className="text-3xl font-bold text-green-600">{summary.summary.total_fixed}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Issues resolved
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Fix Rate</h3>
                <p className="text-3xl font-bold text-purple-600">{summary.summary.avg_fix_rate}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-500" />
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Average resolution rate
            </p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Filter className="w-5 h-5 mr-2" />
            Filters
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">App Type</label>
            <select
              value={filters.app_type}
              onChange={(e) => setFilters({ ...filters, app_type: e.target.value })}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Apps</option>
              {availableFilters.app_types.map(app => (
                <option key={app} value={app}>{app}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Task Type</label>
            <select
              value={filters.task_type}
              onChange={(e) => setFilters({ ...filters, task_type: e.target.value })}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Tasks</option>
              {availableFilters.task_types.map(task => (
                <option key={task} value={task}>{task}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Module</label>
            <select
              value={filters.module}
              onChange={(e) => setFilters({ ...filters, module: e.target.value })}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Modules</option>
              {availableFilters.modules.map(module => (
                <option key={module} value={module}>{module.charAt(0).toUpperCase() + module.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Fix Rate by Report */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Fix Rate by Report</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={fixRateChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip 
                formatter={(value) => [`${value}%`, 'Fix Rate']}
                labelFormatter={(label) => {
                  const item = fixRateChartData.find(d => d.name === label);
                  return item?.fullName || label;
                }}
              />
              <Bar dataKey="fixRate" fill={COLORS.primary} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* App Type Distribution */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Reports by App Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={appTypeDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {appTypeDistribution.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Module Issues Distribution */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Issues by Module</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={moduleIssuesDistribution} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" width={100} />
              <Tooltip />
              <Bar dataKey="issues" fill={COLORS.warning} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Fix Timeline */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Fix History</h3>
          <FixTimeline entries={mockTimelineData} />
        </div>
      </div>

      {/* Detailed Issue Table */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Detailed Issues</h2>
          <button
            onClick={() => setShowIssueDetails(!showIssueDetails)}
            className="inline-flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            <Eye className="w-4 h-4 mr-2" />
            {showIssueDetails ? 'Hide Details' : 'Show Details'}
          </button>
        </div>

        {showIssueDetails && (
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Report</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">App Type</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Issues</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Fixed</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Fix Rate</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">ADO Status</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {summary?.reports.slice(0, 10).map((report) => (
                  <tr key={report.analysis_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium text-gray-900">{report.report_name}</p>
                        <p className="text-sm text-gray-500">{new Date(report.timestamp).toLocaleDateString()}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{report.app_type}</td>
                    <td className="px-4 py-3 text-sm font-medium">{report.total_issues}</td>
                    <td className="px-4 py-3 text-sm font-medium text-green-600">{report.fixed_issues}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center">
                        <div className="w-full bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full" 
                            style={{ width: `${report.fix_rate}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{report.fix_rate}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        report.ado_integration.work_items_created > 0 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {report.ado_integration.work_items_created > 0 
                          ? `${report.ado_integration.work_items_created} items` 
                          : 'No items'
                        }
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        to={`/report/${report.analysis_id}`}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        View Report
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
