# Linux test checklist

For anyone testing WFMT on Linux with Elite Dangerous under Steam Proton (or Wine, Lutris or Heroic).

**What has been tested on Linux**

- The unit and smoke tests, which use mocked system calls.
- Two real passes on KDE Plasma (Wayland) with a Flatpak EDMC, on 2026-10-18 and 2026-10-20.
- Both passes were of earlier builds of this code, before the 1.0.0 restart and rename. No manual pass has been done on Linux since; the window-fit fixes of 2026-10-21 were checked only in a Docker run (a Linux container).

**Reports**

- Real reports are valuable.
- Note your distro, desktop (GNOME, KDE, Sway...), session type (X11 or Wayland), and whether you run EDMC natively or as a Flatpak.
- Where a step fails, copy the relevant lines from EDMC's log (`~/.local/share/EDMarketConnector/logs/EDMarketConnector-debug.log`) into your report.

**Already seen working** (KDE Wayland, Flatpak EDMC):

- The WFMT Settings panel.
- The test overlay, Discovery and Notable Bodies overlays.
- A Flatpak EDMC needs the host-spawn permission in section 0 before overlays will draw.
- Please note exactly what you see (which tabs, which overlays, how often) so anything that differs can be checked against it.

## Testing: start here

### Where testing stands

- Features are tested on Windows first.
- A Linux pass on 2026-10-18 (KDE Plasma and Wayland, a Flatpak EDMC, an earlier build of this code) covered most of the plugin and went well.
  - It found one problem, right-hand overlay cards stopping short of the screen's right edge. That is largely fixed; a small gap remains on Linux (see Known issues).
- A second Linux pass covered the Route Planner checklist and went well.
- The rest of that work is in section 6 below:
  - the Exploration Dashboard
  - the data backup with restore and automatic backup
  - compact data files
  - the Random rebuild
  - POI Reference
  - the My Codex window
  - alphabetical sections in every mode
  - the wrapped-text width fix
  - overlay cards that leave in one step
- On 2026-10-20 the newest features (below) had a quick pass on Linux (also an earlier build), not the full checklist.
- The checklist sections below carry the longer wording for anything those passes did not reach.
- Items marked "Windows-tested only" have not been tried on Linux yet.
- `docs/TODO.md` lists the open checks, and [TEST_PLAN.md](TEST_PLAN.md) is the plan for both systems.

### Newest features (no Linux pass yet)

Do sections 0 and 1 first, then run the unit tests and a build (steps 2 to 4 under "Getting set up") and work through these. They are the work added since the earlier passes; each has its longer wording in `docs/TODO.md` under "Verification in the game".

- **Added in 1.3.3 (not yet run on Linux).**
  - **Powerplay card.** Needs EDMCModernOverlay. Tick *Enable the Powerplay card* (Settings → WFMT → Overlays → Powerplay) and press **Test Card**: a card appears at the top right. Jump into a Powerplay system and then one without Powerplay data (it says **No Powerplay Detected in system**).
  - **Look-ahead.** Tick *Look up the system I am jumping to* and start a hyperspace jump: the card turns to the destination (marked *jumping*) and then to the system you arrive in. Fly a loop twice: the second lap should not look anything up. The steps are in [TEST_PLAN.md](TEST_PLAN.md) section 9.
- **Added in 1.3.2 (not yet run on Linux).**
  - **Windows open on EDMC's monitor.** With two monitors, open a WFMT window you have not opened before (the Notes window, say). On Linux Tk cannot list the monitors, so it opens centered over the EDMC window and kept on the visible screen; note which monitor it lands on, under X11 and under Wayland. Drag it to the other monitor, close it and open it again: it should reopen there. Then tick *Always open WFMT's windows on EDMC's monitor* (Settings → WFMT → General → Window) and open it again: it should open over the EDMC window.
- **Added 2026-10-23 (none of it run on Linux).** The Windows side of each is in [TEST_PLAN.md](TEST_PLAN.md) section 5.
  - **Every overlay off.** After `git pull --rebase`, start EDMC. The log has `All WFMT overlays reset to disabled (one-time), including the saved choices of N commander(s)` once, and no card shows for any commander. Turn one on and restart: it stays on.
  - **Screen size from the operating system.** In Settings → Overlays → Overlay Placement, with the overlay's log and `DisplaySettings.xml` out of the way, press **Detect screen again**. The source line should say it is using the primary display with your real resolution.
    - It runs `xrandr --current` (through `flatpak-spawn --host` from a Flatpak) and takes the primary output. Report the session type (Wayland or X11), whether `xrandr` is installed, and what the source line said.
    - On a multi-monitor desktop only the primary output counts.
  - **A stopped expedition and Rescan.** Stop an expedition, wait a minute, start it again: the clock carries on from where it stopped. Pause one, jump while it is paused, resume, press Rescan: the totals do not include those jumps.
  - **Table text.** A long faction, station, ship, role or site name in Missions, Source commodities, Ship Builds and My Codex is shown whole in a wide window and cut with an ellipsis in a narrow one.
  - **Saved names** (a copy of data from before the spelling change, if you have one): `Renamed saved names:` appears once in the log and the Colonization data is intact.
  - **Ship planner, In storage column (new).** Open Module Storage once at a station, then read a build that holds a module you have stored. The column says Yes for the same engineering at the level or above and Partly for other engineering; select the row for where it is. A module fitted to a ship does not match.
  - **Tests.** Run `python -m unittest discover -s tests` from a desktop session (3,370 tests passed in the Docker run), and say how many are skipped and which fail.
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
  - Each should:
    - appear centered over its window
    - block it until answered
    - wrap long text
    - take Esc as Cancel and Enter as the highlighted button
    - take focus under KDE Wayland
- **Screenshot preview.** Take a screenshot with the preview on, from a very wide capture and a tall one.
  - The window stays on the screen and the picture is whole.
  - Esc and Close work, and resizing re-fits the picture.
  - **Open Folder** opens your file manager. From a Flatpak this goes through the sandbox: say if nothing opens.
- **Spansh requests.**
  - Random, Neutron Star and White Dwarf, Nearest place to land, Where to buy, the Mining price finder, and typing in a system-name box (with the Settings → WFMT → Window suggestion option on) all still answer.
  - Press Random several times quickly: the requests are spaced, not sent together.
  - With the network off, a lookup fails with a clear message. After several failures the message says Spansh is being left alone for a few minutes.
- **Ship links.** Ship planner:
  - Paste a Coriolis or EDSY import link and read it.
  - **Copy Coriolis link** and **Copy EDSY link** copy a link (paste it into a text editor to check it is one long address).
  - **Open in Coriolis** and **Open in EDSY** open your browser.
  - From a Flatpak EDMC, opening a browser also goes through the sandbox: say if nothing opens, and the same for Report an issue under Settings → General → Help.
- **Stored modules.** Open Module Storage at a station in the game, then Ship Builds → **Stored modules**.
  - The list, the freshness line and the transfer cost and time match the game.
  - Store, retrieve and swap a module and check the tab follows.
  - Restart EDMC and check it catches up from the journals (the journal folder is in the Proton prefix: section 0).
- **Start expedition and Review.** Plot a route, press **Start expedition**.
  - The expedition starts together with its Expedition Log run.
  - **Review expedition** opens the Expedition window on it.
  - Pause and Resume from either side agree, and a restart while paused keeps both paused.
  - The plan dialog's **Start it now** tick starts a Road to Riches or Exomastery plan.
- **One Expedition window.** **Expedition** and **Plot** on the panel open the same window with Plan, Route and Log tabs.
  - It is never opened twice.
  - The panel has one Expedition section (the Log's figures, Copy Next and Expedition, with no Start, Pause or Stop) and no Expedition Log section.
  - The tabs' buttons and tables fit at its smallest size and at the full screen width.
  - Report whether the window takes the focus when it opens (it should not steal it from the game).
- **Mining.**
  - The low-limpet alert does not appear for a Rhino or a laser miner with no limpets, and does for a prospector-limpet ship at zero.
  - The HUD and panel show the same limpet count.
  - Relogging inside a ring fills in the ring.
  - Mining History's Earned includes a sale made at a different station than the one you docked at after mining (and *Mined, not sold yet* shows what is waiting).
  - The price finder and What pays leave fleet carriers out and fill *Minimum demand (t)* from your hold.
- **Station price against the average.** Docked after a ring run with the commodities market open, the Space page shows `<commodity> here: N cr/t, P% above/below the galactic average (M)` for what the run refined.
  - It reads `Market.json` from the journal folder.
  - Report whether it appears with a Flatpak or Proton setup.
- **Mining rates and targets.**
  - The Space page, the Live window and the HUD show the same *Refining now*, *Run average*, *Hold full in about N min* and *Hold: N of M t* lines.
  - The target box in Settings → WFMT → Mining takes several names with their own percentages, and its type-ahead works after a comma.
  - Opening Mining History once re-reads old runs in the background.
- **Local star index** (Settings → WFMT → General → Online lookups → Local star index).
  - **Download and build** downloads about 173 MB into the Flatpak's data folder and builds an index of about 110 MB (about 300 MB free is needed while it builds).
    - Progress shows, and **Cancel** works.
    - The finished status shows the systems, size and date.
    - **Neutron Star** then answers from the local index (the status line says so).
    - Report the real build time.
  - **Update** on a later day downloads only a small file (about 3 MB for a day) and the status line says so.
    - Pressing it again at once says the index is up to date.
    - Report the time an update takes.
  - Delete removes it.
  - If the folder is not writable the message says so.
- **Carrier Route, Rare Goods and the earlier quick-pass items** (Mining pages, Mining History, the Space and Surface Mining Books, overlays and panels): the same checks as in [TEST_PLAN.md](TEST_PLAN.md).

Report the distro, desktop, X11 or Wayland, and native or Flatpak EDMC, with the relevant lines of EDMC's log, as usual.

### Areas the checklist covers

Use them for anything the passes did not reach.

**Overlay placement and cards**

- Right-hand overlay cards sit against the screen's right edge with a Flatpak EDMC, with the Graphics folder permission granted (permission 5 in the Linux guide) and with it left out. The Overlay Placement info line says where the screen size came from.
- A long system name (about 28 characters) shows whole on the Route rows and in the Body info, System targets and Bio signals titles with EDMCModernOverlay, whose text measuring differs.
- The items in `docs/TODO.md` for:
  - per-commander overlay settings (two commanders, each with their own cards and placement)
  - Nearest place to land
  - the likely color of a species
  - tracked plant marker rings
  - the Bio radar's north mark
  - The built-in overlay is Windows only, so Linux keeps EDMCModernOverlay.
- The Exobiology cards (Bio status, Biology, Bio radar, Sample popup), System targets and Body info, the Expedition Log (Start and Stop in the Expedition window, the Log tab, Start from my last sale), the drag-and-drop layout editor on Overlay Placement, panel opacity and legible text on every color scheme, and species shown as `Genus species` (the items are in section 6 below).
- The Route overlay, the Expedition card and survey counts, and the overlay padding and alignment (every card's text starts at the same left edge, the same distance from its border), plus a look at the default overlay spots.
- **Section 5, Overlay:** the Colonization card still shows when the game's Market event arrives late (the overlay also watches `Market.json`).
- **Section 7f, Overlay Placement:** an exact position that is off the overlay's canvas (such as a leftover `x = 1280`) falls back to the default spot.
- **Section 7g, Overlay Appearance:** the Text size choice (Default, Larger), and boxes holding their text at each size.

**Data, windows and sources**

- With EDMC started while the game is closed, the BGS, Mining and Trade windows still show a commander's saved data, and the EDMC log has no `Plugin "WFMT" failed` lines.
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
  - Depleted marks that stay and say how long ago
  - the Neutron route in the Expedition window
- The System targets visit history and Spansh lookup items in section 6 and `docs/TODO.md` (the journal folder is found on Linux, the first read finishes, the lookup says what it is doing).
- The Credits Ledger window (click the Credits line: it opens, fits, and the tabs fill), the Colonization History window (History button), fold sections starting folded, and Ship Builds folding.
- The items in section 6 below marked "Windows-tested only": mission progress colors, the alert widths, the Missions window and pinned missions, Best picks and Source commodities, the Missions overlay card, the Upgrade planner, Megaship scans and the Ship planner's subtract option.
- Settings → General → **Help** (Report an issue, Copy diagnostics).
- The Engineering window's **Engineers** tab (places, unlock steps, the Bubble / Colonia filter) and **Ship planner** tab.
- BGS rebuilding a period that closed while EDMC was not running, and finished Colonization builds losing the "Construction Site:" prefix.
- **Materials, Engineering and the Material trader** (Operations mode) and **the Expedition planner** (Exploration mode): the checklists are in section 5 below.

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
  - In Expedition, Materials, Notes and the Trade watch list, lines use the whole width of the window when it is wide, and a narrow window is still never widened.
- **Panel width:**
  - With Expedition (Exploration mode) and Materials (Operations mode) open, the main EDMC window must not grow wider.
  - In Expedition, **Copy on arrival** sits on its own line under **Copy Next** and **Expedition**.
  - In Materials, **Blueprints** sits under **Materials**, not beside it.
  - With a large font the Trade page and the Trade History window should not widen the EDMC window either.
- **History heading and Busiest site:**
  - The Colonization History heading names the commander (`History - NAME`).
  - Busiest site shows the site's name and system rather than `Construction site <number>` once you have docked at it.

### Getting set up

1. Install the plugin: the zip from the [releases page](https://github.com/rwharpernc/wayfarers-multitool/releases/latest), or `npm run deploy` (step 4 below).
   - Restart EDMC.
   - The line under the mode buttons should read `Plugin: v1.3.3`.
   - Work through sections 0 and 1 below first.
2. To get the checklist and the test suite, fetch the repository and use `master`:
   - `git fetch --all --tags`, then `git switch master`, then `git pull --rebase`.
   - Once per machine: `git config core.hooksPath .githooks`.
3. Run the unit tests: `python3 -m unittest discover -s tests`.
   - The window and panel smoke tests need a display; without one they are skipped, so run them from a desktop session.
   - On Arch and CachyOS the host needs `pacman -S nodejs npm tk python-pillow xdotool`.
     - A current Node is needed for the build.
     - `tk` is Python's Tkinter.
     - Pillow is used by the overlay and screenshot tests.
   - A Flatpak EDMC does not use the host's Python, so these are for the tests and the build only.
4. To try the `master` build instead of the release, run `npm run deploy` in the repository.
   - It finds EDMC's plugins folder (native or Flatpak) and copies the build there; restart EDMC afterwards.
   - The build reports the version in `plugin/__init__.py`.
   - For a Flatpak EDMC the plugins folder is `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/plugins/Wayfarers-Multitool`.
   - If the script picks the wrong folder, set `WFMT_PLUGINS_DIR` or pass `--plugins-dir <path>`.

## 0. Setup

- [ ] `xdotool` is installed (`xdotool version` works in a terminal).
- [ ] Elite has been launched at least once through Steam, so its Proton prefix exists.
- [ ] EDMC's **Journal directory** points at
      `<prefix>/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous`. The
      prefix is usually `~/.local/share/Steam/steamapps/compatdata/359320/pfx`.
- [ ] For overlay features: EDMCModernOverlay is installed and its overlay is running.
- [ ] If EDMC is a Flatpak: `flatpak override --user --show io.edcd.EDMarketConnector` lists all five
      permissions from the [Linux guide](guide/linux.md) (Step 3):
  - the journals folder
  - the Bindings folder (`:ro`)
  - the Pictures folder
  - the Graphics folder (`:ro`, for the screen size)
  - `org.freedesktop.Flatpak=talk`
  - Without the last one the overlay's sockets open (so **Check connection** passes) but its window never starts, and `xdotool` is invisible to WFMT.
- [ ] If EDMC is a Flatpak: the EDMC log has no "Host lookup of ... failed" lines from WFMT.
- [ ] **Elite Wine/Proton prefix** in Settings is empty unless you use a custom setup.
- [ ] An `overlay_client` process is running (`ps -eo args | grep overlay_client`).
- [ ] WFMT is copied into EDMC's `plugins` folder, EDMC is restarted, and the panel appears.

## 1. Basics

- [ ] Mode buttons switch, the panel collapses, and text and buttons look right (fonts, colors, dark
      theme).
- [ ] Settings → WFMT opens with every tab.
- [ ] Jump to a system: Powerplay, Exploration Value and Boxel Survey react to the journal event.
- [ ] No Python errors in the EDMC log.

## 2. Paths and journal

- [ ] Settings → Exploration → Auto-Honk shows **no** orange journal hint when the Journal directory is right.
- [ ] Clear the Journal directory: the hint appears, and the log has a "Linux journal folder" warning.
- [ ] Set **Elite Wine/Proton prefix** to a wrong path: Auto-Honk reports the binds file can't be found.
- [ ] Clear it again: the Proton prefix is auto-detected.
- [ ] If you have them: a second Steam library folder, or Flatpak Steam, is detected.

## 3. Auto-Honk

- [ ] Settings → Exploration → Auto-Honk → **Rescan** shows "Will press [key]" for your fire button.
- [ ] Elite running and focused: **Test Honk Now** reports "sent" and the scanner fires.
- [ ] The honk key stays down for the whole **hold time** (set 8 to 10 seconds): the scan completes instead
      of stopping after about a second.
- [ ] Elite not focused, **Focus game window first** on: Elite comes forward and the honk fires.
- [ ] Elite not running: it reports "Elite Dangerous window not found".
- [ ] `xdotool` uninstalled: it reports that it isn't installed, with the install hint.
- [ ] A real jump with Auto-Honk enabled honks once, and not again on a revisit.
- [ ] Try a fire button bound to a letter, an F-key, a numpad key and a modifier if you can.

## 4. Screenshots

- [ ] Take an in-game screenshot: it converts to PNG and appears in the panel.
- [ ] The default source folder is the prefix's `Pictures/Frontier Developments/Elite Dangerous`.
- [ ] The cropped preview matches the panel that was open (this needs `Status.json`).
- [ ] **Open Folder** opens your file manager.
- [ ] The timer icon and auto-capture timer take a screenshot in-game.
- [ ] A folder you can't write to shows a plain permission message, with no Windows text.

## 5. Overlay (needs EDMCModernOverlay)

- [ ] Landing Assist, Interdiction Warning (**Test Warning**), Discovery (**Test Discovery**) and
      Notable Bodies (**Test Notable**, after ticking Enable) all draw over the game.
- [ ] Surface Compass (Exploration mode, **Compass** section; Settings → Overlays → Surface Compass):
  - **Test Compass** draws an arrow and a name on the left.
  - On a planet surface the section shows the nearest hotspot with a distance.
  - **Mark** makes a mark.
  - **Target** steps through the marks here.
  - **Marks** opens the window (edit, **Here**, Delete twice).
  - With the compass enabled the arrow follows the target as you move and turn, and clears when you lift off.
  - Check the Mining settings tab has no waypoint tick.
- [ ] Materials (Operations mode, **Materials** section):
  - Log in and the row shows the pieces of each type.
  - Collect or discard a material and "Last: ..." follows.
  - A material at its limit is named.
  - **Materials** opens the window.
  - Search, Type, Grade and **Only what is at the limit** narrow the table, and headings sort.
  - The window keeps its size and place.
  - Restart EDMC mid-session and the counts are right.
- [ ] Material trader (Materials window, **Find a trader**):
  - The window opens with your system filled in and the type that has the most at the limit.
  - **Find** lists traders nearest first (check one against the galaxy map).
  - The Type, Within and Pad drop-downs change the search.
  - **Here** refills the system, and a typed system works.
  - Double-click copies the system name.
  - With no network the status says Spansh could not be reached and **Find** works again afterwards.
- [ ] Engineering (Operations, **Blueprints** on the Materials section):
  - The window opens with **Blueprints** and **Wishlist** tabs.
  - Search (it waits a moment after typing) and the Module drop-down narrow the list.
  - Picking a row shows its ingredients, what you hold and where each is found.
  - **Add to wishlist** and a double-click add.
  - The Wishlist tab shows each entry's crafts, whether it can be made and the shopping list.
  - **Set crafts**, **Remove** and **Clear list** ask twice.
  - The Materials section shows the `Wishlist:` line and stays narrow.
  - The window keeps its size and place.
  - The **Engineers** tab:
    - It lists engineers with where you stand (after a login), unlocked ones first.
    - **Show their blueprints** switches to the Blueprints tab searching for them.
    - **Put their unlock on the wishlist** adds it.
    - The wishlist's **Who can do it** column names an unlocked engineer or "No engineer unlocked yet".
- [ ] System-name suggestions (Settings → Window): in the Expedition window's System box type two letters of a system you have been in.
  - A list appears under the box.
  - **Down**, **Enter** take one; **Escape** closes it; **Enter** with nothing highlighted adds the stop.
  - The list must appear in front of the window on your desktop and Wayland compositor, and go away when the box loses focus.
  - Tick *Suggest system names from Spansh while typing*, type `outot`: after a pause systems from Spansh appear.
- [ ] Expedition (Exploration mode, **Expedition** section):
  - **Expedition** opens the window.
  - **New** makes an expedition.
  - **Add stop** (and **Here**) add stops.
  - **From plotted route** (after plotting a route in the game) and **Import CSV** add many.
  - **Road to Riches** and **Exomastery** (Spansh): press **Plot**, wait, check the new expedition's stops, notes and order against Spansh's own page.
  - **Neutron route** opens the Route Planner.
  - **Start** (in the Expedition window), then jump to a stop: the section ticks it, counts the jump and shows the next stop with its distance.
  - **Copy Next** and **Copy on arrival** put the next stop's name on the clipboard (check it pastes into the galaxy map's search box).
  - **Locate and reorder (EDSM)** orders the unvisited stops.
  - **Export CSV** saves a file and **Import CSV** reads it back.
  - **Reset** and **Delete** ask twice.
  - The section stays narrow with a long name, and the window keeps its size and place.
- [ ] Notes (Exploration mode, **Notes** section):
  - The quick-add box saves a line against the current system.
  - **Notes** opens the window.
  - The editor's text box takes typing and paste.
  - **Here** fills the system and body.
  - **Delete** asks twice.
  - The window keeps its size and place after closing and reopening.
- [ ] Trade Watch list (Trade mode, **Watch list** row):
  - **Watch** opens the window.
  - Add a commodity by typing (the suggestion list appears and a click or Enter picks it) and **Add**.
  - Open a station's commodity market in the game and the commodity gets a price, with the station under it when picked.
  - **Remove** asks twice.
  - With Trade lookups on, **Refresh** fills in Spansh prices and says so. With them off it says to turn them on.
  - The row stays narrow with a long system name.
  - Restarting EDMC keeps the list and the seen prices.
- [ ] Route overlay (Settings → Overlays → Route):
  - **Test Card** draws a card at the top left that reads `You are navigating to:`, a destination, a jump count, a rule, a list of system names, a rule and the light years left, every line starting at the same left edge.
  - Plot a real route in the game and the list loses a system at each jump and clears at the end.
- [ ] Exobiology cards (Settings → Overlays → Exobiology):
  - **Test Cards** draws all four as plain panels (no colored bar or outline) with the three circles beside the species name inside the card.
  - Sampling on a mapped body fills the circles, moves the progress bar a third per sample, updates the distance and the radar, and shows the popup.
  - Scanning a plant with the Composition Scanner and walking off shows a ring, a pointer line and `Tracking <species>` with the little pointers turning as you turn.
  - Leaving the planet clears the cards.
  - First footfall is marked on a body nobody has landed on.
- [ ] Hide overlays:
  - Click the `Overlays shown (click to hide)` line in the WFMT panel. Every card disappears at once, and the line reads `hidden`.
  - Click again: they come back where they were, including Colonization.
  - Settings → Overlays → Hide overlays has the **Hide / show now** button, and it works. The shortcut keys are grayed out under Settings → WFMT → General → Shortcuts.
- [ ] Duplicate overlay window warning:
  - With one overlay window running, Overlay Connection → Check connection says only that it is connected.
  - Start a second copy of the overlay and it adds a line naming two windows.
  - Copy diagnostics shows `Overlay windows running: N` (read from `/proc` on Linux).
- [ ] Nearest place to land (Exploration → Nearest place to land → Find):
  - The window opens and fits.
  - The box for the lookup must be ticked before Find works.
  - After a jump it shows your system and coordinates and your ship's pad.
  - Find lists stations and carriers.
  - Double-click copies a system name (needs a clipboard).
  - The position is read from the journals after a restart.
- [ ] Overlay font (Settings → Overlays → Appearance):
  - The section lists the fonts in EDMCModernOverlay's `fonts` folder (native or Flatpak).
  - Choosing one and pressing OK rewrites `preferred_fonts.txt` (with a `.bak`).
  - **Add font file...** copies a `.ttf` and selects it.
  - **Open fonts folder** opens it.
  - After a restart the overlay text shows lower case.
- [ ] Expedition Log (Expedition window, Log tab; Settings → Overlays → Expedition Log):
  - Start, a few jumps and scans, Stop (the buttons are in the Expedition window; the panel's Expedition section has none).
  - The Log tab shows the expedition, its facts and editor.
  - Rescan, Reset and Delete (asking twice) work.
  - Export CSV writes a file.
  - The overlay card shows the running totals.
- [ ] Body info as symbols and formulas, the Biology card's ranges and percentages, and Settings → Overlays → Appearance → Panel opacity (a lower value makes every card's background fainter, the text stays solid).
- [ ] Discord sharing: **Copy for Discord** in the BGS Report (**Discord** menu) and the Powerplay Sessions window puts formatted text on the clipboard (the clipboard works under your Wayland and Flatpak setup); **Settings → WFMT → Discord → Test** and **Post to Discord** (with one destination and with two) with a webhook in a private channel work from a Flatpak EDMC (outbound HTTPS to `discord.com`).
- [ ] Expedition Log's **Start from my last** buttons (**sale**, **Discovery Data sale**, **Exobiology Data sale**: just after that sale, filled in from your journals, then counting live).
- [ ] Layout editor (Settings → Overlays → Overlay Placement):
  - The picture of the screen shows with a box per display.
  - Dragging a box fills in the table.
  - A box dropped near an edge snaps flush (offset 0).
  - **Picture size** changes the picture and is remembered.
  - A card placed at the bottom or right with offset 0 sits on the screen edge.
- [ ] A relog, or a return to a system after visiting others, keeps the System targets and Body info cards' bodies.
  - Each commander's surveys are saved in `system_surveys.json`, and a system visited before is rebuilt from the journals.
  - The card's summary line and Done list show where you left off.
- [ ] System targets history and Spansh lookup:
  - After a restart the card shows `Reading your journals for a visit history (n%)` and then `First visit here` or `Been here N times before · last <date>`. The journal folder is the one EDMC uses on Linux, so check that it is found.
  - With the Spansh option ticked, a jump into a system others have surveyed shows `Looking up data (Spansh)...` and then a Known section. A system Spansh does not have says so.
  - `system_history.json` appears beside the plugin.
- [ ] System targets and Body info cards (Settings → Overlays):
  - **Test Card** on each draws a card with every line at the same left edge.
  - After scanning bodies in a system the targets card lists those worth mapping and any with life, and they leave the list when mapped or analyzed.
  - Targeting a body in the system map shows its Body info card.
  - Restarting EDMC mid-system brings the list back.
- [ ] Expedition survey tracking (Exploration → Expedition): start an expedition with two or three stops; arriving in a stop updates its totals in the Expedition row.
- [ ] Flight Alerts (Settings → Overlays → Flight Alerts):
  - **Test Card** draws a card on the right, below where the Inventory display sits.
  - With a carrier jump scheduled the countdown ticks every second and turns red in the last minute.
  - A plotted neutron star with the tank at or under 50% shows the unscoopable-star line.
  - The sound box is available only when `canberra-gtk-play` or `paplay` is installed, and a sound plays when an alert starts.
- [ ] Notable Bodies: scan a terraformable or an Earth-like, water or ammonia world and a violet banner
      appears; the same body does not alert twice.
- [ ] Landing Assist when the overlay starts late: request docking right after starting EDMC and the game, before the
      overlay client has finished starting.
  - The card and pad diagram appear once the overlay is up (within about a minute), without needing another docking event.
  - Switching between a starport and a fleet carrier removes the old diagram straight away.
- [ ] Card backgrounds are visible, not just the text.
- [ ] It works in borderless mode; note what happens in fullscreen.

## 6. Other features

- [ ] The Inventory pickup **sound** plays (Operations → Inventory settings).
- [ ] Codex **My Codex** opens, and its **Backfill Journals** action finds your journals.
- [ ] Codex details window: the Entry and Times found headings sort both ways, the **Not found** tab fills in
      (needs network the first time), and double-clicking an entry opens its Canonn search in your browser.
- [ ] Colony mode → **Dashboard** (colonization sites): after docking at a construction depot, the site appears with its
      outstanding commodities, In Cargo matches your hold, and **Copy Shopping List** pastes elsewhere.
- [ ] Mining: journal backfill works, and in an SRV the surface bearing arrow and coverage map work.
- [ ] Copy buttons (Powerplay, BGS, Boxel **Random**): pasting into another app works. **Random** names are real systems that plot on the galaxy map, and a second press nearby is quicker.
- [ ] Network lookups (EDSM, Spansh, Canonn, GEC) return results.
- [ ] Exploration **Neutron Star** and **White Dwarf** buttons: after a jump, each shows a system and distance and copies the
      name to the clipboard (paste it elsewhere to check).
- [ ] Hovering a button (for example **Auto-Honk**, **Random**, **Report**, **Powerplay**) shows its name and what it does in a
      tooltip that disappears when you move away, and the GEC, Canonn and Codex sections start minimized.
- [ ] Powerplay → **Rares** (rares) opens the Rare Goods Finder: after a jump or login it lists the nearest
      rare goods, the Controlling Power column fills in from Spansh, and double-click opens Inara in
      your browser.
- [ ] Restart EDMC: per-commander data (BGS, Boxel, Codex) is still there.

- [ ] **Mining History**: **Dashboard** in Mining mode reads your journals (check it finds the journal folder), fills the Overview and the three tables, and a run made with EDMC closed appears after a restart.
- [ ] **Random**: press **Random** twice near a procedurally named system.
  - The name plots on the galaxy map.
  - The status line gives a distance and says whether EDSM confirmed it.
  - The second press nearby is much quicker.
  - Settings -> Exploration -> Boxel Survey -> **Systems to request from Spansh** takes a number from 10 to 100.
- [ ] **Region Sweep, skip systems EDSM knows**: tick **Skip systems already visited by anyone (EDSM)** (Settings -> Exploration -> Region Sweep), add a cube and press **Next >**. The status line says `Checking EDSM...` and then how many known systems it skipped (or that the check was unavailable, with the candidate shown anyway).
- [ ] **POI Reference**: one section with **Find POI** and **Update POI**. Find POI shows a GEC line and a Canonn line, and a paste into the galaxy map gives the nearer system.
- [ ] **My Codex**: the Codex Completionist section has one button. The window opens on **Overview**; **Not found** has a **Where to look** column; **Backfill Journals** reads your journals.
- [ ] **Panel order and width**: in every mode the sections are alphabetical, and switching modes or opening the Route Planner and Dashboard never widens EDMC's window (if it does, send the "The WFMT panel widened" line from EDMC's log).
- [ ] **Overlay exit**: when a card goes away its panel goes with its text, in one step (no empty shell left for a few seconds).
  - Switch the Dashboard's Exploration overlays off and on: the cards go together.
  - They come back once Elite is in front (EDMCModernOverlay only shows them while Elite is the window in front).
- [ ] **Route Planner**: **Plot** in the Route Planner section of the Exploration panel (unfold it first) opens the window with your ship read from the journal (no jump range to type).
  - Generate route returns a route (every jump listed).
  - **Copy next system** and the **Copy the next system to the clipboard automatically** tickbox put the name on the clipboard (check a paste works in the galaxy map under Proton).
  - Arriving at a system turns its row green and moves the panel's next-jump line on.
  - With the Route overlay on, the route shows on its card in place of the game's route.
  - The window's status line says the route was sent to the Route overlay and which system is on the clipboard, and says it again at every system you reach.
  - **Start expedition** makes an expedition from the route, starts it and starts its Expedition Log run.
  - **Review expedition** opens the Expedition window with that expedition selected.
  - The Expedition window's **Neutron route** button opens this window.
- [ ] **Route overlay**: the card reads *You are navigating to:*, the destination, *You will be there in N jumps.*, a rule, the systems still to visit (no numbers), a rule, and *N LY left to jump.*
  - Each system shows its star in green (scoopable), yellow (not scoopable), blue (neutron star) or red (white dwarf).
  - At the last system it says the route has ended and is being reset for ten seconds, then closes.
- [ ] **Folding sections**: the Dashboard and Route Planner sections start folded and open on a click of their title.
  - The Dashboard section holds the Exploration Value lines under its Dashboard button.
  - POI Reference has **Update POI** and a **Copy System** button and a details link under both the Canonn and the GEC result.
- [ ] **Exploration Dashboard**: **Dashboard** on the Exploration panel opens the window (check it opens whole on your screen and the tabs wrap).
  - It follows the system after a honk and scans, switches to Surface on landing and back to Orbit on lift-off.
  - The header buttons **Exploration overlays** and **Exobiology overlays** hide and show those cards with EDMCModernOverlay (a hidden card must clear at once, and come back when shown) without changing Settings.
- [ ] Settings -> WFMT -> General -> **Backup** -> **Back up my data** (Windows-tested only):
  - The folder dialog opens.
  - A `WFMT-data-<date>-<time>.zip` is written to the folder you pick and unzips to your JSON files plus `backup-info.json`.
  - With a Flatpak EDMC, pick a folder it can write to (or grant one with `flatpak override`). A folder it cannot write to should give a message in the tab, not a crash.
  - **Restore my data...** with that zip: it shows the file count, asks, says to restart EDMC, and after the restart your data is back (and `backups/pre-restore-<date>.zip` holds what it replaced).
  - **Cancel the waiting restore** removes it.
  - **Back up automatically** with a folder and 1 day: restart EDMC, wait a minute, and a `WFMT-data-auto-....zip` appears.
- [ ] Settings -> WFMT -> General -> **Help** (Windows-tested only):
  - **Report an issue** opens the GitHub bug report in your browser (check `xdg-open` works from EDMC, native and Flatpak).
  - Its Environment box reads like `Ubuntu 24.04, wayland` (distro, X11 or Wayland, `Flatpak` when it is one).
  - **Copy diagnostics** shows *Copied*, pasting gives the version lines and recent WFMT log lines, and the commander name reads `<commander>`.
  - Say which log path the Flatpak case used.

- [ ] Engineering window → **Engineers** tab (Windows-tested only):
  - The table has a **Where** column.
  - Selecting an engineer shows their find, invite and unlock steps under the table, and the grade-profit line sits below that.
  - Selecting Baltanos shows Deriso and "On-foot engineer". Terra Velasquez shows the "reported bugged" note.
  - The **Show** box offers Both / Bubble / Colonia: Colonia lists 8 engineers (`8 of 38 engineers`), Bubble 30, and the choice survives closing and reopening the window.
  - The table stays inside the window with the Where column, with no horizontal scroll.

- [ ] **BGS with EDMC closed over a tick** (Windows-tested only): note the BGS archive, close EDMC, do a few BGS actions (missions, bounties)
      in the game, wait for a tick to pass, start EDMC: the archived tick that just closed includes those actions, and EDMC's log has
      `BGS: rebuilt the closed period ... from the journals`.
- [ ] **Finished colonization build name**: a completed site in the Colonization sites window reads `Example Station`, not `Orbital Construction Site: Example Station`.

- [ ] **Ship planner** (Engineering window, Windows-tested only): export a build from EDSY or Coriolis as SLEF and **Paste from clipboard** (check the clipboard paste works on your desktop, X11 and Wayland).
  - The table lists each engineered module, and the summary line shows blueprints and crafts.
  - **Add plan to wishlist** puts them on the Wishlist tab (a pre-engineered module and an unknown item show their reason).
  - Set **Rolls per grade** to 2 and add again: the crafts double.
  - Tick **Subtract what my current ship already has** with a build for the ship you fly: what the ship holds is left out.
  - Nothing goes online.

- [ ] **Megaship scans** (Powerplay, Windows-tested only): in a Powerplay system, drop out of supercruise at a megaship and scan its datalink.
  - The Powerplay panel gains `Cycle N megaships: 1 (N merits)` and **Report → Megaships** lists it with its name and system.
  - Scanning it again changes nothing.
  - A scan at a station or a settlement adds nothing.
  - After restarting EDMC the list is still there.
  - Needs the Journal directory set on Linux.

- [ ] **Upgrade planner** (Engineering window, Windows-tested only):
  - Pick the Karma AR-50 from class 1 to 5: four steps, 12,500,000 credits, and **Add to wishlist** puts four entries on the Wishlist tab.
  - Press **Read my gear**: your suits and weapons are listed with their class (needs the Journal directory set on Linux). Picking one fills in its item, class and fitted modifications.
  - Pick the TK Zenith: the credits read "not recorded".
  - Pick a modification not offered for the item (they are filtered), and four at most.

- [ ] **Alert widths** (Windows-tested only; needs EDMCModernOverlay): **Test Notable** and a Discovery alert with a long capitalized name fit inside their cards at Default and Larger text; on the Missions overlay card a long station name drops to a line under its title.
- [ ] **Mission progress colors** (Windows-tested only): the Missions window's Progress column shows a bar and `N/total held` for a source-and-return mission, and rows and overlay lines change color as the hold fills.
- [ ] **Missions window and pinned missions** (Windows-tested only):
  - The **Missions window** button at the bottom of the Missions panel opens the window.
  - The Active and By place tabs fill and the times count down.
  - Select a row and **Pin / Unpin** puts a ★ on it and (with the Missions overlay on) a PINNED section on the card.
  - The text beside the arrows is bold and readable.
- [ ] **Best picks and Source commodities** (Windows-tested only; needs Trade lookups on):
  - Trade → Market, type a commodity, **Best picks** shows four labeled stations.
  - Missions → **Find sources** (bottom of the panel) fills the window as each commodity finishes.
  - **Copy system** puts the system on the clipboard, and **Cancel** stops it.
- [ ] **Missions overlay card** (Windows-tested only; needs EDMCModernOverlay): Settings → Overlays → Missions → **Test Card** draws a sample in the bottom-right corner.
  - With a few real missions and the card enabled it lists those for the system you are in under HERE and those for the system you target under NEXT, and times count down.
  - It sits where Overlay Placement says and does not widen as lines change.

## 6b. Fixed in the platform audit - please confirm

- [ ] Settings → Exploration → Auto-Honk, Operations → Screenshots and Operations → Inventory each show a **Works on:** line, green when
      it can work here and orange (with the reason) when it can't. Try it with and without `xdotool`.
- [ ] Take a normal screenshot and an Alt+F10 hi-res one: both are found, converted and named, and the
      hi-res one is treated as hi-res (the journal path is Windows-style, `\ED_Pictures\...`).
- [ ] Open every modal dialog without it erroring or staying behind the main window: Mining → Add/Edit
      Hotspot, Find Hotspots, Find Best Price, Check Ring Reserve, Import/Export Hotspots, and Operations →
      Add/Edit Ship Build. Each should stay on top and block the window behind it.

## 6c. Game mode and credits lines (under the mode buttons)

- [ ] Before logging in, the first line reads "Game mode: waiting for login…" and the second "Credits this
      session: waiting for your balance…".
- [ ] After loading into the game: "You are in Solo mode." (or Open, or Private Group with its name) and
      "Credits this session: no change yet". Both lines (and the Plugin version line above them) stay visible on every
      mode button.
- [ ] Switch through every mode, including Exploration and Trade: the whole block under the mode buttons stays visible.
- [ ] After earning a Powerplay merit, a **Merits this session: +N (+N merits/hr)** line appears under the credits line, on
      every mode except Powerplay, where the page's own lines show it; the rate appears after a few minutes. It is absent before the first merit.
- [ ] Earn or spend some credits: the second line changes to "+N cr earned" or "-N cr lost", and an hourly rate
      appears after a few minutes.
- [ ] Log out to the main menu and back in: the credits total carries on (same session).
  - Restart EDMC while the game is running: the mode line and the credits total come back.
  - Quit the game: the mode line goes back to "waiting for login".
- [ ] `session_credits.json` appears in the WFMT plugin folder, and a plugin update leaves it alone.

## 6d. Trade mode

Windows was checked as Trade was built. The boxes below are unticked so the list can be run again. Settings → WFMT → Trade first: tick **Enable Spansh trade lookups**.

- [ ] The **Trade** button appears with the others, and the **◀** / **▶** buttons at the top of the Trade panel are
      large and show their arrow glyphs (not empty boxes). The same buttons on Mining and Missions look right.
- [ ] **Session**: after docking, the ship and its pad size show; the hold line shows used, capacity and free
      tons. Buy and sell something: the profit lines appear. Refuel and repair: a **Net profit** headline appears
      with Fuel and Repairs lines under it. **Reset** clears it.
- [ ] Trade History: do some trading, press **Save session** (the message at the top says it saved), then **History**.
  - The window opens like the BGS and Powerplay ones, with the session in the drop-down.
  - Visit every tab: the tables fit the window with no column cut off at the right, and the numbers look right.
  - **Route** lists the stations in the order you flew them.
  - **Trades** pages with Earlier / Later.
  - Press **Save session** again after another trade: the entry updates (no duplicate).
  - **Copy summary** pastes into another app.
  - **Export log (CSV)** opens a file dialog and writes the file.
  - **Delete session** asks first.
  - **Reset** with unsaved trades asks whether to save first.
- [ ] A session spans play sessions: trade, log out of the game and back in (a new journal file), restart EDMC, then trade some more.
  - The Session page keeps one running tally through all of it (nothing starts afresh until you press **Reset**), and the numbers don't double.
  - After **Save session** the **Route** tab lists the stations from every part.
  - Also play a short stretch with EDMC closed, then start EDMC: that stretch is added the next time it sees you.
  - With two commanders, switching to the other and back leaves each one's tally as it was.
- [ ] Session page: the sections read "In your ship" (Ship hold, and the cargo with an "In hold"
      column; "Hold space" above it only with limpets, mission or stolen cargo) and, if you have a carrier, "Carrier cargo".
  - There is no unsold-stock list and no Clear stock button.
  - Buy cargo, then save the session: Trade History's **Stock & carrier** tab shows it under "Bought, not yet sold (journal estimate...)".
- [ ] Two computers: copy the other computer's newer journal files into this one's journal folder while EDMC is running.
  - Within a minute EDMC's log reads "Trade read N new or changed journal file(s)".
  - The trades, stock and carrier figure from those files appear (nothing doubles if you copy the same files again).
  - Press **Rebuild** on the Session page, type the date and time the session began (UTC), and check the totals against the other computer.
  - A carrier figure with a `~` in front means estimate: open Carrier Management and it goes away.
- [ ] Carriers (only if you have one): open Carrier Management once.
  - "Carrier cargo" (used / capacity, with the free tons) appears (separate from the "Ship hold" line).
  - Transfer cargo to it: the figure follows.
  - Restart EDMC: it comes back without opening Carrier Management again (this reads the journal folder, so it also checks the Proton journal path).
- [ ] Settings → Trade lists your commanders with a carrier choice each; choosing **None** hides the carrier.
- [ ] **Market**: click the Commodity box.
  - A suggestion list appears **under the box and does not steal the keyboard** (this is a borderless window, so check it stacks above EDMC under your window manager).
  - Typing narrows it.
  - Up/Down/Enter/Esc work.
  - Clicking a name fills the box.
- [ ] Layout: the Session, Routes and Market pages show orange section headings with a rule between them where a page has more than one list (a page with a single list has no heading above it), values on the right, and aligned number columns.
  - Long station names wrap instead of being cut off.
  - Nothing is clipped on the right edge or makes the EDMC window wider.
  - The buttons and (on Market) the Commodity box and **Sell** / **Buy** are **above** the results.
- [ ] Settings → Trade: untick **Include ground facilities** and **Include fleet carriers**; the results then show
      orbital stations only, and a search makes one request instead of two.
- [ ] The **Sell** / **Buy** buttons under the Commodity box: the chosen one is lit, switching clears the results,
      and the results heading says "Selling" or "Buying". All the page's buttons show their full labels (**Near me**,
      **Galaxy**, **Price finder**) with nothing cut off.
- [ ] **Near me** and **Galaxy** each return results for a common commodity (try Gold and Liquid oxygen).
  - Each station says **orbital** or **ground** and its type.
  - A fleet carrier appears in its own section, not mixed with stations.
  - Stations without a pad for your ship are missing.
- [ ] **Routes**: **Find routes** shows "Asking Spansh..." with a counting timer, and a route within a couple of
      minutes. **Cancel** stops it. **Copy next system** puts the system name on the clipboard.
- [ ] **Hops** button cycles 2, 3, 4, 5.
  - **Round trip** (docked at a normal station, not a carrier) answers in about 20 seconds with up to three pairs, each showing what to carry out and back. Both legs are loaded.
  - A route's page shows an estimated profit per hour and supply/demand per hop.
- [ ] Settings → Trade route filters: set **ignore prices older than** to a small number of hours and tick **Routes may use
      systems that need a permit**; **Find routes** and **Round trip** still answer (an old-price filter can leave fewer results).
- [ ] No Python errors in the EDMC log, and the EDMC window did not get wider when you opened Trade.

## 7. BGS

- [ ] The BGS panel's gray line shows "Last tick: ..." within a few seconds (network call works).
- [ ] With the Journal directory set, the log has "BGS journal replay done for [CMDR]" and the totals
      cover the whole tick. With it cleared, the log says the replay was skipped and why.
- [ ] **Report** (view BGS report) opens; the tick drop-down, the tabs (full system names, wrapping onto a second row
      when there are many), **Pin**, **× Close tab** and the footer key all render, with no missing glyphs.
- [ ] **Show a system**: typing narrows the list while you keep typing (the list must not steal the
      keyboard), the arrow shows every system, Up/Down/Enter/Esc work, clicking a name adds its tab.
- [ ] Pins and closed tabs survive restarting EDMC.

## 7b. Catching up after EDMC was closed (Windows-tested only)

All of this is platform-neutral Python reading the journal folder, but it has only been tried on Windows.

- The Linux risks are the Journal directory (section 0), file modified times on the Proton prefix, and large journal folders.
- To test, play a short session with EDMC **closed** (or close it mid-session), then start EDMC and look at each:

- [ ] **Missions**: accept a mission, close EDMC, start it mid-game: the mission shows without logging in again.
  - Hand a mission in with EDMC closed: it disappears after the restart.
  - (An expired mission with no journal entry can stay until the next login; that is expected.)
- [ ] **Colonization**: deliver cargo to a depot with EDMC closed, then start EDMC: the site's figures include the
      delivery once. Restart EDMC again: nothing changes (no double count).
- [ ] **Codex**: find a Codex entry with EDMC closed, start EDMC: the summary line goes up by one.
- [ ] **Boxel Survey**: jump to a few systems with EDMC closed; after a restart the visited count (Settings → Boxel
      Survey) includes them.
- [ ] **Trade**: the route start (Routes page) is the last real station you docked at, also after a restart and after
      switching commander; carrier tritium, location and orders appear under the carrier lines if you have one.
- [ ] **Inventory**: restart EDMC while on foot or with items in the ship locker: the bars fill without a login.
- [ ] **Exploration Value**: after a restart mid-system, "System bodies" shows scanned of total, and "Last data sale"
      shows the last sale of the session.
- [ ] Startup is not noticeably slower, and the EDMC log has no Python errors from `colonization_catchup`,
      `journal_files`, `visited_systems`, `codex_backfill` or `journal_scan`.

## 7c. Per-commander data (Windows-tested only)

Nothing should be shared between commanders.

- Needs two commanders (or one commander and a second journal), on Linux with the Journal directory set (section 0).
- The code only uses JSON keys, UTF-8 files and `os.replace`, so the Linux risks are the journal folder and the order file modified times give.

- [ ] **Mining**: save a hotspot as commander A; log in as B: the Mining Book shows none of A's. Save one as B, log back
      in as A: only A's. The coverage map follows the same way.
- [ ] **Mining Book**:
  - **Market research** (after ticking *Enable Spansh best price finder*) lists buyers for a system where you have saved hotspots.
  - **Share line** on a positioned hotspot and **Paste spot** (refused for a spot within 100 m of one saved).
  - **Stops** lines and dashed rings on the map, and `you are here` with the Rhino within 175 m of a deposit.
  - A Depleted mark stays and the card says how long ago (set Settings → Mining → refill days to see it come off).
  - Nothing here is OS-specific; check the Book fits and the text is readable.
- [ ] **Codex**: log in as each commander in turn: the details window subtitle names whose tally it is, and the counts
      differ. On the first start, each commander's tally is built once from their own journals (the
      panel says so while it reads).
- [ ] **Powerplay**: the Sessions window's History tab and its total show only the commander you are playing.
- [ ] **Boxel Survey**: the "Surveyed: N systems" line and the exported CSV change with the commander.
- [ ] **Trade**: switching commander clears the previous one's ship, hold and route results from the Session page; the
      History window opens on the active commander.
- [ ] A commander typed in another case (the journal can write `EXAMPLECMDR` for `Examplecmdr`) is the same commander.
- [ ] Nothing under the plugin folder is named after a commander except the `mining_sessions/` archive files.

## 7d. Colonization FC column, shopping-list overlay, start-up commander (Linux-tested only: check on Windows)

Written and tried on Linux (Flatpak EDMC, Proton game, EDMCModernOverlay). The code is platform-neutral Python, but none of it has been run on Windows yet. Needs a commander with a fleet carrier and a registered construction site.

- [ ] **FC column**: the Colonization Sites window shows an FC column for a commander with a fleet carrier (and not for one
      without), and it follows a transfer made at the carrier. Restarting EDMC keeps the figures and never counts a
      transfer twice. A commander set to None in the Trade settings gets no FC column.
- [ ] **Window follows the commander**: with the window open, log in as another commander; its sites change.
- [ ] **Start-up commander**: start EDMC with the game closed.
  - The Operations panels (Colonization, Codex, Ship Builds, Trade) show the last commander instead of "waiting for commander login".
  - The EDMC log has "No game running at start-up; restored commander ..." (about four seconds after start).
  - Then log in as someone else: everything switches.
- [ ] **Overlay card** (Settings → Overlays → Colonization: tick the overlay option; **Test Overlay** draws a sample): the table shows
      Commodity, Required, Acquire, FC and Cargo, with a tick when the hold covers a row, and a remaining/trips footer.
- [ ] The card appears:
  - in a commodity market at a station
  - at your own carrier in the station-services screens (the game writes no `Market` event for a carrier's market)
  - with the right-hand cockpit panel open when docked at the carrier (the cargo transfer)
  - in Carrier Management
  - docked at a construction site
  - It goes when you leave, and the **Always show the shopping list** tick (Settings → Overlays → Colonization) forces it on and off.
  - The EDMC debug log lines "Colonization overlay ..." say what was decided and why.
- [ ] Rows left at the default list every commodity not yet covered; the card fits on screen from the default position (20, 300).
- [ ] **List (overlay card):** with **To buy** (the default) a commodity the hold plus the carrier cover is left out and the footer still counts it; **All** brings the covered rows back; **To haul** lists only the covered rows not yet aboard in full (put everything on the carrier and check that the card still lists them, and that a row drops off once its whole need is in the hold).
- [ ] **The hold follows a purchase:** buy a tracked commodity at a market. The In Cargo figures (Sites window, Colony page and card) change within a couple of seconds. WFMT reads `Cargo.json` beside the journals, so check the journal folder is found on Linux/Proton; if the file cannot be read, EDMC's cargo state is used.
- [ ] Windows paths: `Status.json` reports the same `GuiFocus` values (5 in the services screens, 1 for the right-hand panel).

## 7e. Colonization Sites window: sites list, totals, Where to buy (Windows-tested only: check on Linux)

Written and tried on Windows. The code is platform-neutral Python and Tk, but the window layout has only been seen on Windows. Needs a commander with at least one registered construction site and an internet connection.

- [ ] The window opens at about 1300 x 780 with the sites on the left and the detail on the right; nothing is clipped at
      its minimum size (1300 x 640), and the commodity table has the whole height of the right-hand side.
- [ ] Picking a site shows its progress bar, the six totals, and its commodities; the Filter box, the **Show** dropdown
      (All, To buy, To haul) and the column headings (click, click again to reverse) all work.
- [ ] **Buy Trips and Haul Trips** (needs a fleet carrier with stock stored on it): a commodity fully on the carrier shows Buy
      Trips 0 and a Haul Trips above 0; the totals show **t on your carrier**, **trips to buy** and **trips to haul**.
- [ ] **Row colors**: a commodity row turns green when the hold plus the FC column covers the site's remaining need
      (exactly equal is green), orange when together they are more than needed, and keeps the normal look while short.
      The tint stays visible, only lightened, when the row is hovered or selected.
- [ ] **Where to buy** (its own window): pick a commodity row, press **Where to Buy** in the header, then **Find nearest**:
      the window opens with the site's system filled in, results appear, closest first, the button is disabled while it
      searches, and the window stays responsive. Pick another row and the open window's heading follows; closing the Sites
      window closes it; its size and position are remembered.
- [ ] **Landing pad**: Any size lists stations whose largest pad is Medium or Small; Large only lists none of those.
- [ ] **Exclude fleet carriers** (off by default, so carriers are searched and listed): ticked, no carriers are listed; unticked, a **Fleet carriers** group follows the stations.
- [ ] **Only stations with enough stock**, **Only stations with a shipyard** and **Arrival within** (all off by default): after a search each one removes the stations that do not qualify from the lists and the route at once, the commodity heading says **left out by the filters** when none are left, and the note counts what was left out. The window is still laid out cleanly at its minimum size.
- [ ] **Exclude surface ports** (off by default): ticked, planetary stations disappear from the lists and the route at once, and a commodity sold only at surface ports (none at an orbital port in range) shows an **Only at surface ports, so left out of the route** group, one row per commodity, at the top of the route block and **surface ports only (left out)** on its heading; unticked, the group reads **Only at surface ports** and the item is marked under its stop. The choice is remembered.
- [ ] **Following purchases:** after Find all, put some of a listed commodity in the ship's hold (or on the carrier); the route and lists shrink by that much within a moment, and a commodity you have in full disappears, with no new search.
- [ ] **Window positions:** with a monitor to the left of the primary, move a WFMT window onto it, close it and reopen it: it comes back on that monitor.
- [ ] The **Planetary** column says Yes for planetary ports, outposts and settlements and No for orbital stations and
      carriers; the whole results table fits at the window's minimum width.
- [ ] **Here** puts the system you are in (the last system EDMC saw) into Around. **Copy System** copies the selected row, and so does clicking a result row (a station or a route stop) at once.
- [ ] With no network, the panel says the search failed and the button comes back.
- [ ] **Find all**: lists a heading per commodity still to buy with up to 5 stations under each; the
      button reads **Stop** while it runs and stopping keeps what was found; the window stays responsive.
- [ ] **My Projects (needs the internet):** press **Projects** on the Colony page (or **My Projects** in the **Raven Colonial** menu).
  - A window lists your Raven Colonial projects with building, progress and tons still needed; the subtitle adds up the counted ones.
  - Double-clicking a row changes whether it counts, and the subtitle says there are unsaved changes.
  - **More** has Copy Shopping List, the two Open items, Set as My Primary and Save Counted List; the last two ask first and refuse while the master switch is off.
- [ ] **Planned Builds (needs the internet):** select a site, press **Planned Builds** (in the **Raven Colonial** menu).
  - A window lists Raven Colonial's sites for its system (building, planned, complete), marks the ones you track and shows each planned or building site's **Full cost**.
  - Clicking a row names its biggest commodities.
  - **Refresh** works.
  - With no network it says it could not reach Raven Colonial.
- [ ] **Suggested route:** after Find all, a shaded "Closest way to buy everything" block sits above the per-commodity lists, with a "Suggested route" group of numbered stops and, under each, the commodities to buy with their price and supply; **Copy Route** puts plain lines on the clipboard. A plain Find nearest shows no such block.
- [ ] **Remembered choices**: change Within, Sort, Landing pad, Exclude fleet carriers and Exclude surface ports, run a search, close and reopen
      the window: the same choices are back.
- [ ] **Only what [station] sells**: grayed out until you open a station's commodity market; then it names the station and
      narrows the list to what that market has for sale (in stock, with a buy price); it unticks itself when you undock.
      (`Market.json` lives in the journal folder: check EDMC's journal path on Linux/Proton.)

## 7e-1. Rescan Journals (Windows-tested only: check on Linux)

- [ ] With a fleet carrier and some transfers in the journals, **Rescan Journals** in the Colonization Sites window rebuilds the FC column
      from the last 30 days; the status line names the commodities and tons. Pressing it twice gives the same figures.

## 7e-2. Raven Colonial sharing (needs a Raven project for a site; Windows-tested only: check on Linux)

- [ ] **Settings → Colonization → Raven Colonial** has a master switch and two checkboxes (all off, the two grayed out until the master is ticked) and a masked key field. With the master off, Report Complete to Raven refuses.
- [ ] With the first on, a delivery at a construction site Raven has a project for appears on Raven; with it off, nothing is sent.
- [ ] **Raven Progress** shows Raven's remaining need beside WFMT's for the selected site, including one still being built.
- [ ] **Test key** (beside the key box) says the key is accepted, with Raven's name for you, or that it was not accepted.
- [ ] The link under the key box opens ravencolonial.com/user in your browser.

## 7e-3. Overlay Placement: Show checkbox (Windows-tested only: check on Linux)

- [ ] Each row on **Overlays → Overlay Placement** has a **Show** checkbox. Unticking one (then OK) hides that display; ticking it brings it back
      where it was. **Reset all to defaults** ticks them all.

## 7e-4. Colonization Sites window header (Windows-tested only: check on Linux)

- [ ] The header has **Copy Shopping List**, **Where to Buy**, **Rescan Journals**, **Raven Colonial ▾** and **Manage Sites ▾**. The two menus open under their buttons,
      are readable (dark colors) and close when you click elsewhere or pick an item.
- [ ] **Raven Colonial ▾** lists My Projects, Planned Builds, Raven Progress, Open Selected Build on Raven, Open This System on Raven, Raven Colonial
      Website, Create Project on Raven, Report Complete to Raven and Mark Plan Entry Demolished; the three Open items open the right page in your browser.
- [ ] A site you renamed in the game takes its new name after you dock at it again.

## 7f. Overlay Placement and the Overlays settings tab (Windows-tested only: check on Linux)

Written on Windows against a 3840 x 2160 screen in EDMCModernOverlay's fill mode.

- The logic is platform-neutral.
- These have not been seen on Linux:
  - reading the screen size from inside the Proton prefix (and the overlay's log)
  - the display scaling under XWayland
  - how the overlay maps its canvas and sizes there

- [ ] **Settings -> Overlays** has twenty-one tabs: Overlay Connection, Appearance, Overlay Placement, Hide overlays, Colonization, Discovery,
      Inventory, Interdiction Warning, Flight Alerts, Route, System targets, Body info, Exobiology, Expedition Log, Powerplay, Missions, Landing,
      Surface Compass, Mining, Notable Bodies and Screenshots. General has no overlay tab.
- [ ] **Default spots:** with every box ticked, **Show placement preview** on a screen of 1920 x 1080 or more draws the boxes
      without any two overlapping (Interdiction at the top, Discovery below it, Notable find at the top right above Inventory, Flight
      alerts on the right below Inventory). On a smaller screen some may overlap; that is expected, and moving them on the tab fixes it.
- [ ] The Overlay Placement tab's info line shows your real screen size and display scaling, from the EDMCModernOverlay log or `DisplaySettings.xml`.
  - If it says "game files not found", note the Wine/Proton prefix path and report it.
  - If it says "log (window size only; DisplaySettings.xml not readable)" the size is right but the scaling is not read.
    - Set **Display scaling** by hand.
    - For a Flatpak EDMC check permission 5 in the Linux guide.
  - Under XWayland or Wayland scaling the overlay's log is the best source; check its numbers match what you see.
- [ ] It shows the overlay mode EDMCModernOverlay uses (fit or fill).
- [ ] **Show placement preview** draws a labeled box for every display, at its real size, all on the screen.
- [ ] Change a display to **Bottom left** with offsets 20 / 20, press OK, then **Test Overlay** (or the feature's test
      button): it appears in the bottom left corner of the game screen.
- [ ] A display set to **Bottom left** with offsets 40 / 40 sits 40 pixels in from the bottom left corner of the screen.
- [ ] A display set to a **Right** spot (Inventory pickups, Screenshot messages) sits against the right edge of the screen at its full width, not short of it.
  - Settings -> Overlays -> Overlay Placement -> **Show placement preview** shows the same.
  - WFMT sets an offset on that display's EDMCModernOverlay group. If it sits short of the edge, the EDMC log has "Could not set the EDMCModernOverlay offset".
  - Unticking **Carry displays on the right to the screen edge** puts them back at the limit.
- [ ] A position set by exact X/Y numbers shows as **Exact position** with the same numbers.

## 7g. Overlay Appearance (Windows-tested only: check on Linux)

- [ ] **Settings -> Overlays -> Appearance** exists, with a Color scheme menu and a Text size menu (Default, Larger; Larger is the starting value). Pick each size and press **Show sample**: no text may run past its box.
- [ ] **Show sample** draws the Colonization card in the game in the picked scheme.
- [ ] At **Larger** (the starting size), each display (Colonization, Discovery, Notable, Landing, Inventory, Mining,
      Screenshots) keeps its text inside its border without wrapping. Note any that do not, with the font and Proton/Wine setup.
- [ ] Changing the scheme recolors every display; Interdiction stays red.
- [ ] After OK, the choices are still set when Settings is reopened. **Reset appearance** restores Elite orange and Larger.

## 7h. Colonization mode (Windows-tested only: check on Linux)

- [ ] The button row has a **Colony** button (eight buttons); the panel is not noticeably wider than the other modes'.
- [ ] Colony shows **Current project** for your newest active site and a **History** block; Dashboard opens the sites window, and
      Overlay toggles the overlay card (lit while on).
- [ ] Without a fleet carrier there is no On your carrier row, Trips left reads like "3 loads of 400 t", and the sites window has a single
      Trips column (Commodities and Trips left go once the site has nothing left to deliver). With one, On your carrier is shown and Trips left reads "N to buy · N to haul".
- [ ] Overlay Placement tab, with two commanders seen: **Copy all overlay layouts and settings from** lists the other commander; **Copy** then **OK** gives this commander the other's cards, placement and look (the overlay redraws); **Cancel** changes nothing; the other commander's choices are unchanged. With one commander the row is not shown.
- [ ] The Colony page is in sections: the project (Delivered, Still needed), **What you have** and **To finish the build**; there is no Next line. With no site under construction it lists the last 5 completed sites, newest first, as "Name (System) - date".
- [ ] After delivering cargo to a depot, "You delivered" and "Recently" go up by the same tons, and again after restarting EDMC
      (no double counting).
- [ ] After a build completes, History's "done" count goes up.
- [ ] **History rebuild:** on the first start, the log says "Colonization history rebuilt for [CMDR]"
      and the History note's "Counted since" date moves back to the oldest delivery in your journals. Restarting EDMC does not
      rebuild again, and the totals do not double. (Needs Elite's journal folder set; on Linux that is inside the Proton prefix.)
- [ ] **Claims line:** after the history rebuild, the History block has a "Claims" line (for example "5 systems claimed · 5 beacons") for a commander who has claimed systems.
- [ ] **History chart:** the "Last 14 days" line draws a row of blocks of different heights (no empty boxes) and "Busiest site" names a site.
- [ ] **Overlay card footer:** with a fleet carrier it reads `N remaining  N to buy  N to haul`; without one, `N trips to finish`.

## 7i. Boxel Survey catch-up, Colonization and Planned Builds (Windows-tested only: check on Linux)

- [ ] **Boxel Survey catch-up:** scan a few bodies with EDMC closed, start EDMC: Settings -> Boxel Survey shows them, and a second
      restart changes nothing. (Needs the journal folder; on Linux that is inside the Proton prefix.)
- [ ] **Powerplay cycle tally:** the panel shows **Cycle N merits** and **Cycle N CP** under the session lines, and they are still
      there after restarting EDMC.
- [ ] **Trade, Round trip:** each pair lists its loads with prices, profit per ton, supply and demand; docked at a fleet carrier
      the result says it started from the carrier. The Trade setting for the search radius changes how far it looks.
- [ ] **Trade, Session page:** ends with the game's career totals for the commander.
- [ ] **Waypoint Route, From plotted route:** plot a route in the game, press the button: its systems are added.
- [ ] **Community goals:** the Community Goals page lists payouts under **Paid out**.
- [ ] **Colonization, Find all:** the results begin with a suggested shopping route, and **Copy Route** puts it on the clipboard.
- [ ] **Planned Builds:** the **Full cost** column fills, the window's subtitle adds up the planned builds, and clicking a row names
      the building and its five biggest commodities.

## 7j. Plugin version line (Windows-tested only: check on Linux)

- [ ] The first line under the mode buttons reads **Plugin: vX.Y.Z** above the game-mode line, and does not widen the panel.
- [ ] After an automatic update is downloaded it reads **vX.Y.Z download - Restart EDMC** in bold black on orange (check the Default,
      Dark and Transparent themes); after the restart it reads **Plugin: vX.Y.Z (updated)** in green for about 15 seconds.

## 7k. Mining simulation and the Surface Live radar (Windows-tested only: check on Linux)

The Surface Live radar has not been looked at on Linux. The simulation shows it without the game.

- [ ] Settings → Mining → Simulation → **Surface Live (pretend Rhino)** opens a window titled "Surface Mining Live (simulation)" with *SIMULATION* in its subtitle.
- [ ] The radar draws on the left. Check each of these:
  - range rings
  - a trail of ground driven
  - a Rhino arrow that moves and turns along a ring 3.75 km round the middle of a marked location (the 2 km range, the default, shows an arc of it)
  - two marked locations (a cross and a circle through its border; one with no border)
  - five placed deposits with their first letters (one depleted, a hollow ring; a sixth, saved without a position, is listed in the lines on the right and not on the radar)
  - a line to the nearest deposit with a distance
  - Note whether the labels look right (the radar uses Pillow's built-in font).
- [ ] The five range buttons under the radar resize the view, and the choice is kept. Resizing the window resizes the radar and never widens it past the window.
- [ ] The lines on the right update about once a second (refined counts, cargo, nearest marked location, nearest deposit) without flicker, and wrap inside the window.
- [ ] **Mark center** and **Mark border** add or finish a marked location on the pretend ground; **Add hotspot** opens the add-hotspot window filled with the pretend position and a saved deposit shows up on the radar. There is no **Import/export**.
- [ ] The radar also shows:
  - orange dashed **drive rings** round the first marked location (2 km, then 4.5 km on the border)
  - two violet **Stop** circles
  - with a target commodity set in Settings → Mining (try Painite or Platinum), a bright line to the nearest saved deposit of it with the nearest of any kind dotted
  - Press **Help** and check each entry matches what you see, and that the window and its text are whole.
- [ ] **Save map** opens your desktop's save dialog (check it appears in front of the window and takes clicks), writes a PNG, and the picture opens in an image viewer with the title, the marks and the legend legible.
- [ ] Close it, open the real Live window from the Mining page, and check none of the pretend deposits or marks are there.
- [ ] Report the distro, desktop, X11 or Wayland, native or Flatpak EDMC, and any `Plugin "WFMT" failed` or traceback lines in EDMC's log.

## 7k2. The navy look (new, not run on Linux)

- [ ] Open the Sites window, Inventory, the Exploration Dashboard and the Mining Book. Surfaces are navy, not gray; the window title is gold; section labels and table column headers are cyan; the footer message is bright yellow, and green after something succeeds. Nothing is hard to read, on Wayland or on X11.
- [ ] The Colonization overlay card's third column is headed **Acquire**.

## 7k4. Color themes (new, not run on Linux)

- [ ] Press the theme name at the right end of a window's bottom line and choose each of Cyan, Amber, Green and Navy: every open WFMT window recolors at once and stays readable, on Wayland or on X11. The drop-down menu is drawn in the theme's colors.
- [ ] Settings → WFMT → General → Window → Color theme shows the same name; the choice is kept after a restart, and a window opened afterwards uses it.
- [ ] The stat tiles at the top of a dashboard keep their size when **A+** is pressed.

## 7k5. Colonization Archive and the footer message (new, not run on Linux)

- [ ] In the Sites window use **Manage Sites → Archive Finished**: finished sites leave the list and the status line counts them. **Show Archive** lists them with result, dates, time taken and tons needed; selecting one lists its commodities; **Restore**, **Copy Summary** and **Manage → Remove Permanently** (asks first) work. Restart EDMC: the archive is still there. Nothing is cut off at the window's smallest size.
- [ ] The footer message is yellow on Navy, Cyan and Green and cyan on Amber, and green after something succeeds; the note under the Where to buy buttons is in that color while a search runs.
- [ ] **Create Project on Raven** opens its dialog centered and inside the screen on Wayland and on X11.

## 7k3. Text size and column fit (new, not run on Linux)

- [ ] Open the Sites window and press **A+** twice at the right end of its bottom line: the text grows in every open WFMT window, tables stay aligned and nothing is cut off. **A-** shrinks it, and the size is kept after a restart.
- [ ] Settings → WFMT → General → Window → Text size shows the same number; typing one from -2 to 6 and pressing OK applies it.
- [ ] Short columns are narrow and a long name column takes the spare width.

## 7l. Shortcuts: chat commands and the Settings page (Windows-tested only: check on Linux)

Keyboard shortcuts are Windows only; the chat commands are the same on both systems and read the journal's `SendText` line.

- [ ] Settings → General → Shortcuts lists six actions with the key choices **grayed out**, the chat commands (`!wf center`, `!wf border`, `!wf rig`, `!wf zoom`, `!wf live`, `!wf overlays`) and a **Chat commands** tick box (off by default). The page is whole at the default Settings size and nothing is cut off.
- [ ] If the page says it could not find Elite's controls file, note it (the Linux binds file is looked for inside the Proton or Wine folder).
- [ ] Tick **Chat commands**, press OK, then in Elite's chat (a channel with nobody else in it) type `!wf overlays` and press Enter: the overlays hide; type it again: they show. Note how long after pressing Enter it happens, and with a Flatpak EDMC whether it works at all.
- [ ] With the simulation open (Settings → Mining → Simulation) or on real ground:
  - `!wf zoom` steps the radar's range (50 m, 250 m, 500 m, 1 km, 2 km, back).
  - `!wf live` raises the Live window.
  - `!wf center` / `!wf border` say what they did in the window's status line.
- [ ] A message that is not exactly a command (`!wf center now`, `hello`) does nothing, and with the tick box off nothing happens.
- [ ] A sound plays when a command worked (needs `canberra-gtk-play` or `paplay`), and none when it did not.
- [ ] Report the distro, desktop, X11 or Wayland, native or Flatpak EDMC, and any traceback in EDMC's log.

## 7m. What pays (Windows-tested only: check on Linux)

- [ ] With *Enable Spansh best price finder* ticked (Settings → Mining) and a few saved deposits, **Book** → **What pays** opens a window.
  - *Near* holds your system, and *Within 100 ly* is chosen.
  - The table fills in one commodity at a time and is then ordered best price first.
  - Nothing is cut off at the default size.
  - **Help** opens and closes.
- [ ] A commodity nobody pays for shows *No station found*; **Copy report** puts a numbered ranking on the clipboard; changing *Near* or *Within* and pressing **Search** asks again.
- [ ] With the switch off, the button says so in the Book's status line and asks nothing.

## 7n. Get body info and a body's size from Status.json (Windows-tested only: check on Linux)

- [ ] With *Enable body lookup* ticked (Settings → Mining), in a system you are in, **Book** → **Get body info** says it is asking EDSM and Spansh and then how many landable bodies it listed and added, with sizes and mining-location counts.
  - The Book's body list gains them and nothing already there changes.
  - Straight after starting EDMC with no jump or login yet, it says Spansh was not asked.
  - With the box unticked it says to turn the setting on and asks nothing.
- [ ] After **Get body info** in a system, restart EDMC (or jump away and come back): the Book's body list shows the same bodies again with no new request, and a body your journals give later replaces its remembered entry.
- [ ] FSS-scan a body that has mining locations: its count appears in the Book's list without a detailed scan, and a later detailed scan changes it only if the numbers differ.
- [ ] Landed on a body with no `Scan` event in your journals, launch the Rhino: the green ground trail starts on the Live radar and **Mark center** says "Center marked" (the body's size comes from `Status.json`).

## 7o. The Mining radar over the game (Windows only: on Linux, check that it does nothing and says so)

- [ ] Settings → Overlays → Mining shows **Show the Mining radar over the game**, a size, an opacity and **Test radar**.
  - Pressing **Test radar** says it needs WFMT's built-in overlay (Linux has EDMCModernOverlay only) and draws nothing.
  - The page is whole and not cut off.
- [ ] With the box ticked, launching the Rhino on Linux draws nothing over the game and raises no error in EDMC's log (the Surface Live window is the way to see the radar on Linux).

## 7p. Rig placed and the rig bands (Windows-tested only: check on Linux)

- [ ] In the Surface Live window (or the simulation, which has three rigs already):
  - **Rig placed** says `Rig N noted here.`
  - Pressing it again at the same spot says it is already noted.
  - **Clear rigs** forgets them.
  - With a rig gap set in Settings → Mining, a band of that radius appears round each rig (filled while you are inside it, an outline when you are clear).
- [ ] `!wf rig` typed in Elite's chat does the same (with chat commands switched on); the sound plays when it worked.

## Reporting

Open an issue with your setup line, the failing step number, and the log excerpt.
