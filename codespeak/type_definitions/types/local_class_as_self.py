import ast
from typing import Dict
from codespeak.type_definitions.types.local_class import LocalClass


class RemoveFunction(ast.NodeTransformer):
    def __init__(self, function_name):
        self.function_name = function_name

    def visit_FunctionDef(self, node):
        if node.name == self.function_name:
            return None
        return node


def source_code_without_function(code, function_name) -> str:
    tree = ast.parse(code)
    RemoveFunction(function_name).visit(tree)
    return ast.unparse(tree)


class LocalClassAsSelf(LocalClass):
    method_name: str

    def annotate(self) -> Dict:
        return {
            f"{self.import_path()}": {
                "origin": "local",
                "qualname": self.qualname,
                "module": self.module,
                "source_code": source_code_without_function(
                    self.source_code, self.method_name
                ),
                "bases": [base.annotate_in_local_class() for base in self.bases],
                "type_hints": {
                    key: value.annotate_in_local_class()
                    for key, value in self.type_hints.items()
                },
            }
        }
