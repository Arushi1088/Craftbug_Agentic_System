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
    const url = new URL('/api/scenarios', BASE_URL);
    if (app) url.searchParams.set('app', app);
    const res = await fetch(url.toString(), { method: 'GET' });
    const data = await json<{ scenarios: ScenarioDTO[] }>(res);
    return data.scenarios ?? [];
  },

  async getModules(): Promise<
    { key: string; name: string; description: string; enabled: boolean }[]
  > {
    const res = await fetch(`${BASE_URL}/api/modules`);
    const data = await json<{ modules: any[] }>(res);
    return data.modules ?? [];
  },

  // MOCK: URL + Scenario
  async startUrlScenario(url: string, scenario_path: string, modules: ModulesPayload) {
    const res = await fetch(`${BASE_URL}/api/analyze/url-scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, scenario_path, modules }),
    });
    return json<{ analysis_id: string; status: string; message: string }>(res);
  },

  // MOCK: MockApp + Scenario (use app id: 'word'|'excel'|'powerpoint')
  async startMockScenario(app_path: string, scenario_path: string, modules: ModulesPayload) {
    const res = await fetch(`${BASE_URL}/api/analyze/mock-scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ app_path, scenario_path, modules }),
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

  async getReport(id: string) {
    const res = await fetch(`${BASE_URL}/api/reports/${id}`);
    return json<any>(res);
  },

  async getAnalysisStatus(id: string) {
    const res = await fetch(`${BASE_URL}/api/analysis/${id}/status`);
    return json<any>(res);
  },
};
