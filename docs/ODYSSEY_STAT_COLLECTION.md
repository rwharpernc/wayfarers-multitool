# Collecting Odyssey stat data in the game

This page describes the procedure for recording Odyssey suit and weapon stats in the game, the files the data is recorded in, and the checks applied to it. The data is required for the stat preview of the Upgrade planner. The sources already reviewed are listed in [ODYSSEY_STAT_DATA.md](ODYSSEY_STAT_DATA.md).

## Statement of method

The data comes from two origins:

- Values measured in the game by the project author, each with the game version, the date and a screenshot.
- Other authors' published work, which is reviewed, checked against the game, and used once verified, with the original authors credited.

A value not checked in the game is marked as such. The checklist in [data_verification/](data_verification/README.md) records what has and has not been verified.

## License and acknowledgement

- WFMT is licensed under the GNU GPL v3.0. The data collected here is licensed on the same terms.
- Acknowledgement is requested from anyone who reuses the data: credit to the project and, through it, to the authors whose published work was checked against.
- The GPL requires that copyright and license notices accompany the data.
- A specific attribution requirement, such as CC BY 4.0 for the data files, would be decided by the copyright holder.
- Where a value came from a cited source, the source and its license are named in the checklist, in [ATTRIBUTIONS.md](ATTRIBUTIONS.md) and, where the license requires a notice, in `THIRD-PARTY-NOTICES.md`.

## Files

The files are in `docs/odyssey_stats/` (the wider checklist is in `docs/data_verification/`). Each is comma-separated with one value per row.

| File | Content |
|---|---|
| `coverage.csv` | The checklist of items to record: 70 `base` rows (every suit and weapon at each class) and 163 `modification` rows (every item and modification the Upgrade planner knows). Columns: `part`, `kind`, `item`, `class`, `modification`, `done_on`, `notes`. Enter the date in `done_on` when a row is finished. |
| `base_stats.csv` | One row per stat shown for an item at a class. Columns: `kind` (Suit or Weapon), `item`, `class` (1 to 5), `stat_name`, `value`, `unit`, `screen`, `game_version`, `measured_on`, `screenshot_ref`, `notes`. `stat_name`, `value` and `unit` are entered as the game shows them. |
| `mod_effects.csv` | One row per stat a modification changes. Columns: `kind`, `item`, `class`, `modification`, `stat_name`, `value_before`, `value_after`, `unit`, `screen`, `game_version`, `measured_on`, `screenshot_ref`, `notes`. |

The source of any value not measured directly is recorded in `notes`. A value from another author's work remains unverified until it is read in the game.

## Procedure

### Preparation

1. Note the game version. The first line of each journal file (`Fileheader`) contains `gameversion` and `build`. Enter it in `game_version` on every row.
2. Record base stats for every item at the classes available, then record modifications.
3. Take a screenshot of the stats screen for every reading and enter its file name in `screenshot_ref`. Keep the screenshots with the data files, outside this repository.

### Base stats (one item at one class)

1. Open the screen that shows the item's stats (the screen used to buy, equip or upgrade it). Enter its name in `screen`.
2. Record every stat the screen lists as one row each, using the game's wording for `stat_name` and its units.
   - If a value is shown as a bar without a number, record the readable position and state this in `notes`.
3. After an upgrade, record the same item at the next class.
   - If the upgrade screen previews the next class's stats, record the preview and enter `preview` in `notes`. Otherwise read the item after the upgrade.
   - The Upgrade planner shows the materials and credits of each upgrade, and its **Add to wishlist** button adds the materials to the wishlist.
4. Compare the class with the journal where possible. `SuitLoadout` and `UpgradeWeapon` events name the item and class.

### Modifications (one modification on one item)

1. Check the cost in the Upgrade planner before fitting a modification.
2. If the modification screen previews the change, record the stat before and after from the preview and enter `preview` in `notes`. Otherwise record the item's stats screen before fitting and after fitting. The difference is the effect.
3. Record one row per changed stat. Enter the item's class in `class`, because an effect can depend on it.
4. To determine whether an effect is a percentage or a fixed amount, measure the same modification on two different items (for example Magazine size on a Karma AR-50 and on a Manticore Executioner) and enter the result in `notes`.
5. A modification whose name carries a family in brackets, such as "Greater range (Kinematic kinetic)", applies to that family only. Test it on one weapon of that family.

## Verification of recorded data

- Surprising values are read a second time on another day or from a second screen. Both readings are noted.
- Consistency checks applied to a table:
  - Values rise (or fall, for times) in steps from class 1 to 5.
  - A modification's "after" value differs from the "before" value in the direction its name states.
  - Two items of one family lie in the same range.
- A previewed magazine size is compared with the ammo counter on screen. A reload time is compared with a stopwatch.
- A missing value is left blank. It is not estimated.
- If a game update changes a value, the new reading is added as a new row with the new game version. The old row is not overwritten.
