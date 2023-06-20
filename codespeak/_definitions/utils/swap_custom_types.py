from typing import List, Tuple

from codespeak._definitions.definition import Definition
from codespeak._definitions.types.custom_type_reference import CustomTypeReference


def recursively_swap_custom_types_for_references(
    args: List[Definition],
) -> Tuple[List[Definition], List[Definition]]:
    swapped = []
    for i, _def in enumerate(args):
        if _def.type == "TypingType" or _def.type == "UnionType":
            if hasattr(_def, "args") and _def.args is not None:
                _swapped, _args = recursively_swap_custom_types_for_references(
                    _def.args
                )
                swapped.extend(_swapped)
        else:
            if _def.type == "LocalClass":
                swapped.append(_def)
                args[i] = CustomTypeReference(
                    qualname=_def.qualname, module=_def.module, _def=_def
                )
            elif _def.type == "InstalledClass":
                swapped.append(_def)
                args[i] = CustomTypeReference(
                    qualname=_def.qualname, module=_def.module, _def=_def
                )
    return swapped, args
