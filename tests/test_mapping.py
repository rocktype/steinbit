import unittest
from steinbit.core import ColourMapping
import pandas as pd


class MappingTest(unittest.TestCase):

    def test_converted_mapping(self):
        mapping = ColourMapping(pd.DataFrame({
            'Names': ['A', 'B'],
            'Colours': ['#ffffff', '#000000']
        }))
        self.assertListEqual(mapping.minerals, ['A', 'B'])
        self.assertListEqual(mapping.colours.tolist(), [
            [255, 255, 255],
            [0, 0, 0]
        ])

    def test_direct_mapping(self):
        mapping = ColourMapping(pd.DataFrame({
            'Names': ['A', 'B'],
            'R': [255, 0],
            'G': [255, 0],
            'B': [255, 0]
        }))
        self.assertListEqual(mapping.minerals, ['A', 'B'])
        self.assertListEqual(mapping.colours.tolist(), [
            [255, 255, 255],
            [0, 0, 0]
        ])

    def test_mapping_wrong_columns(self):
        self.assertRaises(
                TypeError,
                ColourMapping,
                pd.DataFrame({'a': [], 'b': [], 'c': []}))
        self.assertRaises(
                TypeError,
                ColourMapping,
                pd.DataFrame({'a': []}))
