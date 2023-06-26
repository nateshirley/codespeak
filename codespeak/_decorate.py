from typing import Any, Callable, TypeVar

from pydantic import BaseModel
from codespeak._core.codespeak_service import CodespeakService
from codespeak._declaration.codespeak_declaration import CodespeakDeclaration
from functools import wraps
from codespeak._core import diff, executor
from codespeak._core.code_generator import CodeGenerator
from codespeak._declaration.declaration_file_service import (
    DeclarationFileService,
)
from codespeak._helpers.self_type import self_type_if_exists
from codespeak._core.code_generator import TestFunc
from codespeak._settings import _settings
from codespeak._clean import clean
from codespeak._settings.environment import Environment


R = TypeVar("R")


def codespeak(func: Callable[..., R]) -> Callable[..., R]:
    @wraps(func)
    def dev_execute(*args: Any, **kwargs: Any) -> R:
        if not hasattr(codespeak_function, "file_service"):
            raise Exception("file service not found")
        file_service = codespeak_function.file_service
        self_type = self_type_if_exists(func, list(args), kwargs)
        declaration = CodespeakDeclaration.from_callable(func, self_type, file_service)
        should_generate_new_source_code = diff.require_new_codegen(
            file_service, declaration.digest
        )
        pytest_func: TestFunc | None = getattr(codespeak_function, "pytest_func", None)
        if should_generate_new_source_code:
            code_generator = CodeGenerator(
                declaration=declaration,
                service=CodespeakService.with_defaults(declaration),
                should_execute=True,
                test_func=pytest_func,
                args=list(args),
                kwargs=kwargs,
            )
            generation = code_generator.generate()
            if _settings.should_auto_clean():
                clean(_settings.abspath_to_codegen_dir())
            return generation.execution_result  # type: ignore
        else:
            return executor.execute_with_attributes(
                file_service.generated_module_qualname,
                file_service.generated_entrypoint,
                *args,
                **kwargs,
            )

    class _CodespeakFunction:
        file_service: DeclarationFileService
        pytest_func: TestFunc
        is_prod: bool
        logic: Callable

        def __call__(self, *args, **kwargs) -> R:
            if self.is_prod:
                return self.logic(*args, **kwargs)
            else:
                return dev_execute(*args, **kwargs)

        def use_pytest_function(self, _pytest_func: Callable):
            self.pytest_func = TestFunc.from_callable(_pytest_func)

    codespeak_function = _CodespeakFunction()
    assign_default_attributes(codespeak_function, func)
    return codespeak_function


def assign_default_attributes(codespeak_function: Callable, decorated_func: Callable):
    env = _settings.get_environment()
    codespeak_function.is_prod = env == Environment.PROD
    if env == _settings.Environment.PROD:
        logic = executor.load_generated_logic_from_module_qualname(
            DeclarationFileService.gather_generated_module_qualname(
                decorated_func=decorated_func
            ),
            decorated_func.__name__,
        )
        codespeak_function.logic = logic
    elif env == _settings.Environment.DEV:
        codespeak_function.file_service = DeclarationFileService.from_callable(
            decorated_func
        )
