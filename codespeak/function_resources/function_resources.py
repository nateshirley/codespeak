import json
from typing import Callable, Dict, List
from pydantic import BaseModel
from codespeak.function_resources.programmable_resources import (
    ProgrammableResources,
)
from codespeak.function_resources.declaration_resources import (
    DeclarationResources,
)

# maybe I'll just pull out programmable resources into this class and add declaration resources onto the
# I want to associate declaration resources with the function, but only on my side of the fence
# okay so just make it private


class FunctionResources(BaseModel):
    """Resources used by Codespeak to infer code for a function"""

    programmable_resources: ProgrammableResources
    declaration_resources: DeclarationResources

    def custom_types(self) -> Dict:
        types_ = self.declaration_resources.custom_types
        types_.update(self.programmable_resources.custom_types())
        return types_

    def as_custom_types_str(self) -> str:
        types_ = {"custom_types": self.custom_types()}
        return json.dumps(types_, indent=4)

    def inference_inputs(self) -> str:
        inputs = {
            "incomplete_file": self.declaration_resources.as_incomplete_file(),
            "custom_types": self.custom_types(),
        }
        return json.dumps(inputs, indent=4)

    # def stringified_schema(self) -> Dict:
    #     return json.dumps(self.custom_types(), indent=4)
