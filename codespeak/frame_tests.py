from typing import Callable, List
from pydantic import BaseModel

from codespeak.test_function import TestFunction


class FrameTests(BaseModel):
    """Tests used by Codespeak to infer code for a function"""

    # in the future, this will have more testing options than individual pytests

    test_functions: List[TestFunction] = []
