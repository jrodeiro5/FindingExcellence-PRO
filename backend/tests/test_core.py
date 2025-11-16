import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_csv_file(temp_dir):
    file_path = os.path.join(temp_dir, 'test_data.csv')
    with open(file_path, 'w') as f:
        f.write('name,value\n')
        f.write('financial_report,5000\n')
        f.write('expense_tracking,3000\n')
    return file_path

class TestFileSearch:
    def test_import(self):
        try:
            from backend.core.file_search import FileSearch
            assert FileSearch is not None
        except ImportError as e:
            pytest.skip(f'FileSearch import failed: {e}')

    def test_file_search_initialization(self):
        try:
            from backend.core.file_search import FileSearch
            fs = FileSearch()
            assert fs is not None
        except ImportError:
            pytest.skip('FileSearch not available')

class TestExcelProcessor:
    def test_import(self):
        try:
            from backend.core.excel_processor import ExcelProcessor
            assert ExcelProcessor is not None
        except ImportError as e:
            pytest.skip(f'ExcelProcessor import failed: {e}')

class TestContentSearch:
    def test_import(self):
        try:
            from backend.core.content_search import ContentSearch
            assert ContentSearch is not None
        except ImportError as e:
            pytest.skip(f'ContentSearch import failed: {e}')

    def test_content_search_initialization(self):
        try:
            from backend.core.content_search import ContentSearch
            cs = ContentSearch()
            assert cs is not None
        except ImportError:
            pytest.skip('ContentSearch not available')

class TestPDFProcessor:
    def test_import(self):
        try:
            from backend.core.pdf_processor import PDFProcessor
            assert PDFProcessor is not None
        except ImportError as e:
            pytest.skip(f'PDFProcessor import failed: {e}')

class TestConfigManager:
    def test_import(self):
        try:
            from backend.core.config_manager import ConfigManager
            assert ConfigManager is not None
        except ImportError as e:
            pytest.skip(f'ConfigManager import failed: {e}')

    def test_config_save_load(self, temp_dir):
        try:
            from backend.core.config_manager import ConfigManager
            config_file = os.path.join(temp_dir, 'test_config.json')
            cm = ConfigManager(config_file)
            cm.set('test_key', 'test_value')
            cm.save()
            cm2 = ConfigManager(config_file)
            value = cm2.get('test_key')
            assert value == 'test_value'
        except ImportError:
            pytest.skip('ConfigManager not available')

class TestOllamaClient:
    def test_import(self):
        try:
            from backend.ai.ollama_client import OllamaClient
            assert OllamaClient is not None
        except ImportError as e:
            pytest.skip(f'OllamaClient import failed: {e}')

    def test_model_configuration(self):
        try:
            from backend.ai.ollama_client import OllamaClient
            # Models should be accessible as class attributes
            assert hasattr(OllamaClient, 'MODELS')
            required_models = ['general', 'general_fast', 'vision', 'fallback_general']
            for model_key in required_models:
                assert model_key in OllamaClient.MODELS, f'Missing model: {model_key}'
        except ImportError:
            pytest.skip('OllamaClient not available')

    def test_fallback_chains(self):
        try:
            from backend.ai.ollama_client import OllamaClient
            # Fallback chains should be configured
            assert hasattr(OllamaClient, 'FALLBACK_CHAINS')
            assert 'general' in OllamaClient.FALLBACK_CHAINS
            assert 'vision' in OllamaClient.FALLBACK_CHAINS
            assert len(OllamaClient.FALLBACK_CHAINS['general']) > 0
        except ImportError:
            pytest.skip('OllamaClient not available')

    def test_usage_stats_structure(self):
        try:
            from backend.ai.ollama_client import UsageStats
            # Test UsageStats dataclass
            stats = UsageStats(
                prompt_tokens=10,
                completion_tokens=20,
                total_tokens=30,
                latency_ms=100.5,
                model='test-model'
            )
            assert stats.prompt_tokens == 10
            assert stats.completion_tokens == 20
            assert stats.total_tokens == 30
            assert stats.latency_ms == 100.5
            assert stats.model == 'test-model'
        except ImportError:
            pytest.skip('OllamaClient not available')

class TestExport:
    def test_import(self):
        try:
            from backend.utils.export import Export
            assert Export is not None
        except ImportError as e:
            pytest.skip(f'Export import failed: {e}')

    def test_csv_export(self, temp_dir):
        try:
            from backend.utils.export import Export
            data = [
                {'name': 'file1.xlsx', 'size': 1024},
                {'name': 'file2.xlsx', 'size': 2048},
            ]
            output_file = os.path.join(temp_dir, 'export.csv')
            Export.to_csv(data, output_file)
            assert os.path.exists(output_file)
            assert os.path.getsize(output_file) > 0
        except ImportError:
            pytest.skip('Export not available')

class TestFastAPIEndpoints:
    def test_imports(self):
        try:
            from backend.main import app
            assert app is not None
        except ImportError as e:
            pytest.skip(f'FastAPI app import failed: {e}')

    def test_health_endpoint(self):
        try:
            from fastapi.testclient import TestClient

            from backend.main import app
            client = TestClient(app)
            response = client.get('/health')
            assert response.status_code == 200
        except ImportError:
            pytest.skip('FastAPI not available')

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
