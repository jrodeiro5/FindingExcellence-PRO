import React, { useState } from 'react';
import { backendClient } from '../api/backendClient';

export const SearchPanel = ({ onSearch, isLoading, onLoadingChange }) => {
  const [searchMode, setSearchMode] = useState('filename');
  const [keywords, setKeywords] = useState('');
  const [excludeKeywords, setExcludeKeywords] = useState('');
  const [folders, setFolders] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [caseSensitive, setCaseSensitive] = useState(false);
  const [fileTypes, setFileTypes] = useState('all');
  const [error, setError] = useState('');

  const handleFilenameSearch = async (e) => {
    e.preventDefault();
    setError('');
    if (!keywords.trim()) {
      setError('Please enter search keywords');
      return;
    }
    try {
      onLoadingChange(true);
      const folderArray = folders ? folders.split(';').map(f => f.trim()).filter(f => f) : [];
      const response = await backendClient.searchByFilename(
        keywords.split(',').map(k => k.trim()).filter(k => k),
        folderArray,
        {
          excludeKeywords: excludeKeywords ? excludeKeywords.split(',').map(k => k.trim()).filter(k => k) : [],
          startDate: dateFrom || undefined,
          endDate: dateTo || undefined,
          caseSensitive: caseSensitive,
          fileTypes: fileTypes !== 'all' ? [`.${fileTypes}`] : undefined,
        }
      );
      const transformedResults = response.data.results.map(result => ({
        name: result.filename,
        path: result.path,
        modified_date: result.modified,
        type: result.type,
        full_path: result.path
      }));
      onSearch({ type: 'filename', results: transformedResults, query: keywords });
    } catch (err) {
      setError(`Search failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      onLoadingChange(false);
    }
  };

  const handleNLSearch = async (e) => {
    e.preventDefault();
    setError('');
    if (!keywords.trim()) {
      setError('Please enter a natural language query');
      return;
    }
    try {
      onLoadingChange(true);
      const folderArray = folders ? folders.split(';').map(f => f.trim()).filter(f => f) : [];
      const response = await backendClient.naturalLanguageSearch(keywords, folderArray);
      const transformedResults = response.data.results.map(result => ({
        name: result.filename,
        path: result.path,
        modified_date: result.modified,
        type: result.path?.split('.').pop() || 'unknown',
        full_path: result.path
      }));
      onSearch({
        type: 'natural-language',
        results: transformedResults,
        query: keywords,
        aiData: response.data
      });
    } catch (err) {
      setError(`AI search failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      onLoadingChange(false);
    }
  };

  const handleSubmit = (e) => {
    if (searchMode === 'filename') {
      handleFilenameSearch(e);
    } else {
      handleNLSearch(e);
    }
  };

  const handleClear = () => {
    setKeywords('');
    setExcludeKeywords('');
    setFolders('');
    setDateFrom('');
    setDateTo('');
    setCaseSensitive(false);
    setFileTypes('all');
    setError('');
  };

  return (
    <div className="bg-background-1 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Search Mode Toggle */}
        <div className="flex gap-3 mb-6 p-1 bg-gray-2 rounded-geist-sm w-fit" role="radiogroup" aria-label="Search mode">
          <label className="flex items-center cursor-pointer px-4 py-2 rounded-geist-sm transition-colors duration-geist hover:bg-gray-3">
            <input
              type="radio"
              name="searchMode"
              value="filename"
              checked={searchMode === 'filename'}
              onChange={(e) => setSearchMode(e.target.value)}
              className="sr-only"
              aria-label="File search mode"
            />
            <span className={`text-button-14 ${searchMode === 'filename' ? 'text-gray-10 font-medium' : 'text-gray-7'}`}>
              File Search
            </span>
          </label>
          <label className="flex items-center cursor-pointer px-4 py-2 rounded-geist-sm transition-colors duration-geist hover:bg-gray-3">
            <input
              type="radio"
              name="searchMode"
              value="natural-language"
              checked={searchMode === 'natural-language'}
              onChange={(e) => setSearchMode(e.target.value)}
              className="sr-only"
              aria-label="AI natural language search mode"
            />
            <span className={`text-button-14 ${searchMode === 'natural-language' ? 'text-gray-10 font-medium' : 'text-gray-7'}`}>
              AI Search
            </span>
          </label>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Error Alert */}
          {error && (
            <div role="alert" className="bg-gray-2 border-l-4 border-gray-9 text-gray-10 p-4 rounded-geist-sm">
              <p className="text-copy-14">{error}</p>
            </div>
          )}

          {/* Keywords/Query Input */}
          <div>
            <label htmlFor="search-keywords" className="block text-label-14 font-medium text-gray-10 mb-2">
              {searchMode === 'filename' ? 'Keywords (filename)' : 'Search Query (natural language)'}
            </label>
            <input
              id="search-keywords"
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder={searchMode === 'filename' ? 'e.g., budget, financial, report' : 'e.g., Find all budget files from Q3'}
              className="w-full h-12 px-3 bg-background-1 border border-gray-4 hover:border-gray-5 focus:border-blue-6 focus-visible:ring-2 focus-visible:ring-blue-6 rounded-geist-sm text-base transition-colors duration-geist"
              autoComplete="off"
            />
          </div>

          {/* Exclude Keywords (Filename mode only) */}
          {searchMode === 'filename' && (
            <div>
              <label htmlFor="exclude-keywords" className="block text-label-14 font-medium text-gray-10 mb-2">
                Exclude Keywords
              </label>
              <input
                id="exclude-keywords"
                type="text"
                value={excludeKeywords}
                onChange={(e) => setExcludeKeywords(e.target.value)}
                placeholder="e.g., temp, draft, archive"
                className="w-full h-12 px-3 bg-background-1 border border-gray-4 hover:border-gray-5 focus:border-blue-6 focus-visible:ring-2 focus-visible:ring-blue-6 rounded-geist-sm text-base transition-colors duration-geist"
                autoComplete="off"
              />
            </div>
          )}

          {/* Folders Input */}
          <div>
            <label htmlFor="search-folders" className="block text-label-14 font-medium text-gray-10 mb-2">
              Search Folders
              <span className="text-gray-7 font-normal ml-2">(semicolon-separated)</span>
            </label>
            <input
              id="search-folders"
              type="text"
              value={folders}
              onChange={(e) => setFolders(e.target.value)}
              placeholder="e.g., C:\Documents; C:\Reports"
              className="w-full h-12 px-3 bg-background-1 border border-gray-4 hover:border-gray-5 focus:border-blue-6 focus-visible:ring-2 focus-visible:ring-blue-6 rounded-geist-sm text-base font-mono transition-colors duration-geist"
              autoComplete="off"
            />
          </div>

          {/* Date Range and File Type (Filename mode only) */}
          {searchMode === 'filename' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label htmlFor="date-from" className="block text-label-14 font-medium text-gray-10 mb-2">
                  Date From
                </label>
                <input
                  id="date-from"
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="w-full h-12 px-3 bg-background-1 border border-gray-4 hover:border-gray-5 focus:border-blue-6 focus-visible:ring-2 focus-visible:ring-blue-6 rounded-geist-sm text-base transition-colors duration-geist"
                />
              </div>
              <div>
                <label htmlFor="date-to" className="block text-label-14 font-medium text-gray-10 mb-2">
                  Date To
                </label>
                <input
                  id="date-to"
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="w-full h-12 px-3 bg-background-1 border border-gray-4 hover:border-gray-5 focus:border-blue-6 focus-visible:ring-2 focus-visible:ring-blue-6 rounded-geist-sm text-base transition-colors duration-geist"
                />
              </div>
              <div>
                <label htmlFor="file-type" className="block text-label-14 font-medium text-gray-10 mb-2">
                  File Type
                </label>
                <select
                  id="file-type"
                  value={fileTypes}
                  onChange={(e) => setFileTypes(e.target.value)}
                  className="w-full h-12 px-3 bg-background-1 border border-gray-4 hover:border-gray-5 focus:border-blue-6 focus-visible:ring-2 focus-visible:ring-blue-6 rounded-geist-sm text-base transition-colors duration-geist"
                >
                  <option value="all">All Files</option>
                  <option value="xlsx">Excel (.xlsx)</option>
                  <option value="csv">CSV (.csv)</option>
                  <option value="pdf">PDF (.pdf)</option>
                </select>
              </div>
            </div>
          )}

          {/* Case Sensitive Option (Filename mode only) */}
          {searchMode === 'filename' && (
            <div className="flex items-center">
              <input
                id="case-sensitive"
                type="checkbox"
                checked={caseSensitive}
                onChange={(e) => setCaseSensitive(e.target.checked)}
                className="w-4 h-4 text-blue-6 border-gray-4 rounded focus-visible:ring-2 focus-visible:ring-blue-6"
              />
              <label htmlFor="case-sensitive" className="ml-2 text-label-14 text-gray-9">
                Case Sensitive
              </label>
            </div>
          )}

          {/* Action Buttons - Vercel Style */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 h-12 px-3.5 bg-white hover:bg-gray-10 active:bg-gray-9 text-black rounded-geist-sm text-base font-medium transition-colors duration-geist disabled:bg-gray-3 disabled:text-gray-6 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Searching...' : 'Search'}
            </button>
            <button
              type="button"
              disabled={isLoading}
              onClick={handleClear}
              className="h-12 px-3.5 bg-transparent hover:bg-gray-2 active:bg-gray-3 text-gray-10 border border-gray-4 hover:border-gray-5 rounded-geist-sm text-base font-medium transition-colors duration-geist disabled:bg-transparent disabled:text-gray-5 disabled:border-gray-3 disabled:cursor-not-allowed"
            >
              Clear
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SearchPanel;
