import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000
});

export const backendClient = {
  healthCheck: async () => client.get('/health'),

  searchByFilename: async (keywords, folders, options = {}) =>
    client.post('/api/search/filename', {
      keywords,
      folders,
      exclude_keywords: options.exclude_keywords || options.excludeKeywords || [],
      start_date: options.start_date || options.startDate,
      end_date: options.end_date || options.endDate,
      file_types: options.file_types || options.fileTypes || ['.xlsx', '.xls', '.xlsm', '.pdf']
    }),

  naturalLanguageSearch: async (query, folders) =>
    client.post('/api/search/natural-language', { query, folders }),

  searchContent: async (filePaths, keywords, options = {}) =>
    client.post('/api/search/content', {
      file_paths: filePaths,
      keywords,
      case_sensitive: options.case_sensitive || options.caseSensitive || false,
      search_type: options.search_type || options.searchType || 'excel'
    }),

  analyzeDocument: async (content, analysisType = 'summary') =>
    client.post('/api/analyze', { content, analysis_type: analysisType }),

  ocrImage: async (imageUrl, extractTables = false) =>
    client.post('/api/ocr', { image_url: imageUrl, extract_tables: extractTables }),

  getUsageStats: async () => client.get('/api/usage/stats')
};

export default backendClient;
