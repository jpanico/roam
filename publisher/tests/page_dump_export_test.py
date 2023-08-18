import logging
import unittest
from pathlib import Path

from common.log import configure_logging

from roampub.roam_model import *
from roampub.page_dump import *
from roampub.page_dump_export import *

class PageDumpExportTests(unittest.TestCase):

    def test_export(self):
        path: Path = Path('./tests/data/Creative Brief.zip')
        brief_dump: PageDump = PageDump(path)
        export: str = export_node(brief_dump.root_page, brief_dump.vertex_map)
        logging.debug(f"export: {export}")


    def test_export_block_content_node(self):
        node: BlockContentNode = BlockContentNode('uid.0', MediaType.TEXT_PLAIN, 'block.content')
        vertex_map: VertexMap = OrderedDict([(v.uid, v) for v in [node]])
        from_export: str = export_block_content_node(node, vertex_map)
        logging.debug(f"from_export: {from_export}")
        self.assertEqual(from_export, node.content)

        from_export_node: str = export_node(node, vertex_map)
        self.assertEqual(from_export_node,from_export)


    def setUp(self):
        configure_logging(logging.DEBUG)
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()