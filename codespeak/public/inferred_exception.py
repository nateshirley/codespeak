import inspect
from typing import Dict


class InferredException(Exception):
    """Custom exception class used in code inference to explicitly mark exceptions that are intentionally thrown by the generated code."""

    def __init__(self, exception: Exception):
        self.exception = exception
        super().__init__(str(exception))


def annotate() -> Dict:
    qualname = InferredException.__qualname__
    module = InferredException.__module__
    source_code = inspect.getsource(InferredException)
    return {
        f"{module}.{qualname}": {
            "module": module,
            "qualname": qualname,
            "source_code": source_code,
        }
    }
