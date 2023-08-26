""" functions to convert PageDump to a stream of markdown_it ``Token``s
 

Types:

Functions:

"""
import logging
from typing import cast
from functools import reduce

from markdown_it import MarkdownIt
from markdown_it.token import Token

from common.log import TRACE
from roampub.roam_model import VertexType, RoamNode, PageNode, BlockHeadingNode, BlockContentNode, VertexMap


logger = logging.getLogger(__name__)


def tokenize_page_node(node: PageNode) -> list[Token]:
    logger.log(TRACE, f"node: {node}")
    
    content: str = node.title.strip()
    tokens: list[Token] = [
        Token(type='heading_open', content='', tag='h1', nesting=1, level=0, markup='#', block=True),
        Token(type='inline', content='', tag='', nesting=0, level=1, markup='', block=True, children= [
            Token(type='text', content=f"{content}", tag='', nesting=0, level=0, markup='', block=False)
        ]),
        Token(type='heading_close', content='', tag='h1', nesting=-1, level=0, markup='#', block=True),
    ]    
    return tokens


def tokenize_block_heading_node(node: BlockHeadingNode) -> list[Token]:
    logger.log(TRACE, f"node: {node}")
    
    tag: str = f"h{node.level}"
    markup: str = '#'*node.level
    content: str = node.heading.strip()
    tokens: list[Token] = [
        Token(type='heading_open', content='', tag=f"{tag}", nesting=1, level=0, markup=f"{markup}", block=True),
        Token(type='inline', content='', tag='', nesting=0, level=1, markup='', block=True, children= [
            Token(type='text', content=f"{content}", tag='', nesting=0, level=0, markup='', block=False)
        ]),
        Token(type='heading_close', content='', tag=f"{tag}", nesting=-1, level=0, markup=f"{markup}", block=True),
    ]
    # heading: str = f"{'#'*node.level} {node.heading.strip()}"
    
    return tokens


def tokenize_block_content_node(node: BlockContentNode) -> list[Token]:
    logger.log(TRACE, f"node: {node}")
    
    parser: MarkdownIt = MarkdownIt('commonmark' ,{'breaks':True,'html':False,'xhtmlOut': True})
    return parser.parse(node.content)


def tokenize_node(node: RoamNode, graph: VertexMap)-> list[Token]:
    logger.log(TRACE, f"node: {node}")
    if any(arg is None for arg in [node, graph]):
        raise ValueError("missing required arg")
    if not isinstance(node, RoamNode):
        raise TypeError(f"is not instanceof {RoamNode}; node: {node}")    
    if not isinstance(graph, VertexMap.__origin__):  # type: ignore
        raise TypeError(f"is not instanceof {VertexMap}; node: {graph}")    
    
    node_tokens: list[Token]
    match node.vertex_type:
        case VertexType.ROAM_PAGE:
            node_tokens = tokenize_page_node(cast(PageNode, node))
        case VertexType.ROAM_BLOCK_HEADING:
            node_tokens = tokenize_block_heading_node(cast(BlockHeadingNode, node))
        case VertexType.ROAM_BLOCK_CONTENT:
            node_tokens = tokenize_block_content_node(cast(BlockContentNode, node))
        case _:
            raise ValueError(f"unrecognized vertex_type: {node.vertex_type}")

    if not node.children:
        return node_tokens
    
    children_tokens: list[list[Token]] = [tokenize_node(cast(RoamNode, graph[c_uid]), graph) for c_uid in node.children]
    logger.log(TRACE, f"children_tokens: {children_tokens}")
    children_flat_tokens: list[Token] = list(reduce(lambda accum, iter_val: accum + iter_val, children_tokens, [])) 
    logger.log(TRACE, f"children_flat_tokens: {children_flat_tokens}")
    return node_tokens if not children_flat_tokens else (node_tokens + children_flat_tokens)