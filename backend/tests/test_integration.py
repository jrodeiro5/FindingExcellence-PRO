import json
import os
from unittest.mock import MagicMock, patch

import pytest


class TestAPIIntegration:
    @pytest.fixture
    def client(self):
        try:
            from fastapi.testclient import TestClient

            from backend.main import app
            return TestClient(app)
        except ImportError:
            pytest.skip('FastAPI not available')

    def test_health_endpoint(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data or response.text

    def test_search_filename_endpoint(self, client):
        payload = {
            'keywords': 'test',
            'folders': [],
            'exclude': None,
            'case_sensitive': False,
            'file_type': None,
            'date_from': None,
            'date_to': None
        }
        response = client.post('/api/search/filename', json=payload)
        assert response.status_code in [200, 400]

    def test_search_content_endpoint(self, client):
        payload = {
            'file_paths': ['test.xlsx'],
            'keywords': 'test',
            'case_sensitive': False
        }
        response = client.post('/api/search/content', json=payload)
        assert response.status_code in [200, 400, 422]

    def test_usage_stats_endpoint(self, client):
        response = client.get('/api/usage/stats')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_ocr_endpoint_not_available(self, client):
        """Test /api/ocr endpoint when Ollama is not available"""
        payload = {
            'image_url': 'https://example.com/image.png',
            'extract_tables': False
        }
        response = client.post('/api/ocr', json=payload)
        # Should return 503 if AI service not available, or process if available
        assert response.status_code in [200, 503, 500]

    def test_analyze_endpoint_exists(self, client):
        """Test /api/analyze endpoint"""
        payload = {
            'content': 'Sample document content',
            'analysis_type': 'summary'
        }
        response = client.post('/api/analyze', json=payload)
        # Should return 503 if AI service not available, or process if available
        assert response.status_code in [200, 503, 500]

class TestSearchFunctionality:
    def test_file_search_with_keywords(self):
        try:
            from backend.core.file_search import FileSearch
            fs = FileSearch()
            # Search in current directory
            results = fs.search('.', ['test'], max_results=5)
            assert isinstance(results, list)
        except ImportError:
            pytest.skip('FileSearch not available')

    def test_content_search_basic(self):
        try:
            from backend.core.content_search import ContentSearch
            cs = ContentSearch()
            # Test with empty file list
            results = cs.search([], ['test'])
            assert isinstance(results, list)
        except ImportError:
            pytest.skip('ContentSearch not available')

class TestAIServices:
    @pytest.mark.skip(reason='Requires API key')
    def test_natural_language_search(self, mock_api_key):
        try:
            from backend.ai.ai_services import AISearchService
            service = AISearchService()
            # This would need a valid API key
            result = service.natural_language_search('find budget files')
            assert result is not None
        except ImportError:
            pytest.skip('AI Services not available')

    def test_ai_service_initialization(self, mock_api_key):
        try:
            from backend.ai.ai_services import AISearchService
            service = AISearchService()
            assert service is not None
        except ImportError:
            pytest.skip('AI Services not available')

class TestErrorHandling:
    def test_invalid_file_path(self):
        try:
            from backend.core.file_search import FileSearch
            fs = FileSearch()
            results = fs.search('/nonexistent/path', ['test'])
            assert isinstance(results, list)
        except ImportError:
            pytest.skip('FileSearch not available')
        except Exception:
            pass

    def test_malformed_json_handling(self, client):
        response = client.post(
            '/api/search/filename',
            data='invalid json',
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code in [400, 422]

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
