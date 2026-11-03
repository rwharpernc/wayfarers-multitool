# Getting started

This page describes the requirements, installation and updating of WFMT, the layout of the WFMT panel, how commander data is stored and backed up, the catch-up behavior after EDMC was closed, every Settings tab with its defaults, and the pop-out windows and buttons. For display problems such as doubled or capitalized overlay text, see [Known issues](known-issues.md).

**On this page:**

- [What you need](#what-you-need)
- [Installing](#installing)
- [Updating](#updating)
- [A first five minutes](#a-first-five-minutes)
- [Finding your way around](#finding-your-way-around)
- [Commanders and your data](#commanders-and-your-data)
- [Backing up your data](#backing-up-your-data)
- [If EDMC wasn't running](#if-edmc-wasnt-running)
- [Settings](#settings) (every tab, with its defaults)
- [Typing a system name](#typing-a-system-name)
- [Opening the pop-out windows](#opening-the-pop-out-windows)
- [Button names](#button-names)

## What you need

**1. EDMC.** WFMT is a plugin for [EDMC](https://github.com/EDCD/EDMarketConnector) (Elite Dangerous Market Connector). EDMC reads the game's journal files during play and passes the events to plugins. It runs on Windows and Linux.

**2. An overlay (optional).** An overlay draws on top of the game screen. WFMT requires one only for its on-screen displays:

- Discovery Alerts, Notable Bodies, Landing Assist, Interdiction Warning, Flight Alerts and the Route.
- System targets, Body info, the Exobiology cards, the Expedition Log and the Surface Compass.
- The optional overlays for Inventory, Mining, Missions, Colonization and Screenshots.

All other features work without an overlay. Two overlays are supported:

- **WFMT's built-in overlay** (Windows only): requires no installation. Select it under **Settings → WFMT → Overlays → Overlay Connection → Which overlay draws**. It draws WFMT's displays only.
- **[EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay)** (Windows and Linux): a separate program. On Linux it is required for any WFMT on-screen display. It is also required for the overlays of other plugins; it can run alongside the built-in overlay.

Elite must run in **borderless** or **windowed** mode for the overlay to work. See [Setting up the on-screen overlay](../OVERLAY_SETUP.md).

Every WFMT overlay is off until it is ticked in Settings.

## Installing

1. **Download the plugin.** Open the [latest release](https://github.com/rwharpernc/wayfarers-multitool/releases/latest) and download **`Wayfarers-Multitool.zip`** from the **Assets** list. It contains only the plugin, in one folder named `Wayfarers-Multitool`.

   Do not use the **Code → Download ZIP** button. It downloads the whole source repository, which does not work as a plugin.

2. **Locate EDMC's plugins folder.** In EDMC open **File → Settings → Plugins** and click **Open** next to "Plugins folder". On Windows the folder is usually `%LOCALAPPDATA%\EDMarketConnector\plugins\`.

3. **Extract the ZIP into that folder.**
   - Windows: right-click `Wayfarers-Multitool.zip` → **Extract All…** and set the destination to the plugins folder itself.
   - Linux: `unzip Wayfarers-Multitool.zip -d <plugins folder>`

4. **Check the result.** The file `plugins/Wayfarers-Multitool/load.py` must exist. If `plugins/Wayfarers-Multitool/Wayfarers-Multitool/load.py` exists instead, the ZIP was extracted one level too deep; move the inner folder up.

5. **Restart EDMC.** A **Wayfarer's Multitool (WFMT)** panel appears in the main window. The panel is always shown and has no title that folds it.

If the panel does not appear, see [Troubleshooting](troubleshooting.md#the-wfmt-panel-doesnt-appear). On Linux, read [WFMT on Linux](linux.md) first; EDMC requires several settings there.

## Updating

Download the new `Wayfarers-Multitool.zip` and extract it over the existing `Wayfarers-Multitool` folder, replacing files when prompted. Do not delete the old folder first: the saved data (mining hotspots, trade sessions, ship builds and so on) is stored inside it.

WFMT can also update itself. Tick **Automatically download and install updates** under **File → Settings → WFMT → General → Updates**. The setting is off by default and considers only official published releases (drafts and pre-releases are ignored). The **Release notes** link on that tab opens the latest release's page in the browser.

**In-app updater**

1. **When it checks.** Once in the background at each EDMC start, and only when the setting is ticked. It queries GitHub for the latest release ([what goes on the internet](internet-and-privacy.md)) and compares version numbers. If the installed version is the same or newer, nothing further happens.
2. **What it downloads.** The `.zip` attached to the newer release, into an `updates` folder inside the plugin folder.
3. **What it protects.** Before files are replaced, it makes a data backup if **Back up automatically** is ticked ([Backing up your data](#backing-up-your-data)), and it makes a zip of the program files about to be replaced in the plugin folder's `backups` folder (the newest three are kept). It writes only the files the release contains and skips the names of saved data files, so data, the `star_index` folder and added fonts remain unchanged.
4. **When it takes effect.** The new files are staged at once and take effect at the next EDMC start. Nothing is replaced in a running program.
5. **On failure.** A failed check or download is written to EDMC's log and retried at the next start. The panel is unchanged. Manual extraction of the ZIP always works.

The first line under the mode buttons always shows the running version (**Plugin: v1.5.0**).

- While an update is downloading it reads, for example, **Plugin: v1.5.0 (downloading v1.4.3...)**.
- When the update is downloaded, the line is bold black on **orange** and reads **the new version's number, then download - Restart EDMC**.
- After the restart the line shows the new version followed by **(updated)**, in green for 15 seconds.
- Clicking the line opens the latest release's page in the browser.

Building from source is described in [DEVELOPMENT.md](../DEVELOPMENT.md).

## A first five minutes

No configuration is required to begin. The following steps introduce the panel:

1. The row of buttons at the top of the WFMT panel selects one of the eight **modes**. Clicking a button changes the panel below it. Hovering over a button shows its full name.
2. Open **File → Settings → WFMT**. Each mode has its own tab. Press **OK** at the bottom of EDMC's Settings window to keep changes ([Settings](#settings) lists every tab).
3. For on-screen alerts, set up an overlay (see above), then press a **Test** button in Settings to verify it.
4. Linux only: set EDMC's *Journal directory*. See [WFMT on Linux](linux.md).
5. Optionally enable **Back up automatically** under **Settings → WFMT → General → Backup** ([Backing up your data](#backing-up-your-data)).
6. Play. Most features fill in during play.
7. Each mode guide ends with a section "What the game does and doesn't tell us". It lists what the game does not record (for example, a fleet carrier's cargo is exact only after Carrier Management is opened) and the workarounds.
8. For incorrect behavior, see [Known issues](known-issues.md) and [Troubleshooting](troubleshooting.md), then use **Settings → WFMT → General → Help → Report an issue** ([Reporting a problem](reporting-problems.md)).

**Limits of the data.** WFMT uses only what the game writes to its journal files, and not everything is logged.

- Some gaps are filled from Frontier's servers (through a signed-in EDMC) and from data reported by players and communities (Spansh, EDSM, Canonn, edastro, Raven Colonial).
- The remainder is handled with labeled estimates and manual steps.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## Finding your way around

### The mode buttons

WFMT has one panel with eight modes, selected with the button row at the top of the panel: **Powerplay**, **BGS**, **Explore**, **Mine**, **Trade**, **Mission**, **Operations** and **Colony** (Colonization).

Every mode keeps running in the background while another mode is displayed. For example, mining statistics continue to count while the Trade mode is displayed.

### The lines under the mode buttons

Under the mode buttons, above the page, WFMT shows the following lines in every mode:

- **Plugin**: the running version, for example `Plugin: v1.5.0` (see "Updating" for the text during an update). Clicking it opens the latest release's page.
- **Game mode**: `You are in Open mode.`, `You are in Solo mode.` or `You are in Private Group mode (the group's name).` Before the game has logged in it reads `Game mode: waiting for login…`.
- **Credits this session**: credits earned or lost since login, for example `Credits this session: +1,234,567 cr earned (+411,522 cr/hr)`, `Credits this session: -5,000 cr lost` or `Credits this session: no change yet`. It is the current balance minus the balance at login (`waiting for your balance…` until EDMC has supplied the balance).
  - The hourly rate appears once the session is about three minutes old.
  - Clicking the line opens the **Credits Ledger** (it has a **Help** button):
    - **Income** tab: credits earned per activity for today, the last 7 days, the last 30 days and everything counted.
    - **By day** tab: one row per day, a column per activity and the day's total.
    - **Lifetime** tab: the game's career totals, which the game writes at login only.
    - Activities are kept separate: **Trade** (profit on market sales: the sale minus the cost of the sold tons, which can be negative), **Exploration data** (sold), **Exobiology data** (sold, with the first-discovery bonus), **Mission rewards** (the credit reward only) and **Bounties and bonds** (vouchers cashed in). Days are UTC, as the journal writes them.
    - Limits: the journal does not state which sold commodity was mined, so Mining has no per-day income (its lifetime profits are on the **Lifetime** tab). Credits spent are not counted. The first time a commander is seen, the ledger is rebuilt once from every journal; afterwards it counts during play without double counting.
- **Merits this session**: Powerplay merits earned since login, for example `Merits this session: +1,234 (+567 merits/hr)`. It is shown in every mode except Powerplay, whose page has its own session lines.
  - It appears after the first merit of the session.
  - The rate is the merits divided by the time since login, so it falls while no merits are earned.
  - The Powerplay mode's **CP** figures are Control Points, a separate quantity.
- **Overlays**: `Overlays shown (click to hide)`, or `Overlays are hidden (click to show)` while hidden. Clicking toggles every WFMT overlay at once.
  - See [Overlay setup](../OVERLAY_SETUP.md#hiding-the-overlays-for-a-while).
  - Windows also has a keyboard shortcut, and both systems have a chat command: see [Shortcuts](shortcuts.md).
- **Catch-up notice** (gray, shown only while applicable): `Reading your journals to catch up (the names of the tasks). This happens once and can take a minute.` It appears when a journal read (Powerplay, the BGS replay, the Codex rebuild and similar) has run for more than about a second and a half. Nothing is stored; the notice disappears when the reads finish.

### Pages

Mining, Trade and Missions have more than one page, and each page is a window. The panel shows a short summary and one button per page; each button opens that page's window. Trade has **Session**, **Routes** and **Market**; Mining has **Space Mining** and **Surface Mining**; Missions has **Mission types**.

### Collapsing the panel

The panel itself does not fold. Sections inside the modes (Exploration, Notes, Engineering and so on) start folded; clicking a section's title (▸ / ▾) opens it. Sections fold again at each EDMC start.

### Window height

The EDMC window is shared by all plugins. WFMT resizes the window's height to fit when a section is opened, a mode is switched, or a section is expanded or collapsed. Width and position are not changed.

To set the height manually, untick *Resize the EDMC window's height to fit WFMT automatically* (on by default) under **File → Settings → WFMT → General → Window**. The same page hides the buttons of unused modes under *Mode buttons on the main panel*. A hidden mode keeps running in the background; Colonization is listed there as **Colony**.

WFMT keeps the panel width equal to the width of the mode-button row, so switching modes does not change EDMC's window width. Long names wrap onto the next line.

## Commanders and your data

All data WFMT saves about play belongs to one commander. Nothing is shared between commanders, and switching commander in EDMC switches the data every feature shows:

- Trade sessions and route start, Powerplay and BGS ledgers, Missions.
- Mining hotspots and the ground driven by the Rhino.
- The Boxel Survey position and finds, the Codex tally.
- Colonization sites, Ship Builds, the Combat Record, Organic Scanning and Powerplay history.
- The Credits Ledger and the credits line, expeditions and the Expedition Log, notes, the Surface Compass marks, the engineering materials, blueprint wishlist and engineers, stored modules, pinned missions, the Raven Colonial key and the Discord destinations.
- Each commander's overlay choices (which cards are on, where they sit, how they look).

Names are matched ignoring case, so `EXAMPLE` in the journal and `Example` in EDMC are the same commander.

Data that does not belong to a commander is shared: Settings (the overlay choices are the exception; they are per commander), the downloaded Codex catalog, the optional Local star index, the record of which journal files Trade has read, and the prediction-review record, which is one file shared by every commander on the installation and names none of them.

### Backing up your data

WFMT stores the data it records about play as files in its plugin folder: expeditions and the Expedition Log, system surveys and visit history, Boxel Survey finds, Exobiology state and finds, the Codex tally, missions, trade and ledgers, mining hotspots, notes and others.

Updates do not modify these files. Nothing else copies them, so deleting or reinstalling the plugin folder removes them.

**To make a backup:**

1. Open **File → Settings → WFMT → General → Backup** and press **Back up my data**.
2. Choose a folder in the window that opens (it starts in the folder used last time). WFMT saves all data as one dated zip there (`WFMT-data-20261021-093015.zip`). The Backup tab reports the result: `Saved N files (size) to <path>` or `Backup failed: ...`. A failure is typically caused by a folder inside the plugin folder or a folder EDMC cannot write to. Cancelling the folder window does nothing.

Properties of the backup:

- It is a plain copy of the files. Nothing is changed or sent anywhere.
- The folder must be outside the plugin folder, for example Documents or a cloud-synced folder; WFMT refuses a folder inside it. With a Flatpak EDMC on Linux the folder must be one the Flatpak may write to ([Linux](linux.md)).
- The zip also contains `backup-info.json` (WFMT version, date, platform and the files, with no commander name).
- If **Archive completed mining runs** is ticked (Settings → WFMT → Mining), the `mining_sessions` folder of per-run files is included. If WFMT has nothing saved, it reports that instead of creating an empty zip.
- **Every commander is included.** Most files hold a separate section per commander on the installation, so the zip does too.
- **Excluded by design:**
  - The Raven Colonial keys (`rcc_keys.json`) and the Discord webhook links (`discord_webhooks.json`).
  - The downloaded Codex catalog, which WFMT fetches again.
  - The optional local star index (`star_index` folder, about 110 MB, built from a public download and rebuilt from Settings).
  - Settings and overlay positions held in EDMC's own configuration, which are not files in the plugin folder. `overlay_settings.json` (each commander's overlay choices) is included.
- **Restoring or moving data:** use **Restore my data...** on the same tab.
  1. WFMT asks for a backup zip (opening in the last backup folder), verifies that it is a WFMT data backup (it must contain `backup-info.json`; a zip containing any other file is refused, and a zip that is not recognized is never partly applied), shows its contents (WFMT version, date, number of files, size) and asks for confirmation.
  2. After confirmation, the line under the buttons reads *Restore ready. Restart EDMC to apply it.* and the tab shows *A restore is waiting for the next EDMC start*. The restore is applied at the next EDMC start because WFMT cannot replace files in use. **Cancel the waiting restore** (shown only while a restore is waiting) cancels it.
  3. The restore replaces the backup's files for every commander in them, leaves any file the backup does not contain, and keeps the replaced files in `backups/pre-restore-<date>.zip` in the plugin folder (the newest five). To undo a restore, put those files back.
  4. To move data to another computer: install WFMT there, restore the zip, and start EDMC.
  5. The files are plain JSON.
- **Automatic backups:** tick **Back up automatically**, press **Choose folder...** and set **Every [n] days** (1 to 90; 7 by default).
  - WFMT makes a backup at EDMC start if the newest automatic backup in that folder is at least that many days old (or none exists), and again before an update is installed.
  - Names are `WFMT-data-auto-<date>-<time>.zip`; the newest ten are kept. Backups made with the button are never deleted.
  - The setting is off by default and requires a folder outside the plugin folder. These three choices (and the last manual backup folder) are saved per computer.

### If EDMC wasn't running

If EDMC starts before the game, nothing identifies the commander until login. A few seconds after start, WFMT reads the last commander from the newest journal, and every feature starts with that commander's saved data. A login as another commander then switches all data. The Game Mode and Credits lines wait for a running game.

EDMC passes events to WFMT only while it runs. For play with EDMC closed, WFMT reads the game's journal files at EDMC start (and, for Trade, once per minute afterwards). Each feature does this separately and adds only what is new, so nothing is counted twice:

| Feature | What it catches up on | How far back |
|---|---|---|
| **Trade** | Session tally, stock, carrier figures, route start | New or grown journal files, every minute |
| **Powerplay** | Merits and Control Points | The gap since EDMC last saw the journal (up to the scan depth on the Sessions window's Settings tab) |
| **BGS** | Effect on factions this tick | From the start of the tick |
| **Missions** | Active missions, kill progress, cargo progress, Community Goals | The last 2 weeks |
| **Colonization** | Deliveries (also counted into the history) and sites docked at, and transfers to the fleet carrier (its FC column) | 14 days, or back to the oldest site (30 days at most); the delivery history is also rebuilt once from every journal |
| **Codex Completionist** | Codex finds, for the active commander | Everything since the last find it counted |
| **System targets, Body info and the Exploration Dashboard** | The survey of the current system: bodies scanned, mapped and analyzed there, including a system scanned while EDMC was closed | The journals holding visits to that system, at login or EDMC start |
| **Ship** (Route Planner, fuel percentage, jump range, landing-pad size) | The ship being flown, from the last `Loadout` in the newest journal | When EDMC starts with the game already running |
| **Organic Scanning** | The progress of each species logged, sampled or analyzed (the stage, not the position of a sample), and the conditions, genera and first-footfall flag of bodies scanned with EDMC closed | The last 14 days; a sample is skipped if its body is not named in them |
| **Boxel Survey** | Systems arrived at, and the notable bodies and biological signals scanned (systems new to the survey log; a system already present keeps its scanned count) | The last 14 days |
| **Mining** | The run in progress (the Space Mining and Surface Mining windows); every earlier run (the Mining History window); the rings (the Space Mining Book) and the bodies with mining locations or Rhino mining (the Surface Mining Book's *From your journals* group) | The current journal file for the run in progress; every journal for the history and the two books, read once in the background (a notice is shown) and afterwards only new ones |
| **Carrier Route** | The carrier's location, the tritium in its tank and the space it uses | The last 30 days, when the Carrier Route window first opens |
| **Exploration Value** | Region, system scan progress, last data sales | The current journal file |
| **Inventory** | Backpack and ship locker | Taken from EDMC's own rebuilt state |
| **Credits line** | The session, if it is the same journal file | The saved session |
| **Credits Ledger** | Sales, data, mission rewards and vouchers earned while EDMC was closed; the first time a commander is seen it is rebuilt once from every journal | Every journal once, afterwards only what is newer than the last event counted |

Landing Assist, Interdiction Warning, Discovery Alerts, Notable Bodies, Auto-Honk, Screenshots and the position of an Organic Scanning sample are relevant only at the moment they occur and have no catch-up. See each mode's guide for the limits.

Restarting EDMC is safe at any time:

- Every catch-up only adds what is new or raises a figure, never lowers one, so a restart during a session cannot lose or double-count data.
- A catch-up runs in the background a few seconds after EDMC starts; a card or window can take a moment to fill in.
- Causes for a figure that remains behind the game after a login are listed in the next table.

**What a catch-up cannot recover:**

| After play with EDMC closed | Cause | Action |
|---|---|---|
| A species shows less progress than the game (`2/3` for one analyzed), or a body has no predicted species | Organic Scanning is caught up from the last **14 days** of journals, and a sample is skipped if no event in them names its body (a body scanned and sampled more than 14 days apart) | Restart EDMC once. If still behind, sample or scan the species again; the next scan sets the correct stage |
| The marker for a plant identified with the Composition Scanner is missing | The marker comes from the scan event while EDMC runs and is not rebuilt from old journals (rebuilding it could restore plants already sampled) | Scan the plant with the Composition Scanner again |
| The distance to the last sample on a body is wrong or blank | The journal does not record where a sample was taken; WFMT reads the position from `Status.json` at the time of sampling | Correct from the next sample |
| An expedition's totals are low | The Expedition Log reads the journal live | Press **Rescan** on the expedition |
| Codex entries found before WFMT first ran (a new installation, or a commander new to it) | Codex Completionist catches up forward from the last find it counted, so it starts from nothing on a new installation | **My Codex → Backfill Journals** once |
| A Powerplay session or a BGS period is incorrect | Their catch-ups are limited by the scan depth and the tick | **Rescan** (Powerplay); BGS rebuilds a closed period by itself |
| A mining run that began before a restart | The Mining windows read the current journal file only (Mining History and the two books read every journal) | The run continues from the journal file in use; an earlier file's run is not rejoined |

These are limits of what WFMT can read back from the journals; no game data is lost.

A catch-up writes a line to EDMC's log (`EDMarketConnector-debug.log`, in EDMC's log folder; on Windows `%LOCALAPPDATA%\EDMarketConnector\logs`), such as `Organic Scanning caught up from the journals: 3 bodies`.

## Settings

Most WFMT settings are in EDMC's Settings window: **File → Settings → WFMT**. The display and tuning settings of modes that have windows (Trade, Mining, Missions, Powerplay, BGS, Inventory, Colonization's reporting choices, and three Exploration windows) are on a Settings card, strip or tab inside those windows. A tab here that formerly held them states where they are now. This location holds the switches that let WFMT contact another service, the keys and per-commander choices, the overlay tabs, and everything in General. The mode guides describe each setting in use (their "Settings" sections), and [Setting up the overlay](../OVERLAY_SETUP.md) covers every Overlays tab.

**Behavior of Settings**

- **OK** (at the foot of EDMC's Settings window) keeps changes. Some controls act immediately and need no OK: the **Test** buttons, **Check connection**, the Local star index buttons and its tick, **Add font file...**, **Rescan** and **Test Honk Now** in Auto-Honk, and the restore buttons.
- **Tabs are in alphabetical order**, at the top level and inside every row of inner tabs (the Overlays row starts with its three shared tabs). Each row opens on its first tab. A long tab scrolls, and the mouse wheel works over it.
- **Storage.** Settings are saved in EDMC's own settings for this computer and do not carry to another computer. The exceptions are the overlay choices (which cards are on, where they sit, how they look), which are kept per commander ([Overlay setup](../OVERLAY_SETUP.md#moving-things-around)), and the Raven Colonial key and Discord destinations, which are kept per commander.
- **Restarts.** Almost every change applies on OK. An EDMCModernOverlay font, an update and a data restore wait for the next EDMC start, as their tabs state.
- **Defaults.** Every on-screen display, every write to another site and every online lookup that has a switch starts off, with one exception: BGS tick detection starts on. The Rare Goods Finder and the Codex "Not found" tab have no switch and query their service when opened ([what goes on the internet](internet-and-privacy.md)). [Troubleshooting](troubleshooting.md#nothing-happens-settings-that-start-off) lists the switches that start off.

**The tabs**

| Tab | Contents | Guide |
|---|---|---|
| **BGS** | *Detect BGS ticks (polls tick.infomancer.uk every 60s)* (on), with a note that *Show BGS faction states and activity* (on) and *Keep previous ticks for [n] days* (1 to 90, 7 by default) are on the Settings card of the BGS Report window | [BGS settings](bgs.md#settings) |
| **Colonization** | The Raven Colonial group: *Allow WFMT to write to Raven Colonial (master switch)* (off), *Report my construction progress and deliveries to Raven Colonial* (off), *Also report cargo I move to and from my fleet carrier* (off), the *Raven Colonial key* (hidden as typed) with **Test key**, and a link to the page where the key is made. The two reporting ticks are unavailable until the master switch is on | [Colonization](colonization.md#sharing-your-progress-with-raven-colonial) |
| **Discord** | *Allow Post to Discord* (off); **Destinations** (each a *Name*, a *Webhook link* hidden as typed, and an optional *Thread ID*), saved for the commander being played, with **Test**, **Remove**, **Add destination** and **Copy their destinations**; and **Customize posts…** | [Sharing reports to Discord](discord.md) |
| **Exploration** | A row of inner tabs, below | [Exploration](exploration.md) |
| **General** | A row of inner tabs, below | this page |
| **Mining** | The three opt-in lookups (*Enable Spansh nearby hotspot finder*, *Enable Spansh best price finder*, *Enable EDSM ring reserve lookup*, all off), *Enable body lookup* (off), *Archive completed mining runs* (off), the Surface Live simulation and the saved Known Surface Hotspots list, with a note stating where the remaining settings are: display switches, target commodities, coverage minimap, stop radius, rig gap and refill time are on the Settings card of the Space Mining and Surface Mining windows | [Mining settings](mining.md#settings) |
| **Missions** | No settings; a note pointing to the Display card of the Mission types window, which holds the six display switches (*Show kill progress*, *Show remaining-kills column*, *Show totals row*, *Show mission count*, *Show target settlement (ground missions)*, *Show commodities needed (trade and mining)*; all on by default) | [Missions settings](missions.md#settings) |
| **Operations** | A row of inner tabs, below | [Operations](operations.md) |
| **Overlays** | A row of inner tabs, below | [Overlay setup](../OVERLAY_SETUP.md) |
| **Powerplay** | No settings; a note pointing to the Settings tab of the Powerplay Sessions window, which holds *CP Ratios* (merits for 1 Control Point: Acquisition 4.0, Reinforcement 2.5, Undermining 4.2), the *Copy Progress* format and *Cycles to scan* (1 to 12, 4 by default) | [Powerplay settings](powerplay.md#settings) |
| **Trade** | *Enable Spansh trade lookups* (off); the carrier choice for each commander (Auto, Fleet, Squadron, Both or None), with a note stating where the remaining settings are: search numbers, ticks (large pad, fleet carriers, ground facilities, permits), ship size and the Round trip settings are in the Routes and Market windows, and *Count fines and bounties* is in the Session window | [Trade settings](trade.md#trade-settings) |

**General** (inner tabs: Backup, Help, Online lookups, Shortcuts, Updates, Window)

| Inner tab | Controls and defaults |
|---|---|
| **Backup** | **Back up my data**; **Restore my data...**; **Cancel the waiting restore** (shown only while a restore waits); *Back up automatically* (off) with **Choose folder...** and *Every [n] days* (7). See [Backing up your data](#backing-up-your-data) |
| **Help** | **Report an issue**, **Copy diagnostics**, **Report game data** and *Write a separate diagnostic log* (off) with **Open log folder** and **Copy log path**. See [Reporting a problem](reporting-problems.md) |
| **Online lookups** | A read-out (not controls) of every switch that lets WFMT query another service: On or Off, what it does, which service it queries and which tab changes it; the lookups that need no switch and run only on a button press; and the **Local star index** group below |
| **Shortcuts** | One row per action (Mark the center, Mark the border, Rig placed, Radar range, Open the Live window, Hide or show overlays): the last key of Ctrl+Alt+Shift plus a key (C, B, R, Z, L and O initially; any letter, digit, F1 to F12, or Off), with a warning if two actions share a key or Elite already uses the combination; *Chat commands* (labelled `Chat commands (type  !wf <word>  in Elite's chat)`) (off); *Play a sound when a shortcut worked* (on). The key choices work on Windows only. See [Shortcuts](shortcuts.md) |
| **Updates** | *Automatically download and install updates* (off); the **Release notes** link. See [Updating](#updating) |
| **Window** | *Resize the EDMC window's height to fit WFMT automatically* (on); *Suggest system names from Spansh while typing* (off); *Mode buttons on the main panel*: a tick for each of Powerplay, BGS, Explore, Mining, Trade, Missions, Operations and Colony (all ticked; unticking every one shows them all); *Text size in WFMT's windows* (points larger than normal, -2 to 6; 0); *Color theme of WFMT's windows* (Navy, Cyan, Amber or Green; Navy); *Always open WFMT's windows on EDMC's monitor* (off) |

**The Local star index group** (bottom of Online lookups) is optional; WFMT is fully functional without it.

- It allows **Neutron Star** (nearest neutron star) to answer from a file on this computer instead of querying Spansh each time. The line above its buttons shows what is installed (for example the number of neutron stars, its size and the date it was built from), or `Not installed. The Neutron Star button asks Spansh.`, and shows the progress of a running job.
- **Download and build** (available when nothing usable is installed): fetches one public file from Spansh's download server (about 173 MB) and builds the index from it, about 110 MB on disk. About 300 MB of free space is required during the build; the download is deleted afterwards. A cancelled or interrupted download resumes from where it stopped.
- **Update** (available when an index is installed): fetches only what changed, Spansh's 1-day (about 3 MB) or 1-week (about 19 MB) file of changed systems, when the index is recent enough, and the whole file again only when it is not (or after 20 updates). Pressing it again on the same day downloads nothing.
- **Cancel** (while a job runs) stops it. **Delete** (when an index file exists, usable or not) removes it.
- *Use the local index for Neutron Star when it is installed* (on) determines whether the button uses the index. **White Dwarf** always queries Spansh. The index lists systems whose main star is a neutron star; a neutron star that is a secondary star is not included. A damaged index, or one made by another version of WFMT, is ignored and the button queries Spansh (the line instructs to delete it or press **Download and build**).
- The index is the same for every commander and is not part of the data backup. It is stored in the `star_index` folder in the plugin folder, which updates do not modify.
- Nothing is downloaded unless a button is pressed.

**Exploration** (inner tabs: Auto-Honk, Boxel Survey, Expedition, Exploration Value, Nearest place to land, Organic Scanning, POI Reference, Region Sweep, Waypoint Route)

| Inner tab | Controls and defaults |
|---|---|
| **Auto-Honk** | *Enable Auto-Honk* (off); *Fire button* Primary or Secondary (Secondary); *Hold (sec)* (10); *Focus game window first* (on); *Skip systems already visited* (on); on Linux, *Elite Wine/Proton prefix* (blank means auto-detect Steam); **Rescan** and **Test Honk Now**, which work while Auto-Honk is off. See [Auto-Honk](exploration.md#auto-honk) |
| **Boxel Survey** | *Auto-copy next target to clipboard on jump* (on); *Skip systems already visited this session* (on); *Skip systems already visited by anyone (EDSM)* (off); *Skip systems already fully scanned in EDSM* (off); *Confirm off-sequence arrivals against EDSM* (off); **Export Survey Log**; and for the Random button, **Clear Visited Systems Log** and *Systems to request from Spansh* (10 to 100, 25 by default) |
| **Expedition** | No settings; a note pointing to the Settings strip across the top of the Expedition window (*Copy the next stop on every arrival*, off, the same as **Copy on arrival** on the panel; *Start the Expedition Log with an expedition*, on) |
| **Exploration Value** | *Show estimated scan value, system age, and current region* (on); *Show ELW rarity comparison when you scan an Earthlike World (Spansh)* (off); *Show EDSM upload status when you select a system on the galaxy map (EDSM)* (off) |
| **Nearest place to land** | *Allow this lookup: pressing Find sends Spansh my position, the pad size and my choices, nothing else* (off; the same switch as the tick in the window) |
| **Organic Scanning** | *Show predicted species and scan progress* (on); *Keep a record of what I find, to check the prediction* (on) and **Clear the record...** (both are also at the top of the Prediction review window, as the same settings). See [Exobiology](exobiology.md) |
| **POI Reference** | Three groups on one page: edastro GEC (information only), Canonn (*Include Thargoid sites* on, *Include Guardian sites* on, *Skip sites already logged in Codex Completionist* on) and Codex Completionist (a *View Canonn Codex* link; *Track codex entries*, on, is on the Settings strip of the My Codex window) |
| **Region Sweep** | *Auto-copy next target to clipboard on jump* (on); *Skip systems already visited this session* (on); *Skip systems already visited by anyone (EDSM)* (off); *Require a full FSS scan (not just arrival) to mark a system complete* (off); *Auto-discover more nearby cubes (EDSM) when the queue is running low* (off) |
| **Waypoint Route** | *Auto-copy next waypoint to clipboard on jump* (on) |

**Operations** (inner tabs: Inventory, Screenshots, Ship Builds)

| Inner tab | Controls and defaults |
|---|---|
| **Inventory** | No settings; a note pointing to the Settings tab of the Inventory window, which holds the *Pillage message* format (placeholders `{item}` and `{total}`), *Play a sound on pickup* (off; unavailable where no sound can play), *Announce pickups for* each category and the per-loadout backpack capacity overrides. See [Inventory](operations.md#inventory) |
| **Screenshots** | *Delete original file after conversion* (off); *Include WFMT's built-in overlay in the converted screenshot* (off; Windows, built-in overlay); *Group converted files into a per-system subfolder* (off); *Show the auto-capture timer icon on the main window* (on); *Filename Mask* (a preset list); *Auto-capture poll interval (seconds)*; *Use high-resolution capture on the auto-timer (Solo play only)* (off); *Automatically capture a screenshot when scanning a Thargoid signal* (on). See [Screenshots](operations.md#screenshots) |
| **Ship Builds** | Explanation only: builds are kept by link in the Ship Builds window (**Ships**) |

**Overlays** (inner tabs: Overlay Connection, Appearance and Overlay Placement first, then in order Body info, Colonization, Discovery, Exobiology, Expedition Log, Flight Alerts, Hide overlays, Interdiction Warning, Inventory, Landing, Mining, Missions, Notable Bodies, Powerplay, Route, Screenshots, Surface Compass, System targets). Every option, with its default, is in [Setting up the overlay](../OVERLAY_SETUP.md#every-overlays-tab-in-detail).

## Typing a system name

Every box that takes a system name suggests systems from the second letter. This covers an expedition stop, the Expedition planner's start and end, the trader finder's *Search from*, Colonization's *Around*, a mining hotspot or ring reserve, a note, a waypoint and a Boxel Survey seed.

- **Suggestions:** systems visited in the current session first, then systems WFMT already holds (expedition stops, notes).
- **Keys:** **Down** and **Up** move through the list, **Enter** or a click selects the highlighted entry, and **Escape** closes the list. **Enter** with nothing highlighted performs the box's normal action (adds the stop, runs the search).
- **Other names:** the same keys work in other boxes that take a name WFMT can list, and all suggestions are local (nothing is fetched). The **Body** and **Ring** boxes (Add hotspot, Expedition stops, Surface marks, Notes, the ring reserve lookup, Add a ring) suggest the bodies and rings WFMT knows in the system typed beside them. The **Ship** box of a ship build suggests ships. A single commodity box (such as **Carry only this commodity** in the Routes window) suggests commodities. A box that takes several commodities separated by commas (the **Also check** boxes of the mining price lookups, the **Hotspots** box of Add a ring) suggests the entry being typed.
- **Systems not yet visited:** tick **Suggest system names from Spansh while typing** under Settings → WFMT → General → Window. It is off by default; when ticked, the letters typed so far (from the third) are sent to Spansh ([what goes on the internet](internet-and-privacy.md)).

### What you can and can't switch off

A mode that is not used can be hidden under **Settings → WFMT → General → Window → Mode buttons on the main panel**. A hidden mode keeps running in the background, and at least one mode stays shown. Switches exist for individual features:

| | |
|---|---|
| **Have a switch** | Auto-Honk, Discovery Alerts, Notable Bodies, Organic Scanning, Codex Completionist, Exploration Value (and its two online extras), BGS (and its tick detection), Landing Assist, Interdiction Warning, Flight Alerts, the Surface Compass, the Trade and Mining online lookups, and every overlay |
| **Have no switch** | The core of Powerplay, Missions, Mining and Trade tracking, screenshot conversion, Inventory tracking, Materials and Engineering, the Expedition planner, Colonization, Ship Builds, the Combat Record, Boxel Survey, and the GEC and Canonn POI finders. Some of these (Boxel Survey, the POI finders) only fold and act when a button is pressed |

Most online lookups are off until enabled, or run only on a button press. The exceptions are listed in [what goes on the internet](internet-and-privacy.md).

### Pop-out windows

Sessions, rare goods, inventory, the BGS report, the Surface Mining Book and others open as their own windows. They use a navy look with colored headings. The text size and color theme are configurable (the **A-** and **A+** buttons and the theme name at the right end of the bottom line, or Settings → WFMT → General → Window; one choice for every window, remembered; Navy, Cyan, Amber or Green; the small boxes at the top of a dashboard keep their size). Windows remember their size and position and close with **Esc** or the window's close button. The main panel follows the EDMC theme.

Every pop-out window has the same layout:

- **Header:** the window's title with a one-line subtitle, and its buttons on the right. A button with a small arrow (such as **Raven Colonial** or **Manage Sites** in the Colonization Sites window) opens a menu of related actions.
- **Help:** most windows have a **Help** button at the right of the header, except the Exploration Dashboard, Inventory, Missions, Ship Builds, Colonization Sites, Where to Buy, Nearest place to land, Prediction review, Source commodities and Surface Mining Book windows. It opens a small window of short entries that explain the columns, colors and buttons. Pressing **Help** again brings the same window forward.
- **Body:** tables, sortable by clicking a heading where the window states so. Windows that are tabs of another window (the Expedition window's Plan, Route and Log tabs) share its header.
- **Status line:** the line at the foot of the window shows the result of the last action (a copy, a search, a refusal) and wraps instead of being cut off.
- **Size and position:** remembered; a window opens at least as large as its minimum so nothing is clipped. A window that has never been opened, or whose remembered position is no longer on a connected monitor, opens over the EDMC window on EDMC's monitor. Tick *Always open WFMT's windows on EDMC's monitor* (Settings → WFMT → General → Window) to open every window there.

## Opening the pop-out windows

Select the mode first, then use the button listed.

| Window | Mode | How to open it |
|---|---|---|
| Credits Ledger (tabs: Income, By day, Lifetime) | Any mode | Click the **Credits this session** line under the mode buttons |
| Powerplay Sessions (tabs: Current session, Systems, Cycles, Daily, Megaships, History) | Powerplay | **Report** button (bottom row of the panel) |
| Rare Goods Finder | Powerplay | **Rares** button, next to Report |
| BGS Report | BGS | **Report** button |
| Codex Completionist | Exploration | **My Codex** button in the Codex Completionist section |
| Notes | Exploration | **Notes** button in the Notes section |
| Expedition (tabs: Plan, Route, Log; the Log tab is the Expedition Log archive) | Exploration | **Expedition** button in the Expedition section; **Plot** and the Dashboard's **Route Planner** open it on the Route tab |
| Prediction review (Organic Scanning) | Exploration | **Review** button in the Organic Scanning section |
| Nearest place to land | Exploration | **Find** button in the Nearest place to land section |
| Route Planner | Exploration | **Plot** button in its section of the panel (or **Route Planner** in the Dashboard's header) |
| Carrier Route | Exploration | **Carrier route** button in the Route Planner window |
| Exploration Dashboard (tabs: Overview, Orbit, Surface, Exploration) | Exploration | **Dashboard** button in the Dashboard section |
| Marks (for the Surface Compass) | Exploration | **Marks** button in the Compass section |
| Watch list | Trade | **Watch** button in the Watch list section |
| Missions window (tabs: Active, By place) | Missions | **Missions window** button at the bottom of the panel |
| Mission description | Missions | Click a mission's card in the Mission types window |
| Source commodities | Missions | **Find sources** button at the bottom of the panel (or **Sources** in the Missions window) |
| Inventory | Operations | Click one of the **inventory bars** (there is no button) |
| Materials | Operations | **Materials** button in the Engineering section |
| Engineering (blueprints, wishlist, ship and Odyssey upgrade planners) | Operations | **Blueprints** button in the Engineering section |
| Engineers (standing with each engineer and the path to unlock them) | Operations | **Engineers** button in the Engineering section |
| Material trader | Operations | **Find a trader** button in the Materials window |
| Ship Builds | Operations | **Ships** button |
| Combat Record (tabs: This session, All time, Sessions) | Operations | **Combat** button |
| Colonization Sites | Colonization | **Dashboard** button |
| Colonization History (tabs: Overview, By day, Commodities, Sites) | Colonization | **History** button |
| My Projects (projects on Raven Colonial) | Colonization | **Projects** button, or **Raven Colonial → My Projects** in the Colonization Sites window |
| Planned Builds, Raven Progress and Create Project on Raven | Colonization | **Raven Colonial** menu in the Colonization Sites window |
| Space Mining Book | Mining | **Book** button in the Space Mining window |
| Surface Mining Book | Mining | **Book** button in the Surface Mining window |
| Mining History | Mining | **Dashboard** button, in both mining windows |
| Mining live window (Surface and Space) | Mining | **Space Mining** and **Surface Mining** buttons |
| Trade History (tabs: Overview, Commodities, Stations, Route, Trades, Stock & carrier, Lookups) | Trade | **History** button on the Trade panel |

Notes:

- The Surface Mining Book can be opened without mining; it lists the saved hotspots in either case.
- In Missions, the **Missions window** button opens a table of every active mission with its progress, destination and time left. Missions can be pinned there to show on the overlay. Clicking a mission card opens the window on that mission.
- The BGS, Codex Completionist and Organic Scanning sections can each be switched off under **File → Settings → WFMT** (BGS, Exploration → POI Reference, Exploration → Organic Scanning). All three are on by default.
- Pressing a window's button while the window is open brings it forward and refreshes it; no second copy opens.

## Button names

The mode buttons and the buttons on the panels carry their full names. Hovering over a button shows a tooltip with its name and function. The same applies to buttons in WFMT's windows, where a button's name is written like Mark center or Add hotspot. The table lists the buttons, their function and location.

| Button | Full name | Where |
|---|---|---|
| **Powerplay** | Powerplay | Mode buttons (top of the panel) |
| **BGS** | BGS | Mode buttons |
| **Explore** | Exploration | Mode buttons |
| **Mine** | Mining | Mode buttons |
| **Trade** | Trade | Mode buttons |
| **Mission** | Missions | Mode buttons |
| **Operations** | Operations | Mode buttons |
| **Colony** | Colonization | Mode buttons |
| **Report** | Powerplay Sessions window | Powerplay |
| **Rares** | Rares (rare goods finder) | Powerplay |
| **Rescan** | Rescan | Powerplay |
| **Report** | View BGS report | BGS |
| **Auto-Honk** | Auto-Honk | Exploration |
| **Discovery Alerts** | Discovery Alerts | Exploration |
| **Neutron Star** | Nearest neutron star (primary star), from the Spansh search or the optional local star index | Exploration |
| **White Dwarf** | Nearest white dwarf (primary star) | Exploration |
| **Random** | Random (a real system nearby with no scans on Spansh or EDSM) | Exploration (Boxel Survey section) |
| **Sequence** / **Region Sweep** / **Waypoints** | Select the Boxel Survey sub-mode the section shows | Exploration (Boxel Survey section) |
| **< Prev** / **Next >** / **Copy** | Step to the previous or next target in the sub-mode, or copy the current target's system name to the clipboard | Exploration (Boxel Survey section) |
| **Use Current** / **Set** | Fill the box with the current system / start the survey from the name in the box | Exploration (Boxel Survey section, Sequence) |
| **Find Nearby (EDSM)** | Ask EDSM for the nearest real procedurally named system outside the current cube and put it in the Seed box (**Set** moves the survey there) | Exploration (Boxel Survey section, Sequence) |
| **Find POI** | Find nearest POI (GEC and Canonn) | Exploration |
| **Update POI** | Refresh POI data (Canonn) | Exploration |
| **My Codex** | My Codex window: overview, found and not found, with a Backfill Journals button (Codex Completionist) | Exploration |
| **Add Note** | Save the typed line as a note about the current system | Exploration (Notes section) |
| **Notes** | Open the Notes window | Exploration (Notes section) |
| **Expedition** | Open the Expedition window (tabs Plan, Route and Log), where expeditions are started, paused and stopped | Exploration (Expedition section) |
| **Copy on arrival** (tick) | Copy the next stop's system name to the clipboard at every arrival | Exploration (Expedition section) |
| **Copy Next** | Copy the next expedition stop's system name to the clipboard | Exploration (Expedition section) |
| **Find** | Open the Nearest place to land window | Exploration (Nearest place to land section) |
| **Plot** | Open the Route Planner, which plots a neutron-star route for the ship with Spansh | Exploration (Route Planner section) |
| **Clear Route** | Forget the Route Planner's route and the route the Route overlay follows from the game, so the overlay closes | Exploration (Route Planner section) |
| **Copy the next system to the clipboard automatically** (tick) | Put the next system of the plotted route on the clipboard when the route is plotted and at each stop | Exploration (Route Planner section) |
| **Review** | Open the Prediction review (the species prediction compared with the finds) | Exploration (Organic Scanning section) |
| **Dashboard** | Open the Exploration Dashboard (not the Colonization one below) | Exploration (Dashboard section) |
| **Mark** | Save the current position as a mark for the Surface Compass | Exploration (Compass section) |
| **Target** | Aim the compass at the next target: the nearest hotspot, each mark on this body, then none | Exploration (Compass section) |
| **Marks** | Open the Marks window | Exploration (Compass section) |
| **Materials** | Open the Materials window | Operations (Engineering section) |
| **Blueprints** | Open the Engineering window (blueprints, wishlist, ship and Odyssey upgrade planners) | Operations (Engineering section) |
| **Engineers** | Open the Engineering window on its Engineers tab | Operations (Engineering section) |
| **Hotspots** | Find nearby hotspots | Mine |
| **Add hotspot** | Save hotspot here | Mine (the live window's header) |
| **Prices** | Find best price | Mine |
| **Reserves** | Check ring reserve level | Mine |
| **Import/export** | Import/export hotspots | Mine (the live window's header) |
| **Mark center** | Mark the center of a surface mining location | Mine (the live window's header) |
| **Mark border** | Mark the border of a surface mining location | Mine (the live window's header) |
| **Book** | Space Mining Book (in the Space Mining window) or Surface Mining Book (in the Surface Mining window) | Mine (window headers) |
| **Dashboard** | Open Mining History | Mine (window headers) |
| **Reset** | End this session and start a new tally (offers to save first) | Trade (Session window) |
| **Save session** | Keep this session in Trade History (the tally keeps running; **Reset** starts a new one) | Trade (Session window) |
| **History** | Open the Trade History window | Trade (Session window) |
| **Rebuild** | Recount the session from the journals from a given start time (UTC); for a session that began on another computer | Trade (Session window) |
| **Find routes** / **Cancel** | Ask Spansh for trade routes / stop waiting | Trade (Routes window) |
| **Hops** | Cycle the route length from 2 up to 10 hops | Trade (Routes window) |
| **Round trip** | Find the best back-and-forth pair of stations, loaded both ways | Trade (Routes window) |
| **Copy next system** | Copy the first destination to the clipboard | Trade (Routes window) |
| **Sell** / **Buy** | Select whether the search is for selling or buying | Trade (Market window) |
| **Near me** / **Galaxy** | Best place to sell or buy, nearby / anywhere | Trade (Market window) |
| **Best picks** | Closest, best local, cheapest or highest anywhere, and a price within 10% of the best, for the commodity in the box | Trade (Market window) |
| **Price finder** | The finder behind Mining's **Prices** button, for any commodity | Trade (Market window) |
| **Refresh** | Ask Spansh for the best buy and sell price of each watched commodity nearby (requires Trade lookups on) | Trade (Watch list section) |
| **Watch** | Open the Watch list window | Trade (Watch list section) |
| **Session** / **Routes** / **Market** | Open that page of Trade in its own window | Trade |
| **Space Mining** / **Surface Mining** | Open that page of Mining in its own window | Mining |
| **Mission types** | Open the mission types (massacre stacks, cards, Community Goals) in a window | Mission |
| **Missions window** | Open the window listing every active mission, with progress and pinning | Mission (bottom of the panel) |
| **Find sources** | Where to buy the cargo Collect and Mining missions need, and where to pick up a Delivery mission's cargo (requires Trade lookups on) | Mission (bottom of the panel) |
| **Ships** | Manage ship builds | Operations |
| **Dashboard** | Colonization sites (the Colonization mode's own button) | Colonization |
| **Projects** | Open My Projects, every active project on Raven Colonial | Colonization |
| **History** | Open Colonization History, deliveries over time | Colonization |
| **Create on Raven** / **Not Now** | Shown only when Raven Colonial has no project for a new construction site: open the Create dialog for it / hide the offer | Colonization |

---

Next: select a mode from the [guide index](README.md), or see [what goes on the internet](internet-and-privacy.md).
