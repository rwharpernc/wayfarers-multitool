# Tips, quirks and workarounds

Things that surprise people, and what to do about them. Back to the [README](../../README.md). Every mode guide has a longer list at its end.

## Installing and updating

- **Restart EDMC** after installing or updating. The WFMT panel only appears after a restart.
- Extract the ZIP **over** the old `Wayfarers-Multitool` folder, don't delete it first: your saved data lives there.
- Use the ZIP from the **Releases** page (Assets), not the green **Code → Download ZIP** button.
- The WFMT panel is a little wider because there are eight mode buttons. EDMC sizes its window to the widest plugin, so you may see the main window grow slightly. Every long name wraps instead of widening it, and the panel never changes the window's width as you switch modes.
- **Automatic updates are off until you tick them** (Settings → WFMT → General → Updates). A downloaded update waits for a restart: the version line under the mode buttons turns orange and says *Restart EDMC*.
- Press **OK** in EDMC's Settings window to keep a change.

## Your data and backups

- WFMT keeps what it records about your play in files inside its plugin folder, one section per commander. Updates never touch them, but deleting or reinstalling the folder loses them.
- **Back it up** (Settings → WFMT → General → Backup). Ticking *Back up automatically* with a folder outside the plugin folder (Documents or a cloud-synced folder) makes a zip every 7 days when EDMC starts, and one just before an update installs. A manual **Back up my data** shows a line under the button, `Saved N files (size) to <path>`, or the reason it failed.
- **Restore** is applied when EDMC next starts, so restart EDMC after choosing a zip. The files it replaced are kept in `backups/pre-restore-<date>.zip` inside the plugin folder.
- The Raven Colonial key, the Discord webhook links, the downloaded Codex catalog and the Local star index are not in a backup. Type the key and the webhook links again (or paste them) on a new install.
- Click the **Credits this session** line under the mode buttons to open the **Credits Ledger**: your income by activity and by day, and the game's lifetime totals.

## EDMC, the journal and catching up

- **Run EDMC** while you play.
  - If you forget, WFMT catches up from your recent journals when EDMC starts (up to about 14 to 30 days for most features), counting nothing twice.
  - It cannot catch up on things the game never writes down.
- WFMT, like every third-party tool, only knows what the game writes to its journal, plus what it can add from Frontier's servers and community services.
  - Where it can't be sure, it says so.
  - Each guide lists these gaps and the workaround in "What the game does and doesn't tell us".
- Everything is kept **per commander**. Switching commanders in EDMC switches the data. Overlay choices (which cards are on, where they sit, how they look) are per commander too.
- A gray line under the mode buttons, *Reading your journals to catch up (...)*, means a first-time or long catch-up is running. It happens once, can take a minute, and goes by itself.
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
- **Overlays shown (click to hide)**, under the mode buttons, hides every WFMT overlay for a clean screenshot and brings them back where they were. It is not remembered: they are shown again whenever EDMC starts.
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

**Windows (not the overlay)**

- WFMT's pop-out windows have their own text size and color theme, separate from the overlay's. Use **A-**, **A+** and the theme name at the right end of a window's bottom line, or **Settings → WFMT → General → Window**.
- If a window's text is cut off after you make it larger, drag the window bigger; the size is yours to choose and the windows keep their own minimum sizes.

**Appearance**

- **Appearance** sets the color scheme for every overlay (the overlay's own schemes, apart from the themes of the windows).
- The text size (Default or Larger) is yours to choose, and the spacing is fixed so columns stay aligned.
- The Interdiction warning always stays red.
- **Panel opacity** (Appearance) makes every card's background fainter without touching the text; 75% or more is easiest to read over a bright scene.
- The **Color-blind safe** scheme uses colors that stay apart for the common kinds of color blindness, so good, short and warning never rest on red against green.

## Colonization (work in progress)

- Dock at a construction depot (or open its market) **once** to register a site. Nothing is typed in.
- The Colony page and window show **your** deliveries and cargo. The depot's totals include everyone's deliveries.
- Your **history is rebuilt once from all your journal files** and counts from the first delivery in them (the page says the date). Deleted journals can't be counted.
- **Fleet carrier cargo:** the journal only records cargo you *transfer* to the carrier.
  - For the real hold, sign EDMC in to Frontier and open **Carrier Management** once; WFMT then reads the carrier's actual cargo. It can lag behind the game.
  - If a transfer never registered, **Rescan Journals** (in the Colonization Sites window) rebuilds the tally from your last 30 days of journals.
- Commanders **without** a carrier see simpler wording and one Trips column; the carrier lines appear only if you have one.
- **Where to buy** needs the internet (Spansh) and caches a search for two minutes. Click a result row to copy its system, ready to paste into the galaxy map search. After **Find all** with several commodities, the **Closest way to buy everything** block above the lists gives the stops to fly, what to buy at each and the stock there; **Stop** keeps what was found so far. **Exclude surface ports** (off by default) can be ticked if you cannot land on a planet; the route then says which commodities are only sold on a surface. The route also follows what you buy: once an item is in your hold or on your carrier it comes off the route.
- The **In Cargo** figures come from the game's `Cargo.json`, read again shortly after any event that can change the hold, so they follow what you buy.
- **Raven Colonial** (ravencolonial.com) is optional.
  - Planned Builds, My Projects (to look at), Raven Progress and the page links only read or open your browser.
  - Sending anything to Raven is **off until you tick the master switch** in Settings and save your Raven key (the settings page links to where you get it). That covers progress sharing, **Create Project on Raven**, **Report Complete to Raven**, **Mark Plan Entry Demolished**, and **Set as My Primary** and **Save Counted List** in My Projects.
  - If Raven has no project for the site you are building, **Create Project on Raven** (in the Colonization Sites window) makes one.
  - **Test key** checks the key.
- **Shopping-list overlay:**
  - Switch it on and off with the **Overlay** button (it stays as you leave it).
  - Tick the automatic option in Settings if you want it to appear by itself at a market, in Carrier Management or at a construction site.
  - It leaves out commodities your hold and fleet carrier already cover (*List: To buy*, the default; choose *To haul* once everything is on the carrier) and its Acquire column shows the tons still to get.

## Windows

- A WFMT window opens on the monitor EDMC is on the first time, and again there if the monitor you left it on is gone. To have every window open there, tick *Always open WFMT's windows on EDMC's monitor* in Settings → WFMT → General → Window. A window you left on a second screen otherwise reopens there.
- If screenshots don't save, Windows **Controlled Folder Access** or your antivirus may be blocking EDMC. Allow it, or choose another folder.
