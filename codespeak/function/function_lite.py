import copy
from typing import Any, Dict
from pydantic import BaseModel
from typing import List
from codespeak.function.function_declaration_lite import (
    FunctionDeclarationLite,
    TypeDefinitionLite,
)


class FunctionLite(BaseModel):
    declaration: FunctionDeclarationLite
    custom_types: Dict[str, Any]

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
