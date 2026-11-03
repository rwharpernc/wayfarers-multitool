# Acknowledgements

WFMT is a multitool that I built to play Elite Dangerous with. I wrote it for myself first and then shared it with anyone who may be
interested. Elite Dangerous has a community of tool authors, and many of WFMT's features were informed by the tools they have built. This
page credits the projects and people whose ideas, and in some cases published data and services, were used.

The ideas in other tools were used as inspiration only. The code in WFMT is my own implementation, adapted to my way of playing, and
features continue to be revised as better approaches are found.

Author: R.W. Harper (CMDR Mactavious).

Licensed under the GNU GPL v3.0; see `LICENSE`.

Notices that a license requires are in `THIRD-PARTY-NOTICES.md`.

**On this page**

- [How this page works](#how-this-page-works)
- [Exploration](#exploration)
- [Exobiology](#exobiology)
- [Mining](#mining)
- [Colonization](#colonization)
- [Power, factions and combat](#power-factions-and-combat)
- [Engineering and Odyssey](#engineering-and-odyssey)
- [Trade, missions and the ship](#trade-missions-and-the-ship)
- [Overlays](#overlays)
- [Included data, and reusing WFMT](#included-data-and-reusing-wfmt)
- [Host application, services and data](#host-application-services-and-data)
- [Data gathering and verification](#data-gathering-and-verification)
- [Supporting the tool authors](#supporting-the-tool-authors)
- [AI assistance](#ai-assistance)

## How this page works

Frontier has published little documentation of the journal or of many game mechanics. The Elite Dangerous community has filled part of
that gap through journal analysis, in-game testing, tools, forum threads, wikis and open data. WFMT draws on that work.

The projects listed below are inspiration and reference. No code from them was copied, and none of their code runs inside WFMT. Their
projects were read as a guide to how the journal is used and how less documented mechanics behave. WFMT's code was then written
independently, and its behavior was checked against real journals and the game. Where an entry states that no code was taken, no code was
taken. Where a table or other game data was taken, the entry states so, and `THIRD-PARTY-NOTICES.md` lists it with its license.

Each feature in WFMT is an idea that members of the community have implemented in several forms over several years. No feature belongs to
a single tool. The projects listed are examples of the community's work in each area: tools that were used, examined or learned from. The
list is not complete, and a listing does not indicate that a tool was the first or the only one of its kind.

Each section lists the credits for one area of the game. Entries are structured as follows:

- **Feature:** the WFMT feature, with a short description where needed.
  - **Credit:** the projects and people credited.
  - **Use in WFMT:** what was taken from the credited work (an idea, a reference, data or a service).
  - **Code:** whether any code was taken.

## Exploration

### Surveying and scanning

- **Boxel surveying** (walking the systems of a boxel in order, skipping systems already visited)
  - **Credit:** [EDJP](https://edjp.colacube.net/), [SrvSurvey](https://github.com/njthomson/SrvSurvey),
    [VoxStellar](https://voxstellar.com/), [Elite Observatory](https://github.com/Xjph/EliteObservatory) and
    [SectorLister](https://github.com/mpfj/SectorLister).
  - **Use in WFMT:** idea. The size of a boxel by mass code follows the Frontier forums thread "RV Sonnenkreis: Decoding Universal
    Cartographics".
  - **Code:** none taken.
- **Auto-honk** (firing the Discovery Scanner on arrival)
  - **Credit:** EDCoPilot, VoiceAttack profiles and autopilot tools such as [EDAPGui](https://github.com/SumZer0-git/EDAPGui).
  - **Use in WFMT:** idea.
  - **Code:** none taken.
- **Notable Bodies alerts**
  - **Credit:** [Elite Observatory](https://github.com/Xjph/ObservatoryCore) Explorer plugin (MIT); CMDR Arcanic's
    [ED GGG](https://ed-ggg.github.io/edggg/) work, compiled for Observatory by DaftMav; CMDR Julian Ford's "Custom Criteria for
    Everyone"; Discovery Watch (reference).
  - **Use in WFMT:** the rules and thresholds follow the default criteria of the Elite Observatory Explorer plugin. The green gas giant
    temperature table is community research from ED GGG and "Custom Criteria for Everyone".
  - **Code:** none taken from any of them.
- **System targets and Body info cards** (what remains to be scanned, mapped and sampled in a system, and a card for the targeted body)
  - **Credit:** [SrvSurvey](https://github.com/njthomson/SrvSurvey) (GPL-3.0, the same license as WFMT).
  - **Use in WFMT:** SrvSurvey's system status (scan progress, bodies still worth a DSS, bodies with life remaining) and body info
    plotters informed the idea and the choice of facts shown.
  - **Code:** WFMT's own, built on the journal events, the scan-value estimate described below and the system model in
    `system_survey.py`. None taken from SrvSurvey.
- **Known section** (the life and points of interest that other commanders found in a system)
  - **Credit:** [Spansh](https://spansh.co.uk/).
  - **Use in WFMT:** reads Spansh's public system record, only when the setting is enabled. The visit history is built from the
    commander's own journals (`system_history.py`).
  - **Code:** WFMT's own.
- **Random** (a nearby system with no scans)
  - **Credit:** [Spansh](https://spansh.co.uk/) and [EDSM](https://www.edsm.net/).
  - **Use in WFMT:** Spansh's systems search, sorted by distance from the commander's position, supplies the systems. EDSM's bodies list
    confirms a candidate. Both are called only when the button is pressed.
  - **Code:** WFMT's own.

### System value

- **Exploration value, system age and rarity readouts**
  - **Credit:** EDJP, EDDiscovery, Elite Observatory and other exploration tools.
  - **Use in WFMT:** idea.
  - **Code:** none taken.
- **Exploration value formula and mapping multipliers**
  - **Credit:** [EDDiscovery](https://github.com/EDDiscovery/EliteDangerousCore) (`EstimatedValues.cs`, Apache-2.0); Faber38/CMDRHelper;
    [OD Explorer](https://github.com/WarmedxMints/OD-Explorer) (reference).
  - **Use in WFMT:** from `EstimatedValues.cs`: the base value (k + k x 0.56591828 x mass^0.2, at least 500), the first-discovery
    multiplier of 2.6, the three mapping multipliers (3.699622554 for a body that was neither discovered nor mapped, 8.0956 for a body
    discovered but not mapped, 3.3333333 for a body already mapped), the efficiency bonus (1.25) and the Odyssey bonus (30% of the mapping
    part). The per-class k values come from the same table and from Faber38/CMDRHelper.
  - **Code:** none copied.

### Trip planning

- **Expeditions** (a named trip as an ordered list of stops with notes and progress)
  - **Credit:** [EDDiscovery](https://github.com/EDDiscovery/EDDiscovery) expeditions and the Waypoint Route of Boxel Survey;
    [EDSM](https://www.edsm.net/); [Spansh](https://spansh.co.uk/).
  - **Use in WFMT:** idea. System positions come from EDSM on request. The Road to Riches and Expressway to Exomastery route planners are
    Spansh's, called when **Plot** is pressed.
  - **Code:** none taken.
- **Frame shift drive values** (Route Planner)
  - **Credit:** [EDCD/coriolis-data](https://github.com/EDCD/coriolis-data); [Spansh](https://spansh.co.uk/);
    [EDEB](https://forums.frontier.co.uk/threads/edeb-elite-dangerous-exploration-buddy.615445/).
  - **Use in WFMT:** `plugin/fsd_data.py` holds, for each frame shift drive module, the optimal mass, the maximum fuel usable in one jump
    and the two constants of the fuel formula, together with the jump range added by a Guardian FSD booster. These are game facts required
    by Spansh's exact plotter. They were read on 2026-10-18 from the Coriolis data, as carried by Spansh's exact-plotter page. The
    coriolis-data repository declares no license, so only these facts are used, with credit. The request the plotter makes was taken from
    that page's script and checked against a real answer. The route is Spansh's. EDEB's exact-plotter dialog showed what a ship must
    provide to Spansh, and EDEB is credited for that idea and for the layout of the Route Planner's ship block.
  - **Code:** none taken. No EDEB code was seen.
- **Neutron route**
  - **Credit:** [Spansh](https://spansh.co.uk/).
  - **Use in WFMT:** Spansh's Route Planner, called when **Plot** is pressed.
  - **Code:** none taken.
- **Nearest neutron star and white dwarf lookups**
  - **Credit:** [Spansh](https://spansh.co.uk/).
  - **Use in WFMT:** Spansh answers the Neutron Star and White Dwarf buttons. The optional local index for Neutron Star is built from
    Spansh's published neutron-star data dump (`systems_neutron.json.gz`, from its dumps page), which is downloaded on request.
  - **Code:** WFMT's own.
- **System-name suggestions** (an optional list of matching systems while typing)
  - **Credit:** [Spansh](https://spansh.co.uk/).
  - **Use in WFMT:** Spansh's system-name search, only when the setting is enabled.
  - **Code:** WFMT's own.

### Planetary navigation

- **Surface compass and marks** (an arrow and distance to a chosen latitude and longitude, with saved spots)
  - **Credit:** [SrvSurvey](https://github.com/njthomson/SrvSurvey) target tracking and
    [ODEliteTracker](https://github.com/WarmedxMints/ODEliteTracker) compass and bookmarks.
  - **Use in WFMT:** idea. WFMT's implementation developed from the hotspot arrow of Mining.
  - **Code:** none taken from either.
- **Nearby points of interest**
  - **Credit:** [Canonn](https://canonn.science/) and [edastro.com](https://edastro.com/).
  - **Use in WFMT:** the lists they publish are looked up.
  - **Code:** WFMT's own.

## Exobiology

- **Exobiology overlay cards** (bio status, predicted species, sample radar, sample popup)
  - **Credit:** [SrvSurvey](https://github.com/njthomson/SrvSurvey) biology plotters (GPL-3.0, the same license as WFMT).
  - **Use in WFMT:** the idea of showing sampling progress, predicted species with their values, the first footfall bonus and a radar of
    sample circles as separate cards over the cockpit follows SrvSurvey's biology plotters. The small pointer beside each distance (a
    circle and hand in SrvSurvey, an arrowhead in WFMT) and leading the commander back to identified plants follow SrvSurvey's tracking of
    scan sites.
  - **Code:** WFMT's own, built on Organic Scanning's prediction and sample tracking and on the journal's `ScanOrganic`, `CodexEntry` and
    `Status.json`. None taken from SrvSurvey.
- **Exobiology color variants** (the likely color of a species before it is sampled)
  - **Credit:** [SrvSurvey](https://github.com/njthomson/SrvSurvey) (`bio-criteria` data, GPL-3.0, the same license as WFMT).
  - **Use in WFMT:** the rules that tie a species' color to the star its body orbits or to a surface material are read from the
    `bio-criteria` data and converted into WFMT's own table by `scripts/gen_organic_variants.py`. The predictions can be checked against a
    commander's journals with `scripts/verify_organic_variants.py`.
  - **Code:** WFMT's own. None taken from SrvSurvey.
- **Exobiology species prediction and sampling**
  - **Credit:** [EDMC-BioScan](https://github.com/Silarn/EDMC-BioScan),
    [Artemis Scanner Tracker](https://github.com/Balvald/ArtemisScannerTracker), SrvSurvey and
    [EDMC-Canonn](https://github.com/canonn-science/EDMC-Canonn).
  - **Use in WFMT:** idea.
  - **Code:** none taken.
- **Codex and scan tallies**
  - **Credit:** Artemis Scanner Tracker, EDMC-BioScan, EDMC-Canonn, EDDiscovery and [edastro.com](https://edastro.com/).
  - **Use in WFMT:** idea.
  - **Code:** none taken.
- **My Codex, Where to look**
  - **Credit:** [Canonn](https://canonn.science/).
  - **Use in WFMT:** the species conditions and color rules credited above (the data used by the Bio predictions), matched to Canonn's
    codex catalog by species name. No other data is used.
  - **Code:** WFMT's own.

## Mining

- **Surface mining aids** (tons-remaining estimates, driven-coverage maps, hotspot lists, waypoint arrows)
  - **Credit:** [EDRhinoSpotter](https://github.com/Fumlop/EDRhinoSpotter),
    [Rhino Surface Mapper](https://github.com/pbgaspar/rhino-surface-mapper), EDSMT, EliteMining and
    [EDPlanetNavigator](https://github.com/mcjohnso/EDPlanetNavigator).
  - **Use in WFMT:** idea.
  - **Code:** none taken.
- **Ideas from EDRhinoSpotter** (GPL-3.0, the same license as WFMT)
  - **Credit:** [EDRhinoSpotter](https://github.com/Fumlop/EDRhinoSpotter).
  - **Use in WFMT:** the following ideas.
    - The Mining Book's dated Depleted marks, with an optional assumed refill time and a shorter wait after a deposit that is still empty
      is checked again.
    - Rhino stops (deposits grouped around the deposit with the most rigs, with the best three circled).
    - The selection of the deposit the commander is standing at.
    - The **Mark center** and **Mark border** marks of a mining location.
    - The drive rings of the Surface Live radar (circles to drive around a marked location). WFMT computes them from the scanner reach
      and the border by its own rule, not from EDRhinoSpotter's figures.
    - A line to the nearest deposit of the wanted material.
    - The saved map picture of a location with its legend.
    - Chat commands that stand in for keyboard shortcuts.
  - **Code:** WFMT's own. None taken from EDRhinoSpotter.
- **Market research** in the Mining Book (markets in a system that buy what can be mined there)
  - **Credit:** [Rhino Surface Mapper](https://github.com/pbgaspar/rhino-surface-mapper) (GPL-3.0).
  - **Use in WFMT:** idea. WFMT takes its commodities from the commander's own records instead of a table.
  - **Code:** none taken.
- **Waiting for a late `Market.json`**
  - **Credit:** [BGS-Tally](https://github.com/aussig/BGS-Tally) (MIT).
  - **Use in WFMT:** WFMT follows BGS-Tally's fix for a `Market.json` that the game writes late.
  - **Code:** none taken.

## Colonization

- **Colonization tracking**
  - **Credit:** Architect Tracker, [Raven Colonial](https://ravencolonial.com/), ED Colonization Helper, EDColony and BGS-Tally.
  - **Use in WFMT:** idea.
  - **Code:** none taken.
- **Shopping-list overlay card**
  - **Credit:** [SrvSurvey](https://github.com/njthomson/SrvSurvey).
  - **Use in WFMT:** the layout follows SrvSurvey's.
  - **Code:** none taken.
- **Raven Colonial integration**
  - **Credit:** [Raven Colonial](https://ravencolonial.com/); [SrvSurvey](https://github.com/njthomson/SrvSurvey) (GPL-3.0).
  - **Use in WFMT:** Raven Colonial publishes its API as OpenAPI.
    - The **Planned Builds** window reads one public, key-free endpoint (the build sites of a system) when a button is pressed.
    - The **My Projects** window reads a commander's active projects, hidden list and primary project (public, key-free endpoints) when
      it is opened.
    - **Create Project on Raven** and **My Projects** follow the steps of the same features in SrvSurvey: choosing the location, building
      and layout, picking the body, naming the first port "Primary port", leaving the plan unchanged, and finding a project by the system
      address and market id. SrvSurvey's source was read for the order of the calls.
    - Data that WFMT sends to Raven Colonial (progress, deliveries, carrier cargo, a new project, a primary project, a counted list, a
      completion) is opt-in, off by default, and listed in the privacy page.
  - **Code:** none copied.
- **Building costs** (Planned Builds window)
  - **Credit:** [SrvSurvey](https://github.com/njthomson/SrvSurvey) (`colonization-costs2.json`, GPL-3.0; notice in
    `THIRD-PARTY-NOTICES.md`), compiled by its author from the game.
  - **Use in WFMT:** the cost table is a copy of `colonization-costs2.json`.
  - **Code:** none taken.
- **Shopping list order** (overlay)
  - **Credit:** [SrvSurvey](https://github.com/njthomson/SrvSurvey) shopping overlay and `ColonyData.mapCargoType` (GPL-3.0; notice in
    `THIRD-PARTY-NOTICES.md`).
  - **Use in WFMT:** the list is alphabetical at a construction site and grouped under the market's categories elsewhere, with commodities
    the market does not sell dimmed. The category table (`plugin/commodity_categories.py`) is taken from `ColonyData.mapCargoType`.
  - **Code:** WFMT's own.
- **Where to buy a Colonization commodity**
  - **Credit:** [Spansh](https://spansh.co.uk/).
  - **Use in WFMT:** Spansh's station search, the same search used by the Mining and Trade finders.
  - **Code:** WFMT's own.

## Power, factions and combat

- **Massacre and kill-mission tracking**
  - **Credit:** [EDMC-Massacres](https://github.com/CMDR-WDX/EDMC-Massacres),
    [EDMC-CombatTracker](https://github.com/lunarplasma/EDMC-CombatTracker), [EDCarnage](https://github.com/mmomtchev/EDCarnage) and
    [EDMMC](https://github.com/tautomer/EDMMC).
  - **Use in WFMT:** reference for the Mission mode.
  - **Code:** none taken.
- **Powerplay merit tracking**
  - **Credit:** [EDMC-PowerPlayProgress](https://github.com/alby666/EDMC-PowerPlayProgress),
    [EliteMeritTracker](https://github.com/Fumlop/EliteMeritTracker),
    [EDMC Merit Tracker](https://gitlab.com/valdidan-edtools/edmc_merittracker) and BGS-Tally.
  - **Use in WFMT:** reference for the Powerplay mode.
  - **Code:** none taken.
- **Rare goods lookups**
  - **Credit:** EDMC-PowerPlayProgress, [Inara](https://inara.cz/) and rare-commodity guides.
  - **Use in WFMT:** the legality restrictions and each station's distance from its star in the Rare Goods Finder's list were curated by
    hand from Inara.
  - **Code:** none taken.
- **BGS tracking**
  - **Credit:** [BGS-Tally](https://github.com/aussig/BGS-Tally) and its forks,
    [EliteFactionTracker](https://github.com/Haelnorr/EliteFactionTracker) and other faction trackers.
  - **Use in WFMT:** reference for the BGS mode.
  - **Code:** none taken.
- **Megaship scans** (a count of the megaships scanned each Powerplay cycle, with name and system)
  - **Credit:** [ODEliteTracker](https://github.com/WarmedxMints/ODEliteTracker), whose BGS data store keeps the same list.
  - **Use in WFMT:** its source (no license is declared, so none of it is copied) was read for how it names the ship: the megaship
    dropped to just before the uplink scan. WFMT adds the merits each scan earned, a check that the destination is a megaship, and a
    journal back-fill, and was checked against real journals.
  - **Code:** WFMT's own.

## Engineering and Odyssey

Data was taken from several sources in this section. Each entry states what was taken and from where.

### Materials and blueprints

- **Engineering materials** (the quantity held of each Raw, Manufactured and Encoded material, with its grade and limit)
  - **Credit:** [Elite Dangerous Odyssey Materials Helper](https://github.com/jixxed/ed-odyssey-materials-helper) (source MIT),
    [EDEngineer](https://github.com/msarilar/EDEngineer) (MIT), EDDiscovery and **[EDCD/FDevIDs](https://github.com/EDCD/FDevIDs)**.
  - **Use in WFMT:** material names, types and grades come from FDevIDs' `material.csv` (see Data below).
  - **Code:** WFMT's own, built from the journal's events. None taken from the other projects.
- **Engineering blueprints** (what each blueprint requires and where the ingredients are found)
  - **Credit:** [EDEngineer](https://github.com/msarilar/EDEngineer) (MIT; notice in `THIRD-PARTY-NOTICES.md`),
    [Elite Dangerous Odyssey Materials Helper](https://github.com/jixxed/ed-odyssey-materials-helper),
    [EDDiscovery](https://github.com/EDDiscovery/EliteDangerousCore) (Apache-2.0; notice in `THIRD-PARTY-NOTICES.md`) and
    [EDSY](https://github.com/taleden/EDSY) (notice in `THIRD-PARTY-NOTICES.md`).
  - **Use in WFMT:**
    - The recipes and the "where found" text are a trimmed copy of EDEngineer's `blueprints.json` and `entryData.json`, compiled by its
      contributors from the game.
    - The Materials Helper informed the idea.
    - EDDiscovery's data corrected five synthesis recipes and supplied seven synthesis families and nine Thargoid-war and chip materials. EDDiscovery's engineer table is
      `plugin/engineers_data.py` (each engineer's location and how to find, be invited by and unlock them).
    - EDEngineer's data also records the Coriolis identifier of each grade, which the generated table of journal blueprint names uses.
    - EDSY's data (`eddb.js`, read on 2026-11-03) supplied 18 blueprints that EDEngineer's table, last changed 2024-03-07, lacks: their names, the materials of each grade and
      the module types each applies to, in `plugin/blueprints_edsy.py` (materials only: no engineers or effects, and no grade the source leaves empty). Its limits are stated in
      that file's header. EDSY's materials for the other recipes were compared with the table (712 grade recipes matched) and its ship classes were used to check the landing
      pads (the Lynx Highliner and the Anaconda Mk II).
  - **Code:** none taken. None of the data is from Frontier.

### Engineers

- **Engineer data**
  - **Credit:** EDCoPilot, [Elite Dangerous Odyssey Materials Helper](https://github.com/jixxed/ed-odyssey-materials-helper) (MIT),
    [edblackbox.com](https://edblackbox.com/guides/engineering/engineering-manuals/checklist.html), the community wiki,
    [Inara](https://inara.cz/) and EDDiscovery.
  - **Use in WFMT:**
    - The four Colonia on-foot engineers (Baltanos, Eleanor Bresa, Rosa Dayette and Yi Shen), absent from EDEngineer's table, are in
      WFMT's table. The suit and weapon upgrades each offers come from EDCoPilot's engineer list (read for facts only).
    - Yi Shen's three sets of referral items are game facts as stated in the Materials Helper's English text and in the engineering
      checklist on edblackbox.com.
    - The grade thresholds and net-profit figures for ship engineers are facts from the community wiki.
    - Yarden Bond's meeting requirement is five Smear campaign plans, as stated by the community wiki and Inara. EDDiscovery's table
      lists eight.
  - **Code:** none taken.

### Planners

- **Odyssey upgrade planner** (a suit's or weapon's upgrade and modifications as a wishlist)
  - **Credit:** [Elite Dangerous Odyssey Materials Helper](https://github.com/jixxed/ed-odyssey-materials-helper),
    [EDEngineer](https://github.com/msarilar/EDEngineer) (MIT) and [EDDI](https://github.com/EDCD/EDDI).
  - **Use in WFMT:** the idea follows the Materials Helper's loadout editor. Its stat tables are not public, and none of its data was
    taken. The upgrade costs are read from the game's `UpgradeSuit` and `UpgradeWeapon` journal events (game facts). The modification
    recipes are those of the blueprint table (EDEngineer). The journal names for suit and weapon modifications (`suit_nightvision`,
    `weapon_range`) and for weapons are the game's; EDDI's definitions and real journals agree on them. WFMT's own table maps them to the
    planner's names.
  - **Code:** none taken.
- **Ship engineering planner** (a ship's engineering as a wishlist)
  - **Credit:** [Elite Dangerous Odyssey Materials Helper](https://github.com/jixxed/ed-odyssey-materials-helper),
    [EDCD/coriolis-data](https://github.com/EDCD/coriolis-data) (names only; notice in `THIRD-PARTY-NOTICES.md`),
    [EDSY](https://edsy.org/), [Coriolis](https://coriolis.io/) (MIT) and [EDMC](https://github.com/EDCD/EDMarketConnector).
  - **Use in WFMT:** the idea follows the Materials Helper's ship builder and its wishlist import from EDSY and Coriolis. No data was
    taken from it, and WFMT's design uses the journal's `Loadout` shape. The journal's blueprint and effect names come from
    coriolis-data. EDSY and Coriolis are where a build is designed and exported (SLEF). The import links that WFMT reads and writes (the
    loadout as gzip and URL-safe base64 in a Coriolis import link or an EDSY `#/I=` link) use the format produced by EDMC's shipyard-link
    plugins and read by Coriolis.
  - **Code:** WFMT's own. None taken.
- **Odyssey inventory tracking**
  - **Credit:** EDMC (ship locker data), ED Recon and the Odyssey Materials Helper.
  - **Use in WFMT:** reference.
  - **Code:** none taken.

## Trade, missions and the ship

- **Best picks and Source commodities** (a short list of labeled stations for a commodity, and where to obtain the cargo a mission needs)
  - **Credit:** [EDCoPilot](https://www.edcopilot.com/) market search; [Spansh](https://spansh.co.uk/).
  - **Use in WFMT:** the idea of a short list of the best places to buy or sell follows EDCoPilot's market search. The stations come from
    Spansh's station search.
  - **Code:** WFMT's own. None taken.
- **Material trader finder**
  - **Credit:** [ODEliteTracker](https://github.com/WarmedxMints/ODEliteTracker); [Spansh](https://spansh.co.uk/).
  - **Use in WFMT:** ODEliteTracker's material trader finder informed the idea. The stations come from Spansh's station search, filtered
    by its material trader field.
  - **Code:** WFMT's own. None taken.
- **Landing pad guidance**
  - **Credit:** [LandingPad](https://github.com/bgol/LandingPad) and ED Recon.
  - **Use in WFMT:** reference.
  - **Code:** none taken.
- **Screenshot conversion and renaming**
  - **Credit:** EDMC's built-in screenshot handling and [EDMC-Screenshot](https://github.com/NoFoolLikeOne/EDMC-Screenshot).
  - **Use in WFMT:** reference.
  - **Code:** none taken.

## Overlays

WFMT has its own overlay on Windows and works with a separate overlay on Linux.

- **Built-in overlay**
  - **Credit:** [SrvSurvey](https://github.com/njthomson/SrvSurvey) overlay windows; Source Sans 3 (Adobe, SIL Open Font License 1.1).
  - **Use in WFMT:** the idea of an overlay that WFMT draws itself follows SrvSurvey's overlay windows. Source Sans 3 is the default font,
    bundled unmodified with its license (see `THIRD-PARTY-NOTICES.md`).
  - **Code:** WFMT's own. None taken from SrvSurvey.
- **Hiding the overlays**
  - **Credit:** [SrvSurvey](https://github.com/njthomson/SrvSurvey) overlay toggle.
  - **Use in WFMT:** the overlays can be switched off at a keystroke without leaving the game. WFMT provides a line in the WFMT panel, a
    **Hide / show now** button, a Windows hotkey and a chat command.
  - **Code:** WFMT's own. None taken.
- **Drag-and-drop layout editor on Overlay Placement**
  - **Credit:** none. A grid for placing overlay displays is common to overlay layout tools.
  - **Use in WFMT:** none.
  - **Code:** the editor (a to-scale picture of the screen with a box per display that snaps to edges and a grid) is WFMT's own design and
    code.
- **Color themes of the windows**
  - **Credit:** none.
  - **Use in WFMT:** the four themes (Navy, Cyan, Amber and Green) are the maintainer's own palettes.
  - **Code:** WFMT's own.
- **Overlay placement**
  - **Credit:** [SrvSurvey](https://github.com/njthomson/SrvSurvey) and [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay).
  - **Use in WFMT:** SrvSurvey places each overlay relative to the game window (left, center or right; top, middle or bottom; plus pixels),
    which is the model WFMT's Overlay Placement follows. EDMCModernOverlay's open source was used to check how it maps positions and sizes
    onto the screen.
  - **Code:** none taken.

### The two overlays

- **Windows: WFMT's own overlay.** It is built into WFMT, is WFMT's own code, and requires no other installation.
- **Linux: EDMCModernOverlay.** WFMT draws through the helper app
  **[SweetJonnySauce/EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay)**. The built-in overlay is Windows only, so
  this is the overlay on Linux. It can also be selected on Windows. WFMT communicates with it over its documented local protocol and ships
  none of its code. It is the user's own installation.

## Included data, and reusing WFMT

WFMT's code is its own. Some of its data tables (for example the building cost table, the engineering blueprint recipes and the commodity
category table) are trimmed copies or conversions of data that other projects published, and each is named in the entries above.
`THIRD-PARTY-NOTICES.md` names each source, its license and what was included, and contains the notices that licenses require. Where a
project is credited only for an idea or as a reference, the entry states so and no code was taken.

**Reusing WFMT's ideas and code.** The ideas in WFMT were drawn from the community, and WFMT's ideas and code may be reused in the same
way:

- **Ideas** may be taken freely. This covers how a feature works, how it looks and how the data is read. Several of WFMT's ideas are the
  community's, as the entries above state.
- **Code** is released under the GNU General Public License v3.0 (`LICENSE`). It may be copied, changed, improved and shared, including
  inside a tool that is sold. The license requires that distributed work is also under GPL-3.0 with its source available, and that the
  copyright and license notices stay with the reused code. These are the terms of the license, not additional terms.
- **Acknowledgement** of WFMT, such as a line in a README or credits, is welcome and is not required beyond those notices.
- **Included data tables** keep the license of the party that compiled them. A reused table must keep its notice from
  `THIRD-PARTY-NOTICES.md` and its source, so that credit reaches the compilers.
- **Not an official Frontier product.** WFMT is a fan-made tool, as is anything built from it.

This section is a summary. The license text in `LICENSE` is what applies.

## Host application, services and data

### Host application

**[EDMC](https://github.com/EDCD/EDMarketConnector)** (GPL-2.0) is the host. WFMT uses its plugin API and imports its `config`, `theme`
and `myNotebook` modules at runtime.

### Services

WFMT communicates with the following services:

- [EDSM](https://www.edsm.net/), [Spansh](https://spansh.co.uk/), [edastro.com](https://edastro.com/) (GEC), Canonn's published site lists
  and codex catalog, [Raven Colonial](https://ravencolonial.com/) (Colonization; opt-in or on a button press), `tick.infomancer.uk` (BGS
  tick; optional), GitHub Releases (self-update; opt-in) and Discord (only the user's own webhook, when a Post button is pressed).
- [Inara](https://inara.cz/), [Coriolis](https://coriolis.io/) and [EDSY](https://edsy.org/) are linked to only.
- Every network call goes to a documented API or a published data file, never to another site's HTML. Most calls are opt-in or
  user-triggered.
- The Rare Goods Finder's static list was compiled from public game data, with EDSM coordinates, Inara commodity ids and Spansh system ids
  looked up once (notice in `THIRD-PARTY-NOTICES.md`).

### Data

Game facts such as thresholds, names, coordinates and measured values (the exobiology and region tables, the pad layout, scan-value
constants, mining depletion figures and micro-resource names) come from the community's published work and from the game. Where a source's
license requires a notice, the notice is in `THIRD-PARTY-NOTICES.md`.

- Micro-resource and commodity names come from **[EDCD/FDevIDs](https://github.com/EDCD/FDevIDs)**.
- The landing-pad size of each ship (Trade mode) comes from **[EDCD/coriolis-data](https://github.com/EDCD/coriolis-data)**; the Lynx Highliner and the Anaconda Mk II, which that data lacks, from [EDSY](https://github.com/taleden/EDSY) and Frontier's own ship pages, as [Inara](https://inara.cz/) also lists them.
- Engineering material names, types and grades (Operations → Materials) come from FDevIDs' `material.csv`.

## Data gathering and verification

The game changes, and older data about it remains in circulation. Data is collected from available sources and kept current as follows.

- Other authors' published work is checked against the game by the project owner, used once verified, and credited here and in
  `THIRD-PARTY-NOTICES.md` with its license.
- Data that is not available as open data is measured in the game by the project owner. Each value is recorded with the game version, the
  date and a screenshot.
- A value that has not been checked in the game is marked as such.
- `docs/data_verification/verification_checklist.csv` lists every item that is missing or still to be checked, with its source and
  license, and shows which items have been verified in the game. Tables added before the checklist existed are included.
- WFMT contains no Odyssey suit or weapon stat values. Any that are added will be the owner's in-game measurements, or another author's
  published values that were checked in the game (`docs/ODYSSEY_STAT_COLLECTION.md`).
- Nothing was taken from any program's compiled files.

Published work that was used is credited on this page. A missing or incorrect credit can be reported as an issue and will be corrected.

WFMT's data is open under the project's license (GPL-3.0) and is not restricted further. Reuse is permitted. Acknowledgement of WFMT and
of the authors credited here is appreciated and not required.

## Supporting the tool authors

Third-party tools for Elite Dangerous are maintained by individual authors, and WFMT relies on several of them. Their projects, and where
they can be supported:

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

*Elite Dangerous* and related marks are trademarks of Frontier Developments plc. WFMT is a fan-made tool, not official Frontier software,
and is not affiliated with the EDMC team or any project above.
