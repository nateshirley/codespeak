from typing import List

from codespeak.definitions.definition import Definition


def flatten_definitions(
    definitions: List[Definition],
) -> List[Definition]:
    flattened = []
    for _def in definitions:
        flattened.extend(_def.flatten())
    return flattened
