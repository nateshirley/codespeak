import json
from typing import Any, Dict, List

from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Literal

from codespeak.type_definitions.type_definition import TypeDefinition


class ImportDefinition(BaseModel):
    """To be used as a flattened type definition for imports"""

    qualname: str
    module: str
    type: Literal["ImportDefinition"] = "ImportDefinition"

    def __hash__(self):
        return hash((self.module, self.qualname))

    def __eq__(self, other):
        if isinstance(other, ImportDefinition):
            return (self.module, self.qualname) == (other.module, other.qualname)
        return False

    def __lt__(self, other):
        if isinstance(other, ImportDefinition):
            return self.import_path() < other.import_path()
        return NotImplemented

    def import_path(self) -> str:
        return self.module + "." + self.qualname

    @staticmethod
    def from_type_definition(type_definition: TypeDefinition) -> "ImportDefinition":
        return ImportDefinition(
            qualname=type_definition.qualname,
            module=type_definition.module,
        )
