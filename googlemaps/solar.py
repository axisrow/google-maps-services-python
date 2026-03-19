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

"""Performs requests to the Google Maps Solar API."""

import json

from googlemaps import exceptions


_SOLAR_BASE_URL = "https://solar.googleapis.com"


def _solar_extract(response):
    """
    Mimics the exception handling logic in ``client._get_body``, but
    for Solar API which uses a different response format.
    """
    try:
        body = response.json()
    except json.JSONDecodeError:
        raise exceptions.TransportError("Invalid JSON response from API")

    if response.status_code == 200:
        return body

    error = body.get("error", {})
    message = error.get("message", "Unknown error")

    if response.status_code == 403:
        raise exceptions._OverQueryLimit(response.status_code, message)
    else:
        raise exceptions.ApiError(response.status_code, message)


def _format_solar_location(location):
    """
    Formats a location for the Solar API.

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


def building_insights(client, location, required_quality=None):
    """Returns solar potential information for a building at a specific location.

    The Solar API provides detailed solar potential analysis including
    solar panel placement, energy production estimates, and cost savings.

    For more information see: https://developers.google.com/maps/documentation/solar

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param required_quality: Minimum quality level required. Valid values:
        "HIGH", "MEDIUM", "LOW". Higher quality means more accurate data
        but may take longer to process.
    :type required_quality: string

    :rtype: dict containing building solar insights
    """

    params = {
        "location.latitude": _format_solar_location(location)["latitude"],
        "location.longitude": _format_solar_location(location)["longitude"],
    }

    if required_quality:
        params["requiredQuality"] = required_quality

    return client._request(
        "/v1/buildingInsights:findClosest",
        params,
        base_url=_SOLAR_BASE_URL,
        extract_body=_solar_extract
    )


def solar_data_layers(client, location, required_quality=None,
                      pixel_size_meters=None, view=None):
    """Returns solar data layers (imagery) for a region around a location.

    The data layers include Digital Surface Model (DSM), Digital Terrain Model (DTM),
    RGB imagery, and mask of analyzed buildings.

    For more information see: https://developers.google.com/maps/documentation/solar

    :param location: Center location for the region. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param required_quality: Minimum quality level required. Valid values:
        "HIGH", "MEDIUM", "LOW".
    :type required_quality: string

    :param pixel_size_meters: The size of the region to cover in meters.
        Maximum is 1000 meters. Defaults to 100.
    :type pixel_size_meters: float

    :param view: The view to return. Valid values: "FULL_DATASET" (default),
        "IMAGERY_ONLY", "_MASK_ONLY".
    :type view: string

    :rtype: dict containing URLs to download solar data layers
    """

    params = {
        "location.latitude": _format_solar_location(location)["latitude"],
        "location.longitude": _format_solar_location(location)["longitude"],
    }

    if required_quality:
        params["requiredQuality"] = required_quality

    if pixel_size_meters:
        params["pixelSizeMeters"] = pixel_size_meters

    if view:
        params["view"] = view

    return client._request(
        "/v1/dataLayers:get",
        params,
        base_url=_SOLAR_BASE_URL,
        extract_body=_solar_extract
    )


def geo_tiff(client, url):
    """Returns GeoTIFF imagery data from a URL returned by solar_data_layers.

    :param url: The URL of the GeoTIFF to download.
    :type url: string

    :rtype: bytes (GeoTIFF image data)
    """
    # Validate URL to prevent SSRF
    if not url or not url.startswith("https://solar.googleapis.com"):
        raise ValueError("URL must be from solar.googleapis.com domain, got: %s" % url)

    # For GeoTIFF, we need to return raw bytes
    timeout = client.timeout if client.timeout is not None else 30
    try:
        response = client.session.get(url, timeout=timeout)
    except Exception as e:
        raise exceptions.TransportError(e)

    if response.status_code != 200:
        raise exceptions.HTTPError(response.status_code)

    return response.content
