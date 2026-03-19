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

"""Performs requests to the Google Maps Air Quality API."""

import json

from googlemaps import exceptions


_AIRQUALITY_BASE_URL = "https://airquality.googleapis.com"


def _airquality_extract(response):
    """
    Mimics the exception handling logic in ``client._get_body``, but
    for Air Quality API which uses a different response format.
    """
    try:
        body = response.json()
    except json.JSONDecodeError:
        raise exceptions.TransportError("Invalid JSON response from API")

    if "error" in body:
        error = body["error"]
        status = error.get("status", response.status_code)
        message = error.get("message")

        if response.status_code == 403 or status == "RESOURCE_EXHAUSTED":
            raise exceptions._OverQueryLimit(status, message)

        raise exceptions.ApiError(status, message)

    if response.status_code != 200:
        raise exceptions.HTTPError(response.status_code)

    return body


def _format_location(location):
    """
    Formats a location for the Air Quality API.

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


def current_air_quality(client, location, extra_computations=None,
                        language_code=None, universal_aqi=None,
                        aqi_scale=None):
    """Returns current air quality conditions for a specific location.

    The Air Quality API provides hourly air quality information for
    over 100 countries at up to 500x500 meters resolution.

    For more information see: https://developers.google.com/maps/documentation/air-quality

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param extra_computations: List of extra computations to perform.
        Valid values: "HEALTH_RECOMMENDATIONS", "DOMINANT_POLLUTANT_CONCENTRATION",
        "POLLUTANT_CONCENTRATION", "LOCAL_AQI", "POLLUTANT_ADDITIONAL_INFO".
    :type extra_computations: list of strings

    :param language_code: Language code for the response (e.g., "en").
    :type language_code: string

    :param universal_aqi: Whether to include universal AQI in response.
    :type universal_aqi: bool

    :param aqi_scale: The AQI scale to use for the response. Valid values:
        "UAQI_IN_AQI", "UAQI_IN_GREEN", "PM25_IN_AQI", "PM10_IN_AQI",
        "CO_IN_AQI", "SO2_IN_AQI", "NO2_IN_AQI", "O3_IN_AQI", "EU_AQI",
        "CAQI", "US_AQI".
    :type aqi_scale: string

    :rtype: dict containing air quality information
    """

    request_body = {
        "location": _format_location(location),
    }

    if extra_computations:
        request_body["extraComputations"] = extra_computations

    if language_code:
        request_body["languageCode"] = language_code

    if universal_aqi is not None:
        request_body["universalAqi"] = universal_aqi

    if aqi_scale:
        request_body["uaqiColorPalette"] = aqi_scale

    return client._request(
        "/v1/currentConditions:lookup",
        {},
        base_url=_AIRQUALITY_BASE_URL,
        accepts_clientid=False,
        extract_body=_airquality_extract,
        post_json=request_body
    )


def air_quality_forecast(client, location, period=None, extra_computations=None,
                         language_code=None, universal_aqi=None,
                         page_size=None, page_token=None, aqi_scale=None):
    """Returns air quality forecast for a specific location and time period.

    For more information see: https://developers.google.com/maps/documentation/air-quality

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param period: Time period dict with 'startTime' and 'endTime' keys
        (RFC 3339 timestamps), or a tuple of datetime objects.
    :type period: dict or tuple

    :param extra_computations: List of extra computations to perform.
    :type extra_computations: list of strings

    :param language_code: Language code for the response.
    :type language_code: string

    :param universal_aqi: Whether to include universal AQI in response.
    :type universal_aqi: bool

    :param page_size: Maximum number of hourly info records per page.
    :type page_size: int

    :param page_token: Token for pagination.
    :type page_token: string

    :param aqi_scale: The AQI scale to use for the response.
    :type aqi_scale: string

    :rtype: dict containing forecast information
    """

    request_body = {
        "location": _format_location(location),
    }

    if period:
        if isinstance(period, tuple):
            start_time, end_time = period
            request_body["period"] = {
                "startTime": _format_time(start_time),
                "endTime": _format_time(end_time)
            }
        else:
            request_body["period"] = period

    if extra_computations:
        request_body["extraComputations"] = extra_computations

    if language_code:
        request_body["languageCode"] = language_code

    if universal_aqi is not None:
        request_body["universalAqi"] = universal_aqi

    if page_size:
        request_body["pageSize"] = page_size

    if page_token:
        request_body["pageToken"] = page_token

    if aqi_scale:
        request_body["uaqiColorPalette"] = aqi_scale

    return client._request(
        "/v1/forecast:lookup",
        {},
        base_url=_AIRQUALITY_BASE_URL,
        accepts_clientid=False,
        extract_body=_airquality_extract,
        post_json=request_body
    )


def historical_air_quality(client, location, period, extra_computations=None,
                           language_code=None, universal_aqi=None,
                           page_size=None, page_token=None, aqi_scale=None):
    """Returns historical air quality data for a specific location and time period.

    For more information see: https://developers.google.com/maps/documentation/air-quality

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param period: Time period dict with 'startTime' and 'endTime' keys
        (RFC 3339 timestamps), or a tuple of datetime objects.
    :type period: dict or tuple

    :param extra_computations: List of extra computations to perform.
    :type extra_computations: list of strings

    :param language_code: Language code for the response.
    :type language_code: string

    :param universal_aqi: Whether to include universal AQI in response.
    :type universal_aqi: bool

    :param page_size: Maximum number of hourly info records per page.
    :type page_size: int

    :param page_token: Token for pagination.
    :type page_token: string

    :param aqi_scale: The AQI scale to use for the response.
    :type aqi_scale: string

    :rtype: dict containing historical air quality information
    """

    request_body = {
        "location": _format_location(location),
    }

    if period:
        if isinstance(period, tuple):
            start_time, end_time = period
            request_body["period"] = {
                "startTime": _format_time(start_time),
                "endTime": _format_time(end_time)
            }
        else:
            request_body["period"] = period

    if extra_computations:
        request_body["extraComputations"] = extra_computations

    if language_code:
        request_body["languageCode"] = language_code

    if universal_aqi is not None:
        request_body["universalAqi"] = universal_aqi

    if page_size:
        request_body["pageSize"] = page_size

    if page_token:
        request_body["pageToken"] = page_token

    if aqi_scale:
        request_body["uaqiColorPalette"] = aqi_scale

    return client._request(
        "/v1/history:lookup",
        {},
        base_url=_AIRQUALITY_BASE_URL,
        accepts_clientid=False,
        extract_body=_airquality_extract,
        post_json=request_body
    )


def air_quality_heatmap_tile(client, map_type, zoom, x, y):
    """Returns a PNG heatmap tile for air quality visualization.

    :param map_type: Type of air quality map. Valid values: "US_AQI", "UAQI_RED_GREEN",
        "UAQI_INDIGO_PERSIAN", "PM25", "PM10", "CO", "NO2", "SO2", "O3".
    :type map_type: string

    :param zoom: Zoom level (0-22).
    :type zoom: int

    :param x: Tile X coordinate.
    :type x: int

    :param y: Tile Y coordinate.
    :type y: int

    :rtype: bytes (PNG image data)
    """

    url = "/v1/mapTypes/%s/heatmapTiles/%d/%d/%d" % (map_type, zoom, x, y)

    # For heatmap tiles, we need to return raw bytes, not JSON
    timeout = client.timeout if client.timeout is not None else 30
    try:
        response = client.session.get(
            _AIRQUALITY_BASE_URL + url + "?key=" + client.key,
            timeout=timeout
        )
    except Exception as e:
        raise exceptions.TransportError(e)

    if response.status_code != 200:
        raise exceptions.HTTPError(response.status_code)

    return response.content


def _format_time(time_value):
    """
    Formats a time value for the Air Quality API (RFC 3339 timestamp).

    :param time_value: A datetime object or string timestamp.
    :type time_value: datetime.datetime or string

    :rtype: string
    """
    if isinstance(time_value, str):
        return time_value
    # Assume datetime object - format with timezone
    if hasattr(time_value, 'strftime'):
        return time_value.strftime("%Y-%m-%dT%H:%M:%SZ")
    return time_value
