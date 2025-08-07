import { useState, useMemo } from 'react';
import { 
  CheckSquare, 
  Square, 
  Camera, 
  Clock, 
  ExternalLink,
  AlertCircle,
  CheckCircle,
  Eye,
  User,
  Calendar,
  MapPin,
  ArrowUpDown
} from 'lucide-react';
import { BulkActionsToolbar } from './BulkActionsToolbar';

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

interface IssueTableProps {
  issues: EnhancedIssue[];
  onIssueSelect: (issue: EnhancedIssue) => void;
  onScreenshotView: (issue: EnhancedIssue) => void;
  onTimelineView: (issue: EnhancedIssue) => void;
  onStatusChange: (issueId: string, newStatus: 'open' | 'fixed' | 'ignored') => void;
}

type SortField = 'title' | 'module' | 'status' | 'severity' | 'timestamp';
type SortDirection = 'asc' | 'desc';

// Status and Severity Badge Components
function StatusBadge({ status, severity }: { status: string; severity: string }) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'fixed': return <CheckCircle className="w-3 h-3" />;
      case 'ignored': return <Eye className="w-3 h-3" />;
      case 'open': return <AlertCircle className="w-3 h-3" />;
      default: return <AlertCircle className="w-3 h-3" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'fixed': return 'bg-green-100 text-green-800 border-green-200';
      case 'ignored': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'open': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-yellow-500 text-white';
      case 'low': return 'bg-blue-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md border ${getStatusColor(status)}`}>
        {getStatusIcon(status)}
        <span className="ml-1 capitalize">{status}</span>
      </span>
      <span className={`inline-flex items-center px-2 py-1 text-xs font-bold rounded-full ${getSeverityColor(severity)}`}>
        {severity.toUpperCase()}
      </span>
    </div>
  );
}

export function IssueTable({ 
  issues, 
  onIssueSelect, 
  onScreenshotView, 
  onTimelineView, 
  onStatusChange 
}: IssueTableProps) {
  const [selectedIssues, setSelectedIssues] = useState<Set<string>>(new Set());
  const [sortField, setSortField] = useState<SortField>('timestamp');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  // Sorting logic
  const sortedIssues = useMemo(() => {
    return [...issues].sort((a, b) => {
      let aValue: any = a[sortField];
      let bValue: any = b[sortField];

      // Handle special cases
      if (sortField === 'timestamp') {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      } else if (sortField === 'severity') {
        const severityOrder = { 'critical': 4, 'high': 3, 'medium': 2, 'low': 1 };
        aValue = severityOrder[aValue as keyof typeof severityOrder] || 0;
        bValue = severityOrder[bValue as keyof typeof severityOrder] || 0;
      }

      if (sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  }, [issues, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleIssueSelection = (issueId: string) => {
    const newSelected = new Set(selectedIssues);
    if (newSelected.has(issueId)) {
      newSelected.delete(issueId);
    } else {
      newSelected.add(issueId);
    }
    setSelectedIssues(newSelected);
  };

  const handleSelectAll = () => {
    setSelectedIssues(new Set(issues.map(issue => issue.id)));
  };

  const handleClearSelection = () => {
    setSelectedIssues(new Set());
  };

  const handleBulkAction = (action: 'fix' | 'ignore' | 'reopen' | 'export') => {
    const selectedIssueIds = Array.from(selectedIssues);
    
    switch (action) {
      case 'fix':
        selectedIssueIds.forEach(id => onStatusChange(id, 'fixed'));
        break;
      case 'ignore':
        selectedIssueIds.forEach(id => onStatusChange(id, 'ignored'));
        break;
      case 'reopen':
        selectedIssueIds.forEach(id => onStatusChange(id, 'open'));
        break;
      case 'export':
        // Export functionality would be implemented here
        console.log('Exporting issues:', selectedIssueIds);
        break;
    }
    
    setSelectedIssues(new Set());
  };

  const isAllSelected = selectedIssues.size === issues.length && issues.length > 0;

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* Bulk Actions Toolbar */}
      <BulkActionsToolbar
        selectedCount={selectedIssues.size}
        totalCount={issues.length}
        onSelectAll={handleSelectAll}
        onClearSelection={handleClearSelection}
        onBulkAction={handleBulkAction}
        isAllSelected={isAllSelected}
      />

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left">
                <button
                  onClick={isAllSelected ? handleClearSelection : handleSelectAll}
                  className="text-gray-400 hover:text-gray-600"
                >
                  {isAllSelected ? (
                    <CheckSquare className="w-4 h-4" />
                  ) : (
                    <Square className="w-4 h-4" />
                  )}
                </button>
              </th>
              
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('title')}
              >
                <div className="flex items-center space-x-1">
                  <span>Issue</span>
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('module')}
              >
                <div className="flex items-center space-x-1">
                  <span>Module</span>
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('status')}
              >
                <div className="flex items-center space-x-1">
                  <span>Status</span>
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('timestamp')}
              >
                <div className="flex items-center space-x-1">
                  <span>Date</span>
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Details
              </th>
              
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedIssues.map((issue) => (
              <tr 
                key={issue.id} 
                className={`hover:bg-gray-50 transition-colors ${
                  selectedIssues.has(issue.id) ? 'bg-blue-50' : ''
                }`}
              >
                {/* Selection Checkbox */}
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => handleIssueSelection(issue.id)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    {selectedIssues.has(issue.id) ? (
                      <CheckSquare className="w-4 h-4 text-blue-600" />
                    ) : (
                      <Square className="w-4 h-4" />
                    )}
                  </button>
                </td>

                {/* Issue Details */}
                <td className="px-6 py-4">
                  <div className="flex items-start space-x-3">
                    <div className="flex-1 min-w-0">
                      <button
                        onClick={() => onIssueSelect(issue)}
                        className="text-sm font-medium text-gray-900 hover:text-blue-600 text-left"
                      >
                        {issue.title}
                      </button>
                      <div className="flex items-center mt-1 space-x-2 text-xs text-gray-500">
                        <MapPin className="w-3 h-3" />
                        <span>{issue.element}</span>
                      </div>
                      {issue.recommendation && (
                        <p className="mt-1 text-xs text-gray-600 line-clamp-2">
                          {issue.recommendation}
                        </p>
                      )}
                    </div>
                  </div>
                </td>

                {/* Module */}
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {issue.module}
                  </span>
                </td>

                {/* Status & Severity */}
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge status={issue.status} severity={issue.severity} />
                </td>

                {/* Date */}
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="w-3 h-3 mr-1" />
                    {new Date(issue.timestamp).toLocaleDateString()}
                  </div>
                </td>

                {/* Issue Details */}
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    {issue.fix_history.length > 0 && (
                      <div className="flex items-center">
                        <User className="w-3 h-3 mr-1" />
                        <span>{issue.fix_history.length} updates</span>
                      </div>
                    )}
                    {issue.screenshot_path && (
                      <div className="flex items-center text-green-600">
                        <Camera className="w-3 h-3 mr-1" />
                        <span>Screenshot</span>
                      </div>
                    )}
                  </div>
                </td>

                {/* Actions */}
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center space-x-2">
                    {issue.screenshot_path && (
                      <button
                        onClick={() => onScreenshotView(issue)}
                        className="text-blue-600 hover:text-blue-800 p-1 rounded hover:bg-blue-100"
                        title="View Screenshot"
                      >
                        <Camera className="w-4 h-4" />
                      </button>
                    )}
                    
                    <button
                      onClick={() => onTimelineView(issue)}
                      className="text-purple-600 hover:text-purple-800 p-1 rounded hover:bg-purple-100"
                      title="View Timeline"
                    >
                      <Clock className="w-4 h-4" />
                    </button>
                    
                    {issue.ado_link && (
                      <a
                        href={issue.ado_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-green-600 hover:text-green-800 p-1 rounded hover:bg-green-100"
                        title="Open in ADO"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}

                    {/* Quick Status Change */}
                    <div className="flex items-center space-x-1">
                      {issue.status !== 'fixed' && (
                        <button
                          onClick={() => onStatusChange(issue.id, 'fixed')}
                          className="text-green-600 hover:text-green-800 p-1 rounded hover:bg-green-100"
                          title="Mark Fixed"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                      )}
                      
                      {issue.status !== 'ignored' && (
                        <button
                          onClick={() => onStatusChange(issue.id, 'ignored')}
                          className="text-gray-600 hover:text-gray-800 p-1 rounded hover:bg-gray-100"
                          title="Ignore"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      )}
                      
                      {issue.status !== 'open' && (
                        <button
                          onClick={() => onStatusChange(issue.id, 'open')}
                          className="text-red-600 hover:text-red-800 p-1 rounded hover:bg-red-100"
                          title="Reopen"
                        >
                          <AlertCircle className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Empty State */}
      {issues.length === 0 && (
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No issues found</h3>
          <p className="text-gray-500">Try adjusting your filters or run a new analysis.</p>
        </div>
      )}
    </div>
  );
}
