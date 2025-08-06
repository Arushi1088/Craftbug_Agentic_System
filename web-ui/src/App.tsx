import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { HomePage } from './pages/HomePage';
import { AnalysisPage } from './pages/AnalysisPage';
import { EnhancedReportPage } from './pages/EnhancedReportPage';
import { AnalysisLoadingPage } from './pages/AnalysisLoadingPage';

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
            <Route path="/report/:reportId" element={<EnhancedReportPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
