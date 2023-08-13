from typing import Any, Iterable
from collections.abc import ItemsView
import logging

logger = logging.getLogger(__name__)

def get_properties(cls: type[Any], include_supers: bool = False) -> dict[str,property]: 
    logger.debug(f"cls: {cls}")
    assert isinstance(cls, type)

    class_items: ItemsView[str,Any] = cls.__dict__.items()
    properties: dict[str,property] = {k:v for k,v in class_items if isinstance(v, property)}
    if ((not include_supers) or (cls is object)) :
        return properties

    return properties | get_properties(cls.__bases__[0])
    # (|) is the merge operator for built-in dict class: https://peps.python.org/pep-0584/


def get_property_names(cls: type[Any], include_supers: bool = False) -> Iterable[str]: 
    assert isinstance(cls, type)
    return get_properties(cls,include_supers).keys()


def get_property_values(target: Any, include_supers: bool = False)  -> dict[str,Any]: 
    property_names: Iterable[str] = get_property_names(type(target), include_supers)
    logger.debug(f"property_names: {property_names}")

    return get_attributes(target, property_names)


def get_attributes(target: Any, names: Iterable[str]) -> dict[str,Any]: 
    return {k:getattr(target, k) for k in names}


def has_attribute_value(target: Any, attr_name: str) -> bool: 
    return hasattr(target, attr_name) and (getattr(target, attr_name) is not None)


