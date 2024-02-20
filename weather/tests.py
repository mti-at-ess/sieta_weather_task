import pytest
from django.test import Client
from unittest.mock import patch
from rest_framework import status
from django.urls import reverse
import pandas as pd


# Fixture providing sample weather data.
@pytest.fixture
def weather_data():
    """
    Fixture providing sample weather data.
    """
    return {
        "event_start": [
            "2020-11-01 00:00:00+00",
            "2020-11-01 00:00:00+00",
            "2020-11-01 00:00:00+00",
            "2020-11-01 00:00:00+00",
            "2020-11-01 00:00:00+00",
            "2020-11-01 00:00:00+00",
            "2020-11-01 00:00:00+00",
            "2020-11-01 00:00:00+00",
            "2020-11-01 00:00:00+00",
            "2020-11-01 00:00:00+00",
        ],
        "belief_horizon_in_sec": [
            -637,
            35362,
            38960,
            28162,
            2969,
            20971,
            13775,
            17374,
            10171,
            6570,
        ],
        "event_value": [
            11.36,
            11.06,
            11.41,
            11.25,
            11.39,
            11.65,
            11.51,
            11.61,
            11.5,
            11.47,
        ],
        "sensor": [
            "temperature",
            "temperature",
            "temperature",
            "temperature",
            "temperature",
            "temperature",
            "irradiance",
            "irradiance",
            "wind_speed",
            "wind_speed"
        ],
        "unit": [
            "°C",
            "°C",
            "°C",
            "°C",
            "°C",
            "°C",
            "W/m^2",
            "W/m^2",
            "m/s",
            "m/s"
        ],
    }

# You can use this fixture in your tests to generate sample weather data.


# Fixture providing sample weather data for tomorrow.
@pytest.fixture
def tomorrow_weather_data():
    return {
        "event_start": ["2020-11-02 00:00:00+00", "2020-11-02 00:00:00+00"],
        "belief_horizon_in_sec": [3600, 7200],
        "event_value": [25, 800],
        "sensor": ["temperature", "irradiance"],
        "unit": [
            "°C",
            None,  # Since unit is not specified for irradiance in the provided format
        ],
    }


# Test cases for WeatherViewSet.
class TestWeatherViewSet:
    client = Client()

    # Test for getting weather forecast.
    @patch("weather.views.pd.read_csv")
    def test_get_forecast(self, mock_read_csv, weather_data):
        mock_read_csv.return_value = pd.DataFrame(weather_data)
        url = reverse("forecast")

        response = self.client.get(
            url, {"now": "2020-11-01T00:00:00.0000", "then": "2020-11-02T00:00:00.0000"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["temperature"]["event_value"] == 11.36

    # Test for getting forecast for tomorrow.
    @patch("weather.views.pd.read_csv")
    def test_get_tomorrow_forecast(self, mock_read_csv, tomorrow_weather_data):
        mock_read_csv.return_value = pd.DataFrame(tomorrow_weather_data)
        url = reverse("tomorrow_forecast")

        response = self.client.get(url, {"now": "2020-11-01T00:00:00.0000"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_warm"]
        assert response.json()["is_sunny"]
        assert not response.json()["is_windy"]
