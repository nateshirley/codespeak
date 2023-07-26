import types
from typing import Any, Callable, Dict, Tuple, get_origin
from typing import Any, Union, get_args, get_origin, List, get_type_hints
import inspect
from codespeak.type_definitions.free_modules import FREE_MODULES
import os
import types
from codespeak.type_definitions.type_definition import TypeDefinition
from codespeak.type_definitions.types.local_class import LocalClass
from codespeak.helpers.derive_module_qualname_for_object import (
    derive_module_qualname_for_object,
)
from codespeak.type_definitions.types.installed_class import InstalledClass
from codespeak.type_definitions.types.builtin import Builtin
from codespeak.type_definitions.types.none import NoneDef
from codespeak.type_definitions.types.typing_type import TypingType
from codespeak.type_definitions.types.union_type import UnionType
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
    if is_installed_package_type(module.__name__):
        return False
    if is_builtin_type(module.__name__):
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


def from_any_list(_list: List[Any]) -> List[TypeDefinition]:
    return [from_any(_def) for _def in _list]


def from_any_tuple(tup: Tuple[Any]) -> List[TypeDefinition]:
    return [from_any(_def) for _def in tup]


def from_any(
    definition: Any,
) -> TypeDefinition:
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
                module=derive_module_qualname_for_object(
                    definition
                ),  # definition.__module__,
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


# technically get_type_hints can work on some installed types but we aren't using it for that atm
def collect_type_hints(_class: type) -> Dict[str, TypeDefinition]:
    hints = get_type_hints(_class, include_extras=False)
    definitions = {}
    for name, _def in hints.items():
        typed_def = from_any(_def)
        definitions[name] = typed_def
    return definitions
