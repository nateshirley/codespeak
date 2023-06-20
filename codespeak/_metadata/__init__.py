from pydantic import BaseModel
from codespeak._metadata.digest import DeclarationDigest


class FunctionMetadata(BaseModel):
    declaration_digest: DeclarationDigest
    declaration_source: str
    require_execution: bool
    did_execute: bool
    has_tests: bool
    did_pass_tests: bool
    updated_at: str
