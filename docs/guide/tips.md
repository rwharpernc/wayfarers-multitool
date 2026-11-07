# Tips, quirks and workarounds

Usage notes that are not covered by a single feature guide. Each mode guide has a longer list at its end. Back to the [README](../../README.md).

## Installing and updating

- Restart EDMC after installing or updating. The WFMT panel appears only after a restart.
- Extract the ZIP over the existing `Wayfarers-Multitool` folder. Saved data is stored in that folder.
- Use the ZIP from the **Releases** page (Assets), not the **Code → Download ZIP** button.
- Automatic updates are off by default (**Download and install updates**, Settings → WFMT → Online). A downloaded update takes effect after a restart: the version line under the mode buttons turns orange and reads *Restart EDMC*.
- Select **OK** in EDMC's Settings window to keep a change.

## Data and backups

- WFMT stores recorded play data in files inside its plugin folder, one section per commander. Updates do not change these files. Deleting or reinstalling the folder deletes them.
- **Back up my data** (Settings → WFMT → General → Backup) creates a zip. A manual backup shows the line `Saved N files (size) to <path>` or the reason it failed. With **Back up automatically** selected and a folder outside the plugin folder chosen, a zip is made when EDMC starts if the newest automatic zip is at least as old as the configured number of days (7 by default), and before an update is installed.
- **Restore** is applied when EDMC next starts. The replaced files are kept in `backups/pre-restore-<date>.zip` inside the plugin folder.
- The Raven Colonial key, the Discord webhook links, the downloaded Codex catalog and the Local star index are not included in a backup. The key and webhook links must be entered again on a new installation.
- Selecting the **Credits this session** line under the mode buttons opens the **Credits Ledger**: income by activity and by day, and the game's lifetime totals.

## EDMC, the journal and catching up

- EDMC passes WFMT only the events that occur while EDMC runs. When EDMC starts, WFMT reads recent journals and catches up without counting any event twice. The look-back period differs by feature (see [If EDMC wasn't running](getting-started.md#if-edmc-wasnt-running)). Data the game does not write cannot be recovered.
- WFMT uses what the game writes to its journal, plus data from Frontier's servers and community services. Where a figure is uncertain, WFMT marks it. Each mode guide lists these gaps in "What the game does and doesn't tell us".
- Data is stored per commander. Switching commanders in EDMC switches the data. Overlay choices (enabled cards, positions, appearance) are also per commander. Overlay Placement can copy them from another commander.
- An amber line under the mode buttons reading *Reading your journals to catch up (...)* indicates that a first-time or long catch-up is running. It ends by itself.
- **Linux:**
  - EDMC's **Journal directory** must point at Elite's journal folder inside the Proton or Wine folder.
  - Auto-Honk and the screenshot timer require `xdotool`.
  - A Flatpak EDMC requires permissions ([WFMT on Linux](linux.md)).

## On-screen overlays

**Choosing an overlay**

- **Windows:** the **built-in overlay** (select under **Settings → WFMT → Overlays → Overlay Connection**) or [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay). EDMCModernOverlay is also required to display other plugins' overlays. Both can run at the same time.
- **Linux:** [EDMCModernOverlay](https://github.com/SweetJonnySauce/EDMCModernOverlay) is required. Right-hand cards stop short of the screen edge ([Known issues](known-issues.md#right-hand-cards-stop-a-little-short-of-the-screen-edge-linux-edmcmodernoverlay)).
- A **Test** button checks the overlay. All overlay features are off until enabled.
- **Overlays shown (click to hide)**, under the mode buttons, hides every WFMT overlay and restores them. The state is not saved: overlays are shown whenever EDMC starts.
- Elite must run in borderless or windowed mode ([overlay setup](../OVERLAY_SETUP.md)).

**Settings location**

- All overlay settings are under **Settings → WFMT → Overlays** (Connection, Placement, Appearance, Hide overlays, and one tab per feature).

**Fonts**

- The built-in overlay uses Source Sans 3 by default. Any `.ttf` or `.otf` file can be added under **Appearance → Overlay font** ([Fonts](../OVERLAY_SETUP.md#fonts)).
- The default font of EDMCModernOverlay has capital letters only. Select another font under **Appearance → Overlay font**.

**Placement**

- **Placement** positions each display at one of nine spots plus pixel offsets, using the detected screen size.
- The **layout editor** is a to-scale picture of the screen with a grid. Dragging a display's box snaps it to an edge (offset 0) or to the grid.
- If a position is wrong, select **Show placement preview**, then **Detect screen again**, or **Reset all to defaults**.
- **Display scaling** (the Windows percentage of the monitor) and **Overlay mode** (Fit or Fill) define how the screen is mapped. **Text size** on Appearance changes the text size only ([the three size settings](../OVERLAY_SETUP.md#moving-things-around)).
- EDMCModernOverlay cannot draw flush against the right edge. WFMT applies an offset to compensate (the switch on the Placement tab disables it), and on Linux a gap remains. The built-in overlay has no such limit.

**Pop-out windows**

- WFMT's pop-out windows have their own text size and color theme, separate from the overlay's. Set them with **A-**, **A+** and the theme name at the right end of a window's bottom line, or under **Settings → WFMT → General → Window**.
- Increasing the text size does not change a window's saved size. Resize the window when text is cut off.

**Appearance**

- **Appearance** sets the color scheme of every overlay.
- Text size is Default or Larger. Spacing is fixed so that columns stay aligned.
- The Interdiction warning is always red.
- **Panel opacity** changes the background of every card and does not change the text.
- The **Color-blind safe** scheme uses colors that remain distinguishable for the common kinds of color blindness.

## Colonization

- Dock at a construction depot, or open its market, once to register a site. Nothing is entered manually.
- The Colony page and window show the commander's own deliveries and cargo. The depot's totals include all commanders' deliveries.
- The history is rebuilt once from all of the commander's journal files and counts from the first delivery in them (the page states the date). Deleted journals cannot be counted.
- **Fleet carrier cargo:** the journal records only cargo transferred to the carrier.
  - To read the real hold, sign EDMC in to Frontier and open **Carrier Management** once. WFMT then reads the carrier's cargo. The data can lag behind the game.
  - If a transfer was not registered, **Rescan Journals** (in the Colonization Sites window) rebuilds the tally from the last 30 days of journals.
- Commanders without a carrier see simpler wording and one Trips column. The carrier lines appear only for commanders with a carrier.
- **Where to buy** requires the internet (Spansh) and caches a search for two minutes. Selecting a result row copies its system name. After **Find all** with several commodities, the **Suggested route to buy what you need...** block above the lists shows a **Next stop** card (with a button that copies its system) and the stops in flying order, with the jump to each, the purchases at each and the stock there. **Stop** keeps the results found so far. **Exclude surface ports** (off by default) removes surface ports. The route then states which commodities are sold only on a surface. The route follows purchases: an item in the hold or on the carrier is removed from the route.
- The **In Cargo** figures come from the game's `Cargo.json`, read again shortly after any event that can change the hold.
- **Raven Colonial** (ravencolonial.com) is optional.
  - Planned Builds, My Projects (viewing), Raven Progress, Refresh from Raven and the page links only read data or open the browser.
  - Sending data to Raven is off until **Colonization: share progress and deliveries** is ticked in Settings → WFMT → Online and a Raven key is saved. This covers progress sharing, **Create Project on Raven**, **Report Complete to Raven**, **Mark Plan Entry Demolished**, and **Set as My Primary** and **Save Counted List** in My Projects.
  - **Create Project on Raven** (in the Colonization Sites window) creates a project when Raven has none for the site.
  - **Test key** checks the key.
- **Shopping-list overlay:**
  - **Always show the shopping list, whatever screen you are on** (Settings → WFMT → Overlays → Colonization) keeps the list shown on every screen. The Colony page has no Overlay button. The **Overlays shown (click to hide)** line hides the card together with every other overlay.
  - The automatic option in Settings shows the list at a market, in Carrier Management or at a construction site.
  - The list omits commodities already covered by the hold and fleet carrier (*List: To buy*, the default; *To haul* applies once everything is on the carrier). The Acquire column shows the tons still to obtain.

## Windows and settings

- **Trade, Mining and Missions have no page arrows.** The panel shows a short summary and a button for each page (Trade: **Session**, **Routes**, **Market**, **History**; Mining: **Space Mining**, **Surface Mining**; Missions: **Mission types**). Each button opens its page in its own window.
- **A setting that belongs to a window is in that window.** Routes' hops and filters, Market's radius, Mining's display switches, the Mission types **Display** card, and the **Settings** tabs of Powerplay and Inventory are set there and saved on change, without **OK**. File → Settings → WFMT keeps the switches that allow contact with another service, the keys, and a note on each tab stating where its other settings are.
- Body, Ring, Ship and commodity boxes suggest names while typing, from data WFMT already holds, and so do the Round trip **Start from** box and the search and filter boxes of Materials, Blueprints, Inventory and Stored modules. Nothing is fetched.
- A WFMT window opens on the monitor EDMC is on the first time, and again there if the monitor it was left on is no longer present. To open every window on EDMC's monitor, select *Always open WFMT's windows on EDMC's monitor* in Settings → WFMT → General → Window. Otherwise a window left on a second screen reopens there.
- If screenshots are not saved, Windows **Controlled Folder Access** or an antivirus program may be blocking EDMC. Allow EDMC or choose another folder.
