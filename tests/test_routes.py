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

from datetime import datetime

import responses

import googlemaps
from . import TestCase


class RoutesTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_simple_compute_routes(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": [{"distanceMeters": 1000, "duration": "300s"}]}',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_routes("Sydney", "Melbourne")

        self.assertEqual(1, len(responses.calls))
        self.assertIn("key=%s" % self.key, responses.calls[0].request.url)
        self.assertIn("X-Goog-FieldMask", responses.calls[0].request.headers)

    @responses.activate
    def test_compute_routes_with_latlng(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": [{"distanceMeters": 1000, "duration": "300s"}]}',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_routes(
            origin=(-33.8688, 151.2093),
            destination=(-37.8136, 144.9631),
            travel_mode="DRIVE"
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("location", request_body)
        self.assertIn("latLng", request_body)

    @responses.activate
    def test_compute_routes_with_place_id(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": [{"distanceMeters": 1000, "duration": "300s"}]}',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_routes(
            origin="place_id:ChIJP3Sa8Le5EmsRUbMgbTF5HQs",
            destination="place_id:ChIJ90260r5kGjoR7A9BexBt8iI"
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("placeId", request_body)

    @responses.activate
    def test_compute_routes_with_intermediates(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": [{"distanceMeters": 5000, "duration": "600s"}]}',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_routes(
            origin="Sydney",
            destination="Melbourne",
            intermediates=["Canberra"]
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("intermediates", request_body)

    @responses.activate
    def test_compute_routes_with_routing_preference(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": [{"distanceMeters": 1000, "duration": "300s"}]}',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_routes(
            origin="Sydney",
            destination="Melbourne",
            travel_mode="DRIVE",
            routing_preference="TRAFFIC_AWARE"
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("TRAFFIC_AWARE", request_body)

    @responses.activate
    def test_compute_routes_with_custom_field_mask(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": [{"distanceMeters": 1000, "duration": "300s"}]}',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_routes(
            origin="Sydney",
            destination="Melbourne",
            field_mask="routes.distanceMeters,routes.duration"
        )

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(
            "routes.distanceMeters,routes.duration",
            responses.calls[0].request.headers["X-Goog-FieldMask"]
        )

    @responses.activate
    def test_compute_routes_with_departure_time(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes": [{"distanceMeters": 1000, "duration": "300s"}]}',
            status=200,
            content_type="application/json",
        )

        now = datetime.now()
        result = self.client.compute_routes(
            origin="Sydney",
            destination="Melbourne",
            departure_time=now
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("departureTime", request_body)

    @responses.activate
    def test_compute_route_matrix(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
            body='[{"originIndex": 0, "destinationIndex": 0, "distanceMeters": 1000, "duration": "300s"}]',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_route_matrix(
            origins=["Sydney"],
            destinations=["Melbourne"]
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("key=%s" % self.key, responses.calls[0].request.url)

    @responses.activate
    def test_compute_route_matrix_multiple(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
            body='[{"originIndex": 0, "destinationIndex": 0, "distanceMeters": 1000}, {"originIndex": 1, "destinationIndex": 0, "distanceMeters": 2000}]',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_route_matrix(
            origins=["Sydney", "Brisbane"],
            destinations=["Melbourne"],
            travel_mode="DRIVE"
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("origins", request_body)
        self.assertIn("destinations", request_body)

    @responses.activate
    def test_compute_route_matrix_with_latlng(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
            body='[{"originIndex": 0, "destinationIndex": 0, "distanceMeters": 1000}]',
            status=200,
            content_type="application/json",
        )

        result = self.client.compute_route_matrix(
            origins=[(-33.8688, 151.2093)],
            destinations=[(-37.8136, 144.9631)]
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("latLng", request_body)
