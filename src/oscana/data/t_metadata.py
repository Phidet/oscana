"""\
oscana / data / t_metadata.py
--------------------------------------------------------------------------------

Author - Aditya Marathe
Email  - aditya.marathe.20@ucl.ac.uk

--------------------------------------------------------------------------------

This module contains the `TransformMetadata` class, which is used to keep track
of the cuts and transforms applied to the loaded data. This is useful when we
want to merge two datasets, and we want to ensure that the same cuts and
transforms have been applied to both datasets.
"""

from __future__ import annotations

# Note: There is a compatibility issue with `dataclasses`--in older versions of
#       Python, the `slots` parameter is not available. I will solve this issue
#       if it arises.

__all__ = []

from typing import Any

import logging, re
from dataclasses import dataclass, field

from ..logger import _error
from .transform import TransformBase
from ..escape import Style

# =============================== [ Logging  ] =============================== #

_logger = logging.getLogger("Root")

# ============================== [ Constants  ] ============================== #

TRANSFORM_NAME_REGEX = re.compile(
    r"^uid_(?P<uid>\d{9})_(?P<type>tfm|cut)_(?P<date>\d{8})_(?P<name>.+)$"
)


# ============================ [ File Metadata  ] ============================ #


# TODO: Why are we using a tuple to store our transforms when there is a
#       perfectly sane way of doing this with a dictionary? Change this.


@dataclass(frozen=True, slots=True)
class TransformMetadata:
    """\
    Transform Metadata.

    Parameters
    ----------
    cuts : list[str]
        List of cuts.

    transforms : list[str]
        List of transforms.
    """

    transforms: list[tuple[str, dict[str, Any]]] = field(default_factory=list)

    def _add_transform(self, transform: TransformBase) -> None:
        """\
        Add a new transform to the metadata.

        Parameters
        ----------
        transform: TransformBase
            The transform to add.

        Notes
        -----
        The function names must follow the Oscana naming convention:
            {`cut` / `tfm`}_{YYYYMMDD}_{name}
        """
        # Note: Here I am not checking if the transform has already been added!
        #       This will be taken care of by the `DataHandler` class.

        if not isinstance(transform, TransformBase):
            _error(
                TypeError,
                "Transform must be an instance of `TransformBase`.",
                _logger,
            )

        self.transforms.append(
            (
                transform.__class__.__name__,
                transform._kwargs,
            )
        )

    def _extract_transform_name(self, name: str) -> str:
        """\
        [ Internal ] Extract the transform name from the function name.
        
        Parameters
        ----------
        name : str
            The function name.

        Returns
        -------
        str
            The transform name.
        """
        return "_".join(name.split("_")[2:]).lower()

    def to_dict(self) -> dict[str, dict[str, Any]]:
        """\
        Get the transforms as a dictionary.

        Returns
        -------
        dict[str, dict[str, Any]]
            A dictionary containing the metadata. The keys are the name of the
            transform and the values are keyword arguments passed to the 
            function.
        """
        # Note: Neat way to avoid overwriting repeated transform names.

        return {
            (f"uid_{i:09d}_" + str(data[0])): data[1]
            for i, data in enumerate(self.transforms)
        }

    @staticmethod
    def from_dict(meta_dict: dict[str, dict[str, Any]]) -> TransformMetadata:
        """\
        Load the metadata from a dictionary.

        Parameters
        ----------
        meta_dict : dict[str, dict[str, Any]]
            The dictionary containing the transform metadata.
        """
        metadata = TransformMetadata()

        for name, kwargs in meta_dict.items():
            if not TRANSFORM_NAME_REGEX.match(name):
                _error(
                    ValueError,
                    (
                        f"Transform name '{name}' does not follow the "
                        "naming convention 'uid_XXXXXXXXX_{tfm/cut}_YYYYMMDD_"
                        r"{name}'."
                    ),
                    _logger,
                )

            metadata.transforms.append((name[14:], kwargs))

        return metadata

    def print(self) -> None:
        """\
        Print the metadata.
        """
        print(Style.BD + "Cuts & Transforms\n-----------------" + Style.R)
        for transform in self.transforms:
            type_ = "C" if transform[0].startswith("cut_") else "T"

            fg_colour = Style.FG[88] if type_ == "C" else Style.FG[27]

            name = self._extract_transform_name(transform[0])
            kwargs = ", ".join(
                f"{key}={Style.IT +  Style.FG[33] + repr(value) + Style.R}"
                for key, value in transform[1].items()
            )

            print(
                f"{fg_colour}[{type_}]{Style.R}"
                f"   {name}{Style.FG[3]}({Style.R}{kwargs}"
                f"{Style.FG[3]}){Style.R}"
            )

        if not len(self.transforms):
            print(f"\t{Style.FG[8]}[ No Cuts & Transforms Applied ]{Style.R}")

    def __eq__(self, other: object) -> bool:
        """\
        Check if the metadata is the same for two datasets.

        Parameters
        ----------
        other : object
            The other object to compare with.

        Returns
        -------
        bool
            True if the metadata is the same, False otherwise.
        """
        # (1) Check if the other object is of the same type.

        if not isinstance(other, TransformMetadata):
            _error(
                ValueError,
                (
                    f"{self.__class__.__name__} can only be compared with "
                    "another instance of the same class."
                ),
                _logger,
            )

        # (2) Extract the transfrom names.

        these_names = [
            f"{self._extract_transform_name(data[0])}("
            + ", ".join(f"{key}={value}" for key, value in data[1].items())
            + ")"
            for data in self.transforms
        ]
        other_names = [
            f"{other._extract_transform_name(data[0])}("
            + ", ".join(f"{key}={value}" for key, value in data[1].items())
            + ")"
            for data in other.transforms
        ]

        return these_names == other_names

    def __ne__(self, other: object) -> bool:
        """\
        Check if the metadata is not the same for two datasets.

        Parameters
        ----------
        other : object
            The other object to compare with.

        Returns
        -------
        bool
            True if the metadata is not the same, False otherwise.
        """
        return not self.__eq__(other)

    def __str__(self) -> str:
        return (
            f"oscana.{self.__class__.__name__}"
            f"(n_transforms={len(self.transforms)})"
        )

    def __repr__(self) -> str:
        return str(self)
