# Organic Scanning technical specification

This document specifies Organic Scanning (exobiology): what it predicts, the rules behind the prediction, how scan progress is tracked, and the cases in which the prediction can be wrong. Usage is described in the [Exobiology guide](guide/exobiology.md). The general code organization is described in [TECHNICAL.md](TECHNICAL.md).

- **Author:** R.W. Harper (CMDR Mactavious)

WFMT is journal-first: it uses the information the game writes to its journal files and fills gaps from Frontier data or community services where they exist. Each gap and its workaround is documented. See [the design principle in TECHNICAL.md](TECHNICAL.md).

## 1. Scope

- From the biological signals on a planet, list the candidate species of each genus using the planet's conditions.
- Track Log, Sample and Analyse progress per organism (the game's spelling of the stages) and report when the distance from the last sample is sufficient for the next sample to count. <!-- game spelling -->
- Show the credit value of each species.
- Retain a body's biology across a relog or an EDMC restart.
- Supply the Exobiology overlay cards (section 11): a per-body view of genera, predicted and confirmed species, sample positions and the way back to plants the commander identified.

### 1.1 Not included

- **No network access and no submission.** The feature is local and read-only. It submits no codex or biology data.
- **No first-discovery bonus.** Exobiology analysis pays a flat value per species. The only multiplier shown is the first footfall bonus (five times the value for the first commander on a body, from `WasFootfalled` of the body), which is a property of the body.
- **No certainty before a sample.** Until a scan names the species, the result is a list of candidates.

## 2. Architecture

All modules are in `plugin/`. `PANEL_PLACEMENT = "exploration"`.

| Module | Role |
|---|---|
| `organic_scan.py` | Pure logic: `BodyConditions`, the matching rules, scan-stage tracking, distance. No screen code and no EDMC imports beyond the logger. |
| `organic_scan_state.py` | Per-commander persistence of each body's biology (`organic_scan_state.json`). |
| `exo_observations.py` | Global record of conditions against confirmed species, for checking the prediction (`exo_observations.json`). |
| `exo_analysis.py` | Pure analysis of that record (hit rate, misses, ranges, species found together). |
| `exo_review_window.py` | The Prediction review window: the analysis, with a manual review of each find. |
| `organic_catchup.py` | Reads the last 14 days of journals for samples and bodies seen while EDMC was closed and merges them into the saved state (section 6). |
| `organic_scan_panel.py` | The panel: reads journal events, builds conditions, shows predictions and progress, builds the overlay view. |
| `organic_species_data.py` | Generated reference data: genera, species, values and habitability rulesets. |
| `organic_region_data.py` | Generated reference data: the galactic region grid and the named zones. |
| `organic_variant_data.py` | Generated reference data: the color rules (section 4, Color variants). |
| `exobiology_overlay.py` | The overlay cards: bio status, biology and sample popup. The radar is drawn through `exo_radar.py`. |
| `exo_radar.py` | Geometry of the Bio radar (offsets, bearings, circles, pointers) and its drawing. |

## 3. Inputs

| Source | Data used |
|---|---|
| `Scan` (body) | Planet class, atmosphere type and trace gases, surface gravity, temperature, pressure, volcanism, landable status; `WasFootfalled` (false means no one has set foot there, so the first footfall bonus is open) |
| `Scan` (stars) and the arrival system | The main star type of the system |
| `FSSBodySignals`, `SAASignalsFound` | Genera present on a body and the count of biological signals |
| `ScanOrganic` | Genus and species named at each stage (Log, Sample, Analyse); the color variant (`Variant_Localised`); with the position from `Status.json` at that moment, where each Log and Sample was taken |
| `FSDJump`, `Location` | `StarPos` of the system (light years), for the region lookup |
| `Status.json` | Surface latitude, longitude, heading and planet radius (sample-distance check and radar); the nearby body (`BodyName`; absent after leaving it); `Flags` and `Flags2` (scan mode) |
| `CodexEntry` (organic structures) | Plant name, latitude and longitude, kept as a waypoint |
| `Touchdown`, `Liftoff`, `LaunchSRV`, `DockSRV`, `Disembark`, `Embark` | Where the ship touched down and where the SRV was launched or left |

Gravity is converted from m/s² to G and pressure from pascals to atmospheres, to match the units of the data.

## 4. Species prediction

For each genus detected on a body, every species of that genus is checked. A species has one or more rulesets (alternative sets of conditions). The species is a candidate if any one ruleset matches. A ruleset matches only if every condition it states is satisfied. The conditions are:

- atmosphere type, planet class, and ranges for gravity, temperature and pressure;
- the star type, and a specific system where the data names one;
- volcanism required, forbidden, or of a named kind;
- the galactic region (lists of allowed and excluded region groups);
- Guardian proximity (within range of a known Guardian nebula or site);
- a trace gas above a given percentage;
- the tuber zone distance band (for the species that depend on it);
- a co-located body of a named type in the system.

**Region lookup.** The `StarPos` of the system is converted to a grid cell and looked up in a compact table of the game's 42 named regions. No network call is made.

**Unknown values.** If a value is not yet known (no position seen in the session, no other bodies scanned), the condition is skipped and does not exclude the species. A species can therefore appear as a candidate more often than the game allows, but a real candidate is never hidden. Conditions that appear in the data but are not evaluated (orbital period, parent star, the body's own distance requirement) have the same effect.

Candidates carry no likelihood, because the data lists the species that the conditions of a body allow and not their frequency.

- The overlay percentages are an equal share (100 divided by the number of candidates).
- The value range of an open genus is the lowest and highest value among its candidates.
- A body holds at most one species per genus, so the result is a list per genus.
- A species with no usable rules in the data cannot be predicted and is never listed.

**Approximation.** The star type used is the main (arrival) star of the system. For a body that orbits a secondary star in a multi-star system, this can be incorrect.

### Color variants

`organic_scan.predict_variants(species, cond)` returns the color a species takes on the body, from the rules in `organic_variant_data.py` (generated by `scripts/gen_organic_variants.py`; source and license: see docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md).

- A genus or species follows the class of the star that the body orbits (`star_class`: O to M, L, T, Y, TTS, Ae, W, D, N), or a surface material listed in the `Scan` of the body (`BodyConditions.materials`), or has one fixed color. A color can also require a kind of body.
- The rule of a species takes precedence over the rule of its genus. The plants (Brain Trees, Anemones, Sinuous Tubers) have no rule.
- The star is the main star of the system, as in the rest of the prediction.
- `GenusView.variant_hint` carries the result for the Biology card when all candidates agree and no sample has named the color yet.
- `scripts/verify_organic_variants.py` checks the predictions against a commander's journals.

## 5. Scan progress and distance

A scan has three stages: Log (first sample), Sample (second sample, far enough from the first) and Analyse (third sample, far enough from the second). The third stage pays out. <!-- game spelling -->

- A `ScanOrganic` event confirms the exact species (replacing the candidate list), sets its value and advances the stage.
- Each genus has a minimum distance between samples, which varies by genus. WFMT measures the distance from the last sample as great-circle distance on the radius of the body and reports when it is sufficient.
- Sampling a different genus abandons a scan left part-way (the game requires it to be restarted), so its stage and positions are cleared. A new first sample of the same genus also restarts it.
- The credit estimate is the value of the species from the data.

## 6. Persistence

Data is stored per commander in `organic_scan_state.json` (in the plugin folder, listed in the protected files of the updater):

- Each body's conditions, the genera detected, and each organism's confirmed species and progress.
- Per body: where each sample was taken, the color variant, the first footfall flag and the plant waypoints.

Reasons:

- The biology of a planet persists across logout, and a relog starts a new journal file that does not replay earlier scan events.
- Moving to a different body resets the live tracker, and returning restores the saved progress.
- When `Status.json` names no body (the commander has left the planet), the live view is cleared in the same way, so the overlay cards stop showing a finished planet.

### 6.1 Samples and bodies seen while EDMC was closed

EDMC passes to a plugin only the events that occur while it runs, so a sample taken while it was closed does not reach the tracker.

- Each time a commander is seen at start-up, a worker thread reads that commander's journals from the last `organic_catchup.CATCH_UP_DAYS` (14) days.
- It raises the saved stage of any species logged, sampled or analyzed in that period. The merge only raises a stage (Log 1, Sample 2, Analyse 3), so reading the same events again changes nothing.
- A `ScanOrganic` names its body only by number. The name is taken from the `Scan`, `FSSBodySignals`, `SAASignalsFound` and `ApproachBody` events that name the same body in the same system. A sample whose body cannot be named is skipped.
- For a body scanned while EDMC was closed, the conditions (from the `Scan`), the genera named by its signals and the first footfall flag are also recovered, but only where nothing is saved for that body.
- Positions are not recovered, because the journal does not record them. Scans older than 14 days are not found. The journals are only read.

### 6.2 Observations for checking the prediction

`exo_observations.json` is kept in the plugin folder (protected from updates). It is global and not per commander, unlike every other file about play: it holds facts about bodies and what grows on them, pools the finds of every commander on the installation, and stores no commander name.

Contents:

- Each `ScanOrganic` writes one record per body: the conditions (`planet_class`, `atmosphere`, `atmosphere_components`, `gravity_g`, `temperature_k`, `pressure_atm`, `volcanism`, `star_type`, `materials`, `system_body_types`, `galactic_position`), the genera named by the signals of the body, and for each genus the confirmed species, the color variant, the time first seen, and `predicted` (the species keys the prediction listed at that moment).
- A body seen by two commanders is one record.
- Bodies sampled before the file existed are filled in from each commander's saved per-body state as that commander is seen, and are marked `"source": "backfill"`. Their `predicted` value is the current rules applied to the saved conditions.

Analysis script:

```
python scripts/analyze_exo_observations.py [file]
```

The script prints the hit rate by genus, each find that the rules did not list together with its conditions, where each species was found, the observed temperature, gravity and pressure against the range of the rules, and the species found together on a body.

Switch:

- Recording is on by default (`wfmt_exo_observations_enabled`). It is switched on or off on the Settings strip at the top of the Prediction review window, which also has **Clear the record...**. The Settings → Exploration → Organic Scanning tab refers to that window.
- When recording is off, nothing is recorded and no earlier state is backfilled.

Prediction review window:

- The window (`exo_review_window.py`) presents the analysis of `exo_analysis.py`. It is opened with **Review** on the Organic Scanning panel.
- The Finds tab has a filter, the conditions of each find and the species the prediction listed, and a review status (Needs a rule change, Bad data or journal quirk, Expected, no change, Look at again later) with a note. The review is saved on the find as `review` in the same file and is kept when the species is sampled again.
- Further tabs: By genus, Ranges and Together.
- **Copy report** copies the analysis as text.
- A review does not change the prediction.

## 7. Reference data

`organic_species_data.py` and `organic_region_data.py` are generated files and are not edited by hand. They contain a table of genera, species, values and rulesets, and the region grid with the Guardian and tuber zones. They are a snapshot of community-measured game data (credited in `THIRD-PARTY-NOTICES.md`). A species added by a game update requires the tables to be regenerated; until then it cannot be predicted.

## 8. Tests

- `tests/test_organic_scan.py`: the pure logic in `organic_scan.py` (matching rules, region and zone handling, scan stages and distances) without EDMC.
- `tests/exobiology_checks.py` (run by `tests/test_exobiology_overlay.py` in its own process): overlay cards, radar geometry, pointers, waypoints and the per-body view built from journal events and `Status.json`.
- `tests/test_organic_catchup.py`: the catch-up from journals (stages only rise, a body named from other events, nothing saved is overwritten).
- `tests/test_exo_observations.py`: the observation record and its analysis.
- The panel itself is not covered by an automated test.

## 9. Known gaps

- Predictions are candidates until a sample names the species.
- The main star is assumed to be the illuminating star.
- Some rules in the data are not evaluated (section 4).
- A new species requires the data to be regenerated.
- The position of a plant is known only from the codex entry of the Composition Scanner. Genera whose codex names do not follow the usual pattern (such as Bark Mound) are not tracked.
- The color variant is predicted only for genera whose color follows the star class or a surface material, from the main star. The plants (Brain Trees, Anemones, Sinuous Tubers) are not predicted. Their color is reported once a sample or the Composition Scanner names it.
- The position of the SRV is the position of the commander when the SRV was launched or left, not a reading of the SRV.

`organic_scan.display_species` writes a species as a scientific name: genus capitalized, species epithet in lower case, a color variant after a dash unchanged, and the game's common names such as Bark Mound unchanged. The per-body view, the sample popup, the Composition Scanner footer and the panel use it. Stored names remain as the game wrote them.

## 10. The overlay view

`organic_scan_panel.overlay_view()` builds an `organic_scan.BodyView` from the state of the controller without widgets.

Contents of the view for the body where the commander is:

- Each genus (`GenusView`): predicted candidates with values, the confirmed species and variant, the stage, the sample positions and the distance from the last sample.
- The first footfall flag, the biological signal count, the commander's position and heading, the ship and SRV positions, and the genus in progress.
- The plants identified and not yet sampled (`Waypoint`s of every genus, oldest first; `exo_radar.tracked` selects the latest of each genus).

Use of the view:

- The cards in `exobiology_overlay.py` are built from it.
- `exo_radar.py` converts positions to pixels with a flat-earth offset rotated to the heading.
- The genus of a codex name is determined by `organic_scan.genus_key_for_codex_name`.
- Each genus keeps `WAYPOINTS_PER_GENUS` (4) plants.

Waypoint accuracy:

- The Composition Scanner names a plant from a distance (from a ship or SRV, a long distance), and the journal gives the position of the commander, not of the plant.
- A waypoint therefore records the commander's mode (`organic_scan.scan_mode`, from `Flags` and `Flags2` of `Status.json`: `foot`, `srv`, `ship`, or unknown) and the possible error (`WAYPOINT_ERROR_M`: 40, 150, 250 and 150 m respectively; the source comment describes these as estimates).
- The radar draws its ring with that width. Distances are prefixed with `~` unless the plant was scanned on foot.

Matching a sample to a waypoint:

- A Log or Sample removes the waypoint of its genus nearest to the commander within `WAYPOINT_MATCH_M` for that mode (100, 300, 450 and 250 m), plus `WAYPOINT_SAME_VARIANT_EXTRA_M` (50 m) when the sample names the same color variant.
- With no position available, the plant identified last is removed.
- The mode is saved with the waypoint as a fifth element, which is absent in older saves.
