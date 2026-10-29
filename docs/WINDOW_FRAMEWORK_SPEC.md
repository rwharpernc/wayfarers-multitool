# WFMT Window Kit

The shared look and building blocks for every pop-out (Toplevel) window in WFMT: a consistent navy
palette, flat cards, striped sortable tables, and an embedded map. It lives in `plugin/uikit/`. The rules
that matter when changing a window are in [TECHNICAL.md](TECHNICAL.md) section 5; this page describes what
the kit provides and where it's used.

## 1. Scope

The kit covers external windows only. The main-window panels (`plugin_app`) are **not** part of it: they
follow EDMC's theme and must obey the width-bounding rules in TECHNICAL.md section 5.

Windows that use it: every pop-out window, dialog and the screenshot preview (the Mining Book and the Mining dialogs,
Powerplay Sessions, Rare Goods, Inventory, the BGS Report, Trade History, Codex Completionist, Ship Builds, the
Colonization windows, the Expedition window and the Exploration Dashboard, the Missions pop-ups and the rest).
Settings tabs are not converted, because they live inside EDMC's own preferences
window and follow its theme.

## 2. Hard rule: never touch ttk globally

ttk themes and stock styles (`TButton`, `Treeview` and so on) are application-wide, so changing them
would recolor EDMC's main window and every other plugin.

- The kit therefore uses classic tk widgets plus its own `FlatButton`, `Combobox`, `SlimScrollbar` and `tk.PanedWindow`.
- `style.skin(window)` colors a window's classic widgets through Tk's option database, scoped by that window's own name.
- `tests/test_ui_kit.py` fails if the kit touches the ttk theme or styles.

A consequence:

- ttk `Treeview` tables can only be restyled through a name-scoped style, and their headings stay native on Windows.
- Table-heavy windows therefore use the kit's own table instead.

## 3. Building blocks

- **Palette and tokens** (`palette.py`): navy background layers, text, accent, success, warning and danger
  colors, and three colors for headings and messages (`TITLE` gold for a window title, `HEADING` cyan for section labels and
  table column headers, `STATUS` for the footer message: a bright color of its own on each theme, yellow or cyan), plus a color-blind-safe set for status. Shape or a label carries the state, never color
  alone (the minimap markers work the same way).
- **Style** (`style.py`): applies the look to a window's classic widgets, and holds the shared text size (-2 to +6 points, changed by the footer's A- and A+ or Settings → General → Window). Fonts derive from
  `TkDefaultFont` so Linux and high-DPI displays behave.
- **Window shell** (`shell.py`): a singleton Toplevel with saved geometry, a minimum size, a header (title,
  subtitle, action buttons, a Help button), a status footer and Esc-to-close. `add_action(text, command, accent=False, tip=None)` and `add_menu(text, items, tip=None)` take the button's tooltip as `tip` (the Help button has its own). `TabShell` is the same shell for a window that
  lives in a tab of another window (the Expedition window's Plan, Route and Log tabs): its size and place are the host's. It never touches EDMC's config: the window
  passes it `load_geometry` and `save_geometry` callables. Windows are built hidden and shown once their
  content is laid out, so they never flash at a default size.
- **Widgets** (`widgets.py`, `table.py`): `Card`, `Pill` (status chip), `StatTile` and `TileRow`, `Row` (a selectable list row), `FlatButton`, `MenuButton` (a button that posts a menu), `Combobox`, `SuggestEntry` (a text box that suggests as you type, used for system and commodity names), `SlimScrollbar`, `ProgressBar`, `Tabs`, `FoldList`, `ScrollFrame`, `NoteLabel`, `field_grid` and `DataTable`.
  - `FlatButton(parent, text, command, kind="normal", tip=None)` and `MenuButton` take `tip`, the button's tooltip, written "Name - what it does" like the main panel's buttons. It may be a function returning the text, read each time the tooltip opens, for a button whose caption changes with its state. Every button in a window has one.
  - The tooltip itself is `add_tooltip` in `tooltip.py` (Tk only; `panelkit` re-exports it): a small borderless popup that appears when the pointer has rested on the widget for half a second and so cannot change the size of any window.
  - `Tabs` has an `on_select` callback so a window can redraw only the tab being shown, and `compact=True` for tabs nested inside a pane: smaller labels, the pane's color.
  - `FoldList` is a collapsible grouped list.
  - `NoteLabel` is a body-size note that spans the full width and re-wraps as the window is resized, for hints under a table.
  - `DataTable` is striped, sortable and optionally grouped, with an API like Treeview's, and header and body columns kept aligned.
  - A `DataTable` tag can set a row's text color and a whole-row background tint, which is lightened while hovered or selected.
  - `DataTable.set_rows` refills it and does nothing when the rows haven't changed, for windows that refresh often.
- **Forms** (`form.py`): `FormDialog` is the one add/edit form (hotspots, ship builds): labeled fields (text, system, choice, combo, commodity) under section headings, an error line, Save and Cancel, with `parse_optional_int` and `parse_optional_float` for the typed numbers.
- **Dialogs** (`dialogs.py`): `confirm` (Yes/No), `choose` (a row of buttons, for three-way questions), `prompt` (one line of text, optionally hidden as it is typed) and `info`, `warning` and `error`.
  - They are used instead of the operating system's own boxes so confirmations look and behave the same on Windows and Linux.
  - Each is modal over its parent window, opens centered over it, wraps its text at a fixed width and scrolls a very long message instead of growing.
  - Each returns its cancel value (False, None) rather than raising when it cannot open.
  - Esc cancels, Enter takes the default button.
  - `tests/test_no_native_dialogs.py` fails if a plugin module imports `tkinter.messagebox` or `simpledialog`.
- **Map canvas** (`mapview.py`): a `Canvas`-based map with zoom, hover and click-to-select, and dashed
  rings (`MapCircle`, the Mining Book's stops), used by the Mining Book. The fixed-size minimap image on the Surface Mining page is drawn separately.

Any window content that comes from outside data (Spansh names, file names) is truncated with a hard cap,
for the same discipline as the main panels.

## 4. The theme choice

WFMT's windows deliberately **do not follow EDMC's theme**. They use their own fixed navy look, which gives
every window a consistent feel and works the same on Linux. The cost is that it ignores a user's EDMC
theme choice. The palette is token-based: there are four themes (Navy, the default, and Cyan, Amber and Green after EDDDT), chosen under
Settings → General → Window or in a window's bottom line, and applied to open windows at once.

## 5. The Surface Mining Book layout

The Surface Mining Book has three resizable panes with saved geometry:

1. **Bodies:** the current system's scanned landable bodies plus every saved hotspot, grouped in a
   `FoldList`, with a material filter and a rig-count filter. It opens on the body you're at.
2. **Hotspots:** the selected body's hotspots grouped by location, with rigs, mined tons and the tons-left
   range, plus what *you've* found so far on that kind of ground.
3. **Detail and map:** a card for the selected hotspot (material, density and amount, estimate, notes,
   with Mark depleted, Copy coords, Share line, Edit and Delete) and a map of coverage and hotspots.

See [MINING_TECH_SPEC.md](MINING_TECH_SPEC.md) for the data behind it.

## 6. Display scaling and checking

Default and minimum window sizes are written in 96-dpi pixels and multiplied by `style.dpi_factor` inside
the shell, so keep new layouts expressed that way. Windows have been checked by screenshot at 100% and
150% scaling. Other scales and Linux still need checking, tracked in [LINUX_TESTING.md](LINUX_TESTING.md).
