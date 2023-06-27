import re
from pydantic import BaseModel
from codespeak._core import prompt
from codespeak._core.openai_service import OpenAIService, Roles
from codespeak._core.results_collector import CrashReport
from codespeak._settings._settings import get_verbose
from codespeak.inference._resources import Resources


class IterationState(BaseModel):
    num_code_versions: int = 0
    max_code_versions: int = 3
    num_test_versions: int = 0
    max_test_versions: int = 3
    num_bad_formatting_versions: int = 0
    max_bad_formatting_versions: int = 3


class CodespeakService(BaseModel):
    openai_service: OpenAIService
    iterations: IterationState
    resources: Resources

    @staticmethod
    def with_defaults(resources: Resources) -> "CodespeakService":
        return CodespeakService(
            openai_service=OpenAIService.with_defaults(),
            iterations=IterationState(),
            resources=resources,
        )

    def generate_source_code(self) -> str:
        _prompt = prompt.make(
            incomplete_file=self.resources.declaration_resources.as_incomplete_file(),
            custom_types=self.resources.as_custom_types_str(),
            declaration_docstring=self.resources.declaration_resources.docstring,
            verbose=get_verbose(),
        )
        return self._fetch_new_source_code(prompt=_prompt)

    def _fetch_new_source_code(self, prompt: str) -> str:
        response = self.openai_service.send_user_message(content=prompt)
        if " raise" in response:
            if not "GeneratedException" in response:
                print("possible manual exception will cause regen in future")
        source_code = self._guarantee_source_formatting(response)
        return source_code

    def try_regenerate_from_execution_failure(
        self,
        exception: Exception,
    ) -> str:
        if self.iterations.num_code_versions < self.iterations.max_code_versions:
            print(
                "regenerating for func: ",
                self.resources.declaration_resources.qualname,
                " num attempt: ",
                self.iterations.num_code_versions + 1,
            )
            print("in response to exception: ", exception)
            self.iterations.num_code_versions += 1
            return self._fetch_new_source_code(
                prompt=self._corrective_message_for_execution_failure(exception)
            )
        else:
            raise Exception(
                f"Unable to generate code that executes with the given arguments for {self.resources.declaration_resources.qualname}. Make sure your arguments are of the correct type, clarify your types, or modify your docstring."
            )

    def try_regenerate_from_test_failure(
        self, test_source_code: str, crash_report: CrashReport
    ) -> str:
        if self.iterations.num_test_versions < self.iterations.max_test_versions:
            print(
                "regenerating after failed tests for func: ",
                self.resources.declaration_resources.qualname,
                " num attempt: ",
                self.iterations.num_test_versions + 1,
            )
            self.iterations.num_test_versions += 1
            prompt = self._corrective_message_for_test_failure(
                test_source_code=test_source_code,
                crash_report=crash_report,
            )
            return self._fetch_new_source_code(prompt=prompt)
        else:
            raise Exception(
                f"Unable to generate code that executes with the given arguments for {self.resources.declaration_resources.qualname}. Make sure your arguments are of the correct type, clarify your types, or modify your docstring."
            )

    def _guarantee_source_formatting(self, response: str) -> str:
        pattern = r"```python(.*?)```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(
                1
            ).strip()  # group(1) to get the content between the backticks
        else:
            if (
                self.iterations.num_bad_formatting_versions
                < self.iterations.max_bad_formatting_versions
            ):
                resp = self.openai_service.send_user_message(
                    content="Your response should start with ```python and end with ```. Try again."
                )
                self.iterations.num_bad_formatting_versions += 1
                return self._guarantee_source_formatting(resp)
            else:
                raise Exception("Too many bad formatting versions")

    def _corrective_message_for_execution_failure(self, exception: Exception) -> str:
        msg = "The previous code did not execute. It returned the following exception:"
        msg += f"\n```\n{exception}\n```\n\n"
        msg += "Use the same information in my original message to complete the original task."
        msg += " When correcting your response, be sure to think about the root cause of the exception and adjust for it. Remember, if you want to raise an exception, wrap it in GeneratedException."
        return msg

    def _corrective_message_for_test_failure(
        self, test_source_code: str, crash_report: CrashReport
    ) -> str:
        msg = f"The following tests were executed: \n```\n{test_source_code}\n```\n\n"
        msg += "The tests failed with message:\n```\n"
        msg += crash_report.message
        msg += "\n```\n\n"
        msg += "Use the test's source code to further understand the intended design of the incomplete function, and reference the information in my original message to try again to complete the original task. Be sure to think about the root cause of the test failure and adjust your response to better align with the intent of the incomplete function."
        return msg
