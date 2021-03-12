#!/usr/bin/env python3

"""
Image transformations and statistics
"""

from typing import Dict, List, Tuple
import numpy as np
from sklearn.neighbors import NearestNeighbors
from .types import ColourMapping
from PIL import Image


class Transformation:
    """
    The transformation class represents a transformation
    """

    minerals: List[str]
    __neighbours: NearestNeighbors

    def __init__(self, mapping: ColourMapping):
        """
        ???

        Parameters
        ----------
        mapping :
            A mapping between minerals and colours
        """
        self.__neighbours = NearestNeighbors(n_neighbors=1)
        self.__neighbours.fit(mapping.colours)
        self.minerals = list(mapping.minerals)

    def composition(self, image: Image) -> Tuple[float, Dict[str, int]]:
        """
        Construct a mapping from each mineral to the
        abundance of that mineral in the supplied image

        Parameters
        ----------
        image:
            An image with colours in the mapping

        Returns:
        --------
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
