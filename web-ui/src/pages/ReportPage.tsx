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
import { ENHANCED_SAMPLE_REPORT } from '../data/sampleReport';

// Enhanced type definitions for normalized report structure
type Finding = { 
  id?: string; 
  title?: string; 
  type?: string;
  message?: string;
  severity?: string; 
  ado_url?: string; 
  ado_work_item_id?: string;
  element?: string;
  recommendation?: string;
  fixed?: boolean;
  fix_timestamp?: string;
  ado_status?: string;
  ado_created_date?: string;
  // Media attachments for visual evidence
  screenshot?: string;
  video?: string;
  screenshot_base64?: string;
  video_base64?: string;
  [k: string]: any; 
};

type NormalizedModule = { 
  key: string; 
  title?: string; 
  score?: number; 
  findings: Finding[];
  recommendations?: string[];
  threshold_met?: boolean;
  analytics_enabled?: boolean;
};

type NormalizedReport = {
  analysis_id: string;
  url?: string | null;
  status: string;
  total_issues: number;
  modules: NormalizedModule[];
  timestamp?: string;
  app_type?: string;
  overall_score?: number;
  performance_metrics?: any;
  has_screenshots?: boolean;
  ado_integration?: any;
  scenario_results?: any[];
  ux_issues?: UXIssue[];
  isFailed?: boolean;
  ui_error?: string | null;
  enhanced_report?: any; // Enhanced report data with media attachments
};

// Interface for module findings from real backend data
interface ModuleFinding {
  type: string;
  message: string;
  severity: string;
  element?: string;
  recommendation: string;
  fixed?: boolean;
  fix_timestamp?: string;
  // Azure DevOps integration metadata
  ado_work_item_id?: string;
  ado_status?: string;
  ado_url?: string;
  ado_created_date?: string;
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
  functional: <PlayCircle className="w-5 h-5" />,
  craft_bug: <AlertTriangle className="w-5 h-5" />,
  navigation: <ArrowLeft className="w-5 h-5" />,
  visual_design: <Eye className="w-5 h-5" />
};

const moduleNames: { [key: string]: string } = {
  performance: 'Performance',
  accessibility: 'Accessibility', 
  keyboard: 'Keyboard Navigation',
  ux_heuristics: 'UX Heuristics',
  best_practices: 'Best Practices',
  health_alerts: 'Health Alerts',
  functional: 'Functional Testing',
  craft_bug: 'Craft Bug Detection',
  navigation: 'Navigation',
  visual_design: 'Visual Design'
};

// URL safety helper function
const toAbsoluteUrl = (u?: string | null) => {
  if (!u) return null;
  try { 
    return new URL(u, window.location.origin).toString(); 
  } catch (e) {
    console.warn('Bad URL in report:', u, e);
    return null;
  }
};

// Report normalization function for consistent data shape with scenario fallback
const normalizeReport = (r: any): NormalizedReport => {
  console.log('🔍 Normalizing report data:', r);
  
  // Check if this is a failed report
  const isFailed = r?.status === 'failed' || !!r?.error;
  const ui_error = r?.ui_error || r?.error || null;
  
  if (isFailed) {
    console.log('⚠️ Handling failed report:', ui_error);
    // For failed reports, create a minimal but displayable structure
    return {
      analysis_id: r?.analysis_id ?? '',
      url: toAbsoluteUrl(r?.url ?? null),
      status: 'failed',
      total_issues: 0,
      modules: [],
      timestamp: r?.timestamp || new Date().toISOString(),
      app_type: r?.app_type,
      overall_score: 0,
      performance_metrics: r?.performance_metrics,
      has_screenshots: false,
      ado_integration: r?.ado_integration,
      scenario_results: [],
      ux_issues: [],
      isFailed: true,
      ui_error: ui_error
    };
  }
  
  // Handle the enhanced report structure with module_results
  const mr = r?.module_results && typeof r.module_results === 'object'
    ? r.module_results
    : {};

  let entries = Object.entries(mr);
  console.log('📊 Module results entries:', entries);
  
  // Fallback: derive from scenario_results if module_results empty
  if (entries.length === 0 && Array.isArray(r?.scenario_results)) {
    console.log('⚠️ No module_results found, deriving from scenario_results');
    const derived = deriveFromScenarios(r.scenario_results);
    entries = Object.entries(derived);
  }
  
  // Additional fallback: check for legacy format with direct modules
  if (entries.length === 0 && r?.modules && typeof r.modules === 'object') {
    console.log('⚠️ Using legacy modules format');
    entries = Object.entries(r.modules).map(([key, value]: [string, any]) => [
      key,
      {
        score: value?.score || 0,
        findings: value?.issues ? value.issues.map((issue: any) => ({
          type: issue.title || 'Issue',
          message: issue.description || 'No description',
          severity: issue.severity || 'medium',
          recommendation: 'Review and fix this issue'
        })) : [],
        recommendations: []
      }
    ]);
  }

  const modules: NormalizedModule[] = entries.map(([key, v]: [string, any]) => ({
    key,
    title: v?.title ?? moduleNames[key] ?? key.replace('_', ' '),
    score: typeof v?.score === 'number' ? v.score : undefined,
    findings: Array.isArray(v?.findings) ? v.findings : [],
    recommendations: Array.isArray(v?.recommendations) ? v.recommendations : [],
    threshold_met: v?.threshold_met,
    analytics_enabled: v?.analytics_enabled
  }));

  return {
    analysis_id: r?.analysis_id ?? '',
    url: toAbsoluteUrl(r?.url ?? null),
    status: r?.status ?? 'unknown',
    total_issues: Number.isFinite(r?.total_issues) ? r.total_issues : 
      modules.reduce((n, m) => n + m.findings.length, 0),
    modules,
    timestamp: r?.timestamp,
    app_type: r?.app_type,
    overall_score: r?.overall_score,
    performance_metrics: r?.performance_metrics,
    has_screenshots: r?.has_screenshots,
    ado_integration: r?.ado_integration,
    scenario_results: Array.isArray(r?.scenario_results) ? r.scenario_results : [],
    ux_issues: Array.isArray(r?.ux_issues) ? r.ux_issues : [],
    isFailed: false,
    ui_error: null
  };
};

// Derive modules from scenario results when module_results is empty
const deriveFromScenarios = (scens: any[]): Record<string, any> => {
  const findings: any[] = [];
  for (const sc of scens ?? []) {
    const scenarioName = sc.name || 'Unknown Scenario';
    for (const step of sc.steps ?? []) {
      if (step?.violations) {
        findings.push({ 
          type: 'violation', 
          message: `${step.violations} accessibility violations in ${scenarioName}`, 
          severity: 'medium',
          id: `violation-${findings.length}`
        });
      }
      if (step?.error || step?.status === 'failed') {
        findings.push({ 
          type: 'error', 
          message: `Step error in ${scenarioName}: ${String(step.error || 'Step failed')}`, 
          severity: 'high',
          id: `error-${findings.length}`
        });
      }
    }
  }
  return findings.length ? { ux_heuristics: { findings } } : {};
};

// ADO Integration Status Component
const ADOStatus: React.FC<{ 
  ado_work_item_id?: string;
  ado_status?: string;
  ado_url?: string;
  ado_created_date?: string;
}> = ({ ado_work_item_id, ado_status, ado_url }) => {
  if (!ado_work_item_id) return null;

  const getStatusColor = (status?: string) => {
    switch (status?.toLowerCase()) {
      case 'resolved':
      case 'closed':
        return 'bg-green-100 text-green-800';
      case 'active':
      case 'new':
        return 'bg-blue-100 text-blue-800';
      case 'in progress':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="flex items-center gap-2 text-xs">
      <div className="flex items-center gap-1">
        <ExternalLink className="w-3 h-3 text-blue-600" />
        {ado_url ? (
          <a 
            href={ado_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            ADO #{ado_work_item_id}
          </a>
        ) : (
          <span className="text-gray-600 font-medium">ADO #{ado_work_item_id}</span>
        )}
      </div>
      {ado_status && (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(ado_status)}`}>
          {ado_status}
        </span>
      )}
    </div>
  );
};

// Fix Now Button Component for Legacy Issues
interface FixNowButtonProps {
  issue: UXIssue;
  reportId: string;
  onFixApplied: () => void;
}

// ADO View & Fix Button Component
interface ADOViewFixButtonProps {
  workItemId?: string | number;
  finding?: Finding | ModuleFinding;
}

function ADOViewFixButton({ workItemId, finding }: ADOViewFixButtonProps) {
  const [isOpening, setIsOpening] = useState(false);

  const handleViewInADO = async () => {
    if (!workItemId) return;
    
    setIsOpening(true);
    try {
      const response = await fetch(`/api/ado/issue-url/${workItemId}`);
      const data = await response.json();
      
      if (data.url) {
        window.open(data.url, '_blank');
      } else {
        console.error('No ADO URL returned');
      }
    } catch (error) {
      console.error('Failed to get ADO URL:', error);
    } finally {
      setIsOpening(false);
    }
  };

  const handleTriggerFix = async () => {
    if (!workItemId || !finding) return;
    
    try {
      const response = await fetch('/api/ado/trigger-fix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          work_item_id: workItemId,
          file_path: finding.element || 'frontend/src/App.tsx',
          instruction: `Fix: ${finding.message}`
        })
      });
      
      const result = await response.json();
      console.log('Fix triggered:', result);
      
      // Show success notification
      alert(`Fix triggered for Work Item #${workItemId}. Check ADO for updates.`);
    } catch (error) {
      console.error('Failed to trigger fix:', error);
      alert('Failed to trigger automated fix. Please try again.');
    }
  };

  if (!workItemId) return null;

  return (
    <div className="flex gap-2 mt-2">
      <button
        onClick={handleViewInADO}
        disabled={isOpening}
        className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
      >
        {isOpening ? (
          <>
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            Opening...
          </>
        ) : (
          <>
            <ExternalLink className="w-3 h-3 mr-1" />
            View in ADO
          </>
        )}
      </button>
      
      <button
        onClick={handleTriggerFix}
        className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md bg-green-600 text-white hover:bg-green-700 transition-colors"
        title="Trigger automated fix via Gemini CLI"
      >
        <Settings className="w-3 h-3 mr-1" />
        Auto-Fix
      </button>
    </div>
  );
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

  const fixResult = getFixResult();
  const fixing = isFixing;

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
  finding: Finding | ModuleFinding;
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

  const fixResult = getFixResult();
  const fixing = isFixing;

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
  const { downloadReport } = useReports();
  const [report, setReport] = useState<NormalizedReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [hideFixed, setHideFixed] = useState(false);
  const [debugMode, setDebugMode] = useState(false);
  const [useSampleData, setUseSampleData] = useState(false);

  useEffect(() => {
    if (!reportId) return;
    
    // Handle sample data mode
    if (reportId === 'sample' || useSampleData) {
      console.log('📊 Using sample report data');
      const normalized = normalizeReport(ENHANCED_SAMPLE_REPORT);
      console.log('✅ Sample report normalized:', normalized);
      setReport(normalized);
      return;
    }
    
    let ignore = false;
    const ac = new AbortController();
    
    const loadReport = async () => {
      setLoading(true);
      try {
        console.log('📊 Loading report:', reportId);
        setLocalError(null);
        
        // Use direct fetch instead of hook to avoid dependency issues
        const response = await fetch(`http://localhost:8000/api/reports/${reportId}`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const rawData = await response.json();
        console.log('✅ Raw report data received:', rawData);
        console.log('🔍 Raw data total_issues:', rawData.total_issues);
        console.log('🔍 Raw data module_results:', rawData.module_results);
        
        // Load enhanced report if available
        let enhancedData = null;
        if (rawData.enhanced_report?.json_file) {
          try {
            console.log('📸 Loading enhanced report:', rawData.enhanced_report.json_file);
            const enhancedResponse = await fetch(`http://localhost:8000/${rawData.enhanced_report.json_file}`);
            if (enhancedResponse.ok) {
              enhancedData = await enhancedResponse.json();
              console.log('✅ Enhanced report loaded with media:', enhancedData?.media_attachments);
            }
          } catch (enhancedErr) {
            console.warn('⚠️ Failed to load enhanced report:', enhancedErr);
          }
        }
        
        if (!ignore) {
          const normalized = normalizeReport(rawData);
          console.log('✅ Normalized report:', normalized);
          console.log('🔍 Normalized total_issues:', normalized.total_issues);
          console.log('🔍 Normalized modules count:', normalized.modules.length);
          console.log('🔍 Normalized modules:', normalized.modules.map(m => ({ key: m.key, findings: m.findings.length })));
          console.log('📊 Raw report structure analysis:');
          console.log('- module_results keys:', Object.keys(rawData?.module_results || {}));
          console.log('- scenario_results count:', rawData?.scenario_results?.length || 0);
          console.log('- legacy modules keys:', Object.keys((rawData as any)?.modules || {}));
          console.log('- ux_issues count:', rawData?.ux_issues?.length || 0);
          console.log('- total_issues:', rawData?.total_issues);
          console.log('- overall_score:', rawData?.overall_score);
          console.log('REPORT RAW', rawData);
          console.log('MODULE KEYS', normalized.modules.map(m => m.key));
          console.log('TOTAL ISSUES', normalized.total_issues, 'computed:', normalized.modules.reduce((n,m)=>n+m.findings.length,0));
          
          // Merge enhanced report data with normalized report
          if (enhancedData) {
            console.log('🖼️ Merging enhanced report data with media attachments');
            // Add enhanced report data to the normalized report
            normalized.enhanced_report = enhancedData;
            normalized.has_screenshots = true;
            
            // Merge media attachments with findings
            if (enhancedData.media_attachments?.screenshots) {
              console.log('📸 Found screenshots in enhanced report:', enhancedData.media_attachments.screenshots.length);
              // The enhanced report generator already associates media with findings
              // We just need to make sure the findings have the media data
            }
          }
          
          setReport(normalized);
          
          // Determine active tab based on available data
          if (normalized.modules.length > 0) {
            setActiveTab('overview'); // Always start with overview tab
          } else if (normalized.ux_issues && normalized.ux_issues.length > 0) {
            setActiveTab('overview'); // Start with overview even if there are issues
          } else {
            setActiveTab('overview');
          }
        }
      } catch (err) {
        if (!ignore) {
          console.error('❌ Failed to load report:', reportId, err);
          // Handle specific 404 error for demo reports
          if (err instanceof Error && err.message.includes('404') && reportId.includes('demo')) {
            setLocalError(`Report "${reportId}" not found. Backend server may not be running. Try using the sample data below to see the enhanced analytics modules.`);
          } else {
            setLocalError(err instanceof Error ? err.message : 'Failed to load report');
          }
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    };

    loadReport();
    
    return () => { 
      ignore = true; 
      ac.abort(); 
    };
  }, [reportId, useSampleData]);

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
      setReport(null); // Clear current report to trigger loading state
      // The useEffect will trigger reload
    }
  };

  if (loading || !report) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading report...</span>
      </div>
    );
  }

  if (localError) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Report Not Found</h2>
        <p className="text-gray-600 mb-6">{localError || 'The requested report could not be found.'}</p>
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

  // Group legacy issues by type for tab navigation
  const issuesByType = report.ux_issues?.reduce((acc, issue) => {
    if (!acc[issue.type]) acc[issue.type] = [];
    acc[issue.type].push(issue);
    return acc;
  }, {} as Record<string, UXIssue[]>) || {};

  // Calculate metrics from normalized data
  const totalIssues = report.total_issues;
  const criticalIssues = report.modules.reduce((sum, module) => 
    sum + module.findings.filter(f => f.severity === 'critical' || f.severity === 'high').length, 0
  ) + (report.ux_issues?.filter(issue => 
    issue.severity === 'critical' || issue.severity === 'high'
  ).length || 0);

  const overallScore = report.overall_score || 
    (report.modules.length > 0 
      ? Math.round(report.modules.reduce((sum, m) => sum + (m.score || 0), 0) / report.modules.length)
      : 75);

  return (
    <div className="max-w-7xl mx-auto">
      {/* Debug Controls - Development Only */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-4">
            <h3 className="text-sm font-medium text-yellow-800">Debug Controls</h3>
            <button
              onClick={() => {
                setUseSampleData(!useSampleData);
                if (!useSampleData) {
                  // When enabling sample data, immediately load it
                  const normalized = normalizeReport(ENHANCED_SAMPLE_REPORT);
                  setReport(normalized);
                }
              }}
              className={`px-3 py-1 text-xs rounded ${
                useSampleData 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              {useSampleData ? 'Using Sample Data' : 'Use Sample Data'}
            </button>
            <button
              onClick={() => setDebugMode(!debugMode)}
              className={`px-3 py-1 text-xs rounded ${
                debugMode 
                  ? 'bg-blue-100 text-blue-800' 
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              {debugMode ? 'Debug Mode On' : 'Enable Debug Mode'}
            </button>
            <span className="text-xs text-yellow-700">
              ID: {reportId} | Modules: {report?.modules?.length || 0} | Issues: {report?.total_issues || 0}
            </span>
          </div>
          {debugMode && (
            <div className="mt-2 text-xs text-yellow-600">
              💡 Sample data shows enhanced report with accessibility, UX heuristics, performance, keyboard, best practices, health alerts, and craft bug detection modules
            </div>
          )}
        </div>
      )}

      {/* Failed Report Banner */}
      {report?.isFailed && (
        <div className="mb-6 rounded-md border border-red-200 bg-red-50 p-4">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-red-400 mr-3 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-800">Analysis Failed</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{report.ui_error || 'The analysis could not be completed due to an unknown error.'}</p>
                <div className="mt-3">
                  <p className="text-xs text-red-600">
                    <strong>Troubleshooting steps:</strong>
                  </p>
                  <ul className="list-disc list-inside text-xs text-red-600 mt-1 space-y-1">
                    <li>Verify the target URL is accessible and valid</li>
                    <li>Check that the scenario file exists and contains valid YAML/JSON</li>
                    <li>Ensure the backend server is running and responding</li>
                    <li>Review server logs for detailed error information</li>
                  </ul>
                </div>
                <div className="mt-3">
                  <button
                    onClick={() => window.location.reload()}
                    className="text-xs bg-red-100 hover:bg-red-200 text-red-800 px-2 py-1 rounded border border-red-300"
                  >
                    Retry Analysis
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
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
                href={toAbsoluteUrl(report.url) || report.url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-blue-600 hover:underline flex items-center"
              >
                {(() => {
                  const absoluteUrl = toAbsoluteUrl(report.url);
                  if (absoluteUrl) {
                    try {
                      return new URL(absoluteUrl).hostname;
                    } catch {
                      return report.url;
                    }
                  }
                  return report.url || 'Unknown';
                })()}
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
            {/* Module tabs from normalized data */}
            {report.modules.map((module) => (
              <button
                key={module.key}
                onClick={() => setActiveTab(module.key)}
                className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === module.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {moduleIcons[module.key] || <AlertTriangle className="w-5 h-5" />}
                <span className="ml-2 capitalize">{module.title}</span>
                <span className="ml-2 bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
                  {module.findings.length}
                </span>
              </button>
            ))}
            
            {/* Legacy issue type tabs - only show if not already in modules */}
            {Object.keys(issuesByType)
              .filter(type => !report.modules.some(module => module.key === type))
              .map((type) => (
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
              {(report.modules.some(module => 
                module.findings.some(f => f.fixed)
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
              
              {/* ADO Integration Summary */}
              {report.ado_integration && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Azure DevOps Integration
                  </h3>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <ExternalLink className="w-5 h-5 text-blue-600 mt-0.5" />
                      <div className="flex-1">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Work Items Created:</span>
                            <span className="ml-2 font-medium text-gray-900">
                              {report.ado_integration.work_items_created || 0}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-600">Last Sync:</span>
                            <span className="ml-2 font-medium text-gray-900">
                              {report.ado_integration.last_sync_date 
                                ? new Date(report.ado_integration.last_sync_date).toLocaleDateString()
                                : 'Never'
                              }
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-600">Sync Status:</span>
                            <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${
                              report.ado_integration.sync_status === 'completed'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {report.ado_integration.sync_status || 'Unknown'}
                            </span>
                          </div>
                        </div>
                        {report.ado_integration.work_items_created > 0 && (
                          <p className="text-xs text-gray-600 mt-2">
                            UX issues have been automatically synchronized with Azure DevOps work items. 
                            See individual issues for work item links and status updates.
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Issues Summary Chart */}
              {(report.modules.length > 0 || Object.keys(issuesByType).length > 0) && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Issues by Category
                  </h3>
                  <Plot
                    data={[
                      {
                        x: report.modules.length > 0 
                          ? report.modules.map(module => module.title)
                          : Object.keys(issuesByType).map(type => type.replace('_', ' ')),
                        y: report.modules.length > 0
                          ? report.modules.map(module => module.findings.length)
                          : Object.values(issuesByType).map(issues => issues.length),
                        type: 'bar',
                        marker: {
                          color: report.modules.length > 0
                            ? report.modules.map(module => {
                                const criticalCount = module.findings.filter(f => f.severity === 'critical' || f.severity === 'high').length;
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
              {report.scenario_results && report.scenario_results.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Scenario Test Results
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                    {report.scenario_results.map((scenario, index) => (
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
                                        src={`http://127.0.0.1:8000/reports/${step.screenshot}`}
                                        alt={`Screenshot for ${step.action} step`}
                                        className="w-full border rounded shadow-sm cursor-pointer hover:shadow-md transition-shadow"
                                        onClick={() => window.open(`http://127.0.0.1:8000/reports/${step.screenshot}`, '_blank')}
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
                {report.modules.length === 0 && (!report.ux_issues || report.ux_issues.length === 0) ? (
                  <div className="text-center py-8">
                    <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
                    <h4 className="text-lg font-medium text-gray-900 mb-2">No issues found!</h4>
                    <p className="text-gray-600">This analysis found no UX issues to report.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Show issues from module results if available */}
                    {report.modules.length > 0 ? (
                      report.modules.slice(0, 5).flatMap(module => 
                        module.findings.slice(0, 2).map((finding, index) => {
                          // Filter out fixed issues if toggle is enabled
                          if (hideFixed && finding.fixed) return null;
                          
                          return (
                            <div
                              key={`${module.key}-${index}`}
                              className={`p-4 rounded-lg border ${getSeverityColor(finding.severity || 'medium')} ${
                                finding.fixed ? 'opacity-50 border-gray-300' : ''
                              }`}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center justify-between">
                                    <h4 className="font-medium text-gray-900">
                                      [{module.title}] {finding.type || finding.title || 'Issue'}
                                    </h4>
                                    {finding.fixed && (
                                      <span className="text-green-600 text-sm font-semibold ml-2">✅ Fixed</span>
                                    )}
                                  </div>
                                  <p className="text-sm text-gray-600 mt-1">{finding.message}</p>
                                  {finding.element && (
                                    <p className="text-xs text-gray-500 mt-1">Element: {finding.element}</p>
                                  )}
                                  {finding.fixed && finding.fix_timestamp && (
                                    <div className="text-xs text-gray-500 mt-1">
                                      Fixed on: {new Date(finding.fix_timestamp).toLocaleString()}
                                    </div>
                                  )}
                                </div>
                                <div className="ml-4 text-right">
                                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(finding.severity || 'medium')}`}>
                                    {finding.severity || 'medium'}
                                  </span>
                                  {!finding.fixed && (
                                    <div className="space-y-2 mt-2">
                                      <ModuleFixNowButton 
                                        finding={finding}
                                        moduleKey={module.key}
                                        findingIndex={index}
                                        reportId={reportId!}
                                        onFixApplied={onFixApplied}
                                      />
                                      <ADOViewFixButton 
                                        workItemId={finding.ado_work_item_id}
                                        finding={finding}
                                      />
                                    </div>
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
                )}
              </div>
            </div>
          )}

          {/* Module results view (normalized data) */}
          {activeTab !== 'overview' && report.modules.find(m => m.key === activeTab) && (
            <div className="space-y-4">
              {(() => {
                const currentModule = report.modules.find(m => m.key === activeTab)!;
                return (
                  <>
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {currentModule.title} Analysis 
                        ({currentModule.findings.length} findings)
                      </h3>
                      <div className="text-sm text-gray-600 flex items-center space-x-4">
                        {currentModule.score !== undefined && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            currentModule.score >= 80 ? 'bg-green-100 text-green-800' :
                            currentModule.score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            Score: {currentModule.score}
                          </span>
                        )}
                        {currentModule.threshold_met !== undefined && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            currentModule.threshold_met ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {currentModule.threshold_met ? 'Threshold Met' : 'Below Threshold'}
                          </span>
                        )}
                        {currentModule.analytics_enabled && (
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            Analytics Enabled
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Module Findings */}
                    <div className="space-y-4">
                      {/* Toggle for hiding/showing fixed issues */}
                      {currentModule.findings.some(f => f.fixed) && (
                        <button
                          onClick={() => setHideFixed(!hideFixed)}
                          className="text-sm px-3 py-1.5 rounded bg-gray-200 hover:bg-gray-300 mb-4 transition-colors"
                        >
                          {hideFixed ? "Show All Issues" : "Hide Fixed Issues"}
                        </button>
                      )}
                      
                      {currentModule.findings.length === 0 ? (
                        <div className="text-center py-8">
                          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
                          <h4 className="text-lg font-medium text-gray-900 mb-2">✅ No issues found!</h4>
                          <p className="text-gray-600">This module analysis found no issues to report.</p>
                        </div>
                      ) : (
                        currentModule.findings.map((finding, index) => {
                          // Filter out fixed issues if toggle is enabled
                          if (hideFixed && finding.fixed) return null;
                          
                          return (
                            <div
                              key={index}
                              className={`p-4 rounded-lg border ${getSeverityColor(finding.severity || 'medium')} ${
                                finding.fixed ? 'opacity-50 border-gray-300' : ''
                              }`}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center justify-between">
                                    <h4 className="font-medium text-gray-900">{finding.type || finding.title || 'Issue'}</h4>
                                    {finding.fixed && (
                                      <span className="text-green-600 text-sm font-semibold ml-2">✅ Fixed</span>
                                    )}
                                  </div>
                                  <p className="text-sm text-gray-600 mt-1">{finding.message}</p>
                                  {finding.element && (
                                    <p className="text-xs text-gray-500 mt-1">
                                      <span className="font-medium">Element:</span> {finding.element}
                                    </p>
                                  )}
                                  {finding.recommendation && (
                                    <div className="mt-2">
                                      <p className="text-xs font-medium text-gray-700 mb-1">Recommendation:</p>
                                      <p className="text-xs text-gray-600">{finding.recommendation}</p>
                                    </div>
                                  )}
                                  
                                  {/* ADO Integration Status */}
                                  <div className="mt-2">
                                    <ADOStatus 
                                      ado_work_item_id={finding.ado_work_item_id}
                                      ado_status={finding.ado_status}
                                      ado_url={finding.ado_url}
                                      ado_created_date={finding.ado_created_date}
                                    />
                                  </div>
                                  
                                  {/* Show fix timestamp if available */}
                                  {finding.fixed && finding.fix_timestamp && (
                                    <div className="text-xs text-gray-500 mt-2">
                                      Fixed on: {new Date(finding.fix_timestamp).toLocaleString()}
                                    </div>
                                  )}
                                  
                                  {/* 🖼️ Screenshots and Videos for this finding */}
                                  {(finding.screenshot || finding.screenshot_base64 || finding.video) && (
                                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                                      <div className="flex items-center gap-2 mb-2">
                                        <Eye className="w-4 h-4 text-gray-600" />
                                        <span className="text-sm font-medium text-gray-700">Visual Evidence</span>
                                      </div>
                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                        {/* Screenshot */}
                                        {finding.screenshot && (
                                          <div className="relative group">
                                            <img
                                              src={`http://127.0.0.1:8000/reports/${finding.screenshot}`}
                                              alt={`Screenshot for ${finding.type || 'issue'}`}
                                              className="w-full h-32 object-cover rounded border cursor-pointer hover:shadow-md transition-shadow"
                                              onClick={() => window.open(`http://127.0.0.1:8000/reports/${finding.screenshot}`, '_blank')}
                                              onError={(e) => {
                                                console.error('Failed to load screenshot:', finding.screenshot);
                                                (e.target as HTMLImageElement).style.display = 'none';
                                              }}
                                            />
                                            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all flex items-center justify-center">
                                              <span className="text-white opacity-0 group-hover:opacity-100 text-xs font-medium">Click to enlarge</span>
                                            </div>
                                            <div className="text-xs text-gray-500 mt-1 text-center">Screenshot</div>
                                          </div>
                                        )}
                                        
                                        {/* Video */}
                                        {finding.video && (
                                          <div className="relative group">
                                            <video
                                              src={`http://127.0.0.1:8000/reports/${finding.video}`}
                                              className="w-full h-32 object-cover rounded border cursor-pointer hover:shadow-md transition-shadow"
                                              controls
                                              preload="metadata"
                                              onError={(e) => {
                                                console.error('Failed to load video:', finding.video);
                                                (e.target as HTMLVideoElement).style.display = 'none';
                                              }}
                                            />
                                            <div className="text-xs text-gray-500 mt-1 text-center">Video Recording</div>
                                          </div>
                                        )}
                                        
                                        {/* Base64 Screenshot (if embedded) */}
                                        {finding.screenshot_base64 && (
                                          <div className="relative group">
                                            <img
                                              src={`data:image/png;base64,${finding.screenshot_base64}`}
                                              alt={`Screenshot for ${finding.type || 'issue'}`}
                                              className="w-full h-32 object-cover rounded border cursor-pointer hover:shadow-md transition-shadow"
                                              onClick={() => {
                                                const newWindow = window.open();
                                                if (newWindow) {
                                                  newWindow.document.write(`
                                                    <html>
                                                      <head><title>Screenshot - ${finding.type || 'issue'}</title></head>
                                                      <body style="margin:0;background:#f0f0f0;display:flex;justify-content:center;align-items:center;min-height:100vh;">
                                                        <img src="data:image/png;base64,${finding.screenshot_base64}" style="max-width:100%;max-height:100%;box-shadow:0 4px 20px rgba(0,0,0,0.3);" />
                                                      </body>
                                                    </html>
                                                  `);
                                                }
                                              }}
                                            />
                                            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all flex items-center justify-center">
                                              <span className="text-white opacity-0 group-hover:opacity-100 text-xs font-medium">Click to enlarge</span>
                                            </div>
                                            <div className="text-xs text-gray-500 mt-1 text-center">Screenshot (Embedded)</div>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  )}
                                </div>
                                <div className="ml-4 text-right">
                                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(finding.severity || 'medium')}`}>
                                    {finding.severity || 'medium'}
                                  </span>
                                  {/* Only show Fix Now button if not already fixed */}
                                  {!finding.fixed && (
                                    <ModuleFixNowButton 
                                      finding={finding as ModuleFinding}
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
                        }).filter(Boolean)
                      )}
                    </div>

                    {/* Module Recommendations */}
                    {currentModule.recommendations && currentModule.recommendations.length > 0 && (
                      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <h4 className="font-medium text-blue-900 mb-2">Module Recommendations:</h4>
                        <ul className="text-sm text-blue-800 space-y-1">
                          {currentModule.recommendations.map((rec, index) => (
                            <li key={index} className="flex items-start">
                              <span className="mr-2">•</span>
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                );
              })()}
            </div>
          )}

          {/* Media Gallery Section */}
          {activeTab === 'overview' && report.has_screenshots && (
            <div className="mt-8">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
                    <Eye className="w-5 h-5 text-blue-600" />
                    Media Gallery
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Screenshots and videos captured during analysis
                  </p>
                </div>
                <div className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* Screenshots from scenario steps */}
                    {report.scenario_results?.map((scenario, scenarioIndex) => 
                      scenario.steps?.map((step, stepIndex) => 
                        step.screenshot && (
                          <div key={`${scenarioIndex}-${stepIndex}`} className="relative group">
                            <img
                              src={`http://127.0.0.1:8000/reports/${step.screenshot}`}
                              alt={`Step ${stepIndex + 1}: ${step.action}`}
                              className="w-full h-32 object-cover rounded border cursor-pointer hover:shadow-md transition-shadow"
                              onClick={() => window.open(`http://127.0.0.1:8000/reports/${step.screenshot}`, '_blank')}
                              onError={(e) => {
                                console.error('Failed to load screenshot:', step.screenshot);
                                (e.target as HTMLImageElement).style.display = 'none';
                              }}
                            />
                            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all flex items-center justify-center">
                              <span className="text-white opacity-0 group-hover:opacity-100 text-xs font-medium">Click to enlarge</span>
                            </div>
                            <div className="text-xs text-gray-500 mt-1 text-center">
                              Step {stepIndex + 1}: {step.action}
                            </div>
                          </div>
                        )
                      )
                    )}
                    
                    {/* Placeholder for additional media */}
                    {(!report.scenario_results || report.scenario_results.length === 0) && (
                      <div className="col-span-full text-center py-8 text-gray-500">
                        <Eye className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                        <p>No media captured during this analysis</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Legacy issues view */}
          {activeTab !== 'overview' && issuesByType[activeTab] && !report.modules.find(m => m.key === activeTab) && (
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
                          
                          {/* ADO Integration Status */}
                          <div className="mt-2">
                            <ADOStatus 
                              ado_work_item_id={issue.ado_work_item_id}
                              ado_status={issue.ado_status}
                              ado_url={issue.ado_url}
                              ado_created_date={issue.ado_created_date}
                            />
                          </div>
                          
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
      
      {/* Debug Section - Development Only */}
      {process.env.NODE_ENV === 'development' && report && (
        <div className="mt-8 bg-gray-50 rounded-lg p-4">
          <details open={debugMode}>
            <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
              🐛 Debug Information (Development)
            </summary>
            <div className="mt-4 space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Report Structure</h4>
                  <ul className="space-y-1 text-gray-600">
                    <li>Analysis ID: {report.analysis_id}</li>
                    <li>Status: {report.status}</li>
                    <li>Total Issues: {report.total_issues}</li>
                    <li>Overall Score: {report.overall_score || 'N/A'}</li>
                    <li>Modules Count: {report.modules?.length || 0}</li>
                    <li>URL: {report.url || 'N/A'}</li>
                    <li>Timestamp: {report.timestamp || 'N/A'}</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Module Breakdown</h4>
                  <ul className="space-y-1 text-gray-600">
                    {report.modules?.map((module, idx) => (
                      <li key={idx}>
                        {module.key}: {module.findings?.length || 0} issues 
                        {module.score && ` (Score: ${module.score})`}
                      </li>
                    )) || <li>No modules found</li>}
                  </ul>
                </div>
              </div>
              
              {debugMode && (
                <details>
                  <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                    📊 Raw JSON Data
                  </summary>
                  <pre className="mt-2 text-xs bg-white p-3 rounded border overflow-auto max-h-96">
                    {JSON.stringify(report, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          </details>
        </div>
      )}
    </div>
  );
}
