""" functions to export PageDump as Roam MarkDown
 

Types:

    Exportation



Functions:


"""
from typing import TypeAlias, Callable, cast
import logging

from common.log import TRACE

from roampub.roam_model import VertexType, RoamNode, PageNode, BlockHeadingNode, BlockContentNode, VertexMap


logger = logging.getLogger(__name__)


Exportation: TypeAlias = Callable[[RoamNode, VertexMap], str]


def export_page_node(node: RoamNode, graph: VertexMap) -> str:
    logger.log(TRACE, f"node: {node}")
    if not isinstance(node, PageNode):
        raise TypeError(f"is not instanceof {PageNode}; node: {node}")
    
    page_node: PageNode = cast(PageNode, node)
    heading: str = f"# {page_node.title.strip()}"

    if not page_node.children:
        return heading
    
    children_exports: list[str] = (
        [export_node(cast(RoamNode, graph[c_uid]), graph) for c_uid in page_node.children]
    )
    logger.log(TRACE, f"children_exports: {children_exports}")
    
    nodes_content: str = '\n\n'.join(([heading]+children_exports))
    # add a single newline to end of document
    nodes_content += '\n'
    return nodes_content


def export_block_heading_node(node: RoamNode, graph: VertexMap) -> str:
    logger.log(TRACE, f"node: {node}")
    if not isinstance(node, BlockHeadingNode):
        raise TypeError(f"is not instanceof {BlockHeadingNode}; node: {node}")
    
    block_heading_node: BlockHeadingNode = cast(BlockHeadingNode, node)
    heading: str = f"{'#'*block_heading_node.level} {block_heading_node.heading.strip()}"

    if not block_heading_node.children:
        return heading
    
    children_exports: list[str] = (
        [export_node(cast(RoamNode, graph[c_uid]), graph) for c_uid in block_heading_node.children]
    )
    logger.log(TRACE, f"children_exports: {children_exports}")
    
    return '\n\n'.join(([heading]+children_exports))


def export_block_content_node(node: RoamNode, graph: VertexMap) -> str:
    logger.log(TRACE, f"node: {node}")
    if not isinstance(node, BlockContentNode):
        raise TypeError(f"is not instanceof {BlockContentNode}; node: {node}")
    
    block_content_node: BlockContentNode = cast(BlockContentNode, node)
    content: str = block_content_node.content.strip()

    if not block_content_node.children:
        return content
    
    children_exports: list[str] = (
        [export_node(cast(RoamNode, graph[c_uid]), graph) for c_uid in block_content_node.children]
    )
    logger.log(TRACE, f"children_exports: {children_exports}")
    
    return '\n\n'.join(([content]+children_exports))


def export_node(node: RoamNode, graph: VertexMap)-> str:
    logger.log(TRACE, f"node: {node}")
    if any(arg is None for arg in [node, graph]):
        raise ValueError("missing required arg")
    if not isinstance(node, RoamNode):
        raise TypeError(f"is not instanceof {RoamNode}; node: {node}")    
    if not isinstance(graph, VertexMap.__origin__):  # type: ignore
        raise TypeError(f"is not instanceof {VertexMap}; node: {graph}")    
    
    return EXPORTATION_MAP[node.vertex_type](node, graph)


EXPORTATION_MAP: dict[VertexType, Exportation] = {
    VertexType.ROAM_PAGE: export_page_node,
    VertexType.ROAM_BLOCK_HEADING: export_block_heading_node,
    VertexType.ROAM_BLOCK_CONTENT: export_block_content_node
}