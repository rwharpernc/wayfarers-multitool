# Troubleshooting

Find your symptom below. Most problems are a missing setting or a missing permission. For what is known to go wrong in the current release, including overlay text that looks doubled or ghosted, see [Known issues](known-issues.md).

**Jump to:** [Nothing happens (settings that start off)](#nothing-happens-settings-that-start-off) · [A number looks wrong](#a-number-looks-wrong-or-missing) · [General](#general) · [Overlay](#overlay) · [Linux](#linux) · [Missions](#missions) · [Trade](#trade) · [Still stuck?](#still-stuck)

## Nothing happens (settings that start off)

Before anything else, check whether the feature is simply **switched off**. WFMT starts conservative: every on-screen display, every
online lookup and every write to another site is **off until you tick it** in Settings (**File → Settings → WFMT**). A feature that is
off does not show an error. It just does nothing, which looks exactly like a bug.

| If this does nothing... | ...tick this | Where |
|---|---|---|
| Any card on your game screen | The feature's own **Enable** box, below, and the overlay itself must be running ([setup](../OVERLAY_SETUP.md)) | Settings → WFMT → Overlays |
| Landing Assist diagram | **Enable Landing**, then **Show on Overlay** (the diagram on the game screen is a separate tick, also off) | Settings → WFMT → Overlays → Landing |
| Interdiction warning | **Enable Interdiction Warning** | Settings → WFMT → Overlays → Interdiction Warning |
| The missions list on the game screen | **Show missions on the overlay**; pinned missions need the overlay too | Settings → WFMT → Overlays → Missions |
| Carrier jump and fuel alerts | **Enable Flight Alerts** | Settings → WFMT → Overlays → Flight Alerts |
| Route and ship status card | **Enable the Route overlay** | Settings → WFMT → Overlays → Route |
| A Route Planner route on the Route overlay card | The route is plotted in the Route Planner, and **Enable the Route overlay** is ticked (it does not turn the card on by itself) | Exploration panel, and Settings → WFMT → Overlays → Route |
| The Route Planner copying the next system for you | **Copy the next system to the clipboard automatically** (one tickbox, on the Exploration panel and in the plotter) | Exploration panel (Route Planner) |
| Backups made for you | **Back up automatically** and a folder | Settings → WFMT → General → Backup |
| My Powerplay standing in this system, or the next one, on the game screen | **Enable the Powerplay card** (and, for the system you are jumping to, **Look up the system I am jumping to**) | Settings → WFMT → Overlays → Powerplay |
| The running expedition's totals on the game screen | **Enable the Expedition Log card** (and press Start in the Expedition window) | Settings → WFMT → Overlays → Expedition Log |
| What is left to map and sample in a system | **Enable the System targets card** | Settings → WFMT → Overlays → System targets |
| A card describing the body you target or are near | **Enable the Body info card** | Settings → WFMT → Overlays → Body info |
| Sampling progress, predicted species, the sample radar, the sample popup | The tick for each of the four Exobiology cards | Settings → WFMT → Overlays → Exobiology |
| Discovery alerts | **Enable Discovery Alerts**, or the **Discovery Alerts** button | Settings → WFMT → Overlays → Discovery |
| Notable find banners | **Enable Notable Bodies alerts**, then pick the rules you want | Settings → WFMT → Overlays → Notable Bodies |
| The arrow to a mark or hotspot on a planet | **Enable Surface Compass** | Settings → WFMT → Overlays → Surface Compass |
| Inventory pickups and bars | **Show pillage notifications on the in-game overlay** for pickups, and one tick per bar (Backpack, Ship Locker, Carrier Locker, Cargo) for the bars | Settings → WFMT → Overlays → Inventory |
| Mining stats on the game screen | **Enable HUD Overlay** | Settings → WFMT → Overlays → Mining |
| The Mining radar (the Surface Live radar) over the game | **Show the Mining radar over the game while the Rhino is out**, and WFMT's built-in overlay chosen (Windows) | Settings → WFMT → Overlays → Mining and Overlay Connection |
| "Screenshot saved" message on the game screen | **Show a notification on the in-game overlay when a screenshot is saved** | Settings → WFMT → Overlays → Screenshots |
| The Colonization shopping list appears by itself at markets | **Also show the shopping list automatically**. Otherwise only the **Overlay** button on the Colony page shows it | Settings → WFMT → Overlays → Colonization |
| Auto-Honk | **Enable Auto-Honk** or the **Auto-Honk** button | Settings → WFMT → Exploration → Auto-Honk |
| **Find sources** (Missions) and **Best picks** (Trade) | **Enable Spansh trade lookups**; Find sources asks to turn it on when you press it | Settings → WFMT → Trade |
| Routes and Market on the Trade page | **Enable Spansh trade lookups** ([details](#the-lookup-buttons-are-grayed-out-or-there-is-no-commodity-box)) | Settings → WFMT → Trade |
| The **Hotspots**, **Prices** or **Reserves** buttons in Mining | **Enable Spansh nearby hotspot finder**, **Enable Spansh best price finder**, **Enable EDSM ring reserve lookup** (each separately) | Settings → WFMT → Mining |
| ELW rarity or EDSM upload status in Exploration | The two options under Exploration Value | Settings → WFMT → Exploration → Exploration Value |
| Fleet carriers or surface ports missing from "where to buy" results | **Include fleet carriers** and **Include surface ports** in the Where to Buy window | Where to Buy window (the **Where to Buy** button in the Colonization Sites window) |
| Raven Colonial not updating | The master switch and the two options under it ([steps](#raven-colonial-doesnt-update-as-i-deliver)) | Settings → WFMT → Colonization → Raven Colonial |
| Something else is wrong | **Report an issue**, then **Copy diagnostics** to paste the log lines into it ([how](reporting-problems.md)) | Settings → WFMT → General → Help |
| WFMT never updates itself | **Automatically download and install updates** (see also [the update did not take](#the-update-did-not-take)) | Settings → WFMT → General → Updates |
| **Neutron Star** asks Spansh every time | Install the optional Local star index, and leave **Use the local index for Neutron Star when it is installed** ticked | Settings → WFMT → General → Online lookups |
| Chat commands such as `!wf overlays` do nothing | **Chat commands** | Settings → WFMT → General → Shortcuts |
| Prices and routes near you are for the wrong ship size | **Ship size (landing pad)** | Settings → WFMT → Trade |

Notes:

- **Test buttons work even when a feature is off.** A passing **Test** shows the overlay is reachable; it does not mean the live feature is on.
- **Settings are per computer.** A tick on one machine does not carry to another, so check each one you play on.
- **Overlay settings are per commander.** The cards you switch on, where they sit and how they look are saved for the commander playing.
  - If a card is missing after you change commanders, check Settings → WFMT → Overlays for that commander. Settings say whose choices they are on the Overlay Placement tab.
  - The overlay's connection (which overlay draws, host and port) is shared.
- **Press OK** in Settings to keep a change.
- Anything that contacts the internet is listed, with what it sends, on [what goes on the internet](internet-and-privacy.md).

## General

### The WFMT panel doesn't appear

Check that the folder is named exactly `Wayfarers-Multitool` and sits directly inside EDMC's plugins folder, with files such as
`load.py` right inside it (not another folder inside it). So you want `plugins/Wayfarers-Multitool/load.py`, not
`plugins/Wayfarers-Multitool/Wayfarers-Multitool/load.py`. Then restart EDMC.

### A name in the panel ends in "..."

The panel wraps a long name onto the next line rather than cutting it, and only shortens one that is very long (past about 64 characters for a station, system, site or Trade commodity name, 40 for a commodity in the Colonization panel's lines).

A wrapped line uses the width EDMC's window already has; widening the window gives it more room.

### A button or section is missing

Open **File → Settings → WFMT** and check the feature hasn't been switched off. The BGS, Codex Completionist and Organic Scanning
sections can each be hidden there (Settings → WFMT → BGS; Exploration → POI Reference; Exploration → Organic Scanning), and a mode's own button can be hidden under General → Window → *Mode buttons on the main panel*. Also make sure you're in the right mode, and on the right page (some buttons
only appear on one page).

### Numbers look wrong or out of date

EDMC only passes WFMT what happens while it is running. For play with EDMC closed, WFMT reads the recent journal files
when EDMC starts and catches up by itself; the table in
[If EDMC wasn't running](getting-started.md#if-edmc-wasnt-running) shows what each feature catches up on and how far
back. Things to try if a figure is still off:

- Powerplay has a **Rescan** button.
- Codex Completionist has **Backfill Journals** (in the **My Codex** window) for the commander you are playing, for finds older than the automatic catch-up.
- Trade's **Rebuild** button recounts a session from a start time you give; see
  [How a trading session works](trade.md#how-a-trading-session-works).
- Missions shows what the journals say is active. If a mission expired without the game writing anything, log in
  again and the game's own list replaces it.
- **Starting EDMC before the game.** WFMT reads the last commander from your newest journal a few seconds after
  start-up, so your saved data and panels appear without logging in. If you then log in as someone else, everything
  switches to them.
- A feature can only look back a limited way (Missions two weeks, Colonization, including its FC column, 14 to 30 days, Boxel Survey 14 days).
  Older play with EDMC closed isn't found.

### My hotspots, survey finds or Codex tally are missing for a commander

They belong to one commander each, so a commander you have not used before starts empty (see
[Commanders and your data](getting-started.md#commanders-and-your-data)).

- **Mining hotspots:** to copy them from one commander to another, use **Import/export** in Mining: export as the first commander, then
  import as the second.
- **The Codex tally** is built from each commander's own journals the first time they log in; the panel says so
  while it reads (the section title shows "rebuilding..." even when folded) and the summary fills in when it finishes (a
  minute or two for years of journals). If it was
  interrupted, log in again or press **Backfill Journals** in the **My Codex** window.
- The Powerplay Sessions window's **History** tab shows the commander you are playing. The other commanders' sessions are still saved.

### EDMC shows "Frontier CAPI query failure" for a commander with no fleet carrier

This line comes from **EDMC itself**, not from WFMT. WFMT never asks Frontier for anything; it only receives carrier data
when EDMC fetches it.

EDMC's **Enable Fleetcarrier CAPI Queries** option (in EDMC's own Settings) is one switch for every commander.

- When it is on, EDMC asks Frontier for the fleet carrier at game start-up and on other events that any commander produces (a cargo transfer, buying a commodity), without first checking that the commander owns a carrier.
- Frontier answers with nothing for a commander who has none, and EDMC reports that as a failure.
- It does no harm, and WFMT works normally; the line is noise.

If it bothers you:

- Turn that option off while you play a commander without a carrier, and back on for the one who has one. The carrier's real
  cargo and the Carrier Locker in Inventory only come from this query, so they need it on (see
  [Covered or the Carrier row looks wrong](#covered-or-the-carrier-row-looks-wrong)).
- Or leave it on: the commander with a carrier needs it, and the failures for the others are harmless.

### The Ship planner says a module is "not counted"

The planner only counts what WFMT's blueprint table covers, and it says why in the **Counted?** column and the detail under the table (select the row):
- *Pre-engineered*: the module comes engineered from Frontier, so there is nothing to craft.
- *No module type for this item*: the item is not one the table has blueprints for (a cargo rack, a passenger cabin, a module reinforcement).
- *No blueprint ... for a ...*: the journal's blueprint is not in the table for that module type. The table is bundled with WFMT,
  so a blueprint it does not list may be missing. Check the in-game recipe.
- *Only some grades*: the table has fewer grades of that blueprint than the level asks for.
- The experimental effect is not in the table: the grades are counted and the effect is not.

**Add plan to wishlist** can refuse with a message: no commander yet (log in first), more than 100 blueprints on the list, or more than 99 crafts of one. Nothing
is added when it refuses; remove some entries and try again. If **Paste from clipboard** reports no text, paste into the box by hand and press **Read loadout**.
See [Ship planner](operations.md#engineering-blueprints-and-a-wishlist).

### The Route Planner will not plot, or the route looks wrong

- **"The ship is not known yet"**: the plotter reads your ship from the game's loadout, which the game writes when you log in or change ship. Log in (or switch ship and back) with EDMC running.
- **"WFMT does not know this frame shift drive"**: the plotter has figures for the standard drives, the overcharge drives and the Mk II overcharge drive, and will not guess. Report it with **Report an issue**, naming the drive.
- **"Spansh does not know a system called ..."**: check the spelling of the destination (or the source, if you typed one). The route is for systems Spansh has on file.
- **"Could not reach Spansh"**: check your connection; nothing was plotted. A long route can take a minute or two, and **Cancel** stops waiting.
- **The route is longer than you expected, or you run short of fuel**: Spansh plans from a **full tank** with the ship as the journal describes it. If you changed modules or took on cargo after plotting, plot again. Try another **Algorithm** or **Refuel every scoopable**.
- **Nothing is copied to the clipboard**: tick **Copy the next system to the clipboard automatically** (Exploration panel, under **Plot**), or press **Copy next system** in the plotter.
- **The Route overlay does not show the route**: the overlay itself must be switched on (Settings → WFMT → Overlays → Route); a route plotted in the Route Planner takes over its card once it is on. When you reach the last system the card says the route has ended and closes after ten seconds.

### Back up my data made no zip, or a restore did nothing

After a manual **Back up my data** the Backup tab says `Saved N files (size) to <path>`, or `Backup failed: <reason>`. If the file is not where you expect it, the usual causes are:

- **The folder is inside the WFMT plugin folder.** An update or a reinstall can clear that folder, so a backup is refused there. Pick Documents, another drive or a cloud-synced folder.
- **A Flatpak EDMC cannot write to the folder**: it can only write to folders it has been given ([Linux](linux.md)). Pick one it can reach, or grant it with `flatpak override --user --filesystem=<folder> io.edcd.EDMarketConnector`.
- **WFMT has nothing saved yet** (a brand-new install that has recorded nothing).
- **Automatic backups**: they need **Back up automatically** ticked *and* a folder chosen. They run when EDMC starts, only if the newest `WFMT-data-auto-...` zip in the folder is as old as the number of days you set (7 by default), and again before an update installs. A failure is written to EDMC's log.
- **A restore did nothing so far**: it is applied the next time EDMC **starts**; restart EDMC. The files it replaced are in `backups/pre-restore-<date>.zip` inside the WFMT plugin folder if you need them back, and **Cancel the waiting restore** (Backup tab) drops one you no longer want.
- **"That zip holds a file WFMT does not back up"**: only a zip made by **Back up my data** is accepted, and a restore never applies part of a zip it does not recognize.

### The update did not take

Automatic updates are off until you tick **Automatically download and install updates** (Settings → WFMT → General → Updates). With the tick on:

- **WFMT looks once, when EDMC starts**, and ignores a draft or a pre-release. If a release came out while EDMC was already running, restart EDMC to look again.
- **A downloaded update waits for a restart.** The line under the mode buttons turns orange and reads *vX.Y.Z download - Restart EDMC*. Until EDMC starts again nothing has changed.
- **Check the line after the restart.** It reads *Plugin: vX.Y.Z (updated)* in green for 15 seconds, and the version in it is the one now running.
- **A failed check or download** is written to EDMC's log and tried again at the next start. The WFMT panel is unchanged. Extract the ZIP over the old folder by hand instead ([Updating](getting-started.md#updating)).
- A file named `disable-auto-update.txt` in the plugin folder switches updating off whatever the tick says. Delete it if it was left there.

### The Local star index will not download or build

On **Settings → WFMT → General → Online lookups**, the Local star index line says what went wrong.

- **Not enough room:** the first download needs about 173 MB and building needs about 300 MB more while it works. Free some space and press **Download and build** again; a download that was cut off carries on from where it stopped.
- **Spansh is not answering:** see the next entry.
- **The installed index is damaged or was made by another version of WFMT:** the line says so and the **Neutron Star** button asks Spansh instead. Press **Delete**, then **Download and build**.
- **Update downloads nothing:** that is correct if Spansh's file has not changed since your index was built; the line says "The index is already up to date".
- The index is optional. **Neutron Star** works without it by asking Spansh, and **White Dwarf** always does.

### "Spansh has not been answering, so WFMT is not asking it for another N minute(s)"

WFMT spaces its requests to Spansh out, retries a busy answer a few times, and after five failed requests in a row stops asking for five minutes so as not to press a service that is in trouble. Every Spansh feature (routes, prices, Where to buy, Nearest place to land, the Rare Goods Finder's Power column, system-name suggestions) is quiet during the pause and works again by itself. Check your connection, wait the minutes it names, and press the button again. **Copy diagnostics** lists how many requests the session has sent, how many were retried and how many were not sent during a pause ([Reporting a problem](reporting-problems.md)).

### The credits line says "waiting for your balance" or the Game mode line says "waiting for login"

Both lines fill in from the game's own events:

- **Game mode** is read when you log in, or when EDMC starts with the game already running (from the newest journal). It goes back to *waiting for login* when the game shuts down.
- **Credits this session** starts counting at login and waits for EDMC to pass on your balance. If you restart EDMC in the middle of a session it picks the session back up while the game is still writing the same journal file.
- If you started EDMC before the game, WFMT shows the saved data for the last commander at once, but these two lines still wait for a running game. Log in and they fill in.

### The Exploration Dashboard is empty, or its overlay buttons do nothing

- **Empty or "No system yet"**: it shows what WFMT has seen this session. Jump, or log in with EDMC running; **Orbit** fills as you honk and scan, **Surface** when you are near a body.
- **Surface shows no biology**: the body must have been scanned, and mapped for its genera to be known; scan a plant with the Composition Scanner to name one.
- **The overlay buttons say OFF but the cards come back**: the buttons hide cards that are switched on; they never switch a card on. If a card is not ticked in Settings → WFMT → Overlays it will not appear either way.
- **Everything is hidden**: **Hide overlays** (all of them) is a separate switch ([Overlay setup](../OVERLAY_SETUP.md)); the dashboard's two buttons hide only the exploration or only the exobiology cards.

## Overlay

### On-screen alerts don't show up

They need an overlay running:

- WFMT's **built-in overlay** (Windows): pick it under **Settings → WFMT → Overlays → Overlay Connection → Which overlay draws**, press OK, and run Elite borderless or windowed.
- **EDMCModernOverlay** running (WFMT's host and port on the same tab must match it).

To check, use the **Test** buttons in each feature's Settings tab, and **Check connection** on the Overlay Connection tab.

The full checklist is in [Setting up the overlay](../OVERLAY_SETUP.md#if-nothing-shows-up).

### Notable Bodies never shows anything

It is switched off until you tick **Enable Notable Bodies alerts** under **Settings → WFMT → Overlays → Notable Bodies**. Only some
rules are on to start with, so tick the ones you want. A banner needs the overlay to be running.

### Overlay displays are in the wrong place, cut off, or stop short of the right edge

(A display that is not there at all, though the overlay works, is covered under
[Linux](#one-display-never-shows-though-test-and-the-overlay-window-both-work).)

Open **Settings → WFMT → Overlays → Overlay Placement**.

- The **layout editor** at the top is a to-scale picture of your screen. Drag a display's box where you want it (a box dropped near an edge snaps flush to it with offset 0, and **Picture size** makes the picture bigger).
- Press **Show placement preview** to see a box for every display at its real size.
- Press **Detect screen again** if the screen size or scaling line looks wrong.
- **Reset all to defaults** puts every spot back.
- Displays on the right use an offset to reach the screen edge. If that misbehaves, untick **Carry displays on the right to the screen edge**.

The details are in [Setting up the overlay](../OVERLAY_SETUP.md).

### A species shows 2/3 (or no prediction) after I played with EDMC closed

**What you see:** the Bio status card or the Dashboard shows a species one or two scans short of what the game says, or a body you scanned has no predicted species, although
System targets knows the species is analyzed.

**Why:** EDMC only passes WFMT the events that happen while it runs. WFMT reads the last 14 days of journals when EDMC starts and raises each species to what they show
(and fills in a body's conditions, genera and first-footfall flag if nothing is saved for it), so the usual cause is that EDMC has not been restarted since, or the body was
scanned and sampled more than 14 days apart.

**What to do:** restart EDMC (it is safe at any time) and give it a minute. Look in EDMC's log for `Organic Scanning caught up from the journals`. If it is still short,
scan or sample the species again; the next scan sets the right stage. A plant marker or the distance to the last sample cannot be recovered from the journals: see
[If EDMC wasn't running](getting-started.md#if-edmc-wasnt-running).

### The Exobiology cards are empty, or show a planet I have left

The Exobiology cards (Bio status, Biology, Bio radar) show the body the game says you are at, which it names in `Status.json` only while you are near it.

- They are empty in supercruise and clear when you leave a planet (what you sampled is kept and returns with the body).
- They also need the body to be **mapped** (the genera come with the mapping scan). Until then Bio status shows the signal count.
- If a card is empty on a mapped planet you are standing on, press **Test Cards** (Settings → WFMT → Overlays → Exobiology) to check the overlay itself.

See also [Exobiology](exobiology.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it).

### The Expedition Log shows nothing, or its numbers look low

You start, pause and stop expeditions in the Expedition window (the **Expedition** button in the **Expedition** section of the Exploration panel, which starts folded each time EDMC starts: click its title (▸) to open it). The section only shows what is running. The archive of your expeditions is the **Log** tab of that window.

With the card switched on and no expedition running, the card says so (`No expedition is running`) and how to start one.

The log counts only while an expedition is **running**:

- Press **Start** in the Expedition window (Plan or Log tab) when you set off, and the section and the card show it.
- Anything that happened before you pressed it, or while EDMC was closed, is not counted until you press **Rescan** on that expedition in the Log tab (it works the totals out again from your journals between the expedition's start and end).
- **Start from my last** (**sale**, **Discovery Data sale** or **Exobiology Data sale**) begins one from that sale and fills it in.

Other things to know:

- Earned credits count when you **sell** the data, not when you scan it; the unsold figures are estimates.
- If you play more than one commander, each has its own archive.

### Overlay text looks doubled or ghosted, with a second copy in a different font

(Also listed in [Known issues](known-issues.md).)

Two copies of EDMCModernOverlay's overlay window are running and each draws everything WFMT sends. This happens when EDMC is closed or restarted in a way that leaves the old overlay window running. The old window, which keeps the font it started with, reconnects to the new session and draws over the new one.

To fix it:

1. Open Task Manager (or `ps` on Linux) and look for more than one `overlay_client` process (a `python.exe -m overlay_client.overlay_client` pair for each window, started at different times).
2. End the older ones, or end them all and restart EDMC, and the ghosting goes.

To check, **Settings → WFMT → Overlays → Overlay Connection → Check connection** says when more than one overlay window is running (and Copy diagnostics lists how many). WFMT cannot start or stop the overlay itself, so it cannot end the extra one for you.

### Every overlay is in capital letters

**With EDMCModernOverlay:** it draws every plugin's text in one font, and its preferred font is `Eurocaps.ttf`, Elite's cockpit font, which has capital letters only. WFMT sends the species names in the right case (`Tussock pennatis`), and the font draws them as capitals.

To change it:

1. Open **Settings → WFMT → Overlays → Appearance → Overlay font**.
2. Pick a font with lower case letters (or **Add font file...** to use one you downloaded, for example from Google Fonts).
3. Press OK and restart EDMC.

That changes the font for every overlay, and an update of EDMCModernOverlay can put its old list back.

**With WFMT's built-in overlay (Windows):** it has a font of its own, Source Sans 3, with lower case letters, so this does not happen. You can choose another under the same Overlay font section (it is used as soon as you press OK, and a font you add stays through updates).

Neither overlay can draw italics, so species names are not italicized.

### Overlay text wraps, or a card is too small or too big

Open **Settings → WFMT → Overlays → Appearance** and press **Show sample**.

- **Built-in overlay:** a card's box is measured from the text in the font in use, so it should fit closely. If it does not, or text is cut, report it with a screenshot.
- **EDMCModernOverlay:** cards are sized from an estimate of the text at the chosen size and given 10% extra width, so a card may still be tight on a small screen.
- If **Text size** is set to Larger, try Default on the same tab (the overlay's smallest size is not offered because it is hard to read over the game).

### The built-in overlay shows nothing, or disappears

The checklist is in [Setting up the overlay](../OVERLAY_SETUP.md#if-nothing-shows-up). The usual causes:

- It is not chosen under Overlay Connection (or you did not press OK).
- Elite is in fullscreen rather than borderless or windowed.
- Another program is in front (the overlay hides on purpose; tick **Keep showing...** for a tool WFMT does not recognize).
- You hid the overlays (the line in the WFMT panel says so).

**Check connection** says whether it is running and whether it found Elite's window.

## Missions

### A mission shows no progress

- **Source and return (Collect) missions** get nothing from the game until you hand cargo in, so WFMT shows what is in your hold against what the mission asks for (`36/60 held`).
  - It counts every ton of that commodity aboard, whether or not you bought it for the mission.
  - It does not count cargo in a fleet carrier or another ship.
  - With an empty hold it reads `0/60 held`.
- **Massacre and settlement-raid kills** marked `~` are estimates, and wing and on-foot kills are often missing from the journal until the mission completes.
- A mission accepted more than two weeks ago, before WFMT could see it, is not on the list at all. See [Missions](missions.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it).

### Find sources does nothing, or says it does not know where I am

It needs **Enable Spansh trade lookups** (Settings → WFMT → Trade); the window asks to turn it on.

- "From where I am" uses your current system from EDMC, then from your newest journal, so you do not need to jump first.
- If neither knows, it falls back to the turn-in system and says so.
- If none of your missions needs cargo to be found, the window says that too.

## Colonization

### The Colony page says "No active construction site"

Dock at the construction depot, or open its market, **once**. The game writes the site's needs only then.

### "Covered" or the Carrier row looks wrong

The journal only records cargo you transfer to the carrier, so WFMT's carrier figure is what it saw you move. Two ways to put it right:

- **For the real hold:** sign EDMC in to Frontier and open **Carrier Management** in the game. WFMT then reads the carrier's actual
  cargo (at most every 15 minutes, and Frontier's copy can lag the game by a little).
- **For a transfer that did not register:** press **Rescan Journals** in the Colonization Sites window. It rebuilds the tally from the
  last 30 days of journals and drops any figure taken from Frontier, so it is a quick fix, not a replacement for the real hold. See
  [Rescan Journals](colonization.md#rescan-journals-when-a-load-did-not-register).

### Raven Colonial doesn't update as I deliver

WFMT sends nothing to Raven Colonial until you turn sharing on. It is **off by default**, and it is separate from the Raven features
that only read (Planned Builds, Raven Progress and the quick links work without it). If your deliveries never reach Raven, this is
almost always why.

In **Settings → WFMT → Colonization → Raven Colonial**:

1. Tick **Allow WFMT to write to Raven Colonial (master switch)**. The options under it stay grayed out until you do.
2. Tick **Report my construction progress and deliveries to Raven Colonial**.
3. Tick **Also report cargo I move to and from my fleet carrier** if you want that too.
4. Paste your key from [ravencolonial.com/user](https://ravencolonial.com/user) and press **Test key**. Raven answers with your name
   for you when the key is accepted. With no key, nothing is sent.
5. Press **OK** in Settings.

Only deliveries made while sharing is on are sent. WFMT does not backfill earlier ones.

- The update reaches Raven when the depot's figures change and when you deliver, so dock at the site or open its market to send the current totals.
- If another tool also reports your deliveries to Raven, turn one of them off, or Raven counts each delivery twice.
- The setting is saved per computer, so check it on each machine you play on.
- If it is on and Raven still does not update, the EDMC log shows the failed request; please [report it](../../README.md#getting-help) with those lines.

### Raven Progress says Raven has no project for my site

WFMT finds a site's project in two ways: from the system's plan on Raven (by the site's market id, or by its name while it is being built),
and, if the plan names none, by the system's address and the site's market id. If you renamed the site in the game, dock at it once so
WFMT takes the new name.

A site that is only *planned* on Raven, or one you never started a project for, has no project yet. Select the site and choose
**Create Project on Raven** in the **Raven Colonial** menu to make one (see the
[guide](colonization.md#starting-a-project-on-raven-colonial)). Otherwise see
[sharing your progress](colonization.md#sharing-your-progress-with-raven-colonial).

### Create Project on Raven did not work

The status line at the bottom of the Colonization Sites window says which step Raven refused.

- **"No Raven Colonial key is saved", or switched off:** tick the master switch and paste your key in Settings → Colonization → Raven Colonial.
- **"WFMT does not know this system's address yet":** dock at the site once (or be in that system) so the game reports it, then try again.
- **"Raven Colonial did not accept the key (or this commander may not change that)":** check the key with **Test key**. A system locked to another architect may also refuse.
- **The project was made but linking you, making it primary or attaching your carrier failed:** the project exists. Open **My Projects** and use **Set as My Primary**, or fix the rest on ravencolonial.com.
- **"Attach my fleet carrier" is grayed out:** WFMT has not seen your carrier's id this session. Log in again or open Carrier Management once.
- **"Raven Colonial already has a project":** nothing was created; progress sharing uses the project that is there.

### Test key says Raven did not accept the key

Check that you pasted the key from your account page ([ravencolonial.com/user](https://ravencolonial.com/user)) with no spaces, and
that the commander you are playing is the one the key belongs to (keys are saved per commander). WFMT sends the key and your commander
name together, as Raven's own website does. If a key you know is right is still refused, please [report it](../../README.md#getting-help).

### My history is smaller than what I delivered

The game keeps no delivery history, but your journal files do.

- The first time WFMT sees a commander it reads all of that commander's journals once and rebuilds the history from them, so it goes back as far as your journals do (it logs "Colonization history rebuilt" when it is done).
- Deliveries from journal files you have deleted are missing.
- After that it counts as you play and catches up from 14 to 30 days of journals at start-up.
- The page says which date it counts since.

## Linux

See [WFMT on Linux](linux.md) for the setup these refer to.

### On-screen alerts don't show, and Check connection says OK (Flatpak EDMC)

**Check connection** passes even when the overlay window never started. Grant the "run host programs" permission
(Step 3, command 4 in [WFMT on Linux](linux.md#step-3-if-edmc-is-a-flatpak-grant-it-five-permissions)), then
restart EDMC. You can confirm the overlay window is running with:

```bash
ps -eo args | grep overlay_client
```

### One display never shows, though Test and the overlay window both work

Its saved position may be off the edge of the screen. This can happen with a saved position such as a Colonization shopping list at x = 1280 on a screen that is 1280 wide.

- WFMT sends the display and nothing is wrong with the connection, but it is drawn where you cannot see it.
- WFMT notices a saved exact position that is off the overlay's canvas and uses the display's default placement instead (the EDMC log says so), so the steps below are only needed if the display is still missing.

To confirm, look in the overlay's log (for a Flatpak EDMC,
`~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/logs/EDMCModernOverlay/overlay_client.log`) for lines such as:

```
Payload 'wfmt_colonization_s14_1' from plugin 'WFMT' rendered completely outside the overlay window (bounds=(2536.0, 420.0)-(2569.0, 446.0), window=2048x1280)
```

To fix it, open **Settings → WFMT → Overlays → Overlay Placement**, pick the display, and reset it to its default or choose an anchor
(for example left, middle). **Reset all to defaults** puts every spot back. Then restart EDMC.

**Workaround:** on the Overlay Placement tab, choose a named spot such as Top left, which fits any screen, and save.

- If you type an **Exact position**, keep x between 0 and 1240 and y between 0 and 940 (the overlay's canvas is 1280 x 960).
- Placements are saved per computer in EDMC's own settings, so a fix on one machine does not carry to another; repeat it there.

### Auto-Honk or the screenshot timer say `xdotool` is not installed

Install `xdotool` on your system (Step 1). If EDMC is a Flatpak, also grant the "run host programs" permission
(Step 3, command 4) and restart EDMC. If it still fails, the EDMC log shows a "Host lookup of xdotool failed" line
with the reason.

### Auto-Honk says no usable keybind found

Either your fire button has no keyboard key (Step 4), or WFMT can't read the bindings folder.

- Bind a keyboard key to the second slot of Secondary Fire (Step 4).
- For a Flatpak EDMC, grant Step 3, command 2.
- Make sure **Elite Wine/Proton prefix** in **Settings → WFMT → Exploration → Auto-Honk** is empty unless you really use a
  custom setup. A wrong value there hides your keybindings.

### Features that read the journal find nothing

EDMC's **Journal directory** isn't set, or points at the wrong place. See
[Step 2](linux.md#step-2-tell-edmc-where-elites-journals-are).

## Trade

### The lookup buttons are grayed out, or there is no Commodity box

The Spansh lookups are off until you tick **Enable Spansh trade lookups** under **Settings → WFMT → Trade**. The
Commodity box only appears on the Market page, and only once lookups are on.

### I can't tell whether it's searching for a place to buy or to sell

The **Sell** and **Buy** buttons under the Commodity box choose the side. The lit one is active, and the results
heading says "Selling" or "Buying". Changing the side clears the old results.

### The Market search finds nothing for a commodity

- Pick the name from the suggestion list. Spansh only knows commodities by their exact in-game name (for example
  "Void Opal", not "Void Opals"), and an unknown name finds no markets.
- Check that your ship's pad size is right under **Settings → WFMT → Trade**. Stations without a pad your ship fits
  are left out, and the result says how many were.

### The Session page seems to have lost some trades

A session lasts until you press **Reset**, across logins and EDMC restarts, and catches up from the journals when
EDMC next sees you. So check:

- You didn't press **Reset** (it asks to save first if there was anything unsaved).
- On Linux, that EDMC's **Journal directory** is set. Without it the catch-up can't read the journals.
- Trades made before WFMT first ran aren't counted.

### Save session is grayed out, or the History window is empty

**Save session** needs at least one trade or running cost in the session. The History window only lists sessions you
saved, so press **Save session** first.

### Trade History says I had cargo unsold that I'd already sold

The "Bought, not yet sold" estimate on the Stock & carrier tab only comes down when WFMT sees you sell. Cargo your
carrier sold on a trade order, or that you lost or jettisoned, stays in it. The Session page does not show this
estimate; it shows only your ship hold and the carrier's cargo figures.

### My carrier doesn't show, or its cargo looks wrong

- Check your carrier choice for that commander under **Settings → WFMT → Trade** (Auto, Fleet, Squadron or Both,
  not None).
- Open **Carrier Management** in the game once so the game reports its space.
- Read [what the game does and doesn't tell us](trade.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it):
  it lists every gap in the game's data and the workaround for each.
- If the numbers still look wrong, open an issue with the `CarrierStats` line from your journal (it is in the latest
  `Journal.*.log`).

## A number looks wrong or missing

Often it is a limit of what the game records, not a fault: WFMT, like every third-party tool, only knows what the game writes to its journal files (see [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows)).

Each mode guide ends with "What the game does and doesn't tell us, and how to work around it":

- [Powerplay](powerplay.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)
- [Exploration](exploration.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)
- [Mining](mining.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)
- [Trade](trade.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)
- [Missions](missions.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)
- [Operations](operations.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)
- [Colonization](colonization.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)
- [BGS](bgs.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)
- [Landing and Interdiction](always-on.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)

## Still stuck?

EDMC's **Help** menu can open its log folder. The log often says exactly what went wrong, and including it in a report helps a lot.

**Settings → WFMT → General → Help** has a **Report an issue** button and a **Copy diagnostics** button that do most of the work: see [Reporting a problem](reporting-problems.md).
