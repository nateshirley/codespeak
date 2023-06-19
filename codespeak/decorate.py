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
from codespeak import config


def codespeak(pytest_func: Callable | None = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if wrapper.env == "prod":
                return wrapper.logic(*args, **kwargs)
            else:
                if not hasattr(wrapper, "file_service"):
                    raise Exception("file service not found")
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
                else:
                    return executor.execute_with_attributes(
                        wrapper.file_service.generated_module_qualname,
                        wrapper.file_service.generated_entrypoint,
                        *args,
                        **kwargs,
                    )

        set_decorator_attributes(wrapper, func)
        return wrapper

    return decorator


def set_decorator_attributes(wrapper: Callable, decorated_func: Callable):
    env = config.get_environment()
    setattr(wrapper, "env", env.value)
    if env == config.Environment.PROD:
        logic = executor.load_generated_logic_from_module_qualname(
            DeclarationFileService.gather_generated_module_qualname(
                decorated_func=decorated_func
            ),
            decorated_func.__name__,
        )
        setattr(wrapper, "logic", logic)
        return
    elif env == config.Environment.DEV:
        file_service = DeclarationFileService.from_callable(decorated_func)
        setattr(wrapper, "file_service", file_service)
