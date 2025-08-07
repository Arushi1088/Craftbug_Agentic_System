import { useMemo } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  AlertTriangle,
  CheckCircle,
  BarChart3
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts';

interface ReportSummary {
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

interface DashboardSummaryProps {
  summary: ReportSummary | null;
  loading: boolean;
}

const COLORS = {
  primary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#6366f1',
  gray: '#6b7280'
};

export function DashboardSummary({ summary, loading }: DashboardSummaryProps) {
  // Calculate trend data for charts
  const trendData = useMemo(() => {
    if (!summary?.reports) return [];
    
    return summary.reports
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .map(report => ({
        date: new Date(report.timestamp).toLocaleDateString(),
        issues: report.total_issues,
        fixed: report.fixed_issues,
        fixRate: report.fix_rate
      }));
  }, [summary]);

  // Calculate module distribution
  const moduleData = useMemo(() => {
    if (!summary?.reports) return [];
    
    const moduleCount: Record<string, number> = {};
    summary.reports.forEach(report => {
      report.modules.forEach(module => {
        moduleCount[module] = (moduleCount[module] || 0) + 1;
      });
    });

    return Object.entries(moduleCount)
      .map(([module, count]) => ({
        name: module.charAt(0).toUpperCase() + module.slice(1),
        value: count
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5); // Top 5 modules
  }, [summary]);

  // Calculate key metrics
  const metrics = useMemo(() => {
    if (!summary) return null;

    const recentReports = summary.reports.slice(-7); // Last 7 reports
    const previousReports = summary.reports.slice(-14, -7); // Previous 7 reports

    const recentIssues = recentReports.reduce((sum, r) => sum + r.total_issues, 0);
    const previousIssues = previousReports.reduce((sum, r) => sum + r.total_issues, 0);
    const issuesTrend = previousIssues > 0 ? ((recentIssues - previousIssues) / previousIssues * 100) : 0;

    const recentFixed = recentReports.reduce((sum, r) => sum + r.fixed_issues, 0);
    const previousFixed = previousReports.reduce((sum, r) => sum + r.fixed_issues, 0);
    const fixedTrend = previousFixed > 0 ? ((recentFixed - previousFixed) / previousFixed * 100) : 0;

    const recentFixRate = recentIssues > 0 ? (recentFixed / recentIssues * 100) : 0;
    const previousFixRate = previousIssues > 0 ? (previousFixed / previousIssues * 100) : 0;
    const fixRateTrend = recentFixRate - previousFixRate;

    return {
      totalReports: summary.summary.total_reports,
      totalIssues: summary.summary.total_issues,
      overallFixRate: summary.summary.avg_fix_rate,
      issuesTrend,
      fixedTrend,
      fixRateTrend,
      recentReports: recentReports.length,
      avgIssuesPerReport: summary.summary.total_reports > 0 ? Math.round(summary.summary.total_issues / summary.summary.total_reports) : 0
    };
  }, [summary]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/3"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!summary || !metrics) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Data Available</h3>
        <p className="text-gray-500">Run an analysis to see dashboard metrics.</p>
      </div>
    );
  }

  // Status distribution for pie chart
  const statusData = [
    { name: 'Open', value: summary.summary.total_issues - summary.summary.total_fixed, color: COLORS.danger },
    { name: 'Fixed', value: summary.summary.total_fixed, color: COLORS.success },
    { name: 'Ignored', value: Math.round(summary.summary.total_issues * 0.1), color: COLORS.gray } // Mock ignored issues
  ];

  return (
    <div className="space-y-6">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Issues */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Issues</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.totalIssues}</p>
              <div className="flex items-center mt-1">
                {metrics.issuesTrend >= 0 ? (
                  <TrendingUp className="w-4 h-4 text-red-500 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-green-500 mr-1" />
                )}
                <span className={`text-sm ${metrics.issuesTrend >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {Math.abs(metrics.issuesTrend).toFixed(1)}%
                </span>
                <span className="text-xs text-gray-500 ml-1">vs last week</span>
              </div>
            </div>
            <div className="p-3 bg-red-100 rounded-full">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        {/* Fix Rate */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Fix Rate</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.overallFixRate.toFixed(1)}%</p>
              <div className="flex items-center mt-1">
                {metrics.fixRateTrend >= 0 ? (
                  <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
                )}
                <span className={`text-sm ${metrics.fixRateTrend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {Math.abs(metrics.fixRateTrend).toFixed(1)}%
                </span>
                <span className="text-xs text-gray-500 ml-1">vs last week</span>
              </div>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        {/* Total Reports */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Reports</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.totalReports}</p>
              <p className="text-sm text-gray-500 mt-1">
                {metrics.avgIssuesPerReport} avg issues/report
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Recent Reports</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.recentReports}</p>
              <p className="text-sm text-gray-500 mt-1">Last 7 days</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Issue Trend Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Issue Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area 
                type="monotone" 
                dataKey="issues" 
                stackId="1"
                stroke={COLORS.danger} 
                fill={COLORS.danger}
                fillOpacity={0.6}
                name="Issues Found"
              />
              <Area 
                type="monotone" 
                dataKey="fixed" 
                stackId="2"
                stroke={COLORS.success} 
                fill={COLORS.success}
                fillOpacity={0.6}
                name="Issues Fixed"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Status Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Issue Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({name, percent}) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Module Analysis */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Modules by Issue Count</h3>
        <div className="space-y-4">
          {moduleData.map((module, index) => (
            <div key={module.name} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold text-blue-600">{index + 1}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{module.name}</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${(module.value / moduleData[0].value) * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm text-gray-600 w-8 text-right">{module.value}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Fix Rate Trend */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Fix Rate Trend</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={[0, 100]} />
            <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Fix Rate']} />
            <Line 
              type="monotone" 
              dataKey="fixRate" 
              stroke={COLORS.success} 
              strokeWidth={3}
              dot={{ fill: COLORS.success, strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
