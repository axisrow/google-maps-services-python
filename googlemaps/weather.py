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

"""Performs requests to the Google Maps Weather API."""

from datetime import datetime

from googlemaps._api import extract_api_body
from googlemaps._api import format_lat_lng
from googlemaps._api import modern_api_request


_WEATHER_BASE_URL = "https://weather.googleapis.com"


def _weather_extract(response):
    """
    Mimics the exception handling logic in ``client._get_body``, but
    for Weather API which uses a different response format.
    """
    return extract_api_body(response)


def _format_weather_location(location):
    """
    Formats a location for the Weather API.

    :param location: A lat/lng dict or tuple.
    :type location: dict or tuple

    :rtype: dict
    """
    return format_lat_lng(location)


def _parse_time(time_value):
    if isinstance(time_value, datetime):
        return time_value
    if isinstance(time_value, str):
        return datetime.fromisoformat(time_value.replace("Z", "+00:00"))
    raise ValueError("Invalid time value: %s" % time_value)


def _period_to_size(period, unit_seconds):
    if period is None:
        return None

    if isinstance(period, tuple):
        start_time, end_time = period
    elif isinstance(period, dict):
        start_time = period.get("startTime")
        end_time = period.get("endTime")
    else:
        raise ValueError("Invalid period format: %s" % period)

    if start_time is None or end_time is None:
        raise ValueError("period must include startTime and endTime")

    delta_seconds = (_parse_time(end_time) - _parse_time(start_time)).total_seconds()
    if delta_seconds <= 0:
        raise ValueError("period endTime must be after startTime")

    return max(1, int((delta_seconds + unit_seconds - 1) // unit_seconds))


def _weather_params(location, language_code=None, units=None, page_size=None,
                    page_token=None):
    formatted_location = _format_weather_location(location)
    params = {
        "location.latitude": formatted_location["latitude"],
        "location.longitude": formatted_location["longitude"],
    }

    if language_code:
        params["languageCode"] = language_code

    if units:
        params["unitsSystem"] = units

    if page_size:
        params["pageSize"] = page_size

    if page_token:
        params["pageToken"] = page_token

    return params


def current_weather(client, location, language_code=None, units=None):
    """Returns current weather conditions for a specific location.

    The Weather API provides minute-by-minute, hourly, and daily weather
    forecast data for any location on Earth.

    For more information see: https://developers.google.com/maps/documentation/weather

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param language_code: Language code for the response (e.g., "en").
    :type language_code: string

    :param units: Units for the response. Valid values: "METRIC", "IMPERIAL".
    :type units: string

    :rtype: dict containing current weather information
    """

    params = _weather_params(
        location,
        language_code=language_code,
        units=units,
    )

    return modern_api_request(
        client,
        "/v1/currentConditions:lookup",
        base_url=_WEATHER_BASE_URL,
        params=params,
        extract_body=_weather_extract,
    )


def weather_forecast(client, location, language_code=None, units=None, period=None,
                     page_size=None, page_token=None):
    """Returns weather forecast for a specific location and time period.

    For more information see: https://developers.google.com/maps/documentation/weather

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param language_code: Language code for the response.
    :type language_code: string

    :param units: Units for the response. Valid values: "METRIC", "IMPERIAL".
    :type units: string

    :param period: Time period dict with 'startTime' and 'endTime' keys.
    :type period: dict

    :param page_size: Maximum number of forecast records per page.
    :type page_size: int

    :param page_token: Token for pagination.
    :type page_token: string

    :rtype: dict containing forecast information
    """

    params = _weather_params(
        location,
        language_code=language_code,
        units=units,
        page_size=page_size,
        page_token=page_token,
    )

    if period:
        params["days"] = _period_to_size(period, 86400)

    return modern_api_request(
        client,
        "/v1/forecast/days:lookup",
        base_url=_WEATHER_BASE_URL,
        params=params,
        extract_body=_weather_extract,
    )


def weather_hourly_forecast(client, location, language_code=None, units=None, period=None,
                            page_size=None, page_token=None):
    """Returns hourly weather forecast for a specific location.

    For more information see: https://developers.google.com/maps/documentation/weather

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param language_code: Language code for the response.
    :type language_code: string

    :param units: Units for the response. Valid values: "METRIC", "IMPERIAL".
    :type units: string

    :param period: Time period dict with 'startTime' and 'endTime' keys.
    :type period: dict

    :param page_size: Maximum number of hourly forecast records per page.
    :type page_size: int

    :param page_token: Token for pagination.
    :type page_token: string

    :rtype: dict containing hourly forecast information
    """

    params = _weather_params(
        location,
        language_code=language_code,
        units=units,
        page_size=page_size,
        page_token=page_token,
    )

    if period:
        params["hours"] = _period_to_size(period, 3600)

    return modern_api_request(
        client,
        "/v1/forecast/hours:lookup",
        base_url=_WEATHER_BASE_URL,
        params=params,
        extract_body=_weather_extract,
    )


def historical_weather(client, location, period, language_code=None, units=None,
                       page_size=None, page_token=None):
    """Returns historical weather data for a specific location and time period.

    For more information see: https://developers.google.com/maps/documentation/weather

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param period: Time period dict with 'startTime' and 'endTime' keys.
    :type period: dict

    :param language_code: Language code for the response.
    :type language_code: string

    :param units: Units for the response. Valid values: "METRIC", "IMPERIAL".
    :type units: string

    :param page_size: Maximum number of records per page.
    :type page_size: int

    :param page_token: Token for pagination.
    :type page_token: string

    :rtype: dict containing historical weather information
    """

    params = _weather_params(
        location,
        language_code=language_code,
        units=units,
        page_size=page_size,
        page_token=page_token,
    )
    params["hours"] = _period_to_size(period, 3600)

    return modern_api_request(
        client,
        "/v1/history/hours:lookup",
        base_url=_WEATHER_BASE_URL,
        params=params,
        extract_body=_weather_extract,
    )


def weather_alerts(client, location, language_code=None, page_size=None,
                   page_token=None):
    """Returns public weather alerts for a specific location.

    For more information see: https://developers.google.com/maps/documentation/weather

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param language_code: Language code for the response.
    :type language_code: string

    :param page_size: Maximum number of alert records per page.
    :type page_size: int

    :param page_token: Token for pagination.
    :type page_token: string

    :rtype: dict containing weather alert information
    """
    params = _weather_params(
        location,
        language_code=language_code,
        page_size=page_size,
        page_token=page_token,
    )

    return modern_api_request(
        client,
        "/v1/publicAlerts:lookup",
        base_url=_WEATHER_BASE_URL,
        params=params,
        extract_body=_weather_extract,
    )
