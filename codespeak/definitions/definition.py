import json
from typing import Any, Dict, List

from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Literal


# needs to go above below imports
class Definition(ABC, BaseModel):
    qualname: str
    module: str
    type: Literal["Definition"] = "Definition"
    _def: Any

    def __hash__(self):
        return hash((self.module, self.qualname))

    def __eq__(self, other):
        if isinstance(other, Definition):
            return (self.module, self.qualname) == (other.module, other.qualname)
        return False

    def printable(self) -> str:
        return json.dumps(self.annotate(), indent=4)

    @abstractmethod
    def annotate(self) -> Dict:
        pass

    def ref_nested_locals(self) -> List["Definition"]:
        return []

    def flatten(self) -> List["Definition"]:
        return [self]

    def annotate_in_local_class(self) -> Dict | str:
        return self.annotate()

    def import_path(self):
        return self.module + "." + self.qualname

    @abstractmethod
    def custom_types(self) -> Dict:
        pass

    def reference_nested_custom_types(self) -> List["Definition"]:
        return []
