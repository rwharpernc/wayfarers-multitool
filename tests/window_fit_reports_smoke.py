"""Builds the report pop-out windows (Missions, Source commodities, BGS Report and Powerplay Sessions with all of its tabs) with EDMC stubbed and long data (60-character
station and faction names, 40-character system names, 24-character commander names, credits in the billions), and runs the layout checker (window_fit_check.py) at the
window's minimum size, 640 px wide and 1600 px wide. Fails on text cut off, controls pushed outside the window, labels that cannot wrap and tables whose columns do not fit
or do not use a wide window. Run by test_window_fit_reports_smoke.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not,
77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
import tkinter as tk
import window_fit_check as F

saved = F.install_edmc_stubs()
try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()

from plugin import (bgs_window, megaship_scans, mission_sources, mission_sources_window, missions_board, missions_window, powerplay_ledger as PL,  # noqa: E402
                    powerplay_window, source_picks, trade_prices)
from plugin.bgs_ledger import FactionTrack, PeriodView
from plugin.bgs_tracker import FactionActivity, FactionSnapshot
from plugin.formulas import ACTIVITIES
from plugin.powerplay import PowerplayTracker
from plugin.powerplay_systems_tab import SystemsPane, TabActions
from plugin.session import SessionManager, add_merits
from plugin.store import SessionStore

problems, notes = [], []
NOW = datetime.now(timezone.utc)
STAMP = NOW.strftime("%Y-%m-%dT%H:%M:%SZ")
FACTION = "Brotherhood of the Wayward Nomads Federal Party"[:48]      # a faction name close to the longest the game allows
POWER = "Archon Delaine of the Long Name Kind"

# --- Missions --------------------------------------------------------------------------------------------------------------------------


def mission(number, ready=False, pinned=False):
    return missions_board.Row(
        id=number, title="Deliver 12345 tons of Hydrogen Fuel Rods of the Long Name Kind to " + F.STATION, kind="Trade & Mining (surface) of the long kind",
        faction=FACTION, system=F.SYSTEM, station=F.STATION, progress="12345/12345 held", fraction=0.5, reward=F.BIG, expiry=NOW + timedelta(days=3, hours=number),
        ready=ready, wing=True, illegal=True, pinned=pinned, accepted=STAMP, expiry_text=STAMP, commodity="Hydrogen Fuel Rods of the Long Name Kind",
        needed=12345, cargo_note="12345/12345 collected, 12345 delivered")


rows = [mission(n, ready=n % 3 == 0, pinned=n % 2 == 0) for n in range(1, 13)]
win = missions_window.MissionsWindow(root, lambda: rows, lambda: F.COMMANDER, lambda: F.SYSTEM, lambda: F.SYSTEM[::-1])
F.pump(root)
win.select(3)
F.check_views(root, win._shell.window, "Missions", F.tab_views(win._tabs), problems, notes)
win.close()

# --- Source commodities ----------------------------------------------------------------------------------------------------------------
needs = [mission_sources.Need("Hydrogen Fuel Rods of the Long Name Kind", 12345, 3, F.SYSTEM), mission_sources.Need("Gold", 50, 1, F.SYSTEM, pickup=F.STATION, pickup_pad="Large")]
offer = trade_prices.Offer(F.STATION, F.SYSTEM, "Coriolis Starport", 12345.6, 123456.0, 123456, 12345, 12345, F.BIG, False, False, trade_prices.BUY, "Large")
picks = source_picks.Picks("Hydrogen Fuel Rods of the Long Name Kind", trade_prices.BUY, 12345, {kind: source_picks.Pick(kind, offer, "only 12 t in stock, also the cheapest anywhere")
                                                                                              for kind in source_picks.KINDS}, ["Spansh had no station that stocks all of it"])
sources = mission_sources_window.MissionSourcesWindow(root, lambda: needs, lambda: F.SYSTEM)
sources._results = {needs[0].commodity: picks}
sources.refresh()
sources._shell.set_status("Asking Spansh... 1 of 2 done (press Cancel to stop). " + F.NOTE)
F.pump(root)
F.check_views(root, sources._shell.window, "Source commodities", None, problems, notes)
sources.close()

# --- BGS Report ------------------------------------------------------------------------------------------------------------------------


def snapshot(system, faction, controlling):
    return FactionSnapshot(system, faction, "Civil Liberty of the long state name", "Democracy", "Federation", 0.4321, "Happy", controlling,
                           ["Boom", "Investment", "Expansion"], ["Outbreak", "Lockdown"], ["Civil War", "Election", "Famine"], STAMP)


systems = [F.SYSTEM, F.SYSTEM[::-1], "Sol", "Colonia"]
tracks, activity = [], []
for system in systems:
    for n in range(6):
        faction = f"{FACTION[:44]} {n}"
        tracks.append(FactionTrack(system, faction, snapshot(system, faction, n == 0), snapshot(system, faction, n == 0)))
        activity.append(FactionActivity(system, faction, missions=12345, inf_plus=99999, inf_minus=88888, bounty_credits=F.BIG, combat_bond_credits=F.BIG,
                                        trade_profit_credits=-F.BIG, exploration_credits=F.BIG, missions_failed=12345, missions_abandoned=12345, crimes=12345,
                                        last_at=STAMP))
views = [PeriodView(STAMP, None, True, activity, tracks), PeriodView(STAMP, STAMP, False, activity, tracks)]
bgs_window.show(root, views, F.SYSTEM, ["Sol", F.SYSTEM[::-1]], [], bgs_window.TabActions(toggle_pin=lambda s: None, close=lambda s: None, add=lambda s: None))
bwin = bgs_window._window
F.pump(root)
F.check_views(root, bwin._toplevel, "BGS Report", F.tab_views(bwin._tabs), problems, notes)
# The Discord menu: Copy for Discord puts the tick's report on the clipboard, and Post to Discord refuses until a webhook is saved (nothing is sent).
bwin._on_copy_discord()
copied = root.clipboard_get()
if not copied.startswith("**WFMT BGS report**") or "Copied for Discord" not in bwin._shell._status.cget("text"):
    problems.append(f"BGS Report: Copy for Discord did not copy the report ({copied[:60]!r}, status {bwin._shell._status.cget('text')!r})")
bwin._on_post_discord()
if "Discord tab" not in bwin._shell._status.cget("text"):
    problems.append(f"BGS Report: Post to Discord without a webhook said {bwin._shell._status.cget('text')!r}")
bwin.close()

# --- Powerplay Sessions ----------------------------------------------------------------------------------------------------------------
folder = tempfile.mkdtemp()
manager = SessionManager(SessionStore(folder))
for number in range(4):
    manager.start_session(F.COMMANDER, POWER)
    for index, system in enumerate((F.SYSTEM, F.SYSTEM[::-1], "Sol", "Colonia", F.SYSTEM + " B", F.SYSTEM + " C")):
        for activity_name in ACTIVITIES:
            add_merits(manager.current, activity_name, F.BIG // 1000 + index, system)
tracker = PowerplayTracker()
tracker.my_power, tracker.rank, tracker.total_merits = POWER, 100, F.BIG
tracker.system_name, tracker.system_state, tracker.system_powers, tracker.system_controller = F.SYSTEM, "Fortified of the long state name", [POWER, POWER], POWER

ledger = PL.PowerplayLedger()
for index, system in enumerate(systems + [F.SYSTEM + " B", F.SYSTEM + " C"]):
    ledger.record_snapshot(system, PL.Snapshot(STAMP, "Fortified of the long state name", POWER, [POWER, POWER], 0.4321, 123456, 654321))
    for activity_name in ACTIVITIES:
        ledger.record_merits(system, activity_name, F.BIG // 1000 + index, STAMP)
for index in range(5):
    ledger.record_megaship(megaship_scans.MegaShipScan(f"Megaship {F.STATION} {index}"[:60], F.SYSTEM, 1000 + index, STAMP, 12345 * index))
prefs = PL.TabPrefs(pinned=["Sol", F.SYSTEM[::-1]])
pane = SystemsPane(views=ledger.views, prefs=lambda: prefs, cmdr=lambda: F.COMMANDER, pledge=lambda: "Pledged to " + POWER, status=lambda: "Read " + F.NOTE,
                   known_systems=ledger.known_systems, actions=TabActions(lambda s: True, lambda s: None, lambda s: True))
powerplay_window.show(root, manager, tracker, F.SYSTEM, pane)
pwin = powerplay_window._window
F.pump(root)
pviews = []
for name, select in F.tab_views(pwin._tabs):
    pviews.append((name, lambda select=select: (select(), F.pump(root))))
F.check_views(root, pwin._toplevel, "Powerplay Sessions", pviews, problems, notes)
pwin._on_copy_discord()
copied = root.clipboard_get()
if not copied.startswith("**WFMT Powerplay progress**") or "Copied for Discord" not in pwin._shell._status.cget("text"):
    problems.append(f"Powerplay Sessions: Copy for Discord did not copy the progress ({copied[:60]!r}, status {pwin._shell._status.cget('text')!r})")
pwin._on_post_discord()
if "Discord tab" not in pwin._shell._status.cget("text"):
    problems.append(f"Powerplay Sessions: Post to Discord without a webhook said {pwin._shell._status.cget('text')!r}")
pwin._copy_progress()
if "inara.cz" not in root.clipboard_get():
    problems.append("Powerplay Sessions: the plain Copy Progress no longer copies the Inara lines")
powerplay_window.close()

root.destroy()
for line in notes:
    print("note:", line)
if problems:
    print("PROBLEMS:\n  " + "\n  ".join(problems))
    sys.exit(1)
print("WINDOW FIT REPORTS OK")
