# Linux Test Checklist

Scope: the checks for testing WFMT on Linux with Elite Dangerous under Steam Proton (or Wine, Lutris or Heroic). The Windows-side plan is [TEST_PLAN.md](TEST_PLAN.md); the open checks are in [TODO.md](TODO.md).

## Test History

- The unit and smoke tests use mocked system calls.
- Two manual passes were made on KDE Plasma (Wayland) with a Flatpak EDMC, on 2026-10-18 and 2026-10-20. Both tested builds from before the 1.0.0 restart and rename.
- The window-fit fixes of 2026-10-21 were checked only in a Docker run (a Linux container).
- 1.5.0 was run on Linux on 2026-11-02, before the release, with no failures (section 7r).
- 1.5.1 was run on Linux on 2026-11-03, before the release, with no failures (section 7s). Docker: 3,923 passed, 13 skipped.
- 1.5.3: the Copy next system fix was run on Linux on 2026-11-04 with no major issues (section 7u). Docker: 4,054 passed, 12 skipped on 2026-11-05. The Expedition summary for Discord is not yet run on Linux.
- Seen working (KDE Wayland, Flatpak EDMC): the WFMT Settings panel; the test overlay, Discovery and Notable Bodies overlays.
- A Flatpak EDMC requires the host-spawn permission in section 0 before overlays draw.

## Reporting

- Report the distribution, the desktop (GNOME, KDE, Sway and others), the session type (X11 or Wayland), and whether EDMC runs natively or as a Flatpak.
- For a failed step, include the step number and the relevant lines of EDMC's log (`~/.local/share/EDMarketConnector/logs/EDMarketConnector-debug.log`).
- Record exactly what is observed (which tabs, which overlays, how often), so that differences can be compared.
- Report issues on the [Issues page](https://github.com/rwharpernc/wayfarers-multitool/issues).

## Testing: Start Here

### Where Testing Stands

- Features are tested on Windows first.
- The Linux pass of 2026-10-18 (KDE Plasma and Wayland, a Flatpak EDMC, an earlier build) covered most of the plugin.
  - It found one problem: right-hand overlay cards stopping short of the screen's right edge. This is largely fixed; a small gap remains on Linux (see Known issues).
- A second Linux pass covered the Route Planner checklist.
- Section 6 holds the remaining work of that period:
  - the Exploration Dashboard
  - the data backup with restore and automatic backup
  - compact data files
  - the Random rebuild
  - POI Reference
  - the My Codex window
  - alphabetical sections in every mode
  - the wrapped-text width fix
  - overlay cards that leave in one step
- On 2026-10-20 the newest features of that time had a quick pass on Linux (also an earlier build), not the full checklist.
- The checklist sections below carry the longer wording for anything those passes did not reach.
- Items marked "Windows-tested only" have not been tried on Linux.

### Newest Features (No Linux Pass Yet)

Complete sections 0 and 1 first, then run the unit tests and a build (steps 2 to 4 under "Getting Set Up"), then the items below. They are work added since the earlier passes. Each has its longer wording in `docs/TODO.md` under "Verification in the game".

- **Added in 1.5.1 (run on Linux on 2026-11-03, before the release; no failures).** The Combat Record, the Engineering row's held and session table, and the shared ship names: section 7s.
- **Added in 1.5.0 (run on Linux on 2026-11-02, before the release; no failures).** The pages-as-windows layout, the settings that moved into their windows, the type-ahead boxes and the darker orange on the light theme: section 7r.
- **Added in 1.3.3 (not run on Linux).**
  - **Powerplay card.** Requires EDMCModernOverlay. Tick *Enable the Powerplay card* (Settings → WFMT → Overlays → Powerplay) and press **Test Card**. A card appears at the top right. Jump into a Powerplay system and then into one without Powerplay data (the card reads **No Powerplay Detected in system**).
  - **Look-ahead.** Tick *Look up the system I am jumping to* and start a hyperspace jump. The card turns to the destination (marked *jumping*) and then to the arrival system. Fly a loop twice: the second lap performs no lookup. Steps: [TEST_PLAN.md](TEST_PLAN.md) section 9.
- **Added in 1.3.2 (not run on Linux).**
  - **Windows open on EDMC's monitor.** With two monitors, open a WFMT window not opened before (the Notes window, for example). On Linux, Tk cannot list the monitors, so the window opens centered over the EDMC window and kept on the visible screen. Record which monitor it lands on, under X11 and under Wayland. Drag it to the other monitor, close it and open it again: it reopens there. Then tick *Always open WFMT's windows on EDMC's monitor* (Settings → WFMT → General → Window) and open it again: it opens over the EDMC window.
- **Added 2026-10-23 (none run on Linux).** The Windows side of each is in [TEST_PLAN.md](TEST_PLAN.md) section 5.
  - **Every overlay off.** After `git pull --rebase`, start EDMC. The log has `All WFMT overlays reset to disabled (one-time), including the saved choices of N commander(s)` once, and no card shows for any commander. Turn one on and restart: it stays on.
  - **Screen size from the operating system.** In Settings → Overlays → Overlay Placement, with the overlay's log and `DisplaySettings.xml` out of the way, press **Detect screen again**. The source line states that the primary display is used, with the real resolution.
    - The detection runs `xrandr --current` (through `flatpak-spawn --host` from a Flatpak) and takes the primary output. Report the session type (Wayland or X11), whether `xrandr` is installed, and the source line.
    - On a multi-monitor desktop only the primary output counts.
  - **A stopped expedition and Rescan.** Stop an expedition, wait a minute and start it again: the clock continues from where it stopped. Pause one, jump while it is paused, resume and press Rescan: the totals exclude those jumps.
  - **Table text.** A long faction, station, ship, role or site name in Missions, Source commodities, Ship Builds and My Codex shows whole in a wide window and is cut with an ellipsis in a narrow one.
  - **Saved names** (a copy of data from before the spelling change): `Renamed saved names:` appears once in the log and the Colonization data is intact.
  - **Ship planner, In storage column.** Open Module Storage once at a station, then read a build that holds a stored module. The column reads Yes for the same engineering at the level or above and Partly for other engineering. Select the row for the module's location. A module fitted to a ship does not match.
  - **Tests.** Run `python -m unittest discover -s tests` from a desktop session (3,370 tests passed in the Docker run). Report the number skipped and any failures.
- **Window layout.** Open these windows:
  - Missions, Trade History, Credits Ledger, Engineering (all five tabs)
  - Expedition, Expedition Log, Exploration Dashboard
  - Notes, Marks, Colonization Sites and the Mining windows
  - Make each as narrow as it goes and then as wide as the screen. Check:
    - Nothing is cut off, and no button is pushed out of the window.
    - Tab rows wrap.
    - The stat tiles wrap onto a second line instead of clipping.
    - Tables use the width.
  - The headless version of this check is in the unit tests (`tests/test_window_fit_*_smoke.py`). They run only from a desktop session, so a failure there is a real Linux finding.
- **Themed confirmations and prompts** (they replace the operating system's boxes).
  - Open: Reset Session, Delete session, Reset trade session (three buttons), Paste spot, Delete hotspot, Import Hotspots, Turn on online lookups?, the Raven key prompt (typing is hidden) and Restore my data (Settings, over a Settings page).
  - Each dialog:
    - appears centered over its window
    - blocks the window until answered
    - wraps long text
    - takes Esc as Cancel and Enter as the highlighted button
    - takes focus under KDE Wayland
- **Screenshot preview.** Take a screenshot with the preview on, from a very wide capture and a tall one.
  - The window stays on the screen and the picture is whole.
  - Esc and Close work, and resizing re-fits the picture.
  - **Open Folder** opens the file manager. From a Flatpak this goes through the sandbox. Report if nothing opens.
- **Spansh requests.**
  - Random, Neutron Star and White Dwarf, Nearest place to land, Where to buy, the Mining price finder, and typing in a system-name box (with the Settings → WFMT → Window suggestion option on) all answer.
  - Press Random several times quickly: the requests are spaced, not sent together.
  - With the network off, a lookup fails with a clear message. After several failures the message states that Spansh is being left alone for a few minutes.
- **Ship links.** Ship planner:
  - Paste a Coriolis or EDSY import link and read it.
  - **Copy Coriolis link** and **Copy EDSY link** copy a link (paste it into a text editor to confirm it is one long address).
  - **Open in Coriolis** and **Open in EDSY** open the browser.
  - From a Flatpak EDMC, opening a browser also goes through the sandbox. Report if nothing opens, and the same for Report an issue under Settings → General → Help.
- **Stored modules.** Open Module Storage at a station in the game, then Ship Builds → **Stored modules**.
  - The list, the freshness line and the transfer cost and time match the game.
  - Store, retrieve and swap a module and confirm that the tab follows.
  - Restart EDMC and confirm that it catches up from the journals (the journal folder is in the Proton prefix: section 0).
- **Start expedition and Review.** Plot a route, press **Start expedition**.
  - The expedition starts together with its Expedition Log run.
  - **Review expedition** opens the Expedition window on it.
  - Pause and Resume from either side agree, and a restart while paused keeps both paused.
  - The plan dialog's **Start it now** tick starts a Road to Riches or Exomastery plan.
- **One Expedition window.** **Expedition** and **Plot** on the panel open the same window with Plan, Route and Log tabs.
  - It is never opened twice.
  - The panel has one Expedition section (the Log's figures, Copy Next and Expedition, with no Start, Pause or Stop) and no Expedition Log section.
  - The tabs' buttons and tables fit at its smallest size and at the full screen width.
  - Report whether the window takes the focus when it opens (it is intended not to take focus from the game).
- **Mining.**
  - The low-limpet alert does not appear for a Rhino or a laser miner with no limpets, and appears for a prospector-limpet ship at zero.
  - The HUD and panel show the same limpet count.
  - Relogging inside a ring fills in the ring.
  - Mining History's Earned includes a sale made at a different station than the one docked at after mining (and *Mined, not sold yet* shows what is waiting).
  - The price finder and What pays leave fleet carriers out and fill *Minimum demand (t)* from the hold.
- **Station price against the average.** Docked after a ring run with the commodities market open, the Space Mining window shows `<commodity> here: N cr/t, P% above/below the galactic average (M)` for what the run refined.
  - It reads `Market.json` from the journal folder.
  - Report whether it appears with a Flatpak or Proton setup.
- **Mining rates and targets.**
  - The Space Mining window, the Surface Mining Live window and the HUD show the same *Refining now*, *Run average*, *Hold full in about N min* and *Hold: N of M t* lines.
  - The target box on the Settings card of the Space Mining window takes several names with their own percentages, and its type-ahead works after a comma.
  - Opening Mining History once re-reads old runs in the background.
- **Local star index** (Settings → WFMT → General → Online lookups → Local star index).
  - **Download and build** downloads about 173 MB into the Flatpak's data folder and builds an index of about 110 MB (about 300 MB free is required while it builds).
    - Progress shows, and **Cancel** works.
    - The finished status shows the systems, size and date.
    - **Neutron Star** then answers from the local index (the status line states so).
    - Report the build time.
  - **Update** on a later day downloads only a small file (about 3 MB for a day) and the status line states so.
    - Pressing it again at once reports that the index is up to date.
    - Report the time an update takes.
  - Delete removes the index.
  - If the folder is not writable, the message states so.
- **Carrier Route, Rare Goods and the earlier quick-pass items** (Mining pages, Mining History, the Space and Surface Mining Books, overlays and panels): the same checks as in [TEST_PLAN.md](TEST_PLAN.md).

Report the distribution, desktop, X11 or Wayland, and native or Flatpak EDMC, with the relevant lines of EDMC's log.

### Areas the Checklist Covers

These apply to anything the passes did not reach.

**Overlay placement and cards**

- Right-hand overlay cards sit against the screen's right edge with a Flatpak EDMC, both with the Graphics folder permission granted (permission 5 in the Linux guide) and with it left out. The Overlay Placement info line states where the screen size came from.
- A long system name (about 28 characters) shows whole on the Route rows and in the Body info, System targets and Bio signals titles with EDMCModernOverlay, whose text measuring differs.
- The items in `docs/TODO.md` for:
  - per-commander overlay settings (two commanders, each with their own cards and placement)
  - Nearest place to land
  - the likely color of a species
  - tracked plant marker rings
  - the Bio radar's north mark
  - The built-in overlay is Windows only, so Linux uses EDMCModernOverlay.
- The Exobiology cards (Bio status, Biology, Bio radar, Sample popup), System targets and Body info, the Expedition Log (Start and Stop in the Expedition window, the Log tab, Start from my last sale), the drag-and-drop layout editor on Overlay Placement, panel opacity and legible text on every color scheme, and species shown as `Genus species` (the items are in section 6).
- The Route overlay, the Expedition card and survey counts, and the overlay padding and alignment (every card's text starts at the same left edge, the same distance from its border), plus the default overlay spots.
- **Section 5, Overlay:** the Colonization card still shows when the game's Market event arrives late (the overlay also watches `Market.json`).
- **Section 7f, Overlay Placement:** an exact position that is off the overlay's canvas (such as a leftover `x = 1280`) falls back to the default spot.
- **Section 7g, Overlay Appearance:** the Text size choice (Default, Larger), and boxes holding their text at each size.

**Data, windows and sources**

- With EDMC started while the game is closed, the BGS, Mining and Trade windows show a commander's saved data, and the EDMC log has no `Plugin "WFMT" failed` lines.
- Source commodities:
  - It shows `Pick up at <station>` with the largest landing pad for a Delivery mission.
  - It lists a Delivery mission whose cargo the faction did not hand over.
  - It shows the Largest pad column for market picks.
  - (See the Source commodities and Missions items in `docs/TODO.md`.)
- The Mining Book items, and Trade reading the market right after docking (the Mining Book, Neutron route and Market.json items in `docs/TODO.md`):
  - Market research
  - Share line and Paste spot
  - the stops and their rings
  - `you are here`
  - Depleted marks that stay and state how long ago
  - the Neutron route in the Expedition window
- The System targets visit history and Spansh lookup items in section 6 and `docs/TODO.md` (the journal folder is found on Linux, the first read finishes, the lookup states what it is doing).
- The Credits Ledger window (click the Credits line: it opens, fits, and the tabs fill), the Colonization History window (History button), fold sections starting folded, and Ship Builds folding.
- The items in section 6 marked "Windows-tested only": mission progress colors, the alert widths, the Missions window and pinned missions, Best picks and Source commodities, the Missions overlay card, the Upgrade planner, Megaship scans and the Ship planner's subtract option.
- Settings → General → **Help** (Report an issue, Copy diagnostics).
- The Engineering window's **Engineers** tab (places, unlock steps, the Bubble / Colonia filter) and **Ship planner** tab.
- BGS rebuilding a period that closed while EDMC was not running, and finished Colonization builds losing the "Construction Site:" prefix.
- **Materials, Engineering and the Material trader** (Operations mode) and **the Expedition planner** (Exploration mode): the checklists are in section 5.

**Settings pages**

- Every Settings page's tab row wraps and shows whole labels (Overlays has twenty-one).
- A Related settings link opens its page.
- The mode buttons can be hidden under General → Window.
- Number boxes snap back into their range.
- The Prediction review window opens from Review and its tabs are whole.
- The Route overlay's EDSM option marks a system EDSM does not know.

**Wrapping and panel width**

- **Wrapping:**
  - In Colonization, a long site, project, system or commodity name (such as `Orbital Construction Site: ...`) is shown in full and wraps at the window's width instead of ending in `...`.
  - In Expedition, Materials, Notes and the Trade watch list, lines use the whole width of the window when it is wide, and a narrow window is never widened.
- **Panel width:**
  - With Expedition (Exploration mode) and Materials (Operations mode) open, the main EDMC window does not grow wider.
  - In Expedition, **Copy on arrival** sits on its own line under **Copy Next** and **Expedition**.
  - In Engineering, **Materials**, **Blueprints** and **Engineers** sit in one row.
  - With a large font the Trade windows and the Trade History window do not widen the EDMC window either.
- **History heading and Busiest site:**
  - The Colonization History heading names the commander (`History - NAME`).
  - Busiest site shows the site's name and system rather than `Construction site <number>` once the commander has docked at it.

### Getting Set Up

1. Install the plugin: the zip from the [releases page](https://github.com/rwharpernc/wayfarers-multitool/releases/latest), or `npm run deploy` (step 4).
   - Restart EDMC.
   - The line under the mode buttons reads `Plugin: v1.5.3`.
   - Complete sections 0 and 1 first.
2. Fetch the repository and use `master` to obtain the checklist and the test suite:
   - `git fetch --all --tags`, then `git switch master`, then `git pull --rebase`.
   - Once per machine: `git config core.hooksPath .githooks`.
3. Run the unit tests: `python3 -m unittest discover -s tests`.
   - The window and panel smoke tests require a display. Without one they are skipped, so run them from a desktop session.
   - On Arch and CachyOS the host requires `pacman -S nodejs npm tk python-pillow xdotool`.
     - A current Node is required for the build.
     - `tk` is Python's Tkinter.
     - Pillow is used by the overlay and screenshot tests.
   - A Flatpak EDMC does not use the host's Python, so these packages are for the tests and the build only.
4. To test the `master` build instead of the release, run `npm run deploy` in the repository.
   - It finds EDMC's plugins folder (native or Flatpak) and copies the build there. Restart EDMC afterwards.
   - The build reports the version in `plugin/__init__.py`.
   - For a Flatpak EDMC the plugins folder is `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/plugins/Wayfarers-Multitool`.
   - If the script selects the wrong folder, set `WFMT_PLUGINS_DIR` or pass `--plugins-dir <path>`.

## 0. Setup

- [ ] `xdotool` is installed (`xdotool version` works in a terminal).
- [ ] Elite has been launched at least once through Steam, so its Proton prefix exists.
- [ ] EDMC's **Journal directory** points at `<prefix>/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous`. The prefix is usually `~/.local/share/Steam/steamapps/compatdata/359320/pfx`.
- [ ] For overlay features: EDMCModernOverlay is installed and its overlay is running.
- [ ] If EDMC is a Flatpak: `flatpak override --user --show io.edcd.EDMarketConnector` lists all five permissions from the [Linux guide](guide/linux.md) (Step 3):
  - the journals folder
  - the Bindings folder (`:ro`)
  - the Pictures folder
  - the Graphics folder (`:ro`, for the screen size)
  - `org.freedesktop.Flatpak=talk`
  - Without the last one, the overlay's sockets open (so **Check connection** passes) but its window never starts, and `xdotool` is invisible to WFMT.
- [ ] If EDMC is a Flatpak: the EDMC log has no "Host lookup of ... failed" lines from WFMT.
- [ ] **Elite Wine/Proton prefix** in Settings is empty unless a custom setup is used.
- [ ] An `overlay_client` process is running (`ps -eo args | grep overlay_client`).
- [ ] WFMT is copied into EDMC's `plugins` folder, EDMC is restarted, and the panel appears.

## 1. Basics

- [ ] Mode buttons switch, the panel collapses, and text and buttons render correctly (fonts, colors, dark theme).
- [ ] Settings → WFMT opens with every tab.
- [ ] Jump to a system: Powerplay, Exploration Value and Boxel Survey react to the journal event.
- [ ] No Python errors in the EDMC log.

## 2. Paths and Journal

- [ ] Settings → Exploration → Auto-Honk shows **no** orange journal hint when the Journal directory is correct.
- [ ] Clear the Journal directory: the hint appears, and the log has a "Linux journal folder" warning.
- [ ] Set **Elite Wine/Proton prefix** to a wrong path: Auto-Honk reports that the binds file cannot be found.
- [ ] Clear it again: the Proton prefix is auto-detected.
- [ ] If available: a second Steam library folder, or Flatpak Steam, is detected.

## 3. Auto-Honk

- [ ] Settings → Exploration → Auto-Honk → **Rescan** shows "Will press [key]" for the fire button.
- [ ] Elite running and focused: **Test Honk Now** reports "sent" and the scanner fires.
- [ ] The honk key stays down for the whole **hold time** (set 8 to 10 seconds): the scan completes instead of stopping after about a second.
- [ ] Elite not focused, **Focus game window first** on: Elite comes forward and the honk fires.
- [ ] Elite not running: it reports "Elite Dangerous window not found".
- [ ] `xdotool` uninstalled: it reports that it is not installed, with the install hint.
- [ ] A real jump with Auto-Honk enabled honks once, and not again on a revisit.
- [ ] Test a fire button bound to a letter, an F-key, a numpad key and a modifier where available.

## 4. Screenshots

- [ ] Take an in-game screenshot: it converts to PNG and appears in the panel.
- [ ] The default source folder is the prefix's `Pictures/Frontier Developments/Elite Dangerous`.
- [ ] The cropped preview matches the panel that was open (this requires `Status.json`).
- [ ] **Open Folder** opens the file manager.
- [ ] The timer icon and auto-capture timer take a screenshot in-game.
- [ ] A folder that cannot be written shows a plain permission message, with no Windows text.

## 5. Overlay (Requires EDMCModernOverlay)

- [ ] Landing Assist, Interdiction Warning (**Test Warning**), Discovery (**Test Discovery**) and Notable Bodies (**Test Notable**, after ticking Enable) all draw over the game.
- [ ] Surface Compass (Exploration mode, **Compass** section; Settings → Overlays → Surface Compass):
  - **Test Compass** draws an arrow and a name on the left.
  - On a planet surface the section shows the nearest hotspot with a distance.
  - **Mark** makes a mark.
  - **Target** steps through the marks here.
  - **Marks** opens the window (edit, **Here**, Delete twice).
  - With the compass enabled, the arrow follows the target as the commander moves and turns, and clears on lift-off.
  - The Mining settings tab has no waypoint tick.
- [ ] Materials (Operations mode, **Engineering** section, the first in Operations):
  - After login the row shows the pieces of each type (`Materials held: ...`) and `Engineers: N of 38 unlocked` once the game has listed the engineers. The section title reads Engineering, folded or open.
  - Collecting or discarding a material is followed by "Last change: ...".
  - A material at its limit is named.
  - **Materials** opens the window. **Blueprints** and **Engineers** open the Engineering window on its Blueprints and Engineers tabs.
  - Search, Type, Grade and **Only what is at the limit** narrow the table, and headings sort.
  - The window keeps its size and place.
  - After an EDMC restart mid-session the counts are correct.
- [ ] Material trader (Materials window, **Find a trader**):
  - The window opens with the current system filled in and the type that has the most at the limit.
  - **Find** lists traders nearest first (check one against the galaxy map).
  - The Type, Within and Pad drop-downs change the search.
  - **Here** refills the system, and a typed system works.
  - Double-click copies the system name.
  - With no network the status reads that Spansh could not be reached, and **Find** works again afterwards.
- [ ] Engineering (Operations, **Blueprints** on the Engineering section):
  - The window opens with **Blueprints** and **Wishlist** tabs.
  - Search (it waits a moment after typing) and the Module drop-down narrow the list.
  - Selecting a row shows its ingredients, what is held and where each is found.
  - **Add to wishlist** and a double-click add.
  - The Wishlist tab shows each entry's crafts, whether it can be made and the shopping list.
  - **Set crafts**, **Remove** and **Clear list** ask twice.
  - The Engineering section shows the `Wishlist:` line and stays narrow.
  - The window keeps its size and place.
  - The **Engineers** tab:
    - It lists engineers with the commander's standing (after a login), unlocked ones first.
    - **Show their blueprints** switches to the Blueprints tab searching for them.
    - **Put their unlock on the wishlist** adds it.
    - The wishlist's **Who can do it** column names an unlocked engineer or "No engineer unlocked yet".
- [ ] System-name suggestions (Settings → Window): in the Expedition window's System box, type two letters of a system the commander has been in.
  - A list appears under the box.
  - **Down** and **Enter** take an entry. **Escape** closes the list. **Enter** with nothing highlighted adds the stop.
  - The list appears in front of the window on the desktop and Wayland compositor in use, and goes away when the box loses focus.
  - Tick *Suggest system names from Spansh while typing* and type `outot`: after a pause, systems from Spansh appear.
- [ ] Expedition (Exploration mode, **Expedition** section):
  - **Expedition** opens the window.
  - **New** makes an expedition.
  - **Add stop** (and **Here**) add stops.
  - **From plotted route** (after plotting a route in the game) and **Import CSV** add many.
  - **Road to Riches** and **Exomastery** (Spansh): press **Plot**, wait, and compare the new expedition's stops, notes and order with Spansh's own page.
  - **Neutron route** opens the Route Planner.
  - **Start** (in the Expedition window), then jump to a stop: the section ticks it, counts the jump and shows the next stop with its distance.
  - **Copy Next** and **Copy on arrival** put the next stop's name on the clipboard (confirm that it pastes into the galaxy map's search box).
  - **Locate and reorder (EDSM)** orders the unvisited stops.
  - **Export CSV** saves a file and **Import CSV** reads it back.
  - **Reset** and **Delete** ask twice.
  - The section stays narrow with a long name, and the window keeps its size and place.
- [ ] Notes (Exploration mode, **Notes** section):
  - The quick-add box saves a line against the current system.
  - **Notes** opens the window.
  - The editor's text box accepts typing and paste.
  - **Here** fills the system and body.
  - **Delete** asks twice.
  - The window keeps its size and place after closing and reopening.
- [ ] Trade Watch list (Trade mode, **Watch list** row):
  - **Watch** opens the window.
  - Add a commodity by typing (the suggestion list appears and a click or Enter selects it) and **Add**.
  - Open a station's commodity market in the game. The commodity gets a price, with the station under it when selected.
  - **Remove** asks twice.
  - With Trade lookups on, **Refresh** fills in Spansh prices and states so. With them off it states that they must be turned on.
  - The row stays narrow with a long system name.
  - Restarting EDMC keeps the list and the seen prices.
- [ ] Route overlay (Settings → Overlays → Route):
  - **Test Card** draws a card at the top left that reads `You are navigating to:`, a destination, a jump count, a rule, a list of system names, a rule and the light years left, every line starting at the same left edge.
  - Plot a real route in the game. The list loses a system at each jump and clears at the end.
- [ ] Exobiology cards (Settings → Overlays → Exobiology):
  - **Test Cards** draws all four as plain panels (no colored bar or outline) with the three circles beside the species name inside the card.
  - Sampling on a mapped body fills the circles, moves the progress bar a third per sample, updates the distance and the radar, and shows the popup.
  - Scanning a plant with the Composition Scanner and walking off shows a ring, a pointer line and `Tracking <species>`, with the little pointers turning as the commander turns.
  - Leaving the planet clears the cards.
  - First footfall is marked on a body nobody has landed on.
- [ ] Hide overlays:
  - Click the `Overlays shown (click to hide)` line in the WFMT panel. Every card disappears at once, and the line reads `hidden`.
  - Click again: the cards return where they were, including Colonization.
  - Settings → Overlays → Hide overlays has the **Hide / show now** button, and it works. The shortcut keys are disabled under Settings → WFMT → General → Shortcuts.
- [ ] Duplicate overlay window warning:
  - With one overlay window running, Overlay Connection → Check connection states only that it is connected.
  - Start a second copy of the overlay. A line naming two windows is added.
  - Copy diagnostics shows `Overlay windows running: N` (read from `/proc` on Linux).
- [ ] Nearest place to land (Exploration → Nearest place to land → Find):
  - The window opens and fits.
  - The box for the lookup must be ticked before Find works.
  - After a jump it shows the system, coordinates and the ship's pad.
  - Find lists stations and carriers.
  - Double-click copies a system name (requires a clipboard).
  - The position is read from the journals after a restart.
- [ ] Overlay font (Settings → Overlays → Appearance):
  - The section lists the fonts in EDMCModernOverlay's `fonts` folder (native or Flatpak).
  - Choosing one and pressing OK rewrites `preferred_fonts.txt` (with a `.bak`).
  - **Add font file...** copies a `.ttf` and selects it.
  - **Open fonts folder** opens the folder.
  - After a restart the overlay text shows lower case.
- [ ] Expedition Log (Expedition window, Log tab; Settings → Overlays → Expedition Log):
  - Start, a few jumps and scans, Stop (the buttons are in the Expedition window; the panel's Expedition section has none).
  - The Log tab shows the expedition, its facts and editor.
  - Rescan, Reset and Delete (asking twice) work.
  - Export CSV writes a file.
  - The overlay card shows the running totals.
- [ ] Body info as symbols and formulas, the Biology card's ranges and percentages, and Settings → Overlays → Appearance → Panel opacity (a lower value makes every card's background fainter; the text stays solid).
- [ ] Discord sharing: **Copy for Discord** in the BGS Report (**Discord** menu) and the Powerplay Sessions window puts formatted text on the clipboard (the clipboard works under the Wayland and Flatpak setup). **Settings → WFMT → Discord → Test** and **Post to Discord** (with one destination and with two) with a webhook in a private channel work from a Flatpak EDMC (outbound HTTPS to `discord.com`).
- [ ] Expedition Log's **Start from my last** buttons (**sale**, **Discovery Data sale**, **Exobiology Data sale**): the expedition starts just after that sale, is filled in from the journals, then counts live.
- [ ] Layout editor (Settings → Overlays → Overlay Placement):
  - The picture of the screen shows with a box per display.
  - Dragging a box fills in the table.
  - A box dropped near an edge snaps flush (offset 0).
  - **Picture size** changes the picture and is remembered.
  - A card placed at the bottom or right with offset 0 sits on the screen edge.
- [ ] A relog, or a return to a system after visiting others, keeps the System targets and Body info cards' bodies.
  - Each commander's surveys are saved in `system_surveys.json`, and a system visited before is rebuilt from the journals.
  - The card's summary line and Done list show where the commander left off.
- [ ] System targets history and Spansh lookup:
  - After a restart the card shows `Reading your journals for a visit history (n%)` and then `First visit here` or `Been here N times before · last <date>`. The journal folder is the one EDMC uses on Linux; confirm that it is found.
  - With the Spansh option ticked, a jump into a system others have surveyed shows `Looking up data (Spansh)...` and then a Known section. A system Spansh does not have states so.
  - `system_history.json` appears beside the plugin.
- [ ] System targets and Body info cards (Settings → Overlays):
  - **Test Card** on each draws a card with every line at the same left edge.
  - After scanning bodies in a system, the targets card lists those worth mapping and any with life, and they leave the list when mapped or analyzed.
  - Targeting a body in the system map shows its Body info card.
  - Restarting EDMC mid-system brings the list back.
- [ ] Expedition survey tracking (Exploration → Expedition): start an expedition with two or three stops. Arriving in a stop updates its totals in the Expedition row.
- [ ] Flight Alerts (Settings → Overlays → Flight Alerts):
  - **Test Card** draws a card on the right, below where the Inventory display sits.
  - With a carrier jump scheduled, the countdown ticks every second and turns red in the last minute.
  - A plotted neutron star with the tank at or under 50% shows the unscoopable-star line.
  - The sound box is available only when `canberra-gtk-play` or `paplay` is installed, and a sound plays when an alert starts.
- [ ] Notable Bodies: scan a terraformable or an Earth-like, water or ammonia world. A violet banner appears. The same body does not alert twice.
- [ ] Landing Assist when the overlay starts late: request docking right after starting EDMC and the game, before the overlay client has finished starting.
  - The card and pad diagram appear once the overlay is up (within about a minute), without another docking event.
  - Switching between a starport and a fleet carrier removes the old diagram immediately.
- [ ] Card backgrounds are visible, not only the text.
- [ ] The overlay works in borderless mode. Record the behavior in fullscreen.

## 6. Other Features

- [ ] The Inventory pickup **sound** plays (Operations → Inventory settings).
- [ ] Codex **My Codex** opens, and its **Backfill Journals** action finds the journals.
- [ ] Codex details window: the Entry and Times found headings sort both ways, the **Not found** tab fills in (requires network the first time), and double-clicking an entry opens its Canonn search in the browser.
- [ ] Colony mode → **Dashboard** (colonization sites): after docking at a construction depot, the site appears with its outstanding commodities, In Cargo matches the hold, and **Copy Shopping List** pastes elsewhere.
- [ ] Mining: journal backfill works, and in an SRV the surface bearing arrow and coverage map work.
- [ ] Copy buttons (Powerplay, BGS, Boxel **Random**): pasting into another application works. **Random** names are real systems that plot on the galaxy map, and a second press nearby is quicker.
- [ ] Network lookups (EDSM, Spansh, Canonn, GEC) return results.
- [ ] Exploration **Neutron Star** and **White Dwarf** buttons: after a jump, each shows a system and distance and copies the name to the clipboard (paste it elsewhere to confirm).
- [ ] Hovering a button (for example **Auto-Honk**, **Random**, **Report**, **Powerplay**) shows its name and what it does in a tooltip that disappears when the pointer moves away. The GEC, Canonn and Codex sections start minimized.
- [ ] Powerplay → **Rares** (rares) opens the Rare Goods Finder: after a jump or login it lists the nearest rare goods, the Controlling Power column fills in from Spansh, and double-click opens Inara in the browser.
- [ ] Restart EDMC: per-commander data (BGS, Boxel, Codex) is still there.
- [ ] **Mining History**: **Dashboard** in Mine mode reads the journals (confirm that it finds the journal folder), fills the Overview and the three tables, and a run made with EDMC closed appears after a restart.
- [ ] **Random**: press **Random** twice near a procedurally named system.
  - The name plots on the galaxy map.
  - The status line gives a distance and states whether EDSM confirmed it.
  - The second press nearby is much quicker.
  - Settings -> Exploration -> Boxel Survey -> **Systems to request from Spansh** takes a number from 10 to 100.
- [ ] **Region Sweep, skip systems EDSM knows**: tick **Skip systems already visited by anyone (EDSM)** (Settings -> Exploration -> Region Sweep), add a cube and press **Next >**. The status line reads `Checking EDSM...` and then how many known systems were skipped (or that the check was unavailable, with the candidate shown anyway).
- [ ] **POI Reference**: one section with **Find POI** and **Update POI**. Find POI shows a GEC line and a Canonn line, and a paste into the galaxy map gives the nearer system.
- [ ] **My Codex**: the Codex Completionist section has one button. The window opens on **Overview**. **Not found** has a **Where to look** column. **Backfill Journals** reads the journals.
- [ ] **Panel order and width**: in every mode the sections are alphabetical, and switching modes or opening the Route Planner and Dashboard never widens EDMC's window (if it does, report the "The WFMT panel widened" line from EDMC's log).
- [ ] **Overlay exit**: when a card goes away, its panel goes with its text, in one step (no empty shell left for a few seconds).
  - Switch the Dashboard's Exploration overlays off and on: the cards go together.
  - They return once Elite is in front (EDMCModernOverlay shows them only while Elite is the window in front).
- [ ] **Route Planner**: **Plot** in the Route Planner section of the Exploration panel (unfold it first) opens the window with the ship read from the journal (no jump range to type).
  - Generate route returns a route (every jump listed).
  - **Copy next system** and the **Copy the next system to the clipboard automatically** tickbox put the name on the clipboard (confirm that a paste works in the galaxy map under Proton).
  - Arriving at a system turns its row green and moves the panel's next-jump line on.
  - With the Route overlay on, the route shows on its card in place of the game's route.
  - The window's status line states that the route was sent to the Route overlay and which system is on the clipboard, and repeats this at every system reached.
  - **Start expedition** makes an expedition from the route, starts it and starts its Expedition Log run.
  - **Review expedition** opens the Expedition window with that expedition selected.
  - The Expedition window's **Neutron route** button opens this window.
- [ ] **Route overlay**: the card reads *You are navigating to:*, the destination, *You will be there in N jumps.*, a rule, the systems still to visit (no numbers), a rule, and *N LY left to jump.*
  - Each system shows its star in green (scoopable), yellow (not scoopable), blue (neutron star) or red (white dwarf).
  - At the last system the card states that the route has ended and is being reset for ten seconds, then closes.
- [ ] **Folding sections**: the Dashboard and Route Planner sections start folded and open on a click of their title.
  - The Dashboard section holds the Exploration Value lines under its Dashboard button.
  - POI Reference has **Update POI** and a **Copy System** button and a details link under both the Canonn and the GEC result.
- [ ] **Exploration Dashboard**: **Dashboard** on the Exploration panel opens the window (confirm that it opens whole on the screen and the tabs wrap).
  - It follows the system after a honk and scans, switches to Surface on landing and back to Orbit on lift-off.
  - The header buttons **Exploration overlays** and **Exobiology overlays** hide and show those cards with EDMCModernOverlay (a hidden card clears at once and returns when shown) without changing Settings.
- [ ] Settings -> WFMT -> General -> **Backup** -> **Back up my data** (Windows-tested only):
  - The folder dialog opens.
  - A `WFMT-data-<date>-<time>.zip` is written to the selected folder and unzips to the JSON files plus `backup-info.json`.
  - With a Flatpak EDMC, select a folder it can write to (or grant one with `flatpak override`). A folder it cannot write to produces a message in the tab, not a crash.
  - **Restore my data...** with that zip: it shows the file count, asks, states that EDMC must be restarted, and after the restart the data is back (and `backups/pre-restore-<date>.zip` holds what it replaced).
  - **Cancel the waiting restore** removes it.
  - **Back up automatically** with a folder and 1 day: restart EDMC, wait a minute, and a `WFMT-data-auto-....zip` appears.
- [ ] Settings -> WFMT -> General -> **Help** (Windows-tested only):
  - **Report an issue** opens the GitHub bug report in the browser (confirm that `xdg-open` works from EDMC, native and Flatpak).
  - Its Environment box reads like `Ubuntu 24.04, wayland` (distribution, X11 or Wayland, `Flatpak` when it is one).
  - **Copy diagnostics** shows *Copied*, pasting gives the version lines and recent WFMT log lines, and the commander name reads `<commander>`.
  - Report which log path the Flatpak case used.
- [ ] Engineering window → **Engineers** tab (Windows-tested only):
  - The table has a **Where** column.
  - Selecting an engineer shows their details under the table (see TEST_PLAN.md section 10).
  - Selecting Baltanos shows Deriso and "On-foot engineer". Terra Velasquez shows the "reported bugged" note.
  - The **Show** box offers Both / Bubble / Colonia. Colonia lists 8 engineers (`8 of 38 engineers`), Bubble 30, and the choice survives closing and reopening the window.
  - The table stays inside the window with the Where column, with no horizontal scroll.
  - The unlock path, the **Next step** column, the on-foot hand-in steps and the requirement notes are checked in [TEST_PLAN.md](TEST_PLAN.md) section 10 (not run on Linux).
- [ ] **BGS with EDMC closed over a tick** (Windows-tested only): note the BGS archive, close EDMC, do a few BGS actions (missions, bounties) in the game, wait for a tick to pass, start EDMC. The archived tick that just closed includes those actions, and EDMC's log has `BGS: rebuilt the closed period ... from the journals`.
- [ ] **Finished colonization build name**: a completed site in the Colonization sites window reads `Example Station`, not `Orbital Construction Site: Example Station`.
- [ ] **Ship planner** (Engineering window, Windows-tested only): export a build from EDSY or Coriolis as SLEF and **Paste from clipboard** (confirm that the clipboard paste works on the desktop, X11 and Wayland).
  - The table lists each engineered module, and the summary line shows blueprints and crafts.
  - **Add plan to wishlist** puts them on the Wishlist tab (a pre-engineered module and an unknown item show their reason).
  - Set **Rolls per grade** to 2 and add again: the crafts double.
  - Tick **Subtract what my current ship already has** with a build for the ship flown: what the ship holds is left out.
  - Nothing goes online.
- [ ] **Megaship scans** (Powerplay, Windows-tested only): in a Powerplay system, drop out of supercruise at a megaship and scan its datalink.
  - The Powerplay panel gains `Cycle N megaships: 1 (N merits)` and **Report → Megaships** lists it with its name and system.
  - Scanning it again changes nothing.
  - A scan at a station or a settlement adds nothing.
  - After restarting EDMC the list is still there.
  - Requires the Journal directory set on Linux.
- [ ] **Upgrade planner** (Engineering window, Windows-tested only):
  - Select the Karma AR-50 from class 1 to 5: four steps, 12,500,000 credits, and **Add to wishlist** puts four entries on the Wishlist tab.
  - Press **Read my gear**: the suits and weapons are listed with their class (requires the Journal directory set on Linux). Selecting one fills in its item, class and fitted modifications.
  - Select the TK Zenith: the credits read "not recorded".
  - A modification not offered for the item is filtered out, and four at most are accepted.
- [ ] **Alert widths** (Windows-tested only; requires EDMCModernOverlay): **Test Notable** and a Discovery alert with a long capitalized name fit inside their cards at Default and Larger text. On the Missions overlay card a long station name drops to a line under its title.
- [ ] **Mission progress colors** (Windows-tested only): the Missions window's Progress column shows a bar and `N/total held` for a source-and-return mission, and rows and overlay lines change color as the hold fills.
- [ ] **Missions window and pinned missions** (Windows-tested only):
  - The **Missions window** button at the bottom of the Missions panel opens the window.
  - The Active and By place tabs fill and the times count down.
  - Select a row and **Pin / Unpin** puts a ★ on it and (with the Missions overlay on) a PINNED section on the card.
  - The text beside the arrows is bold and legible.
- [ ] **Best picks and Source commodities** (Windows-tested only; requires Trade lookups on):
  - Trade → Market, type a commodity: **Best picks** shows four labeled stations.
  - Missions → **Find sources** (bottom of the panel) fills the window as each commodity finishes.
  - **Copy system** puts the system on the clipboard, and **Cancel** stops the search.
- [ ] **Missions overlay card** (Windows-tested only; requires EDMCModernOverlay): Settings → Overlays → Missions → **Test Card** draws a sample in the bottom-right corner.
  - With a few real missions and the card enabled, it lists those for the current system under HERE and those for the targeted system under NEXT, and times count down.
  - It sits where Overlay Placement states and does not widen as lines change.

## 6b. Fixed in the Platform Audit

- [ ] Settings → Exploration → Auto-Honk, Operations → Screenshots and Operations → Inventory each show a **Works on:** line, green when it can work here and orange (with the reason) when it cannot. Test with and without `xdotool`.
- [ ] Take a normal screenshot and an Alt+F10 hi-res one. Both are found, converted and named, and the hi-res one is treated as hi-res (the journal path is Windows-style, `\ED_Pictures\...`).
- [ ] Open every modal dialog without an error and without it staying behind the main window: Mining → Add/Edit Hotspot, Find Hotspots, Find Best Price, Check Ring Reserve, Import/Export Hotspots, and Operations → Add/Edit Ship Build. Each stays on top and blocks the window behind it.

## 6c. Game Mode and Credits Lines (Under the Mode Buttons)

- [ ] Before logging in, the first line reads "Game mode: waiting for login…" and the second "Credits this session: waiting for your balance…".
- [ ] After loading into the game: "You are in Solo mode." (or Open, or Private Group with its name) and "Credits this session: no change yet". Both lines (and the Plugin version line above them) stay visible on every mode button.
- [ ] Switch through every mode, including Exploration and Trade: the whole block under the mode buttons stays visible.
- [ ] After earning a Powerplay merit, a **Merits this session: +N (+N merits/hr)** line appears under the credits line, on every mode except Powerplay, where the page's own lines show it. The rate appears after a few minutes. The line is absent before the first merit.
- [ ] Earn or spend some credits: the second line changes to "+N cr earned" or "-N cr lost", and an hourly rate appears after a few minutes.
- [ ] Log out to the main menu and back in: the credits total continues (same session).
  - Restart EDMC while the game is running: the mode line and the credits total return.
  - Quit the game: the mode line returns to "waiting for login".
- [ ] `session_credits.json` appears in the WFMT plugin folder, and a plugin update leaves it alone.

## 6d. Trade Mode

Windows was checked as Trade was built. The boxes below are unticked so that the list can be run again. First: Settings → WFMT → Trade, tick **Enable Spansh trade lookups**.

- [ ] The **Trade** button appears with the others, and the Trade panel shows its summary over the **Session**, **Routes**, **Market** and **History** buttons. Each of the first three opens its own window, and pressing it again brings that window forward.
- [ ] **Session**: after docking, the ship and its pad size show. The hold line shows used, capacity and free tons. Buy and sell something: the profit lines appear. Refuel and repair: a **Net profit** headline appears with Fuel and Repairs lines under it. **Reset** clears it.
- [ ] Trade History: do some trading, press **Save session** (the message at the top states that it saved), then **History**.
  - The window opens like the BGS and Powerplay ones, with the session in the drop-down.
  - Visit every tab: the tables fit the window with no column cut off at the right, and the numbers are plausible.
  - **Route** lists the stations in the order flown.
  - **Trades** opens on the newest 200, and **Show older trades** adds 200 older ones.
  - Press **Save session** again after another trade: the entry updates (no duplicate).
  - **Copy summary** pastes into another application.
  - **Export log (CSV)** opens a file dialog and writes the file.
  - **Delete session** asks first.
  - **Reset** with unsaved trades asks whether to save first.
- [ ] A session spans play sessions: trade, log out of the game and back in (a new journal file), restart EDMC, then trade some more.
  - The Session window keeps one running tally through all of it (nothing starts afresh until **Reset** is pressed), and the numbers do not double.
  - After **Save session** the **Route** tab lists the stations from every part.
  - Also play a short stretch with EDMC closed, then start EDMC: that stretch is added the next time EDMC sees the commander.
  - With two commanders, switching to the other and back leaves each one's tally as it was.
- [ ] Session window: the sections read "In your ship" (Ship hold, and the cargo with an "In hold" column; "Hold space" above it only with limpets, mission or stolen cargo) and, with a carrier, "Carrier cargo".
  - There is no unsold-stock list and no Clear stock button.
  - Buy cargo, then save the session: Trade History's **Stock & carrier** tab shows it under "Bought, not yet sold (journal estimate...)".
- [ ] Two computers: copy the other computer's newer journal files into this one's journal folder while EDMC is running.
  - Within a minute EDMC's log reads "Trade read N new or changed journal file(s)".
  - The trades, stock and carrier figure from those files appear (nothing doubles if the same files are copied again).
  - Press **Rebuild** in the Session window, enter the date and time the session began (UTC), and compare the totals with the other computer.
  - A carrier figure with a `~` in front is an estimate: opening Carrier Management removes it.
- [ ] Carriers (only with a carrier): open Carrier Management once.
  - "Carrier cargo" (used / capacity, with the free tons) appears (separate from the "Ship hold" line).
  - Transfer cargo to the carrier: the figure follows.
  - Restart EDMC: the figure returns without opening Carrier Management again (this reads the journal folder, so it also checks the Proton journal path).
- [ ] Settings → Trade lists the commanders with a carrier choice each. Choosing **None** hides the carrier.
- [ ] **Market**: click the Commodity box.
  - A suggestion list appears **under the box and does not take the keyboard** (this is a borderless window, so confirm that it stacks above EDMC under the window manager in use).
  - Typing narrows it.
  - Up/Down/Enter/Esc work.
  - Clicking a name fills the box.
- [ ] Layout: the Session, Routes and Market windows show orange section headings with a rule between them where a window has more than one list (a window with a single list has no heading above it), values on the right, and aligned number columns.
  - Long station names wrap instead of being cut off.
  - Nothing is clipped on the right edge or makes the EDMC window wider.
  - The buttons and (on Market) the Commodity box and **Sell** / **Buy** are **above** the results.
- [ ] Routes window (or Market): untick **Ground facilities** and **Fleet carriers**. The results show orbital stations only, and a search makes one request instead of two.
- [ ] The **Sell** / **Buy** buttons under the Commodity box: the chosen one is lit, switching clears the results, and the results heading reads "Selling" or "Buying". All the window's buttons show their full labels (**Near me**, **Galaxy**, **Price finder**) with nothing cut off.
- [ ] **Near me** and **Galaxy** each return results for a common commodity (test Gold and Liquid oxygen).
  - Each station reads **orbital** or **ground** and its type.
  - A fleet carrier appears in its own section, not mixed with stations.
  - Stations without a pad for the ship are missing.
- [ ] **Routes**: **Find routes** shows "Asking Spansh..." with a counting timer, and a route within a couple of minutes. **Cancel** stops the search. **Copy next system** puts the system name on the clipboard.
- [ ] **Hops** button cycles 2 up to 10.
  - **Round trip** (docked at a normal station, not a carrier) answers in about 20 seconds with up to three pairs, each showing what to carry out and back. Both legs are loaded.
  - A route shows an estimated profit per hour and supply/demand per hop.
- [ ] Routes window filters: set **Ignore prices older than (hours)** to a small number and tick **Systems that need a permit**. **Find routes** and **Round trip** still answer (an old-price filter can leave fewer results).
- [ ] No Python errors in the EDMC log, and the EDMC window did not become wider when Trade was opened.

## 7. BGS

- [ ] The BGS panel's gray line shows "Last tick: ..." within a few seconds (the network call works).
- [ ] With the Journal directory set, the log has "BGS journal replay done for [CMDR]" and the totals cover the whole tick. With it cleared, the log states that the replay was skipped and why.
- [ ] **Report** (view BGS report) opens. The tick drop-down, the tabs (full system names, wrapping onto a second row when there are many), **Pin**, **× Close tab** and the footer key all render, with no missing glyphs.
- [ ] **Show a system**: typing narrows the list while typing continues (the list does not take the keyboard), the arrow shows every system, Up/Down/Enter/Esc work, and clicking a name adds its tab.
- [ ] Pins and closed tabs survive restarting EDMC.

## 7b. Catching Up After EDMC Was Closed (Windows-Tested Only)

The code is platform-neutral Python reading the journal folder, and has been tried only on Windows.

- The Linux risks are the Journal directory (section 0), file modified times on the Proton prefix, and large journal folders.
- To test, play a short session with EDMC **closed** (or close it mid-session), then start EDMC and check each item:

- [ ] **Missions**: accept a mission, close EDMC, start it mid-game. The mission shows without logging in again.
  - Hand a mission in with EDMC closed: it disappears after the restart.
  - (An expired mission with no journal entry can remain until the next login.)
- [ ] **Colonization**: deliver cargo to a depot with EDMC closed, then start EDMC. The site's figures include the delivery once. Restart EDMC again: nothing changes (no double count).
- [ ] **Codex**: find a Codex entry with EDMC closed, start EDMC. The summary line increases by one.
- [ ] **Boxel Survey**: jump to a few systems with EDMC closed. After a restart the visited count (Settings → Boxel Survey) includes them.
- [ ] **Trade**: the route start (Routes window) is the last real station docked at, also after a restart and after switching commander. Carrier tritium, location and orders appear under the carrier lines for a commander with a carrier.
- [ ] **Inventory**: restart EDMC while on foot or with items in the ship locker. The bars fill without a login.
- [ ] **Exploration Value**: after a restart mid-system, "System bodies" shows scanned of total, and "Last data sale" shows the last sale of the session.
- [ ] Start-up is not noticeably slower, and the EDMC log has no Python errors from `colonization_catchup`, `journal_files`, `visited_systems`, `codex_backfill` or `journal_scan`.

## 7c. Per-Commander Data (Windows-Tested Only)

No data is shared between commanders.

- Two commanders (or one commander and a second journal) are required, and on Linux the Journal directory set (section 0).
- The code uses only JSON keys, UTF-8 files and `os.replace`. The Linux risks are the journal folder and the order given by file modified times.

- [ ] **Mining**: save a hotspot as commander A. Log in as B: the Mining Book shows none of A's. Save one as B, log back in as A: only A's appear. The coverage map follows the same rule.
- [ ] **Mining Book**:
  - **Market research** (after ticking *Enable Spansh best price finder*) lists buyers for a system with saved hotspots.
  - **Share line** on a positioned hotspot and **Paste spot** (refused for a spot within 100 m of one saved).
  - **Stops** lines and dashed rings on the map, and `you are here` with the Rhino within 175 m of a deposit.
  - A Depleted mark stays and the card states how long ago (set the refill time on the Surface Mining window's Settings card to see it come off).
  - Nothing here is OS-specific. Confirm that the Book fits and the text is legible.
- [ ] **Codex**: log in as each commander in turn. The details window subtitle names whose tally it is, and the counts differ. On the first start, each commander's tally is built once from their own journals (the panel states so while it reads).
- [ ] **Powerplay**: the Sessions window's History tab and its total show only the commander being played.
- [ ] **Boxel Survey**: the "Surveyed: N systems" line and the exported CSV change with the commander.
- [ ] **Trade**: switching commander clears the previous one's ship, hold and route results from the Session window. The History window opens on the active commander.
- [ ] A commander name in another case (the journal can write `EXAMPLECMDR` for `Examplecmdr`) is the same commander.
- [ ] Nothing under the plugin folder is named after a commander except the `mining_sessions/` archive files.

## 7d. Colonization FC Column, Shopping-List Overlay, Start-Up Commander (Linux-Tested Only: Check on Windows)

Written and tried on Linux (Flatpak EDMC, Proton game, EDMCModernOverlay). The code is platform-neutral Python and has not been run on Windows. Requires a commander with a fleet carrier and a registered construction site.

- [ ] **FC column**: the Colonization Sites window shows an FC column for a commander with a fleet carrier (and not for one without), and it follows a transfer made at the carrier. Restarting EDMC keeps the figures and never counts a transfer twice. A commander set to None in the Trade settings gets no FC column.
- [ ] **Window follows the commander**: with the window open, log in as another commander. Its sites change.
- [ ] **Start-up commander**: start EDMC with the game closed.
  - The Operations panels (Colonization, Codex, Ship Builds, Trade) show the last commander instead of "waiting for commander login".
  - The EDMC log has "No game running at start-up; restored commander ..." (about four seconds after start).
  - Then log in as another commander: everything switches.
- [ ] **Overlay card** (Settings → Overlays → Colonization: tick the overlay option; **Test Overlay** draws a sample): the table shows Commodity, Required, Acquire, FC and Cargo, with a tick when the hold covers a row, and a remaining/trips footer.
- [ ] The card appears:
  - in a commodity market at a station
  - at the commander's own carrier in the station-services screens (the game writes no `Market` event for a carrier's market)
  - with the right-hand cockpit panel open when docked at the carrier (the cargo transfer)
  - in Carrier Management
  - docked at a construction site
  - It goes when the commander leaves, and the **Always show the shopping list** tick (Settings → Overlays → Colonization) forces it on and off.
  - The EDMC debug log lines "Colonization overlay ..." state what was decided and why.
- [ ] Rows left at the default list every commodity not yet covered. The card fits on screen from the default position (20, 300).
- [ ] **List (overlay card):** with **To buy** (the default) a commodity the hold plus the carrier cover is left out and the footer still counts it. **All** brings the covered rows back. **To haul** lists only the covered rows not yet aboard in full (put everything on the carrier and confirm that the card still lists them, and that a row drops off once its whole need is in the hold).
- [ ] **The hold follows a purchase:** buy a tracked commodity at a market. The In Cargo figures (Sites window, Colony page and card) change within a couple of seconds. WFMT reads `Cargo.json` beside the journals, so confirm that the journal folder is found on Linux/Proton. If the file cannot be read, EDMC's cargo state is used.
- [ ] Windows paths: `Status.json` reports the same `GuiFocus` values (5 in the services screens, 1 for the right-hand panel).

## 7e. Colonization Sites Window: Sites List, Totals, Where to Buy (Windows-Tested Only: Check on Linux)

Written and tried on Windows. The code is platform-neutral Python and Tk, and the window layout has been seen only on Windows. Requires a commander with at least one registered construction site and an internet connection.

- [ ] The window opens at about 1300 x 780 with the sites on the left and the detail on the right. Nothing is clipped at its minimum size (1300 x 640), and the commodity table has the whole height of the right-hand side.
- [ ] Selecting a site shows its progress bar, the six totals, and its commodities. The Filter box, the **Show** dropdown (All, To buy, To haul) and the column headings (click, click again to reverse) all work.
- [ ] **Buy Trips and Haul Trips** (requires a fleet carrier with stock stored on it): a commodity fully on the carrier shows Buy Trips 0 and a Haul Trips above 0. The totals show **t on your carrier**, **trips to buy** and **trips to haul**.
- [ ] **Row colors**: a commodity row turns green when the hold plus the FC column covers the site's remaining need (exactly equal is green), orange when together they are more than needed, and keeps the normal look while short. The tint stays visible, only lightened, when the row is hovered or selected.
- [ ] **Where to buy** (its own window): select a commodity row, press **Where to Buy** in the header, then **Find nearest**. The window opens with the site's system filled in, results appear closest first, the button is disabled while it searches, and the window stays responsive. Selecting another row updates the open window's heading. Closing the Sites window closes it. Its size and position are remembered.
- [ ] **Landing pad**: the default is **Large, then Medium**. Any size lists stations whose largest pad is Medium or Small. Large only lists none of those. For a commodity that no Large-pad station in range sells, Large, then Medium lists Medium-pad stations and the note states so.
- [ ] **Exclude fleet carriers** (on by default, so carriers are left out): unticked, a **Fleet carriers** group follows the stations. Ticked, none is listed.
- [ ] **Your own system first**: **Find nearest** for a commodity that a station in the current system sells lists only that system's stations, and the note reads `Your own system was searched first.` For a commodity nothing there sells, the search goes outside, closest first. A seller at home that the exclusions would hide (for example **Only stations with a shipyard**) does not stop the search going outside. **Find all** does the same per commodity.
- [ ] **Presets**: the **Preset** list opens on **Large, then Medium (default)**. Choosing another sets the pad, radius and ticks. Changing one by hand reads **Custom**. After a search, a change of preset, pad, within, sort or carriers shows `Options changed: press Find nearest or Find all to search again.` until the next search.
- [ ] **Only stations with enough stock**, **Only stations with a shipyard** and **Arrival within** (all off by default): after a search each one removes the stations that do not qualify from the lists and the route at once. The commodity heading reads **left out by the filters** when none are left, and the note counts what was left out. The window is laid out cleanly at its minimum size.
- [ ] **Exclude surface ports** (off by default): ticked, planetary stations disappear from the lists and the route at once. A commodity sold only at surface ports (none at an orbital port in range) shows a collapsed **IMPORTANT: Surface Port Requirements** group at the top of the route block (open it: one row per commodity) and **surface ports only (left out)** on its heading. Unticked, there is no group and the item is an ordinary leg of the trip, its stop noted as a surface port. The choice is remembered.
- [ ] **Following purchases:** after Find all, put some of a listed commodity in the ship's hold (or on the carrier). The route and lists shrink by that amount within a moment, and a commodity held in full disappears, with no new search.
- [ ] **Window positions:** with a monitor to the left of the primary, move a WFMT window onto it, close it and reopen it. It returns on that monitor.
- [ ] The **Planetary** column reads Yes for planetary ports, outposts and settlements and No for orbital stations and carriers. The whole results table fits at the window's minimum width.
- [ ] **Here** puts the current system (the last system EDMC saw) into Around. **Copy System** copies the selected row, and clicking a result row (a station or a route stop) does so at once.
- [ ] With no network, the panel states that the search failed and the button returns.
- [ ] **Find all**: lists a heading per commodity still to buy with up to 5 stations under each. The button reads **Stop** while it runs, and stopping keeps what was found. The window stays responsive.
- [ ] **My Projects (requires the internet):** press **Projects** on the Colony page (or **My Projects** in the **Raven Colonial** menu).
  - A window lists the commander's Raven Colonial projects with building, progress and tons still needed. The subtitle adds up the counted ones.
  - Double-clicking a row changes whether it counts, and the subtitle states that there are unsaved changes.
  - **More** has Copy Shopping List, the two Open items, Set as My Primary and Save Counted List. The last two ask first and refuse while the master switch is off.
- [ ] **Planned Builds (requires the internet):** select a site, press **Planned Builds** (in the **Raven Colonial** menu).
  - A window lists Raven Colonial's sites for its system (building, planned, complete), marks the ones tracked and shows each planned or building site's **Full cost**.
  - Clicking a row names its biggest commodities.
  - **Refresh** works.
  - With no network it states that Raven Colonial could not be reached.
- [ ] **Suggested route:** after Find all, a "Suggested route to buy what you need..." block fills the Suggested route tab (the first tab; Closest stations holds the per-commodity lists), with a "Suggested trip" group of numbered stops (a **Next stop** card above them, and a jump distance on each) and, under each, the commodities to buy with their price and supply. **Copy Route** puts plain lines on the clipboard. A plain Find nearest shows no such block.
- [ ] **Remembered choices**: change the Preset, Within, Sort, Landing pad, Exclude fleet carriers and Exclude surface ports, run a search, close and reopen the window. The same choices return.
- [ ] **Only what [station] sells**: disabled until a station's commodity market is opened. It then names the station and narrows the list to what that market has for sale (in stock, with a buy price). It unticks itself on undocking. (`Market.json` lives in the journal folder: confirm EDMC's journal path on Linux/Proton.)

## 7e-1. Rescan Journals (Windows-Tested Only: Check on Linux)

- [ ] With a fleet carrier and some transfers in the journals, **Rescan Journals** in the Colonization Sites window rebuilds the FC column from the last 30 days. The status line names the commodities and tons. Pressing it twice gives the same figures.

## 7e-2. Raven Colonial Sharing (Requires a Raven Project for a Site; Windows-Tested Only: Check on Linux)

- [ ] **Settings → Colonization → Raven Colonial** has a master switch and two checkboxes (all off, the two disabled until the master is ticked) and a masked key field. With the master off, Report Complete to Raven refuses.
- [ ] With the first on, a delivery at a construction site that Raven has a project for appears on Raven. With it off, nothing is sent.
- [ ] **Raven Progress** shows Raven's remaining need beside WFMT's for the selected site, including one still being built.
- [ ] **Test key** (beside the key box) states that the key is accepted, with Raven's name for the commander, or that it was not accepted.
- [ ] The link under the key box opens ravencolonial.com/user in the browser.

## 7e-3. Overlay Placement: Show Checkbox (Windows-Tested Only: Check on Linux)

- [ ] Each row on **Overlays → Overlay Placement** has a **Show** checkbox. Unticking one (then OK) hides that display. Ticking it brings it back where it was. **Reset all to defaults** ticks them all.

## 7e-4. Colonization Sites Window Header (Windows-Tested Only: Check on Linux)

- [ ] The header has **Copy Shopping List**, **Where to Buy**, **Rescan Journals**, **Raven Colonial ▾** and **Manage Sites ▾**. The two menus open under their buttons, are legible (dark colors) and close when a click lands elsewhere or an item is picked.
- [ ] **Raven Colonial ▾** lists My Projects, Planned Builds, Raven Progress, Open Selected Build on Raven, Open This System on Raven, Raven Colonial Website, Create Project on Raven, Report Complete to Raven and Mark Plan Entry Demolished. The three Open items open the correct page in the browser.
- [ ] A site renamed in the game takes its new name after the commander docks at it again.

## 7f. Overlay Placement and the Overlays Settings Tab (Windows-Tested Only: Check on Linux)

Written on Windows against a 3840 x 2160 screen in EDMCModernOverlay's fill mode.

- The logic is platform-neutral.
- Not yet seen on Linux:
  - reading the screen size from inside the Proton prefix (and the overlay's log)
  - the display scaling under XWayland
  - how the overlay maps its canvas and sizes there

- [ ] **Settings -> Overlays** has twenty-one tabs: Overlay Connection, Appearance, Overlay Placement, Hide overlays, Colonization, Discovery, Inventory, Interdiction Warning, Flight Alerts, Route, System targets, Body info, Exobiology, Expedition Log, Powerplay, Missions, Landing, Surface Compass, Mining, Notable Bodies and Screenshots. General has no overlay tab.
- [ ] **Default spots:** with every box ticked, **Show placement preview** on a screen of 1920 x 1080 or more draws the boxes without any two overlapping (Interdiction at the top, Discovery below it, Notable find at the top right above Inventory, Flight alerts on the right below Inventory). On a smaller screen some boxes can overlap. Moving them on the tab resolves it.
- [ ] The Overlay Placement tab's info line shows the real screen size and display scaling, from the EDMCModernOverlay log or `DisplaySettings.xml`.
  - If it reads "game files not found", record the Wine/Proton prefix path and report it.
  - If it reads "log (window size only; DisplaySettings.xml not readable)", the size is correct and the scaling is not read.
    - Set **Display scaling** by hand.
    - For a Flatpak EDMC, check permission 5 in the Linux guide.
  - Under XWayland or Wayland scaling the overlay's log is the best source. Confirm that its numbers match the display.
- [ ] It shows the overlay mode EDMCModernOverlay uses (fit or fill).
- [ ] **Show placement preview** draws a labeled box for every display, at its real size, all on the screen.
- [ ] Change a display to **Bottom left** with offsets 20 / 20, press OK, then **Test Overlay** (or the feature's test button). It appears in the bottom left corner of the game screen.
- [ ] A display set to **Bottom left** with offsets 40 / 40 sits 40 pixels in from the bottom left corner of the screen.
- [ ] A display set to a **Right** spot (Inventory pickups, Screenshot messages) sits against the right edge of the screen at its full width, not short of it.
  - Settings -> Overlays -> Overlay Placement -> **Show placement preview** shows the same.
  - WFMT sets an offset on that display's EDMCModernOverlay group. If it sits short of the edge, the EDMC log has "Could not set the EDMCModernOverlay offset".
  - Unticking **Carry displays on the right to the screen edge** puts them back at the limit.
- [ ] A position set by exact X/Y numbers shows as **Exact position** with the same numbers.

## 7g. Overlay Appearance (Windows-Tested Only: Check on Linux)

- [ ] **Settings -> Overlays -> Appearance** exists, with a Color scheme menu and a Text size menu (Default, Larger; Larger is the starting value). Select each size and press **Show sample**: no text runs past its box.
- [ ] **Show sample** draws the Colonization card in the game in the selected scheme.
- [ ] At **Larger** (the starting size), each display (Colonization, Discovery, Notable, Landing, Inventory, Mining, Screenshots) keeps its text inside its border without wrapping. Record any that do not, with the font and Proton/Wine setup.
- [ ] Changing the scheme recolors every display. Interdiction stays red.
- [ ] After OK, the choices are still set when Settings is reopened. **Reset appearance** restores Elite orange and Larger.

## 7h. Colonization Mode (Windows-Tested Only: Check on Linux)

- [ ] The button row has a **Colony** button (eight buttons). The panel is not noticeably wider than the other modes'.
- [ ] Colony shows **Current project** for the newest active site and a **History** block. Dashboard opens the sites window, and Overlay toggles the overlay card (lit while on).
- [ ] Without a fleet carrier there is no On your carrier row, Trips left reads like "3 loads of 400 t", and the sites window has a single Trips column (Commodities and Trips left go once the site has nothing left to deliver). With a carrier, On your carrier is shown and Trips left reads "N to buy · N to haul".
- [ ] Overlay Placement tab, with two commanders seen: **Copy all overlay layouts and settings from** lists the other commander. **Copy** then **OK** gives this commander the other's cards, placement and look (the overlay redraws). **Cancel** changes nothing. The other commander's choices are unchanged. With one commander the row is not shown.
- [ ] The Colony page is in sections: the project (Delivered, Still needed), **What you have** and **To finish the build**. There is no Next line. With no site under construction it lists the last 5 completed sites, newest first, as "Name (System) - date".
- [ ] After delivering cargo to a depot, "You delivered" and "Recently" increase by the same tons, and again after restarting EDMC (no double counting).
- [ ] After a build completes, History's "done" count increases.
- [ ] **History rebuild:** on the first start, the log reads "Colonization history rebuilt for [CMDR]" and the History note's "Counted since" date moves back to the oldest delivery in the journals. Restarting EDMC does not rebuild again, and the totals do not double. (Requires Elite's journal folder set; on Linux that is inside the Proton prefix.)
- [ ] **Claims line:** after the history rebuild, the History block has a "Claims" line (for example "5 systems claimed · 5 beacons") for a commander who has claimed systems.
- [ ] **History chart:** the "Last 14 days" line draws a row of blocks of different heights (no empty boxes) and "Busiest site" names a site.
- [ ] **Overlay card footer:** with a fleet carrier it reads `N remaining  N to buy  N to haul`. Without one, `N trips to finish`.

## 7i. Boxel Survey Catch-Up, Colonization and Planned Builds (Windows-Tested Only: Check on Linux)

- [ ] **Boxel Survey catch-up:** scan a few bodies with EDMC closed, start EDMC. Settings -> Boxel Survey shows them, and a second restart changes nothing. (Requires the journal folder; on Linux that is inside the Proton prefix.)
- [ ] **Powerplay cycle tally:** the panel shows **Cycle N merits** and **Cycle N CP** under the session lines, and they remain after restarting EDMC.
- [ ] **Trade, Round trip:** each pair lists its loads with prices, profit per ton, supply and demand. Docked at a fleet carrier, the result states that it started from the carrier. The Round trip radius in the Routes window changes how far it looks.
- [ ] **Trade, Session window:** ends with the game's career totals for the commander.
- [ ] **Waypoint Route, From plotted route:** plot a route in the game and press the button. Its systems are added.
- [ ] **Community goals:** the Community Goals type in the Mission types window lists payouts under **Paid out**.
- [ ] **Colonization, Find all:** the results begin with a suggested shopping route, and **Copy Route** puts it on the clipboard.
- [ ] **Planned Builds:** the **Full cost** column fills, the window's subtitle adds up the planned builds, and clicking a row names the building and its five biggest commodities.

## 7j. Plugin Version Line (Windows-Tested Only: Check on Linux)

- [ ] The first line under the mode buttons reads **Plugin: vX.Y.Z** above the game-mode line, and does not widen the panel.
- [ ] After an automatic update is downloaded it reads **vX.Y.Z download - Restart EDMC** in bold black on orange (check the Default, Dark and Transparent themes). After the restart it reads **Plugin: vX.Y.Z (updated)** in green for about 15 seconds.

## 7k. Mining Simulation and the Surface Live Radar (Windows-Tested Only: Check on Linux)

The Surface Live radar has not been tried on Linux. The simulation shows it without the game.

- [ ] Settings → Mining → Simulation → **Surface Live (pretend Rhino)** opens a window titled "Surface Mining Live (simulation)" with *SIMULATION* in its subtitle.
- [ ] The radar draws on the left. Check each of these:
  - range rings
  - a trail of ground driven
  - a Rhino arrow that moves and turns along a ring 3.75 km round the middle of a marked location (the 2 km range, the default, shows an arc of it)
  - two marked locations (a cross and a circle through its border; one with no border)
  - five placed deposits with their first letters (one depleted, a hollow ring; a sixth, saved without a position, is listed in the lines on the right and not on the radar)
  - a line to the nearest deposit with a distance
  - Record whether the labels render correctly (the radar uses Pillow's built-in font).
- [ ] The five range buttons under the radar resize the view, and the choice is kept. Resizing the window resizes the radar and never widens it past the window.
- [ ] The lines on the right update about once a second (refined counts, cargo, nearest marked location, nearest deposit) without flicker, and wrap inside the window.
- [ ] **Mark center** and **Mark border** add or finish a marked location on the pretend ground. **Add hotspot** opens the add-hotspot window filled with the pretend position and a saved deposit shows up on the radar. There is no **Import/export**.
- [ ] The radar also shows:
  - orange dashed **drive rings** round the first marked location (2 km, then 4.5 km on the border)
  - two violet **Stop** circles
  - with a target commodity set on the Space Mining window's Settings card (try Painite or Platinum), a bright line to the nearest saved deposit of it with the nearest of any kind dotted
  - Press **Help** and confirm that each entry matches the display, and that the window and its text are whole.
- [ ] **Save map** opens the desktop's save dialog (confirm that it appears in front of the window and accepts clicks), writes a PNG, and the picture opens in an image viewer with the title, the marks and the legend legible.
- [ ] Close the simulation, open the real Live window (the **Surface Mining** button), and confirm that none of the pretend deposits or marks are there.
- [ ] Report the distribution, desktop, X11 or Wayland, native or Flatpak EDMC, and any `Plugin "WFMT" failed` or traceback lines in EDMC's log.

## 7k2. The Navy Look (Not Run on Linux)

- [ ] Open the Sites window, Inventory, the Exploration Dashboard and the Mining Book. Surfaces are navy, not gray. The window title is gold. Section labels and table column headers are cyan. The footer message is bright yellow, and green after a success. All text is legible, on Wayland and on X11.
- [ ] The Colonization overlay card's third column is headed **Acquire**.

## 7k4. Color Themes (Not Run on Linux)

- [ ] Press the theme name at the right end of a window's bottom line and choose each of Cyan, Amber, Green and Navy. Every open WFMT window recolors at once and stays legible, on Wayland and on X11. The drop-down menu is drawn in the theme's colors.
- [ ] Settings → WFMT → General → Window → Color theme shows the same name. The choice is kept after a restart, and a window opened afterwards uses it.
- [ ] The stat tiles at the top of a dashboard keep their size when **A+** is pressed.

## 7k5. Colonization Archive and the Footer Message (Not Run on Linux)

- [ ] In the Sites window use **Manage Sites → Archive Finished**. Finished sites leave the list and the status line counts them. **Show Archive** lists them with result, dates, time taken and tons needed. Selecting one lists its commodities. **Restore**, **Copy Summary** and **Manage → Remove Permanently** (asks first) work. Restart EDMC: the archive is still there. Nothing is cut off at the window's smallest size.
- [ ] The footer message is yellow on Navy, Cyan and Green and cyan on Amber, and green after a success. The note under the Where to buy buttons is in that color while a search runs.
- [ ] **Create Project on Raven** opens its dialog centered and inside the screen on Wayland and on X11.

## 7k3. Text Size and Column Fit (Not Run on Linux)

- [ ] Open the Sites window and press **A+** twice at the right end of its bottom line. The text grows in every open WFMT window, tables stay aligned and nothing is cut off. **A-** shrinks it, and the size is kept after a restart.
- [ ] Settings → WFMT → General → Window → Text size shows the same number. Typing one from -2 to 6 and pressing OK applies it.
- [ ] Short columns are narrow and a long name column takes the spare width.

## 7l. Shortcuts: Chat Commands and the Settings Page (Windows-Tested Only: Check on Linux)

Keyboard shortcuts are Windows only. The chat commands are the same on both systems and read the journal's `SendText` line.

- [ ] Settings → General → Shortcuts lists six actions with the key choices **disabled**, the chat commands (`!wf center`, `!wf border`, `!wf rig`, `!wf zoom`, `!wf live`, `!wf overlays`) and a **Chat commands** tick box (off by default). The page is whole at the default Settings size and nothing is cut off.
- [ ] If the page states that it could not find Elite's controls file, record it (the Linux binds file is looked for inside the Proton or Wine folder).
- [ ] Tick **Chat commands**, press OK, then in Elite's chat (a channel with nobody else in it) type `!wf overlays` and press Enter. The overlays hide. Type it again: they show. Record the delay between pressing Enter and the effect, and with a Flatpak EDMC whether it works at all.
- [ ] With the simulation open (Settings → WFMT → Mining → Simulation) or on real ground:
  - `!wf zoom` steps the radar's range (50 m, 250 m, 500 m, 1 km, 2 km, back).
  - `!wf live` raises the Live window.
  - `!wf center` / `!wf border` state what they did in the window's status line.
- [ ] A message that is not exactly a command (`!wf center now`, `hello`) does nothing, and with the tick box off nothing happens.
- [ ] A sound plays when a command worked (requires `canberra-gtk-play` or `paplay`), and none when it did not.
- [ ] Report the distribution, desktop, X11 or Wayland, native or Flatpak EDMC, and any traceback in EDMC's log.

## 7m. What Pays (Windows-Tested Only: Check on Linux)

- [ ] With *Enable Spansh best price finder* ticked (Settings → WFMT → Mining) and a few saved deposits, **Book** → **What pays** opens a window.
  - *Near* holds the current system, and *Within 100 ly* is chosen.
  - The table fills in one commodity at a time and is then ordered best price first.
  - Nothing is cut off at the default size.
  - **Help** opens and closes.
- [ ] A commodity nobody pays for shows *No station found*. **Copy report** puts a numbered ranking on the clipboard. Changing *Near* or *Within* and pressing **Search** queries again.
- [ ] With the switch off, the button states so in the Book's status line and queries nothing.

## 7n. Get Body Info and a Body's Size from Status.json (Windows-Tested Only: Check on Linux)

- [ ] With *Enable body lookup* ticked (Settings → Mining), in the current system, **Book** → **Get body info** states that it is asking EDSM and Spansh and then how many landable bodies it listed and added, with sizes and mining-location counts.
  - The Book's body list gains them and nothing already there changes.
  - Straight after starting EDMC with no jump or login yet, it states that Spansh was not asked.
  - With the box unticked it states that the setting must be turned on and queries nothing.
- [ ] After **Get body info** in a system, restart EDMC (or jump away and come back). The Book's body list shows the same bodies again with no new request, and a body the journals give later replaces its remembered entry.
- [ ] FSS-scan a body that has mining locations. Its count appears in the Book's list without a detailed scan, and a later detailed scan changes it only if the numbers differ.
- [ ] Landed on a body with no `Scan` event in the journals, launch the Rhino. The green ground trail starts on the Live radar and **Mark center** reads "Center marked" (the body's size comes from `Status.json`).

## 7o. The Mining Radar over the Game (Windows Only: On Linux, Confirm That It Does Nothing and Says So)

- [ ] Settings → Overlays → Mining shows **Show the Mining radar over the game**, a size, an opacity and **Test radar**.
  - Pressing **Test radar** states that it requires WFMT's built-in overlay (Linux has EDMCModernOverlay only) and draws nothing.
  - The page is whole and not cut off.
- [ ] With the box ticked, launching the Rhino on Linux draws nothing over the game and raises no error in EDMC's log (the Surface Live window is the way to see the radar on Linux).

## 7p. Rig Placed and the Rig Bands (Windows-Tested Only: Check on Linux)

- [ ] In the Surface Live window (or the simulation, which has three rigs already):
  - **Rig placed** reads `Rig N noted here.`
  - Pressing it again at the same spot states that it is already noted.
  - **Clear rigs** forgets them.
  - With a rig gap set on the Surface Mining window's Settings card, a band of that radius appears round each rig (filled while inside it, an outline when clear).
- [ ] `!wf rig` typed in Elite's chat does the same (with chat commands switched on). The sound plays when it worked.

## 7q. 1.4.2: Where to Buy Tabs and the Colony Page (Not Run on Linux)

- [ ] **Tabs:** the Where to Buy window has **Suggested route** (first) and **Closest stations**. **Find all** with a route opens the first, **Find nearest** the second.
- [ ] **Search is underway:** a large message fills the content area while a search runs and goes when it ends.
- [ ] **Route order:** **Smallest purchase first**, **Largest purchase first**, **Farthest stop first** and **Default (shortest flight)** reorder the same stops. Nothing is searched again.
- [ ] **Sections:** only the first section on each tab starts open. **Expand all** and **Minimize all** work, and a sort keeps what was opened.
- [ ] **Stops:** each stop's Notes give its body and the age of its market data. The trip has no final row for the site.
- [ ] **Colony page:** a **Body** line for the highlighted site, **Commodities** as `N done - N partly - N working on it`, three **Biggest gaps**.
- [ ] **Mode buttons:** the row reads Powerplay, BGS, Explore, Mine, Trade, Mission, Operations, Colony, and the whole row still fits the panel's width.

## 7r. 1.5.0: Pages as Windows, Settings in Their Windows, Type-Ahead (Run on Linux 2026-11-02)

- [x] **No page arrows:** Trade shows a short summary over **Session**, **Routes**, **Market** and **History** in one row. Mining shows a few lines for both sides over **Space Mining** and **Surface Mining**. Missions lists each type with its count over **Mission types**. Each button opens its window. Each window opens in front, fits its text and does not widen EDMC's window.
- [x] **Trade History:** the Trades tab opens on the newest 200 trades and **Show older trades** adds 200 more each press.
- [x] **Mining windows:** **Book** and **Dashboard** are in each window's header and open the correct windows. The `!wf live` command and its Windows shortcut open the Surface Mining window with them.
- [x] **Routes:** every hop shows **Profit**, the running **Total** and the distance. A **Whole route** row and a bold average-per-leg line follow. **Hops** cycles 2 to 10. A **Round trip** pair ends with *Both legs*. **Carry only this commodity** limits both legs and suggests commodity names during typing.
- [x] **Settings in their windows:** each of these saves as it is changed (no **OK**) and shows the same value in File → Settings → WFMT where the tab keeps a copy: Routes and Market (Trade), Session (*Count fines and bounties*), the Settings card of Space Mining and Surface Mining, the Display card of Mission types, the Settings tab of Powerplay Sessions and of Inventory, the Settings card of BGS Report, the Raven Colonial strip of Sites (its ticks disabled while the master switch is off), and the Settings strips of Expedition, Prediction review and My Codex.
- [x] **Settings tabs state where things moved:** the Trade, Mining, Missions, Powerplay, BGS, Inventory, Colonization, Expedition and Organic Scanning tabs each carry a note that matches the new location.
- [x] **Type-ahead:** the Body and Ring boxes (Add hotspot, Expedition stops, Surface marks, Notes, the ring reserve lookup), the Ship box of a ship build, the Also check and Hotspots boxes (after a comma) and the Add a ring and Expedition Log system boxes suggest names. Down, Up, Enter and Escape work, and the list does not take the keyboard.
- [x] **Light theme:** with EDMC on its Default (light) theme the panel's headings, warnings and buttons are a darker orange and legible. On Dark they keep the bright orange.
- [x] **Scrapped carrier:** after decommissioning a fleet carrier in the game (or with a journal containing `CarrierDecommission`), its record goes once the scrap time passes.

## 7s. 1.5.1: Combat Record, Materials This Session, Ship Names (Run on Linux 2026-11-03)

- [x] **Combat Record panel:** the row in Operations shows **Kills**, **Deaths** and **K/D** for **This session** and **All time**. The first start reads the journals (the Proton or Wine folder when EDMC's **Journal directory** points at it) and the **All time** row reads `...` until it is done.
- [x] **Combat window:** **This session**, **All time** and **Sessions** tabs, each with the split by ship. Ship names are the game's (`Anaconda Mk II`, `Kestrel Mk II`), not internal names. **Rebuild from journals** gives the same figures.
- [x] **Session boundaries:** the session is the journal file. A logout to the menu and back stays in one session; a new game start is a new one.
- [x] **Engineering row:** the **Held** and **Session** table. A pick-up raises both; a discard changes **Held** only; the **Session** figure survives a restart of EDMC in the same login.
- [x] **Ship names:** the Trade ship line and the Expedition Log's ship show proper names.
- [x] **Flatpak EDMC:** the new data file `combat_record.json` is in the plugin folder, and **Back up my data** includes it.

## 7t. 1.5.2: Rename Site, Anduliga, Landing Places, Mission Types, Item Names, Blueprints (Not Run on Linux)

Steps for each are in [TEST_PLAN.md](TEST_PLAN.md) section 14.

- [ ] **Rename Site:** **Manage Sites → Rename Site…** and, for an archived site, **Manage → Rename Site…**. The dialog takes the keyboard focus, **Rename** and **Cancel** work, the name shows in the list, the overlay card and the History, survives docking and a restart, and an empty name brings the game's name back.
- [ ] **Refresh from Raven:** the button under the list of sites fills the **Raven** column for the open sites, the note gives the time, and the column and note are readable at the usual size. Nothing is asked before the button is pressed.
- [ ] **Flatpak EDMC:** a renamed site is kept in the sites file in the plugin folder, and **Back up my data** includes it.
- [ ] **Rare Goods Finder:** Anduliga Fire Works is in the list (142 rares).
- [ ] **Nearest place to land:** settlements, Dodec Starports and Asteroid bases appear in the Stations table.
- [ ] **Mission types:** a donation or rescue mission is under **Donation & Rescue**, a scan mission under **Combat**.
- [ ] **Inventory:** the consumables are named Medkit, Energy Cell and so on.
- [ ] **Engineering:** the new blueprints are listed, and the Ship planner skips no module of a build that holds them.

## Reporting a Failure

Open an issue with the setup line (distribution, desktop, X11 or Wayland, native or Flatpak EDMC), the failing step number and the log excerpt.

## 7u. 1.5.3: Copy Next System Follows the Leg (Run on Linux 2026-11-04) and Expedition Summary for Discord

Steps are in [TEST_PLAN.md](TEST_PLAN.md) section 15.

- [x] **Copy next system:** after docking at a leg's destination, the button copies the following destination (never the system you are in), and a loop wraps back to the first stop. Confirm the paste works in the galaxy map under Proton.
- [ ] **Expedition summary for Discord:** in the Expedition window's Log tab the share row fits, **Copy for Discord** copies the summary, and **Customize…** opens on Expedition summary with a working preview. Steps: [TEST_PLAN.md](TEST_PLAN.md) section 15.
