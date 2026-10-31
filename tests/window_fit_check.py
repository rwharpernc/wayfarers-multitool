"""Layout checker for the pop-out windows built on the window kit (plugin/uikit). A helper for the `window_fit_*_smoke.py` scripts, not a test
by itself.

`check_window(root, top, width, height)` resizes a built window, lets Tk lay it out, then walks the widget tree and returns a list of findings,
each a (kind, text) pair. The kinds that fail a smoke test:

  clipped  a Label, Button, Entry or Checkbutton that is mapped but allocated less than it asks for (text or a control cut off)
  outside  a widget whose right or bottom edge lies beyond its toplevel, its parent or the scroll area that holds it (pushed off-screen)
  wrap     a label that holds more text than fits its parent without wrapping (wraplength 0), or whose wraplength is wider than its parent
  table    a DataTable whose columns need more width than it has, or (at a wide size) whose columns stop short of the right edge

and two that are only reported:

  note     a DataTable cell cut at its column's character cap while the column has room for the whole text
  text     a Text widget holding what looks like unwrapped columns of results, where a DataTable would belong

`install_edmc_stubs()` stands in for the modules EDMC provides, the same way the other smoke scripts do, and returns the dict the stand-in config
saves to. `sizes(top)` gives the (narrow, wide) sizes to check a window at."""
from __future__ import annotations

import re
import sys
import tkinter as tk
import tkinter.font as tkfont
import types
from typing import List, Optional, Tuple
from unittest import mock

SLACK = 3                  # pixels of difference that are rounding, not clipping
WIDE = 1600                # the wide size, or the screen's width when that is smaller
TABLE_DEAD_AREA = 40       # pixels a wide table may stop short of its right edge
FAIL_KINDS = ("clipped", "outside", "wrap", "table", "tip")
_CONTROLS = ("Label", "Button", "Entry", "Checkbutton")

Finding = Tuple[str, str]

# Long data for the windows' fixtures.
STATION = "Hephaestus Mining and Refining Industrial Settlement Alpha"       # 60 characters
SYSTEM = "Eorgh Prou JH-V d2-5 B 12 a Eorgh Prou JH-V d2-5 B 12 a"[:40]        # a procedural-style name, 40 characters
NOTE = ("Remember to check the long procedural system names against the carrier's cargo manifest before the next jump, and never "
        "leave the hold full of limpets when docking")[:120]               # 120 characters
COMMANDER = "CMDR Bocheaux Wayward Nomad"[:24]                              # 24 characters
BIG = 12_345_678_901


def install_edmc_stubs() -> dict:
    """The stand-ins for the modules EDMC provides. Returns the dict the stand-in config saves to."""
    class Any(types.ModuleType):
        def __getattr__(self, name):
            if name.startswith("__"):
                raise AttributeError(name)
            return mock.MagicMock()

    for name in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process",
                 "win32clipboard", "pywintypes", "psutil", "ttkHyperlinkLabel"):
        sys.modules[name] = Any(name)
    notebook = Any("myNotebook")
    notebook.Frame, notebook.Label, notebook.Button, notebook.Checkbutton = tk.Frame, tk.Label, tk.Button, tk.Checkbutton
    sys.modules["myNotebook"] = notebook
    theme = Any("theme")
    theme.theme = mock.MagicMock()
    theme.theme.active = None
    theme.theme.THEME_DEFAULT = 0
    sys.modules["theme"] = theme
    saved: dict = {}
    sys.stdout.reconfigure(errors="backslashreplace")   # a finding can quote a table's arrow or an ellipsis

    class Cfg:
        default_journal_dir = ""

        def get_str(self, key, default=""):
            return saved.get(key, default) or ""

        def get_bool(self, key, default=False):
            return saved.get(key, default)

        def get_int(self, key, default=0):
            return saved.get(key, default)

        def get(self, key, default=None):
            return saved.get(key, default)

        def set(self, key, value):
            saved[key] = value

    module = types.ModuleType("config")
    module.appname = "EDMarketConnector"
    module.config = Cfg()
    module.user_agent = "WFMT-test"
    module.appversion = lambda: "5.13.0"
    sys.modules["config"] = module
    return saved


def pump(root: tk.Misc, rounds: int = 4) -> None:
    for _ in range(rounds):
        root.update_idletasks()
        root.update()


def resize(root: tk.Misc, top: tk.Toplevel, width: int, height: int) -> Tuple[int, int]:
    """Ask for a size, let Tk settle, and return the size the window actually has (it refuses to go below its minimum)."""
    top.geometry(f"{width}x{height}+10+10")
    pump(root)
    return top.winfo_width(), top.winfo_height()


def sizes(root: tk.Misc, top: tk.Toplevel) -> List[Tuple[str, int, int]]:
    """The sizes to check at: the window's own minimum, 640 px wide when the minimum is larger (the shell refuses, which is fine), and wide."""
    min_w, min_h = top.wm_minsize()
    wide_w = min(WIDE, root.winfo_screenwidth())
    wide_h = max(min_h, min(900, root.winfo_screenheight() - 80))
    found = [("narrow", min_w, min_h)]
    if min_w > 640:
        found.append(("640", 640, min_h))
    found.append(("wide", max(wide_w, min_w), wide_h))
    return found


def check_window(root: tk.Misc, top: tk.Toplevel, width: int, height: int, wide: Optional[bool] = None) -> List[Finding]:
    """Resize `top` and report what is cut off, pushed outside or left unused. `wide` says whether to check that tables fill the width
    (default: when `width` is at least 1200)."""
    resize(root, top, width, height)
    if wide is None:
        wide = width >= 1200
    findings: List[Finding] = []
    _walk(top, top, findings, wide)
    return findings


def failures(findings: List[Finding]) -> List[Finding]:
    return [f for f in findings if f[0] in FAIL_KINDS]


def describe(widget: tk.Misc) -> str:
    name = widget.winfo_class() + " " + str(widget)
    for option in ("text", "textvariable"):
        try:
            value = widget.cget(option)
        except tk.TclError:
            continue
        if option == "textvariable" and value:
            try:
                value = widget.getvar(str(value))
            except tk.TclError:
                value = ""
        if value:
            text = str(value).replace("\n", " ")
            return f'{name} "{text[:40]}"'
    return name


def _visible(widget: tk.Misc) -> bool:
    try:
        return bool(widget.winfo_viewable())
    except tk.TclError:
        return False


def _walk(widget: tk.Misc, top: tk.Toplevel, findings: List[Finding], wide: bool) -> None:
    from plugin.uikit.table import DataTable

    for child in widget.winfo_children():
        if isinstance(child, tk.Toplevel):
            continue                       # a Help or detail window is not part of this one
        if not _visible(child):
            continue
        if isinstance(child, DataTable):
            _check_table(child, top, findings, wide)
            continue                       # its cells are judged as a table
        _check_widget(child, top, findings)
        _walk(child, top, findings, wide)


def _ancestors(widget: tk.Misc) -> List[tk.Misc]:
    found = []
    node = widget.master
    while node is not None:
        found.append(node)
        node = node.master
    return found


def _check_widget(widget: tk.Misc, top: tk.Toplevel, findings: List[Finding]) -> None:
    cls = widget.winfo_class()
    width, height = widget.winfo_width(), widget.winfo_height()
    if cls in _CONTROLS:
        if widget.winfo_reqwidth() - width > SLACK:
            findings.append(("clipped", f"{describe(widget)} asks for {widget.winfo_reqwidth()}px wide and gets {width}px"))
        elif widget.winfo_reqheight() - height > SLACK:
            findings.append(("clipped", f"{describe(widget)} asks for {widget.winfo_reqheight()}px high and gets {height}px"))
    _check_tip(widget, findings)
    _check_bounds(widget, top, findings)
    if cls == "Label":
        _check_wrap(widget, findings)
    elif cls == "Text":
        _check_text(widget, findings)


def _check_tip(widget: tk.Misc, findings: List[Finding]) -> None:
    """Every button in a window has a tooltip ("Name - what it does"): a FlatButton (or MenuButton) built without one is reported."""
    from plugin.uikit.widgets import FlatButton

    if isinstance(widget, FlatButton) and not getattr(widget, "_has_tooltip", False):
        findings.append(("tip", f"{describe(widget)} has no tooltip"))


def _check_bounds(widget: tk.Misc, top: tk.Toplevel, findings: List[Finding]) -> None:
    right = widget.winfo_rootx() + widget.winfo_width()
    bottom = widget.winfo_rooty() + widget.winfo_height()
    # A scroll area scrolls vertically, so only its right edge limits what is inside it.
    scrolled = any(node.winfo_class() == "Canvas" for node in _ancestors(widget))
    for node in _ancestors(widget):
        limit_right = node.winfo_rootx() + node.winfo_width()
        limit_bottom = node.winfo_rooty() + node.winfo_height()
        if not (node.winfo_class() == "Canvas" or node is top or node is widget.master):
            continue
        if right - limit_right > SLACK:
            findings.append(("outside", f"{describe(widget)} ends {right - limit_right}px beyond the right edge of {node.winfo_class()} {node}"))
            return
        if not scrolled and bottom - limit_bottom > SLACK and widget.winfo_height() > 1:
            findings.append(("outside", f"{describe(widget)} ends {bottom - limit_bottom}px below the bottom edge of {node.winfo_class()} {node}"))
            return


def _longest_line(widget: tk.Misc, text: str) -> int:
    font = tkfont.nametofont(str(widget.cget("font")))
    return max((font.measure(line) for line in text.split("\n")), default=0)


def _check_wrap(widget: tk.Misc, findings: List[Finding]) -> None:
    try:
        text = str(widget.cget("text"))
        wrap = int(float(str(widget.cget("wraplength"))))
    except (tk.TclError, ValueError):
        return
    if not text or "\n" not in text and len(text) < 20:
        return
    parent_width = widget.master.winfo_width()
    needed = _longest_line(widget, text)
    if wrap <= 0 and needed > parent_width + SLACK:
        findings.append(("wrap", f"{describe(widget)} needs {needed}px on one line, wraplength is 0 and its parent is {parent_width}px"))
    elif wrap > parent_width + SLACK and widget.winfo_reqwidth() > parent_width + SLACK:
        findings.append(("wrap", f"{describe(widget)} wraps at {wrap}px but its parent is {parent_width}px wide"))


_ALIGNED = re.compile(r"\S {2,}\S|\t")


def _check_text(widget: tk.Misc, findings: List[Finding]) -> None:
    try:
        content = widget.get("1.0", "end-1c")
        wrap = str(widget.cget("wrap"))
    except tk.TclError:
        return
    lines = [line for line in content.split("\n") if line.strip()]
    aligned = sum(1 for line in lines if _ALIGNED.search(line))
    if len(lines) >= 4 and (aligned >= 4 or wrap == "none"):
        findings.append(("text", f"{describe(widget)} holds {len(lines)} lines of {'aligned columns' if aligned >= 4 else 'unwrapped text'} (wrap={wrap})"))


def _name(table: tk.Misc) -> str:
    return "table[" + ",".join(c.key for c in table._columns[:4]) + ("..." if len(table._columns) > 4 else "") + "]"


def _check_table(table: tk.Misc, top: tk.Toplevel, findings: List[Finding], wide: bool) -> None:
    _check_bounds(table, top, findings)
    headers = table._header_labels
    font = tkfont.nametofont(str(headers[0].cget("font"))) if headers else None
    from plugin.uikit.table import INDENT
    # A column that needs more than it was given: the grid shrinks it and the text is cut.
    for index, column in enumerate(table._columns):
        cells = [row.cells[index] for row in table._rows.values() if index < len(row.cells) and row.cells[index].winfo_viewable()]
        if not cells:
            continue
        need = max([headers[index].winfo_reqwidth()] + [cell.winfo_reqwidth() for cell in cells])
        got = min(cell.winfo_width() for cell in cells)
        if need - got > SLACK:
            findings.append(("table", f"{_name(table)} column '{column.key}' needs {need}px and gets {got}px"))
        # Text cut at the character cap while the column has room for all of it.
        room = max(cell.winfo_width() for cell in cells)
        for row in table._rows.values():
            if index >= len(row.cells) or not row.cells[index].winfo_viewable():
                continue
            shown = str(row.cells[index].cget("text"))
            full = row.values[index] if index < len(row.values) else ""
            if shown != full and shown.endswith("…") and font is not None:
                body_font = tkfont.nametofont(str(row.cells[index].cget("font")))
                # The first column also carries a group's arrow or a child row's indent (DataTable._cell_text).
                lead = "▾  " if row.group and index == 0 else INDENT if row.parent is not None and index == 0 else ""
                if body_font.measure(lead + full) + 16 <= room:
                    findings.append(("note", f"{_name(table)} column '{column.key}' cuts \"{full[:30]}...\" ({len(full)} characters) at {column.max_chars} "
                                             f"although the column is {room}px wide"))
                    break
    if headers and wide:
        header = table._header
        used = max(label.winfo_x() + label.winfo_width() for label in headers)
        dead = header.winfo_width() - used
        if dead > TABLE_DEAD_AREA:
            findings.append(("table", f"{_name(table)} leaves {dead}px unused at the right of a {header.winfo_width()}px table (no column stretches)"))


def report(label: str, findings: List[Finding]) -> List[str]:
    return [f"{label}: {kind}: {text}" for kind, text in findings]


def tab_views(tabs: tk.Misc, titles: Optional[List[str]] = None) -> List[Tuple[str, object]]:
    """(name, select) for each shown tab of a `Tabs`, for `check_views`."""
    views = []
    for index, (label, _underline, _content) in enumerate(tabs._tabs):
        if tabs._visible[index]:
            views.append((str(label.cget("text")).title(), lambda i=index: tabs.select(i)))
    return views


def check_views(root: tk.Misc, top: tk.Toplevel, label: str, views: Optional[List[Tuple[str, object]]] = None,
                problems: Optional[List[str]] = None, notes: Optional[List[str]] = None) -> None:
    """Check `top` at each size in `sizes()`, once per view (a tab, say; `select()` shows it). Failures go to `problems`, reported
    findings to `notes`. A window with no tabs passes no views."""
    views = views or [("", lambda: None)]
    narrow = None
    for size_name, width, height in sizes(root, top):
        if size_name == "640":
            if resize(root, top, width, height)[0] >= narrow:
                continue                   # the window refused to go narrower than its minimum, so this is the narrow size again
        elif narrow is None:
            narrow = width
        for view_name, select in views:
            select()
            found = check_window(root, top, width, height)
            where = f"{label}{' / ' + view_name if view_name else ''} @ {size_name}"
            seen = set()
            for kind, text in found:
                line = f"{where}: {kind}: {text}"
                if line in seen:
                    continue
                seen.add(line)
                if kind in FAIL_KINDS:
                    if problems is not None:
                        problems.append(line)
                elif notes is not None:
                    notes.append(line)
