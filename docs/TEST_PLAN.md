# Test plan: 1.3.3

What to check in EDMC after the 1.3.3 release (and before any later one), on **Windows** first and then on **Linux**.

- This is the quick pass over the whole release:
  - the Rare Goods Finder
  - Mining
  - the Carrier Route window
  - the Expedition, Route Planner and overlay basics
- The rest of the in-game checks (every mode and window) are under "Verification in the game" in [TODO.md](TODO.md).
- The unit and smoke tests pass, but they cannot show what the game, the overlay and a real clipboard do.
- The overview is in [CHANGELOG.md](../CHANGELOG.md) and [STATUS.md](STATUS.md). The longer wording for each check is in [TODO.md](TODO.md) (under "Verification in the game").

## Where the testing stands (2026-10-30)

| Platform | Automated tests | Checks in the game |
|---|---|---|
| **Windows** | The logic tests run natively and pass. The Windows-only code (the overlay, Win32 and WebView2) is proved only by the in-game pass. | Not yet recorded for 1.3.0. Sections 1 to 7 below are open. |
| **Linux** | 3,731 tests pass in the Docker container (Xvfb and a window manager), 13 skipped, run on 2026-10-30 for the 1.3.3 release (3,687 for 1.3.2, 3,656 for 1.3.1, 3,639 before 1.3.0, 3,485 on 2026-10-28 before 1.2.0, 3,471 on 2026-10-27 before 1.1.0). | Not yet recorded for 1.3.0. The last manual passes (2026-10-18 and 2026-10-20) were of builds from before the rename; see [STATUS.md](STATUS.md) and [LINUX_TESTING.md](LINUX_TESTING.md). |

- 1.0.0 was released on 2026-10-26 (tag `v1.0.0`). 1.1.0 was released on 2026-10-27 (tag `v1.1.0`). 1.2.0 was released on 2026-10-28 (tag `v1.2.0`). 1.3.0 was released on 2026-10-29 (tag `v1.3.0`), 1.3.1 the same day (tag `v1.3.1`) and 1.3.2 the same day (tag `v1.3.2`), and 1.3.3 on 2026-10-30 (tag `v1.3.3`). These passes are the checks to run on the released build, and a failure goes to a fix on a short bugfix branch (`bugfix/1.3.2` is open).
- Tick a box in the sections below only when you have seen it pass; nothing here has been ticked from the automated run.

**Reporting**

- Tick a box when the check passes.
- When something fails, say which check, the system, and what you saw, with the relevant lines of EDMC's log.
  - Windows: `%LOCALAPPDATA%\EDMarketConnector\logs\`
  - Linux: `~/.local/share/EDMarketConnector/EDMarketConnector.log`

## Getting the build

1. Run `npm run deploy` from the branch being tested. It builds and merges the result into EDMC's plugins folder (native or Flatpak). Restart EDMC (every deploy needs a restart).
2. New files appear beside the plugin as you use the features: `carrier_route.json` (Carrier Route) and `mining_history.json` (Mining History), one record per commander.

## 1. Rare Goods Finder (Powerplay mode, Rares)

- [ ] The window shows **Distance**, **Arrival**, **Legality** and the other columns without cutting any off, and fits your screen.
- [ ] Distance is 0.0 ly for a rare in your own system and grows down the list; it updates after a jump. Clicking a heading sorts by number, and a second click reverses it.
- [ ] Spot-check Arrival (a station's distance from its star, in light seconds) against the game for a near station, a far one and Hutton Orbital.
- [ ] Legality: most rows say *Legal*; in a Federation or Alliance theocracy or a Prison Colony system, Lavian Brandy says *Illegal here*; selecting a row says where it is illegal. Compare with the station's Prohibited list on the system map.
- [ ] **Large pads only** keeps only large-pad stations.
  - **Only my Power** is grayed out until your Power is known, then keeps the rares whose origin system your Power controls (the status line shows Spansh being asked, ten at a time).
  - Both choices are remembered.
- [ ] **Copy system** puts the selected rare's origin system on the clipboard (check it pastes into the galaxy map).

## 2. Mining (Mining mode)

- [ ] Space Mining page: **Last rock** follows each prospected rock; a core asteroid adds `core: <mineral>` and **Core asteroids found**; the limpet figure reads `(N on board)` and matches your cargo.
- [ ] Settings → Mining: type a target commodity and a percentage; a rock at or over it says `target`.
- [ ] Accept a mining mission: **Mission needs** shows its tons against what you hold, and changes as the hold changes.
- [ ] Flight Alerts (Settings → Overlays → Flight Alerts, Mining alerts ticked): the Test Card shows the green core lines.
  - In a ring a core asteroid and a rich rock give a green card for about 30 seconds.
  - Low limpets and a nearly full hold give amber cards.
  - None shows while you are not mining.
  - The sound plays if ticked.
- [ ] **Mining History** (the Dashboard button): the Overview, Commodities, Rings and Runs tabs fill from your journals and sort; the totals look right against what you remember.
- [ ] **Book** on the Space Mining page opens the **Space Mining Book**.
  - It lists rings from your journals with hotspots per mineral, class, reserve level, tons mined and last mined.
  - Try a note, a favorite, **Find**, **Add ring** and **Copy system**. Restart EDMC and the notes remain.
  - **Book** on the Surface Mining page opens the **Surface Mining Book**, with a **From your journals** group (bodies with mining locations and the tons refined on them).
- [ ] **This system** (in both books):
  - In a system you have mined it goes to the ring or body. In one you have not it says `You have not worked this system yet.`
  - On the first open of each book a notice says the journals are being read, and the list does not flicker while it grows.
- [ ] The Surface Compass, the Surface Mining Book's stops and Market research, and Share line still work (their checks are in [TODO.md](TODO.md)).

## 3. Carrier Route (Route Planner window → Carrier route)

- [ ] The carrier block and the boxes fill in from the journal (where the carrier is, the tritium in its tank, the space used) and match Carrier Management. If they say not known, open Carrier Management once.
- [ ] Type a destination and press **Generate route**. Compare the jumps and the tritium with Spansh's own Fleet Carrier Router page for the same carrier. The first line says how much tritium to have at the start.
- [ ] **Copy next system** puts the next system on the clipboard (check it pastes). Schedule the jump in the game; when the carrier arrives the row turns green and the next is marked. **Mark next as reached** does it by hand.
- [ ] Restart EDMC: the route comes back. A second commander sees none.
- [ ] If you have a squadron carrier, choose it in the Carrier box and plot one.

## 4. Expedition, Route Planner and overlays

- [ ] **Expedition** and **Plot** on the panel open one window with Plan, Route and Log tabs, never twice; its size and position are remembered.
  - The Expedition section holds the Log's figures, Copy Next and Expedition, and has no Start, Pause or Stop.
  - There is no Expedition Log section.
- [ ] The Expedition window's **Neutron route** switches to the Route tab.
  - **Road to Riches** and **Exomastery** open their dialog and **Plot** works.
  - **Start expedition** in the Route Planner window makes an expedition from a plotted route (named `Neutron Highway from <start> to <destination>`) and starts it and its Expedition Log run. The status line turns green and the button reads **Started ✓** for a few seconds.
  - **Review expedition** switches to the Plan tab on it.
  - Pause, Resume and Stop on either side agree.
- [ ] The overlays show and hide from the panel's overlay line; each mode's panel lays out cleanly and does not widen the EDMC window; the Expedition row still shows the next stop, its distance and note.

## 5. Added since this plan was written (2026-10-23)

Do these on **Windows** and again on **Linux**. Where the two differ the line says so.

- [ ] **Every overlay is off after the first start of this build.**
  - Restart EDMC. The log has one line, `All WFMT overlays reset to disabled (one-time), including the saved choices of N commander(s)`, and no overlay card shows for any commander.
  - Turn one card on, restart, and check it is still on (the reset runs once).
  - Windows: log in as each commander you have and check none shows a card. Linux: the same, and check `overlay_settings.json` beside the plugin.
- [ ] **A stopped expedition carries on from where it stopped.**
  - Start an expedition, jump or scan, press Stop, wait a minute, start it again from the Route tab, and check the clock carries on from where it stopped.
  - The Log's **Resume** does the same.
  - Pause one for a minute, make a few jumps while it is paused, resume it, press **Rescan** in the Log window, and check the rescanned totals do not include the jumps made while it was paused.
- [ ] **The screen size.** Settings → Overlays → Overlay Placement says where the size came from.
  - With the game's files or the overlay running it names them.
  - Rename the overlay's log (EDMCModernOverlay's `overlay_client.log`) and the game's `DisplaySettings.xml` so neither is found, press **Detect screen again**, and check it says it is using the primary display, with your real resolution. Put the files back afterwards.
  - Windows: the size is the hardware resolution, not the scaled one (3840 x 2160 at 125% reads 3840 x 2160). Linux: report the session type (Wayland or X11) and whether `xrandr` is installed.
  - On an ultrawide or triple screen, open the placement preview and check no box is off the screen or on top of another.
- [ ] **Long names in the tables.** In the Missions, Source commodities, Ship Builds and My Codex windows a long faction, station, ship, role or site name shows whole at a wide size and cut with an ellipsis at a narrow one, and the window does not grow wider than its size.
- [ ] **Saved data from before the spelling change** (a copy that predates this build). Start EDMC and look for `Renamed saved names:` in the log, once. The Colonization page, the Sites window, the fleet carrier column and the overlay positions are as you left them. A body or system whose name holds the letters of an old spelling inside a word (the old spelling of tons or analyzed) keeps its name.

## 6. Added since section 5 (2026-10-26): Colonization

Do these on **Windows** and again on **Linux**. The longer steps are in [TODO.md](TODO.md) (Missions, trade and colonization) and [LINUX_TESTING.md](LINUX_TESTING.md).

- [ ] **The hold follows a purchase.** Buy a tracked commodity at a market: the **In Cargo** figures in the Sites window, on the Colony page and on the overlay card change within a couple of seconds.
- [ ] **Color themes.** Open the Sites window and press the theme name at the right end of its bottom line: choose Cyan, then Amber, then Green, then Navy. Each time every open WFMT window changes colors at once (surfaces, titles, headings, table rows, buttons, the footer message), nothing becomes hard to read, and a window opened afterwards has the same theme. Settings → WFMT → General → Window → Color theme shows the same name, and the choice is kept after a restart. The stat tiles at the top of a dashboard do not grow when **A+** is pressed.
- [ ] **Text size and column fit.** In the Sites window press **A+** twice at the right end of the bottom line: every window's text grows and columns stay aligned; **A-** shrinks it. Settings → WFMT → General → Window → Text size shows the number and keeps it after a restart. Short columns (such as Required) are narrow and a long name column takes the spare width.
- [ ] **Colonization Archive.** With at least one finished site in the Sites window, open **Manage Sites → Archive Finished**: the finished sites leave the list and the status line counts them (unfinished sites stay). **Manage Sites → Show Archive** lists them with result, dates, time taken and tons needed, and selecting one shows its commodities. **Restore** returns one to the Sites window, **Copy Summary** pastes readable text, and **Manage → Remove Permanently** asks first. Restart EDMC: the archive is still there. The History figures and **Back up my data** still include archived sites. Nothing is cut off at the window's smallest size.
- [ ] **Raven project offer and Create Project.** With Raven sharing on and your key saved, dock at a new construction site that Raven has no project for. A line on the Colony page says `Raven Colonial has no project for <site>.` with **Create on Raven** and **Not Now**. **Create on Raven** opens the Sites window on that site and the Create dialog, centered and fully on the screen; **Not Now** hides the line, and it is not offered again for that site. After creating the project the line is gone. Press **Create Project on Raven** from the menu yourself on a site with a project: the status line says Raven Colonial already has a project for the site and stays up for 30 seconds while the game's construction panel is open. Nothing is sent until you press **Create** in the dialog.
- [ ] **The navy look.** Open the Sites window, Inventory, the Exploration Dashboard and the Mining Book. Surfaces are navy, not gray; the window title is gold; section labels and table column headers are cyan; the footer message is bright yellow, and green after something succeeds (for example Start expedition). Nothing is hard to read, and the Colonization overlay card's header over the third column reads **Acquire**.
- [ ] **Acquire is what is still to get.** It falls as you load the ship or the carrier and reaches 0 once the whole amount is acquired; **Haul Trips** still counts everything the site needs. The overlay card shows the same Acquire and no To buy column.
- [ ] **A lagging Frontier copy does not undo a transfer.** With EDMC signed in to Frontier, unload cargo at your fleet carrier, then open Carrier Management or fly back for another load. The FC column keeps the unloaded stock, and an `ignored` line from `Carrier cargo from Frontier` is in the WFMT log lines (press **Copy diagnostics** to see them). After 15 minutes without a transfer, open Carrier Management again: a Frontier figure that has changed replaces the tally, and one that is unchanged stays ignored.
- [ ] **Show / List: the middle step.** With everything bought and on the fleet carrier, the Sites window's **Show** set to **To buy** lists nothing, **To haul** lists every commodity, and a commodity drops off **To haul** once its whole need is aboard your ship. Settings → WFMT → Overlays → Colonization → **List** does the same for the overlay card; **To buy** (the default) leaves out the covered rows and the footer still counts them, and **All** lists them.
- [ ] **Where to Buy window.** In the Sites window click a commodity row: the footer says what to do next. **Where to Buy** opens its own window with the site's system and a **Commodity** line naming the row; pick another row or site and it follows; **Find nearest** and **Find all** work as before; it remembers its size and position and closes with the Sites window.
- [ ] **Biology overlay card and the layout editor.** Settings → Overlays → Exobiology → **Test Cards** shows the Biology card with a row for each candidate species and its value and share at the right; on a real body with several candidate species check the same, including `+N more` and a long species name. In Overlay Placement drag a tall box (the Biology card) flush to the top: it lands as a top placement with offset 0.
- [ ] **Raven Colonial.** **Projects** opens My Projects (reading needs no key). **Create Project on Raven** at a construction site you are docked at: check the project, the link, the primary project and the attached carrier on ravencolonial.com. **Sync Sites:** delete a project on Raven while its site is still active in WFMT, press **Refresh** and then **Sync Sites** in My Projects: the dialog names that site (and only sites with no Raven project), and after you agree the Colony panel no longer names it as the current project.

## 7. Added in 1.3.0 (2026-10-29)

The longer wording for each is in [TODO.md](TODO.md). Tick a box only when you have seen it pass.

- [ ] **Discord sharing** (needs a webhook in a private test channel of your own): **Settings → WFMT → Discord**, one destination and then two; **Post to Discord** from the BGS Report and the Powerplay Sessions window, posting again to edit, the destination menu, **Copy for Discord**, and the plain **Copy Summary** and **Copy Progress**. The checklist is in [TODO.md](TODO.md) under "Screenshots, settings and general".
- [ ] **Customize Discord posts:** the dialog opens from the BGS Report, the Powerplay Sessions window and the Discord tab; the presets, checkboxes, preview, **Save as…**, **Rename…** and **Delete** work, a saved template survives a restart, and the chosen template is what **Copy for Discord** and **Post to Discord** produce.
- [ ] **Expedition Log:** the three **Start from my last** buttons (sale, Discovery Data sale, Exobiology Data sale).
- [ ] **Expeditions are managed in the Expedition window:** the Exploration panel's Expedition section has no Start, Pause or Stop, and the Expedition window's Plan and Log tabs start, pause and stop them.
- [ ] **Colonization:** the Sites window's **Show** choice and the overlay follow each other; under **To haul** there is no green, and the rows in your hold are tinted (in each theme) in the window and drawn in the theme's blue on the overlay, with the ✓ kept.
- [ ] **Exobiology:** the Bio status card is a wide strip with the distance line beside the species and reward; the Organic Scanning section starts folded; sampling a different genus abandons the unfinished one (back to 0 of 3).

## 8. Added in 1.3.2 (2026-10-29)

- [ ] **Windows open on EDMC's monitor:** with EDMC on one monitor and another connected, open a window you have never opened (the Notes window, say): it opens over the EDMC window on that monitor. Drag it to the other monitor, close it and open it again: it reopens on the other monitor.
- [ ] **Always on EDMC's monitor:** tick *Always open WFMT's windows on EDMC's monitor* (Settings → WFMT → General → Window) and open that window again: it now opens over the EDMC window, wherever you left it. Untick it: it goes back to reopening where you left it.
- [ ] **A monitor that is gone:** with a window left on the second monitor, disconnect that monitor (or on Windows set the display to the first monitor only) and open the window: it opens over the EDMC window, not off-screen.
- [ ] **Buttons and tooltips:** the mode row reads Powerplay, BGS, Explore, Mining, Trade, Missions, Operations, Colony without making EDMC's window wider; every button on the panels and in the windows shows a tooltip when hovered; no button label is in capitals.

## 9. Added in 1.3.3 (2026-10-30)

- [ ] **Powerplay card:** Settings → WFMT → Overlays → Powerplay, tick *Enable the Powerplay card* and press **Test Card**: a card headed *Sample System* with *Rank 12* appears at the top right, showing **Your Power**, Total merits, the Cycle merits, System, Held by, *Merits here count as* and the Reinforcement and Delivery/Donation rows, and clears after a few seconds.
- [ ] **Powerplay card in a Powerplay system:** jump into a system with a Powerplay state: the card shows your Power and rank, the system's state and holder, what merits there count as, and nothing under *Earned here* until you earn some; after earning merits it lists each type with merits and, except for Delivery and Unattributed, the estimated Control Points (they match the Powerplay panel).
- [ ] **No Powerplay Detected:** jump to a system with no Powerplay state (a populated system with no Power presence, say): the card is headed with the system's name and says **No Powerplay Detected in system**. Right after starting EDMC mid-session, before your first jump, the card stays blank instead of saying so.
- [ ] **Look-ahead:** tick *Look up the system I am jumping to* and start a hyperspace jump to a Powerplay system: the card turns to the destination as soon as the jump charges (marked *jumping*, `Looking up Powerplay…` for a moment, then its state, holder, what merits there count as and, when the lookup is fresh, a control progress percentage) and to the system you arrive in when the jump ends. A jump to a system with no Powerplay data says **No Powerplay Detected in system**. A jump you cancel or are interdicted out of puts the card back on the system you are in. With the tick off, the card never turns to the destination and nothing is sent to Spansh.
- [ ] **Loop route:** with the look-ahead on, fly a loop of Powerplay systems twice: the second lap's destinations show at once, with no `Looking up…`, and the log shows no new Spansh request for them (only systems you have not arrived in within the hour are asked about). A destination's percentage is gone ten minutes after the card first showed it.


## 10. Added since 1.3.3 (unreleased)

- [ ] **Closest way to buy everything.** After **Find all** with two or more commodities, a shaded block above the lists shows the suggested route: stops nearest first, and under each the commodities to buy with price and supply. **Copy Route** copies it, and **Stop** keeps what was found.
- [ ] **Where to Buy filters.** **Only stations with enough stock**, **Only stations with a shipyard** and **Arrival within** each narrow the lists and route without a new search; all are off by default and remembered.
- [ ] **Where to Buy: surface ports and purchases.** **Exclude surface ports** ticked removes planetary stations from the lists and route and names any commodity sold only there; buying a listed commodity (hold or carrier) shrinks or removes it on the route without a new search.
- [ ] **Window tooltips.** Hover each button of the pop-out windows and dialogs (the Colonization Sites window, My Projects, Create Project, Add Ring, hotspot import and export, Screenshots, the message dialogs) and the A-, A+ and theme name in a window's footer: after about half a second each shows its tip.
- [ ] **The Colony page.** In the main EDMC window the Colony page is in sections (the project, **What you have**, **To finish the build**) with no Next line, **Still needed** says when a build is complete, and with no site under construction it lists the last 5 completed sites, newest first.
- [ ] **Copy overlay choices from another commander.** With two commanders seen, the Overlay Placement tab lists the other; **Copy** then **OK** gives the current commander the other's cards, placement and look, **Cancel** changes nothing.
- [ ] **Windows keep their monitor.** Move a WFMT window to the monitor left of the primary, close and reopen it: it returns to the same monitor.
- [ ] **The diagnostic log.** Settings → WFMT → General → Help: **Write a separate diagnostic log** is unticked and no `logs/WFMT` folder or file exists. Tick it and press OK: `logs/WFMT/wfmt-diagnostics.log` appears with a start line (versions, system). Press a mode button, open the Colonization Dashboard, press a button in it, run a Where to Buy search and **Rescan Journals**, then jump or dock in the game: each shows as a line (mode selected, window opened, button pressed, the search with its time, the rescan, the journal events with their names), and a Spansh request shows its endpoint, outcome and time. Your commander name appears as `<commander>` and your home folder as `~`. EDMC's own log has no extra DEBUG lines. Untick it and press OK: the file stops growing. **Open log folder** and **Copy log path** work.
- [ ] **The Engineering row.** In Operations mode the first section is **Engineering** (it was Materials): the text reads `Materials held: ...`, `Last change: ...`, `At the limit: ...`, `Engineers: N of 38 unlocked · N invited · N known` and the wishlist; the section title says just **Engineering**, folded or open. **Materials**, **Blueprints** and **Engineers** are in one row; **Engineers** opens the Engineering window on its Engineers tab and **Blueprints** on its Blueprints tab. The EDMC window does not widen.
- [ ] **What you need to hand over.** Select Chloe Sedesi: the items section lists Sensor Fragment, need 25, how it is got (a Thargoid or Guardian site) and **Look up the nearest Thargoid site**; pressing it says it is looking, then the line at the foot of the window names a Thargoid system with its distance (never a Guardian site) and says the system name is copied, so it pastes into the galaxy map (or it says why it could not: not logged in, or Thargoid sites switched off). Select Liz Ryder: Landmines offers **Find where to buy**, which opens Where to buy for Landmines x200 (with Trade's online lookups on, **Find sources** lists stations). Select an engineer whose item is engineering material (data) and one on foot: the text says how it is got, with no button. Chloe Sedesi and Professor Palin show **How to get it** (HIP 17403, steps, cautions) marked community-reported; an engineer with no written guide says so.
- [ ] **Links and copying.** On the Engineers tab select an engineer: their system (in the line under the name and in the **System** row) is underlined and opens the Inara page for that system in the browser when clicked; the pointer becomes a hand over it. Select part of the details with the mouse and press Ctrl+C, then paste elsewhere: the selection pastes. Ctrl+A then Ctrl+C copies everything. Right-click gives Copy selection, Copy all and Select all. **Copy details** copies the whole pane and the footer says so.
- [ ] **Path to unlock.** On the Engineering window's **Engineers** tab, select an engineer you have not unlocked. Under the table the path shows as numbered steps: find them, the permit if one is needed, the invitation, the unlock. Compare each with the in-game Engineers panel: *Known* marks the find done, *Invited* marks the find and the invitation, *Unlocked* marks everything.
- [ ] **Verification needed and Game data.** Select an engineer whose requirement WFMT cannot check (Eleanor Bresa, Marco Qwent, Bill Turner): the details end with the **Verification needed** note; an unlocked or invited engineer, or one WFMT can check (Felicity Farseer), has none. Press **Report engineer data**: the browser opens a GitHub form with the area, the engineer, WFMT's standing and the Environment box filled in and no commander name. **Settings → Help → Report game data** opens the same form with only the Environment filled in. Close the tab without submitting.
- [ ] **Status colors.** The Engineers tab colors a row green for an unlocked engineer, yellow for Known or Invited and red for one the game has not listed you as knowing. Switch through all four themes (the theme name in the window's footer): the three colors stay readable and distinct. Compare a few with the in-game Engineers panel. Select an engineer: the details under the table have a large bold title with a colored status, then bold headings (Location, Path to unlock, Raising your rank with them (one general line marked community-reported, not the table's sentence), Notes), numbered steps with bold labels and wrapped lines indented under the detail, and nothing is cut off at the right or the bottom at the window's minimum size and at the larger text sizes.
- [ ] **A chain.** Select Tiana Fortune (or any engineer found through another). The path starts with the engineers to deal with first, in order (Liz Ryder, then Hera Tani), says `takes 3 engineers, in this order`, and leaves out any you have already unlocked.
- [ ] **Next step column.** The column reads the one thing to do next for each engineer who is not unlocked: their own step, or `First <engineer>:` and that engineer's step when another comes first (Lei Cheung: First The Dweller). A find step that only says "Common knowledge" is skipped. Unlocked engineers list first.
- [ ] **On-foot hand-ins.** Select Kit Fowler: his path has the step "To learn of Kit Fowler, give Domino Green the items: Provide 5 doses of Push." (the hand-in belongs to the *next* engineer). Select Yarden Bond, Oden Geiger, Uma Laszlo and Yi Shen: none has an unlock step of its own, and Yi Shen's path has a hand-in step for each of the three engineers he is found through.
- [ ] **Requirement notes.** Select an engineer whose invitation asks for a rank or a lifetime figure, for example Lori Jameson (Combat rank), Lei Cheung (markets traded with) or Selene Jean (tons mined). The step carries a note such as `(you have Competent: needs Dangerous)` or `(you have 304 markets: met)`, and the figure agrees with the commander's in-game Commander panel (ranks) and Statistics (lifetime figures). The note never marks the step done.
- [ ] **Freshness.** Log out and back in to refresh a lifetime figure; a promotion shows at once. Start EDMC after the game is already logged in: the notes still appear without logging in again (WFMT reads the newest `Rank` and `Statistics` from the journal files once, in the background).
- [ ] **Not checkable.** Select an engineer whose invitation asks for a faction's standing or a bartender sale (for example Marco Qwent or Bill Turner): the table's words show with no note and no mark. 20 of the 38 engineers are like this.

## Linux specifics

The same checks apply. The points that differ:

- Overlays need EDMCModernOverlay (the built-in overlay is Windows only).
- The clipboard needs a working clipboard tool, so check each **Copy** button and paste.
- A Flatpak EDMC needs the permissions in [WFMT on Linux](guide/linux.md).
- The screen size falls back to `xrandr` (through the host from a Flatpak) when the game's files and the overlay's log cannot be read.

Report the distro, desktop, X11 or Wayland, and native or Flatpak EDMC.
