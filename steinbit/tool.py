#!/usr/bin/env python3

from .config import Config
from argparse import ArgumentParser, Namespace


class SteinbitTool:
    """
    Abstract base class for all command line tools
    """

    config: Config

    def __init__(self, config: Config):
        self.config = config

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        """
        Add command line arguments for the sub-command
        """
        raise NotImplementedError()

    def run(self, args: Namespace):
        """
        Run this sub-command
        """
        raise NotImplementedError()
