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

import responses

import googlemaps
from . import TestCase


class PollenTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_current_pollen(self):
        responses.add(
            responses.POST,
            "https://pollen.googleapis.com/v1/currentConditions:lookup",
            body='{"dailyInfo": [], "regionCode": "US"}',
            status=200,
            content_type="application/json",
        )

        result = self.client.current_pollen((37.7749, -122.4194))

        self.assertEqual(1, len(responses.calls))
        self.assertIn("key=%s" % self.key, responses.calls[0].request.url)

    @responses.activate
    def test_current_pollen_with_language(self):
        responses.add(
            responses.POST,
            "https://pollen.googleapis.com/v1/currentConditions:lookup",
            body='{"dailyInfo": [], "regionCode": "US"}',
            status=200,
            content_type="application/json",
        )

        result = self.client.current_pollen(
            (37.7749, -122.4194),
            language_code="en"
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("languageCode", request_body)

    @responses.activate
    def test_pollen_forecast(self):
        responses.add(
            responses.POST,
            "https://pollen.googleapis.com/v1/forecast:lookup",
            body='{"dailyInfo": []}',
            status=200,
            content_type="application/json",
        )

        result = self.client.pollen_forecast((37.7749, -122.4194))

        self.assertEqual(1, len(responses.calls))
        self.assertIn("key=%s" % self.key, responses.calls[0].request.url)

    @responses.activate
    def test_pollen_forecast_with_days(self):
        responses.add(
            responses.POST,
            "https://pollen.googleapis.com/v1/forecast:lookup",
            body='{"dailyInfo": []}',
            status=200,
            content_type="application/json",
        )

        result = self.client.pollen_forecast(
            (37.7749, -122.4194),
            days=3
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("days", request_body)
