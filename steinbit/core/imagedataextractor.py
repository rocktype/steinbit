#!/usr/bin/env python3

"""
Image transformations and statistics
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
from sklearn.neighbors import NearestNeighbors
from .types import ColourMapping, Field
from PIL import Image


class ImageDataExtractor:
    """
    The ImageDataExtractor class combines tools to extract data
    from images via transformations
    """

    minerals: List[str]
    __neighbours: NearestNeighbors
    fields: Dict[str, Field]

    def __init__(
            self,
            mapping: ColourMapping,
            fields: Optional[Dict[str, Field]] = None):
        """
        Construct the extractor using a colour mapping appropriate
        to the images to be supplied. The mapping should assign a
        mineral name to each colour in the image.

        Parameters
        ----------
        mapping :
            A mapping between minerals and colours
        """
        self.__neighbours = NearestNeighbors(n_neighbors=1)
        self.__neighbours.fit(mapping.colours)
        self.minerals = list(mapping.minerals)
        self.fields = fields or {}

    def composition(self, image: Image) -> Tuple[float, Dict[str, int]]:
        """
        Construct a mapping from each mineral to the
        abundance of that mineral in the supplied image

        Parameters
        ----------
        image:
            An image with colours in the mapping

        Returns
        -------
        Tuple[float, Dict[str, int]]
            A tuple of the RMS error in the translation and a mapping from
            mineral names to counts
        """
        data = image.convert('RGB').tobytes()
        array = np.frombuffer(data, dtype=np.uint8).reshape(-1, 3)
        distances, indices = self.__neighbours.kneighbors(array)
        counts = np.bincount(indices.flatten())
        mapping = dict(zip(self.minerals, counts))
        error = np.sqrt(np.mean(np.square(distances.flatten())))
        return error, mapping

    def metadata(self, image: Image) -> Dict[str, Optional[str]]:
        """
        Extract the metadata from the image's exif data. Metadata is
        expected to be a ;-separated list of mappings, e.g.:

        Description:
            Wellbore:_25/2-18_C;
            Depth:1590m;
            RtID:RN2-006;
            Resolution:50micron;
            Supplier:Rocktype

        This is parsed using the field dictionary supplied to extract
        all of the possible fields.

        Parameters
        ----------
        image:
            An image with metadata to extra

        Returns
        -------
        Dict[str, str]
            A dictionary of metadata items
        """
        if 'Description' not in image.info:
            return {}
        items = image.info['Description'].split(';')
        metadata = {k.strip("' \t\v"): v[0].strip("' \t\v")
                    for k, *v in
                    [i.split(':') for i in items]
                    if len(v) == 1}
        return {k: v.extract(metadata) for k, v in self.fields.items()}
