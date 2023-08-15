from typing import Callable, cast
import logging
import unittest

from common.log import configure_logging
from common.collect import *

class CollectTests(unittest.TestCase):

    def test_get_last_value(self):
        with self.assertRaises(TypeError):
            get_last_value(cast(Mapping,None))
        self.assertIsNone(get_last_value({}))
        self.assertEqual(get_last_value({'k1':'v1'}),'v1')
        self.assertEqual(get_last_value({'k1':'v1','k2':'v2'}),'v2')


    def test_get_last_key(self):
        with self.assertRaises(TypeError):
            get_last_key(cast(Mapping,None))
        self.assertIsNone(get_last_key({}))
        self.assertEqual(get_last_key({'k1':'v1'}),'k1')
        self.assertEqual(get_last_key({'k1':'v1','k2':'v2'}),'k2')


    def test_get_last_item(self):
        with self.assertRaises(TypeError):
            get_last_item(cast(Iterable,None))
        self.assertIsNone(get_last_item([]))
        self.assertIsNone(get_last_item({}))
        self.assertIsNone(get_last_item(()))
        self.assertEqual(get_last_item(['first']),'first')
        self.assertEqual(get_last_item(['first','second']),'second')
        self.assertEqual(get_last_item({'first'}),'first')
        self.assertIn(get_last_item({'first','second'}),{'first','second'})
        self.assertEqual(get_last_item({'k1':'v1'}),('k1','v1'))
        self.assertEqual(get_last_item({'k1':'v1','k2':'v2'}),('k2','v2'))
        # looks like a 1-tuple containing a string is interpreted as an n-tuple of chars
        self.assertEqual(get_last_item(('first')),'t')
        self.assertEqual(get_last_item(('first','second')),'second')


    def test_get_last(self):
        with self.assertRaises(TypeError):
            get_last(cast(Iterable,None))
        self.assertIsNone(get_last([]))
        self.assertIsNone(get_last({}))
        self.assertIsNone(get_last(()))
        self.assertEqual(get_last(['first']),'first')
        self.assertEqual(get_last(['first','second']),'second')
        self.assertEqual(get_last({'first'}),'first')
        self.assertIn(get_last({'first','second'}),{'first','second'})
        self.assertEqual(get_last({'k1':'v1'}),'k1')
        self.assertEqual(get_last({'k1':'v1','k2':'v2'}),'k2')
        # looks like a 1-tuple containing a string is interpreted as an n-tuple of chars
        self.assertEqual(get_last(('first')),'t')
        self.assertEqual(get_last(('first','second')),'second')

    def test_get_first_value(self):
        with self.assertRaises(TypeError):
            get_first_value(cast(Mapping,None))
        self.assertIsNone(get_first_value({}))
        self.assertEqual(get_first_value({'k1':'v1'}),'v1')
        self.assertEqual(get_first_value({'k1':'v1','k2':'v2'}),'v1')


    def test_get_first_key(self):
        with self.assertRaises(TypeError):
            get_first_key(cast(Mapping,None))
        self.assertIsNone(get_first_key({}))
        self.assertEqual(get_first_key({'k1':'v1'}),'k1')
        self.assertEqual(get_first_key({'k1':'v1','k2':'v2'}),'k1')


    def test_get_first_item(self):
        with self.assertRaises(TypeError):
            get_first_item(cast(Iterable,None))
        self.assertIsNone(get_first_item([]))
        self.assertIsNone(get_first_item({}))
        self.assertIsNone(get_first_item(()))
        self.assertEqual(get_first_item(['first']),'first')
        self.assertEqual(get_first_item(['first','second']),'first')
        self.assertEqual(get_first_item({'first'}),'first')
        self.assertIn(get_first_item({'first','second'}),{'first','second'})
        self.assertEqual(get_first_item({'k1':'v1'}),('k1','v1'))
        self.assertEqual(get_first_item({'k1':'v1','k2':'v2'}),('k1','v1'))
        # looks like a 1-tuple containing a string is interpreted as an n-tuple of chars
        self.assertEqual(get_first_item(('first')),'f')
        self.assertEqual(get_first_item(('first','second')),'first')


    def test_get_first(self):
        with self.assertRaises(TypeError):
            get_first(cast(Iterable,None))
        self.assertIsNone(get_first([]))
        self.assertIsNone(get_first({}))
        self.assertIsNone(get_first(()))
        self.assertEqual(get_first(['first']),'first')
        self.assertEqual(get_first(['first','second']),'first')
        self.assertEqual(get_first({'first'}),'first')
        self.assertIn(get_first({'first','second'}),{'first','second'})
        self.assertEqual(get_first({'k1':'v1'}),'k1')
        self.assertEqual(get_first({'k1':'v1','k2':'v2'}),'k1')
        # looks like a 1-tuple containing a string is interpreted as an n-tuple of chars
        self.assertEqual(get_first(('first')),'f')
        self.assertEqual(get_first(('first','second')),'first')


    def setUp(self):
        configure_logging(logging.INFO)
        logging.debug("logging configured")


if __name__ == '__main__':
    unittest.main()