import inspect
import json
from typing import Callable, Dict, List
from pydantic import BaseModel
from codespeak._declaration.body_imports import BodyImports
from codespeak._definitions import classify
from codespeak._definitions.definition import Definition
from codespeak.inference._body_resources import BodyResources
from codespeak.inference._programmable_resources import ProgrammableResources
from codespeak._declaration.declaration_resources import DeclarationResources


class Resources(BaseModel):
    """Resources used by Codespeak to infer code for a function"""

    programmable_resources: ProgrammableResources
    declaration_resources: DeclarationResources
    body_resources: BodyResources

    def custom_types(self) -> Dict:
        types_ = self.declaration_resources.custom_types
        types_.update(self.body_resources.custom_types())
        types_.update(self.programmable_resources.custom_types())
        return types_

    def as_custom_types_str(self) -> str:
        return json.dumps(self.custom_types, indent=4)

    def prompt_inputs(self) -> str:
        inputs = {
            "incomplete_file": self.declaration_resources.as_incomplete_file(),
            "custom_types": self.custom_types,
        }
        return json.dumps(inputs, indent=4)

    def add_classes(self, *classes: type):
        for _class in classes:
            if not inspect.isclass(_class):
                raise ValueError(f"Expected class object, got {type(_class).__name__}")
            self.programmable_resources.classes.append(classify.from_any(_class))
