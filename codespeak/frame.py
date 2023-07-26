import inspect
import json
import sys
from typing import Any, Callable, Dict, List, Set, Tuple

from pydantic import BaseModel
from codespeak.public.inferred_exception import InferredExceptionHelpers
from codespeak.type_definitions import classify
from codespeak.type_definitions.type_definition import TypeDefinition
from codespeak.function.function_attributes import FunctionAttributes
from codespeak.function.function_manager import FunctionManager
from codespeak.frame_tests import FrameTests
from codespeak.helpers.guarantee_abspath_to_root_exists import (
    guarantee_abspath_to_project_root_exists,
)
from codespeak.helpers.self_type import self_type_if_exists
from codespeak.test_function import TestFunction

function_manager = FunctionManager()


class Frame(BaseModel):
    # resources /// definitions (TypeTypeDefinitions), functions, modules
    type_definitions: Set[TypeDefinition] = set()
    tests: FrameTests = FrameTests()
    parents: List["Frame"] = []

    def custom_types(self) -> Dict:
        types_ = {}
        for _class in self.type_definitions:
            types_.update(_class.custom_types())
        for parent in self.parents:
            types_.update(parent.custom_types())
        types_.update(InferredExceptionHelpers.annotate())
        return types_

    def printable_custom_types(self) -> str:
        return json.dumps(self.custom_types(), indent=4)

    def printable_type_definitions_with_inheritance(self) -> str:
        return json.dumps(
            [d.annotate() for d in self.type_definitions_with_inheritance], indent=4
        )

    def add_classes(self, *classes: type):
        for _class in classes:
            if not inspect.isclass(_class):
                raise ValueError(f"Expected class object, got {type(_class).__name__}")
            self.type_definitions.add(classify.from_any(_class))

    def add_test_function(self, test_func: Callable):
        if not test_func.__name__.startswith("test_"):
            raise ValueError(
                f"Expected function name to start with 'test_', got {test_func.__name__}"
            )
        self.tests.test_functions.append(TestFunction.from_callable(test_func))

    @property
    def type_definitions_with_inheritance(self) -> Set[TypeDefinition]:
        defs = set()
        for parent in self.parents:
            defs.update(parent.type_definitions_with_inheritance)
        defs.update(self.type_definitions)
        return defs

    @staticmethod
    def this() -> "Frame":
        """Dedicated syntax for accessing Frame for a function from inside its body. Bundled with a context manager in the @infer decorator."""
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
        """Create a frame for a module, whose resources will be used by all inferred functions in that module"""
        mod = sys.modules.get(name)
        if mod is None:
            raise Exception(
                "No module found for the given name. Use python's built-in __name__ atribute."
            )
        if not hasattr(mod, ModuleAttributes.frame):
            guarantee_abspath_to_project_root_exists(mod)
            frame = Frame()
            setattr(mod, ModuleAttributes.frame, frame)
            return frame
        else:
            return getattr(mod, ModuleAttributes.frame)


class ModuleAttributes:
    frame = "_frame"
