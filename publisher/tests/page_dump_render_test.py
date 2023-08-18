import logging
import unittest
from pathlib import Path

from common.log import configure_logging

class PageDumpRenderTests(unittest.TestCase):


    def test_read(self):
        pass


    def setUp(self):
        configure_logging(logging.INFO)
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()