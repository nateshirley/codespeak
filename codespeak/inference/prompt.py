import textwrap
from typing import List


def make_prompt(
    incomplete_file: str,
    custom_types_str: str,
    declaration_docstring: str,
    api_schemas: List[dict] | None,
    verbose: bool = True,
) -> str:
    text = prompt_text(
        incomplete_file, custom_types_str, declaration_docstring, api_schemas
    )
    if verbose:
        print("\n\n------START PROMPT------\n\n")
        print(text)
        print("\n\n------END PROMPT------\n\n")
    return text


def prompt_text(
    incomplete_file: str,
    custom_types_str: str,
    declaration_docstring: str,
    api_schemas: List[dict] | None,
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

Here is a json object that contains metadata about custom python types that are already definied in the project and relevant to the file. They're available via import. Do not redefine them. Import and use them as needed to complete the file:
```
{custom_types_str}
```

For installed types, use the qualname and module to recall your existing knowledge of their variables and methods. For local types, use the type hints and source code provided to understand how they could be used.  

Extremely common types, such as those from python's builtin module or the typing module, are intentionally excluded from the object above. Use your existing knowledge of these types to understand them, then import them and use them as needed. 
{api_schemas_portion(api_schemas)}
In your code, provide type hints that an experienced programmer would find helpful. Use docstrings and comments when helpful. If you would like to raise an exception, wrap it in InferredException.

Respond with only the completed version of the python file, delimited by triple-backticks and using a python identifier. Additional context outside of the code will be ignored.

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


def api_schemas_portion(api_schemas: List[dict] | None) -> str:
    if api_schemas is None or len(api_schemas) == 0:
        return ""
    return textwrap.dedent(
        f"""
        Here is a list of openapi schemas that are likely relevant to the python file. Use the schemas to understand the associated apis and call them as needed in your completed file:
        {str(api_schemas)}

        Remember, you can follow the $ref links in a schema to get more information about the types in its api.
        """
    )
