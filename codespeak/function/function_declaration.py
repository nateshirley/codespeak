import ast
import inspect
import json
import re
import textwrap
from types import MappingProxyType
from typing import Any, Callable, Dict, List, Optional, Set
from pydantic import BaseModel
from codespeak.public.inferred_exception import InferredExceptionHelpers
from codespeak.type_definitions import classify
from codespeak.type_definitions.import_definition import ImportDefinition
from codespeak.type_definitions.type_definition import TypeDefinition


class FunctionDeclaration(BaseModel):
    """Resources that are imputed from the function's declaration"""

    name: str
    qualname: str
    module_name: str
    docstring: str
    source_code: str
    signature_text: str
    import_definitions: Dict[str, Set[ImportDefinition]]
    self_definition: TypeDefinition | None = None

    def as_incomplete_file(self) -> str:
        return self.imports_text() + "\n" + self.signature_text + "\n"

    def as_query_document(self) -> str:
        return self.signature_text

    # potentially buggy
    def imports_text(self) -> str:
        _str = ""
        for module, types in self.import_definitions.items():
            if module == "builtins" or module == "None":
                continue
            _str += f"from {module} import {', '.join([_type.qualname for _type in types])}\n"
        _str += InferredExceptionHelpers.import_text()
        return _str

    def add_import_definition(self, definition: ImportDefinition):
        defs_ = self.import_definitions.get(definition.module, set())
        if not definition in defs_:
            defs_.add(definition)
            self.import_definitions[definition.module] = defs_

    @staticmethod
    def from_inferred_func_declaration(
        inferred_func: Callable,
        all_type_definitions: Set[TypeDefinition],
        self_definition: TypeDefinition | None,
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
                self_definition_qualname=self_definition.qualname
                if self_definition
                else None,
            ),
            self_definition=self_definition,
            import_definitions={},
        )

        flat_import_defs = flatten_type_definitions(all_type_definitions)
        for _def in flat_import_defs:
            declaration.add_import_definition(_def)

        return declaration


def flatten_type_definitions(
    definitions: Set[TypeDefinition],
) -> Set[ImportDefinition]:
    flattened: Set[ImportDefinition] = set()
    for _def in definitions:
        if _def.type == "LocalClass":
            flattened.add(ImportDefinition.from_type_definition(_def))
        else:
            flat_type_defs = _def.flatten()
            flat_import_defs = [
                ImportDefinition.from_type_definition(_def) for _def in flat_type_defs
            ]
            flattened.update(flat_import_defs)
    return flattened


def signature_text_with_self_definition(
    signature_text: str, self_definition_qualname: str
) -> str:
    def text_with_type_name_after_self(signature_text, self_type_name):
        def replace(match):
            return match.group() + ":" + self_type_name

        pattern = r"\(self"
        new_text = re.sub(pattern, replace, signature_text, count=1)
        return new_text

    return text_with_type_name_after_self(signature_text, self_definition_qualname)


def build_signature_text(
    func_name: str, source_code: str, self_definition_qualname: str | None
) -> str:
    module = ast.parse(source_code)
    signature: str | None = None
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            # Reconstruct the function signature from the 'args' attribute
            signature = f"def {node.name}({ast.unparse(node.args)})"
            if node.returns:  # If there's a return annotation, add it
                signature += f" -> {ast.unparse(node.returns)}"
            signature += ":"
            break
    if signature is None:
        raise Exception("function signature not found")
    if self_definition_qualname is not None:
        signature = signature_text_with_self_definition(
            signature_text=signature, self_definition_qualname=self_definition_qualname
        )
    return signature
