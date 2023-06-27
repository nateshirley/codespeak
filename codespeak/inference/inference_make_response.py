from typing import Any
from pydantic import BaseModel


class InferenceMakeResponse(BaseModel):
    execution_result: Any | None
    source_code: str
