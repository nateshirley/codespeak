import inspect
import sys
from typing import Any, Callable

"""
this will only have programmable resources and tests

whereas a function will have programmable resources, tests, and declaration resources
"""


class ModuleAttributes:
    frame = "_frame"


class ModuleFrame:
    @staticmethod
    def add_frame_to_module(module: Any, frame: "ModuleFrame"):
        setattr(module, ModuleAttributes.frame, frame)

    @staticmethod
    def for_module(__name__: str) -> "ModuleFrame":
        """get classified Function object for an inferred function"""
        if not hasattr(sys.modules, __name__):
            raise Exception(
                "No module found for the given name. Use python's built-in __name__ atribute."
            )
        mod = getattr(sys.modules, __name__)
        if not hasattr(mod, ModuleAttributes.frame):
            ModuleFrame.add_frame_to_module(mod, ModuleFrame())
        return getattr(mod, ModuleAttributes.frame)

    @staticmethod
    def for_name(__name__: str) -> "ModuleFrame":
        """get classified Function object for an inferred function"""
        if not hasattr(sys.modules, __name__):
            raise Exception(
                "No module found for the given name. Use python's built-in __name__ atribute."
            )
        mod = getattr(sys.modules, __name__)
        if not hasattr(mod, ModuleAttributes.frame):
            ModuleFrame.add_frame_to_module(mod, ModuleFrame())
        return getattr(mod, ModuleAttributes.frame)
