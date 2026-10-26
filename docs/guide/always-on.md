# Landing Assist, Interdiction Warning, Flight Alerts and the Route overlay

These four tools are always available, whichever mode you're in. They don't belong to a mode.

- Interdiction Warning and Flight Alerts draw only on your game screen, so they need an overlay running.
- Landing Assist can show in the EDMC panel without one, but its diagram on the game screen needs an overlay.

See [Getting started](getting-started.md#what-you-need) and [Setting up the overlay](../OVERLAY_SETUP.md).

**Where this comes from:** Landing Assist, Interdiction Warning and Flight Alerts run on what the game writes (the journal, and for fuel the game's `Status.json`).

- The journal gives Landing Assist a pad number and the station type, with no orientation.
- Interdiction Warning combines the game's early signals with its own `Interdicted` and `EscapeInterdiction` events.
- Flight Alerts reads `CarrierJumpRequest`, `Loadout`, `FSDTarget` and the fuel in `Status.json`.
- Nothing is looked up online. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## Landing Assist

Shows which landing pad you've been assigned while docking, in the EDMC panel and/or as a diagram on your game
screen (you choose which in Settings).

**To set it up:**

1. Open **Settings → WFMT → Overlays → Landing**.
2. Tick **Enable Landing**. It is **off by default**.
3. Choose where it shows: **Show in EDMC app** (the panel; on by default once Landing is enabled) and/or
   **Show on Overlay** (the diagram on your game screen; off by default).
4. Press **Test Overlay** to check the diagram shows.

Where it sits is set on **Overlay Placement** ("Landing assist"); by default it is at the bottom left.

If the overlay is still starting when docking is approved, WFMT keeps retrying for up to three minutes, so the
diagram appears as soon as the overlay is up.

**What it shows.** The status goes through what the game's journal says about your docking request:

| Status | When | What else it shows |
|---|---|---|
| **Docking Requested** | You asked the station for permission | The station name |
| **Docking Approved** | Permission was granted, and again after you touch down | The station name and `Pad 24` |
| **Docking Denied** | The station refused | The reason, in words: *All pads occupied*, *Ship too large*, *Hostile to station*, *Criminal offences*, *Must be within 7.5km*, *Active SLF deployed*, *Carrier access restricted* or *Carrier jump imminent* (any other reason is shown as the game wrote it) |

- In the EDMC panel it is one line, such as `Docking Approved — Jameson Memorial — Pad 24`, with the diagram under it. The line wraps rather than widening the window.
- On the game screen it is a card with the same text and the diagram.
- **The diagram** is a plan of the station's pads with yours marked. There are two layouts: the **starport** layout (Coriolis, Orbis, Ocellus, asteroid bases and planetary ports) and the **fleet carrier** layout, used for fleet carriers, squadron carriers and colonization ships. Outposts and other facilities have no diagram, so you get the pad number and the text only.
- A carrier is told from a station by its type in the journal; a four-character name is taken to be a squadron carrier.
- After you touch down the card stays for about ten seconds and then clears. A new jump, a supercruise entry or a stale request clears a request that never finished.

The panel line and the card appear only for what the journal reports: nothing is drawn for a station you never requested docking at.

## Interdiction Warning

Puts an alert on your game screen the moment an interdiction starts. It has no panel button, only Settings.

**To set it up:**

1. Open **Settings → WFMT → Overlays → Interdiction Warning**.
2. Tick **Enable Interdiction Warning**. It is **off by default**.
3. Press **Test Warning** to see what it looks like. Where it sits is set on **Overlay Placement** ("Interdiction warning"); by default it is at the top center. The test works even while the feature is off, and reports
   whether an overlay could be reached.

**What you see.** A card headed **INTERDICTION WARNING** with a line `Interdictor: CMDR Name (Commander)` (or `(Thargoid)`; the name is `Unknown` until the game gives it, and `— Power: <name>` is added when the interdictor belongs to a Power). When it resolves, the card adds the outcome in color for about eight seconds and then clears:

| Outcome | Shown as |
|---|---|
| You escaped | **Escaped** (green) |
| You were pulled out of supercruise | **Pulled from supercruise** (red) |
| You submitted | **Submitted to interdiction** (amber) |

**How it knows.** Three signals, whichever arrives first:

1. The game's own "being interdicted" flag in `Status.json`, which flips the moment the interdiction minigame starts. The game writes that file about once a second, so this can trail the instant by up to a second.
2. An NPC's taunt in the chat (the `npc` channel only, never system or squadron chat, which other commanders type into). A taunt can arrive before the flag.
3. The authoritative `Interdicted` and `EscapeInterdiction` journal events once it is over. They carry the interdictor's name, whether it is a player or a Thargoid, and its Power.

If the flag drops without a journal event, the card clears after three seconds. A warning that came from a chat taunt and is never confirmed clears after 75 seconds.

## Flight Alerts

One small card on your game screen with three jobs. It has no panel button, only Settings.

- **Fleet carrier jump countdown.** When you schedule a jump, the card counts down to the departure time the game gave, on short lines:
  - `Carrier jump in 14:32`
  - `To: Eorld Byoi XX-X d1-23` (the system, on a line of its own)
  - `Body: A 2` when the jump is to a particular body (just the part of the body's name after the system's, not the whole name again)
  - It turns red for the last minute, and says `Carrier departing now` at the time.
  - A cancelled jump, or the jump itself, clears it.
  - WFMT reads the request back from your newest journals when it starts, so restarting the game or EDMC during the countdown does not lose it.
- **Fuel warnings.** Two warnings:
  - `Low fuel` with `Tank 22% (7.0 t)` under it when the tank is at or under the percentage you choose (the game's own cockpit warning comes at 25%).
  - `No scoop at next star`, `(neutron star)`, `Fuel 38% (12.2 t)` when the star you have plotted to is one you cannot scoop (neutron stars, white dwarfs, black holes and the other non-main-sequence stars) and the tank is at or under a second percentage. That second warning is the one the game does not give you.
- **Mining alerts.** While you mine:
  - A green `Core asteroid` card with the core mineral for 30 seconds when a prospected rock is a core asteroid.
  - A green `Rich rock: Painite` card for each target commodity (set under Settings → WFMT → Mining; several can be set, each with its own percentage) that a rock holds at least the percentage of. A rock rich in more than three targets shows the richest three.
  - An amber `Low on limpets` when the limpets aboard are at or under a number you choose.
  - An amber `Hold nearly full` when the hold is at or over a percentage you choose. It follows the cargo in the game's `Status.json` as it changes, and the `Cargo` event when that is not available; it does not use the figure while the Rhino is out.

  Details of the mining alerts:
  - The limpet and hold alerts only show while you are mining (a prospector, refinery or collector event in the last half hour), so a full hold for another reason never nags.
  - The limpet count is exact once EDMC has told WFMT your cargo.
  - The limpet alert only appears when a limpet controller is fitted (or limpets have been seen aboard since the last loadout), and never while the Rhino is out. A Rhino miner or a laser miner who carries no limpets is not warned.
  - A rock you prospect twice raises its alert once (once for each target it holds), and a rock with under a quarter of itself left does not raise a rich-rock alert (a core alert is still raised).

**To set it up:**

1. Open **Settings → WFMT → Overlays → Flight Alerts**.
2. Tick **Enable Flight Alerts**. It is **off by default**. Under it:
   - **Fleet carrier jump countdown (alerts at 10, 5 and 1 minute, and at departure)** (on).
   - **Fuel warnings** (on), with two percentages, each from 5 to 95: **Warn when the tank is at or under** (25 by default) and **Warn about a star that cannot be scooped when the tank is at or under** (50 by default).
   - **Mining alerts (a core asteroid, a rock rich in your target commodity, low limpets, a nearly full hold)** (on), with **Warn when the limpets aboard are at or under** (0 to 99, 5 by default) and **Warn when the hold is at or over** (50 to 100 percent full, 95 by default).
   - The target commodity and its percentage for the rich-rock alert are set under **Settings → WFMT → Mining**; a core asteroid is always flagged.
3. Optionally tick **Play a sound when an alert starts** (off by default): it plays when a fuel or mining alert starts and at 10 minutes, 5 minutes, 1 minute
   and departure for a carrier jump. The box is grayed out where WFMT cannot play a sound (on Linux it needs `canberra-gtk-play`
   or `paplay`).
4. Press **Test Card** to see it. The test works even while the feature is off, and reports whether an overlay could be reached.

The card is always the same width and wraps what it says onto more lines (at the end of a sentence first), growing downward, so nothing runs off the screen however long a system name is.

- Fuel warnings show only while you are flying your main ship, not docked, landed or scooping.
- Where the card sits is set on **Overlay Placement** ("Flight alerts (carrier jump, fuel)"); by default it is on the right, below the Inventory display.

## Route overlay

One card on your game screen for the route you are following. It has no panel button, only Settings.

It is a copy of the route: the one you plotted in the [Route Planner](exploration.md#route-planner), or else the one the game's galaxy map plotted. It reads like this:

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

- **The systems have no numbers**, the next one first, each with its star on the right.
  - As you reach a system it is taken off the list, the jump count goes down, the light years left are worked out again from where you are, and the list rolls on.
  - **Systems listed** (below) is how many are shown; the jump count and the light years cover the whole route.
- **The Route Planner's route takes over** while it has a jump left; then the game's plotted route comes back. With neither, nothing is drawn.
- **Light years** are the straight-line distances between the systems of the route. A route the game gave without positions shows no light years line rather than a guess.
- **The star is colored.**
  - **Green**: a star you can scoop fuel from (its class letters on the game's route, `FUEL` on a Route Planner route).
  - **Yellow**: a star you cannot scoop (a black hole, a brown dwarf and so on, or `NO FUEL`).
  - **Blue**: a neutron star (**yellow `NEUTRON ?`** when the Route Planner thinks the neutron star may be a secondary star, away from where you arrive).
  - **Red**: a white dwarf.
  - A system EDSM does not know gets a **\*** after its name when that option is ticked (below).
- **At the end of the route** the card says `Route ended.`, `You have arrived at <destination>.` and `The route is being reset.` for ten seconds. Then the route is reset (the Route Planner's route is cleared, or the game's route forgotten) and the card closes. A route that was already finished before WFMT saw it says nothing.
- **What is not on this card:** fuel, jump range, the next supercharge, refuel stops and the running expedition. The Exploration Dashboard shows the fuel, range and route status.

**To set it up:**

1. Open **Settings → WFMT → Overlays → Route**.
2. Tick **Enable the Route overlay**. It is **off by default**. **Systems listed** (3 to 20, 8 to start) is how many of the next systems the card lists.
3. Optionally tick **Mark the systems ahead that EDSM does not know yet** (**off by default**; it asks EDSM, see below).
   - With it ticked, a system on the list that EDSM has no record of gets a **\*** after its name.
   - A system EDSM does not know has not been uploaded by anyone who shares with EDSM, so it may be a first discovery.
   - If EDSM cannot be reached, nothing is marked and it tries again after a few minutes; a failed check never marks a system as unknown.
4. Press **Test Card** to see it with a made-up route (with the EDSM option ticked, the third and seventh systems of the sample show the mark). The test works even while the feature is off, and reports whether an overlay could be reached.

The card follows you along the route as you jump, and clears when you reach the end, clear the route, or jump to a system that is not on it.

- After a restart it reads the route the game has saved, so it comes straight back.
- Every line starts at the same left edge, and the card's padding and text size follow **Appearance**.
- Where it sits is set on **Overlay Placement** ("Route and ship status"); by default it is at the top left, above the Colonization list.

**What it cannot tell you:**

- The journal does not say what the next jump will cost in fuel, so the card shows the fuel on board and what your last jump used, not whether the tank is enough.
- The range is your ship's maximum with its current modules, from the game's `Loadout` event, not the range with the cargo and fuel it carries now.
- Distances are straight lines between the systems on the route.
- The EDSM check covers the systems listed and a few beyond (30 at most), asks once for the whole list, and asks again about a system EDSM did not know after ten minutes, since someone may upload it meanwhile.
- EDSM only knows what its users have uploaded, so a system it lacks is not proof that nobody has been there.

## Overlay connection

All four use the connection settings on the **Overlay Connection** Settings tab (Settings → WFMT → Overlays), and where they appear on screen is set on **Overlay Placement** (same place).

- That tab is also where you choose which overlay draws: WFMT's own built-in overlay (Windows) or EDMCModernOverlay.
- For EDMCModernOverlay the defaults (`127.0.0.1`, port `5010`) match it as they come.
- **Check connection** tells you whether the overlay is reachable.

See [Setting up the overlay](../OVERLAY_SETUP.md).

## What the game does and doesn't tell us, and how to work around it

WFMT, like every third-party tool, only knows what Elite Dangerous writes to its journal files. It needs no outside service here, so the journal is the whole story. Where it can't be sure, WFMT says so rather than guess quietly. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| What you might expect | What the game gives | What to do |
|---|---|---|
| Landing Assist to show which way the pad faces | The journal gives only a **pad number** and the station type, with no orientation. | Use the diagram for which pad is yours; line up by the pad numbers in the game. |
| A diagram for every kind of facility | Some facilities have no diagram, and the journal does not say enough (which layout, which way it faces) to draw one. | Use the pad number and follow the game's own docking guidance. |
| Interdiction Warning to fire before the game confirms | It combines the `Status.json` interdiction flag (written about once a second), an NPC's taunt in chat, and then the game's own `Interdicted` and `EscapeInterdiction` events, because they arrive separately. A taunt is not proof of an interdiction. | Treat the alert as a prompt. The in-game screen is the final word. |
| A fuel warning that says whether you can make the next jump | The journal does not say what a jump costs in fuel. | WFMT compares **percentages** of the tank, so choose the percentages that suit your ship. |
| A fuel percentage the moment EDMC starts | The tank size comes from the game's `Loadout` event, written at login and when you change ship or a module. Until then WFMT has fuel in tons, but no percentage. | Only the game's own low-fuel flag is used until then. Log in again, or change a module or ship, to make the game write it. |
| A countdown for a jump you did not schedule | WFMT only knows a request the game wrote to your journal. | Use the in-game carrier screen for jumps scheduled by someone else. |
| An unscoopable-star warning for a star you have not plotted to | The star class comes from the target the game reports (`FSDTarget`). | Plot or select the next jump as usual; the warning appears then. |
| An overlay to be found automatically | WFMT can only draw if an overlay is listening on the connection details. | Use **Check connection**, **Test Overlay**, **Test Warning** and **Test Card** in Settings. |

