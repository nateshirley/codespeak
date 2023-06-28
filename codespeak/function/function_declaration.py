import ast
import inspect
import json
import re
import textwrap
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel
from codespeak.definitions import classify
from codespeak.definitions.definition import Definition

from codespeak.definitions.utils.dedupe import dedupe
from codespeak.definitions.utils.group import group_by_module
from codespeak.public import inferred_exception


# computed_custom_types: Dict | None = None

# def compute_custom_types(self):
#     defs = {}
#     for _def in self.signature_definitions:
#         defs.update(_def.custom_types())
#     if self.self_definition:
#         defs.update(self.self_definition.custom_types())
#     defs.update(inferred_exception.annotate())
#     self.computed_custom_types = defs

# @property
# def custom_types(self) -> Dict:
#     if not self.computed_custom_types:
#         self.compute_custom_types()
#     if not self.computed_custom_types:
#         raise Exception("custom types not computed")
#     return self.computed_custom_types


class FunctionDeclaration(BaseModel):
    """Resources that are imputed from the function's declaration"""

    name: str
    qualname: str
    module_name: str
    docstring: str
    source_code: str
    signature_text: str
    import_definitions: Dict[str, List[Definition]]
    self_definition: Definition | None = None

    def as_incomplete_file(self) -> str:
        return self.imports_text() + "\n" + self.signature_text + "\n"

    # potentially buggy
    def imports_text(self) -> str:
        _str = ""
        for module, types in self.import_definitions.items():
            if module == "builtins" or module == "None":
                continue
            _str += f"from {module} import {', '.join([_type.qualname for _type in types])}\n"
        return _str

    def try_add_self_definition(self, self_definition: Definition) -> None:
        if self.self_definition:
            return

        def text_with_type_name_after_self(signature_text, self_type_name):
            def replace(match):
                return match.group() + ":" + self_type_name

            pattern = r"\(self"
            new_text = re.sub(pattern, replace, signature_text, count=1)
            return new_text

        self.signature_text = text_with_type_name_after_self(
            self.signature_text, self_definition.qualname
        )
        self.self_definition = self_definition
        self.add_import_definition(self_definition)

    def add_import_definition(self, definition: Definition):
        defs_ = self.import_definitions.get(definition.module, [])
        if not any(def_.qualname == definition.qualname for def_ in defs_):
            defs_.append(definition)
            self.import_definitions[definition.module] = defs_

    @staticmethod
    def from_inferred_func(
        inferred_func: Callable,
        signature_definitions: List[Definition],
    ) -> "FunctionDeclaration":
        source_code = textwrap.dedent(inspect.getsource(inferred_func))

        declaration = FunctionDeclaration(
            name=inferred_func.__name__,
            qualname=inferred_func.__qualname__,
            module_name=inferred_func.__module__,
            docstring=inspect.getdoc(inferred_func) or "",
            source_code=source_code,
            signature_text=build_signature_text(
                func_name=inferred_func.__name__,
                source_code=source_code,
            ),
            import_definitions={},
        )

        flat_sig_defs = flatten_signature_definitions(signature_definitions)
        for _def in flat_sig_defs:
            declaration.add_import_definition(_def)

        return declaration


def flatten_signature_definitions(
    signature_definitions: List[Definition],
) -> List[Definition]:
    flattened = []
    for _def in signature_definitions:
        if _def.type == "LocalClass":
            flattened.append(_def)
        else:
            flattened.extend(_def.flatten())
    return flattened


def build_signature_text(func_name: str, source_code: str) -> str:
    module = ast.parse(source_code)
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            # Reconstruct the function signature from the 'args' attribute
            signature = f"def {node.name}({ast.unparse(node.args)})"
            if node.returns:  # If there's a return annotation, add it
                signature += f" -> {ast.unparse(node.returns)}"
            signature += ":"
            return signature
    raise Exception("function signature not found")
