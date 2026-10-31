# Changelog

All notable changes to Wayfarer's Multitool (WFMT) are documented here. See
`docs/ATTRIBUTIONS.md` for acknowledgements.

## Unreleased

### Changed

- **Operations: Materials is now Engineering:** the section is titled Engineering and, because the sections are listed A to Z, comes first in Operations. Its three buttons (**Materials**, **Blueprints**, **Engineers**) are in one row instead of stacked. The text reads `Materials held: ...` and `Last change: ...`, and a new line counts the engineers (`Engineers: 7 of 38 unlocked · 2 invited · 4 known`); the folded title carries the engineer count too.
- **Copy To Acquire is gone:** the Colonization Sites window's **Copy To Acquire** button gave the same tons as **Copy Shopping List** (what the site still needs, less your ship's hold and your fleet carrier) in a different wording, so only **Copy Shopping List** remains.
- **Colony page:** the page in the main EDMC window is now in short sections: the project (**Delivered**, **Still needed**), **What you have** (**In your ship**, **On your carrier**, **Still to get**) and **To finish the build** (**Commodities**, **Trips left**, **Biggest gaps**). A section is drawn only while it has something to show. The **Next** line is gone: **Still needed** now says when the build is complete or only waits for a final dock. With no site under construction the page lists the **last 5 completed** sites, newest first. The **Overlay** button is gone too (the **Overlays shown (click to hide)** line at the top of the panel already hides every overlay); its job, keeping the shopping list on every screen, is now the tick **Always show the shopping list, whatever screen you are on** in Settings → WFMT → Overlays → Colonization, and a choice saved with the button carries over.
- **Where to Buy:** the shopping route has a block of its own above the per-commodity lists, and each buy line on it shows the supply at that stop. The Best single systems list is gone, and Find all no longer checks systems with Spansh. Every filter is now an exclusion with everything included by default: **Include fleet carriers** is now **Exclude fleet carriers** (carriers are searched and listed unless you tick it). A saved choice of the old Include tick is not carried over. The window is a little taller at its minimum size.
- **Rescan Journals:** the Colonization Sites window's **Rescan Carrier** button is now **Rescan Journals**. It reads your journals again for everything the window shows: it folds in the last 30 days of site activity, rebuilds your delivery history, and rebuilds the fleet carrier tally. It no longer needs a fleet carrier; a commander without one gets the first two.
- **Tooltips on every window button:** the buttons that had no tip text now have one (the Create Project dialog, the Mining Book's Add Ring dialog, the hotspot import and export window, the Screenshots window's Close, the message and form dialogs, and the Close button of the Help windows). A test fails if a window button is added without a tip.

### Added

- **Telling us what the game shows:** engineers whose invitation requirement WFMT cannot check against your journal (20 of the 38) now say **Verification needed** in their details, and a new **Report engineer data** button on the Engineers tab opens a prefilled GitHub form (the engineer, the standing WFMT has, the Environment box) for you to write what the in-game Engineers panel says. The form is general, so other parts of WFMT can use it later: **Settings → WFMT → General → Help → Report game data** opens it blank. Nothing is sent until you submit it on GitHub with your own account, and no commander name is put in it.
- **A separate diagnostic log:** Settings → WFMT → General → Help has a new tick, **Write a separate diagnostic log** (off by default), with **Open log folder** and **Copy log path** buttons. While it is on, WFMT writes a detailed log of its own to `logs/WFMT/wfmt-diagnostics.log` in EDMC's data folder (about 4 MB at most, rotated), apart from EDMC's log: everything WFMT logs including the finer lines EDMC's log leaves out, journal event names, buttons pressed and windows opened, each Spansh request with its outcome and time, Where to Buy searches, Rescan Journals, and Settings saves. Journal contents, keys and webhook links are not written, and your commander name and home folder are replaced. EDMC's own log is unchanged by it.
- **Engineers button:** the Operations panel has a separate **Engineers** button that opens the Engineering window on its Engineers tab (**Blueprints** now opens it on the Blueprints tab).
- **Engineer status colors:** on the Engineers tab a row is green when the engineer is unlocked, yellow when you know of them or have been invited (in progress), and red when they are not available yet (the game has not listed you as knowing them). A key under the table says so. The three colors are the same in every theme (Navy, Cyan, Amber and Green) and are readable on all of them: a test checks their contrast on each theme's rows and that they differ in hue and lightness, so unlocked and in progress are not confused in the Amber and Green themes.
- **Engineer details laid out in sections:** the text under the Engineers table is now in labelled sections separated by blank lines: the engineer and where they are, **Path to unlock** (each engineer's numbered steps indented under their name), **How to gain standing** and **Notes**.
- **Copy overlay choices from another commander:** the Overlay Placement tab has **Copy all overlay layouts and settings from** a list of your other commanders. Pressing **Copy** and then **OK** in Settings replaces the current commander's overlay choices (which cards run, their options, placement and look) with the other's; Cancel keeps yours. The other commander and the machine-wide overlay settings are not changed.
- **More Where to Buy filters:** **Only stations with enough stock** (hides stations holding less than you still have to get), **Only stations with a shipyard** (to keep a smaller cargo ship close by) and **Arrival within** (500 to 25,000 ls from the arrival star). All are off by default, remembered, and applied to what was already found, so changing one asks Spansh for nothing. The window is a little taller at its minimum size to fit the extra row.
- **Surface ports in Where to Buy:** a new **Exclude surface ports** tick (off by default, remembered) leaves stations on a planet's surface out of the lists and the route without asking Spansh again. A commodity found only at surface ports is named on the route (a group at the top of the route block, one commodity per row, headed **Only at surface ports** or **so left out of the route** when they are unticked; Find all first makes one more request per such commodity for orbital stations alone, so one sold at an orbital port farther away is not wrongly named), marked **surface ports only** under its stop and on its heading, and in the note. A route stop on a surface is marked in the Planetary column and in Copy Route.
- **Where to Buy follows your purchases:** when cargo reaches your hold or fleet carrier, or is delivered, the open window works the route and the lists out again from the Sites window's Acquire figures. A commodity you have in full drops off; a part-bought one shrinks. Nothing is asked of Spansh.
- **Requirements checked against your journal:** where an engineer's invitation asks for a rank or a lifetime figure, the path now says where you stand, for example `you have Competent: needs Expert` or `you have 304 markets: met`. It covers 18 engineers: the combat, trade and exploration ranks, the Empire and Federation Navy ranks, the greatest distance from your start, markets and black markets traded with, tons mined, combat bonds and bounty vouchers. Ranks and lifetime figures are read from the `Rank`, `Promotion` and `Statistics` events and kept for each commander, so they are as fresh as your last login (a promotion shows at once). If EDMC starts after you have logged in, the newest ones are read from your journal files once, in the background, so the notes appear without logging in again. The note is information only: a step is marked done by the engineer's standing, as before. Requirements the journal does not total (a faction's standing, missions of one kind, items sold to a bartender) show the table's words with no check.
- **Path to unlock an engineer:** selecting an engineer on the Engineers tab now shows the way to them as numbered steps in order: find them, hold the permit if one is needed, earn the invitation, unlock them. Steps the game says you have done are marked `[done]`. When an engineer is found through another (Tiana Fortune through Hera Tani, who is found through Liz Ryder), the engineers to deal with first are listed in order, and any already unlocked are left out. The steps are the community table's wording; the game does not report permits or invitation requirements, so those are marked done only once the engineer is invited or unlocked.
- **Next step column:** the Engineers table's **To unlock** column is now **Next step**. It shows the one thing to do next: the engineer's own next step, or `First <engineer>:` and that engineer's step when another has to be dealt with first. A step that only says "Common knowledge" is skipped. The unlock items are shown beside the engineer's own step.

### Fixed

- **Tooltips in the pop-out windows never appeared:** a window button (the Colonization Sites window, My Projects and every other window built on the window kit) had its tooltip attached, but the button's hover highlight replaced the handler that shows it, so hovering did nothing. The tooltips now show. The A- and A+ text size buttons and the color theme name in a window's footer, which had no tooltip, have one too. A test now hovers a button and checks the tip appears, and the window-fit test fails any window button with no tip.
- **Windows reopening on the wrong monitor:** a window last closed on a monitor to the left of (or above) the primary one was reopened with its position written as `-2000`, which means 2000 px in from the right edge of the screen, not a place left of the primary. The position is now written as `+-2000`.

## 1.3.3 (2026-10-30)

### Added

- **Powerplay overlay:** a small card on the game screen (Settings → Overlays → Powerplay, off until ticked) with your Powerplay standing in the system you are in: **Your Power**, rank and total merits, the merits of the cycle in progress, the system's state and holder, what merits earned there now count as (Acquisition, Reinforcement or Undermining), and the merits and estimated Control Points earned there this session, by type. In a system without Powerplay data it says **No Powerplay Detected in system**. It has a Test Card button and its own Overlay Placement slot (top right by default).
- **Looking ahead to the next system:** an opt-in tick on the same tab, **Look up the system I am jumping to** (off until ticked; it asks Spansh), turns the card to the destination as soon as the journal says a hyperspace jump has started, marked `jumping`, with its state, holder, what merits there would count as and its control progress. It says `Looking up Powerplay…` while Spansh answers, and `Powerplay lookup unavailable` if Spansh cannot be reached. Answers are kept for an hour, and the systems you arrive in are remembered from the journal, so a loop route asks Spansh about each system only on its first lap. A destination's control progress is shown only while the figure is under ten minutes old, because it moves as players earn merits. The lookup is listed on the Online lookups page and in [What goes on the internet](docs/guide/internet-and-privacy.md).
- **Merit cap research:** [POWERPLAY_MERIT_RESEARCH.md](docs/POWERPLAY_MERIT_RESEARCH.md) records whether merits are capped per day, per cycle or per delivery. The journals show no cap, and the page lists the published claims as unverified and the open items.

## 1.3.2 (2026-10-29)

### Changed

- **Panel buttons:** the mode buttons and the other abbreviated buttons now carry their full names: Powerplay, Exploration, Mining, Trade, Missions, Field Ops and Colony; Auto-Honk, Discovery Alerts, Neutron Star, White Dwarf and Random; Hotspots, Prices and Reserves on Mining; Copy System, Copy Next, Add Note, Find POI and Update POI. The window does not grow, because it was already as wide as the full mode names. Every button on the panels now has a tooltip, including the Trade page buttons and the Boxel Survey, Region Sweep and Waypoint buttons. A row of buttons that would be wider than the window (the Mining bar, Region Sweep's Discover buttons and the Waypoints list buttons) now wraps onto a second line.
- **Window buttons:** the buttons in the pop-out windows now have tooltips too (the Help button included), and the terse ones are spelled out: in the Mining live window **Mark center**, **Mark border**, **Add hotspot**, **Import/export**, **Hotspots**, **Prices** and **Reserves**; **Review expedition** and **Move up** / **Move down** in the Expedition windows; **Add build**, **Edit build** and **Delete build** for Ship Builds; **Clear filter** in the Inventory window; **Copy Coriolis link** and **Copy EDSY link** in the Ship planner. The Route Planner and the two Mining live windows are a little wider at their smallest size so the longer names fit. The two Settings shortcut rows are now **Mark the center** and **Mark the border**.
- **Author line:** the author is credited as R.W. Harper (CMDR Mactavious) in the README, the acknowledgements and the specifications.
- **Windows open on EDMC's monitor:** a pop-out window that has never been opened, or whose remembered place is no longer on a connected monitor (a monitor was unplugged), now opens over the EDMC window on EDMC's monitor instead of wherever the window manager puts it. A window you left on another monitor still reopens there. A new tick in Settings → WFMT → General → Window, *Always open WFMT's windows on EDMC's monitor* (off), opens every window on EDMC's monitor wherever you left it.
- **Button capitals:** buttons that were in capitals (Report, Rares, Rescan, Dashboard, Overlay, Projects, History, My Codex, Find, Plot, Clear Route, Review, Book, Live, Notes, Expedition, Mark, Target and the rest) are now in Mixed Case like the others, in the panels, the docs and the tooltips.
- **Renamed:** the Field Ops mode is now **Operations** (its button, Settings tab and guide, which is now `operations.md`), and the Exploration mode button is now **Explore**. The Exploration section, Settings tab and guide keep their names.
- **Powerplay panel:** the Session and Cycle lines no longer repeat each other. When this login has earned everything the cycle has (the first session of a cycle), the panel shows only the Cycle pair, marked
  **(all this session)**, and the Session pair comes back as soon as the two differ.
- **Less repetition on the panels:** lines that said the same thing twice are gone or shortened.
  - **Powerplay:** the Merits this session line under the mode buttons is left out while the P.P. page is showing, because the page has its own Session line.
  - **Colony:** the Progress row is folded into Delivered (`5,000 of 6,000 t (83%)`), Next no longer repeats the Still to get figure, and a finished project drops the Covered and Trips rows.
  - **Trade:** Hold space shows only the cargo split and leaves the free tons to Ship hold; the pages no longer open with a heading that repeats their name; the Market page loses its Looking to line; the nearby verdict is short; Carrier cargo is one line.
  - **Mining:** the Refined line no longer repeats the Mine via hints, Hold is full is left out while the hold line shows, the Last rock line leaves off a core the Core asteroids line names, and Last DSS scan shows only when it differs from the known hotspots.
  - **Exploration:** the Dashboard summary drops the scanned count that System bodies shows, System age drops the system name, the Expedition and Expedition Log title suffixes no longer repeat their lines, Notes and Region Sweep drop repeated counts, Copied status lines say Copied to clipboard, and Active scan appears once you sample.
  - **Missions:** a single category drops its count from the tab title, and the Sum card appears only with two or more factions.
  - **BGS, Field Ops:** the BGS heading, the Ship Builds prefix, one Screenshots hint and a repeated pillage status are gone.

## 1.3.1 (2026-10-29)

### Fixed

- **Colonization:** the Sites window's **Show** and the shopping-list overlay card's **List** read the same setting but started at different choices (**All** and **To buy**), so they listed
  different rows until you picked. Both now start at **To buy**.
- **Settings text:** the Body info page now mentions the **Mapped value** row, and the EDSM ring reserve lookup says it asks once for each ring until EDMC restarts, not every time you drop into
  one. The online-lookups list names Canonn alone for the Codex **Not found** tab, and Spansh alone for the Rare Goods Finder.

- **Region Sweep:** the option **Skip systems already visited by anyone (EDSM)** was saved but did nothing. It now checks each candidate target with EDSM, after a jump or **Next >**, and steps
  past systems EDSM already knows (at most 20 in a row). If EDSM cannot be reached nothing is skipped. Each name is asked about once per session and only the system name is sent.

### Changed

- **Documentation:** every guide, specification and status page was checked against the code, about 2,000 claims, and the out-of-date ones were corrected (column and button names, defaults,
  limits, sample output, what goes online, what a backup leaves out). Every page now opens the same way, with a title and a lead paragraph. A checker (`scripts/check_docs.py`) now runs before
  every commit and in the test suite, so the documentation cannot drift from the code unnoticed.

## 1.3.0 (2026-10-29)

### Added

- **Sharing to Discord:** the **BGS Report** and the **Powerplay Sessions** window can share a report three ways. The plain **Copy Summary** and **Copy Progress** are unchanged and
  stay the way to share anywhere else. **Copy for Discord** puts the report on the clipboard with Discord's formatting (bold names, bullets, links that do not unfurl), split
  into messages under Discord's 2,000-character limit. **Post to Discord** sends it to a webhook you set up. Nothing is ever posted on its own: every post follows a button press.
  - A new **Settings → WFMT → Discord** tab holds the switch (off by default) and your destinations. A Discord webhook belongs to one channel, so each commander saves a named list
    of destinations: a webhook link (hidden as you type) and an optional thread id for each, with **Test**, **Remove**, **Add destination** and **Copy their destinations** (to reuse
    another commander's list). With one destination **Post to Discord** posts straight to it, and with several a small menu asks which one.
  - The links are saved for each commander, kept across updates and left out of **Back up my data**. They are never written to the log, and are removed from **Copy diagnostics** if
    one ever appeared.
  - Posting the same BGS tick or Powerplay session again to the same destination edits the earlier post instead of adding another. Names with `*`, `_` or `@` cannot format a message
    or ping anyone.
  - **Customize how posts look:** the BGS Report's **Discord** menu (**Customize post…**), the Powerplay Sessions window's **Customize…** button and the Discord tab's **Customize posts…** open a
    dialog with the presets Standard, Compact, Detailed and Plain, checkboxes for which parts of each post appear, a live preview with its length, and templates you save, rename and
    delete. The template shown is the one **Copy for Discord** and **Post to Discord** use for that report. Names are still escaped and posts are still split under Discord's limit,
    whatever the settings.
  - The new guide, [Sharing reports to Discord](docs/guide/discord.md), walks through making the webhook in Discord (with a private test channel), finding a thread id, how commanders
    and channels fit together, and what every message means.
- **Expedition Log:** **Start from my last** has three buttons. **sale** is the earlier of your last two sales (what the old button did), **Discovery Data sale** begins just after your
  last exploration sale, and **Exobiology Data sale** just after your last exobiology sale.
- **Colonization:** the shopping-list overlay follows the Sites window's **Show** choice (**All**, **To buy**, **To haul**). It is one setting, so choosing it in either place changes the
  other, and the window now keeps your choice between sessions.
- **Documentation:** the README is an overview with clear sections, and every feature guide has a How to section and worked examples. A note on reusing WFMT's ideas and code is in the
  README and `docs/ATTRIBUTIONS.md`.

### Changed

- **Expeditions are managed in one place.** The Exploration panel's Expedition section no longer has **START**, **PAUSE** and **STOP**. Start, pause and stop expeditions in the Expedition
  window (the **EXPEDITION** button), which now explains this in its Help. The section still shows what is running, with **COPY**, **Copy on arrival** and **EXPEDITION**.
- **Bio status card:** it is twice as wide (a strip 108 characters wide) and about a quarter shorter, because the distance line now sits beside the species and reward when it fits. The
  tracked-plant lines are no longer cut off.
- **Organic Scanning:** the panel section starts folded, like the other sections.
- **Powerplay:** the **SES** button is now **REPORT**, matching the BGS panel's **REPORT** button. It opens the same Powerplay Sessions window.
- **Colonization, To haul:** with the **To haul** filter on, the Sites window no longer tints every row green. The rows in your ship's hold, the ones you are hauling now, get a tint of
  their own that fits the selected theme. The overlay drops the green too (the **✓** stays) and draws the rows in your hold in the theme's blue.

### Fixed

- **Exobiology:** sampling a different genus part-way through now abandons the unfinished one, as the game does, so going back to it starts at 0 of 3 instead of carrying the old samples
  forward (a second Tussock sample used to read 2 of 3 after you had finished an Aleoida in between).
- **Documentation and code comments:** a pass through the guides, the technical documents and the code comments corrected statements that no longer matched the product (the backup result
  line, a step number in the Linux guide, references to documents and modules that were renamed, and more).

## 1.2.0 (2026-10-28)

### Added

- **Colonization:** **Copy To Acquire** in the Colonization Sites window copies a short list of what is left to acquire: the site, then each
  commodity with the tons still to get (what your ship and fleet carrier hold is taken off), biggest first. Handy to hand over when someone
  asks for the list part way through loading the carrier.
- **Colonization:** an **Archive** for finished sites. **Manage Sites → Archive Finished** moves every completed or failed site out of the
  Sites window into **Manage Sites → Show Archive**, a read-only list with how each ended, when it started and finished, how long it
  took and the commodities it needed. **Restore** brings one back, **Copy Summary** copies its facts and **Remove Permanently** forgets
  it. Archived sites are kept in the same file as the rest (so Back up my data includes them) and still count in the history.
- **Colonization:** when a new construction site appears and Raven Colonial has no project for it, the Colonization panel offers to
  create one (**CREATE ON RAVEN**, or **NOT NOW**). It needs the master switch and progress sharing on and your key saved, and is made once per site.

### Changed

- **Colonization:** Where to buy has its own window. **Where to Buy** in the Colonization Sites window opens it with the site's system and
  the picked commodity filled in, and it follows the commodity and site you pick there. It remembers its size and position and closes with
  the Sites window. The window names the commodity picked (a **Commodity** line) and says how Find nearest and Find all choose what to search,
  and the Sites window's footer says what to do after you pick a row. The commodity table now has the whole height of the right-hand side. The
  search itself, its options and what it sends are unchanged.
- **Windows:** the footer message of WFMT's windows has its own bright color on every theme (yellow on Navy, Cyan and Green, cyan on
  Amber) instead of a pale tint of the accent. The note under the Where to buy buttons uses it while a search runs.
- **Overlay:** the Biology card lists each candidate species of an open genus on its own row, with its value and share lined up at the right
  (after a row for the genus with the range it could pay), instead of running them together on a muted line. The name column is wider, a
  long name stops short of the value beside it, a genus with more than five candidates counts the rest (`+2 more`), and a crowded body
  shows one row per genus so nothing is dropped from the card.

### Fixed

- **Overlay Placement:** a tall or wide box dropped flush to the top, bottom or a side of the layout editor now takes that edge. Before, the
  spot came only from the third of the screen the box's center was in, so a box that filled more than a third of the screen could land in
  the middle row or column with a large offset instead of snapping to the edge.
- **Colonization:** Create Project on Raven could open its dialog out of sight, and the construction panel's depot updates (every few
  seconds) replaced the status message at once. The dialog is now centered and kept on the screen, and the message of a button you press
  stays for 30 seconds. A failure to open the dialog is written to the EDMC log.

## 1.1.0 (2026-10-27)

### Changed

- **Windows:** four color themes for WFMT's own pop-out windows and dashboards: Navy (the default, brighter than before: blue-tinted
  surfaces, gold titles, cyan section labels and table headings, a soft blue footer message that turns green on success), and Cyan,
  Amber and Green. Choose one under Settings → WFMT → General → Window or with the theme name at the right end of a window's bottom line;
  open windows are recolored at once and the choice is remembered. EDMC's window and the overlay cards are not changed.
  The stat tiles at the top of a dashboard and the status chips keep their size when the text size is changed.
- **Windows:** the text size of WFMT's pop-out windows and dashboards can be changed, from -2 to +6 points, with the **A-** and **A+**
  buttons at the right end of a window's bottom line or under Settings → WFMT → General → Window. One size applies to every window
  and is remembered. Table columns now fit their content (short columns stay narrow, long ones take the spare width) instead of
  sharing it equally.
- **Colonization:** a **Show** dropdown (All, To buy, To haul) replaces *Hide rows already covered* in the Sites window, and the overlay
  card has the same choice under Settings → WFMT → Overlays → Colonization (**List**). **To haul** is for the middle step, when
  everything is bought and on the fleet carrier and **To buy** would be empty: it lists the rows that are covered but not yet aboard
  the ship in full. The old overlay tick box carries over as To buy or All.
- **Colonization:** the Remaining column of the Sites window and of the shopping-list overlay card is now called
  **Acquire**, since it shows what is still to get. The figure is unchanged.

### Fixed

- **Colonization:** the fleet carrier column no longer falls back to an older level when Frontier's copy of the
  carrier's cargo is behind. A copy that arrives within 15 minutes of your last transfer, or that repeats one
  already ignored, is left out until Frontier's figure changes or an hour has passed since it was first ignored. Each Frontier figure now writes one line to EDMC's
  log saying what was done with it. The Colonization guide has new notes on how the two sources fit together
  and a list of scenarios with what to do.

## 1.0.0 (2026-10-26)

The first release. WFMT is an add-on for Elite Dangerous that runs inside EDMC (Elite Dangerous Market
Connector) and puts its tools in one panel of eight modes, with optional on-screen overlays on Windows
(built in) and Linux (through EDMCModernOverlay).

### Modes

- **Powerplay:** Merits and Control Points for your Power, megaship scans per cycle and the Rare Goods
  Finder (Distance, Arrival and Legality columns, Large pads only and Only my Power filters, Copy system,
  last known location).
- **Exploration:** auto-honk, discovery alerts, boxel survey, scan values, the System targets and Body
  info cards, exobiology (Bio status, Biology, Bio radar, Sample popup, plant waypoints, prediction
  review), the MY CODEX completion window, notes, the Expedition window (Plan, Route and Log tabs: the
  expedition planner, the Route Planner with Spansh's exact plotter and a carrier route for a fleet or
  squadron carrier, and the Expedition Log) with one Expedition section on the panel and a confirmation
  when a route's expedition starts, the Exploration
  Dashboard, Notable Bodies alerts, POI Reference and a surface compass with marks.
  - An expedition that was stopped and is started again carries its clock on from the time it stopped at, and
    Rescan leaves out the time it was paused or stopped, as the live count does.
- **Mining:** space and surface mining runs, the Space Mining Book and the Surface Mining Book, Mining
  History (with credits after limpets), a live Surface radar with a simulation, core asteroids, a target
  commodity, the time until the hold is full, the station's price against the galactic average, mission
  needs and mining alerts.
- **Trade:** profit after fuel and repairs, fleet carrier cargo, saved sessions, best routes and prices,
  a watch list and source commodities for missions.
- **Missions:** every mission in one view, progress bars, the Missions window and pinned missions, the Community
  Goals page and where to buy the cargo a mission needs.
- **Field Ops:** screenshots, backpack and cargo, materials, a blueprint browser, Engineers, material
  traders, the Ship planner and the Odyssey Upgrade planner.
  - The Ship planner shows which of a build's engineered modules you already have in storage.
- **Colonization:** the current build, history and every site's shopping list.
  - A Sites window with a fleet carrier column and Rescan Carrier, and Where to buy for what a site still needs.
  - **Remaining** is what is still to get: the site's need less the cargo in your ship and on your fleet carrier,
    reaching 0 once you have it all wherever it is stored. The shopping-list overlay card shows the same figure, and
    an option (on by default) leaves out the commodities the ship and the carrier already cover.
  - The ship's hold is read from the game's `Cargo.json`, so the In Cargo figures follow a purchase at once.
  - **Best single systems:** after Find all, the few systems whose stations together stock the most of the list are
    checked with Spansh and ranked, with the stations to visit in order and what to buy at each; Copy Route copies the
    best first. A search in progress is shown in the accent color.
  - Planned Builds, read from Raven Colonial when you press a button.
  - Optional sharing of progress, deliveries and carrier cargo with Raven Colonial, off by default.
  - My Projects lists every active project you have on Raven Colonial, across systems, adds up the ones you count and the trips
    they take, and can set your primary project and save your counted (not hidden) list there.
  - Create Project on Raven starts a Raven Colonial project for a site you are docked at (from a planned site or as a
    project of its own), links you, and can make it your primary project and attach your fleet carrier.
- **BGS:** faction states and what your activity does to them, rebuilt after a tick that passed while
  EDMC was closed. A conflict mission the game reports no influence for counts as ++ in a war and + in
  an election, an assumption the spec records.

### Always on

- Landing Assist, Interdiction Warning, Flight Alerts and the Route overlay.

### Overlays, settings and data

- A built-in overlay on Windows (a transparent window over Elite, with its own fonts and cards sized from
  the measured text) and support for EDMCModernOverlay on Windows and Linux, with a layout editor, panel
  opacity and a Color-blind safe palette.
- When EDMCModernOverlay is the overlay in use and is not installed (always the case for a fresh Linux install), the overlay settings pages say so.
- Every overlay is off until you turn it on. The screen size comes from the game's own files or the overlay's
  log, and when those are not there from the operating system's primary display (Windows and Linux), so an
  ultrawide or a 4K screen is not taken for 1080p. 1920 x 1080 is the smallest screen the default layout is
  made for; it is tested not to overlap on 21:9, 32:9 and triple-screen sizes as well.
- Settings, overlay choices and everything saved about play are kept per commander. Playing with EDMC
  closed is fine: the journals are read back when EDMC starts.
- **Credits and merits this session** in the panel, with a Credits Ledger (income by activity, by day and
  lifetime totals).
- **Nearest place to land:** the nearest station, and the nearest fleet carriers that let anyone dock, that
  can take your ship, for deep space and emergencies.
- **Shortcuts:** six actions as Windows key combinations (checked against Elite's controls file) and as
  `!wf` chat commands read from the journal, which work on Windows and Linux.
- **Local star index (optional):** a file of neutron stars built from Spansh's public dump, so **N.S.**
  answers without a request. **Update** fetches only the small 1-day or 1-week file of changed systems
  and merges it in, and downloads the whole file again only when the index is too far behind.
- **Back up my data:** a zip of the saved data, a restore applied at the next start and an optional
  automatic backup.
- **Help:** **Report an issue** and **Copy diagnostics** under Settings → General, and a Help button in
  the header of the pop-out windows.
- An in-app updater, and a courtesy layer for requests to Spansh and other services (spaced out, retried
  and paused after repeated failures). Every online lookup is opt-in or runs only on a button press, and
  each is listed in `docs/guide/internet-and-privacy.md`.

### Platforms

- Windows and Linux (native or Flatpak EDMC). Windows has been tested most; the Linux checks are in
  `docs/LINUX_TESTING.md`.
