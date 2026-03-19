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

"""Tests for the solar module."""

import json

import responses

import googlemaps
from googlemaps import solar
from googlemaps import exceptions
from . import TestCase


class SolarTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_building_insights(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/buildingInsights:findClosest",
            body='{"solarPotential": {"maxArrayPanelsCount": 100}}',
            status=200,
            content_type="application/json",
        )

        result = self.client.building_insights((40.0, -74.0))

        self.assertEqual(1, len(responses.calls))
        self.assertIn("solarPotential", result)

    @responses.activate
    def test_building_insights_with_required_quality(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/buildingInsights:findClosest",
            body='{"solarPotential": {}}',
            status=200,
            content_type="application/json",
        )

        self.client.building_insights((40.0, -74.0), required_quality="HIGH")

        self.assertEqual(1, len(responses.calls))
        self.assertIn("requiredQuality=HIGH", responses.calls[0].request.url)

    @responses.activate
    def test_solar_data_layers(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/dataLayers:get",
            body='{"imageryDate": {"year": 2023}, "rgbUrl": "https://example.com/rgb"}',
            status=200,
            content_type="application/json",
        )

        result = self.client.solar_data_layers((40.0, -74.0))

        self.assertEqual(1, len(responses.calls))
        self.assertIn("imageryDate", result)

    @responses.activate
    def test_solar_data_layers_with_all_params(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/dataLayers:get",
            body='{"rgbUrl": "https://example.com/rgb"}',
            status=200,
            content_type="application/json",
        )

        self.client.solar_data_layers(
            (40.0, -74.0),
            required_quality="MEDIUM",
            pixel_size_meters=500,
            view="FULL_DATASET"
        )

        self.assertEqual(1, len(responses.calls))
        url = responses.calls[0].request.url
        self.assertIn("radiusMeters=100", url)
        self.assertIn("requiredQuality=MEDIUM", url)
        self.assertIn("pixelSizeMeters=500", url)
        self.assertIn("view=FULL_LAYERS", url)

    @responses.activate
    def test_geo_tiff(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/geoTiff:get",
            body=b'\x00\x01\x02\x03',
            status=200,
            content_type="image/tiff",
        )

        result = self.client.geo_tiff("https://solar.googleapis.com/v1/geoTiff:get?id=test-asset")

        self.assertEqual(1, len(responses.calls))
        self.assertIn("id=test-asset", responses.calls[0].request.url)
        self.assertEqual(result, b'\x00\x01\x02\x03')

    def test_geo_tiff_invalid_url_empty(self):
        with self.assertRaises(ValueError):
            self.client.geo_tiff("")

    def test_geo_tiff_invalid_url_wrong_domain(self):
        with self.assertRaises(ValueError):
            self.client.geo_tiff("https://evil.com/geoTiff")

    def test_geo_tiff_invalid_url_http(self):
        with self.assertRaises(ValueError):
            self.client.geo_tiff("http://solar.googleapis.com/v1/geoTiff:get?id=test")

    def test_geo_tiff_invalid_url_username(self):
        with self.assertRaises(ValueError):
            self.client.geo_tiff("https://solar.googleapis.com@evil.com/v1/geoTiff:get?id=test")

    def test_geo_tiff_invalid_url_subdomain(self):
        with self.assertRaises(ValueError):
            self.client.geo_tiff("https://solar.googleapis.com.evil.com/v1/geoTiff:get?id=test")

    def test_geo_tiff_invalid_url_missing_id(self):
        with self.assertRaises(ValueError):
            self.client.geo_tiff("https://solar.googleapis.com/v1/geoTiff:get")

    @responses.activate
    def test_geo_tiff_error(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/geoTiff:get",
            status=404,
        )

        with self.assertRaises(exceptions.HTTPError):
            self.client.geo_tiff("https://solar.googleapis.com/v1/geoTiff:get?id=test-asset")

    def test_format_solar_location_tuple(self):
        result = solar._format_solar_location((40.0, -74.0))
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_solar_location_list(self):
        result = solar._format_solar_location([40.0, -74.0])
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_solar_location_dict_lat_lng(self):
        result = solar._format_solar_location({"lat": 40.0, "lng": -74.0})
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_solar_location_dict_latitude_longitude(self):
        result = solar._format_solar_location({"latitude": 40.0, "longitude": -74.0})
        self.assertEqual(result, {"latitude": 40.0, "longitude": -74.0})

    def test_format_solar_location_invalid(self):
        with self.assertRaises(ValueError):
            solar._format_solar_location("invalid")


class SolarExtractTest(TestCase):
    def test_extract_success(self):
        """Test _solar_extract with successful response."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 200
        response.json.return_value = {"solarPotential": {}}

        result = solar._solar_extract(response)
        self.assertIn("solarPotential", result)

    def test_extract_403_over_query_limit(self):
        """Test _solar_extract with 403 status (OverQueryLimit)."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 403
        response.json.return_value = {
            "error": {"status": "RESOURCE_EXHAUSTED", "message": "Quota exceeded"}
        }

        with self.assertRaises(exceptions._OverQueryLimit) as context:
            solar._solar_extract(response)

        self.assertEqual(context.exception.status, "RESOURCE_EXHAUSTED")
        self.assertEqual(context.exception.message, "Quota exceeded")

    def test_extract_api_error(self):
        """Test _solar_extract with other API error."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 400
        response.json.return_value = {
            "error": {"status": "INVALID_ARGUMENT", "message": "Bad request"}
        }

        with self.assertRaises(exceptions.ApiError) as context:
            solar._solar_extract(response)

        self.assertEqual(context.exception.status, "INVALID_ARGUMENT")
        self.assertEqual(context.exception.message, "Bad request")

    def test_extract_json_decode_error(self):
        """Test _solar_extract with invalid JSON."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 200
        response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)

        with self.assertRaises(exceptions.TransportError):
            solar._solar_extract(response)
