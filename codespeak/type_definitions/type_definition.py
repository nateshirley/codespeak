import json
from typing import Any, Dict, List

from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Literal


class TypeDefinition(ABC, BaseModel):
    qualname: str
    module: str
    type: Literal["TypeDefinition"] = "TypeDefinition"
    _def: Any

    def __hash__(self):
        return hash((self.module, self.qualname))

    def __eq__(self, other):
        if isinstance(other, TypeDefinition):
            return (self.module, self.qualname) == (other.module, other.qualname)
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
