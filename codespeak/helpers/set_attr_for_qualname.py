from typing import Any


def set_attr_for_qualname(obj: Any, qualname: str, value: Any):
    try:
        attrs = qualname.split(".")
        for attr in attrs[:-1]:
            obj = getattr(obj, attr)
        setattr(obj, attrs[-1], value)
    except AttributeError:
        raise Exception(
            f"Trying to set attr for {qualname} that doesn't exist on object {obj}"
        )
