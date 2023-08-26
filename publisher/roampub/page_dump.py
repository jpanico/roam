""" class to read PageDump generated .zip archives -- the output of PageDump.js
 
Classes:

    PageDump
    
    
Exceptions:

    BadPageDump


Functions:

    load_json_dump(Path) -> VertexMap
    read_page_dump_json(Path) -> list[dict[str, Any]]
    create_vertex_map(list[dict[str, Any]]) -> VertexMap
    create_roam_vertex(dict[str, Any]) -> RoamVertex
    create_page_node(dict[str, Any]) -> PageNode
    create_block_heading_node(dict[str, Any]) -> BlockHeadingNode
    create_block_content_node(dict[str, Any]) -> BlockContentNode
    create_file_vertex(dict[str, Any]) -> FileVertex


"""

from typing import Any, TextIO, Union, Tuple
import logging
from pathlib import Path, PurePath
from json import load, loads
from zipfile import ZipFile, ZipInfo

from common.collect import get_first_value
from roampub.roam_model import *

logger = logging.getLogger(__name__)


class PageDump:
    def __init__(self: Any, zip_path: Path): 
        if any(arg is None for arg in [zip_path]):
            raise ValueError("missing required arg")
        if not isinstance(zip_path, Path):
            raise TypeError(f"is not instanceof {Path}; zip_path: {zip_path}")
        
        # PEP 8: "Use one leading underscore only for non-public methods and instance variables."
        self._zip_file: ZipFile = ZipFile(zip_path, "r")
        _validate_zip_file(self._zip_file)

        self._vertex_map_json: str = None
        self._vertex_map: VertexMap = None

        self.vertex_map_json
        validation_result: ValidationResult = validate(self.vertex_map)
        logger.debug(f"validation_result: {validation_result}")
        if validation_result is not None:
            raise BadPageDump(validation_result)


    @property
    def zip_path(self) -> Path:
        """is read-only"""
        return Path(self._zip_file.filename)  # type: ignore


    @property
    def dump_name(self) -> str:
        """is read-only"""
        return self.zip_path.stem
    

    @property
    def vertex_map_json(self) -> str:
        """is read-only"""
        if self._vertex_map_json is not None:
            return self._vertex_map_json
        

        json_path: PurePath = PurePath(f"{self.dump_name}", f"{self.dump_name}.json")
        logger.debug(f"json_path: {json_path}")
        json_zipinfo: ZipInfo = self._zip_file.getinfo(json_path.as_posix())
        logger.debug(f"json_zipinfo: {json_zipinfo}")
        self._vertex_map_json: str = self._zip_file.read(json_zipinfo).decode(encoding="utf-8")
        logger.log(TRACE, f"_vertex_map_json: {self._vertex_map_json}")

        return self._vertex_map_json
    

    @property
    def vertex_map(self) -> VertexMap:
        if self._vertex_map is not None:
            return self._vertex_map
        
        json_objs: list[dict[str, Any]]  = loads(self.vertex_map_json)
        logger.log(TRACE, f"json_objs: {json_objs}")
        self._vertex_map = create_vertex_map(json_objs)

        return self._vertex_map


    @property
    def root_page(self) -> PageNode:
        return get_first_value(self.vertex_map) # type: ignore


    def get_items(self, keys: list[Uid]) -> VertexMap:
        items: dict[Uid, RoamVertex] =  {k:self.vertex_map[k] for k in keys}
        return OrderedDict(items)


    def get_file(self, key: Uid, include_content: bool = False) -> Union[ZipInfo, Tuple[ZipInfo, bytes]]:
        """
        Args:
            key (Uid): must be the Uid for a ROAM_FILE type RoamVertex; otherwise, an Error will be raised

        Returns:
            ``ZipInfo``: if ``include_content`` is ``False``
            ``Tuple[ZipInfo, bytes]``: if ``include_content`` is ``True``
        """        
        logger.log(TRACE, f"key: {key}, include_content: {include_content}")
        if any(arg is None for arg in [key, include_content]):
            raise ValueError("missing required arg")
        if not isinstance(key, Uid):
            raise TypeError(f"is not instanceof {Uid}; key: {key}")
    
        vertex: RoamVertex = self[key]
        logger.log(TRACE, f"vertex: {vertex}")
        if not isinstance(vertex, FileVertex):
            raise TypeError(f"is not instanceof {FileVertex}; vertex: {vertex}")
        file_vertex: FileVertex = cast(FileVertex, vertex)
        zip_item_path: PurePath = PurePath(f"{self.dump_name}", 'files', f"{file_vertex.file_name}")
        logger.log(TRACE, f"zip_item_path: {zip_item_path.as_posix()}")
        zip_info: ZipInfo = self._zip_file.getinfo(zip_item_path.as_posix())
        logger.log(TRACE, f"zip_info: {zip_info}")

        if not include_content:
            return zip_info
    
        content: bytes = self._zip_file.read(zip_info)
        return (zip_info, content)


    def extract_file(self, key: Uid, destination: Path) -> ZipInfo:
        logger.log(TRACE, f"key: {key}, destination: {destination}")
        if any(arg is None for arg in [key, destination]):
            raise ValueError("missing required arg")

        zip_info: ZipInfo = cast(ZipInfo, self.get_file(key, False))
        logger.log(TRACE, f"zip_info: {zip_info}")

        self._zip_file.extract(zip_info, destination)
        return zip_info


    def _vertex_type_counts(self) -> dict[str, int]:
        vertex_type_map: VertexTypeMap = to_vertex_type_map(self.vertex_map)

        return {vertex_type.name:len(vertex_type_map[vertex_type]) for vertex_type in list(VertexType) }


    def __len__(self):
        return len(self.vertex_map)


    def __getitem__(self, key: Uid) -> RoamVertex:
        return self.vertex_map[key]


    def __str__(self):
        clsname: str = type(self).__name__
        return f"{clsname}<{self.dump_name}>({self._vertex_type_counts()})"
    

def _validate_zip_file(zip_file: ZipFile) -> None:
    logging.debug(f"zip_file: {zip_file}")
    zip_path: Path = Path(zip_file.filename) # type: ignore
    logger.debug(f"zip_path: { zip_path}")
    dump_name: str = zip_path.stem
    logger.debug(f"dump_name: { dump_name}")
    info_list: list[ZipInfo] = zip_file.infolist()
    logger.debug(f"info_list: { info_list}")
    main_dir: ZipInfo = zip_file.getinfo(dump_name + '/')
    logger.debug(f"main_dir: { main_dir}")
    assert(main_dir.is_dir)


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
    
    vertices: list[RoamVertex] = [create_roam_vertex(json_obj) for json_obj in source]
    return OrderedDict([(v.uid, v) for v in vertices])


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


class BadPageDump(Exception):
    def __init__(self: Any, validation_failures: list[ValidationFailure]):
        self._validation_failures = validation_failures
        super().__init__(self._validation_failures.__str__)


    @property
    def validation_failures(self) -> list[ValidationFailure]:
        """is read-only"""
        return self._validation_failures