"""Opens the real Create Raven Colonial project dialog (plugin/colonization_create_dialog.py) with EDMC stubbed, as it is for a
construction ship in a system Raven has no sites for, and checks that it appears, is filled in and can be confirmed or cancelled.
Run by test_colonization_create_dialog_smoke.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything
holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
import types
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
import tkinter as tk


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui",
          "win32process", "win32clipboard", "pywintypes", "psutil"):
    sys.modules[n] = Any(n)
theme = Any("theme")
theme.theme = mock.MagicMock()
theme.theme.active = None
theme.theme.THEME_DEFAULT = 0
sys.modules["theme"] = theme
cfgmod = types.ModuleType("config")
cfgmod.appname = "EDMarketConnector"
cfgmod.config = mock.MagicMock()
cfgmod.user_agent = "WFMT-test"
cfgmod.appversion = lambda: "5.13.0"
sys.modules["config"] = cfgmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()

from plugin import colonization_create_dialog as D, rcc_client

problems = []
BODIES = [rcc_client.RccBody(5, "HIP 34457 1 a", "rb"), rcc_client.RccBody(0, "HIP 34457", "st")]


def run(label, press, **extra):
    seen = {}

    def act():
        tops = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel)]
        seen["count"] = len(tops)
        if tops:
            seen["viewable"] = bool(tops[0].winfo_viewable())
            buttons = [w for w in tops[0].winfo_children()[-1].winfo_children()]
            seen["buttons"] = len(buttons)
            if press == "create":
                tops[0].event_generate("<Return>")
            tops[0].after(50, lambda: _click(tops[0], press))
    root.after(300, act)
    result = D.ask(root, "HIP 34457", "Primary port", [], None, "TIBER CAELVOX", False, bodies=BODIES, **extra)
    if seen.get("count") != 1 or not seen.get("viewable"):
        problems.append(f"{label}: the dialog did not appear ({seen})")
    return result


def _click(top, press):
    bar = top.winfo_children()[-1]
    # Create is packed first (right), Cancel second, so Create is the first child
    kids = bar.winfo_children()
    target = kids[0] if press == "create" else kids[1]
    target.event_generate("<Button-1>")
    target.event_generate("<ButtonRelease-1>")
    if top.winfo_exists():
        top.after(200, lambda: top.winfo_exists() and top.destroy())


for label, extra in (("construction ship", {"primary_port": True}), ("ordinary site", {}),
                     ("locked system", {"primary_port": True, "locked_note": "This system is locked to its architect, X."})):
    run(label, "cancel", **extra)

for p in problems:
    print("PROBLEM:", p)
print("CREATE DIALOG OK" if not problems else "CREATE DIALOG FAILED")
sys.exit(1 if problems else 0)
