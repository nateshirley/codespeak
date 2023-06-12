from typing import Dict, Literal
from codespeak.definitions.definition import Definition


class CustomTypeReference(Definition):
    type: Literal["ComplexTypeReference"] = "ComplexTypeReference"

    def ref(self):
        return "$ref: complex_types/" + self.module + "." + self.qualname

    def annotate(self) -> Dict:
        return {
            f"{self.import_path()}": {
                "module": self.module,
                "qualname": self.qualname,
            }
        }

    def custom_types(self) -> Dict:
        return self.annotate()

    def annotate_in_local_class(self) -> str:
        return self.ref()

    def flatten(self):
        return self
