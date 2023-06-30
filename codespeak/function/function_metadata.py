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

    def _should_infer_new_source_code(
        self,
        active_digest: FunctionDigest,
    ) -> bool:
        if self.require_execution and not self.did_execute:
            return True
        if self.has_tests and not self.did_pass_tests:
            return True
        hash_eq = not self.declaration_digest.shallow_hash == active_digest.shallow_hash
        return hash_eq
