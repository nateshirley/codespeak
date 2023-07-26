import json
from typing import Any, Dict, List

from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Literal


class TypeDefinition(ABC, BaseModel):
    qualname: str
    module: str
    args: List["TypeDefinition"] = []
    type: Literal["TypeDefinition"] = "TypeDefinition"
    _def: Any

    def __hash__(self):
        arg_paths = [arg.import_path() for arg in self.args]
        return hash((self.module, self.qualname, str(arg_paths)))

    def __eq__(self, other):
        if isinstance(other, TypeDefinition):
            self_arg_paths = [arg.import_path() for arg in self.args]
            other_arg_paths = [arg.import_path() for arg in other.args]
            return (self.module, self.qualname, str(self_arg_paths)) == (
                other.module,
                other.qualname,
                str(other_arg_paths),
            )
        return False

    def __lt__(self, other):
        if isinstance(other, TypeDefinition):
            return self.import_path() < other.import_path()
        return NotImplemented

    def printable(self) -> str:
        return json.dumps(self.annotate(), indent=4)

    @abstractmethod
    def annotate(self) -> Dict:
        pass

    def ref_nested_locals(self) -> List["TypeDefinition"]:
        return []

    def flatten(self) -> List["TypeDefinition"]:
        return [self]

    def annotate_in_local_class(self) -> Dict | str:
        return self.annotate()

    def import_path(self) -> str:
        return self.module + "." + self.qualname

    @abstractmethod
    def custom_types(self) -> Dict:
        pass

    def reference_nested_custom_types(self) -> List["TypeDefinition"]:
        return []

    def is_a_union_type(self) -> bool:
        return self.type == "UnionType" or (
            self.type == "TypingType" and self.qualname.lower() == "union"
        )
