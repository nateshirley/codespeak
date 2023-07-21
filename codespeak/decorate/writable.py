from functools import wraps
import inspect
from typing import Any, Callable, Dict, List, Tuple, TypeVar
from functools import wraps
from codespeak import executor
from codespeak.function.function_file_service import (
    FunctionFileService,
)
from codespeak.function.function_declaration import (
    FunctionDeclaration,
)
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

"""
1. get source file 
"""


def writable(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        function = Function(wrapper)
        function_file = inspect.getsourcefile(func)
        source_code = inspect.getsource(func)
        print("\nsource code:\n", source_code)
        print(function_file)
        # with Frame.get_manager().manage_for(wrapper):
        #     func(*args, **kwargs)
        return func(*args, **kwargs)

    _assign_default_inferred_attributes(wrapper, func)
    return wrapper


import libcst as cst
from libcst import MaybeSentinel, RemovalSentinel
from libcst.metadata import ProviderT, ExpressionContextProvider, ExpressionContext
from libcst.helpers import get_docstring


class PassCheckVisitor(cst.CSTVisitor):
    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        body = node.body.body
        docstring = get_docstring(node, clean=False)

        # Remove the leading docstring if it exists
        if docstring is not None:
            body = body[1:]

        # Check if the function only contains a 'pass' statement now
        if len(body) == 1 and isinstance(body[0], cst.SimpleStatementLine):
            first_statement = body[0]
            if len(first_statement.body) == 1 and isinstance(
                first_statement.body[0], cst.Pass
            ):
                print(f"Function {node.name.value} only contains 'pass'.")
