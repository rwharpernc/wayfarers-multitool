"""Powerplay overlay: one small card on the game screen with your Powerplay standing while you are in a system that has Powerplay data.

It shows your pledged Power, rank and total merits; the merits earned so far in the Powerplay cycle in progress; the system's state and who holds it; what
merits earned here now would count as (Acquisition, Reinforcement or Undermining); and the merits and estimated Control Points earned in this system this session,
by type. The Control Points are estimates from the merits-per-CP ratios in Settings -> Powerplay (the journal never reports them). It reads the same tracker, session
and cycle ledger as the Powerplay panel, so the figures match it. Off until ticked in Settings -> Overlays -> Powerplay; it shows only in a system with a Powerplay
state. Where it sits is the Overlay Placement setting ("Powerplay"). Nothing is sent anywhere.
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


def load_config() -> PowerplayOverlayConfig:
    return PowerplayOverlayConfig(enabled=config.get_bool(_CFG_ENABLED, default=False))


def save_config(cfg: PowerplayOverlayConfig) -> None:
    config.set(_CFG_ENABLED, cfg.enabled)


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


def build_card(info: Optional[Info]) -> Card:
    """The card for a system, or an empty one when there is no Powerplay data for it."""
    if info is None or not info.state:
        return Card()
    rows = []
    if info.power:
        rows.append(("Power", cut(info.power, 22), "text"))
        rows.append(("Total merits", f"{info.total_merits:,}" if info.total_merits is not None else "—", "text"))
        rows.append((f"{info.cycle_label} merits", f"{info.cycle_merits:,}", "ok" if info.cycle_merits else "text"))
    else:
        rows.append(("Power", "not pledged", "muted"))
    rows.append(("System", info.state, "title"))
    rows.append(("Held by", cut(info.controller, 22) if info.controller else "no one", "text" if info.controller else "muted"))
    label = ACTIVITY_LABELS.get(info.activity, "") if info.power and info.activity else ""
    if label:
        rows.append(("Merits here count as", label, "title"))
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
    if info.power and not shown:
        rows.append(("Earned here", "nothing yet", "muted"))
    title = cut(info.system, 24)
    return Card((), tuple(rows), None, title=(title, "title"), badge=f"Rank {info.rank}" if info.power and info.rank is not None else "", align="column")


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
              "merits and estimated Control Points you have earned in this system this session, by type. Everything comes from your journal; nothing is sent anywhere."),
        wraplength=440, justify=tk.LEFT,
    ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 4))
    overlay_link.add(frame)

    _vars["enabled"] = tk.BooleanVar(value=cfg.enabled)
    nb.Checkbutton(frame, text="Enable the Powerplay card", variable=_vars["enabled"]).grid(row=2, column=0, sticky=tk.W, padx=10, pady=2)
    nb.Label(frame, text="The card shows only in a system with a Powerplay state; elsewhere it clears.",
             wraplength=440, justify=tk.LEFT).grid(row=3, column=0, sticky=tk.W, padx=(30, 10), pady=2)

    nb.Label(
        frame,
        text=("What WFMT cannot know: the journal never reports Control Points, so they are estimated from the merits-per-CP ratios on the Powerplay tab. Deliveries and unattributed "
              "merits are shown as merits only. What merits count as is a best guess from the system's state and who holds it, as on the Powerplay panel."),
        wraplength=440, justify=tk.LEFT,
    ).grid(row=4, column=0, sticky=tk.W, padx=10, pady=(6, 4))

    action_row = tk.Frame(frame)
    action_row.grid(row=5, column=0, sticky=tk.W, padx=10, pady=(6, 2))
    tk.Button(action_row, text="Test Card", command=_test_card).pack(side=tk.LEFT)
    _result_label = nb.Label(action_row, text="", wraplength=320, justify=tk.LEFT)
    _result_label.pack(side=tk.LEFT, padx=(10, 0))
    nb.Label(frame, text="(Test Card works even while disabled above, and reports whether the overlay was actually reachable.)",
             wraplength=440, justify=tk.LEFT).grid(row=6, column=0, sticky=tk.W, padx=10, pady=(0, 10))


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
        save_config(PowerplayOverlayConfig(enabled=bool(_vars["enabled"].get())))
