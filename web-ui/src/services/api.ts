// web-ui/src/services/api.ts
const BASE_URL = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

type ModulesPayload = {
  performance: boolean;
  accessibility: boolean;
  keyboard: boolean;
  ux_heuristics: boolean;
  best_practices: boolean;
  health_alerts: boolean;
  functional: boolean;
};

export type ScenarioDTO = {
  id: string;
  name: string;
  description?: string;
  category?: string;
  app_type: 'web' | 'word' | 'excel' | 'powerpoint';
  source?: string;
  filename?: string;
  path: string;
  mock_url?: string | null;
};

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export const apiClient = {
  async getScenarios(app?: string): Promise<ScenarioDTO[]> {
    const res = await fetch(`${BASE_URL}/api/scenarios`, { method: 'GET' });
    const data = await json<{ scenarios: ScenarioDTO[] }>(res);
    const allScenarios = data.scenarios ?? [];
    
    // Filter by app type on frontend since backend returns all scenarios
    if (app) {
      return allScenarios.filter(scenario => scenario.app_type === app);
    }
    
    return allScenarios;
  },

  async getModules(): Promise<
    { key: string; name: string; description: string; enabled: boolean }[]
  > {
    const res = await fetch(`${BASE_URL}/api/modules`);
    const data = await json<{ modules: any[] }>(res);
    return data.modules ?? [];
  },

  // MOCK: URL + Scenario - use main analyze endpoint
  async startUrlScenario(url: string, scenario_id: string, modules: ModulesPayload) {
    const res = await fetch(`${BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, scenario_id, use_real_browser: false }),
    });
    return json<{ analysis_id: string; status: string; message: string }>(res);
  },

  // MOCK: MockApp + Scenario - use main analyze endpoint with mock URL
  async startMockScenario(app_path: string, scenario_id: string, modules: ModulesPayload) {
    // Convert app_path to mock URL
    const mockUrls: Record<string, string> = {
      'word': 'http://127.0.0.1:8080/mocks/word/basic-doc.html',
      'excel': 'http://127.0.0.1:8080/mocks/excel/open-format.html', 
      'powerpoint': 'http://127.0.0.1:8080/mocks/powerpoint/basic-deck.html'
    };
    const url = mockUrls[app_path] || `http://127.0.0.1:8080/mocks/${app_path}`;
    
    const res = await fetch(`${BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, scenario_id, use_real_browser: false }),
    });
    return json<{ analysis_id: string; status: string; message: string }>(res);
  },

  // REAL: Playwright
  async startEnhanced(url: string, scenario_path: string, modules: ModulesPayload, headless = true) {
    const res = await fetch(`${BASE_URL}/api/analyze/enhanced`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url,
        scenario_path,
        modules,
        execution_mode: 'realistic',
        headless,
      }),
    });
    return json<{ analysis_id: string; status: string; message: string; execution_mode: string }>(res);
  },

  // EXCEL: Scenario with UX Telemetry
  async startExcelScenario(scenario_id: string) {
    const res = await fetch(`${BASE_URL}/api/analyze/excel-scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario_id,
      }),
    });
    return json<{ 
      status: string; 
      analysis_id: string; 
      telemetry: any; 
      ux_analysis: any; 
      message: string 
    }>(res);
  },

  async getReport(id: string) {
    const res = await fetch(`${BASE_URL}/api/reports/${id}`);
    return json<any>(res);
  },

  async getAnalysisStatus(id: string) {
    const res = await fetch(`${BASE_URL}/api/analysis/${id}/status`);
    return json<any>(res);
  },

  async downloadReport(id: string): Promise<Blob> {
    const res = await fetch(`${BASE_URL}/api/reports/${id}/download`);
    if (!res.ok) throw new Error(`Download failed: ${res.statusText}`);
    return res.blob();
  },
};

// Export additional types for compatibility
export interface AnalysisResponse {
  analysis_id: string;
  status: string;
  message: string;
}

export interface AnalysisReport {
  analysis_id: string;
  timestamp: string;
  status?: string;
  scenario_results?: any[];
  module_results?: Record<string, any>;
  total_issues?: number;
}

export interface UXIssue {
  issue_id: string;
  type: string;
  severity: string;
  title: string;
  description: string;
  location?: string;
  suggestions?: string[];
  fix_applied?: boolean;
  fix_timestamp?: string;
  ado_work_item_id?: string;
  ado_status?: string;
  ado_url?: string;
  ado_created_date?: string;
}

export interface DashboardAnalytics {
  total_analyses: number;
  total_issues: number;
  issue_type_distribution: Record<string, number>;
}

export interface DashboardAlert {
  alert_id: string;
  type: string;
  severity: string;
  message: string;
}
