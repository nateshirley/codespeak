from typing import Any


def get_attr_from_qualname(obj: Any, qualname: str) -> Any:
    try:
        attrs = qualname.split(".")
        for attr in attrs:
            obj = getattr(obj, attr)
        return obj
    except AttributeError:
        raise Exception(
            f"Trying to execute function {qualname} that doesn't exist on object {obj}"
        )
