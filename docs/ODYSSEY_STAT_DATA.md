# Odyssey stat data: where it might come from

Research note. The Upgrade planner ("Odyssey upgrade planner, next step" in [TODO.md](TODO.md)) would need a stat preview:

- each suit's and weapon's base stats
- what each class (1 to 5) changes
- what each modification changes

This note records where that data was looked for, what was found, and the license or terms of each source.

**No stat tables are in WFMT yet, and nothing was decompiled, disassembled or extracted from any program.**

## What is needed

- Per weapon and per suit: base values (damage per shot, rate of fire, magazine and reserve ammo, reload time, effective range, headshot
  multiplier, health, shields, speed and so on) and what each class 2 to 5 changes.
- Per modification: which stat it changes and by how much (for example "Greater Range" and "Magazine Size" on weapons; "Improved Battery
  Capacity" and "Increased Air Reserves" on suits).
- Preferably as a table that can be read as data (CSV or JSON), with a license that allows it to be used and credited in WFMT.

What WFMT already has:

- From the journal, the upgrade materials and credits that have been confirmed in play (`odyssey_upgrade_plan.py`).
- The journal has no stat values.

## Sources, and what each holds

No stat table with a license that allows reuse has been found. The kinds of source that were looked at:

| Kind of source | What it has | License or terms | Status |
|---|---|---|---|
| A community loadout tool | Stats of a suit or weapon at a class with chosen modifications. The values sit in components that are not in its public repository; the public repository has only the stat *names*. | Source code in the repository is open source. The official binaries are proprietary and their license forbids decompiling, reverse engineering and extracting data from them. | Not read from the binaries. |
| Open-source journal tools | Journal handling for `UpgradeWeapon`, `SellWeapon` and the like; weapon and suit internal names, types, manufacturers and base prices only. | Open source; check each repository's license before using anything from it. | Searched with GitHub code search. No stat tables. |
| Journal schema and parser projects | Names and event shapes (`UpgradeWeapon`, `SuitLoadout`, ...). | Not checked. | Not useful for stats. |
| Community wikis | Per-weapon figures (for example base damage per second, headshot multiplier, effective range, magazine and reserve ammo) and a magazine-size modification described as +50%. | Community wikis are normally CC BY-SA, which requires credit and share-alike; confirm on the page footer before use. | The pages could not be fetched, so **none of these numbers is verified**, and sources disagree in places (one post says the magazine modification multiplies rounds by 1.5, which does not match the wiki's own example). |
| Community web databases | Equipment blueprint pages list each modification with its effect (for example "Greater Range", +50% effective range) and the material and credit costs. | Terms not read; treat the content as not reusable until they are. | Pages could not be fetched when tried. |
| Frontier forums | Community tables of modification effects. | Forum posts belong to their authors; ask before reuse. | Fetch returned HTTP 403. |
| The game itself | The only primary source, but its files are not published as data, and its license restricts taking them apart. | Frontier's EULA. | Not attempted. |

Source and license: see docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md.

## Next steps

- To see everything that is missing or unverified in one place, import `docs/data_verification/verification_checklist.csv` into a spreadsheet ([instructions](data_verification/README.md)).
- To build the data set first-hand instead, follow [ODYSSEY_STAT_COLLECTION.md](ODYSSEY_STAT_COLLECTION.md). It covers:
  - what to record in the game
  - the blank templates in `docs/odyssey_stats/`
  - the license decision to make before filling anything in
- Where a source's numbers are wanted, read the pages in a browser, confirm the license of each, and record it in [ATTRIBUTIONS.md](ATTRIBUTIONS.md).
  - An open-source license on a repository's code does not cover proprietary components that hold the data.
- Whatever is obtained:
  - Check a sample of values against the in-game stat screens before shipping a preview.
  - Record in the docs which values were measured in the game and which came from a source.
