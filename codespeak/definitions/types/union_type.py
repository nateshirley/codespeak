from typing import Any, Callable, Dict, List
from typing import Literal

from codespeak.definitions.types.typing_type import TypingType
from codespeak.definitions.definition import Definition


class UnionType(TypingType):
    qualname: str = "UnionType"
    module: str = "types"
    args: List[Definition]
    type: Literal["UnionType"] = "UnionType"

    def annotate(self) -> Dict:
        return {
            f"{self.import_path()}": {
                "qualname": self.qualname,
                "module": self.module,
                "args": [arg.annotate() for arg in self.args] if self.args else None,
            }
        }
