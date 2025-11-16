import React, { useState } from 'react';
import { backendClient } from '../api/backendClient';

export const AISearchPanel = ({ onAnalysisComplete, isLoading, onLoadingChange }) => {
  const [query, setQuery] = useState('');
  const [analysisType, setAnalysisType] = useState('summary');
  const [documentContent, setDocumentContent] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setError('');

    if (!documentContent.trim()) {
      setError('Please paste or enter document content to analyze');
      return;
    }

    try {
      onLoadingChange(true);
      const result = await backendClient.analyzeDocument(documentContent, analysisType);
      setAnalysisResult(result);
      onAnalysisComplete(result);
    } catch (err) {
      setError(`Analysis failed: ${err.message}`);
    } finally {
      onLoadingChange(false);
    }
  };

  const handleSemanticSearch = async (e) => {
    e.preventDefault();
    setError('');

    if (!query.trim()) {
      setError('Please enter a semantic search query');
      return;
    }

    if (!documentContent.trim()) {
      setError('Please paste document content to search within');
      return;
    }

    try {
      onLoadingChange(true);
      const result = await backendClient.semanticSearch(documentContent, query);
      setAnalysisResult(result);
      onAnalysisComplete(result);
    } catch (err) {
      setError(`Search failed: ${err.message}`);
    } finally {
      onLoadingChange(false);
    }
  };

  return (
    <div className="bg-background-1 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <h2 className="text-heading-20 text-gray-10 mb-2">AI Analysis Panel</h2>
          <p className="text-copy-14 text-gray-9">
            Analyze document content with AI-powered insights
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div role="alert" className="bg-gray-2 border-l-4 border-gray-9 text-gray-10 p-4 rounded-geist-sm mb-6">
            <p className="text-copy-14">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Analysis Options */}
          <div className="bg-gray-1 border border-gray-3 rounded-geist-md p-5">
            <h3 className="text-heading-16 text-gray-10 mb-5">Analysis Options</h3>

            <div className="space-y-5">
              <div>
                <label htmlFor="analysis-type" className="block text-label-14 font-medium text-gray-10 mb-2">
                  Analysis Type
                </label>
                <select
                  id="analysis-type"
                  value={analysisType}
                  onChange={(e) => setAnalysisType(e.target.value)}
                  disabled={isLoading}
                  className="w-full h-12 px-3 bg-background-1 border border-gray-4 hover:border-gray-5 focus:border-blue-6 focus-visible:ring-2 focus-visible:ring-blue-6 rounded-geist-sm text-base transition-colors duration-geist disabled:bg-gray-2 disabled:text-gray-6"
                >
                  <option value="summary">Summary</option>
                  <option value="trends">Trend Analysis</option>
                  <option value="anomalies">Anomaly Detection</option>
                  <option value="insights">Key Insights</option>
                </select>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={isLoading || !documentContent.trim()}
                className="w-full h-12 px-3.5 bg-white hover:bg-gray-10 active:bg-gray-9 text-black rounded-geist-sm text-base font-medium transition-colors duration-geist disabled:bg-gray-3 disabled:text-gray-6 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Analyzing...' : 'Analyze Document'}
              </button>

              <div className="border-t border-gray-3 pt-5">
                <h4 className="text-label-14 font-medium text-gray-10 mb-3">Semantic Search</h4>
                <input
                  id="semantic-query"
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g., budget increase, cost reduction"
                  disabled={isLoading}
                  className="w-full h-12 px-3 bg-background-1 border border-gray-4 hover:border-gray-5 focus:border-blue-6 focus-visible:ring-2 focus-visible:ring-blue-6 rounded-geist-sm text-base transition-colors duration-geist disabled:bg-gray-2 disabled:text-gray-6 mb-3"
                  autoComplete="off"
                />
                <button
                  onClick={handleSemanticSearch}
                  disabled={isLoading || !query.trim() || !documentContent.trim()}
                  className="w-full h-12 px-3.5 bg-transparent hover:bg-gray-2 active:bg-gray-3 text-gray-10 border border-gray-4 hover:border-gray-5 rounded-geist-sm text-base font-medium transition-colors duration-geist disabled:bg-transparent disabled:text-gray-5 disabled:border-gray-3 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Searching...' : 'Semantic Search'}
                </button>
              </div>
            </div>
          </div>

          {/* Right Column: Document Input and Results */}
          <div>
            <div className="mb-5">
              <label htmlFor="document-content" className="block text-label-14 font-medium text-gray-10 mb-2">
                Document Content
              </label>
              <textarea
                id="document-content"
                value={documentContent}
                onChange={(e) => setDocumentContent(e.target.value)}
                placeholder="Paste document content here for analysis..."
                disabled={isLoading}
                className="w-full h-56 px-4 py-3 bg-background-1 border border-gray-4 hover:border-gray-5 focus:border-blue-6 focus-visible:ring-2 focus-visible:ring-blue-6 rounded-geist-sm text-copy-13 font-mono transition-colors duration-geist disabled:bg-gray-2 disabled:text-gray-6 resize-none"
              />
            </div>

            {/* Analysis Result */}
            {analysisResult && (
              <div
                className="p-4 bg-gray-1 border border-gray-4 rounded-geist-md shadow-geist-menu"
                role="region"
                aria-label="Analysis result"
              >
                <h4 className="text-label-14 font-medium text-gray-10 mb-3">Analysis Result</h4>
                <div className="text-copy-13 text-gray-9 font-mono whitespace-pre-wrap max-h-48 overflow-y-auto bg-background-1 p-3 rounded-geist-sm border border-gray-3">
                  {typeof analysisResult === 'string' ? analysisResult : JSON.stringify(analysisResult, null, 2)}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AISearchPanel;
