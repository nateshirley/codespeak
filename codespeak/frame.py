import inspect
from typing import Any, Callable, Dict, Tuple
from codespeak.definitions import classify
from codespeak.function.function_attributes import FunctionAttributes
from codespeak.function.function_manager import FunctionManager
from codespeak.function_resources.function_resources import FunctionResources
from codespeak.function.function_tests import FunctionTests
from codespeak.helpers.self_type import self_type_if_exists


class Frame:
    resources: FunctionResources
    tests: FunctionTests
    manager = FunctionManager()

    def __init__(self, resources: FunctionResources, tests: FunctionTests) -> None:
        self.resources = resources
        self.tests = tests

    def add_classes(self, *classes: type):
        for _class in classes:
            if not inspect.isclass(_class):
                raise ValueError(f"Expected class object, got {type(_class).__name__}")
            self.resources.programmable_resources.classes.append(
                classify.from_any(_class)
            )

    def add_test_function(self, test_func: Callable):
        if not test_func.__name__.startswith("test_"):
            raise ValueError(
                f"Expected function name to start with 'test_', got {test_func.__name__}"
            )
        self.tests.test_functions.append(test_func)

    @staticmethod
    def this() -> "Frame":
        """easy way to access Frame for a function from inside it"""
        try:
            return Frame.for_function(Frame.manager.get_function())
        except Exception as e:
            raise Exception(
                "No frame found. Make sure this is an inferred function—it should use codespeak's @infer decorator",
                e,
            )

    @staticmethod
    def for_function(func: Callable[..., Any]) -> "Frame":
        """get classified Function object for an inferred function"""
        if not hasattr(func, FunctionAttributes.frame):
            raise Exception(
                "No frame found. Make sure this is an inferred function—it should use codespeak's @infer decorator"
            )
        return getattr(func, FunctionAttributes.frame)
