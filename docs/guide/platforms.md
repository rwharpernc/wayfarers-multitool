# Windows and Linux

**A note on Linux support.** Linux support is a commitment. WFMT's author uses both Linux (CachyOS) and Windows and spends about equal time on each.

- Most people who use the plugin are on Windows, so new features are proven on Windows first and Linux follows slightly behind.
- If something new works on Windows and not yet on Linux, that is the reason, not neglect: report it and it will be looked at.
- What has and has not been checked on Linux is listed in [Linux testing](../LINUX_TESTING.md).

WFMT runs on **Windows and Linux**, wherever EDMC does. Almost everything is the same on both, because it only reads the game's journal. A handful of features touch the operating system, and those are the ones that differ.

The Settings tabs for Auto-Honk, the screenshot auto-timer and the sound options say which systems the feature works on and whether it can work on *yours* right now. Look for the **Works on:** line (it names the missing tool, for example `xdotool`, when one is needed).

## Side by side

| Feature | Windows | Linux (Elite under Steam Proton or Wine) |
|---|---|---|
| Everything driven by the journal: Powerplay, Exploration, Mining, Missions, BGS, Colonization, Inventory tracking, Materials and Engineering, the Expedition planner, Ship Builds, Boxel Survey, Codex, Landing Assist, Interdiction Warning, Discovery Alerts | Yes | Yes, once EDMC's **Journal directory** points at the game's journals inside the Proton/Wine folder |
| **Report an issue** and **Copy diagnostics** (Settings → WFMT → General → Help) | Yes | Yes. **Report an issue** opens your default browser; the OS line names your distro, X11 or Wayland and whether EDMC is a Flatpak. A Flatpak EDMC keeps its log elsewhere ([Reporting a problem](reporting-problems.md#if-something-does-not-work)) |
| **Back up my data** (Settings → WFMT → General → Backup): one zip of your saved data in a folder you choose | Yes | Yes, with **Restore my data...** and **Back up automatically** on the same tab. A Flatpak EDMC can only write to folders it has been given, so if a backup says it cannot write there, choose one it can reach or grant it with `flatpak override --user --filesystem=<folder> io.edcd.EDMarketConnector` |
| **Route Planner** (PLOT in the section of the Exploration panel): a neutron route from Spansh's exact plotter for your ship (read from the journal), every jump listed and followed, with the next system copied to the clipboard on request or automatically | Yes | Yes. Needs the network only when you press Plot; copying the next system needs a working clipboard |
| **Carrier Route** (the Carrier route button in the Route Planner window): a route for your fleet carrier from Spansh's fleet carrier router, filled in from the journal, followed as the carrier jumps | Yes | Yes. Needs a working clipboard to copy systems (quick pass on Linux, 2026-10-20) |
| **Exploration Dashboard** (DASHBOARD on the Exploration panel): the window of everything known about the system, the body and the biology, with overlay switches | Yes | Yes. Reads only what WFMT already holds; the overlay switches work with either overlay. Needs a window manager that lets WFMT's windows open as it does for the others |
| **Ship planner** (Engineering window): paste an EDSY or Coriolis loadout | Yes | Yes. **Paste from clipboard** needs a working clipboard; you can also paste into the box by hand |
| **Game mode and credits lines** under the mode buttons | Yes | Yes (same journal data; the Journal directory must be set) |
| **Trade**: session profit and costs, stock, carrier cargo, Trade History (including **Export log (CSV)**), and the Spansh route and price lookups | Yes | Yes. The Journal directory must be set: Trade reads the journals to catch a session up after EDMC was closed |
| **Auto-Honk** (presses your Discovery Scanner key for you) | Yes | Yes, needs **`xdotool`**. X11 or XWayland windows only, not a native Wayland window |
| **Screenshot auto-timer** and **Thargoid-scan capture** (press the screenshot key for you) | Yes | Yes, needs **`xdotool`** |
| Screenshot conversion and renaming | Yes | Yes (Elite's `Pictures` folder inside the Proton/Wine folder) |
| **Sounds**: the Inventory pickup sound, the Flight Alerts sound and the Shortcuts confirmation sound | Yes (system beep) | Yes, needs `canberra-gtk-play` or `paplay` where EDMC runs (inside a Flatpak, that means inside the Flatpak); without one the Inventory and Flight Alerts sound ticks are grayed out and the Shortcuts sound stays silent |
| On-screen overlay features | WFMT's built-in overlay (nothing to install), or EDMCModernOverlay | **EDMCModernOverlay is required** (the built-in overlay is Windows only for now; a Linux version is being researched) |
| The Mining radar over the game (a picture on the overlay) | Yes, with WFMT's built-in overlay | No (EDMCModernOverlay cannot draw a picture; use the Surface Live window) |
| Keyboard shortcuts (CTR, BRD, radar range, Live window, hide overlays) | Yes (Ctrl+Alt+Shift plus a key) | No (use the chat commands, which work on both) |
| Chat commands (`!wf center` and the rest, typed in Elite's chat) | Yes | Yes |
| Include the overlay in converted screenshots | Yes (built-in overlay) | No |
| Self-update (Settings → WFMT → General → Updates) and the data backup before it | Yes | Yes |
| **Local star index** (Settings → WFMT → General → Online lookups): download, update and delete | Yes | Yes. Needs about 300 MB of free space while it builds (110 MB afterwards) in the plugin folder; with a Flatpak EDMC that folder is inside its own data folder, which it can write to |
| Finding your screen size for overlay placement | Elite's own window (built-in overlay), `DisplaySettings.xml`, or the operating system's hardware resolution | EDMCModernOverlay's log, `DisplaySettings.xml` (a Flatpak needs permission 5), then `xrandr`. Display scaling cannot be read, so set it by hand ([Overlay Placement](../OVERLAY_SETUP.md#moving-things-around)) |
| Overlay **Corners**, **Keep showing when Elite is not the window in front** and the Windows capture-tool detection | Yes (built-in overlay) | No (they belong to the built-in overlay) |
| Credits line, Credits Ledger, Settings, windows and their Help buttons | Yes | Yes (same journal data; the Journal directory must be set) |
| Copy to clipboard buttons (Copy system, Copy next, Copy Shopping List) | Yes | Yes, needs a working clipboard |

## Windows only

- **OneDrive folder-redirect handling** for the Screenshot Directory, and the **Controlled Folder Access** hint
  when Windows blocks writing screenshots. Both are automatic and only appear on Windows.

## Linux only

- The **Elite Wine/Proton prefix** box in Settings → WFMT → Exploration → Auto-Honk. Leave it blank to auto-detect Steam.
- The hint about EDMC's **Journal directory**.

Full Linux setup is in [WFMT on Linux](linux.md).

## macOS

macOS is **not supported or tested**. Journal-driven features may work, but key simulation and sounds don't, and
nothing has been checked there.

## For the technical details

Exactly which files, folders and commands each system uses is in
[TECHNICAL.md section 18](../TECHNICAL.md#18-platform-support-windows-and-linux).
