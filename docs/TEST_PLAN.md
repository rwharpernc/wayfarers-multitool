# Test plan: 1.0.0

What to check in EDMC after the 1.0.0 release (and before any later one), on **Windows** first and then on **Linux**.

- This is the quick pass over the whole release:
  - the Rare Goods Finder
  - Mining
  - the Carrier Route window
  - the Expedition, Route Planner and overlay basics
- The rest of the in-game checks (every mode and window) are under "Verification in the game" in [TODO.md](TODO.md).
- The unit and smoke tests pass, but they cannot show what the game, the overlay and a real clipboard do.
- The overview is in [CHANGELOG.md](../CHANGELOG.md) and [STATUS.md](STATUS.md). The longer wording for each check is in [TODO.md](TODO.md) (under "Verification in the game").

## Where the testing stands (2026-10-26)

| Platform | Automated tests | Checks in the game |
|---|---|---|
| **Windows** | The logic tests run natively and pass. The Windows-only code (the overlay, Win32 and WebView2) is proved only by the in-game pass. | Not yet recorded for 1.0.0. Sections 1 to 6 below are open. |
| **Linux** | 3,447 tests pass in the Docker container (Xvfb and a window manager), 12 skipped, run on 2026-10-26 before the release was cut. | Not yet recorded for 1.0.0. The last manual passes (2026-10-18 and 2026-10-20) were of builds from before the rename; see [STATUS.md](STATUS.md) and [LINUX_TESTING.md](LINUX_TESTING.md). |

- 1.0.0 was released on 2026-10-26 (tag `v1.0.0`). These passes are the checks to run on the released build, and a failure goes to a fix on a short
  `bugfix/1.0.1` branch.
- Tick a box in the sections below only when you have seen it pass; nothing here has been ticked from the automated run.

**Reporting**

- Tick a box when the check passes.
- When something fails, say which check, the system, and what you saw, with the relevant lines of EDMC's log.
  - Windows: `%LOCALAPPDATA%\EDMarketConnector\logs\`
  - Linux: `~/.local/share/EDMarketConnector/EDMarketConnector.log`

## Getting the build

1. Run `npm run deploy` from the branch being tested. It builds and merges the result into EDMC's plugins folder (native or Flatpak). Restart EDMC (every deploy needs a restart).
2. New files appear beside the plugin as you use the features: `carrier_route.json` (Carrier Route) and `mining_history.json` (Mining History), one record per commander.

## 1. Rare Goods Finder (Powerplay mode, RARES)

- [ ] The window shows **Distance**, **Arrival**, **Legality** and the other columns without cutting any off, and fits your screen.
- [ ] Distance is 0.0 ly for a rare in your own system and grows down the list; it updates after a jump. Clicking a heading sorts by number, and a second click reverses it.
- [ ] Spot-check Arrival (a station's distance from its star, in light seconds) against the game for a near station, a far one and Hutton Orbital.
- [ ] Legality: most rows say *Legal*; in a Federation or Alliance theocracy or a Prison Colony system, Lavian Brandy says *Illegal here*; selecting a row says where it is illegal. Compare with the station's Prohibited list on the system map.
- [ ] **Large pads only** keeps only large-pad stations.
  - **Only my Power** is grayed out until your Power is known, then keeps the rares whose origin system your Power controls (the status line shows Spansh being asked, ten at a time).
  - Both choices are remembered.
- [ ] **Copy system** puts the selected rare's origin system on the clipboard (check it pastes into the galaxy map).

## 2. Mining (Mining mode)

- [ ] Space Mining page: **Last rock** follows each prospected rock; a core asteroid adds `core: <mineral>` and **Core asteroids found**; the limpet figure reads `(N on board)` and matches your cargo.
- [ ] Settings → Mining: type a target commodity and a percentage; a rock at or over it says `target`.
- [ ] Accept a mining mission: **Mission needs** shows its tons against what you hold, and changes as the hold changes.
- [ ] Flight Alerts (Settings → Overlays → Flight Alerts, Mining alerts ticked): the Test Card shows the green core lines.
  - In a ring a core asteroid and a rich rock give a green card for about 30 seconds.
  - Low limpets and a nearly full hold give amber cards.
  - None shows while you are not mining.
  - The sound plays if ticked.
- [ ] **Mining History** (the DASHBOARD button): the Overview, Commodities, Rings and Runs tabs fill from your journals and sort; the totals look right against what you remember.
- [ ] **BOOK** on the Space Mining page opens the **Space Mining Book**.
  - It lists rings from your journals with hotspots per mineral, class, reserve level, tons mined and last mined.
  - Try a note, a favorite, **Find**, **Add ring** and **Copy system**. Restart EDMC and the notes remain.
  - **BOOK** on the Surface Mining page opens the **Surface Mining Book**, with a **From your journals** group (bodies with mining locations and the tons refined on them).
- [ ] **This system** (in both books):
  - In a system you have mined it goes to the ring or body. In one you have not it says `You have not worked this system yet.`
  - On the first open of each book a notice says the journals are being read, and the list does not flicker while it grows.
- [ ] The Surface Compass, the Surface Mining Book's stops and Market research, and Share line still work (their checks are in [TODO.md](TODO.md)).

## 3. Carrier Route (Route Planner window → Carrier route)

- [ ] The carrier block and the boxes fill in from the journal (where the carrier is, the tritium in its tank, the space used) and match Carrier Management. If they say not known, open Carrier Management once.
- [ ] Type a destination and press **Generate route**. Compare the jumps and the tritium with Spansh's own Fleet Carrier Router page for the same carrier. The first line says how much tritium to have at the start.
- [ ] **Copy next system** puts the next system on the clipboard (check it pastes). Schedule the jump in the game; when the carrier arrives the row turns green and the next is marked. **Mark next as reached** does it by hand.
- [ ] Restart EDMC: the route comes back. A second commander sees none.
- [ ] If you have a squadron carrier, choose it in the Carrier box and plot one.

## 4. Expedition, Route Planner and overlays

- [ ] **EXPEDITION** and **PLOT** on the panel open one window with Plan, Route and Log tabs, never twice; its size and position are remembered.
  - The Expedition section holds the Log's figures and START, PAUSE and STOP.
  - There is no Expedition Log section.
- [ ] The Expedition window's **Neutron route** switches to the Route tab.
  - **Road to Riches** and **Exomastery** open their dialog and **Plot** works.
  - **Start expedition** in the Route Planner window makes an expedition from a plotted route (named `Neutron Highway from <start> to <destination>`) and starts it and its Expedition Log run. The status line turns green and the button reads **Started ✓** for a few seconds.
  - **Review** switches to the Plan tab on it.
  - Pause, Resume and Stop on either side agree.
- [ ] The overlays show and hide from the panel's overlay line; each mode's panel lays out cleanly and does not widen the EDMC window; the Expedition row still shows the next stop, its distance and note.

## 5. Added since this plan was written (2026-10-23)

Do these on **Windows** and again on **Linux**. Where the two differ the line says so.

- [ ] **Every overlay is off after the first start of this build.**
  - Restart EDMC. The log has one line, `All WFMT overlays reset to disabled (one-time), including the saved choices of N commander(s)`, and no overlay card shows for any commander.
  - Turn one card on, restart, and check it is still on (the reset runs once).
  - Windows: log in as each commander you have and check none shows a card. Linux: the same, and check `overlay_settings.json` beside the plugin.
- [ ] **A stopped expedition carries on from where it stopped.**
  - Start an expedition, jump or scan, press STOP, wait a minute, start it again from the Route tab, and check the clock carries on from where it stopped.
  - The Log's **Resume** does the same.
  - Pause one for a minute, make a few jumps while it is paused, resume it, press **Rescan** in the Log window, and check the rescanned totals do not include the jumps made while it was paused.
- [ ] **The screen size.** Settings → Overlays → Overlay Placement says where the size came from.
  - With the game's files or the overlay running it names them.
  - Rename the overlay's log (EDMCModernOverlay's `overlay_client.log`) and the game's `DisplaySettings.xml` so neither is found, press **Detect screen again**, and check it says it is using the primary display, with your real resolution. Put the files back afterwards.
  - Windows: the size is the hardware resolution, not the scaled one (3840 x 2160 at 125% reads 3840 x 2160). Linux: report the session type (Wayland or X11) and whether `xrandr` is installed.
  - On an ultrawide or triple screen, open the placement preview and check no box is off the screen or on top of another.
- [ ] **Long names in the tables.** In the Missions, Source commodities, Ship Builds and My Codex windows a long faction, station, ship, role or site name shows whole at a wide size and cut with an ellipsis at a narrow one, and the window does not grow wider than its size.
- [ ] **Saved data from before the spelling change** (a copy that predates this build). Start EDMC and look for `Renamed saved names:` in the log, once. The Colonization page, the Sites window, the fleet carrier column and the overlay positions are as you left them. A body or system whose name holds the letters of an old spelling inside a word (the old spelling of tons or analyzed) keeps its name.

## 6. Added since section 5 (2026-10-26): Colonization

Do these on **Windows** and again on **Linux**. The longer steps are in [TODO.md](TODO.md) (Missions, trade and colonization) and [LINUX_TESTING.md](LINUX_TESTING.md).

- [ ] **The hold follows a purchase.** Buy a tracked commodity at a market: the **In Cargo** figures in the Sites window, on the COL page and on the overlay card change within a couple of seconds.
- [ ] **Acquire is what is still to get.** It falls as you load the ship or the carrier and reaches 0 once the whole amount is acquired; **Haul Trips** still counts everything the site needs. The overlay card shows the same Acquire and no To buy column.
- [ ] **A lagging Frontier copy does not undo a transfer.** With EDMC signed in to Frontier, unload cargo at your fleet carrier, then open Carrier Management or fly back for another load. The FC column keeps the unloaded stock, and an `ignored` line from `Carrier cargo from Frontier` is in the WFMT log lines (press **Copy diagnostics** to see them). After 15 minutes without a transfer, open Carrier Management again: a Frontier figure that has changed replaces the tally, and one that is unchanged stays ignored.
- [ ] **Hide covered rows on the overlay card.** With *Hide commodities already covered by the hold and the fleet carrier* ticked (the default) covered commodities are left out and the footer still counts them; unticked, they are listed.
- [ ] **Best single systems.** After **Find all** with two or more commodities, the results start with the best single systems, each with its coverage, distance, basket cost and stations in the order to visit. **Copy Route** copies the best system first, and **Stop** keeps what was found.
- [ ] **Raven Colonial.** **PROJECTS** opens My Projects (reading needs no key). **Create Project on Raven** at a construction site you are docked at: check the project, the link, the primary project and the attached carrier on ravencolonial.com.

## Linux specifics

The same checks apply. The points that differ:

- Overlays need EDMCModernOverlay (the built-in overlay is Windows only).
- The clipboard needs a working clipboard tool, so check each **Copy** button and paste.
- A Flatpak EDMC needs the permissions in [WFMT on Linux](guide/linux.md).
- The screen size falls back to `xrandr` (through the host from a Flatpak) when the game's files and the overlay's log cannot be read.

Report the distro, desktop, X11 or Wayland, and native or Flatpak EDMC.
