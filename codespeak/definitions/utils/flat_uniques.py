# flat_uniques = dedupe(
#     flatten_definitions(self.args, include_local_classes=False)
# )
from typing import List
from codespeak.definitions.utils.dedupe import dedupe
from codespeak.definitions.utils.flatten import flatten_definitions
from codespeak.definitions.definition import Definition


def flat_uniques(definitions: List[Definition], locals_only: bool) -> List[Definition]:
    f_u = dedupe(flatten_definitions(definitions))
    if locals_only:
        return [local for local in f_u if local.type == "LocalClass"]
    else:
        return f_u
