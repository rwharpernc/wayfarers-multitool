# Changelog

All notable changes to Wayfarer's Multitool (WFMT) are documented here. See
`docs/ATTRIBUTIONS.md` for acknowledgements.

## Unreleased

### Fixed

- **Region Sweep:** the option **Skip systems already visited by anyone (EDSM)** was saved but did nothing. It now checks each candidate target with EDSM, after a jump or **Next >**, and steps
  past systems EDSM already knows (at most 20 in a row). If EDSM cannot be reached nothing is skipped. Each name is asked about once per session and only the system name is sent.

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
  Amber and Green from EDDDT. Choose one under Settings → WFMT → General → Window or with the theme name at the right end of a window's bottom line;
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
