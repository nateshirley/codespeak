import inspect
import textwrap
from typing import Callable, Dict
from pydantic import BaseModel
from codespeak.function_resources.body_imports import BodyImports


class BodyResources(BaseModel):
    imports: BodyImports

    def custom_types(self) -> Dict:
        return self.imports.custom_types()

    def imports_text(self) -> str:
        return self.imports.imports_text()

    @staticmethod
    def from_decorated_func(func: Callable) -> "BodyResources":
        source_code = textwrap.dedent(inspect.getsource(func))
        return BodyResources(imports=BodyImports.from_func_source(source_code))
