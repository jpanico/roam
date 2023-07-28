import logging
import unittest
from typing import Iterator, TextIO

from ebooklib.epub import read_epub, write_epub, EpubBook, EpubItem, EpubHtml, Link, EpubNav, EpubNcx, Section
from ebooklib import ITEM_DOCUMENT

from common.log import configure_logging

class EBookLibTests(unittest.TestCase):


    def test_create_1(self):
        book = EpubBook()

        # add metadata
        book.set_identifier('sample1234567')
        book.set_title('Sample book')
        book.set_language('en')

        book.add_author('Aleksandar Erkalovic')

        # intro chapter
        c1 = EpubHtml(title='Introduction', file_name='intro.xhtml', lang='en')
        c1.content=u'<html><head></head><body><h1>Introduction</h1><p>Introduction paragraph where i explain what is happening.</p></body></html>'

        # about chapter
        c2 = EpubHtml(title='About this book', file_name='about.xhtml')
        c2.content='<h1>About this book</h1><p>Helou, this is my book! There are many books, but this one is mine.</p>'

        # add chapters to the book
        book.add_item(c1)
        book.add_item(c2)
        
        # create table of contents
        # - add section
        # - add auto created links to chapters

        book.toc = (Link('intro.xhtml', 'Introduction', 'intro'), # type: ignore
                    (Section('Languages'),
                    (c1, c2))
                    )

        # add navigation files
        book.add_item(EpubNcx())
        book.add_item(EpubNav())

        nav_css_iostream: TextIO = open("./tests/data/sample_nav.css", "r")
        nav_css_content: str = nav_css_iostream.read()
        logging.debug(f"nav_css_content: {nav_css_content}")
        # add css file
        nav_css = EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=nav_css_content) # type: ignore
        book.add_item(nav_css)

        # create spine
        book.spine = ['nav', c1, c2]

        # create epub file
        write_epub('./out/test.epub', book, {})


    def test_read_items(self):
        book: EpubBook = read_epub('./tests/data/childrens-literature.epub')
        logging.debug(f"book: {book}")
        items: Iterator[EpubItem] = book.get_items()
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