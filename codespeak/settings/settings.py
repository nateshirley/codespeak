from typing import Dict
from pydantic import BaseModel
from codespeak.settings.environment import Environment
import os


api_identifier = str
api_key = str
ApiKeys = Dict[api_identifier, api_key]


class Settings(BaseModel):
    environment: Environment = Environment.DEV
    verbose: bool = False
    is_interactive_mode: bool = False
    api_keys: ApiKeys = {}
    abspath_to_project_root: str | None = None
    current_api_identifier: api_identifier | None = None

    @staticmethod
    def from_env():
        env = os.getenv("ENV")
        if env is not None:
            env = env.lower()
            if env in [e.value for e in Environment]:
                return Settings(
                    environment=Environment(env),
                )
        return Settings(environment=Environment.DEV)


_settings = Settings.from_env()


def is_interactive_mode() -> bool:
    return _settings.is_interactive_mode


def get_api_keys() -> ApiKeys:
    return _settings.api_keys


def set_abspath_to_project_root(abspath: str):
    _settings.abspath_to_project_root = abspath


def get_verbose() -> bool:
    return _settings.verbose


def get_environment() -> Environment:
    return _settings.environment


def set_verbose(verbose: bool):
    _settings.verbose = verbose


def get_abspath_to_project_root() -> str:
    return _settings.abspath_to_project_root or ""


def add_api(api_identifier: str, api_key: str):
    api_identifier = api_identifier.lower()
    _settings.current_api_identifier = api_identifier
    _settings.api_keys[api_identifier] = api_key


def get_current_api_identifier() -> api_identifier | None:
    return _settings.current_api_identifier


def remove_api(api_identifier: str):
    if api_identifier in _settings.api_keys:
        _settings.api_keys.pop(api_identifier)


def set_interactive_mode(should_use_interactive_mode: bool):
    _settings.is_interactive_mode = should_use_interactive_mode


def set_environment(env: Environment | str):
    if isinstance(env, Environment):
        _settings.environment = env
    else:
        env = env.lower()
        if env not in [e.value for e in Environment]:
            raise Exception("Environment doesn't exist, use 'prod' or 'dev'")
        _settings.environment = Environment(env)
