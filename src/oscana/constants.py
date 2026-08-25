"""\
oscana / constants.py

--------------------------------------------------------------------------------

Author - Aditya Marathe
Email  - aditya.marathe.20@ucl.ac.uk

--------------------------------------------------------------------------------

This module contains all the constants used in the package.
"""

from __future__ import annotations

__all__ = [
    # Package Constants
    "RESOURCES_PATH",
    # Data Types
    "IMAGE_DTYPE",
    "NUM_DTYPE",
    # SNTP Branches
    "SNTP_BR_STD",
    "SNTP_BR_BDL",
    "SNTP_BR_FIT",
    # SNTP Variable Collections
    "HEADER_VARIABLES",
    "IMAGE_BASIC_VARIABLES",
    "IMAGE_PE_VARIABLES",
    "IMAGE_SIGCOR_VARIABLES",
    "IMAGE_TIME_VARIABLES",
    "IMAGE_ALL_VARIABLES",
    "EVENT_VERTEX_VARIABLES",
    "MC_4MOMENTUM_VARIABLES",
    "MC_INTERACTION_VARIABLES",
    "MC_TRUTH_EVENT_VARIABLES",
    "MC_PARTICLE_VARIABLES",
    # Enums
    "EIAction",
    "EIResonance",
    "EIdHEP",
    "EInteraction",
    "EPlaneView",
]

from typing import Final, Literal
from pathlib import Path
import importlib.resources as resources
from enum import Enum

import numpy as np

# =========================== [ Package Constants ] ========================== #


# Note: A better way to do this would be using `importlib.resources.files` but
#       I am currenly using Python 3.8 which does not seem to have this feature.
#       The other option is to use `pkg_resources` but it is deprecated! So, for
#       now, I am using `importlib.resources.path` and going back two
#       directories to get the resources folder.


with resources.path("oscana", "") as _path:
    RESOURCES_PATH = Path(_path).parent.parent / "res"


# ============================== [ Data Types ] ============================== #

IMAGE_DTYPE: Final = np.float32
NUM_DTYPE: Final = np.float32

# ============================ [ SNTP Branches  ] ============================ #

SNTP_BR_STD: Final[Literal["NtpSt"]] = "NtpSt"
SNTP_BR_BDL: Final[Literal["NtpBDLite"]] = "NtpBDLite"
SNTP_BR_FIT: Final[Literal["NtpFitSA"]] = "NtpFitSA"

# ============================ [ SNTP Variables ] ============================ #

SNTP_VR_DETECTOR: Final[str] = (
    "NtpStRecord/RecRecordImp<RecCandHeader>/fHeader.RecPhysicsHeader/"
    "fHeader.RecDataHeader/fHeader.RecHeader/fHeader.fVldContext.fDetector"
)
SNTP_VR_SIM: Final[str] = (
    "NtpStRecord/RecRecordImp<RecCandHeader>/fHeader.RecPhysicsHeader"
    "/fHeader.RecDataHeader/fHeader.RecHeader/fHeader.fVldContext.fSimFlag"
)
SNTP_VR_RUN: Final[str] = (
    "NtpStRecord/RecRecordImp<RecCandHeader>/fHeader.RecPhysicsHeader"
    "/fHeader.RecDataHeader/fHeader.fRun"
)
SNTP_VR_EVT_UTC: Final[str] = (
    "NtpStRecord/RecRecordImp<RecCandHeader>/fHeader.RecPhysicsHeader/"
    "fHeader.RecDataHeader/fHeader.RecHeader/"
    "fHeader.fVldContext.fTimeStamp.fSec"
)

# ====================== [ SNTP Variable Collections  ] ====================== #

# See README.md (this directory) for what each variable means, which are
# left out and why, and which `mc.*` fields duplicate the particle table.


class VariableCollection(list):
    """\
    VariableCollection
    ------------------

    A collection of ROOT SNTP variable names under a common ROOT branch.

    Attributes
    ----------
    branch_name : str
        The name of the ROOT branch.

    uproot : list[str]
        The list of variable names prefixed with the ROOT branch name.
    """

    __slots__ = ["_root"]

    def __init__(self, variables: list[str], root: str | None = None) -> None:
        """\
        Initialises a new `VariableCollection`.

        Parameters
        ----------
        variables : list[str]
            The list of variable names.

        root : str | None
            The ROOT branch name for the collection. If `None`, `.uproot` will
            return the variable names as-is.
        """
        super().__init__(variables)

        self._root = root  # The ROOT Branch name!

    @property
    def branch_name(self) -> str | None:
        """\
        The ROOT branch name for the collection, if it exists.
        """
        return self._root

    @property
    def uproot(self) -> list[str]:
        """\
        The list of variable names prefixed with the ROOT branch name.
        """
        if self._root is None:
            return list(self)

        return [f"{self._root}/{var}" for var in self]

    @property
    def list(self) -> list[str]:
        """\
        The variable names as a plain `list`, with no ROOT branch prefix.
        """
        return list(self)

    def __add__(self, other: object) -> "VariableCollection":
        if isinstance(other, VariableCollection):
            if self._root != other._root:
                raise ValueError(
                    "Cannot add `VariableCollections` with different ROOT "
                    f'branches! Found "{self._root}" and "{other._root}".'
                )

            return VariableCollection(
                variables=list(self) + list(other),
                root=self._root,
            )

        elif isinstance(other, list):
            # Check the branch name.
            branch_name = None
            stripped_list: list[str] = []

            for variable in other:
                variable_split = str(variable).split("/")

                if (branch_name is None) and (len(variable_split) > 1):
                    branch_name = variable_split[0]

                if (branch_name != variable_split[0]) and (
                    branch_name is not None
                ):
                    raise ValueError(
                        "Cannot add list of variables with different ROOT "
                        f'branches! Found "{branch_name}" and '
                        f'"{variable_split[0]}".'
                    )

                stripped_list.append(variable_split[-1])

            if (self._root != branch_name) and (branch_name is not None):
                raise ValueError(
                    "Cannot add `VariableCollection` with list of variables "
                    "with different ROOT branches! "
                    f'Found "{self._root}" and "{branch_name}".'
                )

            # Note: This means that we assign the new list of variables the
            #       branch name of this `VariableCollection`. This is just done
            #       to keep this implementation simple.

            return VariableCollection(
                variables=list(self) + stripped_list,
                root=self._root,
            )

        raise ValueError(
            "Operation `+` only supported between `VariableCollections`!"
        )

    def __radd__(self, other: object) -> "VariableCollection":
        return self.__add__(other=other)

    def __mul__(self, value: object) -> "VariableCollection":
        raise ValueError(
            "Operation `*` not supported for `VariableCollections`!"
        )

    def __rmul__(self, value: object) -> "VariableCollection":
        return self.__mul__(value=value)


HEADER_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "fRun",  # Run number
        "fSubRun",  # Subrun number
        "fSnarl",  # Snarl number
        "fEvent",  # Event number (constant -1 in files checked so far)
    ],
    root=SNTP_BR_STD,
)

IMAGE_BASIC_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "stp.planeview",  # Plane view (see README: derivable from plane)
        "stp.strip",  # Strip number
        "stp.plane",  # Plane number
    ],
    root=SNTP_BR_STD,
)

IMAGE_PE_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "stp.ph0.pe",  # Photoelectrons (East)
        "stp.ph1.pe",  # Photoelectrons (West)
    ],
    root=SNTP_BR_STD,
)

IMAGE_SIGCOR_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "stp.ph0.sigcor",  # Normalised strip response (East)
        "stp.ph1.sigcor",  # Normalised strip response (West)
    ],
    root=SNTP_BR_STD,
)

IMAGE_TIME_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "stp.time0",  # Charge weighted mean time [s] (East)
        "stp.time1",  # Charge weighted mean time [s] (West)
    ],
    root=SNTP_BR_STD,
)

IMAGE_ALL_VARIABLES: Final[VariableCollection] = (
    IMAGE_BASIC_VARIABLES
    + IMAGE_PE_VARIABLES
    + IMAGE_SIGCOR_VARIABLES
    + IMAGE_TIME_VARIABLES
)

EVENT_VERTEX_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "evt.vtx.x",  # Event vertex x-coordinate [m]
        "evt.vtx.y",  # Event vertex y-coordinate [m]
        "evt.vtx.z",  # Event vertex z-coordinate [m]
    ],
    root=SNTP_BR_STD,
)

MC_4MOMENTUM_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "mc.p4neunoosc[4]",  # Neutrino 4-momentum
        "mc.p4mu1[4]",  # Primary muon 4-momentum (note: energy sign quirk)
        "mc.p4shw[4]",  # Hadronic shower 4-momentum
    ],
    root=SNTP_BR_STD,
)

# MC truth particle stack: one row per particle, variable length per event.
# Note the `IstHEP == 999` terminator row -- see README.md.
MC_PARTICLE_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "stdhep.IdHEP",  # PDG code
        "stdhep.IstHEP",  # HEPEVT/GENIE status code
        "stdhep.mass",  # Rest mass [GeV]
        "stdhep.p4[4]",  # 4-momentum: (px, py, pz) [GeV], energy [GeV]
        "stdhep.vtx[4]",  # Production 4-position: (x, y, z) [m], time
    ],
    root=SNTP_BR_STD,
)

MC_INTERACTION_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "mc.iaction",  # Interaction type (CC / NC)
        "mc.inunoosc",  # Interacting neutrino PDG code
    ],
    root=SNTP_BR_STD,
)

MC_TRUTH_EVENT_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "mc.itg",  # PDG code of the struck target
        "mc.iresonance",  # Interaction channel (QE / RES / DIS / CPP / IMD)
        "mc.istruckq",  # Struck-quark code, DIS only (encoding unconfirmed)
        "mc.iflags",  # Interaction flag bitmask (encoding unconfirmed)
        "mc.x",  # Bjorken x
        "mc.y",  # Inelasticity y
        "mc.q2",  # Four-momentum transfer squared (negative / spacelike)
        "mc.w2",  # Hadronic invariant mass squared [GeV^2]
        "mc.sigma",  # Cross section (units unconfirmed)
        "mc.sigmadiff",  # Differential cross section (formula unconfirmed)
        "mc.emfrac",  # EM fraction of the hadronic shower energy
        "mc.ndigu",  # Total digits, u-view
        "mc.ndigv",  # Total digits, v-view
        "mc.tphu",  # Summed pulse height, u-view (units unconfirmed)
        "mc.tphv",  # Summed pulse height, v-view (units unconfirmed)
    ],
    root=SNTP_BR_STD,
)

# ================================ [ Enums  ] ================================ #


class _BaseEnum(Enum):
    """\
    [ Internal ] Base class for all Enums in the package.
    """

    @property
    def latex(self) -> str:
        return "< ? >"

    def __str__(self) -> str:
        return self.name.replace("_", " ").title()

    def __repr__(self) -> str:
        return f"oscana.{self.__class__.__name__}.{self.name}"


class EIAction(_BaseEnum):
    """\
    Neutrino Interaction Types (Neutral / Charged Current)
    """

    NC = 0
    CC = 1
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: object) -> EIAction:
        return cls(cls.UNKNOWN)


class EIResonance(_BaseEnum):
    """\
    Neutrino Interaction Types (Resonance)
    """

    QES = 1001  # Quasi-Elastic Scattering
    RES = 1002  # Resonance Production
    DIS = 1003  # Deep Inelastic Scattering
    COH = 1004  # Coherent Pion Production
    IMD = 1005  # Inverse Muon Decay


class EIdHEP(_BaseEnum):
    """\
    Particle ID Codes (PDG Codes)
    """

    PHOTON = 22
    ELECTRON = 11
    MUON = 13
    TAU = 15
    ELECTRON_NU = 12
    MUON_NU = 14
    TAU_NU = 16
    CHARGED_PION = 211
    NEUTRAL_PION = 111
    ETA = 221
    CHARGED_RHO = 213
    NEUTRAL_RHO = 113
    OMEGA = 223
    CHARGED_KAON = 321
    NEUTRAL_KAON = 311
    K_SHORT = 310
    K_LONG = 130
    PROTON = 2212
    NEUTRON = 2112
    DELTA_MINUS = 1114
    DELTA_ZERO = 2114
    DELTA_PLUS = 2214
    DELTA_PLUS_PLUS = 2224
    GEANTINO = 28  # Placeholder
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: object) -> EIdHEP:
        return cls(cls.UNKNOWN)


class EInteraction(_BaseEnum):
    """\
    Interaction Codes

    Note
    ----
    The interaction codes are calculated by multiplying the "mc.iaction" and
    "stdhep.IdHEP" columns in the data. The "mc.iaction" is the true interaction 
     (either CC or NC) and the "stdhep.IdHEP" column is the interacting neutrino
     (NuE, NuMu, NuTau, or their anti-particles).
    """

    # CC Interactions
    NUECC = EIdHEP.ELECTRON_NU.value
    NUMUCC = EIdHEP.MUON_NU.value
    NUTAUCC = EIdHEP.TAU_NU.value

    ANTINUECC = -EIdHEP.ELECTRON_NU.value
    ANTINUMUCC = -EIdHEP.MUON_NU.value
    ANTINUTAUCC = -EIdHEP.TAU_NU.value

    # NC Interactions
    NC = 0

    # Unknown
    UNKNOWN = -1

    @property
    def latex(self) -> str:
        return {
            self.NUECC: r"$\nu_\text{e}$ CC",
            self.NUMUCC: r"$\nu_\mu$ CC",
            self.NUTAUCC: r"$\nu_\tau$ CC",
            self.ANTINUECC: r"$\bar{\nu}_e$ CC",
            self.ANTINUMUCC: r"$\bar{\nu}_\mu$ CC",
            self.ANTINUTAUCC: r"$\bar{\nu}_\tau$ CC",
            self.NC: r"NC",
        }.get(self, r"< ? >")

    @classmethod
    def _missing_(cls, value: object) -> EInteraction:
        return cls(cls.UNKNOWN)


class ESimpleInteraction(_BaseEnum):
    """\
    Simplified Interaction Codes

    Note
    ----
    The simplified interaction codes are calculated by taking the absolute
    value of the product of "mc.iaction" and "stdhep.IdHEP". The "mc.iaction"
    is the true interaction (either CC or NC) and the "stdhep.IdHEP" column is
    the interacting neutrino (NuE, NuMu, NuTau, or their anti-particles).
    """

    # CC Interactions
    NUECC = abs(EIdHEP.ELECTRON_NU.value)
    NUMUCC = abs(EIdHEP.MUON_NU.value)
    NUTAUCC = abs(EIdHEP.TAU_NU.value)

    # NC Interactions
    NC = 0

    # Unknown
    UNKNOWN = -1

    @property
    def latex(self) -> str:
        return {
            self.NUECC: r"$\stackrel{(\rule{0.8em}{0.4pt})}{\nu}_\text{e}$ CC",
            self.NUMUCC: r"$\stackrel{(\rule{0.8em}{0.4pt})}{\nu}_\mu$ CC",
            self.NUTAUCC: r"$\stackrel{(\rule{0.8em}{0.4pt})}{\nu}_\tau$ CC",
            self.NC: r"NC",
        }.get(self, r"< ? >")

    @classmethod
    def _missing_(cls, value: object) -> ESimpleInteraction:
        return cls(cls.UNKNOWN)


class EPlaneView(_BaseEnum):
    # Note: I am using (mostly) the same Enum as the MINOS code (refer to
    #       `EPlaneView` on Doxygen).

    # Standard
    X = 0
    Y = 1
    U = 2
    V = 3

    # Calibration Detector
    A = 4
    B = 5

    # Veto Shield
    TopFlat = 8
    TopESlant = 9
    TopWSlant = 10
    WallOnEdge = 11
    WallESlant = 12
    WallWSlant = 13

    # Unknown
    Unknown = 7  # --> For some reason this is a 7 and not a 6?

    @classmethod
    def _missing_(cls, value: object) -> EPlaneView:
        return cls(cls.Unknown)
