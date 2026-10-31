"""Hovers the window kit's buttons for real and checks that the tooltip appears. A tip bound to a button is not enough: FlatButton once bound its hover
highlight over the tooltip's own <Enter> handler, so every tip was attached and none ever showed. Run by test_uikit_tooltips in a subprocess. Exits 0 if
everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
import time

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
import tkinter as tk

try:
    root = tk.Tk()
except tk.TclError:
    sys.exit(77)
root.geometry("700x500+100+100")

from plugin.uikit.shell import WindowShell
from plugin.uikit.tooltip import TOOLTIP_DELAY_MS
from plugin.uikit.widgets import FlatButton, MenuButton

failures = []


def check(ok, what):
    if not ok:
        failures.append(what)
        print("FAIL:", what)


def hover(widget):
    """Pointer enters `widget`; returns the text of the tooltip that appears (or None), then the pointer leaves."""
    widget.update()
    widget.event_generate("<Enter>")
    deadline = time.time() + TOOLTIP_DELAY_MS / 1000 + 1.0
    text = None
    while time.time() < deadline and text is None:
        root.update()
        time.sleep(0.02)
        for tip in [w for w in widget.winfo_children() if isinstance(w, tk.Toplevel)]:
            labels = [w for w in tip.winfo_children() if isinstance(w, tk.Label)]
            if labels:
                text = str(labels[0].cget("text"))
    widget.event_generate("<Leave>")
    root.update()
    return text


button = FlatButton(root, "Go", lambda: None, tip="Go - do the thing")
button.pack()
check(hover(button) == "Go - do the thing", "a FlatButton shows its tooltip when hovered")

menu = MenuButton(root, "More", [("One", lambda: None)], tip="More - other actions")
menu.pack()
check(hover(menu) == "More - other actions", "a MenuButton shows its tooltip when hovered")

shell = WindowShell(root, "Test", "", size=(500, 300), min_size=(300, 200))
shell.window.update()
action = shell.add_action("Do it", lambda: None, tip="Do it - runs the action")
shell.window.update()
check(hover(action) == "Do it - runs the action", "a window action shows its tooltip when hovered")


def find(widget, text):
    for child in widget.winfo_children():
        if isinstance(child, tk.Label) and str(child.cget("text")) == text:
            return child
        found = find(child, text)
        if found is not None:
            return found
    return None


for caption, expected in (("A+", "A+ - make the text in every WFMT window larger"), ("A−", "A- - make the text in every WFMT window smaller")):
    label = find(shell.window, caption)
    check(label is not None, f"the footer has {caption}")
    if label is not None:
        check(hover(label) == expected, f"{caption} in the footer shows its tooltip when hovered")

if failures:
    sys.exit(1)
print("UIKIT TOOLTIPS OK")
