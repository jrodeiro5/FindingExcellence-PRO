# Backend Testing Guide

## Test Structure

The backend test suite includes:

- **test_core.py**: Unit tests for core modules (FileSearch, ExcelProcessor, ContentSearch, PDFProcessor, ConfigManager)
- **test_integration.py**: Integration tests for API endpoints and service interactions
- **conftest.py**: Pytest configuration and shared fixtures

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest backend/tests/test_core.py -v
```

### Run specific test class:
```bash
pytest backend/tests/test_core.py::TestFileSearch -v
```

### Run specific test:
```bash
pytest backend/tests/test_core.py::TestFileSearch::test_import -v
```

### Run with coverage:
```bash
pytest --cov=backend --cov-report=html
```

### Run only unit tests:
```bash
pytest -m unit
```

### Run only integration tests:
```bash
pytest -m integration
```

## Test Categories

### Unit Tests (test_core.py)

Tests for individual modules:

1. **TestFileSearch**
   - test_import: Verify FileSearch module can be imported
   - test_file_search_initialization: Verify FileSearch initialization
   - test_search_by_filename: Test filename search functionality

2. **TestExcelProcessor**
   - test_import: Verify ExcelProcessor module can be imported
   - test_excel_read: Test Excel file reading

3. **TestContentSearch**
   - test_import: Verify ContentSearch module can be imported
   - test_content_search_initialization: Verify initialization
   - test_search_keywords: Test keyword search in content

4. **TestPDFProcessor**
   - test_import: Verify PDFProcessor module can be imported
   - test_pdf_text_extraction: Test PDF text extraction

5. **TestConfigManager**
   - test_import: Verify ConfigManager module can be imported
   - test_config_save_load: Test config persistence

6. **TestOpenRouterClient**
   - test_import: Verify OpenRouterClient module can be imported
   - test_client_initialization: Verify client initialization
   - test_model_configuration: Verify all required models are configured

7. **TestExport**
   - test_import: Verify Export module can be imported
   - test_csv_export: Test CSV export functionality

8. **TestFastAPIEndpoints**
   - test_imports: Verify FastAPI app can be imported
   - test_health_endpoint: Test /health endpoint

### Integration Tests (test_integration.py)

Tests for API endpoints and service interactions:

1. **TestAPIIntegration**
   - test_health_endpoint: Test health check endpoint
   - test_search_filename_endpoint: Test filename search endpoint
   - test_search_content_endpoint: Test content search endpoint
   - test_usage_stats_endpoint: Test usage statistics endpoint

2. **TestSearchFunctionality**
   - test_file_search_with_keywords: Test file search with keywords
   - test_content_search_basic: Test basic content search

3. **TestAIServices**
   - test_ai_service_initialization: Verify AI service initialization

4. **TestErrorHandling**
   - test_invalid_file_path: Test handling of invalid paths
   - test_malformed_json_handling: Test JSON error handling

## Test Fixtures

Defined in conftest.py:

- **test_env**: Session-scoped fixture for test environment setup
- **mock_api_key**: Fixture providing test OpenRouter API key
- **client**: FastAPI TestClient for API testing
- **temp_dir**: Temporary directory for file operations
- **sample_csv_file**: Sample CSV file for testing

## Coverage Goals

Target test coverage:
- Core modules (file_search, excel_processor, content_search): 80%+
- AI services (openrouter_client, ai_services): 60%+
- API endpoints: 90%+
- Error handling: 85%+

## Dependencies for Testing

Add to requirements.txt:
```
pytest>=7.0
pytest-cov>=4.0
pytest-asyncio>=0.21
pytest-mock>=3.10
```

## Continuous Integration

To run tests in CI:

```bash
# Install test dependencies
pip install -r requirements.txt pytest pytest-cov

# Run all tests with coverage
pytest --cov=backend --cov-report=term-missing

# Generate coverage report
pytest --cov=backend --cov-report=html
```

## Troubleshooting

### ImportError for modules
- Ensure backend is in Python path
- Check that __init__.py files exist in all packages
- Run from project root directory

### API key errors
- Tests requiring API keys will be skipped if key not available
- Set OPENROUTER_API_KEY environment variable for full testing

### File not found errors
- Tests use temporary directories
- Ensure temp directory permissions are correct
- Check disk space availability

## Best Practices

1. **Test isolation**: Each test should be independent
2. **Use fixtures**: Leverage pytest fixtures for setup/teardown
3. **Mock external calls**: Mock API calls to avoid rate limiting
4. **Clear assertions**: Use descriptive assertion messages
5. **Mark slow tests**: Use @pytest.mark.slow for long-running tests
