import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, Settings, Play, Upload, Video, FileVideo } from 'lucide-react';
import { useAnalysis } from '../hooks/useAPI';
import { apiClient } from '../services/api';

type AnalysisConfig = {
  app: string;
  scenarioFile: string;
  mode: 'mock-scenario' | 'video-upload';
  enablePerformance: boolean;
  enableAccessibility: boolean;
  enableKeyboard: boolean;
  enableUxHeuristics: boolean;
  enableBestPractices: boolean;
  enableHealthAlerts: boolean;
  enableFunctional: boolean;
  videoFile?: File;
  frameInterval?: number;
  // Mobile-specific parameters
  surface?: string;
  platform?: string;
  openPath?: string;
  fileSize?: string;
  protection?: string;
  accountState?: string;
};

interface ScenarioDTO {
  id: string;
  name: string;
  description?: string;
  app_type: string;
}

export function AnalysisPage() {
  const navigate = useNavigate();
  const { isAnalyzing, currentAnalysis, error, progress, startMockScenario, startVideoAnalysis, resetAnalysis } = useAnalysis();
  
  const [selectedApp, setSelectedApp] = useState<string>('');
  const [scenarios, setScenarios] = useState<ScenarioDTO[]>([]);
  const [loading, setLoading] = useState(false);
  const [analysisMode, setAnalysisMode] = useState<'scenario' | 'video'>('scenario');
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  
  const [config, setConfig] = useState<AnalysisConfig>({
    app: '',
    scenarioFile: '',
    mode: 'mock-scenario',
    enablePerformance: true,
    enableAccessibility: true,
    enableKeyboard: true,
    enableUxHeuristics: true,
    enableBestPractices: true,
    enableHealthAlerts: true,
    enableFunctional: true,
    frameInterval: 2, // Extract frame every 2 seconds
    // Mobile-specific defaults
    surface: 'Outlook Mobile',
    platform: 'Android',
    openPath: 'link',
    fileSize: 'large',
    protection: 'password',
    accountState: 'work_profile',
  });

  const loadScenarios = useCallback(async (appType: string) => {
    if (!appType) return;
    
    setLoading(true);
    try {
      console.log(`🔍 Loading scenarios for app: ${appType}`);
      const data = await apiClient.getScenarios();
      const filtered = data?.filter((s: ScenarioDTO) => s.app_type === appType) || [];
      console.log(`✅ Found ${filtered.length} scenarios for ${appType}:`, filtered);
      setScenarios(filtered);
    } catch (error) {
      console.error('❌ Failed to load scenarios:', error);
      setScenarios([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleVideoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate video file type
    const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime', 'video/webm'];
    if (!validTypes.includes(file.type)) {
      alert('Please upload a valid video file (MP4, AVI, MOV, WebM)');
      return;
    }

    // Validate file size (max 100MB)
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      alert('Video file size must be less than 100MB');
      return;
    }

    console.log('📹 Video file selected:', file.name, file.size, file.type);
    
    // Create preview URL
    const previewUrl = URL.createObjectURL(file);
    setVideoPreview(previewUrl);
    
    // Update config
    setConfig(prev => ({
      ...prev,
      videoFile: file,
      mode: 'video-upload'
    }));
  };

  const handleAnalysisModeChange = (mode: 'scenario' | 'video') => {
    setAnalysisMode(mode);
    if (mode === 'video') {
      setConfig(prev => ({ ...prev, mode: 'video-upload' }));
    } else {
      setConfig(prev => ({ ...prev, mode: 'mock-scenario' }));
      // Clear video data
      if (videoPreview) {
        URL.revokeObjectURL(videoPreview);
        setVideoPreview(null);
      }
      setConfig(prev => ({ ...prev, videoFile: undefined }));
    }
  };

  const handleAppSelection = (app: string) => {
    console.log(`📱 App selected: ${app}`);
    setSelectedApp(app);
    
    // Update config and reset scenario selection
    setConfig(prev => {
      const next: AnalysisConfig = { ...prev, app: selectedApp, scenarioFile: '' };
      console.log('🔧 Updated config:', next);
      return next;
    });
    
    // Load scenarios for the selected app
    loadScenarios(app);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (analysisMode === 'video') {
      if (!config.videoFile) {
        console.warn('⚠️ No video file selected');
        return;
      }
      console.log('🚀 Starting video analysis with config:', { config });
      
      try {
        const formData = new FormData();
        formData.append('video_file', config.videoFile!);
        formData.append('frame_interval', config.frameInterval?.toString() || '2');
        // Add mobile-specific parameters
        formData.append('surface', config.surface || 'Outlook Mobile');
        formData.append('platform', config.platform || 'Android');
        formData.append('open_path', config.openPath || 'link');
        formData.append('file_size', config.fileSize || 'large');
        formData.append('protection', config.protection || 'password');
        formData.append('account_state', config.accountState || 'work_profile');
        
        // Add enhanced mobile matrix parameters
        formData.append('mode', 'mobile');
        formData.append('device', config.device || 'iPhone');
        formData.append('hub_entry', config.hubEntry || 'message_detail');
        formData.append('source', config.source || 'Attachment');
        formData.append('file_ext', config.fileExt || 'xlsx');
        formData.append('apps_installed', config.appsInstalled || 'None');
        formData.append('host_account', config.hostAccount || 'Primary');
        formData.append('app_account', config.appAccount || 'Primary');
        
        console.log('📹 Uploading video for mobile analysis...', {
          surface: config.surface,
          platform: config.platform,
          openPath: config.openPath,
          fileSize: config.fileSize,
          protection: config.protection,
          accountState: config.accountState
        });
        const result = await startVideoAnalysis(formData);
        console.log('✅ Video analysis completed:', result);
        
        // Check if LLM analysis was successful
        if (result.llm_analysis) {
          console.log('🎯 LLM analysis results:', result.llm_analysis);
          
          // Navigate to the report page
          if (result.analysis_id) {
            console.log('📊 Navigating to report:', result.analysis_id);
            navigate(`/reports/${result.analysis_id}`);
          } else {
            alert(`Video analysis completed! Found ${result.llm_analysis.bugs_strong?.length || 0} major issues and ${result.llm_analysis.bugs_minor?.length || 0} minor issues across ${result.extracted_frames?.length || 0} frames.`);
          }
        } else {
          alert(`Video analysis completed! Extracted ${result.extracted_frames?.length || 0} frames. LLM analysis: ${result.message}`);
        }
        
      } catch (error) {
        console.error('❌ Video analysis failed:', error);
        alert(`Video analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    } else {
      if (!selectedApp || !config.scenarioFile) {
        console.warn('⚠️ Missing required fields');
        return;
      }

      console.log('🚀 Starting analysis with config:', { selectedApp, config });
      
      try {
        const result = await startMockScenario(selectedApp, config.scenarioFile, config);
        if (result?.analysis_id) {
          console.log('✅ Analysis started, navigating to:', result.analysis_id);
          navigate(`/analysis/${result.analysis_id}`);
        }
      } catch (error) {
        console.error('❌ Analysis failed:', error);
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">UX Analysis</h1>
        <p className="text-lg text-gray-600">Configure your analysis settings and choose what to evaluate</p>
        <div className="flex items-center justify-center mt-4 space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-sm text-green-600 font-medium">Connected to API</span>
        </div>
      </div>

      {/* Analysis Mode Selection */}
      <div className="bg-white rounded-xl shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          Choose Analysis Type
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            type="button"
            onClick={() => handleAnalysisModeChange('scenario')}
            className={`p-4 border-2 rounded-lg transition-all ${
              analysisMode === 'scenario' 
                ? 'border-blue-500 bg-blue-50 text-blue-700' 
                : 'border-gray-200 hover:border-gray-300 text-gray-700'
            }`}
            disabled={isAnalyzing}
          >
            <div className="text-center">
              <div className="text-2xl mb-2">🎯</div>
              <div className="font-medium">Scenario Analysis</div>
              <div className="text-sm text-gray-600 mt-1">
                Test predefined user scenarios with browser automation
              </div>
            </div>
          </button>
          
          <button
            type="button"
            onClick={() => handleAnalysisModeChange('video')}
            className={`p-4 border-2 rounded-lg transition-all ${
              analysisMode === 'video' 
                ? 'border-blue-500 bg-blue-50 text-blue-700' 
                : 'border-gray-200 hover:border-gray-300 text-gray-700'
            }`}
            disabled={isAnalyzing}
          >
            <div className="text-center">
              <div className="text-2xl mb-2">📹</div>
              <div className="font-medium">Video Analysis</div>
              <div className="text-sm text-gray-600 mt-1">
                Upload video and analyze frame-by-frame UX issues
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Progress */}
      {isAnalyzing && (
        <div className="bg-white rounded-xl shadow p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="font-semibold">Analysis in Progress</div>
            <div className="text-blue-600">{progress}%</div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
          </div>
          {currentAnalysis?.message && <div className="text-sm text-gray-600 mt-2">{currentAnalysis.message}</div>}
        </div>
      )}

      {/* Errors */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5" />
            <span className="font-medium">Analysis Error:</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Video Upload Section */}
        {analysisMode === 'video' && (
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Video className="w-5 h-5 mr-2" />
              Upload Video for Analysis
            </h2>
            
            <div className="space-y-4">
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium mb-2">Video File</label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                  <input
                    type="file"
                    accept="video/*"
                    onChange={handleVideoUpload}
                    className="hidden"
                    id="video-upload"
                    disabled={isAnalyzing}
                  />
                  <label htmlFor="video-upload" className="cursor-pointer">
                    <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                    <div className="text-sm text-gray-600">
                      Click to upload video or drag and drop
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      MP4, AVI, MOV, WebM (max 100MB)
                    </div>
                  </label>
                </div>
              </div>

              {/* Video Preview */}
              {videoPreview && (
                <div>
                  <label className="block text-sm font-medium mb-2">Preview</label>
                  <video
                    src={videoPreview}
                    controls
                    className="w-full max-w-md rounded-lg border"
                    style={{ maxHeight: '300px' }}
                  />
                  <div className="text-sm text-gray-600 mt-2">
                    File: {config.videoFile?.name} ({(config.videoFile?.size || 0 / 1024 / 1024).toFixed(1)} MB)
                  </div>
                </div>
              )}

              {/* Frame Interval Setting */}
              <div>
                <label className="block text-sm font-medium mb-2">Frame Extraction Interval</label>
                <select
                  value={config.frameInterval || 2}
                  onChange={(e) => setConfig(prev => ({ ...prev, frameInterval: parseInt(e.target.value) }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value={1}>Every 1 second</option>
                  <option value={2}>Every 2 seconds</option>
                  <option value={5}>Every 5 seconds</option>
                  <option value={10}>Every 10 seconds</option>
                </select>
                <div className="text-sm text-gray-600 mt-1">
                  Lower intervals provide more detailed analysis but take longer to process
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Mobile Configuration Section - Only show for video mode */}
        {analysisMode === 'video' && (
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Video className="w-5 h-5 mr-2" />
              Mobile Analysis Configuration
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Surface Selection */}
              <div>
                <label className="block text-sm font-medium mb-2">Entry Surface</label>
                <select
                  value={config.surface || 'Outlook Mobile'}
                  onChange={(e) => setConfig(prev => ({ ...prev, surface: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="Outlook Mobile">Outlook Mobile</option>
                  <option value="Teams Mobile">Teams Mobile</option>
                  <option value="M365 App">M365 App</option>
                </select>
              </div>

              {/* Platform Selection */}
              <div>
                <label className="block text-sm font-medium mb-2">Platform</label>
                <select
                  value={config.platform || 'Android'}
                  onChange={(e) => setConfig(prev => ({ ...prev, platform: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="Android">Android</option>
                  <option value="iOS">iOS</option>
                </select>
              </div>

              {/* Open Path */}
              <div>
                <label className="block text-sm font-medium mb-2">Open Path</label>
                <select
                  value={config.openPath || 'link'}
                  onChange={(e) => setConfig(prev => ({ ...prev, openPath: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="link">Link</option>
                  <option value="attachment">Attachment</option>
                </select>
              </div>

              {/* File Size */}
              <div>
                <label className="block text-sm font-medium mb-2">File Size</label>
                <select
                  value={config.fileSize || 'large'}
                  onChange={(e) => setConfig(prev => ({ ...prev, fileSize: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="small">Small (&lt; 1MB)</option>
                  <option value="large">Large (&gt; 1MB)</option>
                </select>
              </div>

              {/* Protection */}
              <div>
                <label className="block text-sm font-medium mb-2">File Protection</label>
                <select
                  value={config.protection || 'password'}
                  onChange={(e) => setConfig(prev => ({ ...prev, protection: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="normal">Normal</option>
                  <option value="password">Password Protected</option>
                  <option value="IRM">IRM Protected</option>
                  <option value="CLP">CLP Protected</option>
                  <option value="DLP">DLP Protected</option>
                  <option value="double-protected">Double Protected</option>
                </select>
              </div>

              {/* Account State */}
              <div>
                <label className="block text-sm font-medium mb-2">Account State</label>
                <select
                  value={config.accountState || 'work_profile'}
                  onChange={(e) => setConfig(prev => ({ ...prev, accountState: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="primary">Primary Account</option>
                  <option value="secondary">Secondary Account</option>
                  <option value="work_profile">Work Profile</option>
                </select>
              </div>
            </div>
            
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <div className="text-sm text-blue-800">
                <strong>Mobile Analysis:</strong> This configuration helps the AI understand the mobile handoff scenario 
                (e.g., Outlook Mobile → Excel Mobile) and provides context-aware bug detection for mobile-specific issues.
              </div>
            </div>
          </div>
        )}

        {/* Enhanced Mobile Matrix Configuration - Only show for video mode */}
        {analysisMode === 'video' && (
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Video className="w-5 h-5 mr-2" />
              Enhanced Mobile Matrix Configuration
            </h2>
            <p className="text-sm text-gray-600 mb-6">
              Configure the comprehensive mobile Excel handoff scenario matrix parameters for advanced analysis
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Device Selection */}
              <div>
                <label className="block text-sm font-medium mb-2">Device</label>
                <select
                  value={config.device || 'iPhone'}
                  onChange={(e) => setConfig(prev => ({ ...prev, device: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="iPhone">iPhone</option>
                  <option value="iPad">iPad</option>
                </select>
              </div>

              {/* Hub Entry Point */}
              <div>
                <label className="block text-sm font-medium mb-2">Hub Entry Point</label>
                <select
                  value={config.hubEntry || 'message_detail'}
                  onChange={(e) => setConfig(prev => ({ ...prev, hubEntry: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="message_detail">Message Detail</option>
                  <option value="files_search">Files Search</option>
                </select>
              </div>

              {/* Source Type */}
              <div>
                <label className="block text-sm font-medium mb-2">Source Type</label>
                <select
                  value={config.source || 'Attachment'}
                  onChange={(e) => setConfig(prev => ({ ...prev, source: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="Attachment">Attachment</option>
                  <option value="OneDrive">OneDrive</option>
                </select>
              </div>

              {/* File Extension */}
              <div>
                <label className="block text-sm font-medium mb-2">File Extension</label>
                <select
                  value={config.fileExt || 'xlsx'}
                  onChange={(e) => setConfig(prev => ({ ...prev, fileExt: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="xlsx">Excel (.xlsx)</option>
                  <option value="xls">Excel Legacy (.xls)</option>
                  <option value="csv">CSV (.csv)</option>
                </select>
              </div>

              {/* Apps Installed */}
              <div>
                <label className="block text-sm font-medium mb-2">Apps Installed</label>
                <select
                  value={config.appsInstalled || 'None'}
                  onChange={(e) => setConfig(prev => ({ ...prev, appsInstalled: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="None">None</option>
                  <option value="Excel">Excel Only</option>
                  <option value="M365">M365 Only</option>
                  <option value="WXP+M365">Word + M365</option>
                  <option value="All3">All Apps</option>
                </select>
              </div>

              {/* Host Account */}
              <div>
                <label className="block text-sm font-medium mb-2">Host Account</label>
                <select
                  value={config.hostAccount || 'Primary'}
                  onChange={(e) => setConfig(prev => ({ ...prev, hostAccount: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="Primary">Primary Account</option>
                  <option value="Secondary">Secondary Account</option>
                </select>
              </div>

              {/* App Account */}
              <div>
                <label className="block text-sm font-medium mb-2">App Account</label>
                <select
                  value={config.appAccount || 'Primary'}
                  onChange={(e) => setConfig(prev => ({ ...prev, appAccount: e.target.value }))}
                  className="w-full p-3 border rounded-lg"
                  disabled={isAnalyzing}
                >
                  <option value="Primary">Primary Account</option>
                  <option value="Secondary">Secondary Account</option>
                </select>
              </div>
            </div>

            {/* Matrix Preview */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium mb-2">Scenario Matrix Preview</h3>
              <div className="text-xs text-gray-600 font-mono">
                {config.device || 'iPhone'} × {config.surface || 'Outlook Mobile'} × {config.hubEntry || 'message_detail'} × {config.source || 'Attachment'} × {config.fileExt || 'xlsx'} × {config.fileSize || 'Small'} × {config.protection || 'Normal'} × {config.appsInstalled || 'None'} × {config.hostAccount || 'Primary'} × {config.appAccount || 'Primary'}
              </div>
            </div>

            <div className="mt-4 p-4 bg-green-50 rounded-lg">
              <div className="text-sm text-green-800">
                <strong>Enhanced Matrix Analysis:</strong> This configuration enables comprehensive scenario matching against the mobile Excel handoff matrix, 
                providing expected behavior validation and intelligent guardrails for more accurate bug detection.
              </div>
            </div>
          </div>
        )}

        {/* Target App Selection - Only show for scenario mode */}
        {analysisMode === 'scenario' && (
          <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Select Target Application
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {['word', 'excel', 'powerpoint'].map((app) => (
              <button
                key={app}
                type="button"
                onClick={() => handleAppSelection(app)}
                className={`p-4 border-2 rounded-lg transition-all ${
                  selectedApp === app 
                    ? 'border-blue-500 bg-blue-50 text-blue-700' 
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                }`}
                disabled={isAnalyzing}
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">
                    {app === 'word' ? '📄' : app === 'excel' ? '📊' : '📽️'}
                  </div>
                  <div className="font-medium">
                    {app === 'word' ? 'Word' : app === 'excel' ? 'Excel' : 'PowerPoint'}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {app === 'word' ? 'Microsoft Word' : app === 'excel' ? 'Microsoft Excel' : 'Microsoft PowerPoint'}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
        )}

        {/* Scenario Selection - Only show for scenario mode */}
        {analysisMode === 'scenario' && selectedApp && (
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-2">
              Select Scenario for {selectedApp === 'word' ? 'Microsoft Word' : selectedApp === 'excel' ? 'Microsoft Excel' : 'Microsoft PowerPoint'}
            </h2>

            <div>
              <label className="block text-sm font-medium mb-1">Scenario</label>
              <select
                className="w-full p-3 border rounded-lg"
                value={config.scenarioFile || ''}
                onChange={(e) => setConfig(p => ({ ...p, scenarioFile: e.target.value }))}
                required
                disabled={isAnalyzing || scenarios.length === 0}
              >
                <option value="">Choose a scenario...</option>
                {scenarios.map(s => (
                  <option key={s.id} value={s.id} title={s.description || ''}>
                    {s.name}
                  </option>
                ))}
              </select>
              {scenarios.length > 0 && (
                <p className="text-sm text-green-600 mt-1">✅ {scenarios.length} {selectedApp} scenarios loaded</p>
              )}
              {scenarios.length === 0 && !loading && selectedApp && (
                <p className="text-sm text-gray-500 mt-1">No scenarios available for {selectedApp}</p>
              )}
            </div>
          </div>
        )}

        {/* Analysis Modules */}
        {((analysisMode === 'scenario' && selectedApp && config.scenarioFile) || (analysisMode === 'video' && config.videoFile)) && (
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Analysis Modules</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { key: 'enablePerformance', label: 'Performance Analysis', desc: 'Core Web Vitals and loading metrics' },
                { key: 'enableAccessibility', label: 'Accessibility Audit', desc: 'WCAG 2.1 compliance testing' },
                { key: 'enableKeyboard', label: 'Keyboard Navigation', desc: 'Keyboard accessibility testing' },
                { key: 'enableUxHeuristics', label: 'UX Heuristics', desc: 'Nielsen\'s usability principles' },
                { key: 'enableBestPractices', label: 'Best Practices', desc: 'Industry standard compliance' },
                { key: 'enableHealthAlerts', label: 'Health Alerts', desc: 'Critical issue detection' },
                { key: 'enableFunctional', label: 'Functional Testing', desc: 'Feature workflow validation' },
              ].map(module => (
                <label key={module.key} className="flex items-start space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={config[module.key as keyof AnalysisConfig] as boolean}
                    onChange={(e) => setConfig(p => ({ ...p, [module.key]: e.target.checked }))}
                    className="mt-1"
                    disabled={isAnalyzing}
                  />
                  <div>
                    <div className="font-medium">{module.label}</div>
                    <div className="text-sm text-gray-600">{module.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Submit Button */}
        {((analysisMode === 'scenario' && selectedApp && config.scenarioFile) || (analysisMode === 'video' && config.videoFile)) && (
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={isAnalyzing || (analysisMode === 'scenario' && (!selectedApp || !config.scenarioFile)) || (analysisMode === 'video' && !config.videoFile)}
              className="inline-flex items-center px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {analysisMode === 'video' ? (
                <Video className="w-5 h-5 mr-2" />
              ) : (
                <Play className="w-5 h-5 mr-2" />
              )}
              {isAnalyzing ? 'Running Analysis...' : analysisMode === 'video' ? 'Start Video Analysis' : 'Start Analysis'}
            </button>
          </div>
        )}
      </form>
    </div>
  );
}
