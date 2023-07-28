import logging
import unittest
import inspect

from common.log import configure_logging

from roampub.roam_model import *

class RoamTests(unittest.TestCase):

    def test_vertex_create(self):

        pageVertex: PageNode = PageNode('uid.0', MediaType.TEXT_PLAIN)
        logging.debug(f"pageVertex: {pageVertex}")
        logging.debug(f"vars(pageVertex): {vars(pageVertex)}")

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