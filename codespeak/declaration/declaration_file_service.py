from datetime import datetime
import inspect
import json
import os
from typing import Callable
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
        if not module:
            raise Exception("module not found for func: ", func.__name__)
        module_as_filepath = module.__name__.replace(".", "/")
        dirpath = f"{DeclarationFileService.codegen_dirpath(func)}/{module_as_filepath}"
        return DeclarationFileService(
            qualname=func.__qualname__,
            module_name=module.__name__,
            logic_dirpath=dirpath,
            metadata_dirpath=f"{dirpath}/metadata",
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
        return DeclarationFileService.build_logic_modulepath(
            module_name=module.__name__, qualname=func.__qualname__
        )

    @staticmethod
    def qualname_to_system_name(qualname: str) -> str:
        return qualname.replace(".", "___")

    # one module per function, this module contains the logic for the function with the redeclaration
    @staticmethod
    def build_logic_modulepath(module_name: str, qualname: str) -> str:
        return f"{generated_directory_stem}.{module_name}.{DeclarationFileService.qualname_to_system_name(qualname)}"

    @staticmethod
    def codegen_dirpath(func: Callable) -> str:
        # e.g., Users/username/project_root/codespeak_generated
        return abspath_to_project_root(func) + "/" + generated_directory_stem


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
