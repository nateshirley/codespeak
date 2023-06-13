import inspect
import os
from typing import Callable, List, Any
from codespeak.core.codespeak_service import CodespeakService
from codespeak.declaration.codespeak_declaration import CodespeakDeclaration
from functools import wraps
from codespeak.core import diff, executor
from codespeak.core.code_generator import CodeGenerator
from codespeak.declaration.declaration_file_service import (
    DeclarationFileService,
)
from codespeak.helpers.self_type import self_type_if_exists
from codespeak.core.code_generator import TestFunc
from codespeak.config import get_environment, Environment


def codespeak(pytest_func: Callable | None = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(wrapper, "file_service"):
                raise Exception("file service not found")
            if get_environment() == Environment.DEV:
                self_type = self_type_if_exists(func, list(args), kwargs)
                declaration = CodespeakDeclaration.from_callable(
                    func, self_type, wrapper.file_service
                )
                should_generate_new_source_code = diff.require_new_codegen(
                    wrapper.file_service, declaration.digest
                )
                test_func = TestFunc.from_callable(pytest_func) if pytest_func else None
                if should_generate_new_source_code:
                    code_generator = CodeGenerator(
                        declaration=declaration,
                        service=CodespeakService.with_defaults(declaration),
                        should_execute=True,
                        test_func=test_func,
                        args=list(args),
                        kwargs=kwargs,
                    )
                    generation = code_generator.generate()
                    return generation.execution_result
            return executor.execute_with_attributes(
                wrapper.file_service.generated_module_qualname,
                func.__name__,
                *args,
                **kwargs
            )

        setattr(
            wrapper,
            "file_service",
            DeclarationFileService.from_callable(func),
        )
        return wrapper

    return decorator
