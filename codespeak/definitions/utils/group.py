from typing import Dict, List


from codespeak.definitions.definition import Definition


def group_by_module(definitions: List[Definition]) -> Dict[str, List[Definition]]:
    """groups definitions by the module they come from"""
    grouped = {}
    for _def in definitions:
        val = grouped.get(_def.module, [])
        val.append(_def)
        grouped[_def.module] = val
    return grouped
