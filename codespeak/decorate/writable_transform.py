from typing import Sequence
import libcst as cst
import textwrap
from libcst import BaseCompoundStatement, FunctionDef, SimpleStatementLine, CSTNode


class ReplaceFunctionTransformer(cst.CSTTransformer):
    def __init__(
        self,
        function_name: str,
        new_function_def: SimpleStatementLine | BaseCompoundStatement,
    ) -> None:
        self.new_function_def = new_function_def
        self.function_name = function_name

    def leave_FunctionDef(
        self, original_node: FunctionDef, updated_node: FunctionDef
    ) -> CSTNode:
        if original_node.name.value == self.function_name:
            return self.new_function_def
        return updated_node


def get_function_node(
    name: str, body: Sequence[SimpleStatementLine | BaseCompoundStatement]
) -> FunctionDef:
    for node in body:
        if isinstance(node, cst.FunctionDef):
            if node.name.value == name:
                return node
    raise ValueError(f"Function {name} not found in body")


def replace_function(filepath: str, function_name: str, new_source_code: str):
    replaceable_code = ""
    with open(filepath, "r") as f:
        replaceable_code = f.read()

    # Parse the source code into CSTs
    module = cst.parse_module(replaceable_code)
    # new_function_def = cst.parse_statement(new_function)
    new_function_def = cst.parse_statement(new_source_code)

    # Get the original function
    original_function_def = get_function_node(function_name, module.body)
    # [
    #     node for node in module.body if isinstance(node, cst.FunctionDef)
    # ][0]

    # Extract leading lines from original function
    leading_lines = original_function_def.leading_lines

    # Add leading lines to new function
    new_function_with_comments = new_function_def.with_changes(
        leading_lines=leading_lines
    )

    # Create an instance of the transformer and apply it to the CST
    transformer = ReplaceFunctionTransformer(
        function_name=function_name, new_function_def=new_function_with_comments
    )
    new_module = module.visit(transformer)

    # Convert the CST back into source code
    new_source_code = new_module.code

    with open(filepath, "w") as f:
        f.write(new_source_code)
