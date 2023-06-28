import inspect
from typing import List, Set
from codespeak.definitions import classify
from codespeak.definitions.definition import Definition


def get_definitions_from_function_signature(
    sig: inspect.Signature,
) -> Set[Definition]:
    """Definitions for types used in the signature"""
    defs: Set[Definition] = set()
    params = sig.parameters
    for param in params.values():
        _def = param.annotation
        if _def is inspect.Signature.empty:
            continue
        defs.add(classify.from_any(_def))
    return_annotation = sig.return_annotation
    if not return_annotation is inspect.Signature.empty:
        defs.add(classify.from_any(return_annotation))
    return defs
