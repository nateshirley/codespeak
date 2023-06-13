import ast
import inspect
import json
import textwrap
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, validator
from codespeak.declaration.declaration_file_service import DeclarationFileService
from codespeak.declaration import declaration_helpers
from codespeak.definitions import classify
from codespeak.definitions.definition import Definition

from codespeak.definitions.utils.dedupe import dedupe
from codespeak.definitions.utils.group import group_by_module
from codespeak.declaration.body_imports import BodyImports
from codespeak import generated_exception
from codespeak.metadata.digest import DeclarationDigest


class CodespeakDeclaration(BaseModel):
    name: str
    qualname: str
    module_name: str
    docstring: str
    source_code: str
    signature_text: str
    signature_defs: List[Definition]
    computed_custom_types: Dict | None = None
    computed_digest: DeclarationDigest | None = None
    body_imports: BodyImports
    import_defs: Dict[str, List[Definition]]
    file_service: DeclarationFileService

    def compute_custom_types(self):
        defs = {}
        for _def in self.signature_defs:
            defs.update(_def.custom_types())
        defs.update(self.body_imports.custom_types())
        defs.update(generated_exception.annotate())
        self.computed_custom_types = {"custom_types": defs}

    def compute_digest(self) -> DeclarationDigest:
        return DeclarationDigest.from_inputs(
            declaration_source_code=self.source_code,
            custom_types=self.as_custom_types_str(),
        )

    @property
    def digest(self) -> DeclarationDigest:
        if not self.computed_digest:
            self.computed_digest = self.compute_digest()
        if not self.computed_digest:
            raise Exception("unable to compute digest")
        return self.computed_digest

    @property
    def custom_types(self) -> Dict:
        if not self.computed_custom_types:
            self.compute_custom_types()
        if not self.computed_custom_types:
            raise Exception("custom types not computed")
        return self.computed_custom_types

    def as_custom_types_str(self) -> str:
        return json.dumps(self.custom_types, indent=4)

    def as_incomplete_file(self) -> str:
        return self.imports() + "\n" + self.signature_text + "\n"

    def imports(self) -> str:
        grouped_defs = self.import_defs
        _str = ""
        for module, types in grouped_defs.items():
            if module == "builtins" or module == "None":
                continue
            _str += f"from {module} import {', '.join([_type.qualname for _type in types])}\n"
        _str += self.body_imports.import_text()
        return _str

    def prompt_inputs(self) -> str:
        inputs = {
            "incomplete_file": self.as_incomplete_file(),
            "custom_types": self.custom_types,
        }
        return json.dumps(inputs, indent=4)

    def annotate(self) -> Dict:
        signature_defs = {}
        for _def in self.signature_defs:
            signature_defs.update(_def.annotate())
        return {
            "signature_defs": signature_defs,
            "signature_text": self.signature_text,
            "docstring": self.docstring,
            "imports": self.import_defs,
        }

    @staticmethod
    def from_callable(
        func: Callable,
        self_class_obj: Any | None,
        with_file_service: DeclarationFileService | None = None,
    ) -> "CodespeakDeclaration":
        signature = inspect.signature(func)
        source_code = textwrap.dedent(inspect.getsource(func))
        if self_class_obj:
            self_definition = classify.from_self_class_obj(
                self_class_obj, func.__name__
            )
            self_type_name = self_class_obj.__name__
        else:
            self_definition = None
            self_type_name = None

        signature_defs = declaration_helpers.definitions_for_signature(
            signature, self_definition=self_definition
        )
        file_service = with_file_service or DeclarationFileService.from_callable(func)

        return CodespeakDeclaration(
            name=func.__name__,
            qualname=func.__qualname__,
            module_name=func.__module__,
            docstring=inspect.getdoc(func) or "",
            source_code=source_code,
            signature_text=declaration_helpers.build_sig_string(
                func_name=func.__name__,
                source_code=source_code,
                self_type_name=self_type_name,
            ),
            signature_defs=signature_defs,
            import_defs=build_import_defs(signature_defs=signature_defs),
            body_imports=BodyImports.from_func_source(source_code),
            file_service=file_service,
        )


def build_import_defs(signature_defs: List[Definition]) -> Dict[str, List[Definition]]:
    flattened = []
    for _def in signature_defs:
        if _def.type == "LocalClass":
            flattened.append(_def)
        else:
            flattened.extend(_def.flatten())
    return group_by_module(dedupe(flattened))
