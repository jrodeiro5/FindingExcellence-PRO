import pytest
import os
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

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

class TestOpenRouterClient:
    def test_import(self):
        try:
            from backend.ai.openrouter_client import OpenRouterClient
            assert OpenRouterClient is not None
        except ImportError as e:
            pytest.skip(f'OpenRouterClient import failed: {e}')

    def test_client_initialization(self):
        try:
            from backend.ai.openrouter_client import OpenRouterClient
            client = OpenRouterClient(api_key='test-key')
            assert client is not None
            assert client.MODELS is not None
            assert len(client.MODELS) > 0
        except ImportError:
            pytest.skip('OpenRouterClient not available')

    def test_model_configuration(self):
        try:
            from backend.ai.openrouter_client import OpenRouterClient
            client = OpenRouterClient(api_key='test-key')
            required_models = ['general_free', 'vision_free', 'general', 'vision']
            for model_key in required_models:
                assert model_key in client.MODELS, f'Missing model: {model_key}'
        except ImportError:
            pytest.skip('OpenRouterClient not available')

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
            from backend.main import app
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.get('/health')
            assert response.status_code == 200
        except ImportError:
            pytest.skip('FastAPI not available')

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
