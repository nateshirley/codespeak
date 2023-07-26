from typing import Any, Callable, Dict, TypedDict


class APIMetadata(TypedDict):
    base_url: str
    auth_style: int


api_metadatas: Dict[str, APIMetadata] = {
    "harmonic": {"base_url": "https://api.harmonic.ai", "auth_style": 0}
}
