"""The Mining radar card: the Surface Live radar drawn over the game, for the Rhino driver with one screen.

It is the same picture as the Live window's radar (`mining_radar_view.render`), laid over the game as one image by WFMT's built-in overlay (Windows). EDMCModernOverlay has no way to draw a
picture, so with that overlay, or none, the card does nothing and the Settings page says so. The card follows the Rhino: it is drawn while a Rhino is deployed and the position and the body's
size are known, about once a second as Status.json changes, and removed when any of that stops. Its reach is the Live radar's (50 m to 2 km; the radar range shortcut and chat command and the
Live window's buttons step it), where it sits is Overlay Placement's "Mining radar", and its size and the opacity of its background are set on the Overlays → Mining page. The background is
made translucent so the game shows through; the marks stay solid. Rendering runs on a short-lived thread, so the main window never waits for it.
"""
from __future__ import annotations

import hashlib
import logging
import os
import threading
import time
from typing import Optional

from PIL import Image, ImageChops

from config import appname, config

from . import mining_coverage_render as radar
from . import mining_radar_view
from . import mining_sources
from . import overlay, overlay_native, overlay_placement, overlay_profile

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f"{appname}.{plugin_name}")

CFG_ENABLED = "wfmt_mining_radar_enabled"
CFG_SIZE = "wfmt_mining_radar_size"
CFG_OPACITY = "wfmt_mining_radar_opacity"
overlay_profile.register([CFG_ENABLED, CFG_SIZE, CFG_OPACITY])        # a commander's own choices, like every card's

SLOT = "mining_radar"
SIZE_RANGE, SIZE_DEFAULT = (240, 560), 340
OPACITY_RANGE, OPACITY_DEFAULT = (30, 100), 70
ORIGIN_X, ORIGIN_Y = 20, 100
"""The card's top left in the overlay's own canvas; Overlay Placement carries it to where the commander put it."""
SHAPE_ID = "wfmt_mining_radar_picture"
TTL_S = 3
"""A little over the gap between two updates, so the card is replaced before it would run out, and gone a moment after the Rhino stops sending."""
MIN_INTERVAL_S = 1.0

_client: overlay.OverlayClient = overlay.OverlayClient()
_lock = threading.Lock()
_busy = False
_last = 0.0
_shown = False


def set_overlay_client(client: overlay.OverlayClient) -> None:
    global _client
    _client = client


def _clamped(key: str, bounds: tuple, default: int) -> int:
    try:
        value = int(config.get_int(key, default=default))
    except (TypeError, ValueError):
        return default
    return max(bounds[0], min(bounds[1], value))


def enabled() -> bool:
    return bool(config.get_bool(CFG_ENABLED, False))


def card_size() -> int:
    return _clamped(CFG_SIZE, SIZE_RANGE, SIZE_DEFAULT)


def opacity_percent() -> int:
    return _clamped(CFG_OPACITY, OPACITY_RANGE, OPACITY_DEFAULT)


def translucent(picture: Image.Image, opacity: int) -> Image.Image:
    """The radar picture with its plain background and the green of the ground driven made `opacity` percent opaque and everything else drawn on it (rings, marks, deposits, the Rhino)
    fully opaque, as an RGBA image."""
    rgb = picture.convert("RGB")
    not_background = ImageChops.difference(rgb, Image.new("RGB", rgb.size, radar.RADAR_BACKGROUND)).convert("L")
    not_ground = ImageChops.difference(rgb, Image.new("RGB", rgb.size, radar.GROUND_DRIVEN_COLOR)).convert("L")
    drawn = ImageChops.darker(not_background, not_ground).point(lambda value: 255 if value else 0)      # a pixel that is neither plain background nor plain green
    alpha = ImageChops.lighter(drawn, Image.new("L", rgb.size, round(255 * max(0, min(100, opacity)) / 100)))
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def card_picture(src: mining_sources.Sources, range_m: float) -> Optional[Image.Image]:
    """The card's picture now (RGBA, `card_size()` square), or None while there is nothing to draw it from."""
    picture = mining_radar_view.render(src, card_size(), range_m)
    return None if picture is None else translucent(picture, opacity_percent())


def _wanted(src: mining_sources.Sources) -> bool:
    return enabled() and overlay_native.accepting() and src.surface.is_active


def _draw(picture: Image.Image, client, ttl: int) -> bool:
    size = picture.width
    placed = overlay_placement.client_for_measured(SLOT, client, (ORIGIN_X, ORIGIN_Y, size, size))
    key = hashlib.blake2b(picture.tobytes(), digest_size=8).hexdigest()
    return bool(placed.send_image(SHAPE_ID, picture, ORIGIN_X, ORIGIN_Y, size, size, key, ttl=ttl))


def _remove(client) -> None:
    global _shown
    if _shown:
        _shown = False
        client.send_clear(SHAPE_ID)


def update(src: Optional[mining_sources.Sources] = None) -> None:
    """Called as Status.json changes: draw the card, or take it down, at most once a second and never on the caller's thread."""
    global _busy, _last
    src = src or mining_sources.real()
    if not enabled():
        _remove(_client)
        return
    now = time.monotonic()
    with _lock:
        if _busy or now - _last < MIN_INTERVAL_S:
            return
        _busy, _last = True, now
    threading.Thread(target=_work, args=(src,), name="WFMT-mining-radar", daemon=True).start()


def _work(src: mining_sources.Sources) -> None:
    global _busy, _shown
    try:
        picture = card_picture(src, mining_radar_view.saved_range()) if _wanted(src) else None
        if picture is None:
            _remove(_client)
        elif _draw(picture, _client, TTL_S):
            _shown = True
    except Exception:
        logger.debug("Could not draw the Mining radar card", exc_info=True)
    finally:
        _busy = False


def send_test(client) -> bool:
    """Draw the card from the pretend Rhino of the Mining simulation for a few seconds, wherever Overlay Placement puts it (Settings → Overlays → Mining → Test radar). False when the
    built-in overlay is not the one drawing, which is the only one that can draw it."""
    from . import mining_simulation
    if not overlay_native.accepting():
        return False
    picture = card_picture(mining_simulation.SurfaceSimulation().sources, mining_radar_view.saved_range())
    return picture is not None and _draw(picture, client, 8)
