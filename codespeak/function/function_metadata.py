from pydantic import BaseModel
from codespeak.function.function_digest import FunctionDigest


class FunctionMetadata(BaseModel):
    declaration_digest: FunctionDigest
    declaration_source: str
    require_execution: bool
    did_execute: bool
    has_tests: bool
    did_pass_tests: bool
    updated_at: str
