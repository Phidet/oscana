"""\
oscana / data / plugins / pandas_v1.py
--------------------------------------------------------------------------------

Author - Aditya Marathe
Email  - aditya.marathe.20@ucl.ac.uk

--------------------------------------------------------------------------------
"""

from __future__ import annotations

__all__ = ["PandasIO"]

from typing import TYPE_CHECKING, Any, Callable, Literal

import logging
from pathlib import Path

import numpy.typing as npt
import uproot
import numpy as np
import pandas as pd
import h5py, json

from ...logger import _error
from ..io_base import (
    DataIOStrategy,
    LoaderFuncType,
    WriterFuncType,
    LoadedDataType,
)
from ..t_metadata import TransformMetadata
from ..f_metadata import FileMetadata
from ...utils import (
    OscanaError,
    get_func_lookup,
    _get_dir_from_env,
)

if TYPE_CHECKING:
    from ..data_handler import DataHandler


# =============================== [ Logging  ] =============================== #

_logger = logging.getLogger("Root")


# ============================== [ Constants  ] ============================== #

SAVE_FILE_FORMAT = "{timestamp}_{name}.{format}"

# =============================== [ Helpers  ] =============================== #


def _v1_naive_loader(
    variables: list[str], file: str
) -> LoadedDataType[pd.DataFrame]:
    """\
    A simple way to load variables from a ROOT file using Uproot.
    
    Parameters
    ----------
    variables : list[str]
        List of variables to load from the ROOT file.
    
    file : str
        The name of the ROOT file to load the variables from.
        
    Returns
    -------
    LoadedDataType[pd.DataFrame]
        A tuple containing:
        - A `DataFrame` with the loaded variables.
        - A list of `FileMetadata` objects with the metadata of the files.
        - A `TransformMetadata` object with the metadata of the transforms.
    """
    _logger.debug(f"Loading variables from '{file}' using the V1 Naive Loader.")

    file_dir = _get_dir_from_env(file=file)

    uproot_file = uproot.open(file_dir)

    _logger.info(f"Opened '{file}' using Uproot.")

    # This is a really crappy way to extract the metadata...
    metadata = FileMetadata.from_sntp(
        file_name=Path(file_dir).name, file=uproot_file
    )

    data_dict: dict[str, npt.NDArray] = {}

    for variable in variables:
        _logger.debug(f"Extracting variable '{variable}' from '{file}'...")

        # Note: Not great that we need to specify a base in this way.
        # TODO: Fix this.

        base = variable.split("/")[0]
        key = "/".join(variable.split("/")[1:])

        try:
            base_branch = uproot_file[base]
        except uproot.KeyInFileError:
            _error(
                OscanaError,
                f"Base '{base}' not found in '{file}'!",
                _logger,
            )

        try:
            data_dict[key] = base_branch[
                key
            ].arrays(  # pyright: ignore[reportAttributeAccessIssue]
                library="np"
            )[
                key.split("/")[-1]
            ]
        except uproot.KeyInFileError:
            _error(
                OscanaError,
                f"Variable '{key}' not found in '{file}'!",
                _logger,
            )

    uproot_file.close()  # pyright: ignore[reportAttributeAccessIssue]

    _logger.info(f"Extracted variables from '{file}'.")

    return pd.DataFrame(data_dict), [metadata], TransformMetadata()


def _v1_naive_loader_h5(
    variables: list[str], file: str | Path
) -> LoadedDataType[pd.DataFrame]:
    """\
    A simple way to load variables from an HDF5 file using h5py.
    
    Parameters
    ----------
    variables : list[str]
        List of variables to load from the HDF5 file.

    file : str | Path
        The name or path of the HDF5 file to load the variables from.

    Returns
    -------
    LoadedDataType[pd.DataFrame]
        A tuple containing:
        - A `DataFrame` with the loaded variables.
        - A list of `FileMetadata` objects with the metadata of the files.
        - A `TransformMetadata` object with the metadata of the transforms.
    """
    _logger.debug(
        f"Loading variables from '{file}' using the V1 Naive Loader (HDF5)."
    )

    variables_set: set[str] = {var.split("/")[-1] for var in variables}

    with h5py.File(file, "r") as h5_file:
        _logger.info(f"Opened '{file}' using h5py.")

        # (1) Extract the metadata.

        t_branch = h5_file["metadata/transforms"]

        if not isinstance(t_branch, h5py.Dataset):
            _error(
                OscanaError,
                f"The 'transforms' branch in '{file}' is not a dataset!",
                _logger,
            )

        t_branch_dict = json.loads(t_branch[()].decode("utf-8"))
        t_metadata = TransformMetadata.from_dict(meta_dict=t_branch_dict)

        f_branch = h5_file["metadata/files"]

        if not isinstance(f_branch, h5py.Dataset):
            _error(
                OscanaError,
                f"The 'files' branch in '{file}' is not a dataset!",
                _logger,
            )

        f_branch_dict = json.loads(f_branch[()].decode("utf-8"))
        f_metadata = [
            FileMetadata.from_dict(meta_dict=f) for f in f_branch_dict
        ]

        del t_branch, f_branch, f_branch_dict, t_branch_dict

        # (2) Extract the data to a `DataFrame`.

        data_dict: dict[str, npt.NDArray] = {}

        data_branch = h5_file["data"]

        if not isinstance(data_branch, h5py.Group):
            _error(
                OscanaError,
                f"The 'data' branch in '{file}' is not a group!",
                _logger,
            )

        for column_name in data_branch.keys():
            column_name = str(column_name)

            # Note: We should always be loading in all the "ana." variables, at
            #       least for this naive loader. Ideally, we should have some
            #       method of specifying which "ana." variables to load to avoid
            #       hogging up memory with useless data.

            is_not_ana_variable = not column_name.startswith("ana.")

            if is_not_ana_variable and (column_name not in variables_set):
                continue

            _logger.debug(
                f"Extracting variable '{column_name}' from '{file}'..."
            )

            data_dict[column_name] = _read_h5_column(
                data_branch[column_name]
            )

        # The writer only creates this group when there is a non-empty cuts
        # table, so its absence is normal and must not be an error.
        cuts_branch = h5_file.get("cuts")

        if (cuts_branch is not None) and not isinstance(
            cuts_branch, h5py.Group
        ):
            _error(
                OscanaError,
                f"The 'cuts' branch in '{file}' is not a group!",
                _logger,
            )

        for column_name in cuts_branch.keys() if cuts_branch else ():
            column_name = str(column_name)

            _logger.debug(
                f"Extracting cut variable '{column_name}' from '{file}'..."
            )

            data_dict[column_name] = _read_h5_column(
                cuts_branch[column_name]
            )


        return pd.DataFrame(data=data_dict), f_metadata, t_metadata


def _is_jagged_array(data: pd.Series) -> bool:
    """\
    Check if the data is a jagged array (i.e., a list of lists).

    Parameters
    ----------
    data : pd.Series
        The data to check.

    Returns
    -------
    bool
        True if the data is a jagged array, False otherwise.
    """
    # Note: This is a really crappy way to check for jagged arrays!
    # TODO: Make this less crappy.
    return isinstance(data.iloc[0], np.ndarray) and data.dtype == "object"


def _loader_function(
    helper_func: Callable[
        [list[str], str | Path], LoadedDataType[pd.DataFrame]
    ],
    variables: list[str],
    files: list[str | Path],
) -> LoadedDataType[pd.DataFrame]:
    """\
    [ Internal ] Generic loader function to handle loading data from files.

    Parameters
    ----------
    helper_func : Callable
        The helper function to use for loading the data.

    variables : list[str]
        List of variables to load from the files.

    files : list[str | Path]
        List of files to load the data from.
    
    Returns
    -------
    LoadedDataType[pd.DataFrame]
        A tuple containing:
        - A `DataFrame` with the loaded variables.
        - A list of `FileMetadata` objects with the metadata of the files.
        - A `TransformMetadata` object with the metadata of the transforms.
    """
    exceptions_ = []
    data_list: list[pd.DataFrame] = []
    f_metadata_list: list[FileMetadata] = []
    t_metadata_comp: TransformMetadata | None = None

    for file in files:
        try:
            data, f_metadata, t_metadata = helper_func(variables, file)

            if len(f_metadata_list) and all(
                fm != f_metadata_list[-1] for fm in f_metadata
            ):
                _error(
                    OscanaError,
                    "All files must have the same metadata! The metadata for "
                    f"{file} is different from the previous files.",
                    _logger,
                )

            if len(f_metadata_list) and t_metadata_comp != t_metadata:
                _error(
                    OscanaError,
                    "All files must have the same transforms applied! The "
                    f"transforms for {file} are different from the previous "
                    "files.",
                    _logger,
                )

            t_metadata_comp = t_metadata_comp or t_metadata
            data_list.append(data)
            f_metadata_list.extend(f_metadata)

        except Exception as e:
            exceptions_.append(e)

    if len(exceptions_):
        for e in exceptions_:
            if e.__class__.__name__ == "OscanaError":
                continue

            _logger.error(
                f"An execption was supressed! {e.__class__.__name__} - {e!s}"
                + ("." if str(e)[-1] != "." or str(e)[-1] != "!" else "")
            )
        _error(
            OscanaError,
            "One or more files failed to load! (See the above exceptions.)",
            _logger,
        )

    assert (
        t_metadata_comp is not None
    ), "Unreachable: Transform metadata is `None`! "

    return (pd.concat(data_list), f_metadata_list, t_metadata_comp)


# =========================== [ Dynamic Helpers  ] =========================== #


def hlp_20250205_from_sntp(
    variables: list[str], files: list[str]
) -> LoadedDataType[pd.DataFrame]:
    """\
    [ Internal ]
    
    Name: Naïve Loader V1
    """
    return _loader_function(
        helper_func=_v1_naive_loader,  # pyright: ignore[reportArgumentType]
        variables=variables,
        files=files,  # pyright: ignore[reportArgumentType]
    )


def hlp_20250205_from_udst(
    variables: list[str], files: list[str | Path]
) -> LoadedDataType[pd.DataFrame]:
    """\
    [ Internal ]

    Not Implemented!
    """
    _error(
        NotImplementedError,
        "The uDST loader is not implemented yet!",
        _logger,
    )


def hlp_20250205_from_hdf5(
    variables: list[str], files: list[str | Path]
) -> LoadedDataType[pd.DataFrame]:
    """\
    [ Internal ]

    Name: HDF5 Loader V1
    """
    return _loader_function(
        helper_func=_v1_naive_loader_h5,  # pyright: ignore[reportArgumentType]
        variables=variables,
        files=files,  # pyright: ignore[reportArgumentType]
    )


def _write_h5_column(
    group: Any, name: str, column: pd.Series, compression: dict[str, Any]
) -> None:
    """\
    [ Internal ] Write one column into an HDF5 group.

    Jagged columns are stored as a sub-group of two ordinary datasets --
    `values` (all elements concatenated) and `offsets` (where each event's
    slice starts) -- rather than as one variable-length dataset.

    Parameters
    ----------
    group : Any
        The `h5py` group to write into.

    name : str
        The column name.

    column : pd.Series
        The column values.

    compression : dict[str, Any]
        Compression keyword arguments passed to `create_dataset`.
    """
    if not _is_jagged_array(data=column):
        group.create_dataset(
            name=name,
            dtype=column.dtype,
            data=column.to_numpy(),
            **compression,
        )
        return

    cells = [np.asarray(cell) for cell in column]

    # Cells may be 2-D (e.g. a per-event list of 4-momenta), so remember the
    # trailing shape and count offsets in scalars, not rows.
    inner_shape = cells[0].shape[1:] if len(cells) else ()

    offsets = np.zeros(len(cells) + 1, dtype=np.int64)
    np.cumsum([cell.size for cell in cells], out=offsets[1:])

    values = (
        np.concatenate([cell.reshape(-1) for cell in cells])
        if len(cells)
        else np.array([], dtype=column.dtype)
    )

    column_group = group.create_group(name)
    column_group.attrs["jagged"] = True
    column_group.attrs["inner_shape"] = np.asarray(inner_shape, dtype=np.int64)
    column_group.create_dataset(name="values", data=values, **compression)
    column_group.create_dataset(name="offsets", data=offsets, **compression)


def _read_h5_column(node: Any) -> npt.NDArray:
    """\
    [ Internal ] Read one column written by `_write_h5_column`.

    Parameters
    ----------
    node : Any
        The `h5py` dataset (flat column) or group (jagged column).

    Returns
    -------
    NDArray
        The column values, jagged columns as an object array of per-event
        arrays. Those are views into one contiguous block rather than
        separate allocations.
    """
    if not isinstance(node, h5py.Group):
        return node[:]

    values = node["values"][:]
    offsets = node["offsets"][:]
    inner_shape = tuple(int(dim) for dim in node.attrs.get("inner_shape", ()))

    out = np.empty(len(offsets) - 1, dtype=object)
    for i in range(len(offsets) - 1):
        segment = values[offsets[i] : offsets[i + 1]]
        out[i] = (
            segment.reshape((-1,) + inner_shape) if inner_shape else segment
        )

    return out


def hlp_20250205_to_hdf5(
    data: pd.DataFrame,
    cuts: pd.DataFrame | None,
    file_metadata: list[FileMetadata],
    transform_metadata: TransformMetadata,
    file_path: str | Path,
    compression: Literal["gzip", "lzf"] | None,
) -> None:
    """\
    [ Internal ]

    Name: HDF5 Writer V1
    """
    # (1) Check the file path.
    file_path = Path(file_path)

    if not (file_path.is_file and (file_path.suffix == ".h5")):
        _error(
            OscanaError,
            f"File '{file_path}' is not an HDF5 file! "
            + "Please provide a file with the '.h5' extension.",
            _logger,
        )

    file_path.parent.mkdir(parents=True, exist_ok=True)

    # (2) Compression.
    compression_kwargs: dict[str, Any] = {}

    if compression is not None:
        compression_kwargs = {"compression": compression}

    with h5py.File(file_path, "w") as my_file:
        data_branch = my_file.create_group(name="data")

        for column_name in data.columns:
            _write_h5_column(
                group=data_branch,
                name=str(column_name),
                column=data[column_name],
                compression=compression_kwargs,
            )

        if (cuts is not None) and (not cuts.empty):
            cuts_branch = my_file.create_group(name="cuts")

            for column_name in cuts.columns:
                _write_h5_column(
                    group=cuts_branch,
                    name=str(column_name),
                    column=cuts[column_name],
                    compression=compression_kwargs,
                )

        metadata_branch = my_file.create_group(name="metadata")

        metadata_branch.create_dataset(
            name="transforms",
            dtype=h5py.string_dtype(encoding="utf-8"),
            data=json.dumps(transform_metadata.to_dict()).encode("utf-8"),
        )

        metadata_branch.create_dataset(
            name="files",
            dtype=h5py.string_dtype(encoding="utf-8"),
            data=json.dumps([fm.to_dict() for fm in file_metadata]).encode(
                "utf-8"
            ),
        )



# ============================= [ IO Strategy  ] ============================= #

hlp_lookup = get_func_lookup(globals_=globals(), prefix="hlp_")


class PandasIO(DataIOStrategy[pd.DataFrame]):
    _sntp_loader: LoaderFuncType[pd.DataFrame] = hlp_lookup("from_sntp")
    _udst_loader: LoaderFuncType[pd.DataFrame] = hlp_lookup("from_udst")
    _hdf5_loader: LoaderFuncType[pd.DataFrame] = hlp_lookup("from_hdf5")

    _hdf5_writer: WriterFuncType[pd.DataFrame] = hlp_lookup("to_hdf5")

    def __init__(self, parent: DataHandler[pd.DataFrame]) -> None:
        """\
        Pandas IO Strategy.

        Parameters
        ----------
        parent : DataHandler[pd.DataFrame]
            Parent data handler.
        """
        super().__init__(parent=parent)

    def _init_data_table(self) -> pd.DataFrame:
        """\
        Initialize data table.

        Returns
        -------
        DataFrameType
            Data table.
        """
        return pd.DataFrame()

    def _init_cuts_table(self) -> pd.DataFrame:
        """\
        Initialize cuts table.

        Returns
        -------
        DataFrameType
            Cuts table.
        """
        return pd.DataFrame()

    def _from_sntp(self, files: list[str]) -> None:
        data, f_metadata, t_metadata = PandasIO._sntp_loader(
            variables=self._parent._variables,
            files=files,  # pyright: ignore[reportArgumentType]
        )

        if (
            len(self._parent._f_metadata)
            and self._parent._t_metadata != t_metadata
        ):
            _error(
                OscanaError,
                "All files must have the same transforms applied! The "
                "transforms for the SNTP file(s) are different from the "
                "previous files.",
                _logger,
            )

        if not len(self._parent._f_metadata):
            self._parent._t_metadata = t_metadata

        self._parent._data_table = pd.concat([self._parent._data_table, data])
        self._parent._f_metadata.extend(f_metadata)

    def _from_udst(self, files: list[str]) -> None:
        data, f_metadata, t_metadata = PandasIO._udst_loader(
            variables=self._parent._variables,
            files=files,  # pyright: ignore[reportArgumentType]
        )

        if (
            len(self._parent._f_metadata)
            and self._parent._t_metadata != t_metadata
        ):
            _error(
                OscanaError,
                "All files must have the same transforms applied! The "
                "transforms for the uDST file(s) are different from the "
                "previous files.",
                _logger,
            )

        if not len(self._parent._f_metadata):
            self._parent._t_metadata = t_metadata

        self._parent._data_table = pd.concat([self._parent._data_table, data])
        self._parent._f_metadata.extend(f_metadata)

    def _from_hdf5(self, files: list[str | Path]) -> None:
        data, f_metadata, t_metadata = PandasIO._hdf5_loader(
            variables=self._parent._variables,
            files=files,
        )

        if (
            len(self._parent._f_metadata)
            and self._parent._t_metadata != t_metadata
        ):
            _error(
                OscanaError,
                "All files must have the same transforms applied! The "
                "transforms for the H5 file(s) are different from the "
                "previous files.",
                _logger,
            )

        if not len(self._parent._f_metadata):
            self._parent._t_metadata = t_metadata

        self._parent._data_table = pd.concat([self._parent._data_table, data])
        self._parent._f_metadata.extend(f_metadata)


    def to_hdf5(
        self,
        file: str | Path,
        compression: Literal["gzip", "lzf"] | None = None,
    ) -> None:
        """\
        Write the data table to an HDF5 file.

        Parameters
        ----------
        file : str | Path
            The name of the HDF5 file to write to.

        compression : Literal["gzip", "lzf"] | None
            The compression algorithm to use. If `None`, no compression is used.
            Default is `None`.

        Notes
        -----
        Compression algorithms supported by `h5py` include: "gzip", "lzf", and 
        "szip". However, "szip" is not supported due to licensing.

        """
        return PandasIO._hdf5_writer(
            data=self._parent._data_table,
            cuts=(
                self._parent._cuts_table
                if self._parent.has_cuts_table
                else None
            ),
            file_metadata=self._parent._f_metadata,
            transform_metadata=self._parent._t_metadata,
            file_path=file,
            compression=compression,
        )


    def get_data_length(self) -> int:
        """\
        Get the length of the data table.

        Returns
        -------
        int
            Length of the data table.
        """
        return len(self._parent._data_table)

    def get_cuts_length(self) -> int:
        """\
        Get the length of the cuts table.

        Returns
        -------
        int
            Length of the cuts table.
        """
        return (
            len(self._parent._cuts_table) if self._parent.has_cuts_table else 0
        )

    def get_n_variables(self) -> int:
        """\
        Get the number of variables in the data and cuts table.

        Returns
        -------
        int
            Number of variables in the data and cuts table.
        """
        return len(self._parent.data.columns) + (
            len(self._parent.cuts.columns) if self._parent.has_cuts_table else 0
        )
