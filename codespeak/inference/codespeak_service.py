import json
import re
from typing import List
from pydantic import BaseModel
from codespeak.frame import Frame
from codespeak.function.function_declaration_lite import FunctionDeclarationLite
from codespeak.function.function_lite import FunctionLite
from codespeak.inference import prompt
from codespeak.inference.openai_service import OpenAIService, Roles
from codespeak.inference.results_collector import CrashReport
from codespeak.settings._settings import get_verbose
from codespeak.settings import _settings
import requests


class IterationState(BaseModel):
    num_code_versions: int = 0
    max_code_versions: int = 3
    num_test_versions: int = 0
    max_test_versions: int = 3
    num_bad_formatting_versions: int = 0
    max_bad_formatting_versions: int = 3


url = "http://localhost:8000"
# url = "codespeak-api-production.up.railway.app"


class CodespeakService(BaseModel):
    openai_service: OpenAIService
    iterations: IterationState
    function_lite: FunctionLite

    @staticmethod
    def with_defaults(function_lite: FunctionLite) -> "CodespeakService":
        return CodespeakService(
            openai_service=OpenAIService.with_defaults(),
            iterations=IterationState(),
            function_lite=function_lite,
        )

    def generate_source_code(self) -> str:
        custom_types = {"custom_types": self.function_lite.custom_types}
        custom_types_str = json.dumps(custom_types, indent=4)
        api_schemas = self.fetch_relevant_api_schemas(
            document=self.function_lite.declaration.query_document
        )
        _prompt = prompt.make_prompt(
            incomplete_file=self.function_lite.declaration.incomplete_file,
            custom_types_str=custom_types_str,
            declaration_docstring=self.function_lite.declaration.docstring,
            api_schemas=api_schemas,
            verbose=get_verbose(),
        )
        return self._fetch_new_source_code(prompt=_prompt)

    def _fetch_new_source_code(self, prompt: str) -> str:
        self.openai_service.send_user_message(content=prompt)
        response = self.openai_service.latest_message_content
        if " raise" in response:
            if not "InferredException" in response:
                print("possible manual exception will cause regen in future")
        source_code = self._guarantee_source_formatting(response)
        return source_code

    @property
    def already_tried_execution(self) -> bool:
        return self.iterations.num_code_versions > 0

    def try_regenerate_from_execution_failure(
        self,
        exception: Exception,
    ) -> str:
        if self.iterations.num_code_versions < self.iterations.max_code_versions:
            print(
                "regenerating for func: ",
                self.function_lite.declaration.qualname,
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
                f"Unable to generate code that executes with the given arguments for {self.function_lite.declaration.qualname}. Make sure your arguments are of the correct type, clarify your types, or modify your docstring."
            )

    def try_regenerate_from_test_failure(
        self, test_source_code: str, crash_report: CrashReport
    ) -> str:
        if self.iterations.num_test_versions < self.iterations.max_test_versions:
            print(
                "regenerating after failed tests for func: ",
                self.function_lite.declaration.qualname,
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
                f"Unable to generate code that executes with the given arguments for {self.function_lite.declaration.qualname}. Make sure your arguments are of the correct type, clarify your types, or modify your docstring."
            )

    def _guarantee_source_formatting(self, response: str) -> str:
        pattern = r"```python(.*?)```"
        match = re.search(pattern, response, re.DOTALL)
        if match is not None:
            return match.group(
                1
            ).strip()  # group(1) to get the content between the backticks
        else:
            if (
                self.iterations.num_bad_formatting_versions
                < self.iterations.max_bad_formatting_versions
            ):
                self.openai_service.send_user_message(
                    content="Your response should start with ```python and end with ```. Try again."
                )
                self.iterations.num_bad_formatting_versions += 1
                return self._guarantee_source_formatting(
                    self.openai_service.latest_message_content
                )
            else:
                raise Exception("Too many bad formatting versions")

    def _corrective_message_for_execution_failure(self, exception: Exception) -> str:
        msg = "The previous code did not execute. It returned the following exception:"
        msg += f"\n```\n{exception}\n```\n\n"
        msg += "Use the same information in my original message to complete the original task."
        msg += " When correcting your response, be sure to think about the root cause of the exception and adjust for it. Remember, if you want to raise an exception, wrap it in InferredException."
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

    @staticmethod
    def make_inference(function_lite: FunctionLite) -> str:
        path = "/v1/inferences/make"
        data = {
            "function_lite": function_lite.dict(),
            "api": "harmonic",
        }
        response = requests.post(f"{url}{path}", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                "couldn't make inference with codespeak api:",
                response.text,
            )

    @staticmethod
    def fetch_embedding_results(document: str) -> List[dict] | None:
        api_keys = _settings.get_api_keys()
        harmonic_api_key = api_keys.get("harmonic", None)
        if harmonic_api_key is None:
            return None
        path = "/query_for_results"
        data = {
            "document": document,
        }
        response = requests.post(f"{url}{path}", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                "couldn't get api schema from codespeak api: ",
                response.text,
            )

    @staticmethod
    def fetch_relevant_api_schemas(document: str) -> List[dict] | None:
        api_keys = _settings.get_api_keys()
        harmonic_api_key = api_keys.get("harmonic", None)
        if harmonic_api_key is None:
            return None
        path = "/query"
        data = {
            "document": document,
            "n_results": 1,
            "api": "harmonic",
        }
        response = requests.post(f"{url}{path}", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                "couldn't get api schema from codespeak api: ",
                response.text,
            )
