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


class DeclarationResources(BaseModel):
    """Resources that are imputed from the function's declaration"""

    name: str
    qualname: str
    module_name: str
    docstring: str
    source_code: str
    signature_text: str
    signature_defs: List[Definition]
    flat_grouped_signature_defs: Dict[str, List[Definition]]
    self_definition: Definition | None = None
    computed_custom_types: Dict | None = None

    def compute_custom_types(self):
        defs = {}
        for _def in self.signature_defs:
            defs.update(_def.custom_types())
        if self.self_definition:
            defs.update(self.self_definition.custom_types())
        defs.update(inferred_exception.annotate())
        self.computed_custom_types = defs

    @property
    def custom_types(self) -> Dict:
        if not self.computed_custom_types:
            self.compute_custom_types()
        if not self.computed_custom_types:
            raise Exception("custom types not computed")
        return self.computed_custom_types

    def as_incomplete_file(self) -> str:
        return self.imports_text() + "\n" + self.signature_text + "\n"

    # potentially buggy
    def imports_text(self) -> str:
        grouped_defs = self.flat_grouped_signature_defs
        _str = ""
        for module, types in grouped_defs.items():
            if module == "builtins" or module == "None":
                continue
            _str += f"from {module} import {', '.join([_type.qualname for _type in types])}\n"
        return _str

    def annotate(self) -> Dict:
        signature_defs = {}
        for _def in self.signature_defs:
            signature_defs.update(_def.annotate())
        return {
            "signature_defs": signature_defs,
            "signature_text": self.signature_text,
            "docstring": self.docstring,
            "imports": self.flat_grouped_signature_defs,
        }

    def try_add_self_definition(self, self_type: Any) -> None:
        if self.self_definition:
            return

        def text_with_type_after_self(signature_text, self_type_name):
            def replace(match):
                return match.group() + ":" + self_type_name

            pattern = r"\(self"
            new_text = re.sub(pattern, replace, signature_text, count=1)
            return new_text

        self.self_definition = classify.from_self_class(self_type, self.name)
        if self.computed_custom_types:
            """if computed types have already been computed, add the self type to them"""
            self.computed_custom_types.update(self.self_definition.custom_types())
        self.signature_text = text_with_type_after_self(
            self.signature_text, self_type.__name__
        )

    @staticmethod
    def from_inferred_func(
        inferred_func: Callable,
    ) -> "DeclarationResources":
        signature = inspect.signature(inferred_func)
        source_code = textwrap.dedent(inspect.getsource(inferred_func))
        signature_defs = definitions_for_signature(signature)

        return DeclarationResources(
            name=inferred_func.__name__,
            qualname=inferred_func.__qualname__,
            module_name=inferred_func.__module__,
            docstring=inspect.getdoc(inferred_func) or "",
            source_code=source_code,
            signature_text=build_sig_string(
                func_name=inferred_func.__name__,
                source_code=source_code,
            ),
            signature_defs=signature_defs,
            flat_grouped_signature_defs=build_flat_grouped_signature_defs(
                signature_defs=signature_defs
            ),
        )


# this is just to write the imports that are used in the signature's type hints
def build_flat_grouped_signature_defs(
    signature_defs: List[Definition],
) -> Dict[str, List[Definition]]:
    """imports for the types that are used in the signature. a deduped version of the types, grouped by module"""
    flattened = []
    for _def in signature_defs:
        if _def.type == "LocalClass":
            flattened.append(_def)
        else:
            flattened.extend(_def.flatten())
    return group_by_module(dedupe(flattened))


def build_sig_string(func_name: str, source_code: str) -> str:
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


def definitions_for_signature(
    sig: inspect.Signature,
) -> List[Definition]:
    """Definitions for types used in the signature"""
    defs: List[Definition] = []
    params = sig.parameters
    for param in params.values():
        _def = param.annotation
        if _def is inspect.Signature.empty:
            continue
        defs.append(classify.from_any(_def))
    return_annotation = sig.return_annotation
    if not return_annotation is inspect.Signature.empty:
        defs.append(classify.from_any(return_annotation))
    return defs
