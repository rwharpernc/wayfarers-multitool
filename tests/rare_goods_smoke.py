"""Opens the real Rare Goods Finder (plugin/rare_goods_window.py) with EDMC stubbed and the Power lookup faked: the Distance column beside the origin system, its values for a
known position (Lave's own coordinates), the sort on it, and the row shown while the position is not known. Run by test_rare_goods_smoke in a subprocess so the stand-ins never
leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
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


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "ttkHyperlinkLabel"):
    sys.modules[n] = Any(n)
saved = {}


class Cfg:
    def get_str(self, key, default=""):
        return saved.get(key, default) or ""

    def set(self, key, value):
        saved[key] = value


cfgmod = types.ModuleType("config")
cfgmod.appname = "EDMarketConnector"
cfgmod.config = Cfg()
sys.modules["config"] = cfgmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()

from plugin import powerplay_control_lookup, rare_goods, rare_goods_window as WIN  # noqa: E402

powerplay_control_lookup.fetch_missing = lambda ids, callback: None       # no network: the Power column stays as the cache has it
powerplay_control_lookup.cached = lambda id64: (True, None)

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def rows(window):
    table = window._table
    return [table._rows[iid].values for iid in table._order]


heads = [c.heading for c in WIN._COLUMNS]
check(heads.index("Distance") == heads.index("Origin System") + 1, f"the Distance column follows the origin system: {heads}")
check(heads.index("Arrival") == heads.index("Station") + 1, f"the Arrival column follows the station: {heads}")

LAVE = (75.75, 48.75, 70.75)
WIN.show(root, "Lave", LAVE)
window = WIN._window
shown = rows(window)
check(len(shown) == 10 and all(len(r) == len(heads) for r in shown), f"ten rows, one value per column: {len(shown)} rows")
col = heads.index("Distance")
check(shown[0][col] == "0.0 ly", f"the rare in the current system is 0.0 ly away: {shown[0]}")
want = [rare_goods.distance_text(e["distance_ly"]) for e in rare_goods.nearest(LAVE, 10)]
check([r[col] for r in shown] == want, f"the column shows each origin's distance, nearest first: {[r[col] for r in shown]}")

arrive = heads.index("Arrival")
want_ls = [rare_goods.arrival_text(e["distanceToStarLs"]) for e in rare_goods.nearest(LAVE, 10)]
check([r[arrive] for r in shown] == want_ls and shown[0][arrive] == "288 ls", f"the Arrival column shows the station's distance from its star: {[r[arrive] for r in shown]}")

check(len(window._STATUS) < 160, f"the status line is a short hint, not a paragraph: {len(window._STATUS)} characters")
window._shell._show_help()
help_window = window._shell._help_window
check(help_window is not None and help_window.winfo_exists(), "Help opens a window")
window._shell._show_help()   # a second press raises it rather than opening another
check(window._shell._help_window is help_window, "a second Help press reuses the window")
help_window.destroy()

window._table.sort_by("distance")
first = [float(r[col].replace(",", "").split()[0]) for r in rows(window)]
check(first == sorted(first), f"clicking Distance sorts it as numbers: {first}")
window._table.sort_by("distance")
again = [float(r[col].replace(",", "").split()[0]) for r in rows(window)]
check(again == sorted(again, reverse=True), "a second click reverses it")

legal = heads.index("Legality")
check(shown[0][legal] == "Restricted", f"Lavian Brandy is restricted and the place is not known: {shown[0]}")
window.refresh("Lave", LAVE, "Federation", "Theocracy")
check(rows(window)[0][legal] == "Illegal here", f"in a Federation theocracy Lavian Brandy is illegal here: {rows(window)[0]}")
window.refresh("Lave", LAVE, "Federation", "Democracy")
check(rows(window)[0][legal] == "Legal here" and "Legal" in {r[legal] for r in rows(window)}, f"in a Federation democracy it is legal here, and unrestricted rares read Legal: {rows(window)[0]}")

window._copy_selected()
check("Select a row" in window._shell._status.cget("text"), "Copy system with nothing selected says to select a row")
first_iid = window._table._order[0]
window._table.select(first_iid, notify=True)
check("Lavian Brandy" in window._detail.cget("text") and "illegal in" in window._detail.cget("text"), f"selecting a row says where it is illegal: {window._detail.cget('text')!r}")
window._copy_selected()
check(root.clipboard_get() == "Lave", f"Copy system puts the origin system on the clipboard: {root.clipboard_get()!r}")

# the filters apply before the number shown
window.refresh("Lave", LAVE)
window._large_var.set(True)
window._apply_filters()
pad = heads.index("Pad")
big = rows(window)
check(len(big) == 10 and all(r[pad] == "L" for r in big), f"Large pads only keeps ten rows, all large: {[r[pad] for r in big]}")
check(saved.get(WIN.CONFIG_LARGE_ONLY) == "1", "and the choice is remembered")
window._large_var.set(False)
window._apply_filters()
check(any(r[pad] == "M" for r in rows(window)), "unticking it brings the medium pads back")

POWERS = {}                                                   # what "Spansh" says, by origin system address
asked = []
def fake_cached(id64):
    return (id64 in POWERS, POWERS.get(id64))
def fake_fetch(ids, callback):
    for id64 in [i for i in dict.fromkeys(ids) if i not in POWERS]:        # like the real lookup, only those not already known
        asked.append(id64)
        POWERS[id64] = "Aisling Duval" if id64 % 3 == 0 else "Zemina Torval"
        callback(id64, POWERS[id64])
powerplay_control_lookup.cached = fake_cached
powerplay_control_lookup.fetch_missing = fake_fetch
power = heads.index("Controlling Power")

window.refresh("Lave", LAVE, None, None, None)
check(window._mine_check.cget("state") == "disabled", "Only my Power is unavailable until the commander's Power is known")
window._mine_var.set(True)
window._apply_filters()
check(len(rows(window)) == 10 and len(asked) <= 10, f"so ticking it changes nothing: ten rows, and Spansh is asked only about those ({len(asked)})")
asked.clear()
POWERS.clear()

window.refresh("Lave", LAVE, None, None, "Aisling Duval")
for _ in range(60):
    root.update()
mine = rows(window)
expected = [e for e in rare_goods.candidates(LAVE) if e["spanshId64"] % 3 == 0][:10]
check([r[0] for r in mine] == [e["rare"] for e in expected], f"Only my Power shows the nearest ten origin systems of that Power: {[r[0] for r in mine]}")
check(all(r[power] == "Aisling Duval" for r in mine), f"each shows the Power: {[r[power] for r in mine]}")
check(0 < len(asked) < rare_goods.dataset_size(), f"Spansh was asked about some origin systems, not all of them: {len(asked)} of {rare_goods.dataset_size()}")

window._large_var.set(True)
window._apply_filters()
for _ in range(60):
    root.update()
both = rows(window)
check(both and all(r[pad] == "L" and r[power] == "Aisling Duval" for r in both), f"the two filters work together: {[(r[pad], r[power]) for r in both]}")

window.refresh("Lave", LAVE, None, None, "Nobody Nowhere")
for _ in range(120):
    root.update()
none = rows(window)
check(len(none) == 1 and "no rare good matches" in none[0][0], f"a Power that controls none of them says so: {none}")
window._mine_var.set(False)
window._large_var.set(False)
window._apply_filters()

window.refresh("Somewhere", None)
waiting = rows(window)
check(len(waiting) == 1 and len(waiting[0]) == len(heads) and "waiting" in waiting[0][0], f"no position: one waiting row with every column: {waiting}")

window.close()
root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("RARE GOODS OK")
