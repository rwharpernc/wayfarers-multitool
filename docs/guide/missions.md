# Missions

This guide describes the Missions panel, the Mission types window, the Missions window, the Mission description window, the Missions overlay card and the Source commodities window. It also covers Community Goals and the payouts recorded for them.

**Data source:** all mission data comes from the journal. The journal is incomplete in the following respects:

- Wing and on-foot kills are often missing until a mission completes.
- Active missions are listed only at login.
- A Community Goal does not record its end.

Values that WFMT estimates are marked with `~`. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## How to

### See every active mission in one view

1. Press **Mission** in the mode bar.
2. Press **Missions window** at the bottom of the Missions panel. Clicking a mission card in the Mission types window opens the [mission description](#the-mission-description-window) instead.
3. Use the **Active** tab for one row per mission, ready missions first and then by soonest expiry. Use the **By place** tab for the same missions grouped by the system to go to.
4. Select a row to read its faction, destination, cargo, exact reward and expiry in the detail strip.

See [The Missions window](#the-missions-window).

### Read the progress bars

1. Open the **Progress** column in the Missions window. For kill bars, press **Mission types** on the Missions panel and select **Massacre (Space)** or **Settlement Raids (Ground)**.
2. Read the progress text: `20/60` is cargo handed in, `36/36 loaded` is cargo picked up but not handed in, `~18/40 kills` is a kill estimate, and `36/60 held` is cargo in the hold for a source and return mission.
3. Read the row color: green is ready to hand in, red is under an hour left, amber is under six hours, lime is half or more done, and blue is started but under half.
4. A `~` marks an estimate. The game's mission screen is the authoritative count.

See [Progress](#progress) and [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it).

### Open the Missions window

1. Press **Mission** in the mode bar.
2. Press **Missions window** at the bottom of the panel.

The window remembers its size and position. While open, it updates the time left, the progress and the list as missions are accepted and handed in.

### Find where to buy the cargo for a mission

1. Tick **Enable Spansh trade lookups** in Settings → WFMT → Trade (off by default). If it is off, the Source commodities window asks whether to enable it when **Find sources** is pressed.
2. Press **Find sources** at the bottom of the Missions panel, or **Sources** in the Missions window.
3. Choose **From where I am** or **From the turn-in system**, then press **Find sources** in the Source commodities window.
4. Wait for the rows to fill (`Asking Spansh... 2 of 5 done`), select a row and press **Copy system**. Paste the name into the galaxy map.

See [Source commodities](#source-commodities).

### Track kill missions

1. Accept massacre or settlement-raid missions in the game.
2. Press **Mission types** on the Missions panel (or click the **Massacre** line) and select **Massacre (Space)** or **Settlement Raids (Ground)**. One block is shown per issuing faction, with kills as `done/required`.
3. A `~` before a count marks an estimate.
4. When the kills are complete, the mission is marked ready (green, with a tick) and shows where to hand it in.
5. Use **Pin / Unpin** in the Missions window to list a mission first on the overlay card.

See [Using it](#using-it), [Pinned missions](#pinned-missions) and [Missions on the overlay](#missions-on-the-overlay).

### Worked examples

The numbers and names below are illustrative. The wording is what WFMT displays.

**Cargo delivery mission, accept to turn-in** (collect 60 Gold and return it):

1. The mission appears on the **Trade & Mining** page. **Commodities needed:** reads `Gold (1 mission)  x60`.
2. In the Missions window the Progress column reads `0/60 held` when no Gold is in the hold. The game writes nothing about a source and return mission until cargo is handed in.
3. Buy Gold at a station chosen with **Find sources**. The row follows the hold: `36/60 held`, then `60/60 held`. Gold already carried counts. Gold in a fleet carrier does not.
4. Fly to the place in the **Go to** column.
5. After a hand-in the game reports the count and the row shows the game's figure, for example `20/60`. When the mission is complete the row turns green and shows the hand-in place, which can differ from the accepting station.
6. The mission leaves the list when the game reports it completed. A pin on it is removed.

**Kill-mission stack** (three missions for Faction A with 20, 20 and 10 kills; two for Faction B with 15 and 15 kills):

1. In **Massacre (Space)** there are two blocks: Faction A reads `0/50` and Faction B reads `0/30`.
2. Each block shows the summed reward. Faction B shows `Δ20`: the biggest stack (Faction A) needs 20 more kills. Faction A's `Δ` compares it with the next biggest stack and reads `Δ-20`.
3. After 18 kills against Faction A the block reads `~18/50`. The **Sum** line totals the biggest stack with a bar and the total reward.
4. When the kills for a mission are complete, the game redirects the commander and WFMT marks the mission ready with the hand-in place.

**Where to buy lookup** (missions for 60 Gold and 40 Palladium, docked in the system where the Palladium is handed in):

1. **Find sources** opens the Source commodities window with **Need** summed over all missions: Gold 60, Palladium 40.
2. With **From where I am** selected, **Find sources** runs. The status reads `Asking Spansh... 1 of 2 done`, then `2 of 2 done`.
3. Each commodity gets its picks: closest, best local, cheapest anywhere and recommended. The **Largest pad** column shows `Large`, `Medium` or `Small`; `?` means Spansh gave no pad data.
4. Select a row and press **Copy system**.
5. **From the turn-in system** clears the results. Press **Find sources** again.

**Expired mission** (accepted with 2 days to run; no play for a week):

1. The card reads `Expires: 2d 4h`, then `Expires: 1h 30m` with a `⚠` once under two hours remain. The overlay card shows red under an hour and amber under six hours.
2. When the time runs out, the card shows `Expired` (overlay: `expired`) while the game has reported nothing.
3. The game writes nothing when a mission runs out, so the row can remain until the next login, when the game sends its list of active missions and WFMT drops the expired mission. A failed or abandoned event removes the mission at once.
4. A pin on it is removed. Cargo handed in earlier is not counted elsewhere.

## Using it

Press **Mission** in the mode bar. The top line reads `Missions: 7/20` (missions held of the game's limit of 20; hidden by *Show mission count* on the Display card of the Mission types window). Below it, each type that holds a mission is listed with its count (`Combat 3`). Click a line, or press **Mission types**, to open the **Mission types** window: the types are listed on the left with their counts and the selected type's page is shown on the right. The types, in order:

**Massacre (Space) · Settlement Raids (Ground) · Combat · Trade & Mining · Passenger · Covert / On-Foot Ops · Other · Community Goals**

- **Massacre** and **Settlement Raids** pages show grouped kill-progress bars.
  - One block per issuing faction. The top line is the faction name (`⚠ Illegal` when any stacked mission is illegal) and kills as `done/required`. A `~` before the count marks an estimate.
  - The second line is a progress bar, the reward (`12.5M (4.0M)`: the total of the stacked missions, and in brackets the part from wing missions, which are shared), and `Δ` followed by a number. For a non-largest stack, `Δ` is the number of kills by which the biggest stack exceeds it. For the biggest stack it is the next biggest stack's kills minus its own, so it reads negative (for example `Δ-20`). With one stack it reads `Δ0`.
  - A **Sum** line at the end totals the biggest stack with a bar and the total reward (*Show totals row*). It is omitted when only one faction has a block.
  - `Settlements:` lists ground targets (*Show target settlement*). `⚠` notes warn when missions name several target factions or systems, or that `~kills = estimate, not exact`.
  - With no such mission the page says so. With no mission data yet it reads `Relog (main menu and back) to sync missions.`
- Other types show one card per mission, soonest expiry first. A card shows the mission name (with `⚠ Illegal` or `🤝 Wing` badges), the issuing faction, `Mine via: ...` for a mining mission, status (`Pending` or `✓ Complete`), reward, a `Cargo: 120/200 collected, 80 delivered` line for cargo missions, `→ <system> / <station>` (the hand-in place once the mission is done) and `Expires: 2d 4h` (`⚠` under two hours). Clicking a card opens the Mission description window for that mission.
- The **Trade & Mining** page begins with **Commodities needed:**, a per-commodity total (`Gold (2 missions)  x150`) of cargo still to be found (*Show commodities needed*).
- The **Community Goals** page has one card per goal: title, system and market, a bar and the tier reached against the top tier (with `✓ Complete`), `Your contribution`, the bonus, `🏆 Top rank` when in the top rank, and the expiry. **Paid out** below the goals lists the latest three payouts.
- Three buttons at the bottom of the panel: **Missions window** (every active mission), **Mission types** (the pages above) and **Find sources**.

The Mission types window has a **Display** card with six switches: *Show kill progress*, *Show remaining-kills column*, *Show totals row*, *Show mission count*, *Show target settlement (ground missions)* and *Show commodities needed (trade and mining)*. They exist only there, not in Settings → WFMT → Missions (see [Settings](#settings)). A switch saves when clicked and the panel and pages change at once.

## The Missions window

The window opens from the **Missions window** button. It updates live: time left, progress and the list change as missions are accepted and handed in. Its title is **WFMT - Missions**. It keeps the selected mission as the list updates and remembers its size and position.

- **Active** tab: one row per mission, ready missions (✓, green) first, then by soonest expiry.
  - Columns: a pin column (★ for a pinned mission), **Mission**, **Kind**, **Faction**, **Go to** (the hand-in place once a mission is done), **Progress**, **Reward** and **Left** (time left).
  - The window subtitle summarizes: the number of missions, how many are ready or under an hour from expiry, how many are pinned, and the rewards held.
  - The Progress column also draws a small bar.
  - Row colors:
    - **green**: ready to hand in
    - **red**: under an hour left
    - **amber**: under six hours left
    - **lime**: half or more done
    - **blue**: started but under half
- **By place** tab: the missions grouped by destination system: the current system first (`(you are here)`), then the targeted next jump (`(next jump)`), then places with a ready mission. Each group heading gives the mission count and the number ready. Columns: **Mission**, **Station**, **Progress**, **Reward** and **Left**.
- **Detail strip** below the tabs: for the selected mission, the faction, status, destination, cargo and commodity (with tons still needed), exact reward, wing, accepted time and expiry.
- Header buttons:
  - **Pin / Unpin** pins or unpins the selected mission. **Pin all here** pins every mission for the current system. **Unpin all** clears all pins. With no commander known, the status line asks for a login.
  - **Copy system** copies the selected mission's system to the clipboard.
  - **Sources** opens [Source commodities](#source-commodities).

## The Mission description window

Clicking a mission card in the Mission types window opens **WFMT - Mission description**, which shows all data WFMT holds for that mission in groups. Clicking another card switches the same window to that mission. The window updates live (time left, progress) and reports when the mission is handed in, fails or is abandoned.

| Group | Content |
|---|---|
| Overview | The lines of the Missions window detail strip: faction, status, destination, progress, reward, wing, accepted, expires, pinned. |
| Objective | Description, target, target type and faction, kills required, commodity and units, passengers (count, type, VIPs, wanted), destination system, station and settlement, where the game gave them. |
| Cargo | Cargo progress, what remains to pick up, where, the largest pad there, and what remains to find. |
| Reward and standing | Reward, donation, commodity reward, and the influence and reputation the game states. |
| Journal | The mission ID and the game's internal name. |
| Other journal fields | Any other field the game wrote for the mission, as written. |

- **Copy system** copies the destination system. **Copy details** copies everything shown as plain text.
- Fields the game did not write for a mission type are omitted.
- The window reads the journal only and contacts no online service. It remembers its size and position.

### Progress

The source of the progress figure depends on the mission type:

| Shown as | Meaning |
|---|---|
| `20/60` | The game's count of cargo handed in (journal cargo depot events). |
| `36/36 loaded` | Cargo picked up for a haulage mission, not yet handed in. |
| `~18/40 kills` | Massacre and settlement-raid kills. `~` marks an estimate because wing and on-foot kills are often missing from the journal until the mission completes. |
| `36/60 held` | A source and return mission while the cargo is being bought. The game writes nothing about these until cargo is handed in, so WFMT compares the hold with the mission's requirement. Several missions for one commodity share the hold, soonest expiry first, so a ton is not counted twice. |

The same colors apply on the [overlay card](#missions-on-the-overlay). The panel's `Δ` and the massacre-page bars use the same kill counts.

The **held** figure:

- counts all of that commodity in the hold, whether or not it was bought for the mission;
- follows the hold as cargo is bought and sold;
- does not count cargo in a fleet carrier or another ship.

### Pinned missions

A pinned mission (★) is shown on the [Missions overlay card](#missions-on-the-overlay) in a **PINNED** section above all others.

- Each pinned mission has its own line (never stacked), with its place and time left.
- Pinned missions are listed first, then HERE, NEXT and the rest, within the same row limit.
- Pins are stored per commander in `mission_pins.json` (mission numbers only).
- A pin is removed when its mission is handed in, fails, is abandoned or expires.

## What the game does and doesn't tell us, and how to work around it

WFMT uses only what Elite Dangerous writes to its journal files. Missions need no outside service. Where WFMT cannot determine a value, it marks the value as an estimate. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| Item | What the game provides | Handling |
|---|---|---|
| Every kill counted | Wing and on-foot kills are often missing from the journal until the mission completes, so counts run low. WFMT marks them with `~`. Combat-zone kills are recorded as combat bonds, not bounties. WFMT counts them, but they carry no ship type, so an on-foot combat-zone kill can be counted as a ship kill. | `~` means "at least this many". The game's mission screen is authoritative. |
| Active missions after restarting EDMC mid-game | The game lists active missions only in its login event. WFMT derives the list from the last two weeks of journals (the latest login list plus missions accepted, completed, abandoned or failed since). A mission that expired without a journal entry can show until the next login. | Log in again to obtain the game's list. |
| Exact cargo mission progress | The game reports `CargoDepot` (collected, delivered and total) when cargo is collected or handed in, including by a wing-mate. Progress made before WFMT's two-week window, or without an event since, is unknown. | The card shows progress once the game has reported any. |
| Where to buy a mission's cargo, offline | WFMT asks Spansh. This requires the Trade online lookups to be enabled and a button press. | Enable the switch in Settings → WFMT → Trade. |
| Progress on a source and return mission before hand-in | The game writes nothing until then. | WFMT shows the hold against the requirement (`36/60 held`). Cargo in a carrier does not count. |
| Missions for the next jump on the overlay when a route is plotted | The game names the targeted system (`FSDTarget`), not the whole route, so only the next hop is NEXT. | Target each hop as it is reached. |
| Missions accepted long ago | WFMT reads only the last two weeks of journals at start-up. A mission still active but accepted earlier is not found. | Check the game's mission board. |
| Kills made while EDMC was closed | Counted only if they are in the last two weeks of journal files. | Run EDMC during play. |
| Correct category for every mission | Names WFMT does not recognize are placed in **Other**. | The card shows the details. |
| Long-term Community Goal payout memory | The game writes the payout (`CommunityGoalReward`) once. WFMT lists the latest three under **Paid out**, found in the last two weeks of journals at start-up. | None. |
| Community Goal removal at its end | The game gives no end signal, so the panel uses each goal's expiry date. | A goal past its expiry clears itself. |

## Missions on the overlay

The overlay card lists the missions that can be acted on now, since a list of up to twenty missions would cover the screen.

- The card is off by default (Settings → WFMT → Overlays → Missions).
- It requires an overlay to draw on: WFMT's built-in overlay (Windows) or EDMCModernOverlay ([setup](../OVERLAY_SETUP.md)).

```
MISSIONS 14 · 2 ready · 3 soon
HERE Jarogee
✓ Gold > Newcomb Orbital              35m
40 Palladium 12/40 > Fabian Port   3h20m
Massacre x2 Li Yong-Rui > Fabian Port   1d
NEXT Sol
Passengers > Abraham Lincoln       5h00m
ELSEWHERE
Combat > HIP 20019                  3d
+8 more in 5 systems
```

- **PINNED** (present when missions are pinned in the Missions window) comes first, one line per pinned mission, showing the station when it is in the current system and the system otherwise.
- **HERE** lists missions whose turn-in or destination is the current system. **NEXT** lists the same for the targeted next-jump system. **ELSEWHERE** lists the rest. `+N more in M systems` appears when the row limit cuts the list.
- **Order:** finished missions (✓) first, with the hand-in place, then by soonest expiry.
- **Colors:**
  - A mission with less than the configured minutes left (60 by default) is red; under six hours is amber.
  - A finished mission is green regardless of the overlay color scheme.
  - Otherwise the color follows [progress](#progress): lime when half or more done, blue when started.
  - These colors are fixed and do not follow the overlay color scheme. Time pressure (red, amber) takes precedence over progress.
- **Stacking:** massacres and settlement raids against one faction in one place, and other missions with the same title for the same station, are combined into one line with a count (`x3`). A cargo mission shows its progress (`12/40`).
- **Long names:** the card has a fixed width. When a title and place do not fit on one line, the place moves to a line below. Only a name longer than a whole line is shortened. The time left is always shown. The card's top-left corner does not move as lines change.
- **Placement:** Settings → WFMT → Overlays → Overlay Placement ("Missions list"). The default is the bottom-right corner, above the screenshot messages.

Settings (Settings → WFMT → Overlays → Missions):

| Setting | Range | Default |
|---|---|---|
| **Show missions on the overlay** | on/off | off |
| **Show the missions for the next jump (the system you have targeted)** | on/off | on |
| **Mission lines to show (at most)** | 3 to 14 | 8 (the rest become `+N more`) |
| **Show a mission in red when it has less than N minutes left** | 5 to 720 | 60 (amber under six hours) |

**Test Card** draws a sample card and reports whether the overlay could be reached.

Limits: the game lists active missions only at login, so after restarting EDMC mid-game the card is built from the last two weeks of journals. The next jump is the targeted system. With no target there is no NEXT section.

## Source commodities

Collect and Mining missions require cargo that must be found. The **Find sources** button at the bottom of the panel, or **Sources** in the Missions window, opens the Source commodities window.

For each commodity, summed over all active missions, the window shows the same four picks as Trade's [Best picks](trade.md#best-picks):

- closest
- best local
- cheapest anywhere
- recommended (within 10% of the cheapest)

Columns: **Commodity**, **Need** (tons, summed), **Pick**, **Station**, **System**, **Largest pad**, **ly**, **cr/t** and **Note**. **Largest pad** is Large, Medium or Small from the pad counts Spansh holds; `?` means Spansh gave none.

### Delivery missions

A Delivery mission (for example "Deliver 132 units of Personal Weapons") is supplied by the faction and collected free at a specific station, so nothing is bought.

- Some cargo is handed over at acceptance. Other cargo is handed over when collected at the station, which can be later.
- The window lists such a mission as `Pick up at <station>` until the journal shows the cargo collected, and does not search the market for it. The station is the one docked at when the mission was accepted.
- A pick-up row shows the pad size the journal reported on docking at the station that issued the mission, and nothing if none was reported.
- Wing, rank and cooperative deliveries are not listed.

### Finding sources

1. Choose where to measure from:
   - **From where I am**: the current system. If WFMT has not seen a jump since EDMC started, it reads the system from EDMC and then from the newest journal.
   - **From the turn-in system**: where most missions for that commodity are handed in.
   Changing the choice clears the results.
2. Press **Find sources**. WFMT asks Spansh several times per commodity, one commodity at a time, and shows each as it finishes (`Asking Spansh... 2 of 5 done`). The button becomes **Cancel** while the search runs.
3. Select a row and press **Copy system** to copy its system name. With no station on the row, the window asks for a selection.

Behavior:

- The landing pad size, "Near me" radius, carriers and ground settings from Trade apply.
- The search requires **Enable Spansh trade lookups** in Settings → WFMT → Trade (off by default). If it is off, the window asks whether to enable it, and nothing is searched until the answer is yes.
- Nothing is searched until the button is pressed.
- If no mission needs cargo to be found, the window says so.
- At most twelve commodities are listed, largest need first.
- The nearest ring hotspot for a Mining mission is not included (use Mining's hotspot finder). Market data older than 7 days is ignored.

## Settings

The six display switches are on the **Display** card of the **Mission types** window (all on by default). **Settings → WFMT → Missions** only refers to that card.

| Switch | Effect |
|---|---|
| *Show kill progress* | The `done/required` count and the bars on the massacre pages. When off, only the required count is shown. |
| *Show remaining-kills column* | The `Δ` figure. |
| *Show totals row* | The **Sum** line. |
| *Show mission count* | The `Missions: N/20` line. |
| *Show target settlement (ground missions)* | The `Settlements:` line. |
| *Show commodities needed (trade and mining)* | The **Commodities needed:** summary. |

The overlay card has its own settings under Settings → WFMT → Overlays → Missions (see [Missions on the overlay](#missions-on-the-overlay)). The Display switches take effect on click.

See the [Missions specification](../MISSIONS_TECH_SPEC.md).
