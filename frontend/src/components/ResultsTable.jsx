import React, { useState, useMemo } from 'react';

export const ResultsTable = ({ results, searchType, isLoading }) => {
  const [sortConfig, setSortConfig] = useState({ key: 'name', direction: 'asc' });
  const [filterText, setFilterText] = useState('');
  const [copiedIndex, setCopiedIndex] = useState(null);

  const filteredAndSortedResults = useMemo(() => {
    if (!results || results.length === 0) return [];

    let filtered = results;
    if (filterText) {
      filtered = results.filter(item => {
        const searchableText = Object.values(item).join(' ').toLowerCase();
        return searchableText.includes(filterText.toLowerCase());
      });
    }

    const sorted = [...filtered].sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];

      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;

      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();

      if (aStr < bStr) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aStr > bStr) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return sorted;
  }, [results, filterText, sortConfig]);

  const handleSort = (key) => {
    setSortConfig(prevConfig => ({
      key,
      direction: prevConfig.key === key && prevConfig.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  const handleCopyPath = (path, index) => {
    if (path) {
      navigator.clipboard.writeText(path);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64" role="status" aria-live="polite">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-gray-3 border-t-blue-6 mx-auto mb-4"></div>
          <p className="text-copy-14 text-gray-9">Searching...</p>
        </div>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div className="p-8 text-center">
        <p className="text-copy-16 text-gray-7">No results found. Try a different search.</p>
      </div>
    );
  }

  const columns = results.length > 0 ? Object.keys(results[0]) : [];
  const displayColumns = columns.filter(col => col !== 'id' && col !== 'full_path');

  return (
    <div className="p-6 bg-background-2">
      <div className="max-w-full mx-auto">
        {/* Header with Filter */}
        <div className="mb-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h3 className="text-heading-18 text-gray-10">
            Results
            <span className="ml-2 text-label-14 text-gray-7 font-normal">
              ({filteredAndSortedResults.length} of {results.length})
            </span>
          </h3>
          <input
            type="text"
            placeholder="Filter results..."
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            className="h-12 px-3 bg-background-1 border border-gray-4 hover:border-gray-5 focus:border-blue-6 focus-visible:ring-2 focus-visible:ring-blue-6 rounded-geist-sm text-base transition-colors duration-geist w-full sm:w-64"
            aria-label="Filter results"
          />
        </div>

        {/* Table Container */}
        <div className="bg-background-1 rounded-geist-md shadow-geist-menu overflow-hidden border border-gray-3">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-2 border-b border-gray-4">
                <tr>
                  {displayColumns.map(col => (
                    <th
                      key={col}
                      onClick={() => handleSort(col)}
                      className="px-6 py-3 text-left text-label-13 font-medium text-gray-10 cursor-pointer hover:bg-gray-3 transition-colors duration-geist select-none"
                      tabIndex={0}
                      role="button"
                      aria-sort={sortConfig.key === col ? (sortConfig.direction === 'asc' ? 'ascending' : 'descending') : 'none'}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          handleSort(col);
                        }
                      }}
                    >
                      <div className="flex items-center gap-2">
                        <span>{col.replace(/_/g, ' ').toUpperCase()}</span>
                        {sortConfig.key === col && (
                          <span className="text-copy-13 text-blue-6" aria-hidden="true">
                            {sortConfig.direction === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </th>
                  ))}
                  <th className="px-6 py-3 text-left text-label-13 font-medium text-gray-10">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredAndSortedResults.map((result, idx) => (
                  <tr
                    key={idx}
                    className="border-b border-gray-3 hover:bg-gray-1 transition-colors duration-geist"
                  >
                    {displayColumns.map(col => (
                      <td key={col} className="px-6 py-4 text-copy-14 text-gray-10">
                        <div className="truncate max-w-xs" title={String(result[col])}>
                          {col === 'modified_date'
                            ? new Date(result[col]).toLocaleDateString()
                            : String(result[col])}
                        </div>
                      </td>
                    ))}
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handleCopyPath(result.full_path, idx)}
                        className="h-8 px-3 bg-transparent hover:bg-gray-2 active:bg-gray-3 text-gray-10 border border-gray-4 hover:border-gray-5 rounded-geist-sm text-button-12 font-medium transition-colors duration-geist"
                        aria-label={`Copy path for ${result.name}`}
                      >
                        {copiedIndex === idx ? 'Copied!' : 'Copy Path'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Results Info */}
        <div className="mt-4 text-copy-13 text-gray-7">
          Showing {filteredAndSortedResults.length} result{filteredAndSortedResults.length !== 1 ? 's' : ''}
          {filterText && ` filtered by "${filterText}"`}
        </div>
      </div>
    </div>
  );
};

export default ResultsTable;
