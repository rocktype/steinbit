#!/usr/bin/env python3

"""
The configuration file
"""

from .core import ColourMapping

import os
import configparser
from typing import Optional
import pandas as pd


MODULEPATH = os.path.abspath(os.path.join(__file__, '../../'))


class ConfigException(Exception):
    """
    Raised if a configuration file is in
    the wrong format or cannot be parsed
    """


class Config:
    """
    Find and parse values from the configuration file
    """

    detailed_mapping: ColourMapping
    reduced_mapping: ColourMapping
    translation: pd.DataFrame

    @classmethod
    def search_config(cls):
        """
        Search for a config file
        """
        filename = 'steinbit.cfg'
        defaults = [
            os.path.join(os.getcwd(), filename),
            os.path.expanduser('~/' + filename),
            os.getenv('STEINBIT', default=None)]
        for path in defaults:
            if path and os.path.isfile(path):
                return path
        return None

    def __init__(self, filename: Optional[str]):
        """
        Parse the config file supplied
        """
        filename = filename or self.search_config()
        config = configparser.ConfigParser()
        if filename:
            config.read(filename)
        section = config['DEFAULT']
        detailed_mapping = section.get(
            'DetailedMapping',
            os.path.join(MODULEPATH, 'data/bls.csv'))
        reduced_mapping = section.get(
            'ReducedMapping',
            os.path.join(MODULEPATH, 'data/rs.csv'))
        translation = section.get(
            'Translation',
            os.path.join(MODULEPATH, 'data/translation.csv'))
        self.detailed_mapping = ColourMapping(pd.read_csv(detailed_mapping))
        self.reduced_mapping = ColourMapping(pd.read_csv(reduced_mapping))
        self.translation = pd.read_csv(translation)

        trns = self.translation
        detailed_list = set(trns[trns.columns[1]])
        reduced_list = set(trns[trns.columns[0]])
        if set(self.detailed_mapping.minerals) - detailed_list != set():
            raise ConfigException("""
                Translation detailed list (%s, column 2) does not
                match detailed list from colour mapping (%s).
                """ % (translation, detailed_mapping))
        if set(self.reduced_mapping.minerals) - reduced_list != set():
            raise ConfigException("""
                Translation reduced list (%s, column 1) does not
                match reduced list from colour mapping (%s).
                """ % (translation, detailed_mapping))