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

"""Performs requests to the Google Maps Route Optimization API."""

import re

from googlemaps._api import extract_api_body
from googlemaps._api import format_lat_lng
from googlemaps._api import modern_api_request


_ROUTE_OPTIMIZATION_BASE_URL = "https://routeoptimization.googleapis.com"


def _route_optimization_extract(response):
    """
    Mimics the exception handling logic in ``client._get_body``, but
    for Route Optimization API which uses a different response format.
    """
    return extract_api_body(response)


def _format_ro_location(location):
    """
    Formats a location for the Route Optimization API.

    :param location: A lat/lng dict or tuple.
    :type location: dict or tuple

    :rtype: dict
    """
    if isinstance(location, dict) and "latLng" in location:
        return location
    lat_lng = format_lat_lng(location)
    return {"latLng": lat_lng}


def optimize_tour(client, parent, model, timeout=None, populate_transition_polylines=None,
                  allow_large_deadline_despite_interruption_risk=None,
                  interpret_injected_solutions_using_model=None,
                  cost_model=None, search_mode=None, geodesic_meters_per_second=None,
                  max_interpolation_distance_meters=None):
    """Sends a request to optimize a tour with multiple shipments and vehicles.

    The Route Optimization API solves vehicle routing and scheduling problems
    by finding optimal routes for vehicles to visit a set of locations.

    For more information see: https://developers.google.com/maps/documentation/route-optimization

    :param parent: The parent resource name. Format: "projects/{projectId}".
        Example: "projects/my-project".
    :type parent: string

    :param model: The optimization model containing shipments, vehicles,
        and constraints. This is a dict with the following structure:
        {
            "shipments": [
                {
                    "pickup": {"arrivalLocation": {...}, "duration": "300s"},
                    "delivery": {"arrivalLocation": {...}, "duration": "300s"},
                    "penaltyCost": 100.0
                }
            ],
            "vehicles": [
                {
                    "startLocation": {...},
                    "endLocation": {...},
                    "costPerKilometer": 1.0,
                    "costPerHour": 10.0
                }
            ],
            "globalStartTime": "2024-01-01T00:00:00Z",
            "globalEndTime": "2024-01-02T00:00:00Z"
        }
    :type model: dict

    :param timeout: Maximum time for the request. Example: "60s".
    :type timeout: string

    :param populate_transition_polylines: If true, polylines will be computed
        for all transitions between visits.
    :type populate_transition_polylines: bool

    :param allow_large_deadline_despite_interruption_risk: If true, the request
        may have a longer timeout at the risk of interruption.
    :type allow_large_deadline_despite_interruption_risk: bool

    :param interpret_injected_solutions_using_model: If true, injected solutions
        will be interpreted using the provided model.
    :type interpret_injected_solutions_using_model: bool

    :param cost_model: Cost model to use. Valid values: "COST_MODEL_STATIC",
        "COST_MODEL_TRAFFIC_AWARE", "COST_MODEL_TRAFFIC_AWARE_OPTIMAL".
    :type cost_model: string

    :param search_mode: Search mode. Valid values: "SEARCH_MODE_UNSPECIFIED",
        "PARALLEL_SCH_ORIGINAL", "PARALLEL_SCH_FAST", "GUIDED_LOCAL_SEARCH".
    :type search_mode: string

    :param geodesic_meters_per_second: Speed in meters per second for geodesic
        distance computation.
    :type geodesic_meters_per_second: float

    :param max_interpolation_distance_meters: Maximum distance for interpolation
        in meters.
    :type max_interpolation_distance_meters: int

    :rtype: dict containing the optimized tour solution
    """

    # Validate parent format
    if not parent or not re.match(r"^projects/[^/]+(?:/locations/[^/]+)?$", parent):
        raise ValueError(
            "parent must be in format 'projects/{projectId}' or "
            "'projects/{projectId}/locations/{locationId}', got: %s" % parent
        )

    request_body = {
        "model": model,
    }

    if timeout:
        request_body["timeout"] = timeout

    if populate_transition_polylines is not None:
        request_body["populateTransitionPolylines"] = populate_transition_polylines

    if allow_large_deadline_despite_interruption_risk is not None:
        request_body["allowLargeDeadlineDespiteInterruptionRisk"] = allow_large_deadline_despite_interruption_risk

    if interpret_injected_solutions_using_model is not None:
        request_body["interpretInjectedSolutionsUsingModel"] = interpret_injected_solutions_using_model

    if cost_model:
        request_body["costModel"] = cost_model

    if search_mode:
        request_body["searchMode"] = search_mode

    if geodesic_meters_per_second:
        request_body["geodesicMetersPerSecond"] = geodesic_meters_per_second

    if max_interpolation_distance_meters:
        request_body["maxInterpolationDistanceMeters"] = max_interpolation_distance_meters

    return modern_api_request(
        client,
        "/v1/%s:optimizeTours" % parent,
        base_url=_ROUTE_OPTIMIZATION_BASE_URL,
        post_json=request_body,
        extract_body=_route_optimization_extract,
    )


def batch_optimize_tours(client, parent, requests, model_configs=None,
                         timeout=None, allow_large_deadline_despite_interruption_risk=None):
    """Runs Route Optimization asynchronously and returns a long-running operation.

    For more information see:
    https://developers.google.com/maps/documentation/route-optimization

    :param parent: The parent resource name. Format: "projects/{projectId}" or
        "projects/{projectId}/locations/{locationId}".
    :type parent: string

    :param requests: A list of optimizeTours-style request objects.
    :type requests: list

    :param model_configs: Optional list of async model configuration objects.
    :type model_configs: list

    :param timeout: Maximum time for each optimization request. Example: "60s".
    :type timeout: string

    :param allow_large_deadline_despite_interruption_risk: Whether larger
        deadlines are allowed at the risk of interruption.
    :type allow_large_deadline_despite_interruption_risk: bool

    :rtype: dict containing the long-running operation metadata
    """
    if not parent or not re.match(r"^projects/[^/]+(?:/locations/[^/]+)?$", parent):
        raise ValueError(
            "parent must be in format 'projects/{projectId}' or "
            "'projects/{projectId}/locations/{locationId}', got: %s" % parent
        )
    if not requests:
        raise ValueError("requests must be a non-empty list")

    request_body = {
        "parent": parent,
        "requests": requests,
    }

    if model_configs is not None:
        request_body["modelConfigs"] = model_configs

    if timeout:
        request_body["timeout"] = timeout

    if allow_large_deadline_despite_interruption_risk is not None:
        request_body["allowLargeDeadlineDespiteInterruptionRisk"] = allow_large_deadline_despite_interruption_risk

    return modern_api_request(
        client,
        "/v1/%s:batchOptimizeTours" % parent,
        base_url=_ROUTE_OPTIMIZATION_BASE_URL,
        post_json=request_body,
        extract_body=_route_optimization_extract,
    )
