import time
import openai
from typing import Any, List

from pydantic import BaseModel, validator
from codespeak.settings import _settings


class Roles:
    @staticmethod
    def user():
        return "user"

    @staticmethod
    def system():
        return "system"

    @staticmethod
    def assistant():
        return "assistant"


class Message(BaseModel):
    role: str
    content: str

    @validator("role")
    def check_color(cls, v):
        allowed_values = ["user", "system", "assistant"]
        if v not in allowed_values:
            raise ValueError(f"role must be one of {allowed_values}")
        return v


class OpenAIService(BaseModel):
    model: str
    messages: List[Message]
    num_retries: int = 0
    router_mode: bool = False

    @staticmethod
    def with_defaults():
        return OpenAIService(
            model=_settings.get_openai_model(),
            messages=[
                Message(
                    role=Roles.system(),
                    content="You are a competent and diligent python programmer. You write and communicate in python code.",
                ),
            ],
            num_retries=0,
        )

    @staticmethod
    def with_system_message(msg: str):
        return OpenAIService(
            model=_settings.get_openai_model(),
            messages=[
                Message(role=Roles.system(), content=msg),
            ],
            num_retries=0,
        )

    def json_messages(self):
        return [m.dict() for m in self.messages]

    def send_user_message(self, content: str) -> None:
        self.messages.append(Message(role=Roles.user(), content=content))
        completion = self.get_completion()
        self.add_message(content=completion, role=Roles.assistant())

    @property
    def latest_message_content(self) -> str:
        if len(self.messages) == 0:
            raise Exception("no messages")
        return self.messages[-1].content

    def add_message(self, content: str, role: str):
        self.messages.append(Message(role=role, content=content))

    def get_completion(self) -> str:
        openai_key = _settings.get_openai_api_key()
        if openai_key is None or openai_key == "":
            raise Exception(
                "OpenAI API key not configured, use codespeak.set_openai_key() to set it, or load an env variable OPENAI_API_KEY",
            )
        openai.api_key = _settings.get_openai_api_key()
        if self.router_mode:
            openai.api_base = "https://openrouter.ai/api/v1"
            openai.api_key = "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"
        try:
            referrer = "https://github.com/nateshirley/codespeak"
            response: Any = openai.ChatCompletion.create(
                model=self.model,
                messages=self.json_messages(),
                stream=True,
                headers={"HTTP-Referer": referrer} if self.router_mode else None,
            )
            result = ""
            print("\n\n------MAKING INFERENCE------\n\n")
            for chunk in response:
                chunk: Any = chunk
                choices: list = chunk.choices
                if choices is None:
                    raise Exception("choices does not exist on completion")
                if len(choices) == 0:
                    continue
                delta = choices[0].delta
                if "content" in delta:
                    result += delta.content
                    print(f"{delta.content}", end="")
            print("\n\n------END INFERENCE------\n\n")
            return result
        except Exception as e:
            if self.num_retries < 5:
                print("retr completion!!!")
                self.num_retries += 1
                time.sleep(1)
                return self.get_completion()
            else:
                raise Exception("couldn't get completion")
