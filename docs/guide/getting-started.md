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
- [Settings](#settings) (every tab, with its defaults)
- [Typing a system name](#typing-a-system-name)
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

- **WFMT's built-in overlay** (**Windows only**; there is no Linux version yet; one is being researched): nothing to install. Choose it under **Settings → WFMT → Overlays → Overlay Connection → Which overlay draws**. It draws WFMT's displays only.
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
releases (a draft or a pre-release is ignored). The **Release notes** link on that tab opens the latest release's page in your browser.

**How the in-app updater works**

1. **When it looks.** Once, in the background, each time EDMC starts, and only with the tick on. It asks GitHub for the latest release ([what goes on the internet](internet-and-privacy.md)) and compares its version number with yours. If yours is the same or newer, nothing more happens.
2. **What it downloads.** The `.zip` attached to the newer release, into an `updates` folder inside the plugin folder.
3. **What it protects.** Before anything is swapped, it makes a data backup first if **Back up automatically** is ticked ([Backing up your data](#backing-up-your-data)), and a zip of the program files it is about to replace in the plugin folder's `backups` folder (the newest three are kept). It writes only the files the release holds and skips the names of your saved data files, so your data, the `star_index` folder and any fonts you added stay as they are.
4. **When it takes effect.** The new files are staged now and run when EDMC starts again; nothing is swapped into a running program. Restart EDMC when you are ready.
5. **If it fails.** A failed check or download is written to EDMC's log and tried again at the next start. The panel is unchanged. Extracting the ZIP by hand always works.

The first line under the mode buttons always says which version you are running (**Plugin: v1.3.3**).

- While an update is coming it says, for example, **Plugin: v1.3.3 (downloading v1.3.4...)**.
- Once the update is downloaded it turns bold black on **orange** and reads **the new version's number, then download - Restart EDMC**.
- The update only takes effect when EDMC starts again; nothing is swapped in while it runs.
- After the restart the line shows the new version with **(updated)** after it, in green for 15 seconds.
- Clicking the line opens the latest release's page in your browser.

*Building from source is for developers only. See [DEVELOPMENT.md](../DEVELOPMENT.md).*

## A first five minutes

You don't have to configure anything to get value out of WFMT, but this short tour helps:

1. Look at the row of buttons at the top of the WFMT panel. Those are the eight **modes**. Click one and the panel below
   changes. Hover over a button for a moment to see its full name.
2. Open **File → Settings → WFMT**. Each mode has its own tab. Look through the ones you care about and turn
   things on or off. Press **OK** at the bottom of EDMC's Settings window to keep what you changed ([Settings](#settings) lists every tab).
3. If you want on-screen alerts, set up an overlay (see above), then press a **Test** button in Settings to
   check it works.
4. **Linux only:** make sure EDMC's *Journal directory* is set. See [WFMT on Linux](linux.md).
5. Optional but wise: switch on **Back up automatically** under **Settings → WFMT → General → Backup** ([Backing up your data](#backing-up-your-data)).
6. Play. Most things fill themselves in as you go.
7. Skim the "What the game does and doesn't tell us" section at the end of each mode's guide. It lists what the
   game never records (for example, a fleet carrier's cargo is only exact after you open Carrier Management) and
   how to work around it.
8. If something looks wrong, try [Known issues](known-issues.md) and [Troubleshooting](troubleshooting.md), then **Settings → WFMT → General → Help → Report an issue** ([Reporting a problem](reporting-problems.md)).

**Why WFMT sometimes can't tell you something.** WFMT, like every third-party tool, only knows what the game writes to its journal files, and not everything is logged.

- It fills some gaps from Frontier's servers (through a signed-in EDMC) and from data players and communities report (Spansh, EDSM, Canonn, edastro, Raven Colonial).
- It works around the rest with labeled estimates and small steps you take.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## Finding your way around

### The mode buttons

WFMT has one panel with eight modes. You switch between them with the button row at the top of the panel:
**Powerplay**, **BGS**, **Explore**, **Mining**, **Trade**, **Missions**, **Operations** and **Colony** (Colonization).

**Every mode keeps working in the background** while you look at a different one. Nothing pauses. If you're
mining and flip to Trade to check a price, your mining stats keep counting.

### The lines under the mode buttons

Just under the mode buttons, above the page itself, WFMT shows these lines, on every mode:

- **Plugin**: the version you are running, for example `Plugin: v1.3.3` (see "Updating" for what it says during an update). Click it to open the latest release's page.
- **Game mode**: `You are in Open mode.`, `You are in Solo mode.` or `You are in Private Group mode (the group's name).` Until the game has logged in it reads `Game mode: waiting for login…`.
- **Credits this session**: what you've earned or lost since you logged in, for example `Credits this session: +1,234,567 cr earned (+411,522 cr/hr)`, `Credits this session: -5,000 cr lost` or `Credits this session: no change yet`. It is your balance now minus your balance at login (`waiting for your balance…` until EDMC has told WFMT the balance).
  - The hourly rate appears once the session is about three minutes old.
  - **Click it** to open the **Credits Ledger** (it has a **Help** button):
    - **Income** tab: credits earned per activity for today, the last 7 days, the last 30 days and everything counted.
    - **By day** tab: one row per day, a column per activity and the day's total.
    - **Lifetime** tab: the game's own career totals, which the game writes at login only.
    - The activities are kept apart and never merged: **Trade** (the profit on market sales: the sale minus what the sold tons cost, which can be negative), **Exploration data** (what you sold), **Exobiology data** (what you sold, with the first-discovery bonus), **Mission rewards** (the credit reward only) and **Bounties and bonds** (vouchers cashed in). Days are UTC, as the journal writes them.
    - Limits: the journal does not say which commodity sold was mined, so Mining has no per-day income here (its lifetime profits are on the **Lifetime** tab); nothing is counted for credits spent. The first time a commander is seen, the ledger is rebuilt once from every journal, and after that it counts as you play without counting anything twice.
- **Merits this session**: Powerplay merits earned since you logged in, for example `Merits this session: +1,234 (+567 merits/hr)`. It shows in every mode except Powerplay, whose page has its own session lines.
  - It appears after your first merit of the session, so it stays out of the way if you do not play Powerplay.
  - The rate is the merits divided by the time since you logged in, so it falls while you stop earning.
  - The Powerplay mode's **CP** figures are Control Points, a separate number.
- **Overlays**: `Overlays shown (click to hide)`, which reads `Overlays are hidden (click to show)` while they are hidden. Click it to hide every WFMT overlay at once and click again to bring them back.
  - See [Overlay setup](../OVERLAY_SETUP.md#hiding-the-overlays-for-a-while).
  - Windows also has a keyboard shortcut, and both systems have a chat command: see [Shortcuts](shortcuts.md).
- **Catch-up notice** (gray, and only while it is true): `Reading your journals to catch up (the names of the tasks). This happens once and can take a minute.` It appears when a journal read (Powerplay, the BGS replay, the Codex rebuild and similar) has run for more than about a second and a half, so the quick everyday reads never flash it. Nothing is stored; it goes by itself when the reads finish. It is the first sign that WFMT is working, not stuck, after a first start or a long gap.

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

If you'd rather set the height yourself, untick *Resize the EDMC window's height to fit WFMT automatically* (on by default) under
**File → Settings → WFMT → General → Window**. The same page lets you hide the buttons of modes you do not use under *Mode buttons on the main panel* (a hidden mode keeps working in the background; Colonization is listed there as **Colony**).

WFMT also keeps the panel's **width** to the width of the mode-button row, so switching modes never makes EDMC's window wider or narrower. Long names wrap onto the next line instead.

## Commanders and your data

**Everything WFMT saves about your play belongs to one commander.** Nothing is shared between commanders, and switching commander in EDMC switches what every feature shows:

- Trade sessions and route start, Powerplay and BGS ledgers, Missions.
- Mining hotspots and the ground your Rhino has driven.
- The Boxel Survey position and finds, the Codex tally.
- Colonization sites, Ship Builds, Organic Scanning and Powerplay history.
- The Credits Ledger and the credits line, expeditions and the Expedition Log, notes, the Surface Compass marks, the engineering materials, blueprint wishlist and engineers, stored modules, pinned missions, the Raven Colonial key and the Discord destinations.
- Each commander's overlay choices (which cards are on, where they sit, how they look).

Names are matched ignoring case, so `EXAMPLE` in the journal and `Example` in EDMC are the same commander.

The few things that are not about a commander are the same for everyone: your Settings (the overlay choices are the exception: they are per commander), the downloaded Codex catalog, the optional Local star index, the record of which journal files Trade has read, and the prediction-review record, which is one file shared by every commander on the install and names none of them.

### Backing up your data

WFMT keeps what it records about your play as files in its plugin folder. That covers expeditions and the Expedition Log, system surveys and visit history, Boxel Survey finds, Exobiology state and finds, the Codex tally, missions, trade and ledgers, mining hotspots, notes and so on.

Updates never touch these files, but nothing else copies them, so a deleted or reinstalled plugin folder loses them.

**To make a backup:**

1. Open **File → Settings → WFMT → General → Backup** and press **Back up my data**.
2. Choose a folder in the window that opens (it starts in the folder you used last time). WFMT saves all of your data as one dated zip there (`WFMT-data-20261021-093015.zip`), and the Backup tab reports what was saved (`Saved N files (size) to <path>`) or why it failed (`Backup failed: ...`). If it fails, the folder is the likely cause: one inside the plugin folder, or one EDMC may not write to. Pressing Cancel in the folder window does nothing.

About the backup:

- It is a plain copy of the files, usually a tenth of their size, and nothing is changed or sent anywhere.
- Choose a folder outside the plugin folder, such as Documents or a cloud-synced folder; WFMT refuses one inside it. With a Flatpak EDMC on Linux the folder must be one the Flatpak may write to ([Linux](linux.md)).
- The zip also holds `backup-info.json` (WFMT version, date, platform and the files, with no commander name).
- If you switched on **Archive completed mining runs** (Settings → WFMT → Mining), the `mining_sessions` folder of per-run files is in the zip too. If WFMT has nothing saved yet, it says so instead of making an empty zip.

- **Every commander is in it.** Most files hold a separate section for each commander on the install, so the zip does too.
- **Left out on purpose:**
  - The Raven Colonial keys (`rcc_keys.json`) and the Discord webhook links (`discord_webhooks.json`), because a backup is meant to be copied around.
  - The downloaded Codex catalog, which WFMT fetches again.
  - The optional local star index (`star_index` folder, about 110 MB, built from a public download and made again from Settings).
  - Your Settings and your overlay positions held in EDMC's own configuration are not files in the plugin folder, so they are not in it either. `overlay_settings.json` (each commander's overlay choices) is.
- **To restore or move it:** use **Restore my data...** on the same tab.
  1. It asks for a backup zip (it opens in your last backup folder), checks that it is a WFMT data backup (it must hold `backup-info.json`; a zip with any other file in it is refused, and WFMT never applies part of a zip it does not recognize), shows what it holds (WFMT version, date, number of files, size) and asks before doing anything.
  2. After you confirm, the line under the buttons reads *Restore ready. Restart EDMC to apply it.* and the tab shows *A restore is waiting for the next EDMC start*. The restore happens the next time EDMC starts, because WFMT cannot replace files it is using. **Cancel the waiting restore** (the button shows only while one is waiting) undoes it until then.
  3. It replaces the backup's files for every commander in them, leaves any file the backup does not hold, and keeps the files it replaced in `backups/pre-restore-<date>.zip` in the plugin folder (the newest five). To undo a restore, put those files back.
  4. To move your data to another computer, install WFMT there, restore the zip, and start EDMC.
  5. The files are plain JSON, so other tools can read them too.
- **Automatic backups:** tick **Back up automatically**, press **Choose folder...** and set **Every [n] days** (1 to 90; 7 by default).
  - WFMT makes a backup when EDMC starts if the newest automatic one in that folder is that many days old (or there is none), and again just before an update installs.
  - They are named `WFMT-data-auto-<date>-<time>.zip` and only the newest ten are kept; backups you make with the button are never deleted.
  - It is off until you switch it on, and it needs a folder outside the plugin folder. These three choices (and the last manual backup folder) are saved per computer.

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
| **Credits Ledger** | Sales, data, mission rewards and vouchers earned while EDMC was closed; the first time a commander is seen it is rebuilt once from every journal | Every journal once, then only what is newer than the last event it counted |

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
| Codex entries you found before WFMT first ran (a new install, or a commander new to it) | Codex Completionist catches up forward from the last find it counted, so it starts from nothing for a new install | **My Codex → Backfill Journals** once |
| A Powerplay session or a BGS period looks wrong | Their catch-ups are limited by the scan depth and the tick | **Rescan** (Powerplay); BGS rebuilds a closed period by itself |
| A mining run that began before a restart | The Mining pages read the current journal file only (Mining History and the two books read every journal) | The run carries on from the journal file in use; an earlier file's run is not rejoined |

None of these is lost data in the game; they are limits of what WFMT can read back from the journals.

To tell that a catch-up ran, look in EDMC's log (`EDMarketConnector-debug.log`, in EDMC's log folder; on Windows `%LOCALAPPDATA%\EDMarketConnector\logs`). A catch-up writes a line such as `Organic Scanning caught up from the journals: 3 bodies`, which is the quickest way to tell it ran.

## Settings

All of WFMT's settings live in EDMC's Settings window: **File → Settings → WFMT**. This section lists every tab, what is on it and what it starts as. The mode guides describe what each setting does in use (their "Settings" sections), and [Setting up the overlay](../OVERLAY_SETUP.md) goes through every Overlays tab.

**How Settings behaves**

- **Press OK** (at the foot of EDMC's Settings window) to keep what you changed. A few controls act at once and need no OK: the **Test** buttons, **Check connection**, the Local star index buttons and its tick, **Add font file...**, **Rescan** and **Test Honk Now** in Auto-Honk, and the restore buttons.
- **The tabs are in alphabetical order**, at the top level and inside every row of inner tabs (the Overlays row starts with its three shared tabs). Each row opens on its first tab. A long tab scrolls, and the mouse wheel works over it.
- **Where a setting is kept.** Settings are saved in EDMC's own settings for this computer, so a tick on one machine does not carry to another. The exceptions are the overlay choices (which cards are on, where they sit, how they look), which are kept for the commander who is playing ([Overlay setup](../OVERLAY_SETUP.md#moving-things-around)), and your Raven Colonial key and Discord destinations, which are kept for each commander.
- **Restarts.** Almost every change applies when you press OK. An EDMCModernOverlay font, an update and a data restore wait for the next EDMC start, as their tabs say.
- **Off to start with.** Every on-screen display, every write to another site and every online lookup that has a switch starts off, with one exception: BGS tick detection starts on. The Rare Goods Finder and the Codex "Not found" tab have no switch and ask their service when you open them ([what goes on the internet](internet-and-privacy.md)). [Troubleshooting](troubleshooting.md#nothing-happens-settings-that-start-off) lists the switches with the tick that turns each on.

**The tabs**

| Tab | What is on it | Guide |
|---|---|---|
| **BGS** | *Show BGS faction states and activity* (on); *Detect BGS ticks (polls tick.infomancer.uk every 60s)* (on); *Keep previous ticks for [n] days* (1 to 90, 7 by default) | [BGS settings](bgs.md#settings) |
| **Colonization** | The Raven Colonial group: *Allow WFMT to write to Raven Colonial (master switch)* (off), *Report my construction progress and deliveries to Raven Colonial* (off), *Also report cargo I move to and from my fleet carrier* (off), your *Raven Colonial key* (hidden as you type) with **Test key**, and a link to the page where the key is made. The two reporting ticks stay grayed out until the master switch is on | [Colonization](colonization.md#sharing-your-progress-with-raven-colonial) |
| **Discord** | *Allow Post to Discord* (off); your **Destinations** (each a *Name*, a *Webhook link* hidden as you type, and an optional *Thread ID*), saved for the commander you are playing, with **Test**, **Remove**, **Add destination** and **Copy their destinations**, and **Customize posts…** (how the posts look) | [Sharing reports to Discord](discord.md) |
| **Exploration** | A row of inner tabs, below | [Exploration](exploration.md) |
| **General** | A row of inner tabs, below | this page |
| **Mining** | Display switches, the three opt-in lookups, *Enable body lookup*, *Show coverage minimap*, *Archive completed mining runs*, the stop radius, the refill time, *Target commodities* with its percentage, *Too close to place another rig*, the saved Known Surface Hotspots list and the Surface Live simulation | [Mining settings](mining.md#settings) |
| **Missions** | Six display switches, all on by default: *Show kill progress*, *Show remaining-kills column*, *Show totals row*, *Show mission count*, *Show target settlement (ground missions)*, *Show commodities needed (trade and mining)* | [Missions settings](missions.md#settings) |
| **Operations** | A row of inner tabs, below | [Operations](operations.md) |
| **Overlays** | A row of inner tabs, below | [Overlay setup](../OVERLAY_SETUP.md) |
| **Powerplay** | *CP Ratios* (merits for 1 Control Point: Acquisition 4.0, Reinforcement 2.5, Undermining 4.2); *Clipboard* (the format of **Copy Progress**); *Journal scan* (*Cycles to scan*, 1 to 12, 4 by default) | [Powerplay settings](powerplay.md#settings) |
| **Trade** | *Enable Spansh trade lookups* (off) and the search numbers under it; *Only stations with a large landing pad* (off); *Include fleet carriers in prices and routes* (on); *Include ground facilities in prices and routes* (on); *Routes may use systems that need a permit* (off); *Count fines and bounties I pay as a running cost*; *Ship size (landing pad)*: From my ship, Small, Medium or Large; the carrier choice (Auto, Fleet, Squadron, Both or None) | [Trade settings](trade.md#trade-settings) |

**General** (inner tabs: Backup, Help, Online lookups, Shortcuts, Updates, Window)

| Inner tab | Controls and their starting values |
|---|---|
| **Backup** | **Back up my data**; **Restore my data...**; **Cancel the waiting restore** (shown only while one waits); *Back up automatically* (off) with **Choose folder...** and *Every [n] days* (7). See [Backing up your data](#backing-up-your-data) |
| **Help** | **Report an issue** and **Copy diagnostics**. See [Reporting a problem](reporting-problems.md) |
| **Online lookups** | A read-out (not controls) of every switch that lets WFMT ask another service: On or Off, what it does, who it asks and which tab changes it; the lookups that need no switch and run only when you press a button; and the **Local star index** group below it |
| **Shortcuts** | One row per action (Mark the center, Mark the border, Rig placed, Radar range, Open the Live window, Hide or show overlays): the last key of Ctrl+Alt+Shift plus a key (C, B, R, Z, L and O to start; any letter, digit, F1 to F12, or Off), with a warning if two actions share a key or Elite already uses the combination; *Chat commands* (labelled `Chat commands (type  !wf <word>  in Elite's chat)`) (off); *Play a sound when a shortcut worked* (on). The key choices work on Windows only. See [Shortcuts](shortcuts.md) |
| **Updates** | *Automatically download and install updates* (off); the **Release notes** link. See [Updating](#updating) |
| **Window** | *Resize the EDMC window's height to fit WFMT automatically* (on); *Suggest system names from Spansh while typing* (off); *Mode buttons on the main panel*: a tick for each of Powerplay, BGS, Explore, Mining, Trade, Missions, Operations and Colony (all ticked; unticking every one shows them all); *Text size in WFMT's windows* (points larger than normal, -2 to 6; 0); *Color theme of WFMT's windows* (Navy, Cyan, Amber or Green; Navy); *Always open WFMT's windows on EDMC's monitor* (off) |

**The Local star index group** (bottom of Online lookups) is optional; WFMT works fully without it.

- It lets **Neutron Star** (nearest neutron star) answer from a file on this computer instead of asking Spansh each time. The line above its buttons says what is installed (for example how many neutron stars, its size and the date it was built from), or `Not installed. The Neutron Star button asks Spansh.`, and shows the progress of a running job.
- **Download and build** (available when nothing usable is installed): fetches one public file from Spansh's download server (about 173 MB) and builds the index from it, about 110 MB on disk. It needs about 300 MB of free space while it builds and deletes the download afterwards. A cancelled or interrupted download carries on from where it stopped.
- **Update** (available when an index is installed): fetches only what changed, Spansh's 1-day (about 3 MB) or 1-week (about 19 MB) file of changed systems, when your index is recent enough, and the whole file again only when it is not (or after 20 updates). Pressing it again the same day downloads nothing.
- **Cancel** (while a job runs) stops it. **Delete** (when there is an index file, usable or not) removes it.
- *Use the local index for Neutron Star when it is installed* (on) decides whether the button uses the index. **White Dwarf** always asks Spansh. The index lists systems whose main star is a neutron star; a neutron star that is a secondary star is not in it. A damaged index, or one made by another version of WFMT, is ignored and the button asks Spansh (the line tells you to delete it or press **Download and build**).
- The index is the same for every commander and is not part of the data backup. It is kept in the `star_index` folder in the plugin folder, which updates leave alone.
- Nothing is downloaded unless you press a button.

**Exploration** (inner tabs: Auto-Honk, Boxel Survey, Expedition, Exploration Value, Nearest place to land, Organic Scanning, POI Reference, Region Sweep, Waypoint Route)

| Inner tab | Controls and their starting values |
|---|---|
| **Auto-Honk** | *Enable Auto-Honk* (off); *Fire button* Primary or Secondary (Secondary); *Hold (sec)* (10); *Focus game window first* (on); *Skip systems already visited* (on); on Linux, *Elite Wine/Proton prefix* (blank means auto-detect Steam); **Rescan** and **Test Honk Now**, which work even while Auto-Honk is off. See [Auto-Honk](exploration.md#auto-honk) |
| **Boxel Survey** | *Auto-copy next target to clipboard on jump* (on); *Skip systems already visited this session* (on); *Skip systems already visited by anyone (EDSM)* (off); *Skip systems already fully scanned in EDSM* (off); *Confirm off-sequence arrivals against EDSM* (off); **Export Survey Log**; and for the Random button, **Clear Visited Systems Log** and *Systems to request from Spansh* (10 to 100, 25 by default) |
| **Expedition** | *Copy the next stop's system name to the clipboard every time I arrive anywhere* (off; the same switch as **Copy on arrival** on the panel); *Start the Expedition Log when I start an expedition* (on) |
| **Exploration Value** | *Show estimated scan value, system age, and current region* (on); *Show ELW rarity comparison when you scan an Earthlike World (Spansh)* (off); *Show EDSM upload status when you select a system on the galaxy map (EDSM)* (off) |
| **Nearest place to land** | *Allow this lookup: pressing Find sends Spansh my position, the pad size and my choices, nothing else* (off; the same switch as the tick in the window) |
| **Organic Scanning** | *Show predicted species and scan progress* (on); *Keep a record of what I find, to check the prediction* (on) and **Clear the record...**. See [Exobiology](exobiology.md) |
| **POI Reference** | Three groups on one page: edastro GEC (information only), Canonn (*Include Thargoid sites* on, *Include Guardian sites* on, *Skip sites already logged in Codex Completionist* on) and Codex Completionist (*Track codex entries*, on) |
| **Region Sweep** | *Auto-copy next target to clipboard on jump* (on); *Skip systems already visited this session* (on); *Skip systems already visited by anyone (EDSM)* (off); *Require a full FSS scan (not just arrival) to mark a system complete* (off); *Auto-discover more nearby cubes (EDSM) when the queue is running low* (off) |
| **Waypoint Route** | *Auto-copy next waypoint to clipboard on jump* (on) |

**Operations** (inner tabs: Inventory, Screenshots, Ship Builds)

| Inner tab | Controls and their starting values |
|---|---|
| **Inventory** | The *Pillage message* format (placeholders `{item}` and `{total}`); *Play a sound on pickup* (off; grayed out where no sound can play); *Announce pickups for* each category; the per-loadout backpack capacity overrides. See [Inventory](operations.md#inventory) |
| **Screenshots** | *Delete original file after conversion* (off); *Include WFMT's built-in overlay in the converted screenshot* (off; Windows, built-in overlay); *Group converted files into a per-system subfolder* (off); *Show the auto-capture timer icon on the main window* (on); *Filename Mask* (a preset list); *Auto-capture poll interval (seconds)*; *Use high-resolution capture on the auto-timer (Solo play only)* (off); *Automatically capture a screenshot when scanning a Thargoid signal* (on). See [Screenshots](operations.md#screenshots) |
| **Ship Builds** | An explanation only: the builds are kept by link in the Ship Builds window (**Ships**) |

**Overlays** (inner tabs: Overlay Connection, Appearance and Overlay Placement first, then in order Body info, Colonization, Discovery, Exobiology, Expedition Log, Flight Alerts, Hide overlays, Interdiction Warning, Inventory, Landing, Mining, Missions, Notable Bodies, Powerplay, Route, Screenshots, Surface Compass, System targets). Every option, with its starting value, is in [Setting up the overlay](../OVERLAY_SETUP.md#every-overlays-tab-in-detail).

## Typing a system name

Every box that takes a system name suggests systems as you type, from the second letter. That covers an expedition stop, the Expedition planner's start and end, the trader finder's *Search from*, Colonization's *Around*, a mining hotspot or ring reserve, a note, a waypoint and a Boxel Survey seed.

- **What it suggests:** the systems you have been in this session first, then ones WFMT already holds (expedition stops, notes).
- **Keys:** **Down** and **Up** move through the list, **Enter** or a click takes the highlighted one, and **Escape** closes it. **Enter** with nothing highlighted does what the box always did (add the stop, run the search).
- **Systems you have never been to:** tick **Suggest system names from Spansh while typing** under Settings → WFMT → General → Window. It is off until you tick it, and then the letters you have typed so far (from the third) go to Spansh ([what goes on the internet](internet-and-privacy.md)).

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
navy look with colored headings, a text size and a color theme you can change (the **A-** and **A+** buttons and the theme name at the right end of the bottom line, or Settings → WFMT → General → Window; one choice for every window, remembered; Navy, Cyan, Amber or Green; the small boxes at the top of a dashboard keep their size), remember their size and position, and close with **Esc** or the window's close button. The main panel itself follows your
EDMC theme.

Every pop-out window has the same layout:

- **Header:** the window's title with a one-line subtitle under it, and its buttons on the right. A button with a small arrow (such as **Raven Colonial** or **Manage Sites** in the Colonization Sites window) opens a menu of related actions.
- **Help:** most windows (not the Exploration Dashboard, Inventory, Missions, Ship Builds, Colonization Sites, Where to Buy, Nearest place to land, Prediction review, Source commodities or Surface Mining Book windows) have a **Help** button at the right of the header. It opens a small window of short entries that explain the columns, the colors and the buttons, so the explanation is not a paragraph in the window itself. Press **Help** again and the same window comes forward.
- **Body:** tables you can sort by clicking a heading where the window says so. Windows that are tabs of another window (the Expedition window's Plan, Route and Log tabs) share its header.
- **Status line:** the line at the foot of the window gives the result of what you pressed (a copy, a search, a refusal) and wraps rather than cutting off.
- **Size and place:** remembered for next time; a window opens at least as big as its minimum so nothing is clipped. A window that has never been opened, or whose remembered place is no longer on a connected monitor, opens over the EDMC window on EDMC's monitor. Tick *Always open WFMT's windows on EDMC's monitor* (Settings → WFMT → General → Window) to open every window there instead of where you left it.

## Opening the pop-out windows

Switch to the mode first, then use the button listed here.

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
| Missions window (tabs: Active, By place) | Missions | **Missions window** button at the very bottom of the panel, or click a mission's card |
| Source commodities | Missions | **Find sources** button at the very bottom of the panel (or **Sources** in the Missions window) |
| Inventory | Operations | Click one of the **inventory bars** (there is no button) |
| Materials | Operations | **Materials** button in the Materials section |
| Engineering (blueprints, wishlist, ship and Odyssey upgrade planners, engineers) | Operations | **Blueprints** button in the Materials section |
| Material trader | Operations | **Find a trader** button in the Materials window |
| Ship Builds | Operations | **Ships** button |
| Colonization Sites | Colonization | **Dashboard** button |
| Colonization History (tabs: Overview, By day, Commodities, Sites) | Colonization | **History** button |
| My Projects (your projects on Raven Colonial) | Colonization | **Projects** button, or **Raven Colonial → My Projects** in the Colonization Sites window |
| Planned Builds, Raven Progress and Create Project on Raven | Colonization | **Raven Colonial** menu in the Colonization Sites window |
| Space Mining Book | Mining | **Book** button on the Space Mining page |
| Surface Mining Book | Mining | **Book** button on the Surface Mining page |
| Mining History | Mining | **Dashboard** button, on both mining pages |
| Mining live window (Surface and Space) | Mining | **Live** button, on each mining page |
| Trade History (tabs: Overview, Commodities, Stations, Route, Trades, Stock & carrier, Lookups) | Trade | **History** button on the Session page |

Notes:

- You don't need to be mining to open the Surface Mining Book. It lists your saved hotspots either way.
- In Missions, the **Missions window** button is a table of every active mission with its progress, where to go and time left; you can pin
  missions there so they show on the overlay. Clicking a mission card opens the window on that mission.
- If you can't find the BGS, Codex Completionist or Organic Scanning sections, each can be switched off under
  **File → Settings → WFMT** (BGS, Exploration → POI Reference, Exploration → Organic Scanning). All three are on by default.
- Pressing a window's button while it is open brings that window forward and refreshes it; you do not get a second copy.

## Button names

The mode buttons and the buttons on the panels carry their whole names. **Hover over any button for
a moment and a tooltip shows its name and what it does.** The same goes for the buttons in WFMT's windows, where a button's name is written like Mark center or Add hotspot. The table below lists them with what each one does and where it is.

| Button | Full name | Where |
|---|---|---|
| **Powerplay** | Powerplay | Mode buttons (top of the panel) |
| **BGS** | BGS | Mode buttons |
| **Explore** | Exploration | Mode buttons |
| **Mining** | Mining | Mode buttons |
| **Trade** | Trade | Mode buttons |
| **Missions** | Missions | Mode buttons |
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
| **Sequence** / **Region Sweep** / **Waypoints** | Choose which Boxel Survey sub-mode the section shows | Exploration (Boxel Survey section) |
| **< Prev** / **Next >** / **Copy** | Step to the previous or next target in the sub-mode, or copy the current target's system name to the clipboard | Exploration (Boxel Survey section) |
| **Use Current** / **Set** | Fill the box with the system you are in / start the survey from the name in the box | Exploration (Boxel Survey section, Sequence) |
| **Find Nearby (EDSM)** | Ask EDSM for the nearest real procedurally named system outside the current cube and put it in the Seed box (press **Set** to move the survey there) | Exploration (Boxel Survey section, Sequence) |
| **Find POI** | Find nearest POI (GEC and Canonn) | Exploration |
| **Update POI** | Refresh POI data (Canonn) | Exploration |
| **My Codex** | My Codex window: overview, found and not found, with a Backfill Journals button (Codex Completionist) | Exploration |
| **Add Note** | Save the line you typed as a note about the system you are in | Exploration (Notes section) |
| **Notes** | Open the Notes window | Exploration (Notes section) |
| **Expedition** | Open the Expedition window (tabs Plan, Route and Log), where expeditions are started, paused and stopped | Exploration (Expedition section) |
| **Copy on arrival** (tick) | Copy the next stop's system name to the clipboard every time you arrive anywhere | Exploration (Expedition section) |
| **Copy Next** | Copy the next expedition stop's system name to the clipboard, to paste into the galaxy map | Exploration (Expedition section) |
| **Find** | Open the Nearest place to land window | Exploration (Nearest place to land section) |
| **Plot** | Open the Route Planner, which plots a neutron-star route for your ship with Spansh | Exploration (Route Planner section) |
| **Clear Route** | Forget the Route Planner's route and the route the Route overlay is following from the game, so the overlay closes | Exploration (Route Planner section) |
| **Copy the next system to the clipboard automatically** (tick) | Put the next system of the plotted route on the clipboard when you plot and at each stop | Exploration (Route Planner section) |
| **Review** | Open the Prediction review (what the species prediction listed against what you found) | Exploration (Organic Scanning section) |
| **Dashboard** | Open the Exploration Dashboard (not the Colonization one below: this is in Exploration) | Exploration (Dashboard section) |
| **Mark** | Save where you are as a mark for the Surface Compass | Exploration (Compass section) |
| **Target** | Aim the compass at the next target: the nearest hotspot, each mark on this body, then none | Exploration (Compass section) |
| **Marks** | Open the Marks window | Exploration (Compass section) |
| **Materials** | Open the Materials window | Operations (Materials section) |
| **Blueprints** | Open the Engineering window (blueprints, wishlist, ship and Odyssey upgrade planners, engineers) | Operations (Materials section) |
| **Hotspots** | Find nearby hotspots | Mining |
| **Add hotspot** | Save hotspot here | Mining (the live window's header) |
| **Prices** | Find best price | Mining |
| **Reserves** | Check ring reserve level | Mining |
| **Import/export** | Import/export hotspots | Mining (the live window's header) |
| **Mark center** | Mark the center of a surface mining location | Mining (the live window's header) |
| **Mark border** | Mark the border of a surface mining location | Mining (the live window's header) |
| **Live** | Open the live window for the Mining page you are on (a radar and the controls on Surface, the live numbers on Space) | Mining |
| **Book** | Space Mining Book (Space page) or Surface Mining Book (Surface page) | Mining |
| **Dashboard** | Open Mining History (the Mining mode's own button) | Mining |
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
| **Price finder** | The finder behind Mining's **Prices** button, for any commodity | Trade (Market page) |
| **Refresh** | Ask Spansh for the best buy and sell price of each watched commodity near you (needs Trade lookups on) | Trade (Watch list section) |
| **Watch** | Open the Watch list window | Trade (Watch list section) |
| **◀** / **▶** | Previous / next page | Mining, Trade, Missions |
| **Missions window** | Open the window listing every active mission, with progress and pinning | Missions (bottom of every page) |
| **Find sources** | Where to buy the cargo your Collect and Mining missions need, and where to pick up a Delivery mission's cargo (needs Trade lookups on) | Missions (bottom of every page) |
| **Ships** | Manage ship builds | Operations |
| **Dashboard** | Colonization sites (the Colonization mode's own button) | Colonization |
| **Projects** | Open My Projects, every active project you have on Raven Colonial | Colonization |
| **History** | Open Colonization History, what you have delivered over time | Colonization |
| **Create on Raven** / **Not Now** | Shown only when Raven Colonial has no project for a new construction site: open the Create dialog for it / hide the offer | Colonization |

---

Next: pick a mode from the [guide index](README.md), or see [what goes on the internet](internet-and-privacy.md).
