# Installing WFMT

WFMT is a plugin for [EDMC](https://github.com/EDCD/EDMarketConnector) (Elite Dangerous Market Connector). This page covers installing, updating and removing WFMT and, for developers, building it from source. Usage is described in the [guide](guide/README.md).

**On this page:**

- [What you need](#what-you-need)
- [Install from a release](#install-from-a-release)
- [Linux](#linux)
- [Overlays](#overlays)
- [Update](#update)
- [What is in the plugin folder](#what-is-in-the-plugin-folder)
- [Remove](#remove)
- [Build from source](#build-from-source)
- [If it does not appear](#if-it-does-not-appear)

## What you need

- **EDMC**, on Windows or Linux. WFMT runs inside it. All features except the on-screen displays work with EDMC alone.
- **Elite Dangerous**, with EDMC reading its journal folder. On Linux the journal folder usually must be set manually: see [Linux](#linux).
- **An overlay** (optional), required only for the on-screen displays: see [Overlays](#overlays).

## Install from a release

1. Download **`Wayfarers-Multitool.zip`** from the [latest release](https://github.com/rwharpernc/wayfarers-multitool/releases/latest), under **Assets**. The **Code → Download ZIP** button provides the source code, which EDMC cannot load as a plugin.
2. In EDMC, open **File → Settings → Plugins** and select **Open** beside the plugins folder.
   - Windows: usually `%LOCALAPPDATA%\EDMarketConnector\plugins`.
   - Linux: usually `~/.local/share/EDMarketConnector/plugins`. For a Flatpak EDMC: `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/plugins`.
3. Extract the ZIP into that folder.
   - Windows: right-click the ZIP, select **Extract All…**, and choose the plugins folder.
   - Linux: `unzip Wayfarers-Multitool.zip -d <plugins folder>`.
4. Confirm that `plugins/Wayfarers-Multitool/load.py` exists. If the file is at `plugins/Wayfarers-Multitool/Wayfarers-Multitool/load.py`, move the inner folder up one level.
5. Restart EDMC. The **Wayfarer's Multitool (WFMT)** panel appears in the main window. Settings are under **File → Settings → WFMT**.

The first line under the mode buttons shows the running version (**Plugin: v1.5.2**).

**After installation:** every on-screen display, every online lookup and every write to another site is off by default. Review **File → Settings → WFMT** ([each tab and its starting values](guide/getting-started.md#settings)). **Back up automatically** (General → Backup) copies saved data to a folder outside the plugin folder.

## Linux

EDMC requires the following configuration before most features find data:

- Set EDMC's **Journal directory** to the game's journal folder inside the Steam Proton or Wine folder.
- Install `xdotool` for Auto-Honk and the screenshot timer (X11 or XWayland windows).
- With a Flatpak EDMC, grant access to the required folders.

The steps are in [WFMT on Linux](guide/linux.md). Differences between Windows and Linux are in [Windows and Linux](guide/platforms.md). Tested configurations are in [Linux testing](LINUX_TESTING.md).

## Overlays

An overlay draws WFMT's displays over the game.

- **Windows:** WFMT has a built-in overlay. Select it under **Settings → WFMT → Overlays → Overlay Connection**.
- **Linux (and optionally Windows):** install [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay). The built-in overlay is Windows only.
- Set Elite to **borderless** or **windowed** mode. Every WFMT overlay is off until enabled in Settings.

See [Overlay setup](OVERLAY_SETUP.md).

## Update

- Extract the new ZIP over the existing `Wayfarers-Multitool` folder and confirm file replacement. Do not delete the old folder first: saved data is stored inside it.
- Alternatively, enable **Automatically download and install updates** under **Settings → WFMT → General → Updates**. The option is off by default and follows published releases only (not drafts or pre-releases).
  - WFMT checks once each time EDMC starts. If a newer release exists, WFMT downloads the ZIP, makes a data backup first if **Back up automatically** is on, keeps a zip of the replaced program files in `backups` (the newest three), and stages the new files.
  - The update takes effect at the next EDMC start. The line under the mode buttons turns orange and states that EDMC must be restarted. Saved data is not changed by an update.
  - [How the updater works](guide/getting-started.md#updating). [The update did not take](guide/troubleshooting.md#the-update-did-not-take).

To back up data before an update: **Settings → WFMT → General → Backup → Back up my data**.

## What is in the plugin folder

All data WFMT saves about play is stored as plain files in the `Wayfarers-Multitool` folder.

| What | Where | Notes |
|---|---|---|
| The program | `load.py`, the other `.py` files, `fonts`, `icons`, `LICENSE`, `THIRD-PARTY-NOTICES.md` | Replaced by an update |
| Saved data | The `.json` files WFMT writes during play (trade, mining, missions, ledgers, notes, expeditions, surveys, ship builds, `overlay_settings.json` for each commander's overlay choices, and others; not `colonization_costs.json` and `rare_goods.json`, which ship with the program), and `mining_sessions` if runs are archived | Kept by updates; included in **Back up my data**. One section per commander |
| Raven Colonial keys and Discord webhook links | `rcc_keys.json` and `discord_webhooks.json` | Kept by updates; excluded from backups |
| Local star index | `star_index` folder (about 110 MB, optional) | Kept by updates; not in backups; rebuilt from Settings |
| Downloaded Codex catalog | `codex_catalog.json` | Kept by updates; not in backups; downloaded again by WFMT |
| Update files | `updates` (the downloaded ZIP) and `backups` (program files replaced by an update, and `pre-restore-<date>.zip` files from restores) | Can be deleted when no longer needed |
| A pending restore | `restore_pending` | Applied at the next start, then removed |

Settings (every option on every Settings tab) are not stored in this folder. EDMC keeps them in its own settings, so they survive removal of the plugin folder and are not part of a data backup. The per-commander overlay choices are stored in `overlay_settings.json`.

## Remove

Close EDMC and delete the `Wayfarers-Multitool` folder from the plugins folder. Saved data is stored in that folder: run **Back up my data** first to keep it. WFMT's settings remain in EDMC's settings and apply again after a later installation.

## Build from source

Building requires Python 3, a current Node.js and Git.

```bash
git clone https://github.com/rwharpernc/wayfarers-multitool.git
cd wayfarers-multitool
npm run package     # writes dist/Wayfarers-Multitool.zip
```

`npm run deploy` builds the plugin and copies it into EDMC's plugins folder for the current system. Tests and the code layout are in the [development guide](DEVELOPMENT.md).

## If it does not appear

See [Troubleshooting](guide/troubleshooting.md#the-wfmt-panel-doesnt-appear). To report a problem, use **Settings → WFMT → General → Help → Report an issue**: see [Reporting a problem](guide/reporting-problems.md).
