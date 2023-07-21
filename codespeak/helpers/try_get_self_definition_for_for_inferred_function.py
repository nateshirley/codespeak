import inspect
from types import MappingProxyType
import importlib
from typing import Callable
from codespeak.type_definitions import classify
from codespeak.type_definitions.type_definition import TypeDefinition


def try_get_self_definition_for_for_inferred_function(
    function: Callable,
    params: MappingProxyType[str, inspect.Parameter],
) -> None | TypeDefinition:
    if len(params) == 0:
        return None
    first_key = next(iter(params))
    first_param = params[first_key]
    if first_key == "self" and first_param.annotation == inspect._empty:
        if function.__qualname__.count(".") == 1:
            class_name = function.__qualname__.split(".")[0]
            module = inspect.getmodule(function)
            if not module:
                return None
            module_name = module.__name__
            module_object = importlib.import_module(module_name)
            class_obj = getattr(module_object, class_name)
            self_definition = classify.from_any(class_obj)
            return self_definition
    return None
