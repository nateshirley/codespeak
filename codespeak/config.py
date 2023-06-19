from enum import Enum
import os
from typing import Callable
from pydantic import BaseModel
from codespeak.helpers.auto_detect_abspath_to_project_root import (
    auto_detect_abspath_to_project_root,
)


class Environment(Enum):
    PROD = "prod"
    DEV = "dev"


class _Config(BaseModel):
    """
    Configurable settings for codespeak.

    - environment: 'prod' or 'dev'
    - openai_api_key: your openai api key, NOT required in prod
    - verbose: whether to print out debug statements
    - abspath_to_project_root: This will be automatically determined the first time a codespeak function is called if it's not set, and it's used to load generated code.

    """

    openai_api_key: str | None = None
    environment: Environment
    verbose: bool = False
    # automatically determined if not set
    abspath_to_project_root: str | None = None

    @staticmethod
    def from_env():
        env = os.getenv("ENVIRONMENT")
        if env:
            env = env.lower()
            if env in [e.value for e in Environment]:
                return _Config(
                    openai_api_key=os.getenv("OPENAI_API_KEY"),
                    environment=Environment(env),
                )
        return _Config(
            openai_api_key=os.getenv("OPENAI_API_KEY"), environment=Environment.DEV
        )


_config = _Config.from_env()


def manually_set_abspath_to_project_root(abspath: str):
    _config.abspath_to_project_root = abspath


def get_abspath_to_project_root(decorated_func: Callable) -> str:
    if _config.abspath_to_project_root is None:
        _config.abspath_to_project_root = auto_detect_abspath_to_project_root(
            decorated_func
        )
    return _config.abspath_to_project_root


def set_openai_api_key(key: str):
    _config.openai_api_key = key


def get_openai_api_key() -> str | None:
    return _config.openai_api_key


def set_verbose(verbose: bool):
    _config.verbose = verbose


def get_verbose() -> bool:
    return _config.verbose


def set_environment(env: Environment | str):
    if isinstance(env, Environment):
        _config.environment = env
    else:
        if env not in [e.value for e in Environment]:
            raise Exception("Environment doesn't exist, use 'prod' or 'dev'")
        _config.environment = Environment(env)


def get_environment() -> Environment:
    return _config.environment
