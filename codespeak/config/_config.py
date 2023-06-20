from enum import Enum
import os
from typing import Callable
from pydantic import BaseModel
from codespeak.helpers.auto_detect_abspath_to_project_root import (
    auto_detect_abspath_to_project_root,
)
from codespeak.declaration.declaration_file_service import codegen_dirname
from codespeak.config.environment import Environment


class _Config(BaseModel):
    """
    Internal representation of settings for codespeak.

    - all borrowed from codespeak_config.ConfigOptions, except for abspath_to_project_root
    - abspath_to_project_root: This will be automatically determined the first time a codespeak function is called if it's empty—it's used to load generated code. Can be manually set with helper func

    """

    openai_api_key: str | None = None
    environment: Environment
    verbose: bool = False
    abspath_to_project_root: str | None = None
    openai_model: str = "gpt-4"
    auto_clean: bool = True

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


def abspath_to_codegen_dir() -> str:
    return f"{_config.abspath_to_project_root}/{codegen_dirname}"


def should_auto_clean() -> bool:
    return _config.auto_clean


def get_openai_model() -> str:
    return _config.openai_model


def get_abspath_to_project_root(decorated_func: Callable) -> str:
    if _config.abspath_to_project_root is None:
        _config.abspath_to_project_root = auto_detect_abspath_to_project_root(
            decorated_func
        )
    return _config.abspath_to_project_root


def get_openai_api_key() -> str | None:
    return _config.openai_api_key


def get_verbose() -> bool:
    return _config.verbose


def get_environment() -> Environment:
    return _config.environment
