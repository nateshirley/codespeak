import inspect
from typing import Dict, Literal

from codespeak._definitions.definition import Definition


class Builtin(Definition):
    type: Literal["Builtin"] = "Builtin"

    def annotate(self) -> Dict:
        return {
            self.qualname: {
                "module": self.module,
                "qualname": self.qualname,
            }
        }

    def custom_types(self) -> Dict:
        return {}

    def annotate_in_local_class(self) -> str:
        return self.qualname
