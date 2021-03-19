#!/usr/bin/env python3

import unittest
from steinbit.core import (
        ImageDataExtractor, ColourMapping, Frame,
        ColumnMismatchException, InvalidTranslationException)
import pandas as pd
import numpy as np
from numpy.testing import assert_array_equal
from PIL import Image, ImageColor


def make_image(pixels):
    image = Image.new('RGB', (len(pixels), 1))
    for index, colour in enumerate(pixels):
        image.putpixel((index, 0), ImageColor.getcolor(colour, 'RGB'))
    return image


DETAILED_IMAGE = make_image([
    '#000000', '#333333', '#777777', '#aaaaaa', '#ffffff'
])

DETAILED_MAPPING = ColourMapping(pd.DataFrame({
    'Names': ['A0', 'A1', 'A2', 'B0', 'B1'],
    'Colours': ['#000000', '#333333', '#777777', '#aaaaaa', '#ffffff']
}))

DETAILED_DF = pd.DataFrame({
    'A0': [1],
    'A1': [1],
    'A2': [1],
    'B0': [1],
    'B1': [1]
})

REDUCED_IMAGE = make_image([
    '#000000', '#000000', '#ffffff', '#ffffff', '#ffffff'
])

REDUCED_MAPPING = ColourMapping(pd.DataFrame({
    'Names': ['A', 'B'],
    'Colours': ['#000000', '#ffffff']
}))

REDUCED_DF = pd.DataFrame({
    'A': [1],
    'B': [1]
})

TRANSLATION = pd.DataFrame({
    'Reduced': ['A', 'A', 'A', 'B', 'B'],
    'Detailed': ['A0', 'A1', 'A2', 'B0', 'B1']
})


class FrameTest(unittest.TestCase):

    def test_frame_partitions_images(self):
        frame = Frame([
            ImageDataExtractor(DETAILED_MAPPING),
            ImageDataExtractor(REDUCED_MAPPING)])
        frame.append_image(DETAILED_IMAGE)
        frame.append_image(REDUCED_IMAGE)
        self.assertTrue(frame.requires_translation())

    def test_frame_partitions_df(self):
        frame = Frame([
            ImageDataExtractor(DETAILED_MAPPING),
            ImageDataExtractor(REDUCED_MAPPING)])
        frame.append_frame(REDUCED_DF)
        frame.append_frame(DETAILED_DF)
        self.assertTrue(frame.requires_translation())

    def test_frame_detects_bad_df(self):
        frame = Frame([
            ImageDataExtractor(DETAILED_MAPPING),
            ImageDataExtractor(REDUCED_MAPPING)])
        with self.assertRaises(ColumnMismatchException):
            frame.append_frame(pd.DataFrame({
                'No matching column': [1]}))

    def test_frame_translates(self):
        frame = Frame([
            ImageDataExtractor(DETAILED_MAPPING),
            ImageDataExtractor(REDUCED_MAPPING)])
        frame.append_frame(REDUCED_DF)
        frame.append_frame(DETAILED_DF)
        self.assertTrue(frame.requires_translation())
        frame.apply_translation(TRANSLATION)
        self.assertFalse(frame.requires_translation())

    def test_frame_translates_correctly(self):
        frame = Frame([
            ImageDataExtractor(DETAILED_MAPPING),
            ImageDataExtractor(REDUCED_MAPPING)])
        frame.append_frame(REDUCED_DF)
        frame.append_frame(DETAILED_DF)
        frame.apply_translation(TRANSLATION)
        assert_array_equal(frame.result().values, np.array([[1, 1], [3, 2]]))

    def test_frame_requires_good_translation(self):
        frame = Frame([
            ImageDataExtractor(DETAILED_MAPPING),
            ImageDataExtractor(REDUCED_MAPPING)])
        frame.append_frame(REDUCED_DF)
        frame.append_frame(DETAILED_DF)
        with self.assertRaises(InvalidTranslationException):
            frame.apply_translation(pd.DataFrame({
                'Missing': ['Undefined']}))
        with self.assertRaises(ColumnMismatchException):
            frame.apply_translation(pd.DataFrame({
                'Missing': ['Undefined'],
                'Something': ['Undefined']}))
