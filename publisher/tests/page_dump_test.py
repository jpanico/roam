import logging
import unittest

from common.log import configure_logging

from roampub.roam_model import *
from roampub.page_dump import *

class PageDumpTests(unittest.TestCase):


    def test_create_page_node(self):
        text: str = "Page 3"
        children: list[Uid] = [
            "IO75SriD8",
            "uFL-CFN6i",
            "LXoC6aV1-",
            "dftwwQg-V"
        ]
        uid: Uid = "hfm6NKq2c"
        vertex_type: str = VertexType.ROAM_PAGE._value_
        media_type: str = MediaType.TEXT_PLAIN._value_
        source: dict = {
            "text": text,
            "children": children,
            "uid": uid,
            "vertex-type": vertex_type,
            "media-type": media_type
        }
        # logging.debug(f"page_node.uid: {page_node.uid}")
        page_node: PageNode = create_page_node(source)
        logging.debug(f"page_node: {page_node}")
        self.assertEqual(page_node.uid,uid)
        self.assertEqual(page_node.vertex_type,VertexType.ROAM_PAGE)
        self.assertEqual(page_node.media_type,MediaType.TEXT_PLAIN)
        self.assertEqual(page_node.title,text)
        self.assertEqual(page_node.children,children)
        self.assertEqual(page_node.references,None)


    def setUp(self):
        configure_logging()
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()