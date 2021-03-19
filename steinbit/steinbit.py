#!/usr/bin/env python3

from .core import ImageDataExtractor, Frame
from .config import Config

import argparse
from typing import Optional, List
import pandas as pd
from PIL import Image
from tqdm import tqdm
import magic


class Steinbit:

    config: Config

    def __init__(self, configfile: Optional[str] = None):
        self.config = Config(configfile)

    def process_files(self, files: List[str]) -> pd.DataFrame:
        """
        Process a list of images or CSVs and print out a combined CSV

        Parameters
        ----------
        files: List[str]
            A list of filenames to process

        Returns
        -------
        Frame
            A table mapping well depths to their compositions for
            each extractor used (detailed or reduced)
        """
        cfg = self.config
        result = Frame([
                ImageDataExtractor(cfg.detailed_mapping, cfg.fields),
                ImageDataExtractor(cfg.reduced_mapping, cfg.fields)
            ])
        for filepath in tqdm(files, desc="Processing files"):
            mime = magic.detect_from_filename(filepath).mime_type
            if not mime.startswith('image'):
                result.append_frame(pd.read_csv(filepath))
            else:
                result.append_image(Image.open(filepath))
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
            'files', type=str, nargs='+',
            help='images or csv files to parse')
        args = parser.parse_args()
        steinbit = Steinbit(configfile=args.config)
        frame = steinbit.process_files(args.files)
        if args.translate or frame.requires_translation():
            frame.apply_translation(steinbit.config.translation)
        result = frame.result()
        if args.percent:
            result = steinbit.percentages(result)
        if args.output:
            result.to_csv(args.output, index=False)
        else:
            print(result)
        return 0


if __name__ == '__main__':
    exit(Steinbit.run())
