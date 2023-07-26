from codespeak.settings import _settings


def get_api_key(api_name: str) -> str | None:
    api_keys = _settings.get_api_keys()
    return api_keys.get(api_name, None)
