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

"""Internal helpers shared by newer Google Maps API modules."""

import json

from googlemaps import exceptions


def parse_json_response(response):
    """Parse a JSON response and normalize decode failures."""
    try:
        return response.json()
    except json.JSONDecodeError:
        raise exceptions.TransportError("Invalid JSON response from API")


def extract_api_body(response):
    """Extract a JSON API body using the newer error response contract."""
    body = parse_json_response(response)

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


def format_lat_lng(location):
    """Normalize supported lat/lng inputs into a latitude/longitude dict."""
    if isinstance(location, (tuple, list)):
        return {"latitude": location[0], "longitude": location[1]}
    elif isinstance(location, dict):
        if "latitude" in location and "longitude" in location:
            return location
        elif "lat" in location and "lng" in location:
            return {"latitude": location["lat"], "longitude": location["lng"]}
    raise ValueError("Invalid location format: %s" % location)


def request_binary_content(client, url):
    """Perform a GET request that returns raw bytes instead of JSON."""
    timeout = client.timeout if client.timeout is not None else 30
    try:
        response = client.session.get(url, timeout=timeout)
    except Exception as exc:
        raise exceptions.TransportError(exc)

    if response.status_code != 200:
        raise exceptions.HTTPError(response.status_code)

    return response.content
