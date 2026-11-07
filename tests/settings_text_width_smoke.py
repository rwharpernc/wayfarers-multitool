"""A Settings page's descriptions use the page's whole width (plugin/settings_scroll.py, ScrolledPage.fit_text): a label written with a fixed wraplength is re-wrapped to
the room the page has, follows a resize both ways, and a label that shares its row (a table cell, a line beside a control) is left alone. Run by
test_settings_text_width in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import os
import sys
import types
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
import tkinter as tk
from tkinter import ttk


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


nbmod = Any("myNotebook")
nbmod.Frame, nbmod.Label, nbmod.Button, nbmod.Checkbutton = tk.Frame, tk.Label, tk.Button, tk.Checkbutton
sys.modules["myNotebook"] = nbmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


from plugin import settings_scroll  # noqa: E402

LONG = "A description of what this setting does and what it sends, long enough that it takes several lines when it is narrow. " * 6
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)
root.geometry("1000x700+0+0")
built = {}


def build(content):
    frame = tk.Frame(content)
    frame.columnconfigure(0, weight=1)
    content.add(frame, text="Page")
    built["long"] = tk.Label(frame, text=LONG, wraplength=440, justify=tk.LEFT)
    built["long"].grid(row=0, column=0, sticky=tk.W, padx=10)
    built["head"] = tk.Label(frame, text="Heading with no wrap")
    built["head"].grid(row=1, column=0, sticky=tk.W, padx=10)
    built["cell_a"] = tk.Label(frame, text=LONG, wraplength=300)
    built["cell_a"].grid(row=2, column=0, sticky=tk.W)
    built["cell_b"] = tk.Label(frame, text="beside it")
    built["cell_b"].grid(row=2, column=1, sticky=tk.W)
    inner = tk.Frame(frame)
    inner.grid(row=3, column=0, sticky=tk.W)
    tk.Checkbutton(inner, text="a box").grid(row=0, column=0)
    built["beside_box"] = tk.Label(inner, text=LONG, wraplength=250)
    built["beside_box"].grid(row=0, column=1)


page = settings_scroll.scrolled_page(notebook, build, "#ffffff")
for _ in range(5):
    root.update()
    root.after(20)
    root.update()
canvas = page._canvas
width = canvas.winfo_width()
long = built["long"]
check(width > 700, f"the page is wide: {width}")
wrap = settings_scroll._wrap_of(long)
check(wrap > 440, f"the description is no longer held to its fixed 440: {wrap}")
check(wrap <= width, f"and never wider than the page: {wrap} of {width}")
check(width - wrap < 60, f"it uses the room the page has: wrap {wrap} of {width}")
check(long.winfo_width() > width * 0.8, f"drawn, it spans most of the page: {long.winfo_width()} of {width}")
check(settings_scroll._wrap_of(built["head"]) == 0, "a label that does not wrap is untouched")
check(settings_scroll._wrap_of(built["cell_a"]) == 300, "a label sharing its row with another is untouched")
check(settings_scroll._wrap_of(built["beside_box"]) == 250, "a label beside a control is untouched")
check(canvas.winfo_width() >= width, "and nothing was pushed off the page")

root.geometry("600x700+0+0")
for _ in range(5):
    root.update()
    root.after(20)
    root.update()
narrow = canvas.winfo_width()
shrunk = settings_scroll._wrap_of(long)
check(narrow < width, f"the window got narrower: {narrow}")
check(shrunk < wrap and shrunk <= narrow, f"and the description followed it: {shrunk} of {narrow}")
check(shrunk >= settings_scroll.MIN_TEXT_WIDTH, f"never narrower than the floor: {shrunk}")

root.geometry("1100x700+0+0")
for _ in range(5):
    root.update()
    root.after(20)
    root.update()
check(settings_scroll._wrap_of(long) > shrunk, "and widens again when the window does")

root.destroy()
if problems:
    print("\n".join(problems))
    sys.exit(1)
print("SETTINGS TEXT WIDTH OK")
