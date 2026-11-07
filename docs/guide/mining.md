# Mining

This guide describes Mine mode: live tracking of ring mining in a ship and surface mining in the Rhino SRV, the Space Mining Book and Surface Mining Book, Mining History, the online lookups (switched in Settings → WFMT → Online), mining alerts and the related settings.

Mine mode provides:

- **Space Mining** (in the ship), with the **Space Mining Book**: every ring the journals have shown, with its hotspots, tons mined and notes.
- **Surface Mining** (in the Rhino SRV), with the **Surface Mining Book**: the catalog of saved deposits and the bodies the journals show mining on.
- **Mining History**: every run in the journals, summed.

The Mining panel is a short summary and a row of buttons. It shows a few lines for the ring run and a few for the Rhino, then **Space Mining** and **Surface Mining**, which each open that page's own window: the live numbers (for the Rhino also the radar and the controls), with **Book** and **Dashboard** in its header and a **Settings** card at the top. **Hotspots**, **Prices** and **Reserves** appear on the panel and in the Space Mining window once those lookups are enabled. There are no pages to switch between and no page arrows.

**On this page:** [How to](#how-to) · [What each page shows](#what-each-page-shows) · [The buttons](#the-buttons) · [A typical run](#a-typical-run) · [Mining History](#mining-history) · [The live window](#the-live-window) · [Marking a mining location](#marking-a-mining-location) · [The Space Mining Book](#the-space-mining-book) · [The Surface Mining Book](#the-surface-mining-book) · [Mining alerts](#mining-alerts) · [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it) · [Settings](#settings)

**Data sources:**

- The journal records prospecting, refining and collection.
- The journal does not record a ring's deposit amounts or density; these are entered manually.
- The hotspot catalog is the commander's own.
- Ring reserve and hotspot lookups use data players have uploaded to EDSM and Spansh.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## How to

**Start a Space Mining run.** See [Space Mining](#space-mining).

1. Check the panel while in the ship. It shows a few lines for the ring run. **Space Mining** opens the full page in its window.
2. Undock. A new run begins. The Space Mining window shows `No active mining run. Undock to start tracking a new run.` until the run has something to show (tons in the hold, a prospected rock, a launched limpet or a refined ton).
3. Fly to the ring and mine. The **Hold**, **Asteroids prospected** and **Refined** lines fill in.

**Start a Surface Mining run.** See [Surface Mining](#surface-mining).

1. Launch the Rhino. The panel's Rhino lines change from `Rhino: not deployed.` to `Rhino deployed`.
2. Press **Surface Mining** to open the full page. Until the launch it reads `No active Rhino deployment. Launch the Rhino to start tracking a new run.`; afterwards it shows the live numbers.
3. Stow the Rhino to end the run. The numbers remain on the page and the panel, marked `Rhino stowed (last deployment)`, until the next launch.

**Read the radar.** See [Surface Mining Live](#surface-mining-live).

1. Press **Surface Mining** on the panel.
2. Be on or just above the ground. Until then the window reads `The radar draws when you are on or just above the ground.`
3. Select a reach with the **Radar reaches** buttons (50 m to 2 km). Press **Help** in the window header for the meaning of each mark.

**Log a ring.** See [The Space Mining Book](#the-space-mining-book).

1. Press **Space Mining**, then **Book** in its header. Rings that were DSS-scanned or mined are added automatically.
2. For a ring the journals have not shown, press **Add ring** and complete the form.
3. Select a ring, type in **Your note**, press **Save note**, and use **Favorite** to star it.

**Log a surface deposit.** See [Adding or editing a hotspot](#adding-or-editing-a-hotspot).

1. Stand at the deposit in the Rhino and press **Add hotspot** in the Surface Mining window (the Surface Mining Book also has one).
2. Check the **Contains**, **Rigs**, **Amount** and **Density** fields, and save.

**Use Mining History.** See [Mining History](#mining-history).

1. Press **Space Mining** or **Surface Mining**, then **Dashboard** in its header (rings from the Space Mining window, the Rhino from the Surface Mining window).
2. Read the **Overview** tab, then open **Rings**, **Commodities** or **Runs**. Click a heading to sort.
3. Press **Refresh** to read the newest journal immediately.

**Set mining alerts.** See [Mining alerts](#mining-alerts).

1. Open **Settings → WFMT → Overlays → Flight Alerts** and tick *Enable Flight Alerts*.
2. Confirm *Mining alerts* is ticked, then set the limpet number and the hold percentage.
3. For rich-rock cards, type commodities in the **Target commodities** box on the Settings card of the Space Mining window ([details](#target-commodities)).

**Find a hotspot.** See [Hotspots: Find Nearby Hotspots](#hotspots-find-nearby-hotspots).

1. Tick **Mining: nearby hotspot finder** in **Settings → WFMT → Online**.
2. Press **Hotspots** (on the panel or in the Space Mining window), select a **Material** and a **Where** distance, and press **Search**.
3. Select a row and press **Copy system** to copy the system name for the galaxy map.

## What each page shows

**The panel** shows a short version of both sides. For the ring run: `Ring mining` (or `Ring mining (paused in supercruise)`), the hold, the mission needs, **Refined** and **Refining now**. Before a run: `Ring mining: no active run. Undock to start one.` with the mission needs. For the Rhino: `Rhino deployed` (or `Rhino stowed (last deployment)`, or `Rhino: not deployed.`), its hold while it is out, and **Refined**. Before the game has identified the commander, the panel reads `No commander detected yet.`

Three switches on the Settings card of the Space Mining and Surface Mining windows (all on by default) control which lines appear:

| Setting | Lines controlled |
|---|---|
| *Show the cargo bar* | The hold lines (**Hold** on the Space page; **SRV hold** and **Ship hold** on the Surface page) |
| *Show session totals* | **Refined**, **Refining now**, **Run average**, **Hold full in** and **What the station pays** (Space page); **Refined**, the rates, **SRV hold full in**, **Transferred to ship** and **Raw materials** (Surface page) |
| *Show prospector hints* | **Asteroids prospected**, **Materials seen**, **Last rock**, **Core asteroids found**, **Asteroids cracked** and **Limpets launched** (Space page); the **Last DSS scan** line (Surface page); the `Mine via` method hint beside each commodity in **Materials seen** |

The HUD overlay follows the same three switches, so a line that is turned off is hidden in both places.

Before a run starts, the page states this instead of showing zeros: `No commander detected yet.` until the game has identified the commander, then `No active mining run. Undock to start tracking a new run.` on the Space page and `No active Rhino deployment. Launch the Rhino to start tracking a new run.` on the Surface page. Mission needs and the ring's reserve level still show on the Space page while waiting.

### Space Mining

A run is one trip from `Undocked` to `Docked`. The next undocking starts a new run; the numbers of the finished run stay on the page until then.

- **Hold**, for example `Hold: 64 of 200 t`.
  - The tons the ship carries, read live from `Status.json` (the `Cargo` event is used until it has reported), and the capacity from the last loadout.
  - The same line is on the HUD overlay.
  - The ring at the current location is shown with its reserve level once **Mining: ring reserve lookup** is ticked (Settings → WFMT → Online) and EDSM knows the ring, for example `Ring: Example 2 A Ring (Metallic) - Reserve: Pristine`. A ring that is not Metallic is shown in red with a reminder that laser mining pays best on Metallic rings. Nothing is shown while the answer is unknown.
- **Asteroids prospected**, with the count of each content grade (for example `Asteroids prospected: 14 (High x3, Medium x6, Low x5)`), and the **materials seen**. A rock prospected again with the same composition is counted once, and the page states the number of repeats ignored (`[2 duplicate(s) ignored]`).
  - Each material in **Materials seen** is on its own line with the number of rocks that held it, the lowest, average and highest percentage seen this run in square brackets, and `Mine via` with the method that usually applies (core, laser surface or sub-surface deposit; laser surface when no other is known). The method hints are a static lookup table in the plugin (`mining_methods.py`).
- **Last rock**: the latest rock's materials with percentages and its grade, for example `Last rock: Painite 34%, Platinum 12% (High), target: Painite`.
  - A **core asteroid** (the game names a core mineral in the prospector result) is counted by **Core asteroids found** (`Core asteroids found: 3 (last: Painite)`), which names the latest core. **Last rock** adds `core: Painite` only when its core is not the latest one.
  - `target:` names each target commodity that the rock holds at least the configured percentage of (Settings card of the Space Mining window; several targets can be set).
- **Mission needs**: for each commodity the active mining missions still require, the tons already held, for example `Mission needs: Painite 50 of 120 t held (2 missions)`. It is computed as in the Missions window and shows before mining starts. Up to three commodities get a line; more are summarized as `+2 more commodities`. A commodity required by several missions states the count (`(2 missions)`).
- **Asteroids cracked** (core mining).
- **Limpets launched** by type, with the count still aboard. The count is exact once EDMC has supplied the cargo. Otherwise it is bought less launched, marked `~`. The HUD overlay's *Limpets remaining* line shows the same number.
- **Refined**, by commodity. Then:
  - **Refining now** (for example `Refining now: 840 t/h`): the tons refined in the last minute, scaled to an hour, falling to 0 within a minute of a lull.
  - **Run average** (for example `Run average: 720 t/h over 41 min`): the tons refined this run over its mining time, shown once the run has a minute of mining time.
  - One refined unit in the journal is one ton.
  - Mining time runs from the run's first to its last mining event (a limpet launched, an asteroid prospected, a ton refined or a rock cracked). A gap of more than 10 minutes between two such events is excluded, so a long flight or break does not lower the average.
  - The HUD overlay carries the same two lines, and Mining History's *Mining time* and *t / hour* use the same definition.
- **Hold full in** (for example `Hold full in about 14 min`): the room left in the hold divided by the **Run average**.
  - Before an average exists (the first minute), *Refining now* is used.
  - It is shown with the other refining lines when the ship's capacity is known and something is being refined.
  - It reads `Hold is full` once the hold is full, unless the **Hold** line (*Show the cargo bar*) is on the page, which already shows the hold at capacity. The same applies to the SRV hold on the Surface page.
  - A laser works in bursts and the rate varies with the rocks, so the figure is an estimate.
  - The HUD overlay and the live window carry it too.
- **What the station pays**, when docked and the station's commodities market has been opened (for example `Painite here: 521,400 cr/t, 8% above the galactic average (482,000)`).
  - One line per commodity refined this run that the station buys, most tons first, up to three.
  - It compares the station's price with the galactic average the game lists beside it.
  - It reads the game's `Market.json` on the local computer and contacts no online service.
  - A station that lists a price for something it does not buy (no demand) is skipped.
  - The lines are removed on undocking.
- A **Paused** note (`Paused (in supercruise)`) is shown in supercruise. The run keeps its numbers and continues after dropping out.

**Example: a Space run.** Undocked in a 200 t ship, about 40 minutes into mining, the page can read:

```
Hold: 64 of 200 t
Asteroids prospected: 14 (High x3, Medium x6, Low x5)
Last rock: Painite 34%, Platinum 12% (High), target: Painite
Refining now: 840 t/h
Run average: 720 t/h over 41 min
Hold full in about 14 min
```

- The hold has 136 t of room; 14 minutes is that room divided by the run average.
- The last rock held Painite above the configured share, so the page names it as a target. A card for it also shows on the overlay when Flight Alerts is enabled.
- After docking and opening the commodities market, **What the station pays** compares the station's price for the refined commodities with the galactic average.

### Surface Mining

A run lasts from launching the Rhino to stowing it. The page keeps the last run's numbers (`Rhino stowed (last deployment)`) until the next launch, but the hold lines and *Refining now* show only while the Rhino is out.

- While the Rhino is out: its hold (`SRV hold: 40 of 72 t`) and the ship's (`Ship hold: 64 of 200 t`, from the last `Cargo` event). Both lines disappear when the Rhino is stowed.
- **Refined**, **Refining now** and the **Run average**, worded as on the Space page. *Refining now* shows only while the Rhino is out.
- **SRV hold full in**: the same estimate for the Rhino's 72 t hold, only while it is out.
- **Transferred to ship** and the **Raw materials** collected.
- **Last DSS scan**: the number of mining locations the scan found on a body (`Last DSS scan: 4 Planetary Mining Location(s) on <body>`). It is shown only when that count differs from the number of **Known hotspots here**, which states the same information otherwise.
- **Known hotspots here (N)**: the hotspots saved on the current body, one per line with the material, rigs, signal number, position, the tons-left estimate in square brackets and the note.
- The **coverage minimap** (when ticked on the Surface Mining window's Settings card): ground the Rhino has driven over, with the position, saved hotspots and the mining locations marked with **Mark center** and **Mark border**. In the ship it appears only close to the ground (under about 2 km).
- **Nearest marked location**: the size of the nearest marked mining location, the direction of its center and the share of its edge driven (see [Marking a mining location](#marking-a-mining-location)).
- **Nearest saved deposit**: the closest saved deposit, its material, distance and direction, with the rig-gap verdict when one is set.
- **Rigs noted**: the number of rigs noted with **Rig placed** and the distance to the nearest (see [Rig bands](#rig-bands)). Nothing is shown until a rig is noted.
- A line stating what **Mark center** or **Mark border** last did, or why it could not (`WFMT cannot read your position: be on or just above the ground.`).

**Example: a Rhino run.** After launching on a body with a mining signal, the page can show:

```
SRV hold: 40 of 72 t
Ship hold: 64 of 200 t
Last DSS scan: 4 Planetary Mining Location(s) on <body>
```

- The SRV hold line shows how full the Rhino is; **SRV hold full in** estimates the time remaining.
- The ship hold line is the last `Cargo` figure, because WFMT does not read the ship's hold while the Rhino is out.

Both pages carry the buttons below. The Surface Mining Book and the coverage map are per commander.

## The buttons

The panel's buttons sit side by side and wrap onto a second line when they do not fit. **Book** and **Dashboard** are in the header of the Space Mining and Surface Mining windows, as are **Hotspots**, **Prices** and **Reserves** in the Space Mining window. The buttons shown depend on the page and on Settings. Hovering over a button shows a tip with its name and function.

| Button | Function | Shown when |
|---|---|---|
| **Space Mining** / **Surface Mining** (panel) | Opens that page's window: a radar and the controls on Surface Mining, the live numbers on Space Mining. Suited to a second screen ([the live window](#the-live-window)). | Always |
| **Book** (Space Mining and Surface Mining windows) | Opens the book for that window: the **Space Mining Book** (rings) from Space Mining, the **Surface Mining Book** (Rhino deposits) from Surface Mining. | Always |
| **Dashboard** (Mining History; both windows) | Opens every mining run found in the journals, summed (see below). | Always |
| **Hotspots** (find nearby hotspots) | Opens the Find Nearby Hotspots window. | Panel and Space Mining window; needs **Mining: nearby hotspot finder** (Settings → WFMT → Online). The window shows the standard warning while it is off |
| **Prices** (find best price) | Opens the Find Best Price window. | Panel and Space Mining window; needs **Mining: best price finder and Market research** (Settings → WFMT → Online), the same switch that Market research and What pays use in the Surface Mining Book. The window shows the standard warning while it is off |
| **Reserves** (check ring reserve level) | Opens the Check Ring Reserve Level window. | Panel and Space Mining window; needs **Mining: ring reserve lookup** (Settings → WFMT → Online). The window shows the standard warning while it is off |

The online lookups are off by default and are switched on the Online tab (Settings → WFMT → Online). When one of these dialogs needs a lookup that is off, it shows `This needs "<lookup name>" (<service>), which is off. Turn it on in Settings > Online.` See [what goes on the internet](internet-and-privacy.md).

### Hotspots: Find Nearby Hotspots

1. In **Material**, select or type a mineral (the list holds the known materials; a name not in it is accepted).
2. In **Where**, choose the distance: within 25, 50, 100 (default), 250, 500 or 1,000 ly.
3. In **Search from**, type the system to measure from. It starts as the current system; **Here** restores it. System names are suggested from the systems visited, and from Spansh while typing only if **System name suggestions while typing** is ticked in Settings → WFMT → Online.
4. Press **Search** (or Enter).

The table lists up to 25 rings that Spansh confirms have a hotspot for that material, nearest first. Columns: **Ring**, **Body**, **System**, **Hotspots** (the number of that material in the ring), **Distance (ly)**, **Arrival (ls)** (distance from the arrival star) and **Reserve level**. Click a heading to sort. Select a row and use **Copy ring**, **Copy body** or **Copy system** in the header, or double-click a row to copy its system.

Only the system name and the material are sent. A search with no result advises a longer distance or checking the spelling.

**Example: Painite.**

1. Tick **Mining: nearby hotspot finder** in **Settings → WFMT → Online**, then press **Hotspots** on the Space Mining page.
2. Type or select `Painite` in **Material**.
3. Keep **Where** at 100 ly and **Search from** unchanged (**Here** restores the current system).
4. Press **Search**. The table lists rings with Painite hotspots, nearest first.
5. Sort by a heading if needed, select a row and press **Copy system**. If nothing is found, set **Where** to 250 ly and search again.

### Prices: Find Best Price

1. Type a commodity in **Commodity**. Suggestions follow the input, with the commodities refined this run first. Down on an empty box shows the list.
2. Choose **I am selling** (default) or **I am buying**.
3. In **Where**, choose **This system only** (for goods that must be sold inside a Powerplay system), within 10, 25, 50 (default), 100, 250, 500 or 1,000 ly, or **Anywhere**.
4. In **Search from**, type the system to measure from (it starts as the current system; **Here** resets it).
5. Press **Search** (or Enter).

The table lists up to 25 stations Spansh shows paying the most (or selling cheapest). Columns: **Station**, **System**, **Price (cr)**, **Demand** (**Supply** when buying), **Distance (ly)**, **Arrival (ls)**, **Pad** (the largest pad Spansh counts, or `?`) and **Kind** (for example `Orbital Coriolis Starport` or `Ground Planetary Outpost`). Click a heading to sort. Double-click a row to copy its system, or use **Copy system** or **Copy station** in the header.

- **Minimum demand (t)** (Minimum supply when buying) is the least a station must show, a whole number from 1 to 1,000,000. When selling it starts at the tons of that commodity in the hold if EDMC knows them, otherwise 1, and follows the typed commodity until a figure is typed.
- Fleet carriers are excluded, and only markets updated in the last 30 days are requested.
- Pad size and a market's exact age are not filtered. The largest pad is in the table, and a station the ship cannot land at can be listed.

**Example: selling 120 t of Painite.**

1. Tick **Mining: best price finder and Market research** in **Settings → WFMT → Online**, then press **Prices**.
2. Type `Painite` in **Commodity**. **I am selling** is selected by default.
3. Keep **Where** at 50 ly. **Minimum demand (t)** starts at the tons in the hold if EDMC knows them.
4. Press **Search**. Read **Price (cr)**, **Demand**, **Pad** and **Arrival (ls)**. A **Pad** of `?`, or one too small for the ship, requires checking before travel.
5. Select a row and press **Copy system**.

### Reserves: Check Ring Reserve Level

1. Type a system in **System** (it starts as the current system).
2. In **Body or ring**, optionally type a body or ring name. It starts as the tracked ring at the current location, if any. Empty lists every ringed body in the system.
3. Press **Search**. **Here** fills in the current system.

The table gives each ring with its **Body**, **Reserve level**, **Ring type** and a **Laser mining** note; rings that are not Metallic are flagged in amber. Select a row and use **Copy ring** or **Copy system**, or double-click a row to copy its system. The lookup uses EDSM and sends only the system name. When EDSM has no ringed body on file for the system (or none with the typed name), the status line says so.

**Example.**

1. Tick **Mining: ring reserve lookup** in **Settings → WFMT → Online**, then press **Reserves**.
2. Type the system name in **System**. Leave **Body or ring** empty to list every ringed body.
3. Press **Search**. Each row gives the **Reserve level**, **Ring type** and **Laser mining** note.
4. If the status line states that EDSM has no ringed body on file, the system has not been recorded.

**Automatic lookup.** When enabled, the EDSM ring reserve lookup also contacts edsm.net automatically when the ship drops into a ring (once per ring until EDMC restarts; the answer is kept meanwhile), as well as on manual searches.

## A typical run

**In space:**

1. Mine at a ring. The Space Mining page shows live stats; a core asteroid or a rock rich in a target commodity is shown on the page (and on the overlay when Flight Alerts is enabled).
2. Open **Book** in the Space Mining window's header. The ring is in the **Space Mining Book** with the tons mined; a note or a favorite star can be added. **This system** jumps to the rings in the current system.
3. **Dashboard** (Mining History) sums every run.

**On the surface:**

1. Launch the Rhino and mine. The Surface Mining page shows live stats.
2. Press **Add hotspot** in the Surface Mining window to save a deposit.
3. Open **Book** in the Surface Mining window's header to see the saved hotspots, including tons mined and an estimate of tons left; use **Mark depleted** when one is exhausted.
4. In the same system later, the Surface Mining Book lists the scanned bodies and the hotspots there, and its **From your journals** group lists other bodies the journals show mining on.

## Mining History

**Dashboard** opens a window that sums all mining in the journals for the current commander.

- The Space and Surface pages show only the run in progress. Mining History includes all earlier runs, including runs made with EDMC closed, across restarts and relogs.
- A **run** is one trip from undocking to docking, the same trip the Space Mining page counts.
- Mining that starts with no undocking before it (a relog in space) is a run of its own.

### The tabs

- **Overview**: tiles for runs, hours mining, tons refined, tons per hour, credits from sales, credits after limpets and credits per hour, and the share of asteroids rated High. Then:
  - **Prospecting**: asteroids by content grade, motherlodes, asteroids cracked, tons per asteroid.
  - **Limpets**: launched by type, prospectors per asteroid, collectors per ton.
  - **Sales**: with the limpet cost, the credits left after limpets and the tons mined and not yet sold.
  - The **best runs** by tons refined.
- **Commodities**: what was refined and sold, with the average price per ton sold and each commodity's share of the refined total.
- **Rings**: where mining took place, with runs, tons, asteroids prospected, the share rated High and the last visit.
- **Runs**: every run, newest first, with location, mining time, tons, tons per hour, asteroids prospected, the share rated High, limpets (prospector / collector), earnings and what remains after limpets.

Click a heading on the last three tabs to sort. Columns:

| Tab | Columns |
|---|---|
| **Commodities** | Commodity, Refined (t), Sold (t), Earned, Average per ton, Share of refined |
| **Rings** | Ring, System, Runs, Refined (t), Prospected, High, Last visit (most tons first until sorted) |
| **Runs** | Started (UTC), Where, Mining time, Refined (t), t / hour, Prospected, High, Limpets P / C (prospector and collector), Earned, After limpets |

The window header has **Refresh**, **Rebuild from journals** and **Help** (which explains *Mining time*, *Earned* and *After limpets*). The line under the title gives the commander and the number of runs since a date. If no commander is known, the status line asks for a login or play.

**Example: reading the Earned figure.** 100 t of Painite is mined on Monday and the ship docks without selling. On Tuesday the 100 t is sold at a station that pays more.

1. **Dashboard**, **Runs** tab: Monday's run shows 100 in **Refined (t)** and `-` in **After limpets**, because nothing has been sold.
2. After the sale, **Refresh**. The sale is taken off the waiting list, oldest run first, so Monday's run shows what the 100 t paid.
3. **Overview**, **Sales** block: the limpet cost, the credits after limpets and the tons still waiting to be sold (none).
4. The figure is takings, not profit: fuel, repairs and ammunition are not deducted.

### Surface Mining History

**Dashboard** follows the window in which it is pressed. In Space Mining it is the ring history above. In Surface Mining it opens **Surface Mining History**, the same window for the Rhino.

- Runs are counted from launch to stowing.
- It shows tons refined by the Rhino and what they sold for.
- The Overview omits the tiles that apply only to a ship (*asteroids rated High* and *credits after limpets*). Its Prospecting and Limpets blocks are replaced by **The Rhino's bodies**: the number of bodies mined on, the most tons on one body and the average tons per body.
- Sales are matched to each half by the commodity sold, so a commodity mined both ways counts its sales in both windows.
- A **Bodies** tab replaces Rings, with each body's runs, tons refined, tons per hour and last visit. Its **Runs** tab has Started (UTC), Where, Mining time, Refined (t), t / hour and Earned.
- Each window remembers its own size and position.
- A Rhino that was already out when EDMC or the game started is recognized from the SRV's hold in the journal or from `Status.json`. Its tons count as Surface mining from the first refined ton.

### Commodity names

Commodity names are suggested as typed in the Find Best Price window, the Add/Edit Hotspot form's *Contains* box and the Space Mining window's *Target commodities*.

- A short list appears under the box. Down and Up move the selection, Enter or a click takes one, and Escape closes the list.
- In the target box the list follows the item being typed, after the last comma, and taking a name replaces only that item.
- Nothing is fetched online.

### How the numbers are worked out

- **Mining time** is from a run's first mining event to its last, not the time undocked.
  - A mining event is a limpet launched, an asteroid prospected, a ton refined or a rock cracked.
  - A gap of more than 10 minutes between two mining events is excluded. This is the same definition as the Space Mining page's *Run average*.
  - The two can differ slightly: the page counts from the moment WFMT saw each event, the history from the journal's time stamps, and the page's average appears only after a minute of mining.
  - Runs saved before the 10-minute rule are read from the journals again in the background.
- **Asteroids prospected** counts a rock once, the same rule as the Space Mining page.
  - A rock prospected again within a run with the same composition is not counted again.
  - The game gives asteroids no identity, so two different rocks with the same composition to a tenth of a percent also count as one.
  - A grade WFMT cannot read (an unknown game language) is counted as unknown, not Low, and is excluded from the High and Low shares.
  - Runs saved before this rule keep the counts they were saved with.
- **Earned** is what selling the tons a run mined paid, at any station.
  - WFMT keeps a list of tons mined and not yet sold. Each `MarketSell` takes tons off it, oldest run first, crediting those runs with the tons and the same share of the sale's total.
  - Mining, docking without selling and selling at a different station still credits the run.
  - A sale can raise the *Earned* of an older run.
  - Tons sold beyond what was mined (cargo bought, or mined while EDMC was closed) earn nothing here.
  - If less is sold than was mined, the remainder stays waiting. The Sales block shows the tons waiting.
  - It is not profit: fuel, repairs and ammunition are not deducted. *After limpets* deducts the limpet cost, below.
  - WFMT cannot distinguish mined tons from bought tons of the same commodity. Cargo that is jettisoned, lost or moved to a carrier stays on the waiting list, and a later sale of that commodity (including bought cargo) is credited to it.
  - Runs saved before this was added start with nothing waiting. What they sold is as counted then, and **Rebuild from journals** recounts it under the current rule.
- **After limpets** is *Earned* less the cost of the limpets launched in the run.
  - WFMT reads the price from `BuyDrones` events and charges each limpet launched at the price last paid for limpets, so a run is charged for the limpets it used, not for the ones bought and kept.
  - Limpets sold back (`SellDrones`) are not credited.
  - A limpet launched before WFMT has seen a price (bought before the journals available, or received as a gift) is counted as launched with no price known and costs nothing here. That run's figure is slightly high and is marked `~` in the Runs tab.
  - A run with nothing sold yet shows `-` there, and in the totals its limpets show as a cost until it is sold.
  - Fuel, repairs, ammunition and the Rhino's costs are not deducted.
- A run's **ring** is the ring most recently dropped into before the run's first mining event. A run that mines more than one ring is listed under the first.

### Reading the journals

- The first time WFMT runs with a known commander, it reads every finished journal once in the background (not only when the window opens). The window's header and status bar show progress.
- The runs are stored in `mining_history.json` beside the plugin, one record per commander. Later starts read only the journals written since.
- The newest journal, which may be growing, is read again about every 15 seconds while the window is open, so a run in progress is included and nothing is counted twice.
- **Refresh** reads immediately.
- **Rebuild from journals** discards the saved runs and reads every journal again.
- Nothing is sent anywhere.

## The live window

**Space Mining** or **Surface Mining** opens a window intended to stay on a second screen or in a corner of the first.

- It needs no overlay: everything is drawn in the window.
- It redraws once a second and remembers its size and position.
- There is one window per page.

### Surface Mining Live

On the left is a **radar** centered on the Rhino with north at the top. It draws:

- range rings,
- the ground driven,
- the marked mining locations (a cross at the center and the circle through the border),
- saved deposits, labeled with the first letters of the material (a hollow ring for a depleted deposit),
- a line to the nearest deposit with its distance,
- **rig bands** (see below),
- an arrow for the direction the Rhino faces.

Three further elements appear when they apply:

- **Drive rings**: orange dashed circles around the nearest marked location, showing where to drive so the scanner covers it.
  - The first is at 2 km from the center, and the rest a little under 4 km further out.
  - The last is on the border or, before a border is marked, as far out as the Rhino has driven.
  - They derive from a scanner reach of 2 km (`SCAN_RADIUS_M`).
- **Stop circles**: violet, around the best stops from the Book, using the stop radius on the Surface Mining window's Settings card.
- When a **target commodity** is set in the Space Mining window: a bright line to the nearest saved deposit of it, with the nearest deposit of any kind dotted.

Other controls and lines:

- The **Help** button in the window header explains every mark.
- The **Radar reaches** buttons under the radar set its reach: 50 m, 250 m, 500 m, 1 km or 2 km (2 km is the default, and the choice is remembered). The current reach is highlighted.
- The radar needs the position and the body's size. Until available (not on or just above the ground), it reads `The radar draws when you are on or just above the ground.`
- On the right are the lines of the Surface Mining page described above: the run, cargo, refined, the last DSS scan, saved deposits here, the nearest marked location and the nearest saved deposit.

The controls that act on the ground are in the header:

| Button | Function |
|---|---|
| **Mark center** | Marks the center of the mining location at the current position ([details](#marking-a-mining-location)). |
| **Mark border** | Marks its border, which gives the radius. |
| **Add hotspot** | Saves the deposit at the current position as a hotspot (the same form as in the Surface Mining Book). |
| **Rig placed** | Notes the Rhino's position as a mining rig just placed (Ctrl+Alt+Shift+R, or `!wf rig` in Elite's chat, does the same without the window). The journal does not record where a rig was placed. |
| **Clear rigs** | Discards the rigs. They are also discarded when the Rhino is launched or stowed, destroyed, or the body changes; nothing about them is saved. |
| **Save map** | Saves a picture of the location (the ground driven, the border, the drive rings, the stops and the deposits, with a title and a legend) to a PNG file. It holds no commander name or date. |
| **Help** | Explains every mark on the radar. |
| **Import/export** | Imports or exports saved hotspots. |

The radar draws when the Rhino is on or just above the ground and the body's size is known; otherwise it states this. The ground "driven" is where the Rhino has been, not what was scanned, as on the minimap.

The window subtitle names the body and system. **Save map** needs the same two items; without them its status line reads `The map needs your position and the body's size: land, or launch the Rhino, first.` The offered file name is the body's name, a space and `map.png`. The picture is centered on the nearest marked location (on the Rhino when none is marked).

### Keyboard shortcuts and chat commands

Three of the controls, the radar range and the window itself have shortcuts. They are set on **Settings → WFMT → General → Shortcuts** and listed in [Shortcuts](shortcuts.md).

| Action | Default key (Windows) | Chat command |
|---|---|---|
| Mark the center (**Mark center**) | Ctrl+Alt+Shift+C | `!wf center` |
| Mark the border (**Mark border**) | Ctrl+Alt+Shift+B | `!wf border` |
| **Rig placed** | Ctrl+Alt+Shift+R | `!wf rig` |
| Radar range (steps 50 m, 250 m, 500 m, 1 km, 2 km, then back to 50 m) | Ctrl+Alt+Shift+Z | `!wf zoom` |
| Open the Surface Mining Live window (with its Book and Dashboard buttons) | Ctrl+Alt+Shift+L | `!wf live` |

Chat commands are off until *Chat commands* is ticked on that page. The key combinations work on Windows only; on Linux the chat commands are used.

### The radar over the game

**Settings → WFMT → Overlays → Mining → Show the Mining radar over the game** draws the same radar over the game while the Rhino is out, about once a second, and removes it when the Rhino is stowed.

- It requires WFMT's built-in overlay (Windows; **Overlays → Overlay Connection**). EDMCModernOverlay cannot draw a picture, so on Linux, or with that overlay, the setting has no effect.
- The background and the green of the ground driven are translucent. Everything else is solid.
- The card size (240 to 560 pixels, 340 by default) and the background opacity (30 to 100 percent, 70 by default) are on the same page, with a **Test radar** button that draws the simulation's pretend Rhino for a few seconds at the size and opacity typed in the boxes (they are saved only when OK is pressed). It reports `Needs WFMT's built-in overlay` when that overlay is not in use.
- The card appears only while the Rhino is out and WFMT knows the position and the body's size; it is removed when any of these stops.
- Its reach equals the Live radar's, so the radar range shortcut or chat command, or the Live window's range buttons, change it too.
- Its position is set under **Overlay Placement → Mining radar**. The default is the Bio radar's position at the left.

### Rig bands

The game does not publish how close two mining rigs may be, so WFMT uses a distance entered by the commander: *Too close for another rig* on the Surface Mining window's Settings card.

To measure it: stand at one rig, press **Mark center**, drive until the game permits placing the next rig, press **Mark border**, and enter that distance.

With the distance set:

- Each rig noted with **Rig placed** gets a band of that radius on the radar: a filled disc while the Rhino is inside it, and a thin outline once the Rhino is clear.
- The lines on the right give the number of rigs noted and the distance to the nearest.
- Each rig is a small numbered square (1 is the first placed).
- Pressing **Rig placed** twice within 5 m of the same rig adds nothing, and WFMT keeps at most 40 rigs on a body.
- With no gap set, the radar shows only the squares and states that a gap can be set.
- The rigs and the radar card over the game follow the same rule.

### Space Mining Live

- It shows all lines of the Space Mining page described above, with the **Settings** card at the top, and **Hotspots**, **Prices** and **Reserves** in the header when those lookups are enabled in Settings.
- It has no radar: the journal does not record where a ring's hotspots are.

The panel keeps the summary and the **Space Mining**, **Surface Mining** and lookup buttons. **Book**, **Dashboard**, **Mark center**, **Mark border**, **Add hotspot** and **Import/export** are in the windows only.

### Trying the live window without the game

**Settings → WFMT → Mining → Simulation → Surface Live (pretend Rhino)** opens the Surface Live window on simulated data:

- a Rhino driving a ring round the middle of a simulated mining location 4.5 km in radius,
- some ground already driven,
- six saved deposits (one depleted, drawn as a hollow ring, and one saved without a position, which is listed but not placed on the radar),
- two marked mining locations (one without a border),
- ore being refined.

At the default 2 km range, an arc of the ring and the nearest deposit are visible.

The simulation checks that the radar, its range buttons, the lines on the right and **Mark center**, **Mark border** and **Add hotspot** work on the local computer. The window title contains *(simulation)* and the subtitle *SIMULATION*; it has no **Import/export**.

Nothing shown is real and nothing entered in it is saved.

- It keeps its own copy of the data in memory, does not read or change the saved deposits, marks or runs, and is discarded when closed.
- It opens as its own window, so it never replaces a live window showing a real run.

## Marking a mining location

A surface mining signal is a circle of ground with the deposits scattered inside it and a few just outside its edge. The journal states that a body has mining locations but not their position or size, so they are marked manually:

1. Open **Surface Mining**. Drive to the middle of the signal and press **Mark center** (in the live window's header).
   - Pressing it again within 100 m of the same center moves it.
   - Pressing it elsewhere starts another location (up to 12 per body; past that the oldest is dropped).
2. Drive to the edge of the signal and press **Mark border** (also in the live window). The radius is the distance from the center, shown on the page (`Border marked: the signal is 1.50 km in radius`). **Mark border** works on the marked center nearest the Rhino. Within 100 m of that center, it states the distance and asks to drive to the edge first. With no center marked on the body it asks to press **Mark center** first. Pressing **Mark border** again elsewhere resets the border.
3. The minimap draws a cross at the center and the circle through the border.

**Nearest marked location** on the page gives:

- the radius,
- the direction and distance of the center,
- `edge driven 64%`: the share of the circle's edge within about 2 km of driven ground (the same reach the minimap paints).

Driving around the edge, with the scanner overlapping, raises it to 100%.

**Example.**

1. Press **Surface Mining**, drive to the middle of the signal and press **Mark center**. The minimap draws a cross at the center.
2. Drive to the edge and press **Mark border**. The page reads, for example, `Border marked: the signal is 1.50 km in radius`.
3. Drive around the edge. **Nearest marked location** shows the radius, the direction and distance of the center, and `edge driven 64%`.
4. Afterwards the line reads `you are inside it, 410 m from the edge` or `you are outside it by 150 m`.
5. If **Mark border** was pressed within 100 m of the center, the page asks to drive to the edge first. Nothing is changed.

### Am I inside it, and is there room for another rig?

Once the border is marked, the **Nearest marked location** line reads `you are inside it, 410 m from the edge` or `you are outside it by 150 m`. The page also gives the **nearest saved deposit** (its material, distance and direction).

The game does not publish how close two rigs may be, so WFMT has no built-in value. A value can be set:

- Set **Too close for another rig** (the Surface Mining window's Settings card, 0 to 2000 m, off at 0).
- The line then also states whether that deposit is closer than the set distance ("too close to place another rig") or farther ("far enough").
- To determine the value, stand at one rig and press **Mark center**, drive until the game permits placing the next, press **Mark border**, and read the distance.
- The comparison is against saved deposits, not placed rigs: the journal does not report where a rig is.

### What is kept

The marks are per commander and persist for the body. They are the commander's own readings: the game does not report the signal's size, and "driven" is not "scanned". They are not sent anywhere.

## The Space Mining Book

**Book** in the Space Mining window's header opens the book. It lists every ring that the journals show hotspots for or that was mined. It is built from what the game wrote when the ring was DSS-scanned and mined, so it fills itself.

- A ring the journals show only as part of a scanned planet (no hotspots, no mining) is omitted.
- A ring with a note, a favorite star, or added by hand remains.

The window is one table with a detail panel under it. Columns: **★** (favorite), **Ring**, **System**, **Hotspots (count per mineral)**, **Class**, **Reserve**, **Tons mined** and **Last mined**. Click a heading to sort. Until sorted: favorites first, then the ring with the most tons, then the one with the most hotspots. Selecting a row fills the panel under the table with the ring's hotspots (up to 30 minerals), class and reserve, `Mined: 620 t in 3 runs, last 2026-10-12` (or `Not mined yet`) and `Added by hand` for rings added manually. The subtitle gives the commander, the number of rings and the tons mined in total.

Per ring:

- **Hotspots**: each mineral a DSS scan found, with its hotspot count, for example `Painite 3, Platinum 2`. The journal gives only the count, not the positions or whether two minerals share a spot.
- **Class and Reserve**: the ring class (Icy, Rocky, Metallic, Metal rich) and its reserve level (Pristine, Major, Common, Low, Depleted), from the scan of the planet the ring circles, when the journal has it.
- **Tons mined** and **Last mined**: what was refined in the ring, from the mining runs ([Mining History](#mining-history) reads them).

Actions:

- **Your note** and a favorite star. Select a ring, type in **Your note** and press **Save note** (or Enter). **Favorite** toggles the star; starred rings move to the top.
- **Copy system** copies the ring's system for the galaxy map.
- **Find** narrows the list by ring, system, mineral or note while typing.
- **Favorites only** shows only starred rings.
- **Add ring** (top right) adds a ring by hand. The form asks for the ring's name as the game names it (required), the system, the hotspots written like `Painite 3, Platinum 2`, the class (Icy, Rocky, Metallic or Metal rich) and the reserve level (Pristine, Major, Common, Low or Depleted). A hotspot list that does not read that way is refused with a hint. A known commander is required.
- **Remove** removes a ring added by hand. A ring from the journals cannot be removed (it returns when the journals are read); the status line says so.
- **This system** (header button) goes to the rings in the current system, or reads `You have not worked this system yet.` It puts the system name in **Find**.
- **Refresh** reads the newest journal immediately. The window also stays current while the journals are read for the first time.
- **Help** explains where the rings come from and what **Remove** does.

If the list is long, the first 150 rings are drawn (favorites first, then the most tons mined) so the window opens and closes quickly. The subtitle states when more match, and **Find** reaches them.

**Example.**

1. Press **Book** in the Space Mining window's header and press **Add ring**.
2. Enter the ring's name as the game names it, the system, hotspots written as `Painite 3, Platinum 2`, a class (for example Metallic) and a reserve level (for example Pristine), then save. The ring shows `Added by hand`.
3. Select a mined ring, type a note in **Your note**, press **Save note**, then press **Favorite**. The ring moves to the top and its panel shows `Mined: 620 t in 3 runs, last 2026-10-12`.
4. In that system later, press **This system** to list the rings there.

### Reading the journals

- The first time, WFMT reads every journal in the background for ring scans, as Mining History does.
- A notice at the top of the window gives the progress (for example `Reading your journals for rings and mining (40%)`), and the list grows as it proceeds. The list is redrawn only when something has changed.
- Afterwards only new journals are read.
- Rings, notes and favorites belong to the current commander. Only that commander's journals are read; another commander's are skipped.
- Nothing is sent anywhere.

## The Surface Mining Book

**Book** in the Surface Mining window's header opens the book. Mining is not required to open it; it lists saved hotspots in either case.

The Surface Mining Book is the book for the Rhino's surface deposits (the Space Mining Book, above, is the one for rings). It lists:

- the bodies scanned in the current system,
- every saved hotspot,
- a **From your journals** group: every other body whose DSS scan found planetary mining locations (how many) or on which the Rhino refined (the tons), read from all the journals.

About the **From your journals** group:

- It shows which bodies were worth landing on. The journal does not give a deposit's position, so deposits remain the hotspots that are saved.
- A body with saved hotspots also shows the journals' tons.
- The first time, the window's subtitle and status line state that the journals are being read, and the list grows as it proceeds.
- It is built from the current commander's journals only.

**This system** (header button) goes to the body worked in the current system (saved hotspots, tons refined or mining locations found), or reads `You have not worked this system yet.`

### The three panes

- **Left, Bodies.** Two filters on top: a material (`All materials` or any saved material) and a number of rigs (`Any rigs`, `1 rigs`, and so on for the saved counts). Under them the bodies are grouped: one group per planet class among the bodies scanned in the current system (with the number of mining locations the scan found and the tons refined there), then **Saved, not scanned this session** (saved bodies in this system that the journals show no scan of), **Other systems** (saved bodies elsewhere) and **From your journals**. A pill shows the number of hotspots saved on a body. Clicking a group heading folds it. With a material filter, a scanned body also remains when the commander's own records show that material on its kind of ground, highest share first, and a line gives the percentage of recorded deposits there that are that material. The **From your journals** group is hidden while a filter is on.
- **Middle, Hotspots.** The selected body's saved deposits, grouped by location number (`Location 1`, `Location 2` and so on, with `Unnumbered` last), each with its material, rigs, tons-left estimate, tons mined and a pill for its Amount. Three tiles give the hotspots saved, the tons mined here and the number not depleted. A summary line gives the materials saved on the body (`Monazite ×2 · Painite ×1`). Below it are the best stops and, for a scanned body, the **Your records** table (Material, Share, Recorded, Saved) of what has been found on that kind of ground, which describes the commander's own finds and not what the body holds.
- **Right, the card and the map.** The selected deposit's material, location and rigs, its Density and Amount pills, the tons-left estimate, its depleted status, the tons mined, its coordinates and its note, with these buttons: **Mark depleted** (not shown once depleted), **Copy coords** (shown when it has a position), **Share line** (when it can be shared), **Edit** and **Delete** (it asks first). Under the card is a zoomable map of the body: the ground driven, the deposits (with their signal numbers, a hollow ring for a depleted one), the position, and the stop circles. The map needs the body's size, which WFMT has only for a body visited this session; otherwise it states this.

The header buttons are **Add hotspot**, **Market research**, **What pays**, **Get body info**, **Paste spot** and **This system**. The window opens on the current body when there is one, and refreshes itself when a hotspot is saved or changed.

Functions:

- filter by material or number of rigs,
- view tons mined and an estimate of tons left,
- add a hotspot by hand (**Add hotspot**, top right),
- edit a hotspot or mark it as depleted,
- copy its coordinates,
- view a zoomable map,
- view the best **stops** on the current body (below),
- open **Market research** and **What pays** (below),
- press **Get body info** to add the landable bodies EDSM lists for the system (below),
- **Share line** and **Paste spot** (below).

### Adding or editing a hotspot

**Add hotspot** (in the Surface Mining Book and in the Live window, and **Add** in Settings) opens one form; **Edit** opens the same form filled in. It starts with the current system, body and position when on the ground. Fields:

| Field | Entry |
|---|---|
| **System**, **Body** | Required. |
| **Latitude**, **Longitude** | Optional, in degrees. Without them the deposit is listed but not placed on the map or radar, and cannot be shared. |
| **Contains** | Required. The commodity the deposit holds, for example Painite. Suggestions follow the input, with the already saved materials first. The spelling is normalized, so `painite` and `Painite` are one material. |
| **Rigs** | Optional, 1 to 7: the number of mining rigs the deposit takes. |
| **Signal number** | Optional. Which of the body's mining locations contains the deposit. Hotspots with the same number are listed together. |
| **Amount** | The scanner's readout: `High`, `Medium`, `Low` or `Depleted`. Only these four are offered, because any other text would drop out of the tons-left estimate. |
| **Density** | The scanner's readout: `Low`, `Medium` or `High`. |
| **Folder** | A name to file it under. A name that does not exist yet creates the folder. |
| **Notes** | Free text. |

**Example.**

1. At the deposit, press **Add hotspot** in the **Live** window. The form opens with the system, body and position filled in.
2. Type `Painite` in **Contains** and set **Rigs** to the number the deposit takes, for example 4.
3. Set **Amount** and **Density** to the scanner readout, and type a **Signal number** if known.
4. Save. The deposit appears in the Surface Mining Book and on the radar.

An edit keeps the tons mined and the kind of ground that WFMT recorded. A form with a missing or invalid entry shows a one-line error and stays open. Saving a new hotspot with a position from **Add hotspot**, within 100 m of an existing hotspot on the same body, updates that hotspot (keeping its position, folder, notes and tons mined unless new ones are supplied) instead of adding a second. This allows correcting a material by saving again at the same spot. **Add** in Settings always adds.

### Depleted marks

A hotspot marked depleted is dated, and its card states how long ago.

- No refill time for a mined-out deposit is known (the game gives no date). By default the mark stays until changed: read the deposit's Amount again and edit the hotspot.
- If a refill time has been observed, set it in **Deposit refills after (days)** on the Surface Mining window's Settings card (0 = unknown, up to 90 days). With a time set, the mark is removed that long after it was set, and the hotspot has no Amount until it is read again.
- If **Mark depleted** is pressed on it and nothing has been refined there since, WFMT treats this as another look at a deposit that is still empty. It keeps the first date and looks again 7 days later (`Still depleted at 15 d; look again in 7 d`).
- Tons refined since make it a fresh depletion.

**Example.**

1. At the exhausted deposit, the Book marks it `you are here` and selects it. Open **Book** and press **Mark depleted**.
2. The card shows the date and how long ago. The mark stays until changed, unless a refill time is set on the Surface Mining window's Settings card.
3. Later, read the Amount again and press **Edit** to set the new reading if the deposit has refilled.
4. If a set refill time has removed the mark and **Mark depleted** is pressed again with nothing refined there since, WFMT keeps the first date and looks again 7 days later.

### Stops

Rigs sit around the Rhino, so deposits close together can be worked from one place.

- For the current body, the Book takes the saved deposit with the most rigs and every other one within the **stop radius** of it as one stop. The stop radius is on the Surface Mining window's Settings card (500 to 2500 m, default 1250 m).
- The best three are listed above the hotspots, with the tons left summed. They are circled on the map and tagged `stop 1` to `stop 3` on each row.
- The best three are led by a deposit of 5 or more rigs (4 or more if the body has none).
- Deposits that are depleted, or have no position or rig count, are excluded.
- Stops need the body's radius, which WFMT has only for a body visited this session. A body that is not the current one shows none.

### Market research

**Market research** determines which markets in the system buy the commodities that can be mined there.

- It uses only the commander's own records: deposits saved in that system, what has been recorded on the same kind of ground as its scanned bodies, and anything typed into *Also check*.
- For each commodity it lists the markets that buy it, best price first, with demand, the age of the prices, the distance from the star and the pad size.
- A system with no records suggests nothing until a commodity is added or a hotspot is saved.
- It is off until **Mining: best price finder and Market research** is ticked (Settings → WFMT → Online); the window says so while it is off.
- It excludes fleet carriers and markets not updated in 30 days.
- It sends only the system's name.
- Prices are the last ones players uploaded.

### Get body info

The Book's list of bodies comes from the `Scan` events in the journals. A body scanned in a session whose journal is no longer available is missing from it, and its ground type is unknown to the rates.

**Get body info** asks EDSM, and Spansh when WFMT knows the system's id (from the latest jump or login), for the bodies of the current system.

- It adds each landable planet the journals did not give: its name, kind, volcanism and size.
- From Spansh, it adds the number of mining locations a body carries.
- It then reports how many of each it added.
- A body, size or count that the journals already gave is never replaced.
- The services hold only systems that players' tools uploaded, and neither gives the position of a mining location, so marks come from the commander's own driving.

Privacy and settings:

- It sends only the system's name to EDSM and its id to Spansh (one request each, under the same courtesy rules as other Spansh calls).
- It is off until **Mining: Get body info in the Surface Mining Book** is ticked in Settings → WFMT → Online; the Book says so when **Get body info** is pressed while it is off.

Storage:

- The result is stored per commander (the newest 60 systems, in `mining_body_cache.json`), so returning to the system or restarting EDMC restores the bodies without another request.
- The bodies the System targets cards already know for a system (saved between sessions, and rebuilt from the journals) are also added to the list on arrival.
- The mining-location count of a body is also filled in when it is FSS-scanned (the game writes it without a visit), and a detailed surface scan replaces that.
- A body's size is also read from `Status.json` whenever the Rhino is near the ground, so the radar, **Mark center** and **Mark border** work on a body that was never scanned, without this lookup.

### What pays

**What pays** ranks the commodities that can be mined by the best price Spansh shows for them.

**Commodities priced**, one after another (at most 16 in all):

- the target commodity from Settings,
- every material in the saved deposits (in any system),
- what has been recorded on the same kind of ground as the bodies scanned in the current system,
- any commodities typed into *Also check*.

**Query.** For each commodity, Spansh is asked for the station that pays most:

- within the chosen distance (10 ly to anywhere, or only the system in the box) of the system in *Near* (the current system by default);
- among stations updated in the last 30 days;
- fleet carriers are excluded. Spansh is asked for stations only (orbital and ground ports, outposts, settlements, asteroid bases and megaships), and any carrier that is still returned is dropped;
- a station must show demand of at least the tons of that commodity in the hold when EDMC knows them, otherwise at least 1 t;
- pad size is not filtered (the table shows it), and neither is a market's age within the 30 days.

**Table.**

- It fills as answers arrive and is ordered best price first when it finishes.
- Columns: the commodity, its best price, the station, system, distance, demand, arrival distance, landing pads and the reason it is listed.
- Click a heading to sort. **Copy report** copies the ranking. **Help** explains the columns.
- A commodity no station pays for shows *No station found*.

**Notes.**

- It sends only a commodity's name, the system's name, the distance and the minimum demand.
- It uses the same **Mining: best price finder and Market research** switch (Settings → WFMT → Online).
- It ranks what pays, not what a body holds. The game does not state which commodities a body carries, so a commodity is listed because of the commander's own records and not because of the kind of body.

### Sharing a deposit

- **Share line** on a hotspot's card copies one line of text (`WFMT-SPOT1:...`) that can be posted in Discord.
- In another Surface Mining Book, **Paste spot** (top of the window) reads it from the clipboard, validates it and asks for confirmation before adding it to the current commander.
- The line holds the system, body, material, rigs, location number, position, Amount, Density and kind of ground. It never holds a commander name, notes, folder, tons mined or dates.
- A line that was cut short or altered is refused, and so is a deposit within 100 m of an existing deposit on that body.
- A hotspot with no position cannot be shared.

**Example.**

1. In the Surface Mining Book, select the hotspot and press **Share line**. The line (`WFMT-SPOT1:...`) is on the clipboard.
2. Paste it into Discord.
3. The recipient copies the line, opens their Surface Mining Book and presses **Paste spot**. WFMT validates it and asks before adding it to their commander.
4. If the line was cut short, or a deposit within 100 m already exists on that body, it is refused.

### The `you are here` marker

With the Rhino on the body, the deposit within 175 m of it is marked `you are here` and selected, so **Mark depleted** requires one click. It is computed when the Book is opened or refreshed, not while driving.

### Per commander

Hotspots, tons mined, depleted marks and the ground driven belong to the current commander.

- Switching commander switches the Surface Mining Book and the coverage map. One commander never sees or changes another's.
- To transfer a hotspot list to another commander, use **Import/export** (in the live window) to export it as the first commander and import it as the second.

For a scanned body, the Book also shows what the commander has found so far on that kind of body. That starts empty and fills as hotspots are saved. It describes the commander's own finds, not what a body holds.

## Mining alerts

Mining alerts are cards on the Flight Alerts overlay, so an overlay must be running and Flight Alerts enabled. They are set on **Settings → WFMT → Overlays → Flight Alerts**: tick *Enable Flight Alerts* (off by default), confirm *Mining alerts* is ticked (on by default), then set the limpet number and the hold percentage. See [Always on](always-on.md#flight-alerts).

| Card | Condition | Settings |
|---|---|---|
| `Core asteroid` and the core mineral (green) | A prospected rock names a core mineral. It stays 30 seconds. | None; a core asteroid is always flagged. |
| `Rich rock: Painite`, `38% of the rock` (green) | A rock holds at least a target commodity's percentage. One card per target it holds enough of (the richest three at most), 30 seconds each. No card when the rock has less than a quarter of itself left. | *Target commodities* in Settings → WFMT → Mining |
| `Low on limpets`, `3 aboard` (amber) | The limpets aboard are at or under the configured number (5 by default, 0 to 99). | *Warn when the limpets aboard are at or under* |
| `Hold nearly full`, `190 of 200 t` (amber) | The hold is at or over the configured percentage (95 by default, 50 to 100) of the capacity from the last loadout. | *Warn when the hold is at or over* |

- A rock prospected again with the same composition does not raise a second card or sound. A new run (the next undocking) clears the rocks seen.
- The limpet and hold cards show only while mining, meaning a prospector, refinery, limpet or cracking event in the last half hour.
- The low-limpet card applies only when a prospector or collector limpet controller is in the last loadout or limpets have been seen aboard, and never while a Rhino is out.
- The hold figure comes from `Status.json` about once a second when in the ship, and from the `Cargo` event otherwise.
- *Play a sound when an alert starts* on the same page plays a sound for a new alert.

**Example.**

1. Open **Settings → WFMT → Overlays → Flight Alerts**, tick *Enable Flight Alerts* and keep *Mining alerts* ticked.
2. Keep the hold percentage at 95 and the limpet number at 5, or change them.
3. With a 200 t hold, a `Hold nearly full` card reading `190 of 200 t` appears in amber at 190 t. At 3 limpets, a `Low on limpets` card reading `3 aboard` appears.
4. With Painite set as a target, a prospected rock with enough of it raises a green `Rich rock: Painite` card for 30 seconds.

## What the game does and doesn't tell us, and how to work around it

WFMT uses what Elite Dangerous writes to its journal files, plus what Spansh and EDSM report. Where a value cannot be determined, WFMT marks it as an estimate. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| Item | What the game provides | Handling |
|---|---|---|
| Ring and deposit amounts | Amount and Density are not given to WFMT. They are typed in by hand. | The entered figure determines the range; a wrong entry gives a wrong range. |
| When a mined-out deposit refills | Nothing in the journal states it. WFMT shows it as unknown and leaves the mark. | Read the Amount again at the deposit and edit the hotspot, or set a time to assume in Settings → WFMT → Mining. |
| Which commodities a body carries | The game does not state it. Market research and What pays use the commander's own records. | Save hotspots as found, or type commodities into *Also check*. |
| Exact tons left in a deposit | The deposit figures are measurements from a small number of deposits, so the ranges are wide. | "Tons left" is a guide, not a count. |
| A map of everywhere mined | Coverage means ground the Rhino has driven over, not ground it has scanned. | The minimap shows where the Rhino has been, not what is left. |
| Mining history from before WFMT first ran, or from deleted journals | The history is built from the journal files that exist. | WFMT keeps the runs it has already read. |
| The ship's hold while the Rhino is out | `Status.json` carries a `Cargo` figure, but what it counts while an SRV is out could not be checked, so WFMT does not use it then, or on foot. | The Ship hold line shows the last `Cargo` event's figure until the commander is back in the ship. |
| An exact count of limpets aboard | The exact count comes from EDMC's cargo once it has been supplied; until then "on board" is an estimate (bought less launched, marked `~`). The low-limpet alert applies only when a prospector or collector limpet controller is in the last loadout or limpets have been seen aboard, and never while a Rhino is out. | The cargo screen shows the actual number. |
| Best mining method per commodity | The method hints are a static table in `mining_methods.py`, not journal data. | The game is authoritative. |
| Where a ring's hotspots are, or whether two minerals share one | A DSS scan gives each mineral's hotspot count only. | The Space Mining Book lists counts. Findings can be recorded in **Your note**. |
| Where a surface mining location is and how big it is | The journal states that a body has mining locations, not where or how large. | Mark the center and border with **Mark center** and **Mark border** ([marking a location](#marking-a-mining-location)). |
| Where a mining rig went, and how close two rigs may be | The journal does not state where a rig was placed, and the game does not publish a minimum gap. | Press **Rig placed** after each rig and enter the measured gap in Settings. |
| How far the Rhino's scanner reaches | No figure from Frontier. WFMT uses 2 km for the driven-ground map, the edge percentage and the drive rings. | Treat those as approximate. |
| Ring reserve and hotspot lookups always answering | They know only what players have uploaded to EDSM or Spansh. | No answer means the ring has not been recorded. Scan the ring, then save the hotspot with **Add hotspot**. |

## Settings

**Settings → WFMT → Mining**

The in-game Mining displays are set on **Settings → WFMT → Overlays → Mining** (see below).

**In the windows.** The display and tuning settings are in the **Settings** card at the top of the **Space Mining** and **Surface Mining** windows, and nowhere else. A tick saves on click; a box saves on Enter or when focus leaves it, and a number is kept inside its range.

- Both windows: *Show session totals*, *Show the cargo bar* and *Show prospector hints* (on by default). See [What each page shows](#what-each-page-shows) for the lines each controls.
- Space Mining: *Target commodities* with *worth cracking at* (and the line under them that states how many targets are set, or what is wrong). See [Target commodities](#target-commodities).
- Surface Mining:
  - *Show coverage minimap*: a small map of ground the Rhino has driven over on the current body, redrawn once a second while the Rhino is deployed.
  - *Stop radius*: how close deposits must be to the lead deposit to share a stop in the Surface Mining Book (500 to 2500 m in steps of 250, default 1250).
  - *Too close for another rig*: the distance used for the Surface Mining page's "far enough" note and the radar's rig bands (0 turns it off; 0 to 2000 m, steps of 5).
  - *Deposit refills after (days)*: 0 (default) means unknown and marks stay; a number from 1 to 90 removes a Depleted mark that long after it was set.

**Settings → WFMT → Online** holds the switches that permit WFMT to contact other services (the four Mining lookups below), and **Settings → WFMT → Mining** holds the archive option and the simulation and shows a note pointing to the Online tab:

- **Mining: nearby hotspot finder** (Space Mining page): lets **Hotspots** search.
- **Mining: best price finder and Market research**: lets **Prices** search and enables **Market research** and **What pays** in the Surface Mining Book.
- **Mining: ring reserve lookup** (Space Mining page): lets **Reserves** search and looks up each ring dropped into automatically.
- **Mining: Get body info in the Surface Mining Book**: enables **Get body info** in the Surface Mining Book (asks edsm.net and spansh.co.uk for the bodies of the system, sending only its name or id).
- *Archive completed mining runs*: writes a JSON file per run to `mining_sessions/`. A trip with nothing in it writes nothing.
- **Simulation: Surface Live (pretend Rhino)**: opens the Live window on simulated data (see [Trying the live window without the game](#trying-the-live-window-without-the-game)). The simulation window has no Settings card.

**Known Surface Hotspots.** At the bottom of the same page is a list of every saved hotspot, grouped by folder (`Unfiled` last), one line each with the system, body, material, rigs, signal number and tons-left estimate. Select a line and use **Add**, **Edit**, **Delete** (a folder heading cannot be edited or deleted), **Import...** and **Export...**. These open the same form and the same import and export as the Surface Mining Book and the Live window's **Import/export** button. **Import...** reads a hotspot file exported by WFMT and asks whether to merge with the list (Yes) or replace it (No). **Export...** writes the saved hotspots to a JSON file. A list belongs to the current commander, and an export holds only that commander's list.

**Settings → WFMT → Overlays → Mining**

- *Enable HUD Overlay*: sends the hold, *Refining now*, *Run average*, *Hold full in* and *Limpets remaining* lines to the overlay. It follows the three display switches above. On the Surface page it sends the SRV and ship holds and the rates, and it stops while the ship is in supercruise. Its position is **Overlay Placement → Mining stats**. **Test HUD** draws a sample panel for a few seconds and reports whether the overlay was reachable (it works even while the HUD is off).
- *Show the Mining radar over the game while the Rhino is out*, with its **Size (pixels)**, **Background opacity (%)** and **Test radar** (see [The radar over the game](#the-radar-over-the-game)).

**The arrow to the nearest known hotspot** is the **Surface Compass** (Settings → WFMT → Overlays → Surface Compass, and the Compass section in [Exploration](exploration.md#compass)). It points at the nearest hotspot by default, and also works from any mode.

### Target commodities

Enter a commodity as the game names it (for example Painite) and the least share of a rock that makes it worth cracking.

- Several can be entered, separated by commas or semicolons, each with its own percentage after the name: `Painite 30, Platinum 25, Void Opals`.
- A name with no number uses the percentage beside the box (20 by default, 1 to 100).
- Up to 8 are used. A line under the box states what is wrong, such as a percentage outside 1 to 100.
- The commodity may be typed in any spelling (Void Opals or Void Opal, Low Temperature Diamonds or Low Temp. Diamonds).
- Empty means none.
- A core asteroid is always flagged.

Effects:

- The page marks a rock at or over one of them and names which (`target: Painite`).
- Flight Alerts can show a card on the overlay for each, `Rich rock: Painite`.
- The radar and What pays use the first one.
- A rich-rock card is not raised for a rock with less than a quarter of itself left.
- A rock prospected again with the same composition does not raise a second card or sound.
- Each target a rock holds enough of raises its own card once.

**Example.** With `Painite 30, Platinum 25, Void Opals` entered and the percentage box at 20:

- A rock with Painite 34% and Platinum 12% is marked `target: Painite`: Painite is over its 30, Platinum is under its 25.
- A rock with Void Opals 22% counts as a target, because a name with no number uses the 20 beside the box.
- The radar and What pays use the first target, Painite.

See the [Mining specification](../MINING_TECH_SPEC.md).
