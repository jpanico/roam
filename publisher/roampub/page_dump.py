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

def _validate_create_source(source: dict[str, Any], vertex_type: VertexType) -> MediaType:
    logging.debug(f"source: {source}, vertex_type: {vertex_type}")
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

