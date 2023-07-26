import re


def extract_delimited_python_code_from_string(string: str) -> str:
    pattern = r"```python(.*?)```"
    match = re.search(pattern, string, re.DOTALL)
    if match is None:
        raise ValueError("Could not find python code in response")
    return match.group(1).strip()
