"""Powerplay overlay: one small card on the game screen with your Powerplay standing in the system you are in, or the one a hyperspace jump is heading for.

It shows your pledged Power, rank and total merits; the merits earned so far in the Powerplay cycle in progress; the system's state and who holds it; what
merits earned here now would count as (Acquisition, Reinforcement or Undermining); and the merits and estimated Control Points earned in this system this session,
by type. The Control Points are estimates from the merits-per-CP ratios in Settings -> Powerplay (the journal never reports them). It reads the same tracker, session
and cycle ledger as the Powerplay panel, so the figures match it. Off until ticked in Settings -> Overlays -> Powerplay; it shows only in a system with a Powerplay
state; in a system without one it says "No Powerplay Detected in system". With *Look up the system I am jumping to* ticked, the card turns to the destination as soon as the journal
says the jump has started, asking Spansh (powerplay_system_lookup.py) for its standing, and to the system you arrive in when the jump ends. Where it sits is the Overlay Placement
setting ("Powerplay"). Nothing is sent anywhere unless that tick is on, and then only the destination's system id goes to Spansh.
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import tkinter as tk

import myNotebook as nb
from config import appname, config

from . import overlay, overlay_appearance, overlay_link, overlay_placement, restore
from .formulas import ACTIVITIES, ACTIVITY_LABELS, NO_CP_ACTIVITIES
from .overlay import OverlayClient
from .overlay_card import Card, CardLayout, LiveCard, Ticker, cut
from .overlay_style import LEGACY, Look

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

PANEL_PLACEMENT = None   # Settings-tab-only, no main-panel widget

_CFG_ENABLED = "wfmt_powerplay_overlay"
_CFG_LOOKAHEAD = "wfmt_powerplay_overlay_lookahead"

NO_POWERPLAY, LOOKING, UNAVAILABLE = "none", "looking", "unavailable"      # what an Info with no state is saying

OVERLAY_TTL = 4
GROUP_NAME = "wfmt_powerplay"
GROUP_PREFIX = "wfmt_powerplay_"
NAME_CHARS = 16
SAMPLE_TAG = "Reinforcement"
LAYOUT = CardLayout(GROUP_PREFIX, x=650, y=100, max_header=1, max_rows=12, name_chars=NAME_CHARS, tag_chars=14, sample_tag=SAMPLE_TAG, sample_lines=11,
                    title_chars=24, sample_badge="Rank 100")


@dataclass
class PowerplayOverlayConfig:
    enabled: bool = False
    lookahead: bool = False         # look up the system a jump is heading for (asks Spansh)


def load_config() -> PowerplayOverlayConfig:
    return PowerplayOverlayConfig(enabled=config.get_bool(_CFG_ENABLED, default=False), lookahead=config.get_bool(_CFG_LOOKAHEAD, default=False))


def save_config(cfg: PowerplayOverlayConfig) -> None:
    config.set(_CFG_ENABLED, cfg.enabled)
    config.set(_CFG_LOOKAHEAD, cfg.lookahead)


# --- what the card says (pure) ---------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Info:
    """What the card is drawn from. `here` is the merits earned in this system this session by activity, and `cp` the estimated Control Points for the same."""
    system: str
    state: str                                   # the system's PowerplayState
    controller: str = ""                         # the Power that holds it, if any
    power: str = ""                              # your pledged Power ("" when not pledged)
    rank: Optional[int] = None
    total_merits: Optional[int] = None
    cycle_label: str = "Cycle"
    cycle_merits: int = 0
    activity: str = ""                           # what merits earned here now would count as (an ACTIVITIES key, "" when unknown)
    here: Tuple[Tuple[str, int], ...] = ()       # (activity, merits) for each activity that earned merits here this session
    cp: Tuple[Tuple[str, float], ...] = ()       # (activity, estimated CP) for the same
    status: str = ""                             # "" when `state` says it; NO_POWERPLAY, LOOKING or UNAVAILABLE when the system has no state to show
    destination: bool = False                    # the system a jump is heading for, not the one you are in
    progress: Optional[float] = None             # the destination's control progress (0-1), when known


def build_card(info: Optional[Info]) -> Card:
    """The card for a system, or an empty one when there is nothing to say."""
    if info is None:
        return Card()
    title = cut(info.system, 24)
    badge = "jumping" if info.destination else ""
    if not info.state:
        words = {NO_POWERPLAY: ("No Powerplay Detected in system", "muted"), LOOKING: ("Looking up Powerplay…", "muted"),
                 UNAVAILABLE: ("Powerplay lookup unavailable", "muted")}.get(info.status)
        return Card((words,), title=(title, "title"), badge=badge) if words else Card()
    rows = []
    if info.power:
        rows.append(("Power", cut(info.power, 22), "text"))
        rows.append(("Total merits", f"{info.total_merits:,}" if info.total_merits is not None else "—", "text"))
        rows.append((f"{info.cycle_label} merits", f"{info.cycle_merits:,}", "ok" if info.cycle_merits else "text"))
    else:
        rows.append(("Power", "not pledged", "muted"))
    rows.append(("System", info.state if info.progress is None else f"{info.state} · {info.progress * 100:.0f}%", "title"))
    rows.append(("Held by", cut(info.controller, 22) if info.controller else "no one", "text" if info.controller else "muted"))
    label = ACTIVITY_LABELS.get(info.activity, "") if info.power and info.activity else ""
    if label:
        rows.append(("Merits there count as" if info.destination else "Merits here count as", label, "title"))
    merits = dict(info.here)
    cp = dict(info.cp)
    shown = False
    for activity in ACTIVITIES:
        if merits.get(activity, 0) <= 0:
            continue
        shown = True
        short = ACTIVITY_LABELS[activity]
        value = f"{merits[activity]:,} merits" if activity in NO_CP_ACTIVITIES else f"{merits[activity]:,} merits · ~{cp.get(activity, 0.0):.0f} CP"
        rows.append((short, value, "ok"))
    if info.power and not shown and not info.destination:
        rows.append(("Earned here", "nothing yet", "muted"))
    if not badge and info.power and info.rank is not None:
        badge = f"Rank {info.rank}"
    return Card((), tuple(rows), None, title=(title, "title"), badge=badge, align="column")


def sample_info() -> Info:
    """A made-up system for the Test Card."""
    return Info("Sample System", "Fortified", "Aisling Duval", "Aisling Duval", 12, 1_204_500, "Cycle 41", 86_300, "reinforcement",
                (("reinforcement", 4_200), ("delivery", 1_500)), (("reinforcement", 1_680.0),))


# --- state and the live path -----------------------------------------------------------------------------------------

_overlay_client = overlay.OverlayClient()


def set_overlay_client(client: overlay.OverlayClient) -> None:
    global _overlay_client
    _overlay_client = client


def block_rect(look: Look = LEGACY, card: Optional[Card] = None) -> tuple:
    return LAYOUT.block_rect(look, card)


def placed_client(client: OverlayClient, look: Look = LEGACY, card: Optional[Card] = None) -> OverlayClient:
    return overlay_placement.client_for_measured("powerplay", client, block_rect(look, card), look)


def render(card: Card, client: OverlayClient, look: Look = LEGACY) -> None:
    LAYOUT.render(card, client, look, ttl=OVERLAY_TTL)


def _build() -> Card:
    from . import powerplay, system_survey
    if not system_survey.survey.playing:
        return Card()
    return build_card(powerplay.controller.overlay_info())


def _draw_live(card: Card) -> None:
    look = overlay_appearance.current_look()

    def worker() -> None:
        try:
            render(card, placed_client(_overlay_client, look, card), look)
        except OSError:
            logger.debug("Could not reach the overlay for the Powerplay card", exc_info=True)

    threading.Thread(target=worker, name="WFMT-powerplay-render", daemon=True).start()


live = LiveCard(_build, lambda: load_config().enabled, _draw_live)
_ticker = Ticker("WFMT-powerplay-tick", live.refresh, 1.0, logger)


def start(plugin_dir: str) -> None:
    _ticker.start()


def stop() -> None:
    _ticker.stop()


def refresh() -> None:
    """The Powerplay panel calls this after it has counted an event."""
    live.refresh()


def handle_event(entry: Dict[str, Any], cmdr: str, system: Optional[str], station: Optional[str], state: Dict[str, Any]) -> None:
    """Runs on a start-up, shut-down or restore, when the card must be redrawn or cleared (the Powerplay panel refreshes it after every other event)."""
    if entry.get("event") in ("StartUp", "Shutdown", restore.RESTORE_EVENT):
        live.refresh()


# --- Settings tab ----------------------------------------------------------------------------------------------------------

_vars: Dict[str, Any] = {}
_result_label: Optional[nb.Label] = None


def build_settings(notebook: nb.Notebook) -> None:
    global _result_label
    frame = nb.Frame(notebook)
    frame.columnconfigure(0, weight=1)
    notebook.add(frame, text="Powerplay")
    cfg = load_config()

    nb.Label(
        frame,
        text=("A small card on your in-game overlay, through the overlay (WFMT's built-in one on Windows, or EDMCModernOverlay: a separate, optional helper WFMT does not install or launch; its "
              "connection settings are on the Overlay Connection tab), with your Powerplay standing while you are in a system that has Powerplay data: your Power, rank and total merits, the "
              "merits earned in the cycle in progress, the system's state and who holds it, what merits earned here now count as (Acquisition, Reinforcement or Undermining), and the "
              "merits and estimated Control Points you have earned in this system this session, by type. In a system without Powerplay data it says \"No Powerplay Detected in system\". "
              "Everything comes from your journal, except the look-ahead below, which is off until you tick it."),
        wraplength=440, justify=tk.LEFT,
    ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 4))
    overlay_link.add(frame)

    _vars["enabled"] = tk.BooleanVar(value=cfg.enabled)
    nb.Checkbutton(frame, text="Enable the Powerplay card", variable=_vars["enabled"]).grid(row=2, column=0, sticky=tk.W, padx=10, pady=2)
    nb.Label(frame, text="In a system with no Powerplay state the card says so.",
             wraplength=440, justify=tk.LEFT).grid(row=3, column=0, sticky=tk.W, padx=(30, 10), pady=2)
    _vars["lookahead"] = tk.BooleanVar(value=cfg.lookahead)
    nb.Checkbutton(frame, text="Look up the system I am jumping to (asks Spansh)", variable=_vars["lookahead"]).grid(row=4, column=0, sticky=tk.W, padx=10, pady=(8, 2))
    nb.Label(frame, text=("Off, the card shows only the system you are in. On, it turns to the destination as soon as the jump starts (marked jumping) and asks spansh.co.uk for that "
                          "system's Powerplay standing, sending only the system's id and nothing about you, then shows the system you arrive in. The answer is kept for an hour."),
             wraplength=440, justify=tk.LEFT).grid(row=5, column=0, sticky=tk.W, padx=(30, 10), pady=(0, 4))

    nb.Label(
        frame,
        text=("What WFMT cannot know: the journal never reports Control Points, so they are estimated from the merits-per-CP ratios on the Powerplay tab. Deliveries and unattributed "
              "merits are shown as merits only. What merits count as is a best guess from the system's state and who holds it, as on the Powerplay panel."),
        wraplength=440, justify=tk.LEFT,
    ).grid(row=6, column=0, sticky=tk.W, padx=10, pady=(6, 4))

    action_row = tk.Frame(frame)
    action_row.grid(row=7, column=0, sticky=tk.W, padx=10, pady=(6, 2))
    tk.Button(action_row, text="Test Card", command=_test_card).pack(side=tk.LEFT)
    _result_label = nb.Label(action_row, text="", wraplength=320, justify=tk.LEFT)
    _result_label.pack(side=tk.LEFT, padx=(10, 0))
    nb.Label(frame, text="(Test Card works even while disabled above, and reports whether the overlay was actually reachable.)",
             wraplength=440, justify=tk.LEFT).grid(row=8, column=0, sticky=tk.W, padx=10, pady=(0, 10))


def _test_card() -> None:
    if _result_label is None:
        return
    cfg = overlay.load_config()
    client = overlay.OverlayClient(cfg)
    label = _result_label
    look = overlay_appearance.current_look()

    def worker() -> None:
        try:
            sample = build_card(sample_info())
            render(sample, placed_client(client, look, sample), look)
            outcome, color = "Sent: check your overlay.", "#2e7d32"
        except OSError as err:
            outcome, color = f"Could not reach the overlay at {cfg.host}:{cfg.port} ({err}).", "#c07000"
        try:
            label.after(0, lambda: label.configure(text=outcome, foreground=color))
        except tk.TclError:
            pass   # the Settings dialog was closed before the test finished

    threading.Thread(target=worker, name="WFMT-powerplay-test", daemon=True).start()


def save_settings() -> None:
    if _vars:
        save_config(PowerplayOverlayConfig(enabled=bool(_vars["enabled"].get()), lookahead=bool(_vars["lookahead"].get())))
