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

"""Tests for the air quality module."""

import json
from datetime import datetime

import responses

import googlemaps
from googlemaps import airquality
from googlemaps import exceptions
from . import TestCase


class AirQualityTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_current_air_quality(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/currentConditions:lookup",
            body='{"location": {"latitude": 40.0, "longitude": -74.0}, "index": {"code": "uaqi", "value": 50}}',
            status=200,
            content_type="application/json",
        )

        result = self.client.current_air_quality((40.0, -74.0))

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(result["index"]["code"], "uaqi")

    @responses.activate
    def test_current_air_quality_with_all_params(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/currentConditions:lookup",
            body='{"location": {"latitude": 40.0, "longitude": -74.0}}',
            status=200,
            content_type="application/json",
        )

        self.client.current_air_quality(
            (40.0, -74.0),
            extra_computations=["HEALTH_RECOMMENDATIONS", "DOMINANT_POLLUTANT_CONCENTRATION"],
            language_code="en",
            universal_aqi=True,
            aqi_scale="UAQI_IN_AQI"
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(body["location"]["latitude"], 40.0)
        self.assertEqual(body["extraComputations"], ["HEALTH_RECOMMENDATIONS", "DOMINANT_POLLUTANT_CONCENTRATION"])
        self.assertEqual(body["languageCode"], "en")
        self.assertTrue(body["universalAqi"])
        self.assertEqual(body["uaqiColorPalette"], "UAQI_IN_AQI")

    @responses.activate
    def test_air_quality_forecast(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/forecast:lookup",
            body='{"hourlyForecasts": []}',
            status=200,
            content_type="application/json",
        )

        start_time = datetime(2024, 1, 1, 0, 0, 0)
        end_time = datetime(2024, 1, 2, 0, 0, 0)

        self.client.air_quality_forecast(
            (40.0, -74.0),
            period=(start_time, end_time)
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertIn("period", body)
        self.assertEqual(body["period"]["startTime"], "2024-01-01T00:00:00Z")

    @responses.activate
    def test_air_quality_forecast_with_dict_period(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/forecast:lookup",
            body='{"hourlyForecasts": []}',
            status=200,
            content_type="application/json",
        )

        period = {
            "startTime": "2024-01-01T00:00:00Z",
            "endTime": "2024-01-02T00:00:00Z"
        }

        self.client.air_quality_forecast(
            (40.0, -74.0),
            period=period,
            page_size=24,
            page_token="token123"
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(body["period"]["startTime"], "2024-01-01T00:00:00Z")
        self.assertEqual(body["pageSize"], 24)
        self.assertEqual(body["pageToken"], "token123")

    @responses.activate
    def test_historical_air_quality(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/history:lookup",
            body='{"hours": []}',
            status=200,
            content_type="application/json",
        )

        start_time = datetime(2024, 1, 1, 0, 0, 0)
        end_time = datetime(2024, 1, 2, 0, 0, 0)

        self.client.historical_air_quality(
            (40.0, -74.0),
            period=(start_time, end_time)
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertIn("period", body)

    @responses.activate
    def test_historical_air_quality_with_dict_period(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/history:lookup",
            body='{"hours": []}',
            status=200,
            content_type="application/json",
        )

        period = {
            "startTime": "2024-01-01T00:00:00Z",
            "endTime": "2024-01-02T00:00:00Z"
        }

        self.client.historical_air_quality(
            (40.0, -74.0),
            period=period
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(body["period"]["startTime"], "2024-01-01T00:00:00Z")

    @responses.activate
    def test_air_quality_heatmap_tile(self):
        responses.add(
            responses.GET,
            "https://airquality.googleapis.com/v1/mapTypes/US_AQI/heatmapTiles/10/20/30",
            body=b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            status=200,
            content_type="image/png",
        )

        result = self.client.air_quality_heatmap_tile("US_AQI", 10, 20, 30)

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(result, b'\x89PNG\r\n\x1a\n\x00\x00\x00')

    @responses.activate
    def test_air_quality_heatmap_tile_error(self):
        responses.add(
            responses.GET,
            "https://airquality.googleapis.com/v1/mapTypes/US_AQI/heatmapTiles/10/20/30",
            status=404,
        )

        with self.assertRaises(exceptions.HTTPError):
            self.client.air_quality_heatmap_tile("US_AQI", 10, 20, 30)

    def test_format_location_tuple(self):
        result = airquality._format_location((40.0, -74.0))
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_location_list(self):
        result = airquality._format_location([40.0, -74.0])
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_location_dict_lat_lng(self):
        result = airquality._format_location({"lat": 40.0, "lng": -74.0})
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_location_dict_latitude_longitude(self):
        result = airquality._format_location({"latitude": 40.0, "longitude": -74.0})
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_location_invalid(self):
        with self.assertRaises(ValueError):
            airquality._format_location("invalid")


class AirQualityExtractTest(TestCase):
    def test_extract_success(self):
        """Test _airquality_extract with successful response."""
        import requests
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 200
        response.json.return_value = {"index": {"code": "uaqi"}}

        result = airquality._airquality_extract(response)
        self.assertEqual(result["index"]["code"], "uaqi")

    def test_extract_403_over_query_limit(self):
        """Test _airquality_extract with 403 status (OverQueryLimit)."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 403
        response.json.return_value = {"error": {"message": "Quota exceeded"}}

        with self.assertRaises(exceptions._OverQueryLimit):
            airquality._airquality_extract(response)

    def test_extract_api_error(self):
        """Test _airquality_extract with other API error."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 400
        response.json.return_value = {"error": {"message": "Bad request"}}

        with self.assertRaises(exceptions.ApiError):
            airquality._airquality_extract(response)

    def test_extract_json_decode_error(self):
        """Test _airquality_extract with invalid JSON."""
        from unittest.mock import Mock
        import json

        response = Mock()
        response.status_code = 200
        response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)

        with self.assertRaises(exceptions.TransportError):
            airquality._airquality_extract(response)


class AirQualityFormatTimeTest(TestCase):
    def test_format_time_string(self):
        result = airquality._format_time("2024-01-01T00:00:00Z")
        self.assertEqual(result, "2024-01-01T00:00:00Z")

    def test_format_time_datetime(self):
        dt = datetime(2024, 1, 1, 12, 30, 45)
        result = airquality._format_time(dt)
        self.assertEqual(result, "2024-01-01T12:30:45Z")
