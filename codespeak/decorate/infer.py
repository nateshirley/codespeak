import inspect
from typing import Any, Callable, Dict, List, Tuple, TypeVar
from functools import wraps
from codespeak import executor
from codespeak.function.function_file_service import (
    FunctionFileService,
)
from codespeak.function.function_declaration import (
    FunctionDeclaration,
)
from codespeak.helpers.guarantee_abspath_to_root_exists import (
    guarantee_abspath_to_project_root_exists,
)
from codespeak.settings import _settings
from codespeak.settings.environment import Environment
from codespeak.function import Function
from codespeak.function.function_attributes import FunctionAttributes
from codespeak.frame_tests import FrameTests
from codespeak.frame import Frame
from codespeak.helpers.get_definitions_from_function_signature import (
    get_definitions_from_function_signature,
)

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
                with Frame.get_manager().manage_for(wrapper):
                    func(*args, **kwargs)
                function._try_add_self_to_frame(args, kwargs)
                has_executed = True
            if function._is_testing:
                return function.execute_latest_inference(*args, **kwargs)
            return function._infer(args, kwargs)

    has_executed = False
    _assign_default_attributes(wrapper, func)
    return wrapper


def _assign_default_attributes(wrapper: Callable, decorated_func: Callable):
    env = _settings.get_environment()
    setattr(wrapper, FunctionAttributes.is_prod, env == Environment.PROD)
    guarantee_abspath_to_project_root_exists(decorated_func)
    if env == _settings.Environment.PROD:
        logic = executor.load_generated_logic_from_module_qualname(
            FunctionFileService.gather_generated_module_qualname(
                decorated_func=decorated_func
            ),
            decorated_func.__name__,
        )
        setattr(wrapper, FunctionAttributes.logic, logic)
    elif env == _settings.Environment.DEV:
        file_service = FunctionFileService.from_decorated_func(decorated_func)
        setattr(wrapper, FunctionAttributes.file_service, file_service)
        signature_definitions = get_definitions_from_function_signature(
            inspect.signature(decorated_func)
        )
        setattr(
            wrapper,
            FunctionAttributes.declaration,
            FunctionDeclaration.from_inferred_func(
                decorated_func, signature_definitions
            ),
        )
        setattr(
            wrapper,
            FunctionAttributes.frame,
            Frame(
                type_definitions=signature_definitions,
                tests=FrameTests(),
                parents=[Frame.for_module(decorated_func.__module__)],
            ),
        )
