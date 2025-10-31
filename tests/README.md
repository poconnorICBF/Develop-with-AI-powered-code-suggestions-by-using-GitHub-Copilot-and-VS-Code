# Tests for Mergington High School Activities API

This directory contains comprehensive test suites for the Activities API using pytest.

## Test Structure

- **`conftest.py`**: Test configuration and fixtures
- **`test_api.py`**: Main API endpoint tests
- **`test_edge_cases.py`**: Edge cases and error handling tests

## Test Coverage

- ✅ **Root endpoint** - Redirect functionality
- ✅ **Activities endpoint** - GET /activities
- ✅ **Signup endpoint** - POST /activities/{activity_name}/signup
- ✅ **Unregister endpoint** - DELETE /activities/{activity_name}/unregister
- ✅ **Static file handling** - CSS, JS, HTML files
- ✅ **Error handling** - 400, 404 error responses
- ✅ **Input validation** - Missing parameters, special characters
- ✅ **Data consistency** - Structure validation, duplicate prevention
- ✅ **Integration workflows** - Complete signup/unregister cycles

## Running Tests

### Quick Start
```bash
# Run all tests
python run_tests.py

# Run tests without coverage
python run_tests.py --no-coverage

# Using pytest directly
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Test Categories

#### API Endpoint Tests (`test_api.py`)
- Root endpoint redirect behavior
- Activities listing functionality
- Signup process (success and error cases)
- Unregister process (success and error cases)
- Integration scenarios and workflows

#### Edge Case Tests (`test_edge_cases.py`)
- Input validation (empty emails, missing parameters)
- Special character handling and URL encoding
- Error message formatting
- Data structure consistency
- Static file serving

## Test Environment

- **Framework**: pytest
- **HTTP Testing**: FastAPI TestClient
- **Coverage**: pytest-cov
- **Fixtures**: Automatic data reset between tests

## Test Results

Current test status: **29 tests passing** with **100% code coverage**

## Test Fixtures

The test suite includes automatic data reset between tests to ensure isolation:
- Activities database is reset to original state before each test
- No cross-test contamination
- Predictable test environment

## Adding New Tests

When adding new features to the API:

1. Add tests to the appropriate test file
2. Use the existing fixtures in `conftest.py`
3. Follow the established naming patterns
4. Include both success and error scenarios
5. Update this README with new test categories

## Dependencies

See `requirements.txt` for all testing dependencies:
- `pytest` - Testing framework
- `pytest-asyncio` - Async testing support
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for testing