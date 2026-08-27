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
    "MC_STRIP_TRUTH_VARIABLES",
    "DETECTOR_STATE_VARIABLES",
    "DAQ_CONTEXT_VARIABLES",
    "VETO_SHIELD_VARIABLES",
    "IMAGE_RAW_VARIABLES",
    "MC_PARTICLE_LINEAGE_VARIABLES",
    "MC_FLUX_VARIABLES",
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

# See README.md (in this directory) for variable explanations.

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
        "fEvent",  # Event number
    ],
    root=SNTP_BR_STD,
)

IMAGE_BASIC_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "stp.planeview",  # Plane view: 2 = U, 3 = V
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
        "mc.p4mu1[4]",  # Primary muon 4-momentum
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
        "mc.istruckq",  # PDG id of the struck quark (0 none, 1 d, 2 u)
        "mc.iflags",  # Hadronisation model -- see README
        "mc.x",  # Bjorken x
        "mc.y",  # Inelasticity y
        "mc.q2",  # Four-momentum transfer squared (negative / spacelike)
        "mc.w2",  # Hadronic invariant mass squared [GeV^2]
        "mc.sigma",  # Cross section (units unconfirmed)
        "mc.sigmadiff",  # Differential cross section (formula unconfirmed)
        "mc.emfrac",  # EM fraction of the hadronic shower energy
        "mc.ndigu",  # Truth-matched raw digits, u-view
        "mc.ndigv",  # Truth-matched raw digits, v-view
        "mc.tphu",  # Summed pulse height, u-view [raw ADC, pedestal-subtracted]
        "mc.tphv",  # Summed pulse height, v-view [raw ADC, pedestal-subtracted]
    ],
    root=SNTP_BR_STD,
)

# Truth for each strip in `IMAGE_*`: which simulated particles put energy
# there and in what proportion.
MC_STRIP_TRUTH_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "thstp.neumc",  # Index of the interaction (mc record) responsible
        "thstp.nneu",  # Number of interactions contributing to the strip
        "thstp.sigflg",  # Signal flag
        "thstp.stdhep[3]",  # Up to 3 contributing stdhep particle indices
        "thstp.phfrac[3]",  # Pulse-height fraction from each of those
    ],
    root=SNTP_BR_STD,
)

# Detector conditions. Constant within a file, but needed to interpret it:
# the coil current sets the magnetic field, and gevpermip converts the
# pulse heights in `IMAGE_PE_VARIABLES` into energy.
DETECTOR_STATE_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "calstatus.gevpermip",  # MIP -> GeV calibration constant
        "detstatus.coilcurrent1",  # Magnet coil current
        "detstatus.coilcurrent2",  # Second coil current reading
        "detstatus.coilstatus",  # Magnet on/off/polarity
        "detstatus.dcscoilstatus",  # Same, from the slow-control system
        "detstatus.dbuhvstatus",  # Photomultiplier high-voltage status
    ],
    root=SNTP_BR_STD,
)

# Beam, trigger and absolute timing context for the snarl.
# Note: unset (-1) for Monte Carlo files
DAQ_CONTEXT_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "dataquality.spillstatus",  # Beam spill status
        "dataquality.spilltype",  # Beam spill type
        "dataquality.spilltimeerror",  # Spill timing error
        "dataquality.trigsource",  # What triggered the readout
        "dataquality.trigtime",  # Trigger time
        "dataquality.snarlmultiplicity",  # Interactions in this snarl
        "dataquality.errorcode",  # DAQ error code
        "timestatus.sgate_10mhz",  # Spill gate, 10 MHz clock
        "timestatus.sgate_53mhz",  # Spill gate, 53 MHz clock
        "timestatus.rollover_53mhz",  # 53 MHz counter rollovers
        "timestatus.crate_t0_ns",  # Crate time zero [ns]
        "timestatus.timeframe",  # Time frame number
    ],
    root=SNTP_BR_STD,
)

# Raw hits in the veto shield.
VETO_SHIELD_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "vetostp.pln",  # Shield plane
        "vetostp.plank",  # Shield plank within the plane
        "vetostp.x",  # Position [m]
        "vetostp.y",  # Position [m]
        "vetostp.z[2]",  # Position at each strip end [m]
        "vetostp.adc[2]",  # Raw pulse height at each end [ADC]
        "vetostp.time[2]",  # Hit time at each end
        "vetostp.ndigit",  # Digits on this shield strip
    ],
    root=SNTP_BR_STD,
)

# Uncalibrated pulse height -- what the electronics actually recorded, as
# opposed to `IMAGE_PE_VARIABLES`, which is MINOS's calibrated product.
IMAGE_RAW_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "stp.ph0.raw",  # Raw ADC, east end
        "stp.ph1.raw",  # Raw ADC, west end
    ],
    root=SNTP_BR_STD,
)

# Particle genealogy: the decay chain behind each `stdhep` row.
MC_PARTICLE_LINEAGE_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        "stdhep.parent[2]",  # Indices of the particle's parents
        "stdhep.child[2]",  # Indices of its daughters
        "stdhep.ndethit",  # Digits it deposited energy in
    ],
    root=SNTP_BR_STD,
)

# The gnumi beam-simulation record: where this neutrino came from, from the
# primary proton through to its weight at each detector.
MC_FLUX_VARIABLES: Final[VariableCollection] = VariableCollection(
    variables=[
        # Which gnumi beam-simulation event this neutrino came from.
        "mc.flux.fluxrun",
        "mc.flux.fluxevtno",
        # The neutrino as generated: direction cosines, momentum, energy, flavour.
        "mc.flux.ndxdz",
        "mc.flux.ndydz",
        "mc.flux.npz",
        "mc.flux.nenergy",
        "mc.flux.ntype",
        # The same neutrino as it would appear at each detector, with the weight
        # that turns generated events into a flux prediction there. This pair is
        # what the near/far extrapolation is built from.
        "mc.flux.ndxdznear",
        "mc.flux.ndydznear",
        "mc.flux.nenergynear",
        "mc.flux.nwtnear",
        "mc.flux.ndxdzfar",
        "mc.flux.ndydzfar",
        "mc.flux.nenergyfar",
        "mc.flux.nwtfar",
        # The decay that produced it: mode, where it happened, parent momentum.
        "mc.flux.norig",
        "mc.flux.ndecay",
        "mc.flux.vx",
        "mc.flux.vy",
        "mc.flux.vz",
        "mc.flux.pdpx",
        "mc.flux.pdpy",
        "mc.flux.pdpz",
        "mc.flux.necm",
        # The parent hadron itself -- type, momentum and where it was produced.
        "mc.flux.ptype",
        "mc.flux.ppdxdz",
        "mc.flux.ppdydz",
        "mc.flux.pppz",
        "mc.flux.ppenergy",
        "mc.flux.ppmedium",
        "mc.flux.ppvx",
        "mc.flux.ppvy",
        "mc.flux.ppvz",
        # If the parent was a muon, its momentum and energy.
        "mc.flux.muparpx",
        "mc.flux.muparpy",
        "mc.flux.muparpz",
        "mc.flux.mupare",
        # The ancestry in the target: `tgen` counts how many hadronic
        # interactions deep the chain goes, which hadron-production reweighting
        # needs.
        "mc.flux.tvx",
        "mc.flux.tvy",
        "mc.flux.tvz",
        "mc.flux.tpx",
        "mc.flux.tpy",
        "mc.flux.tpz",
        "mc.flux.tptype",
        "mc.flux.tgen",
        "mc.flux.tgptype",
        "mc.flux.tgppx",
        "mc.flux.tgppy",
        "mc.flux.tgppz",
        "mc.flux.tprivx",
        "mc.flux.tprivy",
        "mc.flux.tprivz",
        # The primary proton beam that started it all (120 GeV at the Main
        # Injector), and the ray-traced point used for the weights.
        "mc.flux.beamx",
        "mc.flux.beamy",
        "mc.flux.beamz",
        "mc.flux.beampx",
        "mc.flux.beampy",
        "mc.flux.beampz",
        "mc.flux.xpoint",
        "mc.flux.ypoint",
        "mc.flux.zpoint",
        # Importance weight from the beam simulation, then the overall flux
        # weight with its uncertainty and the version that produced it.
        "mc.flux.nimpwt",
        "mc.fluxwgt.version",
        "mc.fluxwgt.weight",
        "mc.fluxwgt.weighterr",
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
