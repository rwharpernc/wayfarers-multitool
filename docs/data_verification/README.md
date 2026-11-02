# Data verification checklist

`verification_checklist.csv` lists the data that WFMT carries, or would carry, that is missing or requires verification in the game, with its origin and license. `sheet_lists.csv` holds the status and priority value lists.

The method is stated under "Data" in [ATTRIBUTIONS.md](../ATTRIBUTIONS.md):

- Values are measured in the game by the project owner.
- Other authors' published values are reviewed, checked against the game, and used once verified, with credit.

The checklist was generated from the project's own tables and from [TODO.md](../TODO.md). It lists only data known to be unverified. A table that is not listed has not been audited.

## Columns

| Column | Meaning |
|---|---|
| `id` | Stable row number (`V-0001`). Rows are not renumbered; new rows are added at the bottom with the next number. |
| `status` | `Missing`: nothing recorded. `Needs verification`: a value exists and has not been checked in the game. `Verified - journal`: confirmed by journal events. `Verified - in game`: read in the game by the project owner. |
| `priority` | High, Medium or Low. |
| `area`, `item` | Where the data belongs and the specific item. Rows are sorted by area, then priority. |
| `what_to_check` | The value to inspect. |
| `current_value_in_wfmt` | The value WFMT carries, if any. |
| `value_from_source` | A value from a cited source that is not in WFMT (a candidate for verification). |
| `source`, `source_license`, `source_url` | Origin and license. "Confirm" in a license cell means the license was not checked. |
| `how_to_verify_in_game` | The verification steps. |
| `verified_value`, `verified_on`, `game_version`, `screenshot_ref` | Entered on verification: the value read, the date, the game version (the journal `Fileheader` event contains it) and the screenshot file name. |
| `notes` | Additional information, including disagreements between sources. |

## Import into Google Sheets

1. Choose File > Import > Upload and select `verification_checklist.csv`.
   - Set Import location to "Insert new sheet(s)" (or "Replace spreadsheet" for a new file).
   - Set Separator type to "Comma".
   - Clear "Convert text to numbers, dates, and formulas" so that values such as `1,875,000` and `+50%` remain as written.
2. Choose View > Freeze > 1 row and 2 columns, so that `id` and `status` stay visible.
   - Choose Data > Create a filter and filter by `area` or `status`.
3. Optional: import `sheet_lists.csv` into a second sheet.
   - Select the `status` column and choose Data > Data validation > Dropdown (from a range) with the status list as the range. Repeat for `priority`.
   - Choose Format > Conditional formatting by `status` to color the rows.
4. Widen `what_to_check`, `how_to_verify_in_game` and `notes` and set them to wrap text.

## Procedure

1. Process High-priority rows first, then the Odyssey stat rows ([ODYSSEY_STAT_COLLECTION.md](../ODYSSEY_STAT_COLLECTION.md) describes how to record them).
2. After checking a row, set `status` to `Verified - in game` and fill in the verified columns.
   - If the game differs from WFMT or the source, record the difference in `notes`.
3. A value from a source keeps the status `Needs verification` until it has been read in the game.
4. Transfer the checked values to the repository. Odyssey values go to `docs/odyssey_stats/base_stats.csv` and `docs/odyssey_stats/mod_effects.csv`.
   - Credit the source of any value that originated as another author's published data. See the license section of [ODYSSEY_STAT_COLLECTION.md](../ODYSSEY_STAT_COLLECTION.md).
