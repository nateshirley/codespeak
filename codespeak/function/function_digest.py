import hashlib
import inspect
import json
from typing import Any, Dict, List, Set

from pydantic import BaseModel

from codespeak.type_definitions.type_definition import TypeDefinition


class FunctionDigest(BaseModel):
    shallow_hash: str

    @staticmethod
    def from_inputs(
        function_declaration_signature_text: str,
        function_declaration_docstring: str,
        type_definitions_without_inheritance: Set[TypeDefinition],
    ) -> "FunctionDigest":
        declaration_hash = hashlib.sha1(
            function_declaration_signature_text.encode()
        ).hexdigest()
        docstring_hash = hashlib.sha1(
            function_declaration_docstring.encode()
        ).hexdigest()
        type_def_hash_object = hashlib.sha256()
        for type_def in sorted(type_definitions_without_inheritance):
            type_def_hash_object.update(type_def.import_path().encode())
        type_definitions_hash = type_def_hash_object.hexdigest()

        components = [declaration_hash, docstring_hash, type_definitions_hash]
        shallow_hash = hashlib.sha1("".join(components).encode()).hexdigest()

        return FunctionDigest(
            shallow_hash=shallow_hash,
        )

    def __eq__(self, other):
        if isinstance(other, FunctionDigest):
            return self.shallow_hash == other.shallow_hash
        return False


def to_buffer(_val: Dict[str, Any] | str | List[Dict[str, Any] | str]) -> bytes:
    if isinstance(_val, str):
        return _val.encode()
    else:
        return json.dumps(_val, indent=4).encode()
