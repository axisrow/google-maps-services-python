# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
nox

# Run tests with coverage
python3 -m pytest tests/ -v --cov=googlemaps --cov-report=term-missing

# Run a single test file
python3 -m pytest tests/test_directions.py -v

# Run a single test
python3 -m pytest tests/test_directions.py::DirectionsTest::test_simple_directions -v

# Build documentation
nox -e docs

# Install package in development mode
pip install -e .
```

## Architecture

This is a Python client library for Google Maps Platform Web Services APIs.

### Core Components

- **`googlemaps/client.py`** — Central `Client` class that handles:
  - Authentication (API key or enterprise client_id/client_secret)
  - HTTP requests with automatic retry logic
  - Rate limiting (queries_per_second/queries_per_minute)
  - Response extraction via `_get_body()` or custom `extract_body` functions

- **`googlemaps/exceptions.py`** — Exception hierarchy:
  - `ApiError` — API returned an error status
  - `TransportError` — Network/transport issues
  - `HTTPError` — Unexpected HTTP status codes
  - `Timeout` — Request timeout
  - `_OverQueryLimit` — Rate limit exceeded (retriable)

- **`googlemaps/convert.py`** — Utilities for converting Python types to API-compatible strings (lat/lng formatting, time conversion, etc.)

### API Module Pattern

Each API (directions, geocoding, places, etc.) is implemented as a separate module with:

1. **Standalone function** — Takes `client` as first parameter, returns API response
2. **Helper functions** — `_xxx_extract()` for custom response handling (some APIs return different formats)
3. **Registration in client.py** — Imported and attached to `Client` class via `make_api_method()`

Example from `directions.py`:
```python
def directions(client, origin, destination, ...):
    # Build params, call client._request(), return response
```

Then in `client.py`:
```python
from googlemaps.directions import directions
Client.directions = make_api_method(directions)
```

### Two API Styles

1. **Classic APIs** — Use GET requests to `maps.googleapis.com/maps/api/...` with query parameters. Response has `status` field.

2. **Newer APIs** (Routes, Solar, Weather, Air Quality, etc.) — Use POST with JSON body to service-specific domains. Response handling requires custom `_extract` functions.

### Testing

- Uses `unittest` with `responses` library for HTTP mocking
- Base test class in `tests/__init__.py` provides `TestCase` with `assertURLEqual()` helper
- Test files mirror module names: `tests/test_directions.py` tests `googlemaps/directions.py`
