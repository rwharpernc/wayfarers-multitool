# Exobiology

Everything WFMT does for exobiology (the plants and organisms you sample on a planet's surface) in one place: the **Organic Scanning** panel in Exploration
mode, the four **overlay cards** that follow you across the surface, the way WFMT **leads you back to a plant** you identified, and the **first footfall**
bonus.

**Where this comes from:**

- Your scans, signals, codex finds and samples come from the journal.
- Your position, heading and the body you are near come from the game's `Status.json`.
- So everything about *your* sampling is exact.
- What the game does not say is predicted, and marked as a prediction. That means which species a planet hosts before you sample, and the color variant before the first sample (where the game's rules for it are known).
- Nothing here contacts the internet.

**On this page:** [The pieces](#the-pieces) · [Organic Scanning panel](#organic-scanning-panel) · [The overlay cards](#the-overlay-cards) ·
[Finding your way back to a plant](#finding-your-way-back-to-a-plant) · [First footfall](#first-footfall) · [When the cards reset](#when-the-cards-reset) ·
[Setting up](#setting-up) · [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)

## The pieces

| Piece | Where | What it does |
|---|---|---|
| **Organic Scanning panel** | Exploration mode | Predicts the species of each signal, tracks Log, Sample and Analyse, and says when you are far enough for the next sample |
| **Bio status** card | Overlay | Progress, the species and color variant being sampled with three circles, the reward, and the distance to the last sample |
| **Biology** card | Overlay | Each genus on the body with the species it could be, or is, and what each pays |
| **Bio radar** | Overlay | A top-down plot of your samples' circles, your ship and SRV, and the plants you are tracking, with little pointers |
| **Sample popup** | Overlay | A few seconds after each sample: what it was and what it pays |
| **Exploration Dashboard, Surface tab** | Window | The same exobiology in a window instead of on the screen: each genus, what it could be and pay, how far you are from the last sample, the plants you are tracking, and the body's conditions ([Exploration Dashboard](exploration.md#exploration-dashboard)) |

The overlay pieces need an overlay ([WFMT's built-in one on Windows, or EDMCModernOverlay](../OVERLAY_SETUP.md)) and are **off until you tick them**. They use the Organic Scanning panel's own prediction and
sample tracking, so the cards and the panel never disagree.

## Organic Scanning panel

Helps you find and identify exobiology life on a planet's surface.

1. Detect biological signals on a body (the system scan gives how many) and map it, which names the genera.
2. WFMT shows which species each genus is likely to be, based on the planet's atmosphere, gravity, temperature, pressure, volcanism, its star, the region of
   the galaxy and more, with an estimated credit value.
3. When you start sampling, it tracks your progress (Log, Sample, Analyse) and tells you when you have walked far enough from the last sample for the next one
   to count.

**What the section shows.** It is always visible in Exploration mode (it has no fold), under the title **Organic Scanning**:

- **`Predicted species: (land on a body with biological signals)`** until you are on a body that has them. When you are, and the body has been scanned, it reads `Predicted species (<body>):` and one line for each genus: `Tussock: Tussock pennatis (~1,000,000 cr)` when only one species fits, or `Bacterium: Bacterium aurasus, Bacterium nebulus` when several do, or `<genus>: unknown` when the body's conditions match none of the rules. Until the body's scan arrives it says `waiting on body scan data...`.
- **`Active scan: (none yet)`** until you sample. Then one line for each organism in progress: `Tussock pennatis: Sample (2/3)`, with `(~1,000,000 cr)` once it is analyzed and ` - next sample ready` or ` - move further away` while you walk between samples. The stage names are Log, Sample and Analyse, and the count is out of three.
- **REVIEW** opens the [Prediction review window](#the-prediction-review-window).

**How to use it, step by step.**

1. Fly to a planet with biological signals (the system scan or the FSS tells you how many). Map it with the Detailed Surface Scanner: the mapping scan is what names the genera.
2. Land, or fly low, and read the `Predicted species` lines to see what each genus could be and what it pays.
3. Optionally use the Composition Scanner on a plant from a distance to identify it. WFMT remembers where it is so the cards can lead you back to it ([Finding your way back to a plant](#finding-your-way-back-to-a-plant)). The first scan of an organism with the Genetic Sampler is the **Log**, and the `Active scan` line starts.
4. Take the second (**Sample**) and third (**Analyse**) scans of the same species, each at least the genus's minimum distance from the previous one. The `Active scan` line says `next sample ready` when you are far enough and `move further away` when you are not.
5. After the third scan the organism shows its payout, and the cards (below) mark the genus `Done`.

You can switch the section off under **Settings → WFMT → Exploration → Organic Scanning** (**Show predicted species and scan progress**, on by default). It uses only your own journal and
makes no internet connection, and it submits nothing. The rules behind the prediction are in the [specification](../ORGANIC_SCANNING_TECH_SPEC.md).

## The overlay cards

Four cards for the body you are on, whether you are in the ship, the SRV or on foot. Each has its own switch under **Settings → WFMT → Overlays → Exobiology** and its
own entry on **Overlay Placement**.

**How names are written**

- Species are written as scientific names: the genus with a capital and the species in lower case (`Tussock pennatis`, `Bacterium aurasus`; the game writes both words with capitals).
- A color variant keeps its capital (`Tussock pennatis - Lime`).
- The game's own common names (Bark Mound, Brain Tree, Amphora Plant and the like) are left as the game writes them.
- The overlay draws plain text, so a name cannot be italicized there.

### Bio status

Top center. It is a short, wide strip, so it can sit above the game's compass.

- The heading is *Biological signals*, with a count of how many you have analyzed (`1 of 4 analyzed`) and a progress bar. The bar moves a third of a genus with each Log or Sample, and all of it once analyzed.
- While you are sampling a genus it shows:
  - the species and color variant in large type, with three circles (filled as you take each sample),
  - what the species pays, at the right end of that row (**five times as much on a first footfall**, marked `FF 5x`),
  - how far you are from the last sample against the distance the genus needs (`Move 122 m further: 78 m of 200 m`, or `Clear: 210 m from the last sample, 200 m needed` once you can take the next).
- With nothing in progress it lists each genus with the distance it needs between samples, and `Done` once analyzed.
- A plant you have identified with the Composition Scanner is named at the foot until you sample it.
- On a body you have not mapped it says `Map this body with the surface scanner to learn what lives here`, with the number of signals.
- While you are sampling and have not taken a first sample yet, the line under the reward reads `Samples must be 200 m apart`.
- With nothing in progress, the foot of the card reads `Use the Composition Scanner on a plant to begin`, `First footfall: every reward here is five times as much` on an untouched body, or `All samples analyzed` when you are done.

### Biology

Bottom, left of center. Its heading is `Bio signals <body>` with `1 of 4 done` at the right. It lists every genus on the body with the species it could be, or is once a sample has named it (with its color variant), and what it pays. A genus with no usable prediction reads `unknown`.

- Before a sample names the real color, a genus whose colors follow the **star** the body orbits or a **surface material** shows `Likely color: Emerald` under its row (or `Lime or White` when more than one material fits).
- While the species is open, the genus shows the **range** it could pay (`1.0M - 5.3M CR`), and each candidate species has its own row under it, indented, with its value and a percentage (`5.3M CR  ~50%`) at the right. A genus with more than five candidates shows the five that pay most and counts the rest (`+2 more`); on a crowded body each genus is one row with its range. A single likely species has a `~` before its value.
- The footer is the range the whole body could pay (`Rewards: 7.6M - 11.9M CR`). With a first footfall, the larger figure is on its own line (`First footfall (5x): 38.2M - 59.6M CR`).
- Analyzed species are in the good color.
- **The percentages are an even share.** The data says which species the body's conditions allow, not how likely each one is, so with two candidates each shows about 50%. Treat them as a count of the candidates, not as odds.

### Bio radar

A top-down plot centered on you, with straight ahead up.

- A small arrowhead with an **N** on its edge shows which way north lies. The plot turns as you turn, so north moves around it.
- Each sample you took has a circle as wide as the genus's minimum distance between samples: **red** while you are inside it (too close for the next sample), **green** once you are clear.
- The ship (where it touched down) and the SRV (where you launched or left it) are marked `S` and `V`.
- Under the plot are the distances to the ship, the SRV and your first two samples. Each has a **little pointer** before it, turned to show which way that thing lies relative to the way you face (straight up means straight ahead).
- **Circle sizes.**
  - The scale adapts so every circle's center fits.
  - The circles themselves are drawn within a fixed size range (about 5% to 16% of the plot's width as a radius), so a circle is never a dot or a blob however far you zoom out.
  - Because of that, a circle's size is not to scale, though its position is. A circle that reads as overlapping another may not be.
- **Settings** (**Settings → WFMT → Overlays → Exobiology**):
  - **Radar size**: pixels across, from 200 to 800. 260 by default, and 520 for twice the size, which draws every sample circle larger.
  - **Circle fill**: how solid a circle is while you are inside it, as a percentage from 0 (an outline only) to 100. 70 by default.
  - **Circle outline**: its thickness in pixels, from 1 to 6. 2 by default.
- **How far it shows.** The plot never shows less than a 150 m radius around you, nor more than 3 km. Up to 12 sample circles and 5 tracked plants are drawn.

### Sample popup

For ten seconds after each sample, it shows:

- the species and variant as its heading,
- **Estimated value**, in credits (five times as much on a first footfall, marked `(FF bonus)`),
- **Colony range**, the distance the genus needs between samples,
- at the foot, whether it was **Logged**, **Sampled** or **Analyzed**.

## Finding your way back to a plant

When you identify a plant with the Composition Scanner, WFMT remembers where it is (the journal gives its latitude and longitude).

- It follows **one plant for each genus you have identified**: the most recent one of that genus that you have not sampled.
- Identify a Tussock, a Bacterium and a Frutexa and you have three pointers at once.
- Up to four plants of a genus are kept for the body, and the list survives restarting EDMC.
- Bark Mound and a few other genera whose codex names do not follow the usual pattern are not tracked.

### Where the pointers show

- The **Bio radar** marks each tracked plant with a ring and the genus's letter, and draws a line from you toward it. It lists the plant under the plot (`Tussock 94 m`) with a **little pointer** that turns to show which way it lies.
- Each genus has its own color, the same for its ring, its line, its row and its line on Bio status.
- **Bio status** has a line for each, with the distance and direction (`Tussock: 94 m, 60° right`). The lines sit side by side in one row, each in its genus's color. It says `ahead` or `behind` when the plant is nearly straight on or off.

### How exact a marker is

The Composition Scanner names a plant from a distance, and the journal records where *you* were when it did, not where the plant is. So a marker is only as exact as that distance.

- Scanned **on foot**, it is close to the plant.
- From an **SRV**, it can be a hundred meters or more off.
- From a **ship**, it can be two hundred or more.
- The numbers are estimates (about 40, 150 and 250 m for foot, SRV and ship).

WFMT remembers which you were in, draws the marker's ring as wide as the marker may be off, and writes the distance with a `~` (`Tussock: ~210 m, 30° right`) unless you scanned on foot.

Walk to the ring and look: the plant is inside it. **Sampling the plant makes its spot exact.**

### When a pointer goes

- A Log or Sample taken at a plant drops the marker nearest you for that genus, when you are within its reach:
  - about 100 m for an on-foot marker,
  - 300 m for an SRV one,
  - 450 m for a ship one (50 m more when the sample names the same color variant).
- The next marker is the next most recent plant of that genus you identified, or none if there is no other.
- Analyzing a genus clears all of its pointers, wherever you did it.

## First footfall

The first commander to set foot on a body is paid **five times** the usual exobiology reward there. The game says whether anyone has, in the body's scan
(`WasFootfalled`), and WFMT shows it:

- **Bio status** and **Biology** mark the reward (`first footfall bonus`) and the Biology footer shows what the body could pay with it.
- **Body info** flags the body (`First footfall`) and adds a row saying exobiology pays five times there when it has life.
- **System targets** marks a body with life where the first footfall is still open (`0/3 life FF`).

The flag is kept once seen, because a later scan after you have landed says the body has been footfalled, and the bonus is still yours.

A body scanned long ago may show as footfalled if someone has landed since. Treat the flag as a strong hint, and check the in-game body information if it matters.

## When the cards reset

- **Leaving the planet** clears the Exobiology cards: the game stops naming a body once you are away from it. What you sampled is kept for the body and returns
  if you come back.
- The cards are also hidden in hyperspace, while docked, when the game is closed or at its main menu (including while another commander signs in), and a
  different commander loading in starts with a clean slate.
- **System targets** and **Body info** move on to the next body to map or sample: a body drops off System targets when you map it or analyze its last organism, and
  Body info does not hold on to a targeted body that is finished (see [System targets and Body info](exploration.md#system-targets-and-body-info)).
- After a relog or an EDMC restart the cards are rebuilt from your journals, reading back through earlier journals of the same commander while you stayed in the
  system, so a body you scanned before the relog still shows.

## Setting up

1. Set up the [overlay](../OVERLAY_SETUP.md).
2. **Settings → WFMT → Overlays → Exobiology**: tick the cards you want and press **Test Cards**. The four ticks are *Enable the Bio status card (progress, current species, distance to the last sample)*, *Enable the Biology card (predicted species and what they pay)*, *Enable the Bio radar (samples, their circles, your ship and SRV)* and *Enable the Sample popup (a few seconds after each sample)*. All four are off at first. **Test Cards** draws a made-up body (a Tussock being sampled, with a first footfall) on all four, works even while they are off, and says whether an overlay could be reached.
3. **Settings → WFMT → Overlays → Overlay Placement**: drag each card where you want it in the layout editor. The cards start at the top center (Bio status), the bottom
   center left of the Body info card (Biology), the left middle (Bio radar) and above Biology (Sample popup).

The cards are plain dark panels, so they sit quietly over the game; the text size and colors follow **Settings → WFMT → Overlays → Appearance**.

## What the game does and doesn't tell us, and how to work around it

| What you might expect | What the game gives | What to do |
|---|---|---|
| The species before you map the body | The scan gives only the number of biological signals; the genera come with the mapping scan. | Map the body. Until then Bio status shows the signal count. |
| The color variant before the first sample | The variant is named by the first sample (or the Composition Scanner). For the genera whose colors follow the star or a surface material, WFMT shows the likely color from the body's star and materials; it takes the system's main star as the star, so in a system with several stars it can be wrong, and a material rule can name more than one color. The plants (Brain Trees, Anemones, Sinuous Tubers) follow the environment in ways WFMT does not predict. | Sample, or scan the plant with the Composition Scanner: the real color replaces the guess. |
| A real chance for each candidate species | The data lists which species a body's conditions allow, with no frequency for each, so the percentages are an even share of the candidates. | The sample names the real species. |
| Predictions for a body scanned while EDMC was closed | The conditions come from the body's Scan event, which EDMC does not pass on while it is closed. | Each time EDMC starts, WFMT reads the last 14 days of journals and fills in the conditions, genera and first-footfall flag of bodies it has nothing saved for. A body scanned longer ago than that has no prediction until it is scanned again. |
| A certain species before a sample names it | The prediction is a list of candidates from the body's conditions; unknown conditions never eliminate a species, so a candidate may be listed that the game would not allow. | The sample names the real species. |
| The position of a sample taken while EDMC was closed | The journal does not record positions; WFMT reads yours from `Status.json` as you sample. | None for the position. The stage is not lost: each time EDMC starts, WFMT reads the last 14 days of journals and raises the saved progress of any species logged, sampled or analyzed while EDMC was closed (a species analyzed with EDMC closed shows `Analyzed: 3/3`, not `2/3`). Samples taken with EDMC running are kept for the body across restarts. |
| The SRV's position | The journal does not give it; WFMT uses where you were when you launched or left it. | None. |
| A plant's position without the Composition Scanner | Only the scanner's codex entry carries a position. | Scan the plant with the Composition Scanner. |
| The first footfall mark on an old body | It comes from the body's own scan (`WasFootfalled`). | Scan the body again if the mark is missing. |
| A new species from a game update | The species data is a snapshot; a species added later cannot be predicted until the data is regenerated. | Sample it: the sample still names it. |

## What WFMT keeps to improve the prediction

Each time a sample names a species, WFMT adds a line to `exo_observations.json` (in the plugin folder).

Each line holds:

- the body's conditions: type, atmosphere and its trace gases, gravity, temperature, pressure, volcanism, the star, surface materials, the system's other body types and its position in the galaxy,
- the species and color found,
- which species the prediction had listed.

It is used to check the prediction over time: how often the species was on the list, what the rules missed, and which species turn up together.

**Privacy and control**

- Unlike everything else WFMT saves about your play, this file is **shared by every commander on the install and names none of them**. It holds facts about bodies, not about who found them.
- Nothing is sent anywhere.
- Turn the record off, or clear it, under **Settings → WFMT → Exploration → Organic Scanning → Prediction review**. Clearing deletes every recorded find and review, for every commander on the install.

### The Prediction review window

Press **REVIEW** on the Organic Scanning panel (Exploration mode) to open it.

- **Finds** lists every confirmed species. The columns are **Result** (`On list` or `MISSED`, with a **!** added when the body was outside the range the data allows that species), **Species**, **System and body**, **Body type / atmosphere**, **Listed** (how many species the prediction listed for that genus) and **Review**.
  - The **Show** box filters the list: *All finds*, *Not on the predicted list*, *Outside a rule's range*, *Not reviewed yet*, *Needs a rule change*, *Look at again later* and *Recorded live only*. A count (`12 of 40`) shows how many match.
  - **MISSED** means a rule is missing or too strict.
  - Select a find to see the body's conditions and the species that were listed. Give it a **Review** (*Needs a rule change*, *Bad data or journal quirk*, *Expected, no change* or *Look at again later*) and a **Note**, then press **Save review**.
- **By genus** shows, for each genus, the number of **Finds**, how many were **On the list**, the **Hit rate** and the **Average list length** (how long the predicted list usually was).
- **Ranges** shows, for each species and condition (temperature, gravity, pressure), the **Observed** range of your finds beside the range the **Rules allow**, with a flag when a find falls outside.
- **Together** shows the species that shared a body, by body type and atmosphere.
- **Copy report** copies all of it as text.

A review changes nothing in the prediction; it is a note for whoever next tunes the rules. `python scripts/analyze_exo_observations.py` (from a copy of the source) prints the same report.

The Odyssey exobiology tools in the game itself remain the final word.
