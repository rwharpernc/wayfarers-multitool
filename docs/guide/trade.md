# Trade

This guide describes Trade mode: the running profit after fuel and repairs, unsold cargo, the ship hold and fleet carrier space, saved sessions, Spansh route and price lookups, and the commodity watch list.

The Trade panel shows a summary (net profit and hold) and four buttons: **Session**, **Routes**, **Market** and **History**. The first three each open a window of their own, and WFMT remembers where each was left. **History** opens the Trade History window.

| Page | Purpose | Needs internet |
|---|---|---|
| **Session** | Running profit, costs, hold and carrier cargo | No |
| **Routes** | The best trade routes from the current position | Yes (Spansh, off until enabled) |
| **Market** | Where to sell or buy a commodity | Yes (Spansh, off until enabled) |

The **Trade History** window keeps the sessions that are saved.

Each page is laid out in sections with headings, muted labels beside bright values, and tables with aligned numbers. Gains are green, losses red and warnings amber. Long station names wrap. A page's buttons are at the top of its window (on Market, the Commodity box and the search buttons come first).

**On this page:** [How to](#how-to) · [How a trading session works](#how-a-trading-session-works) ·
[The Session page](#the-session-page) · [Trade History](#trade-history-saving-sessions) · [Routes](#routes) ·
[Market](#market) · [Watch list](#watch-list) · [Fleet and squadron carriers](#your-fleet-carrier-and-squadron-carrier) ·
[What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it) ·
[Using Trade on two computers](#using-trade-on-two-computers) · [Settings](#trade-settings)

**Data sources:**

- Trades, costs and cargo come from the journal.
- A carrier's space is written only when Carrier Management is opened.
- A carrier's bay contents are not listed in the journal. WFMT shows the carrier's orders and an estimate marked `~`.
- Routes and prices come from Spansh, a community database.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## How to

The numbers in the examples are illustrative.

**Read the profit after fuel and repairs**

1. Trade in the game. WFMT counts each purchase, sale and running cost seen in the journal.
2. Press **Session** on the Trade panel.
3. Read **Net profit**: trade profit less fuel, repairs, advanced maintenance, rearm and limpets. The costs are listed under it.

See [The Session page](#the-session-page) and [Worked example: profit after costs](#worked-example-profit-after-costs).

**Track a fleet carrier's cargo**

1. In **Settings → WFMT → Trade**, set the carrier choice for the commander (**Auto** applies when the journal has shown a carrier).
2. In the game, open **Carrier Management** once so the game writes the carrier's space.
3. Read **Carrier cargo** (used out of capacity, with free tons) and **Carrier reserved for orders** on the Session page. A `~` before the figure marks an estimate. Opening Carrier Management again makes it exact.

See [Your fleet carrier and squadron carrier](#your-fleet-carrier-and-squadron-carrier).

**Save and review a session**

1. On the Session page, press **Save session**. The message `Saved to Trade History.` appears.
2. Press **Reset** to start the next session.
3. Press **History**, select the session in the **SESSION** drop-down, and open the tabs (**Overview**, **Commodities**, **Stations** and others).

See [Trade History](#trade-history-saving-sessions) and [Worked example: review a saved session](#worked-example-review-a-saved-session).

**Find the best route or price**

1. Tick **Enable Spansh trade lookups** in **Settings → WFMT → Trade**.
2. For a route, open the **Routes** page and press **Find routes** (or **Round trip** for a back-and-forth pair).
3. For a price, open the **Market** page, choose **Sell** or **Buy**, select a commodity, then press **Near me**, **Galaxy** or **Best picks**.

See [Routes](#routes) and [Market](#market).

**Use the watch list**

1. Open the **Watch list** row in Trade mode and press **Watch**.
2. In the box beside **Add a commodity**, type a name, select it from the suggestions and press **Add**.
3. Press **Refresh** to request prices from Spansh. Opening station markets in the game also records prices.

See [Watch list](#watch-list).

## How a trading session works

A session is a running tally that belongs to a commander. It starts the first time WFMT sees the commander and lasts until **Reset** is pressed, across any number of logins and EDMC restarts.

- Each commander has a separate session. Switching commander does not affect another commander's tally.
- When EDMC is closed during play, WFMT catches the session up from the game's journal files the next time EDMC sees that commander. It adds only what is new, so nothing is counted twice. On Linux this requires EDMC's **Journal directory** to be set; see [WFMT on Linux](linux.md#step-2-tell-edmc-where-elites-journals-are).
- Only what WFMT has seen is counted. Trades made before WFMT first ran, or in a session that was reset, are not included.
- Nothing is kept permanently unless **Save session** is pressed.

### Finishing a session and starting the next

There is no Start or Track button, because tracking does not stop.

1. Press **Save session** to copy the tally into Trade History. The tally keeps running and the button stays **Save session**. Saving again updates the same entry.
2. Press **Reset** to begin a new session. If the current session has unsaved trades, WFMT offers to save first.

If **Reset** is not pressed, later trades are added to the old session.

Example: after hauling Tritium on Saturday, pressing **Save session** and then **Reset** keeps Saturday's session in History. A mining run sold on Sunday is a new session with its own profit figure.

## The Session page

The page reads the journal only and sends nothing anywhere.

**Top of the page.** Before anything has been traded the page shows `No trades yet this session.` and `Buy or sell at a market and they are counted here.` When only running costs exist, they are listed with a **Net** figure.

**Profit.** Trade profit is the amount paid minus the cost of the tons sold, as the game reports it. Stolen or black-market cargo counts the whole sale. Credits per hour (`+1,200,000 cr/hr`) appears after about three minutes of trading (first trade to last trade). Below it are **Bought** and **Sold** (tons and credits) and a **Best sales** list of the five most profitable commodities with profit and tons. If more than five commodities were traded and the worst one lost money, a **Worst** line names it.

**Running costs:**

- **Fuel** (refuelling)
- **Repairs**
- **Advanced maintenance**: the game logs it as a repair that includes module "Wear". The whole charge is listed on its own line.
- **Rearm** (ammunition, and restocking an SRV or fighter)
- **Limpets** (bought, less any sold back)
- **Fines and bounties paid** (only when enabled in the Session window)

Once any cost exists, the headline becomes **Net profit**: trade profit less the costs. Credits per hour is the net. The trade profit and each cost are listed under it.

Not counted as costs:

- Insurance rebuys.
- Fines and bounties paid off. Tick **Count fines and bounties I pay as a running cost** in the Session window to count them. Enabling it counts payments made from then on, not earlier ones.

A cost counts only once WFMT has seen it.

#### Worked example: profit after costs

100 t of Gold is sold for 1,200,000 cr, having cost 900,000 cr to buy. Fuel costs 18,000 cr and repairs 12,000 cr. The Session page shows trade profit of 300,000 cr, the fuel and repairs lines, and the headline **Net profit** of 270,000 cr (300,000 less 30,000). Credits per hour is computed from the net after about three minutes of trading.

**In your ship.** The page shows **Ship** and the **Landing pad** it needs (for example "Type-9 Heavy" and "Large"; `Unknown` when WFMT cannot determine it, in which case no pad filter is applied), then:

- **Ship hold**: tons used, capacity and free tons. It reads `Ship hold: empty` when the capacity is not yet known and nothing is aboard.
- **Worth at (station)**: what the docked station would pay for the whole hold, once its commodity market has been opened.
- An **In hold / Sells here** table: what each commodity aboard would sell for there. The four largest loads are listed, followed by `+N more`.

**Hold space**, below the landing pad, splits the hold into cargo and limpets (limpets take hold space like cargo), for example "312 t cargo (40 t mission, 12 t stolen), 16 t limpets". The free tons are on the **Ship hold** line. The line appears only when there are mission or stolen tons or limpets to show. The mission and stolen figures come from the game's cargo list (`Cargo.json`).

**Carrier cargo.** The carrier's cargo storage, shown only when a carrier is configured (see [below](#your-fleet-carrier-and-squadron-carrier)). Each carrier has its own heading, `Fleet carrier: NAME` or `Squadron carrier: NAME`. Until the game has reported the carrier's space, a note under the heading reads `Open Carrier Management once to read its cargo space.`

- The figures are labeled **Carrier cargo** (for example `12,400 / 25,000 t (12,600 free)`) and **Carrier reserved for orders**, to distinguish them from the ship hold. **Carrier reserved for orders** is omitted when 0.
- Under the cargo line, **Carrier crew services** and **Carrier ship / module packs** show the other uses of the carrier's space. A line is omitted when 0.
- Below those, when the journal has provided them: the carrier's tritium, its location, a planned jump, its balance and the trade orders that are set (the first six, followed by `+N more carrier orders`).

**No history.** The Session page shows the present only. The game's lifetime totals (trading, mining, exobiology, fleet carrier) and income over time are in the **Credits Ledger** window (opened from the *Credits this session* line under the mode buttons), where Trade, Exploration and Exobiology are kept separate. Saved sessions are in **History**.

### Buttons

- **Reset**: restarts the tally. If the session has unsaved trades, the prompt `Save it before starting again?` offers **Yes**, **No** and **Cancel**.
- **Save session**: keeps the session in Trade History. It is disabled until there is something to save (a trade or a running cost). A message at the top of the page begins `Saved to Trade History.` or `Updated this session in Trade History.`, then gives the number of saved sessions and reminds that **Reset** starts a new one.
- **History**: opens the Trade History window.
- **Rebuild**: recounts the session from the journals starting at a time entered in UTC as `YYYY-MM-DD` or `YYYY-MM-DD HH:MM`, and replaces the tally. It is intended for a session that began on another computer. It asks first if the current tally is unsaved, and reports when nothing is found for the commander in that period. It is disabled until WFMT knows the commander. After it finishes, check the totals, then press **Save session**.

## Trade History (saving sessions)

**Save session** keeps a session. Pressing it again after more trading updates the same entry instead of adding a second. **Reset** starts a new session, which becomes a new entry when saved.

**History** opens the **Trade History** window. A **SESSION** drop-down at the top selects a saved session (newest first). With more than one commander, a **COMMANDER** filter is shown. Up to 500 sessions are kept; past that, the oldest are removed first. The window opens on the commander being played; other commanders, or **All commanders**, are one drop-down choice away.

| Tab | Content |
|---|---|
| **Overview** | Net profit, trade profit, running costs, net per hour, tons sold and trading time. Then commander, ship, start, end, session length and when saved, balance change, trades, tons bought and sold, profit per ton sold, margin on cost, jumps and light years, net per jump and per light year, each running cost's share of sales, and the best and weakest commodity. |
| **Commodities** | Per commodity: Bought t, Spent, Avg buy, Sold t, Revenue, Avg sell, Profit, Margin, Profit/t and Unsold t. |
| **Stations** | The same, summed per station: Visits, Bought t, Spent, Sold t, Revenue, Profit, Costs and Net. |
| **Route** | The stations in the order visited (#, Time, Station, System, What happened, Net and Running, the running total of the net). Returning to a station later is a new visit. |
| **Trades** | Every purchase, sale and cost with Time, Type, Commodity, t, Unit, Total, Profit, Station and System. The newest 200 are shown first; **Show older trades** adds 200 older ones per press. The table scrolls vertically. |
| **Stock & carrier** | Cargo bought but not sold (a journal estimate, with its cost and average cost per ton), the ship hold at the time of saving, and the carrier's used and free cargo space and space reserved for orders at the time of saving. |
| **Lookups** | Two tables of Spansh requests made during the session: **Spansh routes searched** (Time (UTC), Started from, Hops, Total profit (cr) and the Route) and **Market searches** (Time (UTC), Side, Commodity, Tons, Scope, Best result, System, cr/t and ly). |

Header buttons: **Help** explains the figures. **Copy summary** copies a plain-text report to the clipboard. **Export log (CSV)** saves the full trade log to a chosen file. **Delete session** removes a saved session after confirmation. With no saved sessions, the window instructs to press **Save session** on the Trade > Session page.

### Worked example: review a saved session

1. On **Session**, press **Save session**. The message at the top reads `Saved to Trade History.`
2. Press **Reset**.
3. Press **History**. The newest session is selected in the **SESSION** drop-down.
4. On **Overview**, read net profit and net per hour. On **Commodities**, read Profit/t for each load. On **Route**, read the stations in visit order.
5. Press **Copy summary** for a plain-text report, or **Export log (CSV)** for the full trade log.

**Notes:**

- The balance change is the actual credits difference, so it includes any other income.
- Times are UTC.
- A session keeps its most recent 5,000 trades and costs. The totals are exact.
- History is stored in `trade_history.json` in the WFMT plugin folder, which updates leave unchanged.

## Routes

Requires the Spansh lookups to be enabled (Settings → WFMT → Trade).

**Find routes** asks Spansh for the most profitable trade route from the current position.

**Inputs:**

- *Start:* the docked station, or the last station this commander docked at. Each commander's start is saved, survives commander switches and EDMC restarts, and is updated from journals written while EDMC was closed. A commander who has never docked has no start, and the page says so.
- *Cargo size and credits:* from the game.
- *Jump range:* the ship's unladen range. **Jump range** in the Routes window overrides it.
- *Pad size:* if the ship needs a large pad, only stations with one are considered.

Before a search, the page shows the inputs that will be used (start, ship, cargo, jump range, budget).

**Fleet carriers:** Spansh's planner does not support fleet carriers as a start, so a route never starts from one. When docked at the commander's carrier, the route starts from the last station docked at, and the page names it. If Spansh refuses a search, the page shows its reason.

**Round trip is the exception:** it pairs stations from a station search, which lists fleet carriers. When docked at a fleet carrier, the round trip starts from that carrier's market, and the result names the start. Spansh must hold a recent market for the carrier, so the carrier's commodity market must have been opened once. If Spansh has none, the page says so.

### Worked example: find a route

1. Tick **Enable Spansh trade lookups** in **Settings → WFMT → Trade**.
2. Open the **Routes** page. Check the listed inputs: start, ship, cargo, jump range and budget.
3. Press **Hops** until it reads `Hops: 3`, then press **Find routes**.
4. The page states whether the search is in Spansh's queue or being calculated. **Cancel** stops the search.
5. Read **Total profit** and **Est. profit / hour**, then each numbered hop. **Copy next system** copies the first destination for the galaxy map.

### Hops

The Routes window has a **Routes** box at the top with the search parameters: **Hops**, **Furthest from the star (ls)**, **Jump range (ly, blank = my ship's)**, **Ignore prices older than (hours)**, and ticks for **Systems that need a permit**, **Fleet carriers**, **Ground facilities** and **Large landing pad only**. Under **Round trip** are **Least supply to buy**, **Least demand to sell**, **Search radius** and **Carry only this commodity**. A box saves on Enter or when focus leaves it; a tick saves at once. These settings exist only in the window, not in Settings → WFMT → Trade (see [Trade settings](#trade-settings) for the complete list and location of each).

Other Trade settings are also in their windows: **Ship size (landing pad)** in the Routes and Market windows, **Fleet carriers** and **Ground facilities** also in Market, the **'Near me' search radius (ly)** in the Market window, and **Count fines and bounties I pay as a running cost** in the Session window.

The **Hops** button shows the current value (for example `Hops: 3`). Each press cycles it from 2 to 10 and back to 2. It is the same value as the **Hops** box in the Routes window, which accepts 1 to 10.

With 2 hops, when the route ends at its starting station and every leg carries cargo, the result is headed "repeatable loop". With 2 hops that do not form a pair, the page states that the second hop ends at a third station. A leg with no cargo is flagged.

### Round trip

Spansh's planner returns the best chain, which does not necessarily return to its start. **Round trip** finds the best back-and-forth pair directly.

Procedure:

1. Request the markets of the nearest stations from Spansh: up to 300, within twice the jump range but never less than 20 ly or more than 100 ly, unless a search radius is set in the Routes window.
2. For each neighboring station, compute what to carry out and what to bring back.
3. A pair counts only when both legs make a profit.
4. Each leg fills the hold with the most profitable commodity first and tops up with the next, limited by supply at the buying station, demand at the selling station and the available credits.
5. Pairs are ranked by estimated profit per hour, and the top three are shown. Every pair lists, per leg, three commodities (followed by "+N more") with tons, profit, the cost where bought, the sale price where sold (and profit per ton), and the supply and demand behind them.

The same filters as Find routes apply (price age, ground facilities, fleet carriers, ship pad size, distance from the star), plus the **least supply** and **least demand** settings (200 t each by default), which exclude thin markets. The search makes one to three Spansh requests (100 stations each).

### Reading the result

While waiting, the page states whether the search is in Spansh's queue or being calculated. **Cancel** stops waiting. The result shows:

- **Total profit** and **Est. profit / hour** (a rough figure derived from the jump range), then **Hops**.
- Each hop, numbered: the two stations, then the hop's **Profit**, the **Total** so far (so the last hop's Total is the route's profit) and the distance in light years; beneath them the destination system and its distance from the star, the best commodity with tons, and the supply at the buying station and the demand at the selling one. A **Whole route** row under the last hop sums the profit of all hops, repeats that figure under **Total**, and gives the distance flown. A bold line below reads `Average per leg: +1,067 cr × 3 legs = +3,200 cr estimated total earnings`. In a **Round trip**, each pair ends with `Both legs: out + back = per loop` and an average line for its two legs. Gains are green and losses red.

**Copy next system** copies the first destination for the galaxy map.

## Market

Requires the Spansh lookups to be enabled.

Market finds where to sell or buy a commodity.

The **Commodity** box, the **Sell** / **Buy** buttons beside **I want to**, and the search buttons (**Near me**, **Galaxy**, **Best picks**, **Price finder**, after **Then search**) work only when the Spansh lookups are enabled. Otherwise they are disabled and the window directs to Settings → WFMT → Trade.

1. Choose **Sell** or **Buy** with the **I want to** buttons under the Commodity box (the lit button is selected). The choice is remembered.
2. Select a commodity. Click the **Commodity** box and type. Enter in the box runs **Near me**. Suggestions list first the cargo carried and what the docked station buys, then every commodity.
   - When selling, an empty box searches for the commodity carried in the greatest quantity.
   - When buying, a commodity must be typed.
3. Press **Near me** (the first button after **Then search**) to search within a radius of the current system (100 ly by default), or **Galaxy** to search everywhere. Both may be pressed. While a search runs, **Near me** becomes **Cancel** and the page counts seconds.

Before a search, the page shows what it will use: ship and landing pad, the commodity and amount (marked `(your free hold space)` when buying), and the radius. The lit **Sell** or **Buy** button shows the direction.

Example: with 200 t of Palladium aboard, leave the box empty (it selects Palladium), press **Sell**, then **Near me**. The result lists stations within 100 ly ranked by what the whole load would earn.

### How results are ranked

- **Selling:** by what the load would earn: price per ton times the tons the station still wants. If none of the commodity is held, a full hold is assumed.
- **Buying:** the amount is the free hold space. Stations that can supply all of it come first, cheapest first. Stations that can supply only part follow, marked "only N t in stock".

When both searches (near and galaxy) have run, the page states which is better and by how much (more money when selling, lower price when buying) and how much further away it is. When nothing in the galaxy beats the best nearby result, it reads `Best overall is nearby.` (the station is the first one listed).

### What each result shows

Every result states whether the place is **orbital** or **ground** (on a planet's surface), the station type (Coriolis Starport, Planetary Outpost and so on), and the distance from the arrival star in light seconds. Stations with no landing pad that fits the ship are omitted.

### Fleet carriers in results

Fleet carriers are listed in a separate section, marked "they can move". They are requested separately and weighted at about one carrier to every three stations. A line states when a carrier would beat the best station.

In the Routes and Market windows, **Fleet carriers** and **Ground facilities** (planetary ports and outposts, and settlements) can each be excluded. Excluding both leaves only stations in space.

### Best picks

**Best picks** returns four choices for the commodity in the box (buying: the typed commodity; selling: the typed commodity or the largest load):

| Pick | Meaning |
|---|---|
| **Closest** | The nearest station that has it in stock (buying) or wants it (selling), at any price. |
| **Best local** | The cheapest (buying) or highest-paying (selling) station within the **Near me** radius. |
| **Cheapest anywhere** / **Highest anywhere** | The best price in the galaxy, nearest first when prices tie. |
| **Recommended** | The nearest station whose price is within **10%** of the best price in the galaxy. |

- "In stock" means at least the amount shown (free hold space when buying, the load when selling). If no station has that much, the pick falls back to the nearest with any and states the quantity ("only 12 t in stock" when buying, "only 12 t wanted" when selling).
- The landing pad size, ground-facilities and carriers settings apply.
- Market data older than 7 days is ignored.
- A fleet carrier is not offered as a pick. If a carrier has a better price than the cheapest station, it is noted underneath.
- A station that is two picks is listed for each, with "same as ..." beside the second.

Best picks makes about four Spansh requests (five with carriers), one after another. Results show cr/t, the total for the amount, and distance.

Example: for 64 t of Tritium with 64 t of free hold space, choose **Buy**, type `Tritium` in the Commodity box (select it from the suggestions) and press **Best picks**. The result shows **Closest**, **Best local**, **Cheapest anywhere** and **Recommended**.

The same four picks for a mission's cargo are in Mission mode ([Source commodities](missions.md#source-commodities)).

### Price finder

**Price finder** opens the finder that Mining's **Prices** button also uses ([Find Best Price](mining.md#prices-find-best-price)), for any commodity, to buy or sell, with its own **Where** distance drop-down. The button is disabled until Trade's Spansh lookups are enabled. Its suggestions list the cargo carried and what the docked station buys first, then every commodity. The finder always excludes fleet carriers and requests only markets updated in the last 30 days, regardless of the Trade settings.

Prices are only as recent as the last player who docked at the station. Markets older than 30 days are ignored.

## Watch list

The watch list tracks selected commodities and shows the best price to buy and to sell each. It is a collapsible **Watch list** row in Trade mode, under the page. It starts folded; clicking its heading opens or folds it, and the folded heading shows `- 3 watched`. Each line reads like `Gold: buy 9,100 / sell 11,200`, with `-` for a side with no price. Five commodities are listed, then `+N more in the window`. Two buttons sit under the lines: **Refresh** requests prices from Spansh, and **Watch** opens the window. A status line under the list reports the result of the last refresh. With nothing watched, the row reads `Nothing watched yet. Press Watch to add commodities.`

- **Add a commodity** (window): click the box beside **Add a commodity**, type, select from the suggestions (the same names as the Market page), then press **Add** or Enter. The limit is 30 commodities. Select a commodity and press **Remove** to take it off and discard its prices; the first press asks for confirmation and a second press within a few seconds removes it.
- **The two tables.** The top table lists every watched commodity with **Commodity**, **Buy (cr/t)**, **Buy at**, **Sell (cr/t)** and **Sell at**. Selecting a row fills the lower table with where it was seen: **From** (`Seen` for a market that was opened, `Spansh: buy` or `Spansh: sell`), **Station**, **System**, **Buy (cr/t)**, **Stock**, **Sell (cr/t)**, **Demand**, **ly** and **Age**. The window's **Help** button explains them.
- **Where prices come from.** Each time a station's commodity market is opened in the game, WFMT reads it and keeps the buy price (what the station charges), the sell price (what it pays), the stock and the demand of each watched commodity, for the newest 12 stations. This requires no setting and sends nothing.
- **Refresh from Spansh.** **Refresh** on the row (or **Refresh from Spansh** in the window) asks Spansh for the cheapest station to buy and the dearest to sell each watched commodity, within the "Near me" radius of the current system.
  - It requires *Enable Spansh trade lookups* in Settings.
  - It sends only the commodity names and the system name, never the commander name.
  - Fleet carriers are excluded because they move.
  - The answer is kept until EDMC closes. The search radius is the "Near me" radius, limited to 5 to 5,000 ly.
- **Displayed price.** The cheapest to buy and the dearest to sell among the opened markets and Spansh's answer. The window shows where each price is, how many tons the station has to sell (or still wants), the price source and its age. The row shows only prices.
- **Spansh's five best stations for each side** are kept and listed under the selected commodity, with their stock or demand and distance in light years.

Example:

1. Open the **Watch list** row and press **Watch**.
2. In the box beside **Add a commodity**, type `Gold`, select it and press **Add**. Repeat for `Palladium`.
3. Press **Refresh from Spansh** in the window. The status line reports completion.
4. Close the window. The row shows lines such as `Gold: buy 9,100 / sell 11,200` (example prices).
5. Reopen the window and select Gold to see where each price was seen, its stock or demand, the distance and the age.

A price is a snapshot of when it was seen. A market opened last week may have changed, and Spansh's data is only as recent as the last player who docked (the refresh ignores markets older than 7 days).

The list is stored on the computer for the commander who created it. Another commander on the same install has a separate list.

## Your fleet carrier and squadron carrier

Each commander WFMT has seen has a carrier choice under **Settings → WFMT → Trade**:

**Auto** (show whatever the journal has revealed) · **None** · **Fleet** · **Squadron** · **Both**

Nothing is shown for a carrier that is not selected. For each carrier, the Session page shows:

- cargo used, free, and reserved for orders, for example "5,060 / 23,720 t used, 18,660 t free";
- what the rest of the space is used for (crew, packs);
- when the journal has provided them: **Carrier tritium**, **Carrier is at**, **Carrier jump planned**, **Carrier balance**;
- one line per order that is set (**Carrier selling Gold** 300 t @ 12,000 cr, **Carrier buying Tritium**).

A carrier being decommissioned is flagged. Once the game scraps it (the scrap time in the journal, or seven days after the last report that said it was pending if the journal gave no date), WFMT forgets it, so a scrapped carrier stops showing on Auto.

Example for loading 20,000 t of cargo onto a carrier:

1. In **Settings → WFMT → Trade**, set the commander's choice to **Fleet** (or leave it on **Auto**).
2. Dock at the carrier and perform the transfers. **Carrier cargo** on the Session page increases with each transfer.
3. If the figure shows a `~` or appears wrong after a large unload, open Carrier Management in the game. Within a couple of seconds the page shows the exact **Carrier cargo** and **Carrier reserved for orders**.

### How the number stays up to date

The game reports a carrier's space only when **Carrier Management** is opened. WFMT also reads recent journal files at start-up, so it finds the last time this occurred, even after an EDMC restart.

Afterwards:

- WFMT follows cargo transfers. A transfer is counted for the carrier the commander is docked at, so docking at another commander's carrier does not change the figure.
- Reserved space, and the tons moved by the carrier's trade orders, update only the next time Carrier Management is opened. The orders themselves, tritium deposits, the carrier's location and jump plans are recorded as they happen.

To obtain the exact cargo figure, open Carrier Management (the carrier's management screen, which shows its services and cargo). The game writes a report of the whole inventory and WFMT shows it within a couple of seconds. The game's files do not list everything in the carrier's hold (the report gives only the total, and the orders name only the commodities on order).

### Quirks worth knowing

- **A `~` before the figure** (for example `~23,720 / 23,720 t`) marks an estimate. The transfers WFMT has seen add up to more than the carrier can hold (or remove more than it holds), so cargo left the carrier without the game writing anything, usually through a trade order or a sale made from the carrier. A note under the figure states this. Opening Carrier Management removes the `~`.
- **Playing on another computer leaves the figure stale** until the journals are copied over and read, and then it is only as accurate as the last time Carrier Management was opened. Play with EDMC closed on this computer is read when EDMC next starts.
- **The figure can be wrong right after an unload.** The unload is in the journal but the total is not. Open Carrier Management after a large load to restore an exact number.

## What the game does and doesn't tell us, and how to work around it

WFMT uses what Elite Dangerous writes to its journal files, what Spansh (a community database) reports, and what Frontier's servers give a signed-in EDMC (a carrier's real cargo). Where the game records a value late, partly or not at all, WFMT shows the figure it has and states its certainty. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

### Fleet carrier

| Item | What the game provides | Handling |
|---|---|---|
| Carrier space known at login | The space report (`CarrierStats`) is written only when Carrier Management is opened, not at login. | Open Carrier Management once per session. WFMT reads recent journals at start-up, so the last report still counts after an EDMC restart. |
| List of commodities in the carrier's bay | Only the total tons in the bay. Commodity names are not in the space report. | WFMT lists the carrier's orders (a sale order names a commodity that is aboard). Carrier Management in the game lists the contents. WFMT does not construct a per-commodity list. |
| Trade orders tracked as they fill | The game writes an order when it is placed or canceled (`CarrierTradeOrder`), not each ton later moved. | WFMT shows the orders that are set (commodity, tons, price). The tons moved and the cargo figure update only in the next space report. Until then the cargo figure may be too high and shows a `~`. |
| Space reserved for orders | Updated only in the space report. | Open Carrier Management. |
| Lifetime totals while playing | The game writes its `Statistics` event only at login. | They are on the Credits Ledger's Lifetime tab and refresh at the next login. |
| Tritium, location and jump plans | Tritium comes from the space report and from each fuel deposit; the location is written at login and after a jump; a jump request carries the destination and departure time. Fuel the carrier burns jumping is not written. | WFMT shows the tritium, the carrier location and a planned jump. After a jump, open Carrier Management for the real tritium figure. A plan is dropped once its departure time is well past. |
| Cargo moved by another commander | WFMT follows the transfers recorded in the commander's own journal while docked at the carrier. | Open Carrier Management when another commander may have used the bay (a squadron carrier especially). |
| Figure correct right after unloading | The transfer is in the journal but the total is not updated. | WFMT counts the transfer itself. Open Carrier Management after a large load for the exact number. |
| Crew and pack space by type | Crew services, ship packs and module packs are reported only in the space report. | Open Carrier Management. |

A `~` before a figure marks an estimate: the transfers seen add up to more than the bay can hold, so something left the bay without a journal entry. Opening Carrier Management removes it.

### Ship hold

- **Mission and stolen cargo** are distinguished using the cargo list the game writes whenever the hold changes (each entry states whether it is stolen or belongs to a mission). If the list is missing or unreadable, the line shows the total without the split.
- **Limpets are counted as cargo by the game**, so they are shown as their own part of **Hold space**.
- **Some SRV and vehicle capacities are unknown.** The Inventory window shows the count with "capacity unknown" instead of an estimated figure.
- **"Bought, not yet sold" is an estimate.** It decreases only when WFMT sees a sale. Cargo lost, jettisoned, sold by a carrier order, or moved to a carrier without WFMT running is not subtracted. **Rebuild** recounts from a chosen start time, and **Reset** starts clean.

### Profit and costs

- Only what WFMT has seen is counted. Trades before it first ran are not in the session. The catch-up from copied journals adds only what is new (see [two computers](#using-trade-on-two-computers)).
- Insurance rebuys and fines are not counted, and a cost counts only once WFMT has seen it.
- The game logs advanced maintenance as a repair, so it is given its own line.
- The session balance change is the actual credits difference, so it includes other income.

### Routes and Market (Spansh)

- Prices are only as recent as the last player who docked. Spansh obtains them from other players' game data. Markets older than 30 days are ignored.
- Spansh does not support fleet carriers as route starts, so a route never starts from a carrier. The last real station docked at is used.
- Fleet carriers in results can jump away, so they are listed separately and marked. They can be excluded in the Routes or Market window.
- The jump range is the ship's unladen range. A full hold jumps shorter; **Jump range** in the Routes window overrides it.
- Commodity names must match the game exactly ("Void Opal", not "Void Opals"). Select from the suggestion list.
- The landing pad size is derived from the ship and can be wrong for unusual ships. **Ship size** in the Routes or Market window overrides it.
- Spansh can be slow or refuse a search. The page shows its reason. WFMT retries a busy answer several times, and after repeated failures stops asking Spansh for five minutes and states so.

### Watch list

- A seen price is a snapshot. The game writes a market only when it is opened, so a watched commodity has no price until a station that trades it has been visited or **Refresh** has been pressed. It never updates by itself.
- Stock and demand are from the same moment.
- Fleet carriers are not in the Spansh refresh, so a carrier that sells a commodity cheaply appears only if its market was opened.
- The Spansh refresh makes two requests per commodity (buy, then sell), at least 0.4 seconds apart, so thirty commodities take at least half a minute. It runs in the background, and the row reports completion.

### Limitations

- **Spansh's route planner** accepts a large-pad filter only (`requires_large_pad`).
- **On a first run, Stock looks back only 14 days**, so older purchases that are still unsold are not known.

### Playing on more than one computer, or with EDMC closed

The journal files are the only link, so everything above applies to each machine separately. Copy all journals across (with the game closed where possible), let WFMT read them, and use **Rebuild** for a session that began elsewhere. See [Using Trade on two computers](#using-trade-on-two-computers).

## Using Trade on two computers

Each computer keeps its own Trade records. The game's journals are the only data that must be transferred, and WFMT reads them.

**Files on each computer** (in the WFMT plugin folder, not shared):

| File | Holds |
|---|---|
| `trade_ledger.json` | the session tally |
| `trade_stock.json` | the stock list |
| `trade_carrier.json` | the carrier figures |
| `trade_route_start.json` | each commander's route start |
| `trade_history.json` | saved sessions |
| `trade_journal_scan.json` | the list of journals already read |
| `trade_watch.json` | the watch list and the prices seen in opened markets (one list per commander) |

Copying these files between computers is not needed.

### What to do

1. Copy the journal files from the computer played on into the other computer's journal folder (the folder EDMC's **Journal directory** points at). Copy all files, not only the newest. Copying a file that is already present is harmless. Copying while the game is closed is preferred, because a file still being written is read again later.
2. WFMT looks for unread journal files a few seconds after EDMC starts and then once a minute. It reads each new file (and any file that has grown) once, and adds its trades, costs, stock, carrier figures and docks (for the route start) to this computer's records.

   The Session page does not report this. Each review that reads something is logged in EDMC's log, for example *"Trade read 1 new or changed journal file(s)"*. A new journal is one that was not present at the previous review, or that has grown since.
3. WFMT only adds what is new. Reading a file twice, or out of order, does not count anything twice and does not overwrite a newer carrier figure with an older one.

### Notes

- The file being played now is left alone (EDMC delivers its events live). It is read at a later review, after the game has moved to a new file or EDMC restarts.
- On the first run, only the 80 newest files are read. Older history is not read. If the session began earlier, use **Rebuild**.
- A session that began on the other computer is not copied; only the journals are. If this computer first saw the commander partway through, its tally starts from there. To correct it:
  1. Press **Rebuild** on the Session page and enter the date and time (UTC) the session began.
  2. WFMT recounts the journals from then on and replaces the tally.
  3. Compare the totals with the other computer, adjusting the start time until they match.
  4. Press **Save session** to keep it.
- **Reset** and **Save session** affect only the computer on which they are pressed. Press **Reset** on both when starting a new session.
- Carrier cargo becomes exact only when Carrier Management is opened. Copying journals does not change that.

## Trade settings

Trade's settings are in two places. A number typed outside its range is set to the nearest limit, a box saves on Enter or when focus leaves it, and a tick saves at once.

**In Settings → WFMT → Trade:**

| Setting | Default | Notes |
|---|---|---|
| Enable Spansh trade lookups | Off | The Routes and Market windows do nothing without it. It is the permission to contact Spansh, so it is in Settings. |
| Carrier choice, per commander | Auto | See [above](#your-fleet-carrier-and-squadron-carrier). |

**In the windows:**

| Window | Setting | Default | Notes |
|---|---|---|---|
| Routes | Hops | 3 (range 1 to 10) | Also set by the **Hops** button. |
| Routes | Furthest from the star (ls) | 5,000 (1 to 1,000,000) | |
| Routes | Jump range (ly, blank = my ship's) | blank | Blank uses the ship's unladen range. |
| Routes | Ignore prices older than (hours) | 72 (0 = any age, up to 8,760) | |
| Routes | Systems that need a permit | Off | |
| Routes and Market | Fleet carriers, Ground facilities | On, On | In Routes they apply to routes; in Market to price results and Best picks. Both windows hold the same setting. |
| Routes | Large landing pad only | Off | Excludes stations without a large pad. |
| Routes and Market | Ship size (landing pad) | From my ship | Small, Medium or Large to override. |
| Routes, Round trip | Least supply to buy, Least demand to sell | 200 t each | Excludes thin markets. |
| Routes, Round trip | Search radius (ly, 0 = from jump range) | 0 | 0 uses twice the ship's jump range, between 20 and 100 ly. A value from 5 to 500 is used as given; the search reads at most the nearest 300 stations. |
| Routes, Round trip | Carry only this commodity | blank (anything) | A commodity name (case-insensitive). Both legs of a round trip carry only that commodity. A pair counts only if it trades that commodity at a profit in both directions. |
| Market | 'Near me' search radius (ly) | 100 (1 to 100,000) | Also the Watch list refresh radius (limited to 5 to 5,000 ly there). |
| Session | Count fines and bounties I pay as a running cost | Off | Adds a **Fines and bounties paid** line to the costs; only payments made after enabling are counted. |

See [what goes on the internet](internet-and-privacy.md) for the services contacted, and the [Trade specification](../TRADE_TECH_SPEC.md) for the implementation.

For problems, see [Troubleshooting](troubleshooting.md#trade).
