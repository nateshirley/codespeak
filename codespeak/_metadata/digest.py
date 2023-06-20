import hashlib
import inspect
import json
from typing import Any, Dict, List

from pydantic import BaseModel


# in future, break up the digest into separate parts so that u could see which part caused the diff
class DeclarationDigest(BaseModel):
    source_hash: str
    deep_hash: str

    @staticmethod
    def from_inputs(
        declaration_source_code: str,
        custom_types: str,
    ) -> "DeclarationDigest":
        source_hash = hashlib.sha1(declaration_source_code.encode()).hexdigest()
        custom_types_hash = hashlib.sha1(to_buffer(custom_types)).hexdigest()

        components = [source_hash, custom_types_hash]
        deep_hash = hashlib.sha1("".join(components).encode()).hexdigest()

        return DeclarationDigest(
            source_hash=source_hash,
            deep_hash=deep_hash,
        )


def to_buffer(_val: Dict[str, Any] | str | List[Dict[str, Any] | str]) -> bytes:
    if isinstance(_val, str):
        return _val.encode()
    else:
        return json.dumps(_val, indent=4).encode()
