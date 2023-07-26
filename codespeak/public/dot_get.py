from typing import Any, Dict


def dot_get(data_dict: Dict, map_str: str, default_value: Any = None) -> Any:
    if data_dict is None:
        return default_value
    map_list = map_str.split(".")
    for k in map_list:
        if k not in data_dict:
            return default_value
        data_dict = data_dict[k]
        if data_dict is None:
            return default_value
    return data_dict
