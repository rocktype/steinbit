#!/usr/bin/env python3

"""
Encapsulate frame types from sets of mappings
"""

from typing import List, Tuple, Any, Dict, Iterable, Optional
from PIL import Image
from .imagedataextractor import ImageDataExtractor
import math
import pandas as pd
from enum import Enum


class ColumnMismatchException(Exception):
    """
    An exception thrown when the number of columns
    in the supplied data do not match those of an
    extractor used to construct a frame
    """


class ConsistencyException(Exception):
    """
    An exception thrown when the consistency of the
    frame is violated
    """


class InvalidTranslationException(Exception):
    """
    Thrown if an invalid translation is supplied
    """


class RequiredFields(Enum):
    """
    Fields that absolutely must be included in the configuration
    """
    D_UNIT = 'd_unit'
    DEPTH = 'depth'
    WELL = 'well'
    BACKGROUND = 'background'

    def is_consistent(self):
        "Return true if this field is consistent"
        return self in [RequiredFields.D_UNIT, RequiredFields.WELL]

    def match_name(self, names: Iterable[str]) -> Optional[str]:
        "Find a matching name from a list of names"
        try:
            return next(x for x in names if x.lower() == self.value.lower())
        except StopIteration:
            return None


class Frame:
    """
    A frame holds a list of Pandas Dataframes and a
    list of extractors that are used to construct rows
    in each frame.
    """

    data: List[pd.DataFrame]
    extractors: List[ImageDataExtractor]

    def __init__(self, extractors: List[ImageDataExtractor]):
        """
        Construct a Frame from a list of extractors,
        the appropriate extractor will be used to match
        the CSV or image supplied and the result stored
        in the matching section.

        Parameters
        ----------
        extractors: List[ImageDataExtractor]
            A non-empty list of image data extractors
        """
        self.extractors = extractors
        self.data = [pd.DataFrame() for _ in self.extractors]

    def __eindex_by_cols(self, columns: List[str]):
        """
        Find an extractor by a list of columns

        Parameters
        ----------
        columns: List[str]
            The list of columns to match on
        """
        cset = set(c.lower() for c in columns)
        matches = []
        unmatched = []
        for idx, extractor in enumerate(self.extractors):
            eset = set(x.lower() for x in extractor.minerals)
            eset -= {RequiredFields.BACKGROUND.value}
            if eset - cset == set():
                matches.append((len(eset - cset), idx))
            else:
                unmatched.append((idx, next((eset - cset).__iter__())))
        if matches:
            return sorted(matches, key=lambda x: x[0])[0][1]
        raise ColumnMismatchException(
            "Unmatched columns: {%s} not in [%s]" % (
                ", ".join("%d: %s" % (i, v) for i, v in unmatched),
                ", ".join(cset)))

    def __check_frame(self):
        """
        Check consistency of frame
        """
        for column in RequiredFields.__members__.values():
            for data in self.data:
                if len(data.columns) == 0:
                    continue
                matched = column.match_name(data.columns)
                if not matched:
                    raise ConsistencyException(
                        "Required column %s is missing" % column.value)
                if not column.is_consistent():
                    continue
                items = data[matched].drop_duplicates()
                if len(items) > 1:
                    raise ConsistencyException(
                        "%s is not consistent, values: [%s]" % (
                            column.value,
                            ", ".join(items.tolist())))

    @staticmethod
    def __sq_diff(value):
        """
        Guess a square difference from a sum to calculate background
        """
        if value < 100:
            return 100.0 - value
        side = int(math.sqrt(value) + 1)
        return side * side

    def add_background(self, row: pd.DataFrame, index: int):
        """
        Add in the missing background column
        """
        minerals = [
            x for x in self.extractors[index].minerals
            if x.lower() != RequiredFields.BACKGROUND.value]
        background = row[minerals].sum(axis=1).map(Frame.__sq_diff)
        row[RequiredFields.BACKGROUND.value] = background

    def append_frame(self, row: pd.DataFrame):
        """
        Append a new data frame

        Parameters
        ----------
        row: pd.DataFrame
            A data-frame to be appended
        """
        index = self.__eindex_by_cols(row.columns)
        if RequiredFields.BACKGROUND.value not in row.columns:
            self.add_background(row, index)
        self.data[index] = self.data[index].append(row)
        self.__check_frame()

    def __min_error_index(self, counts: List[Tuple[float, Any]]):
        """
        Return the index of the element with the minimum error
        and the lowest number of minerals if two sets have the
        same error.
        """
        errors = [
            (c[0], len(self.extractors[i].minerals))
            for i, c in enumerate(counts)]
        return errors.index(min(errors))

    def append_image(self, image_data: Image):
        """
        Append an image

        Parameters
        ----------
        image: Image
            An image to be appended
        """
        results = [e.composition(image_data) for e in self.extractors]
        index = self.__min_error_index(results)
        fields = self.extractors[index].metadata(image_data)

        row: Dict[str, Any] = {}
        row.update(results[index][1])
        row.update(fields)
        if RequiredFields.BACKGROUND.value not in row:
            row[RequiredFields.BACKGROUND.value] = 0
        self.data[index] = self.data[index].append(row, ignore_index=True)
        self.__check_frame()

    def apply_translation(self, translation: pd.DataFrame):
        """
        Apply a translation matrix to reduce one form of
        extraction to another.

        Parameters
        ----------
        translation: pd.DataFrame
            A translation such that for a pair of extractors
            each element in one extractor is injectively mapped to some
            element in the other.
        """
        if len(translation.columns) != 2:
            raise InvalidTranslationException()
        source_columns = translation[translation.columns[1]].tolist()
        source = self.__eindex_by_cols(source_columns)
        target_columns = translation[translation.columns[0]].tolist()
        target = self.__eindex_by_cols(target_columns)

        df = self.data[source]
        grouped = translation.groupby(by=translation.columns[0])
        extra = [c for c in df.columns if c not in source_columns]
        result = pd.DataFrame()
        result[extra] = df[extra]
        for reduced, basic in grouped:
            result[reduced] = sum(
                    df[b[2]]
                    for b in basic.itertuples()
                    if b[2] in df.columns)
        self.data[target] = self.data[target].append(result)
        self.data[source].drop(df.index, inplace=True)

    def requires_translation(self) -> bool:
        """
        Determine whether this frame needs a translation applied

        Returns
        -------
            True, if there are multiple types of data and a translation
            must be performed
        """
        return sum(1 for x in self.data if len(x.index) > 0) > 1

    def result(self) -> pd.DataFrame:
        """
        Return the final resulting dataframe after all translations
        have been applied
        """
        return [x for x in self.data if len(x.index) > 0][0]

    def minerals(self) -> List[str]:
        """
        Return the mineral list for the extractor in use
        """
        return [x.minerals
                for x, d in zip(self.extractors, self.data)
                if len(d.index) > 0][0]
