from typing import Dict, List, Any
import requests
from furl import furl
from codespeak.apis import api_keys
from codespeak.public.inferred_exception import InferredException
from codespeak.public.rest_requests.request import Request


def get(
    api: str,
    path: str,
    path_params: Dict[str, Any] | None = None,
    query_params: Dict[str, Any] | None = None,
    headers: Dict[str, Any] = {},
):
    """
    Makes a get request to an api with automatic authentication and formatted params. No api keys required.

    Args:
        api (str): The name of the api to use.
        path (str): The openapi path for the operation.
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
        data=None,
        json_=None,
        cookies=None,
        headers=headers,
    )
    request.authenticate()
    response = requests.get(
        url=request.make_url(),
        params=request.query_params,
        headers=request.headers,
    )
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise e
    return response.json()
