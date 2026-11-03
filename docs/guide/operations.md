# Operations

This page describes the Operations mode: screenshots, inventory, engineering materials (with blueprints, wishlist, ship planner and engineers), saved ship builds and the combat record. Colonization is a separate mode: see [Colonization](colonization.md).

**Data sources:**

- Screenshots, the backpack and ship locker, ship loadouts, and kills and deaths come from the journal (or from EDMC's own state, which EDMC rebuilds from the journal).
- The journal does not report the backpack capacity; WFMT uses a built-in table.
- The Carrier Locker is not in the journal. It comes from Frontier's servers through a signed-in EDMC.
- See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

**On this page:**

- [How to](#how-to)
- [Screenshots](#screenshots)
- [Inventory](#inventory)
- [Materials](#materials)
- [Engineering](#engineering-blueprints-and-a-wishlist) (including the [Ship planner](#engineering-blueprints-and-a-wishlist))
- [Ship Builds](#ship-builds)
- [Combat Record](#combat-record)
- [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)

## How to

Common tasks, each with a link to the full description.

**Set up screenshots** (details: [Screenshots](#screenshots))

1. Open **Settings → WFMT → Operations → Screenshots**.
2. Verify that **Screenshot Directory** is the folder in which the game saves screenshots (use **Browse…** to change it).
3. Select a **Converted Directory** for the PNG copies and a **Filename Mask** from the drop-down.
4. Optionally tick **Delete original file after conversion**.
5. Take a screenshot in the game. The status line on the Operations panel shows the converted file's name.

**View the backpack and cargo** (details: [Inventory](#inventory))

1. Switch to Operations mode. The Inventory bars show the Backpack, the Ship Locker and, while in a ship or SRV, the Cargo.
2. Click a bar to open the Inventory window.
3. Select the **Backpack**, **Ship Locker** or **Cargo** tab. Text in **Filter** narrows every tab at once.

**Check materials for a blueprint** (details: [Engineering](#engineering-blueprints-and-a-wishlist))

1. Press **Blueprints** on the Engineering row to open the Engineering window.
2. On the **Blueprints** tab, enter the module or effect in **Search** and select the blueprint. The ingredients show what one craft takes and how many are held.
3. Set **Crafts**, then press **Add to wishlist**.
4. Open the **Wishlist** tab to see whether the entry **can be made now** and what it is **short** of.

**Find a material trader** (details: [Materials](#materials))

1. Press **Materials**, then **Find a trader** in the Materials window.
2. Select the **Type**, **Within** distance and **Pad** size, and check **Search from**.
3. Press **Find**. The **Material trader** window lists the closest stations first.

**Save a ship build** (details: [Ship Builds](#ship-builds))

1. Design the build on Coriolis, EDSY or Spansh and copy its address from the browser.
2. Press **Ships** in the **Ship Builds** row, then **Add build**.
3. Fill in **Name**, **Ship**, **Site** and **Link**, then press **Save**.

**See your kills and deaths** (details: [Combat Record](#combat-record))

1. Open the **Combat Record** row. A small table shows the **Kills**, **Deaths** and **K/D** of **This session** and **All time**. **Kills** includes PvP kills, as K/D does. While the journals are being read, the **All time** row reads `...`.
2. Press **Combat**.
3. Select the **This session**, **All time** or **Sessions** tab. Every tab splits the figures by ship.

**Plan the engineering of a whole ship** (details: the Ship planner in [Engineering](#engineering-blueprints-and-a-wishlist))

1. Export the build from EDSY or Coriolis as SLEF and copy it.
2. In the Engineering window open **Ship planner** and press **Paste from clipboard**.
3. Set **Rolls per grade**, then press **Add plan to wishlist**.

## Screenshots

Converts Elite's screenshots to PNG automatically, with an optional crop to the relevant HUD panel. No action is required: conversion occurs when the game's journal reports a screenshot.

**Panel** (Operations mode, **Operations**):

- A status line. It reads `Waiting for a screenshot…` until a screenshot is taken, then the converted file's name (cut to 40 characters). Clicking the status line opens the folder the last screenshot was saved in.
- The **clock icon** to its right turns the auto-capture timer on and off (see below). It is hidden when the timer cannot work on the system or when the icon is turned off in Settings.
- **Click to expand** / **Click to collapse** shows or hides the thumbnails. They start collapsed at each EDMC start.
- Expanded, the panel shows the newest screenshot as a thumbnail (and, when a crop was made, the cropped copy beside it), then **Recent - click to preview**: the eight screenshots before it, in rows of four. Clicking any thumbnail, including the newest, opens a larger preview.
- The preview window is view-only. It scales the image to fit the window (never larger than the image), remembers its size, and has an **Open Folder** button for the folder the file was saved in, a **Close** button and a help button.

**Processing of each screenshot.**

1. The game saves its own image file in its screenshots folder and writes a `Screenshot` entry to the journal.
2. WFMT locates the file, converts it to PNG in the **Converted Directory**, and names it from the **Filename Mask** (the system, the body or station, the commander name, a five-digit number or the date and time in UTC).
3. If **Delete original file after conversion** is ticked, the game's original is deleted after a 60-second grace period so that other tools can access it first.
4. If the panel that was open when the key was pressed has a crop rectangle, a cropped copy is also made: the target panel, the comms panel, the role panel or the left-hand (systems) panel. A high-resolution screenshot is never cropped. The rectangles are fixed measurements for a 1920 by 1080 screen, scaled to the screenshot's size and centered on wider screens.
5. The status line, the thumbnails and (if enabled) the on-screen **Screenshot saved** message update.

The status line also reports problems: `Screenshot not found - check Screenshot Directory in Settings` (the file is in none of the known folders) and `Conversion failed: <reason>`. If the file is not in the configured folder but is found in a known fallback folder, WFMT corrects the Screenshot Directory (and moves the Converted Directory with it when that was still the default).

**The auto-capture timer.** The clock icon presses the game's screenshot key (F10) on a timer.

- Clicking the icon starts the timer (`Auto-capture enabled`); clicking again stops it (`Auto-capture disabled`). The timer is off at every EDMC start and stops by itself when the game shuts down or the commander dies (`Auto-capture stopped`).
- The key is pressed only while Elite is the foreground window; otherwise the status line reads `Auto-capture paused (Elite not focused)`.
- The key is pressed once per **poll interval** (1 second by default, 0.2 second minimum).
- The key press is supported on Windows, and on Linux under X11 or XWayland with `xdotool`.
- **Thargoid scans.** When a Thargoid signal's data is collected, WFMT presses the key once (if *Automatically capture a screenshot when scanning a Thargoid signal* is on) and crops the copy to the bottom-left quarter of the screen, where the scan result appears. The same crop is used for the next screenshot taken while the game's Thargoid encounter music is playing.

**Settings → WFMT → Operations → Screenshots:**

| Setting | Default and detail |
|---|---|
| **Screenshot Directory** | Where the game saves screenshots. **Browse…** selects a folder |
| **Converted Directory** | Where the PNG copies are stored. **Browse…** selects a folder |
| **Delete original file after conversion** | Off |
| *Include WFMT's built-in overlay in the converted screenshot (the game's own capture never shows an overlay)* | Off. Windows; requires the built-in overlay selected under Settings → WFMT → Overlays. WFMT draws the cards that were on screen when the key was pressed onto the converted copy. A failure never loses the screenshot |
| **Group converted files into a per-system subfolder** | Off |
| **Show the auto-capture timer icon on the main window** | On |
| **Filename Mask** | A drop-down of presets, from `SYSTEM(BODY)_NNNNN.png` (the default) through `SYSTEM(CMDR)_DATE.png`, `BODY(CMDR)_NNNNN.png`, `SYSTEM BODY (CMDR) NNNNN.png` to `DATE_SYSTEM_BODY_CMDR.png`. `NNNNN` is a running five-digit number, `DATE` the date and time |
| **Auto-capture poll interval (seconds)** | 1; minimum 0.2. This setting, the timer icon option, the high-resolution option and the Thargoid option appear only where WFMT can press the screenshot key (Windows, or Linux with `xdotool`) |
| **Use high-resolution capture on the auto-timer (Solo play only)** | Off. The timer holds Left Alt with F10, which the game honors in Solo only |
| **Automatically capture a screenshot when scanning a Thargoid signal** | On |
| **Show a notification on the in-game overlay when a screenshot is saved** | Set on **Settings → WFMT → Overlays → Screenshots**. Off; requires an overlay; has a **Test Overlay** button |

**Example: one folder per system.**

1. Open **Settings → WFMT → Operations → Screenshots**.
2. Tick **Group converted files into a per-system subfolder**.
3. Keep **Filename Mask** on `SYSTEM(BODY)_NNNNN.png`.
4. Take a screenshot at a planet. WFMT converts it and the status line shows the new file name. Clicking the status line opens the folder.

**Example: auto-capture during scanning.**

1. With Elite in the foreground, click the clock icon on the Operations panel. The status line reads `Auto-capture enabled`.
2. WFMT presses F10 once per poll interval.
3. When Elite loses focus, the status line reads `Auto-capture paused (Elite not focused)` and no key is pressed.
4. Clicking the icon again shows `Auto-capture disabled`. The timer also stops when the game shuts down or the commander dies.

On Linux, the auto-timer requires `xdotool`, and a Flatpak EDMC requires the screenshots permission. See [WFMT on Linux](linux.md). On Windows, OneDrive-redirected folders are handled automatically.

## Inventory

Tracks Odyssey **microresources** and the cargo hold as capacity bars. Microresources follow the game's three categories: **Assets**, **Goods** and **Data** (the journal calls these Component, Item and Data).

**Panel:** a status line (`Awaiting Odyssey loot…` until an event occurs), then up to four bars. Each shows `count/capacity`, or only the count where the capacity is unknown.

| Bar | Capacity | When it appears |
|---|---|---|
| **Backpack** | From the suit, if known (see below) | Always |
| **Ship Locker** | 1,000 each of Assets, Goods and Data (3,000 in all) | Always |
| **Carrier Locker** | Not shown | Only once WFMT has real fleet carrier locker data for the commander |
| **Cargo** | The ship's cargo capacity; Scarab 4 t, Scorpion 2 t; Rhino capacity unknown | While in a ship or SRV; hidden on foot. The label reads Ship Cargo, Scarab Cargo and so on |

Under the bars a small line names the last change (a pick-up or a transfer), followed by the reminder `Click Inventory Bar to Open Inventory Panel`. Clicking a bar opens the Inventory window.

### The Inventory window

Tabs: **Backpack**, **Ship Locker**, **Carrier Locker** (only once a carrier is confirmed), **Cargo** and **Settings** (see [Settings](#settings) below). Each of the first three lists **Resource**, **Category** and **Held**; the Cargo tab lists **Commodity** and **Tons** for the hold in use (ship or SRV).

- The **Filter** box at the top filters every tab at once. **Clear filter** empties it.
- **Refresh** redraws the window.
- The subtitle shows the current suit (`Suit: ...`).
- The Cargo tab opens with a bar and `tons / capacity` (or `capacity unknown`), then the commodities, most tons first. On foot it reads `Cargo - not applicable on foot`.
- The window remembers its size and position and follows the commander when the commander changes.
- A note on the Backpack tab reads `Not yet synced this session` if the game has not yet reported the backpack (for example after logging in already on foot). Looting, resupplying or disembarking refreshes it.
- Capacity colors change as a category fills: amber near the limit, red when full. The ship locker warning level is **90%** of 1,000 for a category. When a category crosses it, WFMT logs `⚠ Ship Locker <Assets|Goods|Data>: n/1000 — nearing capacity` and shows it on the overlay if pickup notifications are on (and the category is ticked under *Announce pickups for*). The same warning appears for a remote transfer through an Apex shuttle's Manage Items screen.

### Things worth knowing

- **The Carrier Locker comes from Frontier's servers, not the journal.** EDMC must be signed in to Frontier. The Carrier Locker tab is labeled `Carrier Locker — from CAPI, may lag 15–30 min`.
- **The backpack capacity is a built-in table, not a value the game reports.** WFMT looks up the suit and whether it has the *Extra Backpack Capacity* mod. The table does not include the engineering grade and has no figure for the Flight Suit (its bar shows a count with no limit). The Settings tab accepts the real number for each suit loadout.

| Suit | Assets | Goods | Data |
|---|---|---|---|
| Maverick (unmodded / extra capacity) | 60 / 120 | 40 / 80 | 20 / 40 |
| Artemis | 40 / 80 | 20 / 40 | 10 / 20 |
| Dominator | 20 / 40 | 10 / 20 | 10 / 20 |

### Worked examples

**Finding a single item.**

1. Click a bar on the Operations panel to open the Inventory window.
2. Enter part of the item's name in **Filter**. Every tab is filtered at once; the item appears on the **Backpack** or **Ship Locker** tab with its **Category** and the quantity held.
3. Press **Clear filter** to show everything again.

**Checking the hold before a haul.**

1. Click the **Cargo** bar, or open the Inventory window and select the **Cargo** tab.
2. The tab shows a bar and `tons / capacity`, then the commodities with the most tons first. On foot it reads `Cargo - not applicable on foot`.

**Correcting a backpack limit** (the built-in table does not include the engineering grade).

1. Open the **Inventory** window and select its **Settings** tab.
2. Under *Suit Backpack Capacity*, find the suit loadout and enter the number the game shows. If the tab reads `No suits recorded yet for this commander`, wear a suit in the game, then reopen the Settings tab.

### Settings

The pillage message, the sound, the announced categories and the suit backpack capacities are on the **Settings** tab of the Inventory window (press **Inventory** on the Operations panel). **Settings → WFMT → Operations → Inventory** only points there. The overlay switches are on **Settings → WFMT → Overlays → Inventory**.

| Setting | Where | Default |
|---|---|---|
| Show pillage notifications on the in-game overlay | Overlays → Inventory | Off |
| Pillage message (placeholders `{item}`, `{total}`) | Inventory window → Settings | `[{item}] pillaged! New Inventory Total: {total}` |
| Play a sound on pickup | Inventory window → Settings | Off |
| Show these inventory bars on the overlay (one tick per bar) | Overlays → Inventory | All off |
| Position on screen | Overlays → Overlay Placement | Top right area |
| Announce pickups for (Assets, Goods, Data) | Inventory window → Settings | All three |
| Suit Backpack Capacity (per suit loadout) | Inventory window → Settings | The built-in table. One row per suit loadout WFMT has seen for the commander, pre-filled with the unengineered default. Until a suit has been seen the tab reads `No suits recorded yet for this commander`; wear a suit in the game, then reopen Settings |
| Test pickup (button) | Overlays → Inventory | Sends a sample pickup to the overlay and reports whether the overlay could be reached, even while notifications are off |

On the Inventory Settings tab a tick saves when clicked and a box saves on Enter or when focus leaves it. A blank message restores the default. A capacity left blank, or set to the unengineered default, clears the entered number. A capacity that is not a number above 0 leaves the saved one. A suit worn after the window was opened appears as a new row. The overlay switches and the Test pickup button remain on the Overlays tab.

Unticking a category in *Announce pickups for* only mutes its notifications; the category is still counted. The overlay settings require a running overlay; see [Setting up the overlay](../OVERLAY_SETUP.md).

On Linux, the pickup sound requires `canberra-gtk-play` or `paplay`; see [Windows and Linux](platforms.md).

## Materials

Shows the engineering materials held: **Raw** (mined and scanned), **Manufactured** and **Encoded**, with each material's grade (1 very common to 5 very rare) and the maximum the game allows.

A collapsible **Engineering** row (named Materials before 1.4.1; first in Operations mode, which lists its sections A to Z) shows the following. Clicking its title folds it; the title reads **Engineering**, and everything below is in the section.

- A small table with a row for each type (**Raw**, **Manufactured**, **Encoded**, and **Other** for a material the table does not know) and two columns: **Held**, the pieces held, and **Session**, the pieces picked up this session. Only materials picked up from the world (`MaterialCollected`) count in **Session**; a trade, a mission reward, a discard or a craft does not. A session is one game login (the journal file it is played in), so the figure survives a restart of EDMC and starts again at the next login. Pick-ups made before EDMC started, in the same login, are read from the journal file and counted.
- The last pick-up or discard (`Last change: +3 Carbon (now 123)`).
- Which materials are **at the limit** (`At the limit: ...`).
- `As of your last session.` until the game has sent a fresh list.
- The number of engineers unlocked (`Engineers: 7 of 38 unlocked · 2 invited · 4 known`), once the game has listed them.
- A wishlist line when a wishlist exists.

Before the game has reported anything the row reads `Log in to see your materials.`; with an empty book it reads `No materials yet. The counts fill in when you are in the game.` (the engineers line still appears if the game has listed the engineers).

Three buttons sit in one row under the text: **Materials** opens the Materials window, **Blueprints** opens the Engineering window on its Blueprints tab, and **Engineers** opens the Engineering window on its Engineers tab. If the row would be wider than EDMC's window, the last button wraps to a second line.

**Procedure:**

1. Switch to Operations mode and open the **Engineering** row if it is folded. Log in to the game once so that WFMT has the full list.
2. Read the row: pieces held of each type, the last change, and anything at the limit.
3. Press **Materials** to search, filter and sort. Press **Find a trader** inside that window to find where to trade materials (see below).
4. To plan crafts, press **Blueprints** (see [Engineering](#engineering-blueprints-and-a-wishlist)).

**The window** lists every material held in the columns **Material**, **Type**, **Grade**, **Held**, **Limit** and **Room**. A help button repeats these notes. Text in **Search** must match every word in the name; **Type** and **Grade** filter the list; **Only what is at the limit** restricts it to materials at the limit; clicking a heading sorts.

**Source of the counts.**

- The game writes the whole list at login, then one entry for every change: pick-ups, discards, material trades, synthesis, engineering crafts, the Technology Broker, materials handed to an engineer and mission rewards. WFMT follows those entries.
- If EDMC starts in the middle of a session, WFMT takes EDMC's own running totals once.
- The counts are stored on the computer for the commander they belong to, and nothing is sent anywhere.

**Limits.** The limits are 300, 250, 200, 150 and 100 for grades 1 to 5. The names, types and grades are a built-in table of the game's 146 materials. A material the table does not know is still counted, with no grade or limit shown, until WFMT is updated.

**Find a trader.** A material trader exchanges materials within one category (a Raw trader trades Raw materials, and so on). **Find a trader** in the Materials window opens a window to find the closest one.

1. Select the **Type** (initially the type with the most materials at the limit), the search distance (**Within**: 50, 100, 250 or 500 ly, or any distance; 100 ly by default) and the smallest landing **Pad** required (**Any size**, **Medium or larger** or **Large only**).
2. Check the system in **Search from**. It starts as the current system; another system can be entered, or **Here** pressed.
3. Press **Find**.

Results:

- The window is titled **Material trader**. Its columns are **Station**, **System**, **Where** (in space or on a surface, with the distance from the arrival star), **Distance (ly)** and **Largest pad**, closest first.
- Double-clicking a row copies its system name for the galaxy map.
- Above the results is the quantity held of that type by grade, with the number of materials at the game's limit.

Pressing **Find** is the only action that goes online: it sends Spansh the system name and the type. The same search within two minutes is answered from memory.

**Example: trading away surplus Raw materials.**

1. The Engineering row reads `At the limit: ...` and lists several Raw materials.
2. Press **Materials**, then **Find a trader**. **Type** starts as the type with the most materials at the limit, here Raw.
3. Keep **Within** at 100 ly. Set **Pad** to **Large only** if the ship requires it.
4. Check **Search from** (initially the current system) and press **Find**.
5. In the **Material trader** window, the closest station is listed first; its **Where** column states whether it is in space or on a surface, with the distance from the arrival star.
6. Double-click the row to copy the system name and paste it into the galaxy map.
7. Check the rate at the trader itself: WFMT does not show rates.

## Engineering: blueprints and a wishlist

**Blueprints** on the Engineering row opens the Engineering window. It has five tabs: Blueprints, Wishlist, Ship planner, Upgrade planner and Engineers. **Refresh counts** (top right) re-reads the holdings used by the Have and Short figures.

**Procedure:**

1. Press **Blueprints** on the Engineering row. On the **Blueprints** tab, search for a module or an effect and select a blueprint.
2. Read its ingredients: how many one craft takes, how many are held and where each is found. Set **Crafts** to the number expected to be needed.
3. Press **Add to wishlist**. Repeat for each planned blueprint.
4. Open the **Wishlist** tab: it states which entries can be made now, what is short, and the shopping list for the whole wishlist.
5. Open the **Engineers** tab to see which engineers are unlocked and what unlocking the others requires. **Put their unlock on the wishlist** adds it.

**Example: two crafts of one blueprint.**

1. Press **Blueprints** and stay on the **Blueprints** tab. Enter the module name in **Search**; every word must match.
2. Select the blueprint. Beneath it appear who offers it, its effects and what **one craft** takes: each ingredient with the quantity needed, the quantity held and where it is found.
3. Set **Crafts** to 2 and press **Add to wishlist**.
4. Open the **Wishlist** tab. The entry states whether it **can be made now** and how many pieces it is **short**. The shopping list below lists each ingredient's need, have and short, with the shortfalls at the top, and where each is found.
5. On the Engineering row the wishlist line reads like `Wishlist: 3 blueprints, 2 can be made, 14 pieces short`.

The number of crafts is an estimate: the game rolls each result, so the actual number can differ. **Set crafts** changes it.

**Example: a whole build from EDSY.**

1. In EDSY, export the build as SLEF and copy it.
2. In the Engineering window open **Ship planner** and press **Paste from clipboard**. If the text holds several ships, select one in the **Ship** box.
3. Read the table: one row per engineered module. A pre-engineered module takes nothing, and anything the table does not cover reads **not counted**.
4. Tick **Subtract what my current ship already has** if the build is for the ship being flown. Modules already done read **already done**.
5. Set **Rolls per grade** (for example 3) and read the summary line for the totals.
6. Press **Add plan to wishlist**, then use the **Wishlist** tab for what can be made now and the shopping list.

**Blueprints.** Every engineering blueprint in the table (1,177: ship modules, Guardian items, Technology Broker unlocks, engineer unlocks, synthesis recipes, and Odyssey suit and weapon upgrades).

- The table has the columns **Module**, **Blueprint**, **Grade** and **Offered by**. **Search** matches the module, blueprint name, engineer, effect or an ingredient (every word must match), and **Module** narrows the list to one type; a count beside them states how many match.
- Selecting a blueprint shows who offers it, its effects, and what **one craft** takes: each ingredient with the quantity needed, the quantity held and where it is found.
- Set **Crafts** and press **Add to wishlist** (or double-click a row to add one craft).

**Wishlist.** The list of blueprints, with a number of crafts each, stored on the computer for the commander who made it.

- For each entry it states whether it **can be made now** and how many pieces it is **short**.
- Below is one **shopping list** for the whole wishlist: need, have, short and where each ingredient is found, with the shortfalls at the top.
- Each entry also states **who can do it**: an engineer who is unlocked, or a vendor or the synthesis panel (which need no unlocking), or "No engineer unlocked yet".
- The table has the columns **Blueprint**, **Crafts**, **Can be made now**, **Short** and **Who can do it**. The shopping list has **Ingredient**, **Kind**, **Need**, **Have**, **Short** and **Where it is found**.
- To change an entry, select it, enter the new number in **Crafts** and press **Set crafts**. **Remove** takes an entry off and **Clear list** empties the list. Each of the last two requires a second press of the button to confirm.
- The Engineering row shows a line such as `Wishlist: 3 blueprints, 2 can be made, 14 pieces short`.
- The wishlist holds 100 blueprints and 99 crafts of each.

**Ship planner.** Calculates what the engineering of a whole ship requires and adds it to the wishlist in one step.

1. In **EDSY** or **Coriolis**, design the ship with its engineering and export it as **SLEF** (the Ship Loadout Exchange Format). Other input methods:
   - Paste one `Loadout` line from the journal to plan the current ship.
   - Paste an **import link** (`https://coriolis.io/import?data=...` or `https://edsy.org/#/I=...`), such as one copied with the **Copy Coriolis link** or **Copy EDSY link** buttons below, or made by EDMC's own shipyard links.
   - The address a site shows for a build designed there (EDSY's `#/L=...`, Coriolis's `/outfit/...`) holds that site's own code, which WFMT cannot read, and short links would require a request to another website. For those, use **Export**, SLEF, instead.
2. In the Engineering window open the **Ship planner** tab and press **Paste from clipboard**, or paste into the box and press **Read loadout**. If the text holds several ships, select one in the **Ship** box.
3. The table has the columns **Slot**, **Module**, **Engineering**, **Level**, **Experimental** and **Counted?** (and **In storage**, below), one row per engineered module. Selecting a row shows the detail. **Clear** empties the box and the table.
   - A module with no engineering is omitted.
   - A **pre-engineered** module (supplied that way by Frontier) is labeled as such and takes nothing.
   - Anything WFMT's table does not cover reads **not counted** with the reason.
4. Optionally tick **Subtract what my current ship already has**. WFMT reads the newest journal for the ship being flown and omits what it already holds.
   - For a module in the same slot with the same blueprint, the grades up to its level are done (only higher ones are planned), and an experimental effect it already carries is done.
   - A module that is completely done reads **already done**.
   - Subtraction applies only when the build is the same kind of ship as the one flown (otherwise the line under the table says so).
   - It assumes the build is intended for the ship being flown; two ships of one kind cannot be distinguished.
   - A different blueprint in that slot is not subtracted from.
   - If no ship is found, the status line says so and nothing is subtracted.
5. The **In storage** column states whether the module is in Module Storage.
   - **Yes**: a stored module of the same kind (the same module, size and class) with the engineering the build requires, at that level or higher.
   - **Partly**: a stored module of the same kind with other engineering, or none. Selecting the row shows what it has and where it is.
   - Only storage counts. A module fitted to a ship is not listed, and the plan is not reduced by what is in storage.
   - The list is as current as the last visit to Module Storage (see the Stored modules tab), and it does not state which experimental effect a stored module carries.
6. Set **Rolls per grade**. To reach level 5 the game applies grades 1 to 5 in order. The number of rolls per grade depends on the game's dice, which the journal does not report, so the number to plan for (1 to 10) is entered. An experimental effect is one craft. The summary line shows the totals.
7. Press **Add plan to wishlist**. The same blueprint on several modules is added together.
   - The wishlist holds 100 blueprints and 99 crafts of each. If the plan would exceed either, **nothing is added** and the message states why.
   - Then use the **Wishlist** tab for what can be made now and the shopping list.

**This build on a site.** With a ship read and selected:

- **Copy Coriolis link** and **Copy EDSY link** copy a link that opens that build on the site.
- **Open in Coriolis** and **Open in EDSY** open it in the browser.
- The link carries the whole loadout (ship, name, modules and engineering) in the address, so the site needs nothing else. When the link is opened or shared, that site and every recipient can see the build.
- Coriolis refuses a link of 2,083 characters or more, so for a very large engineered build WFMT reports this instead of opening it; the EDSY link is the alternative.
- WFMT sends nothing itself: the browser in which **Open** is pressed makes the request.
- Links use the sites' main addresses (not their beta pages). Whether a site accepts a link is determined by the site.

Nothing is sent anywhere by the planner: the text comes from the user and all calculation is done on the computer.

Limits:

- The number of rolls required is not known.
- It cannot determine which of two ships of one kind a build is intended for.
- It covers only module types in the blueprint table.

The journal's names for blueprints and effects are matched to the table's from public lists (see [Technical](../TECHNICAL.md#ship-engineering-planner-ship_planpy-ship_plan_tabpy-journal_blueprintspy)); a name that is not recognized is shown as **not counted**.

**Upgrade planner.** Puts what it takes to upgrade an Odyssey suit or weapon, and to fit its modifications, onto the wishlist.

1. Open the **Upgrade planner** tab and select the **Item**: the Artemis, Dominator or Maverick suit, or one of the Karma, Manticore and TK weapons.
   - Alternatively press **Read my gear**: WFMT reads the suits and weapons owned from the journal (the loadouts the game lists when logging in on foot, plus any upgrade since) and offers them in the box beside it.
   - Selecting one fills in the item, its current class and the modifications it already carries.
2. Set **Class now** and the wanted class (**Wanted**; 1 to 5). The table lists each step, from the current class to the wanted class, with the materials and the credits. A line under the table gives the total.
3. Optionally select up to four **Modifications**. An item read from the journal that already carries some has fewer slots left, and the ones it has are not offered again.
   - The boxes offer the modifications the table has for the item.
   - A weapon modification marked with a family in brackets, such as "(Kinematic kinetic)", is offered only for that family (Karma is kinetic, Manticore is plasma, TK is laser).
   - The table does not state whether the game offers every unmarked modification for every weapon.
4. Press **Add to wishlist**. Each class step and each modification is added once, all or nothing (the limits are the wishlist's: 100 blueprints, 99 crafts). The Wishlist tab then shows the shopping list: what is held in the ship locker and what is short.

**Costs counted and not counted:**

- **The materials** are the game's current ones.
  - The schematic, the item's family item and Manufacturing Instructions (a Health Monitor for a suit) take 1, 2, 4 and 5 for classes 2 to 5.
  - The item's other two materials take 2, 5, 9 and 12.
  - These counts were read from upgrade events in journals for the Karma AR-50, C-44 and L-6, the Manticore Tormentor and Executioner, and the Maverick, Artemis and Dominator suits.
  - The counts were the same for every item, so they are used for the rest (the Karma P-15, Manticore Intimidator and Oppressor, and the three TK lasers); those have not been confirmed by an upgrade of their own.
- **The credits** are a unit for the item times 1, 3, 6 and 10 for classes 2 to 5 (the Karma AR-50 costs 625,000 for class 2, so 12,500,000 for classes 2 to 5 together).
  - They are shown only for the eight items listed above.
  - For the others the tab states that the credits are **not recorded**, and still plans the materials.
- **A modification's engineer fee** is not in the table and is not counted.
- **Read my gear** shows what the game last listed, not a live inventory.
  - A suit or weapon bought, sold or changed since the last time the commander logged in on foot may not appear.
  - A session that never went on foot has no loadouts, so WFMT looks back through the newest journals.
  - It reads only the commander of the newest journal.
  - A modification the planner has no name for is mentioned in the status line and omitted.
- The planner does not preview an item's stats.

**Engineers.** All 38 engineers (ship and on-foot, including the Colonia ones).

- **Show** box: above the table, it selects **Both**, **Bubble** (the 30 engineers in the human bubble) or **Colonia** (the 8 in the Colonia region, about 22,000 ly away: Baltanos, Eleanor Bresa, Etienne Dorn, Marsha Hicks, Mel Brandon, Petra Olmanova, Rosa Dayette and Yi Shen). The count beside it reads like `8 of 38 engineers`, and the choice is remembered. An engineer the location table lacks (a name known only to the journal) appears under **Both** only.
- **Row colors:** an unlocked engineer's row is green, one known or invited (in progress) is yellow, and one the game has not listed as known (not available yet) is red. The colors are the same in every theme. Before the game has listed any engineers no row is colored.
- **Each row** has the columns **Engineer**, **You are** (the standing: Known, Invited, or Unlocked with the rank), **Works on** (the module types the engineer works on, each with the top grade, such as `Frame Shift Drive 5, Thrusters 3`; an on-foot engineer shows `Suit, Weapon`), **Where** (base, system and planet, with "on foot" or "permit needed") and **Next step** (toward unlocking).
- **Next step column:** until an engineer is unlocked, it gives the one next action. That is the engineer's own next step, or `First <engineer>:` and that engineer's step when another engineer must be dealt with first (Lei Cheung is found through The Dweller). A find step that only reads "Common knowledge" is skipped. When the step is the engineer's own and the unlock is items, it adds the quantity held (such as 200 Gold for Lei Cheung); those items can go on the wishlist. Unlocked engineers are listed first.
- **Selecting an engineer** shows the full details under the table. The pane has a large title with the standing (colored: green, yellow or red), then headed sections in bold type: **Location** (base, system, body, region and how to get there), **Works on** (each module type with the top grade offered and any experimental effects, or the suit and weapon upgrades of an on-foot engineer), **Path to unlock**, **What to hand over**, **Raising your rank with them** (a general line, marked community-reported, until an engineer's own text is confirmed) and **Notes**. Each step of the path is numbered, with its label in bold and the detail after it. The pane follows the text size setting (the A- and A+ in the window's footer).
  - **The engineer's system is a link** (underlined, in the subtitle and in the System row): clicking opens that system's page on Inara in the browser (only on click).
  - **To copy the text:** select part of it with the mouse and press **Ctrl+C**; press **Ctrl+A** then **Ctrl+C** for all of it; right-click for **Copy selection**, **Copy all** and **Select all**; or press **Copy details** under the table to copy the whole pane as plain text.
- The pane contains:
  - **The path to unlock the engineer**, as numbered steps in order: find them, hold the permit if one is needed, earn the invitation and unlock them. A step the game reports as done is marked `[done]`: *Known* marks the find, *Invited* marks the find and the invitation, and *Unlocked* marks everything. The game does not report permits or what an invitation requires, so those stay open until the engineer is invited or unlocked.
  - **The standing on the invitation requirements**, for the requirements the game's journal totals. A rank or a lifetime figure shows beside the step, for example `(you have Competent: needs Expert)` or `(you have 304 markets: met)`. It covers combat, trade and exploration ranks, the Empire and Federation Navy ranks, the greatest distance from the start, markets and black markets traded with, tons mined, combat bonds and bounty vouchers. The game writes these at login, so the figures are as old as the last login (a promotion shows at once). If EDMC was started after login, WFMT reads the newest ones from the journal files once, in the background. The note is information: the step is marked `[done]` only by the engineer's standing. A requirement the journal does not total (a faction's standing, missions of one kind, items sold to a bartender) shows the table's words with no check.
  - **The engineers to deal with first**, when one is found through another. Tiana Fortune's path starts with Liz Ryder, then Hera Tani, and reads `takes 3 engineers, in this order`. An engineer already unlocked on the way is omitted.
  - **On-foot engineers:** what is handed to an on-foot engineer is for learning of the *next* one, so it appears as a step on the next engineer's path ("To learn of Kit Fowler, give Domino Green the items: Provide 5 doses of Push."). Yarden Bond, Oden Geiger, Uma Laszlo and Yi Shen end their chains and hand nothing over, so they have no unlock step of their own. Yi Shen's path has one hand-in step for each of the three engineers he is found through.
  - How to gain standing with the engineer.
  - Whether the engineer works on foot (no ranks: every upgrade is offered once the engineer has been met).
- **Verification needed:** for an engineer whose invitation requirement WFMT cannot check against the journal (a faction's standing, a kind of mission, a data sale and similar), the details end with a note saying so, until the engineer is invited or unlocked. The tables are community lists; **Report engineer data** opens a prefilled GitHub form (the engineer, the standing WFMT has, the Environment box) in which the in-game Engineers panel text can be entered. Nothing is sent until the form is submitted there. See [Telling us what the game shows](reporting-problems.md#telling-us-what-the-game-shows-game-data).
- **What to hand over** lists each item the engineer requires with the quantity needed and held (a commodity is not counted from the journal), how it is obtained (buy at a market, mine it, trade engineering materials, collect at a Thargoid or Guardian site, collect at a planetary settlement on foot, scan ships or data points, or a mission reward or rescue) and where the data states it is found. Where WFMT has a finder for that kind it offers it under the item:
  - **Find where to buy** (items bought at a market) opens the Source commodities lookup for that commodity: the nearest stations with it in stock, nearest, best nearby and cheapest. It is the same Spansh lookup as the Mission mode's, so it requires the **Enable Spansh trade lookups** tick in Settings (Trade) and acts only when **Find sources** is pressed there.
  - **Find a material trader** (engineering materials) opens the Material trader finder.
  - **Look up the nearest Thargoid site** (Sensor Fragments and other Thargoid items) finds the nearest Thargoid site in Canonn's list from the current position (always a Thargoid site, never a Guardian one, whether or not it is logged in Codex Completionist). The answer, the system and the distance with Canonn's note on it, appears in the line at the foot of the window, and the system name is copied for the galaxy map. It requires the game to be running and a known position (a jump to a system or a load into one); otherwise the line instructs to log in to the game. It also requires **Include Thargoid sites** on (Settings → WFMT → Exploration → POI Reference, on by default); if it is off, the line states where to turn it on.
  - Items mined, from settlements, from scanning or from missions have no finder; the text states where they come from.
- **How to get it** is a written guide for the engineer, when one exists: the steps in order, where, hazards, and a note on each item. A guide is marked **Community-reported and not yet confirmed in the game** until it has been checked in the game, and then reads **Confirmed in the game** with the date. Chloe Sedesi and Professor Palin have one (collecting Sensor Fragments from a crashed Thargoid ship with the SRV), still community-reported; an engineer without one states so. **Report engineer data** accepts corrections.
- **Buttons:** **Show their blueprints** lists what the engineer offers, **Put their unlock on the wishlist** adds what unlocking requires, **Copy details** copies the selected engineer's details as plain text, and **Report engineer data** opens a prefilled GitHub form.
- **Source of standings:** the game's engineer list, sent at login and whenever one changes (including a rank-up), and stored on the computer for each commander.

**How "can be made now" is determined.** Entries are evaluated in list order, as they would be crafted: an entry that can be made takes what it needs, and the entries below it see only what is left. An entry that cannot be made takes nothing, so it does not consume materials a later entry could use.

**Number of crafts.** A blueprint's ingredients are what one craft takes. How many crafts reach the wanted result depends on the game's rolls, which no tool can know; the expected number is entered manually.

**What is counted:**

- **Ship materials** (Raw, Manufactured, Encoded): from the Materials counts above.
- **On-foot items** (Odyssey components, goods and data): from the **ship locker**, as the Inventory tracks it. The backpack and a fleet carrier's locker are not counted: items to be used must be moved into the ship locker. WFMT counts the ship locker as available and shows a carrier's stock separately.
- **Trade goods** (a Technology Broker unlock takes commodities): shown as needed but **not counted**. An entry that needs them reads "Yes, not counting ..." rather than guessing.

## Ship Builds

Stores ship builds designed on sites such as Coriolis, EDSY or Spansh, one list per commander. WFMT does not design ships; it stores the link and name entered.

**To save a build:**

1. Design the build on the chosen site.
2. Click **Ships** (manage ship builds) in the **Ship Builds** row of the WFMT panel. The row is collapsible, and its text shows the number of builds.
3. Click **Add build** (the highlighted button).
4. Fill in the **Add Ship Build** form. **Name**, **Ship**, **Site** and **Link** are required. **Ship** starts as the ship being flown; **Role** is the purpose of the build, such as "PvE Exploration"; **Notes** is free text.
5. Select the **Site** (**Coriolis**, **EDSY (E:D Shipyard)**, **Spansh** or **Other**; another name can also be typed) and paste the build's web address, which must start with `http://` or `https://`, into **Link**.
6. Click **Save** (or **Cancel**).

**Example:** name `Krait Phantom explorer`, role `Exploration`, site `Coriolis`, and the link from the browser's address bar.

**Retrieving a build.**

1. Press **Ships** in the **Ship Builds** row. The **Builds** tab lists the builds with their **Name**, **Ship**, **Role**, **Site** and **Updated**.
2. Select `Krait Phantom explorer`, then press **Open Link** to open it in the browser, or **Copy Link** to copy the address.
3. If the site's address changed, press **Edit build**, paste the new link and save.

**Edit build** and **Delete build** act on the selected build.

### Stored modules

The **Stored modules** tab of the Ship Builds window lists the modules in Module Storage and where they are. For each it shows:

- **Module** and **Class**,
- **Engineering** (blueprint and grade, or `-`),
- **Where** (the station and system),
- **Transfer** (the cost and time),
- **Marks** (hot modules and modules still in transit).

Text in the **Filter** box narrows the list (a count beside it reads `Showing N of M; filter to narrow` for a long list); every word must match something in the row (a name, a blueprint, a system, `hot`, `in transit`). The list is kept per commander, and the line above it states when it was last written.

How it stays current:

- The game writes the full list each time **Module Storage** is opened at a station.
- Between visits WFMT follows the modules stored and taken out.
- When EDMC starts it reads the newest journals to catch up on events that occurred while it was closed.
- Until Module Storage has been opened once, the tab states so and shows nothing.

A module fitted to a ship is part of that ship's loadout and is not listed here.

## Combat Record

Counts the commander's kills and deaths, split by ship, for the session being played and added up over every session. One record is kept per commander.

**What is counted:**

| Figure | Counted from |
|---|---|
| **Kills** | A ship destroyed for a bounty (`Bounty`) or a conflict zone or faction bond (`FactionKillBond`), and an on-foot target that paid a bounty |
| **PvP kills** | Another commander destroyed (`PVPKill`). They are counted apart from kills |
| **Deaths** | Each time the ship, SRV or suit was destroyed (`Died`), on the vessel that was lost |
| **K/D** | Kills and PvP kills divided by deaths. A dash shows while there has been no death |
| **Rewards (cr)** | The credits the bounties and bonds paid. This is what the game said was owed, not profit |

**To see the record:**

1. Open the **Combat Record** row of the WFMT panel. The table shows **Kills**, **Deaths** and **K/D** for **This session** (the login being played) and **All time**. **Kills** there includes PvP kills, as K/D does; the window lists them apart. While the journals are being read, the **All time** row reads `...`.
2. Press **Combat**. The window has three tabs:
   - **This session**: tiles for **Kills**, **PvP kills**, **Deaths**, **K/D** and **Rewards (cr)**, and a table with a row for each ship.
   - **All time**: the same, over every session.
   - **Sessions**: one row per session, newest first, with the start time (the session being played reads `(this session)`). Selecting a row shows that session's ships below.
3. Click a column heading to sort a table.

**Ships.** Each ship is a row with its **Ship** (the kind, such as `Federal Corvette`) and **Name** (the ship's own name and ident, such as `Wayward Star [WS-01]`). A ship is known by its kind and the game's number for it, so two ships of one kind are two rows, and renaming a ship does not start a new row. The **SRV** and **On foot** have rows of their own. Kills of on-foot targets are always on the **On foot** row.

**A session** is one game login: the journal file it was played in. A logout to the menu and back is the same session. A session appears in the list once it has a kill or a death. The last 300 sessions are listed; the totals and the per-ship figures cover all of them.

**Earlier play.** When EDMC starts, WFMT reads the commander's journals in the background: all of them the first time, so play from before WFMT counts, and afterwards only the files that changed. An event is never counted twice. **Rebuild from journals** (in the window) clears this commander's record and reads every journal again; it gives the same figures when all the journals are still there.

Nothing is sent anywhere. The record is the file `combat_record.json`, kept per commander and included in the data backup. There is no Settings tab.

## What the game does and doesn't tell us, and how to work around it

WFMT uses only what Elite Dangerous writes to its journal files, plus what Frontier's servers give a signed-in EDMC (for the Carrier Locker). Where WFMT cannot be certain, it states so. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| Expectation | What the game provides | Action |
|---|---|---|
| Screenshots cropped exactly | The crop rectangles are **fixed measurements** and may need adjusting if Frontier changes the HUD | Turn the crop off, or report it, if a crop is wrong after a game update |
| The screenshot timer presses any button | It can press **keyboard** keys only. macOS is not supported for key simulation, and Linux on Wayland without XWayland is not either (conversion and cropping still work) | Bind a keyboard key to the screenshot control |
| Screenshots always save | Windows Controlled Folder Access or antivirus can block file access. The error message states this | Allow EDMC through, or choose another save folder |
| The backpack capacity is reported | The game does not report it. WFMT uses a **built-in table** by suit and the Extra Backpack Capacity mod. The table does not include the engineering grade and has no figure for the Flight Suit | Enter the real number for each suit loadout in the Inventory settings |
| The Backpack is known at login | After a login already on foot, the game has not yet reported it (the tab reads `Not yet synced this session`) | Loot, resupply or disembark to refresh it |
| The Carrier Locker is live | It comes from **Frontier's servers**, not the journal. EDMC must be signed in to Frontier. The Carrier Locker tab is labeled `Carrier Locker — from CAPI, may lag 15–30 min` | Sign EDMC in. The locker is hidden until real data arrives |
| The Rhino's cargo capacity | No journal field for the fitted capacity is known to WFMT, so the bar shows the count with no limit | Read the tons, not a percentage |
| Materials are correct as soon as EDMC starts | The game writes the full list only at **login**. Between logins WFMT follows each change, and after a restart it shows the counts from the last session until the next login list arrives (the window states this) | Log in to the game, or start EDMC before the game |
| Materials that could not be carried are counted | At the limit, the game discards what cannot be carried. WFMT never counts above the limit | None; the login list corrects any difference |
| Which engineer or blueprint needs a material | Not shown. This page counts what is held; it does not know what the material is needed for | Use a site such as Inara or EDSY for what a blueprint takes |
| The blueprint table is current | The recipes are a table bundled with WFMT, supplemented with the suit and weapon upgrade costs seen in upgrade events and with synthesis recipes and Thargoid-war and chip materials. The table is not Frontier's own list. A blueprint or material added to the game since may be missing, and a recipe Frontier changed may be out of date. Experimental effects are entered in the table as one-craft entries | Check the in-game recipe before spending rare materials, and report a difference |
| Which upgrades each Colonia engineer offers | The places, unlock steps and the suit and weapon upgrades each Colonia on-foot engineer (Baltanos, Eleanor Bresa, Rosa Dayette and Yi Shen) offers are bundled with WFMT; other sources may differ, and none is Frontier's own list. Yi Shen's unlock is the three sets of items handed to the other three | Check what an engineer offers in the game's Engineers panel before spending items, and report a difference |
| Engineer places and steps are current | They come from a table bundled with WFMT and can drift when the game changes | Check the engineer's requirements in the game's Engineers panel |
| What unlocking an engineer takes is complete | The table lists the **materials or goods** an engineer requires. An invitation can require more (a rank, a visit, a referral), which the table does not list | Check the engineer's requirements in the game's Engineers panel |
| Materials match the game after every pick-up | The journal does not report every gain. Counts can differ from the game until the next login list | The next login list corrects the counts |
| The Engineering window knows how many crafts are needed | The game rolls the result of each craft; nothing in the journal states how many will be required | Enter the expected number of crafts |
| On-foot upgrades count the backpack | The wishlist counts the **ship locker** only. Whether the game also draws on the backpack is not confirmed | Stow carried items in the ship locker, or check the count in the game |
| The trader finder states what a trade would give | It finds the stations. The rates a trader offers are not in the journal or in Spansh's data, so WFMT does not show or calculate a rate | Check the rate at the trader before trading |
| The trader finder is current | The list is Spansh's, from player reports: a station can have lost its trader or be closed to the commander (a permit, a faction state) | Check the station on arrival; the `Pad` column is the largest pad Spansh knows |
| The stored modules list is live | The game writes the whole list only when **Module Storage** is opened at a station. In between, WFMT applies the store and retrieve events the game reports, so a change the game does not report with those events (finished transfers move modules between stations) shows only at the next visit. The tab states when the last visit was | Open Module Storage at a station to refresh the list |
| Modules on ships kept in storage are listed | The game reports a stored ship by its type, not by what is fitted to it, so those modules are not in the list. A module fitted to the ship being flown is in its loadout, not in storage | Check the ship's loadout in the game |
| Transfer cost and time are current | They are the game's figures at the last visit to Module Storage and are not updated until the next one. A module that is not at a station reads `In transit` and may have no station or cost | Open Module Storage again for current figures |
| Every station has a name | The list gives a system and a market number for each module, and a station's name only when WFMT has seen it in the journals (the station where Module Storage was opened, or one docked at). Other stations appear as `System (market 123456)` | Look the market up on a site such as Inara or EDSM |
| A module swapped out of a ship shows its engineering | When a swap puts a module into storage, the game does not report how that module was engineered, so the Engineering column shows `?` until the next visit to Module Storage | Open Module Storage to read it |
| Every kill is counted | Only the kills the game writes as a bounty, a faction or conflict-zone bond or a PvP kill. A kill that pays nothing and is not a PvP kill (for example, a ship that was not wanted, outside a conflict zone) is not in the journal, so it is not counted | None; the figure is the kills the game recorded |
| Capital ship kills are separate | A capital ship bond (`CapShipBond`) is not counted, to avoid counting a kill twice | None |
| Every death is on the right vessel | WFMT follows the vessel from the events that change it. A login made while on foot or in the SRV is not reported as such, so a death or kill before the next change of vessel can appear on the ship | None; the row is a best estimate for that session |
| Journals from before WFMT are counted | The journals still on the disk are. Journals that were deleted, or play on another computer, are not | Point EDMC's journal folder at the full set |
| Ship Builds are checked | WFMT stores only the link and name entered. It does not read or check the build | Keep the link current if the site changes |
