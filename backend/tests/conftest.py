import pytest
import sys
import os

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_path)

@pytest.fixture(scope='session')
def test_env():
    os.environ['TESTING'] = 'true'
    os.environ['OPENROUTER_API_KEY'] = 'test-key-do-not-use'
    yield
    if 'TESTING' in os.environ:
        del os.environ['TESTING']

@pytest.fixture
def mock_api_key(monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY', 'test-key-12345')
    return 'test-key-12345'

def pytest_configure(config):
    config.addinivalue_line('markers', 'unit: mark test as a unit test')
    config.addinivalue_line('markers', 'integration: mark test as an integration test')
    config.addinivalue_line('markers', 'api: mark test as an API test')
