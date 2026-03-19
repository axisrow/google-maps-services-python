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
from datetime import datetime

import responses

import googlemaps
from googlemaps import weather
from . import GoogleMapsClientTestCase
from . import JsonApiExtractTestCase
from . import TestCase


class WeatherTest(GoogleMapsClientTestCase):

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


class WeatherExtractTest(JsonApiExtractTestCase):
    def test_extract_success(self):
        response = self.make_json_response(body={"temperature": {"degrees": 20.0}})
        result = weather._weather_extract(response)
        self.assertIn("temperature", result)

    def test_extract_http_error(self):
        self.assertApiHttpError(weather._weather_extract, body={"temperature": {}})

    def test_extract_403_over_query_limit(self):
        self.assertApiOverQueryLimit(weather._weather_extract)

    def test_extract_api_error(self):
        self.assertApiErrorStatus(weather._weather_extract)

    def test_extract_json_decode_error(self):
        self.assertApiTransportError(weather._weather_extract)


class WeatherUtilityTest(TestCase):
    def test_parse_time_with_string(self):
        """Test _parse_time with string input."""
        result = weather._parse_time("2024-01-15T08:00:00Z")
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)

    def test_parse_time_with_datetime(self):
        """Test _parse_time with datetime input."""
        dt = datetime(2024, 1, 15, 8, 0, 0)
        result = weather._parse_time(dt)
        self.assertEqual(result, dt)

    def test_parse_time_invalid(self):
        """Test _parse_time with invalid input."""
        with self.assertRaises(ValueError):
            weather._parse_time(12345)

    def test_period_to_size_with_tuple(self):
        """Test _period_to_size with tuple period."""
        period = ("2024-01-01T00:00:00Z", "2024-01-01T02:00:00Z")
        result = weather._period_to_size(period, 3600)  # hourly
        self.assertEqual(result, 2)

    def test_period_to_size_invalid_format(self):
        """Test _period_to_size with invalid format (not tuple/dict)."""
        with self.assertRaises(ValueError):
            weather._period_to_size("invalid", 3600)

    def test_period_to_size_missing_times(self):
        """Test _period_to_size with missing startTime/endTime."""
        with self.assertRaises(ValueError):
            weather._period_to_size({"startTime": "2024-01-01T00:00:00Z"}, 3600)

    def test_period_to_size_negative_duration(self):
        """Test _period_to_size with endTime before startTime."""
        with self.assertRaises(ValueError):
            weather._period_to_size({
                "startTime": "2024-01-02T00:00:00Z",
                "endTime": "2024-01-01T00:00:00Z"
            }, 3600)
