# Exploration

Exploration mode is one scrolling panel (press **Explore** in the mode row to show it). It has a row of buttons at the top, then several sections stacked top to bottom in
alphabetical order of their names (in every mode the sections are alphabetical, so one can be found without scanning).

- **The top row** holds **Auto-Honk** (Auto-Honk), **Discovery Alerts** (Discovery Alerts), **Neutron Star** and **White Dwarf** (nearest neutron star and white dwarf) and **Random** (a system nobody
  has scanned). A short status line under it reports Discovery Alerts and the last Neutron Star or White Dwarf answer.
- **The sections** are Boxel Survey, Codex Completionist, Compass, Dashboard, Expedition, Nearest place to land, Notes, Organic Scanning, POI Reference and Route Planner.
- **Folding.** Every section with a ▸ / ▾ in its title starts folded: click the title to open it. A section you open stays open until EDMC restarts, and
  every section is folded again at each start, so the panel is the same short height every time.
- **Long values never widen EDMC's window.** Names, notes and results in this panel wrap or are cut to a fixed length, so a long system name cannot make the main window wider.

**Where the settings are.** Everything is under **Settings → WFMT**:

| Feature | Settings page |
|---|---|
| Auto-Honk | Exploration → Auto-Honk |
| Boxel Survey, Region Sweep, Waypoint Route | Exploration → Boxel Survey (one page, the three sections one under another) |
| Expedition | Exploration → Expedition |
| Exploration Value | Exploration → Exploration Value |
| Nearest place to land | Exploration → Nearest place to land |
| Organic Scanning | Exploration → Organic Scanning |
| POI Reference and Codex Completionist | Exploration → POI Reference (the Canonn, edastro and Codex sections one under another) |
| Discovery Alerts, Notable Bodies | Overlays → Discovery, Overlays → Notable Bodies |
| System targets, Body info, Route, Expedition Log card, Surface Compass, Exobiology cards | Overlays → the page of the same name |
| Where each card sits, its colors and the overlay connection | Overlays → Overlay Placement, Appearance and Overlay Connection |
| Local star index and the online lookups | General → Online lookups |
| Keyboard shortcuts and chat commands | General → Shortcuts |

**Where this comes from:**

- Your scans, jumps, honks and Codex finds come from the journal, so everything about *your* exploring is exact.
- The journal can't say which systems exist or are unvisited, a gas giant's color, or which species a planet hosts before you sample it.
- Those are filled from what EDSM, Spansh, Canonn and edastro report, or worked out and labeled as a lead to check.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

**On this page:** [How to: the common tasks](#how-to-the-common-tasks) · [Auto-Honk](#auto-honk) · [Discovery Alerts](#discovery-alerts) ·
[Notable Bodies](#notable-bodies) · [Boxel Survey](#boxel-survey) · [Exploration Value](#exploration-value) ·
[Organic Scanning](#organic-scanning) ([Exobiology guide](exobiology.md)) · [Codex Completionist](#codex-completionist) ·
[POI Reference](#poi-reference) · [Notes](#notes) · [Expedition](#expedition) · [Expedition Log](#expedition-log) · [System targets and Body info](#system-targets-and-body-info) · [Exploration Dashboard](#exploration-dashboard) · [Route Planner](#route-planner) ([Carrier route](#carrier-route)) · [Nearest place to land](#nearest-place-to-land) · [Compass](#compass) ·
[What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)

Anything that draws on your game screen needs an overlay. See [Getting started](getting-started.md#what-you-need)
and [Setting up the overlay](../OVERLAY_SETUP.md).

## How to: the common tasks

Short step lists for the things players ask for most. Each links to the section with the full detail and a worked example.

**Set up auto-honk** ([details](#auto-honk))

1. Open **Settings → WFMT → Exploration → Auto-Honk**.
2. Tick **Enable Auto-Honk**, and set **Fire button** to the one your Discovery Scanner is on.
3. Press **Test Honk Now** and read the result beside the button.
4. Jump into a system. The scanner fires once on arrival.

**Use the Boxel Survey** ([details](#boxel-survey))

1. Open the **Boxel Survey** section and choose **Sequence**.
2. Type a procedural system name into **Seed system** (or press **Use Current**) and press **Set**.
3. Press **Copy**, paste the target into the galaxy map and jump.
4. On arrival WFMT marks the system visited and moves to the next name. Press **Next >** to skip a name the galaxy map cannot find.

**Read the System targets card** ([details](#system-targets-and-body-info))

1. Tick **Enable the System targets card** under **Settings → WFMT → Overlays → System targets** and press **Test Card**.
2. Honk and scan in a system. The card lists **To map**, **Life**, **Known** and **Done**.
3. Map a body or analyze its last organism and it leaves the list.

**Use the Codex Completionist** ([details](#codex-completionist))

1. Open the **Codex Completionist** section and press **My Codex**.
2. On the **Overview** tab read **Closest to complete** to see which types are quickest to finish.
3. On the **Not found** tab read **Where to look** to choose a planet.
4. Press **Backfill Journals** once to bring in older finds.

**Use the Route Planner** ([details](#route-planner))

1. Press **Plot** in the Route Planner section.
2. Type the destination and press **Generate route**.
3. Open the galaxy map and paste the system that is on your clipboard. Repeat after every jump.

**Use the surface compass** ([details](#compass))

1. Land (or get out of your ship) on a planet.
2. Type a name in the Compass box and press **Mark** to save the spot.
3. Press **Target** until it says `Now aiming at ...` and your mark.
4. Tick **Enable Surface Compass** under **Settings → WFMT → Overlays → Surface Compass** to see the arrow on your screen.

**Use the Dashboard** ([details](#exploration-dashboard))

1. Press **Dashboard** in the Dashboard section.
2. Read the tab that opens (**Orbit** in space, **Surface** when landed), or pick **Overview** or **Exploration**.
3. Click a heading on the **Orbit** tab to sort the bodies, and click a row for that body in full.

**Write a note** ([details](#notes))

1. Open the **Notes** section, type a line in the box and press **Add Note**.
2. Press **Notes** to search, change or delete notes.

**Find somewhere to land** ([details](#nearest-place-to-land))

1. Press **Find** in the Nearest place to land section.
2. Tick what you need, tick **Allow this lookup**, and press **Find**.
3. Double-click a row to copy its system name.

**Find a point of interest** ([details](#poi-reference))

1. Press **Find POI** in the POI Reference section.
2. Paste the system name that is now on your clipboard into the galaxy map.

## Auto-Honk

Fires your Discovery Scanner automatically every time you jump into a system, so you never forget to honk.

**How to use it:**

1. Turn it on with its toggle button (**Auto-Honk**, which is highlighted while it is on) or the **Enable Auto-Honk** box in Settings. It is **off by default**.
2. Open **Settings → WFMT → Exploration → Auto-Honk** and set:
   - **Fire button**: **Primary** or **Secondary** (the default is Secondary). This is the Elite control WFMT looks up in your key bindings, so pick the one your Discovery Scanner is on.
   - **Hold (sec)**: how long the key is held down. The default is 10. The Discovery Scanner charges while the button is held and fires only when it is full, so a quick tap does nothing; the charge time depends on your scanner and its engineering. A value under 1 second is saved as 1 second.
   - **Focus game window first** (on by default): brings the Elite window to the front before pressing the key. Turn it off only if you want WFMT to press the key into whichever window already has focus.
   - **Skip systems already visited** (on by default): see below.
3. Read the status line under the options. It says which key WFMT will press (`Status: Will press <key> when you jump into a system.`, in green) or why it cannot (in amber). Press **Rescan** after you change your bindings in the game, or after you change the fire button here, to read them again.
4. Press **Test Honk Now** to press the key at once and check it works without waiting for a real jump. The result appears beside the button (`Last test (Test): sent`, or the reason it failed, such as `Elite Dangerous window not found`). **Rescan** and **Test Honk Now** work even while Auto-Honk is off.

**Example: setting it up.** Your Discovery Scanner is on the keyboard key `U`, bound as the secondary fire.

1. Open **Settings → WFMT → Exploration → Auto-Honk**, tick **Enable Auto-Honk** and leave **Fire button** on **Secondary**.
2. Press **Rescan**. The status line turns green and reads `Status: Will press U when you jump into a system.`
3. Press **Test Honk Now** with the game running. Beside the button you see `Last test (Test): sent`.
4. Jump to the next system. WFMT presses `U` once for the arrival. If you jump away and straight back, it does not honk that system a second time in the same session.

**When it fires.** On every jump into a system (`FSDJump`) and every fleet carrier jump (`CarrierJump`) while Auto-Honk is on. It does nothing at any other time, and it presses the key once for each arrival.

**What *Skip systems already visited* means.** WFMT remembers the systems it has honked in since you loaded into the game, and does not honk the same system twice in that session (for example when you jump away and straight back). The memory is cleared each time you load a game. It is not a record of your whole travel history.

**What it can and cannot do.**

- It presses a **keyboard** key. If the fire button you chose is bound only to a joystick or HOTAS button, the status line says so and nothing is pressed; bind a keyboard key to it in the game, or switch to the other fire button.
- If the fire button is bound to nothing in your active control preset, or to a key WFMT does not know how to press, the status line says so.
- If WFMT cannot find or read your Elite controls file, it says that instead. It reads the most recently saved `Custom.<version>.binds` file of the preset named in `StartPreset.start`.
- It does not check what your ship is doing. If you are in a ship with no Discovery Scanner, or the game has a menu open, the key press simply does nothing useful.

If another program also fires your Discovery Scanner for you (some co-pilot apps do), turn one of the two off, or they'll fight each other. The status line warns you when it sees a known co-pilot program running.

*On Linux this needs `xdotool` and a keyboard key bound to your fire button. A second box, **Elite Wine/Proton prefix**, tells WFMT where Elite's prefix is if it cannot find it from Steam by itself (leave it blank to auto-detect). See [WFMT on Linux](linux.md).*

## Discovery Alerts

Puts a banner on your in-game screen the moment you jump into a system nobody has scanned, or the moment you're the
first to scan or map a body.

**How to use it:**

1. Click its toggle button (**Discovery Alerts**) or tick **Enable Discovery Alerts** in **Settings → WFMT → Overlays → Discovery**. It is **off by default**.
2. Make sure an overlay is running. The connection details are on the **Overlay Connection** tab under Settings → WFMT → Overlays.
3. Press **Test Discovery** on the Discovery page to send both banners (it works even while the feature is off and says whether an overlay could be reached), and use **Settings → WFMT → Overlays → Overlay Placement** to move them. By default they sit at the top center.

**What you see.** Two banner cards, one under the other:

| Banner | Shown when | Stays up |
|---|---|---|
| **NEW SYSTEM DISCOVERY**, with the system name | You jump into a system and the game's automatic scan of the arrival star says nobody had scanned that star before (`WasDiscovered` is false) | 12 seconds |
| **First scan of a new discovery** or **First to map this body**, with the body name | A body you scan (or map) was undiscovered, or unmapped, when you did it | 8 seconds |

The status line under the buttons on the panel says the same in text (`New system: ...`, `Scanned first: ...`, `Mapped first: ...`), or `Watching for new discoveries...` when there is nothing to report.

**What it does not do.** It stays silent for a system or body that was already discovered, since that is the usual case. The first-to-map banner needs the body's own scan to have been seen earlier in the system, because the mapping event does not say whether the body had been mapped before; a body whose scan WFMT did not see (for example because EDMC was closed) is not announced.

### Neutron Star and White Dwarf buttons

Next to the toggle, these find the nearest system whose *primary* star is a **neutron star (Neutron Star)** or a **white
dwarf (White Dwarf)**, measured from where you are now. They show the system name and distance, and copy the name to your
clipboard so you can paste it into the galaxy map.

They are manual only: they contact Spansh when you click and never on their own. Jump or reload first so WFMT knows
your position.

**What you see.** After the click the line under the buttons reads `Neutron Star: searching...` and both buttons are grayed until the answer arrives. The answer reads like
`Neutron Star: Sample Sector AB-C d1-2 - 84.3 ly, Spansh (copied)`: the system, how far it is, which source answered (**Spansh** or **local index**, see below) and `(copied)` once the full name is on your clipboard. A name longer than the panel allows is cut with an ellipsis on the panel only; the copy is always the whole name. The system you are in is never offered as the answer.

- `position unknown - jump or reload first` means WFMT has not yet seen a jump or login that gave it your coordinates.
- `lookup failed - see EDMarketConnector.log` means Spansh could not be reached or answered something WFMT could not read.
- Only the **primary** (main) star of a system counts, and **White Dwarf** accepts a white dwarf of any class.

### The local star index

**Neutron Star can answer from a file on your computer.** This is an optional enhancement.

- WFMT works fully without it, and nothing is downloaded unless you press a button.
- It speeds up and takes load off the features that look for neutron stars (today the **Neutron Star** button) by answering from a local file instead of a request.

**Setting it up.** In **Settings → WFMT → General → Online lookups**, the **Local star index** group has **Download and build**.

1. It downloads one public file from Spansh's download server (about 173 MB, once).
2. It builds an index of the neutron stars from it. The index is about 110 MB on disk. Building needs about 300 MB more free space for a few minutes, and the downloaded file is deleted afterward.
3. From then on **Neutron Star** looks in that index instead of asking Spansh. The result line says which answered: *local index* or *Spansh*.

The download starts only when you press the button. WFMT never fetches it by itself.

**The buttons and the tick.**

- **Update** keeps the index current by fetching only what changed.
  - It fetches one of Spansh's small update files (about 3 MB for a day, 19 MB for a week) and merges it in.
  - It fetches the whole file again only when the index is more than a week behind, after 20 updates, or when the base file is more than 60 days old.
  - Pressing it twice in a day downloads nothing the second time.
- **Cancel** stops a download or a build.
- **Delete** removes the index.
- The tick **Use the local index for Neutron Star when it is installed** is on by default and can be turned off at any time. With it off, or with no index, **Neutron Star** asks Spansh as before.

What the index does and does not cover:

- **Neutron stars only.** **White Dwarf** has no local index and always asks Spansh.
- **Main stars only.** The file lists a system's main star, so a neutron star that is a secondary star of its system is
  not in the index, the same as in the Spansh search Neutron Star otherwise makes.
- **As old as the file.** The index holds what Spansh's file held on the date shown in the status line (Spansh updates the file
  regularly); a system added since then is not in it until you press **Update**. Positions are kept to 1/32
  light year, the precision of the data.
- **Within 5,000 light years.** If the index has no neutron star that near, Neutron Star asks Spansh.
- **No region name.** The local answer gives the system and the distance only.
- **If the file cannot be used.** An index that is cut short, damaged or made by another version of WFMT is ignored, the
  status line says so, and Neutron Star asks Spansh until you download it again.
- **Disk and folder.** The index is kept in the plugin folder (`star_index`), which must be writable. The updater leaves
  it alone, and it is not part of **Back up my data**; it is the same for every commander and holds nothing about your
  play.

## Notable Bodies

Puts a violet banner on your in-game screen when a body you scan is worth a second look. A match comes from the scan
data, so check the body in the system map before you plan around it. It needs the same overlay as Discovery Alerts.

**How to use it:**

1. Open **Settings → WFMT → Overlays → Notable Bodies**.
2. Tick **Enable Notable Bodies alerts**. It is off until you do.
3. Choose which rules you want.
4. Press **Test Notable** to see a sample banner. Move it under **Settings → WFMT → Overlays → Overlay Placement**.

It has no button on the main panel.

### What it looks for

Each rule has a tick box on the Notable Bodies settings page, with a one-line description. The limits are fixed.

| Rule | Matches | Starts |
|---|---|---|
| **Terraformable landable** | A landable body that is terraformable, being terraformed or already terraformed | On |
| **High-value body** | Any terraformable world, and every Earth-like, water and ammonia world, landable or not; the log line says if it is undiscovered or unmapped | On |
| **High-g landable** | A landable body above about 3 g (29.4 m/s²) | On |
| **Shepherd moon** | A moon orbiting inside the outer edge of its parent's outermost ring | On |
| **Good FSD injection** | A landable body with 5 or 6 of the 6 premium FSD boost materials (carbon, germanium, arsenic, niobium, yttrium, polonium) | On |
| **Green gas giant** | A Codex entry that names one, or a gas giant of a class whose surface temperature matches a confirmed green one. The game never records a planet's color, so treat this as a lead, not a fact | On |
| **Colliding binary** | Two bodies sharing a barycenter whose closest approaches are less than their radii apart | On |
| **Large landable** | A landable body over 18,000 km in radius | Off |
| **Landable ringed** | A landable body that also has rings | Off |
| **Close orbit** | A moon whose orbit is under three times its parent's radius | Off |
| **Close binary** | Two bodies orbiting so close to their shared center (radius over 0.4 of the orbit) that they nearly touch, but do not collide | Off |
| **High eccentricity** | An orbit with eccentricity above 0.9 | Off |
| **Fast orbit** | A planet orbiting in under 8 hours | Off |
| **Fast rotation** | A planet with a day under 8 hours that is not tidally locked | Off |
| **Wide ring** | A ring wider than five times the radius of the body it circles | Off |

The last eight start off because they are common.

### How alerts behave

- If a body matches several rules you get **one banner**, for example "High-value body +2".
- A body only alerts **once per rule**.
- Each banner stays up for 6 seconds. Banners take turns if several come at once: up to three wait behind the one on screen, and the body's name on the banner then ends with `(N more)` for the cards still to come. Any beyond three waiting are not shown separately.
- A banner shows two lines: the title of the first rule that matched (with `+N` for the others) over the body's name. The measurements that matched (such as the gravity or the orbit) are written to EDMC's log, not drawn on the banner.
- A Codex entry for a green gas giant raises the same banner (title **Green gas giant**, with the name of the nearest destination) when that rule is on.
- The banner widens to fit the body's name and the rule's title, so a long catalog name shows in full (only text past about 56 characters is cut with "…").
- The limits are fixed defaults.
- It starts at the top right of the screen ("Notable find card" on **Overlay Placement**). If the banner lands on top of other overlay text, move it there.

## Boxel Survey

**Work in progress.** Boxel Survey is still being built, and I'd really appreciate your feedback. Please
[open an issue](https://github.com/rwharpernc/wayfarers-multitool/issues).

A helper for exploring the galaxy system by system, using Elite's procedurally generated system names. A name like
`Outotz LS-K d8-0` has four parts: a sector name (`Outotz`), a three-character cube ID (`LS-K`), a mass-code letter
a to h (`d`), and a number or number pair at the end (`8-0`). The "boxel" is the cube of space that shares the
first three parts; the trailing number picks one system inside it.

The section is **folded by default**: click `▸ Boxel Survey` to open it. Inside, three buttons choose a sub-mode:
**Sequence**, **Region Sweep** and **Waypoints**. WFMT remembers which one you used last.

**What WFMT does and doesn't know.** It works with *names*, not coordinates. It counts through the trailing number
to make the next candidate name, and it does not know whether a candidate actually exists. The in-game galaxy map
is what tells you. Real positions only come from EDSM or Spansh lookups.

### Which sub-mode should I use?

| If you want to... | Use |
|---|---|
| Work through one boxel from start to finish, in order | **Sequence** |
| Clear a whole region (several boxels), tracking what's left across all of them | **Region Sweep** |
| Visit a fixed list of specific systems in a sensible order (a rendezvous, a squadron staging route) | **Waypoints** |

If you're not sure, start with **Sequence**. Waypoints is the odd one out: it accepts any system name, not just
procedurally named ones.

All three are remembered **per commander**.

### Sequence

The panel shows a **Target**, **< Prev**, **Next >** and **Copy** buttons, a **Seed system** box with **Use
Current** and **Set**, a **Find Nearby (EDSM)** button, a line of survey counts and a status line.

**To start a survey:**

1. Type a procedural system name into **Seed system** (or press **Use Current** to fill in the system you are in).
   A gray hint under it says whether the name looks like a boxel name.
2. Press **Set**. The seed becomes the first target.
3. Paste the target into the galaxy map (**Copy** puts it on your clipboard) and jump.
4. When you arrive at the target, WFMT marks it visited and moves to the next candidate. With *Auto-copy next
   target to clipboard on jump* on (the default), it also copies that next name for you.

**Example: working through one boxel.** You are in `Outotz LS-K d8-0` and want to survey the systems around it in order.

1. Open the **Boxel Survey** section, choose **Sequence**, press **Use Current** and then **Set**. The gray hint says the name looks like a boxel name, and **Target** shows the seed.
2. Press **Copy**, open the galaxy map, paste the name and plot the jump.
3. Jump. On arrival WFMT marks the system visited, moves **Target** to the next candidate and, with the default *Auto-copy next target to clipboard on jump*, copies that name too.
4. Paste it into the galaxy map and repeat. If the map cannot find a name, press **Next >** to skip it.
5. The line under the buttons keeps your tally of what you found, in the form `Surveyed: N systems | ELW | WW | AW | terraformable | bio`.

**If a candidate doesn't exist:** the galaxy map won't find it. Press **Next >** to skip it. (**< Prev** steps
back; at the very start it says "Already at the start of the sequence".) After **3** manual **Next >** presses in a
row without a confirmed jump, WFMT asks EDSM for the nearest real procedurally named system outside the current
cube, and fills the Seed box with it. It does not switch automatically: press **Set** to move the survey there.

**Find Nearby (EDSM)** does the same lookup on demand. It needs to know your position, so jump or reload first.

**What it keeps.** The line under the buttons counts what you've found in surveyed systems:
`Surveyed: N systems | ELW | WW | AW | terraformable | bio`.

- These come from your scans: Earth-like, water and ammonia worlds, terraformable planets, and bodies with biological signals.
- To write them to a CSV file, open **Settings → WFMT → Exploration → Boxel Survey** and press **Export Survey Log**.
- The file is always called `boxel_survey_export.csv` and is saved **in the WFMT plugin folder**. You do not choose where.
- The survey log is kept **per commander**, and the export holds the active commander's finds. Exporting as another commander replaces the file.

**Scans made while EDMC was closed.** At start-up WFMT reads the last 14 days of your journals. It adds the notable bodies and biological signals it finds there to the survey log, and the systems that were missing from it.

It is careful not to count anything twice:

- A system the log already had keeps its "bodies scanned" number (only its missing finds are added).
- A system new to the log gets one count per body.
- Running it again changes nothing.
- Scans older than 14 days, made with EDMC closed, are not found.
- The game's journals are only read, never changed.

**Settings → WFMT → Exploration → Boxel Survey (the first section of that page):**

| Setting | Default |
|---|---|
| Auto-copy next target to clipboard on jump | On |
| Skip systems already visited this session | On |
| Skip systems already visited by anyone (EDSM) | Off (adds a network call per advance) |
| Skip systems already fully scanned in EDSM | Off (another network call per candidate) |
| Confirm off-sequence arrivals against EDSM (catches a target that resolved under a different display name) | Off |

### Region Sweep

For clearing several cubes and seeing what's left. It keeps a **queue of cubes**. Each entry in the list looks
like `> Outotz LS-K d [3/12]`: the `>` marks the current cube and `[3/12]` is systems done out of systems known.

**Setting up the queue:**

1. Type a seed system under *Add cube — seed system* and press **Add** (or **Use Current**, then **Add**).
2. Press **Discover Nearby Cubes (EDSM)** to add cubes near your current position, and fill in the systems EDSM
   knows. It needs your position.
3. Select a cube and press **Discover Known Systems (Spansh)** to fill in the systems Spansh knows for that cube.

**Example: clearing a small region.** You are in `Outotz LS-K d8-0`.

1. Choose **Region Sweep**, press **Use Current** under *Add cube — seed system*, then **Add**. The list shows the cube with `>` marking it as current.
2. Press **Discover Nearby Cubes (EDSM)**. More cubes join the list, each with the systems EDSM knows.
3. Select a cube and press **Discover Known Systems (Spansh)** to fill in more of its systems.
4. Press **Copy**, paste the **Target** into the galaxy map and jump. The count for that cube moves up, for example `> Outotz LS-K d [3/12]`.
5. When every known system in the cube is done, the sweep moves to the next unfinished cube. If you judge a cube not worth the time, select it and press **Mark Empty** (the list shows `[empty]`).

**Working through it:** the **Target**, **< Prev**, **Next >** and **Copy** buttons work as in Sequence, on the
current cube. **Set Current** makes the selected cube the current one (the status line says `Set as current`), and **Remove** deletes it from the queue.

**What "complete" means.** A cube is complete once *every system WFMT knows about in it* is done, or once you mark it **Empty**.

- WFMT can't know a cube's true total, only what EDSM, Spansh and your own visits have revealed.
- A system counts as done when you arrive there.
- If you turn on *Require a full FSS scan*, a system counts as done when the game reports that your FSS has found every body in it (the `FSSAllBodiesFound` journal event). That check uses only your journal, with no internet lookup.

**Mark Empty / Unmark Empty** flags the selected cube as having nothing worth surveying (the list shows `[empty]`).
Empty cubes count as complete and are skipped. When you arrive at a cube's target and that cube is complete, the
sweep moves on to the next unfinished cube in the queue (wrapping around to the start).

**Settings → WFMT → Exploration → Boxel Survey, in the Region Sweep section (further down the same page):**

| Setting | Default |
|---|---|
| Auto-copy next target to clipboard on jump | On |
| Skip systems already visited this session | On |
| Skip systems already visited by anyone (EDSM) | Off. When on, each candidate target is checked with EDSM before it is offered, and WFMT steps past systems EDSM already knows (at most 20 in a row) |
| Require a full FSS scan (not just arrival) to mark a system complete | Off |
| Auto-discover more nearby cubes (EDSM) when the queue is running low | Off. When on, runs the Discover Nearby lookup after a jump once one or fewer cubes still have work left |

**What *Skip systems already visited by anyone (EDSM)* does.** With it ticked, WFMT asks EDSM about each candidate before showing it as the next target, whether it came from a jump or from **Next >**.
- If EDSM already has the system, WFMT moves on to the next candidate in the cube and asks again. It stops after 20 in a row and shows the last one, and the status line says so.
- The target (and the copy to the clipboard) appears when the check is done. The status line reads `Checking EDSM...` meanwhile.
- If EDSM cannot be reached, nothing is skipped: the candidate is shown and the status line says `EDSM check unavailable`.
- Each name is asked about once per session. Only the system name is sent (see [What goes on the internet](internet-and-privacy.md)).
- A skipped system is not marked visited or complete in your queue; it is only passed over.

### Waypoints

A plain route tool. It takes any system names, not only procedural ones: a rendezvous, a point of interest, a
squadron staging system.

1. Add waypoints in any of these ways:
   - Type a name under *Add waypoint* and press **Add**.
   - Press **Use Current**.
   - Load a list with **Import CSV…**. It reads **one system name per row, from the first column**. Blank rows and a header row (a first cell like `system`, `name` or `waypoint`) are skipped, and names already in the list aren't added twice.
   - Press **From plotted route** to add the systems of the route you have plotted on the galaxy map in the game (the system you are in is left out). They come with their coordinates, so the reorder below needs no lookup for them.
2. **Move Up** and **Move Down** change the order by hand. **Remove** deletes the selected waypoint.
3. **Reorder (Nearest-Neighbor, EDSM)** asks EDSM for each system's coordinates, then builds a route that starts at
   your current position and always goes to the nearest unvisited waypoint next. Waypoints you've already visited
   keep their place at the front, and ones EDSM can't locate keep their order at the end. It needs your position.
4. **Copy** copies the current target. With *Auto-copy next waypoint to clipboard on jump* on, WFMT copies the next
   one when you arrive. That tick is in the Waypoint Route section at the foot of **Settings → WFMT → Exploration → Boxel Survey**.
5. The waypoints are saved for each commander, so the list and the current target are still there after a restart.

**Example: a squadron staging route.** Four systems to visit, in a sensible order.

1. Choose **Waypoints**. Type the first system name under *Add waypoint* and press **Add**; repeat for the other three. (Or put one name per row in the first column of a CSV file and press **Import CSV…**.)
2. Jump once so WFMT knows your position, then press **Reorder (Nearest-Neighbor, EDSM)**. The list is rebuilt starting from where you are and always going to the nearest unvisited waypoint next.
3. Use **Move Up** and **Move Down** if you want a different order.
4. Press **Copy**, paste the target into the galaxy map and jump. With *Auto-copy next waypoint to clipboard on jump* on, the next waypoint is copied when you arrive.

### Random: find something nobody has discovered

**Example.** You are exploring and want a system that has no scans on record.

1. Press **Random** on the button row (the Boxel Survey section can stay folded).
2. Read the status line, for example `Copied: <name> (31 ly away, no scans on Spansh or EDSM)`.
3. Open the galaxy map, paste the name and plot the jump.
4. If you want a different one, press **Random** again. Within 5 light-years of the first search it picks another from the same list and only the EDSM check takes time.

**Random** sits on the Exploration button row, next to Auto-Honk, Discovery Alerts, Neutron Star and White Dwarf, so it is visible even while the
Boxel Survey section is folded, and works whichever sub-mode is selected. It does not touch your Sequence target.

When you press it, WFMT:

1. asks Spansh for the systems nearest your position, nearest first, and keeps the ones with **no scan data on
   record** (Spansh lists the system but no bodies have been submitted);
2. drops any system in your own visited-systems log, and the system you are in;
3. picks one at random from the nearest eight and asks EDSM for its bodies, trying up to **6** until one has none;
4. copies that name to your clipboard.

Paste it into the galaxy map. Every name comes from a service's list of real systems; none is made up. A status
line says what happened, for example `Copied: <name> (31 ly away, no scans on Spansh or EDSM)`. If EDSM cannot be
reached, the name is still offered and the line says `EDSM unreachable`. If Spansh cannot be reached, the line says
so and nothing is copied.

"No scans on record" is the closest thing to "undiscovered" the services can tell you: the system exists, but nobody
has uploaded a scan of it. It does not prove nobody has flown there, because a visit without a scan leaves no body
data. Anything you find by scanning is yours to claim.

The visited-systems log records every system you arrive at, whichever sub-mode is selected. Clear it under
**Settings → WFMT → Exploration → Boxel Survey → Clear Visited Systems Log**.

WFMT keeps the Spansh list in memory for 10 minutes. Pressing Random again within 5 light-years of where it was fetched
skips the Spansh search and picks a different system from that list, so only the EDSM check takes time. Systems
already offered, or found scanned on EDSM, are not offered again. Nothing is saved to disk; restarting EDMC clears it.

The same Settings page has **Systems to request from Spansh** (10 to 100, default 25). Spansh's search takes several
seconds whatever the size, and a larger request takes longer; raise it only if Random often says it found no unscanned
system near you.

More detail: [Boxel Survey specification](../BOXEL_SURVEY_TECH_SPEC.md).

## Exploration Value

A quiet readout of what you're finding, in the **Dashboard** section of the Exploration panel (click its title to unfold it; the **Dashboard** button and a one-line summary of the system sit at the top of that section). Nothing to turn on. The lines read:

| Line | What it says |
|---|---|
| `Last scan: <body> - est. 1,234,567 cr` | The estimated payout for the last body you scanned (stars as well as planets), with the first-discovery multiplier when nobody had found it. `Last scan: (none yet)` until you scan |
| `System age: <age>` | The age of the current system, from the star's `Age_MY` in the scan, written in million years (`4,200 My (~4.2 By)` for the oldest) |
| `Region: Inner Orion Spur` | Which of the galaxy's 42 named regions you are in, worked out from your coordinates |
| `System bodies: 6 scanned of 14 - all found` | How many of the system's bodies you have scanned out of the number the honk found. `all found` appears once the game reports that your FSS has found every body; before a honk it says `(honk to count them)` |
| `Last data sale: exploration 1,234,567 cr, organic 350,000 cr` | What your last data sales actually paid, to set against the estimate. `Last data sale: (none yet)` until one is read |

All of that is worked out on your computer. The estimate is the value of scanning the body (with the first-discovery multiplier when nobody had found it); the value of
mapping it as well is on the [Body info](#system-targets-and-body-info) card (**Mapped value**) and counted in the [Expedition Log](#expedition-log).

The readout itself is on by default (*Show estimated scan value, system age, and current region*, in **Settings → WFMT → Exploration → Exploration Value**). Two extras are
optional on the same page, and both are off until you tick them because they contact the internet:

- *Show ELW rarity comparison when you scan an Earthlike World* (Spansh). A line `ELW rarity: <body> - 2 known ELWs within 250 ly - a rare find` appears (`not unusual here` when more than 3 are known), after `checking Spansh...`. The count is of Earth-like worlds Spansh already lists around the system.
- *Show EDSM upload status when you select a system on the galaxy map* (EDSM). A line `EDSM upload status: <system> - already in EDSM` (or `not yet in EDSM`, or `EDSM check unavailable`) appears when you select a system in the galaxy map. A system is asked about once in ten minutes.

## Organic Scanning

Helps you find and identify exobiology life on a planet's surface: which species each signal is likely to be, with an estimated credit value, your Log,
Sample and Analyse progress, and when you have walked far enough for the next sample. It also has four overlay cards for the body you are on (bio status,
predicted species, a sample radar and a popup after each sample), leads you back to plants you identified, and shows the first footfall bonus.

The section starts folded (click its title to open it) and has two text readouts, `Predicted species` and `Active scan`, and a **Review** button for the prediction review window. All of it is in its own guide: **[Exobiology](exobiology.md)**. You can switch the panel's section off under **Settings → WFMT → Exploration → Organic Scanning**
(**Show predicted species and scan progress**); it uses only your own journal and makes no internet connection.

## Codex Completionist

*(Starts folded: click the title to open it.)*

A running tally of the Codex entries your game has reported, such as biological, geological, Guardian, human and
Thargoid finds. It is built from the `CodexEntry` events in your journal.

- The section shows one summary line, for example `120 distinct entries, 340 total finds`, followed by your three biggest categories.
- It has one button: **My Codex**, which opens the [My Codex window](#the-my-codex-window).
- It is on by default. Switch it off with *Track codex entries* in **Settings → WFMT → Exploration → POI Reference**, where there is also a *View Canonn Codex* link.

**Each commander has their own tally.** Switching commander switches the tally (the window's subtitle names whose it is), and one commander's finds never appear in another's.

WFMT builds each commander's tally from their own journals the first time they log in (one time). Years of journals can take a minute.

- While it reads, the Codex Completionist title reads **"- rebuilding..."** (even when the section is folded).
- The summary line says it is rebuilding that commander's tally. The summary fills in when it finishes.

**Finds made while EDMC was closed** are counted automatically: each time EDMC starts, WFMT reads only the journal files
written since the last find it counted and adds the newer ones, once each. The first start only sets
that starting point, so use **Backfill Journals** once to bring in older history.

### The My Codex window

Press **My Codex**. The subtitle reads, for example, `120 distinct entries — 340 total finds — 95 of 1,070
catalogued entries found (9%)`, and there are three tabs:

- **Overview**: how far along you are. The first row is every catalogued entry; **Closest to complete** lists the
  types you have started but not finished, fewest entries left first, so you can see which are quickest to finish;
  then each category with its types. Columns: **Found**, **Of** (how many exist), **Left** and **Done** (percent).
  Click a heading to sort the types inside each category (**Left** ascending is the default).
- **Found**: your entries grouped by category, with the columns **Entry**, **Times found** and **First found in**.
  A ⭐ means that at least one of your sightings was reported by the game as a new entry (a first discovery). Click
  a column heading to sort; click again to reverse. (**Times found** sorts highest first on the first click.)
- **Not found**: Canonn's catalog of **biological, civilization and stellar-body** entries, minus the ones you
  have found. Columns: **Entry**, **Type**, **Platform** (Odyssey or Legacy) and **Where to look**. It sorts the same
  way. Canonn's catalog has no geological or anomaly entries, so those never appear here.

**Where to look** is worked out from WFMT's own species data, the same data the Bio predictions use.

- For a biological entry such as `Bacterium Aurasus - Teal` it gives the body type, atmosphere, gravity and temperature the species needs.
- It also says what decides the color: the class of the star the body orbits (`Teal: orbiting a class M star`) or a material in the surface (`Gold: surface holds Polonium`).
- A species can have several sets of conditions and any one is enough. The hint shows the first set and counts the others (`+1 other set`).
- Entries WFMT has no species data for (Thargoid and Guardian entries, stellar bodies) have no hint. Use **POI Reference** to find Thargoid and Guardian sites near you.
- The hint says where an entry *can* appear, not where one is. It is a filter for choosing a planet, not a location.

**Buttons:** **Open Reference**, **Refresh Catalog** and **Backfill Journals**. Double-click a row on the Found or Not
found tab, or select it and press **Open Reference**. This opens a **search** on canonn.science for that entry's name
in your browser, not a fixed page for the entry.

**Backfill Journals** is an action you press yourself, because reading years of journals takes a while.

- It reads **all** the journal files in EDMC's journal folder, with no date limit.
- It counts only the **current commander's** entries (a journal file says whose events follow, and one file can hold several commanders).
- Its progress shows in the window's status bar and in the section under the button.
- It is safe to press more than once. For each entry it compares how many times your journals record it with the count already in the tally and keeps the larger. So nothing is counted twice, and finds from journals you've since deleted are kept.
- It can also fill in an earlier first sighting and a first-discovery star.

**The catalog** is downloaded from Canonn the first time you open the window and whenever the saved copy is
more than 14 days old, and **Refresh Catalog** fetches it again on demand. It is saved in the plugin folder, so
after the first download it opens instantly and works offline. If the download fails, the tab says so, and shows
the saved copy if there is one.

**Example: choosing what to hunt for.** You have found 95 of 1,070 catalogued entries and want the quickest category to finish.

1. Press **My Codex** and stay on the **Overview** tab.
2. Under **Closest to complete**, read the first row. Types are listed with the fewest entries left first, and the columns show **Found**, **Of**, **Left** and **Done**.
3. Switch to the **Not found** tab and look for entries of that type. Click the **Where to look** heading to sort if you like.
4. Read the hint for an entry such as `Bacterium Aurasus - Teal`. It gives the body type, atmosphere, gravity and temperature the species needs, and what decides the color (`Teal: orbiting a class M star`). Use it to choose a planet; it says where the entry can appear, not where one is.
5. Select the row and press **Open Reference** to search canonn.science for the entry in your browser.
6. If the numbers look low, press **Backfill Journals** once. It is safe to press again.

Codex Completionist has no specification page of its own. The code is `codex_completionist.py`,
`codex_completionist_window.py`, `codex_hints.py`, `codex_catalog.py` and `codex_backfill.py` in the plugin folder.

## POI Reference

*(Starts minimized.)*

One section for finding somewhere worth visiting near you, from two catalogs. Click **Find POI** and WFMT looks in both at
once, shows the nearest result from each on its own line, and copies the system name of the **nearer** of the two to
your clipboard so you can paste it into the galaxy map. It only looks something up when you ask. **Update POI** downloads
Canonn's lists again and then searches.

It needs to know where you are, so jump (or log in) first. If EDMC started after you were already in the game, it reads
your position from the current journal.

**GEC (edastro.com).** The nearest point of interest from edastro's exploration catalog. The line shows:

- the point of interest and its category,
- **the system to look for in the galaxy map**,
- how far away it is, its region and rating,
- a link to its page (the system's Inara search when edastro gives none),
- a **Copy System** button for the system name, which is useful when the Canonn result was the nearer one.

**The first Find POI of a session downloads edastro's whole list** (about 2 MB, 650 points of interest) and works out the nearest one itself. Later presses use that list for six hours without another download.

**Canonn.** The nearest of Canonn's Thargoid and Guardian sites.

- The first click downloads the lists, which are then kept for the rest of your session.
- A **Copy System** button under the result puts that result's system name on your clipboard (Find POI copies only the nearer of
  the two sources, so use Copy System when you want Canonn's).
- A **View site details** link beside it opens that site's page in your browser. Canonn's list gives no page for some
  sites; for those the link opens the system's Inara search instead.
- Choose which kinds of site to include in **Settings → WFMT → Exploration → POI Reference**.
- By default it skips sites you've already logged in Codex Completionist, so it points you somewhere new. You can
  turn that off in the same place.

**Example: finding a Guardian site.**

1. Jump or log in so WFMT knows your position, then open the **POI Reference** section and press **Find POI**.
2. Two result lines appear, one for **GEC (edastro.com)** and one for **Canonn**, each with its nearest result. The name of the nearer system is already on your clipboard.
3. Paste it into the galaxy map and plot the jump. If you wanted the other source's result instead, press that line's **Copy System** button.
4. Press **View site details** on the Canonn line to read about the site in your browser.
5. Press **Update POI** if you want Canonn's lists downloaded again before searching.

## Notes

*(Starts minimized.)*

Your own notes on a system or a body: "come back for the rings", "ELW with a moon, scan the other side". The journal has no place
for a commander's own words, so these are kept by WFMT, on your computer, **for the commander who wrote them** (another commander on
the same install does not see them). Nothing is sent anywhere.

The section shows the newest note for the system you are in, so a note you wrote on an earlier visit is in front of
you when you arrive. With the section folded, the title says how many the system has, such as `- 2 here`.

- **Quick note:** type a line in the box and press **Add Note** (or Enter). It is saved against the system you are in, and the body too
  when you are near one (the game's `Status.json` names it).
- **Notes** opens the Notes window: a **Search** box (every word you type must appear in the system, body or note), a list of every
  note, newest change first, and an editor underneath. The list's columns are **System**, **Body**, **Note** (the start of it) and **Changed (UTC)**. Select a note to change it, press **New note** (in the header) to write another. **Here**
  beside the System and Body boxes fills in where you are now (the System box also suggests names as you type). Press **Save** to keep what is in the editor. Tick **Only the system I am in** to see just this system's notes.
- **Delete** asks you to press it a second time, because a note cannot be got back.
- A note can be up to 2,000 characters, a system or body name up to 100, and you can keep 2,000 notes. Past a limit WFMT tells you
  rather than cutting the note short.

**Example: leave yourself a reminder.** You find an Earth-like world with a moon and want to come back.

1. Open the **Notes** section, type `ELW with a moon, scan the other side` in the box and press **Add Note** (or Enter). The note is saved against the system you are in, and the body too when the game names one near you.
2. Fold the section. Its title now reads `- 1 here`.
3. Later, when you arrive in that system, the section shows the note again. To change it, press **Notes**, select it in the list, edit it and press **Save**.
4. To find it from anywhere, press **Notes** and type a word from the system, body or note into **Search**.

Notes are matched to a system by its name (ignoring capitals and spaces at the ends), so a note about `Sol` shows when you are in Sol.

## Expedition

A planner for a trip. An **expedition** is a named list of **stops** (systems, each with an optional body and note). Start it and WFMT ticks stops
off as you arrive and keeps the totals; you can keep several expeditions and run one at a time. Starting an expedition also starts a run in the [Expedition Log](#expedition-log), and the two start, pause and stop together.

### Starting and managing an expedition

**Everything is done in the Expedition window.** Press **Expedition** in the panel's Expedition section to open it. The panel only shows what is running (and has **Copy Next** and **Copy on arrival**); it has no Start, Pause or Stop.

There are two ways to start, and you pick one by the tab you are on:

| You want | Go to | Press | What happens |
|---|---|---|---|
| A trip with stops, ticked off as you arrive | **Plan** tab | **Start** | The expedition starts, and a run starts in the Log with the same name (unless switched off in Settings) |
| To record a trip without planning stops | **Log** tab | **Start** | A run starts from the system you are in, in the ship you are flying. There are no stops to tick off |
| To count a trip you are already on | **Log** tab | **Start from my last** and **sale**, **Discovery Data sale** or **Exobiology Data sale** | The expedition begins just after that sale and fills itself in from your journals |

Whichever you use, the same buttons manage it afterwards, on either tab:

- **Pause** holds it: nothing is counted and the clock stops. The button reads **Resume** while it is held.
- **Stop** ends it. The expedition and its Log run stop together, because they are linked.
- Starting another one sets the running one aside, so only one runs at a time.
- The panel's Expedition section, the Dashboard and the overlay card always show the one that is running.

**Example 1: plan a trip from Sol to Colonia.**

1. Press **Expedition**. On the **Plan** tab type `Colonia run` in the **Name** box and press **New**.
2. Type `Sol` in **System** and press **Add stop**. Type `Colonia` and press **Add stop** again. (**Here** fills in the system you are in.)
3. Press **Start**. The status line says it started and that it is logging in the Expedition Log.
4. Play. Each time you arrive in Sol or Colonia the stop is ticked off, and every jump adds to the totals. The panel shows `1 of 2 stops` and the next stop; while the section is folded its title shows `- 1/2` instead.
5. **Pause** for a break and **Resume** after it. When you are done, press **Stop**. The trip stays in the **Log** tab with what it found and earned.

**Example 2: record a trip with no plan.** You are leaving the Bubble to explore and have no route yet.

1. Open **Expedition** and switch to the **Log** tab.
2. Type a name such as `Bubble to the Rim` in **New expedition name** (or leave it empty) and press **Start**.
3. Explore. The Log counts systems, jumps, light-years, bodies, mapping, species and credits from your journal. The panel and the overlay card show the running totals.
4. Press **Stop** when you finish.

**Example 3: you are already out there.** You have been exploring for two days and have not sold anything since leaving.

1. Open **Expedition** and switch to the **Log** tab.
2. Press **Start from my last** and **sale**. It begins just after your last sale, so everything you are still holding counts.
3. To count only the exobiology you have gathered, press **Exobiology Data sale** instead (or **Discovery Data sale** for exploration data alone).
4. It then carries on counting live. Press **Stop** when you sell up and finish.

**The Expedition row** (a collapsible section in Exploration mode) shows the one running:

- its name, `7 of 20 stops`,
- the jumps and light-years flown,
- the time it has taken (when the Expedition Log is following it, the time paused is not counted),
- the next stop with its distance (and its note),
- the stop you have just reached.

Buttons:

- **Copy Next** puts the next stop's system name on the clipboard to paste into the galaxy map.
- **Copy on arrival** does it for you every time you arrive anywhere. It is off until ticked. The same switch is in Settings → WFMT → Exploration → Expedition.
- **Expedition** opens the window.

**One window, three tabs.** The Expedition window has a tab for each part of a trip:

- **Plan**: the expeditions and their stops.
- **Route**: the [Route Planner](#route-planner).
- **Log**: the [Expedition Log](#expedition-log).

How the tabs work together:

- **Expedition** and **Plot** on the panel each open this same window (on the Plan and Route tabs).
- The tabs switch from one to the next.
- **Neutron route** and **Review expedition** switch to the tab they need, so a trip is planned, plotted and recorded in one place.
- **Start expedition** is pressed on the Route tab, so it stays there. The status line says what happened, and **Review expedition** takes you to the Plan tab.
- A tab is built the first time it is shown.
- The window remembers its size and position.

**What you find at each stop.** While an expedition is running, WFMT counts what you do in each stop's system against that stop:

- the bodies you scan,
- how many nobody had discovered before (the game says so in the scan),
- how many you map.

Once you have honked, it also knows how many bodies the system has, so a stop reads `5 of 12 scanned · 2 first · 1 mapped`.

- The row shows the running totals (`Found: ...`).
- The window has a **Found here** column for every stop.
- The stop you are at shows in the Expedition row.
- A body scanned twice counts once, belt clusters are not counted, and nothing is counted in a system that is not a stop you have reached.

### The Expedition window

**Expedition** on the panel opens it on the **Plan** tab. From top to bottom:

- **The header** has **Start**, **Pause** and **Stop** for the expedition picked below, and a Help button. The subtitle names the commander and how many expeditions they have (up to 30).
- **The picker** is a list of your expeditions, each written as `Name (status, 3 of 20)`. The status is *planned*, *active*, *paused* or *done*. **Name** and **New**, **Rename**, **Reset** and **Delete** are beside it.
- **The totals line** under it reads like `Active · 7 of 20 stops · 31 jumps · 1,204 ly · 2 d 4 h · 38 scanned · 6 first · 4 mapped`: the status, stops ticked, jumps, light-years, time and the bodies found across all stops.
- **The stops table** lists the stops in order (up to 500 for each expedition):

  | Column | What it shows |
  |---|---|
  | **#** | The stop's number in the order |
  | **System**, **Body**, **Note** | What you or the planner entered |
  | **Reached (UTC)** | When the stop was ticked off. The next stop shows `next` while the expedition is active |
  | **Found here** | What you did at the stop, such as `5 of 12 scanned · 2 first · 1 mapped` |
  | **From you (ly)** | The straight-line distance from where you are now, or `-` when the stop has no position yet |

- **The editor** under the table has **System** (with suggestions as you type, and **Here** to fill in the system you are in), **Body (optional)** and **Note (optional)** boxes and the buttons **Add stop**, **Save changes**, **Mark visited**, **Move up**, **Move down** and **Remove**. **Mark visited** on a ticked stop takes the tick away again.
- **Make an expedition with Spansh** has **Road to Riches**, **Exomastery** and **Neutron route**.
- **The tools row** has **From plotted route**, **Import CSV**, **Locate and reorder (EDSM)**, **Copy list**, **Export CSV** and **Copy next**.
- **The status line** at the foot says what the last button did, including why it refused.

**Reset**, **Delete** and **Remove** ask you to press the button a second time within five seconds before they act.

### Using the Expedition window

1. **Create an expedition.** Type a name and press **New**.
   - Pick an expedition from the list at the top. **Rename**, **Reset** and **Delete** act on it.
   - To rename, press **Rename**: the current name appears in the Name box. Change it and press **Rename** again.
   - Reset forgets the progress and keeps the stops. Reset and Delete ask twice.
2. **Add stops.** Type the system (or press **Here** for the one you are in) and press **Add stop** or Enter. Only the system is needed. The body and the note are optional.
   - **Capitals do not matter**: type `sol` and the stop is `Sol`. WFMT uses the spelling of the system you are in or of a stop you already have.
   - While *Check system names on EDSM when adding* is ticked under the editor (it is by default), WFMT also asks EDSM. EDSM fixes the capitals of any system and fills in the stop's position. It sends only the system name.
   - A system EDSM does not know, because nobody has charted it or because of a typo, is kept as you typed it, and the status line says so.
   - Untick the box to stay offline.
   - If you have no expedition yet, the first stop makes one called "My expedition" (or the name you typed in the Name box), so you can start straight away.
   - Select a stop to change it (**Save changes**), move it (**Move up**, **Move down**), tick it off yourself (**Mark visited**) or **Remove** it (asks twice).
3. **Or add many at once.** These also make an expedition if you have none.
   - **From plotted route** adds the systems of the route you plotted in the game. The one you are in is left out, and they come with their positions.
   - **Import CSV** reads a file with the columns system, body and note (a one-column list of systems works too).
4. **Make an expedition with Spansh.** **Road to Riches** and **Exomastery** (a row above the other tools) ask [Spansh](https://spansh.co.uk/)'s route planners for places worth visiting and turn the answer into a new expedition.
   - **Road to Riches** picks the bodies worth the most credits to scan, near a route, in a good order. Tick *Count what mapping pays as well as the first scan* to include mapping.
   - **Exomastery** (Spansh's Expressway to Exomastery) picks planets with the most valuable biological signals.
   - **Neutron route** opens the [Route Planner](#route-planner), which plots a neutron route for your ship (nothing to type about the ship) and can turn it into an expedition with **Start expedition** or **Review expedition**.
   - A small window asks for:

     | Box | What it means | Starts at |
     |---|---|---|
     | **Start from** | Where the route begins (the system you are in is filled in) | Your system |
     | **End at (optional)** | Leave empty for a route that just goes where the best places are | Empty |
     | **Jump range (ly)** | Your ship's range, taken from your last loadout when WFMT has seen one; change it if it is wrong | 30 when no loadout is known |
     | **Look this far from the route (ly)** | How far off the route a place may be | 25 |
     | **Most results** | Up to 100 | 100 |
     | **Furthest from the arrival star (ls)** | Leaves out bodies that are a long way from where you arrive | 50,000 |
     | **Least a body is worth (credits)** (Road to Riches) or **Least a planet's biology is worth (credits)** (Exomastery) | Raise it for fewer, better places | 100,000 for Road to Riches, 10,000,000 for Exomastery |

   - **Avoid systems the Thargoids control** is ticked. **Come back to the start** is not. **Start it now** is a third tick (see below).
   - Each of the number boxes must be a number above 0; otherwise the window tells you which one to fix.
   - Press **Plot**. Spansh can take from a few seconds to a couple of minutes (WFMT waits up to five minutes, then says so).
     - While it works, the **Plot** button reads *Plotting...*, a bar moves along the window, and a timer counts what you have waited, with Spansh's own word beside it (waiting in the queue, or calculating). So you can see it has not stalled.
     - **Cancel** stops waiting.
     - When the answer arrives it becomes a new expedition (named, for example, *Road to Riches from Sol*) with a stop for each system: the best body, a note of what is worth scanning there and its position.
     - Check the order, then press **Start**. Or tick **Start it now** in the window before you press Plot to have it start as soon as it arrives.
   - This is online, and only when you press **Plot**. It sends Spansh the start system, the end system if you typed one, and the numbers above, nothing else (see [what goes on the internet](internet-and-privacy.md)).
   - If Spansh cannot find a system, it says so in the window. If nothing worth stopping for is found, no expedition is made: lower the least worth or look further from the route.
5. **Locate and reorder (EDSM)** asks EDSM for the positions of the unvisited stops that have none. Then it puts the unvisited stops in order, always going to the nearest next, starting from where you are.
   - This is the only part of the Expedition planner that goes online, and it sends only system names.
   - A stop EDSM cannot place keeps its place at the end.
6. **Start.** Press **Start**.
   - From then on, arriving in a stop's system (a jump, a carrier jump, or logging in there) ticks off the first unvisited stop of that name, wherever it is in the list. Each jump adds to the totals.
   - **Pause** stops counting and keeps the progress. Starting another expedition pauses this one.
   - When the last stop is ticked the expedition stays running until you press **Stop**.
   - Starting a stopped expedition again reopens it, and its clock picks up from the time it stopped at.
7. **Share it.** **Copy list** puts a text list on the clipboard. **Export CSV** saves the stops (it can be imported again). **Copy next** copies the next stop's name.

### The Expedition Log goes with it

Unless you untick *Start the Expedition Log when I start an expedition* (Settings → WFMT → Exploration → Expedition; it is on to start with), **Start** also starts a run in the [Expedition Log](#expedition-log) under the same name, in the ship you are flying. The status line says so (*Logging in Expedition Log.*).

- **Pause** pauses the run, **Stop** stops it, and starting the expedition again carries the same run on.
- The Log tab's **Pause**, **Resume** and **Stop** act on the expedition too. The panel's Expedition section only shows what is running, so that section, the Exploration Dashboard and the overlay card always agree with the window.
- Starting a second expedition sets the first aside. It is paused, and its run is paused with it (or stopped, when the new expedition gets a run of its own, because the log keeps one run going at a time).
- An expedition started with the box unticked, or one made before this was added, has no run. Its time is counted from its start on the wall clock.

The expeditions are kept on your computer for each commander, and nothing is sent anywhere except the EDSM lookup above. It does not replace
**Waypoints** (Boxel Survey), which stays a single quick list; **From plotted route** and the CSV import work the same way in both.

## Expedition Log

An archive of your exploration expeditions, and a card that keeps the running one in view. It is separate from the [Expedition planner](#expedition) above, which plans stops to
visit; the log records what **happened** on a trip, whether or not you planned a route.

**An expedition from the planner.** Starting an expedition in the [Expedition planner](#expedition) or the [Route Planner](#route-planner) also starts a run here with the same name, unless that is switched off (Settings → WFMT → Exploration → Expedition, *Start the Expedition Log when I start an expedition*).

- The run and the expedition are linked. **Pause**, **Resume** and **Stop** in the Log tab pause, resume and stop the expedition too, and the other way round.
- Starting a different run here (**Start**) stops the expedition that was linked to the run it replaces.
- Deleting a run from the log leaves the expedition as it is, without a run.

**Starting an expedition you are already on.** In the Log window, the **Start from my last** row has three buttons. Each begins an expedition one second after a sale in your journals:

- **sale** is the earlier of your last Discovery Data sale and your last Exobiology Data sale, so it covers everything you are still holding. If you have only ever sold one kind, it is that one.
- **Discovery Data sale** is your last exploration sale alone.
- **Exobiology Data sale** is your last exobiology sale alone.
- If your journals hold no sale of the kind you chose, it says so and starts nothing. Use **Start** instead.

- It fills the expedition in from your journals since then, so the data you are still holding is what the expedition covers.
- It then carries on counting live.
- It is how to pick up a trip that was under way before you used the log.

**The row.** The Log has no section of its own: its figures are in the Exploration panel's **Expedition** section ([above](#expedition)). That section only shows what is running: you start, pause and stop expeditions in the Expedition window (the **Expedition** button).

- While an expedition is running the section shows the expedition's own lines (its name, stops, jumps, light-years and time, the next stop). Under them it shows what the Log adds: the systems, bodies and species, what you have earned and the unsold data (`paused` in front while it is held).
- A Log run that was started with **Start** and has no planned expedition behind it is shown in the Log's own words: its name and how long, systems, jumps and light-years, bodies and species, earned and unsold.
- The section's title says whether a run is going (`- running` or `- paused`) even while it is folded; the open section has the name and figures.
- **Start** (in the Expedition window) begins a new expedition now, from the system you are in and in the ship you are flying, and stops the one that was running.
- **Pause** becomes **Resume** while paused. **Stop** ends it.
- The archive is the **Log** tab of the Expedition window (**Expedition**, then the Log tab).

**What it counts**, from your journal, while an expedition runs:

| | |
|---|---|
| **Exploration** | systems visited, jumps and light-years, honks, bodies scanned (each once) and first discoveries, Earth-likes, water worlds, ammonia worlds and terraformables, bodies mapped and first maps, landings, new codex entries, **the credits earned when you sell exploration data**, and an estimate of what the scans and mapping you have not yet sold are worth (with the first discovery, first map, efficiency and Odyssey bonuses) |
| **Exobiology** | samples taken, species analyzed, genera, first footfalls, **the credits earned when you sell exobiology data**, and an estimate of what the species you have analyzed but not yet sold are worth (five times as much on a first footfall) |
| **Ships** | each ship you flew (type, name and ident), added as you load into it |

Earned figures are what the game reports when you sell, so they count when you sell, not when you scan.

- The unsold figures are estimates, marked `~`. Selling clears them, since the game sells what you hold.
- The estimates follow the community formula: the base value of the body from its class and mass, the first-discovery multiplier, the mapping multipliers (for a first map, a first map of an already discovered body, and an already mapped body), the efficiency bonus when your probe run met the target, and the Odyssey bonus.
- Expect them to be close, not exact.

**The Log window** is the archive (the **Log** tab of the Expedition window). Up to 200 expeditions are kept.

- **The header** has **Start**, **Pause** and **Stop**. They are the only place on the Exploration side to manage an expedition: the panel's Expedition section has no such buttons.
- **The starter row** has the **New expedition name** box (optional; **Start** begins it now, from where you are) and the **Start from my last** row (**sale**, **Discovery Data sale** and **Exobiology Data sale**).
- **The table** lists every expedition, newest first. Its columns are **Name**, **Status**, **Started (UTC)**, **Ended (UTC)**, **Systems**, **Jumps**, **Bodies**, **Species**, **Exploration cr**, **Exobiology cr** and **Total cr**.
- **Under the table** is everything the selected expedition recorded, then the editor.

Select one to read everything it recorded and to **edit** these, then press **Save changes**:

- its name,
- when it started and ended (UTC; `2026-10-16` or `2026-10-16 18:30`),
- where it started and ended,
- the ships used,
- your notes.

The buttons:

- **Start** (with an optional name)
- **Pause** (pause the running expedition, or resume the paused one)
- **Stop**
- **Resume** (carry on counting one that was paused or stopped)
- **Reset** (clear its totals and count again from now; it asks twice)
- **Rescan** (work its totals out again from *your* journals between its start and its end, which fills in an expedition that missed events or one you gave an earlier start)
- **Delete** (asks twice)
- **Copy summary**
- **Export CSV** (the whole archive, for a spreadsheet)

**The overlay card** (Settings → WFMT → Overlays → Expedition Log, off until ticked) shows the running expedition's exploration and exobiology totals and what it has earned.

- With no expedition running, it says so and how to start one.
- The heading has its name and how long it has run. The total earned is at the foot.
- It shows the expedition that is **running or paused**. A paused one keeps what it had counted (its heading says `paused`) until you resume or stop it.
- **Stopping resets the card**, which goes back to saying no expedition is running.
- Place it on **Overlay Placement** ("Expedition Log (totals of the running expedition)"); it starts at the top left, beside the Route card.

Everything is kept for your commander only (another commander has their own archive) and never leaves your computer.

**Pause, stop and resume.**

- **Pause** holds an expedition. Nothing is counted while it is paused, and its clock stops (the time paused is not part of the expedition's time). The row and the card keep showing it. It stays paused across an EDMC restart.
- **Resume** carries on counting, and the clock starts again.
- **Stop** ends the expedition, whether it was running or paused, and the card resets. A stopped expedition can still be resumed from the Log window, and its clock picks up from the time it stopped at (the time stopped is not part of the expedition's time).
- **Rescan** works an expedition out from the journals between its start and its end. What happened while it was paused, or stopped between a stop and its restart, is left out, because nothing was counted then.

**What it cannot tell you:**

| What you might expect | What the game gives | What to do |
|---|---|---|
| Earnings the moment you scan | Credits are paid when you sell the data at a station | Sell as usual; the unsold estimate shows what is waiting |
| Counting while EDMC was closed | The journal is read live; events written while EDMC was closed are not seen | Press **Rescan** on the expedition |
| Which sale was for which expedition | The game reports a sale, not what it covered | A sale counts for the expedition running when you sell |
| The exact value of a map | The journal gives the figures the estimate uses, not the payout, which is reported when you sell | The estimate is close; the sale reports the exact figure in the earned total |

## System targets and Body info

Two cards on your game screen for working a system. Both are **off by default**, have no panel button, and are set up under **Settings → WFMT → Overlays**.
They need an overlay ([WFMT's built-in one on Windows, or EDMCModernOverlay](../OVERLAY_SETUP.md)). They read your journal and send nothing anywhere, except the two lookups on System targets that you can tick (EDSM and Spansh, below).

**System targets** (Settings → WFMT → Overlays → System targets) is a list of what is left to do in the system you are in. Its settings:

| Setting | What it does | Starts at |
|---|---|---|
| **Enable the System targets card** | Switches the card on | Off |
| **List bodies worth at least** [N] **credits, judged by** [basis] | The threshold (0 to 50,000,000, in steps of 25,000), and whether bodies are judged and ranked by **Mapped value (what scanning and mapping pays)** or **Scan value (what scanning alone pays)** | 100,000, Mapped value |
| **Rows shown** | 3 to 16 rows across all the lists; the rest are counted (`+ 3 more`) | 6 |
| **Also list bodies with life that I have not finished analyzing** | The Life list | On |
| **Also list the bodies I have finished (mapped, and their life analyzed), so I can see where I left off** | The Done list | On |
| **Also look up bodies other commanders have scanned (EDSM, once per system)** | See below | Off |
| **Also look up the life and points of interest other commanders found in the system (Spansh, once per system, on arrival)** | See below | Off |
| **Test Card** | Draws a made-up system, so you can see and place the card | |

The card is drawn in lists under the heading, each headed with its count: **To map (n)**, **Life (n)**, **Known (n)** and **Done (n)**. What each list holds:

- After you have scanned bodies, it lists the planets and moons **worth mapping that you have not mapped**.
  - These are the ones whose estimated value is at or above a threshold you choose (100,000 credits to start), most valuable first.
  - The value is what **scanning and then mapping** the body pays by default, so a body worth mapping is ranked by what mapping it earns. A choice in Settings → WFMT → Overlays → System targets switches it to the scan alone.
  - Each row has the body's short name (`A 1`), a tag for the classes that matter (`ELW`, `WW`, `AW`, `HMC`, `MR`, and `TF` for any other terraformable world) and the value (`1.2M`, with `first` when nobody had discovered it).
- Below that it lists the bodies **with life that you have not finished analyzing**, as `1/3 life`.
- A body leaves the list when you **map it** or **analyze its last organism**.
- The card's heading is the system name with a progress bar for the system scan and a count (`4 of 8 scanned`) once you have honked.
- A message says so when nothing at or above your threshold is left. Before your FSS has found every body it reads `Nothing over 100k to map yet`; once the game says every body is found it reads `Nothing over 100k left to map or sample`. While the Spansh lookup runs it says `Looking up data (Spansh)...`; if Spansh has nothing, `Spansh has nothing on this system`; if the lookup failed, `Spansh lookup failed; will retry`. A long message continues on the next line.
- With the EDSM lookup on, the heading's count gains `· 3 online` for the bodies that came from EDSM.
- Each row shows the body, a muted tag and distance (`HMC  82k ls`) or the genera once known, and the value on the right.
- **Also look up bodies other commanders have scanned** (off until you tick it).
  - Right after you honk, WFMT asks [EDSM](https://www.edsm.net/) once for the system's planets. It sends only the system name (see [What goes on the internet](internet-and-privacy.md)).
  - It lists the worthwhile ones with their estimated value, marked `EDSM`, before you have scanned anything.
  - Your own scan then replaces what EDSM said, and the Body info card shows them as `From EDSM, not scanned by you`.
  - EDSM does not say who has mapped a body, so a looked-up body stays on the list until you map it.
- **Also look up the life and points of interest other commanders found in the system** (off until you tick it).
  - When you arrive in a system (or tick it while you are in one), WFMT asks [Spansh](https://spansh.co.uk/) once for the system's record. It sends only the system's number (see [What goes on the internet](internet-and-privacy.md)).
  - The card then shows a **Known** section for the bodies other commanders found **life or a point of interest** on, before you have honked or scanned anything.
    - Life looks like `3 b  Fungoida Setisis x2 +1`, with the reward for the life on the right (`2.6M`).
    - A wreck, a beacon or a Guardian site shows as `POI`.
  - The heading line reads `Known (Spansh): 1 with life · 3 points of interest`. It takes the place of `Nothing over 100k to map yet` when there is anything to show.
  - A body you have found life on yourself stays on the Life list, and a body whose life you have finished leaves the Known section.
  - Spansh knows only what other commanders have uploaded. A system nobody has scanned shows nothing, and a body scanned by someone else shows its life only if they landed and scanned it.
  - Settlements, geysers and vents are not listed.
- **Where you have been before.** A line under the heading says `First visit here` or `Been here 3 times before · last 10 Oct 2026 · you scanned here`.
  - WFMT builds this from your own journals, for the active commander only.
  - The first time, it reads all of your finished journals in the background. The card says `Reading your journals for a visit history (n%)`. It takes about 40 seconds for 5,800 journals. After that it reads only new ones.
  - It is kept in `system_history.json` and nothing is sent anywhere.
  - It counts a visit when you arrive somewhere other than where you last were, so a relog in the same system is not another visit.
  - It counts only journals that still exist.
- Under the heading a **summary line** says how far you have got (`1 mapped · life 1 of 3 done · 4 of 9 analyzed`). That counts the bodies with life you have finished, and every biological signal in the system you have analyzed.
- A third section, **Done**, lists the bodies you have finished (mapped, and any life analyzed) as `2 d  mapped · life 3/3`. So after a break you can see where you left off as well as what is left. You can switch the Done list off.
- **Coming back to a system.** WFMT keeps each system's survey for you between sessions (the 60 most recently visited, kept separately for each commander). So leaving a system, logging out, or visiting it again later brings the card back as you left it.
  - For a system that you scanned while EDMC was closed (you then log in and find it empty), it rebuilds the survey from your journals.
  - It uses your own commander's journals, the ones your visit history says hold your visits.
- **Rows shown** (3 to 16, 6 to start) caps the list, and the rest are counted (`+ 3 more`). You can switch the life list off.

**Example: working a new system with System targets.**

1. Under **Settings → WFMT → Overlays → System targets**, tick **Enable the System targets card** and press **Test Card** once to place it.
2. Jump into a system and honk. The heading shows the system name with a progress bar and a count such as `4 of 8 scanned`.
3. As you scan bodies, the ones worth at least 100,000 credits appear under **To map (n)**, most valuable first, each with a short name (`A 1`), a tag (`ELW`, `WW`, `HMC` and so on) and a value such as `1.2M`.
4. Bodies with life you have not finished appear under **Life (n)** as `1/3 life`.
5. Map a body and it leaves **To map**. Analyze the last organism of a body and it leaves **Life**. The finished ones are listed under **Done (n)**, so after a break you can see where you left off.
6. When the list is empty it says `Nothing over 100k to map yet`, or `Nothing over 100k left to map or sample` once the game reports every body found.

**Body info** (Settings → WFMT → Overlays → Body info) describes one body. It shows:

- its name and class,
- flags (`Undiscovered`, `Terraformable`, and `Unmapped`, `Mapped before` or `Mapped by you`),
- its materials, written as element symbols (`Fe 18.4% · S 18.2%`),
- then the estimated scan value, temperature, gravity (in the warning color at 2.0 g and over), pressure, atmosphere and its composition (formulas such as `CO2`), volcanism, life signals (how many, how many are done, and the genera once you have mapped it), geology signals and distance.

It shows for **the body you have targeted** in the galaxy or system map or the nav panel, and for **the body you are close to**. The targeted body wins when both apply, and a targeted body that is already finished (mapped by you, with all its life analyzed) is not held on the card, so it moves on to the next. A body you have targeted but not scanned shows its name with `Scan required`, and the number of life signals if the system scan gave one.

Its settings (**Settings → WFMT → Overlays → Body info**):

| Setting | What it does | Starts at |
|---|---|---|
| **Enable the Body info card** | Switches the card on | Off |
| **Show the body I have targeted** | Follow the destination you set in the map or nav panel | On |
| **Show the body I am close to** | Follow the body the game's `Status.json` says you are near | On |
| **Element and compound names** | **Symbols (Fe, CO2)** or **Full names (Iron, carbon dioxide)** for materials and atmosphere gases | Symbols |
| **Test Card** | Draws a made-up body | |

On the card, **Scan value** shows `first` after the amount when nobody had discovered the body, **Mapped value** (with a `~`) shows until you have mapped it, and the distance from the arrival star is the badge at the right of the title (`3,936 ls`). A **Footfall** row says `First: exobiology pays 5x` on a body with life that nobody has stood on.

**What they cannot tell you:**

| What you might expect | What the game gives | What to do |
|---|---|---|
| A body to be listed as soon as you honk | The honk gives only a count. A body's class and mass come with its **scan** (the system scan, or a detailed scan), so a body appears when you have scanned it. | Scan the bodies, and they appear. Or tick **Also look up bodies other commanders have scanned** (below). |
| Bodies in a system nobody has scanned | The EDSM lookup only knows what other commanders have uploaded. A system nobody has surveyed returns nothing. | Scan the bodies. |
| Whether a body has been stood on | The scan's `WasFootfalled` says whether anyone has set foot on a landable body. WFMT flags a first footfall (Body info: `First footfall`, and the five times exobiology reward; System targets: `FF` on a life row). It reflects the scan you made; a body scanned by someone before you but not yet footfalled in the data may show as footfalled. | Treat the flag as a strong hint and check the in-game body info if it matters. |
| What mapping pays | The **Scan value** is the estimated value of scanning (the same estimate the [Exploration Value](#exploration-value) readout uses); Body info's **Mapped value** is the estimate of scanning and mapping it with an efficient probe run. The System targets list is ranked by the mapped value by default (the scan value if you choose it in Settings). | Use the threshold as a guide to which bodies are worth a probe run. |
| The kinds of life before you map | The system scan gives the **number** of biological signals; the genera are given when you map the body. | Map it to see the genera. |
| The cards to remember a system after a restart, a relog or a visit later | The survey of each system is saved for each commander and merged back when you return; for a system with no saved survey, it is rebuilt from the journals that hold your visits (your commander's, found through the visit history). | Nothing: it happens by itself. Bodies the journals never recorded (a system you never scanned) cannot be recovered. |
| To be told about life and points of interest in a system you have not scanned | Your own journal knows only what you scanned. Spansh knows what other commanders uploaded. | Tick **Also look up the life and points of interest other commanders found** (above). A system nobody has scanned shows nothing, and the card says `Spansh has nothing on this system`. |
| The visit line to be right straight after installing | The history is read from your journals once, in the background (about 40 seconds for 5,800 journals), and the line waits for it (`Reading your journals for a visit history`). It counts only journals that still exist, and a relog in the same system is not a second visit. | Wait for the first read to finish; it is quick afterwards. |

**When the cards show.** They follow the commander and the situation, so they are there when you are exploring and gone when you are not.

- They hide in hyperspace, while docked or on a carrier, when the game is closed or at its main menu (including while another commander signs in).
- A different commander loading in starts with a clean slate.
- They come back when you arrive in a system.
- The cards are drawn by the overlay over your game window. The overlay's own settings decide whether they show when another window has focus.

Where each card sits is set on **Overlay Placement** ("System targets" and "Body info"). They start in the lower middle of the right half of the screen,
one above the other; move them to suit your HUD.

The Exobiology cards (bio status, predicted species, the sample radar and the sample popup) are described in the [Exobiology guide](exobiology.md#the-overlay-cards).

## Exploration Dashboard

The overlays draw over the game. The **Exploration Dashboard** is for the times you would rather read than have your screen cluttered.

The **Dashboard** button in the Dashboard section of the Exploration panel (which also holds the [Exploration Value](#exploration-value) lines, and a one-line summary of the system beside the button: its name, how many bodies are worth mapping and how many have life still to do) opens a window with everything WFMT knows about:

- the system you are in,
- the body under you,
- the biology on it,
- your exploration so far.

It only reads what the other features already hold (the system survey, Organic Scanning, the Expedition Log, the Route). It costs nothing to leave open, and sends nothing anywhere.

It opens on the tab that suits where you are, and switches by itself when you land (to **Surface**) and when you lift off (back to **Orbit**). It only does that while you
are on **Orbit** or **Surface**: if you picked **Overview** or **Exploration** yourself, it stays there.

**The tabs:**

- **Overview**: the system in numbers, and the expedition in a few lines.
  - The system: bodies scanned of the honk's count, planets mapped, how many are worth mapping at your System targets threshold, biological signals analyzed, the scan value of what you have scanned, what mapping would add, first discoveries.
  - *This system* and *You* (where you are, altitude, position, heading, fuel).
- **Orbit**: every body in the system in a table you can sort.
  - Columns: **Body**, **Type**, a small tag for the classes that matter, **Distance** (light-seconds from the arrival star), **Gravity**, **Landable**, **Atmosphere**, **Temp**, **Scan value**, **Mapped value**, **Bio** and **Geo** (signal counts) and **Status** (what has been done with it). Click a heading to sort by it.
  - Rows are tinted: green for nothing left to do, amber for worth mapping, green text for unfinished biology.
  - Click a row for that body in full (conditions, atmosphere gases, materials, signals, genera, value).
  - Beside it are **Worth mapping**, **Life to analyze** and **Found by others** (what Spansh lists in the system, when the lookup under Settings → WFMT → Overlays → System targets is on).
- **Surface**: the body you are on or near.
  - Where you are (and how far your ship and SRV are), the body's conditions and materials.
  - The exobiology: each genus with what it could be and pay (an even share per candidate, as on the Biology card).
  - Its progress as `Collecting: 1/3` (the Log, Sample and Analyse scans make three; `Analyzed: 3/3` once it has paid out).
  - How far you are from the last sample and how far you must be.
  - The reward range, with the first footfall bonus applied where it counts.
  - Then the specimens you have scanned with the Composition Scanner (a plant, a fungus, a shard and so on), with their distance and direction from where you stand.
- **Exploration**: the running expedition in full, the route and the Exploration panel's own readouts.
  - The expedition: time, systems, jumps, distance, bodies, first discoveries, maps, landings, Codex entries, samples and species, earned and unsold.
  - The route: fuel, range, jumps left, the next supercharge.

**Example: a landing.** You drop to a planet's surface.

1. Press **Dashboard**. The window opens on the tab that suits where you are.
2. When you land it switches to **Surface** by itself. There you see the body's conditions and materials, each genus with what it could be and its pay, and progress such as `Collecting: 1/3`.
3. It also shows how far you are from your last sample and how far you must be for the next one.
4. When you lift off it switches back to **Orbit**, where you can click the **Scan value** heading to sort the system's bodies by value and click a row to see that body in full.
5. If you picked **Overview** or **Exploration** yourself, the window leaves it alone.

**Route Planner.** The window's header also has a **Route Planner** button, which opens the [plotter](#route-planner).

**Switching overlays off and on.** The two buttons at the top right of the window, **Exploration overlays** and **Exobiology overlays**, hide and show those cards without touching Settings. Each says what pressing it will do: `Exploration overlays: ON - hide`, or (in the warning color) `Exploration overlays: OFF - show`.

- Exploration covers Route, System targets, Body info, Expedition Log, Compass, Discovery Alerts and Notable Bodies.
- Exobiology covers its four cards.
- Hiding clears the cards from the screen and stops them being drawn.
- Showing puts back exactly the cards you had switched on, nothing more.
- It is not saved: overlays are shown whenever EDMC starts.
- Flight Alerts, Interdiction and the other overlays are not affected.
- **Hide overlays** (all of them at once) still works on top of this.

**Limits.** The tables show what the journal gave: a body you have not scanned is not listed, and values are estimates (they match the game's payout closely, not
exactly). Spansh's finds appear only when you have switched that lookup on. The window never asks the game for anything it was not already told.

## Route Planner

The **Plot** button in the Route Planner section of the Exploration panel (click its title to unfold it) (and **Route Planner** in the Dashboard's header) opens a window that plots a route with
[Spansh](https://spansh.co.uk/)'s **exact plotter** for **your ship**. You type where you are going; nothing about the ship.

**When to use it.**

- Neutron routers, this one included, are made for long-distance, deep-space travel: the Bubble to deep space, or to Colonia.
- Inside the Bubble a route from here may be no better than the one your galaxy map plots for you, so use the game's own routing there.
- **An add-on cannot give the game a route.** You paste each system into the galaxy map's search and set it as your destination yourself, one leg at a time.
- WFMT does its best to always have the next system ready. It puts it on the clipboard when the route is ready and again every time you reach a system on it (see *Copying the next system* below), so the next step is always a paste away.

### Your ship

- **Your ship, read from the journal.** The window shows what Spansh will be told, from your last loadout:
  - the ship's name,
  - the frame shift drive (class and rating),
  - whether you carry a Guardian FSD booster,
  - the drive's optimal mass (with your engineering),
  - whether it supercharges (and at 4x or 6x),
  - the cargo you carry,
  - the ship's mass, its fuel tank and the drive's fuel figures.
- There is **no jump range to type**. Spansh works the range out itself, jump by jump, so it knows the ship lightens as it burns fuel and where it has to refuel.
- Fuel burning does not change anything in the window. Only a new loadout or a change of cargo does.
- **If the ship is not known.** The game writes your ship's loadout when you log in or change its fit.
  - If you started EDMC after the game, WFMT reads the last one from your newest journal when EDMC starts (and again when you open the window or press Generate route). So you do not have to log out and in.
  - Only if there is no loadout in the journals at all does the ship block say it is not known yet.
- **No fuel scoop.** The ship block shows whether a fuel scoop is fitted. If there is none and the route has refuel stops, the status line warns you after Generate route, because those stops need a scoop. WFMT cannot tell Spansh to plan without one.

### Plotting a route

- **Source and destination.** The source is the system you are in (type another if you are planning ahead). Type the destination (system names are suggested as you type, if you have that switched on). Press **Generate route**.
- **The choices:**
  - **Use supercharge** (on)
  - **Use FSD injections** (off)
  - **Exclude secondary stars** (off)
  - **Refuel every scoopable** (off)
  - **Algorithm** (Optimistic to start; Fuel, Fuel and jumps, Guided and Pessimistic are Spansh's others)
  - **Mark white dwarfs the route passes (asks EDSM)** (off), described under *White dwarfs* below

  The choices are remembered. Spansh starts from a full tank.
- **The route.** A long route can take a minute or two. There is a bar, a timer and Spansh's own word for what it is doing, and **Cancel** stops waiting.
  - The table lists **every jump**. Its columns are **#**, **System**, **Distance (ly)** (this jump), **Left (ly)** (still to go), **Fuel (t)** (in the tank after the jump) and **At this system** (what to do there: supercharge at a neutron star, refuel, use an injection).
  - Systems you have reached turn green and the next one is marked.
  - The panel button's line says what is next (for example *Next: Colonia Neutron 4 (neutron) · 41 jumps left*).
- **Messages.**
  - When a route is ready the window says so, that it was sent to the Route overlay (when that overlay is switched on), and which system is on the clipboard.
  - At every system you reach it says which system is next and that it is on the clipboard.
  - At the end it says the route is finished and will reset.

**Example: a long trip to Colonia.** You are flying a ship with a Guardian FSD booster.

1. Press **Plot** (the window shows your ship, drive and booster as read from the journal).
2. Leave the source as the system you are in, type `Colonia` as the destination and press **Generate route**. Leave **Use supercharge** on. Tick **Use FSD injections** only if you carry the materials and want them used.
3. Wait for the bar and timer. A long route can take a minute or two.
4. The table lists every jump with **Distance (ly)**, **Left (ly)**, **Fuel (t)** and **At this system** (supercharge at a neutron star, refuel, use an injection).
5. The first system is already on your clipboard. Open the galaxy map, paste it into the search and set it as your destination.
6. After each jump the next system is copied. Paste it again. Systems you have reached turn green.
7. To keep the trip in one place, press **Start expedition**. The status line reads like `Started 'Neutron Highway from Sol to Colonia': 12 stops. Logging in Expedition Log.`

### White dwarfs

A white dwarf also supercharges the drive, but Spansh's plotter knows only neutron stars and cannot be told to use white dwarfs.

- With **Mark white dwarfs the route passes** ticked, WFMT asks EDSM, after the route is plotted, which of the route's systems have a white dwarf as their main star.
- It marks them *white dwarf: supercharge* in the table, on the Route overlay and in the Expedition it makes.
- They are **extra boosts, not planned stops**. Spansh did not route through them, and its jump counts and fuel figures do not count their boost.
- A system EDSM does not know is left unmarked. If EDSM cannot be reached, the route is shown as plotted with a note saying so.
- This sends EDSM the names of the route's systems (no more than that), only when you press Generate route with the box ticked.

### A neutron star that may be a secondary star

Spansh counts a supercharge at any system with a neutron star, even when that star is not the one you arrive at.

- The *Exclude secondary stars* choice acts on the main-star record in Spansh's data. That record comes from submitted scans and can differ from what the game shows. Lalande 25224 is recorded with its neutron star as the main star, while the star named for the system is a different one.
- After a route is plotted, and as you progress, WFMT looks at the stars of the next dozen neutron stops (it asks Spansh for each system's stars, by its address).
- Where the star named for the system is not the neutron star, it marks the stop **NEUTRON ?** in yellow on the Route overlay, says so in the table, and says so in the window when you get there.
- It means *the supercharge there may need a long flight to a secondary star, and the next jump, planned for the boost, may take more jumps*. Check the system map.
- It is a name rule and a warning, not a fact. It cannot judge a system whose stars are all named by letter, and a system Spansh has no stars for is not marked.

### Copying the next system

**Copy the next system to the clipboard automatically** is **on to start with**. It is one setting, shown on the Exploration panel under the button and in the window, and it is remembered. Untick it to stop.

- With it on, the first system is on the clipboard the moment the route is ready and the next one after every jump, so you can open the galaxy map and paste.
- The panel line says *copied* when the next system is on the clipboard.
- With it off, **Copy next system** does the same on request, **Copy all remaining** copies the rest one per line, and double-clicking a row copies that system.

### The route overlay and clearing the route

- **On the Route overlay.** A plotted route also shows on the [Route overlay](always-on.md#route-overlay), in place of the game's plotted route, until you have made every jump. Each system's star is in a color, and a message shows when the route ends.
  - The overlay's own switch under Settings → WFMT → Overlays → Route still decides whether it is drawn.
  - Its option to mark systems EDSM does not know applies to the neutron route too.
- **Clearing the route.** **Clear route** in the window, or **Clear Route** in the Route Planner section of the Exploration panel (always there), clears everything the Route overlay is following.
  - That is the route plotted here (the panel line, the window's table) and the route it was following from the game, so the card closes.
  - The game's own route is not touched in the game. The overlay follows it again after the next route you plot in the galaxy map, or after a restart.
  - Plotting a new route replaces the old one without clearing.

### Start expedition

**Start expedition** turns the stops still ahead into an expedition in the [Expedition planner](#expedition), starts it, and (unless switched off in Settings → WFMT → Exploration → Expedition) starts its [Expedition Log](#expedition-log) run, in one press.

- The status line says what happened, in green when it started (*Started 'Neutron Highway from Sol to Colonia': 12 stops. Logging in Expedition Log.*), and the button reads **Started ✓** for a few seconds.
- The Expedition window, when you open it, is on that expedition.
- The stops are the neutron stars, the marked white dwarfs, the refuel stops and the destination, in route order, each with what to do there. A neutron star the route marks as possibly a secondary star carries that warning in its note.
- The expedition is named *Neutron Highway from <start> to <destination>*.
- Pressing the button again for the same route does not make a second expedition. It says the first is running (or paused).
- **Review expedition** opens the Expedition window on that expedition to check the order before you start it, and makes it (not started) if there is none yet.
- An expedition made from a route is a snapshot. Plotting another route, or **Clear route**, does not change an expedition that is running or paused.

### Limits

- Spansh plans for the ship as the journal describes it, from a full tank. If your loadout changes after you plot (a new module, more cargo), plot again.
- A drive WFMT has no figures for is reported in the ship block rather than guessed.
- The route is kept when you restart EDMC (saved on your computer, one per commander, in `route_planner_route.json`), and picks up where you are on it. A route you had already finished is not brought back.
- It sends Spansh the two systems and the ship's numbers, nothing else ([what goes on the internet](internet-and-privacy.md)).
- The Expedition window's **Neutron route** button opens this window.

### Carrier route

The **Carrier route** button in the Route Planner window opens a second window that plans a route for your **fleet carrier** (or squadron carrier) with Spansh's fleet carrier router.

WFMT reads your carrier from the journal, so you only type the destination. It reads:

- where the carrier is,
- the tritium in its tank,
- the space it uses.

These come from `CarrierLocation` and `CarrierStats`, which the game writes at login and when you open Carrier Management.

**How to use it:**

1. In the Route Planner window press **Carrier route**. The carrier block shows what the journal says about your carrier; if it says *not known yet*, open Carrier Management once in the game, or log in again.
2. Check **Carrier** (Fleet carrier or Squadron carrier, if you have both), **Where it is now** (filled in), **Destination system** (type it; suggestions appear), and the **Space used** and tritium boxes (filled in from the journal; you can change them).
3. Leave **Work out the tritium I need to start with** ticked to let Spansh say how much to have at the start, or untick it to enter the tritium you already have in the tank and in the carrier's market.
4. Press **Generate route**. Spansh works out each jump (up to 500 ly), the tritium each one uses and where there is an icy ring; the summary says how much tritium to have at the start. **Cancel** stops waiting.
5. Work down the table. Its columns are **#**, **System**, **Distance (ly)**, **Left (ly)**, **Tank (t)** and **Market (t)** (the tritium in the tank and in the carrier's market after the jump) and **At this system** (for example where there is an icy ring to mine tritium).
   - **Copy next system** (or double-click a row) puts the next system on the clipboard. Paste it into Carrier Management's jump search and schedule the jump in the game.
   - The route moves on by itself when your carrier arrives (green rows are done, the next is marked). WFMT sees it in the journal when you are aboard or log in.

**Controls:**

| Control | What it does |
|---|---|
| **Generate route** / **Cancel** | Ask Spansh for the route / stop waiting |
| **Carrier**, **Where it is now**, **Destination system** | Which carrier, where it starts and where it is going |
| **Space used (t)**, **Tritium in the tank (t)**, **Tritium in the market (t)** | The numbers Spansh plans with (filled in from the journal) |
| **Work out the tritium I need to start with** | Let Spansh work out the starting fuel, or enter your own |
| **Copy next system** / **Copy all remaining** | The next system, or every system still to visit, one per line |
| **Mark next as reached** | Move the route on by hand, if the carrier jumped while WFMT could not see it |
| **Clear route** | Forget the route |

- The route is kept when you restart EDMC (one per commander, in `carrier_route.json`).
- It sends Spansh only the systems and the carrier's size, space used and tritium ([what goes on the internet](internet-and-privacy.md)).
- One destination per route for now.
- The tritium figures are Spansh's, and the table shows the tritium in the tank and in the carrier's market after each jump.

## Nearest place to land

*(Starts folded.)*

For deep space and emergencies: the nearest station that can take your ship and has what you need, and the nearest fleet carriers that let anyone dock.

The panel section has a line saying where you are and which pad your ship needs (`From Sol; your ship needs a large pad.`, or `Needs your position: it comes from your next jump, or from the journal when you log in.`) and a **Find** button that opens the window.

**To use it:**

1. Press **Find**. The window opens with **From** showing your system and coordinates.
2. Under **I need**, tick what the place must offer: **Refuel**, **Repair**, **Rearm (restock)** and **Outfitting**. Refuel and Repair are ticked at first. Only stations that offer *all* the ticked services are listed.
3. Choose the **Landing pad**: **My ship's pad** (the default), **Any size**, **Medium or larger** or **Large only**. With **My ship's pad** WFMT uses your ship's size from your last loadout (a Python is never sent to an outpost with only small pads); a small ship has no restriction, since it fits everywhere.
4. Leave **Include fleet carriers open to all, updated within** ticked to list carriers too, and choose how fresh a carrier's record must be: **7 days**, **14 days** (the default), **30 days** or **90 days**. Untick it to leave carriers out; the carrier table then says `Fleet carriers were not asked for`.
5. Tick **Allow this lookup: pressing Find sends Spansh my position, the pad size and these choices, nothing else**. It is off until you tick it, and it is the same switch as **Settings → WFMT → Exploration → Nearest place to land**. Nothing is sent before it is ticked.
6. Press **Find**. The window asks Spansh and fills two tables. An answer is remembered for two minutes, so pressing Find again with the same choices costs no new request.

**Example: low on fuel in deep space.**

1. Press **Find**. **From** shows your system and coordinates.
2. Leave **Refuel** and **Repair** ticked, and leave **Landing pad** on **My ship's pad** so a large ship is not sent to a small outpost.
3. Tick **Allow this lookup**, then press **Find**.
4. Read the **Stations** table for the nearest place with a suitable pad (the **Pads** and **Has** columns say what it offers), and the carrier table for carriers open to all. Check a carrier's **Last reported** age before relying on it.
5. Double-click the row you want. Its system name is copied; paste it into the galaxy map.

**The tables.** Up to eight places are listed in each, nearest first.

| Table | Columns |
|---|---|
| **Stations with <services>** (starports, outposts, planetary ports and outposts, megaships and colonization sites) | **Station**, **System**, **Where** (where in the system), **Distance (ly)**, **Pads** (the pad sizes it has), **Has** (which of your ticked services it offers) |
| **Fleet carriers open to all, reported within <days> days** | **Carrier**, **System**, **Distance (ly)**, **Pads**, **Has**, **Last reported** (how long ago Spansh had a report of it) |

**Double-click a row** to copy its system name, to paste into the galaxy map. The status line at the foot of the window says what happened and reminds you that carriers move: check a carrier's age before you rely on it. Stations rarely change.

- **It starts from where you are.** The position comes from the journal (`StarPos`, set by each jump), not from a system name, so it works in a system nobody has charted yet. If WFMT has not seen a jump this session it reads the newest journals; if it still has no position, the window says `Your position is not known yet. Jump to a system or log in first.` Jump once.
- **Fleet carriers** are listed only when Spansh says docking is open to everyone, and only if its record is recent, because carriers jump and change who may dock.
- **It is online, and only when you press Find**, once you have ticked the box that allows it. It sends Spansh your position, the pad size and your choices, and nothing about you (see [What goes on the internet](internet-and-privacy.md)). If Spansh cannot be reached, the window says so and suggests trying again.
- The window remembers your choices and its size and position.

What this cannot tell you is in the last section of this guide.

## Compass

*(Starts folded.)*

Points you at a spot on the planet you are on, from wherever you are on its surface (on foot, or in a vehicle), in any mode. It replaces the arrow Mining used to draw for hotspots, and a Mining waypoint arrow you had switched on carries over as the Compass, with its place on screen.

What it can point at:

- **The nearest hotspot** you have recorded on this body (the default). Hotspots with no position yet are
  skipped.
- **One of your marks**: a name, a body and a latitude and longitude, kept for you alone (another commander on the same install does
  not see them) and never sent anywhere. Up to 500 marks can be kept; a name can be 60 characters and a body name 100.
- **Nothing.**

**The panel section** shows a line saying what it is aiming at and how far (`↗ Ship - 340m NE`; the arrow is left out until the game has given your heading), a box and three buttons:

- **Mark** saves where you are now as a mark, named with what you typed in the box (or `Mark 1`, `Mark 2` ... if it is empty), then clears the box. The body
  comes from the game's `Status.json`. Without a surface position it says `No surface position yet: land, or get out, first.`
- **Target** steps through what to aim at: the nearest hotspot, then each mark on this body, then nothing, then round again. It says `Now aiming at ...`.
- **Marks** opens the Marks window.

When the target is a mark on another body than the one you are on, the line says so (`Mark Ship is on <body>, not here.`) instead of pointing.

**Example: finding your way back to a spot.** You land by a crashed ship and want to return to it after exploring.

1. Standing at the spot, type `Wreck` in the Compass box and press **Mark**. The box clears and the mark is saved with the body and your latitude and longitude.
2. Go exploring. Press **Target** until the line reads `Now aiming at ...` with `Wreck`.
3. The line shows the distance and direction, for example `↗ Wreck - 340m NE`. With **Enable Surface Compass** ticked, the arrow on your screen turns as you turn, and straight up means straight ahead.
4. To check or edit the mark, press **Marks**, select it and use **Save** or **Delete**. In that window, **Nearest hotspot** and **Nothing** change what the compass points at.

**The Marks window.** Its table lists every mark with the columns **Name**, **Body**, **Latitude**, **Longitude** and **From here** (the distance from you now, when the mark is on your body). Under the heading **The compass points at:** (with what it is now aiming at) are three buttons: **Nearest hotspot**, **Selected mark** and **Nothing**. Below the table is the editor:

1. Press **New mark** (in the header) or select a mark to change it.
2. Fill in **Name**, **Body**, **Latitude** and **Longitude**. **Here** fills in your own position and body. You can also type a position, for example one from a guide or a screenshot.
3. Press **Save**. **Delete** removes the selected mark; press it twice, since a deleted mark cannot be got back.

**To see the arrow on your game screen**, tick **Settings → WFMT → Overlays → Surface Compass → Enable Surface Compass** (**off by default**) and
press **Test Compass**. Where it sits is set on **Overlay Placement** ("Surface compass"). The overlay card is one line of text (an arrow glyph, the name, the distance and the compass point) with a drawn arrow under it that turns as you turn, so straight up means straight ahead.

The distance and direction are great-circle on a sphere the size of the body (from the body's radius in `Status.json`), good for "which
way and how far", not for the last few meters. The compass only points at things on the body you are on, and shows nothing until you
have a surface position.

## What the game does and doesn't tell us, and how to work around it

WFMT, like every third-party tool, only knows what Elite Dangerous writes to its journal files.

- It adds what EDSM, Spansh, Canonn and edastro report and works around the rest.
- Where it can't be sure, WFMT says so rather than guess quietly.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| What you might expect | What the game gives | What to do |
|---|---|---|
| The planner to know a stop was visited when you were not in the game | It counts arrivals the journal reports while the expedition is **running** (Start). A system you reached while it was paused, or before you started, is not ticked. | Use **Mark visited** for those. |
| Scans to count in a system that is not a stop, or at a stop you have not reached | Survey counts go to a stop you have reached, in the system the scan happened in, while the expedition is running. | Add the system as a stop, or use **Mark visited** for a stop you reached while it was paused. |
| The distance to the next stop on every stop | A distance needs a position for both ends. The game gives yours on every jump; a stop has one only if it came from a plotted route or EDSM. | Press **Locate and reorder (EDSM)**. A stop EDSM does not know shows `-`. |
| The jump total to include carrier jumps | A fleet carrier jump is not your ship's jump, so it ticks stops but does not add to the jump count or the light-years. | Nothing needed. |
| The light-years to be the whole route | It adds each jump's own distance as the game reports it, so it is the distance you flew, not the straight line between stops. | Nothing needed. |
| A note to know which body you are at | The body comes from `Status.json` (`BodyName`), which the game writes only while you are near a body, and not in supercruise between bodies. | Press **Here** in the Notes window beside Body, or type the name. A note can be about the system alone. |
| The nearest place to land to include a carrier that has only just jumped, or one whose docking access Spansh does not know | Spansh reports a carrier as it last saw it (when a commander's EDMC sent it), and a carrier's docking access is in the data for only some carriers. A carrier whose access is not "All", or not known, is left out. | Check the age shown for a carrier; for one you want to try, request docking when you arrive. |
| The nearest place to land to know a station's state right now | Spansh's records are what EDMC users last reported. A station that was attacked, or a carrier that moved, may differ, and a place nobody has visited recently may not be listed. | Treat the list as where to try first. |
| The compass to work in space or in a ship above the ground | The game gives a latitude and longitude only on a landable surface (on foot or in a vehicle). | Land, or get out, and it appears. |
| A mark to know which body it is on | The body comes from `Status.json` (`BodyName`), which the game writes only near a body. Marks are matched by body name. | Use **Here** while standing there, or type the body's full name as the game shows it. |
| Auto-Honk to press any control | It can only press **keyboard** keys, so your fire button must be bound to one. On Linux it needs `xdotool`; Wayland without XWayland is unsupported. | Bind a keyboard key to your fire button and use **Rescan** after changing bindings. |
| Auto-Honk to know the honk worked | WFMT presses the key and reports only that the key press was sent. The game's `FSSDiscoveryScan` event is what the rest of WFMT uses to know a honk happened. | If nothing happens in the game, press **Rescan** and **Test Honk Now**, and check the status line. |
| A first-to-map banner for a body whose scan was not seen | The mapping event carries no "mapped before" flag; WFMT takes it from the same body's earlier scan in this system. | Scan the body (or let the system scan reach it) before mapping, and the banner can fire. |
| The Route Planner or Carrier route to set the game's destination | An add-on cannot give the game a route. The journal and `NavRoute.json` only report what you plotted. | Paste each system into the galaxy map (or Carrier Management) yourself; WFMT keeps the next one on the clipboard. |
| The Route Planner's fuel figures to include a white dwarf boost | Spansh's plotter knows only neutron stars. | White dwarfs are marked as extra boosts only when you tick the EDSM option; the jump counts do not include them. |
| Boxel Survey to know where a system is | It works with **names**, not coordinates. It counts through the trailing number to make the next name and does not know whether that system exists. | The galaxy map is the judge. Press **Next >** to skip a name that won't plot. |
| The game to tell WFMT a candidate failed to plot | Nothing is written to the journal when the galaxy map can't find a name. | After 3 skips WFMT asks EDSM for a real nearby system. Press **Set** to move there. |
| Whether anyone has flown to an Random system | Random offers real systems with no scans on Spansh or EDSM. A visit without a scan leaves no trace in either. | Treat a result as a strong lead; the first scan you upload settles it. |
| A cube's real system count | WFMT only knows what EDSM, Spansh and your own visits revealed, so "complete" means every system **known** is done, or you marked it **Empty**. | Use **Mark Empty** when you have judged a cube done. |
| The color of a gas giant | The game never records it. The Green gas giant rule uses the Codex or matches the surface temperature of a confirmed green one. | Treat it as a lead and check the body in the system map. |
| Notable Bodies to be certain | A match comes from scan data, using its default limits. | Check the body before you plan around it. |
| Organic Scanning to name the species | Until a sample names it, the result is a **list of candidates** worked out from the planet's conditions. The main star is assumed to be the illuminating one, which can be wrong near a secondary star. A species with no usable rules can't be predicted, and new species need a WFMT update. | Take a first sample, which replaces the list with the exact species. The in-game exobiology tools are the final word. |
| Systems visited with EDMC closed to be known | The journals record every jump, so each start reads the last 14 days of journals for your arrivals and adds them to the visited list that **Skip systems already visited** and **Random** use. | Nothing needed for the last 14 days. Older jumps made with EDMC closed are not found. |
| Bodies-scanned count to be right after a restart | The honk (`FSSDiscoveryScan`) gives the body count and each scan counts one. If EDMC started after the honk, WFMT replays the current journal file for them. | If it still says to honk, honk again. A system's scans made in another journal file are not included. |
| The sale line to include sales before the current journal file | It is read from the current journal file when EDMC starts, then kept up to date live. | It resets to "none yet" when you restart EDMC after a new game session. |
| Codex Completionist to cover everything | Canonn's catalog has no geological or anomaly entries, so those never appear under **Not found**. The tally is per commander. | Use the game's Codex for those. Press **Refresh Catalog** if the saved copy is old. |
| POI lists to be current | They are snapshots from Canonn and edastro, and are fetched only when you ask. | Press **Find POI** or **Update POI** to refresh. |
| edastro's own "nearest" lookup to work | It does not use your position: a check on 2026-10-10 got "The Solar System" for every coordinate and name tried. WFMT downloads the full list and finds the nearest itself. | None needed. If FIND says the lookup failed, edastro's list could not be downloaded; try again later. |

