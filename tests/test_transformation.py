import unittest
from steinbit.core import Transformation, ColourMapping
import pandas as pd
from PIL import Image


class TransformationTest(unittest.TestCase):

    def test_image_composition_clean(self):
        mapping = ColourMapping(pd.DataFrame({
            'Names': ['A', 'B'],
            'Colours': ['#ffffff', '#000000']
        }))
        image = Image.new('RGB', (2, 2))
        image.putpixel((0, 0), (0, 0, 0))
        image.putpixel((0, 1), (255, 255, 255))
        image.putpixel((1, 0), (0, 0, 0))
        image.putpixel((1, 1), (255, 255, 255))
        trns = Transformation(mapping)
        error, counts = trns.composition(image)
        self.assertDictEqual(
                counts,
                {'A': 2, 'B': 2})
        self.assertEqual(error, 0)

    def test_image_composition_unclean(self):
        mapping = ColourMapping(pd.DataFrame({
            'Names': ['A', 'B'],
            'Colours': ['#ffffff', '#000000']
        }))
        image = Image.new('RGB', (2, 2))
        image.putpixel((0, 0), (100, 100, 100))
        image.putpixel((0, 1), (200, 200, 200))
        image.putpixel((1, 0), (100, 100, 100))
        image.putpixel((1, 1), (200, 200, 200))
        trns = Transformation(mapping)
        error, counts = trns.composition(image)
        self.assertDictEqual(
                counts,
                {'A': 2, 'B': 2})
        self.assertNotEqual(error, 0)
