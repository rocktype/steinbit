import unittest
from steinbit.core import ImageDataExtractor, ColourMapping, Field
import pandas as pd
from PIL import Image

MAPPING = ColourMapping(pd.DataFrame({
    'Names': ['A', 'B'],
    'Colours': ['#ffffff', '#000000']
}))


class ImageDataExtractorTest(unittest.TestCase):

    def test_image_composition_clean(self):
        image = Image.new('RGB', (2, 2))
        image.putpixel((0, 0), (0, 0, 0))
        image.putpixel((0, 1), (255, 255, 255))
        image.putpixel((1, 0), (0, 0, 0))
        image.putpixel((1, 1), (255, 255, 255))
        extractor = ImageDataExtractor(MAPPING)
        error, counts = extractor.composition(image)
        self.assertDictEqual(
                counts,
                {'A': 2, 'B': 2})
        self.assertEqual(error, 0)

    def test_image_composition_unclean(self):
        image = Image.new('RGB', (2, 2))
        image.putpixel((0, 0), (100, 100, 100))
        image.putpixel((0, 1), (200, 200, 200))
        image.putpixel((1, 0), (100, 100, 100))
        image.putpixel((1, 1), (200, 200, 200))
        extractor = ImageDataExtractor(MAPPING)
        error, counts = extractor.composition(image)
        self.assertDictEqual(
                counts,
                {'A': 2, 'B': 2})
        self.assertNotEqual(error, 0)

    def test_metadata(self):
        image = Image.new('RGB', (2, 2))
        image.info['Description'] = "a:b;x:bcde;Z"
        extractor = ImageDataExtractor(MAPPING, {
            '1': Field('a'),
            '2': Field('x', 'b([cd]*)e')})
        self.assertDictEqual(
            extractor.metadata(image),
            {'1': 'b', '2': 'cd'})
