import requests
from .api_codes import headers_settings_lang
from .custom_api_errors import (
    BadRequestAPIError,
    UnauthorizedAPIError,
    ForbiddenAPIError,
    ParamStrNoneOrEmptyError,
    HeadersNumberError,
    NonTypicalStatusAPIError,
)

base_url = "https://global.metadapi.com/lang/v1/languages"


def get_data_lang_on_code(lang_code: str, headers_number: int = 1) -> list[dict]:
    """
    Fetches language data based on the provided language code and headers number.

    Args:
        lang_code (str): The language code to query.
        headers_number (int, optional): The number corresponding to the desired headers. Defaults to 1.

    Returns:
        list[dict]: A list containing dictionaries with country data.
    """
    if not lang_code:
        raise ParamStrNoneOrEmptyError()
    try:
        headers = headers_settings_lang[headers_number]
    except KeyError:
        raise HeadersNumberError(headers_number)
    params = {"langCode": lang_code}
    response = requests.get(base_url, headers=headers, params=params)
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


def get_data_all_lang(headers_number: int = 1) -> list[dict]:
    try:
        headers = headers_settings_lang[headers_number]
    except KeyError:
        raise HeadersNumberError(headers_number)
    response = requests.get(base_url, headers=headers)
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
