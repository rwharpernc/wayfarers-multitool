"""Checks plugin/commit_entry.py: a settings box commits on Return or leaving it only when its text changed, once for Return then leaving, and shows the
text the commit returns. Run by test_commit_entry.py in a subprocess. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import os
import sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ".")
import tkinter as tk

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.geometry("300x100")      # shown: a withdrawn window does not deliver the focus events the boxes listen for
root.update()

from plugin import commit_entry  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()


calls = []


def commit(text):
    calls.append(text)
    return str(min(int(text), 100)) if text.isdigit() else "5"       # clamps to 100; a bad value goes back to 5


var = tk.StringVar(value="5")
entry = tk.Entry(root, textvariable=var)
entry.pack()
commit_entry.bind_commit(entry, var, commit)
pump()
entry.focus_force()      # Return is a key event: it goes to the box that has the focus
pump()
entry.event_generate("<FocusOut>")
entry.event_generate("<Return>")
pump()
check(calls == [], f"nothing is saved when the text did not change: {calls}")
var.set("40")
entry.event_generate("<Return>")
entry.event_generate("<FocusOut>")
pump()
check(calls == ["40"], f"Return then leaving saves once: {calls}")
var.set("900")
entry.event_generate("<FocusOut>")
pump()
check(calls == ["40", "900"] and var.get() == "100", f"a clamped value is shown: {calls} {var.get()!r}")
entry.event_generate("<FocusOut>")
pump()
check(calls == ["40", "900"], "and leaving again saves nothing")
var.set("abc")
entry.event_generate("<Return>")
pump()
check(var.get() == "5", f"a bad value goes back to what is held: {var.get()!r}")
var.set("7")                                  # changed from elsewhere (another window), then entered and left unedited
entry.event_generate("<FocusIn>")
entry.event_generate("<FocusOut>")
pump()
check(calls[-1] == "abc" and len(calls) == 3, f"a value changed elsewhere is not saved again just for passing through: {calls}")

if problems:
    print("PROBLEMS:")
    for line in problems:
        print("  -", line)
    sys.exit(1)
print("COMMIT ENTRY OK")
