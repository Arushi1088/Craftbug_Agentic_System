// API Service Layer for UX Analyzer Frontend
// Handles all communication with FastAPI backend

const API_BASE_URL = 'http://127.0.0.1:8000';

// Types for API responses
export interface AnalysisResponse {
  analysis_id: string;
  status: 'started' | 'completed' | 'failed';
  message: string;
  estimated_duration_minutes?: number;
}

export interface UXIssue {
  issue_id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  location?: string;
  suggestions?: string[];
  status?: string;
  fix_applied?: boolean;
  fix_timestamp?: string;
  fix_suggestions?: string[];
  // Azure DevOps integration metadata
  ado_work_item_id?: string;
  ado_status?: string;
  ado_url?: string;
  ado_created_date?: string;
}

export interface AnalysisReport {
  report_id?: string;
  analysis_id: string;
  url?: string;
  timestamp: string;
  status?: string;
  app_type?: string;
  type?: string;
  scenario_file?: string;
  overall_score?: number;
  has_screenshots?: boolean;  // New field for screenshot support
  
  // Real backend format fields
  scenario_results?: Array<{
    name: string;
    score: number;
    status: string;
    duration_ms: number;
    steps: Array<{
      action: string;
      status: string;
      duration_ms: number;
      analytics?: any[];
      violations?: number;
      scope?: string;
      selector?: string;
      url?: string;
      screenshot?: string;  // New field for step screenshots
      errors?: string[];
    }>;
  }>;
  
  module_results?: Record<string, {
    score: number;
    threshold_met: boolean;
    analytics_enabled: boolean;
    findings: Array<{
      type: string;
      message: string;
      severity: string;
      element?: string;
      recommendation: string;
    }>;
    recommendations: string[];
  }>;
  
  metadata?: {
    total_scenarios: number;
    total_steps: number;
    analysis_duration: number;
    scenarios_passed: number;
    analytics_features: any[];
    deterministic_mode: boolean;
  };
  
  // Legacy fields for backward compatibility
  total_issues?: number;
  ai_analysis_enabled?: boolean;
  ux_issues?: UXIssue[];
  performance_metrics?: {
    load_time: number;
    page_size: number;
    requests: number;
  };
  accessibility_score?: number;
  usability_score?: number;
}

export interface DashboardAnalytics {
  total_analyses: number;
  total_issues: number;
  avg_issues_per_analysis: number;
  most_common_issue_type: string;
  issue_severity_distribution: Record<string, number>;
  issue_type_distribution: Record<string, number>;
  recent_analyses: Array<{
    analysis_id: string;
    timestamp: string;
    url: string;
    total_issues: number;
  }>;
  trending_issues: Array<{
    type: string;
    count: number;
    trend: 'up' | 'down' | 'stable';
  }>;
}

export interface DashboardAlert {
  alert_id: string;
  type: 'critical_issue' | 'performance_degradation' | 'accessibility_violation';
  severity: 'high' | 'medium' | 'low';
  message: string;
  timestamp: string;
  analysis_id?: string;
  acknowledged: boolean;
}

export interface ReportSummary {
  summary: {
    total_reports: number;
    total_issues: number;
    total_fixed: number;
    avg_fix_rate: number;
  };
  reports: Array<{
    analysis_id: string;
    report_name: string;
    timestamp: string;
    total_issues: number;
    fixed_issues: number;
    fix_rate: number;
    app_type: string;
    task_type: string;
    modules: string[];
    ado_integration: {
      work_items_created: number;
      last_sync_date?: string;
      sync_status: string;
    };
  }>;
  filters: {
    app_types: string[];
    task_types: string[];
    modules: string[];
  };
}

// API Client Class
class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  private async requestFormData<T>(
    endpoint: string,
    formData: FormData
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // Analysis API Methods
  async analyzeUrl(url: string, scenarioName?: string): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('url', url);
    if (scenarioName) {
      formData.append('scenario_name', scenarioName);
    }

    return this.requestFormData<AnalysisResponse>('/api/analyze/url', formData);
  }

  async analyzeScreenshot(
    screenshot: File, 
    config: Record<string, any>
  ): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('screenshot', screenshot);
    formData.append('config', JSON.stringify(config));

    return this.requestFormData<AnalysisResponse>('/api/analyze/screenshot', formData);
  }

  async analyzeWithScenario(
    scenarioFile: File,
    url?: string
  ): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('scenario_file', scenarioFile);
    if (url) {
      formData.append('url', url);
    }

    return this.requestFormData<AnalysisResponse>('/api/analyze/scenario', formData);
  }

  async getAnalysisStatus(analysisId: string): Promise<{ status: string; message?: string }> {
    return this.request<{ status: string; message?: string }>(`/api/analysis/${analysisId}/status`);
  }

  // Reports API Methods
  async getReport(reportId: string): Promise<AnalysisReport> {
    return this.request<AnalysisReport>(`/api/reports/${reportId}`);
  }

  async getAllReports(): Promise<AnalysisReport[]> {
    return this.request<AnalysisReport[]>('/api/reports');
  }

  async getReportsSummary(): Promise<ReportSummary> {
    return this.request<ReportSummary>('/api/reports/summary');
  }

  async getReportStatistics(): Promise<{
    total_reports: number;
    total_issues: number;
    avg_issues_per_report: number;
    most_common_issue_type: string;
  }> {
    return this.request('/api/reports/statistics');
  }

  async downloadReport(reportId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/reports/${reportId}/download`);
    if (!response.ok) {
      throw new Error(`Download failed: ${response.statusText}`);
    }
    return response.blob();
  }

  async searchReports(query: {
    url_pattern?: string;
    date_from?: string;
    date_to?: string;
    min_issues?: number;
    max_issues?: number;
  }): Promise<AnalysisReport[]> {
    return this.request<AnalysisReport[]>('/api/reports/search', {
      method: 'POST',
      body: JSON.stringify(query),
    });
  }

  // Fix Now API Methods
  async applyFix(
    issueId: string,
    reportId: string,
    fixType: string
  ): Promise<{
    status: string;
    message: string;
    fix_suggestions: string[];
    issue_status: string;
  }> {
    const formData = new FormData();
    formData.append('issue_id', issueId);
    formData.append('report_id', reportId);
    formData.append('fix_type', fixType);

    return this.requestFormData('/api/fix-now', formData);
  }

  // Dashboard API Methods
  async getDashboardAnalytics(): Promise<DashboardAnalytics> {
    return this.request<DashboardAnalytics>('/api/dashboard/analytics');
  }

  async getDashboardAlerts(): Promise<DashboardAlert[]> {
    return this.request<DashboardAlert[]>('/api/dashboard/alerts');
  }

  async processAnalysisResults(reportData: any): Promise<{ status: string; message: string }> {
    return this.request('/api/dashboard/process-results', {
      method: 'POST',
      body: JSON.stringify({ report_data: reportData }),
    });
  }

  async createADOTickets(
    reportId: string,
    demoMode: boolean = true
  ): Promise<{
    status: string;
    work_items_created: number;
    work_items: any[];
    demo_mode: boolean;
  }> {
    const formData = new FormData();
    formData.append('report_id', reportId);
    formData.append('demo_mode', demoMode.toString());

    return this.requestFormData('/api/dashboard/create-ado-tickets', formData);
  }

  // Utility Methods
  async getScenarios(): Promise<Array<{
    filename: string;
    path: string;
    name: string;
    description: string;
  }>> {
    const response = await this.request<{
      scenarios: Array<{
        filename: string;
        path: string;
        name: string;
        description: string;
      }>
    }>('/api/scenarios');
    return response.scenarios;
  }

  async getModules(): Promise<Array<{
    key: string;
    name: string;
    description: string;
    enabled: boolean;
  }>> {
    const response = await this.request<{
      modules: Array<{
        key: string;
        name: string;
        description: string;
        enabled: boolean;
      }>
    }>('/api/modules');
    return response.modules;
  }

  async getStatistics(): Promise<Record<string, any>> {
    return this.request<Record<string, any>>('/api/statistics');
  }

  async cleanup(maxAge: number = 24): Promise<{ message: string; deleted_reports: number }> {
    const formData = new FormData();
    formData.append('max_age_hours', maxAge.toString());

    return this.requestFormData('/api/reports/cleanup', formData);
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/`);
      if (response.ok) {
        return { status: 'healthy', timestamp: new Date().toISOString() };
      } else {
        throw new Error('Server not responding');
      }
    } catch (error) {
      throw new Error(`Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}

// Create singleton instance
export const apiClient = new APIClient();

// Export API client and types
export default apiClient;
export type { APIClient };
