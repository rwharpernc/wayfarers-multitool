"""RichText: a read-only block of formatted text for detail panes (a title, a status line, section headings, labelled rows, numbered steps with a hanging
indent, notes). It is a `tk.Text` with ready-made tags, so one pane can mix sizes, bold, color and indents, and it is as tall as its text (no scroll bar of
its own: the page around it scrolls). Fonts come from `style.font`, which resizes them in place, so the pane follows the text size setting; its colors are
the palette's, which a theme change recolors with the rest of the window.

Use: `clear()`, then `title`, `subtitle`, `heading`, `row`, `step`, `bullet`, `paragraph`, then `finish()` to size the pane to what was written. `text()` gives
the plain text back. A link is written with `row(..., url=)` or `subtitle(..., (text, url))`: it is underlined in the accent color, opens in the browser when clicked, and
the pane can be copied from (select and Ctrl+C, a right-click menu, or `copy_all`)."""
from __future__ import annotations

import tkinter as tk
import webbrowser
from typing import Callable, Dict, Optional, Sequence, Tuple, Union

from . import palette as P
from . import style

_LABEL_WIDTH = 120      # pixels the label of a row takes before its value starts
_STEP_INDENT = 22       # pixels a numbered step is indented, and its wrapped lines further


class RichText(tk.Text):
    def __init__(self, parent: tk.Misc, bg: Optional[str] = None) -> None:
        super().__init__(parent, wrap="word", height=1, bd=0, highlightthickness=0, relief="flat", padx=P.PAD, pady=P.PAD_SM,
                         cursor="arrow", takefocus=0, insertwidth=0, bg=bg or P.PANE, fg=P.TEXT, font=style.font(P.FONT_BODY),
                         selectbackground=P.SELECT, selectforeground=P.TEXT, inactiveselectbackground=P.SELECT, state="disabled")
        self._fit_pending = False
        self._links: Dict[str, str] = {}        # link tag name -> address, for the text written now
        self._actions: Dict[str, Callable[[], None]] = {}   # action tag name -> what a click runs
        self._tags()
        self.bind("<Configure>", lambda _e: self._schedule_fit())
        self._make_copyable()

    def _tags(self) -> None:
        body, bold = style.font(P.FONT_BODY), style.font(P.FONT_BOLD)
        self.tag_configure("title", font=style.font(P.FONT_TITLE), foreground=P.TEXT, spacing3=2)
        self.tag_configure("subtitle", font=body, foreground=P.MUTED, spacing3=6)
        self.tag_configure("heading", font=style.font(P.FONT_SECTION), foreground=P.HEADING, spacing1=16, spacing3=4)
        self.tag_configure("label", font=bold, foreground=P.TEXT)
        self.tag_configure("muted", font=body, foreground=P.MUTED)
        self.tag_configure("body", font=body, foreground=P.TEXT)
        self.tag_configure("row", lmargin1=P.PAD, lmargin2=P.PAD + _LABEL_WIDTH, tabs=(P.PAD + _LABEL_WIDTH,), spacing1=2, spacing3=2)
        self.tag_configure("paragraph", lmargin1=P.PAD, lmargin2=P.PAD, spacing1=2, spacing3=4)
        self.tag_configure("stop", font=bold, foreground=P.TEXT, lmargin1=P.PAD, lmargin2=P.PAD, spacing1=8, spacing3=2)
        self.tag_configure("step", lmargin1=P.PAD + _STEP_INDENT, lmargin2=P.PAD + _STEP_INDENT * 2, spacing1=2, spacing3=3)
        self.tag_configure("bullet", lmargin1=P.PAD, lmargin2=P.PAD + _STEP_INDENT, spacing1=2, spacing3=3)
        self.tag_configure("hang", lmargin1=P.PAD + _STEP_INDENT, lmargin2=P.PAD + _STEP_INDENT, spacing1=1, spacing3=1)
        self.tag_configure("good", font=bold, foreground=P.ENGINEER_UNLOCKED)
        self.tag_configure("progress", font=bold, foreground=P.ENGINEER_PROGRESS)
        self.tag_configure("bad", font=bold, foreground=P.ENGINEER_UNAVAILABLE)
        self.tag_configure("warn", font=bold, foreground=P.WARN)

    # --- writing ---------------------------------------------------------------------------------------------------

    def clear(self) -> None:
        self.configure(state="normal")
        self.delete("1.0", "end")
        for name in [*self._links, *self._actions]:
            self.tag_delete(name)
        self._links.clear()
        self._actions.clear()

    def _put(self, text: str, *tags: str) -> None:
        self.insert("end", text, tags)

    def title(self, text: str, status: str = "", status_tag: str = "") -> None:
        self._put(text, "title")
        if status:
            self._put("   ", "title")
            self._put(status, status_tag or "label")
        self._put("\n")

    def subtitle(self, *parts: Union[str, Tuple[str, str]]) -> None:
        """A muted line made of parts: plain text, or `(text, url)` for a link."""
        for part in parts:
            if isinstance(part, tuple):
                self._link(part[0], part[1], "subtitle")
            else:
                self._put(part, "subtitle")
        self._put("\n", "subtitle")

    def heading(self, text: str) -> None:
        self._put(text + "\n", "heading")

    def row(self, label: str, value: str, url: str = "") -> None:
        """A label in bold and its value after a tab, wrapped lines lining up under the value (the value is a link when `url` is given)."""
        self._put(label, "row", "label")
        self._put("\t", "row", "body")
        if url:
            self._link(value, url, "row")
        else:
            self._put(value, "row", "body")
        self._put("\n", "row", "body")

    def paragraph(self, text: str, *tags: str) -> None:
        self._put(text + "\n", "paragraph", *(tags or ("body",)))

    def stop(self, text: str) -> None:
        """The name of the engineer whose steps follow."""
        self._put(text + "\n", "stop")

    def step(self, number: int, label: str, detail: str, done: bool = False, note: str = "") -> None:
        """`1. Label: detail`, the number and label in bold, the rest in the body font, a tick when done and the journal's note after it; a wrapped line hangs under the detail."""
        self._put(f"{number}.  ", "step", "label")
        self._put(label, "step", "label")
        if detail:
            self._put(": " + detail, "step", "body")
        if done:
            self._put("   Done", "step", "good")
        if note:
            self._put(f"   ({note})", "step", "muted")
        self._put("\n")

    def numbered(self, number: int, text: str) -> None:
        """A numbered line of plain text with a hanging indent (the steps of a guide)."""
        self._put(f"{number}.  ", "step", "label")
        self._put(text + "\n", "step", "body")

    def bullet(self, text: str, label: str = "", tag: str = "body") -> None:
        self._put("•  ", "bullet", "label")
        if label:
            self._put(label + " ", "bullet", tag if tag != "body" else "label")
        self._put(text + "\n", "bullet", "body")

    def _link(self, text: str, url: str, *tags: str) -> None:
        """Text that opens `url` in the browser when it is clicked."""
        name = f"link{len(self._links)}"
        self._links[name] = url
        self._style_link(name, lambda _e, n=name: self.open_link(n))
        self._put(text, *tags, name)

    def _style_link(self, name: str, on_click: Callable[[tk.Event], object]) -> None:
        self.tag_configure(name, foreground=P.ACCENT, underline=True)
        self.tag_bind(name, "<Button-1>", on_click)
        self.tag_bind(name, "<Enter>", lambda _e: self.configure(cursor="hand2"))
        self.tag_bind(name, "<Leave>", lambda _e: self.configure(cursor="arrow"))

    def action(self, text: str, callback: Callable[[], None], *tags: str) -> None:
        """Text that runs `callback` when it is clicked, drawn like a link."""
        name = f"action{len(self._actions)}"
        self._actions[name] = callback
        self._style_link(name, lambda _e, n=name: self.run_action(n))
        self._put(text, *tags, name)

    def run_action(self, name: str) -> bool:
        callback = self._actions.get(name)
        if callback is None:
            return False
        callback()
        return True

    def actions(self) -> Dict[str, str]:
        """The clickable actions in the text written now: tag name -> the text shown."""
        out: Dict[str, str] = {}
        for name in self._actions:
            ranges = self.tag_ranges(name)
            if ranges:
                out[name] = self.get(ranges[0], ranges[1])
        return out

    def item(self, name: str, quantity: str, how: str, actions: Sequence[Tuple[str, Callable[[], None]]] = (), note: str = "") -> None:
        """One thing the player has to get: its name in bold with the quantity (`need 25, have 6`), a line on how to get it, and clickable actions under it."""
        self._put(name, "bullet", "label")
        self._put("   " + quantity + "\n", "bullet", "muted")
        if how:
            self._put(how + "\n", "hang", "body")
        if note:
            self._put(note + "\n", "hang", "muted")
        if actions:
            self._put("", "hang")
            for index, (text, callback) in enumerate(actions):
                if index:
                    self._put("   ", "hang", "muted")
                self.action(text, callback, "hang")
            self._put("\n", "hang")

    def open_link(self, name: str) -> bool:
        """Open the address behind a link tag (nothing happens for a name that is not one)."""
        url = self._links.get(name)
        if not url:
            return False
        webbrowser.open(url)
        return True

    def links(self) -> Dict[str, str]:
        """The addresses of the links in the text written now, by tag name."""
        return dict(self._links)

    def message(self, text: str) -> None:
        """A single plain line, for 'Select an engineer for the details.'"""
        self.clear()
        self.paragraph(text, "muted")
        self.finish()

    def finish(self) -> None:
        self.configure(state="disabled")
        self._schedule_fit()

    # --- copying ---------------------------------------------------------------------------------------------------

    def _make_copyable(self) -> None:
        """Let the pane be selected from and copied: a click gives it the keyboard focus, Ctrl+C copies the selection (or everything when nothing is selected), Ctrl+A
        selects all, and a right-click opens a small menu."""
        self.bind("<Button-1>", lambda _e: self.focus_set(), add="+")
        for sequence in ("<Control-c>", "<Control-C>", "<Command-c>"):
            self.bind(sequence, lambda _e: self._copy_selection() or "break")
        for sequence in ("<Control-a>", "<Control-A>", "<Command-a>"):
            self.bind(sequence, lambda _e: self._select_all() or "break")
        self.bind("<Button-3>", self._menu)
        self.bind("<Button-2>", self._menu)

    def _select_all(self) -> None:
        self.tag_add("sel", "1.0", "end-1c")

    def _copy_selection(self) -> None:
        try:
            text = self.get("sel.first", "sel.last")
        except tk.TclError:
            text = self.text()
        self._to_clipboard(text)

    def copy_all(self) -> bool:
        """Put all of the text on the clipboard; False when there is none."""
        text = self.text()
        if text.strip():
            self._to_clipboard(text)
        return bool(text.strip())

    def _to_clipboard(self, text: str) -> None:
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
        except tk.TclError:
            pass

    def _menu(self, event: tk.Event) -> None:
        menu = tk.Menu(self, tearoff=0, bg=P.BUTTON, fg=P.TEXT, activebackground=P.HOVER, activeforeground=P.TEXT, bd=0, relief="flat", font=style.font(P.FONT_BODY))
        has_selection = bool(self.tag_ranges("sel"))
        menu.add_command(label="Copy selection", command=self._copy_selection, state="normal" if has_selection else "disabled")
        menu.add_command(label="Copy all", command=self.copy_all)
        menu.add_command(label="Select all", command=self._select_all)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # --- reading and sizing ----------------------------------------------------------------------------------------

    def text(self) -> str:
        return self.get("1.0", "end-1c")

    def _schedule_fit(self) -> None:
        if not self._fit_pending:
            self._fit_pending = True
            self.after_idle(self._fit)

    def _fit(self) -> None:
        """As tall as the text is (done again when the width changes, since a narrower pane wraps onto more lines). The height is set in lines of the pane's own
        font, but the title is larger and headings and steps have space around them, so it is worked out from the pixels the content really takes."""
        self._fit_pending = False
        try:
            self.update_idletasks()
            pixels = self.count("1.0", "end", "ypixels")
            line = max(1, int(style.font(P.FONT_BODY).metrics("linespace")))
            wanted = max(1, -(-int(pixels[0] if pixels else line) // line))
            if int(self.cget("height")) != wanted:
                self.configure(height=wanted)
        except (tk.TclError, TypeError, ValueError):
            pass
