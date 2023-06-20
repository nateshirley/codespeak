from typing import Any, Callable, Dict, List

from pydantic import BaseModel
from codespeak._core.executor import (
    load_generated_logic_from_module_qualname,
)
from codespeak._declaration.declaration_file_service import DeclarationFileService
from codespeak._settings import _settings


def unsafe_execute(
    func: Callable,
    args: List[Any] | None = None,
    kwargs: Dict[str, Any] | None = None,
) -> str:
    """Direct execution of a function's logic in development mode, bypassing any diff checks"""
    args = args or []
    kwargs = kwargs or {}
    if _settings.get_environment() == _settings.Environment.PROD:
        raise Exception(
            "unsafe_execute is not available in production, call the Codespeak function directly"
        )
    return _UnwrappedCodespeakFunction.try_from_callable(func).execute(*args, **kwargs)


class _UnwrappedCodespeakFunction(BaseModel):
    file_service: DeclarationFileService
    logic: Callable

    def execute(self, *args, **kwargs) -> str:
        if _settings.get_environment() == _settings.Environment.PROD:
            raise Exception(
                "unsafe_execute is not available in production, call the Codespeak function directly"
            )
        return self.logic(*args, **kwargs)

    @staticmethod
    def try_from_callable(func: Callable) -> "_UnwrappedCodespeakFunction":
        if _settings.get_environment() == _settings.Environment.PROD:
            raise Exception(
                "unsafe_execute is not available in production, call the Codespeak function directly"
            )
        file_servie: DeclarationFileService | None = getattr(func, "file_service", None)
        if file_servie is None:
            raise Exception("missing file_service attribute on development wrapper")

        logic = load_generated_logic_from_module_qualname(
            module_qualname=file_servie.generated_module_qualname,
            func_name=file_servie.generated_entrypoint,
        )
        return _UnwrappedCodespeakFunction(file_service=file_servie, logic=logic)
