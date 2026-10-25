# Installing WFMT

WFMT is a plugin for [EDMC](https://github.com/EDCD/EDMarketConnector) (Elite Dangerous Market Connector). This page covers installing it, updating it, removing it and, for developers, building it from source. Day-to-day use is in the [guide](guide/README.md).

**On this page:**

- [What you need](#what-you-need)
- [Install from a release](#install-from-a-release)
- [Linux](#linux)
- [Overlays](#overlays)
- [Update](#update)
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

The first line under the mode buttons says which version is running (**Plugin: v1.0.0**).

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
- Or turn on **Automatically download and install updates** under **Settings → WFMT → General → Updates**. It is off by default and only follows published releases. The update takes effect when EDMC next starts.

Back up your data first if you like: **Settings → WFMT → General → Back up my data**.

## Remove

Close EDMC and delete the `Wayfarers-Multitool` folder from the plugins folder. Your saved data is inside that folder, so use **Back up my data** first if you want to keep it.

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
