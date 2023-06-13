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
    qualname: str
    module_name: str
    logic_dirpath: str
    metadata_dirpath: str

    def write_metadata(
        self,
        source_code: str,
        require_execution: bool,
        did_execute: bool,
        has_tests: bool,
        did_pass_tests: bool,
        digest: DeclarationDigest,
    ):
        if not os.path.exists(self.metadata_dirpath):
            os.makedirs(self.metadata_dirpath)

        metadata = FunctionMetadata(
            declaration_digest=digest,
            declaration_source=source_code,
            require_execution=require_execution,
            did_execute=did_execute,
            has_tests=has_tests,
            did_pass_tests=did_pass_tests,
            updated_at=datetime.utcnow().isoformat(),
        ).dict()

        with open(self.metadata_filepath, "w") as file:
            json.dump(metadata, file)

    def write_logic(self, source_code: str):
        if not os.path.exists(self.logic_dirpath):
            os.makedirs(self.logic_dirpath)

        with open(self.logic_filepath, "w") as file:
            file.write(source_code)

    @property
    def logic_filepath(self) -> str:
        return f"{self.logic_dirpath}/{self.system_name}.py"

    @property
    def metadata_filepath(self) -> str:
        return f"{self.metadata_dirpath}/metadata___{self.system_name}.json"

    @property
    def logic_modulepath(self) -> str:
        return DeclarationFileService.build_logic_modulepath(
            module_name=self.module_name, qualname=self.qualname
        )

    @property
    def system_name(self) -> str:
        return DeclarationFileService.qualname_to_system_name(self.qualname)

    @staticmethod
    def from_callable(func: Callable) -> "DeclarationFileService":
        module = inspect.getmodule(func)
        # print("module: ", module)
        if not module:
            raise Exception("module not found for func: ", func.__name__)
        # module name includes nesting
        abspath_to_proj = abspath_to_project_root(func)
        # module is __main__ when running a script directly, we don't want to use the module name in that case
        module_name = get_full_module_name(module, abspath_to_proj, func)
        print("full mod name: ", module_name)
        print("file: ", inspect.getsourcefile(func))
        # if module.__name__.endswith("__main__"):
        #     mod_path = get_module_path_with_filepath(
        #         inspect.getfile(func), abspath_to_proj
        #     )
        #     module_name = mod_path
        # else:
        #     module_name = module.__name__
        module_as_filepath = module_name.replace(".", "/")
        dirpath_in_codespeak_generated = (
            f"{abspath_to_proj}/{generated_directory_stem}/{module_as_filepath}"
        )
        return DeclarationFileService(
            qualname=func.__qualname__,
            module_name=module_name,
            logic_dirpath=dirpath_in_codespeak_generated,
            metadata_dirpath=f"{dirpath_in_codespeak_generated}/metadata",
        )

    def does_metadata_exist(self) -> bool:
        return os.path.exists(self.logic_filepath) and os.path.exists(
            self.metadata_filepath
        )

    def load_metadata(self) -> FunctionMetadata | None:
        if not os.path.exists(self.metadata_filepath):
            return None
        with open(self.metadata_filepath, "r") as file:
            data = json.load(file)
        return FunctionMetadata.parse_obj(data)

    def load_logic(self) -> str:
        with open(self.logic_filepath, "r") as file:
            return file.read()

    @staticmethod
    def logic_modulepath_from_callable(func: Callable) -> str:
        module = inspect.getmodule(func)
        if not module:
            raise Exception("module not found for func: ", func.__name__)
        module_name = get_full_module_name(module, abspath_to_project_root(func), func)
        return DeclarationFileService.build_logic_modulepath(
            module_name=module_name, qualname=func.__qualname__
        )

    @staticmethod
    def qualname_to_system_name(qualname: str) -> str:
        return qualname.replace(".", "___")

    # do i have a flatness issue here?
    # one module per function, this module contains the logic for the function with the redeclaration
    @staticmethod
    def build_logic_modulepath(module_name: str, qualname: str) -> str:
        return f"{generated_directory_stem}.{module_name}.{DeclarationFileService.qualname_to_system_name(qualname)}"

    # @staticmethod
    # def codegen_dirpath(func: Callable) -> str:
    #     # e.g., Users/username/project_root/codespeak_generated
    #     return abspath_to_project_root(func) + "/" + generated_directory_stem


def get_full_module_name(
    module_obj: ModuleType, abspath_to_proj_root: str, func: Callable
) -> str:
    mod_path = get_module_path_with_filepath(
        inspect.getfile(func), abspath_to_proj_root
    )
    return mod_path
    # if module_obj.__name__.endswith("__main__"):
    #     mod_path = get_module_path_with_filepath(
    #         inspect.getfile(func), abspath_to_proj_root
    #     )
    #     return mod_path
    # else:
    #     return module_obj.__name__


def get_module_path_with_filepath(filepath: str, project_root: str):
    # Make sure both paths are absolute and normalized
    filepath = os.path.normpath(os.path.abspath(filepath))
    project_root = os.path.normpath(os.path.abspath(project_root))

    # Check if the filepath is in the project_root
    if not filepath.startswith(project_root):
        raise ValueError("The filepath must be inside the project root")

    # Get the relative path from project_root to filepath
    rel_path = os.path.relpath(filepath, project_root)

    # Remove the '.py' extension
    module_path = os.path.splitext(rel_path)[0]

    # Replace path separators with dots
    module_path = module_path.replace(os.sep, ".")

    # If the function is in '__init__', use the parent directory as the module
    if module_path.endswith(".__init__"):
        module_path = module_path[: -len(".__init__")]

    return module_path


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


"""
okay so some of the issues to summarize:

- unable to locate module when running a script directly
- function swapper causes the module to be reloaded, which causes the function to be reloaded, which causes the function to be swapped again, which causes the module to be reloaded again, etc.
- function swapper loading module at new path
- function getting reloaded inside the function swapper
"""
