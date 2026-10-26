<p align="center">
  <img src="images/logo.png" alt="Wayfarer's Multitool logo: a compass ring with a ship's arrowhead and a wrench, above the name" width="240">
</p>

# Wayfarer's Multitool (WFMT)

A free add-on for **Elite Dangerous** that puts a set of handy tools in one panel. It is open to anyone who wants it.

- **What it covers:** Powerplay, exploration, mining, trading, missions, on-foot and cargo tracking, colonization, the BGS and more.
- **Where it runs:** inside [EDMC](https://github.com/EDCD/EDMarketConnector) (Elite Dangerous Market Connector), a free companion program many commanders already use, on Windows and Linux.
- **What you need to know:** nothing about programming.

**Version 1.0.0** is being prepared for release. The download links below start working once it is published.

## Contents

- [Download and install](#download-and-install)
- [What's in the multitool](#whats-in-the-multitool)
- [Finding your way around](#finding-your-way-around)
- [About WFMT](#about-wfmt)
- [How WFMT knows what it knows](#how-wfmt-knows-what-it-knows)
- [Known issues](#known-issues)
- [Getting help](#getting-help)
- [All the guides](#all-the-guides)
- [For developers, credits and license](#for-developers-credits-and-license)

<a id="quick-start"></a>

## Download and install

1. Download **`Wayfarers-Multitool.zip`** from the [latest release](https://github.com/rwharpernc/wayfarers-multitool/releases/latest). (The green **Code → Download ZIP** button is the source code, not the plugin.)
2. In EDMC open **File → Settings → Plugins → Open** and extract the ZIP there, so you end up with `plugins/Wayfarers-Multitool/load.py`.
3. Restart EDMC. The **Wayfarer's Multitool (WFMT)** panel appears. Settings are under **File → Settings → WFMT**.

On **Linux**, EDMC needs a few settings first (the journal folder, `xdotool`, Flatpak permissions): see [WFMT on Linux](docs/guide/linux.md). For on-screen displays, Windows has a built-in overlay and Linux uses [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay).

**Full instructions** (folders for each system, updating, removing, building from source): [docs/INSTALL.md](docs/INSTALL.md). To update later, extract the new ZIP over the old folder without deleting it first, or turn on **Automatically download and install updates** under **Settings → WFMT → General → Updates**.

## What's in the multitool

One panel, eight **modes**. Click a button to switch between them.

| Mode (button) | What it's for | Guide |
|---|---|---|
| **Powerplay** (**P.P.**) | Merits and Control Points for your Power; a rare goods finder. | [Powerplay](docs/guide/powerplay.md) |
| **Exploration** (**EXP**) | Auto-honk, discovery alerts, boxel survey, scan values, exobiology, Codex tally, notes, expeditions, ship and carrier route planners, a dashboard window, a surface compass. | [Exploration](docs/guide/exploration.md), [Exobiology](docs/guide/exobiology.md) |
| **Mining** (**MIN**) | Space and surface mining runs, a book of rings and a book of deposits, Mining History, mining alerts. | [Mining](docs/guide/mining.md) |
| **Trade** (**TRD**) | Profit after fuel and repairs, fleet carrier cargo, saved sessions, best routes and prices, a watch list. | [Trade](docs/guide/trade.md) |
| **Missions** (**MSN**) | Every mission in one view, progress bars, a Missions window, where to buy the cargo. | [Missions](docs/guide/missions.md) |
| **Field Ops** (**OPS**) | Screenshots, backpack and cargo, materials, a blueprint browser, material traders, ship builds. | [Field Ops](docs/guide/field-ops.md) |
| **Colonization** (**COL**) | Your current build, history, and every site's shopping list. | [Colonization](docs/guide/colonization.md) |
| **BGS** (**BGS**) | Faction states and what your activity does to them. | [BGS](docs/guide/bgs.md) |

Four more tools are always on and belong to no mode: **Landing Assist**, **Interdiction Warning**, **Flight Alerts** and the **Route overlay** ([guide](docs/guide/always-on.md)).

**Looking for something specific?** [Features at a glance](docs/guide/features.md) lists every feature with the buttons to press, and starts with a "I want to…" table that points to the right guide.

**Colonization is a work in progress.**

- The COL page, the Sites window, My Projects (your projects on Raven Colonial), starting a Raven project for a site, Where to buy (with the best single systems for a whole list), and the shopping-list overlay work today.
- Co-op building and colony tracking are planned.
- Until then, everything on the COL page is about **you**.

## Finding your way around

These work the same in every mode:

- **Mode buttons** at the top switch modes; the panel remembers where you were. **Hover** over any button for its full name ([button names](docs/guide/getting-started.md#button-names)).
- **◀ ▶** page between a mode's pages. **Click a section's title** to fold or unfold it.
- **Pop-out windows** open from panel buttons, remember their size and place, and close with **Esc** ([the list](docs/guide/getting-started.md#opening-the-pop-out-windows)).
- **Copy buttons** put a system name on the clipboard for the galaxy map search. System-name boxes suggest as you type.
- **Settings** are under **File → Settings → WFMT**, one tab per feature. Alerts, overlays and online lookups are **off until you turn them on**.
- **Each commander's data is separate**, and playing with EDMC closed is fine: WFMT catches up from your journals when EDMC starts.
- **Help and backups** are under **Settings → WFMT → General**: **Report an issue**, **Copy diagnostics**, **Back up my data**.

More: [Tips, quirks and workarounds](docs/guide/tips.md) · [Planned and being researched](docs/guide/planned.md).

## About WFMT

WFMT is built around the author's own ways of playing: exploring, mining, trading, colonizing and Powerplay. Elite Dangerous has a long line of community tools, and [docs/ATTRIBUTIONS.md](docs/ATTRIBUTIONS.md) credits the projects and data that helped. [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) carries the licenses for any data included.

If a workflow feels clumsy, a window is hard to read, or your playstyle is missing, please say so on the [issue tracker](https://github.com/rwharpernc/wayfarers-multitool/issues).

## How WFMT knows what it knows

Like every third-party tool for Elite Dangerous, WFMT only knows what the game writes to its journal files, and not everything is logged. Where the journal is silent, WFMT uses three layers:

1. **The journal.** Everything WFMT shows about *you* starts here. If the game doesn't write it down, WFMT can't see it.
2. **Other places that know more.** Frontier's servers (through a signed-in EDMC) and community services: [Spansh](https://spansh.co.uk), [EDSM](https://www.edsm.net), Canonn, edastro, [Raven Colonial](https://ravencolonial.com). These fill gaps and never replace the journal. Each is listed on the [internet page](docs/guide/internet-and-privacy.md).
3. **Workarounds, marked as such.** WFMT's own bookkeeping, estimates labeled as estimates, and steps you can take (such as opening Carrier Management so the game reports the figure).

Each guide ends with a table of what the game does and doesn't tell us, and how to work around it. If a number looks wrong, start there.

## Known issues

The full list, with the fix for each, is in [Known issues](docs/guide/known-issues.md). The ones people meet most:

- **Linux: right-hand overlay cards stop a little short of the screen edge.**
  - Fix: with a Flatpak EDMC, grant the Graphics folder permission and set **Display scaling** on Overlay Placement ([details](docs/guide/known-issues.md#right-hand-cards-stop-a-little-short-of-the-screen-edge-linux-edmcmodernoverlay)).
- **Overlay text looks doubled or ghosted** (EDMCModernOverlay only).
  - Cause: an old overlay window is still running.
  - Fix: end the older `overlay_client` processes and restart EDMC ([details](docs/guide/known-issues.md#overlay-text-looks-doubled-or-ghosted)).
- **Overlay text is all capitals** (EDMCModernOverlay only).
  - Fix: pick another font under **Settings → WFMT → Overlays → Appearance → Overlay font**.
- **Windows: screenshots do not save.**
  - Cause: Controlled Folder Access or your antivirus may be blocking EDMC.
  - Fix: allow it, or choose another folder.

### Linux support

Linux support is a commitment. The author uses both Linux and Windows.

New features are proven on Windows first and Linux follows slightly behind. What is still to check is in [Linux testing](docs/LINUX_TESTING.md).

## Getting help

Found a bug? The plugin can start the report for you:

1. Open **File → Settings → WFMT → General → Help**.
2. Press **Copy diagnostics**. This copies your versions and the matching log lines to the clipboard.
3. Press **Report an issue**. This opens a bug report in your browser with your versions already filled in.
4. Paste the diagnostics into the log box, read the form through, and submit it.

Step by step, with what is and isn't included: [Reporting a problem](docs/guide/reporting-problems.md).

You can also open an issue by hand on the [Issues page](https://github.com/rwharpernc/wayfarers-multitool/issues):

- Say what you were doing, what you expected and what happened.
- EDMC's log helps a lot.
- Something looks wrong? Try [Troubleshooting](docs/guide/troubleshooting.md) first.

Ideas, comments on how WFMT feels to use, and suggestions for other playstyles belong on the same Issues page.

## All the guides

- **Set up:** [Installing WFMT](docs/INSTALL.md) · [Getting started](docs/guide/getting-started.md) · [Windows and Linux](docs/guide/platforms.md) · [WFMT on Linux](docs/guide/linux.md) · [Overlay setup](docs/OVERLAY_SETUP.md) · [What goes on the internet](docs/guide/internet-and-privacy.md)
- **Use it:** [Features at a glance](docs/guide/features.md) · [full guide index](docs/guide/README.md)
- **When something's wrong:** [Known issues](docs/guide/known-issues.md) · [Troubleshooting](docs/guide/troubleshooting.md) · [Linux testing](docs/LINUX_TESTING.md)

## For developers, credits and license

- [docs/INSTALL.md](docs/INSTALL.md): installing, updating and building from source.
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md): setting up to build, test and change WFMT.
- [docs/TECHNICAL.md](docs/TECHNICAL.md): how WFMT works and why. [docs/DESIGN_NOTES.md](docs/DESIGN_NOTES.md): the reasoning behind the main decisions. [docs/MODULES.md](docs/MODULES.md): every module in `plugin/`.
- **Feature specifications:** [Missions](docs/MISSIONS_TECH_SPEC.md), [Mining](docs/MINING_TECH_SPEC.md), [Trade](docs/TRADE_TECH_SPEC.md), [Boxel Survey](docs/BOXEL_SURVEY_TECH_SPEC.md), [BGS](docs/BGS_TECH_SPEC.md), [Organic Scanning](docs/ORGANIC_SCANNING_TECH_SPEC.md), [Powerplay](docs/POWERPLAY_TECH_SPEC.md), [Screenshots and input automation](docs/SCREENSHOTS_AND_INPUT_TECH_SPEC.md).
- [CHANGELOG.md](CHANGELOG.md) · [docs/ATTRIBUTIONS.md](docs/ATTRIBUTIONS.md) (thanks and acknowledgements).

Built and maintained by R.W. Harper: CMDR Mactavious.

Copyright (c) 2026 R.W. Harper. Released under the [GNU General Public License v3.0](LICENSE). Third-party notices are in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

*Elite Dangerous* is a trademark of Frontier Developments plc. WFMT is a fan-made tool and is not official Frontier software.
