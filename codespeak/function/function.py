import inspect
import json
from typing import Any, Callable, Dict, List, ClassVar, Tuple
from codespeak import executor
from codespeak.function.function_declaration import FunctionDeclaration
from codespeak.helpers.self_type import self_type_if_exists
from codespeak.inference.inference_engine import InferenceEngine, TestFunction
from codespeak.inference.codespeak_service import CodespeakService
from codespeak.frame import Frame
from codespeak.function.function_file_service import FunctionFileService
from codespeak.function.function_digest import FunctionDigest
from codespeak.settings import _settings
from codespeak.function.function_metadata import FunctionMetadata
from codespeak.function.helper_types.make_inference_response import (
    MakeInferenceResponse,
)
from codespeak.function.function_manager import FunctionManager
from codespeak.function.function_attributes import FunctionAttributes
from codespeak.clean import clean


class Function:
    func: Callable
    _digest: FunctionDigest

    def __init__(self, func: Callable) -> None:
        if not hasattr(func, FunctionAttributes.frame):
            raise Exception(
                "No frame found. Make sure this is an inferred function—it should use codespeak's @infer decorator"
            )
        self.func = func
        self._digest = FunctionDigest.from_inputs(
            declaration_source_code=self.declaration.source_code,
            custom_types=self.frame.custom_types(),
        )

    @property
    def logic(self) -> Callable:
        if not self._file_service.does_metadata_exist():
            raise Exception("No logic found. Execute the function to generate it.")
        return executor.load_generated_logic_from_module_qualname(
            module_qualname=self._file_service.generated_module_qualname,
            func_name=self._file_service.generated_entrypoint,
        )

    @property
    def declaration(self) -> FunctionDeclaration:
        return getattr(self.func, FunctionAttributes.declaration)

    @property
    def frame(self) -> Frame:
        return Frame.for_function(self.func)

    @property
    def _file_service(self) -> FunctionFileService:
        return getattr(self.func, FunctionAttributes.file_service)

    def execute_latest_inference(self, *args: Any, **kwargs: Any) -> Any:
        """Executes the latest inferred logic without checking if any exists"""
        if _settings.get_environment() == _settings.Environment.PROD:
            raise Exception(
                "unsafe_execute is not available in production, call the inferred function directly"
            )
        return self.logic(*args, **kwargs)

    def make_inference(
        self,
        args: List[Any] | None = None,
        kwargs: Dict[str, Any] | None = None,
        should_execute: bool = False,
    ) -> Any:
        """Explicitly make a new inference for a function. If using a method, must pass args to attach self type."""
        args = args or []
        kwargs = kwargs or {}
        self._try_add_self_to_frame(tuple(args), kwargs)
        return self._make_inference(
            args=args,
            kwargs=kwargs,
            should_execute=should_execute,
        )

    def _make_inference(
        self,
        args: List[Any],
        kwargs: Dict[str, Any],
        should_execute: bool,
    ) -> MakeInferenceResponse:
        if _settings.get_environment() == _settings.Environment.PROD:
            raise Exception("Make is not available in production.")
        inference_engine = InferenceEngine(
            function_declaration=self.declaration,
            digest=self._digest,
            codespeak_service=CodespeakService.with_defaults(
                function_declaration=self.declaration, frame=self.frame
            ),
            file_service=self._file_service,
            should_execute=should_execute,
            test_functions=self.frame.tests.test_functions,
            args=list(args),
            kwargs=kwargs,
        )
        inference = inference_engine.make_inference()
        logic = executor.load_generated_logic_from_module_qualname(
            module_qualname=self._file_service.generated_module_qualname,
            func_name=self._file_service.generated_entrypoint,
        )
        setattr(self.func, FunctionAttributes.logic, logic)
        return MakeInferenceResponse(
            execution_result=inference.execution_result,
            source_code=inference_engine.latest_source_code,
        )

    def inference_inputs(self) -> str:
        inputs = {
            "incomplete_file": self.declaration.as_incomplete_file(),
            "custom_types": self.frame.custom_types(),
        }
        return json.dumps(inputs, indent=4)

    def _try_add_self_to_frame(self, args: Tuple[Any], kwargs: Dict[str, Any]):
        self_type = self_type_if_exists(self.func, args, kwargs)
        if self_type:
            self.declaration.try_add_self_definition(self_type)

    def should_infer_new_source_code(self) -> bool:
        return _should_infer_new_source_code(self._file_service, self._digest)

    def _infer(self, args: Tuple[Any], kwargs: Dict[str, Any]):
        if self.should_infer_new_source_code():
            inference = self.make_inference(
                args=list(args),
                kwargs=kwargs,
                should_execute=True,
            )
            if _settings.should_auto_clean():
                clean(_settings.abspath_to_codegen_dir())
            return inference.execution_result
        else:
            return self.execute_latest_inference(*args, **kwargs)

    @staticmethod
    def from_function_object(func: Callable[..., Any]) -> "Function":
        """get classified Function object for an inferred function"""
        return Function(func=func)


def _should_infer_new_source_code(
    file_service: FunctionFileService,
    active_digest: FunctionDigest,
    require_deep_hash_match: bool = False,
) -> bool:
    if not file_service.does_metadata_exist():
        return True
    try:
        existing_metadata = file_service.load_metadata()
    except Exception as e:
        print("unable to load prev metadata")
        return True
    if existing_metadata is None:
        raise Exception("Metadata should exist if the file exists")
    if existing_metadata.require_execution and not existing_metadata.did_execute:
        return True
    if existing_metadata.has_tests and not existing_metadata.did_pass_tests:
        return True
    return _has_function_changed(
        existing_metadata, active_digest, require_deep_hash_match
    )


def _has_function_changed(
    existing_metadata: FunctionMetadata,
    active_digest: FunctionDigest,
    require_deep_hash_match: bool = False,
):
    if require_deep_hash_match:
        return existing_metadata.declaration_digest.deep_hash != active_digest.deep_hash
    else:
        return (
            existing_metadata.declaration_digest.source_hash
            != active_digest.source_hash
        )
