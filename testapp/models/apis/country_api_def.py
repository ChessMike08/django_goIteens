import requests
from .custom_api_errors import (
    BadRequestAPIError,
    UnauthorizedAPIError,
    ForbiddenAPIError,
    ParamStrNoneOrEmptyError,
    NonTypicalStatusAPIError,
)

base_url = "https://restcountries.com/v3.1"
filter_url = "fields=name,cca2,ccn3,cca3,cioc,capital,translations,flag,maps,timezones,flags,postalCode,region"
filter_fullname_url = "fullText=true"


def search_by_name_or_fullname(
    name: str, is_filter: bool = True, is_fullname: bool = False
) -> list[dict]:
    """
    Fetches country data based on the provided name.

    Args:
        name (str): The name of the country to query.
        is_filter (bool, optional): Specifies whether to apply filtering or not. Defaults to True.
        is_fullname (bool, optional): Specifies whether to search by full name or not. Defaults to False.

    Returns:
        list[dict]: A list containing dictionaries with country data.
    """
    if not name:
        raise ParamStrNoneOrEmptyError()
    endpoint = f"/name/{name}?"
    url = base_url + endpoint
    if is_fullname:
        url += filter_fullname_url + "&"
    if is_filter:
        url += filter_url
    return make_request(url)


def search_by_code(code: str, is_filter: bool = True) -> list[dict]:
    """
    Fetches country data based on the provided country code.

    Args:
        code (str): The country code to query.
        is_filter (bool, optional): Specifies whether to apply filtering or not. Defaults to True.

    Returns:
        list[dict]: A list containing dictionaries with country data.
    """
    if not code:
        raise ParamStrNoneOrEmptyError()
    endpoint = f"/alpha/{code}?"
    url = base_url + endpoint
    if is_filter:
        url += filter_url
    return make_request(url)


def search_by_region(region: str, is_filter: bool = True) -> list[dict]:
    """
    Fetches country data based on the provided region.

    Args:
        region (str): The region to query.
        is_filter (bool, optional): Specifies whether to apply filtering or not. Defaults to True.

    Returns:
        list[dict]: A list containing dictionaries with country data.
    """
    if not region:
        raise ParamStrNoneOrEmptyError()
    endpoint = f"/region/{region}?"
    url = base_url + endpoint
    if is_filter:
        url += filter_url
    return make_request(url)


def search_all(is_filter: bool = True) -> list[dict]:
    """
    Fetches data for all countries.

    Args:
        is_filter (bool, optional): Specifies whether to apply filtering or not. Defaults to True.

    Returns:
        list[dict]: A list containing dictionaries with country data.
    """
    endpoint = f"/all?"
    url = base_url + endpoint
    if is_filter:
        url += filter_url
    return make_request(url)


def make_request(url: str) -> list[dict]:
    """
    Sends a GET request to the specified URL and returns the JSON response.

    Args:
        url (str): The URL to send the request to.

    Returns:
       list[dict]: A list containing dictionaries with country data.

    Raises:
        BadRequestAPIError: If the server returns a 400 status code.
        UnauthorizedAPIError: If the server returns a 401 status code.
        ForbiddenAPIError: If the server returns a 403 status code.
        NonTypicalStatusAPIError: If the server returns a non-typical status code.
    """
    response = requests.get(url=url, timeout=10)
    status = response.status_code
    if status == 200:
        return response.json()
    elif status == 400:
        raise BadRequestAPIError()
    elif status == 401:
        raise UnauthorizedAPIError()
    elif status == 403:
        raise ForbiddenAPIError()
    else:
        raise NonTypicalStatusAPIError(status)
