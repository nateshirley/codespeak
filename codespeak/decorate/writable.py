from functools import wraps
import inspect
from typing import Any, Callable, Dict, List, Tuple, TypeVar
from functools import wraps
from codespeak.function.function_declaration import (
    FunctionDeclaration,
)
from codespeak.function.writable_function import WritableFunction
from codespeak.settings import settings
from codespeak.settings.environment import Environment
from codespeak.function.function_attributes import FunctionAttributes
from codespeak.frame_tests import FrameTests
from codespeak.frame import Frame
from codespeak.helpers.get_definitions_from_function_object import (
    get_definitions_from_function_object,
)
from codespeak.settings.settings import Environment


def writable(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if wrapper._is_dev:  # type: ignore
            if should_write_function(func):
                writable_function = WritableFunction(wrapper)
                return writable_function._write(get_source_file(func))
        return func(*args, **kwargs)

    _assign_default_function_attributes(wrapper, func)

    return wrapper


def get_source_file(function: Callable) -> str:
    ff = inspect.getsourcefile(function)
    if ff is None:
        raise ValueError("Function must be defined in a file")
    return ff


import libcst as cst
from libcst import MaybeSentinel, RemovalSentinel
from libcst.metadata import ProviderT, ExpressionContextProvider, ExpressionContext


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


def _assign_default_function_attributes(wrapper: Callable, decorated_func: Callable):
    env = settings.get_environment()
    setattr(wrapper, FunctionAttributes.is_dev, env != Environment.PROD)
    if env == Environment.DEV:
        function_definitions = get_definitions_from_function_object(decorated_func)
        setattr(
            wrapper,
            FunctionAttributes.declaration,
            FunctionDeclaration.from_inferred_func_declaration(
                inferred_func=decorated_func,
                all_type_definitions=function_definitions["all"],
                self_definition=function_definitions["self"],
                return_type_definition=function_definitions["return_type"],
                param_definitions=function_definitions["params"],
            ),
        )
        setattr(
            wrapper,
            FunctionAttributes.frame,
            Frame(
                type_definitions=function_definitions["all"],
                tests=FrameTests(),
                parents=[Frame.for_module(decorated_func.__module__)],
            ),
        )
