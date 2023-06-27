# def __make__(
#     args: List[Any],
#     kwargs: Dict[str, Any],
#     should_execute: bool,
#     declaration: CodespeakDeclaration,
# ) -> Any:
#     if _settings.get_environment() == _settings.Environment.PROD:
#         raise Exception("Make is not available in production.")
#     pytest_func: TestFunc | None = self.tests.try_get_test_func()
#     code_generator = CodeGenerator(
#         declaration=declaration,
#         service=CodespeakService.with_defaults(declaration),
#         file_service=self.__file_service__,
#         should_execute=should_execute,
#         test_func=pytest_func,
#         args=list(args),
#         kwargs=kwargs,
#     )
#     generation = code_generator.generate()
#     logic = executor.load_generated_logic_from_module_qualname(
#         module_qualname=self.__file_service__.generated_module_qualname,
#         func_name=self.__file_service__.generated_entrypoint,
#     )
#     setattr(self.func, InferenceAttributes.logic, logic)
#     return {
#         "execution_result": generation.execution_result,
#         "source_code": code_generator.latest_source_code,
#     }
