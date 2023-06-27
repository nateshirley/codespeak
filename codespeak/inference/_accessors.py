from typing import Callable
import copy
from codespeak.inference._resources import Resources
from codespeak.inference._tests import Tests
from codespeak.inference.inference_attributes import InferenceAttributes


def _set_resources_for_function(func: Callable, resources: Resources):
    if not hasattr(func, InferenceAttributes.resources):
        raise Exception(
            "No resources found. Make sure this is an inferred function—it should use codespeak's @infer decorator"
        )
    setattr(func, "__resources__", copy.deepcopy(resources))


def _get_resources_for_function(func: Callable) -> Resources:
    if not hasattr(func, InferenceAttributes.resources):
        raise Exception(
            "No resources found. Make sure this is an inferred function—it should use codespeak's @infer decorator"
        )
    resources: Resources = getattr(func, InferenceAttributes.resources)
    return resources


def _get_tests_for_function(func: Callable):
    if not hasattr(func, InferenceAttributes.tests):
        raise Exception(
            "No tests found. Make sure this is an inferred function—it should use codespeak's @infer decorator"
        )
    return getattr(func, InferenceAttributes.tests)


def _set_tests_for_function(func: Callable, tests: Tests):
    if not hasattr(func, InferenceAttributes.tests):
        raise Exception(
            "No tests found. Make sure this is an inferred function—it should use codespeak's @infer decorator"
        )
    setattr(func, "__tests__", copy.deepcopy(tests))


def _get_logic_for_function(func: Callable) -> Callable:
    if not hasattr(func, InferenceAttributes.logic):
        raise Exception(
            "No logic found. Make sure this is an inferred function—it should use codespeak's @infer decorator. The function will not have a logic attribute until it is first executed. Execute it by calling it."
        )
    return getattr(func, InferenceAttributes.logic)
