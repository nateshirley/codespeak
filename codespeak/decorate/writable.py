from functools import wraps
import inspect
import textwrap
from typing import Any, Callable, Dict, List, Tuple, TypeVar
from functools import wraps
from codespeak import executor
from codespeak.function.function_file_service import (
    FunctionFileService,
)
from codespeak.function.function_declaration import (
    FunctionDeclaration,
)
from codespeak.function.writable_function import WritableFunction
from codespeak.helpers.guarantee_abspath_to_root_exists import (
    guarantee_abspath_to_project_root_exists,
)
from codespeak.settings import _settings
from codespeak.settings.environment import Environment
from codespeak.function import Function
from codespeak.function.function_attributes import FunctionAttributes
from codespeak.frame_tests import FrameTests
from codespeak.frame import Frame
from codespeak.helpers.get_definitions_from_function_object import (
    get_definitions_from_function_object,
)
from codespeak.decorate.infer import _assign_default_inferred_attributes
from codespeak.decorate.writable_transform import replace_function


def writable(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        writable_function = WritableFunction(wrapper)
        should_write = should_write_function(func)
        if should_write:
            return writable_function.write(func, args, kwargs)
        else:
            return func(*args, **kwargs)

    _assign_default_inferred_attributes(wrapper, func)
    return wrapper


import libcst as cst
from libcst import MaybeSentinel, RemovalSentinel
from libcst.metadata import ProviderT, ExpressionContextProvider, ExpressionContext

# from libcst._nodes.module import get_docstring


class ShouldWriteVisitor(cst.CSTVisitor):
    def __init__(self) -> None:
        self.should_write = False

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        body = node.body.body
        docstring = node.get_docstring(clean=True)

        # Remove the leading docstring if it exists
        if docstring is not None:
            body = body[1:]

        # Check if the function only contains a 'pass' statement now
        if len(body) == 1 and isinstance(body[0], cst.SimpleStatementLine):
            first_statement = body[0]
            if len(first_statement.body) == 1 and isinstance(
                first_statement.body[0], cst.Pass
            ):
                self.should_write = True


def should_write_function(func: Callable) -> bool:
    source = inspect.getsource(func)
    module = cst.parse_module(source)
    visitor = ShouldWriteVisitor()
    module.visit(visitor)
    return visitor.should_write
