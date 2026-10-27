# To do

Open work and open questions.

- Completed work is recorded in [CHANGELOG.md](../CHANGELOG.md).
- Current test status and working rules are in [STATUS.md](STATUS.md).
- Step-by-step Linux checks are in [LINUX_TESTING.md](LINUX_TESTING.md).
- Bug reports and suggestions are welcome on the [Issues page](https://github.com/rwharpernc/wayfarers-multitool/issues).

## In progress

Work that is under way, being researched, or waiting on a decision. Items are listed once, here, and not again below.

### Local star index: neutron stars built, the rest open

- Built: the Online lookups page has a Local star index group.
  - It downloads Spansh's `systems_neutron.json.gz` when the player asks.
  - It builds a local index (about 100 MB) and uses it for N.S., falling back to the Spansh search.
  - Update now fetches the small 1-day or 1-week file and merges it in (the full file only when the index is more than a week behind).
- Still open:
  - Out of scope: a white dwarf local index. W.D. keeps asking Spansh, which publishes no white dwarf dump (checked 2026-10-23) and offers only the whole galaxy, far too large to download.
  - Keeping the secondary-star check's per-system lookups, since the dumps list only a system's main star.

### Ship Builds and Coriolis / EDSY: first step built, next steps open

- Built: the Ship planner reads a pasted Coriolis import link or EDSY `#/I=` link as well as SLEF.
  - It copies or opens a link that shows the selected build on either site (`ship_links.py`; offline, the browser makes the request).
- Still open:
  - Confirm in a browser that EDSY opens a link WFMT makes.
  - Whether to also read EDSY's `#/L=` and Coriolis's `/outfit` links (they need the sites' own identifier tables).
  - Built: the Ship planner has an In storage column. A stored module matches on the same module; it is Yes with the planned engineering at the level or above, and Partly otherwise. Only storage counts, not modules fitted to a ship.
  - Open: whether the plan should also subtract the engineering of a matching stored module, as the current-ship option does.

### Expedition page and its workflow: built, to try in the game

- Built:
  - The Route Planner window's **Start expedition** makes an expedition from the route, starts it and starts a linked Expedition Log run (a setting).
  - **Review** opens the Expedition window on it.
  - Pause, Resume and Stop agree between the planner and the Log.
  - **Road to Riches** and **Exomastery** can start the plan at once.
  - The Expedition window, the Route Planner and the Expedition Log are the Plan, Route and Log tabs of one window (`expedition_hub.py`), and the panel's two rows are one Expedition section.
- Settled: **Start expedition** does not switch tabs.
  - It is pressed on the Route tab of the open window.
  - The status line says what happened, and **Review** goes to the Plan tab.
- Decided 2026-10-23: reopening a stopped expedition (the Route tab's Start, or the Log's Resume) picks the clock up from the time it stopped at, so the time stopped is not counted. To try: stop an expedition, wait a minute, start it again, and check the clock carries on from where it stopped.

### Next area of work: Mining, including surface mining

- A desk review (2026-10-21) compared the following against what the journal offers:
  - the Space and Surface pages
  - Mining History
  - the Mining Books
  - the live window
  - the guide
- It found the coverage broad. The run's ore, limpets, rates, hold, targets, missions, sales, history, hotspots, prices and reserve lookups are all there.
- It found some candidates, none confirmed by play. Profit, the time until the hold is full and the price against the galactic average are built (see their steps in the checklist below).
- **Not assessed without playing:** the Surface (Rhino) tools and the radar over the game, the overlay layouts, and whether the Space and Surface pages show too much or too little at a glance.
  - Those need your impressions from a play-through (the checklist below covers them).
- Not subtracted from *After limpets*: fuel, repairs and ammunition. The journal records them; they are not tied to a run the way launches are.

### To review: window layout on real screens, and the table text caps

- Done: every pop-out window, dialog and the screenshot preview is on the shared window kit.
  - Each has been opened headless at its minimum and at a wide size with long names (`tests/window_fit_check.py` and the `window_fit_*` smoke tests).
  - The clipped, squeezed or overflowing cases that found are fixed.
- Still to do by eye: the windows at 100, 150 and 200 percent display scaling, and on Linux. The cases to look at:
  - the wrapped stat tiles in Mining History, the Surface Mining Book and the Exploration Dashboard
  - the Add/Edit forms that grow to fit their hints
  - the Plan dialog's height on a 768 px screen
  - the screenshot preview header
- Decided 2026-10-23: table text caps.
  - A stretch column is clipped to the width it gets (up to 300 characters), so its own cap no longer matters, and that covers most of the columns that were listed.
  - The caps were raised to 60 on the remaining name columns that do not stretch: Missions (Faction, Go to, Station), Source commodities (System, Note), Ship Builds (Ship, Role, Site) and My Codex (First found in).
  - To check by eye: a long faction or station name in those windows at a narrow size.
- These stay as they are:
  - The tooltip, the system name suggestions and the commodity type-ahead are small pop-ups drawn in EDMC's own theme because they sit on its main window.
  - The EDMC Settings pages follow EDMC's look.

### Shortcuts: built, to try in the game

- Settings → General → Shortcuts has six actions: CTR, BRD, Rig placed, radar range, the Live window and hide overlays.
  - Each has a Windows key combination (Ctrl+Alt+Shift plus one key, checked against Elite's own controls).
  - Each has a chat command (`!wf center` and so on, Windows and Linux; see [Shortcuts](guide/shortcuts.md)).
- Still to decide or check:
  - Whether more actions deserve one (start or pause an expedition, copy the next system), and whether a Linux desktop binding that runs a command WFMT listens for is worth adding beside the chat commands.
  - On Windows, in the game: each combination works while Elite has the focus, the sound plays, and nothing else reacts to the keys.
  - On Linux: the chat commands work with a Flatpak and a native EDMC, and the journal's `SendText` line arrives in time (steps in `docs/LINUX_TESTING.md`).

### Data verification

- [ ] **Data verification.** Work through [data_verification/verification_checklist.csv](data_verification/verification_checklist.csv) (356 rows, for a spreadsheet): what is missing and what is carried from other authors' work but not yet checked in the game.
  - Checked against journals: the carrier jump fields, the Status.json Destination and (2026-10-23) the Route Planner's supercharge multipliers (V-0351) are Verified - journal.
  - V-0076, V-0077, V-0092, V-0093 and V-0097 carry what the journals showed.
  - The open findings are V-0350 (two costs for one synthesis), V-0352 (the drive table: matches Coriolis, and the fuel formula reproduces recorded jumps, but unengineered optimal mass and maximum fuel need the outfitting screen) and V-0353 (a flown route).
  - What is left needs the game: 233 Odyssey stat rows, the Engineers panel rows and the static-data spot checks.
  - Mark each row as it is verified. Change the method statement in [ATTRIBUTIONS.md](ATTRIBUTIONS.md) to the past tense only when none are left.

### Odyssey upgrade planner

- [ ] **Odyssey upgrade planner, next step:** a stat preview.
  - The stat tables are not available as open data, so they are being gathered and checked in the game ([ODYSSEY_STAT_COLLECTION.md](ODYSSEY_STAT_COLLECTION.md); the sources looked at, with their licenses, are in [ODYSSEY_STAT_DATA.md](ODYSSEY_STAT_DATA.md)).
  - The preview itself waits for that data.
  - Another possible shortcut is a request to the owner of an existing data set.

## Verification in the game

The items below are implemented and covered by unit tests, but have not all been verified in the game.

- Linux passes of earlier builds were made on 2026-10-18 and 2026-10-20 (see [STATUS.md](STATUS.md)), so items that do not end in "Then Linux" do not ask for a Linux check.
- Items that end in "Then Linux" need the Linux checklist ([LINUX_TESTING.md](LINUX_TESTING.md)) as well.

### Expedition and route planning

- [ ] **Start expedition and Review.** Plot a route in the Route Planner window and press **Start expedition**.
  - The status line names the expedition and its stop count.
  - The Expedition section, the Dashboard and the Expedition Log card show it running.
  - **Review** opens the Expedition window with that expedition selected (also when another expedition is running or the window is already open).
  - Press it again on the same route: no duplicate.
  - Pause and Resume from the Expedition window, then from the Log row. Check both agree and the time excludes the pause.
  - Stop from either side.
  - Restart EDMC while paused and check both stay paused.
  - With *Start the Expedition Log when I start an expedition* unticked (Settings → Exploration → Expedition), starting an expedition starts no Log run.
  - Road to Riches and Exomastery: tick **Start it now** and check the expedition starts.
  - Check the Route Planner buttons and the plan dialog fit at a small window size.
  - Then Linux.
- [ ] **One Expedition section on the panel.** The Exploration panel has an **Expedition** section and no separate Expedition Log section.
  - With nothing running it says so.
  - Press **START**: the section shows the Log's own lines (name and time, systems, jumps and light-years, bodies and species, earned and unsold).
  - **PAUSE** becomes **RESUME** and the lines gain `(paused)`. **STOP** ends it.
  - Start a planned expedition (Plan tab, **Start**): the section shows its stops, jumps, light-years, time and next stop and, under them, the systems, bodies, species and credits, with the name and jumps said once.
  - Fold the section: the title says what is running.
  - **COPY** and **Copy on arrival** work as before.
  - The section must not widen EDMC's window.
- [ ] **One Expedition window with Plan, Route and Log tabs.**
  - Press **EXPEDITION** and **PLOT** on the panel in turn.
    - Each opens the same window (never a second one) on its tab.
    - The Log tab shows the archive.
    - The window opens in a sensible place at a sensible size.
    - Resize and move it, close it and open it again: size and position are remembered.
  - On the Plan tab make an expedition and press **Start**. The **Log** tab shows its run.
  - On the Route tab plot a route and press **Start expedition**.
    - The Plan tab has the new expedition.
    - The status line says so in green and the button reads **Started ✓** for a few seconds (then **Start expedition** again). A press that starts nothing, such as with no route, shows neither.
    - **Review** switches to the Plan tab on it.
  - **Neutron route** on the Plan tab switches to the Route tab.
  - Close the window with a route plotted and open it again: the route is still there.
  - Check each tab's buttons (Start, Pause, Stop, Help) and that nothing is cut off at the smallest size.
  - Leave it open while playing: arriving in a stop's system ticks it off in the Plan tab, and the Route tab follows the route.
  - Then Linux.
- [ ] **Expedition planner.** The planner was replayed against 132 recorded sessions (2,354 jumps) on 2026-10-13.
  - Every stop was ticked in order and the jump and light-year totals were exact. `JumpDist` and `StarPos` are present in the real events.
  - The user interface itself remains to be verified:
    - Confirm that stop names are respelled and located through EDSM when added: type `sol`, expect `Sol`; try a mixed-case boxel name; an invented name should be kept with a note.
    - Check the **Road to Riches** and **Exomastery** buttons: press Plot and compare the new expedition's stops and notes with spansh.co.uk/riches and /exobiology. Both endpoints were checked with live requests.
    - Create an expedition and add stops manually, from a plotted route and from a CSV file.
    - Press Start. Jump to a stop and confirm that it is ticked, the jump is counted and the next stop's distance is shown.
    - Verify COPY and Copy on arrival pasting into the galaxy map.
    - Verify **Locate and reorder (EDSM)** against EDSM.
    - Check that the row does not widen the EDMC window.
- [ ] **Expedition survey tracking.** Start an Expedition with two or three stops.
  - Confirm that arriving in a stop updates its totals in the Expedition row (bodies scanned of the honk's count, first discoveries, maps).
  - Confirm that a body scanned twice counts once.
- [ ] **Expedition Log.** Press START in the Expedition section, make a few jumps, scan and map a few bodies, analyze a species and sell the data.
  - The section and the card (Settings → Overlays → Expedition Log) should count each.
  - The earned figures should match what the game paid.
  - Open the Expedition window's Log tab and try each of these:
    - rename it, edit the dates, start location, ships and notes and save
    - try a bad date
    - Stop and Resume
    - Reset and Delete (each asks twice)
    - **Rescan** an expedition you gave an earlier start, and check the totals fill in from your journals
    - Copy summary and Export CSV
    - **Start since my last sale**: it should start just after your last exploration or exobiology sale, fill in the totals from your journals and carry on counting
  - Check another commander sees none of it and that `expedition_log.json` survives an update.
  - The earned figures assume the journal's sale events (`MultiSellExplorationData`, `SellExplorationData`, `SellOrganicData`) carry the totals as read here. Confirm against a real sale.
- [ ] **Expedition Log: pause and stop.** Turn the Expedition Log overlay on, press START, jump or scan a little, then **PAUSE**.
  - The card should keep its totals with `paused` in its heading and nothing more should count.
  - RESUME should carry on (check the clock did not run while paused).
  - Restart EDMC while paused: it should still be paused.
  - Then **STOP**: the card should reset to saying none is running, even after a pause.
- [ ] **Expedition: restart a stopped one, and Rescan.** (Windows and Linux; steps also in [TEST_PLAN.md](TEST_PLAN.md) section 5.)
  - Start an expedition, jump or scan, press **STOP**, wait a minute, then start it again from the Route tab: the clock carries on from where it stopped, not a minute later. The Log's **Resume** does the same.
  - Pause one, make a few jumps while it is paused, **RESUME**, then press **Rescan** in the Log window: the totals do not include those jumps. Stop one, play a little, start it again and Rescan: the same.
  - An expedition that was paused before this build has no pause recorded, so its Rescan can still count that pause.
- [ ] **Neutron route, Share line, Market.json.**
  - Expedition window: press **Neutron route** and check it opens the Route Planner.
  - Mining Book: **Share line** on a positioned hotspot.
    - Paste the line into a text editor to see it is one line with no name or notes.
    - **Paste spot** on a second commander: refused for a spot within 100 m of one saved, accepted otherwise after the prompt.
    - Damage a line by deleting its last characters and check the message.
  - Dock at a station and open the commodities market right after docking, several times, on a slow disk if possible. Check Trade Watch and Trade show that station's prices (the log has no read errors).
- [ ] **Route Planner.** Press **PLOT** (in the Route Planner section of the Exploration panel, which starts folded, and the Route Planner button in the Dashboard's header).
  - Check the ship block against the game for the same ship (name, drive class and rating, booster, optimal mass, supercharge, cargo).
    - It never changes while you fly (only a new loadout or cargo does).
    - The source is the system you are in.
  - Plot a long route (for example to Colonia). Compare the jump count, the neutron stops and the refuel points with Spansh's own exact plotter for the same ship (V-0351 to V-0353).
  - Fly some of it:
    - Check the fuel column against your fuel gauge.
    - Systems turn green and the next is marked as you jump.
    - **Copy next system** pastes into the galaxy map search.
    - The **Copy the next system to the clipboard automatically** tickbox (on the panel and in the window, one setting) puts the first system on the clipboard when the route is ready and the next after every jump (the panel line says *copied*).
    - **Start expedition** gives the neutron stars, the refuel stops and the destination ahead.
  - With the Route overlay switched on:
    - The plotted route replaces the game's route on its card: titled *Neutron route*, a neutron star picked out, a refuel marked, the jumps and light-years left and the next supercharge right, moving on after each jump.
    - The game's route returns after the last jump.
    - With Settings -> Overlays -> Route -> *Mark the systems ahead that EDSM does not know yet* ticked, a system EDSM lacks gets a star on the neutron card too. Most neutron-route systems will be known, since Spansh only routes through systems it has.
  - Also try each option (injections, exclude secondary stars, refuel every scoopable, the algorithms) and a loadout change after plotting.
  - Then Linux.
- [ ] **Route Planner: white dwarfs and fuel scoop.**
  - Tick *Mark white dwarfs the route passes (asks EDSM)* and plot a route through the Bubble.
    - Systems with a white dwarf main star get *white dwarf: supercharge* in the table and a WHITE DWARF tag on the Route overlay.
    - Unticking it removes them.
  - Block the network to EDSM and check the status line says white dwarfs are not marked.
  - Fit no fuel scoop (or use a ship without one). Check the ship block says NONE FITTED and a route with refuel stops warns.
  - Check the Canonn and GEC **COPY** buttons and links (the fallback to Inara when no URL is given).
  - Then Linux.
- [ ] **Ship known after an EDMC restart.** With the game running and logged in, restart EDMC without relogging.
  - The Route Planner window's ship block should show your ship at once.
  - The Route overlay's fuel percentage should appear.
  - Generate route should not say the ship is not known.
  - Check the wait line while plotting does not move, only its timer ticks.
- [ ] **Route Planner: a neutron star that may be a secondary star.** Plot a route that passes Lalande 25224 (for example one through Jackson's Lighthouse).
  - The stop should be marked `NEUTRON ?` in yellow on the Route overlay and say so in the table.
  - The window should say to check the system map when the stop is next.
  - Check an ordinary neutron stop is not marked.
  - Check that a stop 20 or more jumps ahead is marked once you are within about a dozen neutron stops of it.
- [ ] **Route Planner: the route survives a restart.** Plot a route, jump a system or two along it, restart EDMC (with the game running, and again with it closed).
  - The panel line, the window's table and the Route overlay should show the same route from where you are on it.
  - Press CLEAR ROUTE and restart: it should stay gone.
  - Check a second commander does not see the first one's route.
- [ ] **Route Planner: clearing a route.** Plot a route, then press **CLEAR ROUTE** on the Exploration panel and **Clear route** in the window (plot again between).
  - The panel line, the window's table and the Route overlay's card should all go, and the card should close, even when the card was following a route from the galaxy map.
  - The button should be there before any route is plotted (and say so when there is nothing to clear).
  - Check the destination line on the card reads whole for a long procedural name.
- [ ] **Carrier Route.** Route Planner window → **Carrier route**.
  - Check the carrier block and the boxes fill in from the journal (where it is, tritium in the tank, space used: open Carrier Management once if they say not known) and match Carrier Management.
  - Type a destination, press **Generate route**, and compare the jumps and the tritium with Spansh's own Fleet Carrier Router page for the same carrier.
  - Check the first-jump line says how much tritium to have.
  - Schedule a jump in the game and copy the next system. Check the table moves on (green, next marked) when the carrier arrives, or **Mark next as reached** does it by hand.
  - Restart EDMC: the route should come back. A second commander should see none.
  - Try a squadron carrier if you have one.
  - Then Linux.
- [ ] **Route overlay EDSM check.** Tick the option and plot a route through uncharted systems.
  - A system EDSM does not know gets a `*` after its name (and nothing else is added to the card).
  - Nothing is marked when EDSM cannot be reached.
  - The Test Card shows the mark on the third and seventh systems.
- [ ] **Route overlay.** Enable it (Settings → Overlays → Route), press **Test Card**, then plot a real route in the galaxy map.
  - The card should read `You are navigating to:`, the destination, `You will be there in N jumps.`, a rule, the systems still to visit (names only, no numbers), a rule and `N LY left to jump.`.
  - Confirm that the systems match the plotted route (`NavRoute.json`).
  - Confirm that each one is taken off as you reach it, with the jump count and the light years following, and that the light years agree with the galaxy map.
  - Confirm that the card clears at the end, when the route is cleared and when you jump to a system that is not on it.
  - Check the star colors: green for a star you can scoop, yellow for one you cannot, blue for a neutron star, red for a white dwarf.
  - Plot a route in the Route Planner too:
    - It should take over the card until its last jump.
    - The window should say it was sent to the Route overlay and which system is on the clipboard (and again at each system you reach).
    - At the last system the card should say the route has ended and is being reset, then close after ten seconds.
  - Restart EDMC mid-route and confirm the card comes back.
  - Then Linux.

### Mining

- [ ] **Mining rates, targets and the live hold.** Mine a ring.
  - The Space page, the Live window and the HUD show the same lines:
    - *Refining now* (tons per hour over the last minute)
    - *Run average* (over mining time; a gap of more than ten minutes is left out)
    - *Hold: N of M t*
  - The hold alert fires from the live hold without a Cargo event.
  - Settings → WFMT → Mining → target box: type several names with their own percentages (`Painite 30, Platinum 25, Void Opals`).
    - Check the type-ahead after a comma, the status line under the box and a long list wrapping.
    - Last rock reads `target: <name>` and each target hit gets its own card.
  - Open Mining History once: old runs are re-read in the background.
  - Then Linux.
- [ ] **Mining History earned across stations, and the price finder.** Mine, dock and sell nothing, undock and sell at a different station.
  - Mining History's Earned, credits per hour and the Commodities *Sold* columns include the sale.
  - *Mined, not sold yet* shows the tons still waiting.
  - Rebuild from journals gives the same numbers.
  - In the price finder and What pays:
    - Fleet carriers are left out.
    - The *Minimum demand (t)* box is prefilled with the tons of that commodity in your hold when selling.
    - Compare a result with the in-game market for pad size and demand.
  - Then Linux.
- [ ] **Mining History: credits after limpets.** Buy limpets (note the price), mine with some launched and sell.
  - Mining History's Overview shows a *credits after limpets* tile.
  - The Sales block shows what the limpets cost and the credits left.
  - The Runs tab has an *After limpets* column equal to Earned less the number launched times the price you paid.
  - Check a run before you bought any limpets in the journals WFMT has (the figure carries a `~`), and a run with nothing sold yet (`-`).
  - Check that the first open after updating re-reads your journals once.
  - Compare the cost with your own credit balance for a run you remember.
  - Check the new column fits the window at its smallest size.
- [ ] **Mining History.** In Mining mode press **DASHBOARD**.
  - The header shows the one-time read of your journals.
  - The Overview should add up to what you remember (tons, hours, credits from sales).
  - Check **Commodities** against a few sales.
  - Check that **Rings** groups the runs by ring.
  - Check that **Runs** has the run you just finished (a run in progress appears within about 15 seconds, or press **Refresh**).
  - Check that sorting a heading works.
  - Check that **Rebuild from journals** ends with the same numbers.
  - Mine for a few minutes with EDMC closed, start it, and confirm the run is there.
  - Then Linux.
- [ ] **Station price against the galactic average.** Mine and dock, open the station's commodities market in the game.
  - The Space page gains a line for each commodity the run refined that this station buys, such as `Painite here: 521,400 cr/t, 8% above the galactic average (482,000)`. Most tons first, at most three.
  - Check the percentage against the market screen's own average.
  - Check that a commodity the station lists without demand is skipped.
  - Check that Low Temperature Diamonds and Void Opals are found (their internal names differ from the display names).
  - Check that the lines go when you undock.
  - Nothing is fetched.
  - Then Linux: the market is read from the journal folder where `Market.json` is written.
- [ ] **Hold full in.** Mine a ring with the Space page, the HUD overlay and the Live window open.
  - Once a minute of mining has passed, a line `Hold full in about N min` appears under *Run average* on all three.
  - N matches the free tons divided by the run average (for example 100 t free at 75 t/h is about 80 min).
  - It drops as the hold fills, and it reads `Hold is full` when the hold is at capacity.
  - It does not show before a Loadout has been seen (no capacity), and not at all while nothing is being refined.
  - Launch the Rhino and check `SRV hold full in about N min` on the Surface page for the 72 t hold. It is gone once the Rhino is stowed.
  - Check the extra line fits the panel width and the HUD panel.
- [ ] **Mining: core asteroids, target rock, mission needs, alerts.** Mine at a ring.
  - Space Mining page:
    - The **Last rock** line follows each prospected rock.
    - A core asteroid adds `core: <mineral>` and the **Core asteroids found** count.
    - The limpet figure reads `(N on board)` and matches your cargo.
  - Settings → Mining: type a target commodity (for example Painite) and a percentage. Check a rock at or over it says `target`.
  - Accept a mining mission and check **Mission needs** shows its tons against what you hold.
  - Flight Alerts (Settings → Overlays → Flight Alerts, Mining alerts ticked):
    - a green card for a core asteroid and for a rich rock (30 seconds)
    - amber cards when the limpets aboard fall to the number you set and when the hold passes the percentage
    - none while you are not mining
    - the sound if ticked
  - Then Linux.
- [ ] **Space Mining Book.** On the Space Mining page press **BOOK**.
  - The window fills with the rings your journals show (it reads them once in the background, so give it a moment on the first open). It shows hotspots per mineral, class, reserve level, tons mined and last mined.
  - Compare a few rings with the game (the hotspot counts, the reserve level).
  - Type a note, press **Favorite**, **Find** by a mineral, **Add ring** by hand and remove it, and **Copy system**.
  - Restart EDMC: notes and favorites remain. A second commander sees none.
  - Check **BOOK** on the Surface Mining page opens the Surface Mining Book as before.
  - Check its body list has a **From your journals** group of bodies with mining locations and tons refined (compare a body or two with what you remember).
  - Then Linux.
- [ ] **Surface Live radar: drive rings, stops, target line, Save map.** *Windows: tried on the simulation only.*
  - On a body with a marked location (CTR, then BRD) and several saved deposits, open **LIVE**.
  - Check the orange dashed rings are drawn as described. The 2 km reach behind them is a community figure that will not be measured (see STATUS.md).
  - Check that the first ring starts at the center and the last sits on the border, and that before a border is marked they reach as far as you have driven.
  - Check that violet circles sit round the best stops (the radius is Settings → Mining).
  - Check that with a target commodity set (Settings → Mining) a bright line runs to the nearest saved deposit of it, and a far one is labeled at the edge.
  - Check that **Help** matches what you see.
  - Check that **Save map** writes a PNG that opens, reads well and holds no commander name.
- [ ] **Shortcuts.** *Windows: the key combinations were registered and fired with simulated key presses; nothing was tried in the game.*
  - Settings → General → Shortcuts: pick keys, press OK, then in the game press each combination (Ctrl+Alt+Shift plus the key) with Elite in front.
    - **CTR** and **BRD** mark and say so in the Live window's status line.
    - The radar range steps.
    - The Live window opens.
    - The overlays hide and show.
  - Check the sound plays.
  - Check that nothing in Elite reacts to the same keys (the page reads your controls file and names a clash).
  - Check that a combination another program holds is reported after OK.
  - Tick **Chat commands**, type `!wf zoom` and `!wf overlays` in a chat channel with nobody else in it, and check they run within a second or two. This also confirms the journal's `SendText` line carries the text in a `Message` field.
  - Linux steps are in `docs/LINUX_TESTING.md` section 7l.
- [ ] **Rig placed and the rig bands.** Measure the game's rig gap: stand at one rig, CTR, drive until the game lets you place the next, BRD. Enter it in Settings → Mining (*Too close to place another rig*).
  - In the Rhino press **Rig placed** (or Ctrl+Alt+Shift+R, or type `!wf rig`) each time you put a rig down.
  - A band of that radius should appear round it, filled while you are inside and an outline once you are clear.
  - The lines on the right should say how far the nearest rig is.
  - Check the gap you measured is the one at which the game refuses to place a rig.
  - Check that stowing or launching the Rhino forgets the rigs.
  - Check that the radar card over the game shows the bands too.
- [ ] **The Mining radar over the game, Windows.** *Tried on the simulation's picture and in tests only.*
  - Choose WFMT's built-in overlay (Overlays → Overlay Connection), tick **Show the Mining radar over the game** (Overlays → Mining), press **Test radar**.
  - Check the card appears for a few seconds where Overlay Placement says (Mining radar), the background and the green are see-through and the marks solid.
  - Launch the Rhino on a body with marked locations and saved deposits:
    - The card should follow the Rhino about once a second.
    - The radar range shortcut should change its reach.
    - Stowing the Rhino should take it down.
    - Hiding the overlays should hide it.
  - Check the size and opacity settings, that it does not cost frames in the game, and where it sits against your other cards.
- [ ] **Surface mining on a body you never scanned, and Get body info.** Land on a body with no `Scan` event in your journals and launch the Rhino.
  - The ground trail should start on the Live radar.
  - **CTR** and **BRD** should mark (the body's name and size come from `Status.json`).
  - Tick *Enable body lookup* (Settings → Mining), open **BOOK** and press **Get body info**.
    - The system's landable bodies appear in the list with their kinds, sizes and mining-location counts. The counts come from Spansh and need a jump or login since EDMC started.
    - The status line says how many were added.
  - Check a body your journals did give keeps its own data.
  - Check that FSS-scanning a body fills its mining-location count.
  - Restart EDMC (or jump away and back): the body list should return at once, and `mining_body_cache.json` should appear beside the plugin with no commander in its name.
- [ ] **What pays.** Tick *Enable Spansh best price finder*, save deposits of two or three materials, open **BOOK** then **What pays**.
  - Check the ranking against Spansh's own price search for the same commodities.
  - Check that a commodity nobody pays for says so.
  - Check that *Near* and *Within* change the answer.
  - Check that **Copy report** pastes a numbered list.
- [ ] **Surface Live simulation.** Settings → Mining → Simulation → **Surface Live (pretend Rhino)**.
  - The radar, its range buttons, **CTR**, **BRD**, **+H.S.** and **Save map** work on the pretend ground.
  - Nothing you press changes your own deposits or marks.
  - The window closes with its close button while Settings is still open.
- [ ] **Surface Mining Book: refilling marks, stops, you are here.** In the Rhino on a body with several saved deposits (some with rigs and positions):
  - Check the **Stops** lines above the hotspots, the dashed rings on the map at 1x/2x/4x and the `stop N` tags. Changing Settings → Mining → Stop radius changes them.
  - Standing within 175 m of a deposit selects it and marks `you are here`, and Mark depleted there is one click.
  - Mark a deposit depleted. Check the card says `Depleted N d ago. When it refills is unknown` and that the mark stays.
  - Set Settings → Mining → refill days to 14, edit `depleted_at` in `mining_hotspots.json` to 15 days ago, reopen the Book. Check the mark is gone and the card says `Assumed refilled`.
  - Press Mark depleted again with no mining and check `Still depleted at ...; look again in 7 d`.
  - Check the dialog's Edit keeps these dates.
- [ ] **Surface Mining Book: Market research.** Tick *Enable Spansh best price finder*, open the Book on a system where you have saved hotspots, press **Market research**.
  - Check the buyers against the in-game market (price, demand, pad size).
  - Try a system with no records (it should say so and suggest nothing).
  - Try the *Also check* box with a misspelled name.
  - Try a busy system (the note about the first 100 stations).
- [ ] **Surface Compass.** The compass replaces the Mining waypoint arrow. On a landable surface, verify:
  - **Test Compass**.
  - The arrow follows the nearest hotspot as the commander turns.
  - **MARK** (the body name is taken from `Status.json`'s `BodyName`, which was seen in a real file on 2026-10-16, game 4.4.1.1).
  - **TARGET**.
  - The Marks window.
  - The previous Mining tick and arrow are removed while the saved placement is kept.

### Overlays and cards

- [ ] **Built-in overlay.** Settings → Overlays → Overlay Connection → Which overlay draws → WFMT built-in overlay, OK, start Elite borderless or windowed (EDMCModernOverlay may stay running).
  - Check:
    - Every card appears where Overlay Placement says (try the corners and edges).
    - Text and panels look right at every text size and color scheme.
    - The radar's circles and lines are the right size and place.
    - The Sample popup shows and goes away.
    - The Hide overlays shortcut (Ctrl+Alt+Shift+O by default) hides and shows it.
    - The overlay follows the game window, hides on alt-tab and comes back above Elite.
    - Clicks reach the game, and there is no stutter.
    - Win+Shift+S and Print Screen keep it up.
    - The converted screenshot includes it when ticked.
    - Switching back to EDMCModernOverlay works.
  - **Fonts:**
    - Appearance → Overlay font lists Source Sans 3.
    - Add font file... copies a font into WFMT's `fonts` folder and it is used at once.
    - A font stays after a WFMT update.
    - A deleted font falls back to Source Sans 3.
  - Not yet checked: the triple-screen span, ultrawide, other monitors.
  - Details of what is left are in `docs/NATIVE_OVERLAY_SPEC.md`.
- [ ] **Per-commander overlay settings.** With two commanders (Mactavious is the second test commander):
  - Switch the Expedition Log card on and move a card for the first.
  - Log in as the second and confirm the second starts with a copy. Then turn the card off and move another card.
  - Log back in as the first (without restarting EDMC, then again after a restart). Confirm each commander's cards, positions, Show ticks, text size, color scheme and font are their own and appear at once.
  - Confirm the Overlay Placement tab names the commander.
  - Confirm that `overlay_settings.json` appears beside the plugin and survives an update.
  - Confirm that the overlay's connection (which overlay draws, host and port) stays the same for both.
  - Check a card shown by one commander is cleared when the other logs in.
- [ ] **Every overlay off after the reset.** (Windows and Linux.) Restart EDMC with this build. The log has `All WFMT overlays reset to disabled (one-time), including the saved choices of N commander(s)` once, and no card shows for any commander (log in as each one you have). Turn a card on, restart, and it is still on.
- [ ] **Screen size from the operating system.** (Windows and Linux.) Overlay Placement names where the size came from.
  - With the game's `DisplaySettings.xml` and the overlay's log out of the way, **Detect screen again** should say it is using the primary display, with your real resolution. Windows reads the hardware size (3840 x 2160 at 125% reads 3840 x 2160). Linux reads `xrandr`'s primary output, through the host from a Flatpak: report the session type and whether `xrandr` is installed.
  - On an ultrawide (21:9 or 32:9) or a triple-screen span: the placement preview draws every box on the screen and none on another, and the cards sit where the preview put them in the game.
- [ ] **Clearing lines and circles on the overlay.** With EDMCModernOverlay:
  - Sample a plant with the Exobiology radar on and walk away or analyze it. The pointer and circle go at once, not after a few seconds, and no white dot is left where a circle was.
  - Land, then lift off with Landing's diagram on. The diagram goes.
  - Switch on the Surface Compass, then turn it off. The arrow goes.
  - Press **Hide overlays** with the radar showing. Lines and circles go.
  - Open `EDMarketConnector.log` and check there are no `Dropping vect payload with insufficient points` lines for `wfmt_` ids.
  - With the built-in overlay, check the same displays clear.
  - Then Linux.
- [ ] **Layout editor and card anchoring.** *Windows: the drag-and-drop editor confirmed working in the game, 2026-10-16; the flush-edge and circle-placement checks are still to confirm.*
  - Open Overlay Placement. Drag a few boxes and check the table fills in and the boxes snap to the edges and grid.
  - Press *Show placement preview* and compare with the picture.
  - Set a card to the bottom or right with offset 0 (for example Biology at the bottom left and System targets at the bottom right).
    - Check each sits flush against the screen edge.
    - Check that the Bio radar's circles and the Bio status dots sit inside their cards.
  - Report any card that is still off by a fixed amount.
- [ ] **Alert widths.** Trigger a Notable Bodies alert (or **Test Notable**) and a Discovery alert for a body or system with a long capitalized catalog name.
  - Confirm that the whole name fits inside the card at Default and Larger text sizes.
  - On the Missions overlay card, check a mission with a long station or system name: the place should move to a second line under the title, in the same color.
  - Report any text that still extends past an edge.
- [ ] **Overlay padding and alignment.** The overlay cards share one padding and left-justify their text.
  - Check these cards: Colonization, Discovery (system and body), Notable Bodies, Interdiction, Landing, Missions, Flight Alerts, Mining, Surface Compass and the Screenshot message.
  - On each, confirm:
    - The text sits the same distance from the border on all four sides.
    - Every line starts at the same left edge (no centered title or name).
    - The right edge has no extra blank strip.
    - No text runs past the border at Default and Larger text sizes.
  - Also confirm the Text size menu offers only Default and Larger.
- [ ] **Flight Alerts.**
  - Verify the Test Card.
  - Verify fuel warnings with a plotted neutron star and with a high fuel percentage.
  - Verify the carrier jump countdown with a real scheduled jump. This is not yet verified: the feature reads `CarrierJumpRequest`, and its field names and flag bits come from the journal documentation rather than from a recorded event.
  - Verify the sound.
  - Verify the card position (right side, below the Inventory display).
- [ ] **Body info symbols, Biology ranges and panel opacity.** On a landable body, check:
  - Body info writes the materials as symbols (`Fe`, `S`, `Na`) and the atmosphere and volcanism as formulas (`CO2`, `SO2`). The Body info tab's choice of full names switches it back.
  - The Biology card shows the range an open genus could pay with an even-share percentage for each candidate, and the footer range with the first footfall figure on its own line.
  - Settings → Overlays → Appearance → Panel opacity changes every card's background (lower values let the game show through, the text stays solid).
- [ ] **System targets and Body info cards.** Enable both (Settings → Overlays), press **Test Card** on each, then explore a system.
  - After a honk and some scans, confirm:
    - System targets lists the scanned planets and moons at or above the threshold with sensible values. Compare a few with the credits the game pays when you scan them; the estimate is the scan value, not the mapping value.
    - A body drops off when you map it.
    - Bodies with life appear with the right count and drop off when you analyze the last organism.
    - It clears when you jump, and restarting EDMC mid-system brings it back.
  - Target a body in the system map and fly close to one. Body info should show the body you targeted, then the one you are near.
  - Check the default spots (lower middle of the right half) against your HUD and note any card that sits badly.
  - The format of `Status.json`'s `Destination` is confirmed (2026-10-16: `System` is the system address, `Body` the body ID, `Name` the full name).
- [ ] **Mapped value and the corrected scan value.** Compare the Scan value and Mapped value on Body info with what the game paid for a few bodies you scan and map (the estimates should be close, not exact). Check the Exploration Value readout and System targets read sensibly.
- [ ] **Missions overlay card.** Enable the card (Settings → Overlays → Missions), press **Test Card**, and then fly with a real mission board.
  - Verify that HERE and NEXT follow the current system and the targeted system.
  - Verify that times count down.
  - Verify that a finished mission shows a tick.
  - Verify that the card keeps one width.
  - Verify that it sits in the chosen corner without covering the HUD.
  - Record which rows should be added or removed (the label for each kind of mission, and the row limit).

### Exploration and survey

- [ ] **Local star index.** Settings → WFMT → General → Online lookups → Local star index: press **Download and build**.
  - Check the progress.
  - Check that **Cancel** stops it (a cancelled download resumes the next press).
  - Check the free-space message with little disk left.
  - Check the finished status (systems, size, date).
  - Press **N.S.**: the status line reads `... local index` and the result matches Spansh's own search for the same position.
  - Untick *Use the local index* and N.S. asks Spansh again.
  - **Delete** removes it.
  - Restart EDMC and the index is still there.
  - After a WFMT update it is still there, and Back up my data leaves it out.
  - Check the N.S. line fits the panel's wrap width.
  - Then **Update** the next day or later:
    - The status line reads `Updated from Spansh's 1-day file (about 3 MB)` with a count of systems changed.
    - The line under Installed says `up to date as of` today's date and `1 update since`.
    - Pressing **Update** again at once says it is already up to date without downloading.
    - After a week or more without updating, **Update** uses the 1-week file (about 19 MB).
    - More than a week behind, it downloads the full 173 MB file again.
    - N.S. still answers the same as Spansh's own search after an update.
  - Then Linux:
    - The plugin folder of a Flatpak EDMC is writable and has room (about 300 MB free while building).
    - Check the real build time on the real 173 MB file and on an update.
- [ ] **Exploration Dashboard.** Press **DASHBOARD** on the Exploration panel in each of these places and check the window against the game and your overlays.
  - In a system with several bodies after a honk and some scans (Orbit):
    - Orbit lists every body with sensible distance, gravity, atmosphere and values.
    - Click a row for the details.
    - The worth-mapping and life lists agree with the System targets card.
    - First discoveries and first footfalls are marked.
  - Land. The window should switch to Surface by itself.
    - The body's conditions and materials match Body info.
    - The genus table agrees with the Biology card.
    - Its Progress column reads `Collecting: 1/3` after a Log and `Analyzed: 3/3` once paid out.
    - It follows each sample with the distance from the last one.
    - The Specimens being tracked table's distance and direction match the Bio radar.
    - Ship and SRV distances look right.
  - Lift off (back to Orbit), and look at Overview and Exploration with an expedition running.
  - Then the header buttons:
    - **Exploration overlays** should clear Route, System targets, Body info, Expedition Log, Compass, Discovery and Notable cards and bring back exactly the ones you had switched on.
    - **Exobiology overlays** the same for its four cards.
    - Hiding both then **Hide overlays** and showing again must leave them hidden/shown as expected.
    - Neither changes anything in Settings (open Settings and check the ticks).
  - Check it with the built-in overlay and with EDMCModernOverlay.
  - Check that leaving the window open does not slow the game or EDMC.
  - Then Linux.
- [ ] **RND.** Press **RND** a few times near a procedurally named system.
  - Check that each name plots on the galaxy map.
  - Check that the status line gives a distance and says whether EDSM confirmed it.
  - Check that a second press within 5 ly is much quicker (the Spansh list is cached for 10 minutes) and offers a different system.
  - Check that **Settings → Exploration → Boxel Survey → Systems to request from Spansh** changes how many systems are requested.
  - Then Linux.
- [ ] **System targets, visit history.** Restart EDMC and watch the card.
  - It should say `Reading your journals for a visit history (n%)` for the first read (about 40 seconds for thousands of journals).
  - Then it should show `First visit here` in a system you have never entered, and `Been here N times before · last <date> · you scanned here` in one you have.
  - A relog in the same system must not add a visit. Jumping away and back adds one.
  - Check `system_history.json` appears and is not shared with a second commander.
- [ ] **System targets, what others found (Spansh).** Tick the Spansh option under Settings → Overlays → System targets, then jump to a system others have surveyed (one with biology).
  - Check the card shows a Known section and a `Known (Spansh)` line before you honk, with rewards that look right against the in-game signals.
  - Check that scanning a body with life moves it to the Life list.
  - Check that a system nobody has scanned shows no Known section and the usual `Nothing ... to map yet`.
  - Check that unticking it clears the section on the next jump.
- [ ] **A system scanned while EDMC was closed.** Close EDMC, play: jump to a system nobody has scanned, honk and scan several bodies, quit the game.
  - Start EDMC, then the game, and Continue into the same system (a relog into it, EDMC started before the game).
  - System targets, Body info and the Dashboard's Orbit tab should list the bodies you scanned and what is worth mapping, within a few seconds.
  - Check an EDMC start while already in the game too.
  - Check that a system you scan with EDMC running is unchanged.
  - Then Linux.
- [ ] **System survey memory (where you left off).** Survey a few bodies in a system, jump away and back (and log out and back in).
  - The System targets card should show the same `N of M scanned`, the summary line (`1 mapped · life 1 of 3 done`), what is left to map and the life still to analyze, and the **Done** list of what you finished.
  - For a system you were in before WFMT was installed, the first return should rebuild it from your journals within a second or two.
  - Check that another commander sees none of it.
  - Check that `system_surveys.json` appears beside the plugin, survives an update, and stays small.
- [ ] **Nearest place to land.** In the game: press FIND in Exploration, tick the box, press Find.
  - Check your system, coordinates and ship's pad are right.
  - Check the nearest stations and carriers look sensible against the galaxy map (for the carriers, the age shown).
  - Check that a pad your ship cannot use never appears.
  - Check that the fuel, repair, rearm and outfitting choices change the list.
  - Try it from a system nobody has charted (a fresh discovery) and with a small, a medium and a large ship.
- [ ] **Exobiology cards.** *Windows: used in the game on 2026-10-16 (status, biology, radar, circles, first footfall and the progress bar) and working; the sample popup and the red and green circles are still to confirm.*
  - Enable them (Settings → Overlays → Exobiology), press **Test Cards**, then sample on a body you have mapped.
  - Bio status shows the species, variant, three circles filling as you sample, the reward (with the first footfall bonus where it applies) and the distance to the last sample.
  - Biology lists the genera with sensible candidates and values.
  - The Bio radar's circles sit where you took the samples, turn red when you walk back inside them and show the ship and SRV. The circle shape's position and radius are drawn from the overlay's circle command and have not been seen in the game yet.
  - The Sample popup appears for each sample.
- [ ] **Plant waypoints.**
  - *Several genera at once:* identify plants of two or three genera. Check there is a colored pointer, ring and row for each, that sampling a plant removes its pointer and the genus moves to its next plant, and that analyzing a genus removes it.
  - *Windows: confirmed working in the game with the little pointers, 2026-10-16; the persistence across a restart and the dropped-on-sample behavior are still to confirm.*
  - Scan a plant with the Composition Scanner, walk off, and check:
    - The Bio radar shows a ring with the genus letter, a pointer line toward it and `Tracking <species>` with the right distance and direction (it should read `ahead` when you face it and swap right and left if you turn around).
    - The little pointers before each distance under the radar turn to face the ship, the SRV, your first samples and the tracked plant. A pointer that is up means straight ahead.
    - Bio status shows the same line.
    - Taking the first sample at the plant removes it from the list.
    - It all survives restarting EDMC.
  - The codex scan's latitude and longitude are assumed to be the plant's own position. Compare with where you stood.
- [ ] **Tracked plant markers and likely colors.** Scan a plant from your ship, then from an SRV, then on foot.
  - Check the marker's ring is widest for the ship and smallest on foot.
  - Check the distance has a `~` unless on foot.
  - Check a sample taken within the reach (about 450, 300 and 100 m) drops the marker.
  - On a body with life, check the Biology card's `Likely color` matches the color a sample then names, and that a multi-star system can be wrong.
- [ ] **Prediction review and the record of finds.** Sample a few species with WFMT running.
  - Check that `exo_observations.json` gains a record for each.
  - Open **REVIEW** on the Organic Scanning panel and check the Finds, By genus, Ranges and Together tabs, a review status and note, and Copy report.
  - Turn the record off and clear it under Settings → Exploration → Organic Scanning.
- [ ] **MY CODEX.** Press **MY CODEX** in the Codex Completionist section.
  - Check the Overview totals against the Found tab.
  - Check that Closest to complete lists types that are started but not finished.
  - Check that a missing biological entry's **Where to look** names conditions and a star class or material you can check in the game.
  - Check that sorting a heading works on each tab.
  - Check that **Backfill Journals** reports in the window's status bar and the section.
  - Then Linux.
- [ ] **Megaship scans.** In a Powerplay system, drop out of supercruise at a megaship and scan its datalink.
  - Confirm that the panel line and the **SES → Megaships** row appear with the correct name and system.
  - Confirm that the merits are filled in shortly afterward.
  - Confirm that a second scan of the same megaship changes nothing, and that a scan at a station adds nothing.
  - Restart EDMC and confirm that the list is retained.

### Ships, materials and engineering

- [ ] **Stored modules.** Open Module Storage at a station, then Ship Builds → **Stored modules**.
  - The list matches the game's Module Storage (module, class, engineering, system and station, transfer cost and time, hot, in transit).
  - The freshness line names the last visit.
  - Store a module, retrieve one and swap one, and check the tab follows. A swapped-out module shows engineering as `?` until the next visit to Module Storage.
  - Restart EDMC after a session with storage changes and check the list catches up from the journals.
  - Check a second commander sees none of it, the filter box, and the tab at its minimum width.
  - Then Linux.
- [ ] **Ship planner links.** Paste a Coriolis link made with **Coriolis link** and an EDSY link made with **EDSY link** into the Ship planner.
  - Check the same build is read.
  - Press **Open in Coriolis** and **Open in EDSY** and check each site shows the ship with its modules and engineering. EDSY has not been tried with a link WFMT made.
  - Try a very large engineered build for the Coriolis length message.
  - Paste an EDSY `#/L=` address and a Coriolis `/outfit/` address and check the message explains why they cannot be read.
- [ ] **Ship planner.** Export a build from EDSY and from Coriolis as SLEF, paste it, and compare the modules, levels and experimental effects with the build.
  - Verify **Add plan to wishlist**, including the refusal when it would exceed 100 blueprints or 99 crafts.
  - Verify the **Rolls per grade** setting.
  - Verify a pre-engineered module, and a `Loadout` line copied from a journal.
  - Then verify **Subtract what my current ship already has** with a build for the ship currently flown (it reads the newest journal).
  - Verify the **In storage** column: open Module Storage once at a station, then read a build that holds a module you have stored. It should say Yes for the same engineering at the level or above, Partly for other engineering, and nothing for a module fitted to a ship. Select the row for where it is.
- [ ] **Materials.** Compare the login `Materials` list with the in-game inventory.
  - Verify that MaterialCollected, MaterialDiscarded, a trade, a synthesis and an engineer craft each change the correct counts.
  - Verify the display at a grade limit.
  - Verify that the row does not widen the EDMC window.
  - EDMC's state keys `Raw`, `Manufactured` and `Encoded` were checked against EDMC's `monitor.py` on 2026-10-13.
- [ ] **Material trader finder.** Find a trader from the current system and compare a result with the galaxy map (the station has that trader type and the stated pad size).
  - Verify the Within and Pad filters, a typed system, copy on double-click, and that no other network request is made.
  - Spansh's `material_trader` filter was checked with live requests for all three values, but not through the window.
- [ ] **Engineering blueprints, wishlist and Engineers tab.** Select several blueprints (a ship module, and an Odyssey suit or weapon blueprint).
  - Compare each ingredient's Have value with the in-game inventory.
  - Confirm that an Odyssey ingredient counts the **ship locker**. The game's rule is unconfirmed: does an upgrade also draw on the backpack?
  - Confirm that an unlock requiring trade goods states that they are not counted.
  - Confirm which engineer can complete each wishlist entry, that "ready" follows list order, and the Wishlist line on the Materials section.
  - On the Engineers tab:
    - Compare status, rank and rank-ups (a rank-only event) with the in-game Engineers panel.
    - Verify the **Where** column, the detail text and the Bubble / Colonia filter.
  - The Colonia engineers' upgrades and locations come from a published table and a community list, not from the game.
  - Also compare several recipes with the game: the table dates from March 2024 plus later corrections.
- [ ] **Upgrade planner.** Select an item, a class range and modifications and add them to the wishlist.
  - Compare the materials with the in-game upgrade screen for an item other than the eight confirmed ones (Karma P-15, Manticore Intimidator and Oppressor, TK Aphelion, Eclipse and Zenith).
  - Test **Read my gear** and compare the result with the commander's loadouts.
  - Record the credits shown at the upgrade screen. Each confirmed value is a line in `odyssey_upgrade_plan.CREDIT_UNIT` (or submit the `UpgradeWeapon` journal line).

### Missions, trade and colonization

- [ ] **Missions window and pinned missions.** With a real mission board, open the window from the **Missions window** button at the bottom of the panel.
  - Check the Active and By place tabs, the summary line and the detail strip against the game's mission board.
  - Pin two missions and confirm the PINNED section on the overlay card (and that a pinned mission is removed when it is handed in).
  - Check the text size beside the panel arrows.
- [ ] **Mission progress colors.** Take two source-and-return missions and buy part of the cargo.
  - Confirm that the Missions window shows `N/total held` with a bar.
  - Confirm that the row turns blue and then lime past halfway, and that the overlay line follows.
  - Hand a mission in and confirm that it turns green.
  - Confirm that a massacre stack's color changes as kills are recorded.
  - Report whether the colors, or the held count (all of that commodity in the hold), do not match expected behavior.
- [ ] **Best picks and Source commodities.** With Trade lookups enabled: Market → enter a commodity → **Best picks** (buy and sell), and Missions → **Find sources** with several Collect or Mining missions active.
  - Check the four picks against the market data for the same commodity, ship and system.
  - Record any differences (the 10% band is measured against the cheapest station in the galaxy).
  - Not implemented: the nearest ring hotspot for Mining missions in the same window.
- [ ] **Source commodities: Delivery pickups.** Accept a plain "Deliver N units of X" mission (for example Personal Weapons) at a station and open Source commodities.
  - It should read `Pick up at <that station>` with the tonnage and no Spansh search.
  - Collect the cargo at the station and check the row goes away.
  - Accept a war-supplies delivery and check it drops off within seconds.
  - Restart EDMC with an uncollected delivery active and check the station is still named.
  - Check that a Collect or Mining mission still shows market picks.
- [ ] **Trade Watch list.** Add several commodities and open real markets (the `Market` event and `Market.json` for a watched item).
  - Press **REFRESH** against Spansh with Trade lookups enabled (two requests per commodity).
  - Verify the age and place columns and removal.
  - Verify that the EDMC window does not become wider.
- [ ] **Themed confirmations and prompts.** Open each from its place and check it is centered over its window, blocks that window until answered, wraps long text, and that Esc cancels and Enter takes the highlighted button.
  - The dialogs to open:
    - Reset Session, Reset Current System and Delete session (Powerplay and Trade windows)
    - Reset trade session (three buttons) and Rebuild trade session (a prompt, then a warning for a bad date)
    - Paste spot and Delete hotspot (Surface Mining Book)
    - Import Hotspots
    - Report to Raven Colonial and the Raven key prompt (typing is hidden)
    - Turn on online lookups? (Missions)
    - Clear the record (Organic Scanning)
    - Restore my data (Settings → General → Backup, a dialog over a Settings page)
  - Then Linux: the dialog really blocks its window, appears without a flash, and opens over a window on a second monitor.
- [ ] **Credits Ledger and Colonization History windows.**
  - Verify that clicking the Credits line opens the ledger.
  - Verify that the Income, By day and Lifetime tabs fill for each commander.
  - Verify that **Rebuild from journals** reports its progress and result.
  - Verify that the HISTORY button on the Colonization panel opens its window.
- [ ] **BGS** after a tick passes while EDMC is closed: the period that closed should contain the play made in the meantime. Also verify that a finished Colonization build is displayed without the "Construction Site:" prefix.
- [ ] Colonization window: **Find all** against Spansh, **Only what [station] sells** with a real `Market.json`, and copying a system by clicking a result row.
- [ ] **Colonization: hold, Remaining and best single systems** (Windows, then Linux; steps in [LINUX_TESTING.md](LINUX_TESTING.md)).
  - Buy a tracked commodity at a market: the **In Cargo** figures in the Sites window, on the COL page and on the overlay card follow the hold within a couple of seconds (WFMT reads the game's `Cargo.json`).
  - **Remaining** falls as you load the ship or the carrier and reaches 0 once the whole amount is acquired, wherever it is stored; **Haul Trips** still counts everything the site needs.
  - The overlay card shows the same Remaining and no To buy column. With *Hide commodities already covered by the hold and the fleet carrier* on (the default), those commodities are left out and the footer still counts them.
  - **A lagging Frontier copy does not undo a transfer** (EDMC signed in to Frontier): unload cargo at your carrier, then open Carrier Management. The FC column keeps the unloaded stock and **Copy diagnostics** shows an `ignored` line from `Carrier cargo from Frontier`. After 15 minutes without a transfer, a changed Frontier figure replaces the tally and an unchanged one stays ignored. The rules and log lines are in [the Colonization guide](guide/colonization.md).
  - After **Find all** with two or more commodities, **Best single systems** lists the few best systems with their stations in visiting order; **Copy Route** copies the best system first. The note under the buttons is in the accent color while a search runs.
- [ ] **Raven Colonial writes not yet observed:** Report Complete on a finished build, and carrier cargo sharing (the second switch).
  - **Create Project on Raven** has never run against the live service: try it docked at a construction ship, once with a planned site and once with none, and check the project, the link, the primary project and the attached carrier on ravencolonial.com.
  - **Mark Plan Entry Demolished** is likewise unobserved.
  - **My Projects:** reading was checked against the live service (an empty list for a commander with no projects). With a real project, check the rows, the counted totals, **Set as My Primary** and **Save Counted List** on ravencolonial.com.
  - Carrier cargo sharing requires a transfer at the commander's own carrier with that option enabled, followed by a check of Raven's carrier record.
  - Depot progress and deliveries have been verified, and the Test key button accepts a valid key.
- [ ] **Raven Progress and Open Selected Build on Raven** on real in-progress builds (the Raven Colonial menu).
  - These find a build from the system's plan (by name while it is being built) and, failing that, by the system's address and the site's market id. Check both routes, including a project named *Primary port* and one on a station the game has renamed.
  - A renamed station therefore requires a new dock before WFMT uses the new name.

### Screenshots, settings and general

- [ ] **Screenshot preview window.** Take a screenshot with a preview shown, from a very wide source (a triple-screen or ultrawide capture) and a tall one.
  - The window stays on the screen and the picture is whole.
  - **Open Folder** opens the folder.
  - Esc and **Close** close it.
  - Resizing the window re-fits the picture.
  - The size and place come back on the next preview.
  - Then Linux.
- [ ] **Back up my data.**
  - *Windows: confirmed 2026-10-18.* A backup of the real data was made, opened and checked: every data file present, no `rcc_keys.json` or Codex catalog, `backup-info.json` correct.
  - *Still to try in the game* (both are covered by unit tests only):
    - Pick a folder inside the plugin folder and check it is refused.
    - Cancel the dialog and check nothing is written.
  - **Restore and automatic backup (untried in the game):**
    - Press **Restore my data...** and pick a backup (pick a non-WFMT zip and check it is refused), confirm, restart EDMC. Check the data is back and `backups/pre-restore-….zip` holds what it replaced.
    - Stage a restore and press **Cancel the waiting restore**.
    - Tick **Back up automatically**, choose a folder, set 1 day, restart EDMC. Check a `WFMT-data-auto-….zip` appears after about a minute, and that restarting again the same day makes none.
    - Check one is made before an update installs.
  - Then Linux (a Flatpak EDMC needs a writable folder).
- [ ] **Compact storage.** Play for a while.
  - Check that the per-commander files (`system_history.json`, `system_surveys.json`, `codex_completionist_state.json`, `organic_scan_state.json`, `survey_log.json`, `expedition_log.json`) are rewritten without indentation and shrink.
  - Check that every feature still shows the same data after a restart.
  - Check that a second commander's data is untouched.
  - Then Linux.
- [ ] **Settings tabs.** Check:
  - With a narrow Settings window, the tab rows wrap and every label is whole (Overlays has twenty).
  - A **Related settings** link opens its page (the link click was not tried in EDMC).
  - Hiding mode buttons under General → Window works.
  - OK stays on screen on a 1080p display.
- [ ] **System-name suggestions.** Test every box that accepts a system name: Expedition System, the planner's Start and End, the trader finder, Colonization Around, Notes, Waypoint Route, Boxel Survey seed.
  - Check the list below the box.
  - Check Down, Enter and Escape.
  - Check Enter with nothing highlighted still acting.
  - Check the list matching the EDMC theme in the main panel boxes.
  - Then enable Settings → Window → Suggest system names from Spansh and type `outot`.
- [ ] **Notes.** Verify quick add, the window, **Here**, deletion with confirmation, and the count shown when jumping into a system that has notes. Verify that the EDMC window does not become wider.
- [ ] **Help tab** (Settings → General → Help).
  - Verify that **Report an issue** opens the prefilled form (this requires the issue template on GitHub).
  - Verify that **Copy diagnostics** places the versions and recent WFMT log lines on the clipboard with the commander name redacted.
- [ ] The Powerplay panel and the other mode panels (bold and small fonts, grouping rules) under the Default, Dark and Transparent EDMC themes.
- [ ] In a running EDMC: the Inventory start-up synchronization from EDMC's rebuilt state, and whether the `Complete` ids in the login `Missions` event are a subset of `Active` (currently assumed).

## Colonization

WFMT's own tracking is the reference, and reporting to Raven Colonial is **opt-in**: a finished build, depot progress, deliveries and (separately) carrier cargo changes.

Not implemented:

- Assigning commodities to commanders on a project, linking other commanders, and showing other linked carriers' cargo.
- A guided tool that fills in a system's whole plan on Raven (bodies, installations and statuses) from play.
- Ready flags.
- Raven's `supply` call, which Raven's documentation describes as unsuitable for a tool that reads the journal.

Open check:

- [ ] **Where to buy: verify in the window.** The "sells everything" search runs first and skips per-commodity searches that it satisfies in full; a second request covers leftovers from the returned whole markets.
  - Checked with a script against Spansh:
    - A 6-commodity list required 1 request.
    - A 14-commodity list required 1 + 12 searches + 1 leftover request, and the 2 commodities with no stock within 50 ly were reported as not covered.
  - Verification in the window itself remains.

## Implemented from earlier plans

Implemented so far:

- the fleet carrier jump countdown
- low-fuel and next-star warnings
- system and body notes
- the Surface Compass with marks
- the Trade watch list
- materials and engineering (including the blueprint wishlist, the engineers and the ship planner)
- the material trader finder
- expedition planning

What remains of it is under "In progress" and "Verification in the game" above.

## Low priority

No work is planned on these items. They are retained so that the ideas are not lost.

- [ ] Raven Colonial: read-only polling of tracked projects (remaining needs and other commanders' progress alongside WFMT's own), followed by opt-in writes.
  - Completion, progress, deliveries, carrier cargo, creating a project and My Projects are implemented; the remainder is deferred.
  - Reads need no key.
  - The public documentation would need to list exactly what is sent and when.
- [ ] **Team projects:** several commanders working on one project.
  - The depot event reports only the project's totals, so a per-commander breakdown would have to come from each member.
  - All data is currently per commander and will remain so unless a commander opts in to sharing.
- [ ] Co-operative building and colony tracking: not available yet.
- [ ] History ideas:
  - Tons per hour (the journal does not record time spent hauling, so this would be estimated from the gaps between deliveries).
  - Credits earned from deliveries (the depot reports a `Payment` per commodity, but it has not been verified that this is the amount paid out).
- [ ] Round trip: a Powerplay bonus filter (this depends on what the price service can report and on how "bonus" should be defined).
- [ ] **Landing Assist: the project's own pad layouts,** with fore and aft cues and diagrams for facilities that have none today, settlements first.
  - The pad numbering of settlements must be confirmed in the game before any layout is drawn.
  - This differs from the "Landing-pad diagrams" item under Not planned, which is about reading a layout from the journal. The journal has none, so these would be the project's own.
- [ ] **Mining: the share of a rock that is left** on the surface side.
  - It is an idea only, and it has not been looked at.
- Decided 2026-10-23: 1920 x 1080 is the smallest screen WFMT is laid out for, and ultrawide screens must work. The default spots are tested not to overlap or leave the screen at 2560 x 1080, 3440 x 1440, 3840 x 1080, 5120 x 1440 and 5760 x 1080. When nothing from the game or the overlay gives the screen size, WFMT reads the primary monitor from the operating system. Still to check by eye on a real ultrawide screen: the cards in the game, and the layout picture on Overlay Placement.

## Not planned

The journal does not contain the data these features would require. Decisions are recorded in [STATUS.md](STATUS.md).

- Guardian ruin and structure surveying: the journal does not record the structures' layout or contents.
- Landing-pad diagrams: the journal provides no layout, orientation or positions.
- An FSS spectrum guide (which body types sit where on the scanner's band): the journal never records where a signal sits on the band and no open table of ranges exists, so the ranges would have to be measured in the game.
