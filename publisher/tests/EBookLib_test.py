import unittest

from ebooklib.epub import read_epub, EpubBook, EpubItem
from ebooklib import ITEM_DOCUMENT

from common.LoggingConfig import logging, configure_logging

class EBookLib_test(unittest.TestCase):

    def test_items(self):
        book: EpubBook = read_epub('./tests/data/childrens-literature.epub')
        logging.debug(f"book: {book}")
        items: tuple[EpubItem] = book.get_items()
        logging.debug(f"items: {items}")
        [logging.debug(f"id: {item.get_id()}, type: {item.get_type()}") for item in items] 

        for item in book.get_items():
            if item.get_type() == ITEM_DOCUMENT:
                logging.debug(f"id: {item.get_id()}, content: {item.get_content()}")


    def test_read_meta(self):
        book: EpubBook = read_epub('./tests/data/childrens-literature.epub')
        logging.debug(f"book: {book}")


        # Minimal required metadata from Dublic Core set (for EPUB3) is:
        #   DC:identifier
        #   DC:title
        #   DC:language
        identifier: list = book.get_metadata('DC', 'identifier')
        logging.debug(f"identifier: {identifier}")
        self.assertEquals(len(identifier), 1)
        self.assertEquals(identifier[0], ('http://www.gutenberg.org/ebooks/25545', {'id': 'id'}))


        title: list = book.get_metadata('DC', 'title')
        logging.debug(f"title: {title}")
        self.assertEquals(len(title), 2)
        self.assertEquals(title[0], ("Children's Literature", {'id': 't1'}))
        # this is the subtitle
        self.assertEquals(title[1], ('A Textbook of Sources for Teachers and Teacher-Training Classes', {'id': 't2'}))

        language: list = book.get_metadata('DC', 'language')
        logging.debug(f"language: {language}")
        self.assertEquals(len(language), 1)
        self.assertEquals(language[0], ('en', {}))

        # Optional metadata from the Dublic Core set is:
        #   DC:creator
        #   DC:contributor
        #   DC:publisher
        #   DC:rights
        #   DC:coverage
        #   DC:date
        #   DC:description
        optional_meta_keys: list = ['creator', 'contributor', 'publisher', 'rights', 'coverage', 'date', 'description']
        logging.debug(f"optional_meta_keys: {optional_meta_keys}")
        [logging.debug(f"key: {key}, value: {book.get_metadata('DC', key)}") for key in optional_meta_keys] 

    def setUp(self):
        configure_logging()
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()