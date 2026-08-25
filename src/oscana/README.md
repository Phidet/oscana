# MINOS SNTP variables

Reference for the `VariableCollection`s in [`constants.py`](constants.py),
which name the branches read from MINOS `.sntp.root` (`NtpSt`) files.

Meanings come from the MINOS offline (LOON) source where possible —
`NtpMCTruth.h`, `Truth.h`, `NtpMCStdHep.h`, `PlaneView.h`, and the fill code
in `NtpMCModule.cxx` — otherwise from the 2003 `NtpSR` glossary, `NuEvent.h`,
or the observed distributions in a Far Detector MC file. Anything still
unresolved is marked **`???`** rather than guessed at.

## `HEADER_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `fRun` | DAQ run number. |
| `fSubRun` | DAQ subrun number. |
| `fSnarl` | Snarl (readout window) number within the run. |
| `fEvent` | Event number within the snarl. Constant `-1` in every file checked — the reconstruction chain assigns it. |

## `IMAGE_*` — digitised strip hits

Jagged: one entry per hit, per event. Occupancy is ~0.1%, hence a sparse
list rather than a dense image. `IMAGE_ALL_VARIABLES` concatenates all four.

### `IMAGE_BASIC_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `stp.planeview` | Strip orientation: `2` = U, `3` = V (`PlaneView.h`, which also defines `kX=0, kY=1, kA=4, kB=5, kUnknown=7` and 8–15 for VetoShield). A pure function of `stp.plane` — see [Geometry](#geometry). |
| `stp.strip` | Strip number within the plane, 0–191. |
| `stp.plane` | Plane number along the beam axis, 1–485 in a Far Detector file. |

### `IMAGE_PE_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `stp.ph0.pe` | Calibrated light yield, east end [photoelectrons]. |
| `stp.ph1.pe` | Same, west end. |

### `IMAGE_SIGCOR_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `stp.ph0.sigcor` | Attenuation-normalised strip response, east end. |
| `stp.ph1.sigcor` | Same, west end. |

Not a rescaling of `pe`: the ratio spans 20–1901 over ~3.9 M distinct values
in one file, i.e. a per-strip, per-hit calibration.

### `IMAGE_TIME_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `stp.time0` | Charge-weighted mean hit time, east end [s], relative to the trigger. `-999999` means that end saw no signal. |
| `stp.time1` | Same, west end. |

The sentinel fires on ~23% of hits per end but never on both at once, so
every hit has a usable time from at least one end. Mask it before averaging
or differencing.

## `EVENT_VERTEX_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `evt.vtx.x` | Reconstructed event vertex x [m]. |
| `evt.vtx.y` | Reconstructed event vertex y [m]. |
| `evt.vtx.z` | Reconstructed event vertex z [m]. |

Reconstruction output, unlike everything else here. Not the truth vertex
(`mc.vtxx/y/z`, not read — see [Not included](#not-included)).

## `MC_4MOMENTUM_VARIABLES`

Components are `(px, py, pz)` then energy, all GeV.

| Variable | Meaning |
|----------|---------|
| `mc.p4neunoosc[4]` | Neutrino 4-momentum under the unoscillated hypothesis. Matches no `stdhep` row — a hypothetical never generated as a particle. |
| `mc.p4mu1[4]` | Primary muon 4-momentum. Duplicates a `stdhep` lepton row, but with the energy component's sign flipped for the matter lepton (`NuEvent.h`: "not proper p4"). |
| `mc.p4shw[4]` | Final-state hadronic system. Not the sum of `stdhep` hadrons — evaluated pre-FSI, while `stdhep` is post-FSI. |

## `MC_INTERACTION_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `mc.iaction` | `0` = NC, `1` = CC. |
| `mc.inunoosc` | PDG code of the neutrino flavour at production. Equals `mc.inu` throughout the file checked, but would differ in a sample where flavours are swapped. |

## `MC_TRUTH_EVENT_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `mc.itg` | PDG code of the struck target: `2212`/`2112` nucleons, a large nucleus code for coherent events, `11` for inverse muon decay. |
| `mc.iresonance` | Channel: `1001` QE, `1002` resonance, `1003` DIS, `1004` coherent pion, `1005` inverse muon decay. |
| `mc.istruckq` | PDG id of the struck quark: `0` none (non-DIS), `1` d, `2` u. |
| `mc.iflags` | Hadronisation model, **not** a bitmask: `0` non-DIS, `1` old KNO, `2` modified KNO, `3` charm, `11`/`12`/`13` JETSET string/cluster/other. |
| `mc.x` | Bjorken x, [0, 1]. |
| `mc.y` | Inelasticity y, [0, 1]. The invariant form, not the lab-frame ratio, which ignores Fermi motion. |
| `mc.q2` | Four-momentum transfer squared. **Negative** here — negate for the usual positive `Q²`. |
| `mc.w2` | Hadronic invariant mass squared [GeV²]. QE events sit at ≈0.880 = (proton mass)². |
| `mc.sigma` | Cross section for this interaction. Units unconfirmed — passed through unchanged from NEUGEN, which is Fortran and outside the LOON tree. **`???`** |
| `mc.sigmadiff` | Differential cross section. Same provenance, same open question. Exactly `0` for the inverse-muon-decay events, where `x`/`y` are undefined. **`???`** |
| `mc.emfrac` | EM fraction of hadronic shower energy, [0, 1]. Pre-FSI like `p4shw`, so it disagrees with a post-FSI computation from `stdhep`. |
| `mc.ndigu` | Raw digits in the u-view truth-matched to this interaction. Counts *digits*, not reconstructed strips, so it cannot be rebuilt from `stp.*`. |
| `mc.ndigv` | Same, v-view. A digit touching both views is counted in u only. |
| `mc.tphu` | Summed pulse height, u-view — **raw ADC, pedestal-subtracted**, over the same digits as `ndigu`. Hence the scale far above `pe`. |
| `mc.tphv` | Same, v-view. |

## `MC_PARTICLE_VARIABLES`

The `stdhep` truth particle stack: one row per particle, variable length.

| Variable | Meaning |
|----------|---------|
| `stdhep.IdHEP` | PDG code. |
| `stdhep.IstHEP` | Status code. `1` final state, `0` initial state, `11` struck nucleon. |
| `stdhep.mass` | Rest mass [GeV]. |
| `stdhep.p4[4]` | 4-momentum: `(px, py, pz)` then energy, all GeV. |
| `stdhep.vtx[4]` | Production 4-position: `(x, y, z)` in metres, then time in seconds. |

**Every event carries one `IstHEP == 999`, `IdHEP == 0` row** — a *rootino*,
a null placeholder never tracked. LOON strips them too (`HepevtModule`'s
`DropStatus999`). Filter `IstHEP != 999` before particle-level physics.

## Geometry

`stp.z` and `stp.planeview` are both pure functions of `stp.plane` — they
describe the detector, not the hit. Measured over 14.7 M hits: no plane
disagrees on either.

`z` is a 484-entry lookup, near-affine in two segments split by the
supermodule gap — pitch 59.490 mm (planes 1–248) and 59.430 mm (250–485),
which a single global fit misses by 54.7 cm. `planeview` alternates with
plane parity, the sense inverting between supermodules because plane 249 is
absent while the physical alternation continues.

Both are Far-Detector measurements. The Near Detector differs in plane
count, coverage and view arrangement — re-derive before applying there.

## Not included

Fields inside branches that are otherwise read.

| Branch | Why |
|--------|-----|
| `stp.z` | Fixed per plane — see [Geometry](#geometry). |
| `stp.ph0.raw` | Earlier calibration stage than `pe` (ADC counts), east end. |
| `stp.ph1.raw` | Same, west end. |
| `stp.ph0.siglin` | Nonlinearity-corrected stage, before `pe`, east end. |
| `stp.ph1.siglin` | Same, west end. |
| `stp.tpos` | Transverse position; follows from `plane` + `strip`. |
| `stp.pmtindex0` | Electronics channel address, east end. |
| `stp.pmtindex1` | Same, west end. |
| `stp.index` | Index of the strip within its own array. |
| `stp.ndigit` | Number of digits on the strip. |
| `stp.demuxveto` | Demultiplexing veto flag. |
| `mc.inu` | The `stdhep` initial-state neutrino row (`status == 0`). |
| `mc.iboson` | Should hold the exchange boson PDG (Z0=23, W+=24) but is an unset sentinel in every file checked. |
| `mc.a` | Decodes from the `stdhep` nucleus row's PDG code. |
| `mc.z` | Likewise. Not Bjorken z, and not a position. |
| `mc.vtxx` | The `stdhep` neutrino row's `vtx[0]`. |
| `mc.vtxy` | Its `vtx[1]`. |
| `mc.vtxz` | Its `vtx[2]`. |
| `mc.p4neu[4]` | The `stdhep` neutrino row's `p4`. |
| `mc.p4tgt[4]` | The `stdhep` struck-nucleon or nucleus row's `p4`. |
| `mc.p4mu2[4]` | A second `stdhep` muon row, where one exists. |
| `mc.p4el1[4]` | An `stdhep` electron row. |
| `mc.p4el2[4]` | A second `stdhep` electron row. |
| `mc.p4tau[4]` | An `stdhep` tau row. No ντ events in any file checked. |
| `mc.index` | Index of the record within the `mc` array. |
| `mc.stdhep[2]` | Index range into `stdhep` — redundant once joined per event. |
| `mc.flux.*` | NuMI beamline provenance, ~60 fields; for flux systematics. |
| `mc.fluxwgt.*` | Flux reweighting factors, likewise. |
| `stdhep.index` | Index of the particle within its own array. |
| `stdhep.mc` | Back-index to the interaction record. |
| `stdhep.parent[2]` | Genealogy: parent particles. |
| `stdhep.child[2]` | Genealogy: daughter particles. |
| `stdhep.ndethit` | Number of digits this particle deposited in. |
| `stdhep.dethit[2]` | Which digits those were. |

Whole branch groups, none of them read.

| Group | Why |
|-------|-----|
| `trk` | Reconstructed tracks. |
| `shw` | Reconstructed showers. |
| `slc` | Reconstructed slices. |
| `clu` | Clusters, upstream of track and shower fitting. |
| `evt` | Reconstructed events — bar the vertex, kept above. |
| `thevt` | Reco↔truth matching for events; meaningless without the reco object. |
| `thtrk` | Likewise for tracks. |
| `thshw` | Likewise for showers. |
| `thslc` | Likewise for slices. |
| `thstp` | Likewise for strips. |
| `crhdr` | Cosmic-ray header. |
| `vetohdr` | Veto shield header. |
| `vetostp` | Veto shield strips. |
| `vetoexp` | Veto shield expected-hit information. |
| `calstatus` | Calibration status. |
| `detstatus` | Detector status. |
| `timestatus` | Timing status. |
| `dataquality` | Data-quality flags. |
| `dmxstatus` | Demultiplexer status. |
| `deadchips` | Dead-electronics map. |
| `detsim` | Hits and digits surviving each simulation stage. |
| `photon` | Photon-counting QA. |
| `mchdr` | Generator codename, host and timestamp. |
| `evthdr` | Header summary counts, partly reco-derived. |
| `digihit` | Per-digit truth, one tier below the `stdhep` stack. |
