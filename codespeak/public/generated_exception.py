import inspect
from typing import Dict


class GeneratedException(Exception):
    """Custom exception class used in codegen to explicitly mark intentional exceptions."""

    def __init__(self, exception: Exception):
        self.exception = exception
        super().__init__(str(exception))


def annotate() -> Dict:
    qualname = GeneratedException.__qualname__
    module = GeneratedException.__module__
    source_code = inspect.getsource(GeneratedException)
    return {
        f"{module}.{qualname}": {
            "module": module,
            "qualname": qualname,
            "source_code": source_code,
        }
    }
