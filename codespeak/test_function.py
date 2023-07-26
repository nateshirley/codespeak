import inspect
from typing import Callable
from pydantic import BaseModel


class TestFunction(BaseModel):
    file: str
    qualname: str
    source_code: str

    @staticmethod
    def from_callable(test_func: Callable) -> "TestFunction":
        source_code = inspect.getsource(test_func)
        file = inspect.getfile(test_func)
        return TestFunction(
            file=file,
            qualname=test_func.__qualname__,
            source_code=source_code,
        )
