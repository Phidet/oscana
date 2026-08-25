# MINOS SNTP variables

Reference for the `VariableCollection`s defined in [`constants.py`](constants.py),
which name the branches read out of MINOS `.sntp.root` (`NtpSt`) files.

Meanings below are cross-checked against a 2003 MINOS internal glossary for
the predecessor `NtpSR` tree, the `NuEvent.h` common-ntuple header, and the
observed value distributions in a real Far Detector MC file. Fields marked
**`???`** are genuinely unresolved — best guess only. Fuller derivations,
and the validation scripts behind the redundancy claims, live in the
`minos_data_storage` repo (`SCHEMA.md`, `validate_redundancy.py`).

## Scope

These collections deliberately cover only raw digitized hits and MC truth.
Nothing here references the MINOS reconstruction chain (tracks, showers,
slices, fit results), the veto/cosmic-ray subsystem, detector/DAQ status
monitoring, or NuMI beamline flux provenance — those branch groups are never
requested, not merely filtered out downstream. `EVENT_VERTEX_VARIABLES` is
the one exception: `evt.vtx.*` is reconstruction output, kept because
analyses rely on it.

## `HEADER_VARIABLES` — event identifiers

| Variable | Redundant? | Meaning |
|----------|------------|---------|
| `fRun` | no | DAQ run number. |
| `fSubRun` | no | DAQ subrun number. |
| `fSnarl` | no | Snarl (readout window / trigger) number within the run. |
| `fEvent` | **no information** — constant `-1` | Event number within the snarl. Found constant (`-1`) in every file checked so far — that indexing is assigned by the reconstruction chain. Kept anyway, since that's a finding from a limited sample, not a guarantee for every file; check before relying on it. |

## `IMAGE_*` — digitized strip hits

Jagged: one entry per hit, per event. Occupancy is very low (~0.1% of the
plane×strip grid), which is why this stays a sparse list rather than a dense
image.

`IMAGE_ALL_VARIABLES` is the concatenation of all four collections below.

### `IMAGE_BASIC_VARIABLES`

| Variable | Redundant? | Meaning |
|----------|------------|---------|
| `stp.planeview` | **yes** — from `stp.plane` | Strip orientation — one of MINOS's two ±45° readout views (no separate X view). Only values `2` and `3` occur. The MINOS `PlaneView::PlaneView_t` enum is documented as having `kU`/`kV` (used by all three detectors) plus `kB` for CalDet and VetoShield orientations, but the integer values are not given anywhere available, so which of `2`/`3` is U is unconfirmed. **`???`** Also derivable from `stp.plane` — see [Geometry-derived columns](#geometry-derived-columns). |
| `stp.strip` | no | Strip number within the plane (0–191). |
| `stp.plane` | no | Scintillator plane number along the beam axis (1–485 in a Far Detector file). The primary geometry key: `stp.planeview`, and `stp.z` where it is requested, both follow from it. |

### `IMAGE_PE_VARIABLES`

| Variable | Redundant? | Meaning |
|----------|------------|---------|
| `stp.ph0.pe` | no | Calibrated light yield at the strip's **east** end [photoelectrons]. |
| `stp.ph1.pe` | no | Same, **west** end. |

MINOS also defines `raw` (ADC counts) and `siglin` (nonlinearity-corrected)
calibration stages for the same hit; neither is requested here.

### `IMAGE_SIGCOR_VARIABLES`

| Variable | Redundant? | Meaning |
|----------|------------|---------|
| `stp.ph0.sigcor` | no | Attenuation-normalised strip response, east end. |
| `stp.ph1.sigcor` | no | Same, west end. |

Not redundant with `pe`, despite measuring the same hit: the
`sigcor / pe` ratio spans 20–1901 (median 81) and takes ~3.9 M distinct
values across a single file, i.e. it is a per-strip, per-hit calibration
rather than a constant factor.

### `IMAGE_TIME_VARIABLES`

| Variable | Redundant? | Meaning |
|----------|------------|---------|
| `stp.time0` | no | Charge-weighted mean hit time at the east end [s], relative to the event trigger. Sentinel `-999999` means that end saw no signal. |
| `stp.time1` | no | Same, west end. |

The sentinel fires on 22.9% of hits for `time0` and 22.4% for `time1`, but
on **0.00%** for both ends at once — every recorded hit has a usable time
from at least one end. Mask the sentinel before averaging or differencing
the two.

## `EVENT_VERTEX_VARIABLES` — reconstructed vertex

| Variable | Redundant? | Meaning |
|----------|------------|---------|
| `evt.vtx.x` | no | Reconstructed event vertex x [m]. |
| `evt.vtx.y` | no | Reconstructed event vertex y [m]. |
| `evt.vtx.z` | no | Reconstructed event vertex z [m]. |

Not to be confused with the *truth* vertex `mc.vtxx/vtxy/vtxz` (see
[Redundant branches](#redundant-branches)).

## `MC_4MOMENTUM_VARIABLES` — truth 4-vectors

Components are `(px, py, pz)` [GeV] then energy [GeV].

| Variable | Redundant? | Meaning |
|----------|------------|---------|
| `mc.p4neunoosc[4]` | no | 4-momentum under the unoscillated-neutrino hypothesis. Matches no particle-table row — a hypothetical quantity never generated as a particle, so genuinely distinct. |
| `mc.p4mu1[4]` | **yes** — particle table | Primary muon 4-momentum. A verified duplicate of a particle-table row (see [Redundant branches](#redundant-branches)), kept because nothing here reconstructs it — dropping it would lose the information, not save it. Note its energy component carries a sign convention quirk. |
| `mc.p4shw[4]` | no | Total 4-momentum of the final-state hadronic system. Does **not** equal the sum of final-state hadrons in the particle table — likely evaluated pre-FSI, while the particle table is post-FSI. Genuinely distinct. |

## `MC_INTERACTION_VARIABLES`

| Variable | Redundant? | Meaning |
|----------|------------|---------|
| `mc.iaction` | no | Interaction type: `0` = NC, `1` = CC. |
| `mc.inunoosc` | in this file only | PDG code of the neutrino's flavour at production, before oscillation. Equal to `mc.inu` for 100.000% of events in the file checked — the generator applies oscillation as a downstream weight rather than swapping the interacting flavour. Do **not** treat that as general: the two would genuinely differ in a sample where flavours are swapped. |

## `MC_TRUTH_EVENT_VARIABLES` — per-event interaction truth

Each field below was checked to be genuinely non-reconstructable from the
particle table, or else is cheap enough that re-deriving it isn't worth it.

| Variable | Redundant? | Meaning |
|----------|------------|---------|
| `mc.itg` | **yes** — but it's the join key | PDG code of the struck target: `2212`/`2112` for nucleons, a large nucleus code for coherent events, `11` for inverse muon decay. Technically a particle-table duplicate, but kept — it's the *key* needed to find the right row, and it's one cheap scalar. |
| `mc.iresonance` | no | Interaction channel: `1001` QE, `1002` RES, `1003` DIS, `1004` CPP (coherent pion production), `1005` inverse muon decay. Despite the name, this is the channel selector, not just baryon resonances. |
| `mc.istruckq` | no | Struck-quark-related code (DIS only). Only `{0, 1, 2}` observed — too few values for a raw PDG code, so probably a small enumeration. Encoding unconfirmed. **`???`** |
| `mc.iflags` | no | Bitmask of additional interaction flags. Values `{0, 2, 3, 11}` observed. Encoding unconfirmed. **`???`** |
| `mc.x` | no | Bjorken x, range [0, 1]. Equals `-q2 / (2 p_tgt·q)` for QE/RES/DIS; kept because that breaks for coherent and inverse-muon-decay events. |
| `mc.y` | no | Inelasticity y, range [0, 1]. Equals the **invariant** `(p_tgt·q)/(p_tgt·p4neu)` — *not* the naive lab-frame `(Eν−Elep)/Eν`, which disagrees ~93% of the time because it ignores Fermi motion. Kept rather than making every user get that right. |
| `mc.q2` | no | Four-momentum transfer squared. **Negative** (spacelike) here — negate for the usual positive-`Q²` convention. Equals `(p4neu − p4lep)²` for QE/RES/DIS; breaks for coherent + IMD. |
| `mc.w2` | no | Hadronic invariant mass squared `W²` [GeV²]. QE events sit at ≈0.880 = (proton mass)², as expected. Equals `(p_tgt + q)²` for QE/RES/DIS; breaks for coherent (nucleus target). |
| `mc.sigma` | no | Cross section for this interaction. Units and normalisation **unconfirmed** — does not match the textbook CC scaling `σ ≈ 0.67×Eν[GeV] ×10⁻³⁸ cm²`, even per-nucleon. **`???`** |
| `mc.sigmadiff` | no | A differential cross section, plausibly `d²σ/dx dy` (formula unconfirmed). Exactly `0` for precisely the 8 inverse-muon-decay events where `x`/`y` are themselves undefined, which supports the general reading. **`???`** |
| `mc.emfrac` | no | Fraction of hadronic shower energy that is electromagnetic, range [0, 1]. Distinct from a naive post-FSI computation off the particle table (median abs. difference 0.41) — likely evaluated pre-FSI, like `p4shw`. |
| `mc.ndigu` | no | Total digits in the u-view. **Not** a hit count you can rebuild from the hit table: counting hits per view matches only ~3% of the time, and matches no better against either view (2.94–3.07% for all four pairings), so it is not simply a U/V labelling mismatch. |
| `mc.ndigv` | no | Same, v-view. |
| `mc.tphu` | no | Summed pulse height, u-view. Much larger scale than the calibrated per-hit `pe` values, consistent with a pre-calibration quantity. Units unconfirmed. **`???`** |
| `mc.tphv` | no | Same, v-view. |

## `MC_PARTICLE_VARIABLES` — MC truth particle stack

`NtpStRecord/stdhep`: one row per particle, variable length per event.

| Variable | Redundant? | Meaning |
|----------|------------|---------|
| `stdhep.IdHEP` | no | PDG code of the truth particle. |
| `stdhep.IstHEP` | no | HEPEVT/GENIE status code. By convention `1` is a stable final-state particle; `0` initial-state; `11` the struck nucleon. |
| `stdhep.mass` | needs external PDG table | Rest mass [GeV]. A pure function of the PDG code, but recovering it needs an external PDG mass table rather than other columns here — so it stays stored. |
| `stdhep.p4[4]` | no | 4-momentum: `(px, py, pz)` [GeV], then energy [GeV]. |
| `stdhep.vtx[4]` | no | Production 4-position: `(x, y, z)` [m], then time. |

**Gotcha:** every event carries one terminator row with `IstHEP == 999`,
`IdHEP == 0` and a large nonphysical energy. It is generator padding, not a
particle — filter it out before doing particle-level physics.

## Geometry-derived columns

`stp.z` and `stp.planeview` are both **pure functions of `stp.plane`** —
they describe where a plane sits and how it is oriented, not anything about
the hit. `stp.planeview` is requested by `IMAGE_BASIC_VARIABLES` because
`images.py` and `plotting.py` select on it; `stp.z` is not requested by any
collection here, and this is the record of why it does not need to be. Measured on a full Far Detector MC file (14.7 M hits, 484 distinct
planes):

| Column | Result | Cost |
|--------|--------|------|
| `stp.planeview` | 0 of 484 planes carry more than one view. | 1.9 MB, 0.9% |

`stp.z` reduces to a 484-entry lookup (1.9 KB as float32) that reproduces it
bit-exactly. It is also near-affine in two segments, split at the
supermodule gap:

| Segment | Planes | Pitch | Offset | Max residual |
|---------|--------|-------|--------|--------------|
| SM1 | 1–248 | 59.48997 mm | −5.498 mm | 0.048 mm |
| SM2 | 250–485 | 59.42997 mm | 1103.558 mm | 0.052 mm |

A single global fit is useless by comparison (max residual 54.7 cm) — the
gap between supermodules shows up as one 1.213 m step from plane 248 to 250,
against a ~59 mm normal pitch. Note the two supermodules have *slightly*
different pitches, so the formula is accurate to ~0.05 mm but not exact; use
the lookup where exactness matters.

`stp.planeview` follows plane parity, with the sense **inverted** between
supermodules:

| Segment | Even planes | Odd planes |
|---------|-------------|------------|
| SM1 (1–248) | view `2` | view `3` |
| SM2 (250–485) | view `3` | view `2` |

The flip is a numbering artefact, not physics: plane 249 is absent from the
file, so the physical U/V alternation continues across the gap while the
parity of the plane number does not.

**Caveats.** All of the above is measured on one Far Detector file. The Near
Detector has a different plane count, partial scintillator coverage and its
own view arrangement, so both the lookup and the parity rule are
detector-specific — re-derive them before applying to ND data. The 484 (not
485) planes also mean a lookup built from data alone has a hole at plane
249; a complete table needs the detector geometry, not just an observed file.

Neither column is dropped from any collection here, for the same reason as
the fields below: this package has no mechanism to reconstruct them, so
dropping would lose information rather than save it. They are prime
candidates for a storage format that keeps a geometry table alongside the
hits.

## Redundant branches

The `mc.*` fields below are exact duplicates of a row in the particle table,
verified row-by-row across every event by `minos_data_storage`'s
`validate_redundancy.py`.

**None of them are dropped from any collection here, and nothing in this
package reconstructs them.** This is a record of what duplicates what, not a
mechanism. It's written down so that anyone later dropping one — or reading a
storage format that already did — knows the join instead of re-deriving it.

| Field | Recover from the particle table by |
|-------|------------------------------------|
| `mc.p4neu[4]` | The row with `pdg == mc.inu`, `status == 0`. |
| `mc.p4tgt[4]` | `pdg == mc.itg`, `status == 11` (QE/RES/DIS); else `status == 0` (coherent nucleus, or the inverse-muon-decay electron). |
| `mc.vtxx`, `mc.vtxy`, `mc.vtxz` | `vtx[:3]` of the same row `p4neu` uses. |
| `mc.a`, `mc.z` | Decoded from the nucleus row's PDG code (`pdg > 1e9`, `status == 0`): `a = (pdg // 1e6) % 1000`, `z = (pdg // 1e3) % 1000`. Falls back to hydrogen (`a=1, z=1`) when no nucleus row exists. |
| `mc.p4mu1[4]`, `mc.p4mu2[4]` | See the lepton rule below, with `\|pdg\| == 13`. |
| `mc.p4el1[4]`, `mc.p4el2[4]` | Same rule, `\|pdg\| == 11`. |
| `mc.p4tau[4]` | Same rule, `\|pdg\| == 15`. Never exercised — no ντ events in any file checked. |

### The lepton rule

Among rows with the matching `|pdg|` and `status == 1`, find the one whose
momentum `(px, py, pz)` matches the `mc.*` field — momentum is never
sign-flipped, so it is an unambiguous key. That row's **energy is negated iff
its own `pdg` is positive** (e.g. `+13`, the μ⁻), a documented MINOS
convention (`NuEvent.h`: `p4mu1[3];//not proper p4: muon energy (+/- !!!)`).

This is **not** "the first matching row in stack order". That rule looked
correct on a hand-picked sample and is wrong in general — stack order does
not reliably correspond to the mu1/mu2 slot, and the sign flip follows
whichever slot the matter lepton lands in. Worth stating plainly, since it
was already gotten wrong once.
