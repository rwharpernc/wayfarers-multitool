# WFMT on Linux

## Linux support

Linux support is a commitment. WFMT's author uses both Linux (CachyOS) and Windows and spends about equal time on each. Most people who use the plugin are on Windows, so new features are proven on Windows first and Linux follows slightly behind.

If something new works on Windows and not yet on Linux, that is the reason, not neglect: report it and it will be looked at. What has and has not been checked on Linux is listed in [Linux testing](../LINUX_TESTING.md).

## What has been tested

WFMT runs on Linux wherever EDMC does. It has been tested on one real install: KDE Plasma on Wayland, Elite under Steam Proton, EDMC as a Flatpak.

- **2026-10-18:** a Linux pass of an earlier build of this code on that setup went well. It covered the Settings panel, the on-screen overlays, Auto-Honk, the screenshot features, Trade, Exploration and the rest. It also passed the Route Planner checklist.
- **2026-10-20 (an earlier build of this code):** the Carrier Route window, the two mining books, Mining History and the Rare Goods Finder had a quick pass on Linux, not the full checklist.
- **The one problem found** on 2026-10-18, right-hand overlay cards stopping short of the screen edge, is described in [Known issues](known-issues.md).
- **Not tested yet:** other distributions, other desktops, X11 sessions or a non-Flatpak EDMC, so they may behave differently. The data backup has not been tried on Linux. Please report anything odd.

## Overlays on Linux

**On-screen overlays on Linux need EDMCModernOverlay.**

- WFMT's own built-in overlay is **Windows only**, and a Linux version is being researched (it needs window handling that differs between X11 and Wayland). Until one exists, this is the overlay to use.
- Linux has no built-in overlay to switch to, so install [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay) (Step 1) for every WFMT on-screen display.
- Without it everything else in WFMT still works.
- If EDMCModernOverlay is not found, the overlay settings pages say so, in orange at the top. The settings can still be changed and are kept; nothing appears on screen until it is installed.

Elite runs under Steam Proton or Wine on Linux, which needs a few extras. **Work through the steps in order.**

**Which steps do I need?**

| Your setup | Steps |
|---|---|
| Just the journal-based features (Powerplay, Missions, BGS, Trade...) | 2 (and 3 if EDMC is a Flatpak) |
| Plus Auto-Honk or the screenshot timer | 1, 2, 4 (and 3 if Flatpak) |
| Plus on-screen overlays | 1, 2, 5 (and 3 if Flatpak) |
| Plus backups, the star index, updates or sounds | 7 |

## Step 1: Install the helper tools

- **`xdotool`** presses keys in Elite's window for Auto-Honk and the screenshot auto-timer. Install it **on your
  system** (not inside anything):

  | Distribution | Command |
  |---|---|
  | Debian / Ubuntu | `sudo apt install xdotool` |
  | Arch / CachyOS | `sudo pacman -S xdotool` |
  | Fedora | `sudo dnf install xdotool` |

  It works on X11, and on Wayland through XWayland (which is where a Proton game's window lives). It does not
  work with a *native* Wayland window.

- **EDMCModernOverlay** draws the on-screen cards. Install it as an EDMC plugin from its
  [project page](https://github.com/SweetJonnySauce/EDMCModernOverlay).
  WFMT's default connection settings (`127.0.0.1`, port 5010) already match it.
  - **Required for every WFMT on-screen display on Linux:** WFMT's own built-in overlay is **Windows only** for now, so this is the only overlay you can use on Linux.
  - Its default font has capital letters only. **Settings → WFMT → Overlays → Appearance → Overlay font** can put a lower case font first in its list (restart EDMC afterwards).
- Optional: `canberra-gtk-play` or `paplay` for notification sounds.

## Step 2: Tell EDMC where Elite's journals are

Linux has no default journal folder, and without one WFMT's journal-based features have nothing to read (that
includes BGS rebuilding the tick's totals).

1. In EDMC, open **File → Settings → Configuration**.
2. Set **Journal directory** to the `Saved Games/Frontier Developments/Elite Dangerous` folder inside Elite's
   Proton folder. It is usually:

   ```
   ~/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous
   ```

3. Restart EDMC.

WFMT shows a hint under **Settings → WFMT → Exploration → Auto-Honk** and **Settings → WFMT → BGS** if it looks wrong, and logs one at startup.

**The Elite Wine/Proton prefix box.**

- WFMT finds the Proton folder itself, including extra Steam library folders and Flatpak Steam.
- Only if you use Lutris, Heroic or a custom setup should you enter the folder under **Settings → WFMT → Exploration → Auto-Honk → Elite Wine/Proton prefix**. Otherwise **leave that field empty**.
- **Warning:** a wrong value in that box stops WFMT from finding your keybindings, because it deliberately does not fall back to auto-detection.

## Step 3: If EDMC is a Flatpak, grant it five permissions

A Flatpak runs in a sandbox that cannot see your Steam folders, your keyboard tools or your desktop. Without these
permissions, WFMT looks fine in its settings but does nothing.

Run each command once in a terminal, then **restart EDMC**. They only widen what EDMC can reach; nothing else
about the sandbox changes.

```bash
# Set this to your Elite Proton folder (the same one as Step 2, without the trailing parts).
PFX="$HOME/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser"

# 1. Journals (EDMC reads the journal and Status.json, and keeps a lock file there)
flatpak override --user --filesystem="$PFX/Saved Games/Frontier Developments/Elite Dangerous" io.edcd.EDMarketConnector

# 2. Keybindings (read-only; Auto-Honk needs to know which key you bound)
flatpak override --user --filesystem="$PFX/AppData/Local/Frontier Developments/Elite Dangerous/Options/Bindings:ro" io.edcd.EDMarketConnector

# 3. Screenshots (read and write; WFMT converts and files them)
flatpak override --user --filesystem="$PFX/Pictures/Frontier Developments/Elite Dangerous" io.edcd.EDMarketConnector

# 4. Run host programs: lets the overlay window start, and lets WFMT use your system's xdotool
flatpak override --user --talk-name=org.freedesktop.Flatpak io.edcd.EDMarketConnector

# 5. Screen size (read-only; Overlay Placement reads Elite's screen size, so cards at the right and bottom edges land where you place them)
flatpak override --user --filesystem="$PFX/AppData/Local/Frontier Developments/Elite Dangerous/Options/Graphics:ro" io.edcd.EDMarketConnector
```

**Permission 5 is the one people skip** because nothing breaks without it.

- Without it WFMT cannot read Elite's `DisplaySettings.xml`, so it takes the overlay window's size from EDMCModernOverlay's log instead.
- If that is not there either, it asks `xrandr` for the primary monitor's size (through the host from a Flatpak), which is right for an ultrawide or 4K screen.
- Only if `xrandr` is missing too does it assume a 1920 x 1080 screen, which puts cards at the right and bottom edges in the wrong place.
- Overlay Placement says which source it used.
- On a desktop with display scaling (KDE or GNOME at 125% or more), also set **Display scaling** on Overlay Placement to match, because WFMT cannot read it on Linux.

(If your shell is fish, replace the first line with `set PFX "$HOME/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser"`
and use `$PFX` in the rest.)

Check them with:

```bash
flatpak override --user --show io.edcd.EDMarketConnector
```

Other things to know:

- **Flatpak Steam:** your Proton folder is under `~/.var/app/com.valvesoftware.Steam/.local/share/Steam/` instead.
- **Plugin folder:** a Flatpak EDMC keeps its plugins in
  `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/plugins`.
- **Not a Flatpak?** (A native or AppImage install.) Skip this whole step.

**Why permission 4 matters.** EDMCModernOverlay starts its drawing window through the host, and WFMT runs `xdotool` the same way. Without it:

- WFMT's **Check connection** still reports success (the overlay's port is open) but nothing is drawn.
- Auto-Honk says `xdotool` is not installed even though it is.

## Step 4: Bind a keyboard key for the honk (Auto-Honk only)

Auto-Honk can only press **keyboard** keys. If your fire buttons are bound only to a mouse button or a HOTAS
button, it reports "only bound to a joystick/HOTAS button".

1. In Elite, open **Options → Controls → Ship → Cockpit Modes**.
2. Add a keyboard key to the **second** slot of **Secondary Fire**. Keep your mouse or stick binding in the first
   slot.
3. In EDMC, open **Settings → WFMT → Exploration → Auto-Honk** and press **Rescan**. It should say "Will press &lt;your
   key&gt;".
4. Press **Test Honk Now** with the ship able to use its scanner.
5. Set the **hold time** to the seconds the scan needs (8 to 10 is typical). The key is held down for the full
   time.

## Step 5: Check the overlay

1. Start EDMC and Elite (borderless or windowed).
2. Open **Settings → WFMT → Overlays → Overlay Connection** and press **Check connection**.
3. Press a **Test** button, such as **Test Discovery** or **Test Notable** under **Settings → WFMT → Overlays**.

Cards should appear over the game. If they don't, see the Linux items in [Troubleshooting](troubleshooting.md).

- One display missing while the others show usually means its saved position is off the screen. The fix is [there too](troubleshooting.md#one-display-never-shows-though-test-and-the-overlay-window-both-work).
- The general overlay guide is [Setting up the on-screen overlay](../OVERLAY_SETUP.md).

## Step 6: Trade (nothing extra to install)

Trade needs nothing beyond Step 2, but it leans on it more than most features. EDMC's **Journal directory** is what lets WFMT:

- catch a trading session up after you played with EDMC closed,
- rebuild your carrier's cargo history at start-up,
- read the docked station's `Market.json`.

If it is wrong or empty, those quietly find nothing, and the session only counts what EDMC delivered while it was running. For a Flatpak EDMC, the journals permission in Step 3 already covers it.

Other points:

- The Spansh lookups just need the network.
- **Export log (CSV)** in Trade History uses a standard file dialog. If EDMC is a Flatpak and the save fails, pick a folder EDMC is allowed to write to (WFMT shows the error).

## Step 7: Backups, the star index and updates

Nothing extra to install, but a Flatpak EDMC has a few limits:

- **Back up my data** (Settings → WFMT → General → Backup) and **Back up automatically** write to a folder you choose, and the folder must be outside the plugin folder. A Flatpak EDMC can only write to folders it has been given, so pick one it can reach (its own data folder, or one you grant with `flatpak override --user --filesystem=<folder> io.edcd.EDMarketConnector`). A manual backup shows a line under the button (`Saved N files (size) to <path>`, or the reason it failed); the new file is `WFMT-data-<date>.zip`. The data backup has not been tried on Linux yet, so please say if it misbehaves.
- **Restore my data...** needs the same folder permission to read the zip. The restore is applied the next time EDMC starts.
- **The Local star index** (General → Online lookups) downloads one file from Spansh (about 173 MB) and builds an index in the plugin folder, which needs about 300 MB free while it builds. It is optional.
- **Automatic updates** (General → Updates) work the same on Linux. The update waits for you to restart EDMC.
- **Sounds** (the Inventory pickup sound, Flight Alerts and the shortcut confirmation) need `canberra-gtk-play` or `paplay` on your system; the tick is grayed out without one. WFMT looks for the player inside the Flatpak's own environment, not on the host, so with a Flatpak EDMC the sounds can be unavailable even when your system has one.
- **Keyboard shortcuts** are not available on Linux; use the chat commands (`!wf overlays` and so on) after switching them on under General → Shortcuts.

## More help

- A step-by-step checklist for testers: [LINUX_TESTING.md](../LINUX_TESTING.md).
- The platform differences and the reasoning behind them:
  [TECHNICAL.md section 18](../TECHNICAL.md#18-platform-support-windows-and-linux).
- What works where: [Windows and Linux](platforms.md).
