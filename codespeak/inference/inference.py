import inspect
from typing import Any, Callable, Dict, List, ClassVar, Tuple
from codespeak._core import executor
from codespeak._core.code_generator import CodeGenerator, TestFunc
from codespeak._core.codespeak_service import CodespeakService
from codespeak._declaration.codespeak_declaration import CodespeakDeclaration
from codespeak._declaration.declaration_file_service import DeclarationFileService
from codespeak._helpers.self_type import self_type_if_exists
from codespeak._metadata.digest import DeclarationDigest
from codespeak._settings import _settings
from codespeak.inference.inference_make_response import InferenceMakeResponse
from codespeak.inference.inference_manager import InferenceManager
from codespeak.inference.inference_attributes import InferenceAttributes
from codespeak.inference._inference_attributes import _InferenceAttributes
from codespeak.inference._resources import Resources
from codespeak.inference._tests import Tests
from codespeak.inference import _accessors


class Inference:
    func: Callable
    manager: InferenceManager = InferenceManager()

    def __init__(self, func: Callable) -> None:
        if not hasattr(func, InferenceAttributes.resources):
            raise Exception(
                "No resources found. Make sure this is an inferred function—it should use codespeak's @infer decorator"
            )
        self.func = func

    @property
    def goal(self) -> str | None:
        return inspect.getdoc(self.func)

    @property
    def resources(self) -> Resources:
        return _accessors._get_resources_for_function(self.func)

    @property
    def tests(self) -> Tests:
        return _accessors._get_tests_for_function(self.func)

    @property
    def logic(self) -> Callable:
        if not self._file_service.does_metadata_exist():
            raise Exception("No logic found. Execute the function to generate it.")
        return executor.load_generated_logic_from_module_qualname(
            module_qualname=self._file_service.generated_module_qualname,
            func_name=self._file_service.generated_entrypoint,
        )

    def execute_latest_unsafe(self, *args: Any, **kwargs: Any) -> Any:
        """Executes the inferred logic without checking if it exists"""
        if _settings.get_environment() == _settings.Environment.PROD:
            raise Exception(
                "unsafe_execute is not available in production, call the inferred function directly"
            )
        return self.logic(*args, **kwargs)

    def make(
        self,
        args: List[Any] | None = None,
        kwargs: Dict[str, Any] | None = None,
        should_execute: bool = False,
    ) -> Any:
        """Explicitly generate a new inference for a function. If using a method, must pass args to attach self type."""
        args = args or []
        kwargs = kwargs or {}
        self._try_add_self_definition(tuple(args), kwargs)
        digest = DeclarationDigest.from_inputs(
            declaration_source_code=self.resources.declaration_resources.source_code,
            custom_types=self.resources.as_custom_types_str(),
        )
        return self._make(
            args=args,
            kwargs=kwargs,
            should_execute=should_execute,
            digest=digest,
        )

    def _try_add_self_definition(self, args: Tuple[Any], kwargs: Dict[str, Any]):
        self_type = self_type_if_exists(self.func, args, kwargs)
        if self_type:
            self.resources.declaration_resources.try_add_self_definition(self_type)

    def set_resources(self, resources: Resources):
        """set resources object for an inferred function, overwriting any existing resources"""
        return _accessors._set_resources_for_function(self.func, resources)

    def set_tests(self, tests: Tests):
        """set tests object for an inferred function, overwriting any existing tests"""
        return _accessors._set_tests_for_function(self.func, tests)

    @property
    def _file_service(self) -> DeclarationFileService:
        return getattr(self.func, _InferenceAttributes.file_service)

    def _make(
        self,
        args: List[Any],
        kwargs: Dict[str, Any],
        should_execute: bool,
        digest: DeclarationDigest,
    ) -> InferenceMakeResponse:
        if _settings.get_environment() == _settings.Environment.PROD:
            raise Exception("Make is not available in production.")
        pytest_func: TestFunc | None = self.tests.try_get_test_func()
        code_generator = CodeGenerator(
            resources=self.resources,
            digest=digest,
            service=CodespeakService.with_defaults(self.resources),
            file_service=self._file_service,
            should_execute=should_execute,
            test_func=pytest_func,
            args=list(args),
            kwargs=kwargs,
        )
        generation = code_generator.generate()
        logic = executor.load_generated_logic_from_module_qualname(
            module_qualname=self._file_service.generated_module_qualname,
            func_name=self._file_service.generated_entrypoint,
        )
        setattr(self.func, InferenceAttributes.logic, logic)
        return InferenceMakeResponse(
            execution_result=generation.execution_result,
            source_code=code_generator.latest_source_code,
        )

    @staticmethod
    def this() -> "Inference":
        """easy way to access classified object for a function from inside it"""
        try:
            _func = Inference.manager.get_function()
            return Inference(func=_func)
        except Exception as e:
            raise Exception(
                "No managed resources found, only inside codespeak functions"
            )

    @staticmethod
    def for_function(func: Callable) -> "Inference":
        """get classified Inference object for an inferred function"""
        return Inference(func=func)
