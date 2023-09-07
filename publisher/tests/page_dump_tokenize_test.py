import logging
import unittest
from collections.abc import Mapping
from pathlib import Path

from markdown_it import MarkdownIt as MDParser
from markdown_it.token import Token
from mdformat.renderer import MDRenderer

from common.log import configure_logging, TRACE

from roampub.roam_model import *
from roampub.page_dump import *
from roampub.page_dump_tokenize import *

class PageDumpTokenizeTests(unittest.TestCase):

    def test_normalize_tokenize_node(self):
        path: Path = Path('./tests/data/Creative Brief.zip')
        brief_dump: PageDump = PageDump(path)
        tokens: list[Token] = tokenize_node(brief_dump.root_page, brief_dump.vertex_map, True)
        logging.info(f"tokens: {tokens}")

        renderer: MDRenderer = MDRenderer()
        options: Mapping[str, Any] = {}
        env: Mapping = {}
        rendered_md: str = renderer.render(tokens, options, env)
        logging.info(f"rendered_md: {rendered_md}")
        dest_path: Path = Path("./out", f"{brief_dump.dump_name}-rendered.md")
        dest_writer: TextIO = dest_path.open("w")
        dest_writer.write(rendered_md)
        
        expected_md_path: Path = Path(f"./tests/data/{brief_dump.dump_name}-normalize-expected.md")
        expectedIO: TextIO = open(expected_md_path, "rt")
        expected_md = expectedIO.read()
        self.assertEqual(rendered_md, expected_md)


    def test_tokenize_node(self):
        path: Path = Path('./tests/data/Creative Brief.zip')
        brief_dump: PageDump = PageDump(path)
        tokens: list[Token] = tokenize_node(brief_dump.root_page, brief_dump.vertex_map, False)
        logging.info(f"tokens: {tokens}")

        renderer: MDRenderer = MDRenderer()
        options: Mapping[str, Any] = {}
        env: Mapping = {}
        rendered_md: str = renderer.render(tokens, options, env)
        logging.info(f"rendered_md: {rendered_md}")
        dest_path: Path = Path("./out", f"{brief_dump.dump_name}-rendered.md")
        dest_writer: TextIO = dest_path.open("w")
        dest_writer.write(rendered_md)
        
        expected_md_path: Path = Path(f"./tests/data/{brief_dump.dump_name}-export-expected.md")
        expectedIO: TextIO = open(expected_md_path, "rt")
        expected_md = expectedIO.read()
        self.assertEqual(rendered_md, expected_md)


    def test_tokens_render(self):
        tokens: list[Token] = [
            Token(type='heading_open', content='', tag='h1', nesting=1, level=0, markup='#', block=True),
            Token(type='inline', content='', tag='', nesting=0, level=1, markup='', block=True, children= [
                Token(type='text', content='Creative Brief', tag='', nesting=0, level=0, markup='', block=False)
            ]),
            Token(type='heading_close', content='', tag='h1', nesting=-1, level=0, markup='#', block=True),

            Token(type='paragraph_open', content='', tag='p', nesting=1, level=0, markup='', block=True),
            Token(type='inline', content='', tag='', nesting=0, level=1, markup='', block=True, children= [
                Token(type='text', content='Natural language, English for instance, is written for a single species of audience: human readers. It is used to convey ideas from one human to another, and is, by its nature, ambiguous in terms of', tag='', nesting=0, level=0, markup='', block=False)
            ]),
            Token(type='paragraph_close', content='', tag='p', nesting=-1, level=0, markup='', block=True)
        ]

        renderer: MDRenderer = MDRenderer()
        options: Mapping[str, Any] = {}
        env: Mapping = {}
        rendered_md = renderer.render(tokens, options, env)
        logging.info(f"rendered_md: {rendered_md}")

        expected_md = '# Creative Brief\n\nNatural language, English for instance, is written for a single species of audience: human readers. It is used to convey ideas from one human to another, and is, by its nature, ambiguous in terms of\n'
        self.assertEqual(rendered_md, expected_md)


    def setUp(self):
        configure_logging(TRACE)
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()