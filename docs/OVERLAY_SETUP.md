# Setting up the on-screen overlay

Some WFMT features draw on top of the game: discovery alerts, the assigned landing pad, the interdiction warning, cards for the current body, and others. Drawing requires a transparent layer over Elite, called an **overlay**. WFMT supports two overlays.

Every WFMT feature works without an overlay. Only the on-screen displays are unavailable.

## Which features use it

| Feature | What appears on screen |
|---|---|
| **Discovery Alerts** | A banner on entering an unscanned system, or on being first to scan or map a body |
| **Notable Bodies** | A banner when a scanned body matches a selected rule (terraformable, high-value world, shepherd moon and more) |
| **Landing Assist** | The assigned pad, with a diagram of the station or carrier |
| **Interdiction Warning** | An alert the moment an interdiction starts |
| **Flight Alerts** | A small card with the fleet carrier jump countdown, the low-fuel and unscoopable-star warnings and the mining alerts (a core asteroid, a rich rock, low limpets, a nearly full hold) |
| **Route** | A card with the navigation target, the jumps left, the systems still to visit (neutron stars, white dwarfs and scoopable stars picked out) and the light years left; a route plotted in the Route Planner takes its place. Fuel and jump range are on the Exploration Dashboard, not on this card |
| **Expedition Log** | The running expedition's exploration and exobiology totals and what it has earned |
| **Powerplay** | The commander's Power, rank and merits, the system's Powerplay state and holder, what merits earned here count as, and the merits and estimated Control Points earned here this session |
| **Bio status**, **Biology**, **Bio radar**, **Sample popup** | The Exobiology cards: sampling progress and distance, predicted species and what they pay, a plot of the samples and their circles, and a popup after each sample |
| **System targets** | A list of scanned bodies worth mapping and bodies with life not yet analyzed, with the scan progress |
| **Body info** | A card describing the body that is targeted or close |
| **Missions** | A small card of the commander's missions: those here and at the next jump first, then the rest by urgency |
| **Colonization** | The shopping list for the active construction site: what it still needs, what the hold and fleet carrier cover |
| **Inventory** | Capacity bars and pickup messages |
| **Mining** | Live stats, and (built-in overlay only) the Surface Live radar over the game while the Rhino is out |
| **Surface Compass** | An arrow, a name and a distance pointing at a hotspot or a mark on the planet the commander is on |
| **Screenshots** | A short "Screenshot saved" message |

## Step 1: Choose an overlay

**Linux:** the built-in overlay is Windows only. On Linux, EDMCModernOverlay is used for every WFMT on-screen display.

The overlay is selected under **Settings → WFMT → Overlays → Overlay Connection → Which overlay draws**.

| | **WFMT's built-in overlay** | **EDMCModernOverlay** |
|---|---|---|
| What it is | A transparent window WFMT itself lays over Elite, drawn from inside EDMC | A separate program (an EDMC plugin with its own helper window) WFMT sends its drawings to |
| Systems | **Windows only** | Windows and Linux |
| Install | Nothing: it is part of WFMT | Install separately ([project page](https://github.com/SweetJonnySauce/EDMCModernOverlay) and its wiki) |
| Draws | **WFMT's displays only** | WFMT's and every other plugin that supports it |
| Chosen with | The setting above (off until selected) | The same setting (it is the default) |
| Font | Its own: Source Sans 3 (lower case), or any added `.ttf` or `.otf` file; used as soon as OK is selected, no restart | One font for all plugins, in its own list; takes effect after a restart |
| Cards fit their text | Exactly (the text is measured in the font in use) | By estimate, with 10% added to every width |
| Card corners | Rounded (selectable: square to very rounded) | Square |
| Stray windows | None: it ends with EDMC | An old window can remain running (see [Known issues](guide/known-issues.md)) |
| Elite must run | Borderless or windowed | Borderless or windowed (EDMCModernOverlay also lists fullscreen; see its documentation) |

### Do I need EDMCModernOverlay?

- **WFMT's displays on Windows: not required.** The built-in overlay needs nothing else.
- **Linux: required.** The built-in overlay is Windows only.
- **Other plugins' overlays: required.** The built-in overlay draws WFMT's displays only. A plugin that draws through EDMCModernOverlay (or the older EDMCOverlay) requires EDMCModernOverlay, independent of WFMT's setting.

### Using both

EDMCModernOverlay can remain installed and running beside the built-in overlay:

- **Only one draws WFMT's displays.** With the built-in overlay chosen WFMT sends nothing to EDMCModernOverlay, so nothing of WFMT's is drawn twice. EDMCModernOverlay keeps drawing the other plugins' displays.
- **Two windows over Elite.** Each is transparent and passes clicks through. They do not coordinate, so a display of another plugin and a display of WFMT at the same position overlap. Move WFMT's display in Overlay Placement.
- **Switching** takes effect when **OK** is selected. Restart EDMC after switching, so that anything the other overlay still shows from WFMT expires (most displays last a few seconds; the Colonization card is left up for up to an hour).
- **Fonts stay separate.** The built-in overlay's font and EDMCModernOverlay's are chosen independently (see [Fonts](#fonts)).
- **The Hide overlays switch hides WFMT's displays only**, in whichever overlay draws them.

WFMT does not install or start EDMCModernOverlay. The built-in overlay starts and stops with EDMC.

## Step 2: Set Elite up so the overlay can show

An overlay draws a transparent layer on top of the game, so Elite cannot run in exclusive fullscreen. In Elite's graphics options, select **borderless** or **windowed** mode. EDMCModernOverlay also supports fullscreen (see its documentation). The built-in overlay does not.

## Step 3: Check the settings

In EDMC, open **File → Settings → WFMT**, choose **Overlays**, then the **Overlay Connection** tab.

- **Built-in overlay:** select **WFMT built-in overlay (Windows)** under *Which overlay draws* and select **OK**. The tab then states whether the overlay is running over Elite.
- **EDMCModernOverlay:** the defaults are **Host** `127.0.0.1` and **Port** `5010`. These match the defaults of EDMCModernOverlay. If the port of the overlay was changed, enter the same port here.

## Step 4: Turn the features on and test them

Every overlay setting is under **File → Settings → WFMT → Overlays**: a tab for the shared connection, placement, appearance and hiding, and a tab for each feature that draws on the screen. Each feature tab has its switch and, where applicable, a test button:

| Overlays tab | What it controls | Test button |
|---|---|---|
| **Overlay Connection** | Which overlay draws; EDMCModernOverlay's host and port; keep showing for screenshots | **Check connection** |
| **Appearance** | Color scheme, text size, panel opacity, corners and the overlay font | **Show sample** |
| **Overlay Placement** | Where every display sits (layout editor) | **Show placement preview** |
| **Body info** | The body card (targeted body, nearby body, symbols or full names for elements and compounds) | **Test Card** |
| **Colonization** | The shopping list card | **Test Overlay** |
| **Discovery** | New system and body discovery alerts | **Test Discovery** |
| **Exobiology** | Four switches, one for each Exobiology card, and the radar's size and circles | **Test Cards** |
| **Expedition Log** | The card of the running expedition's totals | **Test Card** |
| **Powerplay** | The card of the Powerplay standing in the current system | **Test Card** |
| **Flight Alerts** | The carrier jump countdown, fuel warnings and mining alerts card | **Test Card** |
| **Hide overlays** | A button to hide or show every overlay (its keyboard shortcut and chat command are under General → Shortcuts; the Exploration Dashboard's two header buttons hide only the exploration cards, or only the exobiology cards, and never change these settings) | **Hide / show now** |
| **Interdiction Warning** | The warning when the ship is interdicted | **Test Warning** |
| **Inventory** | Pickup notifications and the inventory bars | **Test pickup** |
| **Landing** | The assigned pad and diagram | **Test Overlay** |
| **Mining** | The mining stats, and the **Mining radar**: the Surface Live radar drawn over the game while the Rhino is out (WFMT's built-in overlay only: EDMCModernOverlay cannot draw a picture), with its size, background opacity and a **Test radar** button (see [the Mining guide](guide/mining.md#the-live-window)) | **Test HUD**, **Test radar** |
| **Missions** | The missions card (rows to show, next jump, urgent limit) | **Test Card** |
| **Notable Bodies** | Alerts for bodies worth a look, with a tick for each rule | **Test Notable** |
| **Route** | The route card (how many systems to list; marking systems EDSM does not know is switched in Settings → WFMT → Online) | **Test Card** |
| **Screenshots** | The "screenshot saved" message | **Test Overlay** |
| **Surface Compass** | The arrow, name and distance pointing at a hotspot or a mark on the planet the commander is on | **Test Compass** |
| **System targets** | The list of bodies to map and sample (value threshold, what the value is judged by, rows, life list; the EDSM and Spansh lookups of what others found are switched in Settings → WFMT → Online) | **Test Card** |

The test buttons work while the feature is switched off and report whether the overlay could be reached. A feature's other settings (what it tracks, how it behaves) are on its own tab elsewhere in Settings; only the overlay settings are here.

**Check connection** reports whether the overlay is reachable: for EDMCModernOverlay, whether one is listening at the host and port shown (it sends nothing); for the built-in overlay, whether it is running and
whether it has found Elite's window. It also says when more than one EDMCModernOverlay window is running.

To verify: start the overlay (EDMCModernOverlay) or start EDMC (built-in overlay), start the game, and select a test button. The message appears on the screen when the overlay works.

## Every Overlays tab in detail

Open **File → Settings → WFMT → Overlays**. The tabs start with **Overlay Connection**, **Appearance** and **Overlay Placement**, followed in alphabetical order by: Body info, Colonization, Discovery, Exobiology, Expedition Log, Flight Alerts, Hide overlays, Interdiction Warning, Inventory, Landing, Mining, Missions, Notable Bodies, Powerplay, Route, Screenshots, Surface Compass, System targets. Select **OK** to keep a change.

Properties of every feature tab:

- **Every feature's own enable switch starts off.** The options under a switch have the starting values given below (for example *Show the body I have targeted* is on by default but has no effect until the card is enabled).
- **Test buttons** draw a sample on the overlay for a few seconds and report whether the overlay could be reached. They work while the feature is off, so a passing test shows that the overlay works and not that the live feature is on.
- Where the display sits is **not** on its own tab: it is on **Overlay Placement**. Its look is on **Appearance**.
- If EDMCModernOverlay is the overlay in use and is not installed, each tab says so in orange at the top (the settings are kept and take effect once it is installed). A **Get EDMCModernOverlay** link shows on the tabs while it is the overlay in use.
- Overlay choices are kept per commander ([below](#moving-things-around)).

### Overlay Connection

| Control | Starts as | What it does |
|---|---|---|
| **Overlay** drop-down in the *Which overlay draws* box (Windows only) | EDMCModernOverlay (a separate app) | Choose **WFMT built-in overlay (Windows)** or **EDMCModernOverlay (a separate app)**. Takes effect when **OK** is selected. The box is not shown on Linux, which has only EDMCModernOverlay |
| *Keep showing when Elite is not the window in front (to take screenshots with another tool)* (Windows only) | off | Leaves the built-in overlay up whenever Elite is running, so a capture tool that takes the focus still records it |
| Status line under the box | | Whether the built-in overlay is running and has found Elite's window |
| **Host** and **Port** | `127.0.0.1` and `5010` | Where EDMCModernOverlay listens. They match its defaults. Change them only if the overlay's port was changed. Ignored while the built-in overlay is chosen |
| **Check connection** | | With EDMCModernOverlay, connects to the host and port and closes again (nothing is sent) and says whether something is listening; with the built-in overlay, says whether it is running and has found Elite. Either way it names the process numbers when more than one EDMCModernOverlay window is running ([Known issues](guide/known-issues.md#overlay-text-looks-doubled-or-ghosted)) |

### Appearance

| Control | Starts as | What it does |
|---|---|---|
| **Color scheme** | Elite orange | Elite orange, Ice blue, Phosphor green, Amber mono, High contrast or Color-blind safe (Okabe-Ito colors). A row of chips (Title, Text, Covered, Caution, Carrier, Warning, Border) previews the choice |
| **Text size** | Larger | Default or Larger. Every box is sized from it |
| **Panel opacity** | 90% (default) | 100% (solid), 90%, 75%, 60%, 40% or 25% (faint). Only the box background; the text stays solid |
| **Corners (built-in overlay)** (Windows only) | Rounded | Square, Slightly rounded, Rounded or Very rounded. Panels only; applies to the built-in overlay |
| **Overlay font** group: **Font**, **Add font file...**, **Open fonts folder** | Source Sans 3 (built-in overlay) or *Overlay default* (EDMCModernOverlay) | See [Fonts](#fonts) |
| **Show sample** | | Draws the Colonization card for 12 seconds with the scheme, size and opacity as currently picked, before **OK** is selected, at the position of that display |
| **Reset appearance** | | Puts the scheme, text size, opacity and corners back to the starting values on the tab (select **OK** to keep them). It does not change the font |

### Overlay Placement

| Control | Starts as | What it does |
|---|---|---|
| Layout editor (the to-scale picture) | | Drag a box to place a display; **Picture size** (Default, Large, Extra large) enlarges the picture and is remembered; *Snap to the grid and to edges* with a grid of 20, 40, 60 or 120 pixels |
| The table: **Display**, **Spot**, **Offset X**, **Offset Y**, **Show** | Each display's default spot, all shown | One row per display (21 in all): Colonization shopping list, Discovery alerts, Notable find card, Flight alerts, Route and ship status, System targets, Body info, Biology, Bio status, Bio radar, Sample popup, Expedition Log, Powerplay, Missions list, Interdiction warning, Landing assist, Inventory pickups and bars, Mining stats, Mining radar, Surface compass and Screenshot messages. *Spot* is one of nine places or **Exact position**; the offsets are screen pixels in from the edge, or the overlay's own x and y for Exact position. Unticking *Show* hides that display whatever its own settings say |
| **Display scaling** | Automatic (from the overlay and Windows) | Automatic, 100%, 125%, 150%, 175%, 200%, 250% or 300% |
| **Overlay mode** | Automatic (from the overlay's settings) | Fit (canvas keeps its shape) or Fill (canvas stretched over the screen); ignored by the built-in overlay |
| *Carry displays on the right to the screen edge* | on | EDMCModernOverlay only: sets an offset on a right-hand display's group so it reaches the edge. Clear the option if displays are placed incorrectly |
| **Show placement preview** | | Draws a labeled box for every display at its real size for 12 seconds, using what is typed now |
| **Reset all to defaults** | | Shows every display's default spot, makes them all shown, and sets scaling, mode and the edge carry back to their starting values (select **OK** to keep) |
| **Detect screen again** | | Reads the overlay's log and the game's files again; the line above shows what it found |
| **Copy all overlay layouts and settings from** (a list of the other commanders, and **Copy**) | Shown once a second commander has been seen | Replaces this commander's overlay choices with the chosen commander's when **OK** is selected in Settings; Cancel keeps the current choices ([details](#moving-things-around)) |

### Body info

*Enable the Body info card* (off); *Show the body I have targeted* (on); *Show the body I am close to* (on); *Element and compound names*: **Symbols (Fe, CO2)** (the starting choice) or **Full names (Iron, carbon dioxide)**; **Test Card**. The card describes one body: its class, whether it is undiscovered, terraformable or mapped, the estimated scan value, temperature, gravity, pressure, atmosphere, volcanism, life and materials. See [System targets and Body info](guide/exploration.md#system-targets-and-body-info).

### Colonization

*Always show the shopping list, whatever screen you are on* (off); *Also show the shopping list automatically (markets, carrier inventory, construction sites)* (off); *Also show whenever the right-hand cockpit panel is open, anywhere* (off); **Rows** (0 to 60; 0, the starting value, lists every commodity and a number limits the list, the rest being summarized); **List** (All, To buy, To haul; To buy); **Test Overlay**. The first tick keeps the card up on every screen whether or not the second is ticked. See [the shopping list on the overlay](guide/colonization.md#the-shopping-list-on-the-overlay).

### Discovery

*Enable Discovery Alerts* (off; the same switch as **Discovery Alerts** on the Exploration panel); **Test Discovery**. A gold alert for a system nobody has scanned before, and a cyan alert when the commander is first to scan or map a body.

### Exobiology

Four ticks, all off: *Enable the Bio status card (progress, current species, distance to the last sample)*, *Enable the Biology card (predicted species and what they pay)*, *Enable the Bio radar (samples, their circles, your ship and SRV)*, *Enable the Sample popup (a few seconds after each sample)*. Under them, for the radar: **Radar size** (200 to 800 pixels across, 260 to start), **Circle fill** (0 to 100%, 70 to start; the share that is solid while the ship is inside a circle, 0 leaving an outline) and **Circle outline** (1 to 6 pixels, 2 to start). **Test Cards** draws all four. See [Exobiology](guide/exobiology.md).

### Expedition Log

*Enable the Expedition Log card* (off); **Test Card**. The card shows the expedition that is running or paused. A paused one keeps its totals until it is resumed or stopped; stopping resets the card. An expedition is started, paused and stopped in the Expedition window (its Plan and Log tabs; the Expedition section of the Exploration panel has no such buttons), and named and edited in the Log tab. See [Expedition Log](guide/exploration.md#expedition-log).

### Powerplay

*Enable the Powerplay card* (off); **Test Card**; the look-ahead lookup (**Powerplay card: the system you are jumping to**, off) is switched in Settings → WFMT → Online, and the tab shows a note saying so. In a system without a Powerplay state the card says **No Powerplay Detected in system**. With the look-ahead on it turns to the jump's destination as soon as the journal says the jump has started, using a Spansh lookup of the destination's id (see [What goes on the internet](guide/internet-and-privacy.md)). It lists the commander's Power, rank, total merits and the merits of the cycle in progress; the system's state and who holds it; what merits earned here now count as (Acquisition, Reinforcement or Undermining, a best guess as on the Powerplay panel); and the merits and estimated Control Points earned in this system this session, by type. The Control Points use the ratios on the Powerplay tab. See [Powerplay](guide/powerplay.md).

### Flight Alerts

*Enable Flight Alerts* (off); *Fleet carrier jump countdown (alerts at 10, 5 and 1 minute, and at departure)* (on); *Fuel warnings* (on) with *Warn when the tank is at or under [n]%* (25) and *Warn about a star that cannot be scooped when the tank is at or under [n]%* (50), both 5 to 95; *Play a sound when an alert starts* (off; grayed out where no sound can play); *Mining alerts (a core asteroid, a rock rich in your target commodity, low limpets, a nearly full hold)* (on) with *Warn when the limpets aboard are at or under [n]* (0 to 99; 5) and *Warn when the hold is at or over [n]% full (only while you are mining)* (50 to 100; 95); **Test Card**. The target commodity is set under Settings → WFMT → Mining. See [Flight Alerts](guide/always-on.md#flight-alerts).

### Hide overlays

**Hide / show now**: hides every WFMT overlay at once or shows them again. The same action is the **Overlays** line in the WFMT panel, a keyboard shortcut (Windows) and the `!wf overlays` chat command ([Hiding the overlays for a while](#hiding-the-overlays-for-a-while)). It is never saved: the overlays are shown whenever EDMC starts.

### Interdiction Warning

*Enable Interdiction Warning* (off); **Test Warning**. An alert on the screen the moment an interdiction starts, before it resolves. Its red alert colors do not follow the color scheme. See [Interdiction Warning](guide/always-on.md#interdiction-warning).

### Inventory

*Show pillage notifications on the in-game overlay* (off); *Show these inventory bars on the overlay*: **Backpack**, **Ship Locker**, **Carrier Locker**, **Cargo** (each off); **Test pickup**. What the pickup message says, the sound and the categories are on Settings → WFMT → Operations → Inventory.

### Landing

*Enable Landing* (off); *Show on Overlay* (off; the pad diagram and docking text on the screen); *Show in EDMC app* (on; the line and diagram in the WFMT panel); **Test Overlay**, which also previews the in-app text and diagram whatever the ticks say. See [Landing Assist](guide/always-on.md#landing-assist).

### Mining

*Enable HUD Overlay (sends live stats to the overlay - see the Overlay Connection tab)* (off) with **Test HUD**; and the radar: *Show the Mining radar over the game while the Rhino is out (WFMT's built-in overlay, Windows)* (off), **Size (pixels)** (240 to 560; 340), **Background opacity (%)** (30 to 100; 70) and **Test radar**. EDMCModernOverlay cannot draw a picture, so the radar needs the built-in overlay. See [the Mining guide](guide/mining.md#the-live-window).

### Missions

*Show missions on the overlay* (off); *Show the missions for the next jump (the targeted system)* (on); **Mission lines to show (at most)** (3 to 14; 8; the rest become "+N more"); *Show a mission in red when it has less than [n] minutes left* (5 to 720; 60; amber under six hours); **Test Card**. See [Missions on the overlay](guide/missions.md#missions-on-the-overlay).

### Notable Bodies

*Enable Notable Bodies alerts* (off) and a tick for each rule, with its description; **Test Notable**. A violet alert when a scanned body matches a ticked rule. The rules and whether they start ticked:

| Rule | Starts | Matches |
|---|---|---|
| Terraformable landable | on | A landable body that is terraformable, or being or already terraformed |
| High-value body | on | Any terraformable, Earth-like, water or ammonia world, landable or not |
| High-g landable | on | A landable body above about 3 g (29.4 m/s²) |
| Shepherd moon | on | A moon orbiting inside the outer edge of its parent's outermost ring |
| Good FSD injection | on | A body with 5 or 6 of the premium FSD boost materials |
| Green gas giant | on | A Codex entry for one, or a gas giant at a confirmed green temperature |
| Colliding binary | on | Two bodies whose orbits overlap, so they will collide |
| Large landable | off | A landable body over 18,000 km in radius |
| Landable ringed | off | A landable body that also has rings |
| Close orbit | off | A moon orbiting very close to its parent planet |
| Close binary | off | Two bodies orbiting so close to their shared center that they nearly touch |
| High eccentricity | off | An orbit with eccentricity above 0.9 |
| Fast orbit | off | A planet orbiting in under 8 hours |
| Fast rotation | off | A planet with a day under 8 hours (not tidally locked) |
| Wide ring | off | A ring far wider than the body it circles |

If several bodies match at once the cards take turns. See [Notable Bodies](guide/exploration.md#notable-bodies).

### Route

*Enable the Route overlay* (off); **Systems listed** (3 to 20; 8; the jump count and the light years cover the whole route); **Test Card**. With **Route overlay: systems EDSM does not know** ticked in Settings → WFMT → Online (off; it asks EDSM and sends the names of the next systems on the route), a system EDSM has no record of gets a `*`; the Route tab shows a note pointing there. The card follows the route plotted in the game, or the Route Planner's route when there is one. It is shown while the ship is in one of the route's systems; if the ship jumps off it, the card clears until a new route is plotted. See [Route overlay](guide/always-on.md#route-overlay).

### Screenshots

*Show a notification on the in-game overlay when a screenshot is saved* (off); **Test Overlay**. Whether screenshots are converted at all, and where they go, is on Settings → WFMT → Operations → Screenshots (which also has *Include WFMT's built-in overlay in the converted screenshot*).

### Surface Compass

*Enable Surface Compass* (off); **Test Compass**. An arrow, a name and a distance pointing at a hotspot or a mark on the planet the commander is on. What it points at is chosen in the Compass section of the Exploration panel (**Mark**, **Target**, **Marks**); by default it points at the nearest recorded hotspot. See [Compass](guide/exploration.md#compass).

### System targets

*Enable the System targets card* (off); *List bodies worth at least [n] credits, judged by* **Mapped value (what scanning and mapping pays)** (the starting choice) or **Scan value (what scanning alone pays)** (the threshold is 0 to 50,000,000; 100,000 to start); **Rows shown** (3 to 16; 6; the rest are counted); *Also list bodies with life that I have not finished analyzing* (on); *Also list the bodies I have finished (mapped, and their life analyzed), so I can see where I left off* (on); **Test Card**. The two lookups (**System targets: bodies other commanders scanned** (EDSM, once per system) and **System targets: life and points of interest others found** (Spansh, once per system, on arrival), both off) are switched in Settings → WFMT → Online; the tab shows a note pointing there. See [System targets and Body info](guide/exploration.md#system-targets-and-body-info).

## Moving things around

Where each display goes is set once, for every WFMT overlay, on **Settings → WFMT → Overlays → Overlay Placement**.

**Overlay settings are per commander.**

- Saved for the commander who is playing: which cards are switched on, their options, where each one sits, which are hidden, the screen scaling and the look (color scheme, text size, panel opacity, font, corners).
- A card can be off for one commander and on for another.
- The first time a commander is seen, that commander starts with a copy of the choices already in place, so nothing moves.
- A commander's choices are filed when Settings are saved and when the commander changes (log in as another commander, or restart EDMC).
- The three overlay lookups (System targets, Route and Powerplay) are one setting for the whole installation, switched in Settings → WFMT → Online, not per commander.
- Which overlay draws (the built-in one or EDMCModernOverlay), its host and port and the shortcut keys describe the computer, so they are shared.
- Choices saved when EDMC does not yet know the commander go to the first commander it sees.
- **To copy another commander's choices:** play the commander who should receive them, open the **Overlay Placement** tab, pick the other commander next to **Copy all overlay layouts and settings from** (the row shows once a second commander has been seen), press **Copy**, then **OK** in Settings. Everything in the list above is replaced with the other commander's, including turning off cards they do not use; **Cancel** changes nothing, and the other commander is not touched. Machine settings (the overlay connection, the hide hotkey) are not copied.

**Why positions are not raw x and y values**

- Both overlays place things on a fixed 1280 × 960 canvas and map it onto the game window. It treats *positions* and *sizes* differently.
- A position is a fraction of the screen (x ÷ 1280 across, y ÷ 960 down), so the canvas is stretched over the whole screen.
- A size, though, is in screen pixels, scaled by Windows' display scaling. On a 3840 × 2160 screen at 125% scaling that makes a 360-pixel-wide card only 12% of the screen's width.
- A raw number therefore corresponds to a different position on every monitor, and a "right edge" position depends on the size of the display.

**How to place something**

- Select one of nine spots (Top left, Top center, Top right, Middle left, Center, Middle right, Bottom left, Bottom center, Bottom right) and two offsets **in screen pixels**.
- For the edge spots the offsets move the display inward from the chosen edge; for Center and Middle they nudge it.
- "Bottom left, 40 and 40" is 40 pixels in from the bottom left corner of the screen on any monitor, whatever size the display is.
- **Exact position** uses overlay-canvas x and y values instead.

**Hiding a display**

- Each row has a **Show** checkbox. When it is unticked, that display is never drawn, whatever its own settings say, and what is already on screen goes the next time it would redraw.
- The spot and offsets are kept, so ticking it again restores the display to that position.
- It works for every display on the tab (Colonization shopping list, Discovery, Notable, Flight alerts, Route, Expedition Log, Powerplay, Biology, Bio status, Bio radar, Sample popup, System targets, Body info, Interdiction, Missions, Landing, Inventory, Mining stats, Mining radar, Surface compass, Screenshot messages).
- **Reset all to defaults** shows them all again.

**How WFMT determines the screen**

- **With the built-in overlay** it reads Elite's own window: its size and the display scaling where it sits, live, so it follows the window when the game is moved or resized.
- **With EDMCModernOverlay** it reads what that overlay itself is using: the window size, fit or fill mode and display scaling from EDMCModernOverlay's own log (its newest "Overlay scaling updated" line).
- If that isn't there it falls back to Elite's `DisplaySettings.xml` (in `Options\Graphics`; on Linux inside the Proton prefix) for the size, Windows' display scaling, and EDMCModernOverlay's settings for the mode.
- If `DisplaySettings.xml` cannot be read either (a Flatpak EDMC on Linux that has not been given the Graphics folder, for example), it takes the window size from the `size=` line EDMCModernOverlay always writes to its log.
  - That line has no display scaling, so the scaling is the selected one, Windows' where that applies, or 100%.
- With none of these it reads the primary monitor's size from the operating system (on Windows the hardware resolution, whatever the display scaling; on Linux `xrandr`, run on the host when EDMC is a Flatpak), so an ultrawide or a 4K screen is not taken for 1080p.
- Only when that cannot be read either does it assume a 1920 x 1080 screen.
- The tab shows what it found, for example *3840 x 2160, full screen, display scaling 125% (EDMCModernOverlay log); overlay mode fill*.
- The display scaling and the mode can be set manually on that tab if they are wrong.

**The three size settings.** They answer different questions, and the first two are found on Overlay Placement:

- **Display scaling** is the percentage Windows applies to the monitor Elite is on (Settings > System > Display > Scale).
  - WFMT sizes every display in pixels, and Windows' scaling multiplies those pixels, so it needs the percentage to know how much room a display takes and where its edge is.
  - The choices are Automatic, 100%, 125%, 150%, 175%, 200%, 250% and 300%.
  - Where the value cannot be read (Linux, a Flatpak EDMC without the Graphics folder) it is the value selected, or 100%.
- **Overlay mode** is how the overlay's 1280 x 960 canvas is laid over the game window.
  - **Fit** keeps the canvas's 4:3 shape and shows it with bars on a wider screen, and the overlay limits a display's far edge on both axes.
  - **Fill** stretches the canvas over the whole window, and on a wide screen the limit applies only across (the right-hand edge below).
  - **Automatic** follows EDMCModernOverlay's own setting, or Fill when it is not found.
  - The built-in overlay has no canvas and draws exactly where it is told, so it ignores the mode.
- **Text size** (Appearance: Default or Larger) is separate. It makes the text itself bigger, and every display is sized from it.

If displays land in the wrong place or at the wrong size, check that the line on the tab matches the screen, correct whichever of display scaling and mode is wrong, and press **Detect screen again** or **Show placement preview**. All three are saved per commander.

**The right-hand edge (EDMCModernOverlay only; the built-in overlay has no such limit and draws against any edge)**

- Across a wide screen EDMCModernOverlay limits a shape's left position plus its pixel width to the canvas width, and squashes the shape if it would pass that, so a display cannot simply be drawn against the right edge.
- The overlay does apply a *group offset* after that limit (it is how its own Overlay Controller moves things), and offers it to plugins.
- So for a display on the right, WFMT draws it as far right as the limit allows and sets that display's group offset through EDMCModernOverlay's own plugin API to carry it the rest of the way.
- These appear as offsets on WFMT's groups in the Overlay Controller. A group moved manually in the Overlay Controller takes precedence over WFMT's setting.
- This needs EDMCModernOverlay. Without it (or if the call fails) a display on the right stops where the limit allows, a little short of the edge.
- The Overlay Placement tab has a switch, **Carry displays on the right to the screen edge**, that turns this off (and clears the offsets) when displays are placed incorrectly.
- The bottom edge needs none of this.
- The two Mining displays share one overlay group, so they stop at the limit rather than being offset.

**Opacity and clicking through**

- The built-in overlay lets clicks and keys through to the game and never takes the focus.
- **Settings → WFMT → Overlays → Appearance → Panel opacity** sets how solid every WFMT display's background is (100%, 90% by default, 75%, 60%, 40% or 25%). The text stays solid, so a faint panel lets the game show through behind readable text.

**Plain panels.** The Route, System targets, Body info and Exobiology cards and the Bio radar are plain dark panels, with no colored bar or outline.

**The layout editor**

- Above the table is a to-scale picture of the screen with a grid and a box for every display.
- Drag a box and drop it: WFMT works out the spot (the third of the screen its center is in) and the offset in screen pixels and fills in the table.
- A box dropped within a few pixels of an edge snaps flush to it (offset 0), however large the box is, one near the middle snaps to the center line, and the rest snap to the selected grid (20, 40, 60 or 120 pixels). Untick *Snap to the grid and to edges* to place a box exactly.
- Boxes are drawn at each display's size at the chosen text size, so the picture shows the room each display takes.
- A card that grows (a list with more rows) is placed from the size it is drawn at, so a zero offset at the bottom or right is the screen edge.
- **Picture size** (Default, Large or Extra large) makes the picture bigger for finer placement; the choice is remembered.
- Typing in the table moves the box, and *Show placement preview* draws the real display on the screen.

**Default spots**

- On a 1920 x 1080 screen or larger the default spots do not overlap each other. That includes ultrawide screens: 21:9 (2560 x 1080, 3440 x 1440), 32:9 (3840 x 1080, 5120 x 1440) and a triple-screen span of 5760 x 1080.
  - 1920 x 1080 is the smallest screen WFMT is laid out for. On a smaller one some boxes can overlap until they are moved on Overlay Placement.
  - The Route card is at the top left.
  - The right-hand column runs Notable, Surface compass, Inventory, Mining stats, Flight alerts, Missions and Screenshot messages from the top.
  - System targets and Body info sit one above the other in the lower middle of the right half of the screen.
- The Exobiology cards start at the top center (Bio status), the bottom center left of the Body info card (Biology), the left middle (Bio radar) and above Biology (Sample popup).
- The Expedition Log card sits at the top left, to the right of the Route card. The Powerplay card sits at the top right, to the left of the Notable find and Inventory cards.
- The Bio radar and the Mining radar share a spot with the Colonization list, and Bio status and the Expedition Log with the Interdiction warning, because those are not normally up at the same time (a planet's surface, a construction depot, supercruise).
- The displays are sized in pixels, so on a smaller screen they take up more of it and some can overlap: use **Show placement preview** and move them.
- A position set manually is never changed.

**Checking placement on the real screen**

- **Show placement preview** draws a labeled box for every display, at its real size, for 12 seconds, using the values currently typed (before **OK** is selected).
- **Reset all to defaults** puts everything back.
- **Detect screen again** re-reads the overlay's log and the game's files.

An **Exact position** that would leave a display off the overlay's canvas (for example a leftover `x = 1280` on a 1280-wide screen) is ignored: the display uses its default spot instead, and the EDMC log says so. The saved text is not changed.

### Appearance: colors and text size

**Settings → WFMT → Overlays → Appearance** sets how every WFMT overlay looks, all at once:

- **Color scheme**: Elite orange (the default), Ice blue, Phosphor green, Amber mono, High contrast, or Color-blind safe (Okabe-Ito colors). The chips show each color's role.
- **Text size**: Default or Larger. The starting value is **Larger**.
- **Panel opacity**: how solid every display's background is (100%, 90% by default, 75%, 60%, 40% or 25%).
  - The text stays solid, so a faint panel lets the game show through behind readable text.
- **Corners (built-in overlay)**: how rounded every card's corners are: Square, Slightly rounded, **Rounded** (the default), or Very rounded.
  - It applies to the panels only (dividers and bars stay square) and only to WFMT's built-in overlay.
  - EDMCModernOverlay cannot draw rounded rectangles, so its cards stay square.
- **Overlay font**: the font the overlay draws in; see [Fonts](#fonts) below. It follows whichever overlay is chosen.
- **Show sample** draws the Colonization card with the scheme and size currently picked (before **OK** is selected); **Reset appearance** restores the starting values.

**Padding and line spacing** are **fixed**, so columns stay lined up.

- Every card uses the same padding, so its text sits the same distance from the border on all four sides, and every line of text starts at the card's left edge (no card centers its text).
- With the built-in overlay each card's box is sized from the text itself, measured in the font in use (with 5% to spare for the font's rounding), so the box fits closely and right-hand values sit against its edge.
- EDMCModernOverlay cannot measure text for a plugin, so with it each card's width and height are worked out from the character count at the chosen size, with a further 10% added to every width, so text sits inside the border. Its own font limits (`min_font_point` and `max_font_point`) apply on top.
- Placement accounts for the new size too (a display anchored to the bottom or right keeps its edge).
- The Interdiction warning keeps its fixed red alert colors whatever scheme is chosen.

- If the overlay is still starting when Landing Assist has something to draw, WFMT retries for up to three minutes, so
  the diagram shows up once the overlay is ready.
- **EDMCModernOverlay has its own placement tool**, the Overlay Controller, which moves each
  plugin's display, change anchors and backgrounds, and keep different profiles. See its wiki.

## The built-in overlay (Windows)

WFMT's own overlay is a transparent window it lays over Elite, drawn from inside EDMC. Select it under **Settings → WFMT → Overlays → Overlay Connection → Which overlay draws**, select **OK**, and start
Elite in **borderless or windowed** mode (a fullscreen game cannot be drawn over). It is off until selected, and selecting EDMCModernOverlay again switches back. See [the comparison above](#step-1-choose-an-overlay).

**How it behaves**
- It follows Elite's window as the window is moved or resized, and uses the display scaling where the window is.
- It shows only while Elite is the window in front, and hides when another window is brought to the front (a stale card is never left over another program). It lets clicks and keys through to the game and never takes the focus.
- When Elite returns to the front, the overlay places itself above it; it checks every half second.
- It lives and dies with EDMC, so it cannot leave a second overlay window behind (see [Known issues](guide/known-issues.md)).
- It draws all of WFMT's displays, with Overlay Placement and its layout editor, panel opacity, color schemes, text size and Hide overlays working as they do with EDMCModernOverlay.
- **Check connection** reports whether it is running and whether it has found Elite's window.

**Screenshots**
- Elite's own screenshot key (F10) never includes an overlay.
- **Windows' capture tools** (the Snipping Tool, Win+Shift+S, Print Screen and the Game Bar) take the focus during capture. WFMT recognizes them, so the overlay stays up and is in the picture.
- For any **other tool** that takes the focus, tick **Keep showing when Elite is not the window in front** in the same box; the overlay then stays up whenever Elite is running.
- To have the cards in a screenshot Elite itself takes, tick **Include WFMT's built-in overlay in the converted screenshot** under **Settings → WFMT → Operations → Screenshots**: the converted copy then has
  the cards that were on screen when the key was pressed drawn onto it.

**Limits**
- Windows only; Linux uses EDMCModernOverlay.
- It draws WFMT's displays only. Other plugins' displays need EDMCModernOverlay (see [Do I need EDMCModernOverlay?](#do-i-need-edmcmodernoverlay)).
- The design and the remaining work are in [the built-in overlay specification](NATIVE_OVERLAY_SPEC.md).

## Fonts

**Settings → WFMT → Overlays → Appearance → Overlay font** chooses the font the overlay draws in. Which font that is depends on the selected overlay:

**Built-in overlay: WFMT's own fonts**
- It starts with **Source Sans 3**, which WFMT ships (a clear font with lower case letters; SIL Open Font License, the license is in the `fonts` folder next to it).
- **Add font file...** copies a selected `.ttf` or `.otf` file into WFMT's own `fonts` folder (inside the plugin folder) and chooses it (select **OK** in Settings to keep the choice). The change is used as soon as **OK** is selected; no restart is needed. **Open fonts folder** shows the folder;
  font files can also be copied into it manually and selected from the list.
- An added font **remains through WFMT updates** (an update replaces only the files it ships). Delete the file to remove the font.
- WFMT does not install or license fonts. The license of an added font applies to its use and redistribution.
- If a chosen file is missing or unreadable, WFMT falls back to Source Sans 3.

**EDMCModernOverlay: its font, for every plugin**
- The overlay takes the first font it can load from the list in its `overlay_client/fonts/preferred_fonts.txt`, and its default is Elite's cockpit font, which has **capital letters only**: every plugin's text shows in capitals.
- WFMT edits that list: select a font from the folder, or select **Add font file...** to copy one in, and WFMT places it first (keeping a `.bak` of the old list once). **Overlay default** goes back to the cockpit font.
- The change takes effect when EDMCModernOverlay starts again (restart EDMC) and applies to every plugin's text, because the overlay uses one font. WFMT cannot give its own cards a different font here.
- An EDMCModernOverlay update can put its own list back.

**Both:** the font choices are independent. WFMT's species names are written `Tussock pennatis`; in the cockpit font they show as `TUSSOCK PENNATIS`. No overlay can draw italics, so scientific names are not italicized.

## Streaming and recording

Both overlays (WFMT's built-in overlay and EDMCModernOverlay) draw in a separate transparent window laid over Elite. They do not draw inside the game's own graphics. Whether a stream or recording includes the overlay depends on the capture method, and no capture program has been tested.

- The built-in overlay is shown only while Elite is the window in front (see [The built-in overlay](#the-built-in-overlay-windows)). **Keep showing when Elite is not the window in front** in the same box keeps it shown whenever Elite is running.
- Elite must run borderless or windowed.
- Converted screenshots can include the overlay: select **Include WFMT's built-in overlay in the converted screenshot** under **Settings -> WFMT -> Operations -> Screenshots** (Windows, built-in overlay only).

## Hiding the overlays for a while

Every WFMT overlay can be hidden at once and restored to its previous state:

- Select the **Overlays shown (click to hide)** line in the WFMT panel (under the credits and merits lines); it then reads **Overlays are hidden (click to show)**.
- Use the keyboard shortcut (Windows, works while Elite has the focus; Ctrl+Alt+Shift+O by default) or type `!wf overlays` in Elite's chat (Windows and Linux, once chat commands are switched on).
  Both are set under **Settings → WFMT → General → Shortcuts** (see [Shortcuts](guide/shortcuts.md)). **Settings → WFMT → Overlays → Hide overlays** has a **Hide / show now** button.
- Hiding clears what is on screen at once, and showing puts back what had not run out, including the Colonization card, which is drawn once and left up.

Limits:

- It hides WFMT's overlays only, not another plugin's.
- It is not saved, so the overlays are shown whenever EDMC starts.
- The keyboard shortcut exists on Windows only, because a Linux desktop gives a program no portable way to hear keys while another window has the focus (and Wayland gives none). On Linux, use the chat command, the panel line or the button.
- It does not hide overlays automatically, for example in the galaxy map.

## Without an overlay

With EDMCModernOverlay selected, WFMT tries to reach it when a feature draws something. When none is running, WFMT stops trying for 30 seconds before the next attempt, writes one line to EDMC's log stating that no overlay was found, and the on-screen displays do not appear.

## If nothing shows up

**With the built-in overlay (Windows)**
1. Is **WFMT built-in overlay** selected under Overlay Connection, and was **OK** selected? **Check connection** says whether it is running and whether it has found Elite.
2. Is Elite in **borderless or windowed** mode? A fullscreen game cannot be drawn over.
3. Is Elite the window in front? The overlay hides when another program is in front (**Keep showing...** keeps it shown).
4. Are the overlays hidden (the line in the WFMT panel reads *Overlays are hidden*)? Select the line to show them again.
5. Select a feature's test button, check the placement preview, and reset a display to its default position on Overlay Placement when only one display is missing.
6. Check EDMC's log (Help menu) for a WFMT line about the overlay, and include it in a problem report.

**With EDMCModernOverlay**
1. **Is the overlay running?** WFMT cannot start it.
2. **Does the port match?** Compare the port on WFMT's Overlay Connection tab with the overlay's.
3. **Is Elite in borderless or windowed mode?** Some overlays cannot draw over exclusive fullscreen.
4. **Select the feature's test button.** The result states whether the overlay was reachable. The message "could not reach the overlay" indicates step 1 or 2.
5. **Was EDMC restarted?** Restart EDMC (and the game, if needed) after installing or changing an overlay.
6. **Check the logs.** EDMC's Help menu opens its log folder. EDMCModernOverlay keeps its own logs. Include them in a problem report.
7. **Linux:** EDMCModernOverlay is required (the built-in overlay is Windows only; the original EDMCOverlay is Windows-only too). See the
   [Linux guide](guide/linux.md). If EDMC is a **Flatpak** and
   **Check connection** succeeds but nothing is drawn, the Flatpak needs permission to start the overlay
   window; the Linux guide gives the one-line `flatpak override` command.
8. **Is text doubled or ghosted?** Two overlay windows can be running; see [Known issues](guide/known-issues.md).

**Either:** does only one display never show? Its saved position can be outside the screen. Reset it on the Overlay Placement tab; see
[Troubleshooting](guide/troubleshooting.md#one-display-never-shows-though-test-and-the-overlay-window-both-work).

## Technical notes

**With EDMCModernOverlay**

- WFMT sends its drawings to the overlay over a local network connection on the same computer (the port above). Nothing leaves the computer.
- WFMT keeps a single connection open for every feature, and registers a "Plugin Group" with EDMCModernOverlay for each on-screen card so its background draws properly.

**With the built-in overlay**

- Nothing is sent anywhere.
- WFMT draws the window itself, from Pillow (the imaging library EDMC ships), and reads Elite's window position and size.

The technical details are in [TECHNICAL.md](TECHNICAL.md) section 10 and the [built-in overlay specification](NATIVE_OVERLAY_SPEC.md).
