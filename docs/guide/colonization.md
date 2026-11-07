# Colonization

Colonization mode tracks colonization construction sites, the commodities each site still needs, the cargo in the ship and on the fleet carrier, and optional sharing with Raven Colonial. It is opened with the **Colony** button in the mode bar.

- The page shows the project currently under construction. With no site under construction, it lists the last 5 completed sites. The remaining history is in the History window.
- Three buttons are under the page, left to right:
  - **Dashboard** opens the [Colonization Sites window](#the-colonization-sites-window).
  - **Projects** opens [My Projects](#my-projects): all projects on Raven Colonial.
  - **History** opens the [history](#history) in its own window.
  - Each button has a tooltip describing its function.
- The page behaves the same for a commander with a fleet carrier and for one without. The wording changes accordingly, and the carrier lines are omitted when the commander has no carrier.

Colonization tracking is a work in progress. Several commanders on one project and colony tracking are not supported. The page covers the commander's own deliveries, ship and carrier.

**Data sources**

- The journal reports a construction site's totals when the commander docks or opens its market, and each delivery made.
- The ship's hold is read from the game's `Cargo.json` (next to the journals), which the game rewrites on every change. WFMT reads the file again about 1.5 seconds after each cargo event in case the game had not finished writing it. When the file cannot be read, or describes the SRV, WFMT uses the hold EDMC reports.
- The journal does not report who delivered what, and it records only cargo transferred to or from the carrier.
- WFMT adds the carrier's hold from Frontier's servers (through a signed-in EDMC), nearby stock from Spansh, plans entered by players on Raven Colonial, and a bundled table of building costs.
- WFMT keeps its own tallies of transfers for the remaining data.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

**On this page:** [How to](#how-to) · [The Colony page](#the-colony-page) · [Tracking a site](#tracking-a-site) · [The Colonization Sites window](#the-colonization-sites-window) · [Where to buy](#where-to-buy) · [My Projects](#my-projects) · [Planned builds](#planned-builds) · [The shopping list on the overlay](#the-shopping-list-on-the-overlay) · [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)

## How to

Each task list links to the section with the detail. Numbers in the examples throughout this guide are illustrative.

**View the current build**

1. Press **Colony** in the mode bar.
2. Read **Current project**: **Delivered** and **Still needed**, then **What you have** (with **Still to get**) and **To finish the build** (with **Trips left**). With no site under construction, the page lists the last five completed sites.
3. With more than one active site, the **Others** line shows the count. Press **Dashboard** to select a different site.

See [The Colony page](#the-colony-page).

**Track a new construction site**

1. Dock at the construction depot, or open its market, once.
2. Press **Colony**. The site appears under **Current project**. Press **Dashboard** to see it in the list.

See [Starting to track a site](#starting-to-track-a-site).

**Build a shopping list**

1. Press **Dashboard** and select the site on the left.
2. Use **Show** (**To buy**) and the **Filter** box to narrow the table.
3. Press **Copy Shopping List** (top right) and paste the text into a note or chat.

See [The Colonization Sites window](#the-colonization-sites-window) and [Buttons](#buttons).

**Find where to buy a commodity**

1. In the Sites window, select a commodity row.
2. Press **Where to Buy** in the window header.
3. Check **Around**, **Within**, **Sort** and **Landing pad**, then press **Find nearest** for that commodity, or **Find all** for the whole list.
4. Select a result row to copy its system name, then paste it into the galaxy map search.

See [Where to buy](#where-to-buy).

**Copy the list of what is still needed**

1. Press **Dashboard** and select the site.
2. If a transfer to the carrier did not register, press **Rescan Journals** first.
3. Press **Copy Shopping List** and paste the result.

See [Buttons](#buttons).

**Start a Raven Colonial project for a new site**

1. Tick the master switch, **Colonization: share progress and deliveries**, in **Settings → WFMT → Online**, then save the Raven key in **Settings → WFMT → Colonization → Raven Colonial** (the key is available at ravencolonial.com/user).
2. Dock at the new site. On the Colony page press **Create on Raven**, or in the Sites window select the site and choose **Raven Colonial → Create Project on Raven…**.
3. In the dialog, select the plan entry (or **None**), the Location, Building and Layout, then press **Create**.

See [Starting a project on Raven Colonial](#starting-a-project-on-raven-colonial).

**Archive a finished site**

1. Press **Dashboard**.
2. Choose **Manage Sites → Archive Finished**.
3. To view archived sites, choose **Manage Sites → Show Archive**. Select the site and press **Restore** to return it to the Sites window.

See [The archive](#the-archive).

**Show the shopping list on the overlay**

1. Start an overlay ([Setting up the overlay](../OVERLAY_SETUP.md)).
2. Tick **Always show the shopping list, whatever screen you are on** in **Settings → WFMT → Overlays → Colonization**.
3. Clear the checkbox to turn the card off. The choice is stored across restarts. The **Overlays shown (click to hide)** line at the top of the WFMT panel hides every overlay, including this card, until it is clicked again.

See [The shopping list on the overlay](#the-shopping-list-on-the-overlay).

## The Colony page

**Current project** is the most recently updated active site. The page has three sections:

| Section and line | Content |
|---|---|
| Name, system and a bar | The site and the progress of its build. The bar is green when the build is complete. |
| Body | The body of the site, as named by Raven Colonial's plan. The lookup runs once per site per session, the first time the site is the current project, and the result is stored. The line is omitted when Raven does not report the body or cannot be reached. |
| Delivered | Tons handed over by all commanders against tons needed, with the build percentage (`1,200 of 8,000 t (15%)`). |
| Still needed | Tons left to deliver. When nothing remains, the line reads `Nothing: the build is complete` or `Nothing: dock at the site to finish the build`. |
| **What you have** | |
| In your ship | Tons of needed commodities in the ship (read from `Cargo.json`). |
| On your carrier | Only with a fleet carrier. Tons of needed commodities transferred onto it. |
| Still to get | Tons left to buy or mine after the ship (and carrier). |
| **To finish the build** | Omitted when nothing remains to deliver. |
| Commodities | Of the commodities still needed, the number **done** (fully covered), **partly** covered and **working on it** (not covered): `3 done - 2 partly - 5 working on it (of 10 commodities)`. Coverage counts the ship, or the ship and carrier together. |
| Trips left | Without a carrier: the loads of the current ship needed to finish (`4 loads of 400 t`; one trip buys and delivers). With a carrier: `N to buy · N to haul (400 t ship)`. `Unknown (ship size not seen yet)` until EDMC has reported the ship's cargo capacity. |
| Biggest gaps (t) | The three commodities with the most tons still to get, with their tons. Omitted when nothing is left to get. |
| Others | `+N more active sites` when more than one site is active. Omitted otherwise. |

**No site under construction.** The page shows `No active construction site. Dock at one to register it.`, followed by the **Last 5 completed** sites, newest first, each as `Name (System) - date`. The date is omitted for a site finished before WFMT kept the completion date. Archived sites are included. Before WFMT knows the commander, the page shows `Waiting for commander login`.

**Example (illustrative numbers).** Building an outpost that needs 8,000 t, with 1,200 t delivered, a fleet carrier and a 400 t ship:

```
Delivered         1,200 of 8,000 t (15%)
Still needed      6,800 t

What you have
In your ship      180 t
On your carrier   120 t
Still to get      6,500 t

To finish the build
Commodities       3 done - 2 partly - 5 working on it (of 10 commodities)
Trips left        9 to buy · 17 to haul (400 t ship)
```

Ten commodities are outstanding. Three need nothing more. Nine loads are needed to buy the remainder and seventeen to haul everything to the site.

**Offer to start a Raven project.** When a construction site appears for the first time and [Raven Colonial](https://ravencolonial.com) has no project for it, a line above **Current project** reads `Raven Colonial has no project for <site>.` with two buttons.

- **Create on Raven** opens the Colonization Sites window on the site and its [Create dialog](#starting-a-project-on-raven-colonial).
- **Not Now** hides the line.
- The offer is made once per site and disappears once a project exists.
- It requires the master switch on, progress sharing on and a saved Raven key, because WFMT looks at Raven for a site only when it is permitted to share.

**Finished builds.** The game names a depot `Orbital Construction Site: Example Station` while it is being built. After the build completes, WFMT drops the `Construction Site:` part (`Example Station`) in the Sites window, the shopping list and the history.

### History

History is per commander and is kept off the page. Press **History** to open the Colonization History window, which names the commander under its title. The window has four tabs:

- **Overview**
- **By day**: tons delivered on each day (UTC), newest first. Only days with a delivery are listed.
- **Commodities**: everything delivered, most first.
- **Sites**: every depot delivered to, most first.

A help button in the window header repeats the notes. The window stores its size and position and follows the commander on a login as another commander. A row with no content (for example Best day before any delivery) is omitted from the Overview.

| Overview line | Content |
|---|---|
| Sites | Number of tracked sites done, in progress and failed. |
| You delivered | Tons and number of deliveries made by the commander. |
| Recently | Tons in the last 7 and 30 days. |
| Best day | The largest single day. |
| Busiest site | The site with the most tons delivered, with the tons. A delivery in the journal names the depot only by a number, so WFMT takes the name and system from the time the commander docked there (it reads the journals for this once and stores the result). A depot never docked at in a journal shows as `Construction site <number>`. |
| Claims | Number of systems claimed (`ColonisationSystemClaim`), number released, and number of colonization beacons deployed. These are counts only: the game does not report when a claim ends, so WFMT does not list which systems are still claimed. |
| Average build | Days from the first time WFMT saw a site to the day the depot reported it complete, over the sites for which both are known. |
| Counted since | The first delivery WFMT has counted. |

**Example.** To review recent activity, press **History**, open **Overview** and read **Recently** (for example `3,200 t this week · 9,800 t this month`) and **Best day**. **By day** lists the days that make up the week, **Commodities** lists what was moved most, and **Sites** lists which depot received the most.

**History depth**

- The game keeps no delivery history for a plugin to read, but the journal files contain one.
- The first time WFMT sees a commander, it reads all of that commander's journals once, in the background, and rebuilds the history from every delivery in them.
- After that, each delivery is counted as it happens.
- When EDMC starts, WFMT catches up from the recent journals (14 days, or back to the oldest active site, never more than 30).
- Deleted journals cannot be read. The History window shows the date from which it is counting.
- A rebuild never replaces figures that are larger than it can find.

**Notes on the figures**

- A site's build time is known only for a site WFMT saw being started or finished. Other sites are left out of the average.
- The tons under **Delivered** at the top of the page are the totals of all commanders, because the game reports them for the whole depot. **You delivered** counts the commander's own deliveries only.

## Tracking a site

WFMT tracks what each colonization construction site still needs delivered.

- The data can be read from anywhere, not only while docked.
- The page shows what remains to be found after counting the cargo already in the ship.
- There is no on/off setting for site tracking.

**Data source.** The journal writes a `ColonisationConstructionDepot` event when the commander docks at a construction depot or opens its market, and a `ColonisationContribution` event for each cargo delivery.

### Starting to track a site

1. Dock at the construction depot, or open its market, once. No input is required.
2. The **Colony** page shows the site under **Current project**. It is the most recently updated active site, with a line `+N more active sites` when others exist.
3. Press **Dashboard** to open the **Colonization Sites** window.

A site that has been flown past without docking or opening its market does not appear. After the first dock, the site appears under **Current project** with the name the game gave the depot's market, and in the list in the Sites window with its tons in **Left** and a percentage in **Status**.

### Who is playing

At start-up WFMT takes the commander from the newest journal (the last login in it), so the Colony page shows the commander's sites immediately. After a login as another commander, the page and the open Colonization windows follow that commander.

### The site name

- The name is the one the game gives the depot's market when the commander docks there.
- If WFMT has not seen the commander dock there, the site is named `Construction site <number>`.
- Docking again after a rename in the game updates the name (and the system, if it changed).
- Raven Colonial keeps a separate list. A rename in the game must be repeated there, otherwise WFMT cannot match the two by name.
- **Your own name.** Select a site (or an archived site) and choose **Manage Sites → Rename Site…** (in the Archive, **Manage → Rename Site…**). The name you type is shown everywhere WFMT names the site: the Sites window, the overlay card, the History, the Archive and the copied text. It is kept in WFMT only: the game's name and Raven Colonial are not changed, and docking there again does not undo it. Leave the box empty, or type the game's own name, to go back to the game's name. A name has at most 80 characters.
- WFMT still uses the game's name to find the site's project on Raven Colonial, so a name of your own never breaks that match.

### Keeping it right

Each time the commander docks or opens the depot market again, WFMT replaces its figures with the game's figures. Between visits, WFMT adds the deliveries reported in the journal. All data is stored per commander.

### Deliveries made with EDMC closed

Deliveries made while EDMC was closed are found again when EDMC starts.

- WFMT reads the recent journals (14 days, or back to the oldest tracked site, never more than 30) and applies each depot snapshot and delivery once.
- A site docked at during that time is registered.
- A delivery to a site for which no journal in that window has a depot snapshot is ignored, because there is nothing to add it to.

## The Colonization Sites window

Sites are listed on the left under four headings: **Site** (the name), **Left** (tons the site still needs), **Raven** (Raven Colonial's own figure for the site, empty until you press **Refresh from Raven**; see below) and **Status** (progress as a percentage, or `complete` or `failed`). Finished sites are grayed. The subtitle reads `<commander> — N active of M sites`. With no sites, the list shows `No construction sites yet - dock at a construction depot to register one.` The window stores its size and position.

Select a site to view it on the right. The first active site is selected when the window opens. The right side contains:

- The site name and system.
- A progress bar.
- Six totals.
- A **Filter** box, a **Show** drop-down (**All**, **To buy**, **To haul**) and two checkboxes (**Only what this station sells** and **Group by category**).
- A table with one row per commodity still outstanding.

A **Raven Colonial** strip across the top is described in [Sharing your progress with Raven Colonial](#sharing-your-progress-with-raven-colonial).

### The six totals

The totals always apply to the whole site, regardless of the filters. A commander without a fleet carrier sees four of them: the carrier tile and *trips to buy* are omitted, and *trips to haul* is captioned **trips to finish** (one load is bought and delivered in one trip).

| Total | Content |
|---|---|
| t still to get | Tons still to buy or mine: what the site still needs, less the cargo in the ship and the cargo transferred to the fleet carrier. It equals the sum of the table's Acquire column. |
| t on your carrier | Of the remaining need, the tons transferred to the carrier (never more than the site needs). A dash without a carrier. |
| t already in your ship | Of the remaining need, the tons in the ship now (never more than the site needs). |
| t ship capacity | Cargo capacity of the current ship as reported by EDMC. It follows ship changes. A dash until EDMC has reported it. |
| trips to buy | Loads of that capacity needed to gather what is still to get, rounded up. 0 once everything is in the ship or on the carrier. |
| trips to haul | Loads of that capacity needed to carry all the tons the site still needs to the site, rounded up. The cargo in the ship is the start of the first load, and cargo on the carrier still has to be carried to the site, so this value does not fall when cargo is moved to the carrier. |

Building a colony has two legs, counted separately:

- **Buying** moves cargo from the markets to the carrier (or directly to the site).
- **Hauling** moves cargo from the carrier, or the ship, to the construction site.
- A commodity already stored on the carrier needs no more buying trips but still needs hauling trips.

### Filters and sorting

- The **Filter** box keeps the commodities whose names contain the typed text.
- **Show** selects the stage of the work. See the row colors below for what counts as covered. It starts at **To buy** until a choice is made, then keeps the choice. The [shopping-list overlay](#the-shopping-list-on-the-overlay) lists the same rows, so changing **Show** changes the card at once. The **Filter** box and the two checkboxes apply to the window only.
  - **To buy** lists the rows not yet covered.
  - **To haul** is for the step after everything is bought and stored on the carrier. It lists the rows that are covered but not yet fully aboard the ship. A row leaves the list when its whole need is loaded, and the site drops it when it is delivered.
  - **All** lists every commodity the site still needs.
- **Only what [station] sells** keeps only the commodities the docked station has for sale. Once the station's commodity market has been opened, the checkbox names the station (clipped to 24 characters) and becomes usable. Until then it is grayed. It switches off on leaving the station.
- A column heading sorts by that column. A second click reverses the order. The default order is alphabetical.
- The status line at the bottom states how many commodities are still needed, how many the ship (and carrier) cover, and the trips: `Your 400 t ship needs 21 trips to buy what is missing and 33 to haul it all to the site.` When the filters hide every row, the line reads `The filters hide every commodity this site still needs.`

**Example: shopping at a station.** The commodity market of the station has been opened once.

1. In the Sites window, select the site and set **Show** to **To buy**.
2. Tick **Only what [station] sells**.
3. The table lists commodities that are still short and sold at this station. As cargo is loaded, the **In Cargo** and **Acquire** columns change. A row drops out of **To buy** once it is covered.
4. Type `steel` in **Filter** to show only that commodity.

### The table columns

| Column | Content |
|---|---|
| Required | Total the site needs. |
| Delivered | Total handed over. |
| Acquire | What remains to be obtained: Required minus Delivered, less the cargo in the ship and the cargo transferred to the fleet carrier. It reaches 0 once everything is held, wherever it is stored, and falls as cargo is loaded. |
| In Cargo | Cargo in the ship (or SRV) now. |
| FC | Tons of the commodity transferred onto the **fleet carrier**. Shown only once WFMT has seen the commander has a carrier. |
| Buy Trips | Only with a fleet carrier. Loads of the current ship needed to gather what is still missing of the commodity: Acquire divided by the ship's cargo capacity. 0 when enough is held, wherever it is stored. |
| Haul Trips | Loads of the current ship needed to carry everything the site still needs of the commodity (Required less Delivered) to the site. It stays above 0 for a commodity on the carrier, because it still has to be moved. |
| Trips | Without a fleet carrier, one trips column replaces the last two: the loads of the ship needed to buy and deliver the commodity. |

The trip columns show at most two decimals (`4`, `1.5`, `1.25`, `0.33`), never round a small remainder down to 0, and show a dash until EDMC has reported the ship's capacity.

**Example row (illustrative numbers).** Steel, with a fleet carrier and a 400 t ship:

| Required | Delivered | Acquire | In Cargo | FC | Buy Trips | Haul Trips |
|---|---|---|---|---|---|---|
| 1,000 | 200 | 300 | 100 | 400 | 0.75 | 2 |

The site needs 800 t more (1,000 less 200). The ship holds 100 t and 400 t were transferred to the carrier, leaving 300 t to acquire. At 400 t per load this is 0.75 of a buying trip and 2 loads to carry all 800 t to the site. The row has no tint because the commodity is still short.

### Row colors

The whole row is tinted according to what is held for the commodity, counting the ship plus the cargo transferred to the fleet carrier (the FC column):

- **Green:** together they cover what the site still needs, exactly or with a surplus. Nothing more to buy.
- **Orange:** together they exceed what the site still needs.
- **No tint:** the commodity is still short.
- **Under the To haul filter** the colors differ, because every listed row is already covered. There is no green. Rows in the ship's hold (those being hauled) get their own tint, a blue-violet that follows the selected theme (Navy, Cyan, Amber or Green). A row held in surplus but not in the hold keeps its orange.

The carrier figure is what WFMT saw transferred (see the FC column), so it can differ from the carrier's actual cargo.

- The **t still to get** total and the copied shopping list count the carrier figure and drop when cargo is moved onto the carrier. Buy Trips behaves the same.
- Haul Trips does not drop, because everything still has to be carried to the site.

### The FC column

The FC column sums the journal's `CargoTransfer` events made while docked at the commander's fleet carrier: tons moved to the carrier minus tons moved back to the ship. It lowers the **t still to get** total. It is per commander.

**When it appears.** The column appears for a commander WFMT knows has a fleet carrier, using the same knowledge as Trade:

- The commander's choice in the Trade settings (None, Fleet, Squadron, Both or Auto) decides when the carriers are named.
- On Auto, a fleet carrier that Trade has recorded counts. Trade reads the recent journals at start-up and stores them.
- Otherwise the column appears once WFMT has seen a carrier of the commander (a transfer, opening Carrier Management, buying one, or docking at one).

**Rules**

- **Transfers made with EDMC closed are found.** At start-up WFMT reads the recent journals and adds any transfer it has not counted. A transfer is never counted twice, even if EDMC also saw it live.
- **Read depth:** 14 days, or back to the last counted transfer if that is older, never more than 30 days. Transfers older than that are not counted. Taking cargo back off the carrier that was moved earlier leaves the figure at zero.
- **The figure is the tally of observed transfers, not the carrier's actual hold.** Changes that are not transfers are not counted: buying from or selling to the carrier's market, trade orders, and cargo moved by a squadron member.
- **Frontier's figure can replace the tally** under the rules in the next section.

### How Frontier's figure and transfers fit together

Two sources feed the FC column.

- **Transfers** (the journal) are exact and immediate, but cover only what the commander moved.
- **Frontier's figure** is the carrier's actual hold, available only when EDMC is signed in to Frontier. EDMC requests it when a carrier event such as Carrier Management opens, at most every 15 minutes, and Frontier's copy can lag behind the latest changes.

A lagging copy would undo the most recent unload if every Frontier figure replaced the tally. WFMT therefore applies these rules to each Frontier figure:

1. A figure that matches the tally changes nothing.
2. A figure that differs, within 15 minutes of the last transfer, is ignored. The figure may not include that transfer yet.
3. A figure that differs but repeats a copy already ignored is ignored, for up to one hour after it was first ignored. Frontier has not updated. After one hour the repeated copy is applied.
4. Any other figure replaces the tally. Transfers made afterwards are added on top.

The ignored copy is stored in the saved carrier file, so restarting EDMC does not discard it. **Rescan Journals** clears it.

**Log lines.** Each Frontier figure writes one line to EDMC's log (Help → Open Log Folder in EDMC):

| Log line | Meaning |
|---|---|
| `Carrier cargo from Frontier: 18806 t against 18806 t tallied (same)` | Frontier agrees with the tally. Nothing changed. |
| `Carrier cargo from Frontier: 15011 t against 18806 t tallied (changed)` | Rule 4. The tally now follows Frontier's figure. |
| `Carrier cargo from Frontier ignored: ... (the last transfer was 291 s ago)` | Rule 2. |
| `Carrier cargo from Frontier ignored: ... (unchanged since an earlier fetch)` | Rule 3. |

To report a column that appears wrong, press **Copy diagnostics** soon afterwards. These lines are among the WFMT lines it copies (see [Reporting problems](reporting-problems.md)).

### Rescan Journals: when a load did not register

Two actions correct the FC column, for different problems.

- **Opening Carrier Management** in the game (with EDMC signed in to Frontier) brings in the carrier's actual hold from Frontier. Use it after taking cargo off the carrier or when others have moved stock.
- **Rescan Journals** reads the commander's journals again. Use it when a transfer made by the commander did not register, or when a delivery or site is missing. It also folds in the last 30 days of site activity and rebuilds the delivery history. It works for a commander with no fleet carrier as well (the carrier step is skipped).

**Rescan Journals** is at the top right of the Colonization Sites window. For the commander shown in the window it does up to three things:

1. **Sites.** It reads the journals of the last 30 days and folds in any delivery or depot visit a site has not seen, by the same newest-only rule as the start-up catch-up, so nothing is counted twice.
2. **Delivery history.** It reads all journals again and rebuilds the figures on the History page. Saved figures that are larger (because older journals were deleted) are kept.
3. **Fleet carrier** (only with a carrier). WFMT discards its saved carrier tally, including any Frontier figure, reads the last 30 days of journals oldest first and counts every transfer made while docked at the fleet carrier: tons moved to the carrier minus tons moved back to the ship.

The status line at the bottom states how many site updates were applied and, with a carrier, how many commodities and tons were found. Transfers made afterwards count on top.

Limits:

- Only transfers shown in the journals are counted. Cargo that reached the carrier another way (bought through its market, a trade order, a squadron member), or moved more than 30 days ago, is not included.
- A later Frontier figure replaces the rescanned tally only if it has changed and the last transfer is more than 15 minutes old (see [How Frontier's figure and transfers fit together](#how-frontiers-figure-and-transfers-fit-together)). A rescan also clears any Frontier copy WFMT was ignoring, so the next figure is judged as new.
- Rescan Journals can be pressed repeatedly and never counts a transfer twice. It affects only the commander shown in the window and reads local files only. Nothing is sent.

### Scenarios: what to expect and what to do

| Situation | Behavior and action |
|---|---|
| Unloading at the carrier, then buying another load | The column keeps the unloaded stock. If Frontier's copy arrives and lacks the unload, WFMT ignores it. No action required. |
| Several trips in a row | Each unload adds to the tally, and every Frontier figure is checked against it. The column keeps climbing even if Frontier's figure stays at an old value. The log shows `ignored` lines. |
| The column is higher than the carrier's actual hold | WFMT counts transfers, so the figure is high when stock left the carrier without a transfer by the commander (sale from the carrier's market, a filled trade order, a squadron member taking cargo). Correction: (1) make no transfers for 15 minutes; (2) open Carrier Management in the game (EDMC signed in to Frontier); a figure that has moved replaces the tally; (3) if the log says `unchanged since an earlier fetch`, Frontier has not updated: open Carrier Management again later (a repeating copy is applied once an hour has passed since it was first ignored), or press **Rescan Journals**. |
| The column is lower than the carrier's actual hold | Stock reached the carrier without a transfer by the commander, or was moved more than 30 days ago. Apply the same three steps. **Rescan Journals** does not help, because it counts only the commander's own transfers. |
| A moved load never appeared | The game did not write the transfer, or EDMC was closed and the transfer was not caught up. Press **Rescan Journals**. A transfer present in the journals is counted, and never twice. |
| Cargo taken off the carrier to the ship | This is a transfer. The column drops at once. No action required. |
| EDMC is not signed in to Frontier | There is no Frontier figure. The column contains transfers only. Sign EDMC in to Frontier and open Carrier Management. Until then, **Rescan Journals** is the only correction. |
| Playing with EDMC closed | At the next start WFMT reads the last 14 to 30 days of journals and adds uncounted transfers. Press **Rescan Journals** only if one is still missing. |
| The column stays on an old Frontier value known to be wrong | Check the log. If every line says `ignored`, Frontier's copy is not updating, which occurs on Frontier's side. Press **Rescan Journals** to rebuild from the journals, or move some cargo, wait 15 minutes and open Carrier Management again. |
| The column drops after opening Carrier Management | Frontier's figure had changed and the last transfer was more than 15 minutes old, so WFMT took Frontier's figure as the actual hold. If a load is missing from it, Frontier's copy was updated only partly. Press **Rescan Journals**. |

**Example sequence.** Continuing the steel row above, where **Acquire** was 300 t:

1. 300 t of steel is bought. **Acquire** falls to 0 as the cargo is loaded, and the row turns green because the ship and carrier together cover the 800 t the site still needs.
2. If 350 t had been bought, the total would exceed the need and the row would turn orange.
3. The cargo is carried to the site and delivered. The row leaves the table once the site has it all.

### The commodity table: grouped, like the overlay

The commodity table is the shopping list, with the same order and graying as the overlay.

- **Group by category** (a checkbox above the table, on by default, stored) places the commodities under a heading for each market category (Chemicals, Foods, Industrial Materials, Machinery, Metals and so on).
  - Each heading shows the tons still to get under it (the sum of their Acquire figures). The commodities under it are alphabetical.
  - A click on a heading folds or opens its group.
  - Clearing the checkbox, or clicking a column heading to sort (a second click on the commodity column reverses), gives a plain sorted list.
- **Grayed out when the market does not sell it.** While docked at a commodity market that WFMT has seen, a commodity that the market does not sell is shown in faint gray with **(not available here)** after its name, unless the ship and carrier already cover it (it keeps its green or amber tint). This marks rows only; **Only what this station sells** hides them.

## Where to buy

**Where to buy** finds the closest places to buy a commodity. It has its own window, opened with **Where to Buy** in the header of the Colonization Sites window. The window stores its size and position, opens with the selected commodity and the site's system filled in, and closes with the Sites window.

1. In the Sites window, select a commodity row. The Sites window footer shows the next step, the **Commodity** line of the Where to Buy window names the commodity, and the note reads `Ready to search for <commodity>. Press Find nearest.` Selecting another row or another site updates the open window.
2. Check the options.
3. Press **Find nearest**. While the search runs, the note is shown in the accent color and the button is disabled.

With no row selected, the window asks for a selection. With no system in the **Around** box, it asks for a system or the **Here** button. The same search repeated within two minutes is answered from memory instead of being sent to Spansh again.

The search uses [Spansh](https://spansh.co.uk), a community-run map of the game, and requires an internet connection.

- Nothing is fetched until a search button is pressed.
- Only the commodity name and the system searched around are sent.

**Example: finding Steel for a site.** The site is in a system other than the current one.

1. Select the **Steel** row in the Sites window, then press **Where to Buy**. The note reads `Ready to search for Steel. Press Find nearest.`
2. Leave **Around** as the site's system (or press **Here** to measure from the current system), keep **Within** at 50 ly, and leave **Preset** on the default (or select **Large ship**).
3. Press **Find nearest**. The table lists stations with Distance, Arrival, Price and Supply.
4. Select a result row. The note states that the system name was copied. Paste it into the galaxy map search.
5. If no result is returned, raise **Within** or set **Landing pad** to **Any size**, and search again.

### Current system first

This behavior applies to Where to Buy only (Trade, Missions, Mining and the other finders do not use it). Before searching elsewhere, WFMT searches the system the commander is in (the system WFMT last saw, regardless of the **Around** box).

- If a station there has the commodity in stock, those stations are the result and nothing outside is searched.
- If none does (a station hidden by the exclusion options does not count), WFMT searches around the **Around** system, and **Sort** and the filters decide the order (closest first by default).
- **Find all** does the same for each commodity, at the cost of one additional Spansh request per commodity.

### Presets

The **Preset** list sets the options below in one step. Every preset sorts closest first and excludes fleet carriers. Any option can be changed afterwards; the list then reads **Custom**. The surface, arrival, stock and shipyard choices redraw the table at once. The other options (preset, pad, within, sort, carriers) require a new search, and a note beside the list states this until a search is run.

| Preset | Settings |
|---|---|
| Large, then Medium (default) | Landing pad **Large, then Medium** |
| Large ship | Landing pad **Large only** |
| Medium ship | Landing pad **Medium or larger** |
| One trip (enough stock) | **Large only**, and only stations with enough stock |
| Quick top-up (25 ly, orbital) | **Large only**, within 25 ly, no surface ports, arrival within 2,500 ls |
| Orbital only (near arrival) | **Large, then Medium**, no surface ports, arrival within 1,000 ls |
| Shipyard stops | **Large, then Medium**, only stations with a shipyard |

**Large, then Medium** searches stations with a Large pad first (the current system, then outside). Only when no Large-pad station in range has the commodity does it search stations with a Medium pad or larger, and the note then states this.

### The options

| Option | Content |
|---|---|
| Around | The system to measure from. It starts as the site's system and follows the selected site until another system is typed. System names autocomplete. **Here** uses the current system and reports if WFMT has not yet seen the current system. |
| Within | Search radius: 25, 50, 100, 200 or 500 ly, or no limit. Default 50. |
| Sort | **Closest first** (default) or **Cheapest first**. This decides which stations Spansh returns, not only their order. A click on a result heading re-sorts the returned stations. |
| Landing pad | **Large, then Medium** (default), **Large only**, **Medium or larger** or **Any size**. Any size lists stations whose largest pad is small, for switching to a smaller cargo ship when a commodity is not sold at a large-pad station. The **Pad** column shows each station's largest pad. |
| Exclude fleet carriers | On by default. Clearing it includes carriers. They are searched separately and listed under their own **Fleet carriers** heading after the stations (one more request per commodity). |
| Exclude surface ports | Off by default. Ticking it omits stations on a planet's surface (planetary ports) from the lists and from the route. It changes what is shown, not what is requested from Spansh, so changing it after a search redraws the results at once. The stock, shipyard and arrival choices work the same way. |
| Only stations with enough stock | Off by default. Omits any station holding less of a commodity than remains to be obtained (the Sites window's **Acquire** figure), so every listed station can fill the commodity in one visit. It follows purchases as the need shrinks. |
| Only stations with a shipyard | Off by default. Keeps only stations with a shipyard. Spansh reports it for each station, so it costs no extra request. |
| Arrival within | **No limit** by default, or 500, 1,000, 2,500, 5,000, 10,000 or 25,000 ls. Omits stations farther than this from their arrival star. A station whose distance is unknown is kept. |

The options preset, within, sort, landing pad, and the exclude, stock, shipyard and arrival choices are stored for the next time the window opens. Choices saved by an earlier version give way to the new defaults, keeping only **Within**. The search system is not stored: it starts as the site's system.

### Find all

**Find all** searches every commodity that remains to be bought, using the same options. It lists the closest 5 stations (and, when fleet carriers are included, the closest 2 carriers) under a heading for each commodity. A commodity that a station in [the current system](#current-system-first) sells is answered from the current system alone.

- It follows the table as filtered. Rows already covered are omitted, and so are rows hidden by the Filter box, **Show** or **Only what [station] sells**.
- Spansh looks up one commodity per request. WFMT therefore sends one request per commodity, 0.4 second apart, plus one more request for the nearest stations that have every commodity on the list in stock (see below).
- The note under the buttons shows progress, in amber while a search is running. A large **Search is underway...** also fills the empty area below (the tabs stay usable) and disappears when the search ends or is stopped.
- While it runs, **Find all** is relabeled **Stop** and **Find nearest** is disabled. **Stop** ends the search after the search in progress and keeps what was found (the note shows `(stopped early)`).
- A commodity that fails is named and the others still show. Press **Find all** again to retry.
- Commodities with no source in range are listed in the note.

**A station that sells the whole list.** The extra request finds stations (and carriers, unless excluded) that have every commodity being searched in stock.

- Stations found are added under each commodity with that commodity's price and stock, so the route can use a station that is not among the nearest few for any single commodity.
- For a long list Spansh usually has no such station, and nothing is added.
- If this request fails, Find all continues without it.

**Request reduction**

- The whole-list request goes first. A commodity that one of those stations can supply in full is not searched on its own (the answer comes from that station's market), so a list that one station can fill takes a single request.
- After the searches, if the route still leaves two or more commodities uncovered, one more request asks for stations that have all of those in stock. The whole market it returns also fills in any other commodity on the list that those stations sell.
- A commodity whose every found seller is on a planet's surface costs one more request, for orbital stations alone (see [Suggested route](#suggested-route)).

**Example: planning the whole list.** Twelve commodities remain to be bought.

1. In the Sites window, set **Show** to **To buy**, so covered rows are omitted.
2. In Where to Buy, set **Within** to 100 ly and press **Find all**. The note shows progress. **Stop** ends the search early and keeps the results.
3. Read the **Next stop** card at the top of the **Suggested trip** block: where to go and what to buy there. Press **Copy next system** and paste it into the galaxy map search. Below the card, the whole trip is listed in flying order with the price and stock of every item. Anything the trip cannot cover is named in the note.
4. Buy what the card lists. When the hold (or carrier) has the goods, the stop is ticked off and the card moves to the next stop. After the last stop the card states to deliver at the site.
5. Press **Copy Route** to copy the plan as text.

### Suggested route

Find all also computes a shopping trip and shows it on its own tab, **Suggested route** (the first tab; the **Closest stations** tab beside it holds the per-commodity lists; the route scrolls when long), headed **Suggested route to buy what you need...**. The trip has at most 6 stops that between them supply the most of what remains to be obtained.

- **The Next stop card.** At the top of the block: the stop's position in the trip (`Next stop: 2 of 4`), the station and system with the jump distance and its notes (pad, surface port, fleet carrier), and `Buy: Steel 120 t, Titanium 80 t`. When the commander is already in that system, the card says so. **Copy next system** copies the system name. **Skip this stop** omits the stop and plans the trip again without it (its goods go to other stops, or are named as not covered).
- **Done stops remain.** A stop at which purchases were made, or whose goods are now held, is ticked and grayed (**done**; **skipped** if skipped) instead of disappearing, and the heading counts them (`1 of 4 done`). When every stop is done, the card states to deliver at the site. Changing a filter plans the trip afresh, so the ticks restart.
- A station that sells several of the needed commodities counts for all of them, so it is taken first. Ties go to the nearer station, then the cheaper.
- Each stop shows what to buy there, with the price per ton and the stock (**Supply**) at that stop. A click on a stop copies its system name. The stop's **Notes** also give the body (as Spansh names it, without the system's name) and the age of its market data, such as `data today` or `data 12 days old`. The data is what players' game clients last reported.
- The stops are ordered for the shortest flight: every order is tried (there are at most six stops), starting from the search system. **Jump** is the distance from the previous stop, and the heading gives the whole trip in light years. If Spansh gives no position for a stop, the jumps are blank and the stops are ordered nearest to the search system first.
- What no station in range can supply is named in the note.
- **Surface ports.** A stop on a planet's surface is marked **Yes** in the **Planetary** column. When a commodity is sold only at surface ports among the stations found, Find all makes one more request for each such commodity asking for orbital stations alone, because the nearest sellers can all be on planets and push the orbital ones out of the list. Only if that finds nothing is the commodity planned at a surface port, as a stop noted as a surface port (landing on the planet is required). Orbital and surface ports are both searched unless **Exclude surface ports** is ticked. With it ticked, those commodities are left out of the route and the lists. A collapsed group at the top of the route block, **IMPORTANT: Surface Port Requirements**, names each one (one commodity per row), the commodity's heading says **surface ports only (left out)**, and the note repeats it.
- **It follows purchases.** When purchased cargo reaches the ship's hold or the fleet carrier (or is delivered), the route and the lists are recomputed from the stations already found, with no new search. A commodity now held in full leaves the route and its heading disappears. A commodity partly held shrinks to the tons still to get. The tons come from the Sites window's **Acquire** column. The note under the buttons is left unchanged, except to state when everything is bought.
- Only the stations returned by Find all are considered (including any that sell the whole list): the nearest 25 per commodity within the radius.
- **Copy Route** copies the route as plain lines; each stop's line also gives its body and the age of its market data.
- **Route order.** The **Route order** list at the top of the route tab sets the order of the stops: **Default (shortest flight)** is the order above; **Smallest purchase first** or **Largest purchase first** order the stops by the tons to buy at each stop; **Farthest stop first** starts at the stop farthest from the search system and works back toward it. The stops are the same in every order; only their sequence and the jump from each to the next change (the heading's total follows). Changing the order redraws the route at once and requests nothing from Spansh.
- **Expand all and Minimize all.** Each tab has an **Expand all** and a **Minimize all** button for its sections (a stop on the route, a commodity on the lists). Only the first section on each tab starts open. Sorting or changing a filter keeps the sections as they were, and a new search resets them to the defaults.

### Reading the results

The results table has the columns **Station**, **System**, **Type**, **Planetary**, **Pad** (largest landing pad), **Distance** (light years from the Around system), **Arrival** (distance from the arrival star, in ls), **Price** (per ton) and **Supply** (the stock). **Find nearest** lists up to 25 stations and, when fleet carriers are included, up to 10 carriers. The filters in the third and fourth rows (surface ports, stock, shipyard, arrival distance) change only what is shown. The note states how many stations they omitted, and loosening a filter restores them without a new search.

- **Planetary: Yes** means a base on a planet's surface, which requires descending to land (planetary ports and outposts, settlements).
- **Planetary: No** means an orbital station, asteroid base, megaship or fleet carrier, which is docked at in space.
- A click on a heading sorts by it.
- The window has two tabs under the options: **Suggested route** (first) and **Closest stations**. A Find all that produces a route opens the first; a Find nearest opens the second.
- **A click on a result row** (a station, or a stop in the suggested trip) copies its system name for the galaxy map search. The note under the buttons states what was copied. Headings and the "buy" lines under a trip stop copy nothing.
- **Copy System** does the same for the selected row (it asks for a result row if none is selected).
- **Copy Route** requires a **Find all** first. It copies the trip as plain lines, with each jump and the total.

### Things worth knowing

- Only stations whose market was updated in the last 7 days are listed. Prices and stock come from players' own market updates.
- A fleet carrier can move or sell out at any time, and its prices are set by its owner. Carriers are therefore kept in their own section and can be left out with **Exclude fleet carriers**.
- The stock, shipyard, arrival and surface-port filters act on the stations Spansh returned (the nearest 25 per commodity within the radius, 5 shown per commodity in Find all). If a filter leaves a commodity with nothing, a qualifying station may exist farther out: widen **Within**, sort by **Closest first**, or loosen the filter. "Surface Port Requirements" likewise means no orbital port among the stations found.
- A station for which Spansh gives no pad figures is kept in the list (its Pad shows `?`).
- If Spansh is busy or unreachable, the panel states that the search failed. Nothing else in WFMT is affected.
- The search covers stock that is for sale. It does not know what a station's market will have later.

### Buttons

The window header, top right. All of the buttons act on the site selected on the left.

- **Copy Shopping List** (highlighted) copies the site's list to the clipboard: a first line such as `Example Outpost (Example System) - still to get:`, then lines like `1,200 t  Steel`, largest first. Cargo in the ship and on the fleet carrier is already subtracted.
- **Rescan Journals** reads the journals again for the sites, the delivery history and (with a fleet carrier) the carrier tally; see [Rescan Journals](#rescan-journals-when-a-load-did-not-register).
- **Raven Colonial** (a menu): **My Projects**, **Planned Builds**, **Raven Progress**, then **Open Selected Build on Raven**, **Open This System on Raven**, **Raven Colonial Website**, then **Create Project on Raven…**, **Report Complete to Raven** and **Mark Plan Entry Demolished…**. The last three write to Raven Colonial; the ellipsis indicates a following question. See [Planned builds](#planned-builds), [Starting a project on Raven Colonial](#starting-a-project-on-raven-colonial) and [Sharing your progress with Raven Colonial](#sharing-your-progress-with-raven-colonial).
- **Manage Sites** (a menu):
  - **Rename Site…** gives the selected site a name of your own (see [The site name](#the-site-name)).
  - **Archive Finished** moves every complete or failed site into the [Archive](#the-archive).
  - **Show Archive** opens the archive.
  - **Remove Site** stops tracking the selected site.
  - **Remove Finished** deletes every complete or failed site and states how many it removed.
  - Neither removal asks for confirmation. Removing a site only drops WFMT's tracking of it: docking at the depot again registers it afresh.

**Example: copied list.** For a site that needs 1,200 t of Steel and 800 t of Titanium, with nothing aboard, **Copy Shopping List** places this text on the clipboard:

```
Example Outpost (Example System) - still to get:
1,200 t  Steel
800 t  Titanium
```

After 500 t of Steel is moved onto the carrier, the list shows `700 t` for Steel.

### The archive

Finished sites stay in the Sites window until they are removed or archived. WFMT does not clear them automatically. The **Archive** keeps them for reference without crowding the list of active sites.

- **Archive Finished** (Manage Sites) moves every complete or failed site to the archive. An unfinished site is never archived.
- **Show Archive** opens a window listing archived sites, newest finish first: the site, its system, how it ended (**Result**), when WFMT first saw it (**Started**) and when it finished (**Finished**), how long it took (**Took**), and the tons it needed (**Needed**). Selecting a site lists each commodity it needed (**Commodity**, **Required**, **Delivered**, **Left**). Delivered counts all commanders' deliveries, as the depot reports them.
- **Restore** returns the selected site to the Sites window. **Copy Summary** copies its facts as text. **Manage → Rename Site…** renames the selected archived site (see [The site name](#the-site-name)). **Manage → Remove Permanently** deletes the site after confirmation. The delivery history keeps the commander's own totals but not the site's list of commodities.
- Archived sites still count in the [History](#history) figures. They are stored in the same data file as the other sites, so **Back up my data** includes them. If a depot reports an archived site as under construction again, the site returns to the Sites window.

**Example.** Two of six sites show `complete` and one shows `failed`. **Manage Sites → Archive Finished** moves the three out of the list; the count of active sites in the subtitle is unchanged. **Manage Sites → Show Archive** lists them, newest finish first, with the duration of each. **Copy Summary** copies the facts of the selected site and **Restore** returns it. The History totals still include them.

## My Projects

The Colonization Sites window knows only the sites the commander has docked at. **My Projects** (the **Projects** button on the Colony page, or **My Projects** in the **Raven Colonial** menu) lists every active project of the commander on [Raven Colonial](https://ravencolonial.com), across systems.

- **Reading needs no key and no switch.** Opening the window sends only the commander name, to read the projects, the hidden list and the primary project.
- **The table** has the columns **Count** (a tick when counted), **Project**, **System**, **Building** (the game's name and the build type Raven uses, such as *Industrial Outpost (vulcan)*), **Done** (percent delivered), **Still needed** (tons, or `complete`) and **Note**. The Note column shows **Primary** for the primary project and **Here** for a site WFMT also tracks from the journal. Completed and uncounted projects are grayed.
- **Count.** A project is counted unless it is on the commander's hidden list on Raven Colonial. The line under the title reads like `<commander> - 6 projects · 5 counted need 41,000 t · 105 trips in your ship`. It adds up the counted projects and the trips they take in the current ship, and adds `unsaved changes to the counted list` after the counted list has been changed here. A double-click on a row, or selecting it and pressing **Count / Don't Count**, changes the count.
- **Refresh** (highlighted) reads everything again. The window follows a login as another commander. A **My Projects help** button repeats these notes.
- **Sync Sites** applies to a project deleted on Raven Colonial: WFMT still tracks its construction site as active, so the Colony panel keeps naming it as the current project. The button lists the active sites tracked by WFMT that none of the commander's Raven projects is for (matched by market id, or by name and system for a project for which Raven holds no market id) and, on confirmation, stops tracking them. It works from the list on screen, so press **Refresh** first. Nothing is sent to Raven Colonial; docking at a site again tracks it afresh. A site without a project is also listed, so the names must be checked before confirming.
- **More** menu:
  - **Copy Shopping List** copies the needs of the selected project, largest first.
  - **Open Project on Raven** and **Open My Projects on Raven** open ravencolonial.com in the browser.
  - **Set as My Primary…** makes the selected project the primary project on Raven Colonial. It asks for confirmation.
  - **Save Counted List…** replaces the hidden list on Raven Colonial with the one on screen. It asks for confirmation, because other tools that read the list, such as SrvSurvey, see the change.
- **The two writes** require the Raven Colonial key and the master switch (see [Sharing your progress with Raven Colonial](#sharing-your-progress-with-raven-colonial)). Nothing is saved until the button is pressed.
- Apart from **Sync Sites**, the window does not change WFMT's own tracking. A project never docked at is listed from Raven's figures alone, so its commodity list is Raven's, not the journal's.

**Example.** The line under the title reads `CMDR Example - 6 projects · 5 counted need 41,000 t · 105 trips in your ship`. Select the project marked **Here** and choose **More → Copy Shopping List** to copy its needs, largest first. A double-click on a finished project's row stops counting it, and the line shows `unsaved changes to the counted list`. Nothing reaches Raven Colonial until **More → Save Counted List…** is chosen and confirmed.

## Planned builds

The journal reports a construction site only after the commander docks at it, so a build that is only planned does not appear in WFMT's own tracking.

**Planned Builds** (in the **Raven Colonial** menu, top right of the Colonization Sites window) shows what [Raven Colonial](https://ravencolonial.com), the community planning site, holds for the system of the selected site.

- Every site is listed, building sites first, with the columns **Site**, **Status** (**Building**, **Planned**, **Complete** or **Demolish**), **Type**, **Body** (the body's number), **Full cost** and **In WFMT**. **Refresh** requests the data again. A help button repeats these notes.
- The top of the window names the system's **architect** (the commander who planned it there) and whether Raven Colonial has the system **open** or **locked**, as Raven Colonial reports them.
- A site that the commander has docked at and WFMT tracks is marked **yes** under *In WFMT*.
- The window opens for the system of the selected site, and shows the new system if it is opened again from another site. With no system known yet for the site, dock at it once.

**Example.** Three outposts are planned in one system, and one has been docked at. **Raven Colonial → Planned Builds** lists all three. The site being built shows **Building** with **yes** under *In WFMT*. The other two show **Planned** with **no**. Selecting a planned row shows its five largest commodities in the footer. The line under the title, `planned builds need N t`, gives the total still to come.

### Full cost

For a planned or building site the window also shows the **full cost**: the tons the whole building needs, taken from a table of building costs bundled with WFMT.

- Full cost is shown for planned and building sites only, not finished ones.
- Selecting a row shows its building, layout and its five largest commodities in the footer.
- The line under the title adds up what all the *planned* builds in the system need (`planned builds need N t`).
- The table is a snapshot. If the game changes a building's cost, the table is out of date until WFMT is updated.
- A building not in the table shows no cost.

### What is sent

- WFMT requests data from Raven Colonial once, when the window opens or **Refresh** is pressed, and sends only the system name.
- The answer is remembered for one minute.
- The window shows what other players have entered. A system with nothing planned on that site shows nothing.

See [what goes on the internet](internet-and-privacy.md).

### Quick links to Raven Colonial

The **Raven Colonial** menu in the Colonization Sites window also opens Raven's own pages in the browser. WFMT sends nothing to Raven for these; the browser makes the request.

- **Open Selected Build on Raven** opens the project page of the selected site. WFMT finds the project as Raven Progress does (one read of the system's plan). A site for which Raven has no project opens its system page.
- **Open This System on Raven** opens the system of the selected site.
- **Raven Colonial Website** opens the home page.

### Sharing your progress with Raven Colonial

Sharing is optional and off by default.

- Nothing is sent to Raven Colonial until the **master switch** (**Colonization: share progress and deliveries**) is ticked in **Settings → WFMT → Online**. The Colonization tab shows a note pointing there and holds the key.
- Clearing the master switch stops every write at once (progress, deliveries, carrier cargo and Report Complete). The other choices are kept for when it is turned on again.
- While the switch is off, the Raven Colonial strip of the Sites window and the My Projects window show `This needs "Colonization: share progress and deliveries" (Raven Colonial), which is off. Turn it on in Settings > Online.` Nothing is shown while it is on.
- With the switch on, WFMT shares what happens at a construction site as it happens.

| Setting | Location | What is sent, and when |
|---|---|---|
| **Colonization: share progress and deliveries** (the master switch) | Settings → WFMT → Online | Nothing by itself. Off by default. The two checkboxes below work only while it is ticked and are grayed while it is not. |
| **Report my construction progress and deliveries** | Sites window, Raven Colonial strip | Requires the key below; with none, nothing is looked up or sent. When the depot's figures change (the `ColonisationConstructionDepot` event): the depot's numbers and how much of each commodity is still needed, which moves *Remaining* on Raven Colonial. When cargo is delivered (`ColonisationContribution`): the commodities and tons, which credit the commander name in Raven's history. Once per project, it also links the commander to the project. |
| **Also report cargo I move to and from my fleet carrier** | Sites window, Raven Colonial strip | When cargo is transferred at the commander's own fleet carrier: the tons moved, to the carrier as plus and back to the ship as minus. It adds to Raven's carrier record and never replaces it, because WFMT's tally contains only observed moves. Requires the key. |
| **Raven Colonial key** | Settings → WFMT → Colonization | Required for every write: progress, deliveries, carrier cargo, **Create Project on Raven**, **Report Complete to Raven**, **Mark Plan Entry Demolished**, and **Set as My Primary** and **Save Counted List** in My Projects. With no key WFMT sends nothing. The key is saved per commander on the local computer, shown masked, and sent only to Raven Colonial. |

**In the Sites window.** The Colonization Sites window has a **Raven Colonial** strip across the top. It states what is being reported (for example "Reporting progress and deliveries; a key is saved for this commander") and holds the two reporting checkboxes, **Report my construction progress and deliveries** and **Also report cargo I move to and from my fleet carrier**. These two exist only in the strip, not in Settings. They are grayed, and a click does nothing, while the master switch is off. The choices are kept for when it is on.

**Settings.** The master switch is in Settings → WFMT → Online and the **Raven Colonial key** is in Settings → WFMT → Colonization. The master switch is the permission for WFMT to send data to a third-party site, so the window cannot turn it on. When a write first needs the key, the window asks for it to be pasted.

**Obtaining the key.** The Settings page has a link to [ravencolonial.com/user](https://ravencolonial.com/user), where Raven shows the key after sign-in (the page can also reset it). WFMT does not fetch the key.

**Test key.** The **Test key** button beside the **Raven Colonial key** box in Settings asks Raven Colonial whether the key as typed is accepted for the commander. The key is saved for the current commander when Settings is closed.

- It uses a read that changes nothing, and shows Raven's name for the commander when the key is accepted.
- It checks the box as typed, so it can be used before closing Settings.

**Functions without a key and without the switch.** **Planned Builds**, **My Projects** (viewing), **Raven Progress** and **Refresh from Raven** only read from Raven Colonial.

- Each runs when its button is pressed or its window is opened. **Planned Builds** sends only the system name. **My Projects** sends only the commander name. **Raven Progress** sends the system name and the project id (and, if the plan does not name the project, the system address and the site's market id). **Refresh from Raven** sends the same for each open site.
- If another tool already reports the builds to Raven, leave the master switch off. WFMT then sends nothing, and Raven Progress can be used to compare Raven's figures with WFMT's.

### Rules for what is sent

- **Only live events.** Activity while EDMC was closed, and anything the start-up catch-up reads, is never sent.
- **Raven must already have a project for the site.** WFMT finds it from the system's plan and, failing that, from the system address and the site's market id (so a project named *Primary port* is still found, and a renamed station does not break the match). If there is none, WFMT sends nothing and asks again no sooner than ten minutes later. To create one, use [Create Project on Raven](#starting-a-project-on-raven-colonial); WFMT then uses it at once.
- **One request per event.** Requests go one at a time in the background. A request is retried once if Raven answers busy (HTTP 429 or 503). A failure is only logged and never interrupts play. The depot figures are sent only when the needed amounts have changed.
- **Raven's `supply` call is never used.** It is meant for tools that cannot read the journal; used beside the depot figures it would reduce the amount needed twice.
- **Do not run two tools that report to Raven.** If another tool (the Raven Colonial EDMC plugin or any other) also reports the deliveries, Raven counts them twice.
- **Raven Progress** (in the **Raven Colonial** menu of the Colonization Sites window) reads Raven's own figures for the selected site and sets them beside WFMT's in the status line (*<site>: Raven Colonial says 12,345 t still needed of 20,000; WFMT says 12,345 t (they agree)*, or *they differ by N t*, with a note when Raven has the site marked complete). It looks up the project first, so it sends the system name and the project id.
- **Refresh from Raven** (the button under the list of sites) does the same for every open site at once and fills the **Raven** column. Each open site shows the tons Raven says are still needed, `done` when Raven has it marked complete, `no project` when Raven has none for it, `error` when the read failed, or `not asked` when the run stopped early. The note under the button says when Raven was last asked and for how many sites it answered (*Raven figures refreshed 14:32: 5 of 6 sites answered.*, with the date when it was not today), and the status line sums up how many agree with WFMT and how many differ. Notes:
  - Nothing is asked until the button is pressed, and nothing is repeated on a timer. The figures stay as they were at the last refresh while you play, so WFMT's **Left** can move on; press the button again to ask again.
  - Only open sites are asked about (not complete, failed or archived ones), at most 25 at a time, one after another with a short pause. Sites in one system share one read of the system's plan. After three failures in a row the run stops and says so.
  - The figures and the time are kept for this session only: after a restart, or a change of commander, the note reads *not refreshed yet*.

WFMT's own tracking remains the source of truth for the site. Raven's figures never overwrite it.

### Starting a project on Raven Colonial

When the commander docks at a construction ship or site for which Raven Colonial has no project, nothing is shared until a project exists. Select the site and choose **Create Project on Raven** in the **Raven Colonial** menu.

- It requires the master switch and the Raven Colonial key (WFMT asks for the key the first time and keeps it once Raven accepts it). It works only for an **active** site; a finished site is refused. With the switch off, the status line shows `This needs "Colonization: share progress and deliveries" (Raven Colonial), which is off. Turn it on in Settings > Online.`
- The Colony page can also offer this when a new site appears (see [Offer to start a Raven project](#the-colony-page)).
- WFMT first reads the system's plan on Raven Colonial. If a project already exists for the site, WFMT states this and does nothing else. The status line shows progress during the lookup. The message from any button pressed in this menu stays for 30 seconds.
- The dialog opens centered over the Sites window and inside the screen. If it does not open, the EDMC log has a `Create project:` line stating where the steps stopped.
- Otherwise the **Create Raven Colonial project** dialog opens.
  - **Plan entry** lists the sites planned for that system that have no project yet, each with its build type. Select one, or leave **None** to create a project of its own (WFMT never edits the system's plan). If only one site is planned, it is preselected.
  - The building is chosen in three steps, as on Raven Colonial: **Location** (orbital or surface), **Building** (by tier and the game's name, such as *Tier 1: Industrial Outpost*), then **Layout (build type)**, the exact identifier Raven Colonial uses, such as `vulcan` or `dual_truss`. That identifier is sent. A planned site fills in all three; changing Location clears Building and Layout. Create is refused until a building and layout are chosen (`Choose the building and its layout.`).
  - **Body** is chosen from the system's bodies as Raven lists them (or left *Unknown*). **Name** defaults to *Primary port* for the system's colonization ship, otherwise the station's own name. **Architect** (defaults to Raven's architect for the system, otherwise the commander), **Notes** and **Due (YYYY-MM-DD)** are optional. A due date in another form is refused.
  - Three checkboxes:
    - **This is the system's primary port**: ticked for a colonization ship. It is grayed and cleared, with a line stating why, when the system already has a primary port: Raven's plan for the system lists another station that is built or started, or WFMT has seen another station there. Raven does not mark the primary port in that list, but a system's first station is always its primary port.
    - **Make it my primary project**.
    - **Attach my fleet carrier**: grayed, with a note, until WFMT has seen the carrier's id this session (on login or on opening Carrier Management).
  - A red note in the dialog warns when Raven reports the system as locked to another architect.
- Nothing is sent until **Create** is pressed (**Cancel** sends nothing, and the status line states this). WFMT then, in order, creates the project from the depot figures it already holds, links the commander, and performs the two optional steps. The status line states what succeeded. If linking, primary or the carrier fails, the project remains and the message names the step.
- **What is sent:** the key, the site's market id, system name, address and position, the commodities still needed with the depot figures, and the dialog input. No other journal data.
- **Limit:** a system locked to another architect can refuse a project. WFMT's own tracking does not change.

**Example: first project in a new system.** The Colony page shows `Raven Colonial has no project for Example Outpost.`

1. Check that **Colonization: share progress and deliveries** is ticked in Settings → WFMT → Online and the key is set in Settings → WFMT → Colonization.
2. Press **Create on Raven**. The Sites window opens on the site with the Create dialog.
3. Select the matching **Plan entry** (its Location, Building and Layout fill in), or leave **None** and choose them manually.
4. Press **Create**. The status line states what succeeded. From then on the deliveries are shared as they happen.

**Mark Plan Entry Demolished…** sets the selected site's entry in Raven's plan to *demolished* after confirmation. It changes Raven's record only, not the game. It requires the master switch and the key like the other writes, and states so when Raven's plan has no entry for the site.

### Reporting a finished build to Raven Colonial

Select a site that the journal has reported **complete** and choose **Report Complete to Raven** (in the **Raven Colonial** menu, top right of the Colonization Sites window).

- WFMT looks up the site in Raven Colonial's plan for its system. It matches on the site's market id, or on its name for a build in progress, for which Raven has no market id yet.
- It then marks that project complete there.
- It never does this automatically. Each time it asks for confirmation (`Tell Raven Colonial that <site> in <system> is complete?`). Before the site is complete in the journal, the command states that there is nothing to report.
- It requires the master switch and the **Raven Colonial key**. The first time, WFMT asks for the key to be pasted. The key is saved for that commander only (in `rcc_keys.json`, in the plugin folder, which updates leave alone) once Raven Colonial has accepted it, and is masked while typed.
- **What is sent:** the key and the one project's id. No deliveries, cargo or journal data.
- **Limit:** Raven Colonial must already have a project for the site, found from its plan or by the site's market id. If it has none (for example the site is only planned there), WFMT states this and sends nothing; **Create Project on Raven** can create one. Reporting copies nothing back: WFMT's own tracking is unchanged.

**Example.** The game reports the site complete after the final delivery and dock. Select the site in the Sites window and choose **Raven Colonial → Report Complete to Raven**. After confirming `Tell Raven Colonial that Example Outpost in Example System is complete?`, the project is marked complete. Nothing is sent before the confirmation.

## The shopping list on the overlay

The card is optional and off until enabled. It requires a running overlay; see [Setting up the overlay](../OVERLAY_SETUP.md).

- Ticking **Always show the shopping list, whatever screen you are on** in **Settings → WFMT → Overlays → Colonization** shows the card on every screen.
- Ticking **Also show the shopping list automatically (markets, carrier inventory, construction sites)** in the same tab shows the card in the places listed below.

### The table

The card is a table with the site name as its title and the columns **Commodity**, **Required**, **Acquire**, **FC** and **Cargo**.

- **Required** is the site's full requirement for the commodity.
- **Acquire** is what remains to be obtained: the site's remaining requirement (required less delivered), less the hold and the fleet carrier, as in the window's Acquire column. It shows 0 once everything is held, wherever it is stored.
- **FC** appears only with a fleet carrier (see the FC column above): the cargo transferred onto it. It is blue once it covers the remaining amount, gray while it does not, and blank when none.
- **Cargo** is the cargo in the ship's hold now. A **✓** after the name means the hold plus the cargo on the fleet carrier already covers the commodity (the row turns green, the same rule as the window's green rows). The row turns amber if together they exceed the site's need.
- **With *List* set to *To haul*** every row is already covered, so there is no green. The **✓** remains, and the rows in the ship's hold (those being hauled) are drawn in the overlay's blue, as the Sites window tints them. A row held in surplus but not in the hold stays amber.

**Example card (illustrative).** Docked at a construction site:

```
Example Outpost
Commodity        Required  Acquire  FC   Cargo
Aluminium           900      300    400   100
Steel ✓           1,000        0    800   200
► 32,769 remaining  ► 21 to buy  ► 33 to haul
```

Steel carries a check mark because the hold plus the carrier cover it, so its row is green. Aluminium is still short, so it has no tint. With **List** set to **To buy**, the Steel row is omitted.

### Order

- At a **construction site** the rows are alphabetical.
- Elsewhere (a commodity market, the carrier's inventory) the rows are **grouped under the market's categories** (Chemicals, Foods, Industrial Materials, Machinery, Metals, Technology and so on).
  - Each group has a heading line, in capitals, in the card's title color.
  - The commodities are alphabetical inside the group, indented under the heading.
  - A commodity without a known category is listed under **Other**, last.

### Grayed out when this market does not sell it

- While docked at a commodity market, a commodity that the market does not have for sale is shown in faint gray with **not available** after its name.
- A commodity that the hold and the fleet carrier already cover keeps its green (or amber) tint regardless of the market's stock.
- Nothing is dimmed away from a market, at a construction site, or if WFMT has not seen the market (its commodity screen must be opened once).

### The last line

The last line gives the tons remaining (still to get, as in the Acquire column) and the trips in the current ship. It requires the ship's cargo capacity, supplied by EDMC.

- **With a fleet carrier** it gives both legs, as the Colony page and the window do: `► 32,769 remaining  ► 21 to buy  ► 33 to haul`.
  - **To buy** is the loads needed to gather what is still to get after the ship and the carrier (0 once all is stocked).
  - **To haul** is the loads needed to carry everything still needed to the site.
- **Without a carrier** there is one figure, `► 32,769 remaining  ► 33 trips to finish`, because one trip buys and delivers.

### When it shows, and settings

**When it shows**

- In a **commodity market** at a station.
  - WFMT uses the journal's `Market` event and the game rewriting `Market.json`, which the game does when a market opens. The journal event can reach EDMC several seconds late on some setups (observed on Linux under Proton).
  - The card hides when the commander leaves the screen, opens another service such as outfitting or the shipyard, or undocks.
  - Backing out of the market to the station-services menu cannot be detected, so the card stays until that menu is left.
- At the commander's **own carrier**, in the station-services screens. The game writes nothing when a carrier's market is opened, so any services screen shows the card there, except after the carrier's outfitting or shipyard screens (which are logged).
- Whenever the commander is **docked at a carrier** and the **right-hand cockpit panel** is open (where cargo is held and transferred to the carrier). The game writes nothing when it is opened, so the open panel is what WFMT uses; the card hides when the panel is closed or the commander undocks.
- Whenever the commander is **docked at a construction site** (looking out of the cockpit or at the station services, but not in a map or another panel).
- In the carrier's **Carrier Management** screen. The game announces both opening and closing it, so the card appears and disappears with the screen.
- Optionally, **whenever the right-hand cockpit panel is open, anywhere** (including in flight). Off by default; tick **Also show whenever the right-hand cockpit panel is open, anywhere** in the Colonization overlay settings.

Most of these rules rely on the game's `Status.json` reporting which screen is open.

**Manual control.** With the automatic option cleared, **Always show the shopping list, whatever screen you are on** in the same settings controls the card.

- Ticked, the card stays on every screen. Cleared, the card returns to the automatic rules (or stays off).
- It works whether or not the automatic option is ticked, and it is stored across EDMC restarts.
- The **Overlays shown (click to hide)** line at the top of the WFMT panel hides every overlay, including this card, until it is clicked again.

**Which site.** The most recently updated active site, the one the Colonization mode summary line names. Completed and failed sites are never shown. The card disappears when nothing is left to get.

**Settings**

| Setting | Description |
|---|---|
| Card position | Settings → WFMT → Overlays → Overlay Placement. The default is the left edge, vertically centered. |
| **Rows** | Number of commodities listed (1 to 60; the rest are summarized as `+N more`). The default, 0, lists all. |
| **List** | **All**, **To buy** or **To haul**, the same choices as the window's **Show**. It is the same setting as the **Show** drop-down in the Sites window, so changing one changes the other. **To buy** (the starting choice) omits the rows that show a **✓**, so the card lists only what remains to be obtained. **To haul** lists the rows that are covered but not yet fully aboard the ship. The last line still counts every commodity the site needs, and when no row is listed the card shows only that line. A choice made with the older *Hide commodities already covered* checkbox carries over. |
| **Test Overlay** | Shows a sample card for about 8 seconds, including while the option is off, and reports `Sent — check your overlay.` or that the overlay could not be reached. |

The card is cleared when EDMC closes. If the overlay program is not running, nothing is drawn and no error is raised.

## What the game does and doesn't tell us, and how to work around it

WFMT knows only what Elite Dangerous writes to its journal files, plus what Frontier's servers give a signed-in EDMC (the carrier's cargo), what Spansh reports (where to buy), what players enter on Raven Colonial (plans and progress) and a bundled table of building costs. WFMT keeps its own tallies for the remaining data. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| Item | What the game provides | Result in WFMT |
|---|---|---|
| All cargo on the carrier | The journal records only cargo transferred to or from the carrier. Stock that arrived any other way is invisible to it. Frontier's carrier data lists the actual hold, but only when EDMC is signed in. It is fetched when Carrier Management is opened (at most every 15 minutes) and can lag, sometimes for longer than 15 minutes. | WFMT ignores a lagging copy, so transfers are not undone. Sign EDMC in to Frontier and open Carrier Management at least 15 minutes after the last transfer; the FC column and the **On your carrier** line then follow the actual hold. See [Scenarios](#scenarios-what-to-expect-and-what-to-do). |
| Colonization sites appearing automatically | The game writes the depot event only when the commander docks or opens the depot market. A delivery to a site for which WFMT has never seen a depot snapshot is ignored. | Dock at the depot (or open its market) once for each new site. Docking again replaces WFMT's figures with the game's figures. Deliveries made with EDMC closed are caught up from the last 14 to 30 days of journals at start-up. |
| A site's name or rename | The name is taken from the last time the commander docked at that market. Otherwise it is `Construction site <number>`. The game does not announce a rename; it appears in the name the market has the next time the commander docks. | Dock at the market once to take the name, and again after a rename. To keep a name of your own, use **Manage Sites → Rename Site…**; docking does not change it. |
| A full history of all deliveries | The journal records each delivery as it happens. WFMT rebuilds the history once from every journal file still present, so deliveries from deleted journals are missing. | The history counts from the first delivery found (shown in the History window). |
| Other commanders' work on the same project | The depot reports only the project's totals, not who delivered what. | The page shows the commander's deliveries and the project's overall progress. |
| The cargo in the hold now | The journal's `Cargo` event carries only a count, and EDMC's cargo state did not follow a purchase. The game rewrites `Cargo.json` on every change. | WFMT reads `Cargo.json` and reads it again about 1.5 seconds after each cargo event. If the file is missing or describes the SRV, WFMT uses the hold EDMC reports. |
| Builds only planned, or projects not docked at | The journal reports a construction site only when the commander docks at it or opens its market. | Planned Builds and My Projects read what players have entered on Raven Colonial. They show other players' entries too, and a project nobody has entered shows nothing. |
| Prices at other markets | The game provides no way to query other stations' markets. | Where to buy asks Spansh, which holds players' market updates. Only markets updated in the last 7 days are listed, and fleet carriers are left out unless **Exclude fleet carriers** is cleared. |
