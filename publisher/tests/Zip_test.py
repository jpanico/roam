import unittest
import logging

from common.LoggingConfig import logging, configure_logging

class Zip_test(unittest.TestCase):


    def test_read(self):
        const = "world"
        logging.info(f"hello: {const}")


    def setUp(self):
        configure_logging()
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()