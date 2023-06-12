import inspect
from typing import Any, Callable, Dict, List
from codespeak.helpers.gather_arguments import gather_arguments


def self_type_if_exists(
    func: Callable, args: List[Any], kwargs: Dict[str, Any]
) -> Any | None:
    bounded_args = gather_arguments(func, args, kwargs)
    for index, arg in enumerate(bounded_args):
        if index == 0:
            _type = type(arg.value)
            if arg.name == "self" and inspect.isclass(_type):
                return _type
        else:
            break
    return None
