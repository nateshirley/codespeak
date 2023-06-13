# need to give it import paths

import inspect
from typing import Any, Callable, Dict, List
from pydantic import BaseModel
import pytest
from codespeak.core.codespeak_service import CodespeakService
from codespeak.generated_exception import GeneratedException
from codespeak.core.executor import execute_no_catch
from codespeak.core.results_collector import TestRunner
from codespeak.declaration.codespeak_declaration import CodespeakDeclaration


class ExecutionResponse(BaseModel):
    result: Any
    did_regenerate_source: bool = False


class TestResponse(BaseModel):
    did_regenerate_source: bool


class GenerationResponse(BaseModel):
    execution_result: Any | None = None


class TestFunc(BaseModel):
    file: str
    qualname: str
    source_code: str

    @staticmethod
    def from_callable(test_func: Callable) -> "TestFunc":
        source_code = inspect.getsource(test_func)
        file = inspect.getfile(test_func)
        return TestFunc(
            file=file,
            qualname=test_func.__qualname__,
            source_code=source_code,
        )


class CodeGenerator(BaseModel):
    # not modified internally
    declaration: CodespeakDeclaration
    service: CodespeakService
    should_execute: bool
    args: List[Any]
    kwargs: Dict[str, Any]
    test_func: TestFunc | None
    latest_source_code: str = ""

    def generate(self) -> GenerationResponse:
        self.latest_source_code = self.service.generate_source_code()
        return self._validate_new_source_code()

    @property
    def require_execution(self) -> bool:
        return self.should_execute

    # this should always be called directly after new source code is generated and stored in self.latest_source_code
    def _validate_new_source_code(self) -> GenerationResponse:
        execution_result = None
        self.declaration.file_service.write_logic(self.latest_source_code)
        self.declaration.file_service.write_metadata(
            source_code=self.declaration.source_code,
            require_execution=self.require_execution,
            did_execute=False,
            has_tests=(not self.test_func is None),
            did_pass_tests=False,
            digest=self.declaration.digest,
        )
        if self.should_execute:
            execution_response = self._try_align_with_execution()
            execution_result = execution_response.result
            if execution_response.did_regenerate_source:
                return self._validate_new_source_code()
        if self.test_func:
            test_response = self._try_align_with_tests()
            if test_response.did_regenerate_source:
                return self._validate_new_source_code()
        return GenerationResponse(execution_result=execution_result)

    def _try_align_with_execution(self) -> ExecutionResponse:
        try:
            result = execute_no_catch(
                self.declaration.file_service.logic_modulepath,
                self.declaration.name,
                *self.args,
                **self.kwargs,
            )
            self._write_execution_status(did_execute=True)
            return ExecutionResponse(result=result, did_regenerate_source=False)
        except Exception as e:
            if isinstance(e, GeneratedException):
                # if the generated code properly raises a GeneratedException, we don't want to regenerate it the next time it's called
                self._write_execution_status(
                    did_execute=True,
                )
                raise e.exception
            else:
                self.latest_source_code = (
                    self.service.try_regenerate_from_execution_failure(exception=e)
                )
                return ExecutionResponse(result=None, did_regenerate_source=True)

    def _try_align_with_tests(self) -> TestResponse:
        if not self.test_func:
            raise Exception("trying to test without a test func")
        self._write_test_status(has_tests=False, did_pass_tests=False)
        test_result = TestRunner.run_test_func(
            test_file=self.test_func.file,
            test_func_qualname=self.test_func.qualname,
        )
        did_pass_tests = test_result.exitcode == pytest.ExitCode.OK
        self._write_test_status(has_tests=False, did_pass_tests=did_pass_tests)
        if test_result.exitcode == pytest.ExitCode.OK:
            print(f"All tests passed successfully in {test_result.total_duration}s")
            return TestResponse(did_regenerate_source=False)
        elif test_result.exitcode == pytest.ExitCode.TESTS_FAILED:
            print("Some tests failed.")
            if len(test_result.crash_reports) == 0:
                raise Exception("no crash reports but tests failed")
            self.latest_source_code = self.service.try_regenerate_from_test_failure(
                test_source_code=self.test_func.source_code,
                crash_report=test_result.crash_reports[0],
            )
            return TestResponse(did_regenerate_source=True)
        else:
            raise exception_for_exitcode(test_result.exitcode)

    def _write_execution_status(self, did_execute: bool) -> None:
        prev_metadata = self.declaration.file_service.load_metadata()
        if prev_metadata:
            has_tests = prev_metadata.has_tests
            did_pass_tests = prev_metadata.did_pass_tests
        else:
            has_tests = not self.test_func is None
            did_pass_tests = False
        self.declaration.file_service.write_metadata(
            source_code=self.declaration.source_code,
            require_execution=self.require_execution,
            did_execute=did_execute,
            has_tests=has_tests,
            did_pass_tests=did_pass_tests,
            digest=self.declaration.digest,
        )

    def _write_test_status(self, has_tests: bool, did_pass_tests: bool) -> None:
        prev_metadata = self.declaration.file_service.load_metadata()
        if prev_metadata:
            did_execute = prev_metadata.did_execute
            require_execution = prev_metadata.require_execution
        else:
            did_execute = False
            require_execution = self.should_execute
        self.declaration.file_service.write_metadata(
            source_code=self.declaration.source_code,
            require_execution=require_execution,
            did_execute=did_execute,
            has_tests=has_tests,
            did_pass_tests=did_pass_tests,
            digest=self.declaration.digest,
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
