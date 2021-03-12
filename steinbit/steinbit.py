#!/usr/bin/env python3

from .core import Transformation
from .config import Config

import os
import argparse
from typing import Optional, List
import pandas as pd
from PIL import Image
from tqdm import tqdm


class Steinbit:

    config: Config

    def __init__(self, configfile: Optional[str] = None):
        self.config = Config(configfile)

    def process_images(self, images: List[str]) -> pd.DataFrame:
        """
        Process a list of images and print out a CSV

        Parameters
        ----------
        images: List[str]
            A list of image filenames to process

        Returns
        -------
        pd.DataFrame
            A table mapping images to their compositions
        """
        transformation = Transformation(self.config.detailed_mapping)
        result = pd.DataFrame()
        errors = []
        for image in tqdm(images, desc="Processing images"):
            image_data = Image.open(image)
            error, counts = transformation.composition(image_data)
            errors.append(error)
            result = result.append(counts, ignore_index=True)
        result['Filename'] = [os.path.basename(i) for i in images]
        result['Error'] = errors
        cols = result.columns.to_list()
        return result[cols[-2:] + cols[:-2]]

    def translate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reduce the supplied dataframe using the translation matrix

        Parameters
        ----------
        df: pd.DataFrame
            A dataframe of filenames, their composition and their RMS error

        Returns
        -------
        pd.DataFrame
            A dataframe calculated by mapping the minerals to a reduced set
        """
        trns = self.config.translation
        grouped = trns.groupby(by=trns.columns[0])
        result = pd.DataFrame()
        extra = [c for c in df.columns
                 if c not in self.config.detailed_mapping.minerals]
        result[extra] = df[extra]
        for reduced, basic in grouped:
            result[reduced] = sum(
                    df[b[2]]
                    for b in basic.itertuples()
                    if b[2] in df.columns)

        return result

    def percentages(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert an output in pixel numbers to an output in percentages

        Parameters
        ----------
        df: pd.DataFrame
            A dataframe of filenames, their composition and their RMS error

        Returns
        -------
        pd.DataFrame
            A dataframe calculated by converting the sums into percentages
        """
        cols = list(
            set(self.config.detailed_mapping.minerals +
                self.config.reduced_mapping.minerals
                ).intersection(df.columns))
        df[cols] = df[cols].div(df[cols].sum(axis=1), axis=0).multiply(100)
        return df

    @classmethod
    def run(cls):
        parser = argparse.ArgumentParser(
            description='Steinbit command line tool')
        parser.add_argument(
            '-c', '--config', type=str,
            help='a configuration file to use instead of the default')
        parser.add_argument(
            '-o', '--output', type=str,
            help='the output file to write to')
        parser.add_argument(
            '-t', '--translate', action='store_true',
            help='Reduce the output list by applying the transformation')
        parser.add_argument(
            '-p', '--percent', action='store_true',
            help='Write percentages rather than raw pixel counts')
        parser.add_argument(
            'images', type=str, nargs='+',
            help='images to parse')
        args = parser.parse_args()
        steinbit = Steinbit(configfile=args.config)
        result = steinbit.process_images(args.images)
        if args.translate:
            result = steinbit.translate(result)
        if args.percent:
            result = steinbit.percentages(result)
        if args.output:
            result.to_csv(args.output, index=False)
        else:
            print(result)
        return 0


if __name__ == '__main__':
    exit(Steinbit.run())
