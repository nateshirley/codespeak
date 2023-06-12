from enum import Enum
import os
from pydantic import BaseModel


class Environment(Enum):
    PROD = "prod"
    DEV = "dev"


class Config(BaseModel):
    openai_api_key: str | None = None
    environment: Environment
    verbose: bool = False

    @staticmethod
    def from_env():
        env = os.getenv("ENVIRONMENT")
        if env:
            env = env.lower()
            if env in [e.value for e in Environment]:
                return Config(
                    openai_api_key=os.getenv("OPENAI_API_KEY"),
                    environment=Environment(env),
                )
        return Config(
            openai_api_key=os.getenv("OPENAI_API_KEY"), environment=Environment.DEV
        )


_config = Config.from_env()


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
