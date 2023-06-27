from typing import Callable, List
from pydantic import BaseModel

from codespeak._core.code_generator import TestFunc


class Tests(BaseModel):
    """Tests used by Codespeak to infer code for a function"""

    # in the future, this will have more testing options than individual pytests

    pytest_functions: List[Callable] = []

    def add_pytest_function(self, test_func: Callable):
        if not test_func.__name__.startswith("test_"):
            raise ValueError(
                f"Expected function name to start with 'test_', got {test_func.__name__}"
            )
        self.pytest_functions.append(test_func)

    def try_get_test_func(self) -> TestFunc | None:
        if len(self.pytest_functions) == 0:
            return None
        return TestFunc.from_callable(self.pytest_functions[0])
