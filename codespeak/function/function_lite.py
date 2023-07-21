import copy
from typing import Any, Dict
from pydantic import BaseModel
from typing import List
from codespeak.function.function_declaration_lite import (
    FunctionDeclarationLite,
    TypeDefinitionLite,
)
import textwrap


class DotGet(BaseModel):
    source_code: str = textwrap.dedent(
        """
        def dot_get(data_dict: Dict, map_str: str) -> Any | None:
            map_list = map_str.split(".")
            for k in map_list:
                if k not in data_dict:
                    return None
                data_dict = data_dict[k]
                if data_dict is None:
                    return None
            return data_dict
        """
    ).strip("\n")
    import_path: str = "codespeak.dot_get"
    type: str = "function"

    def annotate(self) -> Dict[str, Any]:
        return {
            self.import_path: {
                "origin": "installed",
                "qualname": "dot_get",
                "module": "codespeak",
                "type": self.type,
                "source_code": self.source_code,
            }
        }


class FunctionLite(BaseModel):
    declaration: FunctionDeclarationLite
    custom_types: Dict[str, Any]

    @property
    def custom_types_with_dot_get(self) -> Dict[str, Any]:
        dot_get = DotGet()
        types_copy = copy.deepcopy(self.custom_types)
        types_copy.update(dot_get.annotate())
        return types_copy

    def import_path(self) -> str:
        return self.declaration.module_name + "." + self.declaration.qualname

    def remove_return_types_from_custom_types_if_not_in_params(
        self,
    ) -> List[TypeDefinitionLite]:
        removed = []
        params = self.declaration.params
        for return_type in self.declaration.return_types:
            if return_type not in params:
                print("removing return type from custom types")
                import_path = return_type.import_path()
                if import_path in self.custom_types:
                    del self.custom_types[import_path]
                    removed.append(return_type)
        return removed
