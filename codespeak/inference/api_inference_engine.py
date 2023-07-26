import asyncio
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel
from codespeak.executor import execute_unchecked
from codespeak.function.function_digest import FunctionDigest
from codespeak.function.function_file_service import FunctionFileService

from codespeak.function.function_lite import FunctionLite
from codespeak.inference.codespeak_service import CodespeakService


class MakeInferenceResponse(BaseModel):
    execution_result: Any
    source_code: str


class ExecutionResult(BaseModel):
    result: Any


# this is going to be the thing that talks to the api and writes results for it
# this will write results and test, service will just make calls to codespeak api
class APIInferenceEngine(BaseModel):
    api: str
    function_lite: FunctionLite
    codespeak_service: CodespeakService
    file_service: FunctionFileService
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    latest_source_code: str = ""
    digest: FunctionDigest

    def make_inference(self) -> MakeInferenceResponse:
        source_code = asyncio.run(CodespeakService.make_inference(self.function_lite))
        self.latest_source_code = source_code
        # self.write_inference()
        # source_code = self.codespeak_service.generate_source_code()
        # execution_result = self.execute_inference()
        return MakeInferenceResponse(
            execution_result=None,  # execution_result.result,
            source_code=self.latest_source_code,
        )

    # i'll have the option to reload it and execute it with a load, or just execute the source with exec
    # i'd probably rather reload it so I know it's working in its natural habitat, but that doesn't matter right now

    def write_inference(self) -> None:
        self.file_service.write_logic(self.latest_source_code)
        self.file_service.write_metadata(
            source_code=self.function_lite.declaration.source_code,
            require_execution=True,
            did_execute=False,  # marking all as false for now so I can easily re-run
            has_tests=False,
            did_pass_tests=False,
            digest=self.digest,
        )

    def execute_inference(self) -> ExecutionResult:
        try:
            result = execute_unchecked(
                self.file_service.generated_module_qualname,
                self.file_service.generated_entrypoint,
                self.codespeak_service.already_tried_execution,
                *self.args,
                **self.kwargs,
            )
            return ExecutionResult(result=result)
        except Exception as e:
            print("failed to execute")
            raise e
