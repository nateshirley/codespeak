import types
from typing import Any, Callable, Dict, Tuple, get_origin
import builtins
from typing import Any, Union, get_args, get_origin, List, get_type_hints
import inspect
from codespeak._definitions.free_modules import FREE_MODULES
import os
import types
from codespeak._definitions.definition import Definition
from codespeak._definitions.types.generic import Generic
from codespeak._definitions.types.local_class import LocalClass
from codespeak._definitions.types.local_class_as_self import LocalClassAsSelf
from codespeak._definitions.types.installed_class import InstalledClass
from codespeak._definitions.types.builtin import Builtin
from codespeak._definitions.types.none import NoneDef
from codespeak._definitions.types.typing_type import TypingType
from codespeak._definitions.types.union_type import UnionType
import pkg_resources


def to_union_type(definition: Any) -> UnionType:
    args = get_args(definition)
    _types = []
    for _type in args:
        _types.append(from_any(_type))
    return UnionType(args=_types, _def=definition, origin=get_origin(definition))


def is_builtin_type(module_name: str):
    return module_name == "builtins"


def is_installed_package_type(module_name: str):
    if module_name in FREE_MODULES:
        return True
    else:
        installed_packages = [pkg.key for pkg in pkg_resources.working_set]
        return module_name.split(".")[0] in installed_packages


def is_local_class(definition: type) -> bool:
    module = inspect.getmodule(definition)
    if not module:
        raise Exception(
            "no module found for type, expected one, possibly undefined behavior: ",
            definition,
        )
    is_installed = is_installed_package_type(module.__name__)
    if is_installed:
        return False
    is_builtin = is_builtin_type(module.__name__)
    if is_builtin:
        return False
    # optimistically assumes that if it's not installed and not builtin, it's local
    return True


def to_typing_type(definition: Any) -> TypingType:
    args = get_args(definition)
    defs = []
    for _type in args:
        defs.append(from_any(_type))

    return TypingType(
        qualname=definition.__qualname__,
        module=definition.__module__,
        origin=get_origin(definition),
        args=defs,
        _def=definition,
    )


def may_have_args(qualname: str):
    builtins_with_args = {
        "list": True,
        "dict": True,
        "set": True,
        "tuple": True,
    }
    if qualname in builtins_with_args:
        return True


def from_any_list(_list: List[Any]) -> List[Definition]:
    return [from_any(_def) for _def in _list]


def from_any_tuple(tup: Tuple[Any]) -> List[Definition]:
    return [from_any(_def) for _def in tup]


def from_any(
    definition: Any,
) -> Definition:
    if definition is None:
        return NoneDef()
    if not hasattr(definition, "__module__"):
        raise Exception("expected a module on the type")
    if get_origin(definition) is types.UnionType:
        return to_union_type(definition)
    # types.UnionType has no qualname attr
    if not hasattr(definition, "__qualname__"):
        raise Exception("expected a name on the type")
    elif definition.__module__ == "typing":
        return to_typing_type(definition)
    elif is_builtin_type(module_name=definition.__module__):
        if may_have_args(definition.__qualname__):
            return to_typing_type(definition)
        else:
            return Builtin(
                module=definition.__module__,
                qualname=definition.__qualname__,
                _def=definition,
            )
    elif inspect.isclass(definition):
        if is_local_class(definition):
            return LocalClass(
                qualname=definition.__qualname__,
                module=definition.__module__,
                source_code=inspect.getsource(definition),
                bases=from_any_tuple(definition.__bases__),
                type_hints=collect_type_hints(definition),
                _def=definition,
            )
        else:
            return InstalledClass(
                qualname=definition.__qualname__,
                module=definition.__module__,
                _def=definition,
            )
    elif inspect.isfunction(definition):
        # TODO
        # methods = [attr for attr, value in MyClass.__dict__.items() if inspect.isfunction(value)]
        # print("caught instance of callable", definition)
        raise Exception(
            "no support for functions right now, can't cast definition: ",
            definition,
        )
    else:
        raise Exception("unsure how to handle definition: ", definition)


def from_self_class_obj(self_class_obj: Any, method_name: str) -> Definition:
    _def = from_any(self_class_obj)
    if _def.type == "LocalClass":
        return LocalClassAsSelf(
            qualname=_def.qualname,
            module=_def.module,
            source_code=_def.source_code,
            bases=_def.bases,
            type_hints=_def.type_hints,
            _def=_def,
            method_name=method_name,
        )
    else:
        return _def


# technically get_type_hints can work on some installed types but we aren't using it for that atm
def collect_type_hints(_class: type) -> Dict[str, Definition]:
    hints = get_type_hints(_class, include_extras=False)
    definitions = {}
    for name, _def in hints.items():
        typed_def = from_any(_def)
        definitions[name] = typed_def
    return definitions


# so get_type_hints works for reg classes as long as the instance vars are an_assigned. so it would bundle class vars and instance vars together
