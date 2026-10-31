"""Window shell: a Toplevel with a header bar (title, subtitle, action
buttons), a body, a status footer, a minimum size and saved geometry. The
shell never touches EDMC's config - the owning window passes
`load_geometry`/`save_geometry` callables (a `config.get_str` / `config.set`
pair in the real windows), which also keeps this demoable standalone."""
from __future__ import annotations

import re
import tkinter as tk
from typing import Callable, Optional, Sequence, Union

from . import palette as P
from . import trace
from . import placement
from . import style
from .tooltip import add_tooltip
from .widgets import FlatButton, MenuButton, ScrollFrame

HelpItem = Union[str, tuple]   # "a line", or ("Name", "what it means")

_SUBTITLE_START_WRAP = 600   # until the header is first laid out; an unbounded subtitle would stretch the window

_GEOMETRY = re.compile(r"^(\d+)x(\d+)([+-]-?\d+[+-]-?\d+)?$")


class _Parts:
    """What both shells offer a window: header buttons, a Help window, a subtitle and a status line. Needs `window` (the Toplevel the page belongs to), `actions` (the frame
    that holds the header buttons), `_subtitle` and `_status`."""
    window: tk.Misc
    actions: tk.Frame
    _subtitle: tk.Label
    _status: tk.Label

    def _make_text_size_buttons(self, footer: tk.Frame) -> None:
        """A- and A+ at the right end of the footer: they change the text size of every WFMT window (the setting is shared and saved). They
        are in the footer, not the header, because a narrow window needs the header's width for the title. Call before the status is packed."""
        self._sizer = tk.Frame(footer, bg=P.BG)
        self._sizer.pack(side="right", padx=(6, 0))
        for text, step in (("A−", -1), ("A+", 1)):
            button = tk.Label(self._sizer, text=text, fg=P.MUTED, bg=P.BG, padx=7, cursor="hand2", font=style.font(P.FONT_SMALL_BOLD))
            button.pack(side="left")
            button.bind("<Button-1>", lambda _e, n=step: style.set_text_delta(style.text_delta() + n))
            button.bind("<Enter>", lambda _e, b=button: b.configure(fg=P.TEXT), add="+")
            button.bind("<Leave>", lambda _e, b=button: b.configure(fg=P.MUTED), add="+")
            add_tooltip(button, "A- - make the text in every WFMT window smaller" if step < 0 else "A+ - make the text in every WFMT window larger")
        # The color theme: its name, and a menu of the themes when it is pressed. The label changes with the theme, wherever it is chosen.
        theme = tk.Label(self._sizer, text=style.theme_name(), fg=P.MUTED, bg=P.BG, padx=7, cursor="hand2", font=style.font(P.FONT_SMALL_BOLD))
        theme.pack(side="left")
        theme.bind("<Enter>", lambda _e: theme.configure(fg=P.TEXT), add="+")
        theme.bind("<Leave>", lambda _e: theme.configure(fg=P.MUTED), add="+")
        add_tooltip(theme, "Color theme - choose the colors of every WFMT window")

        menu = tk.Menu(theme, tearoff=0)
        for name in P.THEMES:
            menu.add_command(label=name, command=lambda n=name: style.set_theme(n))

        def paint_menu() -> None:
            menu.configure(bg=P.CARD, fg=P.TEXT, activebackground=P.SELECT, activeforeground=P.TEXT, bd=0)

        def retheme() -> None:
            if theme.winfo_exists():
                theme.configure(text=style.theme_name())
                paint_menu()

        paint_menu()
        theme.bind("<Button-1>", lambda _e: menu.tk_popup(theme.winfo_rootx(), theme.winfo_rooty() + theme.winfo_height()))
        stop = style.add_theme_listener(retheme)
        theme.bind("<Destroy>", lambda _e: stop(), add="+")

    def add_action(self, text: str, command: Callable[[], None], accent: bool = False, tip=None) -> FlatButton:
        """A header button. `tip` is its tooltip ("Name - what it does")."""
        button = FlatButton(self.actions, text, command, kind="accent" if accent else "normal", tip=tip)
        button.pack(side="left", padx=(6, 0))
        return button

    def add_menu(self, text: str, items: Sequence[Optional[tuple]], tip=None) -> MenuButton:
        """A header button that opens a menu of related actions (see `MenuButton`). `tip` is its tooltip."""
        button = MenuButton(self.actions, text, items, tip=tip)
        button.pack(side="left", padx=(6, 0))
        return button

    def add_help(self, title: str, items: Sequence[HelpItem]) -> FlatButton:
        """A Help button in the header that opens a small window of short entries, so the explanation is not a paragraph in the window itself.
        Each item is a plain line or a (name, text) pair; the window is raised, not duplicated, when Help is pressed again."""
        self._help_window: Optional[tk.Toplevel] = None

        def show() -> None:
            if self._help_window is not None and self._help_window.winfo_exists():
                self._help_window.lift()
                return
            window = tk.Toplevel(self.window)
            window.title(title)
            window.configure(bg=P.BG)
            window.transient(self.window)
            window.resizable(False, False)
            window.bind("<Escape>", lambda _e: window.destroy())

            def fill(parent: tk.Misc) -> tk.Frame:
                grid = tk.Frame(parent, bg=P.BG)
                for row, item in enumerate(items):
                    if isinstance(item, str):
                        tk.Label(grid, text=item, fg=P.MUTED, bg=P.BG, anchor="nw", justify="left", wraplength=520).grid(
                            row=row, column=0, columnspan=2, sticky="nw", pady=2)
                        continue
                    name, text = item
                    tk.Label(grid, text=name, fg=P.TEXT, bg=P.BG, anchor="nw", justify="left", font=style.font(P.FONT_BOLD)).grid(
                        row=row, column=0, sticky="nw", padx=(0, P.PAD), pady=2)
                    tk.Label(grid, text=text, fg=P.MUTED, bg=P.BG, anchor="nw", justify="left", wraplength=420).grid(row=row, column=1, sticky="nw", pady=2)
                return grid

            grid = fill(window)
            grid.pack(padx=P.PAD, pady=P.PAD)
            close = FlatButton(window, "Close", window.destroy, tip="Close - close this window")
            close.pack(pady=(0, P.PAD))
            window.update_idletasks()
            room = window.winfo_screenheight() - 160
            if window.winfo_reqheight() > room:
                # More entries than the screen holds: the same entries, in a scrolling area above the Close button.
                width = grid.winfo_reqwidth()
                grid.destroy()
                close.pack_forget()
                close.pack(side="bottom", pady=(0, P.PAD))
                scroll = ScrollFrame(window, bg=P.BG)
                scroll.set_viewport(width + 2 * P.PAD, room - close.winfo_reqheight() - 2 * P.PAD)
                scroll.pack(side="top", fill="both", expand=True, padx=P.PAD, pady=P.PAD)
                fill(scroll.body).pack(fill="x", padx=P.PAD)
            self._help_window = window

        self._show_help = show
        return self.add_action("Help", show, tip="Help - what this window's buttons and tabs do")

    def set_subtitle(self, text: str) -> None:
        self._subtitle.configure(text=text)

    def set_status(self, text: str, ok: bool = False) -> None:
        """The line at the foot of the window; `ok` shows it in the success color until the next message."""
        self._status.configure(text=text, fg=P.OK if ok else P.STATUS)


class WindowShell(_Parts):
    def __init__(self, parent: tk.Misc, title: str, subtitle: str = "",
                 size: tuple[int, int] = (1180, 720), min_size: tuple[int, int] = (900, 520),
                 load_geometry: Optional[Callable[[], str]] = None,
                 save_geometry: Optional[Callable[[str], None]] = None) -> None:
        self.window = tk.Toplevel(parent)
        # Built hidden and shown once (see _present): a window that maps first
        # and is then sized, positioned and filled flashes at its default size.
        self.window.withdraw()
        style.skin(self.window)
        factor = style.dpi_factor(self.window)
        size = (int(size[0] * factor), int(size[1] * factor))
        min_size = (int(min_size[0] * factor), int(min_size[1] * factor))
        self.window.title(title)
        trace.emit("window", "opened", title=title)
        self.window.configure(bg=P.BG)
        self.window.minsize(*min_size)
        self._save_geometry = save_geometry
        geometry = self._geometry(load_geometry, size, min_size)
        shape = _GEOMETRY.match(geometry)
        if shape:      # opens on EDMC's monitor unless it was left somewhere that is still on a monitor (see placement.py)
            geometry = placement.geometry_for(parent, geometry, (int(shape.group(1)), int(shape.group(2))))
        self.window.geometry(geometry)
        self.window.bind("<Escape>", lambda _e: self.close())
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        header = tk.Frame(self.window, bg=P.BG, padx=P.PAD * 2, pady=P.PAD)
        header.pack(fill="x")
        # The buttons are packed first so a long subtitle can never push them out of the window; the subtitle wraps in what is left.
        self.actions = tk.Frame(header, bg=P.BG)
        self.actions.pack(side="right")
        titles = tk.Frame(header, bg=P.BG)
        titles.pack(side="left")
        tk.Label(titles, text=title, fg=P.TITLE, bg=P.BG, font=style.font(P.FONT_TITLE)).pack(anchor="w")
        self._subtitle = tk.Label(titles, text=subtitle, fg=P.MUTED, bg=P.BG, justify="left", wraplength=_SUBTITLE_START_WRAP)
        self._subtitle.pack(anchor="w")
        for part in (header, self.actions):   # the buttons are added after this, so both a resize and a new button refit the subtitle
            part.bind("<Configure>", lambda _e, h=header: self._fit_subtitle(h))

        # Footer first so it keeps its height when the body is squeezed.
        footer = tk.Frame(self.window, bg=P.BG, padx=P.PAD * 2, pady=P.PAD_SM)
        footer.pack(side="bottom", fill="x")
        self._make_text_size_buttons(footer)
        self._status = tk.Label(footer, text="", fg=P.STATUS, bg=P.BG, anchor="w",
                                font=style.font(P.FONT_SMALL))
        self._status.pack(side="left", fill="x", expand=True)
        footer.bind("<Configure>", lambda e: self._status.configure(
            wraplength=max(e.width - self._sizer.winfo_reqwidth() - 8 - 2 * P.PAD * 2, 100)))  # long hints wrap instead of clipping

        self.body = tk.Frame(self.window, bg=P.BG, padx=P.PAD * 2)
        self.body.pack(fill="both", expand=True)

        # Runs once the owning window's __init__ has finished adding content.
        self.window.after_idle(self._present)

    def _fit_subtitle(self, header: tk.Frame) -> None:
        width = max(header.winfo_width() - self.actions.winfo_reqwidth() - 4 * P.PAD - 8, 80)
        if width != int(str(self._subtitle.cget("wraplength"))):
            self._subtitle.configure(wraplength=width)

    def _present(self) -> None:
        """Lay everything out while hidden, then show the finished window."""
        if not self.alive:
            return
        self.window.update_idletasks()   # also runs content layout queued with after_idle
        self.window.deiconify()
        self.window.lift()

    @staticmethod
    def _geometry(load: Optional[Callable[[], str]], size: tuple[int, int],
                  min_size: tuple[int, int]) -> str:
        """Saved geometry grown to the minimum size; the default otherwise."""
        saved = load() if load else ""
        match = _GEOMETRY.match(saved or "")
        if not match:
            return f"{size[0]}x{size[1]}"
        width = max(int(match.group(1)), min_size[0])
        height = max(int(match.group(2)), min_size[1])
        return f"{width}x{height}{match.group(3) or ''}"

    @property
    def alive(self) -> bool:
        try:
            return bool(self.window.winfo_exists())
        except tk.TclError:
            return False

    def close(self) -> None:
        if self.alive:
            if self._save_geometry:
                self._save_geometry(self.window.winfo_geometry())
            trace.emit("window", "closed", title=str(self.window.title()), geometry=self.window.winfo_geometry())
            self.window.destroy()


class TabShell(_Parts):
    """The shell a window gets when it is a page in another window's tab instead of a window of its own: the same header buttons, Help, subtitle, status line and body, in a
    frame of `page`. `window` is the host's Toplevel (for `after`, the clipboard, dialogs and variables); the page's size and position are the host's, so `size`, `min_size` and the
    geometry callables are accepted and ignored. A window opts in by building its shell with `host(...)` in place of `WindowShell(...)`, where `host` is
    `functools.partial(TabShell, page=..., on_close=...)`. `close` empties the page and calls `on_close(self)`; it never closes the host."""

    def __init__(self, parent: tk.Misc, title: str, subtitle: str = "", size: tuple[int, int] = (0, 0), min_size: tuple[int, int] = (0, 0),
                 load_geometry: Optional[Callable[[], str]] = None, save_geometry: Optional[Callable[[str], None]] = None, *,
                 page: tk.Frame, on_close: Optional[Callable[["TabShell"], None]] = None) -> None:
        self.window = parent.winfo_toplevel()
        self._page = page
        self._on_close = on_close
        self._closed = False
        self._root = tk.Frame(page, bg=P.BG)
        self._root.pack(fill="both", expand=True)
        header = tk.Frame(self._root, bg=P.BG, padx=P.PAD * 2, pady=P.PAD_SM)
        header.pack(fill="x")
        self.actions = tk.Frame(header, bg=P.BG)
        self.actions.pack(side="right")
        self._subtitle = tk.Label(header, text=subtitle, fg=P.MUTED, bg=P.BG, justify="left", anchor="w", wraplength=_SUBTITLE_START_WRAP)
        self._subtitle.pack(side="left", fill="x", expand=True)
        for part in (header, self.actions):
            part.bind("<Configure>", lambda _e, h=header: self._fit_subtitle(h))
        footer = tk.Frame(self._root, bg=P.BG, padx=P.PAD * 2, pady=P.PAD_SM)
        footer.pack(side="bottom", fill="x")
        self._make_text_size_buttons(footer)
        self._status = tk.Label(footer, text="", fg=P.STATUS, bg=P.BG, anchor="w", font=style.font(P.FONT_SMALL))
        self._status.pack(side="left", fill="x", expand=True)
        footer.bind("<Configure>", lambda e: self._status.configure(wraplength=max(e.width - self._sizer.winfo_reqwidth() - 8 - 2 * P.PAD * 2, 100)))
        self.body = tk.Frame(self._root, bg=P.BG, padx=P.PAD * 2)
        self.body.pack(fill="both", expand=True)

    def _fit_subtitle(self, header: tk.Frame) -> None:
        width = max(header.winfo_width() - self.actions.winfo_reqwidth() - 4 * P.PAD - 8, 80)
        if width != int(str(self._subtitle.cget("wraplength"))):
            self._subtitle.configure(wraplength=width)

    @property
    def alive(self) -> bool:
        try:
            return not self._closed and bool(self._root.winfo_exists())
        except tk.TclError:
            return False

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._root.destroy()
        except tk.TclError:
            pass
        if self._on_close is not None:
            self._on_close(self)
