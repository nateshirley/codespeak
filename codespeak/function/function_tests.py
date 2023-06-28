from typing import Callable, List
from pydantic import BaseModel

from codespeak.inference.inference_engine import TestFunc


class FunctionTests(BaseModel):
    """Tests used by Codespeak to infer code for a function"""

    # in the future, this will have more testing options than individual pytests

    pytest_functions: List[Callable] = []

    def try_get_test_func(self) -> TestFunc | None:
        if len(self.pytest_functions) == 0:
            return None
        return TestFunc.from_callable(self.pytest_functions[0])
