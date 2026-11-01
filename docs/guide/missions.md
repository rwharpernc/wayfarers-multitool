# Missions

One view of every mission on your board, sorted by type, plus Community Goals and what they paid you.

**Where this comes from:** everything here comes from the journal alone, and the journal is thin in places.

- Wing and on-foot kills are often missing until a mission completes.
- Active missions are only listed at login.
- A Community Goal never announces its end.

Where WFMT has to work something out, it marks it (a `~`). See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## How to

Short steps for the common jobs. Each one points at the section with the full detail.

### See every active mission in one view

1. Press **Missions window** at the bottom of the Missions panel (or click any mission's card).
2. Stay on the **Active** tab for one row per mission, ready ones first and then the soonest to expire. Use the **By place** tab to see the same missions grouped by the system you must go to.
3. Click a row to read its faction, where to go, cargo, exact reward and expiry in the detail strip.

More: [The Missions window](#the-missions-window).

### Read the progress bars

1. Open the **Progress** column in the Missions window, or page the Missions panel to **Massacre (Space)** or **Settlement Raids (Ground)** for the kill bars.
2. Read the text first: `20/60` is cargo handed in, `36/36 loaded` is cargo picked up but not yet handed in, `~18/40 kills` is a kill estimate and `36/60 held` is cargo in your hold for a source and return mission.
3. Read the color of the row: green is ready to hand in, red is under an hour left, amber is under six hours, lime is half or more done and blue is started but under half.
4. Treat a `~` as "at least this many". The game's own mission screen is the final word.

More: [Progress](#progress) and [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it).

### Open the Missions window

1. Press **Mission** in the mode bar.
2. Press **Missions window** at the bottom of the panel, or click a mission's card to open the window on that mission.
3. Close it when you are done. It remembers its size and position, and while it is open it keeps counting down and updating as you accept and hand in missions.

More: [The Missions window](#the-missions-window).

### Find where to buy the cargo for a mission

1. Turn on **Enable Spansh trade lookups** in Settings → WFMT → Trade (it is off by default). If you skip this, the window asks when you press **Find sources**.
2. Press **Find sources** at the bottom of the Missions panel, or **Sources** in the Missions window.
3. Choose **From where I am** or **From the turn-in system**, then press **Find sources** in the new window.
4. Wait for the rows to fill in (`Asking Spansh... 2 of 5 done`), pick a row and press **Copy system** to paste the name into the galaxy map.

More: [Source commodities](#source-commodities) and [Finding sources](#finding-sources).

### Track kill missions

1. Accept your massacre or settlement-raid missions as usual.
2. Page the Missions panel to **Massacre (Space)** (or **Settlement Raids (Ground)**). There is one block per issuing faction with the kills as `done/required`.
3. Fly and fight. The `~` before a count means an estimate, because wing and on-foot kills are often missing from the journal until the mission completes.
4. When the kills are done the mission turns ready (green, with a tick) and shows where to hand it in.
5. Pin a mission (the **Pin / Unpin** button in the Missions window) if you want it listed first on the overlay card.

More: [Using it](#using-it), [Pinned missions](#pinned-missions) and [Missions on the overlay](#missions-on-the-overlay).

### Worked examples

The numbers and names below are made up to show how the screens read. The wording is what WFMT shows.

**A cargo delivery mission, from accept to turn-in.** You accept a mission to collect 60 Gold and bring it back.

1. The mission appears on the **Trade & Mining** page. At the top, **Commodities needed:** reads `Gold (1 mission)  x60`.
2. Open the Missions window. The Progress column starts at `0/60 held` if you hold no Gold, because the game writes nothing about a source and return mission until you hand cargo in.
3. Press **Find sources**, choose where to measure from, and buy at the station you pick. As the Gold arrives in your hold the row follows: `36/60 held`, then `60/60 held`. If you already carried Gold, that counts too, and Gold in a fleet carrier does not.
4. Fly to the place in the **Go to** column. The row's `→` line on the panel card shows the same place.
5. Hand the cargo in. The game now reports the count, and the row reads by the game's own figure, for example `20/60` after a partial hand-in. When the whole mission is done the row turns green and shows the hand-in place, which may be a different station from the one you accepted at. Hand in there.
6. The mission leaves the list when the game reports it completed, and a pin on it is removed with it.

**A kill-mission stack.** You hold five massacre missions from three stations. Three are for Faction A (20, 20 and 10 kills) and two are for Faction B (15 and 15 kills).

1. Page to **Massacre (Space)**. There are two blocks, not five counters. Faction A reads `0/50` and Faction B reads `0/30`.
2. Under each block's bar the reward shows the total of the stacked missions. Faction B's block shows `Δ20`: the biggest stack (Faction A) needs 20 more kills than this one. Faction A's `Δ` compares it with the next biggest stack (Faction B) and reads `Δ-20`: it leads by 20.
3. After 18 kills against Faction A, its block reads `~18/50`, because some of those kills may have come from a wing-mate. The **Sum** line at the end totals the biggest stack (Faction A, 50 kills) with a bar and the total reward.
4. Kill with a wing-mate, then check the game's own mission screen if the count looks low. The `~` means "at least this many".
5. Once the kills for a mission are done, the game redirects you and WFMT marks it ready, with the place to hand it in.

**A Where to buy lookup.** You hold missions for 60 Gold and 40 Palladium and you are docked in the system where you will hand in the Palladium.

1. Press **Find sources**. The Source commodities window lists the commodities with the **Need** summed over all your missions: Gold 60 and Palladium 40.
2. Leave **From where I am** selected, then press **Find sources**. The status reads `Asking Spansh... 1 of 2 done`, then `2 of 2 done`.
3. Each commodity gets its picks: closest, best local, cheapest anywhere and recommended. Read the **Largest pad** column before you go. `Large`, `Medium` or `Small` says whether your ship fits, and `?` means Spansh gave no pad data.
4. Select the Gold row you prefer and press **Copy system**. Paste the name into the galaxy map to plot the route.
5. To compare against your delivery point instead, choose **From the turn-in system**. That clears the results, so press **Find sources** again.

**A mission that expired.** You accepted a delivery mission with 2 days to run and then stopped playing for a week.

1. While the mission was running its card read `Expires: 2d 4h`, then `Expires: 1h 30m` with a `⚠` once it dropped under two hours, and the overlay card showed it red under an hour and amber under six hours.
2. When the time ran out, the card and the overlay show `Expired` (overlay: `expired`) while the game has not yet reported anything.
3. The game writes nothing when a mission simply runs out, so the row can stay on your board until your next login. The game then sends its own list of active missions and WFMT drops the dead one.
4. If you want the board correct sooner, log in again (main menu and back). If the game did write a failed or abandoned event, the mission goes at once.
5. A pin on it goes too, and cargo already handed in earlier is not counted anywhere else.

## Using it

Press **Mission** in the mode bar. At the top a line reads `Missions: 7/20` (how many missions you hold of the game's limit of 20; switch it off with *Show mission count* in Settings). Under it the panel shows one category at a time, with a line like `◀  Combat (3)  ▶`. Click the **◀** or **▶** arrow to
page between categories; the number is how many missions are in that category (left off when the count line above is shown and every mission is in that one category, since it would repeat `Missions: N/20`). The pages, in order, are:

**Massacre (Space) · Settlement Raids (Ground) · Combat · Trade & Mining · Passenger · Covert / On-Foot Ops · Other · Community Goals**

- **Massacre** and **Settlement Raids** missions show grouped **kill-progress bars**, so you can see at a glance how
  many kills are still needed across all your missions for the same faction.
  - There is one block per **issuing faction**. The top line is the faction's name (with `⚠ Illegal` when any of its stacked missions is illegal) and its kills as `done/required`. A `~` before the count means an estimate (see below).
  - The second line is a progress bar, the reward (`12.5M (4.0M)`: the total of the stacked missions, and in brackets the part that came from wing missions, which are shared), and `Δ` followed by a number: how many more kills the biggest stack needs than this one (for the biggest stack, the next biggest stack's kills minus its own, so it reads as a negative number such as `Δ-20`: it leads by 20; with only one stack it reads `Δ0`).
  - A **Sum** line at the end totals the biggest stack with a bar and the total reward (switch it off with *Show totals row*). It is left out when only one faction has a block, because it would repeat that block.
  - Under them, `Settlements:` lists the ground targets (switch it off with *Show target settlement*), and `⚠` notes warn when the missions name several target factions or several target systems, or that `~kills = estimate, not exact`.
  - With no such mission the page says so; if WFMT has no mission data yet it asks you to relog (`Relog (main menu and back) to sync missions.`).
- Everything else shows **one card per mission**, soonest to expire first. A card has the mission's name (with `⚠ Illegal` or `🤝 Wing` badges), the issuing faction, `Mine via: ...` for a mining mission, its status (`Pending` or `✓ Complete`) and reward, a `Cargo: 120/200 collected, 80 delivered` line for cargo missions, `→ <system> / <station>` (where to go now: the hand-in place once the mission is done) and `Expires: 2d 4h` (`⚠` when under two hours remain). Click a card to open the Missions window on that mission.
- The **Trade & Mining** page starts with **Commodities needed:** a total per commodity (`Gold (2 missions)  x150`) of the cargo you still have to find (switch it off with *Show commodities needed*).
- The **Community Goals** page has one card per goal: its title, the system and market, a bar and the tier reached against the top tier (with `✓ Complete`), `Your contribution`, the bonus, `🏆 Top rank` when you are in the top rank, and the expiry. Under the goals, **Paid out** lists the latest three payouts.
- Two buttons at the very bottom of the panel, on every page: **Missions window** (every active mission across every category) and **Find sources** (where to buy the cargo your missions need).

## The Missions window

Opens from the **Missions window** button at the bottom of the panel (or by clicking a mission's card). It stays live while you play: times left count down, progress moves, and missions
come and go as you accept and hand them in.

- **Active** tab: one row per mission, ready ones (✓, green) first, then the soonest to expire.
  - Columns: a pin column (★ for a pinned mission), **Mission**, **Kind**, **Faction**, **Go to** (the hand-in place once a mission is done), **Progress** (see below), **Reward** and **Left** (time left).
  - Above the table, in the window's subtitle, the summary: how many missions, how many are ready or under an hour from expiring, how many are pinned, and the rewards held.
  - The progress column also draws a small bar, so it reads by shape as well as color.
  - A row's color tells you where it stands:
    - **green**: ready to hand in
    - **red**: under an hour left
    - **amber**: under six hours left
    - **lime**: half or more done
    - **blue**: started but under half
- **By place** tab: the same missions grouped by the system to go to, your own system first (`(you are here)`), then the next jump you have targeted (`(next jump)`), then the places with
  something ready. A route plan at a glance. Each group's heading counts its missions and how many are ready; under it the columns are **Mission**, **Station**, **Progress**, **Reward** and **Left**.
- **Detail strip** below the tabs: click a mission for the faction, status, where to go, cargo and commodity (with the tons still needed), exact reward, wing,
  when it was accepted and when it expires.
- The buttons are in the window's header:
  - **Pin / Unpin** (the highlighted button) pins the selected mission, or unpins it. **Pin all here** pins every mission for the system you are in. **Unpin all** clears them. With no commander known yet the status line asks you to log in.
  - **Copy system** puts the selected mission's system on the clipboard for the galaxy map.
  - **Sources** opens [Source commodities](#source-commodities).
- The window is titled **WFMT - Missions**, stays on the mission you selected as the list updates, and remembers its size and position.

### Progress

Where the number comes from depends on the mission, and the window says which:

| Shown as | Meaning |
|---|---|
| `20/60` | The game's own count of cargo handed in (from the journal's cargo depot events). |
| `36/36 loaded` | Cargo picked up for a haulage mission but not yet handed in. |
| `~18/40 kills` | Massacre and settlement-raid kills. `~` means an estimate: wing and on-foot kills are often missing from the journal until the mission completes. |
| `36/60 held` | A **source and return** mission, while you are still buying the cargo. The game writes nothing about these until you hand cargo in, so WFMT compares what is in your hold with what the mission asks for. Several missions for one commodity share the hold, the soonest to expire first, so a ton is never counted twice. |

The colors are the same on the [overlay card](#missions-on-the-overlay). The panel's `Δ` and the bars on the massacre pages use the same kill counts.

About **held**:

- It counts everything of that commodity in your hold, whether or not it was bought for the mission.
- It follows the hold as you buy and sell.
- Cargo in a fleet carrier or another ship is not counted.

### Pinned missions

A pinned mission (★) is shown on the [Missions overlay card](#missions-on-the-overlay) in its own **PINNED** section above everything else.

- Each pinned mission is on its own line (never stacked with others), with its place and time left.
- Pinned missions are listed first, then HERE, NEXT and the rest, within the same row limit.
- A pin is kept for each commander (`mission_pins.json`, mission numbers only).
- A pin goes when its mission is handed in, fails, is abandoned or expires.

**Example.** You've taken five massacre missions against the same faction from different stations. Page to
**Massacre (Space)** and the bars show your total progress, rather than five separate counters to remember.

## What the game does and doesn't tell us, and how to work around it

WFMT, like every third-party tool, only knows what Elite Dangerous writes to its journal files.

- It needs no outside service for missions, so the journal is the whole story, and it works around the gaps below.
- Where it can't be sure, WFMT says so rather than guess quietly.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| What you might expect | What the game gives | What to do |
|---|---|---|
| Every kill to be counted | **Wing and on-foot kills** are often missing from the journal until the mission completes, so those counts run low. WFMT marks them with a `~`. Combat-zone kills are recorded as combat bonds, not bounties; WFMT counts them too (checked against real journals), but they carry no ship type, so an on-foot combat-zone kill can be counted as a ship kill. | Read a `~` as "at least this many". The game's own mission screen is the final word. |
| Active missions to appear after restarting EDMC mid-game | The game lists active missions only in its login event, so WFMT works the list out from the last two weeks of journals (the latest login list plus what was accepted, completed, abandoned or failed since). A mission that **expired without a journal entry** can show until your next login. | Log in again to get the game's own list. |
| Cargo mission progress to be exact | The game reports it (`CargoDepot`: collected, delivered and total) when you collect or hand in cargo, and when a wing-mate does. Progress made before WFMT's two-week window, or with no event since, isn't known. | The card shows it once the game has reported any; otherwise check the game's mission screen. |
| Where to find a mission's cargo for sale, offline | It asks Spansh, so it needs Trade's online lookups switched on and a button press. | Turn the switch on in Settings → WFMT → Trade. |
| Progress on a source-and-return mission before you hand cargo in | The game writes nothing about it until then. | WFMT shows what is in your hold against what the mission asks for (`36/60 held`). Cargo in a carrier does not count. |
| The next jump's missions on the overlay when you have a route | The game names the system you have targeted (`FSDTarget`), not the whole route, so only the next hop is NEXT. | Plot the route in the galaxy map and target the hops as you go. |
| Missions accepted a while ago to appear | WFMT reads only the **last two weeks** of journals at start-up. A mission still active but accepted earlier is not found and not shown. | Keep EDMC running while you hold long missions, and check the game's own mission board for older ones. |
| Kills made while EDMC was closed | Counted only if they are in the last two weeks of journal files. | Run EDMC whenever you play. |
| Every mission to land in the right category | Names WFMT does not recognize go to **Other**. | Click the card for details. If a type is always in Other, open an issue so it can be added. |
| A Community Goal's payout to be remembered for long | The game writes the payout (`CommunityGoalReward`) once. WFMT lists the latest three under **Paid out** on the Community Goals page, found in the last two weeks of journals at start-up. | Note a big payout elsewhere if you want to keep it. |
| A Community Goal to disappear when it ends | The game gives no "gone" signal, so the panel relies on each goal's expiry date. | Ignore a goal past its expiry; it clears itself. |

## Missions on the overlay

A small card on your in-game overlay, for flying.

- It is **off until you tick it** (Settings → WFMT → Overlays → Missions).
- Like every overlay, it needs an overlay to draw on: WFMT's built-in one (Windows) or EDMCModernOverlay ([setup](../OVERLAY_SETUP.md)).

With up to twenty missions a list of all of them would cover the screen, so the card shows what you can act on now:

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

- **PINNED** (when you have pinned any in the Missions window) comes first, one line per pinned mission, the station when it is in your system and the system otherwise.
- **HERE** is the missions whose turn-in or destination is the system you are in. **NEXT** is the same for the system you have **targeted** for the next
  jump (plot a route and the game targets each hop in turn). Then the rest (**ELSEWHERE**), and `+N more in M systems` when your row limit cuts it off.
- **Order:** a finished mission (✓) first, with the place to hand it in, then the soonest to expire.
- **Colors:**
  - A mission with under an hour left (you can change it) is red, and under six hours is amber.
  - A finished one (ready to hand in) is always a clear green, whichever overlay color scheme you use.
  - Otherwise a line takes its color from [progress](#progress): lime when a mission is half or more done, blue when it is started.
  - These colors are fixed and do not follow the overlay color scheme. Time pressure (red, amber) comes before progress.
- **Stacking:** massacres and settlement raids against one faction in one place, and any other missions with the same title for the same station, are one
  line with a count (`x3`). A cargo mission shows its progress (`12/40`).
- **Long names** keep the card one fixed width.
  - When a mission's title and place do not fit on one line, the place goes on a line under it.
  - Only a name longer than a whole line is cut short.
  - The time left is always shown.
  - The card's top-left corner never moves as lines come and go.
- **Placement:** Settings → WFMT → Overlays → Overlay Placement ("Missions list"). It starts in the bottom-right corner, above the screenshot messages; move it to
  any corner.
- **Settings** (Settings → WFMT → Overlays → Missions): **Show missions on the overlay**; **Show the missions for the next jump (the system you have targeted)**; **Mission lines to show (at most)** (3 to 14, 8 by default; the rest become `+N more`); **Show a mission in red when it has less than N minutes left** (5 to 720, 60 by default; amber under six hours). **Test Card**
  draws a made-up card and says whether the overlay could be reached.

What it cannot know:

- The game lists your active missions only at login, so after restarting EDMC mid-game the card is built from your last two weeks of journals (as above).
- The next jump is the system you have *targeted*. With no target there is no NEXT section.

## Source commodities

Collect and Mining missions need cargo you have to find. The **Find sources** button at the bottom of the panel (or **Sources** in the Missions window) opens the Source commodities window to help.

For each commodity, summed over all your active missions, it shows the same four picks as Trade's [Best picks](trade.md#best-picks), for buying:

- closest
- best local
- cheapest anywhere
- recommended (within 10% of the cheapest)

The table has the columns **Commodity**, **Need** (tons, summed), **Pick** (closest, best local and so on), **Station**, **System**, **Largest pad**, **ly**, **cr/t** and **Note**. Each row shows the station's **largest landing pad** (Large, Medium or Small, from the pad counts Spansh holds; a `?` means Spansh gave none), so you can see before you go whether your ship fits.

### Delivery missions

A Delivery mission (for example "Deliver 132 units of Personal Weapons") is different. The faction supplies the cargo and you collect it, free, at a specific station, so there is nothing to buy.

- Some are handed over the moment you accept. Others only when you collect them at that station, which can be later.
- The window lists such a mission as `Pick up at <station>` until the journal shows the cargo collected, and never searches the market for it. The station is the one you were docked at when you accepted the mission, which matched every collected case in the journals checked.
- A pick-up row shows the pad size the journal reported when you docked at the station that gave you the mission, and nothing if it did not.
- Wing, rank and cooperative deliveries are not listed.

### Finding sources

1. Pick where to measure from:
   - **From where I am** is your current system. If WFMT has not seen you jump since EDMC started, it reads it from EDMC and then from your newest journal, so you do not need to jump first.
   - **From the turn-in system** is where most of the missions for that commodity are handed in, so you can see what is nearest to the place you will deliver to.
   Changing the choice clears the results.
2. Press **Find sources** (the highlighted button). It asks Spansh a few times per commodity, one commodity after another, and shows each as it finishes (`Asking Spansh... 2 of 5 done`). The button becomes **Cancel** while it runs; press it to stop.
3. Pick a row and press **Copy system** to put its system name on the clipboard for the galaxy map (with no station on the row it asks you to pick one first).

Things to know:

- It uses the landing pad size, "Near me" radius, carriers and ground settings from Trade.
- It only works when **Enable Spansh trade lookups** is on in Settings → WFMT → Trade. It is off by default.
- If it is off when you press **Find sources**, the window asks whether to turn it on, and nothing is searched until you say yes.
- Nothing is searched until you press the button.
- If none of your missions needs cargo to be found, the window says so.
- The window lists at most twelve commodities, the biggest need first.

Not covered: the nearest ring hotspot for a Mining mission (use Mining's hotspot finder), and market data older than 7 days is ignored.

## Settings

**Settings → WFMT → Missions** (all on by default):

- **Show kill progress**: the `done/required` count and the bars on the massacre pages. Off, only the required count shows.
- **Show remaining-kills column**: the `Δ` figure.
- **Show totals row**: the **Sum** line.
- **Show mission count**: the `Missions: N/20` line.
- **Show target settlement (ground missions)**: the `Settlements:` line.
- **Show commodities needed (trade and mining)**: the **Commodities needed:** summary.

The overlay card has its own settings under Settings → WFMT → Overlays → Missions (see above). Settings take effect when you close the Settings window.

More detail: [Missions specification](../MISSIONS_TECH_SPEC.md).
