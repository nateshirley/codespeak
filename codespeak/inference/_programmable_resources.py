from pydantic import BaseModel
from typing import Dict, List
from codespeak._definitions.definition import Definition


class ProgrammableResources(BaseModel):
    classes: List[Definition] = []

    def custom_types(self) -> Dict:
        types_ = {}
        for _class in self.classes:
            types_.update(_class.custom_types())
        return types_
