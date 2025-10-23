# Copilot instructions for the `weather` MCP service

This document explains the `weather` Microservice (FastMCP) implemented in `weather.py`. Use it to guide Copilot (or any code-completion assistant) to safely modify, extend, or call this service.

## Purpose

The `weather` service exposes two asynchronous MCP tools that query the U.S. National Weather Service (NWS) API:

- `get_alerts(state: str) -> str` — returns active weather alerts for a U.S. state (two-letter code).
- `get_forecast(latitude: float, longitude: float) -> str` — returns a short human-readable forecast (next 5 periods) for a coordinate.

These functions are registered with `mcp.tool()` on a `FastMCP` server named `weather` and intended to be called by MCP clients over stdio or other transports supported by FastMCP.

## Files of interest

- `weather.py` — Implementation of the MCP server and tools.
- `main.py` — Simple script that prints a greeting (not part of the MCP server runtime).
- `README.md` — currently empty; could be populated with higher-level project documentation.

## How it works (brief)

- The module initializes `mcp = FastMCP("weather")`.
- The helper `make_nws_request(url)` performs HTTP requests to the NWS API using `httpx.AsyncClient`, sets a simple `User-Agent`, and returns parsed JSON or `None` on errors.
- `get_alerts` builds the `/alerts/active/area/{state}` endpoint, fetches features, formats each alert with `format_alert`, and returns a joined string.
- `get_forecast` requests `/points/{lat},{lon}` to find the forecast URL, then requests the forecast, extracts the `periods`, and formats up to 5 periods into a human-readable summary.
- The module exposes `main()` which runs `mcp.run(transport='stdio')` when executed directly.

## API contract (inputs/outputs/errors)

- get_alerts
  - Inputs: `state` — string (expected two-letter US state code, case-insensitive).
  - Output: `str` — human-readable text with alerts or an error message.
  - Error modes: returns a user-facing string such as "Unable to fetch alerts or no alerts found." or "No active alerts for this state."

- get_forecast
  - Inputs: `latitude` (float), `longitude` (float).
  - Output: `str` — human-readable forecast for up to next 5 periods or an error message.
  - Error modes: returns messages like "Unable to fetch forecast data for this location." or "Unable to fetch detailed forecast."

Notes: The functions never raise exceptions to the MCP caller; errors are swallowed and converted to string messages. This is intentional for simple user-facing responses but might hide underlying failures when used programmatically.

## Edge cases and guidance for changes

- Network errors/timeouts: `make_nws_request` returns `None` on any exception. If adding retry logic, prefer exponential backoff and keep total latency reasonable (< 30s).
- Input validation: Current code trusts inputs. If Copilot edits these functions, add validation for latitude/longitude ranges and a normalized state code argument (e.g., uppercase and strip whitespace).
- Rate limits & caching: NWS APIs have rate limits. If adding heavy usage patterns, add simple in-memory caching (TTL) or respect `Retry-After` headers.
- Response schema changes: Code currently indexes nested keys (e.g., `properties.forecast`). Any change should defensively use `.get()` or try/except to avoid KeyError.
- International/Non-US coordinates: `/points/{lat},{lon}` expects coordinates within the NWS coverage area (U.S. territories). For coords outside, provide a clear message.

## Suggested small, safe improvements Copilot can implement

1. Add input validation and clear error messages.
2. Improve logging for failures (do not expose secrets; include enough context to debug).
3. Limit the number of alerts returned or paginate long results.
4. Convert formatting helpers to return structured data (dict) in addition to human text, enabling clients to programmatically consume results.

## Example prompts for Copilot when editing this project

- "Add input validation to `get_forecast` so latitude must be between -90 and 90 and longitude between -180 and 180, returning a helpful error string if invalid." 
- "Make `make_nws_request` retry twice on network errors with exponential backoff and a maximum timeout of 30 seconds total." 
- "Change `get_alerts` to return results as JSON serializable dict with 'count' and 'alerts' keys, while keeping the existing human-readable string return as an option via a new parameter `format='text'|'json'`." 
- "Add basic in-memory TTL caching for `make_nws_request` to reduce duplicate calls to identical URLs within a 60-second window." 

## Testing and validation

- Unit tests should mock HTTP calls to NWS (e.g., using `respx` or `httpx` mocking) and validate both success and error responses.
- Quick manual test: run the MCP server with `python -m weather.weather` (from the package root or adjust PYTHONPATH) and invoke the tools with a client that speaks MCP (or add a tiny script that imports `mcp` and calls the registered tools).

## Security & privacy notes

- The code sends a `User-Agent` header only. No secrets are present.
- Avoid logging or returning raw API responses to end users in production; format and sanitize outputs.

## Where to start for a contributor

1. Read `weather.py` and run the module locally to see behavior.
2. Add tests under a `tests/` folder that mock HTTP responses.
3. Implement input validation and one of the small improvements above.

## Contact and references

- NWS API: https://api.weather.gov (use the API docs for response shape and field meanings)

-- End of instructions
