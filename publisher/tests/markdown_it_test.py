import logging
import unittest

from markdown_it import MarkdownIt

from common.log import configure_logging

class MarkdownItTests(unittest.TestCase):


    def test_sanity(self):
        md = (
            MarkdownIt('commonmark' ,{'breaks':True,'html':False,'xhtmlOut': True})
            .enable('table')
        )
        text = """
        ---
        a: 1
        ---

        a | b
        - | -
        1 | 2

        A footnote [^1]

        [^1]: some details
        """
        
        tokens = md.parse(text)
        logging.info(f"tokens: {tokens}")
        xhtml_text = md.render(text)
        logging.info(f"xhtml_text: {xhtml_text}")




    def setUp(self):
        configure_logging(logging.INFO)
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()