import inspect
from typing import Dict


# Custom exception class used in code inference to explicitly mark exceptions that are intentionally thrown by the generated code.
class InferredException(Exception):
    def __init__(self, msg: str | None = None, exception: Exception | None = None):
        if msg is not None:
            self.exception = Exception(msg)
            super().__init__(msg)
        elif exception is not None:
            self.exception = exception
            super().__init__(str(exception))
        else:
            raise Exception(
                "InferredException must be instantiated with msg or exception"
            )


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
