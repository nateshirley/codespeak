# need to give it import paths

import inspect
from typing import Any, Callable, Dict, List
from pydantic import BaseModel
import pytest
from codespeak.function.function_declaration import FunctionDeclaration
from codespeak.inference.codespeak_service import CodespeakService
from codespeak.function.function_file_service import FunctionFileService
from codespeak.function.function_digest import FunctionDigest
from codespeak.public.inferred_exception import InferredException
from codespeak.executor import execute_unchecked
from codespeak.inference.results_collector import TestRunner
from codespeak.test_function import TestFunction
from codespeak.settings import _settings


class ExecutionResponse(BaseModel):
    result: Any
    did_regenerate_source: bool = False


class TestResponse(BaseModel):
    did_regenerate_source: bool


class GenerationResponse(BaseModel):
    execution_result: Any | None = None


class InferenceEngine(BaseModel):
    # not modified internally
    function_declaration: FunctionDeclaration
    file_service: FunctionFileService
    digest: FunctionDigest
    codespeak_service: CodespeakService
    should_execute: bool
    args: List[Any]
    kwargs: Dict[str, Any]
    test_functions: List[TestFunction]
    latest_source_code: str = ""

    def make_inference(self) -> GenerationResponse:
        self.latest_source_code = self.codespeak_service.generate_source_code()
        return self._validate_new_source_code()

    @property
    def require_execution(self) -> bool:
        return self.should_execute

    @property
    def has_tests(self) -> bool:
        return len(self.test_functions) > 0

    # this should always be called directly after new source code is generated and stored in self.latest_source_code
    def _validate_new_source_code(self) -> GenerationResponse:
        execution_result = None
        self.file_service.write_logic(self.latest_source_code)
        self.file_service.write_metadata(
            source_code=self.function_declaration.source_code,
            require_execution=self.require_execution,
            did_execute=False,
            has_tests=self.has_tests,
            did_pass_tests=False,
            digest=self.digest,
        )
        if self.should_execute:
            execution_response = self._try_align_with_execution()
            execution_result = execution_response.result
            if execution_response.did_regenerate_source:
                return self._validate_new_source_code()
        if self.has_tests:
            test_response = self._try_align_with_tests()
            if test_response.did_regenerate_source:
                return self._validate_new_source_code()
        return GenerationResponse(execution_result=execution_result)

    def _try_align_with_execution(self) -> ExecutionResponse:
        try:
            result = execute_unchecked(
                self.file_service.generated_module_qualname,
                self.file_service.generated_entrypoint,
                *self.args,
                **self.kwargs,
            )
            self._write_execution_status(did_execute=True)
            return ExecutionResponse(result=result, did_regenerate_source=False)
        except Exception as e:
            if isinstance(e, InferredException):
                # if the generated code properly raises a InferredException, we don't want to regenerate it the next time it's called
                self._write_execution_status(
                    did_execute=True,
                )
                raise e
            else:
                self.latest_source_code = (
                    self.codespeak_service.try_regenerate_from_execution_failure(
                        exception=e
                    )
                )
                return ExecutionResponse(result=None, did_regenerate_source=True)

    def _try_align_with_tests(self) -> TestResponse:
        if not self.has_tests:
            raise Exception("trying to test without a test func")
        total_duration = 0
        _settings.set_is_testing(
            True, logic_at_filepath=self.file_service.codegen_logic_filepath
        )
        for test_function in self.test_functions:
            test_result = TestRunner.run_test_func(
                test_file=test_function.file,
                test_func_qualname=test_function.qualname,
            )
            total_duration += test_result.total_duration
            if test_result.exitcode == pytest.ExitCode.OK:
                continue
            elif test_result.exitcode == pytest.ExitCode.TESTS_FAILED:
                _settings.set_is_testing(False)
                self._write_test_status(has_tests=True, did_pass_tests=False)
                print("Some tests failed.")
                if len(test_result.crash_reports) == 0:
                    raise Exception("no crash reports but tests failed")
                self.latest_source_code = (
                    self.codespeak_service.try_regenerate_from_test_failure(
                        test_source_code=test_function.source_code,
                        crash_report=test_result.crash_reports[0],
                    )
                )
                return TestResponse(did_regenerate_source=True)
            else:
                raise exception_for_exitcode(test_result.exitcode)
        print(f"All tests passed successfully in {total_duration}s")
        _settings.set_is_testing(False)
        self._write_test_status(has_tests=True, did_pass_tests=True)
        return TestResponse(did_regenerate_source=False)

    def _write_execution_status(self, did_execute: bool) -> None:
        prev_metadata = self.file_service.load_metadata()
        if prev_metadata:
            has_tests = prev_metadata.has_tests
            did_pass_tests = prev_metadata.did_pass_tests
        else:
            has_tests = self.has_tests
            did_pass_tests = False
        self.file_service.write_metadata(
            source_code=self.function_declaration.source_code,
            require_execution=self.require_execution,
            did_execute=did_execute,
            has_tests=has_tests,
            did_pass_tests=did_pass_tests,
            digest=self.digest,
        )

    def _write_test_status(self, has_tests: bool, did_pass_tests: bool) -> None:
        prev_metadata = self.file_service.load_metadata()
        if prev_metadata:
            did_execute = prev_metadata.did_execute
            require_execution = prev_metadata.require_execution
        else:
            did_execute = False
            require_execution = self.should_execute
        self.file_service.write_metadata(
            source_code=self.function_declaration.source_code,
            require_execution=require_execution,
            did_execute=did_execute,
            has_tests=has_tests,
            did_pass_tests=did_pass_tests,
            digest=self.digest,
        )


def exception_for_exitcode(exitcode: int) -> Exception:
    msg = ""
    if exitcode == pytest.ExitCode.INTERRUPTED:
        msg = "Test execution interrupted by the user."
    elif exitcode == pytest.ExitCode.INTERNAL_ERROR:
        msg = "Internal error or exception occurred during test execution."
    elif exitcode == pytest.ExitCode.USAGE_ERROR:
        msg = "Usage error in pytest command line."
    elif exitcode == pytest.ExitCode.NO_TESTS_COLLECTED:
        msg = "No tests were collected or executed."
    else:
        msg = f"Unknown exit code: {exitcode}"
    raise Exception(msg)
