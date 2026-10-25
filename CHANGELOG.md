# Changelog

All notable changes to Wayfarer's Multitool (WFMT) are documented here. See
`docs/ATTRIBUTIONS.md` for acknowledgements.

## 1.0.0 (2026-10-25)

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
  Dashboard, POI Reference and a surface compass with marks.
  - An expedition that was stopped and is started again carries its clock on from the time it stopped at, and
    Rescan leaves out the time it was paused or stopped, as the live count does.
- **Mining:** space and surface mining runs, the Space Mining Book and the Surface Mining Book, Mining
  History (with credits after limpets), a live Surface radar with a simulation, core asteroids, a target
  commodity, the time until the hold is full, the station's price against the galactic average, mission
  needs and mining alerts.
- **Trade:** profit after fuel and repairs, fleet carrier cargo, saved sessions, best routes and prices,
  a watch list and source commodities for missions.
- **Missions:** every mission in one view, progress bars, the Missions window and pinned missions.
- **Field Ops:** screenshots, backpack and cargo, materials, a blueprint browser, Engineers, material
  traders, the Ship planner and the Odyssey Upgrade planner.
  - The Ship planner shows which of a build's engineered modules you already have in storage.
- **Colonization:** the current build, history and every site's shopping list.
  - A Sites window with a fleet carrier column and Rescan Carrier, and Where to buy for what a site still needs.
  - Planned Builds, read from Raven Colonial when you press a button.
  - Optional sharing of progress, deliveries and carrier cargo with Raven Colonial, off by default.
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
