from typing import TypeVar


T = TypeVar("T")


def example(item: T) -> T:
    """a helper function to return an example of a type—demonstrates the type for static analysis"""
    return item
