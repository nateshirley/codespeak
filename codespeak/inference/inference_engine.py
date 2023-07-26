import asyncio
import inspect
from typing import Any, Callable, Dict, List, Tuple
from pydantic import BaseModel
from codespeak.function.function_lite import FunctionLite
from codespeak.inference import codespeak_service
from codespeak.helpers.extract_delimited_python_code_from_string import (
    extract_delimited_python_code_from_string,
)


class InferenceEngine(BaseModel):
    api_identifier: str
    function_lite: FunctionLite

    def make_inference(self) -> str:
        inference = asyncio.run(
            codespeak_service.make_inference(self.function_lite, self.api_identifier)
        )
        inference = extract_delimited_python_code_from_string(inference)
        original_source = self.function_lite.declaration.source_code
        decorator = original_source.split("\n")[0]
        source_code = decorator + "\n" + inference
        # print("SOURCE:\n")
        # print(source_code)
        return source_code

    # i'll have the option to reload it and execute it with a load, or just execute the source with exec
    # i'd probably rather reload it so I know it's working in its natural habitat, but that doesn't matter right now
