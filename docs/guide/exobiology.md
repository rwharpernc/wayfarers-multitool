# Exobiology

This guide covers the exobiology features of WFMT (sampling of plants and organisms on planetary surfaces): the **Organic Scanning** panel in Exploration mode, the four overlay cards, the markers that lead back to an identified plant, and the first footfall bonus.

**Data sources**

- Scans, signals, Codex entries and samples come from the journal.
- Position, heading and the nearby body come from the game's `Status.json`.
- Information the game does not provide is predicted and marked as a prediction: the species a planet hosts before sampling, and the color variant before the first sample (where the game's rules for it are known).
- No exobiology feature contacts the internet.

**Contents:** [How to](#how-to) · [Worked examples](#worked-examples) · [The pieces](#the-pieces) · [Organic Scanning panel](#organic-scanning-panel) · [The overlay cards](#the-overlay-cards) · [Finding your way back to a plant](#finding-your-way-back-to-a-plant) · [First footfall](#first-footfall) · [When the cards reset](#when-the-cards-reset) · [Setting up](#setting-up) · [What the game does and doesn't tell us, and how to work around it](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it) · [What WFMT keeps to improve the prediction](#what-wfmt-keeps-to-improve-the-prediction)

## How to

Each task list links to the section with the details. The [worked examples](#worked-examples) show the resulting displays.

### Switch the panel and the cards on

1. The **Organic Scanning** panel is on by default. If it is missing from Exploration mode, open **Settings → WFMT → Exploration → Organic Scanning** and tick **Show predicted species and scan progress**.
2. In EDMC's main window the **Organic Scanning** section starts folded. Click **Organic Scanning** to open it. It stays open until EDMC restarts.
3. Set up an overlay ([WFMT's built-in overlay on Windows, or EDMCModernOverlay](../OVERLAY_SETUP.md)).
4. Open **Settings → WFMT → Overlays → Exobiology** and tick the cards to show: Bio status, Biology, Bio radar and Sample popup. All four are off by default.
5. Press **Test Cards**. It draws a made-up body on all four cards, including cards that are off, and reports whether an overlay could be reached.

### Place the cards

1. Open **Settings → WFMT → Overlays → Overlay Placement**.
2. Drag each card to the wanted position in the layout editor. Bio status is a wide, short strip that starts at the top center, above the game's compass.
3. Adjust the radar under **Settings → WFMT → Overlays → Exobiology** with **Radar size**, **Circle fill** and **Circle outline**.

See [Setting up](#setting-up).

### Sample a plant from start to finish

1. Fly to a planet with biological signals and map it with the Detailed Surface Scanner. The mapping scan names the genera.
2. Land or fly low. The `Predicted species` lines in the panel and the Biology card list the candidate species of each genus and what they pay.
3. Take the first scan with the Genetic Sampler (**Log**). The Bio status card shows the species with the first of three circles filled.
4. Move away from the plant. The distance line on Bio status (`Move 122 m further: 78 m of 200 m`) reads `Clear` when the distance is sufficient.
5. Take the second scan (**Sample**) on another plant of the same species. Move away again and take the third scan (**Analyse**).
6. After the third scan the genus is marked `Done`, and the Sample popup shows the species and its payout.

### Find a plant again

1. Scan the plant with the Composition Scanner. WFMT records the position of the scan.
2. Open the Bio radar and Bio status. Each tracked plant has a line with its distance and direction (`Tussock: ~210 m, 30° right`).
3. Turn until the pointer beside the plant points straight up, and move in that direction.
4. At the plant's ring, search inside the ring. The `~` marks a position as exact as the scan distance allows.
5. Sample the plant. The sample makes its position exact.

See [Finding your way back to a plant](#finding-your-way-back-to-a-plant).

### Review the predictions

1. Sample species. Each sample that names a species adds a line to the record.
2. In Exploration mode, press **Review** on the Organic Scanning panel.
3. On the **Finds** tab, select a filter in the **Show** box (for example *Not on the predicted list*) and select a find to see the body's conditions and the listed species.
4. Select a **Review**, enter a **Note** and press **Save review**.
5. Press **Copy report** to copy the full report as text.

See [The Prediction review window](#the-prediction-review-window).

## Worked examples

The values below are illustrative. The wording on the cards is the wording WFMT produces.

### Example 1: three samples of one genus

A mapped body has four biological signals and no samples have been taken. A Tussock is the first plant reached.

1. **Before the first sample.** Bio status reads `0 of 4 analyzed` with an empty progress bar and lists each genus with the distance it requires (`Tussock    200 m apart`). Its foot reads `Use the Composition Scanner on a plant to begin`. The Biology card lists each genus with its candidate species and the range they could pay.
2. **First scan (Log).** Bio status shows the species in large type (`Tussock pennatis - Lime`) with one of three circles filled and the payout at the right of that row. Below it: `Move 200 m further: 0 m of 200 m`. The progress bar has advanced by a third of a genus. The Bio radar shows a circle around the sample position, red while the commander is inside it. The Organic Scanning panel reads `Tussock pennatis: Log (1/3)`.
3. **Moving away.** The distance line counts up (`Move 122 m further: 78 m of 200 m`). In the panel the line ends with `- move further away`. The radar circle stays at the sample position.
4. **Clear.** At 200 m the line reads `Clear: 210 m from the last sample, 200 m needed`, the radar circle turns green, and the panel adds `- next sample ready`.
5. **Second scan (Sample).** Two circles are filled. The Sample popup shows the species, **Estimated value**, **Colony range** (200 m) and `Sampled` at the foot, for ten seconds. The distance line restarts from the new position.
6. **Third scan (Analyse).** All three circles are filled. The popup reads `Analyzed`, the panel shows the payout, Bio status reads `1 of 4 analyzed`, and the genus is `Done` on the cards. The Biology footer retains the body's total.

### Example 2: a first footfall

The commander is the first to land on a body that has life.

1. In the system scan the body shows `First footfall` on **Body info**, and **System targets** marks it `0/3 life FF`.
2. Before sampling, the Bio status foot reads `First footfall: every reward here is five times as much`.
3. Once a genus is open, its reward carries the marker (`1.0M - 5.3M CR  ·  FF 5x`). The figures are already multiplied by five.
4. On the Biology card the footer shows the range and, on its own line, the range with the bonus (`Rewards: 7.6M - 11.9M CR` and `First footfall (5x): 38.2M - 59.6M CR`).
5. The Sample popup shows the value with `(FF bonus)`.
6. When all samples are analyzed, Bio status reads `All samples analyzed: first footfall paid five times`.

A later scan that reports the body as footfalled does not remove the flag. The flag is kept once seen.

### Example 3: switching genus part-way

A Bacterium is at `Sample (2/3)`. A Frutexa nearby is sampled.

1. The Frutexa becomes the active genus on Bio status, with its first circle filled.
2. The unfinished Bacterium is abandoned. The game requires a genus to be started over when a different genus is sampled before it is finished; WFMT does the same and resets its count to zero.
3. The next Bacterium scan is a new Log, shown as `Log (1/3)`. The distance is measured from the new sample.
4. A genus already analyzed is not affected and stays `Done`.

Sampling a different genus abandons an unfinished one.

### Example 4: finding an identified plant

A Tussock was scanned with the Composition Scanner from an SRV, and the commander then drove away to sample a Bacterium.

1. Bio status carries a line for the Tussock at the right (`Tussock: ~210 m, 30° right`). The `~` appears because an SRV scan can be about 150 m off.
2. The Bio radar shows a ring with the letter for Tussock and a line from the commander toward it, and lists `Tussock ~210 m` under the plot with a pointer showing the direction.
3. Approaching the plant, the line can change to `ahead`. The plant is inside the ring.
4. Taking the Log within reach of the marker drops the marker, and the plant's position becomes exact.
5. A second Tussock identified earlier becomes the next marker. If there is none, the line is removed.

### Example 5: after selling the data

1. Leaving the planet clears the cards. The samples are kept for the body and return if the commander returns.
2. If an expedition is running, the [Expedition Log](exploration.md#expedition-log) counts the sale. It keeps a tally of the exobiology earnings and an estimate of the unsold exobiology data.
3. To count a trip from this point, start an expedition from the last **Exobiology Data sale** in the Expedition window (see [Starting and managing an expedition](exploration.md#starting-and-managing-an-expedition)). It begins just after that sale and fills in from the journals.

## The pieces

| Piece | Where | What it does |
|---|---|---|
| **Organic Scanning panel** | Exploration mode | Predicts the species of each signal, tracks Log, Sample and Analyse, and reports whether the distance to the last sample is sufficient |
| **Bio status** card | Overlay | Progress, the species and color variant being sampled with three circles, the reward, and the distance to the last sample |
| **Biology** card | Overlay | Each genus on the body with the species it could be (or is) and what each pays |
| **Bio radar** | Overlay | A top-down plot of the sample circles, the ship, the SRV and the tracked plants, with direction pointers |
| **Sample popup** | Overlay | For a few seconds after each sample: the species and its payout |
| **Exploration Dashboard, Surface tab** | Window | The same exobiology information in a window: each genus, its possible species and pay, the distance to the last sample, the tracked plants and the body's conditions ([Exploration Dashboard](exploration.md#exploration-dashboard)) |

The overlay pieces require an overlay ([WFMT's built-in overlay on Windows, or EDMCModernOverlay](../OVERLAY_SETUP.md)) and are off until ticked. They use the prediction and sample tracking of the Organic Scanning panel, so the cards and the panel show the same data.

## Organic Scanning panel

The panel predicts the species of each biological signal on a planet and tracks sampling progress.

1. Detect biological signals on a body (the system scan gives the count) and map it. The mapping scan names the genera.
2. WFMT lists the candidate species of each genus, based on the planet's atmosphere, gravity, temperature, pressure, volcanism, its star, the region of the galaxy and other data, with an estimated credit value.
3. When sampling starts, WFMT tracks progress (Log, Sample, Analyse) and reports whether the distance from the last sample is sufficient for the next sample to count.

**Contents of the section.** The section is in Exploration mode and starts folded (click **Organic Scanning** to open it; it stays open until EDMC restarts).

- **`Predicted species: (land on a body with biological signals)`** is shown until the commander is on a body that has biological signals. On such a body that has been scanned, the line reads `Predicted species (<body>):`, followed by one line for each genus:
  - `Tussock: Tussock pennatis (~1,000,000 cr)` when one species fits;
  - `Bacterium: Bacterium aurasus, Bacterium nebulus` when several species fit;
  - `<genus>: unknown` when the body's conditions match no rule.
  - Until the body's scan arrives the line reads `waiting on body scan data...`.
- **`Active scan`** is hidden until sampling starts. It then shows one line for each organism in progress (`Tussock pennatis: Sample (2/3)`). `(~1,000,000 cr)` is added once the organism is analyzed, and ` - next sample ready` or ` - move further away` is added while moving between samples. The stages are Log, Sample and Analyse, counted out of three.
- **Review** opens the [Prediction review window](#the-prediction-review-window).

**Procedure**

1. Fly to a planet with biological signals (the system scan or the FSS gives the count). Map it with the Detailed Surface Scanner. The mapping scan names the genera.
2. Land or fly low. Read the `Predicted species` lines.
3. Optionally scan a plant from a distance with the Composition Scanner to identify it. WFMT records its position so the cards can lead back to it ([Finding your way back to a plant](#finding-your-way-back-to-a-plant)). The first scan of an organism with the Genetic Sampler is the **Log**; the `Active scan` line starts.
4. Take the second (**Sample**) and third (**Analyse**) scans of the same species, each at least the genus's minimum distance from the previous one. The `Active scan` line reads `next sample ready` when the distance is sufficient and `move further away` otherwise.
5. After the third scan the organism shows its payout and the cards mark the genus `Done`.

The section is switched off under **Settings → WFMT → Exploration → Organic Scanning** (**Show predicted species and scan progress**, on by default). It uses only the journal, makes no internet connection and submits nothing. The prediction rules are documented in the [specification](../ORGANIC_SCANNING_TECH_SPEC.md).

## The overlay cards

Four cards show the body the commander is on, in the ship, the SRV or on foot. Each card has its own switch under **Settings → WFMT → Overlays → Exobiology** and its own entry on **Overlay Placement**.

**Name format**

- Species are written as scientific names: the genus with a capital and the species in lower case (`Tussock pennatis`, `Bacterium aurasus`). The game writes both words with capitals.
- A color variant keeps its capital (`Tussock pennatis - Lime`).
- The game's common names (Bark Mound, Brain Tree, Amphora Plant and similar) are written as the game writes them.
- The overlay draws plain text, so names are not italicized.

### Bio status

Position: top center. The card is a short, wide strip, placed above the game's compass.

- The heading is *Biological signals*, with the count of analyzed genera (`1 of 4 analyzed`) and a progress bar. The bar advances by a third of a genus with each Log or Sample, and completely once the genus is analyzed.
- While a genus is being sampled the card shows:
  - the species and color variant in large type, with three circles (filled as each sample is taken);
  - the species' payout at the right end of that row (five times as much on a first footfall, marked `FF 5x`);
  - the distance from the last sample against the distance the genus requires (`Move 122 m further: 78 m of 200 m`, or `Clear: 210 m from the last sample, 200 m needed` once the next sample can be taken). The strip is 108 characters wide; the distance line joins the species row beside the reward when it fits, and otherwise occupies a row of its own.
- With nothing in progress, the card lists each genus with the distance it requires between samples, and `Done` once analyzed.
- A plant identified with the Composition Scanner is named at the foot until it is sampled.
- On a body that has not been mapped, the card reads `Map this body with the surface scanner to learn what lives here`, with the number of signals.
- While sampling, if WFMT has no position for the commander or for the last sample (for example a Log recorded without a position), the distance line reads `Samples must be 200 m apart`.
- With nothing in progress, the foot reads `Use the Composition Scanner on a plant to begin`, `First footfall: every reward here is five times as much` on an untouched body, or `All samples analyzed` when all genera are done.

### Biology

Position: bottom, left of center. The heading is `Bio signals <body>` with `1 of 4 done` at the right. The card lists every genus on the body with the species it could be, or is once a sample has named it (with its color variant), and what it pays. A genus with no usable prediction reads `unknown`.

- Before a sample names the color, a genus whose colors follow the **star** the body orbits or a **surface material** shows `Likely color: Emerald` under its row (or `Lime or White` when more than one material fits).
- While the species is open, the genus shows the **range** it could pay (`1.0M - 5.3M CR`), and each candidate species has its own indented row with its value and a percentage (`5.3M CR  ~50%`) at the right. A genus with more than five candidates shows the five that pay most and counts the rest (`+2 more`). On a crowded body each genus is one row with its range. A single likely species has a `~` before its value.
- The footer is the range the whole body could pay (`Rewards: 7.6M - 11.9M CR`). With a first footfall, the larger figure is on its own line (`First footfall (5x): 38.2M - 59.6M CR`).
- Analyzed species are drawn in the good color.
- The percentages are an even share. The data lists which species the body's conditions allow and gives no frequency for each species, so two candidates each show about 50%. The percentage counts candidates and is not a probability.

### Bio radar

A top-down plot centered on the commander, with straight ahead at the top.

- A small arrowhead with an **N** on its edge shows the direction of north. The plot rotates with the commander's heading.
- Each sample has a circle as wide as the genus's minimum distance between samples: **red** while the commander is inside it (too close for the next sample), **green** once clear.
- The ship (where it touched down) and the SRV (where it was launched or left) are marked `S` and `V`.
- Under the plot are the distances to the ship, the SRV and the first two samples. Each has a **pointer** before it, rotated to show its direction relative to the commander's heading (straight up means straight ahead).
- **Circle sizes**
  - The scale adapts so that the center of every circle fits.
  - Circles are drawn within a fixed size range (a radius of about 5% to 16% of the plot's width).
  - A circle's size is therefore not to scale, while its position is. Circles that appear to overlap may not overlap.
- **Settings** (**Settings → WFMT → Overlays → Exobiology**):

  | Setting | Meaning | Range | Default |
  |---|---|---|---|
  | **Radar size** | Plot width and height in pixels. 520 is twice the default and draws every sample circle larger | 200 to 800 | 260 |
  | **Circle fill** | Opacity of a circle while the commander is inside it, in percent (0 is an outline only) | 0 to 100 | 70 |
  | **Circle outline** | Outline thickness in pixels | 1 to 6 | 2 |

- **Extent.** The plot shows a radius of at least 150 m and at most 3 km around the commander. Up to 12 sample circles and 5 tracked plants are drawn.

### Sample popup

For ten seconds after each sample, the popup shows:

- the species and variant as its heading;
- **Estimated value**, in credits (five times as much on a first footfall, marked `(FF bonus)`);
- **Colony range**, the distance the genus requires between samples;
- at the foot, whether the sample was **Logged**, **Sampled** or **Analyzed**.

## Finding your way back to a plant

When a plant is identified with the Composition Scanner, WFMT records its position (the journal gives the latitude and longitude).

- One plant is followed for each identified genus: the most recent plant of that genus that has not been sampled. Identifying a Tussock, a Bacterium and a Frutexa gives three pointers at once.
- Up to four plants of a genus are kept for the body. The list is kept across EDMC restarts.
- Bark Mound and a few other genera whose Codex names do not follow the usual pattern are not tracked.

### Where the pointers show

- The **Bio radar** marks each tracked plant with a ring and the genus's letter and draws a line from the commander toward it. It lists the plant under the plot (`Tussock 94 m`) with a **pointer** rotated to show the direction.
- Each genus has its own color, used for its ring, line, row and its line on Bio status.
- **Bio status** has a line for each plant with the distance and direction (`Tussock: 94 m, 60° right`). The lines sit side by side in one row, each in its genus's color. The text is `ahead` or `behind` when the plant is nearly straight ahead or behind.

### Accuracy of a marker

The journal records the commander's position at the time of the Composition Scan, not the plant's position. A marker is therefore only as exact as the distance of the scan.

| Scanned from | Estimated error |
|---|---|
| On foot | 40 m |
| SRV | 150 m |
| Ship | 250 m |

WFMT records which of the three applied, draws the marker's ring as wide as the estimated error, and writes the distance with a `~` (`Tussock: ~210 m, 30° right`) unless the scan was made on foot. The plant is inside the ring. Sampling the plant makes its position exact.

### Removal of a pointer

- A Log or Sample taken at a plant drops the nearest marker of that genus when the commander is within its reach:
  - 100 m for an on-foot marker;
  - 300 m for an SRV marker;
  - 450 m for a ship marker (50 m more when the sample names the same color variant).
- The next marker is the next most recent plant of that genus that was identified, or none if there is no other.
- Analyzing a genus clears all of its pointers, wherever the analysis was done.

## First footfall

The first commander to set foot on a body is paid **five times** the usual exobiology reward there. The body's scan reports whether anyone has (`WasFootfalled`), and WFMT shows it:

- **Bio status** and **Biology** mark the reward (`first footfall bonus`), and the Biology footer shows the range the body could pay with the bonus.
- **Body info** flags the body (`First footfall`) and adds a row stating that exobiology pays five times there when the body has life.
- **System targets** marks a body with life where the first footfall is open (`0/3 life FF`).

The flag is kept once seen, because a scan made after the commander has landed reports the body as footfalled while the bonus still applies to the commander.

A body scanned long ago can show as footfalled if another commander has landed since. The flag is an indication; the in-game body information is authoritative.

## When the cards reset

- **Leaving the planet** clears the Exobiology cards, because the game stops naming a body once the commander is away from it. Samples are kept for the body and return when the commander returns.
- The cards are also hidden in hyperspace, while docked, when the game is closed or at its main menu (including while another commander signs in). A different commander loading in starts with a clean state.
- **System targets** and **Body info** move on to the next body to map or sample. A body leaves System targets when it is mapped or its last organism is analyzed. Body info does not hold a targeted body that is finished (see [System targets and Body info](exploration.md#system-targets-and-body-info)).
- After a relog or an EDMC restart the cards are rebuilt from the journals, reading back through earlier journals of the same commander while the commander stayed in the system.

## Setting up

1. Set up the [overlay](../OVERLAY_SETUP.md).
2. Open **Settings → WFMT → Overlays → Exobiology**, tick the cards and press **Test Cards**. The four ticks are:
   - *Enable the Bio status card (progress, current species, distance to the last sample)*
   - *Enable the Biology card (predicted species and what they pay)*
   - *Enable the Bio radar (samples, their circles, your ship and SRV)*
   - *Enable the Sample popup (a few seconds after each sample)*

   All four are off by default. **Test Cards** draws a made-up body (a Tussock being sampled, with a first footfall) on all four cards, works while they are off, and reports whether an overlay could be reached.
3. Open **Settings → WFMT → Overlays → Overlay Placement** and drag each card to the wanted position. The default positions are the top center (Bio status), the bottom center left of the Body info card (Biology), the left middle (Bio radar) and above Biology (Sample popup).

Text size and colors follow **Settings → WFMT → Overlays → Appearance**.

## What the game does and doesn't tell us, and how to work around it

| Information | What the game provides | Workaround |
|---|---|---|
| The species before the body is mapped | The scan gives only the number of biological signals. The genera come with the mapping scan. | Map the body. Until then Bio status shows the signal count. |
| The color variant before the first sample | The first sample (or the Composition Scanner) names the variant. For genera whose colors follow the star or a surface material, WFMT shows the likely color from the body's star and materials. It takes the system's main star as the star, so the result can be wrong in a system with several stars, and a material rule can name more than one color. The plants (Brain Trees, Anemones, Sinuous Tubers) follow the environment in ways WFMT does not predict. | Sample the plant or scan it with the Composition Scanner. The real color replaces the likely color. |
| The probability of each candidate species | The data lists which species a body's conditions allow, with no frequency for each. The percentages are an even share of the candidates. | The sample names the species. |
| Predictions for a body scanned while EDMC was closed | The conditions come from the body's Scan event, which EDMC does not receive while closed. | At each start, WFMT reads the last 14 days of journals and fills in the conditions, genera and first-footfall flag of bodies it has nothing saved for. A body scanned longer ago has no prediction until it is scanned again. |
| A certain species before a sample names it | The prediction is a list of candidates from the body's conditions. Unknown conditions never eliminate a species, so a candidate can be listed that the game would not allow. | The sample names the species. |
| The position of a sample taken while EDMC was closed | The journal does not record positions. WFMT reads the position from `Status.json` as the sample is taken. | The position is not recoverable. The stage is recovered: at each start, WFMT reads the last 14 days of journals and raises the saved progress of any species logged, sampled or analyzed while EDMC was closed (a species analyzed with EDMC closed shows `Analyzed: 3/3`). Samples taken with EDMC running are kept for the body across restarts. |
| The SRV's position | The journal does not record it. WFMT uses the position where the SRV was launched or left. | None. |
| A plant's position without the Composition Scanner | Only the scanner's Codex entry carries a position. | Scan the plant with the Composition Scanner. |
| The first footfall mark on an old body | The mark comes from the body's own scan (`WasFootfalled`). | Scan the body again if the mark is missing. |
| A new species from a game update | The species data is a snapshot. A species added later cannot be predicted until the data is regenerated. | Sample it. The sample names the species. |

## What WFMT keeps to improve the prediction

Each time a sample names a species, WFMT adds a line to `exo_observations.json` (in the plugin folder).

Each line holds:

- the body's conditions: type, atmosphere and its trace gases, gravity, temperature, pressure, volcanism, the star, surface materials, the system's other body types and its position in the galaxy;
- the species and color found;
- the species the prediction had listed.

The record is used to check the prediction over time: how often the species was on the list, which cases the rules missed, and which species occur together.

**Privacy and control**

- Unlike other data WFMT saves about play, this file is shared by every commander on the install and names none of them. It holds facts about bodies, not about who found them.
- Nothing is sent anywhere.
- The record is turned off or cleared with the **Settings** strip at the top of the Prediction review window (*Keep a record of what I find, to check the prediction* and **Clear the record...**). Clearing deletes every recorded find and review for every commander on the install.

### The Prediction review window

Press **Review** on the Organic Scanning panel (Exploration mode) to open it.

- **Finds** lists every confirmed species. The columns are **Result** (`On list` or `MISSED`, with a **!** added when the body was outside the range the data allows for that species), **Species**, **System and body**, **Body type / atmosphere**, **Listed** (the number of species the prediction listed for that genus) and **Review**.
  - The **Show** box filters the list: *All finds*, *Not on the predicted list*, *Outside a rule's range*, *Not reviewed yet*, *Needs a rule change*, *Look at again later* and *Recorded live only*. A count (`12 of 40`) shows how many finds match.
  - **MISSED** means a rule is missing or too strict.
  - Selecting a find shows the body's conditions and the listed species. Assign a **Review** (*Needs a rule change*, *Bad data or journal quirk*, *Expected, no change* or *Look at again later*) and a **Note**, then press **Save review**.
- **By genus** shows, for each genus, the number of **Finds**, the number **On the list**, the **Hit rate** and the **Average list length** (the average length of the predicted list).
- **Ranges** shows, for each species and condition (temperature, gravity, pressure), the **Observed** range of the finds beside the range the **Rules allow**, with a flag when a find falls outside.
- **Together** shows the species that shared a body, by body type and atmosphere.
- **Copy report** copies all of the above as text.

A review does not change the prediction. `python scripts/analyze_exo_observations.py` (run from a copy of the source) prints the same report.
