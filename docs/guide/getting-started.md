# Getting started

This page takes you from nothing to a working WFMT panel, then shows you how to find your way around it.
No programming is needed. If something looks wrong, for example overlay text that looks doubled or is all in capitals, see [Known issues](known-issues.md).

**On this page:**

- [What you need](#what-you-need)
- [Installing](#installing)
- [Updating](#updating)
- [A first five minutes](#a-first-five-minutes)
- [Finding your way around](#finding-your-way-around)
- [Commanders and your data](#commanders-and-your-data)
- [Backing up your data](#backing-up-your-data)
- [If EDMC wasn't running](#if-edmc-wasnt-running)
- [Opening the pop-out windows](#opening-the-pop-out-windows)
- [Button names](#button-names)

## What you need

**1. EDMC.** WFMT is a plugin for [EDMC](https://github.com/EDCD/EDMarketConnector) (Elite Dangerous Market
Connector), a free companion program. EDMC reads the game's journal files while you play and hands the events to
plugins like WFMT. It runs on Windows and Linux. If you already use EDMC, you have it.

**2. An overlay (optional).** An *overlay* draws on top of your game screen.

WFMT only needs one for its on-screen extras:

- Discovery Alerts, Notable Bodies, Landing Assist, Interdiction Warning, Flight Alerts and the Route.
- System targets, Body info, the Exobiology cards, the Expedition Log and the Surface Compass.
- The optional overlays for Inventory, Mining, Missions, Colonization and Screenshots.

Everything else works without one. There are two to choose from:

- **WFMT's built-in overlay** (**Windows only**; there is no Linux version, and none is planned for now): nothing to install. Choose it under **Settings → WFMT → Overlays → Overlay Connection → Which overlay draws**. It draws WFMT's displays only.
- **[EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay)** (Windows and Linux): a separate program you install. **On Linux you must install it** to see any WFMT on-screen display. It is also still what other
  plugins' overlays need; you can run it next to the built-in overlay.

Set Elite to **borderless** or **windowed** mode and the overlay will work. The step-by-step guide is
[Setting up the on-screen overlay](../OVERLAY_SETUP.md).

**Every WFMT overlay is off until you tick it in Settings.**

## Installing

1. **Download the plugin.** Go to the
   [latest release](https://github.com/rwharpernc/wayfarers-multitool/releases/latest) and download
   **`Wayfarers-Multitool.zip`** from the **Assets** list. It holds only the plugin, in one folder called `Wayfarers-Multitool`.

   **Warning:** don't use the green **Code → Download ZIP** button. That downloads the whole source repository, which you don't need and which won't work as a plugin.

2. **Find EDMC's plugins folder.** In EDMC, open **File → Settings → Plugins** and click **Open** next to
   "Plugins folder". A file window opens. On Windows it is usually
   `%LOCALAPPDATA%\EDMarketConnector\plugins\`.

3. **Extract the ZIP into that folder.**
   - *Windows:* right-click `Wayfarers-Multitool.zip` → **Extract All…**, and set the destination to the plugins folder itself.
   - *Linux:* `unzip Wayfarers-Multitool.zip -d <your plugins folder>`

4. **Check the result.** You should now have `plugins/Wayfarers-Multitool/load.py`. If you see `plugins/Wayfarers-Multitool/Wayfarers-Multitool/load.py`, you
   extracted one level too deep; move the inner folder up.

5. **Restart EDMC.** A **Wayfarer's Multitool (WFMT)** panel appears in the main window. It always shows
   (there is no title to fold it away).

If it doesn't, see [Troubleshooting](troubleshooting.md#the-wfmt-panel-doesnt-appear). On Linux, also read
[WFMT on Linux](linux.md) before you go further, because EDMC needs a couple of settings there.

## Updating

Download the new `Wayfarers-Multitool.zip` and extract it over the existing `Wayfarers-Multitool` folder, replacing files when asked.

**Don't delete the old folder first.** Your saved data (mining hotspots, trade sessions, ship builds and so on)
lives inside it.

WFMT can also update itself. Turn on **Automatically download and install updates** under
**File → Settings → WFMT → General → Updates**. It is **off by default**, and it only looks at official published
releases. The **Release notes** link on that tab opens the latest release's page in your browser.

The first line under the mode buttons always says which version you are running (**Plugin: v1.0.0**).

- While an update is coming it says, for example, **Plugin: v1.0.0 (downloading v1.0.1...)**.
- Once the update is downloaded it turns bold black on **orange** and reads **the new version's number, then download - Restart EDMC**.
- The update only takes effect when EDMC starts again; nothing is swapped in while it runs.
- After the restart the line shows the new version with **(updated)** after it, in green for a short while.
- Clicking the line opens the release page.

*Building from source is for developers only. See [DEVELOPMENT.md](../DEVELOPMENT.md).*

## A first five minutes

You don't have to configure anything to get value out of WFMT, but this short tour helps:

1. Look at the row of buttons at the top of the WFMT panel. Those are the eight **modes**. Click one and the panel below
   changes. Hover over a button for a moment to see its full name.
2. Open **File → Settings → WFMT**. Each mode has its own tab. Look through the ones you care about and turn
   things on or off.
3. If you want on-screen alerts, set up an overlay (see above), then press a **Test** button in Settings to
   check it works.
4. **Linux only:** make sure EDMC's *Journal directory* is set. See [WFMT on Linux](linux.md).
5. Play. Most things fill themselves in as you go.
6. Skim the "What the game does and doesn't tell us" section at the end of each mode's guide. It lists what the
   game never records (for example, a fleet carrier's cargo is only exact after you open Carrier Management) and
   how to work around it.

**Why WFMT sometimes can't tell you something.** WFMT, like every third-party tool, only knows what the game writes to its journal files, and not everything is logged.

- It fills some gaps from Frontier's servers (through a signed-in EDMC) and from data players and communities report (Spansh, EDSM, Canonn, edastro, Raven Colonial).
- It works around the rest with labeled estimates and small steps you take.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## Finding your way around

### The mode buttons

WFMT has one panel with eight modes. You switch between them with the button row at the top of the panel:
**P.P.** (Powerplay), **BGS**, **EXP** (Exploration), **MIN** (Mining), **TRD** (Trade), **MSN** (Missions),
**OPS** (Field Ops) and **COL** (Colonization).

**Every mode keeps working in the background** while you look at a different one. Nothing pauses. If you're
mining and flip to Trade to check a price, your mining stats keep counting.

### The lines under the mode buttons

Just under the mode buttons, above the page itself, WFMT shows these lines, on every mode:

- **Plugin**: the version you are running, for example `Plugin: v1.0.0` (see "Updating" for what it says during an update).
- **Game mode**: For example *You are in Solo mode.*, *Open*, or *Private Group* with its name.
- **Credits**: what you've earned or lost since you logged in, for example `+1,234,567 cr earned (+411,522 cr/hr)` or `-5,000 cr lost`. It is your balance now minus your balance at login.
  - The hourly rate appears once the session is a few minutes old.
  - **Click it** to open the Credits Ledger: income by activity (trade, exploration data, exobiology data, mission rewards, bounties and bonds), by day, and the game's lifetime totals.
- **Merits**: Powerplay merits earned since you logged in, for example `Merits this session: +1,234 (+567 merits/hr)`.
  - It appears after your first merit of the session, so it stays out of the way if you do not play Powerplay.
  - The rate is the merits divided by the time since you logged in, so it falls while you stop earning.
  - The Powerplay mode's **CP** figures are Control Points, a separate number.
- **Overlays**: `Overlays shown (click to hide)`. Click it to hide every WFMT overlay at once and click again to bring them back.
  - See [Overlay setup](../OVERLAY_SETUP.md#hiding-the-overlays-for-a-while).
  - Windows also has a keyboard shortcut, and both systems have a chat command: see [Shortcuts](shortcuts.md).

### Pages

Mining, Trade and Missions have more than one page. Click the large orange **◀** and **▶** buttons at the top of
the panel to move between them. For example, Trade has **Session**, **Routes** and **Market** pages.

### Collapsing the panel

The panel itself never folds away. Sections inside the modes (Exploration, Notes, Materials and so on) fold: they start folded, click a
section's title (▸ / ▾) to open it. They fold again each time EDMC starts.

### Window height

The EDMC window is small and every plugin shares it. So WFMT **resizes the window's height to fit** whenever you
open it, switch modes, or expand or collapse a section. You never need to drag it taller. It leaves your width and
position alone.

If you'd rather set the height yourself, untick *Resize the EDMC window's height to fit WFMT automatically* under
**File → Settings → WFMT → General → Window**. The same page lets you hide the buttons of modes you do not use (a hidden mode keeps working in the background).

## Commanders and your data

**Everything WFMT saves about your play belongs to one commander.** Nothing is shared between commanders, and switching commander in EDMC switches what every feature shows:

- Trade sessions and route start, Powerplay and BGS ledgers, Missions.
- Mining hotspots and the ground your Rhino has driven.
- The Boxel Survey position and finds, the Codex tally.
- Colonization sites, Ship Builds, Organic Scanning and Powerplay history.

Names are matched ignoring case, so `EXAMPLE` in the journal and `Example` in EDMC are the same commander.

The few things that are not about a commander are the same for everyone: your Settings, the downloaded Codex catalog
and the record of which journal files Trade has read.

### Backing up your data

WFMT keeps what it records about your play as files in its plugin folder. That covers expeditions and the Expedition Log, system surveys and visit history, Boxel Survey finds, Exobiology state and finds, the Codex tally, missions, trade and ledgers, mining hotspots, notes and so on.

Updates never touch these files, but nothing else copies them, so a deleted or reinstalled plugin folder loses them.

**To make a backup:**

1. Open **Settings → WFMT → General → Backup → Back up my data**.
2. Choose a folder. It saves all of your data as one dated zip there (`WFMT-data-20261021-093015.zip`).

About the backup:

- It is a plain copy of the files, usually a tenth of their size, and nothing is changed or sent anywhere.
- Choose a folder outside the plugin folder, such as Documents or a cloud-synced folder; WFMT refuses one inside it.
- The zip also holds `backup-info.json` (WFMT version, date, platform and the files).

- **Every commander is in it.** Most files hold a separate section for each commander on the install, so the zip does too.
- **Left out on purpose:**
  - The Raven Colonial keys (`rcc_keys.json`), because a backup is meant to be copied around.
  - The downloaded Codex catalog, which WFMT fetches again.
  - The optional local star index (`star_index` folder, about 110 MB, built from a public download and made again from Settings).
  - Your Settings and your overlay positions held in EDMC's own configuration are not files in the plugin folder, so they are not in it either. `overlay_settings.json` (each commander's overlay choices) is.
- **To restore or move it:** use **Restore my data...** on the same tab.
  1. It asks for a backup zip, checks that it is a WFMT data backup (a zip with anything else in it is refused), shows what it holds and asks before doing anything.
  2. The restore happens the next time EDMC starts, because WFMT cannot replace files it is using. **Cancel the waiting restore** undoes it until then.
  3. It replaces the backup's files for every commander in them, leaves any file the backup does not hold, and keeps the files it replaced in `backups/pre-restore-<date>.zip` in the plugin folder (the newest five).
  4. To move your data to another computer, install WFMT there, restore the zip, and start EDMC.
  5. The files are plain JSON, so other tools can read them too.
- **Automatic backups:** tick **Back up automatically**, choose a folder and how many days apart (7 by default).
  - WFMT makes a backup when EDMC starts if the newest automatic one is that old, and again just before an update installs.
  - They are named `WFMT-data-auto-<date>-<time>.zip` and only the newest ten are kept; backups you make with the button are never deleted.
  - It is off until you switch it on, and it needs a folder outside the plugin folder.

### If EDMC wasn't running

If you start EDMC **before the game**, nothing tells WFMT who is playing until you log in. So a few seconds after start-up
it reads the last commander from your newest journal and every feature starts with their saved data; logging in as
someone else then switches everything to them. (The Game Mode and Credits lines still wait for a running game.)

EDMC only hands WFMT the events that happen while it runs. For anything played with EDMC closed, WFMT reads the game's
journal files when EDMC starts (and, for Trade, once a minute after that). Each feature does it its own way and only
adds what is new, so nothing is counted twice:

| Feature | What it catches up on | How far back |
|---|---|---|
| **Trade** | Session tally, stock, carrier figures, route start | New or grown journal files, every minute |
| **Powerplay** | Merits and Control Points | The gap since EDMC last saw the journal (up to the scan depth in Settings) |
| **BGS** | Your effect on factions this tick | From the start of the tick |
| **Missions** | Active missions, kill progress, cargo progress, Community Goals | The last 2 weeks |
| **Colonization** | Deliveries (also counted into your history) and sites docked at, and transfers to your fleet carrier (its FC column) | 14 days, or back to your oldest site (30 days at most); the delivery history is also rebuilt once from every journal |
| **Codex Completionist** | Codex finds, for the active commander | Everything since the last find it counted |
| **System targets, Body info and the Exploration Dashboard** | The survey of the system you are in: the bodies you scanned, mapped and analyzed there, including a system you scanned while EDMC was closed | The journals that hold your visits to that system, when you log in or when EDMC starts |
| **Your ship** (Route Planner, fuel percentage, jump range, landing-pad size) | The ship you are flying, from the last `Loadout` in your newest journal | When EDMC starts with the game already running |
| **Organic Scanning** | The progress of each species you logged, sampled or analyzed (the stage, not the position of a sample), and the conditions, genera and first-footfall flag of bodies scanned with EDMC closed, so the prediction works when you land | The last 14 days; a sample is skipped if its body is not named in them |
| **Boxel Survey** | Systems you arrived at, and the notable bodies and biological signals you scanned (systems new to the survey log; a system it already had keeps its scanned count) | The last 14 days |
| **Mining** | The run in progress (the pages); every earlier run (the Mining History window); the rings (the Space Mining Book) and the bodies with mining locations or Rhino mining (the Surface Mining Book's *From your journals* group) | The current journal file for the pages; every journal for the history and the two books, read once in the background (a notice says so) and then only the new ones |
| **Carrier Route** | Your carrier's place, the tritium in its tank and the space it uses | The last 30 days, when the Carrier Route window first opens |
| **Exploration Value** | Region, system scan progress, last data sales | The current journal file |
| **Inventory** | Backpack and ship locker | Taken from EDMC's own rebuilt state |
| **Credits line** | The session, if it is the same journal file | The saved session |

Landing Assist, Interdiction Warning, Discovery Alerts, Notable Bodies, Auto-Honk, Screenshots and the position
of an Organic Scanning sample only matter at the moment they happen, so there is nothing to catch up. See each
mode's guide for the limits.

**Restarting EDMC is safe, at any time, as often as you like.**

- Every catch-up only adds what is new or raises a figure, never lowers one, so a restart in the middle of a session (to load an update, for example) cannot lose or double-count anything.
- A catch-up runs in the background a few seconds after EDMC starts, and a card or window can take a moment to fill in.
- If a number is still behind the game a minute after you have logged in, the cause is in the next table.

**What a catch-up cannot recover, and what to do:**

| After playing with EDMC closed | Why | What to do |
|---|---|---|
| A species shows less progress than the game (`2/3` for one you analyzed), or a body has no predicted species | Organic Scanning is caught up from the last **14 days** of journals, and a sample is skipped if no event in them names its body (a body scanned and sampled more than 14 days apart) | Restart EDMC once. If it is still behind, sample or scan the species again: the next scan sets the right stage |
| The marker for a plant you identified with the Composition Scanner is missing | The marker comes from the scan event while EDMC runs, and is not rebuilt from old journals (rebuilding it could bring back plants you already sampled) | Scan the plant with the Composition Scanner again |
| The distance to the last sample on a body is wrong or blank | The journal does not record where a sample was taken; WFMT reads your position from `Status.json` as you sample | None: it is right again from your next sample |
| An expedition's totals look low | The Expedition Log reads the journal live | Press **Rescan** on the expedition |
| Codex entries you found before WFMT first ran (a new install, or a commander new to it) | Codex Completionist catches up forward from the last find it counted, so it starts from nothing for a new install | **MY CODEX → Backfill Journals** once |
| A Powerplay session or a BGS period looks wrong | Their catch-ups are limited by the scan depth and the tick | **RESCAN** (Powerplay); BGS rebuilds a closed period by itself |
| A mining run that began before a restart | The Mining pages read the current journal file only (Mining History and the two books read every journal) | The run carries on from the journal file in use; an earlier file's run is not rejoined |

None of these is lost data in the game; they are limits of what WFMT can read back from the journals.

To tell that a catch-up ran, look in EDMC's log (`EDMarketConnector-debug.log`, in EDMC's log folder; on Windows `%LOCALAPPDATA%\EDMarketConnector\logs`). A catch-up writes a line such as `Organic Scanning caught up from the journals: 3 bodies`, which is the quickest way to tell it ran.

### Settings

All settings live under **File → Settings → WFMT**, in tabs: General, Powerplay, Missions, Exploration, Mining,
Trade, BGS, Colonization, Field Ops and Overlays. Some have a row of tabs of their own:

| Tab | Inner tabs |
|---|---|
| **General** | Window (including *Suggest system names from Spansh while typing*), Updates, Backup (**Back up my data**), Help (**Report an issue**, **Copy diagnostics**), Online lookups, Shortcuts |
| **Exploration** | Exploration Value, Organic Scanning, POI Reference (GEC, Canonn and Codex Completionist settings), Boxel Survey, Region Sweep, Waypoint Route, Auto-Honk, Expedition, Nearest place to land |
| **Field Ops** | Screenshots, Inventory, Ship Builds |
| **Overlays** | Overlay Connection (which overlay draws, and EDMCModernOverlay's host and port), Appearance (color schemes, text size, opacity and the overlay font), Overlay Placement, Hide overlays, then one tab for each feature that draws on your screen: Colonization, Discovery, Inventory, Interdiction Warning, Flight Alerts, Route, Expedition Log, System targets, Body info, Exobiology, Missions, Landing, Surface Compass, Mining, Notable Bodies, Screenshots |

This is where you switch things on and off and adjust how they behave.

### Typing a system name

Every box that takes a system name suggests systems as you type, from the second letter. That covers an expedition stop, the Expedition planner's start and end, the trader finder's *Search from*, Colonization's *Around*, a mining hotspot or ring reserve, a note, a waypoint and a Boxel Survey seed.

- **What it suggests:** the systems you have been in this session first, then ones WFMT already holds (expedition stops, notes).
- **Keys:** **Down** and **Up** move through the list, **Enter** or a click takes the highlighted one, and **Escape** closes it. **Enter** with nothing highlighted does what the box always did (add the stop, run the search).
- **Systems you have never been to:** tick **Suggest system names from Spansh while typing** under Settings → WFMT → General → Window. It is off until you tick it, and then the letters you have typed so far go to Spansh ([what goes on the internet](internet-and-privacy.md)).

### What you can and can't switch off

You can hide a mode you don't use under **Settings → WFMT → General → Window → Mode buttons on the main panel**. A hidden mode keeps working in the background, and at least one mode stays shown. Switches exist for individual features:

| | |
|---|---|
| **Have a switch** | Auto-Honk, Discovery Alerts, Notable Bodies, Organic Scanning, Codex Completionist, Exploration Value (and its two online extras), BGS (and its tick detection), Landing Assist, Interdiction Warning, Flight Alerts, the Surface Compass, the Trade and Mining online lookups, and every overlay |
| **Have no switch** | The core of Powerplay, Missions, Mining and Trade tracking, screenshot conversion, Inventory tracking, Materials and Engineering, the Expedition planner, Colonization, Ship Builds, Boxel Survey, and the GEC and Canonn POI finders. Some of these (Boxel Survey, the POI finders) only fold away and do nothing until you press a button |

Most online lookups are off until you switch them on, or only run when you press a button. The exceptions are listed
in [what goes on the internet](internet-and-privacy.md).

### Pop-out windows

Sessions, rare goods, inventory, the BGS report, the Surface Mining Book and others open as their own windows. They have a
dark look, remember their size and position, and close with **Esc** or the ✕. The main panel itself follows your
EDMC theme.

## Opening the pop-out windows

Switch to the mode first, then use the button listed here.

| Window | Mode | How to open it |
|---|---|---|
| Powerplay Sessions (tabs: Current session, Systems, Cycles, Daily, Megaships, History) | Powerplay | **SES** button (bottom row of the panel) |
| Rare Goods Finder | Powerplay | **RARES** button, next to SES |
| BGS Report | BGS | **REPORT** button |
| Codex Completionist | Exploration | **MY CODEX** button in the Codex Completionist section |
| Notes | Exploration | **NOTES** button in the Notes section |
| Expedition | Exploration | **EXPEDITION** button in the Expedition section |
| Nearest place to land | Exploration | **FIND** button in the Nearest place to land section |
| Route Planner | Exploration | **PLOT** button in its section of the panel (or **Route Planner** in the Dashboard's header) |
| Carrier Route | Exploration | **Carrier route** button in the Route Planner window |
| Exploration Dashboard (tabs: Overview, Orbit, Surface, Exploration) | Exploration | **DASHBOARD** button in the Dashboard section |
| Marks (for the Surface Compass) | Exploration | **MARKS** button in the Compass section |
| Watch list | Trade | **WATCH** button in the Watch list section |
| Missions window (tabs: Active, By place) | Missions | **Missions window** button at the very bottom of the panel, or click a mission's card |
| Source commodities | Missions | **Find sources** button at the very bottom of the panel (or **Sources** in the Missions window) |
| Inventory | Field Ops | Click one of the **inventory bars** (there is no button) |
| Materials | Field Ops | **MATERIALS** button in the Materials section |
| Engineering (blueprints, wishlist, ship and Odyssey upgrade planners, engineers) | Field Ops | **BLUEPRINTS** button in the Materials section |
| Material trader | Field Ops | **Find a trader** button in the Materials window |
| Ship Builds | Field Ops | **SHIPS** button |
| Colonization Sites | Colonization | **DASHBOARD** button |
| Space Mining Book | Mining | **BOOK** button on the Space Mining page |
| Surface Mining Book | Mining | **BOOK** button on the Surface Mining page |
| Mining History | Mining | **DASHBOARD** button, on both mining pages |
| Mining live window (Surface and Space) | Mining | **LIVE** button, on each mining page |
| Trade History (tabs: Overview, Commodities, Stations, Route, Trades, Stock & carrier, Lookups) | Trade | **History** button on the Session page |

Notes:

- You don't need to be mining to open the Surface Mining Book. It lists your saved hotspots either way.
- In Missions, the **Missions window** button is a table of every active mission with its progress, where to go and time left; you can pin
  missions there so they show on the overlay. Clicking a mission card opens the window on that mission.
- If you can't find the BGS or Codex Completionist sections, each can be switched off under
  **File → Settings → WFMT**. Both are on by default.

## Button names

The EDMC main window is small, so WFMT's buttons use short names. **Hover over any button for a moment and a tooltip
shows its full name.** Buttons inside pop-out windows and Settings keep their full names.

| Button | Full name | Where |
|---|---|---|
| **P.P.** | Powerplay | Mode buttons (top of the panel) |
| **BGS** | BGS | Mode buttons |
| **EXP** | Exploration | Mode buttons |
| **MIN** | Mining | Mode buttons |
| **TRD** | Trade | Mode buttons |
| **MSN** | Missions | Mode buttons |
| **OPS** | Field Ops | Mode buttons |
| **COL** | Colonization | Mode buttons |
| **SES** | Sessions | Powerplay |
| **RARES** | Rares (rare goods finder) | Powerplay |
| **RESCAN** | Rescan | Powerplay |
| **REPORT** | View BGS report | BGS |
| **A.H.** | Auto-Honk | Exploration |
| **D.A.** | Discovery Alerts | Exploration |
| **N.S.** | Nearest neutron star (primary star), from the Spansh search or the optional local star index | Exploration |
| **W.D.** | Nearest white dwarf (primary star) | Exploration |
| **RND** | Random (a real system nearby with no scans on Spansh or EDSM) | Exploration |
| **FIND** | Find nearest POI (GEC and Canonn) | Exploration |
| **UPDATE** | Refresh POI data (Canonn) | Exploration |
| **MY CODEX** | My Codex window: overview, found, not found and backfill (Codex Completionist) | Exploration |
| **ADD** | Save the line you typed as a note about the system you are in | Exploration (Notes section) |
| **NOTES** | Open the Notes window | Exploration (Notes section) |
| **EXPEDITION** | Open the Expedition window | Exploration (Expedition section) |
| **COPY** | Copy the next expedition stop's system name to the clipboard, to paste into the galaxy map | Exploration (Expedition section) |
| **FIND** | Open the Nearest place to land window | Exploration (Nearest place to land section) |
| **PLOT** | Open the Route Planner, which plots a neutron-star route for your ship with Spansh | Exploration (Route Planner section) |
| **DASHBOARD** | Open the Exploration Dashboard (not the Colonization one below: this is in Exploration) | Exploration (Dashboard section) |
| **MARK** | Save where you are as a mark for the Surface Compass | Exploration (Compass section) |
| **TARGET** | Aim the compass at the next target: the nearest hotspot, each mark on this body, then none | Exploration (Compass section) |
| **MARKS** | Open the Marks window | Exploration (Compass section) |
| **MATERIALS** | Open the Materials window | Field Ops (Materials section) |
| **BLUEPRINTS** | Open the Engineering window (blueprints, wishlist, ship and Odyssey upgrade planners, engineers) | Field Ops (Materials section) |
| **H.S.** | Find nearby hotspots | Mining |
| **+H.S.** | Save hotspot here | Mining (the live window's header) |
| **PRICE** | Find best price | Mining |
| **RES** | Check ring reserve level | Mining |
| **I/E** | Import/export hotspots | Mining (the live window's header) |
| **CTR** | Mark the center of a surface mining location | Mining (the live window's header) |
| **BRD** | Mark the border of a surface mining location | Mining (the live window's header) |
| **LIVE** | Open the live window for the Mining page you are on (a radar and the controls on Surface, the live numbers on Space) | Mining |
| **BOOK** | Space Mining Book (Space page) or Surface Mining Book (Surface page) | Mining |
| **DASHBOARD** | Open Mining History (the Mining mode's own button) | Mining |
| **Reset** | End this session and start a new tally (offers to save first) | Trade (Session page) |
| **Save session** | Keep this session in Trade History (the tally keeps running; press Reset to start a new one) | Trade (Session page) |
| **History** | Open the Trade History window | Trade (Session page) |
| **Rebuild** | Recount the session from the journals from a start time you give (UTC); for a session that began on another computer | Trade (Session page) |
| **Find routes** / **Cancel** | Ask Spansh for trade routes / stop waiting | Trade (Routes page) |
| **Hops** | Cycle the route length through 2, 3, 4 and 5 hops | Trade (Routes page) |
| **Round trip** | Find the best back-and-forth pair of stations, loaded both ways | Trade (Routes page) |
| **Copy next system** | Copy the first destination to the clipboard | Trade (Routes page) |
| **Sell** / **Buy** | Choose whether the search is for selling or buying | Trade (Market page) |
| **Near me** / **Galaxy** | Best place to sell or buy, near you / anywhere | Trade (Market page) |
| **Best picks** | Closest, best local, cheapest or highest anywhere, and a price within 10% of the best, for the commodity in the box | Trade (Market page) |
| **Price finder** | The Mining PRICE finder, for any commodity | Trade (Market page) |
| **REFRESH** | Ask Spansh for the best buy and sell price of each watched commodity near you (needs Trade lookups on) | Trade (Watch list section) |
| **WATCH** | Open the Watch list window | Trade (Watch list section) |
| **◀** / **▶** | Previous / next page | Mining, Trade, Missions |
| **Missions window** | Open the window listing every active mission, with progress and pinning | Missions (bottom of every page) |
| **Find sources** | Where to buy the cargo your Collect and Mining missions need, and where to pick up a Delivery mission's cargo (needs Trade lookups on) | Missions (bottom of every page) |
| **SHIPS** | Manage ship builds | Field Ops |
| **DASHBOARD** | Colonization sites (the Colonization mode's own button) | Colonization |
| **OVERLAY** | Force the colonization shopping list onto the overlay (lit while on), press again to let go | Colonization |

---

Next: pick a mode from the [guide index](README.md), or see [what goes on the internet](internet-and-privacy.md).
