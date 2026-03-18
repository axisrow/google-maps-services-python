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

"""Tests for the route optimization module."""

import json

import responses

import googlemaps
from googlemaps import route_optimization
from googlemaps import exceptions
from . import TestCase


class RouteOptimizationTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_optimize_tour_basic(self):
        responses.add(
            responses.POST,
            "https://routeoptimization.googleapis.com/v1/projects/my-project:optimizeTour",
            body='{"routes": []}',
            status=200,
            content_type="application/json",
        )

        model = {
            "shipments": [
                {
                    "pickup": {"arrivalLocation": {"latLng": {"latitude": 40.0, "longitude": -74.0}}},
                    "delivery": {"arrivalLocation": {"latLng": {"latitude": 41.0, "longitude": -75.0}}}
                }
            ],
            "vehicles": [
                {
                    "startLocation": {"latLng": {"latitude": 40.0, "longitude": -74.0}},
                    "endLocation": {"latLng": {"latitude": 40.0, "longitude": -74.0}}
                }
            ]
        }

        result = self.client.optimize_tour(
            parent="projects/my-project",
            model=model
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("routes", result)

    @responses.activate
    def test_optimize_tour_with_all_params(self):
        responses.add(
            responses.POST,
            "https://routeoptimization.googleapis.com/v1/projects/my-project:optimizeTour",
            body='{"routes": [], "metrics": {}}',
            status=200,
            content_type="application/json",
        )

        model = {
            "shipments": [],
            "vehicles": [],
            "globalStartTime": "2024-01-01T00:00:00Z",
            "globalEndTime": "2024-01-02T00:00:00Z"
        }

        self.client.optimize_tour(
            parent="projects/my-project",
            model=model,
            timeout="60s",
            populate_transition_polylines=True,
            allow_large_deadline_despite_interruption_risk=True,
            interpret_injected_solutions_using_model=False,
            cost_model="COST_MODEL_STATIC",
            search_mode="PARALLEL_SCH_FAST",
            geodesic_meters_per_second=10.0,
            max_interpolation_distance_meters=1000
        )

        self.assertEqual(1, len(responses.calls))
        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(body["timeout"], "60s")
        self.assertTrue(body["populateTransitionPolylines"])
        self.assertEqual(body["costModel"], "COST_MODEL_STATIC")
        self.assertEqual(body["searchMode"], "PARALLEL_SCH_FAST")
        self.assertEqual(body["geodesicMetersPerSecond"], 10.0)

    def test_optimize_tour_invalid_parent(self):
        model = {"shipments": [], "vehicles": []}

        with self.assertRaises(ValueError):
            self.client.optimize_tour(parent="invalid-format", model=model)

        with self.assertRaises(ValueError):
            self.client.optimize_tour(parent="", model=model)

    def test_optimize_tour_parent_without_projects_prefix(self):
        model = {"shipments": [], "vehicles": []}

        with self.assertRaises(ValueError):
            self.client.optimize_tour(parent="my-project", model=model)

    def test_format_ro_location_tuple(self):
        result = route_optimization._format_ro_location((40.0, -74.0))
        self.assertEqual(result, {"latLng": {"latitude": 40.0, "longitude": -74.0}})

    def test_format_ro_location_list(self):
        result = route_optimization._format_ro_location([40.0, -74.0])
        self.assertEqual(result, {"latLng": {"latitude": 40.0, "longitude": -74.0}})

    def test_format_ro_location_dict_lat_lng(self):
        result = route_optimization._format_ro_location({"lat": 40.0, "lng": -74.0})
        self.assertEqual(result, {"latLng": {"latitude": 40.0, "longitude": -74.0}})

    def test_format_ro_location_dict_latitude_longitude(self):
        result = route_optimization._format_ro_location({"latitude": 40.0, "longitude": -74.0})
        self.assertEqual(result, {"latLng": {"latitude": 40.0, "longitude": -74.0}})

    def test_format_ro_location_dict_with_latLng(self):
        location = {"latLng": {"latitude": 40.0, "longitude": -74.0}}
        result = route_optimization._format_ro_location(location)
        self.assertEqual(result, location)

    def test_format_ro_location_invalid(self):
        with self.assertRaises(ValueError):
            route_optimization._format_ro_location("invalid")


class RouteOptimizationExtractTest(TestCase):
    def test_extract_success(self):
        """Test _route_optimization_extract with successful response."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 200
        response.json.return_value = {"routes": []}

        result = route_optimization._route_optimization_extract(response)
        self.assertIn("routes", result)

    def test_extract_403_over_query_limit(self):
        """Test _route_optimization_extract with 403 status (OverQueryLimit)."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 403
        response.json.return_value = {"error": {"message": "Quota exceeded"}}

        with self.assertRaises(exceptions._OverQueryLimit):
            route_optimization._route_optimization_extract(response)

    def test_extract_api_error(self):
        """Test _route_optimization_extract with other API error."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 400
        response.json.return_value = {"error": {"message": "Bad request"}}

        with self.assertRaises(exceptions.ApiError):
            route_optimization._route_optimization_extract(response)

    def test_extract_json_decode_error(self):
        """Test _route_optimization_extract with invalid JSON."""
        from unittest.mock import Mock

        response = Mock()
        response.status_code = 200
        response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)

        with self.assertRaises(exceptions.TransportError):
            route_optimization._route_optimization_extract(response)
