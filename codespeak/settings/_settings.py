from enum import Enum
import os
from typing import Callable
from pydantic import BaseModel
from codespeak.settings.environment import Environment
from codespeak.constants import codegen_dirname


class _Settings(BaseModel):
    """
    Internal representation of settings for codespeak.

    - all borrowed from codespeak_Settings.ConfigOptions, except for abspath_to_project_root
    - abspath_to_project_root: This will be automatically determined the first time a codespeak function is called if it's empty—it's used to load generated code. Can be manually set with helper func

    """

    openai_api_key: str | None = None
    environment: Environment
    verbose: bool = False
    abspath_to_project_root: str | None = None
    openai_model: str = "gpt-4"
    should_auto_clean: bool = False
    is_testing: bool = False
    filepath_for_logic_being_tested: str = ""

    @staticmethod
    def from_env():
        env = os.getenv("ENVIRONMENT")
        if env is not None:
            env = env.lower()
            if env in [e.value for e in Environment]:
                return _Settings(
                    openai_api_key=os.getenv("OPENAI_API_KEY"),
                    environment=Environment(env),
                )
        return _Settings(
            openai_api_key=os.getenv("OPENAI_API_KEY"), environment=Environment.DEV
        )


_settings = _Settings.from_env()


def abspath_to_codegen_dir() -> str:
    return f"{_settings.abspath_to_project_root}/{codegen_dirname}"


def should_auto_clean() -> bool:
    return _settings.should_auto_clean


def get_openai_model() -> str:
    return _settings.openai_model


def set_abspath_to_project_root(abspath: str):
    _settings.abspath_to_project_root = abspath


def get_abspath_to_project_root() -> str:
    if _settings.abspath_to_project_root is None:
        raise Exception("abspath_to_project_root is None")
    return _settings.abspath_to_project_root


def get_openai_api_key() -> str | None:
    return _settings.openai_api_key


def get_verbose() -> bool:
    return _settings.verbose


def get_environment() -> Environment:
    return _settings.environment


def set_is_testing(is_testing: bool, logic_at_filepath: str | None = None):
    _settings.is_testing = is_testing
    if logic_at_filepath is not None:
        _settings.filepath_for_logic_being_tested = logic_at_filepath
