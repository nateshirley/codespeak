import inspect
from typing import Any, Callable, Dict, List, OrderedDict, Tuple
from pydantic import BaseModel


class Argument(BaseModel):
    name: str
    value: Any


def gather_arguments(
    func: Callable, args: Tuple[Any], kwargs: Dict[str, Any]
) -> List[Argument]:
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    lst = []
    for name, value in bound.arguments.items():
        lst.append(Argument(name=name, value=value))
    return lst
