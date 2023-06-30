from typing import List, Tuple

from codespeak.type_definitions.type_definition import TypeDefinition
from codespeak.type_definitions.types.custom_type_reference import CustomTypeReference


def recursively_swap_custom_types_for_references(
    args: List[TypeDefinition],
) -> Tuple[List[TypeDefinition], List[TypeDefinition]]:
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
