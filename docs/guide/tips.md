# Tips, quirks and workarounds

Things that surprise people, and what to do about them. Back to the [README](../../README.md). Every mode guide has a longer list at its end.

## Installing and updating

- **Restart EDMC** after installing or updating. The WFMT panel only appears after a restart.
- Extract the ZIP **over** the old `Wayfarers-Multitool` folder, don't delete it first: your saved data lives there.
- Use the ZIP from the **Releases** page (Assets), not the green **Code → Download ZIP** button.
- The WFMT panel is a little wider because there are eight mode buttons. EDMC sizes its window to the widest plugin, so you may see the main window grow slightly.

## EDMC, the journal and catching up

- **Run EDMC** while you play.
  - If you forget, WFMT catches up from your recent journals when EDMC starts (up to about 14 to 30 days for most features), counting nothing twice.
  - It cannot catch up on things the game never writes down.
- WFMT, like every third-party tool, only knows what the game writes to its journal, plus what it can add from Frontier's servers and community services.
  - Where it can't be sure, it says so.
  - Each guide lists these gaps and the workaround in "What the game does and doesn't tell us".
- Everything is kept **per commander**. Switching commanders in EDMC switches the data.
- **Linux:**
  - EDMC's **Journal directory** must point at Elite's journal folder inside the Proton/Wine folder, or most features will find nothing.
  - Auto-Honk and the screenshot timer also need `xdotool`.
  - A Flatpak EDMC needs permissions granted.
  - See [WFMT on Linux](linux.md).

## On-screen overlays

**Which overlay to use**

- **Windows:** use WFMT's **built-in overlay** (choose it under **Settings → WFMT → Overlays → Overlay Connection**) or [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay). EDMCModernOverlay is needed for other plugins' overlays too; you can run both.
- **Linux:** you must use [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay); the built-in overlay is Windows only. Right-hand cards stop a little short of the screen edge (see [Known issues](known-issues.md#right-hand-cards-stop-a-little-short-of-the-screen-edge-linux-edmcmodernoverlay)).
- Press a **Test** button to check. Everything is **off until you turn it on**.
- Run Elite in borderless or windowed mode; some overlays can't draw over exclusive fullscreen (see the [overlay setup](../OVERLAY_SETUP.md)).

**Where the settings are**

- All overlay settings are in one place: **Settings → WFMT → Overlays** (Connection, Placement, Appearance, Hide overlays, and a tab per feature).

**Fonts**

- The built-in overlay has its own font, Source Sans 3 to start with, and you can add any `.ttf` or `.otf` under **Appearance → Overlay font** ([Fonts](../OVERLAY_SETUP.md#fonts)).
- EDMCModernOverlay's default font has capital letters only.

**Placement**

- **Placement** puts each display at one of nine spots plus pixel offsets, read from your real screen.
- It has a drag-and-drop **layout editor**: a to-scale picture of your screen with a grid, where you drag each display's box and it snaps flush to an edge (offset 0) or to the grid.
- If it looks wrong, press **Show placement preview**, then **Detect screen again**, or **Reset all to defaults**.
- **Display scaling** (Windows' percentage for your monitor) and **Overlay mode** (Fit or Fill) say how your screen is mapped, and **Text size** on Appearance only makes the text larger ([the three size settings](../OVERLAY_SETUP.md#moving-things-around)).
- With EDMCModernOverlay the overlay can't draw flush against the right edge by itself. WFMT works around that with an offset (a switch on the Placement tab turns it off), and on Linux a small gap remains. The built-in overlay has no such limit.

**Appearance**

- **Appearance** sets the color scheme for every overlay.
- The text size (Default or Larger) is yours to choose, and the spacing is fixed so columns stay aligned.
- The Interdiction warning always stays red.

## Colonization (work in progress)

- Dock at a construction depot (or open its market) **once** to register a site. Nothing is typed in.
- The COL page and window show **your** deliveries and cargo. The depot's totals include everyone's deliveries.
- Your **history is rebuilt once from all your journal files** and counts from the first delivery in them (the page says the date). Deleted journals can't be counted.
- **Fleet carrier cargo:** the journal only records cargo you *transfer* to the carrier.
  - For the real hold, sign EDMC in to Frontier and open **Carrier Management** once; WFMT then reads the carrier's actual cargo. It can lag behind the game.
  - If a transfer never registered, **Rescan Carrier** (in the Colonization Sites window) rebuilds the tally from your last 30 days of journals.
- Commanders **without** a carrier see simpler wording and one Trips column; the carrier lines appear only if you have one.
- **Where to buy** needs the internet (Spansh) and caches a search for two minutes. Click a result row to copy its system, ready to paste into the galaxy map search.
- **Raven Colonial** (ravencolonial.com) is optional.
  - Planned Builds, My Projects (to look at), Raven Progress and the page links only read or open your browser.
  - Sending anything to Raven is **off until you tick the master switch** in Settings and save your Raven key (the settings page links to where you get it). That covers progress sharing, **Create Project on Raven**, **Report Complete to Raven**, **Mark Plan Entry Demolished**, and **Set as My Primary** and **Save Counted List** in My Projects.
  - If Raven has no project for the site you are building, **Create Project on Raven** (in the Colonization Sites window) makes one.
  - **Test key** checks the key.
- **Shopping-list overlay:**
  - Switch it on and off with the **OVERLAY** button (it stays as you leave it).
  - Tick the automatic option in Settings if you want it to appear by itself at a market, in Carrier Management or at a construction site.

## Windows

- If screenshots don't save, Windows **Controlled Folder Access** or your antivirus may be blocking EDMC. Allow it, or choose another folder.
