import inspect
import os
from typing import Any

from codespeak.settings import settings


def derive_module_qualname_for_object(_object: Any):
    """Should be a local object"""
    source_file = inspect.getsourcefile(_object)
    if not source_file:
        raise Exception("unable to get source file for func: ", _object.__name__)
    return derive_module_qualname_from_filepaths(
        source_file, settings.get_abspath_to_project_root()
    )


def derive_module_qualname_from_filepaths(declaration_filepath: str, project_root: str):
    # Make sure both paths are absolute and normalized
    filepath = os.path.normpath(os.path.abspath(declaration_filepath))
    project_root = os.path.normpath(os.path.abspath(project_root))

    # Check if the filepath is in the project_root
    if not filepath.startswith(project_root):
        raise ValueError("The filepath must be inside the project root")

    # Get the relative path from project_root to filepath
    rel_path = os.path.relpath(filepath, project_root)

    # Remove the '.py' extension
    module_qualname = os.path.splitext(rel_path)[0]

    # Replace path separators with dots
    module_qualname = module_qualname.replace(os.sep, ".")

    # If the function is in '__init__', use the parent directory as the module
    if module_qualname.endswith(".__init__"):
        module_qualname = module_qualname[: -len(".__init__")]

    return module_qualname
