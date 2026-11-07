# Windows and Linux

WFMT runs on Windows and Linux, wherever EDMC runs. Most features read only the game's journal and behave identically on both systems. Features that use the operating system differ as listed below.

Features are verified on Windows first. The tested Linux configurations and open checks are listed in [Linux testing](../LINUX_TESTING.md).

The Settings tabs for Auto-Honk, the screenshot auto-timer and the sound options contain a **Works on:** line. The line states the systems on which the feature works, whether it can work on the current system, and the missing tool (for example `xdotool`) when one is required.

## Side by side

| Feature | Windows | Linux (Elite under Steam Proton or Wine) |
|---|---|---|
| Journal-driven features: Powerplay, Exploration, Mining, Missions, BGS, Colonization, Inventory tracking, Materials and Engineering, the Expedition planner, Ship Builds, the Combat Record, Boxel Survey, Codex, Landing Assist, Interdiction Warning, Discovery Alerts | Yes | Yes, when EDMC's **Journal directory** points at the game's journals inside the Proton or Wine folder |
| Pop-out windows open on EDMC's monitor | Yes. Each monitor's edges are read | A window without a remembered position opens centered over the EDMC window and is kept on the visible screen. Tk reports only the whole screen, so monitor edges are not known. A remembered position is reused |
| **Report an issue** and **Copy diagnostics** (Settings → WFMT → General → Help) | Yes | Yes. **Report an issue** opens the default browser. The OS line names the distribution, X11 or Wayland, and whether EDMC is a Flatpak. A Flatpak EDMC keeps its log elsewhere ([Reporting a problem](reporting-problems.md#if-something-does-not-work)) |
| **Back up my data** (Settings → WFMT → General → Backup): one zip of saved data in a chosen folder | Yes | Yes, with **Restore my data...** and **Back up automatically** on the same tab. A Flatpak EDMC can write only to folders it has been granted. Choose such a folder or grant one with `flatpak override --user --filesystem=<folder> io.edcd.EDMarketConnector` |
| **Route Planner** (Plot in the Exploration panel): a neutron route from Spansh's exact plotter for the ship read from the journal, with every jump listed and followed, and the next system copied to the clipboard on request or automatically | Yes | Yes. The network is used only when **Plot** is pressed. Copying the next system requires a working clipboard |
| **Carrier Route** (the Carrier route button in the Route Planner window): a route for the fleet carrier from Spansh's fleet carrier router, filled in from the journal and followed as the carrier jumps | Yes | Yes. Copying systems requires a working clipboard |
| **Exploration Dashboard** (Dashboard on the Exploration panel): a window showing what is known about the system, the body and the biology, with overlay switches | Yes | Yes. It reads only data WFMT already holds. The overlay switches work with either overlay |
| **Ship planner** (Engineering window): import of an EDSY or Coriolis loadout | Yes | Yes. **Paste from clipboard** requires a working clipboard; text can also be pasted into the box |
| **Game mode and credits lines** under the mode buttons | Yes | Yes (journal data; the Journal directory must be set) |
| **Trade**: session profit and costs, stock, carrier cargo, Trade History (including **Export log (CSV)**), Spansh route and price lookups | Yes | Yes. The Journal directory must be set: Trade reads the journals to catch a session up after EDMC was closed |
| **Auto-Honk** (presses the Discovery Scanner key) | Yes | Yes. Requires **`xdotool`**. X11 or XWayland windows only, not native Wayland windows |
| **Screenshot auto-timer** and **Thargoid-scan capture** (press the screenshot key) | Yes | Yes. Requires **`xdotool`** |
| Screenshot conversion and renaming | Yes | Yes (Elite's `Pictures` folder inside the Proton or Wine folder) |
| **Sounds**: the Inventory pickup sound, the Flight Alerts sound and the Shortcuts confirmation sound | Yes (system beep) | Yes. Requires `canberra-gtk-play` or `paplay` where EDMC runs (inside the Flatpak for a Flatpak EDMC). Without one, the Inventory and Flight Alerts sound options are grayed out and the Shortcuts sound is silent |
| On-screen overlay features | WFMT's built-in overlay, or EDMCModernOverlay | **EDMCModernOverlay is required.** The built-in overlay is Windows only |
| The Mining radar over the game (a picture on the overlay) | Yes, with WFMT's built-in overlay | No. EDMCModernOverlay cannot draw a picture. The Surface Live window shows the radar |
| Keyboard shortcuts (Mark center, Mark border, radar range, Live window, hide overlays) | Yes (Ctrl+Alt+Shift plus a key) | No. Chat commands work on both systems |
| Chat commands (`!wf center` and the others, typed in Elite's chat) | Yes | Yes |
| Overlay included in converted screenshots | Yes (built-in overlay) | No |
| Self-update (Settings → WFMT → Online) and the data backup before it | Yes | Yes |
| **Local star index** (Settings → WFMT → Online): download, update and delete | Yes | Yes. About 300 MB of free space is needed while the index is built (110 MB afterwards) in the plugin folder. For a Flatpak EDMC the plugin folder is inside its own data folder, which it can write to |
| Screen size detection for overlay placement | Elite's window (built-in overlay), `DisplaySettings.xml`, or the operating system's hardware resolution | EDMCModernOverlay's log, `DisplaySettings.xml` (a Flatpak requires permission 5), then `xrandr`. Display scaling cannot be read and is set manually ([Overlay Placement](../OVERLAY_SETUP.md#moving-things-around)) |
| Overlay **Corners**, **Keep showing when Elite is not the window in front**, and Windows capture-tool detection | Yes (built-in overlay) | No (built-in overlay features) |
| Credits line, Credits Ledger, Settings, windows and their Help buttons | Yes | Yes (journal data; the Journal directory must be set) |
| Copy to clipboard buttons (Copy System, Copy Next, Copy Shopping List) | Yes | Yes. Requires a working clipboard |

## Windows only

- **OneDrive folder-redirect handling** for the Screenshot Directory, and the **Controlled Folder Access** hint shown when Windows blocks writing screenshots. Both are automatic.

## Linux only

- The **Elite Wine/Proton prefix** box in Settings → WFMT → Exploration → Auto-Honk. An empty box selects Steam auto-detection.
- The hint about EDMC's **Journal directory**.

The Linux setup is in [WFMT on Linux](linux.md).

## macOS

macOS is not supported and has not been tested.

## Technical details

The files, folders and commands each system uses are listed in [TECHNICAL.md section 18](../TECHNICAL.md#18-platform-support-windows-and-linux).
