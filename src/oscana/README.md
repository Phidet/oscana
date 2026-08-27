# MINOS SNTP variables

Reference for the `VariableCollection`s in [`constants.py`](constants.py),
which name the branches read from MINOS `.sntp.root` files. Anything still unresolved is marked **`???`**.

## `HEADER_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `fRun` | DAQ run number. |
| `fSubRun` | DAQ subrun number. |
| `fSnarl` | Snarl number within the run. |
| `fEvent` | Event number within the snarl. Constant `-1` in every file checked — the reconstruction chain assigns it. |

## `IMAGE_*` — digitised strip hits

### `IMAGE_BASIC_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `stp.planeview` | Which stereo view the strip belongs to: `2` = U, `3` = V. |
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

### `IMAGE_TIME_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `stp.time0` | Charge-weighted mean hit time, east end [s], relative to the trigger. `-999999` means that end saw no signal. |
| `stp.time1` | Same, west end. |

## `EVENT_VERTEX_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `evt.vtx.x` | Reconstructed event vertex x [m]. |
| `evt.vtx.y` | Reconstructed event vertex y [m]. |
| `evt.vtx.z` | Reconstructed event vertex z [m]. |

Reconstruction output, unlike everything else here (see [Not included](#not-included)).

## `MC_4MOMENTUM_VARIABLES`

Components are `(px, py, pz)` then energy, all GeV.

| Variable | Meaning |
|----------|---------|
| `mc.p4neunoosc[4]` | Neutrino 4-momentum under the unoscillated hypothesis. |
| `mc.p4mu1[4]` | Primary muon 4-momentum. Duplicates a `stdhep` lepton row, but with the energy component's sign flipped for the matter lepton. |
| `mc.p4shw[4]` | Final-state hadronic system. Not the sum of the `stdhep` hadrons: it is evaluated before final-state interactions (FSI) — the rescattering of products inside the struck nucleus — whereas `stdhep` records the particles that emerge after them. |

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
| `mc.iflags` | Hadronisation model: `0` non-DIS, `1` old KNO, `2` modified KNO, `3` charm, `11`/`12`/`13` JETSET string/cluster/other. |
| `mc.x` | Bjorken x. |
| `mc.y` | Inelasticity y. The invariant form, not the lab-frame ratio, which ignores Fermi motion. |
| `mc.q2` | Four-momentum transfer squared. |
| `mc.w2` | Hadronic invariant mass squared [GeV²]. |
| `mc.sigma` | Cross section for this interaction. Units unconfirmed — the value is passed through unchanged from NEUGEN. **`???`** |
| `mc.sigmadiff` | Differential cross section. Same issue as above. **`???`** |
| `mc.emfrac` | EM fraction of hadronic shower energy. Pre-FSI. |
| `mc.ndigu` | Raw digits in the u-view truth-matched to this interaction. |
| `mc.ndigv` | Same, v-view. A digit touching both views is counted in u only. |
| `mc.tphu` | Summed pulse height, u-view — **raw ADC, pedestal-subtracted**, over the same digits as `ndigu`. |
| `mc.tphv` | Same, v-view. |

## `MC_PARTICLE_VARIABLES`

One row per particle, variable length per event: the incoming neutrino,
the struck target, and everything in the final state.

| Variable | Meaning |
|----------|---------|
| `stdhep.IdHEP` | PDG code. |
| `stdhep.IstHEP` | HEPEVT status code: `0` initial state, `1` final state, `11` struck nucleon. |
| `stdhep.mass` | Rest mass [GeV]. |
| `stdhep.p4[4]` | 4-momentum: `(px, py, pz)` then energy, all GeV. |
| `stdhep.vtx[4]` | Production 4-position: `(x, y, z)` in metres, then time in seconds. |

**Every event carries one `IstHEP == 999`, `IdHEP == 0` row** — a *rootino*,
a null placeholder never tracked.

## `MC_STRIP_TRUTH_VARIABLES`

Truth for each strip in `IMAGE_*`: which simulated particles deposited
energy there, and in what proportion. Exactly one record per hit, so it
lines up row-for-row with the hit variables.

| Variable | Meaning |
|----------|---------|
| `thstp.neumc` | Index of the interaction (`mc` record) responsible for the strip. |
| `thstp.nneu` | How many interactions contributed to it. |
| `thstp.sigflg` | Signal flag. |
| `thstp.stdhep[3]` | Up to three contributing `stdhep` particle indices. |
| `thstp.phfrac[3]` | Fraction of the strip's pulse height from each of those. |

## `DETECTOR_STATE_VARIABLES`

| Variable | Meaning |
|----------|---------|
| `calstatus.gevpermip` | Calibration constant converting MIP-equivalent signal to GeV. Needed to turn the `pe` values into energy. |
| `detstatus.coilcurrent1` | Magnet coil current, which sets the field and hence momentum and charge-sign measurement. |
| `detstatus.coilcurrent2` | Second coil current reading. |
| `detstatus.coilstatus` | Magnet on/off and polarity. |
| `detstatus.dcscoilstatus` | The same, as reported by the slow-control system. |
| `detstatus.dbuhvstatus` | Photomultiplier high-voltage status. |

## `DAQ_CONTEXT_VARIABLES`

Beam, trigger and absolute-timing context for the snarl. Unset (`-1`) for Monte Carlo.

| Variable | Meaning |
|----------|---------|
| `dataquality.spillstatus` | Beam spill status. |
| `dataquality.spilltype` | Beam spill type. |
| `dataquality.spilltimeerror` | Spill timing error. |
| `dataquality.trigsource` | What triggered the readout. |
| `dataquality.trigtime` | Trigger time. |
| `dataquality.snarlmultiplicity` | Interactions in this snarl. |
| `dataquality.errorcode` | DAQ error code. |
| `timestatus.sgate_10mhz` | Spill gate on the 10 MHz clock. |
| `timestatus.sgate_53mhz` | Spill gate on the 53 MHz clock. |
| `timestatus.rollover_53mhz` | 53 MHz counter rollovers. |
| `timestatus.crate_t0_ns` | Crate time zero [ns]. |
| `timestatus.timeframe` | Time frame number. |

## `VETO_SHIELD_VARIABLES`

Raw hits in the veto shield.

| Variable | Meaning |
|----------|---------|
| `vetostp.pln` | Shield plane. |
| `vetostp.plank` | Shield plank within the plane. |
| `vetostp.x` | Position [m]. |
| `vetostp.y` | Position [m]. |
| `vetostp.z[2]` | Position at each strip end [m]. |
| `vetostp.adc[2]` | Raw pulse height at each end [ADC]. |
| `vetostp.time[2]` | Hit time at each end. |
| `vetostp.ndigit` | Digits on this shield strip. |

## `IMAGE_RAW_VARIABLES`

Uncalibrated pulse height — what the electronics recorded, before any
correction. `IMAGE_PE_VARIABLES` is the calibrated product derived from it.

| Variable | Meaning |
|----------|---------|
| `stp.ph0.raw` | Raw ADC, east end. |
| `stp.ph1.raw` | Raw ADC, west end. |

## `MC_PARTICLE_LINEAGE_VARIABLES`

The decay chain behind each `stdhep` row.

| Variable | Meaning |
|----------|---------|
| `stdhep.parent[2]` | Indices of the particle's parents. |
| `stdhep.child[2]` | Indices of its daughters. |
| `stdhep.ndethit` | How many digits it deposited energy in. |

## `MC_FLUX_VARIABLES`

The gnumi beam-simulation record: where this neutrino came from, from the
primary proton through to its weight at each detector.

| Fields | What they hold |
|--------|----------------|
| `fluxrun`, `fluxevtno` | Which beam-simulation event this was. |
| `ntype`, `nenergy`, `npz`, `ndxdz`, `ndydz` | The neutrino as generated: flavour, energy, direction. |
| `nenergynear`, `nwtnear`, `ndxdznear`, `ndydznear` | The same neutrino as it would appear at the Near Detector, with the weight that turns generated events into a flux prediction there. |
| `nenergyfar`, `nwtfar`, `ndxdzfar`, `ndydzfar` | The same for the Far Detector. Together with the near fields, this pair is what the near/far extrapolation is built from. |
| `ndecay`, `norig`, `vx`, `vy`, `vz`, `pdpx`, `pdpy`, `pdpz`, `necm` | The decay that produced it: mode, where it happened, parent momentum. |
| `ptype`, `pppz`, `ppenergy`, `ppdxdz`, `ppdydz`, `ppmedium`, `ppvx`, `ppvy`, `ppvz` | The parent hadron: type, momentum, and where it was produced. |
| `muparpx`, `muparpy`, `muparpz`, `mupare` | The muon's momentum and energy, where the parent was a muon. |
| `tgen`, `tptype`, `tgptype`, `tvx…tpz`, `tgppx…tgppz`, `tprivx…tprivz` | Ancestry in the target. `tgen` counts how many hadronic interactions deep the chain runs, which is what hadron-production reweighting needs. |
| `beamx…beampz`, `xpoint`, `ypoint`, `zpoint` | The primary proton beam, and the ray-traced point used for the weights. |
| `nimpwt`, `mc.fluxwgt.weight`, `weighterr`, `version` | Importance weight, then the overall flux weight with its uncertainty and the version that produced it. |

## Not included

Fields inside branches that are otherwise read. Grouped by why.

**Recoverable from what is kept.**

| Branch | Why |
|--------|-----|
| `stp.z` | One fixed z per plane, so a lookup on `stp.plane`. |
| `stp.tpos` | Transverse position, fixed by `plane` and `strip` together. |
| `stp.ndigit` | Only ever 1 or 2: how many ends of the strip fired. The same information as which of `time0`/`time1` holds the `-999999` sentinel. |
| `mc.inu` | Duplicates the PDG code on the `stdhep` initial-state neutrino row (`IstHEP == 0`). |
| `mc.a` | The target nucleus's mass number, encoded in the PDG code of the `stdhep` nucleus row. Hydrogen when there is no such row. |
| `mc.z` | Its atomic number, from the same code. |
| `mc.vtxx` | Duplicates `vtx[0]` on the `stdhep` neutrino row. |
| `mc.vtxy` | Duplicates its `vtx[1]`. |
| `mc.vtxz` | Duplicates its `vtx[2]`. |
| `mc.p4neu[4]` | Duplicates `p4` on the `stdhep` neutrino row. |
| `mc.p4tgt[4]` | Duplicates `p4` on the `stdhep` struck-nucleon or nucleus row. |
| `mc.p4mu2[4]` | Duplicates a second `stdhep` muon row, where the event has one. |
| `mc.p4el1[4]` | Duplicates an `stdhep` electron row. |
| `mc.p4el2[4]` | Duplicates a second one. |
| `mc.p4tau[4]` | Duplicates an `stdhep` tau row. Never non-zero in any file checked — no ντ events. |

Each duplication is re-checked per file before anything is dropped, so a
file that breaks one is refused rather than silently stripped.

**Array bookkeeping — meaningless once loaded.**

| Branch | Why |
|--------|-----|
| `stp.index` | Position of the strip in its array; row order already carries it. |
| `mc.index` | Likewise for the interaction record. |
| `stdhep.index` | Likewise for the particle. |
| `mc.stdhep[2]` | Index range pointing into `stdhep`; both are already joined per event. |
| `stdhep.mc` | The same pointer in reverse. |

**Detector hardware, not event data.**

| Branch | Why |
|--------|-----|
| `stp.pmtindex0` | Which photomultiplier channel the east end is wired to. Fixed per strip, and a property of the readout map rather than the event. |
| `stp.pmtindex1` | The same for the west end. |
| `stp.demuxveto` | Output of demultiplexing, which resolves the Near Detector's several-strips-per-channel readout. Constant `0` in the Far Detector files here, and a reconstruction step in any case. |

**An intermediate calibration stage.**

| Branch | Why |
|--------|-----|
| `stp.ph0.siglin` | Sits between `raw` and `pe`, linearity-corrected but not yet attenuation-corrected. Both endpoints of that chain are kept, and the factor between them is recoverable from the pair, so the middle step adds little. |
| `stp.ph1.siglin` | The same, west end. |

**Unset.**

| Branch | Why |
|--------|-----|
| `mc.iboson` | Should carry the exchange boson's PDG code (Z⁰ = 23, W⁺ = 24) but holds a constant sentinel in every file checked. |

**Truth dropped for a technical reason.**

| Branch | Why |
|--------|-----|
| `stdhep.dethit[2]` | The particle's first and last hit — plane, strip, position and momentum for each. It is left out because uproot reads it as a C++ struct array. Would need work to convert to numpy/python. |

Whole branch groups that are not used.

| Group | Why |
|-------|-----|
| `trk` | Reconstructed tracks. |
| `shw` | Reconstructed showers. |
| `slc` | Reconstructed slices. |
| `clu` | Clusters, upstream of track and shower fitting. |
| `evt` | Reconstructed events. The one exception is the vertex, `evt.vtx.*`, offered as `EVENT_VERTEX_VARIABLES` because analyses rely on it — but it is reconstruction output, so it stays out of archival defaults. |
| `thevt` | Truth matching for reconstructed events. Unlike `thstp`, which labels the strips we keep, this is meaningless without the reco object it describes. |
| `thtrk` | Likewise for tracks. |
| `thshw` | Likewise for showers. |
| `thslc` | Likewise for slices. |
| `crhdr` | Cosmic-ray zenith/azimuth and sky coordinates, derived from reconstructed tracks. |
| `vetohdr` | Veto shield summary; the raw hits are kept, see `VETO_SHIELD_VARIABLES`. |
| `vetoexp` | Where a *reconstructed track* was expected to cross the shield — a projection, not a measurement. The shield's actual hits are kept, see `VETO_SHIELD_VARIABLES`. |
| `dmxstatus` | Demultiplexing quality; demultiplexing is a reconstruction step. |
| `deadchips` | Which channels were dead — genuinely useful for efficiency, but **empty in every file checked**, so there is nothing to keep. |
| `detsim` | Per-snarl counters from the electronics simulation: photoelectrons, pixels hit, cross-talk, and how many digits survived the front-end trigger, sparsification and DAQ trigger in turn. Again a record of the simulation's behaviour rather than the event's. |
| `photon` | Per-snarl counters from the optical simulation: how many blue scintillation photons were made, how many green ones the wavelength-shifting fibre re-emitted, how many photoelectrons resulted, and how much was discarded. Both raw and prescale-corrected counts (simulating every photon is too slow, so a fraction is tracked and scaled up). Describes how the simulation ran, not what physically happened — the resulting light is already in `stp.ph*`. |
| `mchdr` | Generator codename, host and timestamp. |
| `evthdr` | Counts of reconstructed objects per snarl. |
| `digihit` | Per particle per strip: entry and exit point, path length. The finest-grained truth there is — but **empty in every file checked**, so there is nothing to keep. |
