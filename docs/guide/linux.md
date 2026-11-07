# WFMT on Linux

Setup of WFMT on Linux: support status, overlays, and the configuration steps.

## Linux support

WFMT runs on Linux wherever EDMC runs. Features are verified on Windows first. Checked configurations and open checks are listed in [Linux testing](../LINUX_TESTING.md).

## Tested configurations

One real installation has been tested: KDE Plasma on Wayland, Elite under Steam Proton, EDMC as a Flatpak.

- **2026-10-18:** a pass of an earlier build on that configuration covered the Settings panel, the on-screen overlays, Auto-Honk, the screenshot features, Trade and Exploration, including the Route Planner checklist.
- **2026-10-20:** the Carrier Route window, the two mining books, Mining History and the Rare Goods Finder had a quick pass, not the full checklist.
- The problem found on 2026-10-18, right-hand overlay cards stopping short of the screen edge, is described in [Known issues](known-issues.md).
- Not tested: other distributions, other desktops, X11 sessions and a non-Flatpak EDMC. The data backup has not been tried on Linux.

## Overlays on Linux

On-screen overlays on Linux require EDMCModernOverlay.

- WFMT's built-in overlay is Windows only.
- Install [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay) (Step 1) for every WFMT on-screen display.
- Without it, all other WFMT features work.
- When EDMCModernOverlay is not found, the overlay settings pages show a notice in orange at the top. Settings can be changed and are kept; nothing appears on screen until it is installed.

Elite runs under Steam Proton or Wine on Linux, which requires the steps below, in order.

| Setup | Steps |
|---|---|
| Journal-based features only (Powerplay, Missions, BGS, Trade...) | 2 (and 3 if EDMC is a Flatpak) |
| Plus Auto-Honk or the screenshot timer | 1, 2, 4 (and 3 if Flatpak) |
| Plus on-screen overlays | 1, 2, 5 (and 3 if Flatpak) |
| Plus backups, the star index, updates or sounds | 7 |

## Step 1: Install the helper tools

- **`xdotool`** presses keys in Elite's window for Auto-Honk and the screenshot auto-timer. Install it on the system, not inside a container:

  | Distribution | Command |
  |---|---|
  | Debian / Ubuntu | `sudo apt install xdotool` |
  | Arch / CachyOS | `sudo pacman -S xdotool` |
  | Fedora | `sudo dnf install xdotool` |

  `xdotool` works on X11, and on Wayland through XWayland (where a Proton game's window runs). It does not work with a native Wayland window.

- **EDMCModernOverlay** draws the on-screen cards. Install it as an EDMC plugin from its [project page](https://github.com/SweetJonnySauce/EDMCModernOverlay). WFMT's default connection settings (`127.0.0.1`, port 5010) match its defaults.
  - It is required for every WFMT on-screen display on Linux.
  - Its default font has capital letters only. **Settings → WFMT → Overlays → Appearance → Overlay font** can place a lower case font first in its list (restart EDMC afterwards).
- Optional: `canberra-gtk-play` or `paplay` for notification sounds.

## Step 2: Tell EDMC where Elite's journals are

Linux has no default journal folder. Without one, WFMT's journal-based features have no data (including the BGS rebuild of tick totals).

1. In EDMC, open **File → Settings → Configuration**.
2. Set **Journal directory** to the `Saved Games/Frontier Developments/Elite Dangerous` folder inside Elite's Proton folder. A typical path:

   ```
   ~/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous
   ```

3. Restart EDMC.

WFMT shows a hint under **Settings → WFMT → Exploration → Auto-Honk** and **Settings → WFMT → BGS** when the folder appears wrong, and logs a hint at startup.

**The Elite Wine/Proton prefix box.**

- WFMT finds the Proton folder itself, including extra Steam library folders and Flatpak Steam.
- Enter a folder under **Settings → WFMT → Exploration → Auto-Honk → Elite Wine/Proton prefix** only for Lutris, Heroic or a custom setup. Otherwise leave the field empty.
- A wrong value in the box prevents WFMT from finding the keybindings, because WFMT does not fall back to auto-detection when the box is filled.

## Step 3: If EDMC is a Flatpak, grant it five permissions

A Flatpak runs in a sandbox that cannot see the Steam folders, the keyboard tools or the desktop. Without these permissions WFMT's settings display normally but the features do not work.

Run each command once in a terminal, then restart EDMC. The commands widen the access of EDMC only.

```bash
# Set this to the Elite Proton folder (the folder of Step 2, without the trailing parts).
PFX="$HOME/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser"

# 1. Journals (EDMC reads the journal and Status.json, and keeps a lock file there)
flatpak override --user --filesystem="$PFX/Saved Games/Frontier Developments/Elite Dangerous" io.edcd.EDMarketConnector

# 2. Keybindings (read-only; Auto-Honk reads the bound key)
flatpak override --user --filesystem="$PFX/AppData/Local/Frontier Developments/Elite Dangerous/Options/Bindings:ro" io.edcd.EDMarketConnector

# 3. Screenshots (read and write; WFMT converts and files them)
flatpak override --user --filesystem="$PFX/Pictures/Frontier Developments/Elite Dangerous" io.edcd.EDMarketConnector

# 4. Run host programs: starts the overlay window and runs the system's xdotool
flatpak override --user --talk-name=org.freedesktop.Flatpak io.edcd.EDMarketConnector

# 5. Screen size (read-only; Overlay Placement reads Elite's screen size)
flatpak override --user --filesystem="$PFX/AppData/Local/Frontier Developments/Elite Dangerous/Options/Graphics:ro" io.edcd.EDMarketConnector
```

**Permission 5.** No error occurs without it.

- Without it, WFMT cannot read Elite's `DisplaySettings.xml` and takes the overlay window size from EDMCModernOverlay's log.
- If the log does not provide it, WFMT asks `xrandr` for the primary monitor's size (through the host from a Flatpak).
- Only if `xrandr` is also unavailable does WFMT assume a 1920 x 1080 screen, which places cards at the right and bottom edges incorrectly.
- Overlay Placement states which source was used.
- On a desktop with display scaling (KDE or GNOME at 125% or more), set **Display scaling** on Overlay Placement to match, because WFMT cannot read it on Linux.

In fish, replace the first line with `set PFX "$HOME/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser"` and use `$PFX` in the other commands.

Verify the overrides:

```bash
flatpak override --user --show io.edcd.EDMarketConnector
```

Notes:

- **Flatpak Steam:** the Proton folder is under `~/.var/app/com.valvesoftware.Steam/.local/share/Steam/`.
- **Plugin folder:** a Flatpak EDMC keeps its plugins in `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/plugins`.
- **Native or AppImage EDMC:** skip this step.

**Permission 4.** EDMCModernOverlay starts its drawing window through the host, and WFMT runs `xdotool` the same way. Without the permission:

- **Check connection** reports success (the overlay's port is open) but nothing is drawn.
- Auto-Honk reports that `xdotool` is not installed even when it is.

## Step 4: Bind a keyboard key for the honk (Auto-Honk only)

Auto-Honk presses keyboard keys only. When the fire buttons are bound only to a mouse or HOTAS button, Auto-Honk reports "only bound to a joystick/HOTAS button".

1. In Elite, open **Options → Controls → Ship → Cockpit Modes**.
2. Add a keyboard key to the second slot of **Secondary Fire**. Keep the mouse or stick binding in the first slot.
3. In EDMC, open **Settings → WFMT → Exploration → Auto-Honk** and select **Rescan**. The page reports "Will press <key>".
4. Select **Test Honk Now** with the ship able to use its scanner.
5. Set the **hold time** to the number of seconds the scan needs. The key is held for the full time.

## Step 5: Check the overlay

1. Start EDMC and Elite (borderless or windowed).
2. Open **Settings → WFMT → Overlays → Overlay Connection** and select **Check connection**.
3. Select a **Test** button, such as **Test Discovery** or **Test Notable** under **Settings → WFMT → Overlays**.

Cards appear over the game. If they do not, see the Linux entries in [Troubleshooting](troubleshooting.md).

- When one display is missing and the others show, its saved position can be outside the screen. See [the remedy](troubleshooting.md#one-display-never-shows-though-test-and-the-overlay-window-both-work).
- The general overlay guide is [Setting up the on-screen overlay](../OVERLAY_SETUP.md).

## Step 6: Trade

Trade requires no installation beyond Step 2. EDMC's **Journal directory** enables WFMT to:

- catch a trading session up after play with EDMC closed,
- rebuild the carrier's cargo history at start-up,
- read the docked station's `Market.json`.

When the folder is wrong or empty, these functions find no data, and the session counts only what EDMC delivered while running. For a Flatpak EDMC, the journals permission in Step 3 covers this.

- The Spansh lookups require the network.
- **Export log (CSV)** in Trade History uses a standard file dialog. With a Flatpak EDMC, a failed save is resolved by choosing a folder EDMC may write to (WFMT shows the error).

## Step 7: Backups, the star index and updates

No installation is required. A Flatpak EDMC has the following limits:

- **Back up my data** (Settings → WFMT → General → Backup) and **Back up automatically** write to a chosen folder, which must be outside the plugin folder. A Flatpak EDMC can write only to folders it has been granted: choose its own data folder, or grant a folder with `flatpak override --user --filesystem=<folder> io.edcd.EDMarketConnector`. A manual backup shows the line `Saved N files (size) to <path>` or the reason it failed. The file is named `WFMT-data-<date>.zip`. The backup has not been tried on Linux.
- **Restore my data...** requires the same folder permission to read the zip. The restore is applied at the next EDMC start.
- **The Local star index** (Settings → WFMT → Online) downloads one file from Spansh (about 173 MB) and builds an index in the plugin folder, which needs about 300 MB free during the build. The index is optional.
- **Automatic updates** (Settings → WFMT → Online) work as on Windows. The update takes effect when EDMC is restarted.
- **Sounds** (the Inventory pickup sound, Flight Alerts and the shortcut confirmation) require `canberra-gtk-play` or `paplay` on the system. The option is grayed out without one. WFMT looks for the player inside the Flatpak's own environment, not on the host, so with a Flatpak EDMC the sounds can be unavailable although the system has a player.
- **Keyboard shortcuts** are not available on Linux. Use the chat commands (`!wf overlays` and the others) after enabling them under General → Shortcuts.

## More information

- Tester checklist: [LINUX_TESTING.md](../LINUX_TESTING.md).
- Platform differences: [TECHNICAL.md section 18](../TECHNICAL.md#18-platform-support-windows-and-linux).
- Feature availability: [Windows and Linux](platforms.md).
