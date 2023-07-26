import logging
import unittest
import zipfile

from common.log import configure_logging

class ZipFileTests(unittest.TestCase):


    def test_read(self):
        zipFile = zipfile.ZipFile("./tests/data/random.zip", "r")
        paths: list[str] = zipFile.namelist()
        logging.debug(f"paths: {paths}")
        self.assertEqual(paths, ['Page 3/', 'Page 3/files/', 'Page 3/hello.txt', 'Page 3/files/0bca50cb-655a-4cf2-adbe-ca77b402f863.pdf', 'Page 3/files/5211ec15-6748-4226-ad9f-fb358bfb40ac.pdf', 'Page 3/files/81770416-701c-4099-b585-ff0988894cc9_readme.md', 'Page 3/files/9b673aae-8089-4a91-84df-9dac152a7f94_flower.jpeg', 'Page 3/files/cb0679e6-5f80-4a86-bc24-240b3da7ae41.pdf'])

        readmeText: str = zipFile.read(paths[5]).decode(encoding="utf-8")
        logging.debug(f"readmeText: {readmeText}")
        self.assertTrue(readmeText.startswith("## Freenove Ultimate Starter Kit for Raspberry Pi"))


    def setUp(self):
        configure_logging()
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()