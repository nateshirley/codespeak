from typing import Any, Callable, Dict, List
from codespeak.core.code_generator import CodeGenerator, TestFunc
from codespeak.core.codespeak_service import CodespeakService
from codespeak.declaration.codespeak_declaration import CodespeakDeclaration
from codespeak.helpers.self_type import self_type_if_exists


def generate(
    func: Callable,
    args: List[Any] | None = None,
    kwargs: Dict[str, Any] | None = None,
    pytest_func: Callable | None = None,
    should_execute: bool = False,
) -> str:
    """Used to explicitly generate code for a function, skipping the diff check with previous version. Optionally, allows execution with explicitly passed args and kwargs."""
    args = args or []
    kwargs = kwargs or {}
    self_type = self_type_if_exists(func, list(args), kwargs)
    declaration = CodespeakDeclaration.from_callable(func, self_type)
    test_func = TestFunc.from_callable(pytest_func) if pytest_func else None
    code_generator = CodeGenerator(
        declaration=declaration,
        service=CodespeakService.with_defaults(declaration),
        should_execute=should_execute,
        test_func=test_func,
        args=args,
        kwargs=kwargs,
    )
    code_generator.generate()
    return code_generator.latest_source_code
