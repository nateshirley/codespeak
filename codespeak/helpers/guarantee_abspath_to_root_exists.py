import inspect
from typing import Any
from codespeak.helpers.auto_detect_abspath_to_project_root import (
    auto_detect_abspath_to_project_root,
)
from codespeak.settings import settings


def guarantee_abspath_to_project_root_exists(object_in_project: Any):
    if settings._settings.abspath_to_project_root is None:
        path = inspect.getabsfile(object_in_project)
        settings.set_abspath_to_project_root(auto_detect_abspath_to_project_root(path))
