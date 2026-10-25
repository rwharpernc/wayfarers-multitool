"""Opens each themed dialog (plugin/uikit/dialogs.py) for real and drives it: a button, Esc, Enter and closing the window give the right result; a very long message
stays inside the width cap; a missing parent works. Run by test_uikit_dialogs in a subprocess. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
import tkinter as tk

from plugin.uikit import dialogs
from plugin.uikit.widgets import FlatButton

try:
    root = tk.Tk()
except tk.TclError:
    sys.exit(77)
root.geometry("600x400+100+100")
root.update()

failures = []


def check(ok, what):
    if not ok:
        failures.append(what)
        print("FAIL:", what)


def dialog():
    found = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel)]
    return found[-1] if found else None


def buttons(window):
    out = []

    def walk(widget):
        for child in widget.winfo_children():
            if isinstance(child, FlatButton):
                out.append(child)
            walk(child)
    walk(window)
    return sorted(out, key=lambda b: b.winfo_x())


def press(index):
    def go():
        buttons(dialog())[index]._command()
    return go


def key(sequence):
    def go():
        window = dialog()
        window.focus_force()
        window.update()
        window.event_generate(sequence, when="now")
    return go


def run(action, call, parent=root):
    """Schedules `action` once the dialog is up, then runs the (blocking) call."""
    root.after(150, action)
    root.after(8000, lambda: dialog() and dialog().destroy())   # a stuck dialog fails the test instead of hanging it
    return call(parent)


# confirm: both buttons, default button on Enter, Esc, close.
check(run(press(0), lambda p: dialogs.confirm(p, "T", "Sure?")) is True, "confirm Yes")
check(run(press(1), lambda p: dialogs.confirm(p, "T", "Sure?")) is False, "confirm No")
check(run(key("<Return>"), lambda p: dialogs.confirm(p, "T", "Sure?")) is True, "confirm Enter takes Yes by default")
check(run(key("<Return>"), lambda p: dialogs.confirm(p, "T", "Sure?", default_yes=False)) is False, "confirm Enter takes No when it is the default")
check(run(key("<Escape>"), lambda p: dialogs.confirm(p, "T", "Sure?")) is False, "confirm Esc is False")
check(run(lambda: dialog().destroy(), lambda p: dialogs.confirm(p, "T", "Sure?")) is False, "confirm closed is False")
check(run(press(0), lambda p: dialogs.confirm(p, "T", "Sure?", yes="Do it", no="Leave")) is True, "confirm custom labels")

# choose: the pressed label, the cancel value on Esc.
check(run(press(1), lambda p: dialogs.choose(p, "T", "Pick", ["A", "B", "C"])) == "B", "choose returns the label pressed")
check(run(key("<Return>"), lambda p: dialogs.choose(p, "T", "Pick", ["A", "B", "C"], default=2)) == "C", "choose Enter takes the default")
check(run(key("<Escape>"), lambda p: dialogs.choose(p, "T", "Pick", ["A", "B"], cancel_value="none")) == "none", "choose Esc gives cancel_value")
check(run(key("<Escape>"), lambda p: dialogs.choose(p, "T", "Pick", ["A", "B"])) is None, "choose Esc defaults to None")


# prompt: the typed text, None on cancel.
def type_and(index):
    def go():
        entry = [w for w in dialog().winfo_children()[0].winfo_children()[1].winfo_children() if isinstance(w, tk.Entry)][0]
        entry.delete(0, "end")
        entry.insert(0, "typed text")
        press(index)()
    return go


check(run(type_and(0), lambda p: dialogs.prompt(p, "T", "Name?", initial="old")) == "typed text", "prompt returns the entry text")
check(run(key("<Escape>"), lambda p: dialogs.prompt(p, "T", "Name?")) is None, "prompt Esc is None")
check(run(key("<Return>"), lambda p: dialogs.prompt(p, "T", "Name?", initial="kept")) == "kept", "prompt Enter accepts the initial text")


# info / warning / error: one OK button, return None, Esc closes.
def one_button():
    check(len(buttons(dialog())) == 1, "one OK button")
    press(0)()


for fn in (dialogs.info, dialogs.warning, dialogs.error):
    check(run(one_button, lambda p: fn(p, "T", "Done")) is None, f"{fn.__name__} returns None")
    check(run(key("<Escape>"), lambda p: fn(p, "T", "Done")) is None, f"{fn.__name__} Esc closes")

# A very long message stays inside the cap and the screen, and does not widen the parent.
width_seen = []


def measure():
    window = dialog()
    window.update_idletasks()
    width_seen.append((window.winfo_reqwidth(), window.winfo_reqheight()))
    window.destroy()


before = root.winfo_reqwidth()
run(measure, lambda p: dialogs.info(p, "T", "word " * 3000))
run(measure, lambda p: dialogs.info(p, "T", "x" * 5000))
run(measure, lambda p: dialogs.info(p, "T", "\n".join(["line"] * 200)))
run(measure, lambda p: dialogs.confirm(p, "T", "an unbroken run " + "y" * 400))
for w, h in width_seen:
    check(w <= dialogs.MAX_WIDTH + 140, f"dialog width {w} exceeds the cap")
    check(h <= root.winfo_screenheight(), f"dialog height {h} exceeds the screen")
check(len(width_seen) == 4, "every long-message dialog was measured")
check(root.winfo_reqwidth() <= before, "the parent window grew")

# No parent: falls back to the default root and still works; a destroyed parent returns its cancel value.
check(run(press(0), lambda p: dialogs.confirm(None, "T", "No parent")) is True, "confirm with no parent")
gone = tk.Toplevel(root)
gone.destroy()
check(dialogs.confirm(gone, "T", "Parent already destroyed") is False, "a destroyed parent gives False")
check(dialogs.prompt(gone, "T", "Parent already destroyed") is None, "a destroyed parent gives None for prompt")

# Nothing is left behind.
check(dialog() is None, "a dialog window was left open")
root.destroy()
check(dialogs.confirm(None, "T", "No Tk at all") is False, "no Tk root gives False")

if failures:
    sys.exit(1)
print("UIKIT DIALOGS OK")
