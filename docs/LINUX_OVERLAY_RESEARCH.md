# Built-in Overlay on Linux: Research Notes

Scope: the state of WFMT's overlay code with respect to Linux. No Linux overlay window exists in the code. This page records what the code does today and the constraints that follow from it. For the Windows overlay, see [NATIVE_OVERLAY_SPEC.md](NATIVE_OVERLAY_SPEC.md).

**Contents:**

- [Current state](#current-state)
- [Platform-independent layers](#platform-independent-layers)
- [Windows-specific layer](#windows-specific-layer)
- [Existing Linux support code](#existing-linux-support-code)
- [Constraints from the existing design](#constraints-from-the-existing-design)
- [Test setup](#test-setup)
- [Sources consulted](#sources-consulted)

## Current state

- `overlay_window.supported()` returns `sys.platform == "win32"`. The built-in overlay is available on Windows only.
- `overlay_native.supported()` returns `overlay_window.supported()`. `overlay_native.selected()` returns the built-in backend only when the commander chose it and `supported()` is true; otherwise it returns the EDMCModernOverlay backend.
- On Linux, overlays are shown through [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay).
- [NATIVE_OVERLAY_SPEC.md](NATIVE_OVERLAY_SPEC.md) lists the Linux window as not built.
- No experiment results have been recorded.

## Platform-independent layers

Source: `plugin/` and [NATIVE_OVERLAY_SPEC.md](NATIVE_OVERLAY_SPEC.md).

| Module | Role |
| --- | --- |
| Features | Send small payloads to the scene. |
| `overlay_scene.py` | Holds what is on screen. |
| `overlay_raster.py` | Draws the scene into a transparent Pillow image the size of the game window. |
| Placement, groups, fonts, screenshots with the overlay, hide switch | Operate on that image. |

## Windows-specific layer

`overlay_window.py` is the only Windows-specific module. Its `OverlayWindow` class:

- runs on a thread inside EDMC, so it ends with EDMC and no window remains running after EDMC exits;
- finds Elite's window and follows its position, size and display scaling (`Geometry` is x, y, width, height and the scaling factor);
- shows only while Elite is the foreground window, unless the commander chose to keep it showing, and only when there is something to show;
- draws through a topmost layered window with per-pixel alpha (`UpdateLayeredWindow`) that is transparent to the mouse and never takes focus;
- exists only when the commander turns the built-in overlay on;
- does not use the network.

The game must run borderless or windowed; a fullscreen game owns the screen and nothing can be drawn over it.

`overlay_native.py` constructs `OverlayWindow(scene, font_path, keep_showing, groups)` and uses `start()`, `stop()`, `running`, `geometry` and `error`. A class offering the same members can be substituted without changing any feature.

## Existing Linux support code

`platform_support.py` provides:

- `xdotool`, run through `subprocess` and not through a Python binding;
- `xdotool` and other host tools run through `flatpak-spawn --host` when EDMC is a Flatpak, because the Flatpak sandbox cannot see them or the game's processes;
- location of Elite's windows by title (`find_elite_windows`), focus (`focus_window`) and the title of the active window (`active_window_title`);
- location of Elite's folders inside a Wine or Proton prefix;
- the primary monitor's size from `xrandr --current` (`parse_xrandr`), used when no game files or overlay log supply the screen size;
- the statement that Elite, a Windows game, runs as an XWayland window on a Wayland desktop.

## Constraints from the existing design

- The overlay runs inside EDMC's Python, which provides Tk and Pillow.
- A Flatpak EDMC has its own sandboxed Python and cannot see most host libraries.
- No window is to remain after EDMC exits (the Windows design property above).
- No overlay code sends data anywhere.
- The first-tested Linux setup is KDE Plasma on Wayland, Elite under Steam Proton, EDMC as a Flatpak.

## Test setup

Host of the research: KDE Plasma on Wayland; `xdotool`, `xprop`, `xwininfo` and `wmctrl` installed; EDMC installed as a Flatpak.

## Sources consulted

These links were consulted during the research. Their statements about compositor behavior have not been verified against WFMT code or tests.

- Layer-shell and input regions: [gtk4-layer-shell](https://github.com/ainola/gtk4-layer-shell), [Mutter issue 973](https://gitlab.gnome.org/GNOME/mutter/-/issues/973), [KWin mailing list, 2020](https://mail.kde.org/pipermail/kwin/2020-August/005149.html), [Hyprland discussion 14136](https://github.com/hyprwm/Hyprland/discussions/14136).
- X11 input shapes: [Shallow Thoughts, 2017](https://shallowsky.com/blog/2017/Apr/06), [Wine patch discussion](https://list.winehq.org/hyperkitty/list/wine-gitlab@list.winehq.org/message/F6EF5PFQ4SJG4DT3UUBDFUEI27H6QBU3/).
- XWayland and input shapes: [xserver merge request 1517](https://gitlab.freedesktop.org/xorg/xserver/-/merge_requests/1517), [KWin merge request 6247](https://invent.kde.org/plasma/kwin/-/merge_requests/6247), [Mutter issue 2593](https://gitlab.gnome.org/GNOME/mutter/-/issues/2593).
- X Rendering Extension: [Wikipedia](https://en.wikipedia.org/wiki/X_Rendering_Extension).
- Existing overlay: [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay) (public README).
