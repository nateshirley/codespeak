from typing import Any, Callable, Dict, List
from codespeak.core.executor import execute_with_attributes


def unsafe_execute(
    func: Callable,
    args: List[Any] | None = None,
    kwargs: Dict[str, Any] | None = None,
) -> str:
    args = args or []
    kwargs = kwargs or {}
    if not hasattr(func, "file_service"):
        raise Exception("file service not found")
    return execute_with_attributes(
        func.file_service.generated_module_qualname, func.__name__, *args, **kwargs
    )
