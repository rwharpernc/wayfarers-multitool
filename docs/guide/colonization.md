# Colonization

Colonization has its own mode: press the **Colony** button.

- The page shows the project you are building now and nothing historical.
- Four buttons sit under it, left to right:
  - **Dashboard** opens the full [Colonization Sites window](#the-colonization-sites-window).
  - **Overlay** turns the [shopping list on the overlay](#the-shopping-list-on-the-overlay) on or off. It is lit while the card is on.
  - **Projects** opens [My Projects](#my-projects): everything you have on Raven Colonial.
  - **History** opens your [history](#history) in its own window.
  - Hover over a button for a one-line reminder of what it does.
- It works the same for a commander with a fleet carrier and for one without. The wording changes to match, and the carrier lines are left out when you have none.

**Work in progress.** Co-op building (several commanders on one project) and colony tracking are not available yet. For now this
page is about your own deliveries, ship and carrier, and details may change.

**Where this comes from:**

- The journal reports a construction site's totals when you dock or open its market, and each delivery you make.
- The ship's hold is read from the game's own `Cargo.json` (next to the journals), which the game rewrites on every change, so a purchase shows at once. WFMT looks again about a second and a half after each cargo event in case the game had not finished writing it. When the file cannot be read, or describes your SRV, it falls back to the hold EDMC reports.
- It does not say who delivered what, and it only records cargo you *transfer* to or from your carrier.
- WFMT adds the carrier's real hold from Frontier's servers (through a signed-in EDMC), nearby stock from Spansh, plans that players enter on Raven Colonial, and a bundled table of building costs.
- It works around the rest by tallying transfers itself.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

**On this page:** [How to](#how-to) · [The Colony page](#the-colony-page) · [Tracking a site](#tracking-a-site) ·
[The Colonization Sites window](#the-colonization-sites-window) · [Where to buy](#where-to-buy) · [My Projects](#my-projects) · [Planned builds](#planned-builds) ·
[The shopping list on the overlay](#the-shopping-list-on-the-overlay) ·
[What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)

## How to

Short task lists. Each one links to the section with the detail. The numbers in the worked examples throughout this guide are made up to show the shape of what you see; yours will differ.

**See your current build.**

1. Press **Colony** in EDMC.
2. Read **Current project**: **Delivered**, **Still to get**, **Trips left** and **Next**.
3. If you have more than one active site, the **Others** line says so. Press **Dashboard** to pick a different one.

See [The Colony page](#the-colony-page).

**Track a new construction site.**

1. Dock at the construction depot, or open its market, once.
2. Press **Colony**. The site is under **Current project**, or press **Dashboard** to see it in the list.

See [Starting to track a site](#starting-to-track-a-site).

**Build a shopping list.**

1. Press **Dashboard** and click the site on the left.
2. Use **Show** (**To buy**) and the **Filter** box to narrow the table to what you are working on.
3. Press **Copy Shopping List** (top right) and paste it into a note or chat.

See [The Colonization Sites window](#the-colonization-sites-window) and [Buttons](#buttons).

**Use Where to buy.**

1. In the Sites window, click a commodity row.
2. Press **Where to Buy** in the window header.
3. Check **Around**, **Within**, **Sort** and **Landing pad**, then press **Find nearest** for that commodity, or **Find all** for the whole list.
4. Click a result row to copy its system name, then paste it into the galaxy map's search.

See [Where to buy](#where-to-buy).

**Copy a To Acquire list for someone who asks what you still need.**

1. Press **Dashboard** and click the site.
2. If a transfer to your carrier did not register, press **Rescan Journals** first.
3. Press **Copy To Acquire** and paste the result.

See [Buttons](#buttons).

**Start a Raven Colonial project for a new site.**

1. Tick the master switch in **Settings → WFMT → Colonization → Raven Colonial** and save your Raven key there (get it at ravencolonial.com/user).
2. Dock at the new site. On the Colony page press **Create on Raven**, or in the Sites window pick the site and choose **Raven Colonial → Create Project on Raven…**.
3. In the dialog choose the plan entry (or **None**), the Location, Building and Layout, then press **Create**.

See [Starting a project on Raven Colonial](#starting-a-project-on-raven-colonial).

**Archive a finished site.**

1. Press **Dashboard**.
2. Choose **Manage Sites → Archive Finished**.
3. To look at it later, choose **Manage Sites → Show Archive**. Select the site and press **Restore** to bring it back.

See [The archive](#the-archive).

**Use the shopping list on the overlay.**

1. Make sure an overlay is running ([Setting up the overlay](../OVERLAY_SETUP.md)).
2. Press **Overlay** on the Colony page. It lights while the card is on.
3. Press it again to turn the card off. It stays as you left it after a restart.

See [The shopping list on the overlay](#the-shopping-list-on-the-overlay).

## The Colony page

**Current project** is your most recently updated active site:

| Line | What it says |
|---|---|
| Name, system and a bar | The site, and how far its build has come (the bar turns green when the build is complete) |
| Delivered, Still needed | The tons handed over by everyone against the tons it needs, with the build's percentage (`1,200 of 8,000 t (15%)`), and what is left |
| Covered | Of the commodities still needed, how many are **fully** covered, **partly** covered and **not yet** covered (`3 fully · 2 partly · 5 not yet (of 10 commodities)`), counting your ship, or your ship and carrier together if you have one. Left out once nothing remains to deliver |
| On hand | Tons of needed commodities in your ship now (read from `Cargo.json`) |
| Carrier | (Only with a fleet carrier.) Tons of needed commodities you have moved onto it (`120 t moved onto your carrier`) |
| Still to get | What is left to buy or mine after your ship (and carrier) |
| Trips left | **Without a carrier:** the loads of your current ship it takes to finish (`4 loads of 400 t`; one trip buys and delivers). **With a carrier:** `N to buy · N to haul (400 t ship)`. Left out once nothing remains to deliver. `Unknown (ship size not seen yet)` until EDMC has reported your ship's cargo capacity |
| Biggest gaps (t) | The four commodities with the most still to get, with their tons. Left out when nothing is left to get |
| Next | One sentence on what to do now: to buy or mine the rest (with a carrier, buy it or move it onto your carrier; the tons are on the Still to get line), that your ship and carrier hold everything so you should deliver it, that everything is delivered and you should dock to finish the build, or that the build is complete |
| Others | `+N more active sites` when you have more than the one shown (the line is left out when you have none) |

**Example (made-up numbers).** You are building an outpost with 8,000 t to deliver, 1,200 t of it handed over so far, and you have a fleet carrier. Your ship holds 400 t. The page might read:

```
Delivered       1,200 of 8,000 t (15%)
Covered         3 fully · 2 partly · 5 not yet (of 10 commodities)
On hand         180 t
Carrier         120 t moved onto your carrier
Trips left      9 to buy · 17 to haul (400 t ship)
```

Read it as: ten commodities are still outstanding, three need nothing more, and you should expect about nine buying loads and seventeen hauling loads to finish. The **Next** line then tells you in one sentence what to do now.

**An offer to start a Raven project.** When a construction site appears for the first time and [Raven Colonial](https://ravencolonial.com) has no project for it, a line above **Current project** says `Raven Colonial has no project for <site>.` with two buttons. **Create on Raven** opens the Colonization Sites window on that site and its [Create dialog](#starting-a-project-on-raven-colonial); **Not Now** hides the line. It is made once per site and goes away once a project exists. It needs the master switch and progress sharing on, and your Raven key saved, because WFMT only looks at Raven for a site when it is allowed to share.

**A finished build** is shown by its own name. The game calls a depot `Orbital Construction Site: Example Station` while it is being built. Once the build is complete, WFMT drops the `Construction Site:` part (`Example Station`) in the sites window, the shopping list and the history.

### History

History is yours alone (everything is per commander) and is kept off the page. Press **History** to open the Colonization History window, which names the commander it is for under its title. It has four tabs:

- **Overview**
- **By day**: tons delivered on each day (UTC), newest first. Only days with a delivery are listed
- **Commodities**: everything you delivered, most first
- **Sites**: every depot you delivered to, most first

A **help** button in the window's header repeats the notes below. The window keeps its size and position, and it follows the commander if you log in as someone else. A row with nothing to say (for example Best day before any delivery) is left out of the Overview.

The Overview says:

| Line | What it says |
|---|---|
| Sites | How many tracked sites are done, in progress and failed |
| You delivered | The tons and number of deliveries you made |
| Recently | Tons in the last 7 and 30 days |
| Best day | Your biggest single day |
| Busiest site | The site you delivered the most tons to, with the tons. A delivery in the journal names the depot only by a number, so WFMT takes the name and system from the time you docked there (it reads your journals for this once, and remembers it afterwards). A depot you never docked at in a journal shows as `Construction site <number>` |
| Claims | How many systems you have claimed (`ColonisationSystemClaim`), how many of those you released, and how many colonization beacons you deployed. Counts only: the game does not say when a claim ends, so WFMT does not list which systems are still yours |
| Average build | Days from the first time WFMT saw a site to the day the depot reported it complete, over the sites for which both are known |
| Counted since | The first delivery WFMT has counted |

**Example: finding your busiest week.** Press **History**, open **Overview**, and read **Recently** (for example `3,200 t this week · 9,800 t this month`) and **Best day**. Switch to **By day** to see which days made up that week, to **Commodities** to see what you moved most of, and to **Sites** to see which depot took the most. The numbers there are examples of the layout only.

**How far back the history goes.**

- The game does not keep a delivery history for a plugin to read, but your journal files do.
- The first time WFMT sees a commander it reads **all** of that commander's journals once, in the background, and rebuilds the history from every delivery in them. So it reaches back as far as your journals do.
- After that it counts each delivery as it happens.
- When EDMC starts it catches up from the recent journals (14 days, or back to your oldest active site, never more than 30).
- If you have deleted old journals, the figures can only go back as far as what is left. The History window says what date it is counting since.
- A rebuild never replaces figures that are larger than it can find.

**Things to know about the numbers.**

- A site's build time is only known for a site WFMT saw being started or finished. For the others the average leaves it out.
- The tons at the top ("Delivered") are everyone's, because the game reports them for the whole depot. "You delivered" is yours only.

## Tracking a site

WFMT keeps track of what each colonization construction site still needs delivered.

- You can read it from anywhere, not just while docked.
- It shows what's left to find after counting the cargo already in your ship.
- There is no on/off setting for it.

**Where the data comes from.** The journal writes a `ColonisationConstructionDepot` event when you dock at a
construction depot or open its market, and a `ColonisationContribution` event each time you hand cargo over.

### Starting to track a site

1. Dock at the construction depot, or open its market, **once**. There is nothing to type in.
2. The **Colony** page shows that site under **Current project** (see below). It is your most recently updated active
   site, with a line `+N more active sites` if you have others. With none it says `No active construction site. Dock at one to register it.`, and before WFMT knows the commander, `Waiting for commander login`.
3. Press **Dashboard** to open the **Colonization Sites** window.

**Example.** You fly to a new Orbital Construction Site and dock. You do nothing else. Press **Colony**: the site is now under **Current project**, with the name the game gave the depot's market. Press **Dashboard** and it is in the list on the left, with its tons in **Left** and a percentage in **Status**. Had you only flown past it without docking or opening its market, it would not appear.

### Who is playing

At start-up WFMT takes the commander from the newest journal (the last login in it), so the Colony page shows your sites straight away instead of `Waiting for commander login`. After you log in as someone else it follows them, and so do the open Colonization windows.

### The site name

- The name is the one the game gives the depot's market when you dock there.
- If WFMT hasn't seen you dock there, the site is called `Construction site <number>`.
- Dock again after you **rename** a site in the game and WFMT takes the new name (and the system, if that changed).
- Raven Colonial is a separate list. Rename it there too, or WFMT cannot match the two by name.

### Keeping it right

Each time you dock or open the depot market again, WFMT replaces its figures with the game's own. Between visits it adds what you deliver, as reported in the journal. Everything is kept **per commander**.

### Deliveries made with EDMC closed

They are found again when EDMC starts.

- WFMT reads the recent journals (14 days, or back to the oldest site it is tracking, never more than 30) and applies each depot snapshot and delivery once.
- It also registers a site you docked at in that time.
- A delivery to a site that no journal in that window has a depot snapshot for is ignored, since there is nothing to add it to.

## The Colonization Sites window

Sites are listed on the left under three headings: **Site** (the name), **Left** (tons the site still needs) and **Status** (progress as a percentage, or `complete` or `failed`). Finished ones are grayed out. The subtitle reads `<commander> — N active of M sites`. With no sites the list says to dock at a construction depot to register one. The window remembers its size and position. With Where to buy in its own window (the **Where to Buy** button), the commodity table has the whole height.

Click a site to see it on the right. The first active site is picked when the window opens. You see:

- its name and system,
- a progress bar,
- six totals,
- a **Filter** box, a **Show** dropdown (**All**, **To buy**, **To haul**) and two tick boxes (**Only what this station sells** and **Group by category**),
- a table with one row per commodity **still outstanding**.

### The six totals

They are always for the whole site, whatever the filters hide. A commander **without** a fleet carrier sees four of them: the carrier tile and *trips to buy* are left out, and *trips to haul* is captioned **trips to finish** (one load is bought and delivered in one go).

| Total | Meaning |
|---|---|
| t still to get | What you still have to buy or mine: what the site still needs, less what is in your ship and what you have moved onto your fleet carrier. It is the sum of the table's Acquire column |
| t on your carrier | Of the remaining need, what you have moved onto your fleet carrier (never more than the site needs). A dash without a carrier |
| t already in your ship | Of the remaining need, what your ship is carrying now (never more than the site needs) |
| t ship capacity | Your current ship's cargo capacity, as EDMC reports it. It follows you when you swap ships; a dash until EDMC has given it |
| trips to buy | Loads of that capacity to gather what is **still to get**, rounded up. **0** once everything is in your ship or on your carrier |
| trips to haul | Loads of that capacity to carry **all** the tons the site still needs to the site, rounded up. What you carry is the start of the first load, and what is on your carrier still has to be carried over, so this does not fall when you move cargo to the carrier |

Building a colony has two legs, and the window counts them apart.

- **Buying** takes cargo from the markets to your carrier (or straight to the site).
- **Hauling** takes it from the carrier, or your ship, to the construction site.
- A commodity you have already stored on the carrier needs no more buying trips but still needs its hauling trips.

### Filters and sorting

- The **Filter** box keeps the commodities whose names contain what you type.
- **Show** picks the stage of the work you are on (see the colors below for what counts as covered). It starts at **To buy** until you choose, then keeps your choice, and the [shopping-list overlay](#the-shopping-list-on-the-overlay) lists the same rows: change **Show** here and the card follows at once. The **Filter** box and the two tick boxes apply to the window only:
  - **To buy** lists only what is not covered yet, the rows you still have to buy or mine.
  - **To haul** is for the middle step, once everything is bought and parked on the carrier: it lists the rows that are covered but not yet aboard your ship in full, so a row leaves the list when you have loaded its whole need, and the site drops it for good once it is delivered. **To buy** would be empty by then.
  - **All** lists every commodity the site still needs.
- **Only what [station] sells** keeps just the commodities the station you are docked at has for sale. Open its commodity market once and the box names the station (clipped to 24 characters) and becomes usable; until then it is grayed out. It switches itself off when you leave the station.
- Click a column heading to sort by it, and again to reverse. The default is alphabetical, so rows stay put while numbers change.
- The status line at the bottom of the window says how many commodities are still needed, how many your ship (and carrier) cover, and the trips: `Your 400 t ship needs 21 trips to buy what is missing and 33 to haul it all to the site.` Its text changes to `The filters hide every commodity this site still needs.` when the filters hide every row.

**Example: shopping at a station.** You are docked at a market and have opened its commodity screen once. You want only what this station can sell you for the site.

1. In the Sites window click the site, then set **Show** to **To buy**.
2. Tick **Only what [station] sells** (the box names your station).
3. The table now lists only commodities that are still short and for sale here. Buy them, then watch the **In Cargo** and **Acquire** columns change as you load up. A row drops out of **To buy** once it is covered.
4. Type `steel` in **Filter** to look at just that commodity.

### The table columns

| Column | Meaning |
|---|---|
| Required | What the site needs in total |
| Delivered | What's been handed over |
| Acquire | What you still have to get: Required minus delivered, less what is in your ship and what you have moved onto your fleet carrier. It reaches **0** once you have it all, wherever it is stored, so it falls as you load up |
| In Cargo | What is in your ship (or SRV) now |
| FC | Tons of that commodity you have transferred onto your **fleet carrier** (only shown once WFMT has seen you have one) |
| Buy Trips | (Only with a fleet carrier.) Loads of **your current ship** to gather what is still missing of that commodity: what is left to get (the Acquire column) divided by your ship's cargo capacity. **0** when you already have enough, wherever it is stored |
| Haul Trips | Loads of your current ship to carry everything the site still needs of that commodity (Required less Delivered) to the site. This stays above 0 for a commodity sitting on your carrier, because it still has to be moved |
| Trips | Without a fleet carrier there is one trips column in place of the last two, headed **Trips**: the loads of your ship to buy and deliver that commodity |

The trip columns use at most two decimals (`4`, `1.5`, `1.25`, `0.33`), never round a small remainder down to 0, and show a dash
until EDMC has given your ship's capacity.

**Example row (made-up numbers).** Steel, with a fleet carrier and a 400 t ship:

| Required | Delivered | Acquire | In Cargo | FC | Buy Trips | Haul Trips |
|---|---|---|---|---|---|---|
| 1,000 | 200 | 300 | 100 | 400 | 0.75 | 2 |

The site still needs 800 t (1,000 less 200). You hold 100 t and have moved 400 t onto the carrier, so 300 t is left to acquire. At 400 t a load that is 0.75 of a buying trip, and 2 loads to carry all 800 t to the site. The row has no tint because you are still short.

### Row colors

The whole row is tinted by what you already have for that commodity, counting your ship **plus** what
you have moved onto your fleet carrier (the FC column):

- **Green:** the two together cover what the site still needs, exactly or with room to spare. Nothing more to buy.
- **Orange:** together they are **more** than the site still needs.
- **No tint:** you are still short. This is the normal look while you work on it.
- **Under the To haul filter** the colors change, because every row listed there is already covered and green would tint them all. There is **no green**, and the rows **in your ship's hold** (the ones you are hauling now) get a tint of their own: a blue-violet that fits the selected theme (Navy, Cyan, Amber or Green) and keeps the text readable. A row you have more than enough of, but that is not in your hold, keeps its orange.

The carrier figure is what WFMT saw you transfer (see the FC column notes), so it can drift from the carrier's real cargo.

- The **t still to get** total and the copied shopping list count it too, so they drop when you move cargo onto the carrier. So does Buy Trips.
- Haul Trips does not drop: everything still has to be carried to the site, whatever is stored where.

### The FC column

The FC column adds up the journal's `CargoTransfer` events made while docked at your fleet carrier: tons moved to the carrier minus tons moved back to the ship. It does lower the **t still to get** total. It is per commander.

**When it appears.** It appears for a commander WFMT knows has a fleet carrier, using the **same knowledge as Trade**:

- Your choice for that commander in the Trade settings (None, Fleet, Squadron, Both or Auto) decides when it names the carriers.
- On Auto, a fleet carrier Trade has recorded counts. Trade reads your recent journals at start-up and remembers them.
- Failing that, it appears once WFMT has seen one of yours itself (a transfer, opening Carrier Management, buying one, or docking at one).

- **Transfers made with EDMC closed are found.** They are in the journal, and at start-up WFMT reads the recent
  journals and adds any transfer it hasn't counted. A transfer is never counted twice, even if EDMC also saw it live.
- **How far back it reads:** 14 days, or back to the last transfer it counted if that is older, never more than 30.
  Transfers older than that are never counted, so stock you moved to the carrier before then won't show. Taking
  stock back off the carrier that was moved before then just leaves the figure at zero.
- **It is what WFMT saw you transfer, not the carrier's actual hold.** Changes that are not transfers are not in the
  journal as transfers, so they are not counted: buying from or selling to the carrier's market, trade orders, and a
  squadron mate moving cargo. The figure can therefore drift from the real contents.
- **Frontier's own figure can replace it, once it is safe to.** See the next section.

### How Frontier's figure and your transfers fit together

Two sources feed the FC column, and each is wrong in a different way.

- **Your transfers** (the journal) are exact and instant, but they only cover what you moved yourself.
- **Frontier's figure** is the carrier's real hold, but only when EDMC is signed in to Frontier, and it can be old. EDMC asks for it
  when a carrier event such as Carrier Management opens, at most every 15 minutes, and Frontier's copy can lag well behind what you
  just did. It has been seen to stay unchanged for more than 15 minutes while cargo was moved.

If WFMT simply trusted every Frontier figure, a lagging copy would undo your last unload: the column would fall back to an older
level just as you came back for the next load. So WFMT applies these rules to each Frontier figure:

1. **A figure that matches the tally** changes nothing.
2. **A figure that differs, within 15 minutes of your last transfer, is ignored.** It probably predates the transfer.
3. **A figure that differs but repeats a copy already ignored is ignored too.** Frontier has not updated; nothing new has been learned.
4. **Any other figure replaces the tally.** That is a copy that is not recent and has moved, so it can be trusted to show the real hold. Transfers you make afterwards are added on top.

The result: your own transfers are never undone by an old copy, and a Frontier figure that has really changed still corrects stock
that arrived or left some other way. The ignored copy is remembered in the saved carrier file, so a restart of EDMC does not forget it,
and **Rescan Journals** clears it.

**Reading it in the log.** Each Frontier figure writes one line to EDMC's log (Help → Open Log Folder in EDMC). Use it to see what
WFMT decided:

| Log line | What it means |
|---|---|
| `Carrier cargo from Frontier: 18806 t against 18806 t tallied (same)` | Frontier agrees with the tally. Nothing changed. |
| `Carrier cargo from Frontier: 15011 t against 18806 t tallied (changed)` | Rule 4. The tally now follows Frontier's figure. |
| `Carrier cargo from Frontier ignored: ... (the last transfer was 291 s ago)` | Rule 2. Frontier's copy may not include your last transfer yet. |
| `Carrier cargo from Frontier ignored: ... (unchanged since an earlier fetch)` | Rule 3. Frontier still shows the copy that was ignored, less than an hour after it was first ignored. |

If you report a column that looks wrong, press **Copy diagnostics** soon afterward: these lines are among the WFMT lines it copies
(see [Reporting problems](reporting-problems.md)).

### Rescan Journals: when a load did not register

There are two ways to correct the FC column, for different problems.

- **Opening Carrier Management** in the game (with EDMC signed in to Frontier) brings in the carrier's *real* hold from Frontier. This is the right fix after taking cargo *off* the carrier or when others have moved stock.
- **Rescan Journals** reads your own journals again. This is the right fix when a transfer *you* made did not register, or when a delivery or site is missing. It also folds in the last 30 days of site activity and rebuilds your delivery history, and it works for a commander with no fleet carrier too (the carrier step is simply skipped).

If the FC column is missing something you moved to the carrier, press **Rescan Journals** (top right of the Colonization Sites
window; the carrier part applies only to a commander with a fleet carrier).

1. WFMT discards its saved carrier tally for that commander, including any figure taken from Frontier.
2. It reads your journals for the **last 30 days**, oldest first, and counts every transfer you made while docked at your fleet
   carrier: tons moved to the carrier minus tons moved back to the ship.
3. The status line at the bottom says how many commodities and tons it found. Transfers you make after that count on top as usual.

What to expect:

- It only counts what the journals show you moving. Stock that reached the carrier another way (bought through its market, a
  trade order, a squadron mate), or moved more than 30 days ago, is **not** included. Where that matters, leave the tally alone and let
  Frontier's figure fill it in.
- A later Frontier figure replaces the rescanned tally only if it has changed and your last transfer is more than 15 minutes old (see
  [How Frontier's figure and your transfers fit together](#how-frontiers-figure-and-your-transfers-fit-together)), so a rescan is a
  quick fix for a missing load, not a permanent override. A rescan also clears any Frontier copy WFMT was ignoring, so the next
  figure is judged fresh.
- It is safe to press more than once, and it never counts a transfer twice. It only touches the commander shown in the window and
  reads files on your computer; nothing is sent anywhere.

### Scenarios: what to expect and what to do

**You unload at the carrier, then go and buy another load.** The column keeps the unloaded stock. If Frontier's copy arrives and still
lacks the unload, WFMT ignores it, so the column does not fall back. Nothing to do.

**You make several trips in a row.** Each unload adds to the tally, and every Frontier figure is checked against it as above. The
column keeps climbing even if Frontier's figure stays at an old value. The log shows `ignored` lines, which is expected.

**The column is higher than the carrier's real hold.** WFMT counts what you transferred, so it drifts high when stock left the carrier
without a transfer you made: you sold from the carrier's market, a trade order filled, or a squadron mate took some. To correct it:

1. Make no transfers for 15 minutes, so your last transfer is no longer "recent".
2. In the game, open Carrier Management (EDMC must be signed in to Frontier). EDMC fetches the carrier, and a figure that has moved replaces the tally.
3. If the log says `unchanged since an earlier fetch`, Frontier has not updated yet. Wait and open Carrier Management again (a copy that keeps repeating is applied once an hour has passed since it was first ignored), or press **Rescan Journals** to restart from your journals.

**The column is lower than the carrier's real hold.** Stock reached the carrier without a transfer you made (bought through its market, a trade
order, a squadron mate), or it was moved more than 30 days ago. Follow the same three steps. **Rescan Journals** will not help here, because it
only counts your own transfers.

**A load you moved never showed up.** The game did not write the transfer (or EDMC was closed, and it was not caught up). Press
**Rescan Journals**. If the transfer is in your journals it is counted, and it is never counted twice.

**You took cargo off the carrier** (to the ship). That is a transfer, so the column drops at once. Nothing to do.

**EDMC is not signed in to Frontier.** There is no Frontier figure at all. The column is your transfers only, so it drifts as in the
cases above. Sign EDMC in to Frontier, then open Carrier Management. Until then, **Rescan Journals** is the only correction.

**You played with EDMC closed.** At the next start WFMT reads the last 14 to 30 days of journals and adds any transfers it has not
counted. Press **Rescan Journals** only if one is still missing.

**The column stays on an old Frontier value you know is wrong.** Check the log for the lines above. If every line says `ignored`,
Frontier's copy is not updating. This is on Frontier's side. Press **Rescan Journals** to rebuild from your journals, or move a
little cargo, wait 15 minutes and open Carrier Management again.

**The column drops after you opened Carrier Management.** Frontier's figure had changed and your last transfer was more than 15 minutes
old, so WFMT took Frontier's figure as the real hold. If a load of yours is missing from it, Frontier's copy was only partly updated.
Press **Rescan Journals**, and tell us if it happens often, with the log lines.

**Example (a worked sequence).** Following the steel row above, where **Acquire** was 300 t:

1. You buy 300 t of steel. **Acquire** falls to 0 as you load, and the row turns green because your ship and carrier together now cover the 800 t the site still needs.
2. Had you bought 350 t instead, together they would be more than the site needs and the row would turn orange. Nothing is wrong; you simply hold extra.
3. You carry the stock to the site and deliver it. The row leaves the table once the site has it all.

### The commodity table: grouped, like the overlay

For anyone who does not use the overlay, the commodity table is the shopping list, with the same order and the same graying as the overlay:

- **Group by category** (a checkbox above the table, on by default, remembered) puts the commodities under a heading for each market
  category (Chemicals, Foods, Industrial Materials, Machinery, Metals and so on).
  - Each heading shows the tons still to get under it (the sum of their Acquire figures), and the commodities are alphabetical under it.
  - Click a heading to fold or open its group.
  - Untick the box, or click any column heading to sort by it (or the commodity column a second time for reverse order), and you get a plain sorted list instead.
- **Grayed out when the market does not sell it.** While you are docked at a commodity market WFMT has seen, a commodity that market does
  not sell shows in a faint gray with **(not available here)** after its name, unless your ship and carrier already cover it (it keeps its
  green or amber tint). This only marks rows; **Only what this station sells** still hides them.

## Where to buy

**Where to buy** finds the closest places to buy a commodity. It has its own window: press **Where to Buy** in the header of the Colonization Sites window. The window remembers its size and position, opens with the picked commodity and the site's system filled in, and closes with the Sites window.

1. In the Sites window, click a commodity row. The Sites window's footer says what to do next, the Where to Buy window's **Commodity** line names it, and its note says `Ready to search for <commodity>. Press Find nearest.` Pick another row, or another site, and the open window follows.
2. Check the options.
3. Press **Find nearest**. While it runs the note is shown in the accent color and the button is disabled.

With no row picked it asks you to pick one, and with no system in the **Around** box it asks you to enter one or press **Here**. The same search asked again within two minutes is answered from memory rather than sent to Spansh again.

It asks [Spansh](https://spansh.co.uk) (a community-run map of the game), so it needs an internet connection.

- Nothing is fetched until you press the button.
- Only the commodity name and the system you search around are sent.

**Example: finding Steel for a site (made-up).** The site is in a system you are not in.

1. Click the **Steel** row in the Sites window, then press **Where to Buy**. The note reads `Ready to search for Steel. Press Find nearest.`
2. Leave **Around** as the site's system (or press **Here** to measure from where you are), keep **Within** at 50 ly, and choose **Large only** under **Landing pad** if you fly a large ship.
3. Press **Find nearest**. The table lists stations with Distance, Arrival, Price and Supply.
4. Click the first row you like. The note says the system name was copied; paste it into the galaxy map's search.
5. If nothing came back, raise **Within** or set **Landing pad** to **Any size**, and search again.

### The options

| Option | Meaning |
|---|---|
| Around | The system to measure from. It starts as the site's system (and follows the site you pick until you type your own); type another (system names autocomplete), or press **Here** for the system you are in now. **Here** says so if WFMT has not seen which system you are in yet |
| Within | How far to look: 25, 50, 100, 200 or 500 ly, or no limit. Default 50 |
| Sort | **Closest first** (default) or **Cheapest first**. This decides which stations Spansh returns, not just their order. Click a result heading to re-sort what came back |
| Landing pad | **Any size** (default), **Medium or larger**, or **Large only**. Any size lists stations whose biggest pad is small, so you can swap to a smaller cargo ship when a commodity isn't sold at a large-pad station. The **Pad** column shows each station's largest pad |
| Exclude fleet carriers | Off by default, so carriers are included: they are searched separately and listed under their own **Fleet carriers** heading after the stations. Tick it to leave them out (and save one request per commodity) |
| Exclude surface ports | Off by default, so surface ports are included. Tick it to leave out stations on a planet's surface (planetary ports), from the lists and from the route. It changes what is shown, not what is asked of Spansh, so ticking or unticking it after a search redraws the results at once |

The options are **remembered** (within, sort, landing pad and fleet carriers) for the next time you open the window. The
search system is not: it starts as the site's system again.

### Find all

**Find all** searches every commodity you still have to buy, using the same options. It lists the closest 5 stations (and, if carriers are ticked, the closest 2 carriers) under a heading for each commodity.

- It follows the table as you have it filtered. Rows already covered are left out, and so are rows the Filter box, **Show** or **Only what [station] sells** hide.
- Spansh can only look up one commodity per request. So WFMT sends one request per commodity, a short pause (0.4 second) apart, plus one more asking for the nearest stations that have every commodity on the list in stock (see below).
- A list of 20 takes some seconds, and the note under the buttons shows how far it has got, in amber while a search is running so it stands out.
- While it runs, **Find all** is relabeled **Stop** and **Find nearest** is disabled. Press **Stop** to stop after the search in progress, keeping what it found (the note says `(stopped early)`).
- A commodity that fails is named and the others still show. Press **Find all** again to retry.
- Commodities with no source in range are listed in the note.

**A station that sells the whole list.** The extra request finds stations (and carriers, if ticked) that have *every* commodity you are searching for in stock.

- Any it finds are added under each commodity with that commodity's price and stock, so the route can use a station that is not among the nearest few for any one commodity.
- For a long list Spansh usually has no such station and nothing is added.
- If this request fails, Find all carries on without it.

**Fewer requests.**

- That request goes first. A commodity that one of those stations can supply in full is not searched on its own (its answer comes from that station's market), so a list that one station can fill takes a single request.
- After the searches, if the route still leaves two or more commodities uncovered, one more request asks for stations that have all of those in stock. The whole market it returns also fills in any other commodity on your list those stations sell.

**Example: planning the whole list (made-up).** You have 12 commodities left to buy.

1. In the Sites window set **Show** to **To buy**, so covered rows are left out.
2. In Where to Buy set **Within** to 100 ly and press **Find all**. The note shows how far it has got; press **Stop** if you want to stop early and keep what it found.
3. Read the **Closest way to buy everything** block above the lists: the stops in the order to fly them, what to buy at each, and the price and stock of every item. Anything the route cannot cover is named in the note.
4. Press **Copy Route** to paste the plan into a note.

### Suggested route

Find all also works out a shopping route and shows it in a shaded block of its own, **Closest way to buy everything**, above the per-commodity lists (the block scrolls if it is long): the few stops (at most 6) that between them supply the most of what you still have to get.

- A station that sells several of your commodities counts for all of them, so it is taken first. Ties go to the nearer, then the cheaper.
- Each stop shows what to buy there, with the price per ton and the stock (**Supply**) at that stop. Click a stop to copy its system name.
- The stops are listed nearest first, which is the order to fly them.
- What no station in range can supply is named in the note.
- **Surface ports.** A stop on a planet's surface is marked **Yes** in the **Planetary** column. When a commodity is sold *only* at surface ports among the stations found, before saying so, Find all makes one more request for each such commodity asking for orbital stations alone, since the nearest sellers can all be on planets and push the orbital ones out of the list. Only if that finds nothing does the block say so, in a group at its top (**Only at surface ports**, one commodity per row), the item is marked **surface ports only** under its stop, the commodity's heading says so, and the note repeats it. With **Exclude surface ports** ticked those commodities are left out of the route and the lists instead, and the group reads **Only at surface ports, so left out of the route**, so you know why they are missing.
- **It follows your purchases.** When what you have bought reaches your ship's hold or your fleet carrier (or is delivered), the route and the lists are worked out again from the stations already found, with no new search. A commodity you now have in full leaves the route and its heading disappears; one you have part of shrinks to the tons still to get. The tons come from the Sites window's **Acquire** column, so they follow its hold and carrier figures. The note under the buttons is left alone, except to say when everything is bought.
- It only considers the stations Find all returned (including any that sell the whole list), which is the nearest 25 per commodity within your radius.
- Stock changes, so treat it as a plan to check on arrival.
- **Copy Route** copies it as plain lines to paste into a note or chat.

### Reading the results

The results table has the columns **Station**, **System**, **Type**, **Planetary**, **Pad** (largest landing pad), **Distance** (light years from the Around system), **Arrival** (distance from the arrival star, in ls), **Price** (per ton) and **Supply** (the stock). **Find nearest** lists up to 25 stations and, if carriers are ticked, up to 10 carriers.

- **Planetary: Yes** means a base on a planet's surface, so you have to descend to land (planetary ports and outposts, settlements).
- **Planetary: No** means an orbital station, asteroid base, megaship or fleet carrier, which you dock at in space.
- Click a heading to sort by it.
- **Click a result row** (a station, or a stop in the suggested route) to copy its system name, ready to paste into the galaxy map's search. The note under the buttons says what was copied. Headings and the "buy" lines under a route stop copy nothing.
- **Copy System** does the same for the row already selected (it asks you to select a result row first if none is).
- **Copy Route** needs a **Find all** first.

### Things worth knowing

- Only stations whose market was updated in the last 7 days are listed, because older figures are probably out of date.
  The prices and stock come from players' own market updates, so confirm on arrival.
- A fleet carrier can move or sell out at any time, and its prices are set by its owner, which is why carriers are
  opt-in and kept in their own section.
- A station for which Spansh gives no pad figures is kept in the list (its Pad shows `?`) rather than hidden.
- If Spansh is busy or unreachable, the panel says the search failed; try again shortly. Nothing else in WFMT is affected.
- The search looks for stock that is **for sale**. It does not know what a station's market will have tomorrow.

### Buttons

The header of the window, top right. All of them act on the site picked on the left:

- **Copy Shopping List** (the highlighted button) copies that site's list to the clipboard: a first line such as `Example Outpost (Example System) - still to get:`, then lines like `1,200 t  Steel`, biggest first. What is in your ship and on your fleet carrier is already taken off.
- **Copy To Acquire** copies a short list for someone who asks what you still need, for example part way through loading your carrier: a first line such as `Example Outpost (Example System) - still to acquire:`, then one line per commodity such as `Steel: 200 t`, biggest first. Only commodities with something left to acquire are listed; what is in your ship and on your fleet carrier is already taken off. It uses the figures the window shows, so a transfer WFMT missed can be fixed first with **Rescan Journals**.
  The amounts are the **t still to get** figures, so what is on your ship and on your carrier is taken off. If nothing is needed it says
  so.
- **Rescan Journals** rebuilds the fleet carrier tally from your journals; see [Rescan Journals](#rescan-journals-when-a-load-did-not-register).
- **Raven Colonial** (a menu): **My Projects**, **Planned Builds**, **Raven Progress**, then **Open Selected Build on Raven**, **Open This System on Raven**,
  **Raven Colonial Website**, then **Create Project on Raven…**, **Report Complete to Raven** and **Mark Plan Entry Demolished…** (the three that write; the dots mean a question follows). See
  [Planned builds](#planned-builds), [Starting a project on Raven Colonial](#starting-a-project-on-raven-colonial) and
  [Sharing your progress with Raven Colonial](#sharing-your-progress-with-raven-colonial).
- **Manage Sites** (a menu): **Archive Finished** moves every complete or failed site into the [Archive](#the-archive); **Show Archive** opens it. **Remove Site** stops tracking the selected site, and **Remove Finished** deletes every complete or failed site and says how many it removed. Neither removal asks first. Removing a site only forgets WFMT's tracking of it: docking at the depot again registers it afresh.

**Example: copying lists.** For a site that still needs 1,200 t of Steel and 800 t of Titanium, with nothing yet aboard, **Copy Shopping List** puts this on the clipboard (the site and system are made up):

```
Example Outpost (Example System) - still to get:
1,200 t  Steel
800 t  Titanium
```

**Copy To Acquire** gives the same commodities as `Steel: 1,200 t` and `Titanium: 800 t` under its own first line (`... - still to acquire:`). Once you have moved 500 t of Steel onto your carrier, both lists show `700 t` for Steel.

### The archive

Finished sites stay in the Sites window until you remove or archive them; WFMT never clears them by itself. The **Archive** keeps them for reference without crowding the list of sites you still work on.

- **Archive Finished** (Manage Sites) moves every complete or failed site there. An unfinished site is never archived.
- **Show Archive** opens a window listing them, newest finish first: the site, its system, how it ended, when WFMT first saw it and when it finished, how long it took, and the tons it needed. Select one to see each commodity it needed and what was delivered. Delivered counts everyone's deliveries, as the depot reports them.
- **Restore** puts the selected site back in the Sites window. **Copy Summary** copies its facts as text. **Manage → Remove Permanently** forgets it after asking; the delivery history keeps your own totals but not the site's list of commodities.
- Archived sites still count in the [History](#history) figures, and they are in the same data file as the other sites, so **Back up my data** includes them. If a depot reports an archived site as under construction again, it returns to the Sites window.

**Example: tidying up after a build.** Two of your six sites show `complete` and one shows `failed`. Choose **Manage Sites → Archive Finished**. The three leave the list, and the subtitle's count of active sites is unchanged. Choose **Manage Sites → Show Archive** to see them, newest finish first, with how long each took. Select one and press **Copy Summary** to paste its facts, or **Restore** to put it back. Your History totals still include them.

## My Projects

The Colonization Sites window only knows sites you have docked at. **My Projects** (the **Projects** button on the Colony page, or **My Projects** in the **Raven Colonial** menu) lists every active project your commander has on [Raven Colonial](https://ravencolonial.com), across systems.

- **Reading needs no key and no switch.** Opening the window sends only your commander name, to read your projects, your hidden list and your primary project.
- **The table** has the columns **Count** (a tick when counted), **Project**, **System**, **Building** (the game's name and the build type Raven knows it by, such as *Industrial Outpost (vulcan)*), **Done** (percent delivered), **Still needed** (tons, or `complete`) and **Note**. The Note column says **Primary** for your primary project and **Here** for a site WFMT also tracks from your journal. Completed and uncounted projects are grayed.
- **Count.** A project is counted unless it is on your hidden list on Raven Colonial. The line under the title reads like `<commander> - 6 projects · 5 counted need 41,000 t · 105 trips in your ship`: it adds up the counted projects and the trips they take in the ship you are flying, and adds `unsaved changes to the counted list` once you have changed it here. Double-click a row, or select it and press **Count / Don't Count**, to change it.
- **Refresh** (the highlighted button) reads everything again. The window also follows you when you log in as another commander, and a **My Projects help** button repeats these notes.
- **More** menu:
  - **Copy Shopping List** copies the picked project's needs, biggest first.
  - **Open Project on Raven** and **Open My Projects on Raven** open ravencolonial.com in your browser.
  - **Set as My Primary…** makes the picked project your primary one on Raven Colonial. It asks first.
  - **Save Counted List…** replaces your hidden list on Raven Colonial with the one on screen. It asks first, because other tools that read the list, such as SrvSurvey, see the change too.
- **The two writes** need your Raven Colonial key and the master switch (see [Sharing your progress with Raven Colonial](#sharing-your-progress-with-raven-colonial)). Nothing is saved until you press the button.
- It does not change WFMT's own tracking. A project you have never docked at is listed from Raven's figures alone, so its commodity list is Raven's, not your journal's.

**Example: choosing what to work on (made-up).** You open My Projects and the line under the title reads `CMDR Example - 6 projects · 5 counted need 41,000 t · 105 trips in your ship`. You select the project marked **Here**, press **More → Copy Shopping List**, and have its needs biggest first. Another project is finished, so you double-click its row to stop counting it, and the line changes to say `unsaved changes to the counted list`. Nothing reaches Raven Colonial until you choose **More → Save Counted List…** and confirm.

## Planned builds

The journal only reports a construction site once you have docked at it, so a build you have only **planned** never appears in WFMT.

Press **Planned Builds** (in the **Raven Colonial** menu, top right of the Colonization Sites window) to see what [Raven Colonial](https://ravencolonial.com), the community planning site, has for the selected site's system.

- Every site there is listed, building first, in the columns **Site**, **Status** (**Building**, **Planned**, **Complete** or **Demolish**), **Type**, **Body** (the body's number), **Full cost** and **In WFMT**. Click **Refresh** to ask again. A help button repeats these notes.
- The top of the window names the system's **architect** (the commander who planned it there) and whether Raven Colonial has it **open** or **locked**, as Raven Colonial reports them.
- A site you have docked at and WFMT tracks is marked **yes** under *In WFMT*.
- The window opens for the selected site's system, and shows the new system if you open it again from another site. With no system known yet for the site, dock at it once.

**Example (made-up).** You plan three outposts in one system and have docked at only one. Open **Raven Colonial → Planned Builds** from the Sites window. The table lists all three: the one you are building shows **Building** with **yes** under *In WFMT*, the other two show **Planned** with **no**. Click a planned row to see its five biggest commodities in the footer, and read `planned builds need N t` under the title to know the total still to come.

### Full cost

For a planned or building site it also shows the **full cost**: the tons the whole building needs, from a table of what each kind of building costs that is bundled with WFMT.

- Full cost is shown for planned and building sites only, not finished ones.
- Click a row to see its building, layout and its five biggest commodities in the footer.
- The line under the title adds up what all the *planned* builds in the system will need (`planned builds need N t`).
- The table is a snapshot. If the game changes a building's cost, it can be out of date until WFMT is updated.
- A building the table does not know shows no cost.

### What is sent

- It asks Raven Colonial once, when the window opens or you press **Refresh**, and sends only the system's name.
- The answer is remembered for a minute.
- It shows what *other people* have entered there, so a system nobody has planned on that site shows nothing.

See [what goes on the internet](internet-and-privacy.md).

### Quick links to Raven Colonial

The **Raven Colonial** menu in the Colonization Sites window also opens Raven's own pages in your browser (WFMT sends nothing to Raven
for these; your browser does the asking):

- **Open Selected Build on Raven** goes straight to the selected site's project page. WFMT finds the project the way Raven Progress
  does (one read of the system's plan); a site Raven has no project for opens its system page instead.
- **Open This System on Raven** opens the selected site's system.
- **Raven Colonial Website** opens the home page.

### Sharing your progress with Raven Colonial

Optional and **off by default**.

- Nothing is sent to Raven Colonial until you tick the **master switch** in **Settings → WFMT → Colonization → Raven Colonial**.
- Unticking it stops every write at once (progress, deliveries, carrier cargo and Report Complete), keeping your other choices for when you turn it back on.
- With the switch on, WFMT shares what happens at a construction site **as it happens**, in the way Raven Colonial's own documentation recommends for a tool that reads the journal.

| Setting | What WFMT sends, and when |
|---|---|
| **Allow WFMT to write to Raven Colonial** (master switch) | Nothing by itself. Off by default. The two tick boxes below only work while it is ticked, and are grayed out while it is not. |
| **Report my construction progress and deliveries to Raven Colonial** | Needs the key below; with none, nothing is looked up or sent. When the depot's figures change (the game's `ColonisationConstructionDepot` event): the depot's numbers and how much of each commodity is still needed, which is what moves *Remaining* on Raven Colonial. When you deliver cargo (`ColonisationContribution`): the commodities and tons, which credits your commander name in Raven's history. Once per project, it also links your commander to the project. |
| **Also report cargo I move to and from my fleet carrier** | When you transfer cargo at your own fleet carrier: the tons moved, to the carrier as plus and back to the ship as minus. It adds to Raven's carrier record; it never replaces it, because WFMT's own tally is only what it saw you move. Needs the key below. |
| **Raven Colonial key** | Needed for every write: progress, deliveries, carrier cargo, **Create Project on Raven**, **Report Complete to Raven**, **Mark Plan Entry Demolished**, and **Set as My Primary** and **Save Counted List** in My Projects. With no key WFMT sends nothing (Raven's published API description does not say which writes work without one, so none is tried). Saved per commander on your computer, shown masked, and sent only to Raven Colonial. |

**Where to get the key.** The settings page has a link to [ravencolonial.com/user](https://ravencolonial.com/user), where you sign in and Raven shows your key (it is also the page that can reset it). WFMT does not fetch it for you.

**Test key.** The **Test key** button beside the **Raven Colonial key** box in Settings asks Raven Colonial whether the key you typed is accepted for your commander. The key is saved for the current commander when you close Settings.

- It uses a read that changes nothing, and shows Raven's name for you when the key is accepted.
- It checks the box as typed, so you can use it before closing Settings.

**What works with no key and no switch.** **Planned Builds**, **My Projects** (viewing) and **Raven Progress** only *read* from Raven Colonial, so they need neither.

- Each runs when you press its button or open its window. **Planned Builds** sends only the system's name, **My Projects** only your commander name, and **Raven Progress** the system's name and the project's id (and, if the plan does not name the project, the system's address and the site's market id).
- If another tool already reports your builds to Raven, leave the master switch off. WFMT then sends nothing, and Raven Progress is a way to check that Raven's figures match WFMT's.

### Rules for what is sent

- **Only live events.** What you did while EDMC was closed, and anything the start-up catch-up reads, is never sent.
- **Raven must already have a project for the site.** WFMT finds it from the system's plan and, failing that, from the system's address and the site's market id (so a project named *Primary port* is still found, and a renamed station does not break it). If it has none,
  WFMT sends nothing and tries again no sooner than ten minutes later. To make one, use
  [Create Project on Raven](#starting-a-project-on-raven-colonial); WFMT then uses it at once.
- **One request per event.** They go one at a time in the background, are retried once if Raven says it is busy, and a failure is only
  logged; it never interrupts play. The depot figures are sent only when the needed amounts actually changed.
- **Raven's `supply` call is never used.** Raven documents it for tools that cannot read the journal; used beside the depot figures it
  would reduce what is needed twice.
- **Do not run two tools that report to Raven.** If another tool (the Raven Colonial EDMC plugin or any other) also reports your
  deliveries, Raven counts them twice. Turn one of them off.
- **Raven Progress** (in the **Raven Colonial** menu of the Colonization Sites window) reads Raven's own figures for the selected site and sets them beside
  WFMT's in the status line (*<site>: Raven Colonial says 12,345 t still needed of 20,000; WFMT says 12,345 t (they agree)*, or *they differ by N t*, and a note when Raven has it marked complete). It looks the project up first, so it sends the system's name and the project's id.

WFMT's own tracking stays the source of truth for your site; Raven's figures never overwrite it.

### Starting a project on Raven Colonial

When you dock at a construction ship or site that Raven Colonial has no project for, nothing is shared until one exists. Select the site and choose **Create Project on Raven** in the **Raven Colonial** menu.

- It needs the master switch on and your Raven Colonial key (WFMT asks for the key the first time, and keeps it once Raven accepts it). It only works for an **active** site; a finished one is refused. With the switch off the status line points you to Settings.
- You can also be offered this from the Colony page when a new site appears (see [An offer to start a Raven project](#the-colony-page)).
- WFMT first reads the system's plan on Raven Colonial. If a project already exists for the site it says so and does nothing else. The status line shows what it is doing while it looks, and the message from any button you press in this menu stays for 30 seconds, even while the game's construction panel keeps updating the window.
- The dialog opens centered over the Sites window and always inside the screen. If it ever does not open, the EDMC log has a `Create project:` line saying where the steps stopped.
- Otherwise the **Create Raven Colonial project** dialog opens. **Plan entry** lists the sites planned for that system that have no project yet, each with its build type; pick yours, or leave **None** to make a project of its own (WFMT never edits the system's plan). If only one site is planned it is preselected.
- The building is chosen in three steps, as on Raven Colonial: **Location** (orbital or surface), **Building** (by tier and the game's name, such as *Tier 1: Industrial Outpost*), then **Layout (build type)**, the exact identifier Raven Colonial uses, such as `vulcan` or `dual_truss`. That identifier is what is sent. A planned site fills in all three; changing Location clears Building and Layout. Create refuses until a building and layout are chosen (`Choose the building and its layout.`).
- **Body** is chosen from the system's bodies as Raven lists them (or left *Unknown*). **Name** defaults to *Primary port* for the system's colonization ship, otherwise the station's own name. **Architect** (defaults to Raven's architect for the system, otherwise you), **Notes** and **Due (YYYY-MM-DD)** are optional; a due date in another form is refused.
- Three tick boxes: **This is the system's primary port** (ticked for a colonization ship), **Make it my primary project**, and **Attach my fleet carrier** (grayed out, with a note, until WFMT has seen your carrier's id this session, which happens when you log in or open Carrier Management).
- A red note in the dialog warns when Raven reports the system as locked to another architect.
- Nothing is sent until you press **Create** (**Cancel** sends nothing, and the status line says so). Then WFMT, in order: creates the project from the depot figures it already holds, links your commander, and does the two optional ticks. The status line says what worked. If linking, primary or the carrier fail, the project stays and the message names the step.
- **What is sent:** your key, the site's market id, system name, address and position, the commodities still needed with the depot figures, and what you typed in the dialog. No journal data beyond that.
- **Limits:** a system that is locked to another architect may refuse a project (the dialog warns when Raven reports it as locked). WFMT's own tracking never changes.

**Example: first project in a new system (made-up).** The Colony page shows `Raven Colonial has no project for Example Outpost.`

1. Check that **Allow WFMT to write to Raven Colonial** is ticked and your key is set in Settings.
2. Press **Create on Raven**. The Sites window opens on that site with the Create dialog.
3. Pick the matching **Plan entry** (its Location, Building and Layout fill in), or leave **None** and choose them yourself.
4. Press **Create**. The status line says what worked. From then on your deliveries are shared as they happen.

**Mark Plan Entry Demolished…** sets the selected site's entry in Raven's plan to *demolished* after you confirm. It changes Raven's record only, not the game. It needs the master switch and your key like the other writes, and says so when Raven's plan has no entry for the site.

### Reporting a finished build to Raven Colonial

Select a site your journal has reported **complete** and press **Report Complete to Raven** (in the **Raven Colonial** menu, top right of the Colonization Sites window).

- WFMT looks the site up in Raven Colonial's plan for its system. It matches on the site's market id, or on its name for a build still in progress, which Raven has no market id for yet.
- Then it marks that project complete there.
- It never does this by itself. It asks you to confirm each time (`Tell Raven Colonial that <site> in <system> is complete?`). Before the site is complete in your journal it says there is nothing to report.

- It needs the master switch and your **Raven Colonial key**. The first time, WFMT asks you to paste it; it is saved for that commander only (in
  `rcc_keys.json`, in the plugin folder, which updates leave alone) once Raven Colonial has accepted it, and masked as you type.
- **What is sent:** your key and the one project's id, nothing else. No deliveries, cargo or journal data.
- **Limits:** Raven Colonial must already have a project for the site, found from its plan or by the site's market id. If it has none
  (for example it is still only planned there), WFMT says so and sends nothing; **Create Project on Raven** can make one. Reporting does not copy anything back: WFMT's own tracking
  stays as it is.

**Example (made-up).** You finish delivering and dock at the depot, and the game reports the site complete. Select it in the Sites window and choose **Raven Colonial → Report Complete to Raven**. Confirm `Tell Raven Colonial that Example Outpost in Example System is complete?` and the project is marked complete there. Nothing was sent before you confirmed.

## The shopping list on the overlay

Optional, and **off until you ask for it**. It needs an overlay running; see [Setting up the overlay](../OVERLAY_SETUP.md).

- Press **Overlay** on the Colony page to put it up whatever screen you are on.
- Or tick **Also show the shopping list automatically (markets, carrier inventory, construction sites)** in **Settings → WFMT → Overlays → Colonization**, so it appears by itself in the places listed below.

### The table

It draws a table, with the site name as its title and the columns **Commodity**, **Required**, **Acquire**,
**FC** and **Cargo**:

- **Required** is the site's full requirement for that commodity.
- **Acquire** is what is left to get: what the site still requires (required less delivered), less your hold and your
  fleet carrier, the same as the window's Acquire column. It shows **0** once you have it all, wherever it is stored.
- **FC** appears only if you have a fleet carrier (see the FC column above): what you have moved onto it. It is blue
  once it covers the remaining amount, gray while it doesn't, and blank when none.
- **Cargo** is what is in your ship's hold right now, so you can see what you just bought. A **✓** after the name means
  your hold **plus** what is on your fleet carrier already covers it (the row turns green, the same rule as the
  window's green rows); the row turns amber if together they are **more** than the site needs.
- **With *List* set to *To haul*** every row is already covered, so there is **no green**: the **✓** stays, and the rows that are **in your ship's hold** (the ones you are hauling now) are drawn in the overlay's blue instead, as the Sites window tints them. A row you have more than enough of but that is not in your hold stays amber.

**Example card (made-up).** Docked at a construction site, the card might show:

```
Example Outpost
Commodity        Required  Acquire  FC   Cargo
Aluminium           900      300    400   100
Steel ✓           1,000        0    800   200
► 32,769 remaining  ► 21 to buy  ► 33 to haul
```

Steel carries a check mark because the hold plus the carrier cover it, so its row is green. Aluminium is still short, so it has no tint. Set **List** to **To buy** and the Steel row disappears, leaving only what you still have to get.

### Order

- At a **construction site** the rows are alphabetical, so they stay put while numbers change.
- Everywhere else (a commodity market, the carrier's inventory) they are **grouped under the market's categories** (Chemicals, Foods, Industrial Materials, Machinery, Metals, Technology and so on).
  - Each group has a heading line, in capitals, in the card's title color.
  - The commodities are alphabetical inside it, indented under their heading.
  - A commodity WFMT has no category for goes under **Other**, last.

### Grayed out when this market does not sell it

- While you are docked at a commodity market, a commodity that market does not have for sale is shown in a faint gray with **not available** after its name, so what you can buy here stands out.
- A commodity your hold and your fleet carrier already cover keeps its green (or amber) however the market stocks it.
- Nothing is dimmed away from a market, at a construction site, or if WFMT has not seen this market (open its commodity screen once).

### The last line

A last line gives the tons remaining (still to get, as in the Acquire column) and the trips in your current ship. It needs your ship's cargo capacity, which EDMC supplies.

- **With a fleet carrier** it gives both legs, as the Colony page and the window do: `► 32,769 remaining  ► 21 to buy  ► 33 to haul`.
  - **To buy** is the loads to gather what is still to get after your ship and your carrier (0 once it is all stocked).
  - **To haul** is the loads to carry everything still needed to the site.
- **Without a carrier** there is one figure, `► 32,769 remaining  ► 33 trips to finish`, since one trip buys and delivers.

### When it shows, and settings

- **When it shows:**
  - In a **commodity market** at a station.
    - WFMT goes by the journal's `Market` event and also by the game rewriting `Market.json` (which it does the moment a market opens). The journal event can reach EDMC several seconds late on some setups (seen on Linux under Proton).
    - It hides when you leave the screen, open another service such as outfitting or the shipyard, or undock.
    - Backing out of the market to the station-services menu can't be detected, so the card stays until you leave that menu.
  - At **your own carrier**, in the station-services screens. The game writes nothing when you open a carrier's market,
    so any services screen shows it there, except after the carrier's outfitting or shipyard screens (which are
    logged).
  - Whenever you are **docked at a carrier** and have the **right-hand cockpit panel** open (where your cargo is and
    where you transfer to the carrier). The game writes nothing when you open that, so the open panel is what WFMT
    goes by; it hides when you close the panel or undock.
  - Whenever you are **docked at a construction site** (looking out of the cockpit or at the station services, but not
    in a map or another panel).
  - In the carrier's **Carrier Management** screen. The game announces both opening and closing it, so the card
    appears and goes exactly with the screen.
  - Optionally, **whenever the right-hand cockpit panel is open, anywhere** (even in flight). Off by
    default; tick **Also show whenever the right-hand cockpit panel is open, anywhere** in the Colonization settings.

  **Prefer to switch it yourself?** Leave the automatic option unticked and use the **Overlay** button beside Dashboard on the Colony page.
  - It turns the card on or off, whatever screen you are on.
  - The button lights up while the card is on. Its name does not change.
  - It works whether or not the automatic option is ticked, and it **stays as you left it, even after you restart EDMC**.

  Most of these rely on the game's `Status.json` reporting which screen is open.
- **Which site:** your most recently updated active site, the one the Colonization mode summary line names. Completed and
  failed sites are never shown. The card disappears when nothing is left to get.
- **Settings:**
  - Where the card sits: Settings → WFMT → Overlays → Overlay Placement. The default is the left edge, vertically centered, on any screen shape.
  - **Rows:** how many commodities to list (1 to 60; any more are summarized as `+N more`). The default, 0, lists them all.
  - **List** (**All**, **To buy** or **To haul**, the same choices as the window's **Show**) picks which rows the card lists. It is the same setting as the **Show** dropdown in the Sites window, so choosing one changes the other. **To buy** (the starting choice) leaves out the rows that already show a **✓**, so the card lists only what you still have to get; **To haul** lists the rows that are covered but not yet aboard your ship in full, for when everything is on the carrier. The last line still counts every commodity the site needs, and when no row is listed the card shows just that line. A choice made with the older *Hide commodities already covered* tick box carries over.
  - **Test Overlay** shows a sample card for about 8 seconds, even while the option is off, and says `Sent — check your overlay.` or that it could not reach the overlay.
- It is cleared when EDMC closes. If the overlay program isn't running, nothing is drawn and nothing breaks.

## What the game does and doesn't tell us, and how to work around it

WFMT, like every third-party tool, only knows what Elite Dangerous writes to its journal files.

- It adds what Frontier's servers give a signed-in EDMC (the carrier's real cargo), what Spansh reports (where to buy), what players enter on Raven Colonial (plans and progress) and a bundled table of building costs.
- It works around the rest by keeping its own tallies.
- Where it can't be sure, WFMT says so rather than guess quietly.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| What you might expect | What the game gives | What to do |
|---|---|---|
| Everything on your carrier to count | The journal only records cargo you **transfer** to or from the carrier. Stock that arrived any other way is invisible to it. Frontier's carrier data lists the real hold, but only when EDMC is signed in, and it is fetched when you open Carrier Management (or about every 15 minutes) and can lag, sometimes for longer than 15 minutes. WFMT ignores a lagging copy, so your own transfers are not undone. | Sign EDMC in to Frontier, then open Carrier Management once, at least 15 minutes after your last transfer; the Covered line and the Carrier row then follow the real hold. See [Scenarios](#scenarios-what-to-expect-and-what-to-do). |
| Colonization sites to appear on their own | The game writes the depot event only when you **dock or open the depot market**. A delivery to a site WFMT has never seen a depot snapshot for is ignored. | Dock at the depot (or open its market) once for each new site. Docking again replaces WFMT's figures with the game's own. Deliveries made with EDMC closed are caught up from the last 14 to 30 days of journals at start-up. |
| A site to have its real name, or a renamed site to follow | The name is taken from the last time you docked at that market. Otherwise it is `Construction site <number>`. The game does not announce a rename; it shows in the name the market has the next time you dock. | Dock at the market once to pick up the name, and again after a rename. |
| A full history of everything you ever delivered | The journal records each delivery as it happens. WFMT rebuilds your history once from every journal file you still have, so deliveries from journals you deleted are missing. | The history counts from the first delivery it found (shown in the History window) and keeps growing. |
| Your teammates' work on the same project | The depot reports only the project's totals, not who delivered what. | Today the page shows your deliveries and the project's overall progress. Team support is planned. |
| What is in your hold right now | The journal's `Cargo` event carries only a count, and EDMC's own cargo state was seen not to follow a purchase. The game rewrites `Cargo.json` on every change. | WFMT reads `Cargo.json` and reads it again about a second and a half after each cargo event. If the file is missing or describes your SRV, it uses the hold EDMC reports. |
| Builds you have only planned, or projects you have not docked at | The journal reports a construction site only when you dock at it or open its market. | Use Planned Builds and My Projects, which read what players have entered on Raven Colonial. They show other people's entries too, and a project nobody has entered shows nothing. |
| A free-form check of a market's prices | The game gives no way to query other stations' markets. | Where to buy asks Spansh, which holds players' market updates; only markets updated in the last 7 days are listed, and fleet carriers are opt-in. Confirm on arrival. |
