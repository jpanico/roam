import logging
import unittest
from collections.abc import Mapping
from pathlib import Path

from markdown_it import MarkdownIt as MDParser
from markdown_it.token import Token
from mdformat.renderer import MDRenderer

from common.log import configure_logging

from roampub.roam_model import *
from roampub.page_dump import *
from roampub.page_dump_export import *

class PageDumpExportTests(unittest.TestCase):


    def test_parse(self):
        path: Path = Path('./tests/data/Creative Brief.zip')
        brief_dump: PageDump = PageDump(path)
        export_md: str = export_node_str(brief_dump.root_page, brief_dump.vertex_map)

        parser: MDParser = MDParser("commonmark")
        tokens: list[Token] = parser.parse(export_md)
        for token in tokens:
            print(f"{token}\n")


    def test_parse_render_round_trip(self):
        """
        demonstrates that round-tripping an ``export_node()`` generated MD string through ``markdown_it`` parse-render
        results in no changes to the original str
        """      
        path: Path = Path('./tests/data/Creative Brief.zip')
        brief_dump: PageDump = PageDump(path)
        export_md: str = export_node_str(brief_dump.root_page, brief_dump.vertex_map)

        parser: MDParser = MDParser("commonmark")
        tokens: list[Token] = parser.parse(export_md)

        renderer: MDRenderer = MDRenderer()
        options: Mapping[str, Any] = {}
        env: Mapping = {}
        rendered_md = renderer.render(tokens, options, env)
        self.assertEqual(export_md, rendered_md)


    def test_export(self):
        path: Path = Path('./tests/data/Creative Brief.zip')
        brief_dump: PageDump = PageDump(path)
        export_md: str = export_node_str(brief_dump.root_page, brief_dump.vertex_map)
        logging.debug(f"export_md: {export_md}")
        expected_md_path: Path = Path(f"./tests/data/{brief_dump.dump_name}-export-expected.md")
        expectedIO: TextIO = open(expected_md_path, "rt")
        expected_md = expectedIO.read()
        self.assertEqual(export_md, expected_md)


    def test_export_block_content_node(self):
        node: BlockContentNode = BlockContentNode('uid.0', MediaType.TEXT_PLAIN, 'block.content')
        vertex_map: VertexMap = OrderedDict([(v.uid, v) for v in [node]])
        from_export: str = export_block_content_node_str(node, vertex_map)
        logging.debug(f"from_export: {from_export}")
        self.assertEqual(from_export, node.content)

        from_export_node: str = export_node_str(node, vertex_map)
        self.assertEqual(from_export_node,from_export)


    def setUp(self):
        configure_logging(logging.INFO)
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()