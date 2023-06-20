from pydantic import BaseModel
from codespeak.config._config import _config
from codespeak.config.environment import Environment


def set_openai_api_key(key: str):
    _config.openai_api_key = key


def set_verbose(verbose: bool):
    _config.verbose = verbose


def set_auto_clean(auto_clean: bool):
    _config.auto_clean = auto_clean


def set_openai_model(model: str):
    _config.openai_model = model


def manually_set_abspath_to_project_root(abspath: str):
    _config.abspath_to_project_root = abspath


def set_environment(env: Environment | str):
    if isinstance(env, Environment):
        _config.environment = env
    else:
        if env not in [e.value for e in Environment]:
            raise Exception("Environment doesn't exist, use 'prod' or 'dev'")
        _config.environment = Environment(env)


class ConfigOptions(BaseModel):
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


def set(options: ConfigOptions):
    if options.openai_api_key is not None:
        set_openai_api_key(options.openai_api_key)
    if options.environment is not None:
        set_environment(options.environment)
    if options.verbose is not None:
        set_verbose(options.verbose)
    if options.auto_clean is not None:
        set_auto_clean(options.auto_clean)
    if options.openai_model is not None:
        set_openai_model(options.openai_model)
