import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { HomePage } from './pages/HomePage';
import { AnalysisPage } from './pages/AnalysisPage';
import { ReportPage } from './pages/ReportPage';
import { AnalysisLoadingPage } from './pages/AnalysisLoadingPage';
import { DashboardPage } from './pages/DashboardPage';
import { EnhancedDashboardPage } from './pages/EnhancedDashboardPage';
import { AdoDashboardPage } from './pages/AdoDashboardPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/analyze" element={<AnalysisPage />} />
            <Route path="/analysis/:analysisId" element={<AnalysisLoadingPage />} />
            <Route path="/report/:reportId" element={<ReportPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/dashboard/enhanced" element={<EnhancedDashboardPage />} />
            <Route path="/dashboard/ado" element={<AdoDashboardPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
