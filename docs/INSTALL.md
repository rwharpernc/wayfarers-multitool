# Installing WFMT

WFMT is a plugin for [EDMC](https://github.com/EDCD/EDMarketConnector) (Elite Dangerous Market Connector). This page covers installing it, updating it, removing it and, for developers, building it from source. Day-to-day use is in the [guide](guide/README.md).

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

- **EDMC**, on Windows or Linux. WFMT runs inside it. Everything except the on-screen displays works with EDMC alone.
- **Elite Dangerous** with EDMC reading its journal folder. On Linux the journal folder usually has to be set by hand: see [Linux](#linux).
- **An overlay** (optional), only for the on-screen displays: see [Overlays](#overlays).

## Install from a release

1. Download **`Wayfarers-Multitool.zip`** from the [latest release](https://github.com/rwharpernc/wayfarers-multitool/releases/latest), under **Assets**.
   - Do not use the green **Code → Download ZIP** button. That is the source code, and EDMC cannot load it as a plugin.
2. In EDMC open **File → Settings → Plugins** and press **Open** beside the plugins folder.
   - Windows: usually `%LOCALAPPDATA%\EDMarketConnector\plugins`.
   - Linux: usually `~/.local/share/EDMarketConnector/plugins`, or for a Flatpak EDMC `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/plugins`.
3. Extract the ZIP into that folder.
   - Windows: right-click the ZIP, **Extract All…**, and choose the plugins folder itself.
   - Linux: `unzip Wayfarers-Multitool.zip -d <your plugins folder>`.
4. Check you now have `plugins/Wayfarers-Multitool/load.py`. If it is `plugins/Wayfarers-Multitool/Wayfarers-Multitool/load.py`, move the inner folder up one level.
5. Restart EDMC. The **Wayfarer's Multitool (WFMT)** panel appears in the main window. Settings are under **File → Settings → WFMT**.

The first line under the mode buttons says which version is running (**Plugin: v1.3.0**).

**After installing:** every on-screen display, every online lookup and every write to another site starts off, so look through **File → Settings → WFMT** ([every tab and what it starts as](guide/getting-started.md#settings)). Consider turning on **Back up automatically** (General → Backup) so your data is copied outside the plugin folder.

## Linux

EDMC needs a few settings before most features find anything:

- Point EDMC's **Journal directory** at the game's journals inside the Steam Proton or Wine folder.
- Install `xdotool` for Auto-Honk and the screenshot timer (X11 or XWayland windows).
- With a Flatpak EDMC, grant it access to the folders it needs.

The steps, in order, are in [WFMT on Linux](guide/linux.md). What differs between the two systems is in [Windows and Linux](guide/platforms.md), and what has been checked on Linux is in [Linux testing](LINUX_TESTING.md).

## Overlays

An overlay draws WFMT's displays over the game.

- **Windows:** WFMT has a built-in overlay. Choose it under **Settings → WFMT → Overlays → Overlay Connection**.
- **Linux (and optionally Windows):** install [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay). The built-in overlay is Windows only.
- Set Elite to **borderless** or **windowed** mode. Every WFMT overlay is off until you turn it on in Settings.

The step-by-step guide is [Overlay setup](OVERLAY_SETUP.md).

## Update

- Extract the new ZIP over the existing `Wayfarers-Multitool` folder and replace files when asked. **Do not delete the old folder first:** your saved data lives inside it.
- Or turn on **Automatically download and install updates** under **Settings → WFMT → General → Updates**. It is off by default and only follows published releases (not drafts or pre-releases).
  - WFMT looks once each time EDMC starts. If a newer release exists it downloads the ZIP, makes a data backup first if **Back up automatically** is on, keeps a zip of the program files it replaces in `backups` (the newest three), and stages the new files.
  - The update takes effect when EDMC next starts; the line under the mode buttons turns orange and says to restart EDMC. Your saved data is not changed by an update.
  - [How the updater works](guide/getting-started.md#updating) has the details, and [the update did not take](guide/troubleshooting.md#the-update-did-not-take) helps when it seems stuck.

Back up your data first if you like: **Settings → WFMT → General → Backup → Back up my data**.

## What is in the plugin folder

Everything WFMT saves about your play is a plain file in the `Wayfarers-Multitool` folder, so you know what an update keeps and what a removal takes with it:

| What | Where | Notes |
|---|---|---|
| The program | `load.py`, the other `.py` files, `fonts`, `icons`, `LICENSE`, `THIRD-PARTY-NOTICES.md` | Replaced by an update |
| Your data | The `.json` files WFMT writes as you play (trade, mining, missions, ledgers, notes, expeditions, surveys, ship builds, `overlay_settings.json` for each commander's overlay choices and so on; not `colonization_costs.json` and `rare_goods.json`, which ship with the program), and `mining_sessions` if you archive runs | Kept by updates; included in **Back up my data**. One section per commander |
| Raven Colonial keys | `rcc_keys.json` | Kept by updates; **left out** of backups on purpose |
| Local star index | `star_index` folder (about 110 MB, optional) | Kept by updates; not in backups; made again from Settings |
| Downloaded Codex catalog | `codex_catalog.json` | Kept by updates; not in backups; downloaded again by WFMT |
| Update files | `updates` (the downloaded ZIP) and `backups` (the program files an update replaced, and `pre-restore-<date>.zip` files from restores) | Safe to delete once you no longer need them |
| A waiting restore | `restore_pending` | Applied at the next start, then removed |

Your **settings** (every tick on every Settings tab, and your overlay choices while a commander is not active) are not files in this folder. EDMC keeps them in its own settings, so they survive removing the plugin folder and are not in a data backup. Only the files that hold each commander's overlay choices (`overlay_settings.json`) are.

## Remove

Close EDMC and delete the `Wayfarers-Multitool` folder from the plugins folder. Your saved data is inside that folder, so use **Back up my data** first if you want to keep it. WFMT's settings stay in EDMC's own settings and are picked up again if you install it later.

## Build from source

Most people should use a release. To build or change WFMT yourself you need Python 3, Node.js 22.2 or newer and Git:

```bash
git clone https://github.com/rwharpernc/wayfarers-multitool.git
cd wayfarers-multitool
npm run package     # writes dist/Wayfarers-Multitool.zip
```

`npm run deploy` builds and copies the plugin into EDMC's plugins folder for your system. Details, tests and the layout of the code are in the [development guide](DEVELOPMENT.md).

## If it does not appear

See [Troubleshooting](guide/troubleshooting.md#the-wfmt-panel-doesnt-appear). To report a problem, use **Settings → WFMT → General → Help → Report an issue**: see [Reporting a problem](guide/reporting-problems.md).
