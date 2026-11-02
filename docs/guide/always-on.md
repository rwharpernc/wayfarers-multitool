# Landing Assist, Interdiction Warning, Flight Alerts and the Route overlay

This page describes four tools that are available in every mode and belong to no mode: Landing Assist, Interdiction Warning, Flight Alerts and the Route overlay.

- Interdiction Warning and Flight Alerts draw only on the game screen and require a running overlay.
- Landing Assist can display in the EDMC panel without an overlay. Its diagram on the game screen requires an overlay.

See [Getting started](getting-started.md#what-you-need) and [Setting up the overlay](../OVERLAY_SETUP.md).

**Data sources.** Landing Assist, Interdiction Warning and Flight Alerts use data the game writes: the journal and, for fuel, `Status.json`.

- Landing Assist receives a pad number and the station type from the journal, with no pad orientation.
- Interdiction Warning combines the game's early signals with the `Interdicted` and `EscapeInterdiction` events.
- Flight Alerts reads `CarrierJumpRequest`, `Loadout`, `FSDTarget` and the fuel in `Status.json`.
- Nothing is looked up online by these three. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

**On this page:** [How to](#how-to) · [Landing Assist](#landing-assist) · [Interdiction Warning](#interdiction-warning) · [Flight Alerts](#flight-alerts) · [Route overlay](#route-overlay) · [Overlay connection](#overlay-connection) · [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)

## How to

All four tools are off by default. Verify the overlay connection before enabling any of them.

### Check the overlay first

1. Open **Settings → WFMT → Overlays → Overlay Connection**.
2. Choose which overlay draws: WFMT's built-in overlay (Windows) or EDMCModernOverlay.
3. Press **Check connection**. The result states whether the overlay is reachable. See [Overlay connection](#overlay-connection).

### Turn on Landing Assist, place it and test it

1. Open **Settings → WFMT → Overlays → Landing** and tick **Enable Landing**.
2. Select where it displays: **Show in EDMC app** and/or **Show on Overlay**. The diagram on the game screen requires **Show on Overlay**.
3. Press **Test Overlay** to verify that the diagram displays.
4. To move it, open **Overlay Placement** (same location) and adjust "Landing assist". The default is the bottom left.

Detail: [Landing Assist](#landing-assist).

### Turn on Interdiction Warning, place it and test it

1. Open **Settings → WFMT → Overlays → Interdiction Warning** and tick **Enable Interdiction Warning**.
2. Press **Test Warning**. The test works while the feature is off and reports whether an overlay could be reached.
3. To move it, open **Overlay Placement** and adjust "Interdiction warning". The default is the top center.

Detail: [Interdiction Warning](#interdiction-warning).

### Turn on Flight Alerts, place it and test it

1. Open **Settings → WFMT → Overlays → Flight Alerts** and tick **Enable Flight Alerts**.
2. Keep **Fleet carrier jump countdown**, **Fuel warnings** and **Mining alerts** ticked, or untick the unwanted ones. Adjust the percentages.
3. Optionally tick **Play a sound when an alert starts**.
4. Press **Test Card**. The test works while the feature is off.
5. To move it, open **Overlay Placement** and adjust "Flight alerts (carrier jump, fuel)". The default position is on the right, below the Inventory display.

Detail: [Flight Alerts](#flight-alerts).

### Turn on the Route overlay, place it and test it

1. Open **Settings → WFMT → Overlays → Route** and tick **Enable the Route overlay**.
2. Set **Systems listed** (3 to 20; 8 by default).
3. Optionally tick **Mark the systems ahead that EDSM does not know yet**.
4. Press **Test Card** to display a sample route. The test works while the feature is off.
5. To move it, open **Overlay Placement** and adjust "Route and ship status". The default is the top left.

Detail: [Route overlay](#route-overlay).

### Example: docking with Landing Assist

Precondition: **Enable Landing** and **Show on Overlay** are ticked.

1. Docking permission is requested. The card shows **Docking Requested** and the station name, for example `Jameson Memorial`.
2. The station grants permission. The status changes to **Docking Approved** and the card adds the pad (`Pad 24`) with the starport diagram and the assigned pad marked. In the EDMC panel (with **Show in EDMC app** ticked) the line reads `Docking Approved — Jameson Memorial — Pad 24`.
3. After landing, the card remains for about ten seconds, then clears.
4. If the station refuses, the status is **Docking Denied** with the reason in words, such as *All pads occupied*.

The diagram marks the assigned pad but not its orientation; the journal provides only the pad number.

### Example: an interdiction

Precondition: **Enable Interdiction Warning** is ticked; the ship is in supercruise.

1. When the game's interdiction flag changes, a card headed **INTERDICTION WARNING** appears with `Interdictor: CMDR Name (Commander)`. The name reads `Unknown` until the game provides it.
2. If the interdiction is evaded, the game writes `EscapeInterdiction`; the card adds **Escaped** in green for about eight seconds, then clears.
3. If the ship is pulled out of supercruise, the card adds **Pulled from supercruise** in red. If the commander submits, it adds **Submitted to interdiction** in amber.

The in-game screen is the authoritative source.

### Example: a Flight Alert

Precondition: **Enable Flight Alerts** is ticked with the default fuel thresholds (25 and 50 percent).

1. A route to a neutron star is plotted with the tank at 38 percent. The card shows `No scoop at next star`, `(neutron star)` and `Fuel 38% (12.2 t)`.
2. Later the tank falls to 22 percent. The card shows `Low fuel` with `Tank 22% (7.0 t)` beneath it.
3. A fleet carrier jump is scheduled. The card counts down, for example `Carrier jump in 14:32`, turns red for the last minute, and shows `Carrier departing now` at the departure time.

Fuel warnings display only while the main ship is flown, and not while docked, landed or scooping.

### Example: the Route overlay

Precondition: **Enable the Route overlay** is ticked and **Systems listed** is 8.

1. A route to Colonia is plotted in the [Route Planner](exploration.md#route-planner) or on the game's galaxy map.
2. The card shows `You are navigating to:`, `Colonia`, `You will be there in 12 jumps.`, the next systems each with its star on the right, and the light years remaining at the bottom.
3. After a jump to the first system, that system is removed from the list, the jump count decreases by one, and the remaining light years are recalculated from the current position.
4. At the last system, the card shows `Route ended.`, `You have arrived at Colonia.` and `The route is being reset.` for ten seconds, then closes.

Star colors: green can be scooped, yellow cannot, blue is a neutron star, red is a white dwarf.

## Landing Assist

Shows the landing pad assigned during docking, in the EDMC panel and/or as a diagram on the game screen.

**Setup:**

1. Open **Settings → WFMT → Overlays → Landing**.
2. Tick **Enable Landing** (off by default).
3. Select the display: **Show in EDMC app** (the panel; on by default once Landing is enabled) and/or **Show on Overlay** (the diagram on the game screen; off by default).
4. Press **Test Overlay** to verify that the diagram displays.

Position is set on **Overlay Placement** ("Landing assist"); the default is the bottom left.

If the overlay is still starting when docking is approved, WFMT retries for up to three minutes so that the diagram appears when the overlay is available.

**Status.** The status follows the journal's record of the docking request:

| Status | When | Additional content |
|---|---|---|
| **Docking Requested** | Permission was requested from the station | Station name |
| **Docking Approved** | Permission was granted; shown again after touchdown | Station name and `Pad 24` |
| **Docking Denied** | The station refused | The reason: *All pads occupied*, *Ship too large*, *Hostile to station*, *Criminal offences*, *Must be within 7.5km*, *Active SLF deployed*, *Carrier access restricted* or *Carrier jump imminent*. Any other reason is shown as the game wrote it |

- In the EDMC panel the status is one line, such as `Docking Approved — Jameson Memorial — Pad 24`, with the diagram beneath it. The line wraps rather than widening the window.
- On the game screen the status is a card with the same text and the diagram.
- **The diagram** is a plan of the station's pads with the assigned pad marked. Two layouts exist: the **starport** layout (Coriolis, Orbis, Ocellus, asteroid bases and planetary ports) and the **fleet carrier** layout (fleet carriers, squadron carriers, colonization ships and dockable megaships). Outposts and other facilities have no diagram; only the pad number and text are shown.
- The journal's station type distinguishes a carrier from a station. A four-character name is treated as a squadron carrier.
- After touchdown the card remains for about ten seconds, then clears. A new jump, a supercruise entry or a stale request clears a request that never completed.
- Nothing is displayed for a station for which docking was not requested.

## Interdiction Warning

Displays an alert on the game screen when an interdiction starts. There is no panel button; configuration is in Settings.

**Setup:**

1. Open **Settings → WFMT → Overlays → Interdiction Warning**.
2. Tick **Enable Interdiction Warning** (off by default).
3. Press **Test Warning** to display the warning. The test works while the feature is off and reports whether an overlay could be reached. Position is set on **Overlay Placement** ("Interdiction warning"); the default is the top center.

**Display.** A card headed **INTERDICTION WARNING** with the line `Interdictor: CMDR Name (Commander)` (or `(Thargoid)`). The name is `Unknown` until the game provides it; `— Power: <name>` is appended when the interdictor belongs to a Power. When the interdiction ends, the card adds the outcome in color for about eight seconds, then clears:

| Outcome | Shown as |
|---|---|
| Escaped | **Escaped** (green) |
| Pulled out of supercruise | **Pulled from supercruise** (red) |
| Submitted | **Submitted to interdiction** (amber) |

**Detection.** Three signals; the first to arrive raises the warning:

1. The game's "being interdicted" flag in `Status.json`, which changes when the interdiction minigame starts. The game writes the file about once per second, so detection can trail the event by up to one second.
2. An NPC line in chat (the `npc` channel only, never system or squadron chat). A line can arrive before the flag. WFMT reads the game's message key first (the `$Pirate_...` name, identical in every language) and the wording only for a key it does not recognize. Lines from pirates, Hitmen, cargo hunters and bounty hunters targeting the commander in supercruise, an assassin approaching for a failed mission, and a pirate scanning the hold raise the warning. Lines from a pilot calling for help, an escort or a miner do not.
3. The `Interdicted` and `EscapeInterdiction` journal events after the interdiction ends. They carry the interdictor's name, whether it is a player or a Thargoid, and its Power.

If the flag drops without a journal event, the card clears after three seconds. A warning raised by a chat line and never confirmed clears after 75 seconds.

If an interdiction occurs without a prior warning, enable [the diagnostic log](reporting-problems.md#the-diagnostic-log). WFMT then writes the NPC lines from the preceding 75 seconds.

## Flight Alerts

One card on the game screen with three functions. There is no panel button; configuration is in Settings.

- **Fleet carrier jump countdown.** When a jump is scheduled, the card counts down to the departure time the game provided:
  - `Carrier jump in 14:32`
  - `To: Eorld Byoi XX-X d1-23` (the system, on its own line)
  - `Body: A 2` when the jump targets a particular body (only the part of the body name after the system name)
  - The card turns red for the last minute and shows `Carrier departing now` at the departure time.
  - A cancelled jump, or the jump itself, clears it.
  - WFMT reads the request from the newest journals at start-up, so restarting the game or EDMC during the countdown does not lose it.
- **Fuel warnings.** Two warnings:
  - `Low fuel` with `Tank 22% (7.0 t)` beneath it when the tank is at or below the configured percentage (the game's own cockpit warning occurs at 25%).
  - `No scoop at next star`, `(neutron star)`, `Fuel 38% (12.2 t)` when the plotted star cannot be scooped (neutron stars, white dwarfs, black holes and other non-main-sequence stars) and the tank is at or below a second percentage.
- **Mining alerts.** While mining:
  - A green `Core asteroid` card with the core mineral for 30 seconds when a prospected rock is a core asteroid.
  - A green `Rich rock: Painite` card for each target commodity (set on the Settings card of the Space Mining window; several targets can be set, each with its own percentage) of which a rock holds at least the percentage. A rock rich in more than three targets shows the richest three.
  - An amber `Low on limpets` when the limpets aboard are at or below the configured number.
  - An amber `Hold nearly full` when the hold is at or above the configured percentage. It follows the cargo in `Status.json` as it changes, and the `Cargo` event when that is unavailable. The figure is not used while the Rhino is out.

  Mining alert conditions:
  - The limpet and hold alerts display only while mining (a prospector, refinery or collector event within the last half hour).
  - The limpet count is exact once EDMC has supplied the cargo to WFMT.
  - The limpet alert appears only when a limpet controller is fitted (or limpets have been seen aboard since the last loadout) and never while the Rhino is out.
  - A rock prospected twice raises its alert once (once per target it holds). A rock with less than a quarter of itself remaining raises no rich-rock alert; a core alert is still raised.

**Setup:**

1. Open **Settings → WFMT → Overlays → Flight Alerts**.
2. Tick **Enable Flight Alerts** (off by default). Beneath it:
   - **Fleet carrier jump countdown (alerts at 10, 5 and 1 minute, and at departure)** (on).
   - **Fuel warnings** (on), with two percentages, each 5 to 95: **Warn when the tank is at or under** (25 by default) and **Warn about a star that cannot be scooped when the tank is at or under** (50 by default).
   - **Mining alerts (a core asteroid, a rock rich in your target commodity, low limpets, a nearly full hold)** (on), with **Warn when the limpets aboard are at or under** (0 to 99; 5 by default) and **Warn when the hold is at or over** (50 to 100 percent full; 95 by default).
   - The target commodity and its percentage for the rich-rock alert are set on the Settings card of the **Space Mining** window. A core asteroid is always flagged.
3. Optionally tick **Play a sound when an alert starts** (off by default). The sound plays when a fuel or mining alert starts and at 10 minutes, 5 minutes, 1 minute and departure for a carrier jump. The box is unavailable where WFMT cannot play a sound (on Linux it requires `canberra-gtk-play` or `paplay`).
4. Press **Test Card**. The test works while the feature is off and reports whether an overlay could be reached.

The card has a fixed width and wraps text onto additional lines (at the end of a sentence first), growing downward.

- Fuel warnings display only while the main ship is flown, and not while docked, landed or scooping.
- Position is set on **Overlay Placement** ("Flight alerts (carrier jump, fuel)"); the default is on the right, below the Inventory display.

## Route overlay

One card on the game screen for the route being followed. There is no panel button; configuration is in Settings.

The card copies the route plotted in the [Route Planner](exploration.md#route-planner) or, when none exists, the route plotted on the game's galaxy map:

```
You are navigating to:
Colonia
You will be there in 12 jumps.
------------------------------
Alpha Centauri        K
Sample System 3       NEUTRON
Sample System 9       WHITE DWARF
...
------------------------------
4,310 LY left to jump.
```

- **The systems are not numbered.** The next system is listed first, each with its star on the right.
  - On reaching a system, it is removed from the list, the jump count decreases, the remaining light years are recalculated from the current position, and the list advances.
  - **Systems listed** sets the number of systems shown. The jump count and light years cover the whole route.
- **A route recalculated in the galaxy map is followed within a second.** WFMT reads the game's `NavRoute.json` when the journal reports a change and whenever the file is rewritten (the journal can announce a route before the game writes it). Reading starts after the first journal event of the session, so a route left from an earlier session is not shown. A file that cannot be read is retried only when it changes.
- **The Route Planner's route takes precedence** while it has a jump remaining; afterwards the game's plotted route is used. With neither, nothing is drawn.
- **Light years** are the straight-line distances between the systems of the route. A route given by the game without positions shows no light-years line.
- **Star colors.**
  - **Green**: a star that can be scooped (class letters on the game's route; `FUEL` on a Route Planner route).
  - **Yellow**: a star that cannot be scooped (a black hole, a brown dwarf and similar; `NO FUEL`).
  - **Blue**: a neutron star (**yellow `NEUTRON ?`** when the Route Planner indicates the neutron star may be a secondary star away from the arrival point).
  - **Red**: a white dwarf.
  - A system unknown to EDSM receives a **\*** after its name when that option is ticked.
- **End of route.** The card shows `Route ended.`, `You have arrived at <destination>.` and `The route is being reset.` for ten seconds. The route is then reset (the Route Planner's route is cleared, or the game's route forgotten) and the card closes. A route finished before WFMT saw it produces no message.
- **Not on this card:** fuel, jump range, the next supercharge, refuel stops and the running expedition. The Exploration Dashboard shows fuel, range and route status.

**Setup:**

1. Open **Settings → WFMT → Overlays → Route**.
2. Tick **Enable the Route overlay** (off by default). **Systems listed** (3 to 20; 8 by default) sets how many of the next systems the card lists.
3. Optionally tick **Mark the systems ahead that EDSM does not know yet** (off by default). This is the only online part of the Route overlay: it sends EDSM the names of the next systems on the route and nothing about the commander.
   - A listed system with no EDSM record receives a **\*** after its name.
   - A system unknown to EDSM has not been uploaded by any commander sharing with EDSM.
   - If EDSM cannot be reached, nothing is marked and the check is retried after a few minutes. A failed check never marks a system as unknown.
4. Press **Test Card** to display a sample route (with the EDSM option ticked, the third and seventh systems of the sample show the mark). The test works while the feature is off and reports whether an overlay could be reached.

The card follows the route as jumps are made and clears when the end is reached, the route is cleared, or a jump is made to a system not on the route.

- After a restart WFMT reads the route the game has saved, and the card returns.
- Every line starts at the same left edge. Padding and text size follow **Appearance**.
- Position is set on **Overlay Placement** ("Route and ship status"); the default is the top left, above the Colonization list.

**Limits:**

- The journal does not state the fuel cost of the next jump. The card shows the fuel on board and what the last jump used.
- The range is the ship's maximum with its current modules, from the `Loadout` event, not the range with the current cargo and fuel.
- Distances are straight lines between the systems on the route.
- The EDSM check covers the listed systems and a few beyond (30 at most), queries once for the whole list, and queries again about a system EDSM did not know after ten minutes.
- EDSM contains only what its users uploaded; a missing system does not prove that nobody has visited it.

## Overlay connection

All four tools use the connection settings on the **Overlay Connection** Settings tab (Settings → WFMT → Overlays). Screen positions are set on **Overlay Placement** (same location).

- The **Overlay Connection** tab also selects which overlay draws: WFMT's built-in overlay (Windows) or EDMCModernOverlay.
- For EDMCModernOverlay the defaults are `127.0.0.1` and port `5010`.
- **Check connection** reports whether the overlay is reachable.

See [Setting up the overlay](../OVERLAY_SETUP.md).

## What the game does and doesn't tell us, and how to work around it

WFMT uses only what Elite Dangerous writes to its journal files; these tools use no outside service. Where WFMT cannot be certain, it states so. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| Expectation | What the game provides | Action |
|---|---|---|
| Landing Assist shows pad orientation | The journal gives only a **pad number** and the station type | Use the diagram to identify the pad; align using the pad numbers in the game |
| A diagram for every facility type | Some facilities have no diagram, and the journal does not provide enough information (layout, orientation) to draw one | Use the pad number and the game's own docking guidance |
| Interdiction Warning fires before the game confirms | It combines the `Status.json` interdiction flag (written about once per second), an NPC chat line, and then the `Interdicted` and `EscapeInterdiction` events, which arrive separately. A chat line is not proof of an interdiction | Use the in-game screen as the authoritative source |
| A fuel warning stating whether the next jump is possible | The journal does not state the fuel cost of a jump | WFMT compares **percentages** of the tank; choose percentages suited to the ship |
| A fuel percentage immediately after EDMC starts | The tank size comes from the `Loadout` event, written at login and when the ship or a module changes. Until then WFMT has fuel in tons but no percentage | Until then only the game's low-fuel flag is used. Log in again, or change a module or ship, so that the game writes the event |
| A countdown for a jump not scheduled by the commander | WFMT knows only a request the game wrote to the commander's journal | Use the in-game carrier screen |
| An unscoopable-star warning for an unplotted star | The star class comes from the target the game reports (`FSDTarget`) | Plot or select the next jump; the warning then appears |
| Automatic overlay discovery | WFMT draws only if an overlay listens on the configured connection details | Use **Check connection**, **Test Overlay**, **Test Warning** and **Test Card** in Settings |
