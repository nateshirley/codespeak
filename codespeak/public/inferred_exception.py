import inspect
from typing import Dict


class InferredException(Exception):
    """Custom exception class used in code inference to explicitly mark exceptions that are intentionally thrown by the generated code."""

    def __init__(self, exception: Exception):
        self.exception = exception
        super().__init__(str(exception))


class InferredExceptionHelpers:
    @staticmethod
    def annotate() -> Dict:
        qualname = "InferredException"
        module = "codespeak"
        source_code = inspect.getsource(InferredException)
        return {
            f"{module}.{qualname}": {
                "module": module,
                "qualname": qualname,
                "source_code": source_code,
            }
        }

    @staticmethod
    def import_text() -> str:
        return f"from codespeak import InferredException\n"
