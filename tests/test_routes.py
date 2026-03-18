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

"""Tests for the routes module."""

import json
from datetime import datetime

import responses

import googlemaps
from googlemaps import routes
from googlemaps import exceptions
from . import TestCase


class RoutesTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_compute_routes_basic(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": [{"distanceMeters": 1000, "duration": "300s"}]}',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_routes(
            origin=(40.7128, -74.0060),
            destination=(34.0522, -118.2437)
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("routes", result)

    @responses.activate
    def test_compute_routes_with_address(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": []}',
            status=200,
            content_type="application/json",
        )

        self.client.compute_routes(
            origin="New York, NY",
            destination="Los Angeles, CA"
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(body["origin"]["address"], "New York, NY")
        self.assertEqual(body["destination"]["address"], "Los Angeles, CA")

    @responses.activate
    def test_compute_routes_with_place_id(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": []}',
            status=200,
            content_type="application/json",
        )

        self.client.compute_routes(
            origin="place_id:ChIJOwg_06VPwokRYv534QaPC8g",
            destination="place_id:ChIJE9on3F3HwoAR9AhGJW_fL-I"
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(body["origin"]["placeId"], "ChIJOwg_06VPwokRYv534QaPC8g")

    @responses.activate
    def test_compute_routes_with_intermediates(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": []}',
            status=200,
            content_type="application/json",
        )

        self.client.compute_routes(
            origin=(40.7128, -74.0060),
            destination=(34.0522, -118.2437),
            intermediates=[(41.8781, -87.6298), (39.7392, -104.9903)]
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(len(body["intermediates"]), 2)

    @responses.activate
    def test_compute_routes_with_travel_mode(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": []}',
            status=200,
            content_type="application/json",
        )

        self.client.compute_routes(
            origin=(40.7128, -74.0060),
            destination=(34.0522, -118.2437),
            travel_mode="DRIVE"
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(body["travelMode"], "DRIVE")

    @responses.activate
    def test_compute_routes_with_all_params(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": []}',
            status=200,
            content_type="application/json",
        )

        departure = datetime(2024, 1, 15, 8, 0, 0)

        self.client.compute_routes(
            origin=(40.7128, -74.0060),
            destination=(34.0522, -118.2437),
            travel_mode="DRIVE",
            routing_preference="TRAFFIC_AWARE",
            polyline_quality="HIGH_QUALITY",
            polyline_encoding="ENCODED_POLYLINE",
            departure_time=departure,
            compute_alternative_routes=True,
            route_modifiers={"avoidTolls": True, "avoidHighways": False},
            language_code="en-US",
            region_code="us",
            units="IMPERIAL",
            optimize_waypoint_order=True,
            traffic_model="BEST_GUESS",
            field_mask="routes.duration,routes.distanceMeters"
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(body["travelMode"], "DRIVE")
        self.assertEqual(body["routingPreference"], "TRAFFIC_AWARE")
        self.assertEqual(body["departureTime"], "2024-01-15T08:00:00Z")
        self.assertTrue(body["computeAlternativeRoutes"])
        self.assertEqual(body["routeModifiers"]["avoidTolls"], True)

        # Check headers
        headers = responses.calls[0].request.headers
        self.assertIn("X-Goog-FieldMask", headers)

    @responses.activate
    def test_compute_routes_with_transit_preferences(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": []}',
            status=200,
            content_type="application/json",
        )

        self.client.compute_routes(
            origin=(40.7128, -74.0060),
            destination=(34.0522, -118.2437),
            travel_mode="TRANSIT",
            transit_preferences={"routingPreference": "LESS_WALKING"}
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(body["transitPreferences"]["routingPreference"], "LESS_WALKING")

    @responses.activate
    def test_compute_route_matrix(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
            body='[{"originIndex": 0, "destinationIndex": 0, "distanceMeters": 1000}]',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_route_matrix(
            origins=[(40.7128, -74.0060)],
            destinations=[(34.0522, -118.2437)]
        )

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(result[0]["distanceMeters"], 1000)

    @responses.activate
    def test_compute_route_matrix_multiple(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
            body='[{"originIndex": 0, "destinationIndex": 0, "distanceMeters": 1000}, '
                 '{"originIndex": 0, "destinationIndex": 1, "distanceMeters": 2000}]',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_route_matrix(
            origins=[(40.7128, -74.0060)],
            destinations=[(34.0522, -118.2437), (41.8781, -87.6298)]
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(len(body["origins"]), 1)
        self.assertEqual(len(body["destinations"]), 2)

    @responses.activate
    def test_compute_route_matrix_with_route_modifiers(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
            body='[]',
            status=200,
            content_type="application/json",
        )

        self.client.compute_route_matrix(
            origins=[{"waypoint": (40.7128, -74.0060), "routeModifiers": {"avoidTolls": True}}],
            destinations=[(34.0522, -118.2437)],
            travel_mode="DRIVE"
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertIn("routeModifiers", body["origins"][0])

    def test_format_waypoint_string_address(self):
        result = routes._format_waypoint("New York, NY")
        self.assertEqual(result, {"address": "New York, NY"})

    def test_format_waypoint_string_place_id(self):
        result = routes._format_waypoint("place_id:ChIJOwg_06VPwokRYv534QaPC8g")
        self.assertEqual(result, {"placeId": "ChIJOwg_06VPwokRYv534QaPC8g"})

    def test_format_waypoint_tuple(self):
        result = routes._format_waypoint((40.7128, -74.0060))
        self.assertEqual(result, {"location": {"latLng": {"latitude": 40.7128, "longitude": -74.0060}}})

    def test_format_waypoint_dict_lat_lng(self):
        result = routes._format_waypoint({"lat": 40.7128, "lng": -74.0060})
        self.assertEqual(result, {"location": {"latLng": {"latitude": 40.7128, "longitude": -74.0060}}})

    def test_format_waypoint_dict_with_location(self):
        waypoint = {"location": {"latLng": {"latitude": 40.7128, "longitude": -74.0060}}}
        result = routes._format_waypoint(waypoint)
        self.assertEqual(result, waypoint)

    def test_format_waypoint_dict_with_place_id(self):
        waypoint = {"placeId": "ChIJOwg_06VPwokRYv534QaPC8g"}
        result = routes._format_waypoint(waypoint)
        self.assertEqual(result, waypoint)

    def test_format_waypoint_invalid(self):
        with self.assertRaises(ValueError):
            routes._format_waypoint(12345)

    def test_format_time_string(self):
        result = routes._format_time("2024-01-15T08:00:00Z")
        self.assertEqual(result, "2024-01-15T08:00:00Z")

    def test_format_time_datetime(self):
        dt = datetime(2024, 1, 15, 8, 0, 0)
        result = routes._format_time(dt)
        self.assertEqual(result, "2024-01-15T08:00:00Z")

    def test_format_time_none_raises_error(self):
        with self.assertRaises(ValueError):
            routes._format_time(None)


class RoutesExtractTest(TestCase):
    def test_extract_success(self):
        """Test _routes_extract with successful response."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 200
        response.json.return_value = {"routes": []}

        result = routes._routes_extract(response)
        self.assertIn("routes", result)

    def test_extract_403_over_query_limit(self):
        """Test _routes_extract with 403 status (OverQueryLimit)."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 403
        response.json.return_value = {"error": {"message": "Quota exceeded"}}

        with self.assertRaises(exceptions._OverQueryLimit):
            routes._routes_extract(response)

    def test_extract_api_error(self):
        """Test _routes_extract with other API error."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 400
        response.json.return_value = {"error": {"message": "Bad request"}}

        with self.assertRaises(exceptions.ApiError):
            routes._routes_extract(response)

    def test_extract_json_decode_error(self):
        """Test _routes_extract with invalid JSON."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 200
        response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)

        with self.assertRaises(exceptions.TransportError):
            routes._routes_extract(response)
