from importlib import import_module
from typing import Any, Callable


def load_generated_logic_from_module_qualname(
    module_qualname: str, func_name: str
) -> Callable:
    try:
        module = import_module(module_qualname)
    except Exception as e:
        raise Exception(f"Could not import module path at {module_qualname}. e: {e}")
    if hasattr(module, func_name):
        return getattr(module, func_name)
    else:
        raise Exception(
            f"Could not find function {func_name} on module {module_qualname}"
        )


def execute_unchecked(codegen_module_qualname: str, func_name: str, *args, **kwargs):
    logic = load_generated_logic_from_module_qualname(
        codegen_module_qualname, func_name=func_name
    )
    return logic(*args, **kwargs)


# def execute_safe(logic: Callable, *args, **kwargs) -> Any:
#     try:
#         result = logic(*args, **kwargs)
#         return result
#     except Exception as e:
# could put telemetry here to track how often we're not properly wrapping exceptions, leaving for now
#         if isinstance(e, GeneratedException):
#             raise e.exception
#         else:
#             print("--UNSAFE EXCEPTION-- not wrapped in GeneratedException")
#             raise e
