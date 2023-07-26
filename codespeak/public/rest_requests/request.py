from typing import Any, Callable, Dict
from pydantic import BaseModel
from codespeak.apis.api_metadata import api_metadatas
from codespeak.settings import settings


class Request(BaseModel):
    api: str
    path: str
    api_key: str | None
    path_params: Dict[str, Any] | None
    query_params: Dict[str, Any] | None
    data: Dict[str, Any] | None
    json_: Dict[str, Any] | None
    cookies: Dict[str, Any] | None
    headers: Dict[str, Any]

    def get_api_key(self) -> str | None:
        api_keys = settings.get_api_keys()
        return api_keys.get(self.api, None)

    def authenticate(self):
        self.api_key = self.get_api_key()
        if self.api_key is None:
            raise ValueError("no api key found")
        style = api_metadatas[self.api]["auth_style"]
        auth_functions[style](self)

    @property
    def base_url(self):
        return api_metadatas[self.api]["base_url"]

    def make_url(self) -> str:
        if self.path_params is not None and len(self.path_params.keys()) > 0:
            return build_url_with_path_params(
                self.base_url, path=self.path, path_params=self.path_params
            )
        else:
            return f"{self.base_url}{self.path}"


from furl import furl
from typing import Dict, List, Any


def build_url_with_path_params(base_url: str, path: str, path_params: Dict[str, str]):
    url = furl(base_url)
    url /= path.format(**path_params)
    return url.url


def auth_zero(request: Request):
    request.headers["apiKey"] = request.api_key


auth_functions: Dict[int, Callable] = {0: auth_zero}
