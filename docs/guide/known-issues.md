# Known issues

Known faults and rough edges of the current release, their appearance and their remedies. The limits of what the game's journal reports are listed in the last section of each mode guide. Issues not listed here are reported as described in [Reporting a problem](reporting-problems.md).

## Overlay text looks doubled or ghosted

This applies when a separate overlay program draws WFMT's cards. WFMT's built-in overlay does not leave a second window behind, but an overlay window left over from an earlier session can still run beside it.

**Appearance:** every overlay card has a faint second copy of its text beside or behind the first, often in a different font or in capitals, and some rows appear brighter or dimmer than others. The copy does not clear when the card refreshes.

**Cause:** two copies of the overlay window are running, and each draws everything it receives.

- An old window remains running after EDMC is closed or restarted without stopping it (a crash or a forced close). It reconnects to the next EDMC session while a new window starts.
- When both windows use the same font, the copies coincide. When the font or the settings differ, the text appears doubled.
- WFMT does not start that window and cannot end the extra one. **Check connection** reports the number of running windows.

**Remedy:**

1. Open **Settings → WFMT → Overlays → Overlay Connection** and select **Check connection**. When more than one overlay window is running, the result states this and lists the process numbers. **Copy diagnostics** (Help tab) reports the count.
2. Open Task Manager (Windows) or run `ps` (Linux) and look for `overlay_client`. Each window is a `python.exe -m overlay_client.overlay_client`. A launcher and the window it starts share one start time and count as one.
3. End the older processes, or end all of them and restart EDMC. The ghosting ends immediately.

## Overlay text is all in capital letters

**Appearance:** species, rows and headings are shown in capitals, although WFMT writes `Tussock pennatis`.

**Cause:** the overlay draws every plugin's text in one font. Its default (Elite's cockpit font, `Eurocaps.ttf`) has capital letters only.

**Remedy:**

1. Open **Settings → WFMT → Overlays → Appearance → Overlay font**.
2. Select a font with lower case letters, or select **Add font file...** to use a downloaded font.
3. Select OK and restart EDMC.

Notes:

- The font is the overlay's, so it changes every plugin's text. An update of EDMCModernOverlay can restore the old list.
- WFMT cannot select a font for its own cards only, and the overlay cannot draw italics, so species names are not italicized.
- WFMT's built-in overlay (Windows) has its own font (Source Sans 3, lower case, and any `.ttf` or `.otf` added) and is not affected. See [Fonts](../OVERLAY_SETUP.md#fonts).

## Right-hand cards stop a little short of the screen edge (Linux, EDMCModernOverlay)

**Appearance:**

- On Linux, a card placed at the right (Top right, Middle right, Bottom right) with an offset of 0 stops short of the right edge of the screen.
- A negative offset in **Overlay Placement** does not close the gap.
- Cards on the left and top edges are not affected.

**Cause:** WFMT places a card from the screen size and the display scaling.

- WFMT reads the size from Elite's `DisplaySettings.xml`. A Flatpak EDMC cannot read that folder unless it is granted (permission 5 in the [Flatpak steps](linux.md#step-3-if-edmc-is-a-flatpak-grant-it-five-permissions)).
- Without the file, WFMT uses the window size in EDMCModernOverlay's log. A wrong size places right-hand cards incorrectly.
- Display scaling cannot be read on Linux and is assumed to be 100%.

**Remedy:**

1. Grant the Graphics folder permission (step 5 of the [Flatpak steps](linux.md#step-3-if-edmc-is-a-flatpak-grant-it-five-permissions)) and restart EDMC.
2. On **Overlay Placement**, set **Display scaling** to the desktop's scaling (125% for a KDE screen set to 125%), select OK and run **Show placement preview**. The scaling must be set manually.
3. Read the info line on that tab. It states the source of the screen size.

If cards still stop short, report the screen size, the scaling, the desktop and whether the session is X11 or Wayland ([Reporting a problem](reporting-problems.md)).

## The built-in overlay has had less testing

WFMT's own overlay (Windows) is newer and has had less in-game testing.

- It works with every card and with Overlay Placement. A card's box can fit its text differently than in EDMCModernOverlay.
- The radar's circles and lines and cards at the screen edges have had the least testing.
- It draws WFMT's displays only. Other plugins' overlays require EDMCModernOverlay (both can run). See [Setting up the overlay](../OVERLAY_SETUP.md).
- It is off until selected under **Settings → WFMT → Overlays → Overlay Connection**. Switching back is a single setting.

## A tracked plant's marker can be off by a couple of hundred meters

A marker is the position of the commander when the Composition Scanner named the plant. From a ship or SRV the marker can be far from the plant. The radar draws the marker's ring as wide as the possible error, and the distance carries a `~`. See [Exobiology](exobiology.md#finding-your-way-back-to-a-plant) for the judging and removal of markers.

## Overlays do not show over the game

The overlay window can sit over Elite only when the game runs **borderless or windowed**. A fullscreen game owns the screen. See [Setting up the overlay](../OVERLAY_SETUP.md) and [Troubleshooting](troubleshooting.md#overlay).

## Play with EDMC closed: what is and is not recovered

**Appearance:** after play with EDMC closed, most data is correct at the next EDMC start. The following is not recovered:

- a plant marker set while EDMC was closed,
- the distance to the last sample on that body,
- Organic Scanning progress for a body scanned and sampled more than 14 days apart.

**Cause:** WFMT reads the journals back when EDMC starts, and each feature recovers what the journal records.

- The journal has no positions for samples.
- The journal does not carry a plant's identification marker in a form that WFMT can rebuild safely.
- The Organic Scanning catch-up looks back 14 days.

**Remedy:** restart EDMC. The table in [If EDMC wasn't running](getting-started.md#if-edmc-wasnt-running) lists the action that rebuilds each feature.

## Version 1.5.0 moved pages and settings into windows

Version 1.5.0 replaces the page arrows of Trade, Mining and Missions with a button for each page that opens a window, and moves the settings that belong to a window into that window ([Getting started](getting-started.md#settings)). The automated tests cover the change. The in-game pass on Windows and Linux is in progress.

- When a setting is missing from **File → Settings → WFMT**, the tab states where it moved. Saved values are unchanged.
- A window's settings are saved on change, without **OK**.
- A window that opens at an incorrect size or place, a setting that does not persist, or a control that does nothing should be reported ([Reporting a problem](reporting-problems.md)).

## Larger text can need a larger window

- The text size of WFMT's pop-out windows (-2 to +6 points) does not change a window's saved size. At the larger sizes a window may need to be resized before every column and line fits. The stat tiles at the top of a dashboard and the status chips keep their size.
- The color themes (Navy, Cyan, Amber, Green) recolor open windows in place. If a color is wrong in a window that was open when the theme changed, close and reopen the window and report which window it was ([Reporting a problem](reporting-problems.md)).
- The themes and the text size have been checked by automated tests and visually on Windows. The Linux pass is pending ([Linux testing](../LINUX_TESTING.md)).
- The Colonization Archive and the footer message colors have been checked visually on Windows. The Linux pass is pending. The offer to create a Raven project for a new site has been checked by automated tests only.

## Verified on Windows first

Verified on Windows first:

- the Exobiology cards, System targets, Body info and the Expedition Log,
- the layout editor on Overlay Placement, panel opacity, the overlay font choice, hiding the overlays and the duplicate window warning,
- the built-in overlay, nearest place to land, likely colors, marker rings and per-commander overlay settings.

**Linux:** a pass of an earlier build on 2026-10-18 covered these items on one configuration (KDE Plasma, Wayland, a Flatpak EDMC). The built-in overlay is Windows only.

**Not tried:** the data backup on Linux. Other configurations (other distributions and desktops, X11, a non-Flatpak EDMC) have not been tested. The checks are listed in [Linux testing](../LINUX_TESTING.md).

- **Quick pass on Linux only:** the Carrier Route window, the mining alerts, the Space Mining window's rock, core and mission lines, Mining History, and the Rare Goods Finder's columns and filters (2026-10-20, an earlier build). The full checks are in [Linux testing](../LINUX_TESTING.md).
- **Keyboard shortcuts are available on Windows only.** A Linux desktop provides no portable way to receive keys while another window has the focus. On Linux, use the chat commands (`!wf center`, `!wf border` and the others; see [Shortcuts](shortcuts.md)).

## Estimates and limits

These are not faults. Each is described where it belongs:

- **Species percentages are an even share** of the candidates. The data lists which species a body allows and not how likely each is, and a color variant is known only after sampling. See [Exobiology](exobiology.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it).
- **System targets' visit line and Known section have limits.**
  - The visit line comes from the commander's journals and counts only those that still exist. A relog in the same system is not a second visit.
  - The Known section comes from Spansh, which knows only what other commanders uploaded. A system nobody scanned shows nothing. Its figures are Spansh's estimates.
- **Scan, mapping and unsold values are estimates** calculated from a published formula. The game's figure at the time of sale is authoritative. System targets ranks by the mapped value by default (the scan value when selected in Settings). Both appear on Body info and in the Expedition Log. See [Exploration](exploration.md).
- **Plants, samples and the SRV have positions only while EDMC is running**, because the journal does not record them.
- **The Powerplay overlay card has limits.** See [the overlay card](powerplay.md#the-overlay-card).
  - The merit category (Acquisition, Reinforcement or Undermining) is inferred from the system's state and holder. A sale of goods that earns merits, such as Soontill Relics, does not appear in the journal as such and is filed as Acquisition. The merit totals are correct.
  - Control Points are estimated from the merits-per-CP ratios on the Settings tab of the Powerplay Sessions window.
  - The look-ahead is off until enabled and uses only what Spansh knows. A system without Spansh Powerplay data reads **No Powerplay Detected in system**, even when the game shows a state. A destination's control progress is shown only for the first ten minutes after it was fetched.
  - After EDMC is started in the middle of a game, the card stays blank until the first jump, because WFMT has not yet seen the arrival.
  - The card is wider than its slot on Overlay Placement indicates, so at its default position it can overlap the Discovery banner. Move it in that case.
- **The Rare Goods Finder's Legality and Arrival columns come from community data** that has not been checked in the game.
  - A rare is marked *Legal* when the table lists no restriction. This does not guarantee legality. Check the station's Prohibited list before carrying a restricted rare.
  - The Arrival distance (a station's distance from its star) is approximate.
  - See [Powerplay](powerplay.md#rare-goods-finder).
- **Some engineer invitation requirements cannot be checked.** The journal totals ranks and lifetime figures, so those are noted against the commander's standing. For the other engineers (a faction's standing, a kind of mission, a data sale and similar) the details show **Verification needed**, and the step is marked done only once the engineer is invited or unlocked. The steps use the wording of a community table. When the in-game Engineers panel differs, **Report engineer data** on the Engineers tab submits the difference ([Reporting a problem](reporting-problems.md#telling-us-what-the-game-shows-game-data)). See [Operations](operations.md).
- **Carrier Route plans to one destination at a time**, and the tritium figures are Spansh's. WFMT detects the carrier's arrival from the journal (when the commander is aboard or logs in). After a jump that was not observed, use **Mark next as reached**. See [Exploration](exploration.md#carrier-route).
- **The Surface Mining Book's "From your journals" list identifies bodies, not locations.**
  - The journal records the number of mining locations of a body and the tons refined on it, not the position of any deposit. Deposits are the hotspots the commander saves.
  - Tons refined on a body are counted only while a Rhino is deployed and a body is known.
  - See [Mining](mining.md#the-surface-mining-book).
- **Mining: the target commodity must be spelled as the game spells it** (for example Painite). The limpet count is exact only once EDMC has passed the cargo to WFMT. Until then the window shows an estimate marked with `~`. See [Mining](mining.md#what-each-page-shows).
- **Sounds with a Flatpak EDMC on Linux.** The Inventory and Flight Alerts sound options look for `canberra-gtk-play` or `paplay` inside the Flatpak, not on the system, and can be grayed out. See [Windows and Linux](platforms.md).
- **The Local star index covers neutron stars only**, and only a system's main star. **White Dwarf** always asks Spansh. See [Settings](getting-started.md#settings).
- **Hide overlays is not saved and is never automatic.** The overlays are shown whenever EDMC starts, and WFMT does not hide them in the galaxy map. See [Overlay setup](../OVERLAY_SETUP.md#hiding-the-overlays-for-a-while).
- **Linux is verified after Windows.** See [Windows and Linux](platforms.md).

Where the cause is data the journal does not record, each mode guide ends with a section titled "What the game does and doesn't tell us, and how to work around it".
