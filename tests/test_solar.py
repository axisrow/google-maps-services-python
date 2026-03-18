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

import responses

import googlemaps
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

        result = self.client.building_insights((37.7749, -122.4194))

        self.assertEqual(1, len(responses.calls))
        self.assertIn("key=%s" % self.key, responses.calls[0].request.url)
        self.assertIn("location.latitude", responses.calls[0].request.url)

    @responses.activate
    def test_building_insights_with_quality(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/buildingInsights:findClosest",
            body='{"solarPotential": {"maxArrayPanelsCount": 100}}',
            status=200,
            content_type="application/json",
        )

        result = self.client.building_insights(
            (37.7749, -122.4194),
            required_quality="HIGH"
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("requiredQuality=HIGH", responses.calls[0].request.url)

    @responses.activate
    def test_solar_data_layers(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/dataLayers:get",
            body='{"imageryDate": "2023-01-01", "imageryProcessedDate": "2023-01-02"}',
            status=200,
            content_type="application/json",
        )

        result = self.client.solar_data_layers((37.7749, -122.4194))

        self.assertEqual(1, len(responses.calls))
        self.assertIn("key=%s" % self.key, responses.calls[0].request.url)
        self.assertIn("location.latitude", responses.calls[0].request.url)

    @responses.activate
    def test_solar_data_layers_with_options(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/dataLayers:get",
            body='{"imageryDate": "2023-01-01"}',
            status=200,
            content_type="application/json",
        )

        result = self.client.solar_data_layers(
            (37.7749, -122.4194),
            required_quality="HIGH",
            pixel_size_meters=500
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("requiredQuality=HIGH", responses.calls[0].request.url)
        self.assertIn("pixelSizeMeters=500", responses.calls[0].request.url)
