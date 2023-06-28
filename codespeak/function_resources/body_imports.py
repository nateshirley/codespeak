import ast
import inspect
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from codespeak.definitions.definition import Definition
from codespeak.definitions import classify

import importlib
import astor


class BodyImports(BaseModel):
    defs: List[Definition]
    statements: List[str]

    def imports_text(self) -> str:
        return "\n".join(self.statements)

    def insert(self, _obj: Any):
        self.defs.append(classify.from_any(_obj))

    def custom_types(self) -> Dict:
        customs = {}
        for _def in self.defs:
            customs.update(_def.custom_types())
        return customs

    # this is probably buggy
    @staticmethod
    def from_func_source(source_code: str) -> "BodyImports":
        # Get the source code of the function
        # Parse the source code into an AST
        tree = ast.parse(source_code)

        body_imports = BodyImports(defs=[], statements=[])

        # Find all the import statements
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    raise Exception(
                        "whole module imports not supported in body imports. use from"
                    )
                body_imports.statements.append(astor.to_source(node))
                if not hasattr(node, "module"):
                    raise Exception("module expected in 'from' import node")
                module_path: str = getattr(node, "module")
                try:
                    module = importlib.import_module(module_path)
                    for alias in node.names:
                        # Import the module and get the actual object
                        if alias.asname:
                            raise Exception("asname not supported in body imports")
                        if hasattr(module, alias.name):
                            obj = getattr(module, alias.name)
                            if inspect.ismodule(obj):
                                raise Exception(
                                    "whole module imports not supported. only objects"
                                )
                            body_imports.insert(obj)
                        else:
                            print(
                                f"Warning: {alias.name} not found in module {module_path}"
                            )
                except Exception as e:
                    print(f"Failed to import module at path {module_path}: {e}")

        return body_imports
