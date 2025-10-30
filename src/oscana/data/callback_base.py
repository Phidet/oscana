"""\
oscana / data / callback_base.py
--------------------------------------------------------------------------------

Author - Aditya Marathe
Email  - aditya.marathe.20@ucl.ac.uk

--------------------------------------------------------------------------------
"""

from __future__ import annotations

__all__ = ["DataCallbackBase"]

from typing import TYPE_CHECKING

from abc import ABC

from .transform import TransformBase

if TYPE_CHECKING:
    from .data_handler import DataHandler


class DataCallbackBase(ABC):
    def before_transform(
        self, dh: DataHandler, transform: TransformBase
    ) -> None:
        """\
        Callback executed before a transform is applied.

        Parameters
        ----------
        dh : DataHandler
            The `DataHandler` instance.
        
        transform : TransformBase
            The transform that is about to be applied.
        """
        pass

    def after_transform(
        self, dh: DataHandler, transform: TransformBase
    ) -> None:
        """\
        Callback executed after a transform is applied.

        Parameters
        ----------
        dh : DataHandler
            The `DataHandler` instance.
        
        transform : TransformBase
            The transform that has just been applied.
        """
        pass

    def __str__(self) -> str:
        return f"oscana.{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return str(self)
