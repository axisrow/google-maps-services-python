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

"""Tests for the pollen module."""

import json

import responses

import googlemaps
from googlemaps import pollen
from googlemaps import exceptions
from . import GoogleMapsClientTestCase
from . import JsonApiExtractTestCase
from . import TestCase


class PollenTest(GoogleMapsClientTestCase):

    @responses.activate
    def test_current_pollen(self):
        responses.add(
            responses.GET,
            "https://pollen.googleapis.com/v1/forecast:lookup",
            body='{"dailyInfo": [{"pollenTypeInfo": []}]}',
            status=200,
            content_type="application/json",
        )

        result = self.client.current_pollen((40.0, -74.0))

        self.assertEqual(1, len(responses.calls))
        self.assertIn("pollenTypeInfo", result)

    @responses.activate
    def test_current_pollen_with_params(self):
        responses.add(
            responses.GET,
            "https://pollen.googleapis.com/v1/forecast:lookup",
            body='{"dailyInfo": [{"pollenTypeInfo": []}]}',
            status=200,
            content_type="application/json",
        )

        self.client.current_pollen(
            (40.0, -74.0),
            language_code="en",
            plants_description=True
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("days=1", responses.calls[0].request.url)
        self.assertIn("languageCode=en", responses.calls[0].request.url)
        self.assertIn("plantsDescription=True", responses.calls[0].request.url)

    @responses.activate
    def test_pollen_forecast(self):
        responses.add(
            responses.GET,
            "https://pollen.googleapis.com/v1/forecast:lookup",
            body='{"dailyInfo": []}',
            status=200,
            content_type="application/json",
        )

        self.client.pollen_forecast((40.0, -74.0), days=5)

        self.assertEqual(1, len(responses.calls))
        self.assertIn("days=5", responses.calls[0].request.url)

    @responses.activate
    def test_pollen_forecast_with_pagination(self):
        responses.add(
            responses.GET,
            "https://pollen.googleapis.com/v1/forecast:lookup",
            body='{"dailyInfo": [], "nextPageToken": "token123"}',
            status=200,
            content_type="application/json",
        )

        self.client.pollen_forecast(
            (40.0, -74.0),
            days=3,
            language_code="en",
            plants_description=False,
            page_size=10,
            page_token="prev_token"
        )

        self.assertEqual(1, len(responses.calls))
        url = responses.calls[0].request.url
        self.assertIn("days=3", url)
        self.assertIn("pageSize=10", url)
        self.assertIn("pageToken=prev_token", url)
        self.assertIn("languageCode=en", url)
        self.assertIn("plantsDescription=False", url)

    @responses.activate
    def test_pollen_heatmap_tile(self):
        responses.add(
            responses.GET,
            "https://pollen.googleapis.com/v1/mapTypes/TREE_UPI/heatmapTiles/10/20/30",
            body=b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            status=200,
            content_type="image/png",
        )

        result = self.client.pollen_heatmap_tile("TREE_UPI", 10, 20, 30)

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(result, b'\x89PNG\r\n\x1a\n\x00\x00\x00')

    @responses.activate
    def test_pollen_heatmap_tile_grass(self):
        responses.add(
            responses.GET,
            "https://pollen.googleapis.com/v1/mapTypes/GRASS_UPI/heatmapTiles/5/10/15",
            body=b'\x89PNG\r\n\x1a\n',
            status=200,
            content_type="image/png",
        )

        result = self.client.pollen_heatmap_tile("GRASS_UPI", 5, 10, 15)

        self.assertEqual(1, len(responses.calls))
        self.assertIn("GRASS_UPI", responses.calls[0].request.url)

    @responses.activate
    def test_pollen_heatmap_tile_error(self):
        responses.add(
            responses.GET,
            "https://pollen.googleapis.com/v1/mapTypes/TREE_UPI/heatmapTiles/10/20/30",
            status=403,
        )

        with self.assertRaises(exceptions.HTTPError):
            self.client.pollen_heatmap_tile("TREE_UPI", 10, 20, 30)

    def test_format_pollen_location_tuple(self):
        result = pollen._format_pollen_location((40.0, -74.0))
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_pollen_location_dict_lat_lng(self):
        result = pollen._format_pollen_location({"lat": 40.0, "lng": -74.0})
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_pollen_location_dict_latitude_longitude(self):
        result = pollen._format_pollen_location({"latitude": 40.0, "longitude": -74.0})
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_pollen_location_invalid(self):
        with self.assertRaises(ValueError):
            pollen._format_pollen_location("invalid")


class PollenExtractTest(JsonApiExtractTestCase):
    def test_extract_success(self):
        response = self.make_json_response(body={"pollenTypeInfo": []})
        result = pollen._pollen_extract(response)
        self.assertIn("pollenTypeInfo", result)

    def test_extract_http_error(self):
        self.assertApiHttpError(pollen._pollen_extract, body={})

    def test_extract_api_error_not_found(self):
        self.assertApiErrorStatus(
            pollen._pollen_extract,
            error_status="NOT_FOUND",
            message=None,
            status_code=404,
        )

    def test_current_pollen_empty_daily_info(self):
        response = self.make_json_response(body={})
        result = pollen._current_pollen_extract(response)
        self.assertEqual(result, {})


class PollenHeatmapTileTest(GoogleMapsClientTestCase, JsonApiExtractTestCase):

    def test_pollen_heatmap_tile_transport_error(self):
        """Test pollen_heatmap_tile with transport error."""
        from unittest.mock import patch

        with patch.object(self.client.session, 'get') as mock_get:
            mock_get.side_effect = Exception("Network error")

            with self.assertRaises(googlemaps.exceptions.TransportError):
                self.client.pollen_heatmap_tile("TREE_UPI", 10, 20, 30)

    def test_pollen_extract_transport_error(self):
        self.assertApiTransportError(pollen._pollen_extract)

    def test_extract_403_over_query_limit(self):
        self.assertApiOverQueryLimit(pollen._pollen_extract)

    def test_extract_api_error(self):
        """Test _pollen_extract with other API error."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 400
        response.json.return_value = {
            "error": {"status": "INVALID_ARGUMENT", "message": "Bad request"}
        }

        with self.assertRaises(exceptions.ApiError) as context:
            pollen._pollen_extract(response)

        self.assertEqual(context.exception.status, "INVALID_ARGUMENT")
        self.assertEqual(context.exception.message, "Bad request")

    def test_extract_json_decode_error(self):
        """Test _pollen_extract with invalid JSON."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 200
        response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)

        with self.assertRaises(exceptions.TransportError):
            pollen._pollen_extract(response)
