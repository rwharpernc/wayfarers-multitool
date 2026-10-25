# Mining

Mining mode tracks two kinds of mining, keeps a book for each, and adds up everything you have mined:

- **Space Mining**, in your ship, with the **Space Mining Book**: every ring your journals have shown, with its hotspots, tons mined and your notes.
- **Surface Mining**, in the Rhino SRV, with the **Surface Mining Book**: your catalog of deposits, and the bodies your journals show mining on.
- **Mining History**: every run in your journals, added up.

Use the **◀** and **▶** buttons at the top of the panel to switch between the two pages. Each page shows live stats
for your current run, and its **BOOK** button opens the book for that page.

**On this page:** [What each page shows](#what-each-page-shows) · [The buttons](#the-buttons) · [A typical run](#a-typical-run) · [Mining History](#mining-history) · [The live window](#the-live-window) · [The Space Mining Book](#the-space-mining-book) · [The Surface Mining Book](#the-surface-mining-book) · [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it) · [Settings](#settings)

**Where this comes from:**

- The journal records what you prospect, refine and collect.
- It does not record a ring's deposit amounts or density, which you type in.
- The hotspot catalog is your own.
- Ring reserve and hotspot lookups use what players have uploaded to EDSM and Spansh.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## What each page shows

Lines come and go with the settings listed at the end of this page.

### Space Mining

In your ship, from undocking.

- **Hold**, for example `Hold: 64 of 200 t`.
  - The tons your ship carries, read live from `Status.json` (the `Cargo` event is used until it has said), and its capacity from your last loadout.
  - The same line is on the HUD overlay.
  - The ring you are at is shown with its reserve level, once *Enable EDSM ring reserve lookup* is ticked and EDSM knows it.
- **Asteroids prospected**, with how many of each content grade, and the **materials seen** in them. A rock prospected again with the same composition is counted once, and the page says how many repeats it ignored.
- **Last rock**: the latest rock's materials with their percentages and its grade, for example `Last rock: Painite 34%, Platinum 12% (High), target: Painite`.
  - A **core asteroid** (the game names a core mineral in the prospector's result) adds `core: Painite`, and **Core asteroids found** counts them for the run.
  - `target:` names each target commodity the rock holds at least its percentage of (Settings → WFMT → Mining; several can be set).
- **Mission needs**: for each commodity your active mining missions still ask for, how many tons you already hold, for example `Mission needs: Painite 50 of 120 t held (2 missions)`. It is worked out the way the Missions window does it and shows even before you start mining.
- **Asteroids cracked** (core mining).
- **Limpets launched** by type, with the count still on board. The count is exact once EDMC has told WFMT the cargo. Otherwise it is bought less launched, marked with ~. The HUD overlay's *Limpets remaining* line shows the same number.
- **Refined**, by commodity (with the mining method that usually suits it, when prospector hints are on). Then:
  - **Refining now** (for example `Refining now: 840 t/h`): the tons refined in the last minute, scaled to an hour, falling to 0 within a minute of a lull.
  - **Run average** (for example `Run average: 720 t/h over 41 min`): the tons refined this run over its mining time, shown once the run has a minute of it.
  - One refined unit in the journal is one ton.
  - The mining time runs from the run's first to its last mining event (a limpet launched, an asteroid prospected, a ton refined or a rock cracked). It leaves out any gap of more than 10 minutes between two of them, so a long flight or a break does not drag the average down.
  - The HUD overlay carries the same two lines, and Mining History's *Mining time* and *t / hour* use the same definition.
- **Hold full in** (for example `Hold full in about 14 min`): the room left in your hold over your **Run average**.
  - Before there is an average (the first minute), it uses *Refining now*.
  - It shows with the other refining lines when the ship's capacity is known and something is being refined.
  - It says `Hold is full` once it is.
  - It is a guide: a laser works in bursts, and the rate moves with the rocks.
  - The HUD overlay and the live window carry it too.
- **What the station pays**, when you are docked and have opened its commodities market (for example `Painite here: 521,400 cr/t, 8% above the galactic average (482,000)`).
  - A line for each commodity this run refined that the station buys, the most tons first, up to three.
  - It compares the station's price with the galactic average the game lists beside it, so you can tell whether to sell here or fly on.
  - It reads the game's own `Market.json` on your computer and asks nothing online.
  - A good deal is a good one only until you have looked at the next station.
  - A station that lists a price for something it does not buy (no demand) is skipped.
  - The lines go when you undock.
- A **Paused** note while you are in supercruise.

### Surface Mining

In the Rhino SRV.

- Whether the Rhino is deployed or stowed, its hold (`SRV hold: 40 of 72 t`) and your ship's (`Ship hold: 64 of 200 t`, from the last `Cargo` event while the Rhino is out).
- **Refined**, **Refining now** and the **Run average**. They are worded as on the Space page. *Refining now* shows only while the Rhino is out.
- **SRV hold full in**: the same estimate for the Rhino's 72 t hold, only while it is out.
- What was **Transferred to ship** and the **Raw materials** picked up.
- The **Last DSS scan**: how many mining locations the scan found on which body.
- **Known hotspots here**: the ones you have saved on the body you are on.
- The **coverage minimap** (if ticked in Settings): ground the Rhino has driven over, with your position, your saved hotspots and the mining locations you marked with **CTR** and **BRD**. In your ship it appears only close to the ground (under about 2 km).
- **Nearest marked location**: the size of the mining location you marked nearest you, which way its center is and how much of its edge you have driven (see [Marking a mining location](#marking-a-mining-location)).

Both pages carry the buttons below, and the Surface Mining Book and the coverage map are per commander.

## The buttons

The buttons sit side by side in one row, in this order. Which ones you see depends on the page and on your
Settings. Hover for the full name.

| Button | What it does | Shown when |
|---|---|---|
| **BOOK** | Opens the book for the page you are on: the **Space Mining Book** (your rings) on the Space Mining page, the **Surface Mining Book** (Rhino deposits) on the Surface Mining page. | Always |
| **DASHBOARD** (Mining History) | Opens every mining run found in your journals, added up (see below). | Always |
| **LIVE** | Opens the live window for the page you are on: a radar and the controls on the Surface page, the live numbers on the Space page. Meant for a second screen ([the live window](#the-live-window)). | Always |
| **H.S.** (find nearby hotspots) | Opens the Find Nearby Hotspots window (see below). | Space Mining page, once *Enable Spansh nearby hotspot finder* is ticked |
| **PRICE** (find best price) | Opens the Find Best Price window (see below). | Once *Enable Spansh best price finder* is ticked (the same switch also turns on Market research in the Surface Mining Book) |
| **RES** (check ring reserve level) | Opens the Check Ring Reserve Level window (see below). | Space Mining page, once *Enable EDSM ring reserve lookup* is ticked |

The three online lookups are **off until you turn them on in Settings**. See [what goes on the internet](internet-and-privacy.md).

### H.S.: Find Nearby Hotspots

1. Type a material.
2. Choose how far to look and the system to search from.
3. Press **Search**.

The table lists the nearest rings Spansh confirms have a hotspot for it: ring, body, system, hotspots, distance, distance from the star and reserve level. Click a heading to sort. Double-click a row, or use **Copy system**, **Copy body** or **Copy ring**.

### PRICE: Find Best Price

1. Type a commodity.
2. Choose selling or buying.
3. Choose how far to look (or **This system only**, for goods that must be sold inside a Powerplay system) and the system to search from.
4. Press **Search**.

The table lists the stations Spansh shows paying the most (or selling cheapest): price, demand or supply, distance, distance from the star, largest pad and kind of station. Click a heading to sort. Double-click a row, or use **Copy system** or **Copy station**.

- **Minimum demand (t)** (Minimum supply when buying) is the least a station must show. When you are selling it starts at the tons of that commodity in your hold if EDMC knows them, otherwise 1. You can type another whole number.
- Fleet carriers are left out, and only markets updated in the last 30 days are asked for.
- The pad size and a market's exact age are not filtered. The largest pad is in the table, and a station you cannot land at can still be listed.

### RES: Check Ring Reserve Level

1. Type a system.
2. If you want one body, type a body or ring name. Empty lists every ringed body in the system.
3. Press **Search**.

The table gives each ring with its body, the reserve level and the ring type, and flags rings that are not Metallic in amber. It uses EDSM.

**Automatic lookup.** Once on, the EDSM ring reserve lookup also contacts edsm.net **automatically every time you drop into a ring**, as well as when you search by hand.

## A typical run

**In space:**

1. Fly to a ring and start mining. The Space Mining page fills in live stats for your run; a core asteroid or a rock rich in your target commodity shows on the page (and on the overlay, if Flight Alerts is on).
2. Done for the day? Open **BOOK** on the Space page: the ring is in the **Space Mining Book** with the tons you mined; add a note or a favorite star so you find it again. **This system** jumps to the rings you have in the system you are in.
3. Want the bigger picture? **DASHBOARD** (Mining History) adds up every run.

**On the surface:**

1. Launch the Rhino and mine. The Surface Mining page fills in live stats.
2. Found a good deposit? Press **+H.S.** in the **LIVE** window to save the spot.
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

Click a heading on the last three tabs to sort.

### Surface Mining History

**DASHBOARD** follows the page you are on. On the Space page it is the ring history above. On the Surface page it opens **Surface Mining History**: the same window for the Rhino.

- Runs are counted from launch to stowing.
- It shows tons refined by the Rhino (and what they sold for).
- A **Bodies** tab takes the place of Rings, with each body's runs, tons and last visit.
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

- The first time it opens, WFMT reads every finished journal once, in the background. The header and status bar show how far it has got. Years of journals take a minute.
- It keeps the runs in `mining_history.json` beside the plugin, one record per commander. A later start reads only the journals written since.
- The newest journal, which may be growing, is read again every few seconds while the window is open, so a run in progress is included and nothing is counted twice.
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
- The buttons under the radar set how far it reaches, from 50 m to 2 km (the choice is remembered).
- On the right are the same lines the panel shows: the run, cargo, refined, the last DSS scan, your saved deposits here, the nearest marked location and the nearest saved deposit.

The controls that act on the ground are in the header:

| Button | What it does |
|---|---|
| **CTR** | Marks the center of the mining location you are at ([how](#marking-a-mining-location)). |
| **BRD** | Marks its border, which gives the radius. |
| **+H.S.** | Saves the deposit where you stand as a hotspot. |
| **Rig placed** | Notes the Rhino's position as a mining rig you have just placed (Ctrl+Alt+Shift+R, or `!wf rig` in Elite's chat, does the same without the window). The journal never says where a rig went, so this is how WFMT learns it. |
| **Clear rigs** | Forgets the rigs now. They are also forgotten when you launch or stow the Rhino, it is destroyed, or you change body; nothing about them is saved. |
| **Save map** | Saves a picture of the location (the ground driven, the border, the drive rings, the stops and the deposits, with a title and a legend) to a PNG file you choose, to post or keep. It holds no commander name or date. |
| **Help** | Explains every mark on the radar. |
| **I/E** | Imports or exports your saved hotspots. |

The radar draws when you are on or just above the ground and a body's size is known; otherwise it says so. The ground "driven" is where the Rhino has been, not what was scanned, as on the minimap.

### The radar over the game

With one screen you cannot keep the Live window beside the game. **Settings → WFMT → Overlays → Mining → Show the Mining radar over the game** draws the same radar over the game while the Rhino is out, about once a second, and takes it down when you stow the Rhino.

- It needs WFMT's built-in overlay (Windows; **Overlays → Overlay Connection**). EDMCModernOverlay cannot draw a picture, so on Linux, or with that overlay, it does nothing.
- Its background and the green of the ground driven are translucent so the game shows through. Everything else on it is solid.
- The card's size (240 to 560 pixels) and the background opacity (30 to 100 percent) are on the same page, with a **Test radar** button that draws the simulation's pretend Rhino for a few seconds.
- It reaches as far as the Live radar, so the radar range shortcut or chat command, or the Live window's range buttons, change it too.
- Where it sits is **Overlay Placement → Mining radar**. The default is the Bio radar's spot at the left, since both are for a planet's surface.

### Rig bands

The game does not publish how close two mining rigs may be, so WFMT uses the figure you measured: *Too close to place another rig* in Settings → WFMT → Mining.

To measure it: stand at one rig, press CTR, drive until the game lets you place the next, press BRD, and enter that distance.

With it set:

- Each rig you note with **Rig placed** gets a band of that radius on the radar: a filled disc while the Rhino is inside it, and a thin outline once the Rhino is clear. So the next rig goes down outside every band.
- The lines on the right say how many rigs are noted and how far the nearest is.
- Each rig is a small numbered square (1 is the first placed).
- With no gap set the radar shows only the squares, and says to set one.
- The rigs, and the radar card over the game, follow the same rule.

### Space Mining Live

- It shows the same lines as the Space Mining page in a larger window, with **H.S.**, **PRICE** and **RES** in the header when you have switched those lookups on in Settings.
- It has no radar: the journal does not say where a ring's hotspots are, so there is nothing to place on one.

The panel keeps **BOOK**, **DASHBOARD**, **LIVE** and the lookups. **CTR**, **BRD**, **+H.S.** and **I/E** are in the live window only.

### Trying the live window without the game

**Settings → WFMT → Mining → Simulation → Surface Live (pretend Rhino)** opens the Surface Live window on made-up data:

- a Rhino driving a ring (about four and a half minutes a lap) round the middle of a made-up mining location 4.5 km in radius, as you would to cover a real one,
- some ground already driven,
- six saved deposits (one depleted, which the radar draws as a hollow ring, and one saved without a position, which is listed but never placed on the radar),
- two marked mining locations (one without a border),
- ore being refined.

The sizes follow real work, so at the default 2 km range you see an arc of the ring and the nearest deposit.

Use it to see that the radar, its range buttons, the lines on the right and **CTR**, **BRD** and **+H.S.** work on your computer. The window says *(simulation)* in its title and *SIMULATION* in its subtitle, and has no **I/E**.

Nothing it shows is real and nothing you press in it is saved.

- It keeps its own copy of the data in memory, never reads or changes your deposits, marks or runs, and is gone when you close it.
- It opens as its own window, so it never replaces a live window showing your real run.

## Marking a mining location

A surface mining signal is a circle of ground with the deposits scattered inside it, and a few just outside its edge. The journal says a body has mining locations but not where they are or how big, so you mark them yourself:

1. Open **LIVE**. Land and drive to the **middle** of the signal and press **CTR** (in the live window's header).
   - Pressing it again within 100 m of the same center moves it.
   - Pressing it anywhere else starts another location (up to 12 per body).
2. Drive to the **edge** of the signal and press **BRD** (also in the live window). The radius is the distance from the center, shown on the page (`Border marked: the signal is 1.50 km in radius`). **BRD** works on the marked center nearest you.
3. The minimap draws a cross at the center and the circle through the border.

**Nearest marked location** on the page gives:

- the radius,
- which way and how far the center is,
- `edge driven 64%`: the share of the circle's edge within about 2 km of ground you have driven (the same reach the minimap paints).

Drive around the edge, with your scanner overlapping it a little, to bring it to 100%.

### Am I inside it, and is there room for another rig?

Once the border is marked, the **Nearest marked location** line says `you are inside it, 410 m from the edge` or `you are outside it by 150 m`. The page also gives the **nearest saved deposit** (its material, how far and which way).

The game does not publish how close two rigs may be, so WFMT has no number of its own. You can set your own.

- Set **Too close to place another rig** (Settings → WFMT → Mining, 0 to 2000 m, off at 0).
- The line then also says whether that deposit is closer than your distance ("too close to place another rig") or farther ("far enough").
- To find your number, stand at one rig and press **CTR**, drive until the game lets you place the next, press **BRD**, and read the distance.
- This compares against deposits you saved, not rigs you placed: the journal does not report where a rig is.

### What is kept

The marks are per commander and stay for the body. They are your own readings: the game does not report the signal's size, and "driven" is not "scanned" (see below). They are not sent anywhere.

## The Space Mining Book

Press **BOOK** on the Space Mining page. It lists every **ring** your journals show hotspots for or that you mined at. It is built from what the game wrote when you DSS-scanned the ring and mined there, so it fills itself.

- A ring the journals only show as part of a planet you scanned (no hotspots, no mining) is left out, since there are thousands.
- A ring with a note, a favorite star, or added by hand stays.

What each ring shows:

- **Hotspots**: each mineral a DSS scan of the ring found, with its hotspot **count**, for example `Painite 3, Platinum 2`. The journal gives the count only, not where the hotspots are or whether two minerals share a spot, so overlaps cannot be shown.
- **Class and Reserve**: the ring class (Icy, Rocky, Metallic, Metal rich) and its reserve level (Pristine, Major, Common, Low, Depleted), from the scan of the planet the ring circles, when the journal has it.
- **Tons mined** and **Last mined**: what you refined in the ring, from your mining runs ([Mining History](#mining-history) reads them).

What you can do:

- **Your note and a favorite star.** Type a note and press **Save note**. **Favorite** moves a ring to the top.
- **Copy system** puts its system on the clipboard for the galaxy map.
- **Find** narrows the list by a ring, a system, a mineral or a note.
- **Favorites only** shows just the starred ones.
- **Add ring** adds a ring by hand (a ring the journals have not shown, or one you heard about): its name, system, hotspots like `Painite 3, Platinum 2`, class and reserve level. A ring you added can be removed. One from the journals comes back when the journals are read.
- **This system** (a header button) goes to the rings you have in the system you are in, or says `You have not worked this system yet.` It puts the system name in **Find**.

If the list is still long, it draws the first 150 rings (favorites first, then the most tons mined) so the window opens and closes quickly. The subtitle says when more match, and **Find** reaches them.

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

### Depleted marks

A hotspot marked depleted is dated, and its card says how long ago.

- Nobody knows when a mined-out deposit refills (the game gives no date and it may differ from system to system). So by default the mark stays until you change it: read the deposit's Amount again and edit the hotspot.
- If you have seen a refill time, set it in **Settings → WFMT → Mining → Assume a depleted deposit has refilled after (days)** (0 = unknown). With a time set, the mark comes off that long after it was set, and the hotspot has no Amount until you read it again.
- If you then press **Mark depleted** on it and have not refined anything there since, WFMT takes that as a look at a deposit that is still empty. It keeps the first date and looks again 7 days later (`Still depleted at 15 d; look again in 7 d`).
- Tons refined since make it a fresh depletion.

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
- A body's size is also read from `Status.json` whenever you are near the ground, so the radar, **CTR** and **BRD** work on a body that was never scanned without this.

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
- Columns: the station, system, distance, demand, arrival distance, landing pads and *why it is listed*.
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

### You are here

With the Rhino on the body, the deposit within 175 m of it is marked `you are here` and selected, so **Mark depleted** is one click. It is worked out when the Book is opened or refreshed, not while you drive.

### Per commander

**Your hotspots, tons mined, depleted marks and the ground your Rhino has driven over belong to the commander you are playing.**

- Switching commander switches the Surface Mining Book and the coverage map. One commander never sees or changes another's.
- To give a hotspot list to another commander, use **I/E** (in the live window) to export it as the first commander and import it as the second.

For a scanned body it also shows what *you've* found so far on that kind of body. That starts empty and fills in as you save hotspots. It describes your own finds, not what a body actually holds.

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
| Ring reserve and hotspot lookups to always answer | They only know what players have uploaded to EDSM or Spansh. | No answer can mean nobody has recorded it. Scan the ring yourself, then save the hotspot with **+H.S.** |

## Settings

**Settings → WFMT → Mining**

The in-game Mining displays, including *Enable HUD Overlay*, are set on **Settings → WFMT → Overlays → Mining**.

**Checkboxes.** The first three are on by default. The rest are off.

- *Show session totals*, *Show the cargo bar* and *Show prospector hints* (on by default).
- The three online lookups above.
- *Show coverage minimap* (Surface Mining page): a small map of ground the Rhino has driven over on the current body.
- *Archive completed mining runs*: writes a JSON file per run.

**Other settings.**

- *Target commodities* and a percentage (Space Mining page). See below.
- *Assume a depleted deposit has refilled after (days)*: 0 (the default) means unknown and marks stay. A number takes a Depleted mark off that long after it was set.
- *Too close to place another rig (m)*: your own distance for the Surface Mining page's "far enough" note. 0 turns it off (0 to 2000 m, steps of 5).
- *Stop radius in the Surface Mining Book*: how close deposits must be to the lead deposit to share a stop (500 to 2500 m).

**The arrow to the nearest known hotspot** is the **Surface Compass** (Settings → WFMT → Overlays → Surface Compass, and the Compass section in [Exploration](exploration.md#compass)). It points at the nearest hotspot by default, and also works from any mode.

### Target commodities

Type a commodity as the game names it (for example Painite) and the least share of a rock that makes it worth cracking.

- You can type several, separated by commas or semicolons, each with its own percentage after the name: `Painite 30, Platinum 25, Void Opals`.
- A name with no number uses the percentage beside the box.
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

More detail: [Mining specification](../MINING_TECH_SPEC.md).
