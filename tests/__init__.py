#
# Copyright 2014 Google Inc. All rights reserved.
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

import codecs
import json
import unittest

from urllib.parse import urlparse, parse_qsl

import googlemaps
from googlemaps import exceptions


class TestCase(unittest.TestCase):
    def assertURLEqual(self, first, second, msg=None):
        """Check that two arguments are equivalent URLs. Ignores the order of
        query arguments.
        """
        first_parsed = urlparse(first)
        second_parsed = urlparse(second)
        self.assertEqual(first_parsed[:3], second_parsed[:3], msg)

        first_qsl = sorted(parse_qsl(first_parsed.query))
        second_qsl = sorted(parse_qsl(second_parsed.query))
        self.assertEqual(first_qsl, second_qsl, msg)

    def u(self, string):
        """Create a unicode string, compatible across all versions of Python."""
        # NOTE(cbro): Python 3-3.2 does not have the u'' syntax.
        return codecs.unicode_escape_decode(string)[0]


class GoogleMapsClientTestCase(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)


class JsonApiExtractTestCase(TestCase):
    def make_json_response(self, status_code=200, body=None, json_side_effect=None):
        from unittest.mock import Mock

        response = Mock()
        response.status_code = status_code

        if json_side_effect is not None:
            response.json.side_effect = json_side_effect
        else:
            response.json.return_value = {} if body is None else body

        return response

    def assertApiHttpError(self, extract, body=None, status_code=500):
        response = self.make_json_response(status_code=status_code, body=body)

        with self.assertRaises(exceptions.HTTPError):
            extract(response)

    def assertApiOverQueryLimit(
        self,
        extract,
        error_status="RESOURCE_EXHAUSTED",
        message="Quota exceeded",
        status_code=403,
    ):
        response = self.make_json_response(
            status_code=status_code,
            body={"error": {"status": error_status, "message": message}},
        )

        with self.assertRaises(exceptions._OverQueryLimit) as context:
            extract(response)

        self.assertEqual(context.exception.status, error_status)
        self.assertEqual(context.exception.message, message)

    def assertApiErrorStatus(
        self,
        extract,
        error_status="INVALID_ARGUMENT",
        message="Bad request",
        status_code=400,
    ):
        response = self.make_json_response(
            status_code=status_code,
            body={"error": {"status": error_status, "message": message}},
        )

        with self.assertRaises(exceptions.ApiError) as context:
            extract(response)

        self.assertEqual(context.exception.status, error_status)
        self.assertEqual(context.exception.message, message)

    def assertApiTransportError(self, extract):
        response = self.make_json_response(
            status_code=200,
            json_side_effect=json.JSONDecodeError("msg", "doc", 0),
        )

        with self.assertRaises(exceptions.TransportError):
            extract(response)
