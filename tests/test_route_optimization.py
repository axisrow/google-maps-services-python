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

"""Tests for the route_optimization module."""

import responses

import googlemaps
from . import TestCase


class RouteOptimizationTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_optimize_tour(self):
        responses.add(
            responses.POST,
            "https://routeoptimization.googleapis.com/v1/projects/test-project:optimizeTour",
            body='{"routes": [], "totalCost": 0}',
            status=200,
            content_type="application/json",
        )

        model = {
            "shipments": [
                {
                    "pickup": {"arrivalLocation": {"latLng": {"latitude": 37.7749, "longitude": -122.4194}}},
                    "delivery": {"arrivalLocation": {"latLng": {"latitude": 37.7849, "longitude": -122.4094}}}
                }
            ],
            "vehicles": [
                {
                    "startLocation": {"latLng": {"latitude": 37.7649, "longitude": -122.4294}},
                    "endLocation": {"latLng": {"latitude": 37.7649, "longitude": -122.4294}}
                }
            ]
        }

        result = self.client.optimize_tour(
            parent="projects/test-project",
            model=model
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("key=%s" % self.key, responses.calls[0].request.url)

    @responses.activate
    def test_optimize_tour_with_timeout(self):
        responses.add(
            responses.POST,
            "https://routeoptimization.googleapis.com/v1/projects/test-project:optimizeTour",
            body='{"routes": [], "totalCost": 0}',
            status=200,
            content_type="application/json",
        )

        model = {
            "shipments": [],
            "vehicles": []
        }

        result = self.client.optimize_tour(
            parent="projects/test-project",
            model=model,
            timeout="60s"
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("timeout", request_body)

    @responses.activate
    def test_optimize_tour_with_polylines(self):
        responses.add(
            responses.POST,
            "https://routeoptimization.googleapis.com/v1/projects/test-project:optimizeTour",
            body='{"routes": [{"transitions": []}], "totalCost": 0}',
            status=200,
            content_type="application/json",
        )

        model = {
            "shipments": [],
            "vehicles": []
        }

        result = self.client.optimize_tour(
            parent="projects/test-project",
            model=model,
            populate_transition_polylines=True
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("populateTransitionPolylines", request_body)
