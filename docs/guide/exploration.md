# Exploration

This guide covers Exploration mode: the panel layout, each exploration feature, its settings, the windows it opens and the limits of the underlying data.

Exploration mode is one scrolling panel (press **Explore** in the mode row to show it). It has a row of buttons at the top followed by sections in alphabetical order of their names. Sections are alphabetical in every mode.

- **Top row.** **Auto-Honk** and **Discovery Alerts** (toggles for those features), **Neutron Star** and **White Dwarf** (nearest neutron star and white dwarf) and **Random** (a system with no recorded scans). A status line under the row reports Discovery Alerts and the last Neutron Star or White Dwarf answer.
- **Sections.** Boxel Survey, Codex Completionist, Compass, Dashboard, Expedition, Nearest place to land, Notes, Organic Scanning, POI Reference and Route Planner.
- **Folding.** Every section with a ▸ / ▾ in its title starts folded. Clicking the title opens it. An opened section stays open until EDMC restarts. All sections are folded again at each start.
- **Width.** Names, notes and results in this panel wrap or are cut to a fixed length, so a long value does not widen EDMC's main window.

**Location of settings.** Most settings are under **Settings → WFMT**. A few belong to a window and are set only in that window (the table states which). Their Settings tab then points to that window.

| Feature | Settings page |
|---|---|
| Auto-Honk | Exploration → Auto-Honk |
| Boxel Survey, Region Sweep, Waypoint Route | Exploration → Boxel Survey (one page, the three sections one under another) |
| Expedition (copy on arrival, start the Expedition Log with an expedition) | The **Settings** strip across the top of the Expedition window (Exploration → Expedition only points there) |
| Exploration Value | Exploration → Exploration Value |
| Nearest place to land | Exploration → Nearest place to land |
| Organic Scanning | Exploration → Organic Scanning (the switch for the panel's section). Keeping the record for the prediction review is on the **Settings** strip of the Prediction review window |
| POI Reference and Codex Completionist | Exploration → POI Reference (the Canonn, edastro and Codex sections one under another). *Track codex entries* is on the **Settings** strip of the My Codex window |
| Discovery Alerts, Notable Bodies | Overlays → Discovery, Overlays → Notable Bodies |
| System targets, Body info, Route, Expedition Log card, Surface Compass, Exobiology cards | Overlays → the page of the same name |
| Position, colors and connection of each card | Overlays → Overlay Placement, Appearance and Overlay Connection (Overlay Placement can also copy another commander's overlay choices: see [Setting up the overlay](../OVERLAY_SETUP.md#moving-things-around)) |
| Local star index and the online lookups | General → Online lookups |
| Keyboard shortcuts and chat commands | General → Shortcuts |

**Data sources**

- Scans, jumps, honks and Codex finds come from the journal.
- The journal does not state which systems exist or are unvisited, the color of a gas giant, or which species a planet hosts before sampling. These are filled from EDSM, Spansh, Canonn and edastro, or derived and labeled as a lead to check.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

**Contents:** [How to: the common tasks](#how-to-the-common-tasks) · [Auto-Honk](#auto-honk) · [Discovery Alerts](#discovery-alerts) · [Notable Bodies](#notable-bodies) · [Boxel Survey](#boxel-survey) · [Exploration Value](#exploration-value) · [Organic Scanning](#organic-scanning) ([Exobiology guide](exobiology.md)) · [Codex Completionist](#codex-completionist) · [POI Reference](#poi-reference) · [Notes](#notes) · [Expedition](#expedition) · [Expedition Log](#expedition-log) · [System targets and Body info](#system-targets-and-body-info) · [Exploration Dashboard](#exploration-dashboard) · [Route Planner](#route-planner) ([Carrier route](#carrier-route)) · [Nearest place to land](#nearest-place-to-land) · [Compass](#compass) · [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)

Features that draw on the game screen require an overlay. See [Getting started](getting-started.md#what-you-need) and [Setting up the overlay](../OVERLAY_SETUP.md).

## How to: the common tasks

Each task links to the section with the full detail.

**Set up Auto-Honk** ([details](#auto-honk))

1. Open **Settings → WFMT → Exploration → Auto-Honk**.
2. Tick **Enable Auto-Honk** and set **Fire button** to the button the Discovery Scanner is bound to.
3. Press **Test Honk Now** and read the result beside the button.
4. Jump into a system. The scanner fires once on arrival.

**Use the Boxel Survey** ([details](#boxel-survey))

1. Open the **Boxel Survey** section and choose **Sequence**.
2. Enter a procedural system name in **Seed system** (or press **Use Current**) and press **Set**.
3. Press **Copy**, paste the target into the galaxy map and jump.
4. On arrival WFMT marks the system visited and moves to the next name. Press **Next >** to skip a name the galaxy map cannot find.

**Read the System targets card** ([details](#system-targets-and-body-info))

1. Tick **Enable the System targets card** under **Settings → WFMT → Overlays → System targets** and press **Test Card**.
2. Honk and scan in a system. The card lists **To map**, **Life**, **Known** and **Done**.
3. A body leaves the list when it is mapped or its last organism is analyzed.

**Use the Codex Completionist** ([details](#codex-completionist))

1. Open the **Codex Completionist** section and press **My Codex**.
2. On the **Overview** tab, read **Closest to complete** for the types with the fewest entries left.
3. On the **Not found** tab, read **Where to look** to choose a planet.
4. Press **Backfill Journals** once to include older finds.

**Use the Route Planner** ([details](#route-planner))

1. Press **Plot** in the Route Planner section.
2. Enter the destination and press **Generate route**.
3. Open the galaxy map and paste the system on the clipboard. Repeat after every jump.

**Use the surface compass** ([details](#compass))

1. Land (or leave the ship) on a planet.
2. Enter a name in the Compass box and press **Mark** to save the position.
3. Press **Target** until the line reads `Now aiming at ...` with the mark's name.
4. Tick **Enable Surface Compass** under **Settings → WFMT → Overlays → Surface Compass** to show the arrow on the game screen.

**Use the Dashboard** ([details](#exploration-dashboard))

1. Press **Dashboard** in the Dashboard section.
2. Read the tab that opens (**Orbit** in space, **Surface** when landed), or select **Overview** or **Exploration**.
3. On the **Orbit** tab, click a heading to sort the bodies and click a row for the full body.

**Write a note** ([details](#notes))

1. Open the **Notes** section, enter a line in the box and press **Add Note**.
2. Press **Notes** to search, change or delete notes.

**Find a place to land** ([details](#nearest-place-to-land))

1. Press **Find** in the Nearest place to land section.
2. Tick the required services, tick **Allow this lookup** and press **Find**.
3. Double-click a row to copy its system name.

**Find a point of interest** ([details](#poi-reference))

1. Press **Find POI** in the POI Reference section.
2. Paste the system name now on the clipboard into the galaxy map.

## Auto-Honk

Auto-Honk fires the Discovery Scanner automatically on every jump into a system.

**Procedure**

1. Turn the feature on with its toggle button (**Auto-Honk**, highlighted while on) or the **Enable Auto-Honk** box in Settings. The default is off.
2. Open **Settings → WFMT → Exploration → Auto-Honk** and set:

   | Setting | Meaning | Default |
   |---|---|---|
   | **Fire button** | **Primary** or **Secondary**. The Elite control that WFMT looks up in the key bindings. Select the one the Discovery Scanner is bound to | Secondary |
   | **Hold (sec)** | Time the key is held down. The Discovery Scanner charges while the button is held and fires when it is full, so a short tap does nothing. The charge time depends on the scanner and its engineering | 10 |
   | **Focus game window first** | Brings the Elite window to the front before the key is pressed. When off, the key is pressed into the window that has focus | On |
   | **Skip systems already visited** | See below | On |

3. Read the status line under the options. It states the key WFMT will press (`Status: Will press <key> when you jump into a system.`, in green) or the reason it cannot (in amber). Press **Rescan** after changing the bindings in the game or the fire button here, to read them again.
4. Press **Test Honk Now** to press the key immediately. The result appears beside the button (`Last test (Test): sent`, or the failure reason, such as `Elite Dangerous window not found`). **Rescan** and **Test Honk Now** work while Auto-Honk is off.

**Example.** The Discovery Scanner is on the keyboard key `U`, bound as the secondary fire.

1. Open **Settings → WFMT → Exploration → Auto-Honk**, tick **Enable Auto-Honk** and keep **Fire button** on **Secondary**.
2. Press **Rescan**. The status line turns green and reads `Status: Will press U when you jump into a system.`
3. With the game running, press **Test Honk Now**. Beside the button the text `Last test (Test): sent` appears.
4. Jump to the next system. WFMT presses `U` once on arrival. A jump away and straight back does not honk the same system a second time in the same session.

**Trigger.** Auto-Honk fires on every jump into a system (`FSDJump`) and every fleet carrier jump (`CarrierJump`) while it is on. It presses the key once per arrival and does nothing at other times.

**Skip systems already visited.** WFMT keeps the systems it has honked in since the game was loaded and does not honk the same system twice in that session. The memory is cleared each time a game is loaded. It is not a record of the full travel history.

**Behavior and limits**

- Auto-Honk presses a **keyboard** key. If the chosen fire button is bound only to a joystick or HOTAS button, the status line states this and no key is pressed. Bind a keyboard key to the fire button in the game, or select the other fire button.
- If the fire button is bound to nothing in the active control preset, or to a key WFMT cannot press, the status line states this.
- If WFMT cannot find or read the Elite controls file, the status line states this. WFMT reads the most recently saved `Custom.<version>.binds` file of the preset named in `StartPreset.start`.
- Auto-Honk does not check the ship's state. In a ship without a Discovery Scanner, or with a game menu open, the key press has no effect.
- If another program also fires the Discovery Scanner (some co-pilot applications do), one of the two must be turned off. The status line warns when a known co-pilot program is running.

On Linux, Auto-Honk requires `xdotool` and a keyboard key bound to the fire button. The **Elite Wine/Proton prefix** box sets the location of Elite's prefix when it cannot be found from Steam. See [WFMT on Linux](linux.md).

## Discovery Alerts

Discovery Alerts shows a banner on the game screen when the commander jumps into a system that nobody has scanned, or is the first to scan or map a body.

**Procedure**

1. Click the toggle button (**Discovery Alerts**) or tick **Enable Discovery Alerts** in **Settings → WFMT → Overlays → Discovery**. The default is off.
2. Run an overlay. The connection details are on the **Overlay Connection** tab under Settings → WFMT → Overlays.
3. Press **Test Discovery** on the Discovery page to send both banners. It works while the feature is off and reports whether an overlay could be reached. Banner positions are set under **Settings → WFMT → Overlays → Overlay Placement**; the default is the top center.

**Banners.** Two banner cards are shown, one under the other.

| Banner | Shown when | Display time |
|---|---|---|
| **NEW SYSTEM DISCOVERY**, with the system name | The commander jumps into a system and the game's automatic scan of the arrival star reports that the star was not scanned before (`WasDiscovered` is false) | 12 seconds |
| **First scan of a new discovery** or **First to map this body**, with the body name | A scanned (or mapped) body was undiscovered (or unmapped) at that time | 8 seconds |

The status line under the buttons repeats the event in text (`New system: ...`, `Scanned first: ...`, `Mapped first: ...`), or reads `Watching for new discoveries...` when there is nothing to report.

**Limits.** No banner is shown for a system or body that was already discovered. The first-to-map banner requires that the body's own scan was seen earlier in the system, because the mapping event does not state whether the body was mapped before. A body whose scan WFMT did not see (for example because EDMC was closed) is not announced.

### Neutron Star and White Dwarf buttons

These buttons find the nearest system whose *primary* star is a **neutron star (Neutron Star)** or a **white dwarf (White Dwarf)**, measured from the current position. They show the system name and distance and copy the name to the clipboard.

They run only on a click and contact Spansh at that time. The position must be known: jump or reload first.

**Display.** After a click, the line under the buttons reads `Neutron Star: searching...` and both buttons are disabled until the answer arrives. The answer has the form `Neutron Star: Sample Sector AB-C d1-2 - 84.3 ly, Spansh (copied)`: the system, the distance, the source that answered (**Spansh** or **local index**, see below) and `(copied)` once the full name is on the clipboard. A name longer than the panel allows is cut with an ellipsis on the panel only; the copied name is complete. The system the commander is in is never offered.

- `position unknown - jump or reload first` means WFMT has not yet seen a jump or login that gave the coordinates.
- `lookup failed - see EDMarketConnector.log` means Spansh could not be reached or returned data WFMT could not read.
- Only the **primary** star of a system counts. **White Dwarf** accepts a white dwarf of any class.

### The local star index

**Neutron Star** can answer from a file on the local computer. The index is optional.

- WFMT works without it. Nothing is downloaded unless a button is pressed.
- The index answers the neutron star search (currently the **Neutron Star** button) from a local file instead of a request.

**Setup.** In **Settings → WFMT → General → Online lookups**, the **Local star index** group has **Download and build**.

1. It downloads one public file from Spansh's download server (about 173 MB, once).
2. It builds an index of the neutron stars from the file. The index is about 110 MB on disk. Building needs about 300 MB of additional free space during the build, and the downloaded file is deleted afterward.
3. From then on **Neutron Star** searches the index instead of asking Spansh. The result line names the source: *local index* or *Spansh*.

The download starts only when the button is pressed.

**Buttons and tick**

- **Update** keeps the index current by fetching only what changed.
  - It fetches one of Spansh's update files (about 3 MB for a day, 19 MB for a week) and merges it into the index.
  - After 20 updates, or when the base file is more than 60 days old, the next update downloads the whole file again.
  - A second press within the same day downloads nothing.
- **Cancel** stops a download or build.
- **Delete** removes the index.
- The tick **Use the local index for Neutron Star when it is installed** is on by default. With it off, or with no index, **Neutron Star** asks Spansh.

**Coverage**

- **Neutron stars only.** **White Dwarf** has no local index and always asks Spansh.
- **Main stars only.** The file lists the main star of a system. A neutron star that is a secondary star is not in the index, as in the Spansh search that Neutron Star otherwise makes.
- **Age.** The index holds what the Spansh file held on the date shown in the status line. A system added since then is absent until **Update** is pressed. Positions are kept to 1/32 light year, the precision of the data.
- **Range.** Within 5,000 light years. If the index has no neutron star that near, Neutron Star asks Spansh.
- **Region name.** The local answer gives the system and the distance only.
- **Unusable file.** An index that is truncated, damaged or made by another version of WFMT is ignored and the status line states this. Neutron Star asks Spansh until the index is downloaded again.
- **Location.** The index is kept in the plugin folder (`star_index`), which must be writable. The updater does not remove it, and it is not part of **Back up my data**. It is identical for every commander and holds no data about play.

## Notable Bodies

Notable Bodies shows a violet banner on the game screen when a scanned body matches a selected rule. A match derives from scan data. It requires the same overlay as Discovery Alerts.

**Procedure**

1. Open **Settings → WFMT → Overlays → Notable Bodies**.
2. Tick **Enable Notable Bodies alerts**. The default is off.
3. Select the rules.
4. Press **Test Notable** to show a sample banner. The banner position is set under **Settings → WFMT → Overlays → Overlay Placement**.

The feature has no button on the main panel.

### Rules

Each rule has a tick box on the Notable Bodies settings page with a one-line description. The limits are fixed.

| Rule | Matches | Default |
|---|---|---|
| **Terraformable landable** | A landable body that is terraformable, being terraformed or already terraformed | On |
| **High-value body** | Any terraformable world, and every Earth-like, water and ammonia world, landable or not. The log line states whether it is undiscovered or unmapped | On |
| **High-g landable** | A landable body above 29.4 m/s² (about 3 g) | On |
| **Shepherd moon** | A moon orbiting inside the outer edge of its parent's outermost ring | On |
| **Good FSD injection** | A landable body with 5 or 6 of the 6 premium FSD boost materials (carbon, germanium, arsenic, niobium, yttrium, polonium) | On |
| **Green gas giant** | A Codex entry that names one, or a gas giant of a class whose surface temperature matches a confirmed green one. The game does not record a planet's color, so a match is a lead | On |
| **Colliding binary** | Two bodies sharing a barycenter whose closest approaches are less than their radii apart | On |
| **Large landable** | A landable body over 18,000 km in radius | Off |
| **Landable ringed** | A landable body that also has rings | Off |
| **Close orbit** | A moon whose orbit is under three times its parent's radius | Off |
| **Close binary** | Two bodies orbiting so close to their shared center (radius over 0.4 of the orbit) that they nearly touch but do not collide | Off |
| **High eccentricity** | An orbit with eccentricity above 0.9 | Off |
| **Fast orbit** | A planet orbiting in under 8 hours | Off |
| **Fast rotation** | A planet with a day under 8 hours that is not tidally locked | Off |
| **Wide ring** | A ring wider than five times the radius of the body it circles | Off |

The last eight rules are off by default because they match frequently.

### Alert behavior

- A body that matches several rules produces one banner (for example "High-value body +2").
- A body alerts once per rule.
- Each banner is displayed for 6 seconds. Banners are shown in turn: up to three wait behind the banner on screen, and the body name on the banner ends with `(N more)` for the banners still to come. Banners beyond three waiting are not shown separately.
- A banner has two lines: the title of the first rule that matched (with `+N` for the others) above the body's name. The measurements that matched (such as gravity or orbit) are written to EDMC's log and are not drawn on the banner.
- A Codex entry for a green gas giant produces the same banner (title **Green gas giant**, with the name of the nearest destination) when that rule is on.
- The banner widens to fit the body name and rule title. Text beyond about 56 characters is cut with "…".
- The banner starts at the top right of the screen ("Notable find card" on **Overlay Placement**).

## Boxel Survey

Boxel Survey is under development. Feedback is accepted as [issues](https://github.com/rwharpernc/wayfarers-multitool/issues).

Boxel Survey supports exploring the galaxy system by system using Elite's procedurally generated system names. A name such as `Outotz LS-K d8-0` has four parts: a sector name (`Outotz`), a three-character cube ID (`LS-K`), a mass-code letter a to h (`d`) and a number or number pair at the end (`8-0`). The "boxel" is the cube of space that shares the first three parts. The trailing number identifies one system inside it.

The section starts folded (click `▸ Boxel Survey` to open it). Inside, three buttons select a sub-mode: **Sequence**, **Region Sweep** and **Waypoints**. WFMT remembers the sub-mode last used.

**Scope.** Boxel Survey works with names, not coordinates. It counts through the trailing number to produce the next candidate name and does not know whether a candidate exists. The in-game galaxy map determines this. Real positions come only from EDSM or Spansh lookups.

### Choosing a sub-mode

| Purpose | Sub-mode |
|---|---|
| Work through one boxel in order | **Sequence** |
| Clear a region (several boxels) and track the remaining systems across all of them | **Region Sweep** |
| Visit a fixed list of systems in a nearest-neighbor order (a rendezvous, a squadron staging route) | **Waypoints** |

Waypoints accepts any system name, not only procedurally named systems. All three sub-modes are remembered per commander.

### Sequence

The panel shows a **Target**, the buttons **< Prev**, **Next >** and **Copy**, a **Seed system** box with **Use Current** and **Set**, a **Find Nearby (EDSM)** button, a line of survey counts and a status line.

**Starting a survey**

1. Enter a procedural system name in **Seed system** (or press **Use Current** to enter the current system). A gray hint under the box states whether the name looks like a boxel name.
2. Press **Set**. The seed becomes the first target.
3. Paste the target into the galaxy map (**Copy** puts it on the clipboard) and jump.
4. On arrival at the target, WFMT marks it visited and moves to the next candidate. With *Auto-copy next target to clipboard on jump* on (the default), it also copies the next name.

**Example: one boxel.** The commander is in `Outotz LS-K d8-0`.

1. Open the **Boxel Survey** section, choose **Sequence**, press **Use Current** and then **Set**. The gray hint states that the name looks like a boxel name, and **Target** shows the seed.
2. Press **Copy**, open the galaxy map, paste the name and plot the jump.
3. Jump. On arrival WFMT marks the system visited, moves **Target** to the next candidate and, with the default *Auto-copy next target to clipboard on jump*, copies that name.
4. Paste the name into the galaxy map and repeat. If the map cannot find a name, press **Next >** to skip it.
5. The line under the buttons shows the tally: `Surveyed: N systems | ELW | WW | AW | terraformable | bio`.

**A candidate that does not exist.** The galaxy map does not find it. Press **Next >** to skip it. **< Prev** steps back; at the start of the sequence the status line reads "Already at the start of the sequence". After 3 manual **Next >** presses in a row without a confirmed jump, WFMT asks EDSM for the nearest real procedurally named system outside the current cube and enters it in the Seed box. The survey does not switch automatically: press **Set** to move the survey there.

**Find Nearby (EDSM)** performs the same lookup on demand. It requires a known position: jump or reload first.

**Survey counts.** The line under the buttons counts the finds in surveyed systems: `Surveyed: N systems | ELW | WW | AW | terraformable | bio`.

- The counts come from the commander's scans: Earth-like, water and ammonia worlds, terraformable planets, and bodies with biological signals.
- To write them to a CSV file, open **Settings → WFMT → Exploration → Boxel Survey** and press **Export Survey Log**.
- The file is always named `boxel_survey_export.csv` and is saved in the WFMT plugin folder. The location cannot be chosen.
- The survey log is kept per commander and the export holds the active commander's finds. Exporting as another commander replaces the file.

**Scans made while EDMC was closed.** At start-up WFMT reads the last 14 days of journals. It adds the notable bodies and biological signals found there to the survey log, and the systems that were missing from it. No count is made twice:

- A system already in the log keeps its "bodies scanned" number (only missing finds are added).
- A system new to the log gets one count per body.
- Running the pass again changes nothing.
- Scans older than 14 days made with EDMC closed are not found.
- The game's journals are read and never changed.

**Settings → WFMT → Exploration → Boxel Survey (first section of the page)**

| Setting | Default |
|---|---|
| Auto-copy next target to clipboard on jump | On |
| Skip systems already visited this session | On |
| Skip systems already visited by anyone (EDSM) | Off (adds a network call per advance) |
| Skip systems already fully scanned in EDSM (adds another network call per candidate) | Off |
| Confirm off-sequence arrivals against EDSM (catches a target that resolved under a different display name) | Off |

### Region Sweep

Region Sweep clears several cubes and shows what remains. It keeps a **queue of cubes**. Each list entry has the form `> Outotz LS-K d [3/12]`: `>` marks the current cube and `[3/12]` is the number of systems done out of systems known.

**Setting up the queue**

1. Enter a seed system under *Add cube — seed system* and press **Add** (or press **Use Current**, then **Add**).
2. Press **Discover Nearby Cubes (EDSM)** to add cubes near the current position and to fill in the systems EDSM knows. The position must be known.
3. Select a cube and press **Discover Known Systems (Spansh)** to fill in the systems Spansh knows for that cube.

**Example: a small region.** The commander is in `Outotz LS-K d8-0`.

1. Choose **Region Sweep**, press **Use Current** under *Add cube — seed system*, then **Add**. The list shows the cube with `>` marking it as current.
2. Press **Discover Nearby Cubes (EDSM)**. More cubes join the list, each with the systems EDSM knows.
3. Select a cube and press **Discover Known Systems (Spansh)** to fill in more of its systems.
4. Press **Copy**, paste the **Target** into the galaxy map and jump. The count for that cube increases (`> Outotz LS-K d [3/12]`).
5. When every known system in the cube is done, the sweep moves to the next unfinished cube. To skip a cube, select it and press **Mark Empty** (the list shows `[empty]`).

**Operation.** The **Target**, **< Prev**, **Next >** and **Copy** buttons work as in Sequence, on the current cube. **Set Current** makes the selected cube the current one (the status line reads `Set as current`). **Remove** deletes it from the queue.

**Completion.** A cube is complete when every system WFMT knows in it is done, or when it is marked empty.

- WFMT cannot know a cube's total number of systems, only what EDSM, Spansh and the commander's visits have revealed.
- A system counts as done on arrival.
- With *Require a full FSS scan* on, a system counts as done when the game reports that the FSS has found every body in it (the `FSSAllBodiesFound` journal event). That check uses only the journal and no internet lookup.

**Mark Empty / Unmark Empty** flags the selected cube as having nothing to survey (the list shows `[empty]`). Empty cubes count as complete and are skipped. When the commander arrives at a cube's target and that cube is complete, the sweep moves to the next unfinished cube in the queue (wrapping around to the start).

**Settings → WFMT → Exploration → Boxel Survey, Region Sweep section (further down the same page)**

| Setting | Default |
|---|---|
| Auto-copy next target to clipboard on jump | On |
| Skip systems already visited this session | On |
| Skip systems already visited by anyone (EDSM) | Off. When on, each candidate target is checked with EDSM before it is offered, and systems EDSM already knows are skipped (at most 20 in a row) |
| Require a full FSS scan (not just arrival) to mark a system complete | Off |
| Auto-discover more nearby cubes (EDSM) when the queue is running low | Off. When on, the Discover Nearby lookup runs after a jump once one or fewer cubes still have work left |

**Skip systems already visited by anyone (EDSM).** With the box ticked, WFMT asks EDSM about each candidate before showing it as the next target, whether the candidate came from a jump or from **Next >**.

- If EDSM already has the system, WFMT moves to the next candidate in the cube and asks again. It stops after 20 in a row and shows the last candidate; the status line states this.
- The target (and the clipboard copy) appears when the check is complete. The status line reads `Checking EDSM...` meanwhile.
- If EDSM cannot be reached, nothing is skipped: the candidate is shown and the status line reads `EDSM check unavailable`.
- Each name is queried once per session. Only the system name is sent (see [What goes on the internet](internet-and-privacy.md)).
- A skipped system is not marked visited or complete in the queue; it is passed over.

### Waypoints

Waypoints is a route tool that accepts any system names: a rendezvous, a point of interest, a squadron staging system.

1. Add waypoints in any of these ways:
   - Enter a name under *Add waypoint* and press **Add**.
   - Press **Use Current**.
   - Load a list with **Import CSV…**. It reads one system name per row, from the first column. Blank rows and a header row (a first cell such as `system`, `name` or `waypoint`) are skipped, and names already in the list are not added twice.
   - Press **From plotted route** to add the systems of the route plotted on the in-game galaxy map (the current system is left out). The systems are added with their coordinates, so the reorder needs no lookup for them.
2. **Move Up** and **Move Down** change the order by hand. **Remove** deletes the selected waypoint.
3. **Reorder (Nearest-Neighbor, EDSM)** asks EDSM for the coordinates of each system, then builds a route that starts at the current position and always goes to the nearest unvisited waypoint next. Visited waypoints keep their place at the front, and waypoints EDSM cannot locate keep their order at the end. The position must be known.
4. **Copy** copies the current target. With *Auto-copy next waypoint to clipboard on jump* on, WFMT copies the next waypoint on arrival. That tick is in the Waypoint Route section at the foot of **Settings → WFMT → Exploration → Boxel Survey**.
5. Waypoints are saved for each commander. The list and the current target persist across restarts.

**Example: a squadron staging route** with four systems.

1. Choose **Waypoints**. Enter the first system name under *Add waypoint* and press **Add**; repeat for the other three. Alternatively, enter one name per row in the first column of a CSV file and press **Import CSV…**.
2. Jump once so WFMT knows the position, then press **Reorder (Nearest-Neighbor, EDSM)**. The list is rebuilt starting from the current position, always going to the nearest unvisited waypoint next.
3. Use **Move Up** and **Move Down** for a different order.
4. Press **Copy**, paste the target into the galaxy map and jump. With *Auto-copy next waypoint to clipboard on jump* on, the next waypoint is copied on arrival.

### Random

**Random** copies the name of a nearby system that has no recorded scans.

**Example**

1. Press **Random** on the button row (the Boxel Survey section may stay folded).
2. Read the status line, for example `Copied: <name> (31 ly away, no scans on Spansh or EDSM)`.
3. Open the galaxy map, paste the name and plot the jump.
4. Press **Random** again for a different system. Within 5 light-years of the first search it picks another system from the same list, and only the EDSM check takes time.

**Random** is on the Exploration button row next to Auto-Honk, Discovery Alerts, Neutron Star and White Dwarf, so it is available while the Boxel Survey section is folded. It works with any sub-mode selected and does not change the Sequence target.

When pressed, WFMT:

1. asks Spansh for the systems nearest the current position, nearest first, and keeps those with **no scan data on record** (Spansh lists the system but no bodies have been submitted);
2. drops any system in the commander's visited-systems log, and the current system;
3. picks one at random from the nearest eight and asks EDSM for its bodies, trying up to **6** systems until one has none;
4. copies that name to the clipboard.

Every name comes from a service's list of real systems. The status line reports the result, for example `Copied: <name> (31 ly away, no scans on Spansh or EDSM)`. If EDSM cannot be reached, the name is still offered and the line reads `EDSM unreachable`. If Spansh cannot be reached, the line states this and nothing is copied.

"No scans on record" means that the system exists and no scan of it has been uploaded. It does not show that nobody has visited the system, because a visit without a scan leaves no body data.

The visited-systems log records every system the commander arrives at, with any sub-mode selected. It is cleared under **Settings → WFMT → Exploration → Boxel Survey → Clear Visited Systems Log**.

WFMT keeps the Spansh list in memory for 10 minutes. Pressing Random within 5 light-years of where the list was fetched skips the Spansh search and picks a different system from the list. Systems already offered, or found scanned on EDSM, are not offered again. Nothing is saved to disk; restarting EDMC clears the list.

The same Settings page has **Systems to request from Spansh** (10 to 100, default 25). A larger request takes longer.

See the [Boxel Survey specification](../BOXEL_SURVEY_TECH_SPEC.md).

## Exploration Value

Exploration Value is a readout in the **Dashboard** section of the Exploration panel (click its title to unfold it; the **Dashboard** button and a one-line system summary are at the top of that section). It needs no activation.

| Line | Content |
|---|---|
| `Last scan: <body> - est. 1,234,567 cr` | The estimated payout for the last scanned body (stars and planets), with the first-discovery multiplier when nobody had found it. `Last scan: (none yet)` until a scan occurs |
| `System age: <age>` | The age of the current system, from the star's `Age_MY` in the scan, in million years (`4,200 My (~4.2 By)`; a billion-years figure is added from 1,000 My up) |
| `Region: Inner Orion Spur` | The named galaxy region (of 42) containing the commander's coordinates |
| `System bodies: 6 scanned of 14 - all found` | The number of the system's bodies scanned out of the number found by the honk. `all found` appears once the game reports that the FSS has found every body. Before a honk the line reads `(honk to count them)` |
| `Last data sale: exploration 1,234,567 cr, organic 350,000 cr` | The payout of the last data sales, for comparison with the estimate. `Last data sale: (none yet)` until one is read |

The values are computed locally. The estimate is the value of scanning the body (with the first-discovery multiplier when nobody had found it). The value of scanning and mapping is on the [Body info](#system-targets-and-body-info) card (**Mapped value**) and is counted in the [Expedition Log](#expedition-log).

The readout is on by default (*Show estimated scan value, system age, and current region*, in **Settings → WFMT → Exploration → Exploration Value**). Two further options are on the same page. Both are off by default because they contact the internet.

- *Show ELW rarity comparison when you scan an Earthlike World (Spansh)*. A line `ELW rarity: <body> - 2 known ELWs within 250 ly - a rare find` appears (`not unusual here` when more than 3 are known), after `checking Spansh...`. The count is of Earth-like worlds Spansh lists around the system.
- *Show EDSM upload status when you select a system on the galaxy map (EDSM)*. A line `EDSM upload status: <system> - already in EDSM` (or `not yet in EDSM`, or `EDSM check unavailable`) appears when a system is selected in the galaxy map. A system is queried once in ten minutes.

## Organic Scanning

Organic Scanning predicts the species of each biological signal on a planet, with an estimated credit value, and tracks Log, Sample and Analyse progress and the distance required for the next sample. It also provides four overlay cards for the current body (bio status, predicted species, a sample radar and a popup after each sample), markers that lead back to identified plants, and the first footfall bonus display.

The section starts folded (click its title to open it). It contains the `Predicted species` readout, an `Active scan` readout that appears once a scan has started, and a **Review** button for the prediction review window. The full description is in the **[Exobiology](exobiology.md)** guide.

The section is switched off under **Settings → WFMT → Exploration → Organic Scanning** (**Show predicted species and scan progress**). It uses only the journal and makes no internet connection.

## Codex Completionist

The section starts folded (click the title to open it).

Codex Completionist keeps a tally of the Codex entries the game has reported, such as biological, geological, Guardian, human and Thargoid finds. It is built from the `CodexEntry` events in the journal.

- The section shows one summary line (`120 distinct entries, 340 total finds`) followed by the three largest categories.
- The one button, **My Codex**, opens the [My Codex window](#the-my-codex-window).
- The feature is on by default. It is switched off with *Track codex entries* in the **Settings** strip at the top of the My Codex window. **Settings → WFMT → Exploration → POI Reference** has the *View Canonn Codex* link.

**Per-commander tally.** Each commander has a separate tally. Switching commander switches the tally (the window's subtitle names the commander), and one commander's finds never appear in another's.

WFMT builds each commander's tally from that commander's journals the first time the commander logs in.

- While it reads, the Codex Completionist title reads **"- rebuilding..."** (also when the section is folded).
- The summary line states that the commander's tally is being rebuilt. The summary fills in when the rebuild finishes.

**Finds made while EDMC was closed.** At each start, WFMT reads the journal files written since the last counted find and adds the newer finds, once each. The first start only sets this starting point; use **Backfill Journals** once to include older history.

### The My Codex window

Press **My Codex**. The subtitle reads, for example, `120 distinct entries — 340 total finds — 95 of 1,070 catalogued entries found (9%)`. The window has three tabs.

- **Overview**: progress. The first row is every catalogued entry. **Closest to complete** lists the types that are started but not finished, fewest entries left first. Each category with its types follows. Columns: **Found**, **Of** (how many exist), **Left** and **Done** (percent). Clicking a heading sorts the types inside each category (**Left** ascending is the default).
- **Found**: the commander's entries grouped by category, with the columns **Entry**, **Times found** and **First found in**. A ⭐ means that at least one sighting was reported by the game as a new entry (a first discovery). Clicking a column heading sorts; clicking again reverses. **Times found** sorts highest first on the first click.
- **Not found**: Canonn's catalog of **biological, civilization and stellar-body** entries, minus the entries already found. Columns: **Entry**, **Type**, **Platform** (Odyssey or Legacy) and **Where to look**. Sorting works as on the Found tab. Canonn's catalog has no geological or anomaly entries, so these never appear here.

**Where to look** is derived from WFMT's species data, the same data used by the Bio predictions.

- For a biological entry such as `Bacterium Aurasus - Teal` it gives the body type, atmosphere, gravity and temperature the species requires.
- It also states what decides the color: the class of the star the body orbits (`Teal: orbiting a class M star`) or a material in the surface (`Gold: surface holds Polonium`).
- A species can have several sets of conditions, and any one set is sufficient. The hint shows the first set and counts the others (`+1 other set`).
- Entries without species data in WFMT (Thargoid and Guardian entries, stellar bodies) have no hint. Use **POI Reference** to find Thargoid and Guardian sites near the commander.
- The hint states where an entry can appear, not where one is located.

**Buttons:** **Open Reference**, **Refresh Catalog** and **Backfill Journals**. Double-clicking a row on the Found or Not found tab, or selecting it and pressing **Open Reference**, opens a **search** on canonn.science for the entry's name in the browser. It does not open a fixed page for the entry.

**Backfill Journals** is started manually.

- It reads all journal files in EDMC's journal folder, with no date limit.
- It counts only the current commander's entries (a journal file states whose events follow, and one file can hold several commanders).
- Progress shows in the window's status bar and in the section under the button.
- It can be pressed more than once. For each entry it compares the number of times the journals record it with the count already in the tally and keeps the larger. Nothing is counted twice, and finds from journals that have since been deleted are kept.
- It can also fill in an earlier first sighting and a first-discovery star.

**The catalog** is downloaded from Canonn the first time the window is opened and whenever the saved copy is more than 14 days old. **Refresh Catalog** fetches it on demand. It is saved in the plugin folder, so after the first download the window opens without a download and works offline. If the download fails, the tab states this and shows the saved copy if one exists.

**Example: choosing what to hunt for.** The commander has found 95 of 1,070 catalogued entries.

1. Press **My Codex** and stay on the **Overview** tab.
2. Under **Closest to complete**, read the first row. Types are listed with the fewest entries left first, with the columns **Found**, **Of**, **Left** and **Done**.
3. Switch to the **Not found** tab and look for entries of that type. Click the **Where to look** heading to sort.
4. Read the hint for an entry such as `Bacterium Aurasus - Teal`: the body type, atmosphere, gravity and temperature the species requires, and what decides the color (`Teal: orbiting a class M star`).
5. Select the row and press **Open Reference** to search canonn.science for the entry.
6. If the numbers seem low, press **Backfill Journals** once.

Codex Completionist has no specification page. The code is `codex_completionist.py`, `codex_completionist_window.py`, `codex_hints.py`, `codex_catalog.py` and `codex_backfill.py` in the plugin folder.

## POI Reference

The section starts minimized.

POI Reference finds points of interest near the commander from two catalogs. **Find POI** searches both, shows the nearest result from each on its own line, and copies the system name of the nearer of the two to the clipboard. A lookup occurs only on request. **Update POI** downloads Canonn's lists again and then searches.

The position must be known: jump or log in first. If EDMC started after the game was already running, the position is read from the current journal.

**GEC (edastro.com).** The nearest point of interest from edastro's exploration catalog. The line shows:

- the point of interest and its category;
- the system to find in the galaxy map;
- the distance, region and rating;
- a link to its page (the system's Inara search when edastro gives none);
- a **Copy System** button for the system name.

The first **Find POI** of a session downloads edastro's whole list (about 2 MB) and computes the nearest point locally. Later presses use that list for six hours without another download.

**Canonn.** The nearest of Canonn's Thargoid and Guardian sites.

- The first click downloads the lists, which are kept for the rest of the session.
- A **Copy System** button under the result puts that result's system name on the clipboard. Find POI copies only the nearer of the two sources; **Copy System** copies Canonn's.
- A **View site details** link beside it opens the site's page in the browser. For sites without a page in Canonn's list, the link opens the system's Inara search.
- The kinds of site to include are selected in **Settings → WFMT → Exploration → POI Reference**.
- By default sites already logged in Codex Completionist are skipped. This is switched off in the same place.

**Example: a Guardian site**

1. Jump or log in so WFMT knows the position, then open the **POI Reference** section and press **Find POI**.
2. Two result lines appear, one for **GEC (edastro.com)** and one for **Canonn**, each with its nearest result. The name of the nearer system is on the clipboard.
3. Paste it into the galaxy map and plot the jump. To use the other source's result, press that line's **Copy System** button.
4. Press **View site details** on the Canonn line to read about the site in the browser.
5. Press **Update POI** to download Canonn's lists again before searching.

## Notes

The section starts minimized.

Notes stores the commander's own notes on a system or body. The journal has no place for such text, so WFMT stores the notes on the local computer for the commander who wrote them. Another commander on the same install does not see them. Nothing is sent anywhere.

The section shows the newest note for the current system. With the section folded, the title states the number of notes the system has (`- 2 here`).

- **Quick note.** Enter a line in the box and press **Add Note** (or Enter). It is saved against the current system, and the body too when the commander is near one (the game's `Status.json` names it).
- **Notes** opens the Notes window: a **Search** box (every typed word must appear in the system, body or note), a list of every note, newest change first, and an editor underneath. The list columns are **System**, **Body**, **Note** (the start of the text) and **Changed (UTC)**. Selecting a note edits it. **New note** (in the header) starts another. **Here** beside the System and Body boxes fills in the current location (the System box suggests systems and the Body box suggests the bodies WFMT knows in that system). **Save** keeps the editor content. **Only the system I am in** limits the list to the current system.
- **Delete** requires a second press, because a deleted note cannot be recovered.
- Limits: a note up to 2,000 characters, a system or body name up to 100 characters, and 2,000 notes. At a limit WFMT displays a message and does not truncate the note.

Notes are matched to a system by name (ignoring capitals and spaces at the ends), so a note about `Sol` shows when the commander is in Sol.

**Example**

1. Open the **Notes** section, enter `ELW with a moon, scan the other side` in the box and press **Add Note** (or Enter). The note is saved against the current system, and the body when the game names one near the commander.
2. Fold the section. Its title reads `- 1 here`.
3. On a later arrival in that system the section shows the note. To change it, press **Notes**, select it, edit it and press **Save**.
4. To find the note from anywhere, press **Notes** and enter a word from the system, body or note in **Search**.

## Expedition

The Expedition planner plans a trip. An **expedition** is a named list of **stops** (systems, each with an optional body and note). After the expedition is started, WFMT ticks stops off on arrival and keeps totals. Several expeditions can exist; one runs at a time. Starting an expedition also starts a run in the [Expedition Log](#expedition-log). The two start, pause and stop together.

### Starting and managing an expedition

All management is done in the Expedition window. Press **Expedition** in the panel's Expedition section to open it. The panel shows only the running expedition (and has **Copy Next** and **Copy on arrival**); it has no Start, Pause or Stop.

| Purpose | Tab | Button | Result |
|---|---|---|---|
| A trip with stops, ticked off on arrival | **Plan** | **Start** | The expedition starts, and a run starts in the Log with the same name (unless switched off on the Expedition window's Settings strip) |
| Record a trip without stops | **Log** | **Start** | A run starts from the current system, in the current ship. There are no stops to tick |
| Count a trip already under way | **Log** | **Start from my last** and **sale**, **Discovery Data sale** or **Exobiology Data sale** | The expedition begins just after that sale and fills in from the journals |

After starting, the same buttons manage the expedition on either tab:

- **Pause** holds the expedition: nothing is counted and the clock stops. The button reads **Resume** while held.
- **Stop** ends the expedition. The expedition and its Log run stop together because they are linked.
- Starting another expedition sets the running one aside. Only one runs at a time.
- The panel's Expedition section, the Dashboard and the overlay card show the running expedition.

**Example 1: plan a trip from Sol to Colonia**

1. Press **Expedition**. On the **Plan** tab enter `Colonia run` in the **Name** box and press **New**.
2. Enter `Sol` in **System** and press **Add stop**. Enter `Colonia` and press **Add stop** again. (**Here** fills in the current system.)
3. Press **Start**. The status line states that the expedition started and is logging in the Expedition Log.
4. Each arrival in Sol or Colonia ticks that stop, and every jump adds to the totals. The panel shows `1 of 2 stops` and the next stop; while the section is folded its title shows `- 1/2`.
5. **Pause** holds the expedition and **Resume** continues it. **Stop** ends it. The trip stays in the **Log** tab with its findings and earnings.

**Example 2: record a trip without a plan**

1. Open **Expedition** and switch to the **Log** tab.
2. Enter a name such as `Bubble to the Rim` in **New expedition name** (the name is optional) and press **Start**.
3. The Log counts systems, jumps, light-years, bodies, mapping, species and credits from the journal. The panel and the overlay card show the running totals.
4. Press **Stop** to finish.

**Example 3: an expedition already under way**

1. Open **Expedition** and switch to the **Log** tab.
2. Press **Start from my last** and **sale**. The expedition begins just after the last sale, so all data still held counts.
3. To count only the exobiology gathered, press **Exobiology Data sale** instead (or **Discovery Data sale** for exploration data alone).
4. The expedition then continues counting live. Press **Stop** to finish.

**The Expedition row** (a collapsible section in Exploration mode) shows the running expedition:

- its name, `7 of 20 stops`;
- the jumps and light-years flown;
- the elapsed time (when the Expedition Log follows the expedition, paused time is not counted);
- the next stop with its distance (and its note);
- the stop most recently reached.

Buttons:

- **Copy Next** puts the next stop's system name on the clipboard.
- **Copy on arrival** copies the next stop on every arrival anywhere. It is off until ticked. The same switch is in the **Settings** strip across the top of the Expedition window, together with *Start the Expedition Log with an expedition* (on by default). A tick in either place appears at once in the other.
- **Expedition** opens the window.

**One window, three tabs**

- **Plan**: the expeditions and their stops.
- **Route**: the [Route Planner](#route-planner).
- **Log**: the [Expedition Log](#expedition-log).

Interaction of the tabs:

- **Expedition** and **Plot** on the panel each open this window (on the Plan and Route tabs respectively).
- **Neutron route** and **Review expedition** switch to the tab they need, so a trip is planned, plotted and recorded in one window.
- **Start expedition** is pressed on the Route tab and the window stays there. The status line states the result, and **Review expedition** switches to the Plan tab.
- A tab is built the first time it is shown.
- The window remembers its size and position.

**Findings at each stop.** While an expedition runs, WFMT counts against each stop the activity in that stop's system:

- the bodies scanned;
- the bodies nobody had discovered before (the scan states this);
- the bodies mapped.

After a honk the number of bodies in the system is also known, so a stop reads `5 of 12 scanned · 2 first · 1 mapped`.

- The row shows the running totals (`Found: ...`).
- The window has a **Found here** column for every stop.
- The stop the commander is at shows in the Expedition row.
- A body scanned twice counts once, belt clusters are not counted, and nothing is counted in a system that is not a stop already reached.

### The Expedition window

**Expedition** on the panel opens the window on the **Plan** tab. From top to bottom:

- **Header.** **Start**, **Pause** and **Stop** for the expedition selected below, and a Help button. The subtitle names the commander and the number of expeditions (up to 30).
- **Picker.** A list of expeditions, each written `Name (status, 3 of 20)`. The status is *planned*, *active*, *paused* or *done*. **Name** and the buttons **New**, **Rename**, **Reset** and **Delete** are beside it.
- **Totals line.** For example `Active · 7 of 20 stops · 31 jumps · 1,204 ly · 2 d 4 h · 38 scanned · 6 first · 4 mapped`: the status, stops ticked, jumps, light-years, time and the bodies found across all stops.
- **Stops table.** The stops in order (up to 500 per expedition):

  | Column | Content |
  |---|---|
  | **#** | The stop's number in the order |
  | **System**, **Body**, **Note** | The entered values |
  | **Reached (UTC)** | When the stop was ticked. The next stop shows `next` while the expedition is active |
  | **Found here** | Activity at the stop, such as `5 of 12 scanned · 2 first · 1 mapped` |
  | **From you (ly)** | The straight-line distance from the current position, or `-` when the stop has no position yet |

- **Editor.** Under the table: the boxes **System** (with suggestions as typed, and **Here** to fill in the current system), **Body (optional)** (suggesting the bodies WFMT knows in that stop's system) and **Note (optional)**, and the buttons **Add stop**, **Save changes**, **Mark visited**, **Move up**, **Move down** and **Remove**. **Mark visited** on a ticked stop removes the tick.
- **Make an expedition with Spansh.** **Road to Riches**, **Exomastery** and **Neutron route**.
- **Tools row.** **From plotted route**, **Import CSV**, **Locate and reorder (EDSM)**, **Copy list**, **Export CSV** and **Copy next**.
- **Status line.** At the foot, it states the result of the last button, including the reason for a refusal.

**Reset**, **Delete** and **Remove** require a second press within five seconds before they act.

### Using the Expedition window

1. **Create an expedition.** Enter a name and press **New**.
   - Select an expedition from the list at the top. **Rename**, **Reset** and **Delete** act on it.
   - To rename, press **Rename**: the current name appears in the Name box. Change it and press **Rename** again.
   - Reset removes the progress and keeps the stops. Reset and Delete require two presses.
2. **Add stops.** Enter the system (or press **Here** for the current one) and press **Add stop** or Enter. Only the system is required. The body and note are optional.
   - Capitals do not matter: `sol` is stored as `Sol`. WFMT uses the spelling of the current system or of an existing stop.
   - While *Check system names on EDSM when adding* is ticked under the editor (the default), WFMT also queries EDSM. EDSM corrects the capitals of any system and supplies the stop's position. Only the system name is sent.
   - A system EDSM does not know (uncharted or misspelled) is kept as entered, and the status line states this.
   - Unticking the box keeps the operation offline.
   - If no expedition exists, the first stop creates one named "My expedition" (or the name entered in the Name box).
   - Selecting a stop allows changing it (**Save changes**), moving it (**Move up**, **Move down**), ticking it manually (**Mark visited**) or removing it (**Remove**, two presses).
3. **Add many stops at once.** These also create an expedition if none exists.
   - **From plotted route** adds the systems of the route plotted in the game. The current system is left out, and the systems are added with their positions.
   - **Import CSV** reads a file with the columns system, body and note (a one-column list of systems also works).
4. **Make an expedition with Spansh.** **Road to Riches** and **Exomastery** (in a row above the other tools) ask [Spansh](https://spansh.co.uk/)'s route planners for places to visit and turn the answer into a new expedition.
   - **Road to Riches** selects the bodies worth the most credits to scan, near a route, in order. Tick *Count what mapping pays as well as the first scan* to include mapping.
   - **Exomastery** (Spansh's Expressway to Exomastery) selects planets with the most valuable biological signals.
   - **Neutron route** opens the [Route Planner](#route-planner), which plots a neutron route for the current ship and can turn it into an expedition with **Start expedition** or **Review expedition**.
   - A dialog asks for:

     | Box | Meaning | Default |
     |---|---|---|
     | **Start from** | Where the route begins | The current system |
     | **End at (optional)** | Empty gives a route that goes where the best places are | Empty |
     | **Jump range (ly)** | The ship's range, taken from the last loadout WFMT has seen | 30 when no loadout is known |
     | **Look this far from the route (ly)** | How far off the route a place may be | 25 |
     | **Most results** | Up to 100 | 100 |
     | **Furthest from the arrival star (ls)** | Excludes bodies farther from the arrival star | 50,000 |
     | **Least a body is worth (credits)** (Road to Riches) or **Least a planet's biology is worth (credits)** (Exomastery) | Minimum value | 100,000 for Road to Riches, 10,000,000 for Exomastery |

   - **Avoid systems the Thargoids control** is ticked by default. **Come back to the start** is not. **Start it now** is a third tick (see below).
   - Each number box must be a number above 0. Otherwise the dialog names the box to correct.
   - Press **Plot**. Spansh can take from a few seconds to a few minutes. WFMT waits up to five minutes and then states this.
     - While it works, the **Plot** button reads *Plotting...*, a bar moves along the window, and a timer shows the elapsed time with Spansh's status (waiting in the queue, or calculating).
     - **Cancel** stops waiting.
     - The answer becomes a new expedition (named, for example, *Road to Riches from Sol*) with a stop for each system: the best body, a note of what is worth scanning and its position.
     - Check the order, then press **Start**. Alternatively, tick **Start it now** before pressing Plot to start the expedition when the answer arrives.
   - This is an online operation, and only when **Plot** is pressed. It sends Spansh the start system, the end system if entered, and the numbers above (see [what goes on the internet](internet-and-privacy.md)).
   - If Spansh cannot find a system, the dialog states this. If no place worth stopping at is found, no expedition is made: lower the minimum value or increase the distance from the route.
5. **Locate and reorder (EDSM)** asks EDSM for the positions of the unvisited stops that have none, then orders the unvisited stops by always going to the nearest next, starting from the current position.
   - This is the only part of the Expedition planner that goes online, apart from the Spansh plotting above and the EDSM name check. It sends only system names.
   - A stop EDSM cannot place keeps its place at the end.
6. **Start.** Press **Start**.
   - Arriving in a stop's system (a jump, a carrier jump, or logging in there) ticks the first unvisited stop of that name, wherever it is in the list. Each jump adds to the totals.
   - **Pause** stops counting and keeps the progress. Starting another expedition pauses this one.
   - When the last stop is ticked the expedition keeps running until **Stop** is pressed.
   - Starting a stopped expedition again reopens it, and its clock continues from the time it stopped at.
7. **Share.** **Copy list** puts a text list on the clipboard. **Export CSV** saves the stops (the file can be imported again). **Copy next** copies the next stop's name.

### The Expedition Log goes with it

Unless *Start the Expedition Log with an expedition* is unticked (on the **Settings** strip across the top of the Expedition window; on by default), **Start** also starts a run in the [Expedition Log](#expedition-log) under the same name, in the current ship. The status line reads *Logging in Expedition Log.*

- **Pause** pauses the run, **Stop** stops it, and starting the expedition again continues the same run.
- The Log tab's **Pause**, **Resume** and **Stop** act on the expedition too. The panel's Expedition section only shows the running expedition, so that section, the Exploration Dashboard and the overlay card agree with the window.
- Starting a second expedition sets the first aside. It is paused, and its run is paused with it (or stopped, when the new expedition gets a run of its own, because the log keeps one run going at a time).
- An expedition started with the box unticked, or one created before this feature existed, has no run. Its time is counted from its start on the wall clock.

Expeditions are stored on the local computer for each commander. Nothing is sent anywhere except the lookups described above. The planner does not replace **Waypoints** (Boxel Survey), which stays a single quick list. **From plotted route** and the CSV import work the same way in both.

## Expedition Log

The Expedition Log is an archive of exploration expeditions and a card that shows the running one. It is separate from the [Expedition planner](#expedition), which plans stops to visit. The log records what happened on a trip, whether or not a route was planned.

**An expedition from the planner.** Starting an expedition in the [Expedition planner](#expedition) or the [Route Planner](#route-planner) also starts a run here with the same name, unless this is switched off (the *Start the Expedition Log with an expedition* tick on the Expedition window's **Settings** strip).

- The run and the expedition are linked. **Pause**, **Resume** and **Stop** in the Log tab pause, resume and stop the expedition too, and the reverse.
- Starting a different run here (**Start**) stops the expedition that was linked to the run it replaces.
- Deleting a run from the log leaves the expedition unchanged, without a run.

**Starting an expedition already under way.** In the Log window, the **Start from my last** row has three buttons. Each begins an expedition one second after a sale found in the journals:

- **sale** is the earlier of the last Discovery Data sale and the last Exobiology Data sale, so it covers all data still held. If only one kind of sale exists, it is that one.
- **Discovery Data sale** is the last exploration sale alone.
- **Exobiology Data sale** is the last exobiology sale alone.
- If the journals hold no sale of the chosen kind, a message states this and nothing starts. Use **Start** instead.

The expedition is filled in from the journals since that time and then continues counting live.

**The row.** The Log has no section of its own. Its figures are in the Exploration panel's **Expedition** section ([above](#expedition)), which only shows what is running. Expeditions are started, paused and stopped in the Expedition window (the **Expedition** button).

- While an expedition runs, the section shows the expedition's own lines (name, stops, jumps, light-years, time, next stop). Under them it shows what the Log adds: the systems, bodies and species, the earnings and the unsold data (`paused` in front while held).
- A Log run started with **Start** and without a planned expedition is shown in the Log's own terms: name and duration, systems, jumps and light-years, bodies and species, earned and unsold.
- The section's title states whether a run is going (`- running` or `- paused`) also while folded. The open section shows the name and figures.
- **Start** (in the Expedition window) begins a new expedition now, from the current system and in the current ship, and stops the one that was running.
- **Pause** becomes **Resume** while paused. **Stop** ends the expedition.
- The archive is the **Log** tab of the Expedition window (**Expedition**, then the Log tab).

**Counted data.** The following is counted from the journal while an expedition runs:

| Category | Counted |
|---|---|
| **Exploration** | Systems visited, jumps and light-years, honks, bodies scanned (each once) and first discoveries, Earth-likes, water worlds, ammonia worlds and terraformables, bodies mapped and first maps, landings, new Codex entries, the credits earned when exploration data is sold, and an estimate of the value of scans and mapping not yet sold (with the first discovery, first map, efficiency and Odyssey bonuses) |
| **Exobiology** | Samples taken, species analyzed, genera, first footfalls, the credits earned when exobiology data is sold, and an estimate of the value of analyzed species not yet sold (five times as much on a first footfall) |
| **Ships** | Each ship flown (type, name and ident), added as the ship is loaded into |

Earned figures are the amounts the game reports at a sale, so they are counted at the sale and not at the scan.

- The unsold figures are estimates, marked `~`. A sale clears them, since the game sells all data held.
- The estimates use the community formula: the base value of the body from its class and mass, the first-discovery multiplier, the mapping multipliers (for a first map, a first map of an already discovered body, and an already mapped body), the efficiency bonus when the probe run met the target, and the Odyssey bonus.
- The estimates are approximate.

**The Log window** is the archive (the **Log** tab of the Expedition window). Up to 200 expeditions are kept.

- **Header.** **Start**, **Pause** and **Stop**. These are the only place on the Exploration side to manage an expedition; the panel's Expedition section has no such buttons.
- **Starter row.** The **New expedition name** box (optional; **Start** begins it now from the current position) and the **Start from my last** row (**sale**, **Discovery Data sale** and **Exobiology Data sale**).
- **Table.** Every expedition, newest first. Columns: **Name**, **Status**, **Started (UTC)**, **Ended (UTC)**, **Systems**, **Jumps**, **Bodies**, **Species**, **Exploration cr**, **Exobiology cr** and **Total cr**.
- **Under the table.** Everything the selected expedition recorded, then the editor.

Selecting an expedition shows everything it recorded. These fields can be edited, followed by **Save changes**:

- its name;
- when it started and ended (UTC; `2026-10-16` or `2026-10-16 18:30`);
- where it started and ended (the two location boxes suggest systems as typed);
- the ships used;
- notes.

Buttons:

- **Start** (with an optional name)
- **Pause** (pauses the running expedition, or resumes the paused one)
- **Stop**
- **Resume** (continues counting an expedition that was paused or stopped)
- **Reset** (clears its totals and counts again from now; two presses)
- **Rescan** (recomputes its totals from the commander's journals between its start and its end, which fills in an expedition that missed events or was given an earlier start)
- **Delete** (two presses)
- **Copy summary**
- **Export CSV** (the whole archive, for a spreadsheet)

**The overlay card** (Settings → WFMT → Overlays → Expedition Log, off until ticked) shows the running expedition's exploration and exobiology totals and its earnings.

- With no expedition running, it states this and how to start one.
- The heading has the name and the duration. The total earned is at the foot.
- It shows the expedition that is running or paused. A paused expedition keeps its counts (its heading reads `paused`) until it is resumed or stopped.
- Stopping resets the card, which then states that no expedition is running.
- The position is set on **Overlay Placement** ("Expedition Log (totals of the running expedition)"). The default is the top left, beside the Route card.

All data is kept for the commander only (another commander has a separate archive) and does not leave the computer.

**Pause, stop and resume**

- **Pause** holds an expedition. Nothing is counted while it is paused, and its clock stops (paused time is not part of the expedition's time). The row and the card keep showing it. It stays paused across an EDMC restart.
- **Resume** continues counting, and the clock restarts.
- **Stop** ends the expedition, whether running or paused, and the card resets. A stopped expedition can be resumed from the Log window, and its clock continues from the time it stopped at (stopped time is not part of the expedition's time).
- **Rescan** recomputes an expedition from the journals between its start and its end. Activity while it was paused, or stopped between a stop and its restart, is left out because nothing was counted then.

**Limits**

| Information | What the game provides | Workaround |
|---|---|---|
| Earnings at the time of a scan | Credits are paid when the data is sold at a station | Sell the data. The unsold estimate shows the value waiting |
| Counting while EDMC was closed | The journal is read live. Events written while EDMC was closed are not seen | Press **Rescan** on the expedition |
| Which sale was for which expedition | The game reports a sale, not what it covered | A sale counts for the expedition running at the time of the sale |
| The exact value of a map | The journal gives the figures the estimate uses, not the payout, which is reported at the sale | The sale reports the exact figure in the earned total |

## System targets and Body info

System targets and Body info are two cards on the game screen for working a system. Both are off by default, have no panel button and are set up under **Settings → WFMT → Overlays**. They require an overlay ([WFMT's built-in overlay on Windows, or EDMCModernOverlay](../OVERLAY_SETUP.md)). They read the journal and send nothing anywhere, except the two optional lookups on System targets (EDSM and Spansh, below).

**System targets** (Settings → WFMT → Overlays → System targets) lists what remains to do in the current system. Settings:

| Setting | Meaning | Default |
|---|---|---|
| **Enable the System targets card** | Switches the card on | Off |
| **List bodies worth at least** [N] **credits, judged by** [basis] | The threshold (0 to 50,000,000, in steps of 25,000), and whether bodies are judged and ranked by **Mapped value (what scanning and mapping pays)** or **Scan value (what scanning alone pays)** | 100,000, Mapped value |
| **Rows shown** | 3 to 16 rows across all lists; the remaining rows are counted (`+ 3 more`) | 6 |
| **Also list bodies with life that I have not finished analyzing** | The Life list | On |
| **Also list the bodies I have finished (mapped, and their life analyzed), so I can see where I left off** | The Done list | On |
| **Also look up bodies other commanders have scanned (EDSM, once per system)** | See below | Off |
| **Also look up the life and points of interest other commanders found in the system (Spansh, once per system, on arrival)** | See below | Off |
| **Test Card** | Draws a made-up system, to view and place the card | |

The card is drawn in lists under the heading, each headed with its count: **To map (n)**, **Life (n)**, **Known (n)** and **Done (n)**.

- After bodies are scanned, the card lists the planets and moons worth mapping that are not yet mapped.
  - These are the bodies whose estimated value is at or above the threshold (100,000 credits by default), most valuable first.
  - The value is by default what scanning and then mapping the body pays, so a body is ranked by what mapping it earns. The setting in Settings → WFMT → Overlays → System targets switches this to the scan alone.
  - Each row has the body's short name (`A 1`), a tag for the classes that matter (`ELW`, `WW`, `AW`, `HMC`, `MR`, and `TF` for any other terraformable world) and the value (`1.2M`, with `first` when nobody had discovered it).
- Below that, the card lists the bodies with life that are not finished analyzing, as `1/3 life`.
- A body leaves the list when it is mapped or its last organism is analyzed.
- The card's heading is the system name with a progress bar for the system scan and a count (`4 of 8 scanned`) once a honk has occurred.
- A message states when nothing at or above the threshold remains. Before the FSS has found every body it reads `Nothing over 100k to map yet`. Once the game reports every body found it reads `Nothing over 100k left to map or sample`. While the Spansh lookup runs it reads `Looking up data (Spansh)...`. If Spansh has nothing: `Spansh has nothing on this system`. If the lookup failed: `Spansh lookup failed; will retry`. A long message continues on the next line.
- With the EDSM lookup on, the heading's count gains `· 3 online` for the bodies that came from EDSM.
- Each row shows the body, a muted tag and distance (`HMC  82k ls`) or the genera once known, and the value on the right.
- **Also look up bodies other commanders have scanned** (off by default).
  - After a honk, WFMT asks [EDSM](https://www.edsm.net/) once for the system's planets. It sends only the system name (see [What goes on the internet](internet-and-privacy.md)).
  - It lists the bodies above the threshold with their estimated value, marked `EDSM`, before any local scan.
  - The commander's own scan then replaces the EDSM data, and the Body info card shows such bodies as `From EDSM, not scanned by you`.
  - EDSM does not state who has mapped a body, so a looked-up body stays on the list until the commander maps it.
- **Also look up the life and points of interest other commanders found in the system** (off by default).
  - On arrival in a system (or when ticked while in one), WFMT asks [Spansh](https://spansh.co.uk/) once for the system's record. It sends only the system's number (see [What goes on the internet](internet-and-privacy.md)).
  - The card then shows a **Known** section for the bodies where other commanders found life or a point of interest, before any honk or scan.
    - Life appears as `3 b  Fungoida Setisis x2 +1`, with the reward for the life on the right (`2.6M`).
    - A wreck, a beacon or a Guardian site appears as `POI`.
  - The heading line reads `Known (Spansh): 1 with life · 3 points of interest`. It replaces `Nothing over 100k to map yet` when there is anything to show.
  - A body where the commander found life stays on the Life list, and a body whose life is finished leaves the Known section.
  - Spansh holds only what other commanders have uploaded. A system nobody has scanned shows nothing, and a body scanned by someone else shows its life only if they landed and scanned it.
  - Settlements, geysers and vents are not listed.
- **Previous visits.** A line under the heading reads `First visit here` or `Been here 3 times before · last 10 Oct 2026 · you scanned here`.
  - WFMT builds this from the journals of the active commander only.
  - The first time, it reads all finished journals in the background. The card reads `Reading your journals for a visit history (n%)`. Afterwards it reads only new journals.
  - The history is kept in `system_history.json` and nothing is sent anywhere.
  - A visit is counted when the commander arrives somewhere other than the last location, so a relog in the same system is not another visit.
  - Only journals that still exist are counted.
- Under the heading a **summary line** shows progress (`1 mapped · life 1 of 3 done · 4 of 9 analyzed`). It counts the bodies with life that are finished, and every biological signal in the system that has been analyzed.
- A third section, **Done**, lists the bodies that are finished (mapped, and any life analyzed) as `2 d  mapped · life 3/3`. The Done list can be switched off.
- **Returning to a system.** WFMT keeps each system's survey between sessions (the 60 most recently visited systems, kept separately for each commander). Leaving a system, logging out or visiting it again later restores the card.
  - For a system scanned while EDMC was closed (found empty on login), WFMT rebuilds the survey from the journals.
  - It uses the active commander's journals, those the visit history identifies as holding the visits.
- **Rows shown** (3 to 16, default 6) caps the list, and the remaining rows are counted (`+ 3 more`). The life list can be switched off.

**Example: a new system**

1. Under **Settings → WFMT → Overlays → System targets**, tick **Enable the System targets card** and press **Test Card** once to place it.
2. Jump into a system and honk. The heading shows the system name with a progress bar and a count such as `4 of 8 scanned`.
3. As bodies are scanned, those worth at least 100,000 credits appear under **To map (n)**, most valuable first, each with a short name (`A 1`), a tag (`ELW`, `WW`, `HMC` and so on) and a value such as `1.2M`.
4. Bodies with unfinished life appear under **Life (n)** as `1/3 life`.
5. Mapping a body removes it from **To map**. Analyzing the last organism of a body removes it from **Life**. Finished bodies are listed under **Done (n)**.
6. When the list is empty the card reads `Nothing over 100k to map yet`, or `Nothing over 100k left to map or sample` once the game reports every body found.

**Body info** (Settings → WFMT → Overlays → Body info) describes one body. It shows:

- the name and class;
- flags (`Undiscovered`, `Terraformable`, and `Unmapped`, `Mapped before` or `Mapped by you`);
- the materials, written as element symbols (`Fe 18.4% · S 18.2%`);
- the estimated scan value, temperature, gravity (in the warning color at 2.0 g and over), pressure, atmosphere and its composition (formulas such as `CO2`), volcanism, life signals (how many, how many are done, and the genera once the body is mapped), geology signals and distance.

The card shows the body targeted in the galaxy or system map or the nav panel, and the body the commander is close to. The targeted body takes precedence when both apply. A targeted body that is finished (mapped by the commander, with all life analyzed) is not held on the card, which moves on to the next. A targeted body that has not been scanned shows its name with `Scan required`, and the number of life signals if the system scan gave one.

Settings (**Settings → WFMT → Overlays → Body info**):

| Setting | Meaning | Default |
|---|---|---|
| **Enable the Body info card** | Switches the card on | Off |
| **Show the body I have targeted** | Follows the destination set in the map or nav panel | On |
| **Show the body I am close to** | Follows the body the game's `Status.json` reports as nearby | On |
| **Element and compound names** | **Symbols (Fe, CO2)** or **Full names (Iron, carbon dioxide)** for materials and atmosphere gases | Symbols |
| **Test Card** | Draws a made-up body | |

On the card, **Scan value** shows `first` after the amount when nobody had discovered the body. **Mapped value** (with a `~`) shows until the body is mapped. The distance from the arrival star is the badge at the right of the title (`3,936 ls`). A **Footfall** row reads `First: exobiology pays 5x` on a body with life that nobody has stood on.

**Limits**

| Information | What the game provides | Workaround |
|---|---|---|
| A body listed as soon as the honk occurs | The honk gives only a count. A body's class and mass come with its scan (the system scan or a detailed scan), so a body appears when it is scanned. | Scan the bodies, or tick **Also look up bodies other commanders have scanned**. |
| Bodies in a system nobody has scanned | The EDSM lookup knows only what other commanders have uploaded. A system nobody has surveyed returns nothing. | Scan the bodies. |
| Whether a body has been stood on | The scan's `WasFootfalled` states whether anyone has set foot on a landable body. WFMT flags a first footfall (Body info: `First footfall`, and the five times exobiology reward; System targets: `FF` on a life row). The flag reflects the scan made; a body scanned by someone before the commander but not yet footfalled in the data may show as footfalled. | The flag is an indication. The in-game body info is authoritative. |
| What mapping pays | **Scan value** is the estimated value of scanning (the same estimate as the [Exploration Value](#exploration-value) readout). Body info's **Mapped value** is the estimate of scanning and mapping with an efficient probe run. The System targets list is ranked by the mapped value by default (the scan value if selected in Settings). | The threshold indicates which bodies are worth a probe run. |
| The kinds of life before mapping | The system scan gives the number of biological signals. The genera are given when the body is mapped. | Map the body. |
| Remembering a system after a restart, a relog or a later visit | The survey of each system is saved for each commander and merged back on return. For a system with no saved survey, it is rebuilt from the journals that hold the commander's visits (found through the visit history). | None required. Bodies the journals never recorded (a system never scanned) cannot be recovered. |
| Life and points of interest in a system not scanned | The journal knows only what the commander scanned. Spansh holds what other commanders uploaded. | Tick **Also look up the life and points of interest other commanders found**. A system nobody has scanned shows nothing, and the card reads `Spansh has nothing on this system`. |
| The visit line immediately after installation | The history is read from the journals once, in the background, and the line waits for it (`Reading your journals for a visit history`). Only journals that still exist are counted, and a relog in the same system is not a second visit. | Wait for the first read to finish. |

**When the cards show.** The cards follow the commander and the situation.

- They are hidden in hyperspace, while docked or on a carrier, when the game is closed or at its main menu (including while another commander signs in).
- A different commander loading in starts with a clean state.
- They return on arrival in a system.
- The overlay draws the cards over the game window. The overlay's own settings determine whether they show when another window has focus.

The position of each card is set on **Overlay Placement** ("System targets" and "Body info"). They start in the lower middle of the right half of the screen, one above the other.

The Exobiology cards (bio status, predicted species, the sample radar and the sample popup) are described in the [Exobiology guide](exobiology.md#the-overlay-cards).

## Exploration Dashboard

The Exploration Dashboard is a window that presents the information the overlays draw on the game screen.

The **Dashboard** button in the Dashboard section of the Exploration panel opens it. The section also holds the [Exploration Value](#exploration-value) lines and a one-line summary of the system beside the button (its name, the number of bodies worth mapping and the number with life still to do). The window shows:

- the current system;
- the body the commander is on;
- the biology on it;
- the exploration so far.

The window reads only what other features already hold (the system survey, Organic Scanning, the Expedition Log, the Route). It sends nothing anywhere.

It opens on the tab that suits the commander's situation, and switches by itself on landing (to **Surface**) and on lift-off (back to **Orbit**). It switches only while **Orbit** or **Surface** is selected. A selected **Overview** or **Exploration** tab stays.

**Tabs**

- **Overview**: the system in numbers, and the expedition in a few lines.
  - The system: bodies scanned of the honk's count, planets mapped, the number worth mapping at the System targets threshold, biological signals analyzed, the scan value of what has been scanned, what mapping would add, first discoveries.
  - *This system* and *You* (location, altitude, position, heading, fuel).
- **Orbit**: every body in the system in a sortable table.
  - Columns: **Body**, **Type**, a small tag for the classes that matter, **Distance** (light-seconds from the arrival star), **Gravity**, **Landable**, **Atmosphere**, **Temp**, **Scan value**, **Mapped value**, **Bio** and **Geo** (signal counts) and **Status** (what has been done with the body). Clicking a heading sorts by it.
  - Rows are tinted: a green background for nothing left to do, orange text for worth mapping, green text for unfinished biology.
  - Clicking a row shows that body in full (conditions, atmosphere gases, materials, signals, genera, value).
  - Beside the table: **Worth mapping**, **Life to analyze** and **Found by others** (what Spansh lists in the system, when the lookup under Settings → WFMT → Overlays → System targets is on).
- **Surface**: the body the commander is on or near.
  - The location (and the distance of the ship and SRV), the body's conditions and materials.
  - The exobiology: each genus with its possible species and pay (an even share per candidate, as on the Biology card).
  - Progress as `Collecting: 1/3` (the Log, Sample and Analyse scans make three; `Analyzed: 3/3` once paid out).
  - The distance from the last sample and the distance required.
  - The reward range, with the first footfall bonus applied where it counts.
  - The specimens scanned with the Composition Scanner (a plant, a fungus, a shard and so on), with their distance and direction from the commander.
- **Exploration**: the running expedition in full, the route and the Exploration panel's own readouts.
  - The expedition: time, systems, jumps, distance, bodies, first discoveries, maps, landings, Codex entries, samples and species, earned and unsold.
  - The route: fuel, range, jumps left, the next supercharge.

**Example: a landing**

1. Press **Dashboard**. The window opens on the tab that suits the situation.
2. On landing it switches to **Surface**. The tab shows the body's conditions and materials, each genus with its possible species and pay, and progress such as `Collecting: 1/3`.
3. It also shows the distance from the last sample and the distance required for the next sample.
4. On lift-off it switches back to **Orbit**, where clicking the **Scan value** heading sorts the bodies by value and clicking a row shows that body in full.
5. A manually selected **Overview** or **Exploration** tab is left unchanged.

**Route Planner.** The window's header has a **Route Planner** button, which opens the [plotter](#route-planner).

**Overlay switches.** The two buttons at the top right of the window, **Exploration overlays** and **Exobiology overlays**, hide and show those cards without changing Settings. Each states what pressing it does: `Exploration overlays: ON - hide`, or (in the warning color) `Exploration overlays: OFF - show`.

- Exploration covers Route, System targets, Body info, Expedition Log, Compass, Discovery Alerts and Notable Bodies.
- Exobiology covers its four cards.
- Hiding clears the cards from the screen and stops them being drawn.
- Showing restores exactly the cards that were switched on.
- The state is not saved: overlays are shown whenever EDMC starts.
- Flight Alerts, Interdiction and the other overlays are not affected.
- **Hide overlays** (all overlays at once) remains in effect on top of this.

**Limits.** The tables show what the journal provided: a body that has not been scanned is not listed, and values are estimates. Spansh's finds appear only when that lookup is switched on. The window does not request data from the game.

## Route Planner

The **Plot** button in the Route Planner section of the Exploration panel (click its title to unfold it), and **Route Planner** in the Dashboard's header, open a window that plots a route with [Spansh](https://spansh.co.uk/)'s **exact plotter** for the current ship. Only the destination is entered. The ship's data is not entered.

**Constraint.** An add-on cannot give the game a route. Each system is pasted into the galaxy map's search and set as the destination in the game, one leg at a time. WFMT places the next system on the clipboard when the route is ready and on each arrival at a system on the route (see *Copying the next system* below).

### Ship

- **Ship data from the journal.** The window shows the data Spansh receives, from the last loadout:
  - the ship's name;
  - the frame shift drive (class and rating);
  - whether a Guardian FSD booster is fitted;
  - the drive's optimal mass (with engineering);
  - whether the drive supercharges (and at 4x or 6x);
  - the cargo carried;
  - the ship's mass, its fuel tank and the drive's fuel figures.
- **There is no jump range to enter.** Spansh computes the range itself, jump by jump, so it accounts for the ship's mass decreasing as fuel burns and for the refuel points.
- Fuel burn does not change the window. Only a new loadout or a change of cargo does.
- **Unknown ship.** The game writes the loadout at login and when the fit changes.
  - If EDMC started after the game, WFMT reads the last loadout from the newest journal when EDMC starts (and again when the window is opened or Generate route is pressed).
  - Only if the journals hold no loadout does the ship block state that the ship is not known yet.
- **No fuel scoop.** The ship block shows whether a fuel scoop is fitted. If there is none and the route has refuel stops, the status line gives a warning after Generate route, because those stops require a scoop. WFMT cannot instruct Spansh to plan without one.

### Plotting a route

- **Source and destination.** The source is the current system (another can be entered when planning ahead). Enter the destination (system names are suggested as typed, if that is switched on). Press **Generate route**.
- **Options**

  | Option | Default |
  |---|---|
  | **Use supercharge** | On |
  | **Use FSD injections** | Off |
  | **Exclude secondary stars** | Off |
  | **Refuel every scoopable** | Off |
  | **Algorithm** | Optimistic. Spansh's others: Fuel, Fuel and jumps, Guided and Pessimistic |
  | **Mark white dwarfs the route passes (asks EDSM)** | Off. See *White dwarfs* below |

  The options are remembered. Spansh starts from a full tank.
- **The route.** A long route can take a minute or two. A bar, a timer and Spansh's status are shown, and **Cancel** stops waiting.
  - The table lists every jump. Columns: **#**, **System**, **Distance (ly)** (this jump), **Left (ly)** (still to go), **Fuel (t)** (in the tank after the jump) and **At this system** (the action there: supercharge at a neutron star, refuel, use an injection).
  - Systems already reached turn green and the next one is marked.
  - The panel button's line states the next step (for example *Next: Colonia Neutron 4 (neutron) · 41 jumps left*).
- **Messages**
  - When a route is ready the window states this, that it was sent to the Route overlay (when that overlay is on), and which system is on the clipboard.
  - At every system reached it states the next system and that it is on the clipboard.
  - At the end it states that the route is finished and will reset.

**Example: a long trip to Colonia** in a ship with a Guardian FSD booster

1. Press **Plot**. The window shows the ship, drive and booster as read from the journal.
2. Keep the source as the current system, enter `Colonia` as the destination and press **Generate route**. Keep **Use supercharge** on. Tick **Use FSD injections** only if the required materials are carried and their use is wanted.
3. Wait for the bar and timer. A long route can take a minute or two.
4. The table lists every jump with **Distance (ly)**, **Left (ly)**, **Fuel (t)** and **At this system**.
5. The first system is on the clipboard. Open the galaxy map, paste it into the search and set it as the destination.
6. After each jump the next system is copied. Paste it again. Systems reached turn green.
7. To keep the trip in one place, press **Start expedition**. The status line reads like `Started 'Neutron Highway from Sol to Colonia': 12 stops. Logging in Expedition Log.`

### White dwarfs

A white dwarf also supercharges the drive. Spansh's plotter handles neutron stars only and cannot be instructed to use white dwarfs.

- With **Mark white dwarfs the route passes** ticked, WFMT asks EDSM, after the route is plotted, which of the route's systems have a white dwarf as main star.
- It marks them *white dwarf: supercharge* in the table, on the Route overlay and in the expedition it creates.
- They are extra boosts and not planned stops. Spansh did not route through them, and its jump counts and fuel figures do not include their boost.
- A system EDSM does not know is left unmarked. If EDSM cannot be reached, the route is shown as plotted with a note stating this.
- WFMT sends EDSM the names of the route's systems and nothing more, only when Generate route is pressed with the box ticked.

### A neutron star that may be a secondary star

Spansh counts a supercharge at any system with a neutron star, even when that star is not the arrival star.

- The *Exclude secondary stars* option acts on the main-star record in Spansh's data. That record comes from submitted scans and can differ from what the game shows. Lalande 25224 is recorded with its neutron star as the main star, while the star named for the system is a different one.
- After a route is plotted, and as the route progresses, WFMT examines the stars of the next dozen neutron stops (it asks Spansh for each system's stars, by system address).
- Where the star named for the system is not the neutron star, WFMT marks the stop **NEUTRON ?** in yellow on the Route overlay, notes this in the table, and states it in the window on arrival.
- The mark means that the supercharge there may require a long flight to a secondary star, and that the next jump, planned for the boost, may take more jumps. The system map shows the actual situation.
- The mark follows a name rule and is a warning. It cannot judge a system whose stars are all named by letter, and a system for which Spansh has no stars is not marked.

### Copying the next system

**Copy the next system to the clipboard automatically** is on by default. It is a single setting, shown on the Exploration panel under the button and in the window, and it is remembered.

- With the setting on, the first system is on the clipboard when the route is ready and the next after every jump.
- The panel line reads *copied* when the next system is on the clipboard.
- With the setting off, **Copy next system** copies on request, **Copy all remaining** copies the remaining systems one per line, and double-clicking a row copies that system.

### The route overlay and clearing the route

- **Route overlay.** A plotted route also shows on the [Route overlay](always-on.md#route-overlay), in place of the game's plotted route, until every jump has been made. Each system's star is in a color, and a message shows when the route ends.
  - The overlay's own switch under Settings → WFMT → Overlays → Route determines whether it is drawn.
  - Its option to mark systems EDSM does not know applies to the neutron route too.
- **Clearing the route.** **Clear route** in the window, or **Clear Route** in the Route Planner section of the Exploration panel (always present), clears everything the Route overlay follows.
  - That is the route plotted here (the panel line, the window's table) and the route followed from the game, so the card closes.
  - The game's own route is not changed in the game. The overlay follows it again after the next route is plotted in the galaxy map, or after a restart.
  - Plotting a new route replaces the old one without clearing.

### Start expedition

**Start expedition** converts the stops still ahead into an expedition in the [Expedition planner](#expedition), starts it and (unless switched off on the Expedition window's **Settings** strip) starts its [Expedition Log](#expedition-log) run, in one press.

- The status line states the result, in green when started (*Started 'Neutron Highway from Sol to Colonia': 12 stops. Logging in Expedition Log.*), and the button reads **Started ✓** for a few seconds.
- The Expedition window, when opened, is on that expedition.
- The stops are the neutron stars, the marked white dwarfs, the refuel stops and the destination, in route order, each with the action there. A neutron star marked as possibly a secondary star carries that warning in its note.
- The expedition is named *Neutron Highway from <start> to <destination>*.
- Pressing the button again for the same route does not create a second expedition. The status line states that the first is running (or paused).
- **Review expedition** opens the Expedition window on that expedition to check the order before starting, and creates it (not started) if none exists.
- An expedition created from a route is a snapshot. Plotting another route, or **Clear route**, does not change an expedition that is running or paused.

### Limits

- Spansh plans for the ship as the journal describes it, from a full tank. If the loadout changes after plotting (a new module, more cargo), the route must be plotted again.
- A drive for which WFMT has no figures is reported in the ship block.
- The route is kept across EDMC restarts (saved on the local computer, one per commander, in `route_planner_route.json`) and continues from the current position on it. A route that was already finished is not restored.
- WFMT sends Spansh the two systems and the ship's numbers, nothing else ([what goes on the internet](internet-and-privacy.md)).
- The Expedition window's **Neutron route** button opens this window.

### Carrier route

The **Carrier route** button in the Route Planner window opens a second window that plans a route for a fleet carrier (or squadron carrier) with Spansh's fleet carrier router.

WFMT reads the carrier from the journal, so only the destination is entered. WFMT reads:

- where the carrier is;
- the tritium in its tank;
- the space it uses.

These come from `CarrierLocation` and `CarrierStats`, which the game writes at login and when Carrier Management is opened.

**Procedure**

1. In the Route Planner window press **Carrier route**. The carrier block shows what the journal states about the carrier. If it reads *not known yet*, open Carrier Management once in the game, or log in again.
2. Check **Carrier** (Fleet carrier or Squadron carrier, if both exist), **Where it is now** (filled in), **Destination system** (enter it; suggestions appear), and the **Space used** and tritium boxes (filled in from the journal; they can be changed).
3. Keep **Work out the tritium I need to start with** ticked to have Spansh state the starting tritium, or untick it to enter the tritium in the tank and in the carrier's market.
4. Press **Generate route**. Spansh computes each jump (up to 500 ly), the tritium each jump uses and where an icy ring exists. The summary states the tritium needed at the start. **Cancel** stops waiting.
5. Work down the table. Columns: **#**, **System**, **Distance (ly)**, **Left (ly)**, **Tank (t)** and **Market (t)** (the tritium in the tank and in the carrier's market after the jump) and **At this system** (for example where an icy ring allows mining tritium).
   - **Copy next system** (or a double-click on a row) puts the next system on the clipboard. Paste it into Carrier Management's jump search and schedule the jump in the game.
   - The route advances when the carrier arrives (green rows are done, the next is marked). WFMT sees the arrival in the journal when the commander is aboard or logs in.

**Controls**

| Control | Function |
|---|---|
| **Generate route** / **Cancel** | Request the route from Spansh / stop waiting |
| **Carrier**, **Where it is now**, **Destination system** | Which carrier, its start and its destination |
| **Space used (t)**, **Tritium in the tank (t)**, **Tritium in the market (t)** | The numbers Spansh plans with (filled in from the journal) |
| **Work out the tritium I need to start with** | Spansh computes the starting fuel, or the values are entered |
| **Copy next system** / **Copy all remaining** | The next system, or every system still to visit, one per line |
| **Mark next as reached** | Advances the route manually, if the carrier jumped while WFMT could not see it |
| **Clear route** | Discards the route |

- The route is kept across EDMC restarts (one per commander, in `carrier_route.json`).
- WFMT sends Spansh only the systems and the carrier's size, space used and tritium ([what goes on the internet](internet-and-privacy.md)).
- A route has one destination.
- The tritium figures are Spansh's, and the table shows the tritium in the tank and in the carrier's market after each jump.

## Nearest place to land

The section starts folded.

Nearest place to land finds the nearest station that can take the ship and offers the required services, and the nearest fleet carriers that allow anyone to dock.

The panel section has a line stating the current system and the pad size the ship requires (`From Sol; your ship needs a large pad.`, or `Needs your position: it comes from your next jump, or from the journal when you log in.`) and a **Find** button that opens the window.

**Procedure**

1. Press **Find**. The window opens with **From** showing the current system and coordinates.
2. Under **I need**, tick the services the place must offer: **Refuel**, **Repair**, **Rearm (restock)** and **Outfitting**. Refuel and Repair are ticked by default. Only stations that offer all the ticked services are listed.
3. Choose the **Landing pad**: **My ship's pad** (the default), **Any size**, **Medium or larger** or **Large only**. With **My ship's pad** WFMT uses the ship's size from the last loadout (a Python is never sent to an outpost with only small pads). A small ship has no restriction because it fits everywhere.
4. Keep **Include fleet carriers open to all, updated within** ticked to list carriers, and choose how recent a carrier's record must be: **7 days**, **14 days** (the default), **30 days** or **90 days**. Unticking it leaves carriers out, and the carrier table then reads `Fleet carriers were not asked for`.
5. Tick **Allow this lookup: pressing Find sends Spansh my position, the pad size and these choices, nothing else**. It is off by default and is the same switch as **Settings → WFMT → Exploration → Nearest place to land**. Nothing is sent before it is ticked.
6. Press **Find**. The window asks Spansh and fills two tables. An answer is remembered for two minutes, so pressing Find again with the same choices sends no new request.

**Example: low on fuel in deep space**

1. Press **Find**. **From** shows the current system and coordinates.
2. Keep **Refuel** and **Repair** ticked and **Landing pad** on **My ship's pad**.
3. Tick **Allow this lookup**, then press **Find**.
4. Read the **Stations** table for the nearest place with a suitable pad (the **Pads** and **Has** columns state what it offers), and the carrier table for carriers open to all. Check a carrier's **Last reported** age.
5. Double-click the wanted row. Its system name is copied. Paste it into the galaxy map.

**Tables.** Up to eight places are listed in each table, nearest first.

| Table | Columns |
|---|---|
| **Stations with <services>** (starports, outposts, planetary ports and outposts, megaships and colonization sites) | **Station**, **System**, **Where** (where in the system), **Distance (ly)**, **Pads** (the pad sizes it has), **Has** (which of the ticked services it offers) |
| **Fleet carriers open to all, reported within <days> days** | **Carrier**, **System**, **Distance (ly)**, **Pads**, **Has**, **Last reported** (how long ago Spansh had a report of it) |

**Double-clicking a row** copies its system name. The status line at the foot of the window states the result and notes that carriers move: the carrier's age must be checked before relying on it.

- **Origin.** The position comes from the journal (`StarPos`, set by each jump), not from a system name, so it works in an uncharted system. If WFMT has not seen a jump this session, it reads the newest journals. If it still has no position, the window reads `Your position is not known yet. Jump to a system or log in first.`
- **Fleet carriers** are listed only when Spansh states that docking is open to everyone, and only if the record is recent, because carriers jump and change who may dock.
- **Network.** The lookup is online, and only when Find is pressed, once the box that allows it is ticked. It sends Spansh the position, the pad size and the choices, and nothing about the commander (see [What goes on the internet](internet-and-privacy.md)). If Spansh cannot be reached, the window states this and suggests trying again.
- The window remembers the choices, its size and its position.

The limits of this feature are listed in the last section of this guide.

## Compass

The section starts folded.

The Compass points at a position on the planet the commander is on, from any position on its surface (on foot or in a vehicle), in any mode. It replaces the arrow that Mining drew for hotspots. A Mining waypoint arrow that was switched on carries over as the Compass, with its position on screen.

Possible targets:

- **The nearest hotspot** recorded on this body (the default). Hotspots without a position are skipped.
- **A mark**: a name, a body and a latitude and longitude, kept for the commander alone (another commander on the same install does not see them) and never sent anywhere. Up to 500 marks can be kept. A name can have 60 characters and a body name 100.
- **Nothing.**

**The panel section** shows a line stating the current target and the distance (`↗ Ship - 340m NE`; the arrow is omitted until the game has given the heading), a box and three buttons:

- **Mark** saves the current position as a mark, named with the text in the box (or `Mark 1`, `Mark 2` ... if the box is empty), then clears the box. The body comes from the game's `Status.json`. Without a surface position it reads `No surface position yet: land, or get out, first.`
- **Target** steps through the targets: the nearest hotspot, then each mark on this body, then nothing, then again. It reads `Now aiming at ...`.
- **Marks** opens the Marks window.

When the target is a mark on another body than the current one, the line states this (`Mark Ship is on <body>, not here.`) instead of pointing.

**Example: returning to a position.** The commander lands by a crashed ship.

1. At the position, enter `Wreck` in the Compass box and press **Mark**. The box clears and the mark is saved with the body and the latitude and longitude.
2. Press **Target** until the line reads `Now aiming at ...` with `Wreck`.
3. The line shows the distance and direction, for example `↗ Wreck - 340m NE`. With **Enable Surface Compass** ticked, the arrow on the screen turns with the commander, and straight up means straight ahead.
4. To check or edit the mark, press **Marks**, select it and use **Save** or **Delete**. In that window, **Nearest hotspot** and **Nothing** change what the compass points at.

**The Marks window.** The table lists every mark with the columns **Name**, **Body**, **Latitude**, **Longitude** and **From here** (the distance from the commander, when the mark is on the same body). Under the heading **The compass points at:** (with the current target) are three buttons: **Nearest hotspot**, **Selected mark** and **Nothing**. The editor is below the table:

1. Press **New mark** (in the header) or select a mark to change it.
2. Fill in **Name**, **Body** (the bodies of the current system are suggested as typed), **Latitude** and **Longitude**. **Here** fills in the commander's position and body. A position can also be typed, for example from a guide or a screenshot.
3. Press **Save**. **Delete** removes the selected mark; it requires two presses, since a deleted mark cannot be recovered.

**Arrow on the game screen.** Tick **Settings → WFMT → Overlays → Surface Compass → Enable Surface Compass** (off by default) and press **Test Compass**. The position is set on **Overlay Placement** ("Surface compass"). The overlay card is one line of text (an arrow glyph, the name, the distance and the compass point) with a drawn arrow under it that turns with the commander, so straight up means straight ahead.

The distance and direction are great-circle values on a sphere the size of the body (from the body's radius in `Status.json`). The compass points only at targets on the current body and shows nothing until a surface position is available.

## What the game does and doesn't tell us, and how to work around it

WFMT knows only what Elite Dangerous writes to its journal files.

- It adds what EDSM, Spansh, Canonn and edastro report.
- Where a value is uncertain, WFMT labels it.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| Information | What the game provides | Workaround |
|---|---|---|
| A stop recorded as visited while the game was not running | Arrivals are counted that the journal reports while the expedition is running (Start). A system reached while it was paused, or before it was started, is not ticked. | Use **Mark visited**. |
| Scans counted in a system that is not a stop, or at a stop not yet reached | Survey counts go to a stop that has been reached, in the system where the scan happened, while the expedition is running. | Add the system as a stop, or use **Mark visited** for a stop reached while paused. |
| The distance to the next stop on every stop | A distance needs a position for both ends. The game gives the commander's position on every jump. A stop has a position only if it came from a plotted route or EDSM. | Press **Locate and reorder (EDSM)**. A stop EDSM does not know shows `-`. |
| Carrier jumps in the jump total | A fleet carrier jump is not the ship's jump, so it ticks stops but does not add to the jump count or the light-years. | None required. |
| The light-years as the whole route | Each jump's own distance is added as the game reports it, so the total is the distance flown and not the straight line between stops. | None required. |
| A note's body | The body comes from `Status.json` (`BodyName`), which the game writes only near a body, and not in supercruise between bodies. | Press **Here** in the Notes window beside Body, or enter the name. A note can be about the system alone. |
| A carrier that has only just jumped, or one whose docking access Spansh does not know, in Nearest place to land | Spansh reports a carrier as last seen (when a commander's EDMC sent it), and a carrier's docking access is in the data for only some carriers. A carrier whose access is not "All", or not known, is left out. | Check the age shown for a carrier. For a carrier to try, request docking on arrival. |
| A station's current state in Nearest place to land | Spansh's records are what EDMC users last reported. A station that was attacked, or a carrier that moved, can differ, and a place nobody has visited recently may not be listed. | The list shows candidates; the current state is confirmed in the game. |
| The compass in space or in a ship above the ground | The game gives a latitude and longitude only on a landable surface (on foot or in a vehicle). | Land or leave the ship. |
| A mark's body | The body comes from `Status.json` (`BodyName`), which the game writes only near a body. Marks are matched by body name. | Use **Here** at the position, or enter the body's full name as the game shows it. |
| Auto-Honk pressing any control | Only **keyboard** keys can be pressed, so the fire button must be bound to one. On Linux it needs `xdotool`; Wayland without XWayland is unsupported. | Bind a keyboard key to the fire button and use **Rescan** after changing bindings. |
| Auto-Honk detecting that the honk worked | WFMT presses the key and reports only that the key press was sent. The game's `FSSDiscoveryScan` event is what the rest of WFMT uses to detect a honk. | If nothing happens in the game, press **Rescan** and **Test Honk Now**, and check the status line. |
| A first-to-map banner for a body whose scan was not seen | The mapping event carries no "mapped before" flag. WFMT takes it from the same body's earlier scan in this system. | Scan the body (or let the system scan reach it) before mapping. |
| The Route Planner or Carrier route setting the game's destination | An add-on cannot give the game a route. The journal and `NavRoute.json` only report what was plotted. | Paste each system into the galaxy map (or Carrier Management). WFMT keeps the next one on the clipboard. |
| The Route Planner's fuel figures including a white dwarf boost | Spansh's plotter handles neutron stars only. | White dwarfs are marked as extra boosts only when the EDSM option is ticked; the jump counts do not include them. |
| Boxel Survey knowing where a system is | It works with names, not coordinates. It counts through the trailing number to make the next name and does not know whether that system exists. | The galaxy map decides. Press **Next >** to skip a name that does not plot. |
| The game reporting that a candidate failed to plot | Nothing is written to the journal when the galaxy map cannot find a name. | After 3 skips WFMT asks EDSM for a real nearby system. Press **Set** to move there. |
| Whether anyone has flown to a system Random offers | Random offers real systems with no scans on Spansh or EDSM. A visit without a scan leaves no trace in either. | The first scan uploaded settles it. |
| A cube's real system count | WFMT knows only what EDSM, Spansh and the commander's visits revealed, so "complete" means every known system is done, or the cube is marked **Empty**. | Use **Mark Empty** for a cube judged done. |
| The color of a gas giant | The game does not record it. The Green gas giant rule uses the Codex or matches the surface temperature of a confirmed green one. | The result is a lead; check the body in the system map. |
| Certainty of Notable Bodies matches | A match comes from scan data, using its fixed limits. | Check the body before planning around it. |
| Organic Scanning naming the species | Until a sample names it, the result is a list of candidates derived from the planet's conditions. The main star is used as the illuminating one, which can be wrong near a secondary star. A species with no usable rules cannot be predicted, and new species need a WFMT update. | The first sample replaces the list with the exact species. The in-game exobiology tools are authoritative. |
| Systems visited with EDMC closed | The journals record every jump, so each start reads the last 14 days of journals for arrivals and adds them to the visited list used by **Skip systems already visited** and **Random**. | None required for the last 14 days. Older jumps made with EDMC closed are not found. |
| The bodies-scanned count after a restart | The honk (`FSSDiscoveryScan`) gives the body count and each scan counts one. If EDMC started after the honk, WFMT replays the current journal file for them. | If the display still prompts for a honk, honk again. A system's scans made in another journal file are not included. |
| The sale line including sales before the current journal file | It is read from the current journal file when EDMC starts, then kept up to date live. | It resets to "none yet" when EDMC is restarted after a new game session. |
| Codex Completionist covering everything | Canonn's catalog has no geological or anomaly entries, so these never appear under **Not found**. The tally is per commander. | Use the game's Codex for those entries. Press **Refresh Catalog** if the saved copy is old. |
| Current POI lists | They are snapshots from Canonn and edastro and are fetched only on request. | Press **Find POI** or **Update POI** to refresh. |
| A nearest lookup done by edastro | WFMT does not ask edastro for the nearest point. It downloads the full list and computes the nearest from the position. | None required. If Find POI states that the lookup failed, edastro's list could not be downloaded; try again later. |
