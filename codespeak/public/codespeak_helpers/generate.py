from typing import Any, Callable, Dict, List
from codespeak._core.code_generator import CodeGenerator, TestFunc
from codespeak._core.codespeak_service import CodespeakService
from codespeak._declaration.codespeak_declaration import CodespeakDeclaration
from codespeak._helpers.self_type import self_type_if_exists


# def generate(
#     func: Callable,
#     args: List[Any] | None = None,
#     kwargs: Dict[str, Any] | None = None,
#     pytest_func: Callable | None = None,
#     should_execute: bool = False,
# ) -> str:
#     """Used to explicitly generate code for a function, skipping the diff check with previous version. Optionally, allows execution with explicitly passed args and kwargs, but does not return the result."""
#     args = args or []
#     kwargs = kwargs or {}
#     self_type = self_type_if_exists(func, list(args), kwargs)
#     declaration = CodespeakDeclaration.from_callable(func, self_type)
#     test_func = TestFunc.from_callable(pytest_func) if pytest_func else None
#     code_generator = CodeGenerator(
#         declaration=declaration,
#         service=CodespeakService.with_defaults(declaration),
#         should_execute=should_execute,
#         test_func=test_func,
#         args=args,
#         kwargs=kwargs,
#     )
#     code_generator.generate()
#     return code_generator.latest_source_code


"""

                pytest_func: TestFunc | None = inference.tests.try_get_test_func()
                code_generator = CodeGenerator(
                    declaration=declaration,
                    service=CodespeakService.with_defaults(declaration),
                    should_execute=True,
                    test_func=pytest_func,
                    args=list(args),
                    kwargs=kwargs,
                )
                generation = code_generator.generate()
                logic = executor.load_generated_logic_from_module_qualname(
                    module_qualname=file_service.generated_module_qualname,
                    func_name=file_service.generated_entrypoint,
                )
                setattr(wrapper, InferenceAttributes.logic, logic)
"""
