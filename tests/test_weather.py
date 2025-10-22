import asyncio
import importlib.util
from pathlib import Path

import pytest
import respx
from httpx import Response

# Dynamically load the weather module from file so tests run without installing the package
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("weather_mod", ROOT / "weather.py")
weather_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(weather_mod)


@respx.mock
def test_get_alerts_invalid_state():
    result = asyncio.run(weather_mod.get_alerts("California"))
    assert "Invalid state code" in result


@respx.mock
def test_get_alerts_no_data(monkeypatch):
    # Mock the NWS alerts endpoint to return 200 with empty features
    respx.get("https://api.weather.gov/alerts/active/area/CA").mock(
        return_value=Response(200, json={"features": []})
    )

    result = asyncio.run(weather_mod.get_alerts("CA"))
    assert result == "No active alerts for this state."


@respx.mock
def test_get_forecast_invalid_coords():
    result = asyncio.run(weather_mod.get_forecast("abc", "def"))
    assert "Invalid latitude/longitude" in result


@respx.mock
def test_get_forecast_out_of_range():
    result = asyncio.run(weather_mod.get_forecast(1000, 2000))
    assert "Latitude must be between" in result


@respx.mock
def test_get_forecast_success():
    # Mock points endpoint and forecast endpoint
    points_json = {
        "properties": {
            "forecast": "https://api.weather.gov/gridpoints/XXX/37,69/forecast"
        }
    }

    periods = [
        {
            "name": "Tonight",
            "temperature": 55,
            "temperatureUnit": "F",
            "windSpeed": "5 mph",
            "windDirection": "N",
            "detailedForecast": "Clear."
        }
    ]

    forecast_json = {"properties": {"periods": periods}}

    respx.get("https://api.weather.gov/points/37.0,-122.0").mock(return_value=Response(200, json=points_json))
    respx.get("https://api.weather.gov/gridpoints/XXX/37,69/forecast").mock(return_value=Response(200, json=forecast_json))

    result = asyncio.run(weather_mod.get_forecast(37.0, -122.0))
    assert "Tonight:" in result
    assert "Temperature: 55" in result
