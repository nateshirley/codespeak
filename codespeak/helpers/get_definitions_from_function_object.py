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
    for param in params.values():
        _def = param.annotation
        if _def is inspect.Signature.empty:
            continue
        defs.add(classify.from_any(_def))
    return_annotation = sig.return_annotation
    if not return_annotation is inspect.Signature.empty:
        defs.add(classify.from_any(return_annotation))
    return {"all": defs, "self": self_definition}
