""" functions to read PageDump generated .zip archives -- the output of PageDump.js
 
Functions:

    read_page_dump(str) -> VertexMap
    create_page_node(dict) -> PageNode

"""

from typing import TypeAlias, Any, Tuple, TextIO
import logging
from pathlib import Path
from json import load
from zipfile import ZipFile

from roampub.roam_model import *

logger = logging.getLogger(__name__)

class PageDump:
    def __init__(self: Any, zip_path: Path): 
        if any(arg is None for arg in [zip_path]):
            raise ValueError("missing required arg")
        if not isinstance(zip_path, Path):
            raise TypeError(f"is not instanceof {Path}; zip_path: {zip_path}")
        
        # PEP 8: "Use one leading underscore only for non-public methods and instance variables."
        self._zip_path = zip_path
        self._vertex_map = None

    @property
    def zip_path(self) -> Path:
        """is read-only"""
        return self._zip_path

    @property
    def vertex_map(self) -> VertexMap:
        assert self._vertex_map is not None
        return self._vertex_map


def read_page_dump_json(file_path: Path) -> list[dict[str, Any]]: 
    logger.info(f"file_path: {file_path}")
    if any(arg is None for arg in [file_path]):
        raise ValueError("missing required arg")
    if not isinstance(file_path, Path):
        raise TypeError(f"is not instanceof {Path}; file_path: {file_path}")
    jsonFile: TextIO = open(file_path)
    logger.info(f"jsonFile: {jsonFile}")
    return load(jsonFile)


def create_vertex_map(source: list[dict[str, Any]]) -> VertexMap: 
    logger.debug(f"source: {source}")
    if any(arg is None for arg in (source)):
        raise ValueError("missing required arg")
    
    vertices: list[RoamVertex] = [create_roam_vertex(i) for i in source]
    return OrderedDict([(v.uid, v) for v in vertices])


def load_zip_dump(zip_path: Path) -> Tuple[ZipFile, VertexMap]:
    raise NotImplementedError


def load_json_dump(json_path: Path) ->  VertexMap:
    logger.info(f"json_path: {json_path}")
    if not json_path:
        raise ValueError("missing required arg")
    
    json_objs: list[dict[str, Any]] = read_page_dump_json(json_path)
    logger.debug(f"json_objs: {json_objs}")
    return create_vertex_map(json_objs)


def create_roam_vertex(source: dict[str, Any]) -> RoamVertex: 
    logger.debug(f"source: {source}")

    # comparing a string (the value from source dict) to an Enum value only works because VertexType is a StrEnum
    match source['vertex-type']:
        case VertexType.ROAM_PAGE:
            return create_page_node(source)
        case VertexType.ROAM_BLOCK_CONTENT:
            return create_block_content_node(source)
        case VertexType.ROAM_BLOCK_HEADING:
            return create_block_heading_node(source)
        case VertexType.ROAM_FILE:
            return create_file_vertex(source)
        case _:
            raise ValueError(f"unrecognized vertex_type: {source['vertex-type']}")
    

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
        source['text'],
        source['heading'],
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

