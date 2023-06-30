from datetime import datetime
import inspect
import json
import os
from types import ModuleType
from typing import Any, Callable
from pydantic import BaseModel

from codespeak.settings import _settings
from codespeak.function.function_metadata import FunctionMetadata
from codespeak.function.function_digest import FunctionDigest
from codespeak.constants import metadata_file_prefix, codegen_dirname
from codespeak.helpers.derive_module_qualname_for_object import (
    derive_module_qualname_for_object,
)


class FunctionFileService(BaseModel):
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
        digest: FunctionDigest,
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
        return f"{self.codegen_metadata_dirpath}/{metadata_file_prefix}{self.declaration_filesystem_name}.json"

    @staticmethod
    def gather_generated_module_qualname(decorated_func: Callable) -> str:
        module = inspect.getmodule(decorated_func)
        if module is None:
            raise Exception("module not found for func: ", decorated_func.__name__)
        declared_module_qualname = derive_module_qualname_for_object(decorated_func)
        return build_generated_module_qualname(
            declared_module_qualname=declared_module_qualname,
            inferred_func_qualname=decorated_func.__qualname__,
        )

    @staticmethod
    def from_decorated_func(func: Callable) -> "FunctionFileService":
        module = inspect.getmodule(func)
        if module is None:
            raise Exception("module not found for func: ", func.__name__)
        abspath_to_proj = _settings.get_abspath_to_project_root()
        declared_module_qualname = derive_module_qualname_for_object(func)
        declared_module_as_filepath = declared_module_qualname.replace(".", "/")
        return FunctionFileService(
            declaration_filesystem_name=inferred_func_qualname_to_filesystem_name(
                func.__qualname__
            ),
            generated_entrypoint=func.__name__,
            generated_module_qualname=build_generated_module_qualname(
                declared_module_qualname=declared_module_qualname,
                inferred_func_qualname=func.__qualname__,
            ),
            codegen_absolute_dirpath=f"{abspath_to_proj}/{codegen_dirname}/{declared_module_as_filepath}",
        )

    def does_previous_inference_exist(self) -> bool:
        return os.path.exists(self.codegen_logic_filepath) and os.path.exists(
            self.codegen_metadata_filepath
        )

    def does_logic_exist(self) -> bool:
        return os.path.exists(self.codegen_logic_filepath)

    def load_metadata(self) -> FunctionMetadata | None:
        if not os.path.exists(self.codegen_metadata_filepath):
            return None
        try:
            with open(self.codegen_metadata_filepath, "r") as file:
                data = json.load(file)
            return FunctionMetadata.parse_obj(data)
        except Exception as e:
            print("unable to load metadata")
            return None

    def load_logic(self) -> str:
        with open(self.codegen_logic_filepath, "r") as file:
            return file.read()


# this func assumes generated directory is in project root
# could also add flexibity here to configure this in a toml, later
def build_generated_module_qualname(
    declared_module_qualname: str, inferred_func_qualname: str
):
    return f"{codegen_dirname}.{declared_module_qualname}.{inferred_func_qualname_to_filesystem_name(inferred_func_qualname)}"


def inferred_func_qualname_to_filesystem_name(qualname: str) -> str:
    return qualname.replace(".", "___")
