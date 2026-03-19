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

from googlemaps._api import extract_api_body
from googlemaps._api import format_lat_lng
from googlemaps._api import request_binary_content


_POLLEN_BASE_URL = "https://pollen.googleapis.com"


def _pollen_extract(response):
    """
    Mimics the exception handling logic in ``client._get_body``, but
    for Pollen API which uses a different response format.
    """
    return extract_api_body(response)


def _current_pollen_extract(response):
    body = _pollen_extract(response)
    daily_info = body.get("dailyInfo", [])
    if daily_info:
        return daily_info[0]
    return {}


def _format_pollen_location(location):
    """
    Formats a location for the Pollen API.

    :param location: A lat/lng dict or tuple.
    :type location: dict or tuple

    :rtype: dict
    """
    return format_lat_lng(location)


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

    formatted_location = _format_pollen_location(location)
    params = {
        "location.latitude": formatted_location["latitude"],
        "location.longitude": formatted_location["longitude"],
        "days": 1,
    }

    if language_code:
        params["languageCode"] = language_code

    if plants_description is not None:
        params["plantsDescription"] = plants_description

    return client._request(
        "/v1/forecast:lookup",
        params,
        base_url=_POLLEN_BASE_URL,
        accepts_clientid=False,
        extract_body=_current_pollen_extract
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

    formatted_location = _format_pollen_location(location)
    params = {
        "location.latitude": formatted_location["latitude"],
        "location.longitude": formatted_location["longitude"],
    }

    if days:
        params["days"] = days

    if language_code:
        params["languageCode"] = language_code

    if plants_description is not None:
        params["plantsDescription"] = plants_description

    if page_size:
        params["pageSize"] = page_size

    if page_token:
        params["pageToken"] = page_token

    return client._request(
        "/v1/forecast:lookup",
        params,
        base_url=_POLLEN_BASE_URL,
        accepts_clientid=False,
        extract_body=_pollen_extract
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

    return request_binary_content(client, _POLLEN_BASE_URL + url + "?key=" + client.key)
