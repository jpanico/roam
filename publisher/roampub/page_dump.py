""" functions to read PageDump generated .zip archives -- the output of PageDump.js
 
Functions:

    read_page_dump(str) -> VertexMap
    create_page_node(dict) -> PageNode

"""

from typing import TypeAlias, Any, TextIO
import logging
from json import load

from roampub.roam_model import *


def read_page_dump_json(file_path: str) -> list[dict[str, Any]]: 
    logging.debug(f"file_path: {file_path}")
    if any(arg is None for arg in (file_path)):
        raise ValueError("missing required arg")

    jsonFile: TextIO = open(file_path)
    logging.debug(f"jsonFile: {jsonFile}")
    return load(jsonFile)


def create_vertex_map(source: list[dict[str, Any]]) -> VertexMap: 
    logging.debug(f"source: {source}")
    if any(arg is None for arg in (source)):
        raise ValueError("missing required arg")
    
    vertices: list[RoamVertex] = [create_roam_vertex(i) for i in source]
    return OrderedDict([(v.uid, v) for v in vertices])

def create_roam_vertex(source: dict[str, Any]) -> RoamVertex: 
    logging.debug(f"source: {source}")

    vertex_type: VertexType = VertexType(source['vertex-type'])
    logging.debug(f"vertex_type: {vertex_type}")
    if vertex_type is VertexType.ROAM_PAGE:
        return create_page_node(source)
    elif vertex_type is VertexType.ROAM_BLOCK_CONTENT:
        return create_block_content_node(source)
    elif vertex_type is VertexType.ROAM_BLOCK_HEADING:
        return create_block_heading_node(source)
    elif vertex_type is VertexType.ROAM_FILE:
        return create_file_vertex(source)
    else:
        raise ValueError(f"unrecognized vertex_type: {vertex_type}")
        
def _validate_create_source(source: dict[str, Any], vertex_type: VertexType) -> MediaType:
    if not source:
        raise ValueError("missing required arg")
    
    if not source['vertex-type'] == vertex_type.value:
        raise ValueError(f"``vertex-type`` is not {vertex_type} for ``source``: {source}")
    
    # convert MediaType enum value to enum member
    return MediaType(source['media-type'])

def create_page_node(source: dict[str, Any]) -> PageNode: 

    media_type = _validate_create_source(source, VertexType.ROAM_PAGE)
    return PageNode(
        source['uid'],
        media_type,
        source['text'],
        source.get('children'),
        source.get('refs'),
    )

def create_block_heading_node(source: dict[str, Any]) -> BlockHeadingNode: 

    media_type = _validate_create_source(source, VertexType.ROAM_BLOCK_HEADING)
    return BlockHeadingNode(
        source['uid'],
        media_type,
        source['heading'],
        source['level'],
        source.get('children'),
        source.get('refs'),
    )

def create_block_content_node(source: dict[str, Any]) -> BlockContentNode: 

    media_type = _validate_create_source(source, VertexType.ROAM_BLOCK_CONTENT)
    return BlockContentNode(
        source['uid'],
        media_type,
        source['text'],
        source.get('children'),
        source.get('refs'),
    )

def create_file_vertex(source: dict[str, Any]) -> FileVertex: 

    media_type = _validate_create_source(source, VertexType.ROAM_FILE)
    return FileVertex(
        source['uid'],
        media_type,
        source['file-name'],
        source['source']
    )

