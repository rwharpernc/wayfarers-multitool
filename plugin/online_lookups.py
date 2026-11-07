"""The online switches as data, with no Tk, so any feature can ask whether one is on and what to tell the user when it is not.

`LOOKUPS` is every switch that lets WFMT contact another service, with the saved setting that holds it and the default WFMT ships with. The page that changes
them is `settings_online.py` (Settings → Online); a feature only reads them, through `config.get_bool(<its own constant>)` as it always did.

A feature that cannot do its job without a lookup shows `needs(key)` where it is used: it is empty while the switch is on and a one-line warning when it is off,
so the warning is there only when something is wrong. The features that only get an extra from a lookup (a rarity comparison, a nicer sort) show nothing.
`tests/test_settings_online.py` fails when an entry names a setting the code does not have.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from config import config

# (what it does, who it asks, the saved setting, on when never changed, where the feature is, for the "used in" note)
LOOKUPS: Tuple[Tuple[str, str, str, bool, str], ...] = (
    ("BGS tick detection (every minute)", "tick.infomancer.uk", "wfmt_bgs_tick_enabled", True, "BGS"),
    ("Exploration Value: Earth-like world rarity", "Spansh", "wfmt_exploration_value_elw_rarity_enabled", False, "Exploration > Exploration Value"),
    ("Exploration Value: EDSM upload status", "EDSM", "wfmt_exploration_value_edsm_upload_enabled", False, "Exploration > Exploration Value"),
    ("Boxel Survey: skip systems anyone has visited", "EDSM", "wfmt_boxel_skip_edsm_visited", False, "Exploration > Boxel Survey"),
    ("Boxel Survey: skip systems fully scanned", "EDSM", "wfmt_boxel_skip_edsm_scanned", False, "Exploration > Boxel Survey"),
    ("Boxel Survey: confirm off-sequence arrivals", "EDSM", "wfmt_boxel_confirm_alias_arrival", False, "Exploration > Boxel Survey"),
    ("Region Sweep: skip systems anyone has visited", "EDSM", "wfmt_boxel_sweep_skip_edsm_visited", False, "Exploration > Boxel Survey"),
    ("Region Sweep: find more nearby cubes", "EDSM", "wfmt_boxel_sweep_auto_discover", False, "Exploration > Boxel Survey"),
    ("Nearest place to land", "Spansh", "wfmt_landing_finder_allowed", False, "Exploration > Nearest place to land"),
    ("Mining: nearby hotspot finder", "Spansh", "wfmt_mining_spansh_hotspot_finder_enabled", False, "Mining"),
    ("Mining: best price finder and Market research", "Spansh", "wfmt_mining_spansh_price_finder_enabled", False, "Mining"),
    ("Mining: ring reserve lookup", "EDSM", "wfmt_mining_edsm_reserve_lookup_enabled", False, "Mining"),
    ("Mining: Get body info in the Surface Mining Book", "EDSM and Spansh", "wfmt_mining_edsm_body_lookup_enabled", False, "Mining"),
    ("Trade: routes, prices and best picks", "Spansh", "wfmt_trade_lookups_enabled", False, "Trade"),
    ("System targets: bodies other commanders scanned", "EDSM", "wfmt_targets_online", False, "Overlays > System targets"),
    ("System targets: life and points of interest others found", "Spansh", "wfmt_targets_known", False, "Overlays > System targets"),
    ("Route overlay: systems EDSM does not know", "EDSM", "wfmt_route_edsm", False, "Overlays > Route"),
    ("Powerplay card: the system you are jumping to", "Spansh", "wfmt_powerplay_overlay_lookahead", False, "Overlays > Powerplay"),
    ("Colonization: share progress and deliveries", "Raven Colonial", "wfmt_rcc_enabled", False, "Colonization"),
    ("System name suggestions while typing", "Spansh", "wfmt_system_suggest_spansh", False, "Every system box"),
    ("Download and install updates", "GitHub", "wfmt_auto_update", False, "General > Updates"),
)

# Lookups with no switch because they run only when a button is pressed, listed so the page is the whole picture.
BUTTON_ONLY: Tuple[Tuple[str, str], ...] = (
    ("Rare Goods Finder window (it asks when you open it, with no switch)", "Spansh"),
    ("Codex \"Not found\" tab (it asks when you open it, with no switch)", "Canonn"),
    ("Find Nearest POI (Exploration panel)", "edastro.com GEC and Canonn"),
    ("Where to buy, Find sources, the Raven Colonial menu, Report an issue", "Spansh, Raven Colonial, GitHub (your browser)"),
    ("Random (undiscovered system, Exploration panel)", "Spansh and EDSM"),
    ("Route Planner (Generate route, also opened by the Expedition window's Neutron route button, and the star lookups for the neutron stops ahead that follow), and the Expedition window's Road to Riches and Exomastery", "Spansh"),
    ("Local star index: the Download and build and Update buttons below (nothing is downloaded unless you press one; the N.S. button asks nothing once the index is installed)", "Spansh's download server"),
    ("Route Planner, only with *Mark white dwarfs the route passes* ticked: the names of the route's systems, after the route is plotted", "EDSM"),
    ("Post to Discord (BGS report, Powerplay progress; you save a webhook link for each commander on the Discord tab, and nothing is posted until you press the button)", "Discord, to your own webhook"),
)


# Who is asked -> the heading it is listed under (the order here is the order on the page), and a note about how it is reached.
GROUPS: Tuple[Tuple[str, Tuple[str, ...], str], ...] = (
    ("Spansh", ("Spansh",), "spansh.co.uk: routes, prices, places to land, system names"),
    ("EDSM", ("EDSM", "EDSM and Spansh"), "www.edsm.net: what other commanders have scanned and visited"),
    ("Raven Colonial", ("Raven Colonial",), "Colonization progress shared with Raven Colonial; the key and Test key are on the Colonization tab"),
    ("Community tick service", ("tick.infomancer.uk",), "tick.infomancer.uk: plain HTTP, so this one request is unencrypted; on unless you turn it off"),
    ("GitHub", ("GitHub",), "api.github.com: checks for a newer WFMT when EDMC starts"),
)


def _entry(key: str) -> Tuple[str, str, str, bool, str]:
    for entry in LOOKUPS:
        if entry[2] == key:
            return entry
    raise KeyError(key)        # a misspelled key fails loudly instead of showing no warning


def defaults() -> Dict[str, bool]:
    """Every switch as WFMT ships it."""
    return {key: default for _what, _service, key, default, _where in LOOKUPS}


def states() -> List[Tuple[str, str, bool, str]]:
    """(what, service, on now, where) for every lookup, from what is saved."""
    return [(what, service, bool(config.get_bool(key, default=default)), where) for what, service, key, default, where in LOOKUPS]


def is_on(key: str) -> bool:
    _what, _service, _key, default, _where = _entry(key)
    return bool(config.get_bool(key, default=default))


def needs_any(keys: "List[str]") -> str:
    """The warning for a place that offers several lookups: "" when all are on, `needs(key)` when one is off, else one line naming each that is off."""
    off = [_entry(key) for key in keys if not is_on(key)]
    if not off:
        return ""
    if len(off) == 1:
        return needs(off[0][2])
    names = ", ".join(f'"{what}" ({service})' for what, service, _key, _default, _where in off)
    return f"These need lookups that are off: {names}. Turn them on in Settings > Online."


def needs(key: str) -> str:
    """The warning for a feature that cannot work without the lookup `key`: empty while it is on, else one line saying which it is, who it asks and where to turn it on."""
    what, service, _key, default, _where = _entry(key)
    if config.get_bool(key, default=default):
        return ""
    return f'This needs "{what}" ({service}), which is off. Turn it on in Settings > Online.'
