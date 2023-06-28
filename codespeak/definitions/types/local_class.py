from typing import Any, Callable, Dict, List, Tuple

from typing import Literal
from codespeak.definitions.definition import Definition
from codespeak.definitions.types.custom_type_reference import CustomTypeReference


class LocalClass(Definition):
    type: Literal["LocalClass"] = "LocalClass"
    source_code: str
    bases: List[Definition]
    type_hints: Dict[str, Definition]
    origin: str = "local"
    _def: Any

    def reference_nested_custom_types(self) -> List[Definition]:
        referenced = []
        for type_name, _def in self.type_hints.items():
            if _def.type == "LocalClass":
                self.type_hints[type_name] = CustomTypeReference(
                    qualname=_def.qualname, module=_def.module, _def=_def
                )
                referenced.append(_def)
            elif _def.type == "InstalledClass":
                self.type_hints[type_name] = CustomTypeReference(
                    qualname=_def.qualname, module=_def.module, _def=_def
                )
                referenced.append(_def)
        for i, _def in enumerate(self.bases):
            if _def.type == "LocalClass":
                self.bases[i] = CustomTypeReference(
                    qualname=_def.qualname, module=_def.module, _def=_def
                )
                referenced.append(_def)
            elif _def.type == "InstalledClass":
                self.bases[i] = CustomTypeReference(
                    qualname=_def.qualname, module=_def.module, _def=_def
                )
                referenced.append(_def)
        return referenced

    def collect_referenced_types(self) -> List[Definition]:
        referenced = self.reference_nested_custom_types()
        for _, _def in self.type_hints.items():
            referenced.extend(_def.reference_nested_custom_types())
        for _def in self.bases:
            referenced.extend(_def.reference_nested_custom_types())
        return referenced

    def flatten(self) -> List[Definition]:
        return [self]

    def custom_types(self) -> Dict:
        types_replaced = self.collect_referenced_types()
        annotxn = self.annotate()
        for _type in types_replaced:
            annotxn.update(_type.custom_types())
        return annotxn

    def annotate(self) -> Dict:
        return {
            f"{self.import_path()}": {
                "origin": "local",
                "qualname": self.qualname,
                "module": self.module,
                "source_code": self.source_code,
                "bases": [base.annotate_in_local_class() for base in self.bases],
                "type_hints": {
                    key: value.annotate_in_local_class()
                    for key, value in self.type_hints.items()
                },
            }
        }
