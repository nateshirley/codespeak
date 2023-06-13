from datetime import datetime
import inspect
import json
import os
from types import ModuleType
from typing import Any, Callable
from pydantic import BaseModel

from codespeak.metadata import FunctionMetadata
from codespeak.metadata.digest import DeclarationDigest

generated_directory_stem = "codespeak_generated"


class DeclarationFileService(BaseModel):
    declaration_filesystem_name: str
    generated_module_qualname: str
    codegen_absolute_dirpath: str
    generated_entrypoint: str

    def write_metadata(
        self,
        source_code: str,
        require_execution: bool,
        did_execute: bool,
        has_tests: bool,
        did_pass_tests: bool,
        digest: DeclarationDigest,
    ):
        if not os.path.exists(self.codegen_metadata_dirpath):
            os.makedirs(self.codegen_metadata_dirpath)

        metadata = FunctionMetadata(
            declaration_digest=digest,
            declaration_source=source_code,
            require_execution=require_execution,
            did_execute=did_execute,
            has_tests=has_tests,
            did_pass_tests=did_pass_tests,
            updated_at=datetime.utcnow().isoformat(),
        ).dict()

        with open(self.codegen_metadata_filepath, "w") as file:
            json.dump(metadata, file)

    def write_logic(self, source_code: str):
        if not os.path.exists(self.codegen_absolute_dirpath):
            os.makedirs(self.codegen_absolute_dirpath)

        with open(self.codegen_logic_filepath, "w") as file:
            file.write(source_code)

    @property
    def codegen_logic_filepath(self) -> str:
        return f"{self.codegen_absolute_dirpath}/{self.declaration_filesystem_name}.py"

    @property
    def codegen_metadata_dirpath(self) -> str:
        return f"{self.codegen_absolute_dirpath}/metadata"

    @property
    def codegen_metadata_filepath(self) -> str:
        return f"{self.codegen_metadata_dirpath}/metadata___{self.declaration_filesystem_name}.json"

    @staticmethod
    def from_callable(func: Callable) -> "DeclarationFileService":
        module = inspect.getmodule(func)
        if not module:
            raise Exception("module not found for func: ", func.__name__)
        abspath_to_proj = abspath_to_project_root(func)
        declared_module_qualname = get_declared_module_qualname(func)
        declared_module_as_filepath = declared_module_qualname.replace(".", "/")
        return DeclarationFileService(
            declaration_filesystem_name=func_qualname_to_filesystem_name(
                func.__qualname__
            ),
            generated_entrypoint=func.__name__,
            generated_module_qualname=build_generated_module_qualname(
                declared_module_qualname=declared_module_qualname,
                func_qualname=func.__qualname__,
            ),
            codegen_absolute_dirpath=f"{abspath_to_proj}/{generated_directory_stem}/{declared_module_as_filepath}",
        )

    def does_metadata_exist(self) -> bool:
        return os.path.exists(self.codegen_logic_filepath) and os.path.exists(
            self.codegen_metadata_filepath
        )

    def load_metadata(self) -> FunctionMetadata | None:
        if not os.path.exists(self.codegen_metadata_filepath):
            return None
        with open(self.codegen_metadata_filepath, "r") as file:
            data = json.load(file)
        return FunctionMetadata.parse_obj(data)

    def load_logic(self) -> str:
        with open(self.codegen_logic_filepath, "r") as file:
            return file.read()


def build_generated_module_qualname(declared_module_qualname: str, func_qualname: str):
    return f"{generated_directory_stem}.{declared_module_qualname}.{func_qualname_to_filesystem_name(func_qualname)}"


def func_qualname_to_filesystem_name(qualname: str) -> str:
    return qualname.replace(".", "___")


def derive_generated_module_qualname_from_func(func: Callable) -> str:
    declared_mod_qualname = get_declared_module_qualname(func)
    return build_generated_module_qualname(declared_mod_qualname, func.__qualname__)


def get_declared_module_qualname(func: Callable):
    source_file = inspect.getsourcefile(func)
    if not source_file:
        raise Exception("unable to get source file for func: ", func.__name__)
    return derive_declared_module_qualname_from_filepaths(
        source_file, abspath_to_project_root(func)
    )


def derive_declared_module_qualname_from_filepaths(
    declaration_filepath: str, project_root: str
):
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


def abspath_to_project_root(func: Callable):
    import os

    func_path = inspect.getabsfile(func)
    current_directory = func_path
    installed_root = None

    while current_directory != "/":
        if os.path.exists(os.path.join(current_directory, "pyproject.toml")):
            installed_root = current_directory
            break

        current_directory = os.path.dirname(current_directory)

    if installed_root is None:
        raise Exception(
            "Unable to find root directory of project where codespeak is installed. make sure you have a pyproject.toml file in your project root."
        )
    return installed_root
