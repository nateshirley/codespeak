from typing import Dict, List, Any
import requests
from codespeak.public.rest_requests.request import Request


def put(
    api: str,
    path: str,
    path_params: Dict[str, Any] | None = None,
    query_params: Dict[str, Any] | None = None,
    data: Dict[str, Any] | None = None,
    json: Dict[str, Any] | None = None,
    cookies: Dict[str, Any] | None = None,
    headers: Dict[str, Any] = {},
):
    """
    Makes a put request to an api with automatic authentication and formatted params. No api keys required. Uses pythons requests library.

    Args:
        api (str): The name of the api to use.
        path (str): The openapi path for the operation.
        data (Dict[str, Any], optional): The data to use in the operation request. Defaults to None.
        json (Dict[str, Any], optional): The json to use in the operation request. Defaults to None.
        path_params (Dict[str, str], optional): The path parameters to use in the operation. Defaults to None.
        query_params (Dict[str, str], optional): The query parameters to use in the operation. Defaults to None.
        headers (Dict[str, str], optional): The headers to use in the operation. Defaults to {}.

    Returns:
        type: the json-encoded content of the response, if any.
    """
    request = Request(
        api=api,
        path=path,
        api_key=None,
        path_params=path_params,
        query_params=query_params,
        data=data,
        json_=json,
        cookies=cookies,
        headers=headers,
    )
    request.authenticate()
    response = requests.put(
        url=request.make_url(),
        data=request.data,
        json=request.json_,
        params=request.query_params,
        headers=request.headers,
        cookies=request.cookies,
    )
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise e
    return response.json()
