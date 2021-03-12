#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
import pandas as pd
from typing import List

from .core import RequiredFields
from .tool import SteinbitTool
from .create import SteinbitCreate


EPSILON = 0.01


def has_percent_row(minerals: List[str], df: pd.DataFrame) -> bool:
    """
    Return true if this frame has a percentage row
    """
    return any(abs(x - 100) < EPSILON for x in df[minerals].sum(axis=1))


class SteinbitCompare(SteinbitTool):

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        """
        Add command line arguments for the compare tool
        """
        parser.set_defaults(clazz=cls)
        parser.add_argument(
            'file1', type=str, nargs=1,
            help='The first file to compare')
        parser.add_argument(
            'file2', type=str, nargs=1,
            help='The second file to compare')

    def run(self, args: Namespace):
        """
        Compare files by automatically applying any
        required translations
        """
        create = SteinbitCreate(self.config)
        frame1 = create.process_files(args.file1)
        frame2 = create.process_files(args.file2)

        if frame1.requires_translation() or frame2.requires_translation():
            print("Frames require translation...")
            frame1.translate()
            frame2.translate()
        result1 = frame1.result()
        result2 = frame2.result()
        minerals = frame1.minerals()

        if any(has_percent_row(minerals, r) for r in [result1, result2]):
            print("Converting to percentage-based")
            result1 = create.percentages(result1)
            result2 = create.percentages(result2)

        columns = set(result1.columns).intersection(result2.columns)
        extra1 = set(result1.columns) - columns
        extra2 = set(result2.columns) - columns

        print("Comparison result:")
        if extra1:
            print("Extra columns in %s: [%s]" % (
                args.file1[0],
                ", ".join(extra1)))
        if extra2:
            print("Extra columns in %s: [%s]" % (
                args.file2[0],
                ", ".join(extra2)))
        print("-" * 40)
        result1.set_index(RequiredFields.DEPTH.value, inplace=True, drop=False)
        result2.set_index(RequiredFields.DEPTH.value, inplace=True, drop=False)
        comparison = result1[columns].compare(result2[columns])
        if len(comparison.index) == 0:
            print("File data in matching columns is identical")
        else:
            print(comparison.rename(columns={
                'self': args.file1[0], 'other': args.file2[0]}))
