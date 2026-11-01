# Trade

Trade is about buying and selling: what you've earned after fuel and repairs, how much of your cargo is still
unsold, your ship hold and your carrier's space, and where to find the best routes and prices.

It has three pages. Use the large orange **◀** and **▶** buttons at the top of the panel to move between them. The title between them shows where you are, for example `Session (1/3)`, and WFMT remembers the page you were on:

| Page | What it's for | Needs internet? |
|---|---|---|
| **Session** | Your running profit, costs, hold and carrier cargo | No |
| **Routes** | The best trade routes from where you are | Yes (Spansh, off until you tick it) |
| **Market** | Where to sell or buy a commodity | Yes (Spansh, off until you tick it) |

A pop-out **Trade History** window keeps the sessions you choose to save.

Each page is laid out in sections (orange headings with a rule between them), with label-and-value rows and tables
whose numbers line up in columns. Long station names wrap instead of being cut off. A page's buttons are at the top,
under the page arrows.

**On this page:** [How to](#how-to) · [How a trading session works](#how-a-trading-session-works) ·
[The Session page](#the-session-page) · [Trade History](#trade-history-saving-sessions) · [Routes](#routes) ·
[Market](#market) · [Watch list](#watch-list) · [Fleet and squadron carriers](#your-fleet-carrier-and-squadron-carrier) ·
[What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it) ·
[Using Trade on two computers](#using-trade-on-two-computers) · [Settings](#trade-settings)

## How to

Quick steps for the most common jobs. Each links to the section with the detail. The numbers in the examples are made up.

**See your profit after fuel and repairs**

1. Trade as you normally do. WFMT counts every purchase, sale and running cost it sees in the journal.
2. Open the **Session** page (use the **◀** and **▶** buttons until the title reads `Session (1/3)`).
3. Read **Net profit**: trade profit less fuel, repairs, advanced maintenance, rearm and limpets. The costs are listed under it.

More: [Profit](#the-session-page) and [Worked example: profit after costs](#worked-example-profit-after-costs).

**Track a fleet carrier's cargo**

1. In **Settings → WFMT → Trade**, set the carrier choice for your commander (**Auto** works if your journal has shown a carrier).
2. In the game, open **Carrier Management** once so the game writes the carrier's space.
3. Look at **Carrier cargo** (used out of capacity, with the free tons) and **Carrier reserved for orders** on the Session page. A `~` before the figure means an estimate: open Carrier Management again to make it exact.

More: [Your fleet carrier and squadron carrier](#your-fleet-carrier-and-squadron-carrier).

**Save and review a session**

1. On the Session page press **Save session**. The message `Saved to Trade History.` appears.
2. When the job is done, press **Reset** to start the next one.
3. Press **History**, choose the session in the **SESSION** drop-down, and open the tabs (**Overview**, **Commodities**, **Stations**, and so on).

More: [Trade History](#trade-history-saving-sessions) and [Worked example: review a saved session](#worked-example-review-a-saved-session).

**Find the best route or price**

1. Tick **Enable Spansh trade lookups** in **Settings → WFMT → Trade**.
2. For a route, go to the **Routes** page and press **Find routes** (or **Round trip** for a back-and-forth pair).
3. For a price, go to the **Market** page, choose **Sell** or **Buy**, pick a commodity, then press **Near me**, **Galaxy** or **Best picks**.

More: [Routes](#routes) and [Market](#market).

**Use the watch list**

1. Open the **Watch list** row in Trade mode and press **Watch**.
2. In the box beside **Add a commodity**, type a name, pick it from the suggestions, and press **Add**.
3. Press **Refresh** to ask Spansh for prices, or open station markets in the game to record them.

More: [Watch list](#watch-list).

**Where this comes from:**

- Your trades, costs and cargo come from the journal.
- Where it falls short, WFMT works around it:
  - A carrier's space is only written when you open Carrier Management.
  - A carrier's bay contents are not listed at all. WFMT shows the carrier's orders, and an estimate marked `~`.
  - Routes and prices come from Spansh, a community database.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## How a trading session works

**A session is your running tally, and it belongs to a commander.** It starts the first time WFMT sees you and lasts
**until you press Reset**, however many times you log in or restart EDMC. That is what makes a long job, such as
loading a fleet carrier over several evenings, one session.

- **Each commander has their own.** Switching commander never loses anyone's tally.
- **Playing with EDMC closed is fine.** The next time EDMC sees that commander, WFMT catches the session up from the
  game's journal files and adds what it missed. It only adds what is new, so it can't count anything twice. (On
  Linux this needs EDMC's **Journal directory** to be set; see [WFMT on Linux](linux.md#step-2-tell-edmc-where-elites-journals-are).)
- **Only what WFMT has seen is counted.** Trades made before WFMT first ran, or in a session you reset, aren't
  included.
- **Nothing is kept for good unless you ask.** Press **Save session** to put it in Trade History.

### Finishing a session and starting the next

There is no Start or Track button, because tracking never stops. Instead:

1. Press **Save session** to copy the tally into Trade History. The tally keeps running, and the button stays
   **Save session** (saving again updates the same entry).
2. Press **Reset** to begin a new session. If the current one has unsaved trades, it offers to save first.

**If you skip Reset, your next trades are added to the old session.**

**Example.** You spend Saturday hauling Tritium to your carrier. Saturday night: **Save session**, then **Reset**.
Sunday you do a mining run and sell the lot: that's a fresh session with its own profit figure, and Saturday's is
safe in History.

## The Session page

It reads your journal only. Nothing is sent anywhere. Top to bottom:

**Top of the page.** Before anything has been traded the page says `No trades yet this session.` and `Buy or sell at a market and they are counted here.` If you have only had running costs, it lists them with a **Net** figure.

**Profit.** Trade profit is what you were paid minus what the sold tons cost you, as the game reports it. Stolen or
black-market cargo counts the whole sale. Credits per hour (`+1,200,000 cr/hr`) appears once you've traded for about three minutes (it uses
first trade to last trade). Under it are **Bought** and **Sold** (tons and credits) and a **Best sales** list of your five most profitable commodities, each with its profit and tons. If more than five were traded and the worst one lost money, a **Worst** line names it.

**Running costs**, so the profit is honest:

- **Fuel** (refuelling)
- **Repairs**
- **Advanced maintenance** (the game logs it as a repair that includes module "Wear"; the whole charge goes on its
  own line)
- **Rearm** (ammunition, and restocking an SRV or fighter)
- **Limpets** (bought, less any sold back)
- **Fines and bounties paid** (only if you turn it on in Settings; see below)

Once you've spent anything, the headline becomes **Net profit**: trade profit less those costs. The credits per hour is the net. The trade profit and each cost are listed under it.

What is not counted as a cost:

- Insurance rebuys.
- Fines and bounties you pay off, because a fine usually has nothing to do with your trading. Tick **Count fines and bounties I pay as a running cost** in Settings to count them. Turning it on counts payments from then on, not ones already made.

A cost only counts once WFMT has seen it.

#### Worked example: profit after costs

You sell 100 t of Gold for 1,200,000 cr that cost you 900,000 cr to buy, then pay 18,000 cr for fuel and 12,000 cr
for repairs. These figures are examples. The Session page shows trade profit of 300,000 cr, the fuel and repairs
lines, and the headline **Net profit** of 270,000 cr (300,000 less 30,000). The credits per hour figure is
worked out from that net once you have traded for about three minutes.

**In your ship.** Your **Ship** and the **Landing pad** it needs (for example "Type-9 Heavy" and "Large"; `Unknown` when WFMT cannot tell, in which case no pad filter is applied), then:

- **Ship hold**: how many tons are used, the capacity and how much is free (just `Ship hold: empty` when WFMT does not yet know your capacity and nothing is aboard),
- **Worth at (station)**: what the station you're docked at would pay for the whole hold, once you have opened its commodity market,
- an **In hold / Sells here** table: what each commodity aboard would sell for there. The four largest loads are listed, with `+N more` after.

**Hold space**, just under the landing pad, splits the hold into cargo and limpets (they take hold space like any cargo), for example "312 t cargo (40 t mission, 12 t stolen), 16 t limpets". The free tons are on the **Ship hold** line. The line appears only when there are mission or stolen tons or limpets to show. The mission and stolen figures come from the game's cargo list (`Cargo.json`).

**Carrier cargo.** Your carrier's cargo storage, only shown if you have a carrier (see [below](#your-fleet-carrier-and-squadron-carrier)). Each carrier has its own heading, `Fleet carrier: NAME` or `Squadron carrier: NAME`. Until the game has reported its space, a note under the heading says `Open Carrier Management once to read its cargo space.`

- It is shown as **Carrier cargo** (for example `12,400 / 25,000 t (12,600 free)`) and **Carrier reserved for orders**, so it is never mistaken for your ship hold. **Carrier reserved for orders** is left out when it is 0.
- Under the cargo line, **Carrier crew services** and **Carrier ship / module packs** show what the rest of the carrier's space is spent on. A line is left out when it is 0.
- Below those, when the journal has told WFMT, come the carrier's tritium, where it is, a planned jump, its balance and the trade orders you have set (the first six, with `+N more carrier orders` after).

**No history here.** The Session page shows the present only. The game's lifetime totals (trading, mining, exobiology, fleet carrier)
and your income over time are in the **Credits Ledger** window instead (click the *Credits this session* line under the mode buttons),
where Trade, Exploration and Exobiology stay separate. Saved sessions are in **History**.

### Buttons

- **Reset**: starts the tally again. If the session has trades that were never saved it asks `Save it before starting again?` with **Yes**, **No** and **Cancel**.
- **Save session**: keeps the session in Trade History. Grayed out until there is something to save (a trade or a running cost). A short message at the top of the page begins `Saved to Trade History.` or `Updated this session in Trade History.`, then says how many sessions are saved and reminds you to press **Reset** for a new one.
- **History**: opens the Trade History window.
- **Rebuild**: recounts the session from the journals starting at a time you give, in UTC, as
  `YYYY-MM-DD` or `YYYY-MM-DD HH:MM`, and replaces the tally. Use it when the session began on another computer.
  It asks first if the current tally is unsaved, and says if it finds nothing for this commander in that time. It is grayed out until WFMT knows who you are. After it finishes, check the totals, then press **Save session**.

## Trade History (saving sessions)

Press **Save session** to keep a session. You can keep trading and press it again; that updates the same entry
instead of adding a second one. **Reset** starts a new session, which becomes a new entry if you save it.

Press **History** to open the **Trade History** window. It has a **SESSION** drop-down at the top to pick a saved session
(newest first), and, with more than one commander, a **COMMANDER** filter. Up to 500 sessions are kept; past that the oldest go first. **It opens on the commander you are playing**;
the others are one drop-down choice away (or **All commanders**). The tabs:

| Tab | What it shows |
|---|---|
| **Overview** | Net profit, trade profit, running costs, net per hour, tons sold and trading time at a glance. Then commander, ship, start, end, session length and when saved, balance change, trades, tons bought and sold, profit per ton sold, margin on cost, jumps and light years, net per jump and per light year, each running cost's share of sales, and the best and weakest commodity. |
| **Commodities** | For each one: Bought t, Spent, Avg buy, Sold t, Revenue, Avg sell, Profit, Margin, Profit/t and Unsold t. |
| **Stations** | The same, added up for each station you traded at: Visits, Bought t, Spent, Sold t, Revenue, Profit, Costs and Net. |
| **Route** | The stations in the order you flew them (#, Time, Station, System, What happened, Net and Running, the running total of the net). Going back to a station later is a new visit. |
| **Trades** | Every purchase, sale and cost with its Time, Type, Commodity, t, Unit, Total, Profit, Station and System, 200 at a time (**◀ Earlier** and **Later ▶** change page; it opens on the newest). |
| **Stock & carrier** | What was bought but not sold (a journal **estimate**, with its cost and average cost per ton), the ship hold when you saved, and your carrier's used and free cargo space and the space reserved for orders when you saved. |
| **Lookups** | Two tables of what you asked Spansh during the session: **Spansh routes searched** (Time (UTC), Started from, Hops, Total profit (cr) and the Route) and **Market searches** (Time (UTC), Side, Commodity, Tons, Scope, Best result, System, cr/t and ly). |

Buttons in the window's header: **Help** explains the figures. **Copy summary** puts a plain-text report on the clipboard, **Export log (CSV)** saves the full trade log
to a file you choose, and **Delete session** removes a saved session (it asks first). With no saved sessions the window tells you to press **Save session** on the Trade > Session page.

### Worked example: review a saved session

You spent the evening hauling Tritium and finished at the carrier.

1. On **Session**, press **Save session**. The message at the top says `Saved to Trade History.`
2. Press **Reset** so tomorrow starts clean.
3. Press **History**. The newest session is selected in the **SESSION** drop-down.
4. On **Overview**, check Net profit and net per hour. On **Commodities**, look at Profit/t for each load. On **Route**, see the stations in the order you flew them.
5. Press **Copy summary** to paste a plain-text report, or **Export log (CSV)** to save the full trade log.

**Good to know:**

- The balance change is your real credits difference, so it also includes anything else you earned.
- Times are UTC.
- A session keeps its most recent 5,000 trades and costs. The totals are always exact.
- History is kept in `trade_history.json` in the WFMT plugin folder, which updates leave alone.

## Routes

*Needs the Spansh lookups switched on (Settings → WFMT → Trade).*

**Find routes** asks Spansh for the most profitable trade route from where you are.

**What it uses:**

- *Start:* the station you're docked at, or the last one **this commander** docked at. Each commander has their own and it is
  saved, so it survives switching commander and restarting EDMC, and it is brought up to date from journals written
  while EDMC was closed. A commander who has never docked has none, and the page says so.
- *Cargo size and credits:* from the game.
- *Jump range:* your ship's **unladen** range. Lower it in Settings if a full hold jumps shorter.
- *Pad size:* if your ship needs a large pad, only stations with one are considered.

Before you search, the page shows what it will use (start, ship, cargo, jump range, budget), so you can check it.

**Fleet carriers:** Spansh's planner doesn't know them, so a route never starts from one. If you're docked at your
carrier, it starts from the last real station you docked at, and the page says where. If Spansh refuses a search,
the page shows its reason.

**Round trip is the exception:** it pairs stations itself from a station search, which lists fleet carriers, so when you are docked at
a fleet carrier (your own, say) the round trip starts from that carrier's market, and the result names where it started. Spansh must
have a recent market for the carrier, so open its commodity market once so it is reported; if it has none the page says so.

### Worked example: find a route

You are docked at a station and want a profitable run.

1. Tick **Enable Spansh trade lookups** in **Settings → WFMT → Trade** if you have not.
2. Go to the **Routes** page. The page lists what it will use: start, ship, cargo, jump range and budget. Check them.
3. Press **Hops** until it reads `Hops: 3`, then press **Find routes**.
4. Wait while the page says whether the search is in Spansh's queue or being calculated. Press **Cancel** to stop.
5. Read **Total profit** and **Est. profit / hour**, then each numbered hop. Press **Copy next system** and paste it into the galaxy map.

If the first destination is Example System, that is the name now on your clipboard.

### Hops

The **Hops** button shows the current length (for example `Hops: 3`). Each press cycles it through 2, 3, 4 and 5. It
is the same setting as *Route hops* in Settings, which accepts 1 to 10.

**2 hops** is the choice for a back-and-forth pair. When the route ends at the station it started from and every leg
carries cargo, the result is headed "repeatable loop" and says you can fly it again. With 2 hops that do not make a pair, the page says
the second hop ends at a third station. A leg with no cargo is flagged.

### Round trip

Spansh's planner returns the best *chain*, which doesn't always come back. **Round trip** finds the best
back-and-forth pair itself.

How it works, in plain terms:

1. It asks Spansh for the markets of the nearest stations (up to 300, within twice your jump range, but never less
   than 20 ly or more than 100 ly, unless you set a search radius in Settings).
2. For each neighbor, it works out what to carry out and what to bring back.
3. A pair only counts when **both legs make a profit, so you never fly empty**.
4. Each leg fills the hold with the most profitable commodity first and tops up with the next, limited by the supply
   where you buy, the demand where you sell and what you can afford.
5. Pairs are ranked by estimated profit per hour, and the top three are shown with what to carry each way. Every pair, not
   only the best, lists its commodities on each leg with the tons, the profit, what it costs where you buy, what it sells for
   where you sell (and the profit per ton), and the supply and demand behind it. Three commodities are listed per leg, with
   "+N more" after.

It uses the same filters as Find routes (price age, ground facilities, fleet carriers, your ship's pad size,
distance from the star), plus the **least supply** and **least demand** settings (200 t each by default), so thin
markets are left out. It takes about 20 seconds and makes one to three Spansh requests (100 stations each).

**Example.** You want a pair of stations to shuttle between. Dock at your start station, go to **Routes** and press
**Round trip**. After about 20 seconds you see the top three pairs, each with what to carry out and what to bring
back. Every leg makes a profit, so you never fly empty.

### Reading the result

Spansh can take a minute or two. While you wait the page says whether the search is **waiting in Spansh's queue** or being
calculated, so you can tell a busy Spansh from a stalled search. **Cancel** stops waiting. The result shows:

- **Total profit** and **Est. profit / hour** (a rough figure worked out from your jump range), then **Hops**,
- each hop, numbered: the two stations, the profit and the distance in light years, then the destination system and its distance from the star, the best commodity with its tons, and the supply at the buying station and the
  demand at the selling one (the first four hops are shown, with "+N more hop(s)" after).

**Copy next system** puts the first destination on your clipboard so you can paste it into the galaxy map.

## Market

*Needs the Spansh lookups switched on.*

Finds where to **sell** or where to **buy** a commodity.

The **Commodity** box and the **Sell** / **Buy** buttons beside **I want to:** appear on this page only once the Spansh lookups are switched on. Without them the page tells you to turn them on in Settings → WFMT → Trade.

1. **Choose Sell or Buy** with the **I want to** buttons under the Commodity box (the lit one is chosen). It is remembered.
2. **Pick a commodity.** Click the **Commodity** box and start typing. Enter in the box runs **Near me**. Suggestions fill in as you type: first what
   you carry and what the station you're at buys, then every commodity.
   - When *selling*, you can leave it empty to search for the commodity you carry the most of.
   - When *buying*, type what you want.
3. **Press Near me** to look within a radius of your system (100 ly unless you change it), or **Galaxy** to look
   everywhere. You can press both. While a search is running the **Near me** button becomes **Cancel**, and the page counts the seconds.

Before you search, the page shows what it will use: your ship and landing pad, the commodity and amount (marked `(your free hold space)` when you are buying), and the radius. The lit **Sell** or **Buy** button shows which way you are searching.

**Example.** You're hauling 200 t of Palladium and want to sell. Leave the box empty (it picks Palladium), press
**Sell**, then **Near me**. You get a list of stations within 100 ly ranked by what your whole load would earn.

### How results are ranked

- **Selling:** by what *your load* would earn: price per ton times the tons the station still wants. A station
  paying more per ton but wanting only 40 t is worth less to a 200 t hold. If you haven't got any of it, a full
  hold is assumed.
- **Buying:** the amount is your *free hold space*. Stations that can supply all of it come first, cheapest first.
  Stations that can only supply part come after, marked "only N t in stock".

Once you've run both searches (near and galaxy), it tells you which is better and by how much (more money when
selling, a lower price when buying), and how much further away it is. When nothing in the galaxy beats the best nearby it says only `Best overall is nearby.` (the station is the first one listed).

### What each result tells you

Every result says what kind of place it is: **orbital** or **ground** (on a planet's surface), the station type
(Coriolis Starport, Planetary Outpost and so on), and how far it is from the arrival star in light seconds. Stations
with no landing pad your ship fits are left out.

### Fleet carriers in results

**Fleet carriers are listed in their own section**, marked "they can move", because a carrier can jump away before
you arrive. They are asked for separately and weighted about one carrier to every three stations, so cheap carriers
never crowd the real stations out of the list. A line says when a carrier would beat the best station.

In **Settings → WFMT → Trade** you can stop searching for fleet carriers, for **ground facilities** (planetary ports
and outposts, and settlements), or both, which leaves only stations in space.

### Best picks

The **Best picks** button answers "where should I buy (or sell) this?" with four choices for the commodity in the box
(buying: what you typed; selling: what you typed, or your largest load):

| Pick | Meaning |
|---|---|
| **Closest** | The nearest station that has it in stock (buying) or wants it (selling), whatever the price. |
| **Best local** | The cheapest (buying) or highest-paying (selling) station within your **Near me** radius. |
| **Cheapest anywhere** / **Highest anywhere** | The best price in the whole galaxy, nearest first when prices tie. |
| **Recommended** | The nearest station whose price is within **10%** of the best price in the galaxy: nearly the best price without the long trip. |

- "In stock" means at least the amount shown (your free hold space when buying, your load when selling). If no station has that much, the pick falls back to the nearest with any and says how much it has ("only 12 t in stock" when buying, "only 12 t wanted" when selling).
- Your landing pad size, the ground-facilities setting and the carriers setting apply.
- Market data older than 7 days is ignored.
- A fleet carrier is not offered as a pick (it can move). If one has a better price than the cheapest station, it is mentioned underneath.
- A station that is two picks is listed for each, with "same as ..." beside the second.

It asks Spansh about four times (five with carriers), one after another, so it takes a few seconds. The numbers are the same as the other results: cr/t, total for the amount, and distance.

**Example.** You need 64 t of Tritium and have 64 t of free hold space. Choose **Buy**, type `Tritium` in the Commodity box
(pick it from the suggestions) and press **Best picks**. After a few seconds you see **Closest**, **Best local**,
**Cheapest anywhere** and **Recommended**. If **Recommended** is within 10% of the galaxy's best price and much
nearer, that is usually the one to fly to.

The same four picks for a mission's cargo are in the Mission mode ([Source commodities](missions.md#source-commodities)).

### Price finder

Opens the finder that Mining's **Prices** button also uses ([Find Best Price](mining.md#prices-find-best-price)), for any commodity, to buy or sell, with its own **Where** distance
drop-down. The button is grayed out until Trade's Spansh lookups are on. Its suggestions list what you carry and what this station buys first, then every commodity. The finder always leaves fleet carriers out and asks only for markets updated in the last 30 days, whatever the Trade settings say.

**Prices are only as fresh as the last player who docked there.** Markets older than 30 days are ignored. Check the
market when you arrive.

## Watch list

A short list of the commodities you care about, with the best price to buy and to sell each at a glance. It is a collapsible **Watch list**
row in Trade mode, under the page (it starts folded; click its heading to open or fold it, and the heading shows `- 3 watched` when folded). Each line reads like `Gold: buy 9,100 / sell 11,200`, with `-` for a side nobody has a price for. Five commodities are listed, then `+N more in the window`. Two buttons sit under the lines: **Refresh** asks Spansh, and **Watch** opens the window. A status line under the list says what the last refresh did. With nothing watched the row says `Nothing watched yet. Press Watch to add commodities.`

- **Add a commodity** in the window: click the box beside **Add a commodity**, start typing and pick from the suggestions (the same names the Market page uses), then
  press **Add** or Enter. Up to 30. Select a commodity and press **Remove** to take it off and forget its prices; press it twice (the first press asks, the second, within a few seconds, removes).
- **The two tables.** The top table lists every watched commodity with **Commodity**, **Buy (cr/t)**, **Buy at**, **Sell (cr/t)** and **Sell at**. Select a row and the lower table lists where it was seen: **From** (`Seen` for a market you opened, `Spansh: buy` or `Spansh: sell`), **Station**, **System**, **Buy (cr/t)**, **Stock**, **Sell (cr/t)**, **Demand**, **ly** and **Age**. The window's **Help** button explains them.
- **Where the prices come from.** Every time you open a station's commodity market in the game, WFMT reads it and keeps the buy price
  (what the station charges), the sell price (what it pays), the stock and the demand of each commodity you watch, for the newest 12
  stations. This needs nothing turned on and sends nothing anywhere. Pick a commodity in the window to see every market it was seen at.
- **Refresh from Spansh.** **Refresh** on the row (or **Refresh from Spansh** in the window) asks Spansh for the cheapest station to buy and
  the dearest to sell each watched commodity, within your "Near me" radius of the system you are in.
  - It needs *Enable Spansh trade lookups* in Settings.
  - It sends only the commodity names and your system name, never your commander name.
  - Fleet carriers are left out, because they move.
  - The answer is kept until you close EDMC. The search radius is your "Near me" radius (5 to 5,000 ly).
- **The price shown is the best of both**: the cheapest to buy and the dearest to sell among the markets you opened and Spansh's answer. The
  window says where each price is, how many tons the station has to sell you (or still wants from you), where the price is from and how
  old it is. The row shows only the prices; open the window for the place.
- **Spansh's five best stations for each side** are kept, not just the best one, and listed under the commodity you pick, with their stock or
  demand and their distance in light years, so you have others to go to when one runs short.

**Example.** You want to keep an eye on Gold and Palladium.

1. Open the **Watch list** row and press **Watch**.
2. In the box beside **Add a commodity**, type `Gold`, pick it and press **Add**. Do the same for `Palladium`.
3. Press **Refresh from Spansh** in the window. The status line says when it is done.
4. Close the window. The row now shows lines such as `Gold: buy 9,100 / sell 11,200` (example prices).
5. Open the window again and select Gold to see where each price was seen, its stock or demand, the distance and the age.

**A price is only true when it was seen.** A market you opened last week may have changed, and Spansh's data is only as fresh as the last
player who docked there (this refresh ignores markets older than 7 days). Check the age, and the market when you arrive.

The list is kept on your computer for the commander who made it. Another commander on the same install has their own.

## Your fleet carrier and squadron carrier

Not every commander has a carrier, and some have a fleet carrier, a squadron carrier or both. Under
**Settings → WFMT → Trade**, each commander WFMT has seen gets a choice:

**Auto** (show whatever your journal has revealed) · **None** · **Fleet** · **Squadron** · **Both**

Nothing is shown for a carrier you haven't chosen. For each one, the Session page shows:

- cargo used, free, and reserved for orders, for example "5,060 / 23,720 t used, 18,660 t free",
- what the rest of the space is spent on (crew, packs),
- when the journal has told WFMT: **Carrier tritium**, **Carrier is at**, **Carrier jump planned**, **Carrier balance**,
- one line per order you have set (**Carrier selling Gold** 300 t @ 12,000 cr, **Carrier buying Tritium**).

A carrier being decommissioned is flagged.

**Example.** You load 20,000 t of cargo onto your carrier over an evening.

1. In **Settings → WFMT → Trade**, set your commander's choice to **Fleet** (or leave it on **Auto**).
2. Dock at your carrier and do your transfers. The Session page's **Carrier cargo** goes up with each one.
3. If the figure shows a `~` or looks wrong after a big unload, open Carrier Management in the game. Within a couple
   of seconds the page shows the exact **Carrier cargo** and **Carrier reserved for orders**.

### How the number stays up to date

The game only reports a carrier's space when you **open Carrier Management**, so do that once. WFMT also reads your
recent journal files when it starts, so it finds the last time you did, even if EDMC was restarted since.

After that:

- It follows your cargo transfers. A transfer is counted for the carrier you're **docked at**, so docking at
  someone else's carrier never changes your figure.
- Reserved space, and the tons your carrier's trade orders move, only update the next time you open Carrier
  Management. The orders themselves, tritium deposits, the carrier's location and jump plans are recorded as they
  happen, so those lines stay current.

**To get the real, exact cargo figure, open Carrier Management** (the carrier's management screen, where you see its
services and cargo). The game writes a fresh report of the whole inventory and WFMT shows it within a couple of
seconds. Nothing in the game's files lists everything in the carrier's hold (the report gives only the total, and the
orders name only the commodities on order), so there is no other way to read it.

### Quirks worth knowing

- **A `~` before the figure** (for example `~23,720 / 23,720 t`) **means an estimate.** The transfers WFMT has seen
  add up to more than the carrier can hold (or take out more than it holds), so cargo left the carrier without the
  game writing anything down, usually a trade order or a sale made from the carrier. A note under the figure says
  so. Open Carrier Management and the `~` goes away.
- **Playing on another computer leaves the figure stale** until the journals are copied over and read, and even then
  it is only as good as the last time you opened Carrier Management. Play with EDMC closed on this computer is read
  back when EDMC next starts.
- **The figure can look wrong right after you unload.** The unload is in the journal but the total is not. Open
  Carrier Management after a big load to put an exact number back.

## What the game does and doesn't tell us, and how to work around it

WFMT, like every third-party tool, only knows what Elite Dangerous writes to its journal files.

- It adds what Spansh, a community database, reports, and what Frontier's servers give a signed-in EDMC (a carrier's real cargo), and works around the rest.
- Some things the game never records, or records late or only in part. Rather than guess quietly, WFMT shows the figure it has and says how sure it is.
- Below is every gap we know about, what it looks like on screen, and what to do.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

### Your fleet carrier

| What you might expect | What the game gives | What to do |
|---|---|---|
| The carrier's space to be known as soon as you log in | The space report (`CarrierStats`) is written **only when you open Carrier Management**. It is not written at login. | Open Carrier Management once per session. WFMT reads recent journals at start-up, so the last time you did still counts after an EDMC restart. |
| A list of what commodities are in the carrier's bay | Only the **total tons** in the bay. Commodity names are not in the space report. | The carrier's own orders are the closest thing: WFMT lists them (below), and a sale order names a commodity that is aboard. Carrier Management in the game lists the contents. WFMT does not invent a per-commodity list. |
| Trade orders to be tracked as they fill | The game writes an order **when you place or cancel it** (`CarrierTradeOrder`), not each ton it later moves. | WFMT shows the orders you have set (commodity, tons, price). The tons that have moved, and the cargo figure, only update in the next space report: open Carrier Management after an order completes. Until then the cargo figure may be too high and shows a `~`. |
| Space reserved for orders to follow along | Only updates in the space report. | Same: open Carrier Management. |
| Lifetime totals to move while you play | The game writes its `Statistics` event only at login. | They are on the Credits Ledger's Lifetime tab and refresh the next time you log in. |
| Tritium, location and jump plans | Tritium comes from the space report and from each fuel deposit you make; the location is written at login and after a jump; a jump request carries the destination and departure time. Fuel the carrier burns jumping is **not** written. | WFMT shows the tritium, where the carrier is and a planned jump. After a jump, open Carrier Management for the real tritium figure. A plan is dropped once its departure time is well past. |
| Cargo moved by someone else to be seen | WFMT follows the transfers **your** journal records while you are docked at the carrier. We have not seen the game report anyone else's. | Open Carrier Management when someone else may have used the bay (a squadron carrier especially). |
| The figure to be right right after unloading | The transfer is in the journal but the total is not updated. | WFMT counts the transfer itself; open Carrier Management after a big load to put the exact number back. |
| Crew and pack space to be listed by type | Crew services, ship packs and module packs are reported, but only in the same report as above. | Same. |

**A `~` before a figure is WFMT telling you it is an estimate.** The transfers it has seen add up to more than the bay
can hold, so something left the bay without a journal entry. It is a prompt, not an error: open Carrier Management and
it goes away.

### Your ship's hold

- **Mission and stolen cargo** are told apart from the cargo list the game writes whenever the hold changes (each
  entry says if it is stolen, or belongs to a mission). If that list is missing or unreadable, the line shows the
  total without the split.
- **Limpets are counted as cargo by the game**, which is why they are shown as their own part of **Hold space**:
  they use tons you might think are free.
- **Some SRV and vehicle capacities are unknown**; the Inventory window shows the count with "capacity unknown" rather
  than a guessed figure.
- **"Bought, not yet sold" is an estimate.** It only comes down when WFMT sees you sell. Cargo lost, jettisoned, sold by
  a carrier order, or moved to a carrier without WFMT running is not subtracted. Use **Rebuild** to recount from a
  chosen start time, or **Reset** to start clean.

### Profit and costs

- **Only what WFMT has seen is counted.** Trades before it first ran are not in the session. Keep EDMC running, or
  copy the journals over later (see [two computers](#using-trade-on-two-computers)); the catch-up adds only what is
  new.
- **Insurance rebuys and fines are not counted**, and a cost only counts once WFMT has seen it.
- **Advanced maintenance is logged by the game as a repair**, so it gets its own line to keep it visible.
- **The session balance change is your real credits difference**, so it also includes anything else you earned.

### Routes and Market (Spansh)

- **Prices are only as fresh as the last player who docked there.** Spansh gets them from other players' game data.
  Markets older than 30 days are ignored; check the market when you arrive.
- **Spansh doesn't know fleet carriers as route starts**, so a route never starts from your carrier. Dock at a real
  station first, or accept the last station you docked at.
- **Fleet carriers in results can jump away**, so they are listed apart and marked. Switch them off in Settings if you
  only want fixed stations.
- **Jump range is your ship's unladen range.** A full hold jumps shorter, so lower it in Settings if routes are too
  long.
- **Commodity names must match the game exactly** ("Void Opal", not "Void Opals"). Pick from the suggestion list.
- **The landing pad size is worked out from your ship** and can be wrong for unusual ships. Override it in Settings.
- **Spansh can be slow or refuse a search.** Cancel and try again later; the page shows its reason. WFMT retries a busy answer a few times, and after repeated failures stops asking Spansh for five minutes and says so.

### Watch list

- **A seen price is a snapshot.** The game only writes a market when you open it, so a watched commodity has no price until you have
  visited a station that trades it (or pressed Refresh). It never updates by itself.
- **Stock and demand are from that moment too.** A station that showed 5,000 t last week may be empty now.
- **Fleet carriers are not in the Spansh refresh**, so a carrier that sells a commodity cheaply only shows up if you opened its market.
- **The Spansh refresh makes two requests per commodity** (buy, then sell), at least 0.4 seconds apart, so thirty commodities take
  at least half a minute (longer if Spansh is slow). It runs in the background; the row says when it is done.

### Gaps we have not been able to confirm

- **Squadron carriers.** We assume a squadron carrier's space report matches a fleet carrier's. No real one was
  available to check, so treat its figures with care and report anything odd.
- **Ship pad sizes** come from Coriolis data and a partly hand-written name map. A ship that doesn't match shows
  **Landing pad: Unknown** and is not filtered. Set the size yourself in Settings.
- **Spansh's route planner can filter for large pads but not medium ones.** If your ship needs a medium pad, check
  the pad at each stop.
- **A price can't be shown as current**, only that the market was updated in the last 30 days.
- **The commodity list and ship classes are snapshots.** A new commodity or ship needs a WFMT update.
- **On a first run, Stock looks back only 14 days**, so older purchases that are still unsold aren't known.

### Playing on more than one computer, or with EDMC closed

The journal files are the only link, so everything above applies to each machine separately. Copy the journals across
(all of them, with the game closed if you can), let WFMT read them, and use **Rebuild** for a session that began
elsewhere. See [Using Trade on two computers](#using-trade-on-two-computers).

## Using Trade on two computers

If you play on more than one computer (say Windows and Linux), each one keeps **its own** Trade records. The game's
journals are the only thing that has to travel between them, and WFMT reads them for you.

**What lives on each computer** (files in the WFMT plugin folder, never shared):

| File | Holds |
|---|---|
| `trade_ledger.json` | the session tally |
| `trade_stock.json` | the stock list |
| `trade_carrier.json` | the carrier figures |
| `trade_route_start.json` | each commander's route start |
| `trade_history.json` | saved sessions |
| `trade_journal_scan.json` | the list of journals already read |
| `trade_watch.json` | the watch list and the prices seen in markets you opened (one list per commander) |

Copying these between computers is not needed and not recommended.

### What to do

1. **Copy the journal files** from the computer you played on into the other computer's journal folder (the one
   EDMC's **Journal directory** points at). Copy them all, not just the newest. Copying a file that is already there
   is fine. Doing it while the game is closed is best, because a file that is still being written is read again
   later.
2. **That's it.** WFMT looks for journal files it hasn't read **a few seconds after EDMC starts and then once a
   minute**. It reads each new file (and any file that has grown since) once, and adds its trades, costs, stock and
   carrier figures and docks (for the route start) to this computer's records.

   The Session page does not report this (it shows no history). Each review that reads something is logged in EDMC's log,
   for example *"Trade read 1 new or changed journal file(s)"*. A "new" journal is one that was not there at the previous
   review, or that has grown since.
3. It only ever **adds what is new**. Reading a file twice, or out of order, never counts anything twice and never
   overwrites a newer carrier figure with an older one.

### Things that are not obvious

- **The file you are playing right now is left alone** (EDMC already delivers its events live). It is read on a
  later look, after the game has moved on to a new file or after EDMC restarts.
- **The first time, only the 80 newest files are read.** Older history is not crawled. If your session began before
  that, use **Rebuild**.
- **A session that began on the other computer is not copied, only the journals are.** If this computer first met
  the commander partway through, its tally starts from there. To fix it:
  1. Press **Rebuild** on the Session page and give the date and time (UTC) the session began.
  2. WFMT recounts the journals from then on and replaces the tally.
  3. Check the totals against the other computer, adjusting the start time until they match.
  4. Press **Save session** if you want to keep it.
- **Reset and Save session only affect the computer you press them on.** Press Reset on both if you start a fresh
  session.
- **Carrier cargo only becomes exact when you open Carrier Management.** Copying journals does not change that.

## Trade settings

**Settings → WFMT → Trade** (the number settings are grouped under **Routes**, **Round trips** and **Market** headings; a number typed outside its range snaps back inside it when you leave the box):

| Setting | Default | Notes |
|---|---|---|
| Enable Spansh trade lookups | Off | The Routes and Market pages do nothing without it. |
| Route hops | 3 (range 1 to 10) | Also set by the **Hops** button. |
| Max distance from the star | 5,000 ls (1 to 1,000,000) | For Routes. |
| Jump range override | blank | Blank uses your ship's unladen range. |
| Only stations with a large landing pad | Off | Leaves out stations without a large pad, in Routes. |
| Round trips: least supply / least demand | 200 t each | Leaves thin markets out. |
| Round trips: search radius | 0 (from my jump range) | How far around your start to look, in light years. 0 uses twice your ship's jump range, between 20 and 100 ly. Any number from 5 to 500 is used as given; the search reads at most the nearest 300 stations. |
| Routes: **Ignore prices older than** | 72 hours (0 = any age, up to 8,760) | |
| Routes may use systems that need a permit | Off | |
| "Near me" price search radius | 100 ly (1 to 100,000) | Also the Watch list refresh radius (limited to 5 to 5,000 ly there). |
| Include fleet carriers / ground facilities | On / On | Applies to prices **and routes**. |
| Ship size (landing pad) | From my ship | Or Small, Medium or Large if it guesses wrong. |
| Count fines and bounties I pay as a running cost | Off | Adds a **Fines and bounties paid** line to the costs; only payments made after you tick it. |
| Carrier choice, per commander | Auto | See above. |

See [what goes on the internet](internet-and-privacy.md) for exactly what is contacted, and the
[Trade specification](../TRADE_TECH_SPEC.md) for how it all works.

Stuck? See [Troubleshooting](troubleshooting.md#trade).
