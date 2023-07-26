from .function import WritableFunction
from .settings.settings import (
    set_verbose,
    set_environment,
    add_api,
    set_interactive_mode,
    remove_api,
)
from .public.dot_get import dot_get
from .public.rest_requests.get import get
from .public.rest_requests.post import post
from .public.rest_requests.put import put
from .public.rest_requests.delete import delete
from .public.inferred_exception import InferredException
from .decorate.writable import writable
