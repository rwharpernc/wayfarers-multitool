"""Opens the real Space Mining Book (plugin/mining_ring_book.py) with EDMC stubbed and the history faked: the rings listed with their hotspots, tons and notes, finding, the favorite star, saving
a note, copying a system, removing only a ring added by hand, and the ring added by hand showing up. Run by test_mining_ring_book_smoke in a subprocess so the stand-ins never leak into other
tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
import tempfile
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


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes", "psutil",
          "ttkHyperlinkLabel", "myNotebook", "theme"):
    sys.modules[n] = Any(n)
saved = {}


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


cfgmod = types.ModuleType("config")
cfgmod.appname = "EDMarketConnector"
cfgmod.config = Cfg()
cfgmod.user_agent = "WFMT-test"
cfgmod.appversion = lambda: "5.13.0"
sys.modules["config"] = cfgmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()

from plugin import mining_history, mining_location, mining_ring_book as B, mining_rings, mining_rings_data as RD  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


RING_A, RING_B = "Alpha 1 A Ring", "Beta 2 B Ring"
RINGS = {RD.ring_key(RING_A): {**RD.new_ring(RING_A, "Alpha"), "hotspots": {"Painite": 3, "Platinum": 2}, "class": "eRingClass_Icy", "reserve": "MajorResources", "seen": "2026-01-01"},
         RD.ring_key(RING_B): {**RD.new_ring(RING_B, "Beta"), "hotspots": {"Gold": 1}}}
RUNS = [{"ring": RING_A, "system": "Alpha", "start": "2026-01-05T10:00:00Z", "refined": {"Painite": 60}}]

history = mining_history.history
history.rings = lambda: RINGS
history.runs = lambda: RUNS
history.ready = True
history._cmdr = "Bocheaux"
mining_rings.notes.start(tempfile.mkdtemp())
mining_rings.notes.set_commander("Bocheaux")


def rows(book):
    table = book._table
    return [table._rows[iid].values for iid in table._order]


B.show(root)
book = B._window
root.update()
shown = rows(book)
check(len(shown) == 2 and shown[0][1] == RING_A, f"two rings, the one mined most first: {[r[1] for r in shown]}")
check(shown[0][3] == "Painite 3, Platinum 2" and shown[0][4] == "Icy" and shown[0][5] == "Major" and shown[0][6] == "60" and shown[0][7] == "2026-01-05", f"its row: {shown[0]}")
check("2 rings, 60 t mined" in book._shell._subtitle.cget("text") if hasattr(book._shell, "_subtitle") else True, "the subtitle counts the rings and tons")

book._find.set("gold")
book.refresh()
check([r[1] for r in rows(book)] == [RING_B], f"Find narrows by a mineral: {[r[1] for r in rows(book)]}")
book._find.set("")
book.refresh()

book._table.select(RD.ring_key(RING_B), notify=True)
check("Beta" in book._detail.cget("text") and "Gold 1" in book._detail.cget("text") and "Not mined yet" in book._detail.cget("text"), f"the detail card: {book._detail.cget('text')!r}")
book._note.set("  my   best gold ring ")
book._save_note()
check(mining_rings.notes.entries()[RD.ring_key(RING_B)]["note"] == "my best gold ring", "a note is saved")
book._toggle_favorite()
root.update()
check(rows(book)[0][1] == RING_B and rows(book)[0][0] == "★", f"a favorite goes to the top with a star: {rows(book)[:2]}")
book._favorites.set(True)
book.refresh()
check([r[1] for r in rows(book)] == [RING_B], "Favorites only")
book._favorites.set(False)
book.refresh()

book._table.select(RD.ring_key(RING_B), notify=True)
book._copy_system()
check(root.clipboard_get() == "Beta", f"Copy system: {root.clipboard_get()!r}")
book._remove()
check("Only a ring you added by hand" in book._shell._status.cget("text") and len(rows(book)) == 2, "a ring from the journals cannot be removed")

mining_rings.notes.add_manual("Gamma 3 A Ring", "Gamma", {"Alexandrite": 2}, "Rocky", "Pristine")
book.refresh()
check(len(rows(book)) == 3 and any(r[1] == "Gamma 3 A Ring" and r[3] == "Alexandrite 2" for r in rows(book)), "a ring added by hand is listed")
book._table.select(RD.ring_key("Gamma 3 A Ring"), notify=True)
check("Added by hand" in book._detail.cget("text"), "and says so")
book._remove()
check(len(rows(book)) == 2, "and it can be removed")

# while the journals are first read: a visible notice, and no redraw of an unchanged list (it flickered)
history.ready = False
history.reading = "Reading your journals for the mining history (40%)"
cleared = []
real_clear = book._table.clear
book._table.clear = lambda: (cleared.append(1), real_clear())[1]
book.refresh()
book.refresh()
check("Reading your journals for rings and mining (40%)" in book._banner.cget("text"), f"the notice shows how far the read has got: {book._banner.cget('text')!r}")
check(len(cleared) == 0, f"an unchanged list is not redrawn while reading: {len(cleared)} redraws")
history.reading = ""
history.ready = True
book.refresh()
check(book._banner.cget("text") == "", "the notice goes when the read is done")
RINGS[RD.ring_key("Delta 4 A Ring")] = {**RD.new_ring("Delta 4 A Ring", "Delta"), "hotspots": {"Osmium": 1}}
book.refresh()
check(len(cleared) == 1 and len(rows(book)) == 3, f"a changed list is redrawn once: {len(cleared)} redraws, {len(rows(book))} rows")

# This system: go to the ring in the system you are in, or say you have not worked it
book._status_text = lambda: book._shell._status.cget("text")
book._find_here()
check("does not know your current system" in book._status_text(), f"no system known yet: {book._status_text()!r}")
mining_location.set_current_system("Nowhere")
book._find_here()
check(book._status_text() == "You have not worked this system yet.", f"a system with no ring says so: {book._status_text()!r}")
book._find.set("zzz")
book._favorites.set(True)
mining_location.set_current_system("Alpha")
book._find_here()
check(book._find.get() == "Alpha" and not book._favorites.get(), "a filter that would hide the match is replaced by the system, which keeps it")
check(book._table.selection() == [RD.ring_key(RING_A)] and "Alpha 1 A Ring" in book._status_text(), f"it goes to the ring in the system: {book._table.selection()} {book._status_text()!r}")

# A long list draws only the first rows (a label per cell makes thousands slow to open and close); Find reaches the rest
book._find.set("")
book._favorites.set(False)
B.MAX_ROWS = 2
book.refresh()
check(len(rows(book)) == 2 and "showing the first 2 of 3" in book._shell._subtitle.cget("text"), f"the table is capped and says so: {len(rows(book))} {book._shell._subtitle.cget('text')!r}")
book._find.set("gold")
book.refresh()
check(len(rows(book)) >= 1 and "showing the first" not in book._shell._subtitle.cget("text"), "a narrower Find reaches rows beyond the cap")
B.MAX_ROWS = 150

book.close()
root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("RING BOOK OK")
