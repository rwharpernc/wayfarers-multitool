# Planned and being researched

Open work that is recorded in [TODO.md](../TODO.md). The list has no dates or order and is not a commitment. Suggestions are accepted on the [Issues page](https://github.com/rwharpernc/wayfarers-multitool/issues) (see [Getting help](../../README.md#getting-help)).

## Colonization

- **Raven Colonial.** Implemented: sharing of progress, deliveries and carrier cargo (opt-in, off by default; the [internet page](internet-and-privacy.md) lists what is sent and when), **Raven Progress**, **Create Project on Raven** and **My Projects**. Not implemented:
  - reading Raven's progress automatically instead of on a button press,
  - assigning commodities to commanders on a project,
  - showing the cargo of other linked carriers,
  - a guided tool that fills in the whole plan of a system on Raven.
- **Team projects.** Several commanders on one project. All data is currently per commander.
- **Co-op building and colony tracking.** Not available.
- **Tons per hour and credits per delivery.** The journal does not record the time spent hauling, so tons per hour would be estimated from the gaps between deliveries. Whether the credits listed by a depot match the credits paid has not been confirmed.

## Exploration

- **Ship planner links.** The Ship planner reads Coriolis and EDSY links that carry a whole build. Reading EDSY `#/L=` links and Coriolis `/outfit` links requires the sites' identifier tables and is not implemented.
- **Stored modules in a Ship planner plan.** The planner shows which modules are in storage. It does not subtract their engineering from the plan.

## Operations

- **Odyssey upgrade planner, stat preview.** The stat tables are not available as open data. They are being collected and verified in the game ([ODYSSEY_STAT_COLLECTION.md](../ODYSSEY_STAT_COLLECTION.md)). The preview is not implemented.

## Mining

- **Review of Mining, including surface mining.** A desk review found that the run's ore, limpets, rates, hold, targets, missions, sales, history, hotspots, prices and reserve lookups are covered. The Surface (Rhino) tools and the radar over the game have not been assessed in play.

## Landing Assist

- **Own pad layouts** with fore and aft cues and diagrams for facilities that have none, starting with settlements. The pad numbering of settlements must be confirmed in the game before any layout is drawn.

## Trade

- **Round trip:** a Powerplay bonus filter. It depends on what the price service reports and on the definition of "bonus".

## Overlays

- **Built-in overlay for Linux.** Not built. Linux uses EDMCModernOverlay. The window handling differs between X11 and Wayland; see [LINUX_OVERLAY_RESEARCH.md](../LINUX_OVERLAY_RESEARCH.md).
- **Screens smaller than 1920 x 1080.** The default overlay positions are laid out for 1920 x 1080 or larger. Displays are sized in pixels, so on a smaller screen some can overlap until moved on Overlay Placement. On 1920 x 1080 or larger (including ultrawide screens) the default positions do not overlap, except for cards that are never shown together and the wide Bio status strip, which reaches over the top of the Expedition Log card by a few lines.

## Verification

- Several parts have had a first verification pass only. Each mode guide ends with a list of what the game does not report. Open checks are listed in [TODO.md](../TODO.md) and [LINUX_TESTING.md](../LINUX_TESTING.md).
