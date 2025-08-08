// React hooks for UX Analyzer API integration
// Provides state management and real-time updates

import { useState, useEffect, useCallback, useRef } from 'react';
import apiClient, { 
  AnalysisResponse, 
  AnalysisReport, 
  DashboardAnalytics, 
  DashboardAlert 
} from '../services/api';

// Custom hook for analysis workflow
export function useAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const startUrlAnalysis = useCallback(async (url: string, scenarioName?: string) => {
    try {
      setIsAnalyzing(true);
      setError(null);
      setProgress(10);

      const response = await apiClient.analyzeUrl(url, scenarioName);
      setCurrentAnalysis(response);
      setProgress(50);

      // Poll for completion
      if (response.status === 'started') {
        pollAnalysisStatus(response.analysis_id);
      }

      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setIsAnalyzing(false);
      throw err;
    }
  }, []);

  const startScreenshotAnalysis = useCallback(async (
    screenshot: File, 
    config: Record<string, any>
  ) => {
    try {
      setIsAnalyzing(true);
      setError(null);
      setProgress(10);

      const response = await apiClient.analyzeScreenshot(screenshot, config);
      setCurrentAnalysis(response);
      setProgress(50);

      if (response.status === 'started') {
        pollAnalysisStatus(response.analysis_id);
      }

      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Screenshot analysis failed');
      setIsAnalyzing(false);
      throw err;
    }
  }, []);

  const startScenarioAnalysis = useCallback(async (
    scenarioFile: File,
    url?: string
  ) => {
    try {
      setIsAnalyzing(true);
      setError(null);
      setProgress(10);

      const response = await apiClient.analyzeWithScenario(scenarioFile, url);
      setCurrentAnalysis(response);
      setProgress(response.status === 'completed' ? 100 : 50);

      if (response.status === 'started') {
        pollAnalysisStatus(response.analysis_id);
      }

      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scenario analysis failed');
      setIsAnalyzing(false);
      throw err;
    }
  }, []);

  const pollAnalysisStatus = useCallback(async (analysisId: string) => {
    const maxAttempts = 30; // 5 minutes max
    let attempts = 0;

    const poll = async () => {
      try {
        attempts++;
        const status = await apiClient.getAnalysisStatus(analysisId);
        
        setProgress(Math.min(50 + (attempts * 2), 90));

        if (status.status === 'completed') {
          setProgress(100);
          setIsAnalyzing(false);
          setCurrentAnalysis((prev: AnalysisResponse | null) => prev ? { ...prev, status: 'completed' } : null);
        } else if (status.status === 'failed') {
          setError(status.message || 'Analysis failed');
          setIsAnalyzing(false);
        } else if (attempts < maxAttempts) {
          setTimeout(poll, 10000); // Poll every 10 seconds
        } else {
          setError('Analysis timeout - please check server logs');
          setIsAnalyzing(false);
        }
      } catch (err) {
        if (attempts < maxAttempts) {
          setTimeout(poll, 10000);
        } else {
          setError('Failed to check analysis status');
          setIsAnalyzing(false);
        }
      }
    };

    setTimeout(poll, 5000); // Start polling after 5 seconds
  }, []);

  const resetAnalysis = useCallback(() => {
    setIsAnalyzing(false);
    setCurrentAnalysis(null);
    setError(null);
    setProgress(0);
  }, []);

  return {
    isAnalyzing,
    currentAnalysis,
    error,
    progress,
    startUrlAnalysis,
    startScreenshotAnalysis,
    startScenarioAnalysis,
    resetAnalysis,
  };
}

// Custom hook for reports management
export function useReports() {
  const [reports, setReports] = useState<AnalysisReport[]>([]);
  const [currentReport, setCurrentReport] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const reportsData = await apiClient.getAllReports();
      setReports(reportsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch reports');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchReport = useCallback(async (reportId: string) => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔍 Fetching report:', reportId);
      const report = await apiClient.getReport(reportId);
      console.log('✅ Report fetched successfully:', report);
      setCurrentReport(report);
      return report;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch report';
      console.error('❌ Error fetching report:', reportId, errorMessage, err);
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const searchReports = useCallback(async (query: {
    url_pattern?: string;
    date_from?: string;
    date_to?: string;
    min_issues?: number;
    max_issues?: number;
  }) => {
    try {
      setLoading(true);
      setError(null);
      const results = await apiClient.searchReports(query);
      setReports(results);
      return results;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const downloadReport = useCallback(async (reportId: string) => {
    try {
      const blob = await apiClient.downloadReport(reportId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ux-analysis-${reportId}.html`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed');
      throw err;
    }
  }, []);

  // Auto-fetch reports on mount
  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  return {
    reports,
    currentReport,
    loading,
    error,
    fetchReports,
    fetchReport,
    searchReports,
    downloadReport,
    setCurrentReport,
  };
}

// Custom hook for fix management
export function useFixManager() {
  const [fixingIssues, setFixingIssues] = useState<Set<string>>(new Set());
  const [fixResults, setFixResults] = useState<Map<string, any>>(new Map());
  const [error, setError] = useState<string | null>(null);

  const applyFix = useCallback(async (
    issueId: string,
    reportId: string,
    fixType: string
  ) => {
    try {
      setError(null);
      setFixingIssues(prev => new Set(prev).add(issueId));

      const result = await apiClient.applyFix(issueId, reportId, fixType);
      
      setFixResults(prev => new Map(prev).set(issueId, result));
      setFixingIssues(prev => {
        const newSet = new Set(prev);
        newSet.delete(issueId);
        return newSet;
      });

      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fix failed');
      setFixingIssues(prev => {
        const newSet = new Set(prev);
        newSet.delete(issueId);
        return newSet;
      });
      throw err;
    }
  }, []);

  const isFixing = useCallback((issueId: string) => {
    return fixingIssues.has(issueId);
  }, [fixingIssues]);

  const getFixResult = useCallback((issueId: string) => {
    return fixResults.get(issueId);
  }, [fixResults]);

  return {
    applyFix,
    isFixing,
    getFixResult,
    error,
  };
}

// Custom hook for dashboard analytics
export function useDashboard() {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [alerts, setAlerts] = useState<DashboardAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const intervalRef = useRef<NodeJS.Timeout>();

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [analyticsData, alertsData] = await Promise.all([
        apiClient.getDashboardAnalytics(),
        apiClient.getDashboardAlerts(),
      ]);
      
      setAnalytics(analyticsData);
      setAlerts(alertsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  const createADOTickets = useCallback(async (
    reportId: string,
    demoMode: boolean = true
  ) => {
    try {
      const result = await apiClient.createADOTickets(reportId, demoMode);
      // Refresh dashboard data after creating tickets
      await fetchDashboardData();
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create ADO tickets');
      throw err;
    }
  }, [fetchDashboardData]);

  // Auto-refresh functionality
  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, fetchDashboardData]);

  // Initial data fetch
  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const toggleAutoRefresh = useCallback(() => {
    setAutoRefresh(prev => !prev);
  }, []);

  return {
    analytics,
    alerts,
    loading,
    error,
    autoRefresh,
    fetchDashboardData,
    createADOTickets,
    toggleAutoRefresh,
  };
}

// Custom hook for real-time connection status
export function useConnectionStatus() {
  const [isConnected, setIsConnected] = useState(true);
  const [lastCheck, setLastCheck] = useState<Date>(new Date());
  const intervalRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    const checkConnection = async () => {
      try {
        await apiClient.healthCheck();
        setIsConnected(true);
        setLastCheck(new Date());
      } catch (err) {
        setIsConnected(false);
        setLastCheck(new Date());
      }
    };

    // Initial check
    checkConnection();

    // Check every 60 seconds
    intervalRef.current = setInterval(checkConnection, 60000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return { isConnected, lastCheck };
}
