
from typing import Any
from collections.abc import ItemsView
import logging
import unittest
import zipfile

from common.log import configure_logging
from common.introspect import *
from tests.data.test_targets import *

class IntrospectTests(unittest.TestCase):

    def test_has_attribute_value(self):
        base_target: BaseTestTarget = BaseTestTarget('attr1.value1', {'key':'value'})
        self.assertFalse(has_attribute_value(base_target,'does not exist'))
        self.assertTrue(has_attribute_value(base_target,'attr1'))
        self.assertTrue(has_attribute_value(base_target,'attr2'))

        base_target: BaseTestTarget = BaseTestTarget(None, None) # type: ignore
        self.assertFalse(has_attribute_value(base_target,'attr1'))
        self.assertFalse(has_attribute_value(base_target,'attr2'))

        derived_target: DerivedTestTarget = DerivedTestTarget('attr1.value1', {'key':'value'}, 'attr3.value1')
        self.assertFalse(has_attribute_value(derived_target,'does not exist'))
        self.assertTrue(has_attribute_value(derived_target,'attr1'))
        self.assertTrue(has_attribute_value(derived_target,'attr2'))
        self.assertTrue(has_attribute_value(derived_target,'attr3'))

        derived_target: DerivedTestTarget = DerivedTestTarget(None, None, None)  # type: ignore
        self.assertFalse(has_attribute_value(derived_target,'does not exist'))
        self.assertFalse(has_attribute_value(derived_target,'attr1'))
        self.assertFalse(has_attribute_value(derived_target,'attr2'))
        self.assertFalse(has_attribute_value(derived_target,'attr3'))


    def test_get_property_values(self):
        base_target: BaseTestTarget = BaseTestTarget('attr1.value1', {'key':'value'})
        property_values: dict[str,Any] = get_property_values(base_target)
        logging.debug(f"property_values: {property_values}")
        self.assertEqual(property_values, {'attr1': 'attr1.value1', 'attr2': {'key': 'value'}})

        property_values: dict[str,Any] = get_property_values(base_target, True)
        logging.debug(f"property_values: {property_values}")
        self.assertEqual(property_values, {'attr1': 'attr1.value1', 'attr2': {'key': 'value'}})

        derived_target: DerivedTestTarget = DerivedTestTarget('attr1.value1', {'key':'value'}, 'attr3.value1')

        property_values: dict[str,Any] = get_property_values(derived_target)
        logging.debug(f"property_values: {property_values}")
        self.assertEqual(property_values, {'attr3': 'attr3.value1'})

        property_values: dict[str,Any] = get_property_values(derived_target, True)
        logging.debug(f"property_values: {property_values}")
        self.assertEqual(property_values, {'attr1': 'attr1.value1','attr2': {'key': 'value'},'attr3': 'attr3.value1'})


    def test_get_attributes(self):
        base_target: BaseTestTarget = BaseTestTarget('attr1.value1', {'key':'value'})

        logging.debug(f"base_target: {base_target}")
        attributes: dict[str,Any] = get_attributes(base_target, ['attr1'])
        self.assertEqual(attributes, {'attr1': 'attr1.value1'})

        attributes: dict[str,Any] = get_attributes(base_target, ['attr2'])
        logging.debug(f"attributes: {attributes}")
        self.assertEqual(attributes, {'attr2': {'key': 'value'}})

        # demonstrates key order stability
        attributes: dict[str,Any] = get_attributes(base_target, ['attr2', 'attr1'])
        logging.debug(f"attributes: {attributes}")
        self.assertEqual(attributes, {'attr2': {'key': 'value'}, 'attr1': 'attr1.value1'})

        derived_target: DerivedTestTarget = DerivedTestTarget('attr1.value1', {'key':'value'}, 'attr3.value1')

        logging.debug(f"derived_target: {derived_target}")
        attributes: dict[str,Any] = get_attributes(derived_target, ['attr1'])
        self.assertEqual(attributes, {'attr1': 'attr1.value1'})

        attributes: dict[str,Any] = get_attributes(derived_target, ['attr2'])
        logging.debug(f"attributes: {attributes}")
        self.assertEqual(attributes, {'attr2': {'key': 'value'}})

        attributes: dict[str,Any] = get_attributes(derived_target, ['attr3'])
        self.assertEqual(attributes, {'attr3': 'attr3.value1'})

        attributes: dict[str,Any] = get_attributes(derived_target, ['attr1','attr2','attr3'])
        self.assertEqual(attributes, {'attr1': 'attr1.value1','attr2': {'key': 'value'},'attr3': 'attr3.value1'})


    def test_get_property_names(self):
        property_names: Iterable[str] = get_property_names(BaseTestTarget)
        logging.debug(f"property_names: {property_names}")
        self.assertEqual(property_names, {'attr1', 'attr2'})

        property_names: Iterable[str] = get_property_names(BaseTestTarget, True)
        logging.debug(f"property_names: {property_names}")
        self.assertEqual(property_names, {'attr1', 'attr2'})

        property_names: Iterable[str] = get_property_names(DerivedTestTarget)
        logging.debug(f"property_names: {property_names}")
        self.assertEqual(property_names, {'attr3'})

        property_names: Iterable[str] = get_property_names(DerivedTestTarget, True)
        logging.debug(f"property_names: {property_names}")
        self.assertEqual(property_names, {'attr1', 'attr2','attr3'})


    def test_get_properties(self):
        properties: dict[str,property] = get_properties(BaseTestTarget)
        logging.debug(f"properties: {properties}")
        self.assertEqual(properties.keys(), {'attr1', 'attr2'})

        properties: dict[str,property] = get_properties(BaseTestTarget, True)
        logging.debug(f"properties: {properties}")
        self.assertEqual(properties.keys(), {'attr1', 'attr2'})

        mro: tuple[type] = DerivedTestTarget.__mro__
        logging.debug(f"mro: {mro}")
        class_items: ItemsView[str,Any] = type(DerivedTestTarget).__dict__.items()
        logging.debug(f"class_items: {class_items}")

        properties: dict[str,property] = get_properties(DerivedTestTarget)
        logging.debug(f"properties: {properties}")
        self.assertEqual(properties.keys(), {'attr3'})

        properties: dict[str,property] = get_properties(DerivedTestTarget, True)
        logging.debug(f"properties: {properties}")
        self.assertEqual(properties.keys(), {'attr1', 'attr2','attr3'})


    def test_inspect(self):
        derived_target: DerivedTestTarget = DerivedTestTarget('attr1.value1', {'key':'value'}, 'attr3.value1')
        logging.debug(f"derived_target: {derived_target}")
    

    def setUp(self):
        configure_logging(logging.INFO)
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()