from typing import Dict, Literal

from codespeak.type_definitions.type_definition import TypeDefinition


class NoneDef(TypeDefinition):
    module: str = "None"
    type: Literal["NoneDef"] = "NoneDef"
    qualname: str = "None"
    _def: None = None

    def annotate(self) -> Dict:
        return {"None": "None"}

    def custom_types(self) -> Dict:
        return {}

    def annotate_in_local_class(self) -> Dict | str:
        return "None"

    def import_path(self):
        return ""
