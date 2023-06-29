from typing import Callable, Dict, List, OrderedDict, Type
import textwrap


def make_prompt(
    incomplete_file: str,
    custom_types_str: str,
    declaration_docstring: str,
    verbose: bool = True,
) -> str:
    text = prompt_text(incomplete_file, custom_types_str, declaration_docstring)
    if verbose:
        print("\n\n------START PROMPT------\n\n")
        print(text)
        print("\n\n------END PROMPT------\n\n")
    return text


def prompt_text(
    incomplete_file: str, custom_types_str: str, declaration_docstring: str
) -> str:
    return textwrap.dedent(
        f"""
The following message contains an incomplete python file. 

The file has imports and an incomplete function. Your task is to return the completed version of the file. 

Here is the incomplete python file:
```python
{incomplete_file}
```


Pay specific attention to the incomplete function—it should accomplish the following:
```
{declaration_docstring}
```


When available, use the incomplete function's name, parameter names, parameter types, and return type to further understand its intent.

You have an entire python interpreter at your disposal. In the completed file, import modules and define helper functions as needed. Be sure to use the incomplete function's exact signature in your completed file.

Here is a json object that contains metadata about custom python types that are relevant to the file. All of these types are already defined and they're available to your file via import. Do not redefine them. Use them as needed to complete the file:
```
{custom_types_str}
```


For installed types, use the qualname and module to recall your existing knowledge of their variables and methods. For local types, use the type hints and source code provided to understand how they could be used.  

Extremely common types, such as those from python's builtin module or the typing module, are intentionally excluded from the object above. Use your existing knowledge of these types to understand them, then import them and use them as needed. 

In your code, provide type hints that an experienced programmer would find helpful. Use docstrings and comments when helpful. If you would like to raise an exception, wrap it in InferredException.

Respond with only the completed version of the python file, delimited by triple-backticks and using a python identifier. Additional information will be ignored.

Example incomplete file:
```python
from typing import List

def get_even_numbers(numbers: List[int]) -> List[int]:
```


Example response:
```python
from typing import List

def get_even_numbers(numbers: List[int]) -> List[int]:
    return [number for number in numbers if number % 2 == 0]
```
"""
    )
