# WFMT Window Kit

Technical specification of the shared look and building blocks of WFMT's pop-out (Toplevel) windows, located in `plugin/uikit/`. The rules for changing a window are in [TECHNICAL.md](TECHNICAL.md) section 5.

## 1. Scope

- The kit covers external windows only: pop-out windows, dialogs and the screenshot preview (for example the Mining Book and Mining dialogs, Powerplay Sessions, Rare Goods, Inventory, the BGS Report, Trade History, Codex Completionist, Ship Builds, the Colonization windows, the Expedition window, the Exploration Dashboard and the Missions pop-ups).
- The main-window panels (`plugin_app`) are not part of the kit. They follow EDMC's theme and must obey the width-bounding rules in TECHNICAL.md section 5.
- Settings tabs are not part of the kit; they are built inside EDMC's preferences window.

## 2. Rule: no global ttk changes

ttk themes and stock styles (`TButton`, `Treeview` and others) are application-wide. Changing them would recolor EDMC's main window and every other plugin.

- The kit uses classic tk widgets plus its own `FlatButton`, `Combobox`, `SlimScrollbar` and `tk.PanedWindow`.
- `style.skin(window)` colors the classic widgets of a window through Tk's option database, scoped by the window's own name.
- `tests/test_ui_kit.py` (`test_kit_never_touches_global_ttk`) fails when the kit source contains `theme_use(`, `ttk.Style`, `style.configure(`, `style.map(` or `from tkinter import ttk`.
- Tables use the kit's own `DataTable` instead of ttk `Treeview`.

## 3. Building blocks

### Palette and tokens (`palette.py`)

- Tokens: background layers (`BG`, `PANE`, `CARD`, `BUTTON`, `HOVER`, `SELECT`, `LINE`, `STRIPE`), text (`TEXT`, `MUTED`, `FAINT`), accent (`ACCENT`, `ACCENT_HI`, `ACCENT_INK`), status colors (`INFO`, `OK`, `WARN`, `DANGER`), row tints (`ROW_OK`, `ROW_OVER`, `ROW_HAUL`) and map colors (`MAP_*`).
- Three tokens for headings and messages: `TITLE` (window title), `HEADING` (section labels and table column headers) and `STATUS` (footer message; a bright color defined per theme).
- Three fixed row colors for the Engineers tab, identical on every theme: `ENGINEER_UNLOCKED`, `ENGINEER_PROGRESS`, `ENGINEER_UNAVAILABLE`.
- State is conveyed by shape or a label, in addition to color (the minimap markers follow the same rule).

### Style (`style.py`)

- Applies the look to the classic widgets of a window.
- Holds the shared text size: a delta from -2 to +6 points (`TEXT_DELTA_MIN`, `TEXT_DELTA_MAX`), changed by the footer buttons **A−** and **A+** or in Settings → General → Window. The value is stored under `wfmt_window_text_delta`.
- Fonts derive from `TkDefaultFont`. `style.font(spec, scaled=False)` returns a font that ignores the text size setting.
- `style.dpi_factor(widget)` returns the display scaling factor. `style.grab_when_visible(window)` grabs input after the window is mapped.

### Window shell (`shell.py`)

- `WindowShell` is a Toplevel with saved geometry, a minimum size, a header (title, subtitle, action buttons and a Help button), a status footer and the footer text-size buttons. The window is created withdrawn and is shown after its content is laid out.
- The initial position is chosen by `placement.py`: the remembered position while it is on a monitor, otherwise over EDMC's window on EDMC's monitor. The Settings option "Always open WFMT's windows on EDMC's monitor" applies the EDMC monitor every time.
- `add_action(text, command, accent=False, tip=None)` and `add_menu(text, items, tip=None)` add header buttons; `tip` is the tooltip. `add_help(title, items)` adds the Help button, which opens a window of short entries and raises the existing window if it is already open; Esc closes the Help window.
- `TabShell` provides the same interface for a window that lives in a tab of another window (the Plan, Route and Log tabs of the Expedition window). Its size and position belong to the host. It does not access EDMC's configuration; the window passes `load_geometry` and `save_geometry` callables.

### Widgets (`widgets.py`, `table.py`, `tooltip.py`)

| Widget | Description |
|---|---|
| `Card` | Flat container. |
| `Pill` | Status chip. |
| `StatTile`, `TileRow` | Figure tiles and a row of them. |
| `Row` | Selectable list row. |
| `FlatButton(parent, text, command, kind="normal", tip=None)` | Flat button; `kind` is `normal`, `accent` or `danger`. `tip` is the tooltip text, written "Name - what it does", or a function returning the text (read each time the tooltip opens). |
| `MenuButton` | `FlatButton` that posts a menu; takes `tip`. |
| `Combobox` | Kit combo box. |
| `SuggestEntry` | Text box that suggests values while typing; used for system and commodity names. |
| `SlimScrollbar` | Scrollbar. |
| `ProgressBar` | Progress bar. |
| `Tabs` | Tab bar with an `on_select` callback (redraw only the selected tab) and `compact=True` for tabs nested inside a pane (smaller labels, the pane's color). |
| `FoldList` | Collapsible grouped list of selectable rows. |
| `ScrollFrame` | Scrollable frame. |
| `NoteLabel` | Body-size note that spans the full width and re-wraps when the window is resized. |
| `field_grid` | Label and value grid. |
| `DataTable` | Striped, sortable, optionally grouped table with header and body columns kept aligned. A tag can set a row's text color and a whole-row background tint, which is lightened while hovered or selected. `set_rows` refills the table and does nothing when the rows are unchanged. |

- `add_tooltip` (`tooltip.py`) shows a borderless popup after the pointer rests on the widget for 500 ms (`TOOLTIP_DELAY_MS`). The popup does not change the size of any window. `panelkit` re-exports it.
- Window content from external data (Spansh names, file names) is truncated with a hard cap (`widgets.clip`).

### Forms (`form.py`)

`FormDialog` is the add/edit form (hotspots, ship builds). It provides labeled fields (text, system, body, ship, choice, combo, commodity) under section headings, an error line, Save and Cancel. System, body, ship and commodity fields suggest values while typing from `system_autocomplete`, `name_suggestions` and `commodity_autocomplete`. `parse_optional_int` and `parse_optional_float` parse typed numbers.

### Dialogs (`dialogs.py`)

| Function | Purpose |
|---|---|
| `confirm` | Yes/No. |
| `choose` | A row of buttons, for questions with more than two answers. |
| `prompt` | One line of text, optionally hidden while typed. |
| `info`, `warning`, `error` | Messages. |

- The dialogs replace the operating system's message boxes so that confirmations look and behave identically on Windows and Linux. `tests/test_no_native_dialogs.py` fails when a plugin module imports `tkinter.messagebox` or `simpledialog`.
- Each dialog is modal over its parent, is centered over it, wraps the message at 480 pixels (`MAX_WIDTH`) and scrolls a very long message.
- Esc cancels and Enter selects the default button. A dialog that cannot open returns its cancel value (False, None).

### Map canvas (`mapview.py`)

`MapView` is a `Canvas`-based map with zoom, hover and click-to-select. `MapMarker` and `MapCircle` (dashed rings; the Mining Book's stops) are its items. The Mining Book uses it.

## 4. Theme

- WFMT windows use their own fixed palette and do not follow EDMC's theme.
- The palette is token-based. Four themes exist: Navy (default), Cyan, Amber and Green. The theme is chosen in Settings → General → Window or in a window's bottom line and is applied to open windows immediately.
- The rationale for the fixed palette and the theme mechanism is in [DESIGN_NOTES.md](DESIGN_NOTES.md) sections 3.25 to 3.27.

## 5. Surface Mining Book layout

The Mining Book (`mining_ledger.py`) uses a `tk.PanedWindow` with three resizable panes and saved geometry.

1. Bodies: a `FoldList` of bodies with a material filter and a rig-count filter.
2. Hotspots: a `FoldList` of the selected body's hotspots grouped by location.
3. Detail and map: a card for the selected hotspot with the buttons **Mark depleted**, **Copy coords**, **Share line**, **Edit** and **Delete**, and a map.

The data behind the window is described in [MINING_TECH_SPEC.md](MINING_TECH_SPEC.md).

## 6. Display scaling

Default and minimum window sizes are expressed in 96-dpi pixels and multiplied by `style.dpi_factor` inside the shell. New layouts are expressed the same way. Display scaling and Linux checks are tracked in [LINUX_TESTING.md](LINUX_TESTING.md).
