# Known issues

What is known to go wrong in the current release, what it looks like, and what to do about it. This page is for things that are bugs or rough edges; the
limits of what the game's journal tells WFMT are in the last section of each mode guide. If you hit something that is not here, see
[Reporting a problem](reporting-problems.md).

## Overlay text looks doubled or ghosted

(This is EDMCModernOverlay's behavior. WFMT's own built-in overlay cannot leave a second window behind, but an EDMCModernOverlay window can still be running beside it.)

**What you see:** every overlay card has a faint second copy of its text beside or behind the real one, often in a different font or in capitals, and some rows look
brighter or dimmer than others. It does not clear when the card refreshes.

**Why:** two copies of EDMCModernOverlay's overlay window are running, and each draws everything it is sent.

- **How it happens:** an old window is left running after EDMC is closed or restarted without stopping it (a crash or a forced close). It reconnects to the next EDMC session while a new window starts.
- **Why it is easy to miss:** while both use the same font the copies sit exactly on top of each other. If the font or the settings differ, the text looks doubled.
- **Whose it is:** this is EDMCModernOverlay's behavior, not something WFMT starts, and WFMT cannot stop the extra window for you.

**What to do:**
1. Open **Settings → WFMT → Overlays → Overlay Connection** and press **Check connection**. When more than one overlay window is running it says so and names their process numbers. (**Copy diagnostics** in the Help tab gives the count too.)
2. Open Task Manager (Windows) or run `ps` (Linux) and look for `overlay_client`. Each window is a `python.exe -m overlay_client.overlay_client`; a launcher and the window it starts share one start time and count as one.
3. End the older ones, or end them all and restart EDMC. The ghosting goes at once.

## Overlay text is all in capital letters

**What you see:** species, rows and headings all show in capitals, even though WFMT writes `Tussock pennatis`.

**Why:** the overlay draws every plugin's text in one font, and its default (Elite's cockpit font, `Eurocaps.ttf`) has capital letters only.

**What to do:**

1. Open **Settings → WFMT → Overlays → Appearance → Overlay font**.
2. Pick a font with lower case letters (or **Add font file...** to use one you downloaded, for example from Google Fonts).
3. Press OK and restart EDMC.

Things to know:

- The font is the overlay's, so it changes every plugin's text, and an update of EDMCModernOverlay can put the old list back.
- WFMT cannot choose a font for its own cards only, and the overlay cannot draw italics, so species are not italicized.
- WFMT's built-in overlay (Windows) has a font of its own (Source Sans 3, lower case, and any `.ttf` or `.otf` you add) and does not have this problem. See [Fonts](../OVERLAY_SETUP.md#fonts).

## Right-hand cards stop a little short of the screen edge (Linux, EDMCModernOverlay)

**What you see:**

- On Linux, a card placed at the right (Top right, Middle right, Bottom right) with an offset of 0 stops a small gap short of the screen's right edge. The gap is about 1.4% of the screen width (around 36 pixels on a 2560-wide screen).
- A negative offset in **Overlay Placement** does not close it.
- Cards on the left and top edges are not affected.

**Why:** WFMT places a card from the size of your screen and its display scaling.

- It reads the size from Elite's `DisplaySettings.xml`. A Flatpak EDMC cannot read that folder unless it is granted (permission 5 in the [Flatpak steps](linux.md#step-3-if-edmc-is-a-flatpak-grant-it-five-permissions)).
- Without it WFMT falls back to the window size in EDMCModernOverlay's log, and a wrong size puts right-hand cards in the wrong place.
- Display scaling cannot be read on Linux at all, so it is assumed to be 100%.

**What to do:**

1. Grant the Graphics folder permission (step 5 of the [Flatpak steps](linux.md#step-3-if-edmc-is-a-flatpak-grant-it-five-permissions)) and restart EDMC.
2. On **Overlay Placement**, set **Display scaling** to your desktop's scaling (125% on a KDE screen set to 125%), press OK and run **Show placement preview**. The scaling still has to be set by hand.
3. Check the info line on that tab. It says where the screen size came from.

If cards still stop short, report it with your screen size, scaling, desktop and whether it is X11 or Wayland ([Reporting a problem](reporting-problems.md)).

## The built-in overlay is less tested

WFMT's own overlay (Windows) is less tested than EDMCModernOverlay.

- It works with every card and with Overlay Placement, but a card's box may fit its text a little differently than you are used to.
- The radar's circles and lines and cards at the screen edges are the least tested.
- It draws WFMT's displays only, so other plugins' overlays still need EDMCModernOverlay (you can run both). See [Setting up the overlay](../OVERLAY_SETUP.md).
- It is off until you choose it under **Settings → WFMT → Overlays → Overlay Connection**, and switching back is one setting.

## A tracked plant's marker can be off by a couple of hundred meters

A marker is where *you* were when the Composition Scanner named the plant, so from a ship or SRV it can be far from the plant. The radar draws the marker's ring as wide as it may be off, and the distance carries a `~`. See
[Exobiology](exobiology.md#finding-your-way-back-to-a-plant) for how it is judged and removed.

## Overlays do not show over the game

The overlay window can only sit over Elite when the game runs **borderless or windowed**; a fullscreen game owns the screen and nothing can draw over it. See
[Setting up the overlay](../OVERLAY_SETUP.md) for the steps and [Troubleshooting](troubleshooting.md#overlay) for nothing showing up.

## Play with EDMC closed: what is and is not recovered

**What you see:** after playing with EDMC closed, most things are right when EDMC starts, but a few are not:

- a plant marker you set while it was closed,
- the distance to the last sample on that body,
- Organic Scanning progress for a body scanned and sampled more than 14 days apart.

**Why:** WFMT reads the journals back when EDMC starts, and each feature recovers what the journal records.

- The journal has no positions for samples.
- It does not carry a plant's identification marker in a form WFMT rebuilds safely.
- The Organic Scanning catch-up looks back 14 days.

**What to do:** restart EDMC (safe at any time), and see the table in [If EDMC wasn't running](getting-started.md#if-edmc-wasnt-running) for the action that rebuilds each feature.

## Larger text can need a larger window

- The text size of WFMT's pop-out windows (-2 to +6 points) does not change a window's saved size. At the larger sizes a window may need dragging bigger before every column and line fits; the stat tiles at the top of a dashboard and the status chips keep their size on purpose.
- The color themes (Navy, Cyan, Amber, Green) recolor open windows where they stand. If a color looks wrong in a window that was open when you switched, close it and open it again, and tell us which window it was ([Reporting a problem](reporting-problems.md)).
- The themes and the text size have been checked by the automated tests and by eye on Windows; the pass on Linux is still to do ([Linux testing](../LINUX_TESTING.md)).

## Proven on Windows first

These were proven on Windows first:

- the Exobiology cards, System targets, Body info and the Expedition Log,
- the layout editor on Overlay Placement, panel opacity, the overlay font choice, hiding the overlays and the duplicate window warning,
- the built-in overlay, nearest place to land, likely colors, marker rings and per-commander overlay settings.

**Linux so far:** a Linux pass of an earlier build of this code on 2026-10-18 covered them on one setup (KDE Plasma, Wayland, a Flatpak EDMC) and went well. The built-in overlay is Windows only.

**Not yet tried:** the data backup has not been tried on Linux. Other setups (other distributions and desktops, X11, a non-Flatpak EDMC) have not been tested. Please report anything odd. The checks are listed in [Linux testing](../LINUX_TESTING.md).

- **Quick pass on Linux only:** the Carrier Route window, the mining alerts and the Space Mining page's rock, core and mission lines, Mining History, and the Rare Goods Finder's columns and filters. They had a quick pass on Linux on 2026-10-20 (an earlier build of this code); the full checks are in [Linux testing](../LINUX_TESTING.md).
- **Keyboard shortcuts are available on Windows only.** A Linux desktop gives a program no portable way to hear keys while another window has the focus, so on Linux use the chat commands (`!wf center`, `!wf border` and so on; see [Shortcuts](shortcuts.md)). They are the same words on both systems.

## Estimates and limits worth knowing

These are not bugs, but they surprise people. Each is explained where it belongs:

- **Species percentages are an even share** of the candidates, because the data lists which species a body allows and not how likely each is, and a color variant is only known once you sample.
  See [Exobiology](exobiology.md#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it).
- **System targets' visit line and Known section have limits.**
  - The visit line comes from your own journals and counts only those that still exist (and a relog in the same system is not a second visit). The first read takes about 40 seconds for thousands of journals.
  - The Known section comes from Spansh, which knows only what other commanders uploaded, so a system nobody scanned shows nothing. Its figures are Spansh's estimates.
- **Scan, mapping and unsold values are estimates**, worked out from a published formula; the game's own figure when you sell is the truth.
  System targets ranks by the mapped value by default (the scan value if you choose it in Settings), and both
  appear on Body info and in the Expedition Log. See [Exploration](exploration.md).
- **Plants, samples and the SRV have positions only while EDMC is running**, because the journal does not record them.
- **The Rare Goods Finder's Legality and Arrival columns come from community data** that has not been checked in the game.
  - A rare is marked *Legal* when the table lists no restriction, which is not a promise. Check the station's Prohibited list before carrying a restricted rare.
  - Treat the Arrival distance (a station's distance from its star) as approximate.
  - See [Powerplay](powerplay.md#rare-goods-finder).
- **Carrier Route plans to one destination at a time**, and the tritium figures are Spansh's. WFMT sees the carrier arrive from the journal (when you are aboard or log in), so after a jump you did not see, use **Mark next as reached**. See [Exploration](exploration.md#carrier-route).
- **The Surface Mining Book's "From your journals" list says which bodies, not where.**
  - The journal records how many mining locations a body has and the tons you refined on it, but not where any deposit is. Deposits are still the hotspots you save.
  - Tons refined on a body are counted only while a Rhino is deployed and a body is known.
  - See [Mining](mining.md#the-surface-mining-book).
- **Mining: the target commodity must be spelled as the game spells it** (for example Painite). The limpet count is exact only once EDMC has told WFMT your cargo; until then the page shows an estimate, marked with a `~`. See [Mining](mining.md#what-each-page-shows).
- **Sounds with a Flatpak EDMC on Linux.** The sound ticks (Inventory, Flight Alerts, Shortcuts) look for `canberra-gtk-play` or `paplay` inside the Flatpak, not on your system, so they can be grayed out there. See [Windows and Linux](platforms.md).
- **The Local star index covers neutron stars only,** and only a system's main star. **W.D.** always asks Spansh. See [Settings](getting-started.md#settings).
- **Hide overlays is not remembered and never automatic.** The overlays are shown again whenever EDMC starts, and WFMT does not hide them in the galaxy map. See [Overlay setup](../OVERLAY_SETUP.md#hiding-the-overlays-for-a-while).
- **Linux is checked a little behind Windows.** See [Windows and Linux](platforms.md).

Where the cause is something the journal does not record, each mode guide ends with a section called "What the game does and doesn't tell us, and how to work around it".
