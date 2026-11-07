# BGS

The **Background Simulation (BGS)** is the game's model of factions and their influence. BGS mode records faction states in the systems visited and tallies the commander's own missions, bounties, trade, exploration sales and crimes against each faction.

BGS tracking is a work in progress. Report problems or suggestions through the [issue tracker](https://github.com/rwharpernc/wayfarers-multitool/issues).

BGS tracking requires no setup and records activity wherever it occurs. It is on by default. The switch is the **Show BGS faction states and activity** checkbox on the Settings card at the top of the BGS Report window, not in File > Settings. With the switch off, the panel shows `BGS tracking is disabled — see Settings.`

**On this page:** [How to](#how-to) · [The panel](#the-panel) · [What it counts](#what-it-counts) · [The BGS Report window](#the-bgs-report-window) · [Resets and history](#resets-and-history) · [Tick detection](#tick-detection-and-the-internet) · [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it) · [Settings](#settings)

**Data sources**

- The journal records the commander's actions (missions, bounties and bonds, trade, exploration data, crimes). It does not record the effect of those actions on a faction's influence.
- The effects shown by BGS mode are WFMT's own tally of the commander's activity. The trade figure is an approximation.
- The only outside source is a community tick-time service, used to learn when the tick occurred.

See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

## How to

**View a system's faction states**

1. Jump into the system or log in there. The game supplies the faction list only at that moment.
2. Press **BGS** in the mode bar.
3. Read one line per faction: state and influence, controller first. See [The panel](#the-panel).
4. To view the pending, recovering and active states, press **Report** and open the system's tab. See [The BGS Report window](#the-bgs-report-window).

**View the effect of activity on a faction**

1. Perform the activity in the system. See [What it counts](#what-it-counts).
2. Open the BGS page. The `↳` line under the faction lists the activity for the current tick.
3. For the full breakdown, press **Report** and read the **WHAT YOU DID** table on the system's tab.

**View the ledger for an earlier tick**

1. Press **Report** on the BGS page.
2. Open the **TICK** drop-down and select the period (`<start> → <end>`). The archive keeps 7 days by default. See [Resets and history](#resets-and-history).
3. Select a system tab. If the system has no tab, type its name in **SHOW A SYSTEM** and press **Add system**. See [Which systems get a tab?](#which-systems-get-a-tab).

**Copy the whole ledger**

1. Press **Report**, then **Copy Summary**.
2. Paste the text into a note or chat. The text contains every tick and system, regardless of which tabs are shown. It contains no Discord formatting.

**Share a tick to Discord**

1. Press **Report** and select the tick in the **TICK** drop-down.
2. Open the **Discord** menu in the window header.
   - **Copy for Discord** places the tick on the clipboard with Discord formatting.
   - **Post to Discord** sends the tick to the saved webhook.
   - **Customize post…** changes the appearance of the post (presets, parts shown, saved templates).
3. Posting the same tick again edits the earlier post instead of adding another.
4. Webhook setup is described in [Sharing reports to Discord](discord.md).

**Example: exploration data sale**

A commander docks at a station controlled by Example Union and sells 1,200,000 cr of exploration data. WFMT credits the sale to the station's controlling faction. On the BGS page, a `↳` line under Example Union reads `1,200,000 cr exploration data`. In the report, the same figure appears in the **Exploration (cr)** column of that faction's row. If WFMT has not seen the commander dock at the station or log in at it, the station's faction is unknown and the sale is not credited.

**Example: reading a state on the page**

```text
Example System — 2 faction(s):
★ Example Union — Boom, 45.0% (+5.0)
   Example Cartel — None → War, 30.0% (-2.0)
Nothing done here yet this tick.
```

- Example Union controls the system (★), is in Boom, and holds 45.0% influence, up 5.0 points from before the tick.
- Example Cartel changed from no state to War since before the tick and lost 2.0 points.
- The last line indicates no activity in this system during the current tick.
- The figures are as of the last arrival in the system. Jumping out and back in refreshes them.

**Example: activity within one tick**

In one tick the commander completes two missions for Example Union (`+2/-0` and `+1/-0`), sells goods for a profit of 120,000 cr and abandons one mission from Example Cartel.

- The page shows under Example Union a line such as `2 mission(s) done, INF +3/-0; +120,000 cr trade`.
- The page shows under Example Cartel `1 mission(s) abandoned (INF down)`.
- In the report, Example Union's row has Missions `2`, INF pips `+3/-0` and a signed Trade figure. Example Cartel's row has `1` under **Abandoned**.
- At the next tick the totals reset and the closed tick moves to the **TICK** drop-down.

## The panel

Press **BGS** in the mode bar to open the page. The page has the system block, a small gray tick line and a **Report** button.

The system block shows only the system the commander is in:

- A title line: the system name (preceded by ★ when the system is pinned), then `— N faction(s):`.
- One line per faction present, controller first and then alphabetical. ★ marks the controller. At most 8 factions are listed, followed by `…and N more` when there are more.
- On each line, the faction's state and influence, for example `Boom, 45.0% (+5.0)`.
- Under a faction with activity, a `↳` line listing the activity since the last tick: missions done with `INF +2/-0`, failed and abandoned missions, bounty and combat bond credits, trade profit or loss, exploration data, crimes.
- `Nothing done here yet this tick.` when there is no activity in the system this tick.

State and influence are shown together with their change since before the tick: the figures last reported by the journal compared with the figures from before the tick, for example `45.0% (+5.0)` for influence and `None → Boom` for a state that changed. The change is omitted when WFMT has no figure from before the tick.

Other messages in the block:

| Message | Condition |
|---|---|
| `Current system: (unknown — jump somewhere first)` | WFMT has not yet seen a jump or login. |
| `<system> — waiting on faction data...` | The faction list of the system has not been received. A jump into the system or a login there supplies it. |
| `<system> — no factions present (uninhabited system).` | The system has no factions. |

**Tick line.** The line under the block shows the state of tick detection:

- `Tick check: not yet run.`
- `Last tick: 2026-10-25 14:03 UTC`
- `New tick at ... — totals reset, previous tick archived.`
- `Tick check failed (will retry): ...`
- `This needs "BGS tick detection (every minute)" (tick.infomancer.uk), which is off. Turn it on in Settings > Online.` (shown only while the switch is off; nothing is shown while it is on)

The first check runs 3 seconds after the panel is built, then once every 60 seconds.

**Update timing.** The game writes a system's faction list (state, influence, and the pending, recovering and active states) to the journal only on a jump into the system, a login there, or arrival by carrier jump. The panel figures are therefore as of the last arrival and do not change while the commander remains in the system through a tick.

## What it counts

| Activity | Counting rule |
|---|---|
| Missions completed | Influence pips gained or lost. Each effect is counted in the system the game names for it, which is not always the system where the mission is handed in. If the game names no system, the effect is counted in the system where the mission was accepted, and otherwise in the system where it was handed in. The pips are a count of the `+` signs the game shows (`+2/-0`), not a percentage. |
| Missions failed or abandoned | Counted against the issuing faction, in the system where the mission was accepted. A mission that WFMT did not see accepted (for example one accepted before the earliest journal that is re-read) is not counted. |
| Bounty vouchers and combat bonds | Counted for the faction named on the voucher, in the system where it is redeemed. A bounty voucher can name several factions. |
| Trade | Credits from sales minus credits spent on purchases at a station, credited to the station's controlling faction. Requires WFMT to know the station's faction (the commander docked at it, or was at it on login). |
| Exploration data sold | Credited to the station's controlling faction. Requires the same station knowledge as trade. |
| Crimes | `CommitCrime` events, counted against the faction named in the event, with the fine or bounty. Each crime counts as a decrease. |

A completed conflict mission for which the game reports no influence (observed on war and civil war missions) counts as `++` when the issuing faction is in a war or civil war and `+` when it is in an election. These values are assumptions, not values from the game.

Only activity since the start of the current tick counts. Totals reset at each tick (see [Resets and history](#resets-and-history)).

## The BGS Report window

Press **Report** on the BGS page to open the window.

- The **TICK** drop-down selects the period: `Current tick — since <time>`, or an earlier tick from the archive (`<start> → <end>`).
- The subtitle reads `N tab(s) — last 6 systems plus N pinned`.
- The window has one tab per system. The tabs wrap onto additional rows when there are many.
- Each tab has a **FACTIONS** table and a **WHAT YOU DID** table.
- A help button in the header explains the tabs and columns.
- **Copy Summary** copies every tick and system as plain text, ignoring the tab limit. The button text changes to `Copied!` for 1.5 seconds.
- The **Discord** menu contains **Copy for Discord**, **Post to Discord** and **Customize post…**. Copy and post apply to the tick shown only, and the text is split into several messages when it is long. See [Sharing reports to Discord](discord.md).
- The window updates as new data arrives and stores its size and position. The minimum width is 1000 pixels.

**FACTIONS** columns:

| Column | Content |
|---|---|
| **Faction** | Faction name, preceded by ★ for the controller. |
| **State** | The state, for example `Boom`, or `None → Boom` when it changed since before the tick. |
| **Influence (change)** | For example `45.2% (+1.3)`. |
| **Pending**, **Recovering**, **Active** | State names the game lists for the faction. |

A faction with recorded activity but no faction list is shown by name only.

**WHAT YOU DID** has one row per faction with activity:

| Column | Content |
|---|---|
| **Missions** | Missions completed. |
| **INF pips +/-** | Influence pips gained and lost, such as `+3/-0`. |
| **Failed**, **Abandoned** | Missions that cost the issuing faction influence. |
| **Bounties (cr)**, **Combat bonds (cr)** | Voucher value redeemed. |
| **Trade (cr)** | Sales minus purchases, with a sign. A negative value is a loss. |
| **Exploration (cr)** | Exploration data sold. |
| **Crimes** | Crimes committed against the faction. |

Empty cells indicate zero.

### Which systems get a tab?

Tabs show the last 6 systems visited (the current system first), each with its full name, plus every pinned system.

- **☆ Pin** (top right of a tab) keeps the tab. The button then reads **★ Unpin**. A pinned system is marked ★, stays in the tab row regardless of when it was last visited, and is marked ★ on the panel while the commander is in it.
- **× Close tab** hides a tab and unpins the system. The tab stays closed until it is restored with **Add system**.
- The **SHOW A SYSTEM** box lists every system the report has data for or that is pinned. Typing narrows the list; names starting with the typed text come first. Press Enter or press **Add system**. This pins the system and restores a closed tab. Any name up to 60 characters can be typed.
- With no tab to show, the window displays `No systems to show yet — use "Show a system" above to add one.`
- Pins and closed tabs are stored per commander.

## Resets and history

- Totals reset at each tick. The closed tick is archived, the panel starts over, and the closed tick appears in the **TICK** drop-down.
- The archive keeps 7 days of closed ticks by default. The range is 1 to 90 days (Settings card of the Report window). Older ticks are dropped.
- When EDMC starts, WFMT re-reads the journals from 3 days before the start of the current tick, so totals are cumulative since the tick even when EDMC was not running for the whole period.
- Activity recorded while EDMC was closed reaches the history:
  1. When a tick closes a period, WFMT rebuilds that period from the journals.
  2. The rebuilt version replaces the version recorded live, keeping any faction present only in the live version.
  3. The rebuild reads back up to 14 days. An older period remains as filed.
  4. If several ticks passed while EDMC was closed, WFMT cannot separate them. All activity across them is filed in the one period that closed.
- While the journals are re-read in the background, the panel's catch-up note shows `BGS`.
- On Linux the re-read requires EDMC's journal folder to be set. The BGS settings page displays a warning when it is not.
- All data is stored separately for each commander.

## Tick detection and the internet

WFMT requests the latest tick time from a community tick-time service (`tick.infomancer.uk`) once every 60 seconds. This is the only internet connection BGS makes. It is a request for the latest tick time; no information about the commander or play is sent. It is switched on or off on the Online tab of Settings, as **BGS tick detection (every minute)** (see [Settings](#settings)). It ships on.

With tick detection off, the totals never reset on their own and the journals are not replayed, because WFMT does not know when the tick occurred.

## What the game does and doesn't tell us, and how to work around it

WFMT knows only what Elite Dangerous writes to its journal files. The BGS tick time comes from a community tick-time service. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| Item | What the game provides | Result in WFMT |
|---|---|---|
| Exact influence caused by trade | Trade is counted as net credits traded at the station's controlling faction. It is not the game's supply-and-demand calculation. | The figure is an approximation, suitable for comparing the commander's own effort. |
| Several ticks while EDMC was closed | The journal records when an event happened but not which tick it belongs to, and WFMT learns ticks from a third-party service while it runs. | Activity across the missed ticks is filed in the one period that closed. |
| Mission influence as a percentage | The game provides influence pips and a mission count, not a percentage. | Pips are shown as `+n/-n`. |
| Crimes and kills attributed to a victim faction | Only `CommitCrime` events are counted. Kills carry no victim-faction attribution. | Kills are not counted. |
| Combat zones | Only the resulting bounty or combat bond redemption is counted, not zone presence or wins. | Vouchers and bonds redeemed in the system are counted there. |
| Thargoid war states | Not tracked. | No data shown. |
| Ticks before WFMT was installed | The tick service reports only the latest tick, so earlier periods cannot be rebuilt from old journals. | The archive starts at the first tick WFMT sees roll over. |
| Tick service availability | The service is third-party and uses plain HTTP, with no availability guarantee. | When it is unreachable, the status line shows `Tick check failed (will retry): ...` and the totals do not roll over. |

## Settings

| Location | Setting | Default | Effect |
|---|---|---|---|
| Settings card at the top of the BGS Report window | **Show BGS faction states and activity** | On | Switches BGS tracking on or off. The change applies when the box is ticked or cleared. |
| Settings card at the top of the BGS Report window | **Keep previous ticks for (days, 1 to 90)** | 7 | Number of days closed ticks stay in the archive. The value applies when Enter is pressed or the box loses focus. |
| Settings → WFMT → Online | **BGS tick detection (every minute)** | On | Switches tick detection on or off. Off: totals never reset on their own and journals are not replayed. This setting stays in File > Settings (the BGS tab there shows a note pointing to the Online tab) because it controls the one network request BGS makes. **Turn all off** on that tab also turns it off, and **Reset to defaults** turns it back on. |

Further detail: [BGS specification](../BGS_TECH_SPEC.md).
