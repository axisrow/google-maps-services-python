# This Python file uses the following encoding: utf-8
#
# Copyright 2016 Google Inc. All rights reserved.
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

"""Tests for the places module."""

import json
import uuid
import warnings

from types import GeneratorType

import responses

import googlemaps
from . import TestCase


class PlacesTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)
        self.location = (-33.86746, 151.207090)
        self.type = "liquor_store"
        self.language = "en-AU"
        self.region = "AU"
        self.radius = 100

    @responses.activate
    def test_places_find(self):
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        responses.add(
            responses.GET,
            url,
            body='{"status": "OK", "candidates": []}',
            status=200,
            content_type="application/json",
        )

        self.client.find_place(
            "restaurant",
            "textquery",
            fields=["business_status", "geometry/location", "place_id"],
            location_bias="point:90,90",
            language=self.language,
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "%s?language=en-AU&inputtype=textquery&"
            "locationbias=point:90,90&input=restaurant"
            "&fields=business_status,geometry/location,place_id&key=%s"
            % (url, self.key),
            responses.calls[0].request.url,
        )

        with self.assertRaises(ValueError):
            self.client.find_place("restaurant", "invalid")
        with self.assertRaises(ValueError):
            self.client.find_place(
                "restaurant", "textquery", fields=["geometry", "invalid"]
            )
        with self.assertRaises(ValueError):
            self.client.find_place("restaurant", "textquery", location_bias="invalid")

    @responses.activate
    def test_places_text_search(self):
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        responses.add(
            responses.GET,
            url,
            body='{"status": "OK", "results": [], "html_attributions": []}',
            status=200,
            content_type="application/json",
        )

        self.client.places(
            "restaurant",
            location=self.location,
            radius=self.radius,
            region=self.region,
            language=self.language,
            min_price=1,
            max_price=4,
            open_now=True,
            type=self.type,
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "%s?language=en-AU&location=-33.86746%%2C151.20709&"
            "maxprice=4&minprice=1&opennow=true&query=restaurant&"
            "radius=100&region=AU&type=liquor_store&key=%s" % (url, self.key),
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_places_nearby_search(self):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        responses.add(
            responses.GET,
            url,
            body='{"status": "OK", "results": [], "html_attributions": []}',
            status=200,
            content_type="application/json",
        )

        self.client.places_nearby(
            location=self.location,
            keyword="foo",
            language=self.language,
            min_price=1,
            max_price=4,
            name="bar",
            open_now=True,
            rank_by="distance",
            type=self.type,
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "%s?keyword=foo&language=en-AU&location=-33.86746%%2C151.20709&"
            "maxprice=4&minprice=1&name=bar&opennow=true&rankby=distance&"
            "type=liquor_store&key=%s" % (url, self.key),
            responses.calls[0].request.url,
        )

        with self.assertRaises(ValueError):
            self.client.places_nearby(radius=self.radius)
        with self.assertRaises(ValueError):
            self.client.places_nearby(self.location, rank_by="distance")

        with self.assertRaises(ValueError):
            self.client.places_nearby(
                location=self.location,
                rank_by="distance",
                keyword="foo",
                radius=self.radius,
            )

    @responses.activate
    def test_place_detail(self):
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        responses.add(
            responses.GET,
            url,
            body='{"status": "OK", "result": {}, "html_attributions": []}',
            status=200,
            content_type="application/json",
        )

        self.client.place(
            "ChIJN1t_tDeuEmsRUsoyG83frY4",
            fields=["business_status", "geometry/location",
                    "place_id", "reviews"],
            language=self.language,
            reviews_no_translations=True,
            reviews_sort="newest",
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "%s?language=en-AU&placeid=ChIJN1t_tDeuEmsRUsoyG83frY4"
            "&reviews_no_translations=true&reviews_sort=newest"
            "&key=%s&fields=business_status,geometry/location,place_id,reviews"
            % (url, self.key),
            responses.calls[0].request.url,
        )

        with self.assertRaises(ValueError):
            self.client.place(
                "ChIJN1t_tDeuEmsRUsoyG83frY4", fields=["geometry", "invalid"]
            )

    @responses.activate
    def test_photo(self):
        url = "https://maps.googleapis.com/maps/api/place/photo"
        responses.add(responses.GET, url, status=200)

        ref = "CnRvAAAAwMpdHeWlXl-lH0vp7lez4znKPIWSWvgvZFISdKx45AwJVP1Qp37YOrH7sqHMJ8C-vBDC546decipPHchJhHZL94RcTUfPa1jWzo-rSHaTlbNtjh-N68RkcToUCuY9v2HNpo5mziqkir37WU8FJEqVBIQ4k938TI3e7bf8xq-uwDZcxoUbO_ZJzPxremiQurAYzCTwRhE_V0"
        response = self.client.places_photo(ref, max_width=100)

        self.assertTrue(isinstance(response, GeneratorType))
        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "%s?maxwidth=100&photoreference=%s&key=%s" % (url, ref, self.key),
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_autocomplete(self):
        url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        responses.add(
            responses.GET,
            url,
            body='{"status": "OK", "predictions": []}',
            status=200,
            content_type="application/json",
        )

        session_token = uuid.uuid4().hex

        self.client.places_autocomplete(
            "Google",
            session_token=session_token,
            offset=3,
            origin=self.location,
            location=self.location,
            radius=self.radius,
            language=self.language,
            types="geocode",
            components={"country": "au"},
            strict_bounds=True,
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "%s?components=country%%3Aau&input=Google&language=en-AU&"
            "origin=-33.86746%%2C151.20709&"
            "location=-33.86746%%2C151.20709&offset=3&radius=100&"
            "strictbounds=true&types=geocode&key=%s&sessiontoken=%s"
            % (url, self.key, session_token),
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_autocomplete_query(self):
        url = "https://maps.googleapis.com/maps/api/place/queryautocomplete/json"
        responses.add(
            responses.GET,
            url,
            body='{"status": "OK", "predictions": []}',
            status=200,
            content_type="application/json",
        )

        self.client.places_autocomplete_query("pizza near New York")

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "%s?input=pizza+near+New+York&key=%s" % (url, self.key),
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_places_text_search_new(self):
        url = "https://places.googleapis.com/v1/places:searchText"
        responses.add(
            responses.POST,
            url,
            body='{"places": [], "nextPageToken": "token"}',
            status=200,
            content_type="application/json",
        )

        self.client.places_text_search(
            text_query="restaurant",
            field_mask="places.displayName,nextPageToken",
            language_code="en",
            page_size=5,
            location_bias={
                "circle": {
                    "center": {"latitude": -33.86746, "longitude": 151.207090},
                    "radius": 500.0,
                }
            },
            open_now=True,
        )

        self.assertEqual(1, len(responses.calls))
        request = responses.calls[0].request
        self.assertEqual("POST", request.method)
        self.assertEqual(
            "places.displayName,nextPageToken",
            request.headers["X-Goog-FieldMask"],
        )
        body = responses.calls[0].request.body
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        payload = json.loads(body)
        self.assertEqual("restaurant", payload["textQuery"])
        self.assertEqual(5, payload["pageSize"])
        self.assertTrue(payload["openNow"])

        with self.assertRaises(ValueError):
            self.client.places_text_search("restaurant", field_mask=None)

    @responses.activate
    def test_places_nearby_search_new(self):
        url = "https://places.googleapis.com/v1/places:searchNearby"
        responses.add(
            responses.POST,
            url,
            body='{"places": []}',
            status=200,
            content_type="application/json",
        )

        self.client.places_nearby_search(
            location=self.location,
            radius=250.0,
            field_mask="places.displayName",
            included_types=["restaurant"],
            rank_preference="DISTANCE",
            max_result_count=10,
        )

        self.assertEqual(1, len(responses.calls))
        body = responses.calls[0].request.body
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        payload = json.loads(body)
        self.assertEqual(["restaurant"], payload["includedTypes"])
        self.assertEqual(250.0, payload["locationRestriction"]["circle"]["radius"])
        self.assertEqual("DISTANCE", payload["rankPreference"])

    @responses.activate
    def test_place_details_new(self):
        url = "https://places.googleapis.com/v1/places/ChIJj61dQgK6j4AR4GeTYWZsKWw"
        responses.add(
            responses.GET,
            url,
            body='{"id": "ChIJj61dQgK6j4AR4GeTYWZsKWw"}',
            status=200,
            content_type="application/json",
        )

        self.client.place_details(
            "ChIJj61dQgK6j4AR4GeTYWZsKWw",
            field_mask="id,displayName",
            language_code="en",
            region_code="US",
        )

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(
            "id,displayName",
            responses.calls[0].request.headers["X-Goog-FieldMask"],
        )
        self.assertIn("languageCode=en", responses.calls[0].request.url)

    @responses.activate
    def test_place_photo_new_binary(self):
        url = "https://places.googleapis.com/v1/places/foo/photos/bar/media"
        responses.add(responses.GET, url, status=200, body=b"img")

        response = self.client.place_photo(
            "places/foo/photos/bar",
            max_width_px=400,
        )

        self.assertTrue(isinstance(response, GeneratorType) or isinstance(response, bytes))
        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "%s?maxWidthPx=400&key=%s" % (url, self.key),
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_place_photo_new_json(self):
        url = "https://places.googleapis.com/v1/places/foo/photos/bar/media"
        responses.add(
            responses.GET,
            url,
            body='{"name":"places/foo/photos/bar/media","photoUri":"https://example.com/photo"}',
            status=200,
            content_type="application/json",
        )

        result = self.client.place_photo(
            "places/foo/photos/bar",
            max_height_px=400,
            skip_http_redirect=True,
        )

        self.assertEqual("https://example.com/photo", result["photoUri"])

    @responses.activate
    def test_places_autocomplete_new(self):
        url = "https://places.googleapis.com/v1/places:autocomplete"
        responses.add(
            responses.POST,
            url,
            body='{"suggestions": []}',
            status=200,
            content_type="application/json",
        )

        self.client.places_autocomplete_new(
            "pizza",
            field_mask="suggestions.placePrediction.text.text",
            session_token="token123",
            include_query_predictions=True,
            included_primary_types=["restaurant"],
            origin=self.location,
        )

        self.assertEqual(1, len(responses.calls))
        body = responses.calls[0].request.body
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        payload = json.loads(body)
        self.assertEqual("pizza", payload["input"])
        self.assertEqual("token123", payload["sessionToken"])
        self.assertTrue(payload["includeQueryPredictions"])

    @responses.activate
    def test_find_place_with_deprecated_fields_warning(self):
        """Test that deprecated fields raise a DeprecationWarning."""
        import warnings

        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        responses.add(
            responses.GET,
            url,
            body='{"status": "OK", "candidates": []}',
            status=200,
            content_type="application/json",
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.client.find_place(
                "restaurant",
                "textquery",
                fields=["permanently_closed", "place_id"]
            )
            self.assertEqual(1, len(w))
            self.assertEqual(w[0].category, DeprecationWarning)

    @responses.activate
    def test_places_with_page_token(self):
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        responses.add(
            responses.GET,
            url,
            body='{"status": "OK", "results": [], "html_attributions": []}',
            status=200,
            content_type="application/json",
        )

        self.client.places(query="restaurant", page_token="next_page_token_123")

        self.assertEqual(1, len(responses.calls))
        self.assertIn("pagetoken=next_page_token_123", responses.calls[0].request.url)

    @responses.activate
    def test_place_with_deprecated_fields_warning(self):
        """Test that deprecated fields in place() raise a DeprecationWarning."""
        import warnings

        url = "https://maps.googleapis.com/maps/api/place/details/json"
        responses.add(
            responses.GET,
            url,
            body='{"status": "OK", "result": {}, "html_attributions": []}',
            status=200,
            content_type="application/json",
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.client.place(
                "ChIJN1t_tDeuEmsRUsoyG83frY4",
                fields=["review", "place_id"]
            )
            self.assertEqual(1, len(w))
            self.assertEqual(w[0].category, DeprecationWarning)

    @responses.activate
    def test_place_with_session_token(self):
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        responses.add(
            responses.GET,
            url,
            body='{"status": "OK", "result": {}, "html_attributions": []}',
            status=200,
            content_type="application/json",
        )

        session_token = uuid.uuid4().hex
        self.client.place("ChIJN1t_tDeuEmsRUsoyG83frY4", session_token=session_token)

        self.assertEqual(1, len(responses.calls))
        self.assertIn("sessiontoken=%s" % session_token, responses.calls[0].request.url)

    @responses.activate
    def test_places_photo_with_max_height_only(self):
        url = "https://maps.googleapis.com/maps/api/place/photo"
        responses.add(responses.GET, url, status=200)

        ref = "CnRvAAAAwMpdHeWlXl-lH0vp7lez4znKPIWSWvgvZFISdKx45AwJVP1Qp37YOrH7sqHMJ8C-vBDC546decipPHchJhHZL94RcTUfPa1jWzo-rSHaTlbNtjh-N68RkcToUCuY9v2HNpo5mziqkir37WU8FJEqVBIQ4k938TI3e7bf8xq-uwDZcxoUbO_ZJzPxremiQurAYzCTwRhE_V0"
        response = self.client.places_photo(ref, max_height=100)

        self.assertTrue(isinstance(response, GeneratorType))
        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "%s?maxheight=100&photoreference=%s&key=%s" % (url, ref, self.key),
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_autocomplete_with_components_validation_error(self):
        """Test that non-country components raise ValueError."""
        with self.assertRaises(ValueError):
            self.client.places_autocomplete(
                "Google",
                components={"city": "New York"}
            )
