import inspect
from typing import List
from codespeak.definitions import classify
from codespeak.definitions.definition import Definition


def get_definitions_from_function_signature(
    sig: inspect.Signature,
) -> List[Definition]:
    """Definitions for types used in the signature"""
    defs: List[Definition] = []
    params = sig.parameters
    for param in params.values():
        _def = param.annotation
        if _def is inspect.Signature.empty:
            continue
        defs.append(classify.from_any(_def))
    return_annotation = sig.return_annotation
    if not return_annotation is inspect.Signature.empty:
        defs.append(classify.from_any(return_annotation))
    return defs
