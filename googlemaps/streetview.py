#
# Copyright 2026 Google Inc. All rights reserved.
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

"""Performs requests to the Google Street View Static API."""

from googlemaps import convert


STREETVIEW_SOURCES = {"default", "outdoor"}


def street_view(
    client,
    size,
    location=None,
    pano=None,
    heading=None,
    fov=None,
    pitch=None,
    radius=None,
    source=None,
    return_error_code=None,
):
    """Downloads an image from the Street View Static API."""
    if not location and not pano:
        raise ValueError("either location or pano is required")

    params = {"size": convert.size(size)}

    if location:
        params["location"] = convert.latlng(location) if not convert.is_string(location) else location
    if pano:
        params["pano"] = pano
    if heading is not None:
        params["heading"] = heading
    if fov is not None:
        params["fov"] = fov
    if pitch is not None:
        params["pitch"] = pitch
    if radius is not None:
        params["radius"] = radius
    if source:
        if source not in STREETVIEW_SOURCES:
            raise ValueError("Invalid source")
        params["source"] = source
    if return_error_code:
        params["return_error_code"] = "true"

    response = client._request(
        "/maps/api/streetview",
        params,
        extract_body=lambda response: response,
        requests_kwargs={"stream": True},
    )
    return response.iter_content()
