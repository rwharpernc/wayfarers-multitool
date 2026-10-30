# Acknowledgements

WFMT is a multitool I built for Elite Dangerous commanders. Elite Dangerous has a generous community of tool authors, and many of WFMT's
features were shaped by what they have built. This page credits the projects and people whose ideas, and in some cases published data and
services, helped.

Author: R.W. Harper (CMDR Mactavious). Licensed under the GNU GPL v3.0; see `LICENSE`.
Notices that a license requires are in `THIRD-PARTY-NOTICES.md`.

**On this page**

- [How this page works](#how-this-page-works)
- [Finding your way through the galaxy](#finding-your-way-through-the-galaxy)
- [Life on the surface](#life-on-the-surface)
- [Digging in: mining](#digging-in-mining)
- [Building a home: colonization](#building-a-home-colonization)
- [Power, factions and fighting](#power-factions-and-fighting)
- [In the workshop: engineering and Odyssey](#in-the-workshop-engineering-and-odyssey)
- [Trade, missions and the ship](#trade-missions-and-the-ship)
- [On your screen: overlays](#on-your-screen-overlays)
- [Included data, and reusing WFMT](#included-data-and-reusing-wfmt)
- [The ground WFMT stands on: EDMC, services and data](#the-ground-wfmt-stands-on-edmc-services-and-data)
- [How the data is gathered and verified](#how-the-data-is-gathered-and-verified)
- [The people behind the tools](#the-people-behind-the-tools)
- [AI assistance](#ai-assistance)

## How this page works

Frontier has published very little about how the journal works or how many of the game's mechanics behave, and what there is can be unclear
or out of date. The community has spent years filling that gap: reading journals, testing in the game and sharing what they learned in
tools, forum threads, wikis and open data. WFMT is built on that work, and I'm grateful for it.

The projects below are inspiration and reference. They are not work I have copied. I read them and used them as a guide to understand how
the journal is meant to be used and how the unclear mechanics behave, and then wrote WFMT's own code and checked its behavior against real
journals and the game. None of their code runs inside WFMT. Where an entry says no code was taken, that is the case. Where a table or other
game data was taken, the entry says so, and `THIRD-PARTY-NOTICES.md` lists it with its license. I hope the effort I have added is some use
to the community in return.

Every feature in WFMT is an idea that many people in the Elite Dangerous community have built, in many forms, over many years. None of them
belongs to one tool. The projects below are examples of the community's work in each area: tools I've used, looked at or learned from. The
list isn't complete, and being listed doesn't mean a tool was the first or the only one.

Each chapter opens with a few lines on the part of the game it covers, then lists the credits for that area.

## Finding your way through the galaxy

Exploration is where most commanders start, and it is the area with the longest line of community tools behind it. Surveying a boxel,
firing the scanner on arrival, working out what a planet is worth and planning a trip are all things players have solved many times over.
WFMT's versions are its own code, shaped by what these tools showed was worth doing.

### Surveying and scanning

- **Boxel surveying** (walking a boxel's systems in order, skipping ones already visited):
  [EDJP](https://edjp.colacube.net/), [SrvSurvey](https://github.com/njthomson/SrvSurvey),
  [VoxStellar](https://voxstellar.com/), [Elite Observatory](https://github.com/Xjph/EliteObservatory)
  and [SectorLister](https://github.com/mpfj/SectorLister). The size of a boxel by mass code follows the Frontier forums thread
  "RV Sonnenkreis: Decoding Universal Cartographics".
- **Auto-honk** (firing the Discovery Scanner on arrival): EDCoPilot, VoiceAttack profiles and
  autopilot tools such as [EDAPGui](https://github.com/SumZer0-git/EDAPGui).
- **Notable Bodies alerts:**
  - The rules and thresholds follow the default criteria of [Elite Observatory](https://github.com/Xjph/ObservatoryCore)'s Explorer plugin (MIT).
  - The green gas giant temperature table is community research: CMDR Arcanic's [ED GGG](https://ed-ggg.github.io/edggg/) work, compiled for
    Observatory by DaftMav and CMDR Julian Ford's "Custom Criteria for Everyone".
  - Discovery Watch, a standalone journal watcher, was a useful reference for which rules commanders want.
  - No code was taken from any of them.
- **What is left to scan, map and sample in a system, and a card for the body you target:**
  - [SrvSurvey](https://github.com/njthomson/SrvSurvey)'s system status (scan progress, bodies still worth a DSS, bodies with life remaining)
    and body info plotters shaped the idea and which facts to show.
  - WFMT's System targets and Body info cards are its own code, built on the journal events, the scan-value estimate described below, and the
    system model in `system_survey.py`; no code was taken from SrvSurvey (GPL-3.0, the same license as WFMT).
  - The optional **Known** section (the life and points of interest other commanders found in a system) reads
    [Spansh](https://spansh.co.uk/)'s public system record, only when you tick the setting; the visit history is built from your own journals
    (`system_history.py`).
- **Random (a nearby system with no scans):** [Spansh](https://spansh.co.uk/)'s systems search, sorted by distance from your position, for the
  real systems around you, and [EDSM](https://www.edsm.net/)'s bodies list to confirm one. Both are called only when you press the button.

### What a system is worth

- **Exploration value, system age and rarity readouts:** EDJP, EDDiscovery, Elite Observatory and many other exploration tools.
- **Exploration value formula and mapping multipliers:** from [EDDiscovery](https://github.com/EDDiscovery/EliteDangerousCore)'s
  `EstimatedValues.cs` (Apache-2.0).
  - From that file: the base value (k + k x 0.56591828 x mass^0.2, at least 500), the first-discovery multiplier of 2.6, the three mapping
    multipliers (3.699622554 for a body nobody had discovered or mapped, 8.0956 for one discovered but never mapped, 3.3333333 for one
    already mapped), the efficiency bonus (1.25) and the Odyssey bonus (30% on the mapping part).
  - The per-class k values come from the same table and from Faber38/CMDRHelper.
  - [OD Explorer](https://github.com/WarmedxMints/OD-Explorer)'s estimates were used as a check: on the same journals its exobiology
    estimate matched WFMT's to the credit and its cartography estimate was within 0.2%.
  - No code was copied.

### Planning a trip

- **Expeditions** (a named trip as an ordered list of stops with notes and progress):
  [EDDiscovery](https://github.com/EDDiscovery/EDDiscovery)'s expeditions and Boxel Survey's own Waypoint Route. WFMT's is its own, and no
  code was taken. System positions come from [EDSM](https://www.edsm.net/) when you ask, and the Road to Riches and Expressway to Exomastery
  route planners are [Spansh](https://spansh.co.uk/)'s, called when you press **Plot**.
- **Frame shift drive values (Route Planner):**
  - `plugin/fsd_data.py` holds, for each frame shift drive module, its optimal mass, the most fuel one jump can use, and the two constants of
    the fuel formula, plus the jump range a Guardian FSD booster adds.
  - They are game facts that Spansh's exact plotter needs about a ship.
  - They were read on 2026-10-18 from the Coriolis data ([EDCD/coriolis-data](https://github.com/EDCD/coriolis-data); the repository declares
    no license, so only these facts are used, with credit) as [Spansh](https://spansh.co.uk/)'s own exact-plotter page carries them, and the
    request the plotter makes was taken from that page's script and checked against a real answer.
  - No code was taken, and the route is Spansh's.
  - [EDEB](https://forums.frontier.co.uk/threads/edeb-elite-dangerous-exploration-buddy.615445/), whose exact-plotter dialog showed what a ship
    has to tell Spansh, is credited for the idea and for the layout of the Route Planner's ship block; none of its code was seen.
- **The neutron route** is [Spansh](https://spansh.co.uk/)'s Route Planner, called when you press **Plot**.
- **Nearest neutron star and white dwarf lookups:** [Spansh](https://spansh.co.uk/) answers the Neutron Star and White Dwarf buttons. The optional local
  index for Neutron Star is built from Spansh's published neutron-star data dump (`systems_neutron.json.gz`, from its dumps page), which the player
  downloads when they ask.
- **System-name suggestions** (the optional list of matching systems while you type): [Spansh](https://spansh.co.uk/)'s system-name search,
  only when you tick the setting.

### Finding your way on a planet

- **Surface compass and marks** (an arrow and distance to a chosen latitude and longitude, with saved spots):
  [SrvSurvey](https://github.com/njthomson/SrvSurvey)'s target tracking and
  [ODEliteTracker](https://github.com/WarmedxMints/ODEliteTracker)'s compass and bookmarks. WFMT's is its own: it grew out of Mining's own
  hotspot arrow, and no code was taken from either.
- **Nearby points of interest:** [Canonn](https://canonn.science/) and [edastro.com](https://edastro.com/) publish the lists WFMT looks up.

## Life on the surface

Exobiology turned planets into places to work, and it brought a new kind of tool: one that predicts what might grow on a world, tracks your
samples and leads you back to the plants you found. WFMT's Organic Scanning and its overlay cards follow that tradition.

- **Exobiology overlay cards (bio status, predicted species, sample radar, sample popup):**
  - The idea of showing sampling progress, predicted species with their values, the first footfall bonus and a radar of sample circles as
    separate cards over the cockpit follows [SrvSurvey](https://github.com/njthomson/SrvSurvey)'s biology plotters (GPL-3.0, the same license
    as WFMT).
  - The small pointers beside each distance, a circle-and-hand in SrvSurvey and an arrowhead in WFMT, and leading the commander back to plants
    they identified follow SrvSurvey's tracking of scan sites.
  - The cards are WFMT's own code, built on Organic Scanning's prediction and sample tracking and the journal's `ScanOrganic`, `CodexEntry`
    and `Status.json`; no code was taken from SrvSurvey.
- **Exobiology color variants (the likely color of a species before it is sampled):**
  - The rules that tie a species' color to the star its body orbits or to a surface material come from
    [SrvSurvey](https://github.com/njthomson/SrvSurvey)'s `bio-criteria` data (GPL-3.0, the same license as WFMT), read and turned into
    WFMT's own table by `scripts/gen_organic_variants.py`.
  - The code that uses it is WFMT's own and no SrvSurvey code was taken.
  - The predictions can be checked against a commander's own journals with `scripts/verify_organic_variants.py`.
- **Exobiology species prediction and sampling help:** [EDMC-BioScan](https://github.com/Silarn/EDMC-BioScan),
  [Artemis Scanner Tracker](https://github.com/Balvald/ArtemisScannerTracker), SrvSurvey and the
  [EDMC-Canonn](https://github.com/canonn-science/EDMC-Canonn) plugin.
- **Codex and scan tallies:** Artemis Scanner Tracker, EDMC-BioScan, EDMC-Canonn, EDDiscovery and [edastro.com](https://edastro.com/).
- **My Codex's Where to look:** the species conditions and color rules WFMT already credits above (the same data the Bio predictions use),
  matched to [Canonn](https://canonn.science/)'s codex catalog by species name. No other data is used.

## Digging in: mining

Surface mining with the Rhino is a craft of its own, and the community around it has built maps, hotspot lists and waypoint arrows to make
it less of a guessing game. The Mining Book, the Live radar and the market research in WFMT all grew from those ideas.

- **Surface mining aids** (tons-remaining estimates, driven-coverage maps, hotspot lists, waypoint arrows):
  [EDRhinoSpotter](https://github.com/Fumlop/EDRhinoSpotter), [Rhino Surface Mapper](https://github.com/pbgaspar/rhino-surface-mapper),
  EDSMT, EliteMining and [EDPlanetNavigator](https://github.com/mcjohnso/EDPlanetNavigator).
- **Ideas followed from [EDRhinoSpotter](https://github.com/Fumlop/EDRhinoSpotter)** (GPL-3.0, the same license as WFMT):
  - The Mining Book's dated Depleted marks with an optional assumed refill time (and a shorter wait after a look at a deposit that is still
    empty).
  - Its Rhino stops (deposits grouped around the one with the most rigs, the best three circled).
  - Its pick of the deposit you are standing at.
  - The **Mark center** and **Mark border** marks of a mining location's center and border.
  - The Surface Live radar's drive rings (circles to drive round a marked location).
  - Its line to the nearest deposit of the material you are after.
  - The saved map picture of a location with its legend.
  - The chat commands that stand in for keyboard shortcuts.
  - The drive rings are worked out from the scanner reach and the border by WFMT's own rule, not from its figures.
  - The code is WFMT's own and none was taken from it.
- **Market research** in the Mining Book (the markets in a system that buy what you could mine there) follows an idea in
  [Rhino Surface Mapper](https://github.com/pbgaspar/rhino-surface-mapper) (GPL-3.0), but takes its commodities from your own records instead
  of a table.
- **Waiting for a `Market.json`** that the game wrote late follows the fix in [BGS-Tally](https://github.com/aussig/BGS-Tally) (MIT).
- None of their code was taken.

## Building a home: colonization

Colonization is the newest part of the game and the one with the most moving parts: construction sites, shopping lists, carriers and a
planner for what to build next. Several community projects got there first, and WFMT leans on them openly.

- **Colonization tracking:** Architect Tracker, [Raven Colonial](https://ravencolonial.com/), ED Colonization Helper, EDColony and BGS-Tally.
- **The shopping-list overlay card** follows [SrvSurvey](https://github.com/njthomson/SrvSurvey)'s layout.
- **Raven Colonial:**
  - Raven Colonial publishes its API as OpenAPI, which SrvSurvey and BGS-Tally use and which informed WFMT's plans for it.
  - WFMT's **Planned Builds** window reads one public, key-free endpoint of it (the build sites of a system) when you press a button.
  - WFMT's **My Projects** window reads a commander's active projects, hidden list and primary project (public, key-free endpoints) when it
    is opened.
  - **Create Project on Raven** and **My Projects** follow the steps of the same features in
    [SrvSurvey](https://github.com/njthomson/SrvSurvey) (GPL-3.0): choosing the location, building and layout, picking the body, naming the
    first port "Primary port", leaving the plan alone, and finding a project by the system's address and market id. Its source was read for
    the order of the calls; none of it is copied.
  - Anything WFMT sends to Raven Colonial (progress, deliveries, carrier cargo, a new project, a primary project, a counted list, a
    completion) is opt-in, off by default, and listed in the privacy page.
- **What each building costs:** the cost table behind the Planned Builds window is a copy of
  [SrvSurvey](https://github.com/njthomson/SrvSurvey)'s `colonization-costs2.json` (GPL-3.0; notice in `THIRD-PARTY-NOTICES.md`), compiled by
  its author from the game. Raven Colonial's own totals for the same buildings agree with it where I checked.
- **Shopping list order:** the overlay shopping list follows [SrvSurvey](https://github.com/njthomson/SrvSurvey)'s shopping overlay:
  alphabetical at a construction site, grouped under the market's categories elsewhere, with what the market does not sell dimmed. The
  category table (`plugin/commodity_categories.py`) is taken from its `ColonyData.mapCargoType` (GPL-3.0; notice in
  `THIRD-PARTY-NOTICES.md`). The code is WFMT's own.
- **Where to buy a Colonization commodity:** [Spansh](https://spansh.co.uk/)'s station search, the same one the Mining and Trade finders use.
  The **Best single systems** list asks the same search for every station of a few systems, one request each, and adds up their stock; the
  ranking is WFMT's own.

## Power, factions and fighting

Merits, influence and kill counts are all numbers the journal reports in pieces, and a good tracker is mostly careful bookkeeping. These
are the trackers WFMT's Powerplay, BGS and Missions modes were measured against.

- **Massacre and kill-mission tracking:** [EDMC-Massacres](https://github.com/CMDR-WDX/EDMC-Massacres),
  [EDMC-CombatTracker](https://github.com/lunarplasma/EDMC-CombatTracker), [EDCarnage](https://github.com/mmomtchev/EDCarnage) and
  [EDMMC](https://github.com/tautomer/EDMMC).
- **Powerplay merit tracking:** [EDMC-PowerPlayProgress](https://github.com/alby666/EDMC-PowerPlayProgress),
  [EliteMeritTracker](https://github.com/Fumlop/EliteMeritTracker),
  [EDMC Merit Tracker](https://gitlab.com/valdidan-edtools/edmc_merittracker) and BGS-Tally.
- **Rare goods lookups:** EDMC-PowerPlayProgress, [Inara](https://inara.cz/) and many rare-commodity guides. The legality restrictions and each
  station's distance from its star in the Rare Goods Finder's list were curated by hand from Inara.
- **BGS tracking:** [BGS-Tally](https://github.com/aussig/BGS-Tally) and its forks,
  [EliteFactionTracker](https://github.com/Haelnorr/EliteFactionTracker) and other faction trackers.
- **Megaship scans** (a count of the megaships scanned each Powerplay cycle, with name and system):
  [ODEliteTracker](https://github.com/WarmedxMints/ODEliteTracker)'s BGS data store keeps the same list.
  - Its source (no license is declared, so none of it is copied) was read for how it names the ship: the megaship you dropped to just before
    the uplink scan.
  - WFMT's is its own code, checked against real journals, with the merits each scan earned, a check that the destination really is a
    megaship, and a journal back-fill.

## In the workshop: engineering and Odyssey

Engineering is a web of materials, recipes and engineers, and the most useful tools are the ones that turn it into a shopping list. This is
the chapter with the most borrowed data, so it is the most specific about what was taken and from where.

### Materials and blueprints

- **Engineering materials** (what you hold of each Raw, Manufactured and Encoded material, with its grade and limit):
  [Elite Dangerous Odyssey Materials Helper](https://github.com/jixxed/ed-odyssey-materials-helper) (source MIT),
  [EDEngineer](https://github.com/msarilar/EDEngineer) (MIT) and EDDiscovery.
  - WFMT's is its own, built from the journal's events, and no code was taken from any of them. (What is taken is data, below.)
  - Material names, types and grades come from **[EDCD/FDevIDs](https://github.com/EDCD/FDevIDs)** (`material.csv`; see Data below).
- **Engineering blueprints** (what each blueprint takes and where its ingredients are found):
  - The recipes and the "where found" text are a trimmed copy of [EDEngineer](https://github.com/msarilar/EDEngineer)'s `blueprints.json`
    and `entryData.json` (MIT; notice in `THIRD-PARTY-NOTICES.md`), compiled by its contributors from the game.
  - That project is archived, its data last changed in March 2024, and newer game content may be missing.
  - [Elite Dangerous Odyssey Materials Helper](https://github.com/jixxed/ed-odyssey-materials-helper) shaped the idea.
  - [EDDiscovery](https://github.com/EDDiscovery/EliteDangerousCore) (Apache-2.0; notice in `THIRD-PARTY-NOTICES.md`) corrected five
    synthesis recipes, supplied seven synthesis families and nine Thargoid-war and chip materials (whose names, types and grades agree with
    the material table of elite-intel), and its engineer table is `plugin/engineers_data.py` (each engineer's place and how to find, be invited
    by and unlock them).
  - EDEngineer's data also records the Coriolis identifier of each grade, which the generated table of journal blueprint names uses.
  - No code was taken, and none of it is from Frontier.

### Engineers

- The four Colonia on-foot engineers (Baltanos, Eleanor Bresa, Rosa Dayette and Yi Shen), whom EDEngineer's table lacks, are in that table.
  Which suit and weapon upgrades each offers comes from EDCoPilot's engineer list (read for facts only).
- Yi Shen's three sets of referral items are game facts as stated in the Materials Helper's English text (MIT) and the engineering checklist
  on [edblackbox.com](https://edblackbox.com/guides/engineering/engineering-manuals/checklist.html).
- The grade thresholds and net-profit figures for ship engineers are facts from the community wiki.
- Yarden Bond's meeting requirement is five Smear campaign plans, as the community wiki and [Inara](https://inara.cz/) state; EDDiscovery's
  table lists eight.

### Planners

- **Odyssey upgrade planner** (a suit's or weapon's upgrade and modifications as a wishlist):
  - The idea follows [Elite Dangerous Odyssey Materials Helper](https://github.com/jixxed/ed-odyssey-materials-helper)'s loadout editor, which
    WFMT's is not a copy of: its stat tables are not public and none of its data or code was taken.
  - The upgrade costs are read from the game's own `UpgradeSuit` and `UpgradeWeapon` journal events (game facts), and the modification
    recipes are the blueprint table's (EDEngineer, MIT).
  - The names the journal uses for suit and weapon modifications (`suit_nightvision`, `weapon_range`) and for the weapons are the game's, as
    [EDDI](https://github.com/EDCD/EDDI)'s definitions and real journals agree; WFMT's own table maps them to the planner's names.
  - No code was taken.
- **Ship engineering planner** (a ship's engineering as a wishlist):
  - The idea follows [Elite Dangerous Odyssey Materials Helper](https://github.com/jixxed/ed-odyssey-materials-helper)'s ship builder and
    wishlist import from EDSY and Coriolis, which WFMT's is not a copy of: no code or data was taken, and its design here is the journal's own
    `Loadout` shape.
  - The journal's blueprint and effect names come from [EDCD/coriolis-data](https://github.com/EDCD/coriolis-data) (names only; notice in
    `THIRD-PARTY-NOTICES.md`), and [EDSY](https://edsy.org/) and [Coriolis](https://coriolis.io/) are where a build is designed and exported
    (SLEF).
  - The import links WFMT reads and makes (the loadout as gzip and URL-safe base64 in a Coriolis import link or an EDSY `#/I=` link) use the
    format that [EDMC](https://github.com/EDCD/EDMarketConnector)'s own shipyard-link plugins produce and that Coriolis (MIT) reads; WFMT's
    code for it is its own and no code was taken.
- **Odyssey inventory tracking:** EDMC's own ship locker data, ED Recon and the Odyssey Materials Helper.

## Trade, missions and the ship

Getting cargo from where it is cheap to where it pays, and finding where to buy what a mission needs, is a search problem more than a
journal problem. Spansh's station search does the heavy lifting, and WFMT's lists are short and labeled on purpose.

- **Best picks and Source commodities** (a short list of labeled stations for a commodity, and where to get the cargo a mission needs): the
  idea of a short list of the best places to buy or sell follows [EDCoPilot](https://www.edcopilot.com/)'s market search. WFMT's is its own
  and uses [Spansh](https://spansh.co.uk/)'s station search; no code was taken.
- **Material trader finder:** [ODEliteTracker](https://github.com/WarmedxMints/ODEliteTracker)'s material trader finder shaped the idea.
  WFMT's is its own, and no code was taken. The stations are [Spansh](https://spansh.co.uk/)'s station search, filtered by its material
  trader field.
- **Landing pad guidance:** [LandingPad](https://github.com/bgol/LandingPad) and ED Recon.
- **Screenshot conversion and renaming:** EDMC's own built-in screenshot handling and
  [EDMC-Screenshot](https://github.com/NoFoolLikeOne/EDMC-Screenshot).

## On your screen: overlays

An overlay is where all of this meets the player: cards and arrows drawn over the game. WFMT has its own on Windows and works with another
on Linux, and the design of where things go owes a lot to the tools that came before.

- **The built-in overlay's default font:** Source Sans 3 (Adobe, SIL Open Font License 1.1), bundled unmodified with its license (see
  `THIRD-PARTY-NOTICES.md`). The idea of an overlay that WFMT draws itself follows [SrvSurvey](https://github.com/njthomson/SrvSurvey)'s own
  overlay windows; no code was taken from it, and
  [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay) remains the overlay for Linux and for other plugins.
- **Hiding the overlays for a while:** that the overlays can be switched off at a keystroke without leaving the game follows
  [SrvSurvey](https://github.com/njthomson/SrvSurvey)'s overlay toggle. WFMT's is its own code (a line in the WFMT panel, a **Hide / show now** button, a Windows
  hotkey and a chat command); no code was taken from SrvSurvey.
- **The drag-and-drop layout editor on Overlay Placement:** a grid for placing overlay displays is a feature common to overlay layout tools;
  WFMT's editor (a to-scale picture of the screen with a box per display that snaps to edges and a grid) is its own design and code.
- **The color themes of the windows:** Cyan, Amber and Green follow the three themes of EDDDT, the maintainer's own companion app, and use its stylesheet's colors; Navy is WFMT's own. The code that applies a theme is WFMT's own.
- **Overlay placement:** SrvSurvey places each overlay relative to the game window (left, center or right; top, middle or bottom; plus
  pixels), which is the model WFMT's Overlay Placement follows. EDMCModernOverlay's open source made it possible to check how it maps
  positions and sizes onto the screen.

### The two overlays

WFMT has two ways to draw on the game:

- **Windows: WFMT's own overlay.** It is built into WFMT, is WFMT's own code, and needs nothing else installed. The idea of an overlay that
  WFMT draws itself is credited to [SrvSurvey](https://github.com/njthomson/SrvSurvey) above, and no code was taken from it.
- **Linux: EDMCModernOverlay.** WFMT draws through the helper app
  **[SweetJonnySauce/EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay)**. The built-in overlay is Windows only, so on
  Linux this is the overlay. It can also be chosen on Windows.
- **How WFMT uses EDMCModernOverlay:** it talks to it over its documented local protocol and ships none of its code. It is the user's own
  install.

## Included data, and reusing WFMT

WFMT's code is its own. A few of its data tables (for example the building cost table, the engineering blueprint recipes and the commodity
category table) are trimmed copies or conversions of data other projects published, and each is named in the entries above. Where a license
asks for a notice, it is in `THIRD-PARTY-NOTICES.md`, which names each source, its license and what was included. Where a project is only an
idea or a reference, the list above says so, and no code was taken.

**Reusing WFMT's ideas and code.** Every idea in WFMT came from somewhere, and the same goes for WFMT. I had some inspiration, put my own twist on it, and what you
see is the result. I would like to carry that spirit on. If you want to borrow my take on something, make it better, or make it more useful for what you are
building, go ahead. It is all good. I would appreciate a nod, but I am not holding anyone back.

How that fits the license:

- **Ideas** are free to take, with nothing to ask for. This covers how a feature works, how it looks and how the data is read. Several of WFMT's own ideas are
  the community's, as the entries above say.
- **Code** is released under the GNU General Public License v3.0 (`LICENSE`), which is what makes the rest of this possible. You may copy, change, improve and
  share it, including inside a tool you sell. The license asks that what you distribute is also under GPL-3.0 with its source available, and that the copyright
  and license notices stay with the code you reuse. Those are the license's terms, not extra ones from me.
- **A nod** to WFMT, such as a line in your README or credits, is welcome and is not required beyond those notices.
- **Included data tables** keep the license of whoever compiled them. If you reuse one, keep its notice from `THIRD-PARTY-NOTICES.md` with it, and
  pass on where it came from, so credit reaches the people who compiled it.
- **Not an official Frontier product.** WFMT is a fan-made tool, and so is anything built from it.

This note is a plain-language summary. The license text in `LICENSE` is what applies.

## The ground WFMT stands on: EDMC, services and data

### Host application

**[EDMC](https://github.com/EDCD/EDMarketConnector)** (GPL-2.0) is the host. WFMT uses its plugin API and imports its `config`, `theme` and
`myNotebook` modules at runtime.

### Services

WFMT talks to a small number of community services:

- [EDSM](https://www.edsm.net/), [Spansh](https://spansh.co.uk/), [edastro.com](https://edastro.com/) (GEC), Canonn's published site lists
  and codex catalog, [Raven Colonial](https://ravencolonial.com/) (Colonization, opt-in or on a button press), `tick.infomancer.uk` (BGS
  tick, optional), GitHub Releases (self-update, opt-in) and Discord (only your own webhook, when you press a Post button).
- [Inara](https://inara.cz/), [Coriolis](https://coriolis.io/) and [EDSY](https://edsy.org/) are linked to only.
- Every network call goes to a documented API or a published data file, never to another site's HTML, and most are opt-in or
  user-triggered.
- The Rare Goods Finder's static list was compiled from public game data, with EDSM coordinates, Inara commodity ids and Spansh system ids
  looked up once (notice in `THIRD-PARTY-NOTICES.md`).

### Data

Game facts such as thresholds, names, coordinates and measured values (the exobiology and region tables, the pad layout, scan-value
constants, mining depletion figures and micro-resource names) come from the community's published work and from the game itself. Where a
source's license asks for a notice, it is in `THIRD-PARTY-NOTICES.md`.

- Micro-resource and commodity names come from **[EDCD/FDevIDs](https://github.com/EDCD/FDevIDs)**.
- The landing-pad size of each ship (Trade mode) comes from **[EDCD/coriolis-data](https://github.com/EDCD/coriolis-data)**.
- Engineering material names, types and grades (Operations → Materials) come from FDevIDs' `material.csv` too.

## How the data is gathered and verified

The game changes, and a lot of old data about it is still in circulation, so the aim is to collect what can be found and keep it current.

- Other authors' published work is reviewed with respect for what they have built: it is checked against the game by the project owner, used
  once it has been verified, and credited here and in `THIRD-PARTY-NOTICES.md` with its license.
- What is not available as open data is measured in the game by the project owner, each value recorded with the game version, the date and a
  screenshot.
- A value that has not yet been checked in the game is marked as such.
- `docs/data_verification/verification_checklist.csv` lists every item that is still missing or still to be checked, with its source and
  license, and shows which have been verified in the game and which have not (tables added before the checklist existed are on it too).
- No Odyssey suit or weapon stat values are in WFMT yet; when they are, they will be the owner's own in-game measurements, or another author's
  published values that were checked in the game (`docs/ODYSSEY_STAT_COLLECTION.md`).
- Nothing was taken from any program's compiled files.

Where someone's published work helped, it is credited on this page. A missing or incorrect credit can be reported as an issue and will be
corrected.

WFMT's data is open under the project's license (GPL-3.0) and not restricted any further. Reuse of it is welcome; an acknowledgement of WFMT,
and of the authors credited here, is appreciated and not required.

## The people behind the tools

Elite's third-party tools are maintained by individual authors, and WFMT relies on several of them. Their projects, and where they can be
supported:

- [EDSM](https://www.patreon.com/EDSM)
- [Spansh](https://www.patreon.com/cw/spansh)
- [Inara](https://www.patreon.com/cw/artieinara)
- [SrvSurvey](https://www.patreon.com/SrvSurvey)
- [EDCoPilot](https://www.patreon.com/EDCoPilot)
- [EDEB](https://forums.frontier.co.uk/threads/edeb-elite-dangerous-exploration-buddy.615445/)
- [OD Explorer](https://github.com/WarmedxMints/OD-Explorer)
- [OD Elite Tracker](https://github.com/WarmedxMints/ODEliteTracker)

## AI assistance

**Design and coding by R.W. Harper**, with **code review and documentation** (including this page) **by Claude** (Anthropic). Disclosed for
transparency; authorship is unchanged.

*Elite Dangerous* and related marks are trademarks of Frontier Developments plc. WFMT is a fan-made tool, not official Frontier software, and
is not affiliated with the EDMC team or any project above.
