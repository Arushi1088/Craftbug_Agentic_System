import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, Clock, CheckCircle, AlertCircle } from 'lucide-react';

interface AnalysisStatus {
  analysis_id: string;
  status: 'processing' | 'completed' | 'failed';
  message: string;
  estimated_completion?: string;
  progress?: number;
}

export function AnalysisLoadingPage() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) {
      navigate('/');
      return;
    }

    pollAnalysisStatus();
  }, [analysisId]);

  const pollAnalysisStatus = async () => {
    try {
      // Start with initial status
      setProgress(25);
      setStatus({
        analysis_id: analysisId!,
        status: 'processing',
        message: 'Starting analysis...',
        progress: 25
      });
      
      // Small delay to show the loading state
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Try to fetch the completed report immediately for mock data
      try {
        const reportResponse = await fetch(`/api/reports/${analysisId}`);
        
        if (reportResponse.ok) {
          // Report is ready!
          setProgress(100);
          setStatus({
            analysis_id: analysisId!,
            status: 'completed',
            message: 'Analysis completed successfully!',
            progress: 100
          });
          
          // Redirect to report page after showing success
          setTimeout(() => {
            navigate(`/report/${analysisId}`);
          }, 1000);
          return;
        }
      } catch (err) {
        console.error('Initial report fetch error:', err);
      }
      
      // If initial fetch fails, start polling
      const pollInterval = setInterval(async () => {
        try {
          const reportResponse = await fetch(`/api/reports/${analysisId}`);
          
          if (reportResponse.ok) {
            // Report is ready!
            clearInterval(pollInterval);
            setProgress(100);
            setStatus({
              analysis_id: analysisId!,
              status: 'completed',
              message: 'Analysis completed successfully!',
              progress: 100
            });
            
            // Redirect to report page after a brief success message
            setTimeout(() => {
              navigate(`/report/${analysisId}`);
            }, 1000);
            return;
          }
          
          // If report not found, continue polling with visual progress
          setProgress(prev => Math.min(prev + 10, 90));
          setStatus(prev => ({
            analysis_id: analysisId!,
            status: 'processing',
            message: 'Analyzing your content... Please wait.',
            progress: Math.min((prev?.progress || 0) + 10, 90)
          }));
          
        } catch (err) {
          console.error('Polling error:', err);
          // Continue polling on network errors
        }
      }, 3000);

      // Timeout after 30 seconds for mock data
      setTimeout(() => {
        clearInterval(pollInterval);
        if (status?.status === 'processing') {
          setError('Analysis is taking longer than expected. Please try again.');
          setStatus({
            analysis_id: analysisId!,
            status: 'failed',
            message: 'Analysis timeout',
          });
        }
      }, 30000);

    } catch (err) {
      setError('Failed to start analysis polling');
      console.error('Analysis polling error:', err);
    }
  };

  const getStatusIcon = () => {
    if (error || status?.status === 'failed') {
      return <AlertCircle className="w-8 h-8 text-red-500" />;
    }
    if (status?.status === 'completed') {
      return <CheckCircle className="w-8 h-8 text-green-500" />;
    }
    return <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />;
  };

  const getProgressColor = () => {
    if (error || status?.status === 'failed') return 'bg-red-500';
    if (status?.status === 'completed') return 'bg-green-500';
    return 'bg-blue-500';
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="mb-6">
          {getStatusIcon()}
        </div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          {error ? 'Analysis Failed' : 
           status?.status === 'completed' ? 'Analysis Complete!' :
           'Analyzing Your Content'}
        </h1>
        
        <p className="text-gray-600 mb-6">
          {error || status?.message || 'Preparing your UX analysis...'}
        </p>
        
        {!error && (
          <div className="mb-6">
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div 
                className={`h-2 rounded-full transition-all duration-500 ${getProgressColor()}`}
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500">{progress}% complete</p>
          </div>
        )}
        
        <div className="flex items-center justify-center text-sm text-gray-500 mb-4">
          <Clock className="w-4 h-4 mr-2" />
          <span>Analysis ID: {analysisId}</span>
        </div>
        
        {error && (
          <div className="space-y-3">
            <button
              onClick={() => window.location.reload()}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200"
            >
              Try Again
            </button>
            <button
              onClick={() => navigate('/')}
              className="w-full bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400 transition duration-200"
            >
              Start New Analysis
            </button>
          </div>
        )}
        
        {status?.status === 'processing' && (
          <div className="text-xs text-gray-400 mt-4">
            <p>Your analysis is being processed...</p>
            <p>This page will automatically redirect when complete.</p>
          </div>
        )}
      </div>
    </div>
  );
}
