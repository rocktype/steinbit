#!/usr/bin/env python3

from .core import (
    ImageDataExtractor, Frame, ConsistencyException, RequiredFields
)
from .config import Config
from .mnemonic import mnemonics

from argparse import ArgumentParser, Namespace
from typing import Iterator
import pandas as pd
from PIL import Image
from tqdm import tqdm
import magic
import lasio


class SteinbitCreate:

    config: Config

    def __init__(self, config: Config):
        self.config = config

    @staticmethod
    def append_file(filepath: str, result: Frame):
        """
        Append a single file to the frame
        """
        mime = magic.detect_from_filename(filepath).mime_type
        if not mime.startswith('image'):
            try:
                lasfile = lasio.read(filepath)
                frame = lasfile.df().reset_index().rename(
                    columns={x.mnemonic: x.descr for x in lasfile.curves})
                headers = {
                        RequiredFields.D_UNIT.value: lasfile.well.STEP.unit,
                        RequiredFields.WELL.value: lasfile.well.WELL.value}
                for field, header in headers.items():
                    frame[field] = [header for _ in frame.index]
                result.append_frame(frame)
            except KeyError:
                result.append_frame(pd.read_csv(filepath))
        else:
            result.append_image(Image.open(filepath))

    def process_files(self, files: Iterator[str]) -> pd.DataFrame:
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
        for filepath in files:
            try:
                SteinbitCreate.append_file(filepath, result)
            except ConsistencyException:
                print("Consistency error processing: %s" % filepath)
                raise
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
    def output_las(cls, frame: Frame, output: str):
        """
        Output a LAS file
        """
        df = frame.result()
        unit = df[RequiredFields.D_UNIT.value][0]
        depths = df[RequiredFields.DEPTH.value]
        strt = depths.min()
        stop = depths.max()
        step = (stop - strt) / len(df.index)
        las = lasio.LASFile()
        las.well.STRT.unit = unit
        las.well.STRT.value = strt
        las.well.STOP.unit = unit
        las.well.STOP.value = stop
        las.well.STEP.unit = unit
        las.well.STEP.value = step or 1.0
        las.well.WELL.value = df[RequiredFields.WELL.value][0]

        columns = [RequiredFields.DEPTH.value] + frame.minerals()
        for mnemonic, column in zip(mnemonics(columns), columns):
            las.append_curve(mnemonic, df[column], descr=column)
        with open(output, mode="w") as handle:
            las.write(handle)

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
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
        parser.set_defaults(clazz=cls)

    def run(self, args: Namespace):
        frame = self.process_files(tqdm(args.files, desc="Processing files"))
        if args.translate or frame.requires_translation():
            frame.apply_translation(self.config.translation)
        result = frame.result()
        if args.percent:
            result = self.percentages(result)
        if args.output:
            if args.output.lower().endswith('las'):
                self.output_las(frame, args.output)
            else:
                result.to_csv(args.output, index=False)
        else:
            print(result)
