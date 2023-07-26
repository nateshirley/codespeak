import inspect
import textwrap
from typing import Any, Callable, Dict, List, Tuple
from codespeak.decorate.writable_transform import replace_function
from codespeak.function.function import Function
from codespeak.inference.api_inference_engine import MakeInferenceResponse

sample_inference = textwrap.dedent(
    """
    def get_company(company_id: int):
        path = "/companies/{id_or_urn}"
        path_params = {"id_or_urn": str(company_id)}
        return codespeak.get("harmonic", path, path_params=path_params)
    """
).strip("\n")


class WritableFunction(Function):
    def write(
        self, writable_func: Callable, args: Tuple[Any], kwargs: Dict[str, Any]
    ) -> Any:
        function_file = inspect.getsourcefile(writable_func)
        if function_file is None:
            raise ValueError("Function must be defined in a file")
        print("function file:", function_file)
        original_source = self.declaration.source_code
        decorator = original_source.split("\n")[0]
        # source = align(
        #     f"""
        #     def sample(s: str) -> str:
        #         return s + "!"
        #     """
        # )
        # inference = MakeInferenceResponse(
        #     source_code=sample_inference, execution_result=None
        # )
        inference = self._make_api_inference(args, kwargs)
        inference.source_code = decorator + "\n" + inference.source_code
        # print("SOURCE:\n")
        # print(inference.source_code)
        # replace_function(
        #     function_file, writable_func.__qualname__, inference.source_code
        # )
        return None  # inference.execution_result


def align(s: str) -> str:
    return textwrap.dedent(s).strip("\n")
