"""cleans out codespeak_inferred directory and removes unused functions"""
import os
import fnmatch
import shutil
from typing import Any
from importlib import import_module

from codespeak.constants import metadata_file_prefix, codegen_dirname

# if run as command, assume that it's in the same directory as the codespeak_inferred directory
# otherwise, get the rootpath and use that


def extract_modulepath(abs_filepath: str):
    # Split the path into parts
    path_parts = abs_filepath.split(os.sep)

    # Check if root_dir_name is in path_parts
    if codegen_dirname not in path_parts:
        raise ValueError(
            f"Root directory '{codegen_dirname}' not found in the filepath"
        )

    # Find the index of root_dir_name in path_parts
    # add one to get the index of the first part after root_dir_name
    root_index = path_parts.index(codegen_dirname) + 1

    # Keep only the parts from root_dir_name up to the second last part (excluding the filename)
    module_parts = path_parts[root_index:-1]

    # Join the parts with dots to form the module path
    module_path = ".".join(module_parts)

    return module_path


def contains_codegen_files(directory):
    for root, dirs, files in os.walk(directory):
        for _ in fnmatch.filter(files, "*.py"):
            return True
        for _ in fnmatch.filter(files, "*.json"):
            return True
    return False


def remove_metadata(root: str, system_name: str):
    expected_path = f"{root}/metadata/{metadata_file_prefix}{system_name}.json"
    if os.path.exists(expected_path):
        os.remove(expected_path)


def remove_logic_file(root: str, system_name: str):
    expected_path = f"{root}/{system_name}.py"
    if os.path.exists(expected_path):
        os.remove(expected_path)


def try_remove_empty_directory(root: str):
    if os.path.basename(root) == "__pycache__":
        return None
    if not contains_codegen_files(root):
        shutil.rmtree(root)


def system_name_to_func_qualname(system_name: str):
    return system_name.replace("___", ".")


def remove_unused_generated_code(codegen_directory_abspath: str):
    clean_count = 0
    for root, dirs, files in os.walk(codegen_directory_abspath):
        for filename in fnmatch.filter(files, "*.py"):
            abs_filepath = os.path.join(root, filename)
            modulepath = extract_modulepath(abs_filepath)
            system_name = filename.replace(".py", "")
            function_qualname = system_name_to_func_qualname(system_name=system_name)
            function_exists = check_function_exists(modulepath, function_qualname)
            if not function_exists:
                print("deleting undeclared codegen for", modulepath, function_qualname)
                remove_logic_file(root, system_name=system_name)
                remove_metadata(root, system_name=system_name)
                try_remove_empty_directory(root)
                clean_count += 1
    return clean_count


from typing import Any


def has_attr_from_qualname(obj: Any, qualname: str) -> bool:
    try:
        attrs = qualname.split(".")
        for attr in attrs:
            obj = getattr(obj, attr)
        return True
    except AttributeError:
        return False


def check_function_exists(modulepath: str, func_qualname: str):
    try:
        module = import_module(modulepath)
    except Exception as e:
        return False
    return has_attr_from_qualname(module, func_qualname)


# from cwd
def codegen_directory_abspath() -> str:
    cwd = os.getcwd()
    # Look for "codespeak_inferred" in the current directory
    expected_path = os.path.join(cwd, codegen_dirname)
    if not os.path.isdir(expected_path):
        raise Exception(
            f"Couldn't find 'codespeak_inferred' directory, run from project root that contains 'codespeak_inferred'"
        )
    return expected_path


def clean(codegen_directory_abspath: str):
    remove_unused_generated_code(codegen_directory_abspath=codegen_directory_abspath)


def main():
    clean_count = remove_unused_generated_code(
        codegen_directory_abspath=codegen_directory_abspath()
    )
    if clean_count > 0:
        print("Cleaned artifacts for ", clean_count, " codespeak functions.")
    else:
        print("Detected zero recently deleted codespeak functions.")
    print("Done cleaning.\n")


if __name__ == "__main__":
    main()
