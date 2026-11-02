# Odyssey stat data: sources reviewed

This page records where Odyssey suit and weapon stat data was searched for, what each source holds, and the license or terms that apply. The data is required for the stat preview listed under "Odyssey upgrade planner" in [TODO.md](TODO.md).

No stat tables are included in WFMT. No program was decompiled, disassembled or searched for data.

## Data required

- Per weapon and per suit: base values (damage per shot, rate of fire, magazine and reserve ammo, reload time, effective range, headshot multiplier, health, shields, speed) and the change at each class from 2 to 5.
- Per modification: the stat changed and the amount (for example "Greater Range" and "Magazine Size" on weapons; "Improved Battery Capacity" and "Increased Air Reserves" on suits).
- Preferred format: a table readable as data (CSV or JSON) under a license that permits use and credit in WFMT.

Data already in WFMT: the upgrade materials and credits confirmed in play (`odyssey_upgrade_plan.py`). The journal contains no stat values.

## Sources reviewed

No stat table under a license that permits reuse was found.

| Kind of source | Content | License or terms | Result |
|---|---|---|---|
| Community loadout tool | Stats of a suit or weapon at a class with chosen modifications. The values are in components that are not in its public repository, which holds only the stat names. | Repository source code is open source. The official binaries are proprietary and the license prohibits decompiling, reverse engineering and extracting data from them. | Not read from the binaries. |
| Open-source journal tools | Handling of `UpgradeWeapon`, `SellWeapon` and similar events; weapon and suit internal names, types, manufacturers and base prices. | Open source; the license of each repository applies. | Searched with GitHub code search. No stat tables. |
| Journal schema and parser projects | Names and event shapes (`UpgradeWeapon`, `SuitLoadout`). | Not checked. | No stat data. |
| Community wikis | Per-weapon figures (base damage per second, headshot multiplier, effective range, magazine and reserve ammo) and a magazine-size modification of +50%. | Community wikis are normally CC BY-SA; confirm on the page footer. | Pages could not be fetched. No value is verified. Sources disagree in places. |
| Community web databases | Blueprint pages listing each modification with its effect (for example "Greater Range", +50% effective range) and material and credit costs. | Terms not read. | Pages could not be fetched. |
| Frontier forums | Community tables of modification effects. | Posts belong to their authors. | Fetch returned HTTP 403. |
| The game | Primary source. Its files are not published as data. | Frontier EULA. | Not attempted. |

Sources and licenses are also listed in [ATTRIBUTIONS.md](ATTRIBUTIONS.md) and `THIRD-PARTY-NOTICES.md`.

## Related documents

- [data_verification/README.md](data_verification/README.md): the checklist of missing and unverified data.
- [ODYSSEY_STAT_COLLECTION.md](ODYSSEY_STAT_COLLECTION.md): the procedure for recording stat data in the game, including the blank templates in `docs/odyssey_stats/`.
- Values taken from a source are compared with the in-game stats screens before use, and the documentation states which values were measured in the game and which came from a source.
