# A built-in overlay for Linux: research notes

This page is research and planning only. No Linux overlay code exists yet. It records what is known, what is assumed, which options exist, and which experiments settle the open questions. For the Windows overlay it builds on, see [NATIVE_OVERLAY_SPEC.md](NATIVE_OVERLAY_SPEC.md).

How to read it: every statement is marked **known** (checked in WFMT's code or in a cited source), **assumed** (reasonable, not yet checked) or **open** (an experiment in [Experiments](#experiments) answers it).

**On this page:**

- [Goal](#goal)
- [What already exists](#what-already-exists)
- [Constraints](#constraints)
- [What a Linux window has to do](#what-a-linux-window-has-to-do)
- [Options](#options)
- [Display servers and compositors](#display-servers-and-compositors)
- [Experiments](#experiments)
- [Plan](#plan)
- [Risks](#risks)
- [Sources](#sources)

## Goal

A WFMT overlay for Linux that needs nothing else installed, so that a Linux commander gets the same on-screen displays as the Windows built-in overlay. [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay) stays supported for other plugins and for anyone who prefers it.

Not a goal for the first version: fullscreen (exclusive) games, Steam Deck gaming mode, VR, other plugins' overlays.

## What already exists

**Known** (WFMT's code and [NATIVE_OVERLAY_SPEC.md](NATIVE_OVERLAY_SPEC.md)):

- Everything above the window is platform independent. Features send small payloads; `overlay_scene.py` keeps what is on screen; `overlay_raster.py` draws the scene into a transparent Pillow image the size of the game window; placement, groups, fonts, screenshots with the overlay and the hide switch all work on that image.
- Only `overlay_window.py` is Windows specific. It runs on a thread inside EDMC and does five things: find Elite's window, follow its position, size and display scaling, show only while Elite is in front, hand each new image to a transparent click-through topmost window, and keep that window above the game.
- `overlay_native.py` is the seam. It builds `OverlayWindow(scene, font_path, keep_showing, groups)` and uses `start()`, `stop()`, `running`, `geometry` and `error`. A Linux window class that offers the same members would plug in without changing any feature.
- WFMT already runs `xdotool` on Linux (`platform_support.py`), including through `flatpak-spawn --host` for a Flatpak EDMC. It finds Elite's window by title and already knows that Elite under Proton is normally an XWayland window.

So the work is a second window layer, not a second overlay.

## Constraints

- **Runs inside EDMC's Python. Known.** EDMC provides Tk and Pillow. A user should not have to install a toolkit. A Flatpak EDMC has its own sandboxed Python and cannot see most host libraries. **Open:** which libraries a Flatpak EDMC's Python can load (libX11, libXext, libXrender, libXfixes) and whether it may open the X11 socket.
- **No window left behind. Known (design rule).** The Windows overlay lives in EDMC's process so it ends with EDMC. The same rule is wanted here, which argues against a separate helper process unless that process watches its parent.
- **Borderless or windowed only. Known.** A fullscreen game owns the screen. The Windows overlay says the same. **Open:** how compositors treat a borderless game that covers a whole monitor (see [Risks](#risks)).
- **Nothing sent anywhere, no new network use. Known (design rule).**
- **Linux is a first-class platform, tested on one setup. Known.** KDE Plasma on Wayland, Elite under Steam Proton, EDMC as a Flatpak. Other desktops need testers.

## What a Linux window has to do

| Need | Why | Status |
|---|---|---|
| A window with per-pixel transparency (alpha) | Text and rounded panels over the game, anti-aliased | **Open.** Needs a compositor and an ARGB window. |
| Mouse clicks pass through | The game must receive every click | **Known technique:** an empty input region (X11: the XShape extension's input shape; Wayland: an empty input region). **Open:** whether each compositor honors it for XWayland windows. |
| Never takes keyboard focus | Typing goes to the game | **Open.** Window hints plus an empty input region; layer-shell has an explicit "no keyboard" setting. |
| Stays above the game | After alt-tab the game can rise over the overlay | **Open.** Window type and state hints, or re-raising on a timer as the Windows overlay does. |
| Follows the game window's position, size and scaling | Cards must line up with the game | **Open.** `xdotool` reports XWayland coordinates, which may differ from true screen coordinates under fractional scaling. |
| Shows only while Elite is the window in front | Hide when the player is elsewhere | **Open** on Wayland: whether the active-window property reflects the true focus when a native Wayland window has it. |
| Survives Elite restarting, a monitor change and EDMC being slow | Reliability | **Open.** |
| The overlay appears in converted screenshots | Existing feature | **Known.** Works from the scene, not the window. |

## Options

### A. A window drawn by WFMT through Xlib (ctypes), on the X11 or XWayland connection

WFMT opens its own connection to the X server (through `ctypes` and `libX11`), creates a 32-bit ARGB window, sets an empty input shape, marks it as an always-on-top tool window and pushes the Pillow image into it.

- **For:** no new dependency; same in-process, thread-based lifecycle as the Windows overlay; works on X11 and on every Wayland desktop that runs XWayland (which is where Proton games live).
- **Against:** a fair amount of low-level code; works only where an X server is reachable, so not a native Wayland window; behavior differs between compositors.
- **Open:** every item in the table above, plus whether the sandbox allows it (E1, E2).

### B. A Tk toplevel with extras

Tk can make a borderless window and set whole-window opacity, but Tk has no per-pixel alpha on X11 as far as is known (**assumed**, not confirmed in the search done so far). A Tk window could be given a shaped outline (binary transparency, no anti-aliasing) through the XShape extension, which would be a reduced-quality fallback for X11 without a compositor.

- **For:** least new code. Tk is already there.
- **Against:** no smooth edges or translucent panels, and it still needs the same click-through and stacking work as option A.
- **Open:** whether Tk can be asked for a 32-bit visual and whether its drawing then carries alpha (E3). Worth a short test because it would remove most of the low-level code.

### C. A helper process with a full toolkit (Qt or GTK)

A separate Python program that WFMT starts, using Qt's translucent, input-transparent windows or GTK with a layer-shell library, fed the scene over a local socket.

- **For:** mature, well-documented windowing, and a native Wayland path where the compositor supports layer-shell (KDE Plasma, wlroots compositors; GNOME does not, see Sources).
- **Against:** the user must install the toolkit; a Flatpak EDMC cannot run it directly, so it would be started on the host (`flatpak-spawn --host`, which WFMT already uses for `xdotool`); two processes bring back the stale-window problem the Windows design avoids unless the helper exits when its parent does; more code and more things to package.
- **Note:** this is also the general shape of existing Linux overlay tools. Its public README lists Windows and Linux, host and Flatpak EDMC, GPL-3.0 and "100% Python", but does not say how its window is built.

### D. Native Wayland (layer-shell) from WFMT's own code

Talk to the compositor directly through `libwayland-client` with the layer-shell protocol.

- **For:** the proper Wayland way where it exists.
- **Against:** large amount of protocol code through ctypes; GNOME's Mutter does not implement layer-shell, so it would still need option A there; the game is an XWayland window anyway, so a native surface gains little for a borderless game.
- **Verdict:** not for the first version.

### E. Compositor-specific helpers (KWin scripting, GNOME extensions) and graphics-layer injection

KWin can be scripted over D-Bus for exact window geometry and "keep above" rules. A Vulkan layer (the way some frame-rate overlays work) draws inside the game and works even in fullscreen.

- **Verdict:** KWin geometry is worth keeping as an optional accuracy improvement for option A (E5). Everything else is out of scope: GNOME extensions are fragile, and a graphics layer is native code with a very different risk profile.

### Recommendation

Prototype **option A**, with **option B's Tk visual test (E3)** run first because it is cheap, and keep **option C** as the fallback if the sandbox blocks option A (E1) or per-pixel alpha cannot be had. The same `OverlayWindow` interface fits all three.

## Display servers and compositors

| Setup | What is known | What is open |
|---|---|---|
| **X11 with a compositor** | Per-pixel alpha needs a compositor (the core protocol cannot blend). Click-through by an empty input shape is a long-established technique. | Always-on-top behavior over a borderless game. |
| **X11 without a compositor** | No translucency is possible. | Whether a shaped, opaque fallback is worth having. |
| **Wayland, running Elite through XWayland** (the common case for Proton) | Several compositors apply an X11 window's input shape to the Wayland surface, but reports show gaps: one KWin change proposed ignoring the shape of XWayland windows, and a Mutter issue showed XWayland input regions covering more than the visible window. | Whether click-through works as needed on KWin and Mutter (E4). |
| **KDE Plasma on Wayland** | Implements layer-shell. This is the one setup tested for WFMT so far. | Option A behavior (E4, E5). |
| **GNOME on Wayland** | Mutter does not implement layer-shell. | Option A behavior (E6). |
| **wlroots compositors (Sway, Hyprland and similar)** | Implement layer-shell. A report shows an exclusive layer surface with an empty input region still capturing the pointer on Hyprland while it worked on Sway and niri. | Behavior of option A there (E6). |
| **Gamescope / Steam Deck gaming mode** | Not looked at. | Out of scope for now. |

## Experiments

Each is a small standalone script under `scripts/`, run by hand and kept out of the automated tests unless noted. Results go into the table at the end of this page. A script that opens a window is run in a virtual display in Docker where it can be, so it does not disturb a desktop in use.

| # | Question | How | Where |
|---|---|---|---|
| E0 | What does this machine look like? | A read-only script that prints the session type, desktop, whether a compositor owns the compositing selection, the display scaling, the Elite window's class, name, geometry and active state as `xprop`, `xwininfo` and `xdotool` see them, and whether it runs inside a Flatpak. Opens nothing. | Real desktop, Elite running |
| E1 | Can EDMC's Python (host and Flatpak) load libX11, libXext, libXrender and open the X socket? | Run `ctypes.CDLL` loads and `XOpenDisplay` from a plugin stub inside EDMC. | Host EDMC and Flatpak EDMC |
| E2 | Can WFMT create a 32-bit ARGB window, give it an empty input shape, and show a Pillow image with alpha, from a thread? | ctypes prototype. Take a screenshot of the virtual display to check pixels. | Docker: Xvfb + a compositor + a window manager |
| E3 | Can Tk be given an ARGB visual and draw with alpha? | A ten-line Tk test. | Docker, then real desktop |
| E4 | On KWin (Wayland), does the E2 window: show translucent, let clicks through to a window under it, keep keyboard focus off, stay above a borderless window, and follow it? | Manual, with a plain borderless test window first, then Elite. | Real desktop (this machine) |
| E5 | Is the XWayland geometry from `xdotool` right at 100%, 125% and 150% scaling, and with two monitors? Does KWin's D-Bus scripting give better numbers? | Compare against the game's own reported size and visual alignment of a test grid. | Real desktop |
| E6 | The same as E4 on GNOME (Mutter) and one wlroots compositor, and on plain X11. | Needs testers or a test machine. A headless Sway with XWayland may allow part of this in Docker. | Other setups |
| E7 | What happens when the game is borderless and covers the whole monitor: does the compositor skip compositing it (so the overlay cannot show), and does it matter which compositor? | Observe with E2's window over a borderless full-monitor test window. | Real desktop, other compositors |
| E8 | How long does one frame take (convert the Pillow image, send it, draw it) at 1080p, 1440p and 4K? Can it stay near 20 frames a second without burdening EDMC? | Timing in the E2 prototype. | Docker and real desktop |

## Plan

1. **Survey.** Write and run E0 on this machine with Elite running; record the facts that decide everything else (window class, geometry, scaling).
2. **Cheap spikes in Docker.** E3 first, then E1/E2 against a virtual display with a compositor. Pass means: pixels with alpha appear, clicks reach a window beneath, focus is not taken.
3. **Real compositor.** E4 and E5 on KDE Plasma, first with a stand-in borderless window, then with Elite. Decide here between option A and option C.
4. **Other desktops.** E6 and E7 with testers; record per-compositor results in the matrix below and in the Linux guide's known limits.
5. **Build.** A Linux window class with the same members as `OverlayWindow`, selected in `overlay_native.supported()` and `overlay_window` (one platform helper, no OS checks elsewhere), with the Windows-only settings text and the "not found" notice updated. Reuse the scene, raster, placement and tests.
6. **Test.** Pure parts (geometry math, environment detection, hint selection) get unit tests; window behavior is checked by the E-scripts and recorded in [LINUX_TESTING.md](LINUX_TESTING.md).
7. **Document.** Update [OVERLAY_SETUP.md](OVERLAY_SETUP.md), [platforms](guide/platforms.md), the README and [NATIVE_OVERLAY_SPEC.md](NATIVE_OVERLAY_SPEC.md), which currently says Linux is not planned.

**Done when:** on KDE Plasma (Wayland) with Elite borderless, the cards show with smooth edges, clicks and keys reach the game, the overlay hides when Elite is not in front, it follows the window, and closing EDMC removes it. Other desktops are listed with what was and was not checked.

## Risks

- **Compositor differences.** Click-through and stacking are the places compositors disagree. The mitigation is to detect the setup, use the safest hints, and say plainly in the guide where it is untested.
- **Borderless covering the monitor.** Some compositors stop compositing a window that covers its whole monitor, which would hide the overlay. Windowed mode with a slightly smaller window, or a compositor setting, may be needed. This could affect how many players the overlay helps.
- **XWayland scaling.** Fractional scaling can make X11 coordinates differ from what the player sees.
- **Sandbox limits.** A Flatpak EDMC may not be able to reach the X11 socket or libraries the way a host install can.
- **Time and testers.** Only one Linux setup can be checked directly.

## Results so far

| Experiment | Date | Setup | Result |
|---|---|---|---|
| (none run yet) | | | |

**This machine, as noted during this research:** KDE Plasma on Wayland; Tk 8.6, Pillow, python-xlib, PyGObject, PySide6 and pycairo are present in the host Python; `xdotool`, `xprop`, `xwininfo` and `wmctrl` are installed; EDMC is a Flatpak. These are the host's, not EDMC's own Python, which is what matters (E1).

## Sources

- KDE Plasma implements wlr-layer-shell; GNOME's Mutter does not; layer surfaces get pointer input unless the input region is set empty: [gtk4-layer-shell](https://github.com/ainola/gtk4-layer-shell), [Mutter issue 973](https://gitlab.gnome.org/GNOME/mutter/-/issues/973), [KWin mailing list, 2020](https://mail.kde.org/pipermail/kwin/2020-August/005149.html), [Hyprland discussion 14136](https://github.com/hyprwm/Hyprland/discussions/14136).
- X11 click-through by an input shape: [Shallow Thoughts, 2017](https://shallowsky.com/blog/2017/Apr/06), [Wine patch discussion](https://list.winehq.org/hyperkitty/list/wine-gitlab@list.winehq.org/message/F6EF5PFQ4SJG4DT3UUBDFUEI27H6QBU3/).
- XWayland and input shapes: [xserver merge request 1517](https://gitlab.freedesktop.org/xorg/xserver/-/merge_requests/1517), [KWin merge request 6247](https://invent.kde.org/plasma/kwin/-/merge_requests/6247), [Mutter issue 2593](https://gitlab.gnome.org/GNOME/mutter/-/issues/2593).
- Per-pixel alpha needs a compositor: [X Rendering Extension](https://en.wikipedia.org/wiki/X_Rendering_Extension).
- Existing overlay: [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay) (public README only).
