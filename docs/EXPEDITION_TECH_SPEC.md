# Expedition planning technical specification

This page is the design for simplifying how an expedition is planned and run in WFMT, for the 1.6.0 release. It describes what is confusing today, the single model that replaces it, the window and panel that follow from it, what moves or goes, how saved data stays compatible, and how the change is tested and documented. It is written before any code, to be reviewed first.

- **Status:** design for review. Nothing in this page is built yet.
- **Release:** 1.6.0 (a feature release: it changes the screens, not the saved files).
- **Scope:** planning and running an expedition (the Expedition window and the Exploration panel row). The data model underneath is not merged in this release.

**On this page:**

- [Purpose and success criteria](#purpose-and-success-criteria)
- [Today](#today)
- [The design](#the-design)
- [What moves and what goes](#what-moves-and-what-goes)
- [Compatibility and risk](#compatibility-and-risk)
- [Testing and documentation](#testing-and-documentation)
- [Out of scope](#out-of-scope)
- [Decisions made and one left open](#decisions-made-and-one-left-open)

## Purpose and success criteria

The commander finds expeditions confusing to plan and to run. The aim is one clear way to plan a trip and run it, without having to learn the structure underneath, while keeping every capability that exists now: trips with stops, trips from a plotted route, and trips with no list at all.

The change is successful when:

1. A commander can start any kind of trip from one place, New expedition, and finds the same controls in the same place: Start, Pause, Stop, Copy next and Copy on arrival in the window, and the same without Start on the panel row.
2. There are two tabs in the Expedition window, Current and History, instead of Plan, Route and Log.
3. Every expedition and Expedition Log run saved by an earlier version opens exactly as before, with no migration step.
4. The Expedition guide can be explained in one short path: New expedition, then Start.

## Today

The facts below come from the code (`expedition.py`, `expedition_link.py`, `expedition_hub.py`, `expedition_window.py`, `expedition_log_window.py`, `expedition_panel.py`).

- There are two records. An expedition (the planner: a name, a status and stops) and a run in the Expedition Log (what happened, with totals). A link (`expedition_link.py`) keeps their Start, Pause and Stop in step when "Start the Expedition Log with an expedition" is ticked, which it is by default.
- One window holds three tabs: Plan (the expeditions and their stops), Route (the Route Planner) and Log (the archive and totals).
- There are seven ways to begin a trip: typed stops, a CSV import, the route plotted in the game, Road to Riches, Exomastery, Neutron route, and "Start from my last sale" in the Log.
- The Log can start a trip with no stops. The planner cannot: `Expedition.start` refuses an expedition with no stops.
- The controls are split. The Exploration panel row has Copy next and Copy on arrival but no Start or Stop. The window has Start, Pause and Stop but no Copy next.

## The design

### One thing you see: an expedition, with a kind

The commander works with one object, an expedition: a name, optional stops and a state (planned, running, paused or done). New expedition is one dialog that asks which kind of trip it is:

| Kind | How its stops are made | Replaces |
|---|---|---|
| Route | Filled in from a plotted route: Neutron route, Road to Riches, Exomastery, or the route plotted in the game | The Route tab, and the three Spansh planner buttons on the Plan tab |
| Places | Typed, pasted or imported (CSV) by the commander, in their own order, with notes | Adding stops on the Plan tab |
| Free | No stops. Optionally counted from the last sale of a chosen kind | Starting a run in the Log, and "Start from my last sale" |

The kind only decides how the stop list is filled. It is not stored: it can be worked out from the expedition (stops from a route or by hand, or none). After creation every expedition behaves the same: one Start, one Pause, one Stop, and the linked Expedition Log run follows them exactly as `expedition_link.py` does today.

A Free expedition is an expedition with no stops. To make that possible, `Expedition.start` no longer requires a stop. Stops can be added while it runs, and the statistics count while it is active as they do now. Everything that reads the next stop must already cope with there being none, and the plan verifies this.

### The window: two tabs

```
Expedition: [ Colonia run  v ]  [ New expedition... ]
[ Start ] [ Pause ] [ Stop ]  [ Copy next ]  [x] Copy on arrival
Active, 12 of 40 stops, 2 h 14 min, next: <system>
----------------------------------------------------------------
 #  System            Body        Note            Visited
 ... the stops table ...
 [ Add stop ] [ Import ] [ Plot more ] [ Share ]
----------------------------------------------------------------
 Current | History
```

- Current shows the selected expedition: the controls, its progress and its stops in one place. Copy next and Copy on arrival sit beside Start, Pause and Stop, so there is one set of controls.
- History is today's Expedition Log: the archive, the totals and the editing of past runs. Its contents do not change.
- Plot more reuses the Route Planner as a step. The Route tab no longer exists as a tab.
- The Settings strip across the top of the window stays as it is, including "Copy on arrival" and "Start the Expedition Log with an expedition".

### The panel row and the Route Planner section

- The Exploration panel's Expedition row shows the running expedition (name, progress, next stop) with Pause or Resume, Stop, Copy next, Copy on arrival and Open. It has no Start: a trip is started from the window, through New expedition or the Start on Current.
- The Route Planner section stays as the quick way to plot a route. Its "Start expedition" button goes through the same New expedition path (the Route kind), so there is one way to turn a plotted route into an expedition.

## What moves and what goes

- **Goes:** the Route tab (its window code is reused as the Route step of New expedition and as Plot more), and the name "Log" for the second tab, which becomes History.
- **Moves under buttons on Current:** Add stop and Import (CSV, the game's route); Plot more (Road to Riches, Exomastery, Neutron route); Locate and reorder (EDSM); Share (the two Discord posts).
- **Stays as it is:** the Expedition Log's overlay card, the Dashboard, the two Discord posts and their Customize reports, and the Settings strip.

## Compatibility and risk

- `expeditions.json` and `expedition_log.json` keep their format. No migration runs, and a downgrade still reads the files.
- The one rule change is that an expedition may start with no stops. An older version opening such a file sees an active expedition with no stops, which it already displays.
- The largest risk is any code that opens the Log tab or the Route tab by name (from the panel, the Dashboard, the overlay or a Discord share). Those become History and the Route step. The plan begins by finding every such call before the tabs are changed.
- The second risk is the stop-less start: the plan includes a test for the progress, distance and Discord post of an expedition with no stops.

## Testing and documentation

- **Logic tests** (no screen code): a small module makes an expedition of each kind and starts, pauses and stops it through the existing link. Tests cover the stop-less start, a Route kind producing the same stops as the planner buttons do today, a Places kind from CSV, and the Free kind counted from a sale.
- **Window tests** with real Tk windows: the two tabs, the New expedition dialog for each kind, and the single set of controls on Current and on the panel row. Existing tests that name the old tabs move to the new names.
- **Docs:** the Expedition section of the Exploration guide is rewritten shorter, around New expedition then Start. The changelog, `STATUS.md`, the test plan lists and the version bump to 1.6.0 follow at release preparation, as for every release.
- Tests run in the Docker container only, as for every change.

## Out of scope

Merging the planner and Log records into one (a later change, if it proves worth the migration), the Log's editing fields, the carrier route planner, and the Boxel Survey and Region Sweep tools.

## Decisions made and one left open

- **Made:** approach "one expedition, two books underneath" (not three tabs tidied, and not a merged record); three kinds (Route, Places, Free); two tabs (Current and History); the panel row has no Start.
- **Open:** whether "Start the Expedition Log with an expedition" stays an option on the Settings strip or is removed so the Log always follows. This specification keeps it, so existing choices are respected; removing it is a small follow-up if the commander prefers the Log to always follow.
