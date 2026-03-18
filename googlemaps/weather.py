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

from googlemaps import exceptions


_WEATHER_BASE_URL = "https://weather.googleapis.com"


def _weather_extract(response):
    """
    Mimics the exception handling logic in ``client._get_body``, but
    for Weather API which uses a different response format.
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


def _format_weather_location(location):
    """
    Formats a location for the Weather API.

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


def current_weather(client, location, weather_elements=None, extra_computations=None,
                    language_code=None, units=None):
    """Returns current weather conditions for a specific location.

    The Weather API provides minute-by-minute, hourly, and daily weather
    forecast data for any location on Earth.

    For more information see: https://developers.google.com/maps/documentation/weather

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param weather_elements: List of weather elements to include.
        Valid values: "temperature", "dewPoint", "relativeHumidity",
        "windSpeed", "windDirection", "pressure", "precipitation",
        "cloudCover", "visibility", "uvIndex", "feelsLikeTemperature",
        "weatherCondition", "daytime", "airQualityIndex", "sunriseSunset",
        "isobaricCondition", "pressureTendency".
    :type weather_elements: list of strings

    :param extra_computations: List of extra computations to perform.
    :type extra_computations: list of strings

    :param language_code: Language code for the response (e.g., "en").
    :type language_code: string

    :param units: Units for the response. Valid values: "METRIC", "IMPERIAL".
    :type units: string

    :rtype: dict containing current weather information
    """

    request_body = {
        "location": _format_weather_location(location),
    }

    if weather_elements:
        request_body["weatherElements"] = weather_elements

    if extra_computations:
        request_body["extraComputations"] = extra_computations

    if language_code:
        request_body["languageCode"] = language_code

    if units:
        request_body["units"] = units

    return client._request(
        "/v1/currentConditions:lookup",
        {},
        base_url=_WEATHER_BASE_URL,
        extract_body=_weather_extract,
        post_json=request_body
    )


def weather_forecast(client, location, weather_elements=None, extra_computations=None,
                     language_code=None, units=None, period=None,
                     page_size=None, page_token=None):
    """Returns weather forecast for a specific location and time period.

    For more information see: https://developers.google.com/maps/documentation/weather

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param weather_elements: List of weather elements to include.
    :type weather_elements: list of strings

    :param extra_computations: List of extra computations to perform.
    :type extra_computations: list of strings

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

    request_body = {
        "location": _format_weather_location(location),
    }

    if weather_elements:
        request_body["weatherElements"] = weather_elements

    if extra_computations:
        request_body["extraComputations"] = extra_computations

    if language_code:
        request_body["languageCode"] = language_code

    if units:
        request_body["units"] = units

    if period:
        request_body["period"] = period

    if page_size:
        request_body["pageSize"] = page_size

    if page_token:
        request_body["pageToken"] = page_token

    return client._request(
        "/v1/forecast:lookup",
        {},
        base_url=_WEATHER_BASE_URL,
        extract_body=_weather_extract,
        post_json=request_body
    )


def weather_hourly_forecast(client, location, weather_elements=None, extra_computations=None,
                            language_code=None, units=None, period=None,
                            page_size=None, page_token=None):
    """Returns hourly weather forecast for a specific location.

    For more information see: https://developers.google.com/maps/documentation/weather

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param weather_elements: List of weather elements to include.
    :type weather_elements: list of strings

    :param extra_computations: List of extra computations to perform.
    :type extra_computations: list of strings

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

    request_body = {
        "location": _format_weather_location(location),
    }

    if weather_elements:
        request_body["weatherElements"] = weather_elements

    if extra_computations:
        request_body["extraComputations"] = extra_computations

    if language_code:
        request_body["languageCode"] = language_code

    if units:
        request_body["units"] = units

    if period:
        request_body["period"] = period

    if page_size:
        request_body["pageSize"] = page_size

    if page_token:
        request_body["pageToken"] = page_token

    return client._request(
        "/v1/forecast/hours:lookup",
        {},
        base_url=_WEATHER_BASE_URL,
        extract_body=_weather_extract,
        post_json=request_body
    )


def historical_weather(client, location, period, weather_elements=None,
                       extra_computations=None, language_code=None, units=None,
                       page_size=None, page_token=None):
    """Returns historical weather data for a specific location and time period.

    For more information see: https://developers.google.com/maps/documentation/weather

    :param location: Location for the request. Can be a (lat, lng) tuple
        or a dict with 'latitude' and 'longitude' keys.
    :type location: tuple or dict

    :param period: Time period dict with 'startTime' and 'endTime' keys.
    :type period: dict

    :param weather_elements: List of weather elements to include.
    :type weather_elements: list of strings

    :param extra_computations: List of extra computations to perform.
    :type extra_computations: list of strings

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

    request_body = {
        "location": _format_weather_location(location),
        "period": period,
    }

    if weather_elements:
        request_body["weatherElements"] = weather_elements

    if extra_computations:
        request_body["extraComputations"] = extra_computations

    if language_code:
        request_body["languageCode"] = language_code

    if units:
        request_body["units"] = units

    if page_size:
        request_body["pageSize"] = page_size

    if page_token:
        request_body["pageToken"] = page_token

    return client._request(
        "/v1/history:lookup",
        {},
        base_url=_WEATHER_BASE_URL,
        extract_body=_weather_extract,
        post_json=request_body
    )
