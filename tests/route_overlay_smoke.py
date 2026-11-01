"""Exercises the Route overlay (plugin/route_overlay.py) with EDMC stubbed and the overlay, clock and route file injected: what the
card says, when it is redrawn, that every line starts at the card's left padding, and that the card clears off the route. Run by
test_route_overlay_smoke.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not."""
import os
import sys
import types
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui",
          "win32process", "win32clipboard", "pywintypes", "psutil", "ttkHyperlinkLabel", "myNotebook"):
    sys.modules[n] = Any(n)
sys.modules["ttkHyperlinkLabel"].HyperlinkLabel = mock.MagicMock()
theme = Any("theme")
theme.theme = mock.MagicMock()
theme.theme.active = None
theme.theme.THEME_DEFAULT = 0
sys.modules["theme"] = theme


class Cfg:
    default_journal_dir = ""

    def get_str(self, key, default=""):
        return default or ""

    def get_bool(self, key, default=False):
        return default

    def get_int(self, key, default=0):
        return default

    def get(self, key, default=None):
        return default

    def set(self, key, value):
        pass


cfgmod = types.ModuleType("config")
cfgmod.appname = "EDMarketConnector"
cfgmod.config = Cfg()
cfgmod.user_agent = "WFMT-test"
cfgmod.appversion = lambda: "5.13.0"
sys.modules["config"] = cfgmod

from plugin import overlay_placement as P  # noqa: E402
from plugin import overlay_style as S  # noqa: E402
from plugin import route_edsm as RE  # noqa: E402
from plugin import route_overlay as RO  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def route_file(*stops):
    return {"Route": [{"StarSystem": n, "StarClass": c, "StarPos": [60.0 * i, 0.0, 0.0]} for i, (n, c) in enumerate(stops)]}


ROUTE = route_file(("Sol", "G"), ("Alpha", "M"), ("Beta", "N"), ("Gamma", "K"), ("Delta", "DA"), ("Epsilon", "H"), ("Zeta", "N"))


class World:
    def __init__(self, route=ROUTE, rows=3, enabled=True, edsm=False, lookup=None):
        self.at = 1000.0
        self.drawn = []
        self.file = route
        self.cfg = RO.RouteConfig(enabled=enabled, rows=rows, edsm=edsm)
        self.asked = []

        def ask(names):
            self.asked.append(list(names))
            return lookup(names)
        checker = RE.EdsmChecker(lookup=ask, now=lambda: self.at, background=False) if lookup else None
        self.state = RO.RouteOverlay(draw=self.drawn.append, now=lambda: self.at, cfg=lambda: self.cfg, read=lambda: self.file, edsm=checker,
                                     neutron=lambda: None, neutron_done=lambda: None, reset_neutron=lambda: None)

    def event(self, name, system=None, **fields):
        self.state.handle_event({"event": name, **fields}, system)


# --- the game's plotted route becomes a card ---------------------------------------------------------------------------------------------
w = World()
w.event("NavRoute", system="Sol")
card = w.drawn[-1]
check(bool(card), "a plotted route draws a card")
check(card.title is None and card.rule_after_header, "no heading of its own: the first line is the question, and a rule sits under the header")
check(list(card.header) == [("You are navigating to:", "muted"), ("Zeta", "title"), ("You will be there in 6 jumps.", "text")], f"the three header lines: {card.header}")
check([r[0] for r in card.rows] == ["Alpha", "Beta", "Gamma"], f"the next three systems, in order, with no numbers: {card.rows}")
check(list(card.rows) == [("Alpha", "M", "ok"), ("Beta", "NEUTRON", "info"), ("Gamma", "K", "ok")], f"each with its star: a scoopable star is green, a neutron star blue: {card.rows}")
check(card.footer == ("360 LY left to jump.", "text"), f"the light years left: {card.footer}")

# --- progress along the route, then off it -------------------------------------------------------------------------------------------------
w.event("FSDJump", system="Alpha", StarSystem="Alpha", FuelUsed=3.2)
card = w.drawn[-1]
check([r[0] for r in card.rows] == ["Beta", "Gamma", "Delta"], f"a system is taken off when it is reached and the list rolls on: {card.rows}")
check(card.header[2] == ("You will be there in 5 jumps.", "text") and card.footer == ("300 LY left to jump.", "text"), f"the jump count and the light years follow: {card.header[2]} {card.footer}")
for name in ("Beta", "Gamma", "Delta", "Epsilon"):
    w.event("FSDJump", system=name, StarSystem=name, FuelUsed=3.0)
card = w.drawn[-1]
check([r[0] for r in card.rows] == ["Zeta"] and card.header[2] == ("You will be there in 1 jump.", "text"), f"one jump to go is singular, and the last system is listed: {card.header[2]} {card.rows}")
check(card.footer == ("60 LY left to jump.", "text"), f"{card.footer}")
w.event("FSDJump", system="Zeta", StarSystem="Zeta", FuelUsed=3.0)
ended = w.drawn[-1]
check([t for t, _r in ended.header] == ["Route ended.", "You have arrived at Zeta.", "The route is being reset."] and not ended.rows, f"at the destination the card says the route has ended and is being reset: {ended.header}")
w.at += RO.END_SHOW_S - 1
w.state.refresh()
check(bool(w.drawn[-1]) and w.drawn[-1].header[0][0] == "Route ended.", "the message stays up for its time")
w.at += 2
w.state.refresh()
check(not w.drawn[-1] and not w.state.tracker.route, "then the route is reset and the overlay closes")
w.state.refresh()
check(not w.state.showing(), "and stays closed")
w = World()
w.event("NavRoute", system="Sol")
w.event("FSDJump", system="Somewhere Else", StarSystem="Somewhere Else", FuelUsed=3.0)
check(not w.drawn[-1], "off the route the card clears")
w.event("NavRouteClear", system="Somewhere Else")
check(not w.drawn[-1], "a cleared route stays cleared")
none = World(route={"Route": []})
none.event("NavRoute", system="Sol")
check(not none.state.showing() and not none.drawn, "no route: nothing to show")
nopos = World(route={"Route": [{"StarSystem": "Sol", "StarClass": "G"}, {"StarSystem": "Alpha", "StarClass": "M"}]})
nopos.event("NavRoute", system="Sol")
check(nopos.drawn[-1].footer is None and nopos.drawn[-1].header[2] == ("You will be there in 1 jump.", "text"), "a route without positions leaves the light years line out rather than guess")
more = World(rows=3)
more.event("NavRoute", system="Sol")
check(len(more.drawn[-1].rows) == 3 and more.drawn[-1].header[2][0] == "You will be there in 6 jumps.", "only the rows setting's worth of systems is listed, but the jump count is the whole route")
check(not any("Fuel" in t or "Range" in t or "supercharge" in t.lower() for t, _r in more.drawn[-1].header), "no fuel, range or supercharge lines")

# --- CLEAR ROUTE forgets the game route the card is following -----------------------------------------------------------------------------
w = World()
w.event("NavRoute", system="Sol")
check(bool(w.drawn[-1]), "a game route is on the card")
check(w.state.forget_game_route() is True and not w.drawn[-1], "forgetting it closes the card")
check(w.state.forget_game_route() is False, "and forgetting again says there was nothing")
w.event("NavRoute", system="Sol")
check(bool(w.drawn[-1]), "a new route plotted in the game is followed again")

# --- off, redraw rate --------------------------------------------------------------------------------------------------------------------------
off = World(enabled=False)
off.event("NavRoute", system="Sol")
check(off.drawn == [], "nothing is drawn while the overlay is off")
w = World()
w.event("NavRoute", system="Sol")
count = len(w.drawn)
w.state.refresh()
check(len(w.drawn) == count, "an unchanged card is not redrawn at once")
w.at += RO.RESEND_S + 0.1
w.state.refresh()
check(len(w.drawn) == count + 1, "an unchanged card is redrawn now and then so it does not expire")


# --- drawing: left-justified, one padding ------------------------------------------------------------------------------------------------------
class Recorder:
    def __init__(self):
        self.shapes, self.messages = {}, {}

    def send_shape(self, shape_id, shape, color, fill, x, y, w_, h, ttl=8, thickness=None):
        self.shapes[shape_id] = (x, y, w_, h)

    def send_message(self, msg_id, text, color, x, y, ttl=8, size="normal"):
        self.messages[msg_id] = (text, color, x, y, size)


for look in (S.LEGACY, S.DEFAULT, S.look_from_choices("Ice blue", 1, 6, 3)):
    rec = Recorder()
    RO.render(RO.build_card(RO.sample_tracker(), 8), rec, look)
    left, top, width, height = rec.shapes[RO._CARD_ID]
    live = {k: v for k, v in rec.messages.items() if v[0]}
    texts = {k: v for k, v in live.items() if k.startswith("wfmt_route_x")}
    check(RO._X in {v[2] for v in texts.values()} and min(v[2] for v in texts.values()) == RO._X, "lines start at the card's left edge")
    check(RO._X - left == look.pad_x(S.CARD_PAD_X), "the text sits one standard padding in from the card's left border")
    check(min(v[3] for v in live.values()) - top == look.pad_y(S.CARD_PAD_Y), "and one standard padding below its top border")
    bottom = max(v[3] for v in live.values()) + look.line_px("normal")
    check(abs(top + height - bottom - look.pad_y(S.CARD_PAD_Y)) <= 1, f"and one padding above its bottom border ({top + height - bottom})")
    bad = [(v[0], v[2] + look.measured_width(v[0], "normal" if v[4] == look.size("normal") else "large"), left + width - look.pad_x(S.CARD_PAD_X)) for v in texts.values() if v[2] + look.measured_width(v[0], "normal" if v[4] == look.size("normal") else "large") > left + width - look.pad_x(S.CARD_PAD_X) + 1]
    check(not bad, f"every text fits inside the card: {bad}")
    check({v[4] for v in texts.values()} <= {look.size("normal"), look.size("large")}, "only the normal and title sizes are used")
    order = [v[0] for _k, v in sorted(texts.items(), key=lambda kv: kv[1][3])]
    check(order[0] == "You are navigating to:" and order[-1].endswith("LY left to jump."), f"the card reads top to bottom as the three header lines, the systems, the light years: {order}")
    colors = {v[0]: v[1] for v in texts.values()}
    check(colors.get("NEUTRON") == look.color("info") and colors.get("WHITE DWARF") == look.color("danger") and colors.get("BLACK HOLE") == look.color("warn") and colors.get("K") == look.color("ok"),
          f"neutron blue, white dwarf red, a star you cannot scoop yellow, one you can green: {colors}")
    dividers = [shape for key, shape in rec.shapes.items() if key.startswith("wfmt_route_s") and shape[3] == 1 and shape[2] > 0]
    check(len(dividers) == 2, f"a rule under the header and a rule over the light years line: {dividers}")

rec = Recorder()
RO.render(RO.Card(), rec, S.LEGACY)
check(rec.shapes[RO._CARD_ID][2:] == (0, 0) and all(v[0] == "" for v in rec.messages.values()), "an empty card clears everything")

# --- the EDSM check -------------------------------------------------------------------------------------------------------------------------------
UNKNOWN_TO_EDSM = {"Beta", "Delta"}


def edsm_world(**kwargs):
    world = World(rows=5, edsm=True, lookup=kwargs.pop("lookup", lambda names: {n: n not in UNKNOWN_TO_EDSM for n in names}), **kwargs)
    world.event("NavRoute", system="Sol")
    return world


w = edsm_world()
w.state.refresh()
card = w.state.card()
check(w.asked and "Alpha" in w.asked[0] and "Sol" not in w.asked[0], f"it asks about the systems ahead, not the one you are in: {w.asked}")
check([r[0] for r in card.rows][:4] == ["Alpha", "Beta *", "Gamma", "Delta *"], f"unknown systems get a mark: {card.rows}")
check(len(card.header) == 3 and card.footer[0].endswith("LY left to jump."), "and nothing else is added to the card")
check(len(w.asked) == 1, "it asks once for the whole list, and not again for answers it has")

w = edsm_world(lookup=lambda names: None)
w.state.refresh()
card = w.state.card()
check(not any(r[0].endswith("*") for r in card.rows), "a failed lookup marks nothing (could not tell is not unknown)")
asked = len(w.asked)
w.state.refresh()
check(len(w.asked) == asked, "it does not hammer EDSM after a failure")
w.at += RE.FAILED_RETRY_S + 1
w.state.refresh()
check(len(w.asked) == asked + 1, "it tries again after the pause")

w = edsm_world()
w.state.refresh()
before = len(w.asked)
w.at += RE.NOT_KNOWN_TTL_S - 1
w.state.refresh()
check(len(w.asked) == before, "an answer is kept until its time is up")
w.at += 2
w.state.refresh()
check(len(w.asked) == before + 1 and w.asked[-1] == ["Beta", "Delta"], f"systems EDSM did not know are asked about again after a while, and only those: {w.asked[-1]}")

w = World(rows=5, edsm=False, lookup=lambda names: {n: False for n in names})
w.event("NavRoute", system="Sol")
check(not w.asked and not any(r[0].endswith("*") for r in w.state.card().rows), "switched off, it asks nothing and marks nothing")

long_name = "Pru Aescs QN-S b" + "9-" * 6 + "1234"
w = World(route=route_file(("Sol", "G"), (long_name, "M")), rows=3, edsm=True, lookup=lambda names: {n: False for n in names})
w.event("NavRoute", system="Sol")
mark = [r[0] for r in w.state.card().rows][0]
check(mark.endswith(RO.NEW_MARK) and len(mark) <= RO.NAME_CHARS, f"a long name is cut so the mark fits: {mark!r}")

sample = RO.build_card(RO.sample_tracker(), 8, edsm=RE.sample_checker())
check([r[0].endswith(" *") for r in sample.rows][:8] == [False, False, True, False, False, False, True, False], f"the Test Card shows the mark on the third and seventh systems: {sample.rows}")

# --- a route plotted in the Route Planner supersedes the game's route ------------------------------------------------------------------------
from plugin import route_planner as NPL  # noqa: E402

LEGS = NPL.legs_from_result({"jumps": [
    {"name": "Sol", "distance": 0, "distance_to_destination": 400.0, "has_neutron": False},
    {"name": "Neutron One", "distance": 120.0, "distance_to_destination": 280.0, "has_neutron": True},
    {"name": "Plain Stop", "distance": 90.0, "distance_to_destination": 190.0, "has_neutron": False, "must_refuel": True},
    {"name": "Injection Stop", "distance": 20.0, "distance_to_destination": 170.0, "has_neutron": False, "must_inject": 1},
    {"name": "Neutron Two", "distance": 110.0, "distance_to_destination": 60.0, "has_neutron": True},
    {"name": "Neutron Three", "distance": 40.0, "distance_to_destination": 20.0, "has_neutron": True},
    {"name": "Colonia", "distance": 20.0, "distance_to_destination": 0.0, "has_neutron": False}]})


class PlannerWorld(World):
    def __init__(self, route, lookup=None, game_route=ROUTE, **kwargs):
        super().__init__(route=game_route, **kwargs)
        self.planned = route

        def ask(names):
            self.asked.append(list(names))
            return lookup(names)
        checker = RE.EdsmChecker(lookup=ask, now=lambda: self.at, background=False) if lookup else None
        self.state = RO.RouteOverlay(draw=self.drawn.append, now=lambda: self.at, cfg=lambda: self.cfg, read=lambda: self.file, edsm=checker,
                                     neutron=lambda: self.planned if self.planned is not None and self.planned.next_leg else None,
                                     neutron_done=lambda: self.planned.end if self.planned is not None and self.planned.legs and self.planned.next_leg is None else None,
                                     reset_neutron=self._reset)

    def _reset(self):
        self.resets = getattr(self, "resets", 0) + 1
        self.planned = None


plotted = NPL.Route("Sol", "Colonia", list(LEGS))
pw = PlannerWorld(plotted, rows=3)
pw.event("NavRoute", system="Sol")                       # the game also has a route plotted: the Route Planner's wins
card = pw.drawn[-1]
check(list(card.header) == [("You are navigating to:", "muted"), ("Colonia", "title"), ("You will be there in 6 jumps.", "text")], f"the same header, from the Route Planner's route: {card.header}")
check([r[0] for r in card.rows] == ["Neutron One", "Plain Stop", "Injection Stop"], f"the Route Planner's systems, not the game's, names only: {card.rows}")
check(list(card.rows) == [("Neutron One", "NEUTRON", "info"), ("Plain Stop", "NO FUEL", "warn"), ("Injection Stop", "NO FUEL", "warn")], f"each with its star: {card.rows}")
check(card.footer == ("400 LY left to jump.", "text"), f"the light years: {card.footer}")
long_world = PlannerWorld(NPL.Route("Sol", "Myriesly YZ-N c20-6099 4 a", list(LEGS)), rows=3)
long_world.event("NavRoute", system="Sol")
check(long_world.drawn[-1].header[1] == ("Myriesly YZ-N c20-6099 4 a", "title"), f"a long procedural destination is shown whole, not cut: {long_world.drawn[-1].header}")

plotted.arrive("Neutron One")
pw.state.refresh()
check(pw.drawn[-1].rows[0][0] == "Plain Stop" and pw.drawn[-1].header[2][0] == "You will be there in 5 jumps.", f"the card follows arrivals: {pw.drawn[-1].rows}")
check(pw.drawn[-1].footer == ("280 LY left to jump.", "text"), f"{pw.drawn[-1].footer}")

plotted.arrive("Colonia")                                # finished: the end of the route is announced, then the planner's route is reset
pw.event("NavRoute", system="Sol")
check(pw.drawn[-1].header[0][0] == "Route ended.", f"a finished Route Planner route says the route has ended: {pw.drawn[-1].header}")
pw.at += RO.END_SHOW_S + 1
pw.event("NavRoute", system="Sol")
check(pw.drawn[-1].header[1] == ("Zeta", "title") and pw.drawn[-1].rows[0][0] == "Alpha", f"after the reset the game's own route is shown: {pw.drawn[-1].header}")

# arriving at the end of a Route Planner route: the same message, then the planner's route is reset too
fin = PlannerWorld(NPL.Route("Sol", "Colonia", list(LEGS)), rows=3, game_route={"Route": []})
fin.event("NavRoute", system="Sol")
fin.planned.arrive("Colonia")
fin.state.refresh()
check([t for t, _r in fin.drawn[-1].header] == ["Route ended.", "You have arrived at Colonia.", "The route is being reset."], f"the end of a planned route says so: {fin.drawn[-1].header}")
fin.at += RO.END_SHOW_S + 1
fin.state.refresh()
check(not fin.drawn[-1] and getattr(fin, "resets", 0) == 1 and fin.planned is None, "then the planner's route is reset and the card closes")
stale = PlannerWorld(NPL.Route("Sol", "Colonia", list(LEGS)), rows=3)
stale.planned.arrive("Colonia")                      # a route that was already finished before this overlay ever drew it
stale.state.refresh()
check(not stale.drawn or not stale.drawn[-1], "a route finished before the overlay saw it says nothing")

# the tags: scoopable green, no fuel yellow, neutron blue, white dwarf red
tagged = [NPL.Leg(1, "Fuel Star", 1, 10.0, 30.0, False, scoopable=True), NPL.Leg(2, "Dark Star", 1, 10.0, 20.0, False), NPL.Leg(3, "Dwarf", 1, 10.0, 10.0, False, white_dwarf=True),
          NPL.Leg(4, "Neutron", 1, 10.0, 0.0, True, scoopable=True)]
card = RO.build_neutron_card(NPL.Route("Sol", "Neutron", tagged), 8)
check(list(card.rows) == [("Fuel Star", "FUEL", "ok"), ("Dark Star", "NO FUEL", "warn"), ("Dwarf", "WHITE DWARF", "danger"), ("Neutron", "NEUTRON", "info")], f"a planned route's star colors: {card.rows}")

fallback = PlannerWorld(None)
fallback.event("NavRoute", system="Sol")
check(fallback.drawn[-1].header[1] == ("Zeta", "title"), "with no Route Planner route the game's route shows")

show = PlannerWorld(NPL.Route("Sol", "Colonia", list(LEGS)), enabled=False)
show.event("NavRoute", system="Sol")
check(not show.drawn, "the Route overlay's own switch still decides whether anything is drawn")
check(RO.active_neutron_route() is None, "no plotted route by default (the real accessor tolerates a missing panel)")

UNKNOWN_PLANNED = {"Plain Stop", "Neutron Two"}
ew = PlannerWorld(NPL.Route("Sol", "Colonia", list(LEGS)), lookup=lambda names: {n: n not in UNKNOWN_PLANNED for n in names}, edsm=True, rows=5)
ew.event("NavRoute", system="Sol")
card = ew.drawn[-1]
check([r[0] for r in card.rows] == ["Neutron One", "Plain Stop *", "Injection Stop", "Neutron Two *", "Neutron Three"], f"systems EDSM does not know get a star: {card.rows}")
check(len(card.header) == 3, "and no line is added for them")
check(ew.asked and ew.asked[0][:3] == ["Neutron One", "Plain Stop", "Injection Stop"], f"the jumps ahead are asked about: {ew.asked}")

# --- a recalculated route: the file is read again once the game has rewritten it --------------------------------------------------------------
class Recalc:
    """A NavRoute.json that the game rewrites on its own schedule: `stamp` changes with each rewrite."""

    def __init__(self):
        self.file = ROUTE
        self.stamp = (1, 100)
        self.drawn = []
        self.state = RO.RouteOverlay(draw=self.drawn.append, now=lambda: 1000.0, cfg=lambda: RO.RouteConfig(enabled=True, rows=3, edsm=False),
                                     read=lambda: self.file, neutron=lambda: None, neutron_done=lambda: None, reset_neutron=lambda: None,
                                     stamp=lambda: self.stamp)


NEW_ROUTE = route_file(("Sol", "G"), ("Omega", "N"), ("Psi", "K"))
rc = Recalc()
rc.state.handle_event({"event": "NavRoute"}, "Sol")
check(rc.drawn[-1].header[1] == ("Zeta", "title"), "the first route shows")
check(not rc.state.sync_file(), "an unchanged file is not read again")
# The journal says NavRoute before the file has been rewritten: the old route is read, then the file changes.
rc.state.handle_event({"event": "NavRoute"}, "Sol")
check(rc.drawn[-1].header[1] == ("Zeta", "title"), "an event that beats the rewrite still shows the old route")
rc.file, rc.stamp = NEW_ROUTE, (2, 80)
check(rc.state.sync_file(), "the rewritten file is noticed")
check(rc.drawn[-1].header[1] == ("Psi", "title") and [r[0] for r in rc.drawn[-1].rows] == ["Omega", "Psi"], f"and the card shows the recalculated route: {rc.drawn[-1].header}")
check(not rc.state.sync_file(), "once")
# A half-written file cannot be read: it is tried again until it can.
rc.file, rc.stamp = None, (3, 10)
check(not rc.state.sync_file() and rc.drawn[-1].header[1] == ("Psi", "title"), "an unreadable file leaves the card as it was")
rc.file, rc.stamp = route_file(("Sol", "G"), ("Kappa", "M")), (3, 60)
check(rc.state.sync_file() and rc.drawn[-1].header[1] == ("Kappa", "title"), "and is read when it is whole, even if the time did not move")
rc.stamp = None
check(not rc.state.sync_file(), "no file, nothing to read")

# Nothing is read before the first journal event (a route left from an earlier session is not shown), or while the overlay is off, and a file that
# cannot be read is not tried again until it changes.
reads = []
quiet = Recalc()
quiet.state._read = lambda: (reads.append(1), quiet.file)[1]
check(not quiet.state.sync_file() and not reads and not quiet.drawn, "no read before the first journal event")
quiet.state.handle_event({"event": "Music"}, "Sol")
quiet.file, quiet.stamp = None, (5, 10)
reads.clear()
quiet.state.sync_file()
quiet.state.sync_file()
quiet.state.sync_file()
check(len(reads) == 1, f"a file that cannot be read is tried once, not every tick: {len(reads)}")
quiet.stamp = (5, 40)
quiet.state.sync_file()
check(len(reads) == 2, "and again once it changes")
off = Recalc()
off.state.handle_event({"event": "Music"}, "Sol")
off.state._cfg = lambda: RO.RouteConfig(enabled=False, rows=3, edsm=False)
off.stamp = (9, 9)
reads.clear()
off.state._read = lambda: (reads.append(1), off.file)[1]
check(not off.state.sync_file() and not reads, "nothing is read while the Route overlay is off")

# --- placement ----------------------------------------------------------------------------------------------------------------------------------
check("route" in P.SLOTS and P.SLOTS["route"].group == RO.GROUP_NAME, "the slot is registered with the card's group")

if problems:
    print("PROBLEMS:", len(problems))
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("ROUTE OVERLAY OK")
