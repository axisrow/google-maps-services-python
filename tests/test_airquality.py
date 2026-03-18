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

"""Tests for the airquality module."""

from datetime import datetime

import responses

import googlemaps
from . import TestCase


class AirQualityTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_current_air_quality(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/currentConditions:lookup",
            body='{"aqi": 42, "category": "Moderate"}',
            status=200,
            content_type="application/json",
        )

        result = self.client.current_air_quality((37.7749, -122.4194))

        self.assertEqual(1, len(responses.calls))
        self.assertIn("key=%s" % self.key, responses.calls[0].request.url)

    @responses.activate
    def test_current_air_quality_with_dict(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/currentConditions:lookup",
            body='{"aqi": 42, "category": "Moderate"}',
            status=200,
            content_type="application/json",
        )

        result = self.client.current_air_quality(
            {"latitude": 37.7749, "longitude": -122.4194}
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("latitude", request_body)
        self.assertIn("longitude", request_body)

    @responses.activate
    def test_air_quality_forecast(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/forecast:lookup",
            body='{"hourlyForecasts": []}',
            status=200,
            content_type="application/json",
        )

        result = self.client.air_quality_forecast((37.7749, -122.4194))

        self.assertEqual(1, len(responses.calls))
        self.assertIn("key=%s" % self.key, responses.calls[0].request.url)

    @responses.activate
    def test_air_quality_forecast_with_period(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/forecast:lookup",
            body='{"hourlyForecasts": []}',
            status=200,
            content_type="application/json",
        )

        now = datetime.now()
        result = self.client.air_quality_forecast(
            (37.7749, -122.4194),
            period=(now, now)
        )

        self.assertEqual(1, len(responses.calls))
        request_body = responses.calls[0].request.body.decode('utf-8')
        self.assertIn("period", request_body)

    @responses.activate
    def test_historical_air_quality(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/history:lookup",
            body='{"hoursInfo": []}',
            status=200,
            content_type="application/json",
        )

        now = datetime.now()
        result = self.client.historical_air_quality(
            (37.7749, -122.4194),
            period={"startTime": "2024-01-01T00:00:00Z", "endTime": "2024-01-02T00:00:00Z"}
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("key=%s" % self.key, responses.calls[0].request.url)
