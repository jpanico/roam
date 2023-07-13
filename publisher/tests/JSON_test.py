import unittest
import json

from common.LoggingConfig import logging, configure_logging

class JSON_test(unittest.TestCase):


    def test_read(self):
        jsonFile = open("./tests/data/Page 3.json")

        jsonObj: list[dict] = json.load(jsonFile)

        logging.debug(f"jsonObj: {jsonObj}, len: {len(jsonObj)}")
        self.assertEquals(len(jsonObj), 30)
        self.assertEquals(
            jsonObj[0], 
            {'text': 'Page 3', 'children': ['IO75SriD8', 'uFL-CFN6i'], 'uid': 'hfm6NKq2c', 'vertex-type': 'roam/page', 'media-type': 'text/plain'} 
        )
        self.assertEquals(
            jsonObj[29], 
            {'text': 'Block 1.2', 'children': ['Wu-bKjjdJ'], 'uid': 'mvVww9zGd', 'vertex-type': 'roam/block', 'media-type': 'text/plain'} 
        )


    def setUp(self):
        configure_logging()
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()