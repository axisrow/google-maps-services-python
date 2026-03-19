#
# Copyright 2024 Google Inc. All rights reserved.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

"""Tests for the weather module."""

import json

import responses

import googlemaps
from googlemaps import weather
from googlemaps import exceptions
from . import TestCase


class WeatherTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_current_weather(self):
        responses.add(
            responses.GET,
            "https://weather.googleapis.com/v1/currentConditions:lookup",
            body='{"location": {"latitude": 40.0, "longitude": -74.0}, "temperature": {"degrees": 20.0}}',
            status=200,
            content_type="application/json",
        )

        result = self.client.current_weather((40.0, -74.0))

        self.assertEqual(1, len(responses.calls))
        self.assertIn("temperature", result)

    @responses.activate
    def test_current_weather_with_all_params(self):
        responses.add(
            responses.GET,
            "https://weather.googleapis.com/v1/currentConditions:lookup",
            body='{"location": {"latitude": 40.0, "longitude": -74.0}}',
            status=200,
            content_type="application/json",
        )

        self.client.current_weather(
            (40.0, -74.0),
            weather_elements=["temperature", "humidity", "windSpeed"],
            extra_computations=["precipitation_probability"],
            language_code="en",
            units="METRIC"
        )

        self.assertEqual(1, len(responses.calls))
        url = responses.calls[0].request.url
        self.assertIn("languageCode=en", url)
        self.assertIn("unitsSystem=METRIC", url)

    @responses.activate
    def test_current_weather_imperial_units(self):
        responses.add(
            responses.GET,
            "https://weather.googleapis.com/v1/currentConditions:lookup",
            body='{"location": {"latitude": 40.0, "longitude": -74.0}}',
            status=200,
            content_type="application/json",
        )

        self.client.current_weather((40.0, -74.0), units="IMPERIAL")

        self.assertEqual(1, len(responses.calls))
        self.assertIn("unitsSystem=IMPERIAL", responses.calls[0].request.url)

    @responses.activate
    def test_weather_forecast(self):
        responses.add(
            responses.GET,
            "https://weather.googleapis.com/v1/forecast/days:lookup",
            body='{"forecastDays": []}',
            status=200,
            content_type="application/json",
        )

        period = {
            "startTime": "2024-01-01T00:00:00Z",
            "endTime": "2024-01-03T00:00:00Z"
        }

        self.client.weather_forecast((40.0, -74.0), period=period)

        self.assertEqual(1, len(responses.calls))
        self.assertIn("days=2", responses.calls[0].request.url)

    @responses.activate
    def test_weather_forecast_with_pagination(self):
        responses.add(
            responses.GET,
            "https://weather.googleapis.com/v1/forecast/days:lookup",
            body='{"forecastDays": [], "nextPageToken": "token123"}',
            status=200,
            content_type="application/json",
        )

        self.client.weather_forecast(
            (40.0, -74.0),
            weather_elements=["temperature"],
            page_size=24,
            page_token="prev_token"
        )

        self.assertEqual(1, len(responses.calls))
        url = responses.calls[0].request.url
        self.assertIn("pageSize=24", url)
        self.assertIn("pageToken=prev_token", url)

    @responses.activate
    def test_weather_hourly_forecast(self):
        responses.add(
            responses.GET,
            "https://weather.googleapis.com/v1/forecast/hours:lookup",
            body='{"hours": []}',
            status=200,
            content_type="application/json",
        )

        self.client.weather_hourly_forecast((40.0, -74.0))

        self.assertEqual(1, len(responses.calls))
        self.assertIn("forecast/hours:lookup", responses.calls[0].request.url)

    @responses.activate
    def test_weather_hourly_forecast_with_params(self):
        responses.add(
            responses.GET,
            "https://weather.googleapis.com/v1/forecast/hours:lookup",
            body='{"hours": []}',
            status=200,
            content_type="application/json",
        )

        period = {
            "startTime": "2024-01-01T00:00:00Z",
            "endTime": "2024-01-01T12:00:00Z"
        }

        self.client.weather_hourly_forecast(
            (40.0, -74.0),
            weather_elements=["temperature", "windSpeed"],
            language_code="en",
            units="METRIC",
            period=period,
            page_size=12
        )

        self.assertEqual(1, len(responses.calls))
        url = responses.calls[0].request.url
        self.assertIn("hours=12", url)
        self.assertIn("languageCode=en", url)
        self.assertIn("unitsSystem=METRIC", url)
        self.assertIn("pageSize=12", url)

    @responses.activate
    def test_historical_weather(self):
        responses.add(
            responses.GET,
            "https://weather.googleapis.com/v1/history/hours:lookup",
            body='{"hours": []}',
            status=200,
            content_type="application/json",
        )

        period = {
            "startTime": "2023-12-01T00:00:00Z",
            "endTime": "2023-12-02T00:00:00Z"
        }

        self.client.historical_weather((40.0, -74.0), period=period)

        self.assertEqual(1, len(responses.calls))
        self.assertIn("hours=24", responses.calls[0].request.url)

    @responses.activate
    def test_historical_weather_with_all_params(self):
        responses.add(
            responses.GET,
            "https://weather.googleapis.com/v1/history/hours:lookup",
            body='{"hours": []}',
            status=200,
            content_type="application/json",
        )

        period = {
            "startTime": "2023-12-01T00:00:00Z",
            "endTime": "2023-12-02T00:00:00Z"
        }

        self.client.historical_weather(
            (40.0, -74.0),
            period=period,
            weather_elements=["temperature"],
            extra_computations=["uv_index"],
            language_code="en",
            units="IMPERIAL",
            page_size=48,
            page_token="token"
        )

        self.assertEqual(1, len(responses.calls))
        url = responses.calls[0].request.url
        self.assertIn("hours=24", url)
        self.assertIn("unitsSystem=IMPERIAL", url)
        self.assertIn("languageCode=en", url)
        self.assertIn("pageSize=48", url)
        self.assertIn("pageToken=token", url)

    def test_format_weather_location_tuple(self):
        result = weather._format_weather_location((40.0, -74.0))
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_weather_location_list(self):
        result = weather._format_weather_location([40.0, -74.0])
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_weather_location_dict_lat_lng(self):
        result = weather._format_weather_location({"lat": 40.0, "lng": -74.0})
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_weather_location_dict_latitude_longitude(self):
        result = weather._format_weather_location({"latitude": 40.0, "longitude": -74.0})
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_weather_location_invalid(self):
        with self.assertRaises(ValueError):
            weather._format_weather_location("invalid")


class WeatherExtractTest(TestCase):
    def test_extract_success(self):
        """Test _weather_extract with successful response."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 200
        response.json.return_value = {"temperature": {"degrees": 20.0}}

        result = weather._weather_extract(response)
        self.assertIn("temperature", result)

    def test_extract_403_over_query_limit(self):
        """Test _weather_extract with 403 status (OverQueryLimit)."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 403
        response.json.return_value = {
            "error": {"status": "RESOURCE_EXHAUSTED", "message": "Quota exceeded"}
        }

        with self.assertRaises(exceptions._OverQueryLimit) as context:
            weather._weather_extract(response)

        self.assertEqual(context.exception.status, "RESOURCE_EXHAUSTED")
        self.assertEqual(context.exception.message, "Quota exceeded")

    def test_extract_api_error(self):
        """Test _weather_extract with other API error."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 400
        response.json.return_value = {
            "error": {"status": "INVALID_ARGUMENT", "message": "Bad request"}
        }

        with self.assertRaises(exceptions.ApiError) as context:
            weather._weather_extract(response)

        self.assertEqual(context.exception.status, "INVALID_ARGUMENT")
        self.assertEqual(context.exception.message, "Bad request")

    def test_extract_json_decode_error(self):
        """Test _weather_extract with invalid JSON."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 200
        response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)

        with self.assertRaises(exceptions.TransportError):
            weather._weather_extract(response)
