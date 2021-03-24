#!/usr/bin/env python3

from .config import Config
from .create import SteinbitCreate
from .compare import SteinbitCompare

import traceback
import argparse


def main() -> int:
    "Main invocation"
    parser = argparse.ArgumentParser(
        description='Steinbit command line tool')
    parser.add_argument(
        '-c', '--config', type=str,
        help='a configuration file to use instead of the default')
    subparsers = parser.add_subparsers()
    subparsers.required = True
    subparsers.dest = 'command'
    SteinbitCreate.add_arguments(subparsers.add_parser('create'))
    SteinbitCompare.add_arguments(subparsers.add_parser('compare'))

    args = parser.parse_args()
    obj = args.clazz(Config(args.config))
    try:
        obj.run(args)
    except Exception:
        traceback.print_exc()
        return 1
    return 0


if __name__ == '__main__':
    exit(main())
