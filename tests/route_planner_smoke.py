"""Opens the real Route Planner (plugin/route_planner_panel.py, route_planner_window.py) with EDMC stubbed and Spansh faked: the panel button and tickbox, the ship read from a
Loadout, a plot (no jump range asked for), the route table and the Route overlay's card, following the route and the automatic copy, making an expedition, and the Dashboard header
button. Run by test_route_planner_smoke in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
import time
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
          "win32process", "win32clipboard", "pywintypes", "psutil", "ttkHyperlinkLabel"):
    sys.modules[n] = Any(n)
nbmod = Any("myNotebook")
nbmod.Frame, nbmod.Label, nbmod.Button, nbmod.Checkbutton = tk.Frame, tk.Label, tk.Button, tk.Checkbutton
sys.modules["myNotebook"] = nbmod
theme = Any("theme")
theme.theme = mock.MagicMock()
theme.theme.active = None
theme.theme.THEME_DEFAULT = 0
sys.modules["theme"] = theme
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

from plugin import explore_dashboard as DASH, route_planner_panel as PANEL, route_planner_window as WIN, route_overlay, spansh_exact, spansh_planners  # noqa: E402
from plugin.uikit import palette as UP  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)

STAR_DATA = {}                                         # what "Spansh" says about each system's stars, by address (the real lookup would use the network)
spansh_exact.fetch_stars = lambda id64: STAR_DATA.get(id64)
check(PANEL.controller.auto_copy is True, "copying the next system to the clipboard is on by default")
PANEL.controller.auto_copy = False                 # the rest of this script starts from the opt-out and switches it on
saved["wfmt_neutron_plotter_auto_copy"] = False


def pump(times=4):
    for _ in range(times):
        root.update()


def texts(widget):
    found = []
    if isinstance(widget, tk.Label):
        found.append(str(widget.cget("text")))
    for child in widget.winfo_children():
        found.extend(texts(child))
    return found


def all_text(widget):
    return "\n".join(texts(widget))


LOADOUT = {"event": "Loadout", "Ship": "explorer_nx", "Ship_Localised": "Caspian Explorer", "ShipName": "Stellar Mantis", "ShipIdent": "MA-X7N", "UnladenMass": 1532.1,
           "MaxJumpRange": 53.4283, "FuelCapacity": {"Main": 224.0, "Reserve": 1.14},
           "Modules": [{"Slot": "FrameShiftDrive", "Item": "int_hyperdrive_overcharge_size8_class5_overchargebooster_mkii",
                        "Engineering": {"Modifiers": [{"Label": "FSDOptimalMass", "Value": 6304.5}]}}]}
RESULT = {"jumps": [
    {"name": "Sol", "id64": 1, "distance": 0, "distance_to_destination": 300.0, "fuel_in_tank": 224, "fuel_used": 0, "has_neutron": False},
    {"name": "Alpha Neutron", "id64": 2, "distance": 120.5, "distance_to_destination": 179.5, "fuel_in_tank": 218.0, "fuel_used": 6.0, "has_neutron": True, "x": 1, "y": 2, "z": 3},
    {"name": "Beta", "id64": 3, "distance": 99.5, "distance_to_destination": 80.0, "fuel_in_tank": 212.0, "fuel_used": 6.0, "has_neutron": False, "must_refuel": True},
    {"name": "Gamma", "id64": 4, "distance": 80.0, "distance_to_destination": 0.0, "fuel_in_tank": 206.0, "fuel_used": 6.0, "has_neutron": True}]}
asked = []


def fake_job(url, form, cancel=None, on_state=None, slow_hint=""):
    asked.append((url, dict(form)))
    return RESULT


def fake_lookup(name):
    asked.append(("lookup", name))
    return 3238296097059, name.title()


# --- the panel button and tickbox are visible, and the ship is learned from the game ---------------------------------------------------
frame = tk.Frame(root)
frame.pack()
PANEL.build_panel(frame)
pump()
def descendants(widget):
    """Every widget under `widget` (not in other windows): the section builds its controls into a folding body frame."""
    found = []
    for child in widget.winfo_children():
        if isinstance(child, tk.Toplevel):
            continue                      # the plotting window is a child of the panel too
        found.append(child)
        found.extend(descendants(child))
    return found


all_buttons = [w for w in descendants(frame) if isinstance(w, tk.Button)]
buttons = [b for b in all_buttons if b.winfo_manager()]
check(sorted(b.cget("text") for b in buttons) == ["CLEAR ROUTE", "PLOT"], "the panel shows PLOT and CLEAR ROUTE, with or without a route: %s" % [b.cget("text") for b in buttons])
titles = [w.cget("text") for w in frame.winfo_children() if isinstance(w, tk.Label)]
check(any("Route Planner" in t and t.startswith("▸") for t in titles), "the section has a folding title and starts folded: %s" % titles)
check(sorted(b.cget("text") for b in all_buttons) == ["CLEAR ROUTE", "PLOT"], "the panel has a CLEAR ROUTE button")
# EDMC started after the game: no Loadout was seen, so the plotter reads the ship from the journals
from plugin import ship_current  # noqa: E402
ship_current.latest_loadout = lambda folder=None: LOADOUT
check(PANEL.controller.ship.loadout is None, "no ship is known before any Loadout was seen")
check(PANEL.controller.learn_ship() is True and PANEL.controller.ship.loadout is not None, "the ship is read from the journals when no Loadout was seen")
check("Stellar Mantis" in PANEL.controller.ship.name() or PANEL.controller.ship.name() != "", "the ship has a name once read")
PANEL.controller.ship.loadout = None
ship_current.latest_loadout = lambda folder=None: None
check(PANEL.controller.learn_ship() is False, "with no Loadout in the journals the ship stays unknown")
PANEL.handle_event(LOADOUT, "CMDR A", None, None, {})
PANEL.handle_event({"event": "FSDJump", "StarSystem": "Sol", "SystemAddress": 10477373803}, "CMDR A", "Sol", None, {})
PANEL.dashboard_status({"Cargo": 12, "Fuel": {"FuelMain": 100.0}})
PANEL.open_window()
pump(8)
check(WIN.is_open(), "the window opened from the panel")
window = WIN._window
ship_text = all_text(window._ship_block)
check("Stellar Mantis (MA-X7N)" in ship_text and "Class 8, Rating A" in ship_text and "6,304.5 t" in ship_text and "Yes (6x)" in ship_text, "the ship block shows the expected ship values: %s" % ship_text.replace("\n", " | "))
check("12 t" in ship_text, "the ship block shows the cargo")
check("range" not in window._vars and "type your jump range" not in all_text(window._shell.window).lower() and "jump range" not in ship_text.lower(), "the window has no jump range to type, and the ship block shows none")
check(window._vars["start"].get() == "Sol", "the source is the system the commander is in")
before_block = ship_text
PANEL.dashboard_status({"Cargo": 12, "Fuel": {"FuelMain": 90.0}})
pump()
check(all_text(window._ship_block) == before_block, "burning fuel does not change the ship block")

help_text = " ".join(" ".join(item) for item in WIN.HELP)
check("Best for" in help_text and "Long trips" in help_text and "paste each system into the galaxy map" in help_text and "ready to paste" in help_text, "Help tells the commander when it is worth using and that each system is pasted by hand")
check("Long trips" not in all_text(window._shell.window), "the explanation is behind Help, not a paragraph in the window")
window._shell._show_help()
check(window._shell._help_window is not None and window._shell._help_window.winfo_exists(), "Help opens a window")
window._shell._help_window.destroy()

# --- a missing destination is refused, then a plot -------------------------------------------------------------------------------------
window._plot()
check(not window._busy and "go to" in window._shell._status.cget("text"), "plotting without a destination is refused")
window._vars["end"].set("colonia")
auto_boxes = [w for w in descendants(frame) if isinstance(w, tk.Checkbutton)]
check(len(auto_boxes) == 1 and "clipboard" in auto_boxes[0].cget("text"), "the panel has the auto-copy tickbox")
root.clipboard_clear()
root.clipboard_append("something else")
auto_boxes[0].invoke()
pump()
check(PANEL.controller.auto_copy and saved.get("wfmt_neutron_plotter_auto_copy") is True, "ticking the panel box switches auto-copy on and remembers it")
check(window._auto.get() is True or window._auto.get() == 1, "the window's tickbox follows the panel's")
check(root.clipboard_get() == "something else", "with no route yet, switching it on copies nothing")
window._flags["use_injections"].set(True)
window._algorithm.set("Guided")
with mock.patch.object(spansh_exact, "lookup_system", fake_lookup), mock.patch.object(spansh_planners, "fetch_job", fake_job):
    window._plot()
    deadline = time.monotonic() + 10
    while window._busy and time.monotonic() < deadline:       # the worker thread and the after() poll need real time
        pump(1)
        time.sleep(0.05)
check(not window._busy, "the plot finished")
route_calls = [a for a in asked if a[0] == spansh_exact.ROUTE_URL]
check(len(route_calls) == 1, "Spansh's exact plotter was asked once (asked %s)" % [a[0] for a in asked])
form = route_calls[0][1] if route_calls else {}
check(form.get("source") == "10477373803" and form.get("destination") == "3238296097059", "the form has the source's address from the game and the destination looked up: %s" % form)
check(form.get("cargo") == "12" and form.get("optimal_mass") == "6304.5" and form.get("supercharge_multiplier") == "6" and form.get("tank_size") == "224", "the ship's numbers are sent: %s" % form)
check(form.get("use_injections") == "1" and form.get("algorithm") == "guided", "the choices are sent")
check("range" not in form and "jump_range" not in form, "no jump range is sent")
check(("lookup", "Sol") not in asked, "the source is not looked up when the game gave its address")
check("guided" in saved.get("wfmt_neutron_plotter_options", ""), "the choices are remembered")
check(len(window._table.table) == 3, "the route table has three jumps (got %s)" % len(window._table.table))
check("3 jumps" in window._summary.cget("text") and "Alpha Neutron" in window._summary.cget("text"), "the summary names the next jump")
check("Next: Alpha Neutron" in all_text(frame), "the panel line names the next system")
check(root.clipboard_get() == "Alpha Neutron", "with auto-copy on, plotting puts the first system on the clipboard")
check("copied" in all_text(frame), "the panel line says the next system is copied")
check(route_overlay.active_neutron_route() is PANEL.controller.route, "the Route overlay is given the plotted route")
card = route_overlay.get_state().card()
check(card.header[0] == ("You are navigating to:", "muted") and card.header[1][0] == PANEL.controller.route.end, "the Route overlay's card says where the planned route goes: %s" % (card.header,))
check(card.rows == (("Alpha Neutron", "NEUTRON", "info"), ("Beta", "NO FUEL", "warn"), ("Gamma", "NEUTRON", "info")), "the card lists the systems with their star in a color (blue neutron, yellow no fuel): %s" % (card.rows,))

# --- following the route ---------------------------------------------------------------------------------------------------------------
window._copy_all()
check(root.clipboard_get() == "Alpha Neutron\nBeta\nGamma", "Copy all puts the remaining systems on the clipboard")
PANEL.handle_event({"event": "FSDJump", "StarSystem": "Alpha Neutron", "SystemAddress": 2}, "CMDR A", "Alpha Neutron", None, {})
pump(4)
check(PANEL.controller.route.reached == 1, "arriving moves along the route")
check(root.clipboard_get() == "Beta", "arriving copies the next system when asked")
check("Next: Beta" in all_text(frame), "the panel line follows the route")
check(all_text(window._ship_block) == before_block, "the ship block did not change while the route was plotted and followed")
PANEL.controller.set_auto_copy(False)
check(saved.get("wfmt_neutron_plotter_auto_copy") is False, "switching it off is remembered")
PANEL.handle_event({"event": "FSDJump", "StarSystem": "Beta", "SystemAddress": 3}, "CMDR A", "Beta", None, {})
pump(4)
check(PANEL.controller.route.reached == 2 and root.clipboard_get() == "Beta", "with auto-copy off, arriving moves along the route but leaves the clipboard alone")
window._copy_next()
check(root.clipboard_get() == "Gamma", "Copy next system copies on request")

# --- a ship Spansh cannot be told about, and an unknown destination ------------------------------------------------------------------------
window._vars["end"].set("nowhere")
with mock.patch.object(spansh_exact, "lookup_system", side_effect=spansh_exact.RouteSearchError("Spansh does not know a system called 'nowhere'. Check the spelling.")):
    window._plot()
    deadline = time.monotonic() + 10
    while window._busy and time.monotonic() < deadline:
        pump(1)
        time.sleep(0.05)
check("does not know a system" in window._activity.cget("text"), "an unknown destination is explained in the window")

# --- the expedition buttons ------------------------------------------------------------------------------------------------------------------
def flat_buttons(widget):
    """Every FlatButton (a label that acts as a button) under a widget, by its text."""
    found = {}
    for child in widget.winfo_children():
        found.update(flat_buttons(child))
        if type(child).__name__ == "FlatButton":
            found[str(child.cget("text"))] = child
    return found


buttons_in_window = flat_buttons(window._shell.window)
check({"Start expedition", "Review", "Copy next system", "Clear route", "Carrier route"} <= set(buttons_in_window), "the window has Start expedition, Review and the route buttons: %s" % sorted(buttons_in_window))
check("Make an expedition" not in buttons_in_window and "Expedition" not in buttons_in_window, "the old Make an expedition and Expedition buttons are gone")
said = PANEL.controller.start_expedition()
check("Log in" in said or "no commander" in said, "an expedition needs a commander (said: %s)" % said)
said = PANEL.controller.review_expedition()
check("Log in" in said or "no commander" in said, "Review needs one too (said: %s)" % said)

# --- the confirmation on the button -------------------------------------------------------------------------------------------------------------
start_button = window._start
with mock.patch.object(window._ctx, "start_expedition", return_value="Started 'Run': 3 stops. Logging in Expedition Log."):
    window._start_expedition()
check(str(start_button.cget("text")).startswith("Started") and str(start_button.cget("fg")) == UP.OK, "a started expedition shows on the button: %s" % start_button.cget("text"))
check(str(window._shell._status.cget("fg")) == UP.OK and "Started 'Run'" in str(window._shell._status.cget("text")), "and in the status line's success color")
window._restore_start()
check(str(start_button.cget("text")) == "Start expedition", "the button goes back to its name")
with mock.patch.object(window._ctx, "start_expedition", return_value="Plot a route first."):
    window._start_expedition()
check(str(start_button.cget("text")) == "Start expedition" and str(window._shell._status.cget("fg")) != UP.OK, "a start that did not happen shows no confirmation")

import tempfile as _tempfile  # noqa: E402
from plugin import expedition, expedition_log, expedition_log_panel, expedition_panel, expedition_window  # noqa: E402

expedition_folder = _tempfile.mkdtemp()
trips, runs = expedition_panel.book, expedition_log_panel.book
trips.load(expedition_folder)
runs.load(expedition_folder)
trips.set_commander("CMDR A")
runs.set_commander("CMDR A")


def a_route(end="Colonia", suspect=()):
    route = PANEL.NP.Route("Sol", end, PANEL.NP.legs_from_result(RESULT))
    route.suspect.update(suspect)
    return route


maker = PANEL.PlotterController()
check(maker.start_expedition() == "Plot a route first.", "Start expedition with no route says to plot one")
maker.route = a_route(suspect={"alpha neutron"})
check(PANEL.expedition_name(maker.route) == "Neutron Highway from Sol to Colonia", "the expedition is named from the route: %s" % PANEL.expedition_name(maker.route))
stops = PANEL.route_stops(maker.route)
check([s[0] for s in stops] == ["Alpha Neutron", "Beta", "Gamma"], "the stops are the neutron stars, the refuel stop and the destination: %s" % [s[0] for s in stops])
check(stops[0][2] == "neutron: may be a secondary star, check" and stops[1][2] == "refuel" and stops[2][2] == "neutron: supercharge" and stops[0][3] == (1.0, 2.0, 3.0),
      "each stop says what to do there, with the secondary-star note and the position: %s" % (stops,))
maker.route.reached = 1
check([s[0] for s in PANEL.route_stops(maker.route)] == ["Beta", "Gamma"], "only the stops still ahead are used")
maker.route.reached = 0

# Review makes the expedition without starting it, and picks it for the Expedition window (which is closed)
review_id, said = maker.make_expedition(start=False)
made = trips.get(review_id)
check(made is not None and made.status == expedition.PLANNED and len(made.stops) == 3 and "not started" in said, "Review makes it without starting: %s" % said)
check(made.name == "Neutron Highway from Sol to Colonia" and [s.note for s in made.stops][:2] == ["neutron: may be a secondary star, check", "refuel"],
      "with the route's name and the notes: %s" % ([s.note for s in made.stops],))
check(runs.active() is None and expedition_window._wanted == made.id, "no log run is started, and the closed Expedition window will pick it")

# Start expedition on the same route starts that expedition: no duplicate, a linked log run, and it is picked
began_id, said = maker.make_expedition(start=True)
check(began_id == made.id and len(trips.expeditions()) == 1, "pressing Start expedition after Review starts the same expedition (%d expeditions)" % len(trips.expeditions()))
check(made.status == expedition.ACTIVE and runs.active() is not None and made.log_run_id == runs.active().id and runs.active().name == made.name, "it is running with a linked log run")
check(said == "Started 'Neutron Highway from Sol to Colonia': 3 stops. Logging in Expedition Log.", "it says what happened: %s" % said)
again_id, said = maker.make_expedition(start=True)
check(again_id == made.id and len(trips.expeditions()) == 1 and len(runs.runs()) == 1 and "already running" in said, "a second press makes no duplicate and no second run: %s" % said)
check(maker.review_expedition().endswith("(active).") and len(trips.expeditions()) == 1, "Review for a running expedition finds it")

# a new plot, and Clear route, leave the running expedition alone
maker.set_route(a_route("Elsewhere"))
check(made.status == expedition.ACTIVE and len(made.stops) == 3 and runs.active().id == made.log_run_id, "plotting another route leaves the running expedition as it was")
maker.clear_route()
check(made.status == expedition.ACTIVE and len(made.stops) == 3 and runs.active().id == made.log_run_id, "Clear route leaves it too")

# a different route is a different expedition; with the setting off no log run is started
saved["wfmt_expedition_start_log"] = False
maker.set_route(a_route("Colonia Two"))
other_id, said = maker.make_expedition(start=True)
other = trips.get(other_id)
check(other_id != made.id and other.status == expedition.ACTIVE and other.log_run_id == "" and "Logging" not in said, "with the setting off no log run is started: %s" % said)
check(made.status == expedition.PAUSED and runs.get(made.log_run_id).status == expedition_log.PAUSED, "and the one that was running is set aside, with its run held")
saved["wfmt_expedition_start_log"] = True
paused_id, said = maker.make_expedition(start=True)
check(paused_id == other_id and other.status == expedition.ACTIVE, "pressing it again for a running one leaves it alone")
maker.set_route(a_route())
check(maker.make_expedition(start=True)[1].startswith("'Neutron Highway from Sol to Colonia' is paused."), "a paused expedition for the same plot is picked, not duplicated, and Start tells where to carry on")
check(len(trips.expeditions()) == 2, "still two expeditions")
trips.finish(made.id)
runs.stop(made.log_run_id)
again_id, said = maker.make_expedition(start=True)
check(again_id not in (made.id, other_id) and "(2)" in trips.get(again_id).name, "once the first is stopped, the same route makes a new one: %s" % trips.get(again_id).name)

# the Expedition window opens on the one asked for, whichever is running
maker._parent = None
expedition_panel.controller._parent = frame
expedition_panel.open_window(select=made.id)
pump(4)
check(expedition_window._window.alive and expedition_window._window._picked == made.id, "Review's window opens on the expedition asked for, though another is running")
expedition_window.select(again_id)
check(expedition_window._window._picked == again_id, "and selects another when asked while open")
expedition_window.close()
pump()
expedition_panel.controller._parent = None

# --- the wait line does not move while plotting ------------------------------------------------------------------------------------------
import time as _time
window._busy, window._started, window._activity_text = True, _time.monotonic(), ""
texts_seen = set()
for phase in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
    window._phase = phase
    window._animate()
    texts_seen.add(window._activity.cget("text"))
check(len(texts_seen) == 1, "the wait line changed between animation frames within one second (its dots moved the text): %s" % texts_seen)
check(all("..." not in text and text.startswith("Plotting") for text in texts_seen), "the wait line has no animated dots: %s" % texts_seen)
window._busy = False
window._animate()
window._finished()

# --- abandoning the route ---------------------------------------------------------------------------------------------------------------
clear_button = next(b for b in descendants(frame) if isinstance(b, tk.Button) and b.cget("text") == "CLEAR ROUTE")
check(clear_button.winfo_manager() == "grid", "CLEAR ROUTE shows on the panel while a route is plotted")
game_state = route_overlay.get_state()
game_state.tracker.set_route([route_overlay.Hop("Sol", "G", (0.0, 0.0, 0.0)), route_overlay.Hop("Somewhere", "K", (10.0, 0.0, 0.0))])
game_state.tracker.system = "Sol"
check(bool(game_state.tracker.remaining()), "the Route overlay is following a game route too")
PANEL.controller.copied = "Gamma"
window._clear_route()
pump(4)
check(PANEL.controller.route is None and PANEL.controller.copied == "", "clearing drops the route and what was copied")
check(clear_button.winfo_manager() == "grid", "CLEAR ROUTE stays on the panel")
check(not game_state.tracker.route, "clearing also drops the game route the Route overlay was following, so its card closes")
check(not game_state.card(), "and the Route overlay has nothing to draw")
check(len(window._table.table) == 0, "the window's table is empty after clearing")
check(route_overlay.active_neutron_route() is None, "the Route overlay is no longer given a neutron route")
check(not route_overlay.get_state().card().rows or route_overlay.get_state().card().header[1][0] != "Colonia", "the Route overlay no longer shows the planned route")
check("Route cleared" in window._shell._status.cget("text"), "the window says the route was cleared")
window._clear_route()
check("no route" in window._shell._status.cget("text"), "clearing with no route says so")
check(PANEL.controller.clear_route() is False, "clearing again reports there was nothing to clear")

# --- a neutron star that is a secondary star is flagged -----------------------------------------------------------------------------------
STAR_DATA[2] = [{"name": "Alpha Neutron", "subtype": "F (White) Star", "is_main_star": None}, {"name": "PSR J0000+0000", "subtype": "Neutron Star", "is_main_star": True}]
STAR_DATA[4] = [{"name": "Gamma", "subtype": "Neutron Star", "is_main_star": True}]
watcher = PANEL.PlotterController()
watcher.set_route(PANEL.NP.Route("Sol", "Colonia", PANEL.NP.legs_from_result(RESULT)))
for _ in range(60):
    if not watcher._checker.busy():
        break
    time.sleep(0.05)
watcher._poll_checks()
check(watcher.route.suspect == {"alpha neutron"}, "a neutron stop whose neutron star is a secondary star is flagged: %s" % watcher.route.suspect)
check(watcher.route.checked == {"alpha neutron", "gamma"}, "and every neutron stop ahead was looked at once: %s" % watcher.route.checked)
shown = route_overlay.build_neutron_card(watcher.route, 8)
check(shown.rows[0][:3] == ("Alpha Neutron", "NEUTRON ?", "warn") and shown.rows[2][1] == "NEUTRON", "the overlay marks it NEUTRON ? in yellow and leaves the others: %s" % (shown.rows,))
check("secondary star" in WIN.route_table(watcher.route).rows[0].cells[5], "the window's table says so: %s" % WIN.route_table(watcher.route).rows[0].cells)
watcher.check_ahead()
check(not watcher._checker.busy(), "a stop already looked at is not asked about again")

# --- the route survives a restart, per commander -------------------------------------------------------------------------------------------
import tempfile  # noqa: E402

folder = tempfile.mkdtemp()
first = PANEL.PlotterController()
first.start(folder)
first.handle_event({"event": "Music", "MusicTrack": "NoTrack"}, "Bocheaux", "Sol", None, {})
first.set_route(PANEL.NP.Route("Sol", "Colonia", PANEL.NP.legs_from_result(RESULT)))
first.handle_event({"event": "FSDJump", "StarSystem": "Alpha Neutron", "SystemAddress": 2}, "Bocheaux", "Alpha Neutron", None, {})
check(first.route.reached == 1, "arriving at a leg moves along the route")
second = PANEL.PlotterController()                                   # EDMC restarted
second.start(folder)
check(second.route is None, "before the commander is known nothing is restored")
second.handle_event({"event": "StartUp"}, "bocheaux", "Alpha Neutron", None, {})
check(second.route is not None and second.route.next_leg.system == "Beta" and second.route.end == "Colonia", "after a restart the route is back, where the commander was on it")
other = PANEL.PlotterController()
other.start(folder)
other.handle_event({"event": "StartUp"}, "Someone Else", "Sol", None, {})
check(other.route is None, "another commander does not get the route")
second.clear_route()
third = PANEL.PlotterController()
third.start(folder)
third.handle_event({"event": "StartUp"}, "Bocheaux", "Sol", None, {})
check(third.route is None, "a cleared route is not restored")
finished = PANEL.PlotterController()
finished.start(folder)
finished.handle_event({"event": "StartUp"}, "Bocheaux", "Sol", None, {})
finished.set_route(PANEL.NP.Route("Sol", "Colonia", PANEL.NP.legs_from_result(RESULT), reached=3))
again = PANEL.PlotterController()
again.start(folder)
again.handle_event({"event": "StartUp"}, "Bocheaux", "Sol", None, {})
check(again.route is None, "a route that was already finished is not restored")
early = PANEL.PlotterController()
early.start(folder)
early.set_route(PANEL.NP.Route("Sol", "Colonia", PANEL.NP.legs_from_result(RESULT)))      # plotted before the commander is known
early.handle_event({"event": "StartUp"}, "Bocheaux", "Sol", None, {})
check(early.route is not None, "a route plotted before the commander is known is kept")
late = PANEL.PlotterController()
late.start(folder)
late.handle_event({"event": "StartUp"}, "Bocheaux", "Sol", None, {})
check(late.route is not None and late.route.next_leg is not None, "and it is saved for the commander once known")

# --- the dashboard header opens it too ------------------------------------------------------------------------------------------------------
window.close()
pump()
check(not WIN.is_open(), "the window closed")
PANEL.controller._parent = frame
DASH.controller.open_neutron()
pump(6)
check(WIN.is_open(), "the Dashboard's header button opens the plotter")
WIN.close()
pump()

if problems:
    print("PROBLEMS:")
    for problem in problems:
        print(" -", problem)
    sys.exit(1)
print("ROUTE PLANNER OK")
