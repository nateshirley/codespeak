import json
import re
import httpx
from codespeak.function.function_lite import FunctionLite


url = "http://localhost:8000"
# url = "codespeak-api-production.up.railway.app"


@staticmethod
async def make_inference(function_lite: FunctionLite, api_identifier: str) -> str:
    path = "/v1/inferences/make"
    data = {
        "function_lite": function_lite.dict(),
        "api": api_identifier,
    }
    response_text = ""
    _url = f"{url}{path}"
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url=_url, json=data, timeout=30) as response:
            async for chunk in response.aiter_bytes():
                text = chunk.decode()
                response_text += text
                print(text, end="")
    print("\n")
    return response_text


# class CodespeakService(BaseModel):
#     def _guarantee_source_formatting(self, response: str) -> str:
#         pattern = r"```python(.*?)```"
#         match = re.search(pattern, response, re.DOTALL)
#         if match is not None:
#             return match.group(
#                 1
#             ).strip()  # group(1) to get the content between the backticks
# else:
#     if (
#         self.iterations.num_bad_formatting_versions
#         < self.iterations.max_bad_formatting_versions
#     ):
# self.openai_service.send_user_message(
#     content="Your response should start with ```python and end with ```. Try again."
# )
# self.iterations.num_bad_formatting_versions += 1
#     return self._guarantee_source_formatting(
#         self.openai_service.latest_message_content
#     )
# else:
#     raise Exception("Bad formatting")
