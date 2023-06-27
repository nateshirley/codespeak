from typing import Any, Callable, Dict, List, Tuple, TypeVar
from functools import wraps
from codespeak._core import executor
from codespeak._declaration.declaration_file_service import (
    DeclarationFileService,
)
from codespeak._declaration.declaration_resources import DeclarationResources
from codespeak._settings import _settings
from codespeak._clean import clean
from codespeak._settings.environment import Environment
from codespeak.inference import Inference, _Inference
from codespeak.inference.inference_attributes import InferenceAttributes
from codespeak.inference._inference_attributes import _InferenceAttributes
from codespeak.inference._resources import Resources
from codespeak.inference._tests import Tests
from codespeak.inference._body_resources import BodyResources
from codespeak.inference._programmable_resources import ProgrammableResources

# type inference remain on original function when no type hints are on the decorator


def infer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        def make_or_execute_inference(
            _inference: _Inference, args: Tuple[Any], kwargs: Dict[str, Any]
        ):
            if _inference.should_infer_new_source_code():
                response = _inference.make(
                    args=list(args),
                    kwargs=kwargs,
                    should_execute=True,
                )
                if _settings.should_auto_clean():
                    clean(_settings.abspath_to_codegen_dir())
                return response.execution_result
            else:
                return _inference.execute_latest_unsafe(*args, **kwargs)

        if wrapper.__is_prod__:  # type: ignore
            return wrapper.__logic__(*args, **kwargs)  # type: ignore
        else:
            nonlocal has_executed
            _inference = _Inference(wrapper)
            if not has_executed:
                with Inference.manager.manage_for(wrapper):
                    func(*args, **kwargs)
                _inference._try_add_self_definition(args, kwargs)

            has_executed = True
            return make_or_execute_inference(_inference, args, kwargs)

    has_executed = False
    assign_default_attributes(wrapper, func)
    return wrapper


def assign_default_attributes(wrapper: Callable, decorated_func: Callable):
    env = _settings.get_environment()
    setattr(wrapper, _InferenceAttributes.is_prod, env == Environment.PROD)
    if env == _settings.Environment.PROD:
        logic = executor.load_generated_logic_from_module_qualname(
            DeclarationFileService.gather_generated_module_qualname(
                decorated_func=decorated_func
            ),
            decorated_func.__name__,
        )
        setattr(wrapper, InferenceAttributes.logic, logic)
    elif env == _settings.Environment.DEV:
        file_service = DeclarationFileService.from_callable(decorated_func)
        setattr(wrapper, _InferenceAttributes.file_service, file_service)
        setattr(
            wrapper,
            InferenceAttributes.resources,
            Resources(
                declaration_resources=DeclarationResources.from_inferred_func(
                    inferred_func=decorated_func,
                ),
                body_resources=BodyResources.from_decorated_func(decorated_func),
                programmable_resources=ProgrammableResources(classes=[]),
            ),
        )
        setattr(wrapper, InferenceAttributes.tests, Tests())
