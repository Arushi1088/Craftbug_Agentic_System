import { useState } from 'react';
import { 
  X, 
  Camera, 
  Clock, 
  ExternalLink, 
  CheckCircle, 
  AlertCircle, 
  Eye,
  User,
  Calendar,
  MapPin,
  Tag,
  MessageSquare,
  Activity
} from 'lucide-react';

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

interface IssueDetailPanelProps {
  issue: EnhancedIssue | null;
  isOpen: boolean;
  onClose: () => void;
  onStatusChange: (issueId: string, newStatus: 'open' | 'fixed' | 'ignored') => void;
  onScreenshotView: (issue: EnhancedIssue) => void;
}

export function IssueDetailPanel({ 
  issue, 
  isOpen, 
  onClose, 
  onStatusChange, 
  onScreenshotView 
}: IssueDetailPanelProps) {
  const [newComment, setNewComment] = useState('');

  if (!isOpen || !issue) return null;

  const handleStatusChange = (newStatus: 'open' | 'fixed' | 'ignored') => {
    onStatusChange(issue.id, newStatus);
  };

  const handleAddComment = () => {
    if (newComment.trim()) {
      // In a real app, this would call the API to add a comment
      console.log('Adding comment:', newComment);
      setNewComment('');
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'fixed': return 'bg-green-100 text-green-800 border-green-200';
      case 'ignored': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'open': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h2 className="text-xl font-semibold text-gray-900">{issue.title}</h2>
            <span className={`inline-flex items-center px-2 py-1 text-xs font-bold rounded-full ${getSeverityColor(issue.severity)}`}>
              {issue.severity.toUpperCase()}
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6 space-y-6">
            {/* Issue Metadata */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Tag className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Module:</span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {issue.module}
                  </span>
                </div>

                <div className="flex items-center space-x-2">
                  <MapPin className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Element:</span>
                  <code className="text-sm text-gray-900 bg-gray-100 px-2 py-1 rounded">
                    {issue.element}
                  </code>
                </div>

                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Detected:</span>
                  <span className="text-sm text-gray-900">
                    {new Date(issue.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Activity className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Status:</span>
                  <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md border ${getStatusColor(issue.status)}`}>
                    {issue.status.charAt(0).toUpperCase() + issue.status.slice(1)}
                  </span>
                </div>

                <div className="flex items-center space-x-2">
                  <User className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Report ID:</span>
                  <span className="text-sm text-gray-900 font-mono">
                    {issue.report_id}
                  </span>
                </div>

                {issue.ado_link && (
                  <div className="flex items-center space-x-2">
                    <ExternalLink className="w-4 h-4 text-gray-500" />
                    <a
                      href={issue.ado_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      View in Azure DevOps
                    </a>
                  </div>
                )}
              </div>
            </div>

            {/* Recommendation */}
            {issue.recommendation && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-blue-900 mb-2">Recommendation</h3>
                <p className="text-sm text-blue-800">{issue.recommendation}</p>
              </div>
            )}

            {/* Screenshot */}
            {issue.screenshot_path && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-medium text-gray-900">Screenshot</h3>
                  <button
                    onClick={() => onScreenshotView(issue)}
                    className="inline-flex items-center px-3 py-1 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
                  >
                    <Camera className="w-4 h-4 mr-1" />
                    View Full Size
                  </button>
                </div>
                <div className="aspect-video bg-gray-200 rounded-lg flex items-center justify-center">
                  <img
                    src={`/reports/screenshots/${issue.screenshot_path}`}
                    alt={issue.title}
                    className="max-w-full max-h-full rounded-lg"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                      (e.target as HTMLImageElement).nextElementSibling!.classList.remove('hidden');
                    }}
                  />
                  <div className="hidden text-center">
                    <Camera className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">Screenshot not available</p>
                  </div>
                </div>
              </div>
            )}

            {/* Fix History Timeline */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                <Clock className="w-4 h-4 mr-2" />
                Fix History
              </h3>
              
              {issue.fix_history.length > 0 ? (
                <div className="space-y-3">
                  {issue.fix_history.map((entry, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900">{entry.note}</p>
                        <div className="flex items-center mt-1 space-x-2 text-xs text-gray-500">
                          {entry.developer && (
                            <>
                              <User className="w-3 h-3" />
                              <span>{entry.developer}</span>
                              <span>•</span>
                            </>
                          )}
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(entry.timestamp).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No fix history available</p>
              )}
            </div>

            {/* Add Comment Section */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                <MessageSquare className="w-4 h-4 mr-2" />
                Add Update
              </h3>
              
              <div className="space-y-3">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Add a comment about this issue..."
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                />
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="notify-team"
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <label htmlFor="notify-team" className="text-sm text-gray-700">
                      Notify team members
                    </label>
                  </div>
                  
                  <button
                    onClick={handleAddComment}
                    disabled={!newComment.trim()}
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Add Comment
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer - Action Buttons */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Change Status:</span>
            
            {issue.status !== 'fixed' && (
              <button
                onClick={() => handleStatusChange('fixed')}
                className="inline-flex items-center px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700"
              >
                <CheckCircle className="w-4 h-4 mr-1" />
                Mark Fixed
              </button>
            )}
            
            {issue.status !== 'ignored' && (
              <button
                onClick={() => handleStatusChange('ignored')}
                className="inline-flex items-center px-3 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700"
              >
                <Eye className="w-4 h-4 mr-1" />
                Ignore
              </button>
            )}
            
            {issue.status !== 'open' && (
              <button
                onClick={() => handleStatusChange('open')}
                className="inline-flex items-center px-3 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700"
              >
                <AlertCircle className="w-4 h-4 mr-1" />
                Reopen
              </button>
            )}
          </div>

          <div className="flex items-center space-x-3">
            {issue.ado_link && (
              <a
                href={issue.ado_link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                Open in ADO
              </a>
            )}
            
            <button
              onClick={onClose}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
