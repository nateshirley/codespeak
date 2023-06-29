import json
from typing import Any, Dict, List, Tuple

from typing import Literal
from codespeak.type_definitions.types.generic import Generic
from codespeak.type_definitions.type_definition import TypeDefinition
from codespeak.type_definitions.utils.swap_custom_types import (
    recursively_swap_custom_types_for_references,
)


class TypingType(TypeDefinition):
    qualname: str
    module: str
    # could be dict, union, list, some others but not sure all of them
    origin: Any | None
    args: List[TypeDefinition]
    type: Literal["TypingType"] = "TypingType"

    def flatten(self) -> List[TypeDefinition]:
        flat: List[TypeDefinition] = [
            Generic(qualname=self.qualname, module=self.module, _def=None)
        ]
        for arg in self.args:
            flat.extend(arg.flatten())
        return flat

    def annotate(self) -> Dict:
        return {
            f"{self.import_path()}": {
                "qualname": self.qualname,
                "module": self.module,
                "origin": str(self.origin) if self.origin else None,
                "args": [arg.annotate() for arg in self.args],
            }
        }

    def annotate_in_local_class(self) -> Dict | str:
        if len(self.args) == 0:
            return f"{self.module}.{self.qualname}"
        else:
            return {
                f"{self.module}.{self.qualname}": [
                    arg.annotate_in_local_class() for arg in self.args
                ]
            }

    def reference_nested_custom_types(self) -> List[TypeDefinition]:
        args = self.args
        types_replaced, self.args = recursively_swap_custom_types_for_references(args)
        return types_replaced

    def custom_types(self) -> Dict:
        types_replaced = self.reference_nested_custom_types()
        annotxn = {}
        for _type in types_replaced:
            annotxn.update(_type.custom_types())
        return annotxn
