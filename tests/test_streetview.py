#
# Copyright 2026 Google Inc. All rights reserved.
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

"""Tests for the Street View Static API module."""

from types import GeneratorType

import responses

import googlemaps
from . import TestCase


class StreetViewTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_street_view_download(self):
        url = "https://maps.googleapis.com/maps/api/streetview"
        responses.add(responses.GET, url, status=200)

        response = self.client.street_view(
            size=(400, 400),
            location=(40.6892, -74.0445),
            heading=120,
            pitch=5,
            fov=80,
            radius=50,
            source="outdoor",
        )

        self.assertTrue(isinstance(response, GeneratorType))
        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "%s?size=400x400&location=40.6892%%2C-74.0445&heading=120&pitch=5&"
            "fov=80&radius=50&source=outdoor&key=%s" % (url, self.key),
            responses.calls[0].request.url,
        )

    def test_street_view_requires_location_or_pano(self):
        with self.assertRaises(ValueError):
            self.client.street_view(size=(400, 400))

    def test_street_view_rejects_invalid_source(self):
        with self.assertRaises(ValueError):
            self.client.street_view(
                size=(400, 400),
                location=(40.6892, -74.0445),
                source="indoor",
            )
