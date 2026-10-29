# Mining

Mining mode tracks two kinds of mining, keeps a book for each, and adds up everything you have mined:

- **Space Mining**, in your ship, with the **Space Mining Book**: every ring your journals have shown, with its hotspots, tons mined and your notes.
- **Surface Mining**, in the Rhino SRV, with the **Surface Mining Book**: your catalog of deposits, and the bodies your journals show mining on.
- **Mining History**: every run in your journals, added up.

Use the **◀** and **▶** buttons at the top of the panel to switch between the two pages. Each page shows live stats
for your current run, and its **BOOK** button opens the book for that page.

**On this page:** [How to](#how-to) · [What each page shows](#what-each-page-shows) · [The buttons](#the-buttons) · [A typical run](#a-typical-run) · [Mining History](#mining-history) · [The live window](#the-live-window) · [Marking a mining location](#marking-a-mining-location) · [The Space Mining Book](#the-space-mining-book) · [The Surface Mining Book](#the-surface-mining-book) · [Mining alerts](#mining-alerts) · [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it) · [Settings](#settings)

**Where this comes from:**

- The journal records what you prospect, refine and collect.
- It does not record a ring's deposit amounts or density, which you type in.
- The hotspot catalog is your own.
- Ring reserve and hotspot lookups use what players have uploaded to EDSM and Spansh.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## How to

**Start a Space Mining run.** Details: [Space Mining](#space-mining).

1. Use the **◀** and **▶** buttons at the top of the panel until the Space Mining page shows.
2. Undock. A new run begins. The page keeps saying `No active mining run. Undock to start tracking a new run.` until the run has something to show (tons in the hold, a prospected rock, a launched limpet or a refined ton), then the live numbers of the run appear.
3. Fly to the ring and start mining. The **Hold**, **Asteroids prospected** and **Refined** lines fill in as you work.

**Start a Surface Mining run.** Details: [Surface Mining](#surface-mining).

1. Switch to the Surface Mining page with **◀** or **▶**.
2. Launch the Rhino. The page changes from `No active Rhino deployment. Launch the Rhino to start tracking a new run.` to the live numbers.
3. Stow the Rhino to end the run. The numbers stay on the page, marked `Rhino stowed (last deployment)`, until the next launch.

**Read the radar.** Details: [Surface Mining Live](#surface-mining-live).

1. On the Surface Mining page, press **LIVE**.
2. Land, or drive, so you are on or just above the ground. Until then the window says `The radar draws when you are on or just above the ground.`
3. Pick a reach with the **Radar reaches** buttons (50 m to 2 km) and press **Help** in the window's header to see what each mark means.

**Log a ring.** Details: [The Space Mining Book](#the-space-mining-book).

1. Press **BOOK** on the Space Mining page. Rings you DSS-scanned or mined at are added by themselves.
2. For a ring the journals have not shown, press **Add ring** and fill in the form.
3. Select a ring, type in **Your note**, press **Save note**, and use **Favorite** to star it.

**Log a surface deposit.** Details: [Adding or editing a hotspot](#adding-or-editing-a-hotspot).

1. Stand at the deposit in the Rhino and press **Add hotspot** in the **LIVE** window (the Surface Mining Book has one too).
2. Check the **Contains**, **Rigs**, **Amount** and **Density** fields, and save.

**Use Mining History.** Details: [Mining History](#mining-history).

1. Press **DASHBOARD** on the page you are on (rings on the Space page, the Rhino on the Surface page).
2. Read the **Overview** tab first, then open **Rings**, **Commodities** or **Runs** and click a heading to sort.
3. Press **Refresh** to read the newest journal now.

**Set mining alerts.** Details: [Mining alerts](#mining-alerts).

1. Open **Settings → WFMT → Overlays → Flight Alerts** and tick *Enable Flight Alerts*.
2. Make sure *Mining alerts* is ticked, then set the limpet number and the hold percentage.
3. For rich-rock cards, type your commodities in **Settings → WFMT → Mining → Target commodities** ([how](#target-commodities)).

**Find a hotspot.** Details: [HOTSPOTS: Find Nearby Hotspots](#hotspots-find-nearby-hotspots).

1. Tick *Enable Spansh nearby hotspot finder* in **Settings → WFMT → Mining**.
2. On the Space Mining page press **HOTSPOTS**, pick a **Material** and a **Where** distance, and press **Search**.
3. Select a row and press **Copy system** to paste the system into the galaxy map.

## What each page shows

Lines come and go with the settings listed at the end of this page. Three switches under **Settings → WFMT → Mining** decide which lines you see (all three are on by default):

| Setting | Lines it controls |
|---|---|
| *Show the cargo bar* | The hold lines (**Hold** on the Space page; **SRV hold** and **Ship hold** on the Surface page) |
| *Show session totals* | **Refined**, **Refining now**, **Run average**, **Hold full in** and **What the station pays** (Space page); **Refined**, the rates, **SRV hold full in**, **Transferred to ship** and **Raw materials** (Surface page) |
| *Show prospector hints* | **Asteroids prospected**, **Materials seen**, **Last rock**, **Core asteroids found**, **Asteroids cracked** and **Limpets launched** (Space page); the **Last DSS scan** line (Surface page); the `Mine via` method hint beside each commodity in **Materials seen** |

The HUD overlay follows the same three switches, so turning a line off hides it in both places.

Before a run has started the page says so instead of showing zeros: `No commander detected yet.` until the game has told WFMT who you are, then `No active mining run. Undock to start tracking a new run.` on the Space page and `No active Rhino deployment. Launch the Rhino to start tracking a new run.` on the Surface page. Mission needs and the ring's reserve level still show on the Space page while it waits.

### Space Mining

In your ship, from undocking. A run is one trip from `Undocked` to `Docked`: the next undocking starts a fresh run and the numbers of the finished one stay on the page until then.

- **Hold**, for example `Hold: 64 of 200 t`.
  - The tons your ship carries, read live from `Status.json` (the `Cargo` event is used until it has said), and its capacity from your last loadout.
  - The same line is on the HUD overlay.
  - The ring you are at is shown with its reserve level, once *Enable EDSM ring reserve lookup* is ticked and EDSM knows it, for example `Ring: Example 2 A Ring (Metallic) - Reserve: Pristine`. A ring that is not Metallic is shown in red with a reminder that laser mining pays best on Metallic rings. Nothing is shown while the answer is unknown, rather than a stale or guessed one.
- **Asteroids prospected**, with how many of each content grade (for example `Asteroids prospected: 14 (High x3, Medium x6, Low x5)`), and the **materials seen** in them. A rock prospected again with the same composition is counted once, and the page says how many repeats it ignored (`[2 duplicate(s) ignored]`).
  - Each material in **Materials seen** is listed on its own line with how many rocks held it, the lowest, average and highest percentage seen this run in square brackets, and `Mine via` with the method that usually suits it (core, laser surface or sub-surface deposit; laser surface when no other is known). The method hints are community-sourced.
- **Last rock**: the latest rock's materials with their percentages and its grade, for example `Last rock: Painite 34%, Platinum 12% (High), target: Painite`.
  - A **core asteroid** (the game names a core mineral in the prospector's result) is counted by **Core asteroids found** (`Core asteroids found: 3 (last: Painite)`), which names the latest core. The **Last rock** line adds `core: Painite` only when its core is not that latest one.
  - `target:` names each target commodity the rock holds at least its percentage of (Settings → WFMT → Mining; several can be set).
- **Mission needs**: for each commodity your active mining missions still ask for, how many tons you already hold, for example `Mission needs: Painite 50 of 120 t held (2 missions)`. It is worked out the way the Missions window does it and shows even before you start mining. Up to three commodities get a line; more are summed up as `+2 more commodities`. A commodity asked for by several missions says how many (`(2 missions)`).
- **Asteroids cracked** (core mining).
- **Limpets launched** by type, with the count still on board. The count is exact once EDMC has told WFMT the cargo. Otherwise it is bought less launched, marked with ~. The HUD overlay's *Limpets remaining* line shows the same number.
- **Refined**, by commodity. (The `Mine via` method hints are on **Materials seen**.) Then:
  - **Refining now** (for example `Refining now: 840 t/h`): the tons refined in the last minute, scaled to an hour, falling to 0 within a minute of a lull.
  - **Run average** (for example `Run average: 720 t/h over 41 min`): the tons refined this run over its mining time, shown once the run has a minute of it.
  - One refined unit in the journal is one ton.
  - The mining time runs from the run's first to its last mining event (a limpet launched, an asteroid prospected, a ton refined or a rock cracked). It leaves out any gap of more than 10 minutes between two of them, so a long flight or a break does not drag the average down.
  - The HUD overlay carries the same two lines, and Mining History's *Mining time* and *t / hour* use the same definition.
- **Hold full in** (for example `Hold full in about 14 min`): the room left in your hold over your **Run average**.
  - Before there is an average (the first minute), it uses *Refining now*.
  - It shows with the other refining lines when the ship's capacity is known and something is being refined.
  - It says `Hold is full` once it is, unless the **Hold** line (*Show cargo bar*) is on the page, which already shows the hold at capacity. The same goes for the SRV hold on the Surface page.
  - It is a guide: a laser works in bursts, and the rate moves with the rocks.
  - The HUD overlay and the live window carry it too.
- **What the station pays**, when you are docked and have opened its commodities market (for example `Painite here: 521,400 cr/t, 8% above the galactic average (482,000)`).
  - A line for each commodity this run refined that the station buys, the most tons first, up to three.
  - It compares the station's price with the galactic average the game lists beside it, so you can tell whether to sell here or fly on.
  - It reads the game's own `Market.json` on your computer and asks nothing online.
  - A good deal is a good one only until you have looked at the next station.
  - A station that lists a price for something it does not buy (no demand) is skipped.
  - The lines go when you undock.
- A **Paused** note (`Paused (in supercruise)`) while you are in supercruise. It changes nothing: the run keeps its numbers and carries on when you drop out.

**Worked example: reading a Space run.** You undock from a station in a 200 t ship and mine a ring for about 40 minutes. Part way through, the page might read:

```
Hold: 64 of 200 t
Asteroids prospected: 14 (High x3, Medium x6, Low x5)
Last rock: Painite 34%, Platinum 12% (High), target: Painite
Refining now: 840 t/h
Run average: 720 t/h over 41 min
Hold full in about 14 min
```

- The hold has 136 t of room. The 14 minutes is that room divided by the run average, so treat it as a guide.
- The last rock held Painite above the share you set for it, so the page names it as a target. A card for it also shows on the overlay if Flight Alerts is on.
- Dock and open the commodities market, and **What the station pays** compares the station's price for what you refined with the galactic average, so you can choose between selling here and flying on.

### Surface Mining

In the Rhino SRV. A run runs from launching the Rhino to stowing it. The page keeps the last run's numbers (`Rhino stowed (last deployment)`) until the next launch, but the hold lines and *Refining now* show only while the Rhino is out.

- While the Rhino is out, its hold (`SRV hold: 40 of 72 t`) and your ship's (`Ship hold: 64 of 200 t`, from the last `Cargo` event). Both lines go once the Rhino is stowed.
- **Refined**, **Refining now** and the **Run average**. They are worded as on the Space page. *Refining now* shows only while the Rhino is out.
- **SRV hold full in**: the same estimate for the Rhino's 72 t hold, only while it is out.
- What was **Transferred to ship** and the **Raw materials** picked up.
- The **Last DSS scan**: how many mining locations the scan found on which body (`Last DSS scan: 4 Planetary Mining Location(s) on <body>`). It shows only when that count differs from the number of **Known hotspots here**, which says the same thing otherwise.
- **Known hotspots here (N)**: the ones you have saved on the body you are on, one per line with the material, rigs, signal number, position, the tons-left estimate in square brackets and your note.
- The **coverage minimap** (if ticked in Settings): ground the Rhino has driven over, with your position, your saved hotspots and the mining locations you marked with **Mark center** and **Mark border**. In your ship it appears only close to the ground (under about 2 km).
- **Nearest marked location**: the size of the mining location you marked nearest you, which way its center is and how much of its edge you have driven (see [Marking a mining location](#marking-a-mining-location)).
- **Nearest saved deposit**: the closest deposit you saved, its material, how far and which way, with your rig-gap verdict when one is set.
- **Rigs noted**: how many rigs you noted with **Rig placed** and how far the nearest is (see [Rig bands](#rig-bands)). Nothing until you note one.
- A line saying what **Mark center** or **Mark border** last did, or why it could not (`WFMT cannot read your position: be on or just above the ground.`).

**Worked example: a Rhino run.** You launch the Rhino on a body with a mining signal and drive between deposits. The page might show:

```
SRV hold: 40 of 72 t
Ship hold: 64 of 200 t
Last DSS scan: 4 Planetary Mining Location(s) on <body>
```

- The SRV hold line tells you how full the Rhino is, and **SRV hold full in** estimates the time left before it is.
- The ship hold line is the last `Cargo` figure, because WFMT does not read the ship's hold while the Rhino is out.
- Stow the Rhino and the page keeps these numbers as `Rhino stowed (last deployment)` until you launch again.

Both pages carry the buttons below, and the Surface Mining Book and the coverage map are per commander.

## The buttons

The buttons sit side by side in one row, in this order. Which ones you see depends on the page and on your
Settings. Hover for the full name.

| Button | What it does | Shown when |
|---|---|---|
| **BOOK** | Opens the book for the page you are on: the **Space Mining Book** (your rings) on the Space Mining page, the **Surface Mining Book** (Rhino deposits) on the Surface Mining page. | Always |
| **DASHBOARD** (Mining History) | Opens every mining run found in your journals, added up (see below). | Always |
| **LIVE** | Opens the live window for the page you are on: a radar and the controls on the Surface page, the live numbers on the Space page. Meant for a second screen ([the live window](#the-live-window)). | Always |
| **HOTSPOTS** (find nearby hotspots) | Opens the Find Nearby Hotspots window (see below). | Space Mining page, once *Enable Spansh nearby hotspot finder* is ticked |
| **PRICES** (find best price) | Opens the Find Best Price window (see below). | Once *Enable Spansh best price finder* is ticked (the same switch also turns on Market research and What pays in the Surface Mining Book) |
| **RESERVES** (check ring reserve level) | Opens the Check Ring Reserve Level window (see below). | Space Mining page, once *Enable EDSM ring reserve lookup* is ticked |

The three online lookups are **off until you turn them on in Settings**. See [what goes on the internet](internet-and-privacy.md).

### HOTSPOTS: Find Nearby Hotspots

1. In **Material**, pick or type a mineral (the list holds the materials known to work; a name not in it is still accepted).
2. In **Where**, choose how far to look: within 25, 50, 100 (the default), 250, 500 or 1,000 ly.
3. In **Search from**, type the system to measure from. It starts as the system you are in; **Here** puts it back. System names are suggested as you type, from the systems you have been in (and from Spansh while typing only if you ticked *Suggest system names from Spansh while typing* in Settings → WFMT → Window).
4. Press **Search** (or Enter).

The table lists up to 25 rings Spansh confirms have a hotspot for that material, nearest first. Columns: **Ring**, **Body**, **System**, **Hotspots** (how many of that material the ring has), **Distance (ly)**, **Arrival (ls)** (distance from the arrival star) and **Reserve level**. Click a heading to sort. Select a row and use **Copy ring**, **Copy body** or **Copy system** in the header, or double-click a row to copy its system, then paste it into the galaxy map.

Only the system name and the material are sent. A search that finds nothing tells you to try a longer distance or to check the spelling.

**Worked example.** You want Painite and you are in the system you will start from.

1. Tick *Enable Spansh nearby hotspot finder* in **Settings → WFMT → Mining**, then press **HOTSPOTS** on the Space Mining page.
2. Type or pick `Painite` in **Material**.
3. Leave **Where** on 100 ly, and leave **Search from** as it is (press **Here** if you changed it).
4. Press **Search**. The table lists the rings Spansh confirms have Painite hotspots, nearest first, with **Hotspots** (how many Painite hotspots the ring has), **Distance (ly)**, **Arrival (ls)** and **Reserve level**.
5. Click a heading (for example **Distance (ly)**) to sort, select one and press **Copy system**, then paste it into the galaxy map. If nothing came back, set **Where** to 250 ly and search again.

### PRICES: Find Best Price

1. Type a commodity in **Commodity**. Suggestions follow what you type, with what this run refined listed first. Press Down on an empty box to see the list.
2. Choose **I am selling** (the default) or **I am buying**.
3. In **Where**, choose **This system only** (for goods that must be sold inside a Powerplay system), within 10, 25, 50 (the default), 100, 250, 500 or 1,000 ly, or **Anywhere**.
4. In **Search from**, type the system to measure from (it starts as yours; **Here** resets it).
5. Press **Search** (or Enter).

The table lists up to 25 stations Spansh shows paying the most (or selling cheapest). Columns: **Station**, **System**, **Price (cr)**, **Demand** (**Supply** when buying), **Distance (ly)**, **Arrival (ls)**, **Pad** (the largest pad Spansh counts, or `?`) and **Kind** (for example `Orbital Coriolis Starport` or `Ground Planetary Outpost`). Click a heading to sort. Double-click a row to copy its system, or use **Copy system** or **Copy station** in the header.

- **Minimum demand (t)** (Minimum supply when buying) is the least a station must show, a whole number from 1 to 1,000,000. When you are selling it starts at the tons of that commodity in your hold if EDMC knows them, otherwise 1, and follows the commodity you type until you type a figure yourself.
- Fleet carriers are left out, and only markets updated in the last 30 days are asked for.
- The pad size and a market's exact age are not filtered. The largest pad is in the table, and a station you cannot land at can still be listed.

**Worked example.** You have 120 t of Painite in your hold and want to know where to sell it.

1. Tick *Enable Spansh best price finder* in **Settings → WFMT → Mining**, then press **PRICES**.
2. Type `Painite` in **Commodity** (this run's refined commodities are listed first). **I am selling** is already chosen.
3. Leave **Where** on 50 ly. **Minimum demand (t)** starts at the tons in your hold if EDMC knows them, so stations that want only a few tons are not shown.
4. Press **Search**. Read **Price (cr)**, **Demand**, **Pad** and **Arrival (ls)**, and click a heading to sort. A station whose **Pad** is `?` or too small for your ship needs checking before you fly there.
5. Select the row you want and press **Copy system** to paste it into the galaxy map.

### RESERVES: Check Ring Reserve Level

1. Type a system in **System** (it starts as the one you are in).
2. In **Body or ring**, type a body or ring name if you want one. It starts as the ring you are at, if WFMT has tracked one. Empty lists every ringed body in the system.
3. Press **Search**. **Here** fills in the system you are in.

The table gives each ring with its **Body**, **Reserve level**, **Ring type** and a **Laser mining** note, and flags rings that are not Metallic in amber. Select a row and use **Copy ring** or **Copy system**, or double-click a row to copy its system. It uses EDSM and sends only the system name. When EDSM has no ringed body on file for the system (or none with the name you typed) the status line says so.

**Worked example.** You are about to jump to a ringed planet in another system and want to know whether its ring is worth the trip.

1. Tick *Enable EDSM ring reserve lookup* in **Settings → WFMT → Mining**, then press **RESERVES**.
2. Type the system name in **System**. Leave **Body or ring** empty to list every ringed body in the system.
3. Press **Search**. Each row gives the **Reserve level**, the **Ring type** and a **Laser mining** note. A ring that is not Metallic is flagged in amber.
4. If the status line says EDSM has no ringed body on file, nobody has recorded it. Scan the ring yourself when you arrive.

**Automatic lookup.** Once on, the EDSM ring reserve lookup also contacts edsm.net **automatically when you drop into a ring** (once for each ring until EDMC restarts; the answer is kept meanwhile), as well as when you search by hand.

## A typical run

**In space:**

1. Fly to a ring and start mining. The Space Mining page fills in live stats for your run; a core asteroid or a rock rich in your target commodity shows on the page (and on the overlay, if Flight Alerts is on).
2. Done for the day? Open **BOOK** on the Space page: the ring is in the **Space Mining Book** with the tons you mined; add a note or a favorite star so you find it again. **This system** jumps to the rings you have in the system you are in.
3. Want the bigger picture? **DASHBOARD** (Mining History) adds up every run.

**On the surface:**

1. Launch the Rhino and mine. The Surface Mining page fills in live stats.
2. Found a good deposit? Press **Add hotspot** in the **LIVE** window to save the spot.
3. Open **BOOK** on the Surface Mining page to see everything you've saved, including tons mined and an estimate of tons left; **Mark depleted** when one runs out.
4. Next time you're in the system, the Surface Mining Book lists the bodies you've scanned and your hotspots there, and its **From your journals** group lists other bodies your journals show mining on.

## Mining History

**DASHBOARD** opens a window that adds up all the mining in your journals, for the commander you are playing.

- The Space and Surface pages only show the run in progress. This is everything before it as well, including runs made with EDMC closed, across restarts and relogs.
- A **run** is one trip from undocking to docking, the same trip the Space Mining page counts.
- Mining that starts with no undocking before it (you relogged in space) is a run of its own.

### The tabs

- **Overview**: tiles for runs, hours mining, tons refined, tons per hour, credits from sales, credits after limpets, credits per hour and the share of asteroids rated High. Then:
  - **Prospecting**: asteroids by content grade, motherlodes, asteroids cracked, tons per asteroid.
  - **Limpets**: launched by type, prospectors per asteroid, collectors per ton.
  - **Sales**: with what the limpets cost, the credits left after them and the tons mined and not sold yet.
  - Your **best runs** by tons refined.
- **Commodities**: what you refined and sold, with the average price per ton sold and each commodity's share of what you refined.
- **Rings**: where you mined, with runs, tons, asteroids prospected, the share rated High and the last visit.
- **Runs**: every run, newest first, with where, mining time, tons, tons per hour, asteroids prospected, the share rated High, limpets (prospector / collector), what it earned and what is left after the limpets.

Click a heading on the last three tabs to sort. The columns:

| Tab | Columns |
|---|---|
| **Commodities** | Commodity, Refined (t), Sold (t), Earned, Average per ton, Share of refined |
| **Rings** | Ring, System, Runs, Refined (t), Prospected, High, Last visit (most tons first until you sort) |
| **Runs** | Started (UTC), Where, Mining time, Refined (t), t / hour, Prospected, High, Limpets P / C (prospector and collector), Earned, After limpets |

The window's header has **Refresh**, **Rebuild from journals** and **Help** (it explains *Mining time*, *Earned* and *After limpets*). The line under the title says which commander it is and how many runs there are since when. If a commander is not known yet, the status line asks you to log in or play first.

**Worked example: reading the Earned figure.** You mine 100 t of Painite on Monday and dock without selling. On Tuesday you fly to a station that pays more and sell 100 t there.

1. Open **DASHBOARD** and go to the **Runs** tab. Monday's run is listed with 100 in **Refined (t)** and `-` in **After limpets**, because nothing has been sold yet.
2. After the sale, press **Refresh**. The sale is taken off the waiting list, oldest run first, so Monday's run now shows what the 100 t paid.
3. Open the **Overview** tab. The **Sales** block shows the limpets' cost, the credits left after them and how many tons are still waiting to be sold (none, in this case).
4. Treat the figure as takings, not profit: fuel, repairs and ammunition are not taken off.

### Surface Mining History

**DASHBOARD** follows the page you are on. On the Space page it is the ring history above. On the Surface page it opens **Surface Mining History**: the same window for the Rhino.

- Runs are counted from launch to stowing.
- It shows tons refined by the Rhino (and what they sold for).
- The Overview drops the tiles that only make sense in a ship (*asteroids rated High* and *credits after limpets*), and its Prospecting and Limpets blocks give way to **The Rhino's bodies**: how many bodies were mined on, the most tons on one body and the average tons per body.
- Sales are matched to each half by the commodity sold, so a commodity mined both ways counts its sales in both windows.
- A **Bodies** tab takes the place of Rings, with each body's runs, tons refined, tons per hour and last visit. Its **Runs** tab has Started (UTC), Where, Mining time, Refined (t), t / hour and Earned.
- Each window remembers its own size and position.
- A Rhino that was already out when EDMC or the game started is recognized from the SRV's hold in the journal or from `Status.json`. Its tons count as Surface mining, from the first refined ton on.

### Commodity names

Commodity names are suggested as you type in the Find Best Price window, the Add/Edit Hotspot form's *Contains* box and Settings → WFMT → Mining → *Target commodities*.

- A short list appears under the box. Use Down and Up to move, Enter or a click to take one, and Escape to close.
- In the target box the list follows the item you are typing, after the last comma, and taking a name replaces only that item.
- Nothing is fetched.

### How the numbers are worked out

- **Mining time** is from a run's first mining event to its last, not the time undocked, so travel and waiting at the station do not drag the rate down.
  - A mining event is a limpet launched, an asteroid prospected, a ton refined or a rock cracked.
  - Any gap of more than 10 minutes between two mining events is also left out. This is the same definition as the Space Mining page's *Run average*.
  - The two can still differ a little: the page counts from the moment WFMT saw each event, the history from the journal's time stamps, and the page's average appears only after a minute of mining.
  - Runs saved before the 10-minute rule are read from the journals once more, in the background.
- **Asteroids prospected** counts a rock once, the same rule the Space Mining page uses.
  - A rock prospected again within a run with the same composition is not counted again.
  - The game gives asteroids no identity, so two different rocks with the same composition to a tenth of a percent also count as one.
  - A grade WFMT cannot read (a game language it does not know) is counted as unknown, not Low, and is left out of the High and Low shares.
  - Runs saved before this keep the counts they were saved with.
- **Earned** is what selling the tons a run mined paid, at **any station**.
  - WFMT keeps a list of the tons you mined and have not sold yet. Each `MarketSell` takes tons off it, oldest run first, crediting those runs with the tons and the same share of the sale's total.
  - So you can mine, dock without selling and fly to a better-paying station, and the sale still counts for the run.
  - A sale can therefore raise the *Earned* of an older run.
  - Tons you sold beyond what you mined (cargo you bought, or mined while EDMC was closed) earn nothing here.
  - If you sell less than you mined, the rest stays waiting. The Sales block shows how many tons are waiting.
  - It is **not profit**: it does not subtract fuel, repairs or ammunition. The *After limpets* figures take the limpets off, below.
  - WFMT cannot tell mined tons from bought ones of the same commodity. So cargo you jettison, lose or move to a carrier stays on the waiting list, and a later sale of that commodity (bought cargo included) is credited to it.
  - Runs saved before this was added start with nothing waiting. What they sold is as it was counted then, and **Rebuild from journals** counts it all again the new way.
- **After limpets** is *Earned* less what the limpets launched in the run cost.
  - WFMT reads the price from your `BuyDrones` events and charges each limpet launched at the price you last paid for limpets. So a run is charged for the limpets it used, not for the ones you bought and kept.
  - Limpets you sell back (`SellDrones`) are not credited.
  - A limpet launched before WFMT has seen a price (bought before the journals it has, or given to you) is counted as *launched with no price known* and costs nothing here. That run's figure is a little high and is marked `~` in the Runs tab.
  - A run with nothing sold yet shows `-` there, and in the totals its limpets show as a cost until it is sold.
  - Fuel, repairs, ammunition and the Rhino's costs are not taken off.
- A run's **ring** is the ring you dropped into most recently before the run's first mining event. A run that mines more than one ring is listed under the first.

### Reading the journals

- The first time WFMT runs with a known commander, it reads every finished journal once, in the background (not only when the window opens). The window's header and status bar show how far it has got. Years of journals take a minute.
- It keeps the runs in `mining_history.json` beside the plugin, one record per commander. A later start reads only the journals written since.
- The newest journal, which may be growing, is read again about every 15 seconds while the window is open, so a run in progress is included and nothing is counted twice.
- **Refresh** reads now.
- **Rebuild from journals** forgets the saved runs and reads every journal again. Use it if the journals were edited or you think a number is wrong.
- It sends nothing anywhere.

## The live window

Press **LIVE** on either Mining page to open a window made to stay on a second screen, or in a corner of the first.

- It needs no overlay: everything is drawn in the window.
- It redraws once a second, and it remembers its size and place.
- There is one for each page.

### Surface Mining Live

On the left is a **radar** centered on the Rhino with north at the top. It draws:

- range rings,
- the ground you have driven,
- the mining locations you marked (a cross at the center and the circle through the border),
- your saved deposits, with the first letters of their material (a hollow ring for a depleted one),
- a line to the nearest deposit with its distance,
- **rig bands** (see below),
- an arrow for the way the Rhino faces.

Three more things appear when they apply:

- **Drive rings**: orange dashed circles round the nearest marked location, showing where to drive so the scanner covers it.
  - The first is at 2 km from the center, and the rest a little under 4 km further out.
  - The last is on the border or, before a border is marked, as far out as you have driven.
  - They come from the 2 km scanner reach, which is a community estimate, so treat them as a guide.
- **Stop circles**: violet, round the best stops from the Book, using the stop radius in Settings.
- When you have set a **target commodity** in Settings → WFMT → Mining: a bright line to the nearest saved deposit of it, with the nearest deposit of any kind dotted.

Other controls and lines:

- The **Help** button in the window's header explains every mark.
- The **Radar reaches** buttons under the radar set how far it reaches: 50 m, 250 m, 500 m, 1 km or 2 km (2 km is the default, and the choice is remembered). The button for the current reach is highlighted.
- The radar needs your position and the body's size. Until it has them (you are not on or just above the ground) it says `The radar draws when you are on or just above the ground.` instead of a picture.
- On the right are the same lines the panel shows: the run, cargo, refined, the last DSS scan, your saved deposits here, the nearest marked location and the nearest saved deposit.

The controls that act on the ground are in the header:

| Button | What it does |
|---|---|
| **Mark center** | Marks the center of the mining location you are at ([how](#marking-a-mining-location)). |
| **Mark border** | Marks its border, which gives the radius. |
| **Add hotspot** | Saves the deposit where you stand as a hotspot (the same form as in the Surface Mining Book). |
| **Rig placed** | Notes the Rhino's position as a mining rig you have just placed (Ctrl+Alt+Shift+R, or `!wf rig` in Elite's chat, does the same without the window). The journal never says where a rig went, so this is how WFMT learns it. |
| **Clear rigs** | Forgets the rigs now. They are also forgotten when you launch or stow the Rhino, it is destroyed, or you change body; nothing about them is saved. |
| **Save map** | Saves a picture of the location (the ground driven, the border, the drive rings, the stops and the deposits, with a title and a legend) to a PNG file you choose, to post or keep. It holds no commander name or date. |
| **Help** | Explains every mark on the radar. |
| **Import/export** | Imports or exports your saved hotspots. |

The radar draws when you are on or just above the ground and a body's size is known; otherwise it says so. The ground "driven" is where the Rhino has been, not what was scanned, as on the minimap.

The window's subtitle names the body and system you are on. **Save map** needs the same two things; without them its status line says `The map needs your position and the body's size: land, or launch the Rhino, first.` The file name offered is the body's name, a space and `map.png`. The picture is centered on the marked location nearest you (on the Rhino when none is marked).

### Keyboard shortcuts and chat commands

Three of the controls, the radar range and the window itself have shortcuts, so you can use them without taking your hands off the controls. They are set on **Settings → WFMT → General → Shortcuts** and listed in [Shortcuts](shortcuts.md).

| Action | Default key (Windows) | Chat command |
|---|---|---|
| Mark the center (**Mark center**) | Ctrl+Alt+Shift+C | `!wf center` |
| Mark the border (**Mark border**) | Ctrl+Alt+Shift+B | `!wf border` |
| **Rig placed** | Ctrl+Alt+Shift+R | `!wf rig` |
| Radar range (steps 50 m, 250 m, 500 m, 1 km, 2 km, then back to 50 m) | Ctrl+Alt+Shift+Z | `!wf zoom` |
| Open the Live window | Ctrl+Alt+Shift+L | `!wf live` |

Chat commands are off until you tick *Chat commands* on that page. The key combinations are Windows only; on Linux use the chat commands.

### The radar over the game

With one screen you cannot keep the Live window beside the game. **Settings → WFMT → Overlays → Mining → Show the Mining radar over the game** draws the same radar over the game while the Rhino is out, about once a second, and takes it down when you stow the Rhino.

- It needs WFMT's built-in overlay (Windows; **Overlays → Overlay Connection**). EDMCModernOverlay cannot draw a picture, so on Linux, or with that overlay, it does nothing.
- Its background and the green of the ground driven are translucent so the game shows through. Everything else on it is solid.
- The card's size (240 to 560 pixels, 340 by default) and the background opacity (30 to 100 percent, 70 by default) are on the same page, with a **Test radar** button that draws the simulation's pretend Rhino for a few seconds at the size and opacity typed in the boxes (they are saved only when you press OK). It says `Needs WFMT's built-in overlay` when that overlay is not the one in use.
- The card appears only while the Rhino is out and WFMT knows your position and the body's size; it is redrawn about once a second and removed when any of that stops.
- It reaches as far as the Live radar, so the radar range shortcut or chat command, or the Live window's range buttons, change it too.
- Where it sits is **Overlay Placement → Mining radar**. The default is the Bio radar's spot at the left, since both are for a planet's surface.

### Rig bands

The game does not publish how close two mining rigs may be, so WFMT uses the figure you measured: *Too close to place another rig* in Settings → WFMT → Mining.

To measure it: stand at one rig, press Mark center, drive until the game lets you place the next, press Mark border, and enter that distance.

With it set:

- Each rig you note with **Rig placed** gets a band of that radius on the radar: a filled disc while the Rhino is inside it, and a thin outline once the Rhino is clear. So the next rig goes down outside every band.
- The lines on the right say how many rigs are noted and how far the nearest is.
- Each rig is a small numbered square (1 is the first placed).
- Pressing **Rig placed** twice within 5 m of the same rig adds nothing, and WFMT keeps at most 40 rigs on a body.
- With no gap set the radar shows only the squares, and says to set one.
- The rigs, and the radar card over the game, follow the same rule.

### Space Mining Live

- It shows the same lines as the Space Mining page in a larger window, with **Hotspots**, **Prices** and **Reserves** in the header when you have switched those lookups on in Settings.
- It has no radar: the journal does not say where a ring's hotspots are, so there is nothing to place on one.

The panel keeps **BOOK**, **DASHBOARD**, **LIVE** and the lookups. **Mark center**, **Mark border**, **Add hotspot** and **Import/export** are in the live window only.

### Trying the live window without the game

**Settings → WFMT → Mining → Simulation → Surface Live (pretend Rhino)** opens the Surface Live window on made-up data:

- a Rhino driving a ring (about four and a half minutes a lap) round the middle of a made-up mining location 4.5 km in radius, as you would to cover a real one,
- some ground already driven,
- six saved deposits (one depleted, which the radar draws as a hollow ring, and one saved without a position, which is listed but never placed on the radar),
- two marked mining locations (one without a border),
- ore being refined.

The sizes follow real work, so at the default 2 km range you see an arc of the ring and the nearest deposit.

Use it to see that the radar, its range buttons, the lines on the right and **Mark center**, **Mark border** and **Add hotspot** work on your computer. The window says *(simulation)* in its title and *SIMULATION* in its subtitle, and has no **Import/export**.

Nothing it shows is real and nothing you press in it is saved.

- It keeps its own copy of the data in memory, never reads or changes your deposits, marks or runs, and is gone when you close it.
- It opens as its own window, so it never replaces a live window showing your real run.

## Marking a mining location

A surface mining signal is a circle of ground with the deposits scattered inside it, and a few just outside its edge. The journal says a body has mining locations but not where they are or how big, so you mark them yourself:

1. Open **LIVE**. Land and drive to the **middle** of the signal and press **Mark center** (in the live window's header).
   - Pressing it again within 100 m of the same center moves it.
   - Pressing it anywhere else starts another location (up to 12 per body; past that the oldest is dropped).
2. Drive to the **edge** of the signal and press **Mark border** (also in the live window). The radius is the distance from the center, shown on the page (`Border marked: the signal is 1.50 km in radius`). **Mark border** works on the marked center nearest you. If you are within 100 m of that center, it tells you how close you are and asks you to drive to the edge first. With no center marked on the body it asks you to press **Mark center** first. Pressing **Mark border** again somewhere else resets the border.
3. The minimap draws a cross at the center and the circle through the border.

**Nearest marked location** on the page gives:

- the radius,
- which way and how far the center is,
- `edge driven 64%`: the share of the circle's edge within about 2 km of ground you have driven (the same reach the minimap paints).

Drive around the edge, with your scanner overlapping it a little, to bring it to 100%.

**Worked example.** You land near a surface mining signal and want to map it.

1. Press **LIVE** and drive to the middle of the signal. Press **Mark center**. The minimap draws a cross at the center.
2. Drive out to the edge of the signal and press **Mark border**. The page says, for example, `Border marked: the signal is 1.50 km in radius`.
3. Drive around the edge. **Nearest marked location** shows the radius, which way and how far the center is, and `edge driven 64%`. Keep driving, with the scanner overlapping the ground you have already covered, until it reads 100%.
4. Later, the line says `you are inside it, 410 m from the edge` or `you are outside it by 150 m`, so you always know where you stand.
5. If you pressed **Mark border** too close to the center (within 100 m), the page asks you to drive to the edge first. Nothing is changed.

### Am I inside it, and is there room for another rig?

Once the border is marked, the **Nearest marked location** line says `you are inside it, 410 m from the edge` or `you are outside it by 150 m`. The page also gives the **nearest saved deposit** (its material, how far and which way).

The game does not publish how close two rigs may be, so WFMT has no number of its own. You can set your own.

- Set **Too close to place another rig** (Settings → WFMT → Mining, 0 to 2000 m, off at 0).
- The line then also says whether that deposit is closer than your distance ("too close to place another rig") or farther ("far enough").
- To find your number, stand at one rig and press **Mark center**, drive until the game lets you place the next, press **Mark border**, and read the distance.
- This compares against deposits you saved, not rigs you placed: the journal does not report where a rig is.

### What is kept

The marks are per commander and stay for the body. They are your own readings: the game does not report the signal's size, and "driven" is not "scanned" (see below). They are not sent anywhere.

## The Space Mining Book

Press **BOOK** on the Space Mining page. It lists every **ring** your journals show hotspots for or that you mined at. It is built from what the game wrote when you DSS-scanned the ring and mined there, so it fills itself.

- A ring the journals only show as part of a planet you scanned (no hotspots, no mining) is left out, since there are thousands.
- A ring with a note, a favorite star, or added by hand stays.

The window is one table with a detail panel under it. Its columns are **★** (a favorite), **Ring**, **System**, **Hotspots (count per mineral)**, **Class**, **Reserve**, **Tons mined** and **Last mined**. Click a heading to sort. Until you sort, favorites come first, then the ring with the most tons, then the one with the most hotspots. Select a row and the panel under the table repeats the ring's hotspots (up to 30 minerals), class and reserve, `Mined: 620 t in 3 runs, last 2026-10-12` (or `Not mined yet`) and `Added by hand` when you added it yourself. The subtitle gives your commander, how many rings you have and the tons mined in all.

What each ring shows:

- **Hotspots**: each mineral a DSS scan of the ring found, with its hotspot **count**, for example `Painite 3, Platinum 2`. The journal gives the count only, not where the hotspots are or whether two minerals share a spot, so overlaps cannot be shown.
- **Class and Reserve**: the ring class (Icy, Rocky, Metallic, Metal rich) and its reserve level (Pristine, Major, Common, Low, Depleted), from the scan of the planet the ring circles, when the journal has it.
- **Tons mined** and **Last mined**: what you refined in the ring, from your mining runs ([Mining History](#mining-history) reads them).

What you can do:

- **Your note and a favorite star.** Select a ring, type in **Your note** and press **Save note** (or Enter). **Favorite** toggles the star, and starred rings move to the top.
- **Copy system** puts its system on the clipboard for the galaxy map.
- **Find** narrows the list by a ring, a system, a mineral or a note, as you type.
- **Favorites only** shows just the starred ones.
- **Add ring** (top right) adds a ring by hand, for a ring the journals have not shown or one you heard about. The form asks for the ring's name as the game names it (required), the system, the hotspots written like `Painite 3, Platinum 2`, the class (Icy, Rocky, Metallic or Metal rich) and the reserve level (Pristine, Major, Common, Low or Depleted). A hotspot list that does not read that way is refused with a hint. It needs a known commander.
- **Remove** takes away a ring you added by hand. A ring from the journals cannot be removed (it comes back when the journals are read); the status line says so.
- **This system** (a header button) goes to the rings you have in the system you are in, or says `You have not worked this system yet.` It puts the system name in **Find**.
- **Refresh** reads the newest journal again now. The window also keeps itself current while the journals are being read for the first time.
- **Help** explains where the rings come from and what **Remove** does.

If the list is still long, it draws the first 150 rings (favorites first, then the most tons mined) so the window opens and closes quickly. The subtitle says when more match, and **Find** reaches them.

**Worked example.** You want to remember a ring you heard about, and mark a good one you mined.

1. Press **BOOK** on the Space Mining page and press **Add ring**.
2. Enter the ring's name as the game names it, the system, hotspots written as `Painite 3, Platinum 2`, a class (for example Metallic) and a reserve level (for example Pristine), then save. The ring shows `Added by hand`.
3. Select a ring you mined, type `Best Painite, drop in at the north edge` in **Your note**, press **Save note**, then press **Favorite**. The ring moves to the top and its panel shows `Mined: 620 t in 3 runs, last 2026-10-12`.
4. Next time you are in that system, press **This system** to list the rings you have there.

### Reading your journals

- The first time, WFMT reads every journal in the background for ring scans, as Mining History does.
- A notice at the top of the window says how far it has got (for example `Reading your journals for rings and mining (40%)`), and the list grows as it goes. The list is redrawn only when something has changed.
- After that it reads only the new ones.
- Rings, notes and favorites belong to the commander you are playing. Only that commander's journals are read, and another commander's are skipped.
- Nothing is sent anywhere.

## The Surface Mining Book

Press **BOOK** on the Surface Mining page. You don't need to be mining to open it; it lists your saved hotspots either way.

This is the book for the Rhino's surface deposits (the Space Mining Book, above, is the one for rings). It lists:

- the bodies you've scanned in this system,
- every hotspot you've saved,
- a **From your journals** group: every other body whose DSS scan found planetary mining locations (how many) or that you refined on with the Rhino (the tons), read from all your journals.

About the **From your journals** group:

- It shows *which bodies* were worth landing on. The journal does not say where a deposit is, so deposits are still the hotspots you save.
- A body you saved hotspots on also shows the journals' tons.
- The first time, the window's subtitle and status line say the journals are being read, and the list grows as it goes.
- Like everything here, it is built from the commander you are playing, not from other commanders' journals.

**This system** (a header button) goes to the body you have worked in the system you are in (saved hotspots, tons refined or mining locations found), or says `You have not worked this system yet.`

### The three panes

- **Left, Bodies.** Two filters sit on top: a material (`All materials` or any material you have saved) and a number of rigs (`Any rigs`, `1 rigs`, and so on for the counts you have saved). Under them the bodies are grouped: one group for each planet class among the bodies scanned in the system you are in (with how many mining locations the scan found and the tons you refined there), then **Saved, not scanned this session** (saved bodies in this system the journals have not shown a scan of), **Other systems** (saved bodies elsewhere) and **From your journals**. A pill shows how many hotspots you saved on a body. Click a group heading to fold it. With a material filter, a scanned body also stays when your own records show that material on its kind of ground, highest share first, and a line says what percentage of your recorded deposits there are that material. The **From your journals** group is hidden while a filter is on.
- **Middle, Hotspots.** The selected body's saved deposits, grouped by location number (`Location 1`, `Location 2` and so on, with `Unnumbered` last), each with its material, rigs, tons-left estimate, the tons mined and a pill for its Amount. Three tiles give the hotspots saved, the tons mined here and how many are not depleted. A summary line gives the materials saved on the body (`Monazite ×2 · Painite ×1`). Under it come the best stops, and, for a scanned body, the **Your records** table (Material, Share, Recorded, Saved) of what you have found on that kind of ground, which describes your own finds and not what the body holds.
- **Right, the card and the map.** The selected deposit's material, location and rigs, its Density and Amount pills, the tons-left estimate, its depleted status, the tons mined so far, its coordinates and your note, with these buttons: **Mark depleted** (not shown once it is), **Copy coords** (shown when it has a position), **Share line** (when it can be shared), **Edit** and **Delete** (it asks first). Under the card is a zoomable map of the body: the ground you have driven, your deposits (with their signal numbers, a hollow ring for a depleted one), you, and the stop circles. The map needs the body's size, which WFMT has only for a body you have visited this session; otherwise it says so.

The header buttons are **Add hotspot**, **Market research**, **What pays**, **Get body info**, **Paste spot** and **This system**. The window opens on the body you are on when there is one, and refreshes itself when you save or change a hotspot.

You can:

- filter by material or number of rigs,
- see tons mined and an estimate of tons left,
- add a hotspot by hand (**Add hotspot**, top right),
- edit a hotspot or mark it as depleted,
- copy its coordinates,
- view a zoomable map,
- see the best **stops** on a body you are on (below),
- open **Market research** and **What pays** (below),
- press **Get body info** to add the landable bodies EDSM lists for your system (below),
- **Share line** and **Paste spot** (below).

### Adding or editing a hotspot

**Add hotspot** (in the Surface Mining Book and in the Live window, and **Add** in Settings) opens one form; **Edit** opens the same form filled in. It starts with your system, body and position when you are on the ground. The fields:

| Field | What to enter |
|---|---|
| **System**, **Body** | Required. |
| **Latitude**, **Longitude** | Optional, in degrees. Without them the deposit is listed but never placed on the map or radar, and cannot be shared. |
| **Contains** | Required. The commodity the deposit holds, for example Painite. Suggestions follow what you type, the materials you have already saved first. The spelling is made uniform, so `painite` and `Painite` are one material. |
| **Rigs** | Optional, 1 to 7: how many mining rigs the deposit takes. |
| **Signal number** | Optional. Which of the body's mining locations the deposit is in. Hotspots with the same number are listed together. |
| **Amount** | The scanner's readout, `High`, `Medium`, `Low` or `Depleted`. Only these four are offered, because any other text would silently drop out of the tons-left estimate. |
| **Density** | The scanner's readout, `Low`, `Medium` or `High`. |
| **Folder** | A name to file it under. Type a name that does not exist yet to make the folder. |
| **Notes** | Free text. |

**Worked example.** You find a deposit while driving the Rhino and want to save it.

1. Stop at the deposit and press **Add hotspot** in the **LIVE** window. The form opens with your system, body and position filled in.
2. Type `Painite` in **Contains** and set **Rigs** to the number the deposit takes, for example 4.
3. Set **Amount** and **Density** to what the scanner showed, and type a **Signal number** if you know which mining location it is in.
4. Save the form. The deposit appears in the Surface Mining Book and on the radar. If you save again at the same spot (within 100 m) with a corrected material, the existing hotspot is updated instead of a second one being added.

An edit keeps the tons mined and the kind of ground that WFMT recorded. A form with something missing or wrong shows a one-line error and keeps the window open. Saving a new hotspot with a position from **Add hotspot**, within 100 m of one you already have on the same body, updates that one (keeping its position, folder, notes and tons mined unless you supply new ones) instead of adding a second. This lets you correct a material by saving again at the same spot. **Add** in Settings always adds.

### Depleted marks

A hotspot marked depleted is dated, and its card says how long ago.

- Nobody knows when a mined-out deposit refills (the game gives no date and it may differ from system to system). So by default the mark stays until you change it: read the deposit's Amount again and edit the hotspot.
- If you have seen a refill time, set it in **Settings → WFMT → Mining → Assume a depleted deposit has refilled after (days)** (0 = unknown, up to 90 days). With a time set, the mark comes off that long after it was set, and the hotspot has no Amount until you read it again.
- If you then press **Mark depleted** on it and have not refined anything there since, WFMT takes that as a look at a deposit that is still empty. It keeps the first date and looks again 7 days later (`Still depleted at 15 d; look again in 7 d`).
- Tons refined since make it a fresh depletion.

**Worked example.** You have mined a deposit empty.

1. Stand at it. The Book marks it `you are here` and selects it, so open **BOOK** and press **Mark depleted**.
2. The card shows the date and how long ago. The mark stays until you change it, unless you set a refill time in **Settings → WFMT → Mining**.
3. Come back after a few days, read the Amount again, and press **Edit** to set the new reading if it has refilled.
4. If a refill time you set has taken the mark off and you press **Mark depleted** again having refined nothing there since, WFMT keeps the first date and looks again 7 days later.

### Stops

Rigs sit around the Rhino, so deposits close together can be worked from one place.

- For the body you are on, the Book takes the saved deposit with the most rigs and every other one within the **stop radius** of it as one stop. The stop radius is in Settings → WFMT → Mining (500 to 2500 m, default 1250 m).
- The best three are listed above the hotspots, with the tons left added up. They are circled on the map and tagged `stop 1` to `stop 3` on each row.
- The best three are led by a deposit of 5 or more rigs (4 or more if the body has none).
- Deposits that are depleted, or have no position or rig count, are left out.
- Stops need the body's radius, which WFMT only has for a body you have visited this session. A body you are not on shows none.

### Market research

The **Market research** button asks which markets in the system buy the commodities you could mine there.

- It works from your own records only: deposits you saved in that system, what you have recorded on the same kind of ground as its scanned bodies, and anything you type into *Also check*.
- For each commodity it lists the markets that buy it, best price first, with demand, how old the prices are, the distance from the star and the pad size.
- A system where you have recorded nothing suggests nothing until you add a commodity or save a hotspot.
- It is off until you tick *Enable Spansh best price finder* (Settings → WFMT → Mining).
- It leaves out fleet carriers and markets not updated in 30 days.
- It sends only the system's name.
- Prices are the last ones players uploaded.

### Get body info

The Book's list of bodies comes from the `Scan` events in your journals. So a body you scanned in a session whose journal you no longer have is missing from it, and its ground type is unknown to your rates.

**Get body info** asks EDSM, and Spansh when WFMT knows the system's id (from your latest jump or login), for the bodies of the system you are in.

- It adds each landable planet the journals did not give: its name, kind, volcanism and size.
- From Spansh, it adds how many mining locations a body carries.
- Then it tells you how many of each it added.
- A body, size or count your journals already gave is never replaced.
- The services only have systems that players' tools uploaded, and neither says where a mining location is, so marks stay from your own driving.

Privacy and settings:

- It sends only the system's name to EDSM and its id to Spansh (one request each, through the same courtesy rules as other Spansh calls).
- It is off until you tick *Enable body lookup* in Settings → WFMT → Mining.

What is remembered:

- What it found is remembered for each commander (the newest 60 systems, in `mining_body_cache.json`), so coming back to the system or restarting EDMC brings the bodies back without another request.
- The bodies the System targets cards already know for a system (saved between sessions, and rebuilt from your journals) are added to the list on arrival as well.
- The mining-location count of a body also fills in by itself when you FSS-scan it (the game writes it without flying there), and a detailed surface scan replaces that.
- A body's size is also read from `Status.json` whenever you are near the ground, so the radar, **Mark center** and **Mark border** work on a body that was never scanned without this.

### What pays

The **What pays** button ranks the commodities you could mine by the best price Spansh shows for them.

**What it prices**, one after another (at most 16 in all):

- the target commodity from Settings,
- every material in your saved deposits (in any system),
- what you have recorded on the same kind of ground as the bodies scanned in the system you are in,
- any commodities you type into *Also check*.

**How it asks.** For each commodity it asks Spansh for the station that pays most.

- Within the distance you choose (10 ly to anywhere, or only the system in the box) of the system in *Near* (your own by default).
- Among stations updated in the last 30 days.
- Fleet carriers are left out. It asks Spansh for stations only (orbital and ground ports, outposts, settlements, asteroid bases and megaships), and drops any carrier that still comes back.
- A station must show demand of at least the tons of that commodity in your hold when EDMC knows them, otherwise at least 1 t, so a price for a few tons does not top the list.
- Pad size is not filtered (the table shows it), and neither is a market's age within the 30 days.

**The table.**

- It fills in as the answers arrive and is ordered best price first when it finishes.
- Columns: the commodity, its best price, the station, system, distance, demand, arrival distance, landing pads and *why it is listed*.
- Click a heading to sort. **Copy report** copies the ranking. **Help** explains the columns.
- A commodity no station pays for shows *No station found*.

**Good to know.**

- It sends only a commodity's name, the system's name, the distance and that minimum.
- It uses the same *Enable Spansh best price finder* switch (Settings → WFMT → Mining).
- It ranks what pays, not what a body holds. The game does not say which commodities a body carries, so a commodity is listed because of your own records and never because of the kind of body.

### Sharing a deposit

- **Share line** on a hotspot's card copies one line of text (`WFMT-SPOT1:...`) you can post in Discord.
- In another Surface Mining Book, **Paste spot** (top of the window) reads it from the clipboard, checks it and asks before adding it to the commander you are playing.
- The line holds the system, body, material, rigs, location number, position, Amount, Density and kind of ground. It never holds a commander name, notes, folder, tons mined or dates.
- A line that was cut short or changed is refused, and so is a deposit within 100 m of one you already have on that body.
- A hotspot with no position cannot be shared.

**Worked example.** A friend wants the Painite deposit you found.

1. In your Surface Mining Book, select the hotspot and press **Share line**. The line (`WFMT-SPOT1:...`) is on your clipboard.
2. Paste it into Discord.
3. Your friend copies the line, opens their Surface Mining Book and presses **Paste spot**. WFMT checks it and asks before adding it to their commander.
4. If the line was cut short, or they already have a deposit within 100 m on that body, it is refused.

### You are here

With the Rhino on the body, the deposit within 175 m of it is marked `you are here` and selected, so **Mark depleted** is one click. It is worked out when the Book is opened or refreshed, not while you drive.

### Per commander

**Your hotspots, tons mined, depleted marks and the ground your Rhino has driven over belong to the commander you are playing.**

- Switching commander switches the Surface Mining Book and the coverage map. One commander never sees or changes another's.
- To give a hotspot list to another commander, use **Import/export** (in the live window) to export it as the first commander and import it as the second.

For a scanned body it also shows what *you've* found so far on that kind of body. That starts empty and fills in as you save hotspots. It describes your own finds, not what a body actually holds.

## Mining alerts

Mining alerts are cards on the Flight Alerts overlay, so they need an overlay running and Flight Alerts switched on. They are set on **Settings → WFMT → Overlays → Flight Alerts**: tick *Enable Flight Alerts* (off by default), make sure *Mining alerts* is ticked (it is by default), then choose the limpet number and the hold percentage. Details are in [Always on](always-on.md#flight-alerts).

| Card | When it appears | Settings |
|---|---|---|
| `Core asteroid` and the core mineral (green) | A prospected rock names a core mineral. It stays 30 seconds. | None; a core asteroid is always flagged. |
| `Rich rock: Painite`, `38% of the rock` (green) | A rock holds at least a target commodity's percentage. One card for each target it holds enough of (the richest three at most), 30 seconds each. No card when the rock has less than a quarter of itself left. | *Target commodities* in Settings → WFMT → Mining |
| `Low on limpets`, `3 aboard` (amber) | The limpets aboard are at or under your number (5 by default, 0 to 99). | *Warn when the limpets aboard are at or under* |
| `Hold nearly full`, `190 of 200 t` (amber) | The hold is at or over your percentage (95 by default, 50 to 100) of the capacity from your last loadout. | *Warn when the hold is at or over* |

- A rock prospected again with the same composition does not raise a second card or sound. A new run (the next undocking) forgets the rocks seen.
- The limpet and hold cards show only while you are mining, meaning a prospector, refinery, limpet or cracking event in the last half hour, so a hold that is full for another reason never nags.
- The low-limpet card applies only when a prospector or collector limpet controller is in your last loadout or limpets have been seen aboard, and never while a Rhino is out.
- The hold figure comes from `Status.json` about once a second when you are in the ship, and from the `Cargo` event otherwise.
- *Play a sound when an alert starts* on the same page plays a sound for a new alert.

**Worked example.** You want a warning before your hold fills and when limpets run low.

1. Open **Settings → WFMT → Overlays → Flight Alerts**, tick *Enable Flight Alerts* and keep *Mining alerts* ticked.
2. Leave the hold percentage at 95 and the limpet number at 5, or change them.
3. Mine with a 200 t hold. When you reach 190 t, a `Hold nearly full` card reading `190 of 200 t` appears in amber. When you are down to 3 limpets, a `Low on limpets` card reading `3 aboard` appears.
4. If you also set Painite as a target, a prospected rock with enough of it raises a green `Rich rock: Painite` card for 30 seconds.

## What the game does and doesn't tell us, and how to work around it

WFMT, like every third-party tool, only knows what Elite Dangerous writes to its journal files. It adds what Spansh and EDSM report and works around the rest. Where it can't be sure, WFMT says so rather than guess quietly. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| What you might expect | What the game gives | What to do |
|---|---|---|
| Ring and deposit amounts read for you | Amount and Density are not given to WFMT. They are **typed in by hand**. | Check the figure you type. A wrong reading gives a wrong range. |
| When a mined-out deposit refills | Nothing in the journal says, and community testing has not found out: deposits have been seen still empty after about a week, and no refill time is known. WFMT shows it as unknown and leaves the mark. | Read the Amount again at the deposit and edit the hotspot, or set a time to assume in Settings → WFMT → Mining if you have seen one. |
| Which commodities a body carries | The game does not say, and community testing treats planet class as a screening hint only. Market research and What pays use your own records for this. | Save hotspots as you find them, or type commodities into *Also check*. |
| Exact tons left in a deposit | The deposit figures are measurements from a handful of deposits, so the ranges are wide. | Treat "tons left" as a guide, not a count. |
| A map of everywhere you have mined | Coverage means ground the Rhino has **driven over**, not ground it has scanned. | Use the minimap to see where you have been, not what is left. |
| A mining history from before WFMT first ran, or from journals you deleted | The history is built from the journal files that exist. | Nothing can bring back a deleted journal; WFMT keeps the runs it has already read. |
| The ship's hold while the Rhino is out | `Status.json` carries a `Cargo` figure, but what it counts while an SRV is out could not be checked (the file keeps no history), so WFMT does not use it then, or on foot. | The Ship hold line shows the last `Cargo` event's figure until you are back in the ship. |
| An exact count of limpets aboard | The exact count comes from EDMC's cargo once it has told WFMT; until then "on board" is an estimate (bought less launched, marked `~`). The low-limpet alert applies only when a prospector or collector limpet controller is in your last loadout or limpets have been seen aboard, and never while a Rhino is out. | Check your cargo for the real number. |
| Every commodity's best mining method | The method hints are community-sourced and need occasional updating. | If a hint looks wrong, trust the game and open an issue. |
| Where a ring's hotspots are, or whether two minerals share one | A DSS scan gives each mineral's hotspot **count** only. | The Space Mining Book lists counts. Fly the ring and note what you find in **Your note**. |
| Where a surface mining location is and how big it is | The journal says a body has mining locations, not where or how large. | Mark the center and border yourself with **Mark center** and **Mark border** ([marking a location](#marking-a-mining-location)). |
| Where a mining rig went, and how close two rigs may be | The journal does not say where you put a rig, and the game does not publish a minimum gap. | Press **Rig placed** after each rig and enter the gap you measured in Settings. |
| How far the Rhino's scanner reaches | No figure from Frontier. WFMT uses 2 km, a community estimate, for the driven-ground map, the edge percentage and the drive rings. | Treat those as guides. |
| Ring reserve and hotspot lookups to always answer | They only know what players have uploaded to EDSM or Spansh. | No answer can mean nobody has recorded it. Scan the ring yourself, then save the hotspot with **Add hotspot** |

## Settings

**Settings → WFMT → Mining**

The in-game Mining displays are set on **Settings → WFMT → Overlays → Mining** (see below).

**Checkboxes.** The first three are on by default. The rest are off.

- *Show session totals*, *Show the cargo bar* and *Show prospector hints* (on by default). See [What each page shows](#what-each-page-shows) for the lines each one controls.
- *Enable Spansh nearby hotspot finder* (Space Mining page): shows **HOTSPOTS**
- *Enable Spansh best price finder and Market research in the Surface Mining Book*: shows **PRICES** and turns on **Market research** and **What pays**.
- *Enable EDSM ring reserve lookup* (Space Mining page): shows **RESERVES** and looks up each ring you drop into automatically.
- *Enable body lookup*: turns on **Get body info** in the Surface Mining Book (asks edsm.net and spansh.co.uk for the bodies of your system, sending only its name or id).
- *Show coverage minimap* (Surface Mining page): a small map of ground the Rhino has driven over on the current body, redrawn once a second while the Rhino is deployed.
- *Archive completed mining runs*: writes a JSON file per run to `mining_sessions/`. A trip with nothing in it writes nothing.

**Other settings.**

- *Target commodities* and a percentage (Space Mining page). See below.
- *Assume a depleted deposit has refilled after (days)*: 0 (the default) means unknown and marks stay. A number from 1 to 90 takes a Depleted mark off that long after it was set.
- *Too close to place another rig (m, 0 = off)*: your own distance for the Surface Mining page's "far enough" note and the radar's rig bands. 0 turns it off (0 to 2000 m, steps of 5).
- *Stop radius in the Surface Mining Book (m)*: how close deposits must be to the lead deposit to share a stop (500 to 2500 m in steps of 250, default 1250).
- **Simulation: Surface Live (pretend Rhino)**: opens the Live window on made-up data (see [Trying the live window without the game](#trying-the-live-window-without-the-game)).

**Known Surface Hotspots.** At the bottom of the same page is a list of every hotspot you have saved, grouped by folder (`Unfiled` last), one line each with the system, body, material, rigs, signal number and tons-left estimate. Select a line and use **Add**, **Edit**, **Delete** (a folder heading cannot be edited or deleted), **Import...** and **Export...**. These open the same form and the same import and export as the Surface Mining Book and the Live window's **Import/export** button. **Import...** reads a hotspot file exported by WFMT and asks whether to merge with your list (Yes) or replace it (No). **Export...** writes your saved hotspots to a JSON file you choose. A list belongs to the commander you are playing, and an export holds only that commander's list.

**Settings → WFMT → Overlays → Mining**

- *Enable HUD Overlay*: sends the hold, *Refining now*, *Run average*, *Hold full in* and *Limpets remaining* lines to the overlay. It follows the three display switches above. On the Surface page it sends the SRV and ship holds and the rates, and it stops while the ship is in supercruise. Where it sits is **Overlay Placement → Mining stats**. **Test HUD** draws a sample panel for a few seconds and says whether the overlay was reachable (it works even while the HUD is off).
- *Show the Mining radar over the game while the Rhino is out*, with its **Size (pixels)**, **Background opacity (%)** and **Test radar** (see [The radar over the game](#the-radar-over-the-game)).

**The arrow to the nearest known hotspot** is the **Surface Compass** (Settings → WFMT → Overlays → Surface Compass, and the Compass section in [Exploration](exploration.md#compass)). It points at the nearest hotspot by default, and also works from any mode.

### Target commodities

Type a commodity as the game names it (for example Painite) and the least share of a rock that makes it worth cracking.

- You can type several, separated by commas or semicolons, each with its own percentage after the name: `Painite 30, Platinum 25, Void Opals`.
- A name with no number uses the percentage beside the box (20 by default, 1 to 100).
- Up to 8 are used. A line under the box says what is wrong, such as a percentage outside 1 to 100.
- The commodity may be typed in any spelling (Void Opals or Void Opal, Low Temperature Diamonds or Low Temp. Diamonds).
- Empty means none.
- A core asteroid is always flagged.

What it does:

- The page marks a rock at or over one of them and names which (`target: Painite`).
- Flight Alerts can put a card on the overlay for each, `Rich rock: Painite`.
- The radar and What pays use the first one.
- A rich-rock card is not raised for a rock with less than a quarter of itself left.
- A rock prospected again with the same composition does not raise a second card or sound.
- Each target a rock holds enough of raises its own card once.

**Worked example.** You type `Painite 30, Platinum 25, Void Opals` in *Target commodities* with the percentage box left at 20.

- A rock with Painite 34% and Platinum 12% is marked `target: Painite`: Painite is over its 30, Platinum is under its 25.
- A rock with Void Opals 22% counts as a target, because a name with no number uses the 20 beside the box.
- The radar and What pays use the first one, Painite.

More detail: [Mining specification](../MINING_TECH_SPEC.md).
