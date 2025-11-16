import React, { useState, useEffect } from 'react';
import SearchPanel from './components/SearchPanel';
import ResultsTable from './components/ResultsTable';
import AISearchPanel from './components/AISearchPanel';
import { backendClient } from './api/backendClient';

function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [searchResults, setSearchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [usageStats, setUsageStats] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    checkBackendHealth();
    const interval = setInterval(fetchUsageStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkBackendHealth = async () => {
    try {
      await backendClient.healthCheck();
      console.log('Backend is healthy');
    } catch (err) {
      setError('Backend server is not responding. Please ensure the Python backend is running.');
    }
  };

  const fetchUsageStats = async () => {
    try {
      const stats = await backendClient.getUsageStats();
      setUsageStats(stats);
    } catch (err) {
      console.error('Failed to fetch usage stats:', err);
    }
  };

  const handleSearch = (searchData) => {
    setSearchResults(searchData);
    setActiveTab('results');
  };

  const handleAnalysisComplete = (analysisData) => {
    console.log('Analysis completed:', analysisData);
  };

  return (
    <div className="min-h-screen bg-background-1 flex flex-col">
      {/* Skip to content link for accessibility */}
      <a href="#main-content" className="skip-to-content">
        Skip to content
      </a>

      {/* Header - Vercel Black */}
      <header className="bg-black text-white px-6 py-4 border-b border-gray-3">
        <div className="max-w-full">
          <h1 className="text-heading-24 font-sans">FindingExcellence PRO 2.0</h1>
          <p className="text-label-13 text-gray-7">
            Intelligent file and content search with AI analytics
          </p>
        </div>
      </header>

      {/* Error Alert */}
      {error && (
        <div
          role="alert"
          className="bg-gray-2 border-l-4 border-gray-9 text-gray-10 p-4 mx-6 mt-4 rounded-geist-sm"
        >
          <p className="text-label-14 font-medium">Error</p>
          <p className="text-copy-13 text-gray-9 mt-1">{error}</p>
        </div>
      )}

      {/* Tab Navigation */}
      <nav
        className="bg-background-1 border-b border-gray-3 px-6"
        aria-label="Main navigation"
      >
        <div className="flex gap-0" role="tablist">
          <button
            role="tab"
            aria-selected={activeTab === 'search'}
            aria-controls="search-panel"
            onClick={() => setActiveTab('search')}
            className={`px-6 py-4 text-button-14 border-b-2 transition-colors duration-geist ${activeTab === 'search'
              ? 'border-blue-6 text-blue-6'
              : 'border-transparent text-gray-9 hover:text-gray-10 hover:border-gray-4'
              }`}
          >
            File Search
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'ai-analysis'}
            aria-controls="ai-analysis-panel"
            onClick={() => setActiveTab('ai-analysis')}
            className={`px-6 py-4 text-button-14 border-b-2 transition-colors duration-geist ${activeTab === 'ai-analysis'
              ? 'border-blue-6 text-blue-6'
              : 'border-transparent text-gray-9 hover:text-gray-10 hover:border-gray-4'
              }`}
          >
            AI Analysis
          </button>
          {searchResults && (
            <button
              role="tab"
              aria-selected={activeTab === 'results'}
              aria-controls="results-panel"
              onClick={() => setActiveTab('results')}
              className={`px-6 py-4 text-button-14 border-b-2 transition-colors duration-geist ${activeTab === 'results'
                ? 'border-blue-6 text-blue-6'
                : 'border-transparent text-gray-9 hover:text-gray-10 hover:border-gray-4'
                }`}
            >
              Results ({searchResults.results?.length || 0})
            </button>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main id="main-content" className="flex-1 overflow-auto bg-background-2">
        <div
          id="search-panel"
          role="tabpanel"
          hidden={activeTab !== 'search'}
          aria-labelledby="search-tab"
        >
          {activeTab === 'search' && (
            <SearchPanel
              onSearch={handleSearch}
              isLoading={isLoading}
              onLoadingChange={setIsLoading}
            />
          )}
        </div>

        <div
          id="ai-analysis-panel"
          role="tabpanel"
          hidden={activeTab !== 'ai-analysis'}
          aria-labelledby="ai-analysis-tab"
        >
          {activeTab === 'ai-analysis' && (
            <AISearchPanel
              onAnalysisComplete={handleAnalysisComplete}
              isLoading={isLoading}
              onLoadingChange={setIsLoading}
            />
          )}
        </div>

        <div
          id="results-panel"
          role="tabpanel"
          hidden={activeTab !== 'results'}
          aria-labelledby="results-tab"
        >
          {activeTab === 'results' && searchResults && (
            <ResultsTable
              results={searchResults.results}
              searchType={searchResults.type}
              isLoading={isLoading}
            />
          )}
        </div>
      </main>

      {/* Usage Stats Bar */}
      {usageStats && usageStats.ai_enabled && (
        <div
          className="bg-black text-white px-6 py-2 text-label-12 border-t border-gray-3"
          role="status"
          aria-live="polite"
        >
          <span className="font-mono">API Calls: {usageStats.total_requests || 0}</span>
          <span className="mx-2 text-gray-7">|</span>
          <span className="font-mono">Latency: {(usageStats.avg_latency_per_request || 0).toFixed(0)}ms avg</span>
          <span className="mx-2 text-gray-7">|</span>
          <span className="font-mono">Tokens: {usageStats.total_tokens || 0}</span>
          <span className="mx-2 text-gray-7">|</span>
          <span className="font-mono text-green-400">100% Privacy (Local)</span>
        </div>
      )}

      {/* Footer - Vercel Black */}
      <footer className="bg-black text-gray-7 text-center py-4 text-copy-13 border-t border-gray-3">
        <p>FindingExcellence PRO 2.0 | Powered by Local AI (Ollama + Qwen2.5-VL) &amp; Electron | 100% Privacy</p>
      </footer>
    </div>
  );
}

export default App;
