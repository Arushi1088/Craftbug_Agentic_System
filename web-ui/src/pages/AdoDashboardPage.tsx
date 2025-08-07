import { useState, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import {
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Eye,
  TrendingUp,
  Clock,
  User,
  Camera,
  X,
  Activity
} from 'lucide-react';
import { useReportsSummary, useConnectionStatus } from '../hooks/useAPI';
import { IssueTable } from '../components/IssueTable';
import { IssueDetailPanel } from '../components/IssueDetailPanel';
import { DashboardSummary } from '../components/DashboardSummary';

const COLORS = {
  primary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#6366f1',
  gray: '#6b7280'
};

// Enhanced Issue interface for individual issue management
interface EnhancedIssue {
  id: string;
  title: string;
  module: string;
  status: 'open' | 'fixed' | 'ignored';
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  fix_history: Array<{
    timestamp: string;
    note: string;
    developer?: string;
  }>;
  screenshot_path?: string;
  ado_link?: string;
  report_id: string;
  element?: string;
  recommendation?: string;
}

// Screenshot Preview Modal Component
interface ScreenshotModalProps {
  isOpen: boolean;
  onClose: () => void;
  screenshotPath?: string;
  issueTitle: string;
}

function ScreenshotModal({ isOpen, onClose, screenshotPath, issueTitle }: ScreenshotModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-lg p-6 max-w-4xl max-h-[90vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">{issueTitle}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        {screenshotPath ? (
          <img
            src={`/reports/screenshots/${screenshotPath}`}
            alt={issueTitle}
            className="max-w-full h-auto rounded-lg shadow-lg"
            onError={(e) => {
              (e.target as HTMLImageElement).src = '/placeholder-screenshot.png';
            }}
          />
        ) : (
          <div className="flex items-center justify-center h-64 bg-gray-100 rounded-lg">
            <div className="text-center">
              <Camera className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500">No screenshot available</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Fix History Timeline Component
interface FixHistoryProps {
  history: Array<{
    timestamp: string;
    note: string;
    developer?: string;
  }>;
}

function FixHistoryTimeline({ history }: FixHistoryProps) {
  if (!history || history.length === 0) {
    return (
      <div className="text-center py-4 text-gray-500">
        <Clock className="w-8 h-8 mx-auto mb-2 text-gray-400" />
        <p>No fix history available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {history.map((entry, index) => (
        <div key={index} className="flex items-start space-x-3">
          <div className="flex-shrink-0 w-3 h-3 bg-blue-500 rounded-full mt-2"></div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-900">{entry.note}</p>
              <span className="text-xs text-gray-500">
                {new Date(entry.timestamp).toLocaleDateString()}
              </span>
            </div>
            {entry.developer && (
              <p className="text-xs text-gray-600 flex items-center mt-1">
                <User className="w-3 h-3 mr-1" />
                {entry.developer}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// Main ADO Dashboard Page Component
export function AdoDashboardPage() {
  const { summary, loading, error, availableFilters, fetchSummary } = useReportsSummary();
  const { isConnected } = useConnectionStatus();
  
  // Local state for enhanced filtering and UI
  const [statusFilter, setStatusFilter] = useState<'all' | 'open' | 'fixed' | 'ignored'>('all');
  const [selectedModule, setSelectedModule] = useState<string>('');
  const [selectedReport, setSelectedReport] = useState<string>('');
  const [screenshotModal, setScreenshotModal] = useState<{isOpen: boolean, issue?: EnhancedIssue}>({isOpen: false});
  const [showTimeline, setShowTimeline] = useState<string | null>(null);
  const [selectedIssue, setSelectedIssue] = useState<EnhancedIssue | null>(null);
  const [showDetailPanel, setShowDetailPanel] = useState(false);

  // Convert summary data to enhanced issues for granular management
  const enhancedIssues = useMemo(() => {
    if (!summary?.reports) return [];
    
    const issues: EnhancedIssue[] = [];
    
    summary.reports.forEach(report => {
      // Generate mock issues based on report data for demonstration
      report.modules.forEach(module => {
        const issueCount = Math.floor(Math.random() * 3) + 1; // 1-3 issues per module
        
        for (let i = 0; i < issueCount; i++) {
          const issue: EnhancedIssue = {
            id: `${report.analysis_id}-${module}-${i}`,
            title: `${module.charAt(0).toUpperCase() + module.slice(1)} issue detected`,
            module: module,
            status: Math.random() > 0.6 ? 'fixed' : 'open',
            severity: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as 'low' | 'medium' | 'high',
            timestamp: report.timestamp,
            fix_history: Math.random() > 0.5 ? [
              {
                timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
                note: `${module} issue identified during analysis`,
                developer: 'UX Analyzer'
              }
            ] : [],
            screenshot_path: Math.random() > 0.7 ? `${report.analysis_id}-${module}.png` : undefined,
            ado_link: Math.random() > 0.8 ? `https://dev.azure.com/project/workitem/${Math.floor(Math.random() * 1000)}` : undefined,
            report_id: report.analysis_id,
            element: `.${module}-element`,
            recommendation: `Fix ${module} issues according to best practices`
          };
          
          issues.push(issue);
        }
      });
    });
    
    return issues;
  }, [summary]);

  // Filter issues based on current filter state
  const filteredIssues = useMemo(() => {
    return enhancedIssues.filter(issue => {
      if (statusFilter !== 'all' && issue.status !== statusFilter) return false;
      if (selectedModule && issue.module !== selectedModule) return false;
      if (selectedReport && issue.report_id !== selectedReport) return false;
      return true;
    });
  }, [enhancedIssues, statusFilter, selectedModule, selectedReport]);

  // Handle issue status changes
  const handleStatusChange = (issueId: string, newStatus: 'open' | 'fixed' | 'ignored') => {
    // In a real app, this would update the backend
    console.log(`Changing issue ${issueId} status to ${newStatus}`);
    // For now, we'll just log it - the actual implementation would update the state
  };

  // Handle issue selection for detailed view
  const handleIssueSelect = (issue: EnhancedIssue) => {
    setSelectedIssue(issue);
    setShowDetailPanel(true);
  };

  // Calculate stats for filtered issues
  const filteredStats = useMemo(() => {
    const total = filteredIssues.length;
    const fixed = filteredIssues.filter(i => i.status === 'fixed').length;
    const open = filteredIssues.filter(i => i.status === 'open').length;
    const ignored = filteredIssues.filter(i => i.status === 'ignored').length;
    const fixRate = total > 0 ? (fixed / total * 100) : 0;
    
    return { total, fixed, open, ignored, fixRate };
  }, [filteredIssues]);

  // Chart data for module fix rates
  const moduleFixRates = useMemo(() => {
    const moduleStats: Record<string, { total: number, fixed: number }> = {};
    
    filteredIssues.forEach(issue => {
      if (!moduleStats[issue.module]) {
        moduleStats[issue.module] = { total: 0, fixed: 0 };
      }
      moduleStats[issue.module].total++;
      if (issue.status === 'fixed') {
        moduleStats[issue.module].fixed++;
      }
    });
    
    return Object.entries(moduleStats).map(([module, stats]) => ({
      name: module.charAt(0).toUpperCase() + module.slice(1),
      fixRate: stats.total > 0 ? (stats.fixed / stats.total * 100) : 0,
      total: stats.total,
      fixed: stats.fixed
    }));
  }, [filteredIssues]);

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">ADO Issue Triage Dashboard</h1>
          <p className="text-gray-600 mt-1">Manage UX issues with Azure DevOps workflow</p>
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

      {/* Dashboard Summary Section */}
      <DashboardSummary summary={summary} loading={loading} />

      {/* Top Summary Bar */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Total Issues</h3>
              <p className="text-2xl font-bold text-gray-900">{filteredStats.total}</p>
            </div>
            <Activity className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Open Issues</h3>
              <p className="text-2xl font-bold text-red-600">{filteredStats.open}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Fixed Issues</h3>
              <p className="text-2xl font-bold text-green-600">{filteredStats.fixed}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Ignored</h3>
              <p className="text-2xl font-bold text-gray-600">{filteredStats.ignored}</p>
            </div>
            <Eye className="w-8 h-8 text-gray-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Fix Rate</h3>
              <p className="text-2xl font-bold text-purple-600">{filteredStats.fixRate.toFixed(1)}%</p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Filter Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
        
        {/* Status Filter Toggle */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
          <div className="flex space-x-2">
            {['all', 'open', 'fixed', 'ignored'].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status as typeof statusFilter)}
                className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  statusFilter === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Module Filter Pills */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Module</label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedModule('')}
              className={`px-3 py-2 text-sm font-medium rounded-full transition-colors ${
                !selectedModule
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All Modules
            </button>
            {availableFilters.modules.map((module) => (
              <button
                key={module}
                onClick={() => setSelectedModule(module)}
                className={`px-3 py-2 text-sm font-medium rounded-full transition-colors ${
                  selectedModule === module
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {module.charAt(0).toUpperCase() + module.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Report Filter Dropdown */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Report</label>
          <select
            value={selectedReport}
            onChange={(e) => setSelectedReport(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Reports</option>
            {summary?.reports.map((report) => (
              <option key={report.analysis_id} value={report.analysis_id}>
                {report.report_name} - {new Date(report.timestamp).toLocaleDateString()}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Fix Rate Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Fix Rate by Module</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={moduleFixRates}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip
              formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Fix Rate']}
              labelFormatter={(label) => `Module: ${label}`}
            />
            <Bar dataKey="fixRate" fill={COLORS.primary} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Enhanced Issue Triage Table */}
      <IssueTable
        issues={filteredIssues}
        onIssueSelect={handleIssueSelect}
        onScreenshotView={(issue) => setScreenshotModal({isOpen: true, issue})}
        onTimelineView={(issue) => setShowTimeline(showTimeline === issue.id ? null : issue.id)}
        onStatusChange={handleStatusChange}
      />

      {/* Fix History Timeline (Expandable) */}
      {showTimeline && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Fix History Timeline</h3>
            <button
              onClick={() => setShowTimeline(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          {(() => {
            const issue = filteredIssues.find(i => i.id === showTimeline);
            return issue ? (
              <FixHistoryTimeline history={issue.fix_history} />
            ) : (
              <p className="text-gray-500">Issue not found</p>
            );
          })()}
        </div>
      )}

      {/* Screenshot Preview Modal */}
      <ScreenshotModal
        isOpen={screenshotModal.isOpen}
        onClose={() => setScreenshotModal({isOpen: false})}
        screenshotPath={screenshotModal.issue?.screenshot_path}
        issueTitle={screenshotModal.issue?.title || ''}
      />

      {/* Issue Detail Panel */}
      <IssueDetailPanel
        issue={selectedIssue}
        isOpen={showDetailPanel}
        onClose={() => {
          setShowDetailPanel(false);
          setSelectedIssue(null);
        }}
        onStatusChange={handleStatusChange}
        onScreenshotView={(issue) => setScreenshotModal({isOpen: true, issue})}
      />
    </div>
  );
}
