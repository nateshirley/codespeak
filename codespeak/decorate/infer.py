import inspect
from typing import Any, Callable, Dict, List, Tuple, TypeVar
from functools import wraps
from codespeak import executor
from codespeak.function.function_file_service import (
    FunctionFileService,
)
from codespeak.function_resources.declaration_resources import (
    DeclarationResources,
)
from codespeak.helpers.auto_detect_abspath_to_project_root import (
    auto_detect_abspath_to_project_root,
)
from codespeak.settings import _settings
from codespeak.clean import clean
from codespeak.settings.environment import Environment
from codespeak.function import Function
from codespeak.function.function_attributes import FunctionAttributes
from codespeak.function_resources.function_resources import FunctionResources
from codespeak.function.function_tests import FunctionTests
from codespeak.function_resources.programmable_resources import (
    ProgrammableResources,
)
from codespeak.frame import Frame
from unittest.mock import patch

# type inference remain on original function when no type hints are on the decorator


def infer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if wrapper._is_prod:  # type: ignore
            return wrapper._logic(*args, **kwargs)  # type: ignore
        else:
            nonlocal has_executed
            function = Function(wrapper)
            if not has_executed:
                with Frame.manager.manage_for(wrapper):
                    func(*args, **kwargs)
                function._try_add_self_to_frame(args, kwargs)

            has_executed = True
            return function._infer(args, kwargs)

    has_executed = False
    _assign_default_attributes(wrapper, func)
    return wrapper


def _assign_default_attributes(wrapper: Callable, decorated_func: Callable):
    env = _settings.get_environment()
    setattr(wrapper, FunctionAttributes.is_prod, env == Environment.PROD)
    if env == _settings.Environment.PROD:
        logic = executor.load_generated_logic_from_module_qualname(
            FunctionFileService.gather_generated_module_qualname(
                decorated_func=decorated_func
            ),
            decorated_func.__name__,
        )
        setattr(wrapper, FunctionAttributes.logic, logic)
    elif env == _settings.Environment.DEV:
        if _settings._settings.abspath_to_project_root is None:
            _settings.set_abspath_to_project_root(
                auto_detect_abspath_to_project_root(decorated_func)
            )
        file_service = FunctionFileService.from_decorated_func(decorated_func)
        setattr(wrapper, FunctionAttributes.file_service, file_service)
        resources = FunctionResources(
            declaration_resources=DeclarationResources.from_inferred_func(
                inferred_func=decorated_func,
            ),
            programmable_resources=ProgrammableResources(classes=[]),
        )
        frame = Frame(
            resources=resources,
            tests=FunctionTests(),
        )
        setattr(
            wrapper,
            FunctionAttributes.frame,
            frame,
        )
