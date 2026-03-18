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

"""Tests for the exceptions module."""

from googlemaps import exceptions
from . import TestCase


class ExceptionsTest(TestCase):
    def test_api_error_with_message(self):
        error = exceptions.ApiError("NOT_FOUND", "The requested resource was not found")

        self.assertEqual(error.status, "NOT_FOUND")
        self.assertEqual(error.message, "The requested resource was not found")
        self.assertEqual(str(error), "NOT_FOUND (The requested resource was not found)")

    def test_api_error_without_message(self):
        error = exceptions.ApiError("UNKNOWN_ERROR")

        self.assertEqual(error.status, "UNKNOWN_ERROR")
        self.assertIsNone(error.message)
        self.assertEqual(str(error), "UNKNOWN_ERROR")

    def test_transport_error_with_base_exception(self):
        base_exc = ValueError("Connection failed")
        error = exceptions.TransportError(base_exc)

        self.assertEqual(error.base_exception, base_exc)
        self.assertEqual(str(error), "Connection failed")

    def test_transport_error_without_base_exception(self):
        error = exceptions.TransportError()

        self.assertIsNone(error.base_exception)
        self.assertEqual(str(error), "An unknown error occurred.")

    def test_http_error(self):
        error = exceptions.HTTPError(404)

        self.assertEqual(error.status_code, 404)
        self.assertEqual(str(error), "HTTP Error: 404")

    def test_http_error_with_status_code_500(self):
        error = exceptions.HTTPError(500)

        self.assertEqual(error.status_code, 500)
        self.assertEqual(str(error), "HTTP Error: 500")

    def test_timeout(self):
        error = exceptions.Timeout()

        self.assertIsInstance(error, Exception)

    def test_retriable_request(self):
        error = exceptions._RetriableRequest()

        self.assertIsInstance(error, Exception)

    def test_over_query_limit(self):
        error = exceptions._OverQueryLimit("OVER_QUERY_LIMIT", "You have exceeded your quota")

        self.assertEqual(error.status, "OVER_QUERY_LIMIT")
        self.assertEqual(error.message, "You have exceeded your quota")
        self.assertIsInstance(error, exceptions.ApiError)
        self.assertIsInstance(error, exceptions._RetriableRequest)

    def test_over_query_limit_inheritance(self):
        error = exceptions._OverQueryLimit("RATE_LIMIT_EXCEEDED")

        # Should be both ApiError and _RetriableRequest
        self.assertIsInstance(error, exceptions.ApiError)
        self.assertIsInstance(error, exceptions._RetriableRequest)
        # Should also be an Exception
        self.assertIsInstance(error, Exception)
