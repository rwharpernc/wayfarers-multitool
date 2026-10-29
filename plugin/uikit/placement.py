"""Where a pop-out window opens: on the monitor EDMC is running on.

A window remembers the size and position it had when it was closed. Without a remembered position, or with one that is no longer on any
connected monitor (a monitor was unplugged), the window manager picks a place, often the primary monitor. This module puts the window over
EDMC's own window instead, kept inside that monitor. With "always on EDMC's monitor" switched on it does so every time, whatever was
remembered. `place` is pure so it can be tested; only `screens` touches the system (Windows monitors through user32, the Tk virtual screen
elsewhere, which on Linux is the one rectangle Tk can report).
"""
from __future__ import annotations

import re
import sys
import tkinter as tk
from typing import List, Optional, Sequence, Tuple

Rect = Tuple[int, int, int, int]       # x, y, width, height

_POSITION = re.compile(r"([+-]-?\d+)([+-]-?\d+)$")
_MIN_VISIBLE = (120, 60)               # a remembered position counts as on a monitor when this much of the window's top-left shows there

_always = False


def set_always(value: bool) -> None:
    """True: every window opens on EDMC's monitor, ignoring where it was left (the Settings choice)."""
    global _always
    _always = bool(value)


def always() -> bool:
    return _always


def _overlap(a: Rect, b: Rect) -> Tuple[int, int]:
    width = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    height = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return max(0, width), max(0, height)


def monitor_of(rect: Rect, screens: Sequence[Rect]) -> Rect:
    """The monitor `rect` mostly sits on (the first when it sits on none)."""
    best, best_area = screens[0], -1
    for screen in screens:
        width, height = _overlap(rect, screen)
        if width * height > best_area:
            best, best_area = screen, width * height
    return best


def on_a_screen(position: Tuple[int, int], size: Tuple[int, int], screens: Sequence[Rect]) -> bool:
    """Whether a window of `size` at `position` shows enough of its top-left corner (its title bar) on some monitor to be grabbed."""
    window = (position[0], position[1], size[0], size[1])
    for screen in screens:
        width, height = _overlap(window, screen)
        if width >= min(_MIN_VISIBLE[0], size[0]) and height >= min(_MIN_VISIBLE[1], size[1]):
            return True
    return False


def centered_over(parent: Rect, size: Tuple[int, int], screens: Sequence[Rect]) -> Tuple[int, int]:
    """Centered over `parent`, then moved to lie wholly inside the monitor `parent` is on (against its top-left when the window is larger)."""
    screen = monitor_of(parent, screens)
    x = parent[0] + (parent[2] - size[0]) // 2
    y = parent[1] + (parent[3] - size[1]) // 2
    x = max(screen[0], min(x, screen[0] + screen[2] - size[0]))
    y = max(screen[1], min(y, screen[1] + screen[3] - size[1]))
    return x, y


def place(size: Tuple[int, int], saved: Optional[Tuple[int, int]], parent: Rect, screens: Sequence[Rect],
          always_here: bool = False) -> Tuple[int, int]:
    """The top-left corner for a window of `size`: where it was left when that is still on a monitor, otherwise over EDMC's window on EDMC's
    monitor. `always_here` skips the remembered position."""
    if not screens:
        return saved if saved is not None else (parent[0], parent[1])
    if saved is not None and not always_here and on_a_screen(saved, size, screens):
        return saved
    return centered_over(parent, size, screens)


def _windows_monitors() -> List[Rect]:
    """The work area (the monitor without the taskbar) of each connected monitor, in virtual-screen pixels."""
    import ctypes
    from ctypes import wintypes

    class MonitorInfo(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT), ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]

    found: List[Rect] = []
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_int, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)

    def each(monitor, _dc, _rect, _data) -> int:
        info = MonitorInfo()
        info.cbSize = ctypes.sizeof(MonitorInfo)
        if ctypes.windll.user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
            work = info.rcWork
            found.append((work.left, work.top, work.right - work.left, work.bottom - work.top))
        return 1

    ctypes.windll.user32.EnumDisplayMonitors(None, None, callback_type(each), 0)
    return found


def screens(widget: tk.Misc) -> List[Rect]:
    """The monitors Tk can place a window on. Windows lists each; elsewhere Tk reports only the whole virtual screen."""
    if sys.platform == "win32":
        try:
            monitors = _windows_monitors()
            if monitors:
                return monitors
        except Exception:      # noqa: BLE001 - never fail to open a window over a monitor list
            pass
    return [(widget.winfo_vrootx(), widget.winfo_vrooty(), widget.winfo_vrootwidth(), widget.winfo_vrootheight())]


def geometry_for(parent: tk.Misc, geometry: str, size: Tuple[int, int]) -> str:
    """`geometry` ("WxH" or "WxH+x+y") with its position chosen by `place`, as a Tk geometry string. `size` is the window's width and height
    after the minimum size was applied. Never raises: on any trouble the geometry is returned as given."""
    try:
        root = parent._root()                          # EDMC's own window, whichever WFMT window the new one was opened from
        if str(root.state()) in ("iconic", "withdrawn"):      # minimized: its position says nothing about a monitor
            return geometry
        parent_rect = (root.winfo_rootx(), root.winfo_rooty(), root.winfo_width(), root.winfo_height())
        match = _POSITION.search(geometry)
        saved = (int(match.group(1)), int(match.group(2))) if match else None
        x, y = place(size, saved, parent_rect, screens(root), _always)
        return f"{size[0]}x{size[1]}{x:+d}{y:+d}"
    except Exception:          # noqa: BLE001
        return geometry
