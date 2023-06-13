from importlib import import_module
from typing import Any, Callable, Dict, List
from codespeak.generated_exception import GeneratedException
from codespeak.declaration.declaration_file_service import DeclarationFileService


def load_generated_logic_from_callable(callable: Callable) -> Callable:
    modulepath = DeclarationFileService.logic_modulepath_from_callable(callable)
    return load_generated_logic_from_modulepath(modulepath, func_name=callable.__name__)


def load_generated_logic_from_modulepath(modulepath: str, func_name: str) -> Callable:
    try:
        module = import_module(modulepath)
    except Exception as e:
        raise Exception(f"Could not import module path at {modulepath}. e: {e}")
    try:
        return getattr(module, func_name)
    except AttributeError:
        raise Exception(f"Could not find function {func_name} on module {modulepath}")


def execute_no_catch(logic_modulepath: str, func_name: str, *args, **kwargs):
    logic = load_generated_logic_from_modulepath(logic_modulepath, func_name=func_name)
    return logic(*args, **kwargs)


def execute_from_typed_attributes(
    logic_modulepath: str, func_name: str, args: List[Any], kwargs: Dict[str, Any]
):
    logic = load_generated_logic_from_modulepath(logic_modulepath, func_name)
    return execute_logic(logic, *args, **kwargs)


def execute_from_callable(callable: Callable, *args, **kwargs):
    logic = load_generated_logic_from_callable(callable)
    return execute_logic(logic, *args, **kwargs)


def execute_logic(logic: Callable, *args, **kwargs) -> Any:
    try:
        result = logic(*args, **kwargs)
        return result
    except Exception as e:
        if isinstance(e, GeneratedException):
            raise e.exception
        else:
            print("--UNSAFE EXCEPTION-- not wrapped in GeneratedException")
            raise e
