""" Model of the elements that appear in PageDump generated JSON files -- the output of ``PageDump.js``
 
Types:

    Uid
    VertexMap
    ValidationFailure
    ValidationResult
    Validation

    
Enums:

    VertexType
    MediaType

    
Classes:

    RoamVertex
    RoamNode
    PageNode
    BlockHeadingNode
    BlockContentNode
    FileVertex
    ValidationRule

    
Functions:

    validate(VertexMap) -> ValidationResult

"""

from typing import TypeAlias, Any, Optional, Callable, Final, NamedTuple, cast
from abc import ABC, abstractmethod
from enum import StrEnum, unique
from collections import OrderedDict, Counter
from functools import reduce, partial
import logging

from common.types import Url
from common.introspect import get_property_values, has_attribute_value
from common.log import TRACE

logger = logging.getLogger(__name__)

Uid: TypeAlias = str
"""
Type for the values that pair with the key "uid" in PageDump.json.
    - if the Vertex corresponds 1-1 with a Roam Node (VertexType.is_roam_node == True), then uid is the Roam
        generated uid value 
    - if the Vertex is not 1-1 with a Roam Node (VertexType.is_roam_node == False), it was injected by PageDump.js and
        uid is a GUID generated by PageDump.js
"""

@unique
class VertexType(StrEnum):
    ROAM_PAGE = 'roam/page'
    ROAM_BLOCK_CONTENT = 'roam/block-content'
    ROAM_BLOCK_HEADING = 'roam/block-heading'
    ROAM_FILE = 'roam/file'
    

    def __str__(self):
        return f"{self.__class__.__name__}.{self._name_}"


@unique
class MediaType(StrEnum):
    TEXT_PLAIN = 'text/plain'
    TEXT_MARKDOWN = 'text/markdown'
    IMAGE_JPEG = 'image/jpeg'

    def __str__(self):
        return f"{self.__class__.__name__}.{self._name_}"


class RoamVertex(ABC):
    """
    A struct representing a single Vertex that is output by PageDump.js

    ...

    Attributes
    ----------
    uid : Uid
        see ``Uid: TypeAlias`` for description of semantics

    vertex_type : VertexType
        this is abstract -- concrete value is hardwired into subclasses
        
    media_type : MediaType
        https://en.wikipedia.org/wiki/Media_type
        https://www.iana.org/assignments/media-types/media-types.xhtml
    """

    def __init__(self: Any, uid: Uid, media_type: MediaType): 
        if any(arg is None for arg in (uid, media_type)):
            raise ValueError("missing required arg")
        if not isinstance(media_type, MediaType):
            raise TypeError(f"is not instanceof {MediaType}; media_type: {media_type}")
        
        # PEP 8: "Use one leading underscore only for non-public methods and instance variables."
        self._uid = uid
        self._media_type = media_type

    @property
    def uid(self) -> Uid:
        """is read-only"""
        return self._uid

    @property
    def media_type(self) -> MediaType:
        """is read-only"""
        return self._media_type
    
    @property
    @abstractmethod
    def vertex_type(self) -> VertexType:
        """is read-only"""
        pass

    def __repr__(self):
        clsname: str = type(self).__name__
        uid_string: str = self.uid[-9:] if len(self.uid) > 9 else self.uid
        property_values: dict[str,Any] = get_property_values(self, True)
        logger.log(TRACE, f"property_values: {property_values}")
        # filter out the properties that are defined by this class
        property_values = {k:v for k,v in property_values.items() if k not in ['uid', 'vertex_type', 'media_type']}
        return f"{clsname}<{uid_string}>({self.vertex_type}, {self.media_type}, {property_values})"


VertexMap: TypeAlias = OrderedDict[Uid, 'RoamVertex']
"""
The ``VertexMap`` preserves the item order from the PageDump.json file.
"""


class RoamNode(RoamVertex):

    def __init__(self: Any, uid: Uid, media_type: MediaType, children: Optional[list[Uid]] =[], 
                 references: Optional[list[Uid]] =[]): 
        self._children= children
        self._references= references
        super().__init__(uid, media_type)

    @property
    def children(self) -> Optional[list[Uid]]:
        """is read-only"""
        return self._children

    @property
    def references(self) -> Optional[list[Uid]]:
        """is read-only"""
        return self._references


class PageNode(RoamNode):

    def __init__(self: Any, uid: Uid, media_type: MediaType, title: str, children: Optional[list[Uid]] =[], 
                 references: Optional[list[Uid]] =[]): 
        if any(arg is None for arg in (title)):
            raise ValueError("missing required arg")

        self._title = title
        super().__init__(uid, media_type, children, references)

    @property
    def title(self) -> str:
        return self._title
    

    @property
    def vertex_type(self) -> VertexType:
        return VertexType.ROAM_PAGE


class BlockHeadingNode(RoamNode):

    def __init__(self: Any, uid: Uid, media_type: MediaType, heading: str, level: int, 
                 children: Optional[list[Uid]] =[], references: Optional[list[Uid]] =[]): 
        if any(arg is None for arg in (heading, level)):
            raise ValueError("missing required arg")

        self._heading = heading
        self._level = level
        super().__init__(uid, media_type, children, references)

    @property
    def heading(self) -> str:
        return self._heading

    @property
    def level(self) -> int:
        return self._level

    @property
    def vertex_type(self) -> VertexType:
        return VertexType.ROAM_BLOCK_HEADING


class BlockContentNode(RoamNode):

    def __init__(self: Any, uid: Uid, media_type: MediaType, content: str, children: Optional[list[Uid]] =[], 
                 references: Optional[list[Uid]] =[]): 
        self._content = content
        super().__init__(uid, media_type, children, references)

    @property
    def content(self) -> str:
        return self._content
    

    @property
    def vertex_type(self) -> VertexType:
        return VertexType.ROAM_BLOCK_CONTENT


class FileVertex(RoamVertex):

    def __init__(self: Any, uid: Uid, media_type: MediaType, file_name: str, source: Url): 
        if any(arg is None for arg in (file_name, source)):
            raise ValueError("missing required arg")

        self._file_name = file_name
        self._source = source
        super().__init__(uid, media_type)

    @property
    def file_name(self) -> str:
        return self._file_name
    
    @property
    def source(self) -> Url:
        return self._source

    @property
    def vertex_type(self) -> VertexType:
        return VertexType.ROAM_FILE


def all_linked_uids(link_name: str, graph: VertexMap) -> list[Uid]:
    """
    there are 2 kinds of ``link``s amongst RoamNodes: ``children`` and ``references``
    """
    logger.log(TRACE, f"link_name: {link_name}, graph: {graph}")
    if any(arg is None for arg in (link_name, graph)):
        raise ValueError("missing required arg")
    if not isinstance(graph, VertexMap.__origin__): # type: ignore
        raise TypeError()
    if len(graph) == 0: 
        return []
            
    accumulate_func: Callable[[list[Uid], RoamVertex], list[Uid]] = partial(_accumulate_linked_uids, link_name)
    return list(reduce(accumulate_func, graph.values(), []))


def _accumulate_linked_uids(link_name: str, accumulator: list[Uid], vertex: RoamVertex) -> list[Uid]:
    """
    there are 2 kinds of ``link``s amongst RoamNodes: ``children`` and ``references``
    """
    logger.log(TRACE, f"link_name: {link_name}, accumulator: {accumulator}, vertex: {vertex}")
    if any(arg is None for arg in (link_name, accumulator, vertex)):
        raise ValueError("missing required arg")
    if not isinstance(vertex, RoamNode):
        return accumulator
    
    node: RoamNode = cast(RoamNode, vertex)
    linked: Optional[list[Uid]] = getattr(node, link_name)
    if not linked:
        return accumulator

    return accumulator + linked


ValidationFailure = NamedTuple("ValidationFailure", [('rule', 'ValidationRule'), ('failure_message', str)])
ValidationResult: TypeAlias = Optional[list[ValidationFailure]]
Validation: TypeAlias = Callable[['ValidationRule', VertexMap], ValidationResult]


class ValidationRule(NamedTuple):
    name: str
    description: str
    impl: Validation

    def validate(self, graph: VertexMap) -> ValidationResult: 
        logger.debug(f"rule: {self}")
        if graph is None: 
            return None
    
        if not isinstance(graph, VertexMap.__origin__): # type: ignore
            raise TypeError()
    
        return self.impl(self, graph)


def validate_root_page(rule: ValidationRule, graph: VertexMap) -> ValidationResult:
    first_vertex: RoamVertex = list(graph.items())[0][1]
    logger.debug(f"first_node: {first_vertex}")

    if( first_vertex.vertex_type is VertexType.ROAM_PAGE):
        return None
    
    failure_message: str = f"is not {VertexType.ROAM_PAGE}; first vertex: {first_vertex}"
    return [ValidationFailure(rule, failure_message)]


ROOT_PAGE_RULE: Final[ValidationRule] = ValidationRule(
    'RootPageRule', 
    'first RoamVertex in the map is a PageNode; the root of the graph', 
    validate_root_page
)


def validate_children_exist(rule: ValidationRule, graph: VertexMap) -> ValidationResult:
    node_children: list[Uid] = all_linked_uids('children', graph)
    dangling_children: list[Uid] = list(filter(lambda uid: not uid in graph, node_children))
    logger.debug(f"dangling_children: {dangling_children}")

    if not dangling_children:
        return None
    
    # N.B. parens are just for formatting long lines-- PEP 8
    failure_message: str = (
        f"Uids found in ``children`` attributes are not vertices of ``graph``; dangling_children: {dangling_children}"
    )
    return [ValidationFailure(rule, failure_message)]


CHILDREN_EXIST_RULE: Final[ValidationRule] = ValidationRule(
    'ChildrenExistRule', 
    'all ``Uid`` values appearing in ``children`` have corresponding entry in VertexMap', 
    validate_children_exist
)


def validate_references_exist(rule: ValidationRule, graph: VertexMap) -> ValidationResult:
    node_references: list[Uid] = all_linked_uids('references', graph)
    dangling_references: list[Uid] = list(filter(lambda uid: not uid in graph, node_references))
    logger.debug(f"dangling_references: {dangling_references}")

    if not dangling_references:
        return None
    
    # N.B. parens are just for formatting long lines-- PEP 8
    failure_message: str = (
        f"Uids found in ``references`` attributes are not vertices of ``graph``; dangling_references: {dangling_references}"
    )
    return [ValidationFailure(rule, failure_message)]


REFERENCES_EXIST_RULE: Final[ValidationRule] = ValidationRule(
    'ReferencesExistRule', 
    'all ``Uid`` values appearing in ``references`` have corresponding entry in VertexMap', 
    validate_references_exist
)


def validate_block_parents_exist(rule: ValidationRule, graph: VertexMap) -> ValidationResult:
    all_block_nodes: list[RoamVertex] = (
        list(filter(lambda v: v.vertex_type in [VertexType.ROAM_BLOCK_HEADING, VertexType.ROAM_BLOCK_CONTENT], 
                    graph.values()
                )
        )
    )
    logger.log(TRACE, f"all_block_nodes: {all_block_nodes}")

    if not all_block_nodes:
        return None
    
    all_block_uids: list[Uid] = list(map(lambda b: b.uid, all_block_nodes))
    all_children_uids: list[Uid] = all_linked_uids('children', graph)
    children_counter: Counter[Uid] = Counter(all_children_uids)
    logger.log(TRACE, f"children_counter: {children_counter}")
    invalids: dict[Uid, int] = {k:v for (k,v) in children_counter.items() if ((k in all_block_uids) and (v > 1))}
    logger.log(logging.DEBUG if invalids else TRACE, f"invalids: {invalids}")
    if not invalids:
        return None    

    failure_message: str = (
        f"block ``Uids`` with invalid number of parents: {invalids}"
    )
    return [ValidationFailure(rule, failure_message)]


BLOCK_PARENTS_EXIST_RULE: Final[ValidationRule] = ValidationRule(
    'BlockParentsExistRule', 
    'every (BlockHeadingNode | BlockContentNode) ``Uid`` must appear in exactly 1 ``children`` lists', 
    validate_block_parents_exist
)


def validate_children_vertex_types(rule: ValidationRule, graph: VertexMap) -> ValidationResult:
    all_children_uids: list[Uid] = all_linked_uids('children', graph)
    if not all_children_uids:
        return None

    invalid_children_vertices: list[RoamVertex] = (
        [
            graph[uid] 
            for uid in all_children_uids 
            if graph[uid].vertex_type in [VertexType.ROAM_PAGE, VertexType.ROAM_FILE]
        ]
    )
    logger.log(
        logging.DEBUG if invalid_children_vertices else TRACE, 
        f"invalid_children_vertices: {invalid_children_vertices}"
    )
    if not invalid_children_vertices:
        return None    

    failure_message: str = (
        f"(PageNode | FileVertex)s appearing as children: {invalid_children_vertices}"
    )
    return [ValidationFailure(rule, failure_message)]


CHILDREN_VERTEX_TYPES_RULE: Final[ValidationRule] = ValidationRule(
    'ChildrenVertexTypesRule', 
    'no (PageNode | FileVertex) ``Uid`` can appear in any ``children`` lists', 
    validate_children_vertex_types
)


def _validate_node_children(
        rule: ValidationRule, node_type: VertexType, valid_children_types: list[VertexType], graph: VertexMap
    ) -> ValidationResult:

    logger.log(TRACE, f"node_type: {node_type}, valid_children_types: {valid_children_types}")
    target_nodes: list[RoamNode] = (
        cast(list[RoamNode], [v for v in graph.values() if v.vertex_type is node_type])
    )
    logger.log(TRACE, f"target_nodes: {target_nodes}")
    all_target_children: list[list[Uid]] = (
        [node.children for node in target_nodes if node.children is not None]
    )
    logger.log(TRACE, f"all_target_children: {all_target_children}")
    flat_target_children: list[Uid] = list(reduce(lambda accum, iter_val: accum + iter_val, all_target_children, [])) 
    logger.log(TRACE, f"flat_target_children: {flat_target_children}")
    invalid_children: list[Uid] = (
        [
            child_id for child_id in flat_target_children 
            if graph[child_id].vertex_type not in valid_children_types
        ]
    )
    logger.log(TRACE, f"invalid_children: {invalid_children}")
    if not invalid_children:
        return None  

    failure_message: str = (
        f"invalid_children: {invalid_children}"
    )
    return [ValidationFailure(rule, failure_message)]


def validate_page_node_children(rule: ValidationRule, graph: VertexMap) -> ValidationResult:
    return (
        _validate_node_children(
            rule, VertexType.ROAM_PAGE, [VertexType.ROAM_BLOCK_CONTENT, VertexType.ROAM_BLOCK_HEADING], graph
        )
    )


PAGE_NODE_CHILDREN_RULE: Final[ValidationRule] = ValidationRule(
    'PageNodeChildrenRule', 
    'all ``children`` of ``PageNode`` are (BlockHeadingNode | BlockContentNode)', 
    validate_page_node_children
)


def validate_block_heading_children(rule: ValidationRule, graph: VertexMap) -> ValidationResult:
    return (
        _validate_node_children(
            rule, VertexType.ROAM_BLOCK_HEADING, [VertexType.ROAM_BLOCK_CONTENT, VertexType.ROAM_BLOCK_HEADING], graph
        )
    )


BLOCK_HEADING_CHILDREN_RULE: Final[ValidationRule] = ValidationRule(
    'BlockHeadingChildrenRule', 
    'all ``children`` of ``BlockHeadingNode`` are (BlockHeadingNode | BlockContentNode)', 
    validate_block_heading_children
)


def _validate_attribute_appearance(
        rule: ValidationRule, attribute_name: str, valid_carrier_types: list[VertexType], graph: VertexMap
    ) -> ValidationResult:

    logger.log(TRACE, f"attribute_name: {attribute_name}, valid_carrier_types: {valid_carrier_types}")
    carrier_nodes: list[RoamNode] = (
        cast(list[RoamNode], [v for v in graph.values() if has_attribute_value(v, attribute_name)])
    )
    logger.log(TRACE, f"carrier_nodes: {carrier_nodes}")
    invalid_carrier_nodes: list[RoamNode] = (
        [ node for node in carrier_nodes if node.vertex_type not in valid_carrier_types ]
    )
    logger.log(TRACE, f"invalid_carrier_nodes: {invalid_carrier_nodes}")
    if not invalid_carrier_nodes:
        return None  

    failure_message: str = (
        f"invalid_carrier_nodes: {invalid_carrier_nodes}"
    )
    return [ValidationFailure(rule, failure_message)]


def validate_children_attribute_appearance(rule: ValidationRule, graph: VertexMap) -> ValidationResult:
    return (
        _validate_attribute_appearance(
            rule, 'children', 
            [VertexType.ROAM_PAGE, VertexType.ROAM_BLOCK_CONTENT, VertexType.ROAM_BLOCK_HEADING], 
            graph
        )
    )


CHILDREN_ATTRIBUTE_APPEARANCE_RULE: Final[ValidationRule] = ValidationRule(
    'ChildrenAttributeAppearanceRule', 
    '``children`` attribute can only appear on (PageNode | BlockHeadingNode | BlockContentNode)', 
    validate_children_attribute_appearance
)


def validate_references_attribute_appearance(rule: ValidationRule, graph: VertexMap) -> ValidationResult:
    return (
        _validate_attribute_appearance(rule, 'references', [VertexType.ROAM_BLOCK_CONTENT], graph)
    )


REFERENCES_ATTRIBUTE_APPEARANCE_RULE: Final[ValidationRule] = ValidationRule(
    'ReferencesAttributeAppearanceRule', 
    '``references`` attribute can only appear on (BlockContentNode)', 
    validate_references_attribute_appearance
)


def content_contains_reference(target: str, ref: str) -> bool:
    logger.log(TRACE, f"target: {target}, ref: {ref}")
    if any(arg is None for arg in [target, ref]):
        raise ValueError("missing required arg")
    
    valid_ref_strs: list[str] = [f'[[{ref}]]', f'(({ref}))', f'<<{ref}>>']
    logger.log(TRACE, f"valid_ref_strs: {valid_ref_strs}")
    contains: bool = any(r in target for r in valid_ref_strs)
    logger.log(TRACE, f"contains: {contains}")

    return contains


def dangling_references(target: BlockContentNode) -> Optional[list[Uid]]:
    logger.log(TRACE, f"target: {target}")

    if not target.references:
        return None
    
    dangling_refs: list[Uid] = [r for r in target.references if not content_contains_reference(target.content, r)]
    logger.log(TRACE, f"dangling_refs: {dangling_refs}")

    if not dangling_refs:
        return None
    
    return dangling_refs


def validate_references_appear_in_content(rule: ValidationRule, graph: VertexMap) -> ValidationResult:
    all_referencing: list[BlockContentNode] = cast(list[BlockContentNode], 
        [v for v in graph.values() if has_attribute_value(v, 'references')]
    )
    logger.log(TRACE, f"all_referencing: {all_referencing}")

    if not all_referencing:
        return None

    danglers: dict[Uid, list[Uid]] = (
        {
            node.uid: dangling_references(node) 
            for node in all_referencing
            if dangling_references(node) is not None
        }
    ) # type: ignore

    if not danglers:
        return None
    
    failure_message: str = f"references not appearing in content: {danglers}"
    return [ValidationFailure(rule, failure_message)]


REFERENCES_APPEAR_IN_CONTENT_RULE: Final[ValidationRule] = ValidationRule(
    'ReferencesAppearInContentRules', 
    'all ``references`` of BlockContentNode appear in the ``content``, each formatted as a valid ref format type', 
    validate_references_appear_in_content
)


ALL_RULES: Final[list[ValidationRule]] = [
    # simply comment out any rules you wish to disable
    ROOT_PAGE_RULE,
    CHILDREN_EXIST_RULE,
    REFERENCES_EXIST_RULE,
    BLOCK_PARENTS_EXIST_RULE,
    CHILDREN_VERTEX_TYPES_RULE,
    PAGE_NODE_CHILDREN_RULE,
    BLOCK_HEADING_CHILDREN_RULE,
    CHILDREN_ATTRIBUTE_APPEARANCE_RULE,
    REFERENCES_ATTRIBUTE_APPEARANCE_RULE,
    REFERENCES_APPEAR_IN_CONTENT_RULE,
]


def validate(graph: VertexMap) -> ValidationResult: 
    """Checks all of the invariants that should hold for a Roam/PageDump graph

    validations:
    - first RoamVertex in the map is a PageNode; the root of the graph
    - all ``Uid`` values appearing in ``children`` have corresponding entry in VertexMap
    - all ``Uid`` values appearing in ``references`` have corresponding entry in VertexMap
    - every (BlockHeadingNode | BlockContentNode) ``Uid`` must appear in exactly 1 ``children`` lists
    - no (PageNode | FileVertex) ``Uid`` can appear in any ``children`` lists
    - all ``children`` of ``PageNode`` are (BlockHeadingNode | BlockContentNode)
    - all ``children`` of ``BlockHeadingNode`` are ``BlockContentNode``
    - ``children`` attribute can only appear on (PageNode | BlockHeadingNode | BlockContentNode)
    - ``references`` attribute can only appear on (BlockContentNode)
    - all ``references`` of BlockContentNode appear in the ``content``, each formatted as a valid ref format type
    
    Parameters
    ----------
    graph : VertexMap
        the graph to check

    Returns
    -------
    ValidationResult === (None | list[ValidationFailure])
    - None: if there are no validation failures
    - list[ValidationFailure] === list[description of validation failure encountered]
    """
    logger.info(f"graph: {graph}")
    results: list[ValidationResult] = [rule.validate(graph) for rule in ALL_RULES]
    logger.info(f"results: {results}")
    results: list[ValidationResult] = list(filter(lambda x: x is not None, results))

    if not results:
        return None
    
    flat_result: list[ValidationFailure] = (
        list(reduce(lambda accum, iter_val: accum + iter_val, results, []))  # type: ignore
    )

    if not flat_result:
        return None
    
    return flat_result

