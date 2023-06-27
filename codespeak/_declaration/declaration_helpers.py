import ast
import re
from typing import Any, Callable, List
from codespeak._definitions import classify
from codespeak._definitions.definition import Definition
import inspect


def insert_after_self(text, insert_text):
    def replace(match):
        return match.group() + ":" + insert_text

    pattern = r"\(self"
    new_text = re.sub(pattern, replace, text, count=1)
    return new_text


def insert_self_in_signature_text(signature_text: str, self_type_name: str) -> str:
    return insert_after_self(signature_text, self_type_name)

    # if self_definition:
    #     defs.append(self_definition)
    # self_definition: Definition | None

    # if self_type_name:
    #     signature = insert_after_self(signature, self_type_name)


def build_sig_string(func_name: str, source_code: str) -> str:
    module = ast.parse(source_code)
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            # Reconstruct the function signature from the 'args' attribute
            signature = f"def {node.name}({ast.unparse(node.args)})"
            if node.returns:  # If there's a return annotation, add it
                signature += f" -> {ast.unparse(node.returns)}"
            signature += ":"
            return signature
    raise Exception("function signature not found")


def definitions_for_signature(
    sig: inspect.Signature,
) -> List[Definition]:
    """Definitions for types used in the signature"""
    defs: List[Definition] = []
    params = sig.parameters
    for param in params.values():
        _def = param.annotation
        if _def is inspect.Signature.empty:
            continue
        defs.append(classify.from_any(_def))
    return_annotation = sig.return_annotation
    if not return_annotation is inspect.Signature.empty:
        defs.append(classify.from_any(return_annotation))
    return defs
