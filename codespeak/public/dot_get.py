from typing import Any, Dict


def dot_get(data_dict: Dict, map_str: str) -> Any | None:
    map_list = map_str.split(".")
    for k in map_list:
        if k not in data_dict:
            return None
        data_dict = data_dict[k]
        if data_dict is None:
            return None
    return data_dict
