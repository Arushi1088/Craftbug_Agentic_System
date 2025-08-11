// web-ui/src/hooks/useAPI.ts
import { useCallback, useRef, useState } from 'react';
import { apiClient } from '../services/api';

export function useConnectionStatus() {
  // Optional: you can ping /health or rely on fetch successes
  return { isConnected: true };
}

export function useAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentAnalysis, setCurrentAnalysis] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const resetAnalysis = useCallback(() => {
    setIsAnalyzing(false);
    setProgress(0);
    setCurrentAnalysis(null);
    setError(null);
    if (timerRef.current) window.clearInterval(timerRef.current);
    timerRef.current = null;
  }, []);

  const modulesFromConfig = (c: any) => ({
    performance: !!c.enablePerformance,
    accessibility: !!c.enableAccessibility,
    keyboard: !!c.enableKeyboard,
    ux_heuristics: !!c.enableUxHeuristics,
    best_practices: !!c.enableBestPractices,
    health_alerts: !!c.enableHealthAlerts,
    functional: !!c.enableFunctional,
  });

  const startProgress = () => {
    setProgress(5);
    timerRef.current = window.setInterval(() => {
      setProgress((p) => (p < 90 ? p + 3 : p));
    }, 400) as unknown as number;
  };

  const finishProgress = () => {
    if (timerRef.current) window.clearInterval(timerRef.current);
    timerRef.current = null;
    setProgress(100);
  };

  const startUrlScenario = useCallback(async (url: string, scenario_id: string, config: any) => {
    try {
      setError(null);
      setIsAnalyzing(true);
      startProgress();

      const modules = modulesFromConfig(config);
      const resp = await apiClient.startUrlScenario(url, scenario_id, modules);
      finishProgress();
      setCurrentAnalysis({ ...resp, message: resp.message ?? 'Analysis started' });
    } catch (e: any) {
      setError(e?.message || 'Failed to start analysis');
      setIsAnalyzing(false);
    }
  }, []);

  const startMockScenario = useCallback(async (app_path: string, scenario_id: string, config: any) => {
    try {
      setError(null);
      setIsAnalyzing(true);
      startProgress();

      const modules = modulesFromConfig(config);
      const resp = await apiClient.startMockScenario(app_path, scenario_id, modules);
      finishProgress();
      setCurrentAnalysis({ ...resp, message: resp.message ?? 'Analysis started' });
      return resp; // Return the response so it can be used in components
    } catch (e: any) {
      setError(e?.message || 'Failed to start analysis');
      setIsAnalyzing(false);
      throw e; // Re-throw so components can handle the error
    }
  }, []);

  const startEnhanced = useCallback(async (url: string, scenario_path: string, config: any, headless = true) => {
    try {
      setError(null);
      setIsAnalyzing(true);
      startProgress();

      const modules = modulesFromConfig(config);
      const resp = await apiClient.startEnhanced(url, scenario_path, modules, headless);
      // realistic mode may keep processing in background; we just show the start status
      finishProgress();
      setCurrentAnalysis({ ...resp, message: resp.message ?? 'Realistic analysis started' });
    } catch (e: any) {
      setError(e?.message || 'Failed to start enhanced analysis');
      setIsAnalyzing(false);
    }
  }, []);

  return {
    isAnalyzing,
    progress,
    currentAnalysis,
    error,
    resetAnalysis,
    startUrlScenario,
    startMockScenario,
    startEnhanced,
  };
}

// Additional hooks for compatibility
export function useReports() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const fetchReports = useCallback(async () => {
    setLoading(true);
    try {
      setReports([]);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchReport = useCallback(async (id: string) => {
    setLoading(true);
    try {
      return await apiClient.getReport(id);
    } catch (e: any) {
      setError(e.message);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  const downloadReport = useCallback(async (id: string) => {
    return await apiClient.downloadReport(id);
  }, []);

  return { reports, loading, error, fetchReports, fetchReport, downloadReport };
}

export function useDashboard() {
  return {
    analytics: null,
    alerts: [],
    loading: false,
    error: null,
    autoRefresh: false,
    fetchDashboardData: async () => {},
    createADOTickets: async () => {},
    toggleAutoRefresh: () => {},
  };
}

export function useFixManager() {
  const [isApplying, setIsApplying] = useState(false);
  
  const applyFix = useCallback(async (issueId: string, reportId: string, fixType: string) => {
    setIsApplying(true);
    try {
      // Implementation would go here
    } finally {
      setIsApplying(false);
    }
  }, []);

  return {
    applyFix,
    isApplying,
    isFixing: isApplying,
    getFixResult: () => null,
  };
}
