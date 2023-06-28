import inspect
from typing import Callable


def auto_detect_abspath_to_project_root(object_in_project_abspath: str):
    import os

    setup_files = [
        "requirements.txt",
        "Pipfile",
        "pyproject.toml",
        "setup.py",
        "environment.yml",
    ]

    current_directory = object_in_project_abspath

    while current_directory != "/":
        for file in setup_files:
            if os.path.exists(os.path.join(current_directory, file)):
                return current_directory

        current_directory = os.path.dirname(current_directory)

    raise Exception(
        "Unable to find root directory of project where codespeak is installed. make sure you have a pyproject.toml file in your project root."
    )
