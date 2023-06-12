from typing import Any, Callable, Dict
from typing import Literal
from codespeak.definitions.definition import Definition


class InstalledClass(Definition):
    type: Literal["InstalledClass"] = "InstalledClass"
    origin: str = "installed"

    def annotate(self) -> Dict:
        return {
            f"{self.import_path()}": {
                "origin": "installed",
                "module": self.module,
                "qualname": self.qualname,
            }
        }

    def custom_types(self) -> Dict:
        return self.annotate()

    def annotate_in_local_class(self) -> Dict | str:
        return self.module + "." + self.qualname
