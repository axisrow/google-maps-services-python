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

"""Performs requests to the Google Maps Routes API v2."""

from googlemaps import exceptions


_ROUTES_BASE_URL = "https://routes.googleapis.com"


def _routes_extract(response):
    """
    Mimics the exception handling logic in ``client._get_body``, but
    for Routes API which uses a different response format.
    """
    if response.status_code == 200:
        return response.json()

    body = response.json()
    error = body.get("error", {})
    message = error.get("message", "Unknown error")

    if response.status_code == 403:
        raise exceptions._OverQueryLimit(response.status_code, message)
    else:
        raise exceptions.ApiError(response.status_code, message)


def _format_waypoint(waypoint):
    """
    Formats a waypoint for the Routes API.

    :param waypoint: A location as address string, lat/lng dict, lat/lng tuple,
        or a dict with 'location' containing 'latLng' or 'placeId'.
    :type waypoint: string, dict, or tuple

    :rtype: dict
    """
    if isinstance(waypoint, str):
        # Check if it's a place_id
        if waypoint.startswith("place_id:"):
            return {"placeId": waypoint[9:]}
        return {"address": waypoint}
    elif isinstance(waypoint, (tuple, list)):
        return {"location": {"latLng": {"latitude": waypoint[0], "longitude": waypoint[1]}}}
    elif isinstance(waypoint, dict):
        if "placeId" in waypoint or "address" in waypoint or "location" in waypoint:
            return waypoint
        # Assume it's a lat/lng dict
        return {"location": {"latLng": {"latitude": waypoint.get("lat"), "longitude": waypoint.get("lng")}}}
    else:
        raise ValueError("Invalid waypoint format: %s" % waypoint)


def _format_time(time_value):
    """
    Formats a time value for the Routes API (RFC 3339 timestamp).

    :param time_value: A datetime object or string timestamp.
    :type time_value: datetime.datetime or string

    :rtype: string
    """
    if isinstance(time_value, str):
        return time_value
    # Assume datetime object
    return time_value.strftime("%Y-%m-%dT%H:%M:%SZ")


def compute_routes(client, origin, destination, intermediates=None,
                   travel_mode=None, routing_preference=None,
                   polyline_quality=None, polyline_encoding=None,
                   departure_time=None, arrival_time=None,
                   compute_alternative_routes=False, route_modifiers=None,
                   language_code=None, region_code=None, units=None,
                   optimize_waypoint_order=False, requested_reference_routes=None,
                   extra_computations=None, traffic_model=None,
                   transit_preferences=None, field_mask=None):
    """Returns the primary route along with optional alternate routes.

    The Routes API is the next generation of Google Maps routing.
    It uses POST requests with JSON body instead of GET with query parameters.

    For more information see: https://developers.google.com/maps/documentation/routes

    :param origin: Origin waypoint. Can be an address string, (lat, lng) tuple,
        or a dict with 'address', 'placeId', or 'location' keys.
    :type origin: string, tuple, or dict

    :param destination: Destination waypoint. Same format as origin.
    :type destination: string, tuple, or dict

    :param intermediates: List of intermediate waypoints (up to 25).
    :type intermediates: list of waypoints

    :param travel_mode: Mode of transport. One of "DRIVE", "WALK", "BICYCLE",
        "TRANSIT", or "TWO_WHEELER".
    :type travel_mode: string

    :param routing_preference: How to compute the route. One of
        "TRAFFIC_UNAWARE", "TRAFFIC_AWARE", "TRAFFIC_AWARE_OPTIMAL".
    :type routing_preference: string

    :param polyline_quality: Quality of the polyline. One of "OVERVIEW",
        "HIGH_QUALITY".
    :type polyline_quality: string

    :param polyline_encoding: Encoding for the polyline. One of
        "ENCODED_POLYLINE", "GEO_JSON_LINESTRING".
    :type polyline_encoding: string

    :param departure_time: Departure time as datetime or RFC 3339 string.
    :type departure_time: datetime.datetime or string

    :param arrival_time: Arrival time as datetime or RFC 3339 string.
        Only for TRANSIT mode.
    :type arrival_time: datetime.datetime or string

    :param compute_alternative_routes: Whether to calculate alternate routes.
    :type compute_alternative_routes: bool

    :param route_modifiers: Dict with route modifiers like 'avoidTolls',
        'avoidHighways', 'avoidFerries'.
    :type route_modifiers: dict

    :param language_code: BCP-47 language code (e.g., "en-US").
    :type language_code: string

    :param region_code: Region code as ccTLD (e.g., "us").
    :type region_code: string

    :param units: Units for display. One of "METRIC", "IMPERIAL".
    :type units: string

    :param optimize_waypoint_order: Whether to optimize the order of
        intermediate waypoints.
    :type optimize_waypoint_order: bool

    :param requested_reference_routes: List of reference route types.
        E.g., ["FUEL_EFFICIENT", "SHORTER_DISTANCE"].
    :type requested_reference_routes: list of strings

    :param extra_computations: List of extra computations. E.g.,
        ["TOLLS", "FUEL_CONSUMPTION", "TRAFFIC_ON_POLYLINE"].
    :type extra_computations: list of strings

    :param traffic_model: Traffic model for predictions. One of
        "BEST_GUESS", "PESSIMISTIC", "OPTIMISTIC".
    :type traffic_model: string

    :param transit_preferences: Dict with transit preferences like
        'allowedTravelModes', 'routingPreference'.
    :type transit_preferences: dict

    :param field_mask: Comma-separated list of fields to return.
        If not provided, returns basic route information.
        Example: "routes.duration,routes.distanceMeters,routes.polyline"
    :type field_mask: string

    :rtype: dict containing routes and optionally fallbackInfo and geocodingResults
    """

    request_body = {
        "origin": _format_waypoint(origin),
        "destination": _format_waypoint(destination),
    }

    if intermediates:
        request_body["intermediates"] = [_format_waypoint(wp) for wp in intermediates]

    if travel_mode:
        request_body["travelMode"] = travel_mode

    if routing_preference:
        request_body["routingPreference"] = routing_preference

    if polyline_quality:
        request_body["polylineQuality"] = polyline_quality

    if polyline_encoding:
        request_body["polylineEncoding"] = polyline_encoding

    if departure_time:
        request_body["departureTime"] = _format_time(departure_time)

    if arrival_time:
        request_body["arrivalTime"] = _format_time(arrival_time)

    if compute_alternative_routes:
        request_body["computeAlternativeRoutes"] = compute_alternative_routes

    if route_modifiers:
        request_body["routeModifiers"] = route_modifiers

    if language_code:
        request_body["languageCode"] = language_code

    if region_code:
        request_body["regionCode"] = region_code

    if units:
        request_body["units"] = units

    if optimize_waypoint_order:
        request_body["optimizeWaypointOrder"] = optimize_waypoint_order

    if requested_reference_routes:
        request_body["requestedReferenceRoutes"] = requested_reference_routes

    if extra_computations:
        request_body["extraComputations"] = extra_computations

    if traffic_model:
        request_body["trafficModel"] = traffic_model

    if transit_preferences:
        request_body["transitPreferences"] = transit_preferences

    # Set up headers with field mask
    headers = {}
    if field_mask:
        headers["X-Goog-FieldMask"] = field_mask
    else:
        # Default field mask for basic route info
        headers["X-Goog-FieldMask"] = "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"

    return client._request(
        "/directions/v2:computeRoutes",
        {},
        base_url=_ROUTES_BASE_URL,
        extract_body=_routes_extract,
        post_json=request_body,
        requests_kwargs={"headers": headers}
    )


def compute_route_matrix(client, origins, destinations, travel_mode=None,
                         routing_preference=None, departure_time=None,
                         arrival_time=None, language_code=None, region_code=None,
                         units=None, extra_computations=None, traffic_model=None,
                         transit_preferences=None, field_mask=None):
    """Computes a route matrix for multiple origins and destinations.

    Takes a list of origins and destinations and returns route information
    for each combination.

    For more information see: https://developers.google.com/maps/documentation/routes

    :param origins: List of origin waypoints. Each waypoint can be an address
        string, (lat, lng) tuple, or a dict with routeModifiers.
    :type origins: list

    :param destinations: List of destination waypoints.
    :type destinations: list

    :param travel_mode: Mode of transport. One of "DRIVE", "WALK", "BICYCLE",
        "TRANSIT", or "TWO_WHEELER".
    :type travel_mode: string

    :param routing_preference: How to compute the route. One of
        "TRAFFIC_UNAWARE", "TRAFFIC_AWARE", "TRAFFIC_AWARE_OPTIMAL".
    :type routing_preference: string

    :param departure_time: Departure time as datetime or RFC 3339 string.
    :type departure_time: datetime.datetime or string

    :param arrival_time: Arrival time (only for TRANSIT mode).
    :type arrival_time: datetime.datetime or string

    :param language_code: BCP-47 language code.
    :type language_code: string

    :param region_code: Region code as ccTLD.
    :type region_code: string

    :param units: Units for display. One of "METRIC", "IMPERIAL".
    :type units: string

    :param extra_computations: List of extra computations like ["TOLLS"].
    :type extra_computations: list of strings

    :param traffic_model: Traffic model for predictions.
    :type traffic_model: string

    :param transit_preferences: Transit preferences dict.
    :type transit_preferences: dict

    :param field_mask: Comma-separated list of fields to return.
        If not provided, returns basic matrix information.
    :type field_mask: string

    :rtype: list of route matrix elements
    """

    # Format origins - each can be a simple waypoint or a dict with waypoint and routeModifiers
    formatted_origins = []
    for origin in origins:
        if isinstance(origin, dict) and "waypoint" in origin:
            formatted_origins.append({
                "waypoint": _format_waypoint(origin["waypoint"]),
                "routeModifiers": origin.get("routeModifiers")
            })
        else:
            formatted_origins.append({"waypoint": _format_waypoint(origin)})

    # Format destinations
    formatted_destinations = []
    for dest in destinations:
        formatted_destinations.append({"waypoint": _format_waypoint(dest)})

    request_body = {
        "origins": formatted_origins,
        "destinations": formatted_destinations,
    }

    if travel_mode:
        request_body["travelMode"] = travel_mode

    if routing_preference:
        request_body["routingPreference"] = routing_preference

    if departure_time:
        request_body["departureTime"] = _format_time(departure_time)

    if arrival_time:
        request_body["arrivalTime"] = _format_time(arrival_time)

    if language_code:
        request_body["languageCode"] = language_code

    if region_code:
        request_body["regionCode"] = region_code

    if units:
        request_body["units"] = units

    if extra_computations:
        request_body["extraComputations"] = extra_computations

    if traffic_model:
        request_body["trafficModel"] = traffic_model

    if transit_preferences:
        request_body["transitPreferences"] = transit_preferences

    # Set up headers with field mask
    headers = {}
    if field_mask:
        headers["X-Goog-FieldMask"] = field_mask
    else:
        # Default field mask for basic matrix info
        headers["X-Goog-FieldMask"] = "originIndex,destinationIndex,status,condition,distanceMeters,duration"

    return client._request(
        "/distanceMatrix/v2:computeRouteMatrix",
        {},
        base_url=_ROUTES_BASE_URL,
        extract_body=_routes_extract,
        post_json=request_body,
        requests_kwargs={"headers": headers}
    )
