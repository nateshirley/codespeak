import inspect
from types import MappingProxyType
from typing import Callable, List, Set, TypedDict
from codespeak.type_definitions import classify
from codespeak.type_definitions.type_definition import TypeDefinition
from codespeak.helpers.try_get_self_definition_for_for_inferred_function import (
    try_get_self_definition_for_for_inferred_function,
)


class DefinitionsForFunction(TypedDict):
    all: Set[TypeDefinition]
    self: TypeDefinition | None
    params: Set[TypeDefinition]
    return_type: TypeDefinition | None


def get_definitions_from_function_object(
    function: Callable,
) -> DefinitionsForFunction:
    """Definitions for types used in the signature"""
    sig = inspect.signature(function)
    defs: Set[TypeDefinition] = set()
    params: MappingProxyType[str, inspect.Parameter] = sig.parameters
    self_definition = try_get_self_definition_for_for_inferred_function(
        function=function, params=params
    )
    if self_definition:
        defs.add(self_definition)
    param_defs: set[TypeDefinition] = set()
    for param in params.values():
        _def = param.annotation
        if _def is inspect.Signature.empty:
            continue
        param_def = classify.from_any(_def)
        defs.add(param_def)
        param_defs.add(param_def)
    return_type_definition = None
    if not sig.return_annotation is inspect.Signature.empty:
        return_type_definition = classify.from_any(sig.return_annotation)
        defs.add(return_type_definition)
    return {
        "all": defs,
        "self": self_definition,
        "params": param_defs,
        "return_type": return_type_definition,
    }
