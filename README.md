<p align="center">
  <img src="images/logo.png" alt="Wayfarer's Multitool logo: a compass ring with a ship's arrowhead and a wrench, above the name" width="240">
</p>

# Wayfarer's Multitool (WFMT)

**One free add-on for Elite Dangerous that puts exploration, exobiology, mining, trading, missions, colonization, Powerplay and the BGS in a single panel.**
It runs inside [EDMC](https://github.com/EDCD/EDMarketConnector) (Elite Dangerous Market Connector) on Windows and Linux, reads your game's journal, and needs no programming knowledge.

> **Detailed instructions live in the documentation.** This page is the overview. Every feature has its own guide in [`docs/guide`](docs/guide/README.md)
> with step-by-step how-tos and worked examples, organized by feature. Start with [Getting started](docs/guide/getting-started.md), or jump straight to the
> guide for the feature you want in [The eight modes](#the-eight-modes) below.

## Contents

1. [Overview](#overview)
2. [Download and install](#download-and-install)
3. [The eight modes](#the-eight-modes)
4. [Always-on tools](#always-on-tools)
5. [Finding your way around](#finding-your-way-around)
6. [How WFMT knows what it knows](#how-wfmt-knows-what-it-knows)
7. [Known issues](#known-issues)
8. [Getting help](#getting-help)
9. [All the guides](#all-the-guides)
10. [For developers, credits and license](#for-developers-credits-and-license)

## Overview

You drop out of supercruise at the far edge of a boxel nobody has charted. The scanner has already fired, and a card on the edge of your screen lists the
bodies worth a probe run, best first. Later you are on a surface, sampling a plant, with a small radar showing how far to move before the next sample
counts. Back in the bubble, a colony site is waiting for steel and titanium, and one search finds the system that sells most of what you need.

None of these tools are new. They have been in the community for years, in various forms, each made by a dedicated commander. I put these ideas together
into one tool, on a platform that has always served me well, so that I did not have to keep up with the updates of many. WFMT is a big project and not
perfect, but it has the bells and whistles I always wanted, and I am sharing it with you. Feedback and suggestions are welcome.

### At a glance

| | |
|---|---|
| **What it is** | A free add-on for **Elite Dangerous**, open to anyone |
| **What it covers** | Powerplay, exploration and exobiology, mining, trading, missions, on-foot and cargo tracking, colonization, the BGS, sharing reports to Discord and more |
| **Where it runs** | Inside [EDMC](https://github.com/EDCD/EDMarketConnector), on Windows and Linux |
| **What you need to know** | Nothing about programming |
| **Latest release** | **1.3.1**, published 2026-10-29 ([changelog](CHANGELOG.md)) |
| **Cost and privacy** | Free. Alerts, overlays and online lookups are off until you turn them on, and every online lookup is listed on [one page](docs/guide/internet-and-privacy.md) |

## Download and install

Getting started takes a few minutes and nothing needs compiling. If EDMC is already on your computer, you are most of the way there.

1. Download **`Wayfarers-Multitool.zip`** from the [latest release](https://github.com/rwharpernc/wayfarers-multitool/releases/latest). (The green
   **Code → Download ZIP** button is the source code, not the plugin.)
2. In EDMC open **File → Settings → Plugins → Open** and extract the ZIP there, so you end up with `plugins/Wayfarers-Multitool/load.py`.
3. Restart EDMC. The **Wayfarer's Multitool (WFMT)** panel appears. Settings are under **File → Settings → WFMT**.

**On Linux**, EDMC needs a few settings first (the journal folder, `xdotool`, Flatpak permissions): see [WFMT on Linux](docs/guide/linux.md). Windows has a
built-in overlay for on-screen displays, and Linux uses [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay).

**To update**, extract the new ZIP over the old folder without deleting it first, or turn on **Automatically download and install updates** under
**Settings → WFMT → General → Updates**.

More: [Installing WFMT](docs/INSTALL.md) has folders for each system, removing WFMT and building from source.

## The eight modes

WFMT is one panel with eight **modes**, and you click a button to switch between them. Each mode is a small toolbox for one way of playing.
**Each mode has its own guide that explains every button, with how-tos and examples.**

| Mode (button) | What it is for | Detailed guide |
|---|---|---|
| **Powerplay** | Merits and Control Points for your Power; a rare goods finder; share your progress to Discord | [Powerplay](docs/guide/powerplay.md) |
| **Exploration** | Auto-honk, discovery alerts, boxel survey, scan values, Codex tally, notes, expeditions, route planners, a dashboard, a surface compass | [Exploration](docs/guide/exploration.md) |
| **Exobiology** (in **Exploration**) | Species prediction, sample tracking, a sample radar, and overlay cards for the body you are on | [Exobiology](docs/guide/exobiology.md) |
| **Mining** | Space and surface mining runs, a book of rings and deposits, Mining History, mining alerts | [Mining](docs/guide/mining.md) |
| **Trade** | Profit after fuel and repairs, fleet carrier cargo, saved sessions, best routes and prices, a watch list | [Trade](docs/guide/trade.md) |
| **Missions** | Every mission in one view, progress bars, a Missions window, where to buy the cargo | [Missions](docs/guide/missions.md) |
| **Field Ops** | Screenshots, backpack and cargo, materials, a blueprint browser, material traders, ship builds | [Field Ops](docs/guide/field-ops.md) |
| **Colonization** | Your current build, history, an archive of finished sites, and every site's shopping list | [Colonization](docs/guide/colonization.md) |
| **BGS** (**BGS**) | Faction states and what your activity does to them; share a tick's report to Discord | [BGS](docs/guide/bgs.md) |

**Sharing reports.** The BGS report and Powerplay progress can be shared three ways: copied as plain text for anywhere, copied with Discord formatting, or posted to a Discord webhook.

- **Nothing is posted on its own.** Every post follows a button press, and the switch is off until you turn it on.
- **Several channels or servers.** A webhook belongs to one channel, so each commander saves a named list of destinations, and **Post to Discord** asks which one when there are several. Commanders can copy each other's lists.
- **Posts from anywhere.** You do not need to be in the channel, or have Discord open, to post to it. Posting the same report again edits the earlier post.
- **Make it look the way you like.** A customize dialog has presets (Standard, Compact, Detailed, Plain), checkboxes for which parts of a post appear, a live preview, and templates you can save.
- **Your links stay private.** They are saved on your computer for each commander, left out of backups and never logged.

Step by step, with the Discord side explained (making the webhook, thread ids, naming the posts, common questions): [Sharing reports to Discord](docs/guide/discord.md).

**Looking for something specific?** [Features at a glance](docs/guide/features.md) lists every feature with the buttons to press, and starts with an
"I want to..." table that points to the right guide.

**Colonization is a work in progress.** It is the newest part of the game and WFMT is still growing into it. Working today: the Colony page, the Sites
window, My Projects (your projects on Raven Colonial), starting a Raven project for a site, Where to buy (with the best single systems for a whole list)
and the shopping-list overlay. Planned: co-op building and colony tracking.

## Always-on tools

Four more tools work in the background and belong to no mode: **Landing Assist**, **Interdiction Warning**, **Flight Alerts** and the **Route overlay**.
How to turn each on and what it looks like: [Always-on tools](docs/guide/always-on.md).

## Finding your way around

The modes differ, but the habits carry over. Learn these once and they work everywhere:

| To do this | Do this |
|---|---|
| Switch modes | Click a **mode button** at the top. The panel remembers where you were |
| Learn what a button does | **Hover** over it for its name and what it does ([button names](docs/guide/getting-started.md#button-names)) |
| Move around a mode | **◀ ▶** page between a mode's pages. **Click a section's title** to fold or unfold it |
| Open a pop-out window | Press its panel button. Windows remember their size and place, and close with **Esc** ([the list](docs/guide/getting-started.md#opening-the-pop-out-windows)) |
| Search the galaxy map | Use a **copy button** to put a system name on the clipboard. System-name boxes suggest as you type |
| Change a setting | **File → Settings → WFMT**, one tab per feature |
| Keep commanders apart | Each commander's data is separate, and playing with EDMC closed is fine: WFMT catches up from your journals when EDMC starts |
| Get help or save your data | **Settings → WFMT → General**: **Report an issue**, **Copy diagnostics**, **Back up my data** |

More: [Tips, quirks and workarounds](docs/guide/tips.md) · [Planned and being researched](docs/guide/planned.md).

## How WFMT knows what it knows

Like every third-party tool for Elite Dangerous, WFMT only knows what the game writes to its journal files, and not everything is logged. That shapes what
WFMT can show you. Where the journal is silent, it uses three layers, in this order:

1. **The journal.** Everything WFMT shows about *you* starts here. If the game does not write it down, WFMT cannot see it.
2. **Other places that know more.** Frontier's servers (through a signed-in EDMC) and community services: [Spansh](https://spansh.co.uk),
   [EDSM](https://www.edsm.net), Canonn, edastro and [Raven Colonial](https://ravencolonial.com). These fill gaps and never replace the journal.
3. **Workarounds, marked as such.** WFMT's own bookkeeping, estimates labeled as estimates, and steps you can take (such as opening Carrier Management so
   the game reports the figure).

Each guide ends with a table of what the game does and does not tell us, and how to work around it. If a number looks wrong, start there.

## Known issues

Most commanders will never meet these. The full list, with the fix for each, is in [Known issues](docs/guide/known-issues.md).

| Where | What you may see | Fix |
|---|---|---|
| Linux overlay | Right-hand cards stop a little short of the screen edge | With a Flatpak EDMC, grant the Graphics folder permission and set **Display scaling** on Overlay Placement ([details](docs/guide/known-issues.md#right-hand-cards-stop-a-little-short-of-the-screen-edge-linux-edmcmodernoverlay)) |
| EDMCModernOverlay | Text looks doubled or ghosted | An old overlay window is still running: end the older `overlay_client` processes and restart EDMC ([details](docs/guide/known-issues.md#overlay-text-looks-doubled-or-ghosted)) |
| EDMCModernOverlay | Text is all capitals | Pick another font under **Settings → WFMT → Overlays → Appearance → Overlay font** |
| Windows screenshots | Screenshots do not save | Controlled Folder Access or your antivirus may be blocking EDMC: allow it, or choose another folder |

**Linux support is a commitment.** The author uses both Linux and Windows. New features are proven on Windows first and Linux follows slightly behind;
what is still to check is in [Linux testing](docs/LINUX_TESTING.md).

## Getting help

Found a bug? The plugin can start the report for you, so you do not have to remember what to include.

1. Open **File → Settings → WFMT → General → Help**.
2. Press **Copy diagnostics**. This copies your versions and the matching log lines to the clipboard.
3. Press **Report an issue**. This opens a bug report in your browser with your versions already filled in.
4. Paste the diagnostics into the log box, read the form through, and submit it.

- **Step by step, with what is and is not included:** [Reporting a problem](docs/guide/reporting-problems.md).
- **By hand:** open an issue on the [Issues page](https://github.com/rwharpernc/wayfarers-multitool/issues). Say what you were doing, what you expected
  and what happened. EDMC's log helps a lot.
- **Something looks wrong?** Try [Troubleshooting](docs/guide/troubleshooting.md) first.
- **Ideas and feedback:** comments on how WFMT feels to use, and suggestions for other playstyles, belong on the same Issues page.

## All the guides

Everything is written for players, in plain language, with how-tos and examples. Pick the group that matches what you need:

| You want to | Read |
|---|---|
| **Set up** | [Installing WFMT](docs/INSTALL.md) · [Getting started](docs/guide/getting-started.md) · [Windows and Linux](docs/guide/platforms.md) · [WFMT on Linux](docs/guide/linux.md) · [Overlay setup](docs/OVERLAY_SETUP.md) · [What goes on the internet](docs/guide/internet-and-privacy.md) |
| **Use a feature** | [Features at a glance](docs/guide/features.md) · the [full guide index](docs/guide/README.md) · the mode guides in [The eight modes](#the-eight-modes) |
| **Fix a problem** | [Known issues](docs/guide/known-issues.md) · [Troubleshooting](docs/guide/troubleshooting.md) · [Linux testing](docs/LINUX_TESTING.md) |
| **Learn tricks** | [Tips, quirks and workarounds](docs/guide/tips.md) · [Planned and being researched](docs/guide/planned.md) |

## For developers, credits and license

If you want to see how WFMT works, build it or change it, start here.

- [docs/INSTALL.md](docs/INSTALL.md): installing, updating and building from source.
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md): setting up to build, test and change WFMT.
- [docs/TECHNICAL.md](docs/TECHNICAL.md): how WFMT works and why. [docs/DESIGN_NOTES.md](docs/DESIGN_NOTES.md): the reasoning behind the main
  decisions. [docs/MODULES.md](docs/MODULES.md): every module in `plugin/`.
- **Feature specifications:** [Missions](docs/MISSIONS_TECH_SPEC.md), [Mining](docs/MINING_TECH_SPEC.md), [Trade](docs/TRADE_TECH_SPEC.md),
  [Boxel Survey](docs/BOXEL_SURVEY_TECH_SPEC.md), [BGS](docs/BGS_TECH_SPEC.md), [Organic Scanning](docs/ORGANIC_SCANNING_TECH_SPEC.md),
  [Powerplay](docs/POWERPLAY_TECH_SPEC.md), [Screenshots and input automation](docs/SCREENSHOTS_AND_INPUT_TECH_SPEC.md).
- [CHANGELOG.md](CHANGELOG.md): what changed in each version.

WFMT stands on a lot of community work. [docs/ATTRIBUTIONS.md](docs/ATTRIBUTIONS.md) has the thanks and acknowledgements, chapter by chapter, and
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) carries the licenses for any data included.

### Reusing WFMT's ideas and code

Every idea in WFMT came from somewhere. The Elite Dangerous community has built these tools in many forms over many years, and I took some
inspiration, put my own twist on it, and what you see is the result. I would like to carry that spirit on. If you want to borrow my take on
something, make it better, or make it more useful for what you are building, go ahead. It is all good. I would appreciate a nod, but I am not
holding anyone back.

- **Ideas** are yours to take: how a feature works, how it looks, how the data is read. There is nothing to ask for.
- **Code** is released under the [GNU General Public License v3.0](LICENSE). You may copy, change, improve and share it, in a free tool or a paid one,
  as long as what you pass on is also under GPL-3.0 with its source available, and the copyright and license notices stay with the code you reuse.
  That is what the license asks for, and I am not adding anything to it.
- **A nod** (a line in your README, your credits or a post) is welcome and never required beyond those notices.
- **Included data** keeps the license of whoever compiled it, listed in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

The longer version is in [docs/ATTRIBUTIONS.md](docs/ATTRIBUTIONS.md#included-data-and-reusing-wfmt).

Built and maintained by R.W. Harper: CMDR Tiber Caelvox. Copyright (c) 2026 R.W. Harper. Released under the
[GNU General Public License v3.0](LICENSE).

*Elite Dangerous* is a trademark of Frontier Developments plc. WFMT is a fan-made tool and is not official Frontier software.
