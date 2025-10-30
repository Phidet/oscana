"""\
oscana / data / transform.py

--------------------------------------------------------------------------------

Author - Aditya Marathe
Email  - aditya.marathe.20@ucl.ac.uk

--------------------------------------------------------------------------------
"""

from __future__ import annotations

__all__ = ["TransformBase"]

from typing import TYPE_CHECKING, Any

import re
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .data_handler import DataHandler


# ============================== [ Constants  ] ============================== #

TRANSFORM_NAME_REGEX = re.compile(r"^(tfm|cut)_(\d{8})_(.+)$")


# =========================== [ Helper Functions ] =========================== #


def _get_name_matches(class_name: str) -> re.Match[str]:
    """\
    [ Internal ] Get the regex match object for the transform class name.

    Parameters
    ----------
    class_name : str
        The class name of the transform.

    Returns
    -------
    re.Match[str]
        The regex match object for the transform class name.
    """
    match = TRANSFORM_NAME_REGEX.match(class_name)

    if match is None:
        raise ValueError(
            f"Transform class name `{class_name}` does not conform to the "
            'naming convention "tfm_<date>_<name>" or "cut_<date>_<name>".'
        )

    return match


# ============================== [ Transforms ] ============================== #


class TransformBase(ABC):
    """\
    Transform Base Class
    --------------------
    
    This is the base class for all transform functions. It is used to register
    transform functions in the `DataHandler` class.
    """

    def __init__(self, **kwargs: Any) -> None:
        """\
        Initialize the transform function.

        Parameters
        ----------
        kwargs: dict[str, Any]
            The keyword arguments to pass to the transform function.
        """
        self._kwargs: dict[str, Any] = kwargs

    @abstractmethod
    def _transform(self, dh: DataHandler) -> tuple[Any, Any]:
        """\
        Transform the data.

        Parameters
        ----------
        dh: DataHandler
            The data handler object.

        Returns
        -------
        tuple[Any, Any]
            The data and cuts tables.
        """
        pass

    def is_cut(self) -> bool:
        """\
        Check if the transform is a cut.

        Returns
        -------
        bool
            True if the transform is a cut, False otherwise.
        """
        return self.prefix == "cut"

    # Note: I can see how this method name can cause some confusion...

    def is_transform(self) -> bool:
        """\
        Check if the transform is a transform.

        Returns
        -------
        bool
            True if the transform is a transform, False otherwise.
        """
        return self.prefix == "tfm"

    @property
    def prefix(self) -> str:
        """\
        Get the prefix of the transform function.

        Returns
        -------
        str
            The prefix of the transform function.
        """
        return _get_name_matches(self.__class__.__name__).group(1)

    @property
    def name(self) -> str:
        """\
        Get the name of the transform function.
            Returns
        -------
        str
            The name of the transform function.
        """
        return _get_name_matches(self.__class__.__name__).group(3)

    @property
    def date(self) -> str:
        """\
        Get the date of the transform function.

        Returns
        -------
        datetime
            The date of the transform function.
        """
        date_str = _get_name_matches(self.__class__.__name__).group(2)
        return f"{date_str[6:8]}/{date_str[4:6]}/{date_str[0:4]}"

    def __call__(self, dh: DataHandler) -> tuple[Any, Any]:
        """\
        Call the transform function.

        Parameters
        ----------
        dh: DataHandler
            The data to transform.

        Returns
        -------
        tuple[Any, Any]
            The data and cuts tables.
        """
        return self._transform(dh=dh)

    def __str__(self) -> str:
        """\
        String representation of the transform function.

        Returns
        -------
        str
            The string representation of the transform function.
        """
        return (
            f"oscana.{self.__class__.__name__}("
            + ", ".join([f"{k}={repr(v)}" for k, v in self._kwargs.items()])
            + ")"
        )

    def __repr__(self) -> str:
        return str(self)
