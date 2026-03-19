# This Python file uses the following encoding: utf-8
#
# Copyright 2017 Google Inc. All rights reserved.
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

"""Tests for the geocolation module."""

import responses

import googlemaps
from googlemaps import geolocation
from googlemaps import exceptions
from . import TestCase


class GeolocationTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_simple_geolocate(self):
        responses.add(
            responses.POST,
            "https://www.googleapis.com/geolocation/v1/geolocate",
            body='{"location": {"lat": 51.0,"lng": -0.1},"accuracy": 1200.4}',
            status=200,
            content_type="application/json",
        )

        results = self.client.geolocate()

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://www.googleapis.com/geolocation/v1/geolocate?" "key=%s" % self.key,
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_geolocate_with_all_params(self):
        responses.add(
            responses.POST,
            "https://www.googleapis.com/geolocation/v1/geolocate",
            body='{"location": {"lat": 51.0,"lng": -0.1},"accuracy": 1200.4}',
            status=200,
            content_type="application/json",
        )

        results = self.client.geolocate(
            home_mobile_country_code="310",
            home_mobile_network_code="260",
            radio_type="gsm",
            carrier="T-Mobile",
            consider_ip=True,
            cell_towers=[
                {
                    "cellId": 42,
                    "locationAreaCode": 415,
                    "mobileCountryCode": 310,
                    "mobileNetworkCode": 260
                }
            ],
            wifi_access_points=[
                {
                    "macAddress": "00:25:9c:cf:1c:ac",
                    "signalStrength": -43,
                    "channel": 11
                }
            ]
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("location", results)

    @responses.activate
    def test_geolocate_with_wifi_access_points(self):
        responses.add(
            responses.POST,
            "https://www.googleapis.com/geolocation/v1/geolocate",
            body='{"location": {"lat": 51.0,"lng": -0.1},"accuracy": 100}',
            status=200,
            content_type="application/json",
        )

        results = self.client.geolocate(
            wifi_access_points=[
                {"macAddress": "00:25:9c:cf:1c:ac"},
                {"macAddress": "00:25:9c:cf:1c:ad"}
            ]
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("location", results)

    @responses.activate
    def test_geolocate_with_cell_towers(self):
        responses.add(
            responses.POST,
            "https://www.googleapis.com/geolocation/v1/geolocate",
            body='{"location": {"lat": 51.0,"lng": -0.1},"accuracy": 1000}',
            status=200,
            content_type="application/json",
        )

        results = self.client.geolocate(
            cell_towers=[
                {
                    "cellId": 42,
                    "locationAreaCode": 415,
                    "mobileCountryCode": 310,
                    "mobileNetworkCode": 260
                }
            ]
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("location", results)

    @responses.activate
    def test_geolocate_consider_ip_false(self):
        responses.add(
            responses.POST,
            "https://www.googleapis.com/geolocation/v1/geolocate",
            body='{"location": {"lat": 51.0,"lng": -0.1},"accuracy": 2000}',
            status=200,
            content_type="application/json",
        )

        results = self.client.geolocate(consider_ip=False)

        self.assertEqual(1, len(responses.calls))
        self.assertIn("location", results)


class GeolocationExtractTest(TestCase):
    def test_extract_success(self):
        """Test _geolocation_extract with successful response."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 200
        response.json.return_value = {"location": {"lat": 51.0, "lng": -0.1}, "accuracy": 1200.4}

        result = geolocation._geolocation_extract(response)
        self.assertIn("location", result)

    def test_extract_404_not_found(self):
        """Test _geolocation_extract with 404 status (returns body)."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 404
        response.json.return_value = {"error": {"errors": [{"reason": "notFound"}]}}

        # 404 returns the body in geolocation API
        result = geolocation._geolocation_extract(response)
        self.assertIn("error", result)

    def test_extract_403_over_query_limit(self):
        """Test _geolocation_extract with 403 status (OverQueryLimit)."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 403
        response.json.return_value = {"error": {"errors": [{"reason": "rateLimitExceeded"}]}}

        with self.assertRaises(exceptions._OverQueryLimit):
            geolocation._geolocation_extract(response)

    def test_extract_api_error(self):
        """Test _geolocation_extract with other API error."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 400
        response.json.return_value = {"error": {"errors": [{"reason": "invalidRequest"}]}}

        with self.assertRaises(exceptions.ApiError):
            geolocation._geolocation_extract(response)

    def test_extract_api_error_no_reason(self):
        """Test _geolocation_extract with API error without reason."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 500
        response.json.return_value = {"error": {}}

        with self.assertRaises(exceptions.ApiError) as context:
            geolocation._geolocation_extract(response)

        # status_code is passed as status when no reason found
        self.assertEqual(context.exception.status, 500)
        self.assertIsNone(context.exception.message)
