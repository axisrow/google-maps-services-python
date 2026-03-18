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

"""Performs requests to the Google Maps Pollen API."""

from googlemaps import exceptions


_POLLEN_BASE_URL = "https://pollen.googleapis.com"


def _pollen_extract(response):
    """
    Mimics the exception handling logic in ``client._get_body``, but
    for Pollen API which uses a different response format.
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


def _format_pollen_location(location):
    """
    Formats a location for the Pollen API.

    :param location: A lat/lng dict or tuple.
    :type location: dict or tuple

    :rtype: dict
    """
    if isinstance(location, (tuple, list)):
        return {"latitude": location[0], "longitude": location[1]}
    elif isinstance(location, dict):
        if "latitude" in location and "longitude" in location:
            return location
        elif "lat" in location and "lng" in location:
            return {"latitude": location["lat"], "longitude": location["lng"]}
    raise ValueError("Invalid location format: %s" % location)


def current_pollen(client, location, language_code=None, plants_description=None):
    """Returns current pollen conditions for a specific location.

    The Pollen API provides daily pollen forecast information for
    over 65 countries at up to 1km resolution.

    For more information see: https://developers.google.com/maps/documentation/pollen

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param language_code: Language code for the response (e.g., "en").
    :type language_code: string

    :param plants_description: Whether to include plants description in response.
    :type plants_description: bool

    :rtype: dict containing current pollen information
    """

    request_body = {
        "location": _format_pollen_location(location),
    }

    if language_code:
        request_body["languageCode"] = language_code

    if plants_description is not None:
        request_body["plantsDescription"] = plants_description

    return client._request(
        "/v1/currentConditions:lookup",
        {},
        base_url=_POLLEN_BASE_URL,
        extract_body=_pollen_extract,
        post_json=request_body
    )


def pollen_forecast(client, location, days=None, language_code=None,
                    plants_description=None, page_size=None, page_token=None):
    """Returns pollen forecast for a specific location for up to 5 days.

    For more information see: https://developers.google.com/maps/documentation/pollen

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param days: Number of forecast days to return (1-5).
    :type days: int

    :param language_code: Language code for the response.
    :type language_code: string

    :param plants_description: Whether to include plants description in response.
    :type plants_description: bool

    :param page_size: Maximum number of daily info records per page.
    :type page_size: int

    :param page_token: Token for pagination.
    :type page_token: string

    :rtype: dict containing forecast information
    """

    request_body = {
        "location": _format_pollen_location(location),
    }

    if days:
        request_body["days"] = days

    if language_code:
        request_body["languageCode"] = language_code

    if plants_description is not None:
        request_body["plantsDescription"] = plants_description

    if page_size:
        request_body["pageSize"] = page_size

    if page_token:
        request_body["pageToken"] = page_token

    return client._request(
        "/v1/forecast:lookup",
        {},
        base_url=_POLLEN_BASE_URL,
        extract_body=_pollen_extract,
        post_json=request_body
    )


def pollen_heatmap_tile(client, map_type, zoom, x, y):
    """Returns a PNG heatmap tile for pollen visualization.

    :param map_type: Type of pollen map. Valid values: "TREE_UPI", "GRASS_UPI",
        "WEED_UPI".
    :type map_type: string

    :param zoom: Zoom level (0-16).
    :type zoom: int

    :param x: Tile X coordinate.
    :type x: int

    :param y: Tile Y coordinate.
    :type y: int

    :rtype: bytes (PNG image data)
    """

    url = "/v1/mapTypes/%s/heatmapTiles/%d/%d/%d" % (map_type, zoom, x, y)

    # For heatmap tiles, we need to return raw bytes, not JSON
    response = client.session.get(
        _POLLEN_BASE_URL + url + "?key=" + client.key
    )

    if response.status_code != 200:
        raise exceptions.HTTPError(response.status_code)

    return response.content
