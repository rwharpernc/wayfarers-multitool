# WFMT user guide

Index of the Wayfarer's Multitool user documentation.

- [Getting started](getting-started.md): first guide to read.
- [Features at a glance](features.md): every feature and its controls, by mode, with a table that maps tasks to guides.
- [Settings](getting-started.md#settings): each Settings tab and its starting values. [Every Overlays tab](../OVERLAY_SETUP.md#every-overlays-tab-in-detail): the same for the overlays.
- [Tips, quirks and workarounds](tips.md) and [Planned and being researched](planned.md).
- [Known issues](known-issues.md): known faults of the current release.

## How WFMT knows what it knows

WFMT uses the data the game writes to its journal files. Not every event is logged.

Where the journal has no data, WFMT adds data from other sources:

- figures that Frontier's servers provide to a signed-in EDMC (for example a fleet carrier's cargo),
- data reported by players and community services (Spansh, EDSM, Canonn, edastro, Raven Colonial and others).

Where neither source has the data, WFMT uses an estimate that is marked as an estimate, or an action that the commander takes (for example, opening Carrier Management so that the game reports the figure).

The sources, in order of precedence:

1. **The journal** is the source for all data about the commander: trades, scans, missions, deliveries, merits and similar. No setting changes what the game does not write.
2. **Other sources:** Frontier's servers (through a signed-in EDMC) and data reported by players and communities. WFMT uses these to fill gaps in the journal and does not use them to override it. The [internet page](internet-and-privacy.md) lists each one.
3. **Marked workarounds:** WFMT's own bookkeeping (for example, the tally of cargo transferred to a fleet carrier), estimates labeled as estimates, and actions the commander can take (for example, opening Carrier Management).

Every mode guide ends with a section titled "What the game does and doesn't tell us, and how to work around it". The section lists each known gap, its appearance on screen, and the workaround.

## Setting up

| Guide | Contents |
|---|---|
| [Installing WFMT](../INSTALL.md) | Install, update, remove and build from source, with the folders of each system |
| [Getting started](getting-started.md) | Requirements, installing, the in-app updater, the lines under the mode buttons and the Credits Ledger, data and backups, catching up after EDMC was closed, every Settings tab and its starting values, opening windows, button names |
| [Setting up the overlay](../OVERLAY_SETUP.md) | The on-screen overlay: the built-in overlay (Windows) and EDMCModernOverlay, using both, every Overlays tab, placement, color schemes, opacity and fonts |
| [Windows and Linux](platforms.md) | Feature availability by system |
| [WFMT on Linux](linux.md) | Linux and Flatpak setup |
| [What goes on the internet](internet-and-privacy.md) | Every feature that contacts an outside site, its trigger, the data it sends and the address it uses |
| [Known issues](known-issues.md) | Known faults of the current release and their remedies |
| [Reporting a problem](reporting-problems.md) | The **Report an issue** and **Copy diagnostics** buttons and the data they include |

## The modes

| Mode | Guide |
|---|---|
| **Powerplay** | [Powerplay](powerplay.md): merits, cycles, sessions, megaships, the Rare Goods Finder |
| **Explore** (Exploration) | [Exploration](exploration.md): Auto-Honk, alerts, Boxel Survey, Exploration Value, Codex, POI Reference, Notes, Expedition planner, Expedition Log, System targets and Body info, Exploration Dashboard, Route Planner and Carrier Route, Nearest place to land, Compass |
| **Exobiology** | [Exobiology](exobiology.md): the Organic Scanning panel, the four overlay cards (status, predicted species, sample radar, popup), returning to a plant, first footfall |
| **Shortcuts** | [Shortcuts](shortcuts.md): keyboard shortcuts (Windows) and chat commands (Windows and Linux) for Mark center, Mark border, the radar range, the Live window and hiding the overlays |
| **Mine** (Mining) | [Mining](mining.md): space and surface mining, the Space Mining Book and the Surface Mining Book, Mining History, mining alerts |
| **Trade** | [Trade](trade.md): profit, routes, prices, Watch list, carrier cargo, History |
| **Mission** (Missions) | [Missions](missions.md): all missions in one view, the Missions window and pinning, progress colors, sources for mission cargo |
| **Operations** | [Operations](operations.md): screenshots, inventory, engineering materials, blueprints, wishlist, ship and Odyssey upgrade planners, engineers, material traders, ship builds, the combat record |
| **Colony** (Colonization) | [Colonization](colonization.md): the current project, history, the sites window, where to buy |
| **BGS** | [BGS](bgs.md): factions, states and the commander's effect on them |
| *Sharing* | [Sharing reports to Discord](discord.md): copy for Discord, post to a webhook, plain copy, and the Discord-side setup |
| *Always on* | [Landing Assist, Interdiction Warning, Flight Alerts (carrier countdown, fuel and mining alerts) and the Route overlay](always-on.md) |

## When something is wrong

- [Known issues](known-issues.md) lists known faults of the current release and their workarounds.
- [Troubleshooting](troubleshooting.md) lists symptoms and remedies.
- [Reporting a problem](reporting-problems.md) describes how to file a bug report.

## For developers

Technical documentation is in [docs/](..): [DEVELOPMENT.md](../DEVELOPMENT.md), [TECHNICAL.md](../TECHNICAL.md), [MODULES.md](../MODULES.md), the feature specifications, and [TODO.md](../TODO.md) (open work).
