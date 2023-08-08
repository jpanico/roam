""" utility functions for working with Collections

Functions:

    get_first(Iterable)
    get_first_item(Iterable)
    get_first_key(Mapping)
    get_first_value(Mapping)
    get_last(Iterable)
    get_last_item(Iterable)
    get_last_key(Mapping)
    get_last_value(Mapping)

"""

from typing import TypeVar, cast
from collections.abc import Iterable, Mapping

T = TypeVar('T')    # Declare type variable "T"
K = TypeVar('K')
V = TypeVar('V')


def get_first(collect: Iterable[T]) -> T:
    if any(arg is None for arg in (collect)):
        raise ValueError("missing required arg")
    if not collect:
        return cast(T, None)
    return next(iter(collect))


def get_first_item(collect: Iterable[T]) -> T:
    if any(arg is None for arg in (collect)):
        raise ValueError("missing required arg")
    if not collect:
        return cast(T, None)
    if isinstance(collect, Mapping):
        return next(iter(collect.items())) # type: ignore
       
    return next(iter(collect))


def get_first_key(map: Mapping[K,V]) -> K:
    if any(arg is None for arg in (map)):
        raise ValueError("missing required arg")
    if not map:
        return cast(K, None)
    return next(iter(map.keys())) # type: ignore


def get_first_value(map: Mapping[K,V]) -> V:
    if any(arg is None for arg in (map)):
        raise ValueError("missing required arg")
    if not map:
        return cast(V, None)
    return next(iter(map.values())) # type: ignore


def get_last(collect: Iterable[T]) -> T:
    if any(arg is None for arg in (collect)):
        raise ValueError("missing required arg")
    if not collect:
        return cast(T, None)
    *_, last = collect    
    return last


def get_last_item(collect: Iterable[T]) -> T:
    if any(arg is None for arg in (collect)):
        raise ValueError("missing required arg")
    if not collect:
        return cast(T, None)
    if isinstance(collect, Mapping):
        *_, last = collect.items()    
        return last # type: ignore
    *_, last = collect    
    return last


def get_last_key(map: Mapping[K,V]) -> K:
    if any(arg is None for arg in (map)):
        raise ValueError("missing required arg")
    if not map:
        return cast(K, None)
    *_, last = map.keys()
    return last


def get_last_value(map: Mapping[K,V]) -> V:
    if any(arg is None for arg in (map)):
        raise ValueError("missing required arg")
    if not map:
        return cast(V, None)
    *_, last = map.values()
    return last