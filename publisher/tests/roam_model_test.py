import unittest
from operator import contains
from enum import Enum, StrEnum
from logging import DEBUG

from common.log import configure_logging, TRACE
from common.collect import get_first

from roampub.roam_model import *
from roampub.page_dump import *

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3 


class StrColor(StrEnum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'


class RoamModelTests(unittest.TestCase):

    def test_to_vertex_type_map(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        vertex_type_map: VertexTypeMap = to_vertex_type_map(brief_vertex_map)
        logging.debug(f"vertex_type_map: {vertex_type_map}")
        self.assertEqual(len(vertex_type_map[VertexType.ROAM_PAGE]), 1)
        self.assertEqual(len(vertex_type_map[VertexType.ROAM_BLOCK_HEADING]), 3)
        self.assertEqual(len(vertex_type_map[VertexType.ROAM_BLOCK_CONTENT]), 8)
        self.assertEqual(len(vertex_type_map[VertexType.ROAM_FILE]), 0)


    def test_validate(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(validate(brief_vertex_map))


        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self.assertIsNone(validate(page3_vertex_map))


        # add ROAM_FILE vertex (9b673aae-8089-4a91-84df-9dac152a7f94) as child of root PAGE_NODE (hfm6NKq2c)
        node_hfm6NKq2c: RoamNode = cast(RoamNode, page3_vertex_map['hfm6NKq2c'])
        logging.debug(f"node_hfm6NKq2c: {node_hfm6NKq2c}")
        node_hfm6NKq2c.children.append('9b673aae-8089-4a91-84df-9dac152a7f94') # type: ignore
        validation_result: list[ValidationFailure] = validate(page3_vertex_map)  # type: ignore
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 2)
        self.assertIs(validation_result[0].rule, CHILDREN_VERTEX_TYPES_RULE)
        self.assertIn("9b673aae-8089-4a91-84df-9dac152a7f94", validation_result[0].failure_message)
        self.assertIs(validation_result[1].rule, PAGE_NODE_CHILDREN_RULE)
        self.assertIn("9b673aae-8089-4a91-84df-9dac152a7f94", validation_result[1].failure_message)


    def test_validate_references_appear_in_content(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(REFERENCES_APPEAR_IN_CONTENT_RULE.validate(brief_vertex_map))

        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self.assertIsNone(REFERENCES_APPEAR_IN_CONTENT_RULE.validate(page3_vertex_map))

        # find first RoamNode that has refs
        referring_node: BlockContentNode = (cast(BlockContentNode,
            get_first(
                [v for v in page3_vertex_map.values() if has_attribute_value(v, 'references')])
            )
        )       
        logging.debug(f"referring_node: {referring_node}")
        ref_id: Uid = get_first(referring_node.references) # type: ignore
        logging.debug(f"ref_id: {ref_id}")
        updated_content: str = referring_node._content.replace(ref_id, 'xxxxx') 
        updated_node: BlockContentNode = BlockContentNode(
            referring_node.uid, referring_node.media_type, updated_content,
            referring_node.children, referring_node.references
        )
        logging.debug(f"updated_node: {updated_node}")
        page3_vertex_map[referring_node.uid] = updated_node
        validation_result: list[ValidationFailure] = (
            REFERENCES_APPEAR_IN_CONTENT_RULE.validate(page3_vertex_map)  # type: ignore
        )
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, REFERENCES_APPEAR_IN_CONTENT_RULE)
        self.assertIn("Wu-bKjjdJ", validation_result[0].failure_message)
        self.assertIn("IO75SriD8", validation_result[0].failure_message)


    def test_content_contains_reference(self):
        content: str = "Block 1.2.1 -- block-ref-> ((IO75SriD8))"
        self.assertTrue(content_contains_reference(content, 'IO75SriD8'))

        content: str = "Block 1.2.1 -- page-ref-> [[IO75SriD8]]"
        self.assertTrue(content_contains_reference(content, 'IO75SriD8'))

        content: str = "Block 1.2.1 -- file-ref-> <<IO75SriD8>>"
        self.assertTrue(content_contains_reference(content, 'IO75SriD8'))

        content: str = "Block 1.2.1 -- file-ref-> <<xxxxx>>"
        self.assertFalse(content_contains_reference(content, 'IO75SriD8'))

        content: str = "Block 1.2.1 -- file-ref-> <IO75SriD8>"
        self.assertFalse(content_contains_reference(content, 'IO75SriD8'))

        content: str = "Block 1.2.1 -- file-ref-> IO75SriD8"
        self.assertFalse(content_contains_reference(content, 'IO75SriD8'))


    def test_validate_references_attribute_appearance(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(REFERENCES_ATTRIBUTE_APPEARANCE_RULE.validate(brief_vertex_map))

        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self.assertIsNone(REFERENCES_ATTRIBUTE_APPEARANCE_RULE.validate(page3_vertex_map))

        # add references to root ROAM_PAGE vertex (lALsKb-Dx)
        root_node: RoamNode = cast(RoamNode, brief_vertex_map['lALsKb-Dx'])
        logging.debug(f"root_node: {root_node}")
        root_node._references = ['2bW3xKCMS']
        validation_result: list[ValidationFailure] = (
            REFERENCES_ATTRIBUTE_APPEARANCE_RULE.validate(brief_vertex_map)  # type: ignore
        )
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, REFERENCES_ATTRIBUTE_APPEARANCE_RULE)
        self.assertIn("lALsKb-Dx", validation_result[0].failure_message)


    def test_validate_children_attribute_appearance(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(CHILDREN_ATTRIBUTE_APPEARANCE_RULE.validate(brief_vertex_map))

        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self.assertIsNone(CHILDREN_ATTRIBUTE_APPEARANCE_RULE.validate(page3_vertex_map))

        # add children to ROAM_FILE vertex (9b673aae-8089-4a91-84df-9dac152a7f94)
        node_c152a7f94: FileVertex = cast(FileVertex, page3_vertex_map['9b673aae-8089-4a91-84df-9dac152a7f94'])
        logging.debug(f"node_c152a7f94: {node_c152a7f94}")
        setattr(node_c152a7f94, 'children', ['soJKEPwjQ'])
        validation_result: list[ValidationFailure] = (
            CHILDREN_ATTRIBUTE_APPEARANCE_RULE.validate(page3_vertex_map)  # type: ignore
        )
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, CHILDREN_ATTRIBUTE_APPEARANCE_RULE)
        self.assertIn("c152a7f94", validation_result[0].failure_message)


    def test_validate_block_heading_children(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(BLOCK_HEADING_CHILDREN_RULE.validate(brief_vertex_map))

        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self.assertIsNone(BLOCK_HEADING_CHILDREN_RULE.validate(page3_vertex_map))

        # add root PAGE_NODE (lALsKb-Dx) as child of ROAM_BLOCK_HEADING Node soJKEPwjQ
        node_soJKEPwjQ: RoamNode = cast(RoamNode, brief_vertex_map['soJKEPwjQ'])
        logging.debug(f"node_soJKEPwjQ: {node_soJKEPwjQ}")
        node_soJKEPwjQ.children.append('lALsKb-Dx') # type: ignore
        validation_result: list[ValidationFailure] = (
            BLOCK_HEADING_CHILDREN_RULE.validate(brief_vertex_map)  # type: ignore
        )
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, BLOCK_HEADING_CHILDREN_RULE)
        self.assertIn("lALsKb-Dx", validation_result[0].failure_message)


    def test_validate_page_node_children(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(PAGE_NODE_CHILDREN_RULE.validate(brief_vertex_map))

        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self.assertIsNone(PAGE_NODE_CHILDREN_RULE.validate(page3_vertex_map))

        # add ROAM_FILE vertex (9b673aae-8089-4a91-84df-9dac152a7f94) as child of root PAGE_NODE (hfm6NKq2c)
        node_hfm6NKq2c: RoamNode = cast(RoamNode, page3_vertex_map['hfm6NKq2c'])
        logging.debug(f"node_hfm6NKq2c: {node_hfm6NKq2c}")
        node_hfm6NKq2c.children.append('9b673aae-8089-4a91-84df-9dac152a7f94') # type: ignore
        validation_result: list[ValidationFailure] = PAGE_NODE_CHILDREN_RULE.validate(page3_vertex_map)  # type: ignore
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, PAGE_NODE_CHILDREN_RULE)
        self.assertIn("9b673aae-8089-4a91-84df-9dac152a7f94", validation_result[0].failure_message)


    def test_validate_children_vertex_types(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(CHILDREN_VERTEX_TYPES_RULE.validate(brief_vertex_map))

        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self.assertIsNone(CHILDREN_VERTEX_TYPES_RULE.validate(page3_vertex_map))

        # add root PAGE_NODE (lALsKb-Dx) as child of Node soJKEPwjQ
        node_soJKEPwjQ: RoamNode = cast(RoamNode, brief_vertex_map['soJKEPwjQ'])
        logging.debug(f"node_soJKEPwjQ: {node_soJKEPwjQ}")
        node_soJKEPwjQ.children.append('lALsKb-Dx') # type: ignore
        validation_result: list[ValidationFailure] = (
            CHILDREN_VERTEX_TYPES_RULE.validate(brief_vertex_map)  # type: ignore
        )
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, CHILDREN_VERTEX_TYPES_RULE)
        self.assertIn("lALsKb-Dx", validation_result[0].failure_message)


    def test_validate_block_parents_exist(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(BLOCK_PARENTS_EXIST_RULE.validate(brief_vertex_map))

        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self.assertIsNone(BLOCK_PARENTS_EXIST_RULE.validate(page3_vertex_map))

        # C2uKKD4-b is a ``ROAM_BLOCK_CONTENT`` node that is child of root ``PageNode``
        # here we erroneously insert it as a child of 2bW3xKCMS as well
        node_2bW3xKCMS: RoamNode = cast(RoamNode, brief_vertex_map['2bW3xKCMS'])
        logging.debug(f"node_2bW3xKCMS: {node_2bW3xKCMS}")
        node_2bW3xKCMS.children.append('C2uKKD4-b') # type: ignore
        validation_result: list[ValidationFailure] = BLOCK_PARENTS_EXIST_RULE.validate(brief_vertex_map)  # type: ignore
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, BLOCK_PARENTS_EXIST_RULE)
        self.assertIn("{'C2uKKD4-b': 2}", validation_result[0].failure_message)

        # soJKEPwjQ is a ``ROAM_BLOCK_HEADING`` node that is child of 2bW3xKCMS
        # here we erroneously insert it as a child of 4jf3ZlLqF as well
        node_4jf3ZlLqF: RoamNode = cast(RoamNode, brief_vertex_map['4jf3ZlLqF'])
        logging.debug(f"node_4jf3ZlLqF: {node_4jf3ZlLqF}")
        node_4jf3ZlLqF.children.append('soJKEPwjQ') # type: ignore
        validation_result: list[ValidationFailure] = BLOCK_PARENTS_EXIST_RULE.validate(brief_vertex_map)  # type: ignore
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, BLOCK_PARENTS_EXIST_RULE)
        self.assertIn("{'C2uKKD4-b': 2, 'soJKEPwjQ': 2}", validation_result[0].failure_message)


    def test_validate_references_exist(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(REFERENCES_EXIST_RULE.validate(brief_vertex_map))
        
        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self.assertIsNone(REFERENCES_EXIST_RULE.validate(page3_vertex_map))

        del page3_vertex_map['IO75SriD8']
        validation_result: list[ValidationFailure] = REFERENCES_EXIST_RULE.validate(page3_vertex_map)  # type: ignore
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, REFERENCES_EXIST_RULE)
        self.assertIn('IO75SriD8', validation_result[0].failure_message)

        del page3_vertex_map['9b673aae-8089-4a91-84df-9dac152a7f94']
        validation_result: list[ValidationFailure] = REFERENCES_EXIST_RULE.validate(page3_vertex_map)  # type: ignore
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, REFERENCES_EXIST_RULE)
        self.assertIn('IO75SriD8', validation_result[0].failure_message)
        self.assertIn('9b673aae-8089-4a91-84df-9dac152a7f94', validation_result[0].failure_message)


    def test_all_references(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        result: list[Uid] = all_linked_uids('references', brief_vertex_map)
        logging.debug(f"result: {result}")
        self.assertEqual(result, [])

        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        result: list[Uid] = all_linked_uids('references', page3_vertex_map)
        logging.debug(f"result: {result}")
        self.assertEqual(result, ['IO75SriD8', 'A_4nJQ1Y7', 'plH3eTesS', 'o2hTH3dbf', 'YMkrw0y7Y', '9b673aae-8089-4a91-84df-9dac152a7f94', 'Qb2JOnrUQ', 'Pvyh6q_ag', 'mvVww9zGd', 'Pvyh6q_ag', '81770416-701c-4099-b585-ff0988894cc9'])


    def test_validate_children_exist(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(CHILDREN_EXIST_RULE.validate(brief_vertex_map))
        
        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self.assertIsNone(CHILDREN_EXIST_RULE.validate(page3_vertex_map))

        # the last RoamVertex in page3_vertex_map is "uid"="mvVww9zGd", which is in the ``children`` list of 
        # another vertex. 
        del page3_vertex_map['mvVww9zGd']
        validation_result: list[ValidationFailure] = CHILDREN_EXIST_RULE.validate(page3_vertex_map)  # type: ignore
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, CHILDREN_EXIST_RULE)
        self.assertIn('mvVww9zGd', validation_result[0].failure_message)

        del page3_vertex_map['Ww_4xiPko']
        validation_result: list[ValidationFailure] = CHILDREN_EXIST_RULE.validate(page3_vertex_map)  # type: ignore
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, CHILDREN_EXIST_RULE)
        self.assertIn('mvVww9zGd', validation_result[0].failure_message)
        self.assertIn('Ww_4xiPko', validation_result[0].failure_message)


    def test_all_children(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        result: list[Uid] = all_linked_uids('children', brief_vertex_map)
        logging.debug(f"result: {result}")
        self.assertEqual(result, ['C2uKKD4-b', 'ZdZlJbgy1', '6TCv5eKPQ', '2bW3xKCMS', '4jf3ZlLqF', 'ZnUfgOM7W', '6r7Q5nxw5', 'Gi1BCIGoW', 'dkdzOF1XB', 'Kkl93sU4u', 'soJKEPwjQ'])

        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        result: list[Uid] = all_linked_uids('children', page3_vertex_map)
        logging.debug(f"result: {result}")
        self.assertEqual(result, ['IO75SriD8', 'uFL-CFN6i', 'LXoC6aV1-', 'dftwwQg-V', 'nvZuZUSrh', 'plH3eTesS', 'IvK1p6Cqs', 'a9PURgUrs', 'GI38yM-z4', 'Mw66e2LRj', 'q1qajG3Zk', 'cLvvyOfnB', 'MQ5dNpkpA', 'Up_5YBvZg', 'lreFpitoR', 'A_4nJQ1Y7', 'mvVww9zGd', '5_de8n-ih', 'YMkrw0y7Y', 'eqOJ4CH9Y', '9dy8FUY7E', 'Ww_4xiPko', 'yiZaMqbAz', 'Wu-bKjjdJ'])


    def test_validate_root_page(self):
        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self.assertIsNone(ROOT_PAGE_RULE.validate(page3_vertex_map))
    
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(ROOT_PAGE_RULE.validate(brief_vertex_map))

        # remove first item from VertexMap
        page3_vertex_map.popitem(last=False)
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        validation_result: list[ValidationFailure] = ROOT_PAGE_RULE.validate(page3_vertex_map)  # type: ignore
        logging.debug(f"validation_result: {validation_result}")
        self.assertEqual(len(validation_result), 1)
        self.assertIs(validation_result[0].rule, ROOT_PAGE_RULE)

        self.assertIsNone(ROOT_PAGE_RULE.validate(None)) # type: ignore

        wrong_type_vertex_map = dict(brief_vertex_map)
        logging.debug(f"type(wrong_type_vertex_map): {type(wrong_type_vertex_map)}")
        with self.assertRaises(TypeError):
            ROOT_PAGE_RULE.validate(wrong_type_vertex_map) # type: ignore


    def test_validation_rule(self):

        name: str = 'rule.name'
        description: str = 'rule.description'
        rule: ValidationRule = ValidationRule(name, description, validate_root_page)
        logging.debug(f"rule: {rule}")

        self.assertEqual(name, rule.name)
        self.assertEqual(description, rule.description)
        self.assertEqual(validate_root_page, rule.impl)


    def test_validation_failure(self):

        message: str = 'failure message string'
        validation_failure: ValidationFailure = ValidationFailure(ROOT_PAGE_RULE, message)
        logging.debug(f"validation_failure: {validation_failure}")

        self.assertEqual(ROOT_PAGE_RULE, validation_failure.rule)
        self.assertEqual(message, validation_failure.failure_message)


    def test_file_vertex_create(self):

        file_vertex: FileVertex = FileVertex('uid.0', MediaType.TEXT_PLAIN, 'file.file_name', 'file.source')
        logging.debug(f"fileVertex: {file_vertex}")
        self.assertEqual('uid.0', file_vertex.uid)
        self.assertEqual(VertexType.ROAM_FILE, file_vertex.vertex_type)
        self.assertEqual(MediaType.TEXT_PLAIN, file_vertex.media_type)
        self.assertEqual('file.file_name', file_vertex.file_name)
        self.assertEqual('file.source', file_vertex.source)
        

    def test_block_content_create(self):

        block_content_node: BlockContentNode = BlockContentNode('uid.0', MediaType.TEXT_PLAIN, 'block.content')
        logging.debug(f"blockContentNode: {block_content_node}")
        self.assertEqual('uid.0', block_content_node.uid)
        self.assertEqual(VertexType.ROAM_BLOCK_CONTENT, block_content_node.vertex_type)
        self.assertEqual(MediaType.TEXT_PLAIN, block_content_node.media_type)
        self.assertEqual('block.content', block_content_node.content)


    def test_block_heading_create(self):

        block_heading_node: BlockHeadingNode = BlockHeadingNode('uid.0', MediaType.TEXT_PLAIN, 'block.heading', 1)
        logging.debug(f"blockHeadingNode: {block_heading_node}")
        self.assertEqual('uid.0', block_heading_node.uid)
        self.assertEqual(VertexType.ROAM_BLOCK_HEADING, block_heading_node.vertex_type)
        self.assertEqual(MediaType.TEXT_PLAIN, block_heading_node.media_type)
        self.assertEqual('block.heading', block_heading_node.heading)
        self.assertEqual(1, block_heading_node.level)


    def test_page_create(self):

        page_node: PageNode = PageNode('uid.0', MediaType.TEXT_PLAIN, 'page.title')
        logging.debug(f"pageNode: {page_node}")
        self.assertEqual('uid.0', page_node.uid)
        self.assertEqual(VertexType.ROAM_PAGE, page_node.vertex_type)
        self.assertEqual(MediaType.TEXT_PLAIN, page_node.media_type)
        self.assertEqual('page.title', page_node.title)


    def test_node_create(self):

        # Roamnode has abstract method, so creation attempt should raise
        with self.assertRaises(TypeError):
            vertex = RoamNode('uid.0', MediaType.TEXT_PLAIN) # type: ignore


    def test_vertex_create(self):

        # RoamVertex has abstract method, so creation attempt should raise
        with self.assertRaises(TypeError):
            vertex = RoamVertex('uid.0', MediaType.TEXT_PLAIN) # type: ignore


    def test_vertex_type_match(self):
        vertex_type: VertexType = VertexType.ROAM_FILE
        logging.debug(f"vertex_type: {vertex_type}")

        from_match: VertexType
        match vertex_type:
            case VertexType.ROAM_PAGE:
                from_match = VertexType.ROAM_PAGE
            case VertexType.ROAM_BLOCK_CONTENT:
                from_match = VertexType.ROAM_BLOCK_CONTENT
            case VertexType.ROAM_BLOCK_HEADING:
                from_match = VertexType.ROAM_BLOCK_HEADING
            case VertexType.ROAM_FILE:
                from_match = VertexType.ROAM_FILE
            case _:
                raise ValueError(f"unrecognized vertex_type: {vertex_type}")

        self.assertIs(VertexType.ROAM_FILE, from_match)


    def test_vertex_type(self):

        self.assertEqual('roam/page', VertexType.ROAM_PAGE.value)
        self.assertEqual(VertexType.ROAM_PAGE, VertexType.ROAM_PAGE)
        self.assertTrue(VertexType.ROAM_PAGE == VertexType.ROAM_PAGE)
        self.assertIs(VertexType.ROAM_PAGE, VertexType.ROAM_PAGE)
        self.assertTrue(VertexType.ROAM_PAGE is VertexType.ROAM_PAGE)
        self.assertIs(type(VertexType.ROAM_PAGE), VertexType)

        self.assertNotEqual('roam/page', VertexType.ROAM_BLOCK_CONTENT.value)
        self.assertNotEqual(VertexType.ROAM_PAGE, VertexType.ROAM_BLOCK_CONTENT)
        self.assertFalse(VertexType.ROAM_PAGE == VertexType.ROAM_BLOCK_CONTENT)
        self.assertIsNot(VertexType.ROAM_PAGE, VertexType.ROAM_BLOCK_CONTENT)
        self.assertFalse(VertexType.ROAM_PAGE is VertexType.ROAM_BLOCK_CONTENT)
        self.assertIs(type(VertexType.ROAM_BLOCK_CONTENT), VertexType)

        self.assertTrue(VertexType.ROAM_PAGE in [VertexType.ROAM_PAGE, VertexType.ROAM_BLOCK_HEADING])
        self.assertFalse(VertexType.ROAM_BLOCK_CONTENT in [VertexType.ROAM_PAGE, VertexType.ROAM_BLOCK_HEADING])


    def test_enum_compare(self):
        self.assertEqual(Color.RED, Color.RED)
        self.assertNotEqual(Color.RED, Color.BLUE)

        self.assertEqual(StrColor.RED, StrColor.RED)
        self.assertNotEqual(StrColor.RED, StrColor.BLUE)


    def setUp(self):
        configure_logging(logging.INFO)
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()