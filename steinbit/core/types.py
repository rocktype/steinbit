#!/usr/bin/env python3

"""
The traits module supplies type information for common
types and formats
"""

from typing import List, Tuple, Dict, Pattern, Optional
import numpy as np
import pandas as pd
import re
from PIL import ImageColor


class ColourMapping:
    """
    The ColourMapping class represents a mapping from minerals
    to colours and back.
    """

    colours: np.ndarray  # NDArray[(Any, 3), Int[8]]
    minerals: List[str]

    @staticmethod
    def __asrgb(colour: str) -> Tuple[int, int, int]:
        """
        Convert the colour string to an R, G, B value

        Parameters
        ----------
        colour: str
            A colour string, e.g. #ff00ff

        Returns
        -------
        A tuple of Red, Green and Blue integers in the range
        0 to 255
        """
        return ImageColor.getcolor(colour, 'RGB')

    def __init__(self, mapping: pd.DataFrame):
        """
        Construct a ColourMapping directly from a mapping.
        Supported mapping constructions are:

        DataFrame[str, int, int, int] : Name <-> R, G, B
        DataFrame[str, str] : Name <-> Colour string

        Parameters:
        -----------
        mapping: pd.DataFrame
            A mapping used to map image colours to mineral names
        """
        cols = mapping.columns
        if len(cols) == 4:
            self.colours = np.array(mapping[cols[1:4]], dtype=np.uint8)
        elif len(cols) == 2:
            self.colours = np.array([
                ColourMapping.__asrgb(x)
                for x in mapping[cols[1]]], dtype=np.uint8)
        else:
            raise TypeError("Mapping must be an (N,2) or (N,4) array")
        self.minerals = list(mapping[cols[0]])


class Field:
    """
    Represents a metadata field

    A field of the form:
    <exif, regex>
    extracts the item named 'exif' from the image metadata
    and applies the given regex
    """

    exif: str
    regex: Pattern

    def __init__(self, exif: str, regex: Optional[str] = None):
        """
        Construct a field from an exif metadata item and a regex
        """
        self.exif = exif
        self.regex = re.compile(regex) if regex else re.compile('(.*)')

    def extract(self, metadata: Dict[str, str]) -> Optional[str]:
        """
        Extract this field from the metadata
        """
        if self.exif not in metadata:
            return None
        match = self.regex.match(metadata[self.exif])
        if not match:
            return None
        return match.group(1)
