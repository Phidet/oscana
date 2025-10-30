"""\
oscana / images.py

--------------------------------------------------------------------------------

Author - Aditya Marathe
Email  - aditya.marathe.20@ucl.ac.uk

--------------------------------------------------------------------------------

This module contains functions to extract the event images from the SNTP files.
"""

from __future__ import annotations

__all__ = [
    "image_to_sparse",
    "get_image_profiles",
    "calculate_strip_com",
    "create_fd_full_image",
    "create_fd_split_image",
    "create_fd_crop_image",
]

import logging

import numpy as np
import numpy.typing as npt
import scipy.sparse as sps

from .logger import _error
from .utils import minos_numbers
from .constants import IMAGE_DTYPE, EPlaneView

# ================================ [ Logger ] ================================ #

_logger = logging.getLogger("Root")

# =========================== [ Helper Functions ] =========================== #


def image_to_sparse(image: npt.NDArray[IMAGE_DTYPE]) -> sps.csr_matrix:
    """\
    Convert a dense image to a sparse matrix.

    Parameters
    ----------
    image : npt.NDArray[IMAGE_DTYPE]
        The dense image to convert.

    Returns
    -------
    sps.csr_matrix
        The sparse matrix representation of the image.

    Notes
    -----
    More specifically, this function converts the input array into a Compressed
    Sparse Row (CSR) matrix format.
    """
    return sps.csr_matrix(image, shape=image.shape, dtype=IMAGE_DTYPE)


def _get_image_profile_plane(
    target_variable: npt.NDArray,
    mean_pe: npt.NDArray,
) -> tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
    """\
    [ Internal ] Get the image profile for a specific plane.

    Parameters
    ----------
    target_variable : npt.NDArray
        The target variable for a selected plane to bin. Either the strips or
        the planes.

    mean_pe : npt.NDArray
        The mean pulse height for the selected plane.

    Returns
    -------
    tuple[npt.NDArray, npt.NDArray, npt.NDArray]
        The bin centres, binned mean pulse height, and binned digit counts along
        the target variable.
    """
    bin_centres = np.arange(target_variable.min(), target_variable.max() + 1)

    binned_mean_pe = np.zeros_like(bin_centres, dtype=mean_pe.dtype)
    binned_digits = np.zeros_like(bin_centres, dtype=int)

    for i, bin_value in enumerate(bin_centres):
        data_in_bin = mean_pe[target_variable == bin_value]

        binned_mean_pe[i] = np.sum(data_in_bin)
        binned_digits[i] = len(data_in_bin)

    return bin_centres, binned_mean_pe, binned_digits


def get_image_profiles(
    stp_planeview: npt.NDArray,
    target_variable: npt.NDArray,
    mean_pe: npt.NDArray,
) -> dict[str, npt.NDArray]:
    """\
    Bins the digitial hits along with other variables.

    Parameters
    ----------
    stp_planeview : npt.NDArray
        The plane view of strips and planes.

    target_variable : npt.NDArray
        The target variable to bin. Either the strips or the planes.

    mean_pe : npt.NDArray
        The mean pulse height for the selected plane.

    Returns
    -------
    dict[str, npt.NDArray]
        A dictionary containing the binned variables.
    """
    output_dict = {}

    uz_selector = stp_planeview == EPlaneView.U.value
    vz_selector = stp_planeview == EPlaneView.V.value

    bin_centres_uz, binned_digits, binned_mean_pe = _get_image_profile_plane(
        target_variable=target_variable[uz_selector],
        mean_pe=mean_pe[uz_selector],
    )
    output_dict["bin_centres_uz"] = bin_centres_uz
    output_dict["digits_uz"] = binned_digits
    output_dict["mean_pe_uz"] = binned_mean_pe

    bin_centres_vz, binned_digits, binned_mean_pe = _get_image_profile_plane(
        target_variable=target_variable[vz_selector],
        mean_pe=mean_pe[vz_selector],
    )
    output_dict["bin_centres_vz"] = bin_centres_vz
    output_dict["digits_vz"] = binned_digits
    output_dict["mean_pe_vz"] = binned_mean_pe

    return output_dict


def calculate_strip_com(
    stp_planeview: npt.NDArray,
    stp_strip: npt.NDArray,
    stp_pe_east: npt.NDArray,
    stp_pe_west: npt.NDArray,
) -> tuple[int, int]:
    """\
    Calculate the center of mass of the strip profiles in both UZ and VZ planes.

    Parameters
    ----------
    stp_planeview : npt.NDArray
        The `stp.planeview` variable from the SNTP_BR_STD branch of SNTP files.

    stp_strip : npt.NDArray
        The `stp.strip` variable from the SNTP_BR_STD branch of SNTP files.

    stp_pe_east : npt.NDArray
        The `stp.ph0.pe` variable from the SNTP_BR_STD branch of SNTP files.

    stp_pe_west : npt.NDArray
        The `stp.ph1.pe` variable from the SNTP_BR_STD branch of SNTP files.

    Returns
    -------
    tuple[int, int]
        The center of mass of the strip profiles in the UZ and VZ planes
        respectively.    
    """
    # (1) Calculate the mean pulse height.
    mean_ph = (stp_pe_east + stp_pe_west) / 2

    # (2) Get the image profiles for the strip.
    image_profiles = get_image_profiles(
        stp_planeview=stp_planeview,
        target_variable=stp_strip,
        mean_pe=mean_ph,
    )
    image_profiles["mean_pe_uz"] = image_profiles["mean_pe_uz"] / np.sum(
        image_profiles["mean_pe_uz"]
    )
    image_profiles["mean_pe_vz"] = image_profiles["mean_pe_vz"] / np.sum(
        image_profiles["mean_pe_vz"]
    )

    # (3) Calculate the strip center of mass.
    bin_weights = image_profiles["mean_pe_uz"] * image_profiles["digits_uz"]
    strip_com_uz = np.ceil(
        np.sum(bin_weights * image_profiles["bin_centres_uz"])
        / np.sum(bin_weights)
    )

    bin_weights = image_profiles["mean_pe_vz"] * image_profiles["digits_vz"]
    strip_com_vz = np.ceil(
        np.sum(bin_weights * image_profiles["bin_centres_vz"])
        / np.sum(bin_weights)
    )

    return int(strip_com_uz), int(strip_com_vz)


# Note: Old code will be yeeted out soon...
#
# def _create_cropped_image(
#     plane: EPlaneView,
#     stp_planeview: npt.NDArray,
#     stp_strip: npt.NDArray,
#     stp_plane: npt.NDArray,
#     cropped_width: int,
#     cropped_height: int,
#     strip_com: int,
#     fill: list[npt.NDArray],
# ) -> npt.NDArray:
#     """\
#     [ Internal ] Create a cropped image from the full FD image for a particular
#     plane.
#
#     Parameters
#     ----------
#     plane : EPlaneView
#         The plane view to extract the images for (either U-Z or V-Z).
#
#     stp_planeview : npt.NDArray
#         The `stp.planeview` variable from the SNTP_BR_STD branch of SNTP files.
#
#     stp_strip : npt.NDArray
#         The `stp.strip` variable from the SNTP_BR_STD branch of SNTP files.
#
#     stp_plane : npt.NDArray
#         The `stp.plane` variable from the SNTP_BR_STD branch of SNTP files.
#
#     cropped_width: int
#         The width of the cropped image.
#
#     cropped_height: int
#         The height of the cropped image.
#
#     fill : list[npt.NDArray] | None
#         Array(s) to fill the image. If `None`, the image will be filled with
#         "1"s.
#
#     Returns
#     -------
#     npt.NDArray
#         The cropped event image for the selected plane.
#     """
#     # (1) Get data for the selected plane.
#
#     try:
#         plane_selector = stp_planeview == plane.value
#     except ValueError:
#         _error(
#             ValueError,
#             "The `stp_planeview` array should be a 1D array!",
#             _logger,
#         )
#
#     # Note: 'stp.plane' is 1-indexed, while 'stp.strip' is 0-indexed!
#
#     this_stp_strip: npt.NDArray = stp_strip[plane_selector]
#     this_stp_plane: npt.NDArray = stp_plane[plane_selector]
#
#     # (2) Translate the CoM and calculate the offset from the origin.
#
#     # Note: It is very important that these variables are recast to Python
#     #       `int` to avoid overflows!
#
#     event_height = int(this_stp_strip.max()) - int(this_stp_strip.min())
#
#     strip_com = int(strip_com) - int(this_stp_strip.min())
#     strip_com = int(np.floor(cropped_height / 2 - strip_com))
#
#     offset = min(0, cropped_height - 1 - (event_height + strip_com))
#     strip_com = max(0, strip_com + offset)
#
#     # (3) Translate the track digits.
#
#     this_stp_plane = this_stp_plane - this_stp_plane.min()
#     this_stp_strip = this_stp_strip - this_stp_strip.min() + strip_com
#
#     # (4) Fill the image.
#
#     image = np.zeros(shape=(cropped_height, cropped_width, len(fill)))
#
#     for i, fill_value in enumerate(fill):
#         # (4.1) Run checks on the fill value.
#
#         this_fill = fill_value[plane_selector]
#
#         if this_fill.shape != this_stp_strip.shape:
#             _error(
#                 ValueError,
#                 f"The `fill` array #{i + 1} should have the same shape as "
#                 "'stp.strip', 'stp.plane' and 'stp.planeview'!",
#                 _logger,
#             )
#
#         # (4.2) Fill the image.
#
#         image[this_stp_strip, this_stp_plane, i] = this_fill
#
#     return image


def _crop_image(
    image: npt.NDArray,
    x: int,
    y: int,
    width: int,
    height: int,
) -> npt.NDArray:
    """\
    [ Internal ] Crop an image to the given dimensions.
    
    Parameters
    ----------
    image : npt.NDArray
        The image to crop.
        
    x : int
        The x-coordinate of the top-left corner of the crop.
        
    y : int
        The y-coordinate of the top-left corner of the crop.
        
    width : int
        The width of the crop.
        
    height : int
        The height of the crop.
    
    Returns
    -------
    npt.NDArray
        The cropped image.
    """
    image_height, image_width = image.shape[:2]
    image_channels_tuple = image.shape[2:]

    cropped_image = np.zeros(
        shape=(height, width, *image_channels_tuple),
        dtype=image.dtype,
    )

    x_im_beg = max(0, x)
    x_im_end = min(image_width, x + width)

    y_im_beg = max(0, y)
    y_im_end = min(image_height, y + height)

    x_cp_beg = x_im_beg - x
    x_cp_end = x_cp_beg + (x_im_end - x_im_beg)

    y_cp_beg = y_im_beg - y
    y_cp_end = y_cp_beg + (y_im_end - y_im_beg)

    cropped_image[y_cp_beg:y_cp_end, x_cp_beg:x_cp_end, ...] = image[
        y_im_beg:y_im_end, x_im_beg:x_im_end, ...
    ]

    return cropped_image


# ============================== [ Functions  ] ============================== #


def create_fd_full_image(
    plane: EPlaneView,
    stp_planeview: npt.NDArray,
    stp_strip: npt.NDArray,
    stp_plane: npt.NDArray,
    fill: list[npt.NDArray] | None = None,
) -> npt.NDArray[IMAGE_DTYPE]:
    """\
    Get the FD event image for the given plane.

    Parameters
    ----------
    plane : EPlaneView
        The plane view to extract the images for (either U-Z or V-Z).

    stp_planeview : npt.NDArray
        The `stp.planeview` variable from the SNTP_BR_STD branch of SNTP files.

    stp_strip : npt.NDArray
        The `stp.strip` variable from the SNTP_BR_STD branch of SNTP files.

    stp_plane : npt.NDArray
        The `stp.plane` variable from the SNTP_BR_STD branch of SNTP files.

    fill : list[npt.NDArray] | None
        Array(s) to fill the image. Defaults to `None`. If `None`, the image
        will be filled with "1"s.

    Returns
    -------
    npt.NDArray[IMAGE_DTYPE]
        The FD event image for the given plane.
    """
    # (1) Run checks on the user input.

    if not (stp_planeview.shape == stp_strip.shape == stp_plane.shape):
        _error(
            ValueError,
            "The `stp.planeview`, `stp.strip` and `stp.plane` arrays should "
            "have the same shape!",
            _logger,
        )

    if fill is None:
        fill = [np.ones(shape=stp_planeview.shape, dtype=IMAGE_DTYPE)]

    fd_s_n_planes = minos_numbers["FD"]["South"]["NPlanes"]
    fd_n_n_planes = minos_numbers["FD"]["North"]["NPlanes"]
    fd_n_planes = fd_s_n_planes + fd_n_n_planes
    fd_n_strips = minos_numbers["FD"]["NStripsPerPlane"]

    # (2) Get data for the selected plane.

    try:
        plane_selector = stp_planeview == plane.value
    except ValueError:
        _error(
            ValueError,
            "The `stp_planeview` array should be a 1D array!",
            _logger,
        )

    # Note: 'stp.plane' is 1-indexed, while 'stp.strip' is 0-indexed!

    stp_strip = stp_strip[plane_selector]
    stp_plane = stp_plane[plane_selector] - np.array(1, dtype=stp_plane.dtype)

    # (3) Fill the image.

    # Note: Shape of the image should be (HEIGHT, WIDTH, CHANNELS).

    image = np.zeros(
        shape=(fd_n_strips, fd_n_planes, len(fill)), dtype=IMAGE_DTYPE
    )

    for i, fill_value in enumerate(fill):
        # (3.1) Run checks on the fill value.

        fill_value = fill_value[plane_selector]

        if fill_value.shape != stp_strip.shape:
            _error(
                ValueError,
                f"The `fill` array #{i + 1} should have the same shape as "
                "'stp.strip', 'stp.plane' and 'stp.planeview'!",
                _logger,
            )

        # (3.2) Fill the image.

        image[stp_strip, stp_plane, i] = fill_value

    return image


def create_fd_split_image(
    plane: EPlaneView,
    stp_planeview: npt.NDArray,
    stp_strip: npt.NDArray,
    stp_plane: npt.NDArray,
    fill: list[npt.NDArray] | None = None,
) -> tuple[npt.NDArray[IMAGE_DTYPE], npt.NDArray[IMAGE_DTYPE]]:
    """\
    Get the FD event image, split into the South and North submodules, for the 
    given plane.

    Parameters
    ----------
    plane : EPlaneView
        The plane view to extract the images for (either U-Z or V-Z).

    stp_planeview : npt.NDArray
        The `stp.planeview` variable from the SNTP_BR_STD branch of SNTP files.

    stp_strip : npt.NDArray
        The `stp.strip` variable from the SNTP_BR_STD branch of SNTP files.

    stp_plane : npt.NDArray
        The `stp.plane` variable from the SNTP_BR_STD branch of SNTP files.

    fill : list[npt.NDArray] | None
        Array(s) to fill the image. Defaults to `None`. If `None`, the image
        will be filled with "1"s.

    Returns
    -------
    tuple[npt.NDArray[IMAGE_DTYPE], npt.NDArray[IMAGE_DTYPE]]
        The FD event image for the given plane, split into the South and North
        submodules.
    """
    # (1) Get the full image.

    full_image = create_fd_full_image(
        plane=plane,
        stp_planeview=stp_planeview,
        stp_strip=stp_strip,
        stp_plane=stp_plane,
        fill=fill,
    )

    # (2) Split the image into the South and North submodules.

    fd_s_n_planes = minos_numbers["FD"]["South"]["NPlanes"]

    return full_image[:, :fd_s_n_planes, :], full_image[:, fd_s_n_planes:, :]


# def create_fd_crop_image(
#     stp_planeview: npt.NDArray,
#     stp_strip: npt.NDArray,
#     stp_plane: npt.NDArray,
#     stp_pe_east: npt.NDArray,
#     stp_pe_west: npt.NDArray,
#     cropped_width: int,
#     cropped_height: int,
#     fill: list[npt.NDArray] | None = None,
# ) -> tuple[npt.NDArray, npt.NDArray]:
#     """\
#     Create a cropped image from the full FD image.
#
#     Parameters
#     ----------
#     stp_planeview : npt.NDArray
#         The `stp.planeview` variable from the SNTP_BR_STD branch of SNTP files.
#
#     stp_strip : npt.NDArray
#         The `stp.strip` variable from the SNTP_BR_STD branch of SNTP files.
#
#     stp_plane : npt.NDArray
#         The `stp.plane` variable from the SNTP_BR_STD branch of SNTP files.
#
#     stp_pe_east : npt.NDArray
#         The pulse height (photoelectrons) for the east side.
#
#     stp_pe_west : npt.NDArray
#         The pulse height (photoelectrons) for the west side.
#
#     cropped_width: int
#         The width of the cropped image.
#
#     cropped_height: int
#         The height of the cropped image.
#
#     fill : list[npt.NDArray] | None
#         Array(s) to fill the image. Defaults to `None`. If `None`, the image
#         will be filled with "1"s.
#
#     Returns
#     -------
#     tuple[npt.NDArray[IMAGE_DTYPE], npt.NDArray[IMAGE_DTYPE]]
#         The cropped FD event images in the UZ and VZ planes respectively.
#     """
#     # (1) Run checks on the user input.
#
#     if not (stp_planeview.shape == stp_strip.shape == stp_plane.shape):
#         _error(
#             ValueError,
#             "The `stp.planeview`, `stp.strip` and `stp.plane` arrays should "
#             "have the same shape!",
#             _logger,
#         )
#
#     if fill is None:
#         fill = [np.ones(shape=stp_planeview.shape, dtype=IMAGE_DTYPE)]
#
#     stp_strip = stp_strip.copy()
#     stp_plane = stp_plane.copy() - np.array(1, dtype=stp_plane.dtype)
#
#     # (2) Calculate the center of mass for the strips.
#
#     strip_com_uz, strip_com_vz = calculate_strip_com(
#         stp_planeview=stp_planeview,
#         stp_strip=stp_strip,
#         stp_pe_east=stp_pe_east,
#         stp_pe_west=stp_pe_west,
#     )
#
#     # (3) Get the UZ and VZ images.
#
#     image_uz = _create_cropped_image(
#         plane=EPlaneView.U,
#         stp_planeview=stp_planeview,
#         stp_strip=stp_strip,
#         stp_plane=stp_plane,
#         cropped_width=cropped_width,
#         cropped_height=cropped_height,
#         strip_com=strip_com_uz,
#         fill=fill,
#     )
#
#     image_vz = _create_cropped_image(
#         plane=EPlaneView.V,
#         stp_planeview=stp_planeview,
#         stp_strip=stp_strip,
#         stp_plane=stp_plane,
#         cropped_width=cropped_width,
#         cropped_height=cropped_height,
#         strip_com=strip_com_vz,
#         fill=fill,
#     )
#
#     return image_uz, image_vz


def create_fd_crop_image(
    plane: EPlaneView,
    stp_planeview: npt.NDArray,
    stp_strip: npt.NDArray,
    stp_plane: npt.NDArray,
    stp_pe_east: npt.NDArray,
    stp_pe_west: npt.NDArray,
    cropped_width: int,
    cropped_height: int,
    fill: list[npt.NDArray] | None = None,
) -> npt.NDArray[IMAGE_DTYPE]:
    """\
    Create a cropped image from the full FD image for a particular plane.

    Parameters
    ----------
    plane : EPlaneView
        The plane view to extract the images for (either U-Z or V-Z).

    stp_planeview : npt.NDArray
        The `stp.planeview` variable from the SNTP_BR_STD branch of SNTP files.

    stp_strip : npt.NDArray
        The `stp.strip` variable from the SNTP_BR_STD branch of SNTP files.

    stp_plane : npt.NDArray
        The `stp.plane` variable from the SNTP_BR_STD branch of SNTP files.

    stp_pe_east : npt.NDArray
        The pulse height (photoelectrons) for the east side.

    stp_pe_west : npt.NDArray
        The pulse height (photoelectrons) for the west side.

    cropped_width: int
        The width of the cropped image.

    cropped_height: int
        The height of the cropped image.

    fill : list[npt.NDArray] | None
        Array(s) to fill the image. Defaults to `None`. If `None`, the image
        will be filled with "1"s.

    Returns
    -------
    npt.NDArray[IMAGE_DTYPE]
        The cropped FD event image for the selected plane.        
    """

    # (1) Get the full image.
    image = create_fd_full_image(
        plane=plane,
        stp_planeview=stp_planeview,
        stp_strip=stp_strip,
        stp_plane=stp_plane,
        fill=fill,
    )

    # (2) Calculate the center of mass for the strips.
    strip_com_uz, strip_com_vz = calculate_strip_com(
        stp_planeview=stp_planeview,
        stp_strip=stp_strip,
        stp_pe_east=stp_pe_east,
        stp_pe_west=stp_pe_west,
    )

    if plane == EPlaneView.U:
        strip_com = int(strip_com_uz)
    elif plane == EPlaneView.V:
        strip_com = int(strip_com_vz)
    else:
        _error(
            ValueError,
            "Unreachable. The `plane` parameter should be either `EPlaneView.U`"
            " or `EPlaneView.V`!",
            _logger,
        )

    strip_com = strip_com - np.min(stp_strip).astype(int)
    strip_com = cropped_height // 2 - strip_com

    # (3) Create the cropped image.
    return _crop_image(
        image=image,
        x=np.min(stp_plane).astype(int),
        y=np.min(stp_strip).astype(int) - strip_com,
        width=cropped_width,
        height=cropped_height,
    )
