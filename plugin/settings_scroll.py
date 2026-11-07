"""A Settings page that scrolls instead of growing taller than the screen.

EDMC sizes its Settings window to the tallest page in every plugin's notebook. A long WFMT page (Mining,
Exploration > Alerts, ...) used to push the window past the bottom of the screen, taking the OK button with it.
`scrolled_page` wraps one page in a canvas with a scrollbar and caps the canvas at `height_cap`; a page shorter
than the cap looks exactly as it did before (no scrollbar, no extra space).

Each feature's `build_settings(notebook)` is unchanged: it is handed a `ScrollContent`, which accepts
`add(frame, text=...)` like a notebook does, and the finished page is added to the real notebook.
Widgets inside are only ever placed with `grid` (never `pack` into an nb.Frame; see tests/test_settings_layout.py).

Descriptive text uses the whole width of the page. A page's labels are written with a fixed `wraplength` (a width for the first draw), but the Settings window is
wider than that, so left alone the text would stay a narrow column on the left. `ScrolledPage.fit_text` re-wraps every label that has a row to itself to the width
the page really has, whenever the page is resized, so no description is ever shorter than the page (see tests/test_settings_text_width.py).
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

import myNotebook as nb

MIN_CAP = 260           # never shorter than this, so a small screen still shows a usable page
MAX_CAP = 640           # never taller than this, so a huge screen doesn't get an enormous page
CHROME_ALLOWANCE = 530  # window title, EDMC's own tabs, our two tab bars (the Overlays group wraps to three rows), the version line and the OK/Cancel row
_SKIP_WHEEL = {"Listbox", "Text", "Treeview", "TCombobox"}  # these scroll themselves
MIN_TEXT_WIDTH = 200    # a description never wraps narrower than this, whatever the page's width
TEXT_MARGIN = 24        # room kept at the right of a description (the page's padding and the scrollbar's edge)


def height_cap(screen_height: int) -> int:
    """The tallest a page's visible area may be on a screen this tall."""
    return max(MIN_CAP, min(MAX_CAP, screen_height - CHROME_ALLOWANCE))


class ScrollContent(nb.Frame):
    """What a feature's `build_settings` receives in place of a notebook. Its `add` stacks the frames it is given
    (with a rule between them if there is more than one) and, on the first call, adds the scrolling page to the
    real notebook under the same tab options."""

    def __init__(self, page: "ScrolledPage", canvas: tk.Canvas) -> None:
        super().__init__(canvas)
        self._page = page
        self.columnconfigure(0, weight=1)
        self._next_row = 1  # row 0 is nb.Frame's own gridded spacer

    def add(self, child: tk.Misc, **options: Any) -> None:
        if self._next_row > 1:
            ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=self._next_row, column=0, sticky=tk.EW, padx=10, pady=4)
            self._next_row += 1
        child.grid(row=self._next_row, column=0, sticky=tk.EW)
        self._next_row += 1
        self._page.attach(**options)


class ScrolledPage(tk.Frame):
    """A plain tk.Frame (so it may be packed or gridded freely) holding a canvas, a scrollbar and the content."""

    def __init__(self, notebook: tk.Misc, background: str, cap: int) -> None:
        super().__init__(notebook, background=background)
        self._notebook = notebook
        self._cap = cap
        self._attached = False
        self._fit_job: Any = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._canvas = tk.Canvas(self, background=background, highlightthickness=0, borderwidth=0,
                                 yscrollincrement=18)
        self._canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self._bar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._bar.set)
        self.content = ScrollContent(self, self._canvas)
        self._window = self._canvas.create_window(0, 0, window=self.content, anchor=tk.NW)
        self.content.bind("<Configure>", lambda _e: self.refit(), add="+")
        self._canvas.bind("<Configure>", self._canvas_resized, add="+")

    def attach(self, **options: Any) -> None:
        if not self._attached:
            self._attached = True
            self._notebook.add(self, **options)

    def _canvas_resized(self, event: tk.Event) -> None:
        self._canvas.itemconfigure(self._window, width=event.width)
        self.schedule_fit()

    def schedule_fit(self) -> None:
        """Re-wrap the descriptions once the page has settled (several resize events in a row make one pass)."""
        if self._fit_job is None:
            try:
                self._fit_job = self.after_idle(self.fit_text)
            except tk.TclError:
                self._fit_job = None

    def fit_text(self) -> None:
        """Wrap every label that has its row to itself to the room the page has, from the label's own left edge to the page's right edge."""
        self._fit_job = None
        try:
            width = self._canvas.winfo_width()
            if width <= 1:
                return                       # not laid out yet: the canvas's own resize will call again
            if self._bar.winfo_ismapped():
                width -= self._bar.winfo_width()
            origin = self.content.winfo_rootx()
            for label in _full_row_labels(self.content):
                wanted = max(MIN_TEXT_WIDTH, width - (label.winfo_rootx() - origin) - TEXT_MARGIN)
                if abs(_wrap_of(label) - wanted) > 4:          # a few pixels either way is not worth another layout
                    label.configure(wraplength=wanted)
        except tk.TclError:
            pass                              # the page is being destroyed

    def refit(self) -> None:
        """Size the visible area to the content, up to the cap; show the scrollbar only if the content is taller."""
        wanted = self.content.winfo_reqheight()
        shown = min(wanted, self._cap)
        self._canvas.configure(height=shown, width=self.content.winfo_reqwidth(),
                               scrollregion=(0, 0, self.content.winfo_reqwidth(), wanted))
        if wanted > self._cap:
            self._bar.grid(row=0, column=1, sticky=tk.NS)
        else:
            self._bar.grid_remove()
            self._canvas.yview_moveto(0)

    def finish(self) -> None:
        """Call once the page is built: fit it, and make the mouse wheel scroll it from anywhere over it."""
        self.update_idletasks()
        self.refit()
        self._bind_wheel(self)
        self.schedule_fit()

    def _bind_wheel(self, widget: tk.Misc) -> None:
        if widget.winfo_class() not in _SKIP_WHEEL:
            for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                widget.bind(sequence, self._on_wheel, add="+")
        for child in widget.winfo_children():
            self._bind_wheel(child)

    def _on_wheel(self, event: tk.Event) -> None:
        if self.content.winfo_reqheight() <= self._cap:
            return
        if getattr(event, "num", None) == 4 or getattr(event, "delta", 0) > 0:
            self._canvas.yview_scroll(-3, "units")
        else:
            self._canvas.yview_scroll(3, "units")


def _wrap_of(label: tk.Misc) -> int:
    try:
        return int(float(str(label.cget("wraplength")) or 0))
    except (ValueError, tk.TclError):
        return 0


def _full_row_labels(widget: tk.Misc):
    """The wrapping labels under `widget` that sit alone in their grid row, in column 0: a description, never a cell of a table or a line beside a control (making
    one of those wider would push its neighbors off the page)."""
    for child in widget.winfo_children():
        if isinstance(child, tk.Label) and _wrap_of(child) > 0:
            info = child.grid_info()
            if info and str(info.get("column")) == "0" and not any(other is not child for other in child.master.grid_slaves(row=info["row"])):
                yield child
        yield from _full_row_labels(child)


def scrolled_page(notebook: tk.Misc, build: Any, background: str) -> ScrolledPage:
    """Build one feature's Settings page inside a scrolling frame and add it to `notebook`.
    `build` is the feature's `build_settings(notebook)`; it sees a ScrollContent where a notebook would be."""
    page = ScrolledPage(notebook, background, height_cap(notebook.winfo_screenheight()))
    build(page.content)
    page.finish()
    return page
