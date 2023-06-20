from pydantic import BaseModel
from typing import Dict, Literal
from codespeak._definitions.definition import Definition


class Generic(Definition):
    type: Literal["Generic"] = "Generic"

    def annotate(self) -> Dict:
        return {
            f"{self.import_path()}": {
                "module": self.module,
                "qualname": self.qualname,
            }
        }

    def custom_types(self) -> Dict:
        return self.annotate()

    def flatten(self):
        return self
