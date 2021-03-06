import os
import six
import networkx

from netdiff import BatmanParser
from netdiff import diff
from netdiff.tests import TestCase
from netdiff.exceptions import NetParserException


__all__ = ['TestBatmanParser']


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
iulinet = open('{0}/../static/batman.json'.format(CURRENT_DIR)).read()
iulinet2 = open('{0}/../static/batman-1+1.json'.format(CURRENT_DIR)).read()


class TestBatmanParser(TestCase):

    def test_parse(self):
        p = BatmanParser(iulinet)
        self.assertIsInstance(p.graph, networkx.Graph)

    def test_parse_exception(self):
        with self.assertRaises(NetParserException):
            BatmanParser('{ "test": "test" }')

    def test_parse_exception2(self):
        with self.assertRaises(NetParserException):
            BatmanParser('{ "topology": [{ "a": "a" }] }')

    def test_json_dict(self):
        p = BatmanParser(iulinet)
        data = p.json(dict=True)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['type'], 'NetworkGraph')
        self.assertEqual(data['protocol'], 'batman-adv')
        self.assertEqual(data['version'], '2014.3.0')
        self.assertEqual(data['metric'], 'TQ')
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['links'], list)
        self.assertEqual(len(data['nodes']), 5)
        self.assertEqual(len(data['links']), 4)

    def test_json_string(self):
        p = BatmanParser(iulinet)
        data = p.json()
        self.assertIsInstance(data, six.string_types)
        self.assertIn('NetworkGraph', data)
        self.assertIn('protocol', data)
        self.assertIn('version', data)
        self.assertIn('metric', data)
        self.assertIn('batman-adv', data)
        self.assertIn('2014.3.0', data)
        self.assertIn('TQ', data)
        self.assertIn('links', data)
        self.assertIn('nodes', data)

    def test_added_removed_1_node(self):
        old = BatmanParser(iulinet)
        new = BatmanParser(iulinet2)
        result = diff(old, new)
        self.assertTrue(type(result) is dict)
        self.assertTrue(type(result['added']) is list)
        self.assertTrue(type(result['removed']) is list)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 1)
        self.assertEqual(len(result['removed']), 1)
        self._test_expected_links(
            links=result['added'],
            expected_links=[
                ('a0:f3:c1:96:94:10', '90:f6:52:f2:8c:2c')
            ]
        )
        self._test_expected_links(
            links=result['removed'],
            expected_links=[
                ('a0:f3:c1:96:94:06', '90:f6:52:f2:8c:2c')
            ]
        )

    def test_no_changes(self):
        old = BatmanParser(iulinet)
        new = BatmanParser(iulinet)
        result = diff(old, new)
        self.assertTrue(type(result) is dict)
        self.assertTrue(type(result['added']) is list)
        self.assertTrue(type(result['removed']) is list)
        # ensure there are no differences
        self.assertEqual(len(result['added']), 0)
        self.assertEqual(len(result['removed']), 0)
