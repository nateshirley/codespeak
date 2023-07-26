from codespeak.settings import settings


def get_api_key(api_identifier: str) -> str | None:
    api_keys = settings.get_api_keys()
    return api_keys.get(api_identifier, None)
