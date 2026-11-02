# Screenshots and input automation technical specification

This document specifies the two WFMT features that send key presses to the game, **Auto-Honk** and timed or automatic screenshot capture, together with the conversion and cropping of screenshots and the platform differences on Linux. Usage is described in [the operations guide](guide/operations.md). The general code organization is described in [TECHNICAL.md](TECHNICAL.md).

- **Author:** R.W. Harper (CMDR Mactavious)

WFMT is journal-first: it uses the information the game writes to its journal files and fills gaps from Frontier data or community services where they exist. See [the design principle in TECHNICAL.md](TECHNICAL.md).

## 1. Input automation

WFMT asks the operating system to press a key, as if it were pressed on the keyboard, only while an Elite Dangerous window exists. The screenshot timer additionally requires that window to have focus.

- **Windows:** Win32 key events (`keybd_event`, and `ctypes` calls to `user32.dll`).
- **Linux:** the `xdotool` program, which sends keys to the focused window through the X server (X11, or XWayland on a Wayland desktop).

Constraints:

- WFMT does not read or change the game's memory, inject code into the game, or alter game files.
- The feature sends nothing over the network.
- Only keyboard keys can be pressed. Joystick and HOTAS buttons cannot.
- Nothing is sent unless the feature is enabled (the exception is described in section 6).
- Every entry point is a no-op when unsupported (for example on macOS, or on Linux without `xdotool`). It returns "not done" and the rest of WFMT continues. A failed key press does not affect journal handling.

## 2. Auto-Honk

Auto-Honk fires the ship's Discovery Scanner (the system-wide scanner, not the surface scanner) on arrival in a system. It is off by default.

1. **Trigger:** a `FSDJump` or `CarrierJump` journal event. A `LoadGame` event clears the record of systems visited in the session.
2. **Skip repeats** (**Skip systems already visited**, default on): each system is honked once per session, identified by its system address.
3. **Key lookup:** the active binds file is read: the most recently modified `<preset>.<major>.<minor>.binds` file, where the preset is named in `StartPreset.start` (usually `Custom`). The keyboard key assigned to the selected fire button (Primary or Secondary; default Secondary) is used. If that button is bound only to a joystick button, is not bound, or is bound to a key WFMT cannot produce, nothing is sent and the Settings tab states the reason.
4. **Press and hold:** the key is held for the configured time (default 10 seconds, `DEFAULT_HOLD_MS` = 10000). The setting is stored with a minimum of 1 second. The scanner charges while the button is held, so a short press does not honk. The hold runs on a background thread.
5. **Focus** (**Focus game window first**, default on): the Elite window is brought to the front before the key is sent.

Outcomes shown in Settings: sent; Elite window not found; no usable keybind; unsupported OS; `xdotool` missing (Linux); error (see the EDMC log). The **Test Honk Now** button runs the same steps on demand. WFMT shows a warning to disable one of the two when a co-pilot application with its own auto-honk is detected.

## 3. Screenshots

### 3.1 Processing

When Elite takes a screenshot, the game writes a raw file and logs a `Screenshot` event. WFMT then performs the following steps.

1. **Locate the file.** The `Filename` field of the event is not a usable path, so only its base name is used. The file is searched for in the configured Screenshot Directory, then in fallback locations. If the file is found outside the configured folder, the setting is corrected.
2. **Convert to PNG** (Pillow) and save under the generated name in the output folder. The output folder can be grouped into one subfolder per system.
3. **Show thumbnails:** the newest capture, an optional cropped version, and a history of the last 8 captures (4 per row). A thumbnail opens a larger preview.
4. **Delete the original** (optional, off by default) after a grace period of 60 seconds (`_DELETE_GRACE_MS`), so other plugins can read the raw file.
5. **Notify:** a status line in the panel and, when an overlay is in use, an on-screen message shown for 10 seconds (20 seconds for the Settings test message).

Conversion and cropping work on every platform. Only key simulation is platform-specific.

### 3.2 File names

File names are generated from a mask. Tokens:

| Token | Replaced by |
|---|---|
| `SYSTEM` | System name |
| `BODY` | Body name, with the leading system name removed |
| `CMDR` | Commander name |
| `DATE` | UTC timestamp |
| `NNNNN` | Five-digit sequence number, unique per output folder (WFMT reads the existing files and uses the next number) |

Characters that a file system can reject are removed. A hi-res capture (the game's `HighRes` file names) receives the prefix `HighRes_`.

### 3.3 Cropping

The `Screenshot` event does not state the open panel. WFMT reads `GuiFocus` from `Status.json` at the moment of the event. For the Target, Comms, Role and Systems panels it creates a second, cropped picture of that panel. Hi-res captures are not cropped.

| `GuiFocus` | Panel | Crop rectangle (1920×1080 reference frame) |
|---|---|---|
| 1 | Systems (internal panel) | 451, 270, 1460, 837 |
| 2 | Target (external panel) | 850, 279, 1306, 538 |
| 3 | Comms | 406, 123, 919, 832 |
| 4 | Role | 451, 270, 1460, 837 |

The rectangles are scaled uniformly (by the smaller of the two axis ratios) and centered, because the HUD panels keep their proportions and are centered on ultrawide and multi-monitor displays. A Thargoid capture crops the bottom-left quadrant of the screen (see section 6).

### 3.4 Timer

The optional auto-capture timer (a clock icon) presses the screenshot key (F10) every poll interval (default 1 second, minimum 0.2 seconds).

- The timer is off each time EDMC starts.
- It fires only while an Elite window has focus. Otherwise the status reads "Auto-capture paused (Elite not focused)".
- It stops on `ShutDown` and `Died`.
- The key is held for 60 ms (`_KEY_HOLD_MS`) and then released.
- **Hi-res on timer** (off by default) adds Left Alt for an Alt+F10 capture. It applies only in Solo mode, the only game mode in which hi-res captures are permitted.

## 4. Main window size

Every image in the panel is placed in a box of fixed width and height, so an ultrawide capture cannot widen the EDMC main window. See [TECHNICAL.md](TECHNICAL.md) section 5.

## 5. Linux

Elite runs under Steam Proton or Wine on Linux, so the game's Windows folders are inside a Wine prefix.

- `platform_support.py` locates the prefix (including additional Steam library folders and Flatpak Steam; Settings provides an override for Lutris, Heroic and custom setups) and derives the binds folder, the Pictures (screenshot) folder and the journal folder from it.
- Keys are sent with `xdotool` after the game window is focused.
- Auto-Honk and the timer work on X11 and on XWayland.
- A missing item is reported as "not found". No exception is raised.

## 6. Automatic Thargoid capture

The setting **Automatically capture a screenshot when scanning a Thargoid signal** (key `wfmt_screenshot_thargoid_capture`) is on by default. On a `MaterialCollected` event for `tg_shipflightdata` or `unknownshipsignature`, WFMT presses the screenshot key once and crops the result to the bottom-left quadrant. A `Music` event with the track `Unknown_Encounter` or `Combat_Unknown` marks subsequent captures for the same crop, without triggering a capture. This is the only key press WFMT sends without a feature being enabled first. The setting is in Settings → WFMT → Operations → Screenshots.

## 7. Settings

Settings → WFMT → Operations → Screenshots (keys beginning `wfmt_screenshot_`): source and output folders, delete originals, group by system, file-name mask, timer icon, hi-res on timer, Thargoid capture and poll interval. The overlay notification is set in Settings → WFMT → Overlays → Screenshots.

Settings → WFMT → Exploration → Auto-Honk (keys beginning `wfmt_autohonk_`): enabled, fire button, hold time, focus the game window and skip visited systems. The Linux prefix override is stored as `wfmt_elite_prefix`.

## 8. Tests

- `tests/test_platform_support.py`: Linux helpers (prefix and folder discovery, key naming).
- `tests/test_screenshot_files.py`: file-name masks, crop rectangles, conversion, thumbnails (including that a thumbnail is bounded on both axes) and delayed deletion.
- Key simulation is not covered by an automated test.

Every failure path returns a result and does not raise an exception.

## 9. Limitations

- Auto-Honk and the timer press keyboard keys only.
- The crop rectangles are fixed measurements. A change to the game HUD can make them incorrect.
- Controlled Folder Access or antivirus software on Windows can block file access. The error message states this.
- Key simulation is not supported on macOS. Conversion and cropping work.
- Key simulation is not supported on Linux under Wayland without XWayland.
