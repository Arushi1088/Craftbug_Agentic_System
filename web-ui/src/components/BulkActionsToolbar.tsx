import { useState } from 'react';
import { 
  CheckSquare, 
  Square, 
  MoreHorizontal, 
  Check, 
  X, 
  Eye, 
  ExternalLink,
  Download,
  Filter,
  ArrowUpDown
} from 'lucide-react';

interface BulkActionsToolbarProps {
  selectedCount: number;
  totalCount: number;
  onSelectAll: () => void;
  onClearSelection: () => void;
  onBulkAction: (action: 'fix' | 'ignore' | 'reopen' | 'export') => void;
  isAllSelected: boolean;
}

export function BulkActionsToolbar({ 
  selectedCount, 
  totalCount, 
  onSelectAll, 
  onClearSelection, 
  onBulkAction,
  isAllSelected 
}: BulkActionsToolbarProps) {
  const [showActions, setShowActions] = useState(false);

  return (
    <div className="flex items-center justify-between py-3 px-4 bg-gray-50 border-b border-gray-200">
      <div className="flex items-center space-x-4">
        {/* Select All Checkbox */}
        <button
          onClick={isAllSelected ? onClearSelection : onSelectAll}
          className="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900"
        >
          {isAllSelected ? (
            <CheckSquare className="w-4 h-4 text-blue-600" />
          ) : (
            <Square className="w-4 h-4" />
          )}
          <span>Select All ({totalCount})</span>
        </button>

        {/* Selection Counter */}
        {selectedCount > 0 && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">
              {selectedCount} selected
            </span>
            <button
              onClick={onClearSelection}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Clear
            </button>
          </div>
        )}
      </div>

      {/* Bulk Actions */}
      {selectedCount > 0 && (
        <div className="flex items-center space-x-2">
          {/* Quick Actions */}
          <button
            onClick={() => onBulkAction('fix')}
            className="inline-flex items-center px-3 py-1.5 bg-green-100 text-green-800 text-sm font-medium rounded-md hover:bg-green-200 transition-colors"
          >
            <Check className="w-4 h-4 mr-1" />
            Mark Fixed
          </button>

          <button
            onClick={() => onBulkAction('ignore')}
            className="inline-flex items-center px-3 py-1.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-200 transition-colors"
          >
            <Eye className="w-4 h-4 mr-1" />
            Ignore
          </button>

          <button
            onClick={() => onBulkAction('reopen')}
            className="inline-flex items-center px-3 py-1.5 bg-blue-100 text-blue-800 text-sm font-medium rounded-md hover:bg-blue-200 transition-colors"
          >
            <X className="w-4 h-4 mr-1" />
            Reopen
          </button>

          {/* More Actions Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowActions(!showActions)}
              className="inline-flex items-center px-3 py-1.5 bg-white border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50 transition-colors"
            >
              <MoreHorizontal className="w-4 h-4" />
            </button>

            {showActions && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10">
                <div className="py-1">
                  <button
                    onClick={() => {
                      onBulkAction('export');
                      setShowActions(false);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export Selected
                  </button>
                  <button
                    onClick={() => setShowActions(false)}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Create ADO Work Items
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Table Controls */}
      {selectedCount === 0 && (
        <div className="flex items-center space-x-2">
          <button className="inline-flex items-center px-3 py-1.5 text-gray-600 text-sm font-medium hover:text-gray-800 transition-colors">
            <Filter className="w-4 h-4 mr-1" />
            Filter
          </button>
          <button className="inline-flex items-center px-3 py-1.5 text-gray-600 text-sm font-medium hover:text-gray-800 transition-colors">
            <ArrowUpDown className="w-4 h-4 mr-1" />
            Sort
          </button>
        </div>
      )}
    </div>
  );
}
