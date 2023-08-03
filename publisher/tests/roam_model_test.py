import logging
import unittest

from common.log import configure_logging

from roampub.roam_model import *

class RoamModelTests(unittest.TestCase):

    def test_validate_root_page(self):
        name: str = 'rule.name'
        description: str = 'rule.description'
        rule: ValidationRule = ValidationRule(name, description, validate_root_page)
        logging.debug(f"rule: {rule}")

        self.assertEqual(name, rule.name)
        self.assertEqual(description, rule.description)
        self.assertEqual(validate_root_page, rule.impl)


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