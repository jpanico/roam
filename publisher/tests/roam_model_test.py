import logging
import unittest

from common.log import configure_logging

from roampub.roam_model import *

class RoamTests(unittest.TestCase):

    def test_file_vertex_create(self):

        fileVertex: FileVertex = FileVertex('uid.0', MediaType.TEXT_PLAIN, 'file.file_name', 'file.source')
        logging.debug(f"fileVertex: {fileVertex}")
        self.assertEqual('uid.0', fileVertex.uid)
        self.assertEqual(VertexType.ROAM_FILE, fileVertex.vertex_type)
        self.assertEqual(MediaType.TEXT_PLAIN, fileVertex.media_type)
        self.assertEqual('file.file_name', fileVertex.file_name)
        self.assertEqual('file.source', fileVertex.source)
        

    def test_block_content_create(self):

        blockContentNode: BlockContentNode = BlockContentNode('uid.0', MediaType.TEXT_PLAIN, 'block.content')
        logging.debug(f"blockContentNode: {blockContentNode}")
        self.assertEqual('uid.0', blockContentNode.uid)
        self.assertEqual(VertexType.ROAM_BLOCK_CONTENT, blockContentNode.vertex_type)
        self.assertEqual(MediaType.TEXT_PLAIN, blockContentNode.media_type)
        self.assertEqual('block.content', blockContentNode.content)


    def test_block_heading_create(self):

        blockHeadingNode: BlockHeadingNode = BlockHeadingNode('uid.0', MediaType.TEXT_PLAIN, 'block.heading')
        logging.debug(f"blockHeadingNode: {blockHeadingNode}")
        self.assertEqual('uid.0', blockHeadingNode.uid)
        self.assertEqual(VertexType.ROAM_BLOCK_HEADING, blockHeadingNode.vertex_type)
        self.assertEqual(MediaType.TEXT_PLAIN, blockHeadingNode.media_type)
        self.assertEqual('block.heading', blockHeadingNode.heading)


    def test_page_create(self):

        pageNode: PageNode = PageNode('uid.0', MediaType.TEXT_PLAIN, 'page.title')
        logging.debug(f"pageNode: {pageNode}")
        self.assertEqual('uid.0', pageNode.uid)
        self.assertEqual(VertexType.ROAM_PAGE, pageNode.vertex_type)
        self.assertEqual(MediaType.TEXT_PLAIN, pageNode.media_type)
        self.assertEqual('page.title', pageNode.title)


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
        self.assertEqual('roam/page', VertexType.ROAM_PAGE._value_)
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