from typing import Any
from pydantic import BaseModel


class MakeInferenceResponse(BaseModel):
    execution_result: Any | None
    source_code: str
