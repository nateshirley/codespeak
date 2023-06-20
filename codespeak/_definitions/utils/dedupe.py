from typing import List
from codespeak._definitions.definition import Definition


def dedupe(definitions: List[Definition]) -> List[Definition]:
    uniques = []
    paths = {}
    for _def in definitions:
        if hasattr(_def, "module") and hasattr(_def, "qualname"):
            path = f"{_def.module}.{_def.qualname}"
            if path in paths:
                continue
            paths[path] = True
            uniques.append(_def)
        else:
            raise Exception("definition should not be missing module and qualname")
    return uniques
