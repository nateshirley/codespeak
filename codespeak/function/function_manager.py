from typing import Callable


class FunctionManager:
    """Context management class that provides syntax to access the inferred function instance from inside its body"""

    func: Callable | None

    def manage_for(self, func):
        self.func = func
        return self  # return self to enable use as a resources manager

    def get_function(self) -> Callable:
        if not self.func:
            raise Exception(
                "No function found. Can only be used inside a codespeak function."
            )
        return self.func

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.func = None  # reset func_name when exiting the resources
