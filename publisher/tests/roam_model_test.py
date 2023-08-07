import logging
import unittest

from common.log import configure_logging

from roampub.roam_model import *
from roampub.page_dump import *

class RoamModelTests(unittest.TestCase):

    @unittest.skip('wip')
    def test_validate_children_exist(self):
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self.assertIsNone(CHILDREN_EXIST_RULE.validate(brief_vertex_map))
        
        # page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        # logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        # self.assertIsNone(ROOT_PAGE_RULE.validate(page3_vertex_map))
    

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
        """
        Demonstrates very curious property of Python ``Enums`` used in ``match`` statements;
        POLA is violated-- they don't work as expected/inuitively
        """
        vertex_type: VertexType = VertexType.ROAM_FILE
        logging.debug(f"vertex_type: {vertex_type}")

        from_if_tower: VertexType
        if vertex_type is VertexType.ROAM_PAGE:
            from_if_tower = VertexType.ROAM_PAGE
        elif vertex_type is VertexType.ROAM_BLOCK_CONTENT:
            from_if_tower = VertexType.ROAM_BLOCK_CONTENT
        elif vertex_type is VertexType.ROAM_BLOCK_HEADING:
            from_if_tower = VertexType.ROAM_BLOCK_HEADING
        elif vertex_type is VertexType.ROAM_FILE:
            from_if_tower = VertexType.ROAM_FILE
        else:
            raise ValueError(f"unrecognized vertex_type: {vertex_type}")
            
        self.assertIs(VertexType.ROAM_FILE, from_if_tower)

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

        self.assertIs(VertexType.ROAM_PAGE, from_match)


    def test_vertex_type(self):

        logging.debug(f"roam/page: {VertexType.ROAM_PAGE}")
        self.assertEqual('roam/page', VertexType.ROAM_PAGE.value)
        self.assertEqual(VertexType.ROAM_PAGE, VertexType.ROAM_PAGE)
        self.assertTrue(VertexType.ROAM_PAGE == VertexType.ROAM_PAGE)
        self.assertIs(VertexType.ROAM_PAGE, VertexType.ROAM_PAGE)
        self.assertTrue(VertexType.ROAM_PAGE is VertexType.ROAM_PAGE)
        self.assertIs(type(VertexType.ROAM_PAGE), VertexType)


    def setUp(self):
        configure_logging()
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()