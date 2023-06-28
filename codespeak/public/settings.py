from pydantic import BaseModel
from codespeak.settings.environment import Environment
from codespeak.settings._settings import _settings


def set_openai_api_key(key: str):
    _settings.openai_api_key = key


def set_verbose(verbose: bool):
    _settings.verbose = verbose


def set_auto_clean(auto_clean: bool):
    _settings.auto_clean = auto_clean


def set_openai_model(model: str):
    _settings.openai_model = model


def manually_set_abspath_to_project_root(abspath: str):
    _settings.abspath_to_project_root = abspath


def set_environment(env: Environment | str):
    if isinstance(env, Environment):
        _settings.environment = env
    else:
        if env not in [e.value for e in Environment]:
            raise Exception("Environment doesn't exist, use 'prod' or 'dev'")
        _settings.environment = Environment(env)


class Settings(BaseModel):
    """
    Public settings obj for codespeak.

    - openai_api_key: your openai api key, NOT required in prod
    - environment: 'prod' or 'dev'
    - verbose: whether to print out debug statements
    - auto_clean: whether to auto clean the codegen dir after each run
    - openai_model: the openai model to use
    """

    openai_api_key: str | None
    environment: Environment | str | None
    verbose: bool | None
    auto_clean: bool | None
    openai_model: str | None


def set(settings: Settings):
    if settings.openai_api_key is not None:
        set_openai_api_key(settings.openai_api_key)
    if settings.environment is not None:
        set_environment(settings.environment)
    if settings.verbose is not None:
        set_verbose(settings.verbose)
    if settings.auto_clean is not None:
        set_auto_clean(settings.auto_clean)
    if settings.openai_model is not None:
        set_openai_model(settings.openai_model)
