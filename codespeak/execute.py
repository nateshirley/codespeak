from typing import Any, Callable, Dict, List
from codespeak.core.executor import execute_from_callable


def execute(
    func: Callable,
    args: List[Any] | None = None,
    kwargs: Dict[str, Any] | None = None,
) -> str:
    args = args or []
    kwargs = kwargs or {}
    return execute_from_callable(func, *args, **kwargs)
