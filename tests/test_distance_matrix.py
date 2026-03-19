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

"""Tests for the distance matrix module."""

from datetime import datetime
import time

import responses

import googlemaps
from . import TestCase


class DistanceMatrixTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_basic_params(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = [
            "Perth, Australia",
            "Sydney, Australia",
            "Melbourne, Australia",
            "Adelaide, Australia",
            "Brisbane, Australia",
            "Darwin, Australia",
            "Hobart, Australia",
            "Canberra, Australia",
        ]
        destinations = [
            "Uluru, Australia",
            "Kakadu, Australia",
            "Blue Mountains, Australia",
            "Bungle Bungles, Australia",
            "The Pinnacles, Australia",
        ]

        matrix = self.client.distance_matrix(origins, destinations)

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/distancematrix/json?"
            "key=%s&origins=Perth%%2C+Australia%%7CSydney%%2C+"
            "Australia%%7CMelbourne%%2C+Australia%%7CAdelaide%%2C+"
            "Australia%%7CBrisbane%%2C+Australia%%7CDarwin%%2C+"
            "Australia%%7CHobart%%2C+Australia%%7CCanberra%%2C+Australia&"
            "destinations=Uluru%%2C+Australia%%7CKakadu%%2C+Australia%%7C"
            "Blue+Mountains%%2C+Australia%%7CBungle+Bungles%%2C+Australia"
            "%%7CThe+Pinnacles%%2C+Australia" % self.key,
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_mixed_params(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = [
            "Bobcaygeon ON", [41.43206, -81.38992],
            "place_id:ChIJ7cv00DwsDogRAMDACa2m4K8"
        ]
        destinations = [
            (43.012486, -83.6964149),
            {"lat": 42.8863855, "lng": -78.8781627},
        ]

        matrix = self.client.distance_matrix(origins, destinations)

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/distancematrix/json?"
            "key=%s&origins=Bobcaygeon+ON%%7C41.43206%%2C-81.38992%%7C"
            "place_id%%3AChIJ7cv00DwsDogRAMDACa2m4K8&"
            "destinations=43.012486%%2C-83.6964149%%7C42.8863855%%2C"
            "-78.8781627" % self.key,
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_all_params(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = [
            "Perth, Australia",
            "Sydney, Australia",
            "Melbourne, Australia",
            "Adelaide, Australia",
            "Brisbane, Australia",
            "Darwin, Australia",
            "Hobart, Australia",
            "Canberra, Australia",
        ]
        destinations = [
            "Uluru, Australia",
            "Kakadu, Australia",
            "Blue Mountains, Australia",
            "Bungle Bungles, Australia",
            "The Pinnacles, Australia",
        ]

        now = datetime.now()
        matrix = self.client.distance_matrix(
            origins,
            destinations,
            mode="driving",
            language="en-AU",
            avoid="tolls",
            units="imperial",
            departure_time=now,
            traffic_model="optimistic",
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/distancematrix/json?"
            "origins=Perth%%2C+Australia%%7CSydney%%2C+Australia%%7C"
            "Melbourne%%2C+Australia%%7CAdelaide%%2C+Australia%%7C"
            "Brisbane%%2C+Australia%%7CDarwin%%2C+Australia%%7CHobart%%2C+"
            "Australia%%7CCanberra%%2C+Australia&language=en-AU&"
            "avoid=tolls&mode=driving&key=%s&units=imperial&"
            "destinations=Uluru%%2C+Australia%%7CKakadu%%2C+Australia%%7C"
            "Blue+Mountains%%2C+Australia%%7CBungle+Bungles%%2C+Australia"
            "%%7CThe+Pinnacles%%2C+Australia&departure_time=%d"
            "&traffic_model=optimistic" % (self.key, time.mktime(now.timetuple())),
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_lang_param(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = ["Vancouver BC", "Seattle"]
        destinations = ["San Francisco", "Victoria BC"]

        matrix = self.client.distance_matrix(
            origins, destinations, language="fr-FR", mode="bicycling"
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/distancematrix/json?"
            "key=%s&language=fr-FR&mode=bicycling&"
            "origins=Vancouver+BC%%7CSeattle&"
            "destinations=San+Francisco%%7CVictoria+BC" % self.key,
            responses.calls[0].request.url,
        )
    @responses.activate
    def test_place_id_param(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = [
            'place_id:ChIJ7cv00DwsDogRAMDACa2m4K8',
            'place_id:ChIJzxcfI6qAa4cR1jaKJ_j0jhE',
        ]
        destinations = [
            'place_id:ChIJPZDrEzLsZIgRoNrpodC5P30',
            'place_id:ChIJjQmTaV0E9YgRC2MLmS_e_mY',
        ]

        matrix = self.client.distance_matrix(origins, destinations)

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/distancematrix/json?"
            "key=%s&"
            "origins=place_id%%3AChIJ7cv00DwsDogRAMDACa2m4K8%%7C"
            "place_id%%3AChIJzxcfI6qAa4cR1jaKJ_j0jhE&"
            "destinations=place_id%%3AChIJPZDrEzLsZIgRoNrpodC5P30%%7C"
            "place_id%%3AChIJjQmTaV0E9YgRC2MLmS_e_mY" % self.key,
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_transit_mode_list(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = ["New York, NY"]
        destinations = ["Boston, MA"]

        matrix = self.client.distance_matrix(
            origins,
            destinations,
            mode="transit",
            transit_mode=["bus", "subway", "train"]
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("transit_mode=bus%7Csubway%7Ctrain", responses.calls[0].request.url)

    @responses.activate
    def test_transit_mode_single_string(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = ["New York, NY"]
        destinations = ["Boston, MA"]

        matrix = self.client.distance_matrix(
            origins,
            destinations,
            mode="transit",
            transit_mode="rail"
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("transit_mode=rail", responses.calls[0].request.url)

    @responses.activate
    def test_transit_routing_preference(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = ["New York, NY"]
        destinations = ["Boston, MA"]

        matrix = self.client.distance_matrix(
            origins,
            destinations,
            mode="transit",
            transit_routing_preference="fewer_transfers"
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("transit_routing_preference=fewer_transfers", responses.calls[0].request.url)

    @responses.activate
    def test_transit_routing_preference_less_walking(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = ["New York, NY"]
        destinations = ["Boston, MA"]

        matrix = self.client.distance_matrix(
            origins,
            destinations,
            mode="transit",
            transit_routing_preference="less_walking"
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("transit_routing_preference=less_walking", responses.calls[0].request.url)

    @responses.activate
    def test_region_param(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = ["Sydney"]
        destinations = ["Melbourne"]

        matrix = self.client.distance_matrix(
            origins,
            destinations,
            region="au"
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("region=au", responses.calls[0].request.url)

    @responses.activate
    def test_traffic_model_pessimistic(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = ["New York, NY"]
        destinations = ["Boston, MA"]
        now = datetime.now()

        matrix = self.client.distance_matrix(
            origins,
            destinations,
            mode="driving",
            departure_time=now,
            traffic_model="pessimistic"
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("traffic_model=pessimistic", responses.calls[0].request.url)

    @responses.activate
    def test_traffic_model_best_guess(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            body='{"status":"OK","rows":[]}',
            status=200,
            content_type="application/json",
        )

        origins = ["New York, NY"]
        destinations = ["Boston, MA"]
        now = datetime.now()

        matrix = self.client.distance_matrix(
            origins,
            destinations,
            mode="driving",
            departure_time=now,
            traffic_model="best_guess"
        )

        self.assertEqual(1, len(responses.calls))
        self.assertIn("traffic_model=best_guess", responses.calls[0].request.url)

    def test_invalid_travel_mode(self):
        """Test that invalid mode raises ValueError."""
        with self.assertRaises(ValueError):
            self.client.distance_matrix(
                ["New York, NY"],
                ["Boston, MA"],
                mode="invalid_mode"
            )

    def test_invalid_avoid(self):
        """Test that invalid avoid parameter raises ValueError."""
        with self.assertRaises(ValueError):
            self.client.distance_matrix(
                ["New York, NY"],
                ["Boston, MA"],
                avoid="invalid_avoid"
            )

    def test_departure_and_arrival_time_error(self):
        """Test that specifying both departure_time and arrival_time raises ValueError."""
        now = datetime.now()
        with self.assertRaises(ValueError):
            self.client.distance_matrix(
                ["New York, NY"],
                ["Boston, MA"],
                departure_time=now,
                arrival_time=now
            )
