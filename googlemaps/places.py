#
# Copyright 2015 Google Inc. All rights reserved.
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

"""Performs requests to the Google Places API."""
import warnings

from googlemaps import convert
from googlemaps._api import extract_api_body
from googlemaps._api import format_lat_lng
from googlemaps._api import modern_api_request
from googlemaps._api import request_binary_content


_PLACES_NEW_BASE_URL = "https://places.googleapis.com"


PLACES_FIND_FIELDS_BASIC = {"business_status",
        "formatted_address",
        "geometry",
        "geometry/location",
        "geometry/location/lat",
        "geometry/location/lng",
        "geometry/viewport",
        "geometry/viewport/northeast",
        "geometry/viewport/northeast/lat",
        "geometry/viewport/northeast/lng",
        "geometry/viewport/southwest",
        "geometry/viewport/southwest/lat",
        "geometry/viewport/southwest/lng",
        "icon",
        "name",
        "permanently_closed",
        "photos",
        "place_id",
        "plus_code",
        "types",}

PLACES_FIND_FIELDS_CONTACT = {"opening_hours"}

PLACES_FIND_FIELDS_ATMOSPHERE = {"price_level", "rating", "user_ratings_total"}

PLACES_FIND_FIELDS = (
    PLACES_FIND_FIELDS_BASIC
    ^ PLACES_FIND_FIELDS_CONTACT
    ^ PLACES_FIND_FIELDS_ATMOSPHERE
)

PLACES_DETAIL_FIELDS_BASIC = {
    "address_component",
    "adr_address",
    "business_status",
    "formatted_address",
    "geometry",
    "geometry/location",
    "geometry/location/lat",
    "geometry/location/lng",
    "geometry/viewport",
    "geometry/viewport/northeast",
    "geometry/viewport/northeast/lat",
    "geometry/viewport/northeast/lng",
    "geometry/viewport/southwest",
    "geometry/viewport/southwest/lat",
    "geometry/viewport/southwest/lng",
    "icon",
    "name",
    "permanently_closed",
    "photo",
    "place_id",
    "plus_code",
    "type",
    "url",
    "utc_offset",
    "vicinity",
    "wheelchair_accessible_entrance"
}

PLACES_DETAIL_FIELDS_CONTACT = {
    "formatted_phone_number",
    "international_phone_number",
    "opening_hours",
    "current_opening_hours",
    "secondary_opening_hours",
    "website",
}

PLACES_DETAIL_FIELDS_ATMOSPHERE = {
    "curbside_pickup",
    "delivery",
    "dine_in",
    "editorial_summary",
    "price_level",
    "rating",
    "reservable",
    "review",  # prefer "reviews" to match API documentation
    "reviews",
    "serves_beer",
    "serves_breakfast",
    "serves_brunch",
    "serves_dinner",
    "serves_lunch",
    "serves_vegetarian_food",
    "serves_wine",
    "takeout",
    "user_ratings_total"
}

PLACES_DETAIL_FIELDS = (
    PLACES_DETAIL_FIELDS_BASIC
    ^ PLACES_DETAIL_FIELDS_CONTACT
    ^ PLACES_DETAIL_FIELDS_ATMOSPHERE
)

DEPRECATED_FIELDS = {"permanently_closed", "review"}
DEPRECATED_FIELDS_MESSAGE = (
    "Fields, %s, are deprecated. "
    "Read more at https://developers.google.com/maps/deprecations."
)


def find_place(
    client, input, input_type, fields=None, location_bias=None, language=None
):
    """
    Legacy Places API request that takes a text input and returns a place.
    The text input can be any kind of Places data, for example,
    a name, address, or phone number.

    :param input: The text input specifying which place to search for (for
                  example, a name, address, or phone number).
    :type input: string

    :param input_type: The type of input. This can be one of either 'textquery'
                  or 'phonenumber'.
    :type input_type: string

    :param fields: The fields specifying the types of place data to return. For full details see:
                   https://developers.google.com/places/web-service/search#FindPlaceRequests
    :type fields: list

    :param location_bias: Prefer results in a specified area, by specifying
                          either a radius plus lat/lng, or two lat/lng pairs
                          representing the points of a rectangle. See:
                          https://developers.google.com/places/web-service/search#FindPlaceRequests
    :type location_bias: string

    :param language: The language in which to return results.
    :type language: string

    :rtype: result dict with the following keys:
            status: status code
            candidates: list of places
    """
    params = {"input": input, "inputtype": input_type}

    if input_type != "textquery" and input_type != "phonenumber":
        raise ValueError(
            "Valid values for the `input_type` param for "
            "`find_place` are 'textquery' or 'phonenumber', "
            "the given value is invalid: '%s'" % input_type
        )

    if fields:
        deprecated_fields = set(fields) & DEPRECATED_FIELDS
        if deprecated_fields:
            warnings.warn(
                DEPRECATED_FIELDS_MESSAGE % str(list(deprecated_fields)),
                DeprecationWarning,
            )

        invalid_fields = set(fields) - PLACES_FIND_FIELDS
        if invalid_fields:
            raise ValueError(
                "Valid values for the `fields` param for "
                "`find_place` are '%s', these given field(s) "
                "are invalid: '%s'"
                % ("', '".join(PLACES_FIND_FIELDS), "', '".join(invalid_fields))
            )
        params["fields"] = convert.join_list(",", fields)

    if location_bias:
        valid = ["ipbias", "point", "circle", "rectangle"]
        if location_bias.split(":")[0] not in valid:
            raise ValueError("location_bias should be prefixed with one of: %s" % valid)
        params["locationbias"] = location_bias
    if language:
        params["language"] = language

    return client._request("/maps/api/place/findplacefromtext/json", params)


def places(
    client,
    query=None,
    location=None,
    radius=None,
    language=None,
    min_price=None,
    max_price=None,
    open_now=False,
    type=None,
    region=None,
    page_token=None,
):
    """
    Legacy Places API text search.

    :param query: The text string on which to search, for example: "restaurant".
    :type query: string

    :param location: The latitude/longitude value for which you wish to obtain the
        closest, human-readable address.
    :type location: string, dict, list, or tuple

    :param radius: Distance in meters within which to bias results.
    :type radius: int

    :param language: The language in which to return results.
    :type language: string

    :param min_price: Restricts results to only those places with no less than
        this price level. Valid values are in the range from 0 (most affordable)
        to 4 (most expensive).
    :type min_price: int

    :param max_price: Restricts results to only those places with no greater
        than this price level. Valid values are in the range from 0 (most
        affordable) to 4 (most expensive).
    :type max_price: int

    :param open_now: Return only those places that are open for business at
        the time the query is sent.
    :type open_now: bool

    :param type: Restricts the results to places matching the specified type.
        The full list of supported types is available here:
        https://developers.google.com/places/supported_types
    :type type: string

    :param region: The region code, optional parameter.
        See more @ https://developers.google.com/places/web-service/search
    :type region: string

    :param page_token: Token from a previous search that when provided will
        returns the next page of results for the same search.
    :type page_token: string

    :rtype: result dict with the following keys:
        results: list of places
        html_attributions: set of attributions which must be displayed
        next_page_token: token for retrieving the next page of results
    """
    return _places(
        client,
        "text",
        query=query,
        location=location,
        radius=radius,
        language=language,
        min_price=min_price,
        max_price=max_price,
        open_now=open_now,
        type=type,
        region=region,
        page_token=page_token,
    )


def places_nearby(
    client,
    location=None,
    radius=None,
    keyword=None,
    language=None,
    min_price=None,
    max_price=None,
    name=None,
    open_now=False,
    rank_by=None,
    type=None,
    page_token=None,
):
    """
    Performs a legacy Places API nearby search.

    :param location: The latitude/longitude value for which you wish to obtain the
                     closest, human-readable address.
    :type location: string, dict, list, or tuple

    :param radius: Distance in meters within which to bias results.
    :type radius: int

    :param region: The region code, optional parameter.
        See more @ https://developers.google.com/places/web-service/search
    :type region: string

    :param keyword: A term to be matched against all content that Google has
                    indexed for this place.
    :type keyword: string

    :param language: The language in which to return results.
    :type language: string

    :param min_price: Restricts results to only those places with no less than
                      this price level. Valid values are in the range from 0
                      (most affordable) to 4 (most expensive).
    :type min_price: int

    :param max_price: Restricts results to only those places with no greater
                      than this price level. Valid values are in the range
                      from 0 (most affordable) to 4 (most expensive).
    :type max_price: int

    :param name: One or more terms to be matched against the names of places.
    :type name: string or list of strings

    :param open_now: Return only those places that are open for business at
                     the time the query is sent.
    :type open_now: bool

    :param rank_by: Specifies the order in which results are listed.
                    Possible values are: prominence (default), distance
    :type rank_by: string

    :param type: Restricts the results to places matching the specified type.
        The full list of supported types is available here:
        https://developers.google.com/places/supported_types
    :type type: string

    :param page_token: Token from a previous search that when provided will
                       returns the next page of results for the same search.
    :type page_token: string

    :rtype: result dict with the following keys:
            status: status code
            results: list of places
            html_attributions: set of attributions which must be displayed
            next_page_token: token for retrieving the next page of results

    """
    if not location and not page_token:
        raise ValueError("either a location or page_token arg is required")
    if rank_by == "distance":
        if not (keyword or name or type):
            raise ValueError(
                "either a keyword, name, or type arg is required "
                "when rank_by is set to distance"
            )
        elif radius is not None:
            raise ValueError(
                "radius cannot be specified when rank_by is set to " "distance"
            )

    return _places(
        client,
        "nearby",
        location=location,
        radius=radius,
        keyword=keyword,
        language=language,
        min_price=min_price,
        max_price=max_price,
        name=name,
        open_now=open_now,
        rank_by=rank_by,
        type=type,
        page_token=page_token,
    )


def _places(
    client,
    url_part,
    query=None,
    location=None,
    radius=None,
    keyword=None,
    language=None,
    min_price=0,
    max_price=4,
    name=None,
    open_now=False,
    rank_by=None,
    type=None,
    region=None,
    page_token=None,
):
    """
    Internal handler for ``places`` and ``places_nearby``.
    See each method's docs for arg details.
    """

    params = {"minprice": min_price, "maxprice": max_price}

    if query:
        params["query"] = query
    if location:
        params["location"] = convert.latlng(location)
    if radius:
        params["radius"] = radius
    if keyword:
        params["keyword"] = keyword
    if language:
        params["language"] = language
    if name:
        params["name"] = convert.join_list(" ", name)
    if open_now:
        params["opennow"] = "true"
    if rank_by:
        params["rankby"] = rank_by
    if type:
        params["type"] = type
    if region:
        params["region"] = region
    if page_token:
        params["pagetoken"] = page_token

    url = "/maps/api/place/%ssearch/json" % url_part
    return client._request(url, params)


def place(
    client,
    place_id,
    session_token=None,
    fields=None,
    language=None,
    reviews_no_translations=False,
    reviews_sort="most_relevant",
):
    """
    Legacy Places API details for an individual place.

    :param place_id: A textual identifier that uniquely identifies a place,
        returned from a Places search.
    :type place_id: string

    :param session_token: A random string which identifies an autocomplete
                          session for billing purposes.
    :type session_token: string

    :param fields: The fields specifying the types of place data to return,
                   separated by a comma. For full details see:
                   https://cloud.google.com/maps-platform/user-guide/product-changes/#places
    :type input: list

    :param language: The language in which to return results.
    :type language: string

    :param reviews_no_translations: Specify reviews_no_translations=True to disable translation of reviews; reviews_no_translations=False (default) enables translation of reviews.
    :type reviews_no_translations: bool

    :param reviews_sort: The sorting method to use when returning reviews.
                         Can be set to most_relevant (default) or newest.
    :type reviews_sort: string

    :rtype: result dict with the following keys:
        result: dict containing place details
        html_attributions: set of attributions which must be displayed
    """
    params = {"placeid": place_id}

    if fields:
        deprecated_fields = set(fields) & DEPRECATED_FIELDS
        if deprecated_fields:
            warnings.warn(
                DEPRECATED_FIELDS_MESSAGE % str(list(deprecated_fields)),
                DeprecationWarning,
            )

        invalid_fields = set(fields) - PLACES_DETAIL_FIELDS
        if invalid_fields:
            raise ValueError(
                "Valid values for the `fields` param for "
                "`place` are '%s', these given field(s) "
                "are invalid: '%s'"
                % ("', '".join(PLACES_DETAIL_FIELDS), "', '".join(invalid_fields))
            )
        params["fields"] = convert.join_list(",", fields)

    if language:
        params["language"] = language
    if session_token:
        params["sessiontoken"] = session_token
    if reviews_no_translations:
        params["reviews_no_translations"] = "true"
    if reviews_sort:
        params["reviews_sort"] = reviews_sort

    return client._request("/maps/api/place/details/json", params)


def places_photo(client, photo_reference, max_width=None, max_height=None):
    """
    Downloads a photo from the legacy Places API.

    :param photo_reference: A string identifier that uniquely identifies a
        photo, as provided by either a Places search or Places detail request.
    :type photo_reference: string

    :param max_width: Specifies the maximum desired width, in pixels.
    :type max_width: int

    :param max_height: Specifies the maximum desired height, in pixels.
    :type max_height: int

    :rtype: iterator containing the raw image data, which typically can be
        used to save an image file locally. For example:

    .. code-block:: python

        f = open(local_filename, 'wb')
        for chunk in client.places_photo(photo_reference, max_width=100):
            if chunk:
                f.write(chunk)
        f.close()
    """

    if not (max_width or max_height):
        raise ValueError("a max_width or max_height arg is required")

    params = {"photoreference": photo_reference}

    if max_width:
        params["maxwidth"] = max_width
    if max_height:
        params["maxheight"] = max_height

    # "extract_body" and "stream" args here are used to return an iterable
    # response containing the image file data, rather than converting from
    # json.
    response = client._request(
        "/maps/api/place/photo",
        params,
        extract_body=lambda response: response,
        requests_kwargs={"stream": True},
    )
    return response.iter_content()


def places_autocomplete(
    client,
    input_text,
    session_token=None,
    offset=None,
    origin=None,
    location=None,
    radius=None,
    language=None,
    types=None,
    components=None,
    strict_bounds=False,
):
    """
    Returns legacy Places API predictions given a textual search string and optional
    geographic bounds.

    :param input_text: The text string on which to search.
    :type input_text: string

    :param session_token: A random string which identifies an autocomplete
                          session for billing purposes.
    :type session_token: string

    :param offset: The position, in the input term, of the last character
                   that the service uses to match predictions. For example,
                   if the input is 'Google' and the offset is 3, the
                   service will match on 'Goo'.
    :type offset: int

    :param origin: The origin point from which to calculate straight-line distance
                    to the destination (returned as distance_meters).
                    If this value is omitted, straight-line distance will
                    not be returned.
    :type origin: string, dict, list, or tuple

    :param location: The latitude/longitude value for which you wish to obtain the
                     closest, human-readable address.
    :type location: string, dict, list, or tuple

    :param radius: Distance in meters within which to bias results.
    :type radius: int

    :param language: The language in which to return results.
    :type language: string

    :param types: Restricts the results to places matching the specified type.
        The full list of supported types is available here:
        https://developers.google.com/places/web-service/autocomplete#place_types
    :type types: string

    :param components: A component filter for which you wish to obtain a geocode.
        Currently, you can use components to filter by up to 5 countries for
        example: ``{'country': ['US', 'AU']}``
    :type components: dict

    :param strict_bounds: Returns only those places that are strictly within
        the region defined by location and radius.
    :type strict_bounds: bool

    :rtype: list of predictions

    """
    return _autocomplete(
        client,
        "",
        input_text,
        session_token=session_token,
        offset=offset,
        origin=origin,
        location=location,
        radius=radius,
        language=language,
        types=types,
        components=components,
        strict_bounds=strict_bounds,
    )


def places_autocomplete_query(
    client, input_text, offset=None, location=None, radius=None, language=None
):
    """
    Returns legacy Places API predictions given a textual search query, such as
    "pizza near New York", and optional geographic bounds.

    :param input_text: The text query on which to search.
    :type input_text: string

    :param offset: The position, in the input term, of the last character
        that the service uses to match predictions. For example, if the input
        is 'Google' and the offset is 3, the service will match on 'Goo'.
    :type offset: int

    :param location: The latitude/longitude value for which you wish to obtain the
        closest, human-readable address.
    :type location: string, dict, list, or tuple

    :param radius: Distance in meters within which to bias results.
    :type radius: number

    :param language: The language in which to return results.
    :type language: string

    :rtype: list of predictions
    """
    return _autocomplete(
        client,
        "query",
        input_text,
        offset=offset,
        location=location,
        radius=radius,
        language=language,
    )


def _autocomplete(
    client,
    url_part,
    input_text,
    session_token=None,
    offset=None,
    origin=None,
    location=None,
    radius=None,
    language=None,
    types=None,
    components=None,
    strict_bounds=False,
):
    """
    Internal handler for ``autocomplete`` and ``autocomplete_query``.
    See each method's docs for arg details.
    """

    params = {"input": input_text}

    if session_token:
        params["sessiontoken"] = session_token
    if offset:
        params["offset"] = offset
    if origin:
        params["origin"] = convert.latlng(origin)
    if location:
        params["location"] = convert.latlng(location)
    if radius:
        params["radius"] = radius
    if language:
        params["language"] = language
    if types:
        params["types"] = types
    if components:
        if len(components) != 1 or list(components.keys())[0] != "country":
            raise ValueError("Only country components are supported")
        params["components"] = convert.components(components)
    if strict_bounds:
        params["strictbounds"] = "true"

    url = "/maps/api/place/%sautocomplete/json" % url_part
    return client._request(url, params).get("predictions", [])


def _require_field_mask(field_mask, method_name):
    if not field_mask:
        raise ValueError("%s requires a non-empty field_mask" % method_name)


def _format_new_location(location):
    if location is None:
        return None
    return format_lat_lng(location)


def _new_places_headers(field_mask):
    _require_field_mask(field_mask, "Places API (New) method")
    return {"X-Goog-FieldMask": field_mask}


def places_text_search(
    client,
    text_query,
    field_mask,
    location_bias=None,
    location_restriction=None,
    language_code=None,
    region_code=None,
    included_type=None,
    open_now=None,
    min_rating=None,
    rank_preference=None,
    page_size=None,
    page_token=None,
    price_levels=None,
    strict_type_filtering=None,
    ev_options=None,
    routing_parameters=None,
    search_along_route_parameters=None,
    include_pure_service_area_businesses=None,
    include_future_opening_businesses=None,
):
    """Runs a Places API (New) Text Search request."""
    _require_field_mask(field_mask, "places_text_search")
    if location_bias and location_restriction:
        raise ValueError("Specify either location_bias or location_restriction, not both")

    request_body = {"textQuery": text_query}
    if location_bias:
        request_body["locationBias"] = location_bias
    if location_restriction:
        request_body["locationRestriction"] = location_restriction
    if language_code:
        request_body["languageCode"] = language_code
    if region_code:
        request_body["regionCode"] = region_code
    if included_type:
        request_body["includedType"] = included_type
    if open_now is not None:
        request_body["openNow"] = open_now
    if min_rating is not None:
        request_body["minRating"] = min_rating
    if rank_preference:
        request_body["rankPreference"] = rank_preference
    if page_size is not None:
        request_body["pageSize"] = page_size
    if page_token:
        request_body["pageToken"] = page_token
    if price_levels:
        request_body["priceLevels"] = price_levels
    if strict_type_filtering is not None:
        request_body["strictTypeFiltering"] = strict_type_filtering
    if ev_options:
        request_body["evOptions"] = ev_options
    if routing_parameters:
        request_body["routingParameters"] = routing_parameters
    if search_along_route_parameters:
        request_body["searchAlongRouteParameters"] = search_along_route_parameters
    if include_pure_service_area_businesses is not None:
        request_body["includePureServiceAreaBusinesses"] = include_pure_service_area_businesses
    if include_future_opening_businesses is not None:
        request_body["includeFutureOpeningBusinesses"] = include_future_opening_businesses

    return modern_api_request(
        client,
        "/v1/places:searchText",
        base_url=_PLACES_NEW_BASE_URL,
        post_json=request_body,
        headers=_new_places_headers(field_mask),
        extract_body=extract_api_body,
    )


def places_nearby_search(
    client,
    location,
    field_mask,
    radius,
    included_types=None,
    excluded_types=None,
    included_primary_types=None,
    excluded_primary_types=None,
    max_result_count=None,
    rank_preference=None,
    language_code=None,
    region_code=None,
    include_pure_service_area_businesses=None,
    include_future_opening_businesses=None,
):
    """Runs a Places API (New) Nearby Search request."""
    _require_field_mask(field_mask, "places_nearby_search")

    request_body = {
        "locationRestriction": {
            "circle": {
                "center": _format_new_location(location),
                "radius": radius,
            }
        }
    }
    if included_types:
        request_body["includedTypes"] = included_types
    if excluded_types:
        request_body["excludedTypes"] = excluded_types
    if included_primary_types:
        request_body["includedPrimaryTypes"] = included_primary_types
    if excluded_primary_types:
        request_body["excludedPrimaryTypes"] = excluded_primary_types
    if max_result_count is not None:
        request_body["maxResultCount"] = max_result_count
    if rank_preference:
        request_body["rankPreference"] = rank_preference
    if language_code:
        request_body["languageCode"] = language_code
    if region_code:
        request_body["regionCode"] = region_code
    if include_pure_service_area_businesses is not None:
        request_body["includePureServiceAreaBusinesses"] = include_pure_service_area_businesses
    if include_future_opening_businesses is not None:
        request_body["includeFutureOpeningBusinesses"] = include_future_opening_businesses

    return modern_api_request(
        client,
        "/v1/places:searchNearby",
        base_url=_PLACES_NEW_BASE_URL,
        post_json=request_body,
        headers=_new_places_headers(field_mask),
        extract_body=extract_api_body,
    )


def place_details(client, place_id, field_mask, language_code=None, region_code=None):
    """Returns Place Details using Places API (New)."""
    _require_field_mask(field_mask, "place_details")
    params = {}
    if language_code:
        params["languageCode"] = language_code
    if region_code:
        params["regionCode"] = region_code

    return modern_api_request(
        client,
        "/v1/places/%s" % place_id,
        base_url=_PLACES_NEW_BASE_URL,
        params=params,
        headers=_new_places_headers(field_mask),
        extract_body=extract_api_body,
    )


def place_photo(client, name, max_width_px=None, max_height_px=None,
                skip_http_redirect=False):
    """Downloads or resolves photo media using Place Photos (New)."""
    if not max_width_px and not max_height_px:
        raise ValueError("Specify max_width_px, max_height_px, or both")

    if not name:
        raise ValueError("Photo resource name is required")

    photo_name = name
    if not photo_name.endswith("/media"):
        photo_name = "%s/media" % photo_name.rstrip("/")

    params = {}
    if max_width_px:
        params["maxWidthPx"] = max_width_px
    if max_height_px:
        params["maxHeightPx"] = max_height_px
    if skip_http_redirect:
        params["skipHttpRedirect"] = "true"

    authed_url = client._generate_auth_url(
        "/v1/%s" % photo_name,
        params,
        accepts_clientid=False,
    )

    if skip_http_redirect:
        return modern_api_request(
            client,
            "/v1/%s" % photo_name,
            base_url=_PLACES_NEW_BASE_URL,
            params=params,
            extract_body=extract_api_body,
        )

    return request_binary_content(client, _PLACES_NEW_BASE_URL + authed_url)


def places_autocomplete_new(
    client,
    input_text,
    field_mask,
    session_token=None,
    location_bias=None,
    location_restriction=None,
    origin=None,
    included_primary_types=None,
    included_region_codes=None,
    language_code=None,
    region_code=None,
    input_offset=None,
    include_query_predictions=None,
):
    """Returns Autocomplete predictions using Places API (New)."""
    _require_field_mask(field_mask, "places_autocomplete_new")
    if location_bias and location_restriction:
        raise ValueError("Specify either location_bias or location_restriction, not both")

    request_body = {"input": input_text}
    if session_token:
        request_body["sessionToken"] = session_token
    if location_bias:
        request_body["locationBias"] = location_bias
    if location_restriction:
        request_body["locationRestriction"] = location_restriction
    if origin:
        request_body["origin"] = _format_new_location(origin)
    if included_primary_types:
        request_body["includedPrimaryTypes"] = included_primary_types
    if included_region_codes:
        request_body["includedRegionCodes"] = included_region_codes
    if language_code:
        request_body["languageCode"] = language_code
    if region_code:
        request_body["regionCode"] = region_code
    if input_offset is not None:
        request_body["inputOffset"] = input_offset
    if include_query_predictions is not None:
        request_body["includeQueryPredictions"] = include_query_predictions

    return modern_api_request(
        client,
        "/v1/places:autocomplete",
        base_url=_PLACES_NEW_BASE_URL,
        post_json=request_body,
        headers=_new_places_headers(field_mask),
        extract_body=extract_api_body,
    )
