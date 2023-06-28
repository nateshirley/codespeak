import inspect
import json
import sys
from typing import Any, Callable, Dict, List, Set, Tuple

from pydantic import BaseModel
from codespeak.definitions import classify
from codespeak.definitions.definition import Definition
from codespeak.function.function_attributes import FunctionAttributes
from codespeak.function.function_manager import FunctionManager
from codespeak.function.function_tests import FunctionTests
from codespeak.helpers.guarantee_abspath_to_root_exists import (
    guarantee_abspath_to_project_root_exists,
)
from codespeak.helpers.self_type import self_type_if_exists
from codespeak.test_function import TestFunction

function_manager = FunctionManager()


class Frame(BaseModel):
    definitions: Set[Definition] = set()
    tests: FunctionTests = FunctionTests()
    parents: List["Frame"] = []

    def custom_types(self) -> Dict:
        types_ = {}
        for _class in self.definitions:
            types_.update(_class.custom_types())
        for parent in self.parents:
            types_.update(parent.custom_types())
        return types_

    def printable_custom_types(self) -> str:
        return json.dumps(self.custom_types(), indent=4)

    def printable_definitions_with_inheritance(self) -> str:
        return json.dumps(
            [d.annotate() for d in self.definitions_with_inheritance], indent=4
        )

    def add_classes(self, *classes: type):
        for _class in classes:
            if not inspect.isclass(_class):
                raise ValueError(f"Expected class object, got {type(_class).__name__}")
            self.definitions.add(classify.from_any(_class))

    def add_test_function(self, test_func: Callable):
        if not test_func.__name__.startswith("test_"):
            raise ValueError(
                f"Expected function name to start with 'test_', got {test_func.__name__}"
            )
        self.tests.test_functions.append(TestFunction.from_callable(test_func))

    @property
    def definitions_with_inheritance(self) -> Set[Definition]:
        defs = set()
        for parent in self.parents:
            defs.update(parent.definitions_with_inheritance)
        defs.update(self.definitions)
        return defs

    @staticmethod
    def this() -> "Frame":
        """easy way to access Frame for a function from inside it"""
        try:
            return Frame.for_function(Frame.get_manager().get_function())
        except Exception as e:
            raise Exception(
                "No frame found. Make sure this is an inferred function—it should use codespeak's @infer decorator",
                e,
            )

    @staticmethod
    def get_manager() -> FunctionManager:
        return function_manager

    @staticmethod
    def for_function(func: Callable[..., Any]) -> "Frame":
        """get classified Function object for an inferred function"""
        if not hasattr(func, FunctionAttributes.frame):
            raise Exception(
                "No frame found. Make sure this is an inferred function—it should use codespeak's @infer decorator"
            )
        return getattr(func, FunctionAttributes.frame)

    @staticmethod
    def for_module(name: str) -> "Frame":
        mod = sys.modules.get(name)
        guarantee_abspath_to_project_root_exists(mod)
        if mod is None:
            raise Exception(
                "No module found for the given name. Use python's built-in __name__ atribute."
            )
        if not hasattr(mod, ModuleAttributes.frame):
            frame = Frame()
            setattr(mod, ModuleAttributes.frame, frame)
            return frame
        else:
            return getattr(mod, ModuleAttributes.frame)


class ModuleAttributes:
    frame = "_frame"
