""" functions to read PageDump generated .zip archives -- the output of PageDump.js
 
Functions:

    read_page_dump(str) -> VertexMap
    create_page_node(dict) -> PageNode

"""

from typing import TypeAlias
import logging

from roampub.roam_model import *


def read_page_dump(file_path: str) -> VertexMap: 
    raise NotImplementedError

def create_page_node(source: dict[str, Any]) -> PageNode: 
    if not source:
        raise ValueError("missing required arg")
    
    if not source['vertex-type'] == VertexType.ROAM_PAGE._value_:
        raise ValueError(f"``vertex-type`` is not {VertexType.ROAM_PAGE} for ``source``: {source}")
    
    return PageNode(
        source['uid'],
        source['media-type'],
        source['text'],
        source.get('children'),
        source.get('references'),
    )

