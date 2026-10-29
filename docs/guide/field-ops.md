# Field Ops

Field Ops holds the on-foot and housekeeping tools: screenshots, your inventory, your engineering materials (with the blueprints, wishlist, ship planner and engineers) and saved ship builds.
(Colonization has its own mode, with its own page: [Colonization](colonization.md).)

**Where this comes from:**

- Screenshots, your backpack and ship locker, and ship loadouts come from the journal (or from EDMC's own state, which it rebuilds from the journal).
- The journal doesn't give your backpack's capacity, so WFMT uses a built-in table.
- The Carrier Locker isn't in the journal at all: it comes from Frontier's servers through a signed-in EDMC.
- See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

**On this page:**

- [How to](#how-to)
- [Screenshots](#screenshots)
- [Inventory](#inventory)
- [Materials](#materials)
- [Engineering](#engineering-blueprints-and-a-wishlist) (including the [Ship planner](#engineering-blueprints-and-a-wishlist))
- [Ship Builds](#ship-builds)
- [What the game does and doesn't tell us](#what-the-game-does-and-doesnt-tell-us-and-how-to-work-around-it)

## How to

The most common tasks, step by step. Each one links to the section with the full detail.

**Set up screenshots** (details: [Screenshots](#screenshots))

1. Open **Settings → WFMT → Field Ops → Screenshots**.
2. Check **Screenshot Directory** is the folder where the game saves its screenshots (use **Browse…** if not).
3. Choose a **Converted Directory** for the PNG copies, and pick a **Filename Mask** from the drop-down.
4. Optionally tick **Delete original file after conversion**.
5. Take a screenshot in the game. The status line on the Field Ops panel (**OPS**) shows the converted file's name.

**See your backpack and cargo** (details: [Inventory](#inventory))

1. Switch to Field Ops mode (**OPS**). The Inventory bars show the Backpack, the Ship Locker and, while you are in a ship or SRV, the Cargo.
2. Click any bar to open the Inventory window.
3. Pick the **Backpack**, **Ship Locker** or **Cargo** tab. Type in **Filter** to narrow every tab at once.

**Check materials for a blueprint** (details: [Engineering](#engineering-blueprints-and-a-wishlist))

1. Press **BLUEPRINTS** on the Materials row to open the Engineering window.
2. On the **Blueprints** tab, type the module or effect in **Search** and pick the blueprint. Its ingredients show what one craft takes and how many you hold.
3. Set **Crafts**, then press **Add to wishlist**.
4. Open the **Wishlist** tab to see whether it **can be made now** and what you are **short** of.

**Find a material trader** (details: [Materials](#materials))

1. Press **MATERIALS**, then **Find a trader** in the Materials window.
2. Pick the **Type**, **Within** distance and **Pad** size, and check **Search from**.
3. Press **Find**. The **Material trader** window lists the closest stations first.

**Save a ship build** (details: [Ship Builds](#ship-builds))

1. Design the build on Coriolis, EDSY or Spansh and copy its address from your browser.
2. Press **SHIPS** in the **Ship Builds** row, then **Add**.
3. Fill in **Name**, **Ship**, **Site** and **Link**, then press **Save**.

**Plan a whole ship's engineering** (details: the Ship planner in [Engineering](#engineering-blueprints-and-a-wishlist))

1. Export the build from EDSY or Coriolis as SLEF and copy it.
2. In the Engineering window open **Ship planner** and press **Paste from clipboard**.
3. Set **Rolls per grade**, then press **Add plan to wishlist**.

## Screenshots

Converts Elite's screenshots to PNG automatically, with an optional crop to just the relevant HUD panel.

**How to use it:** nothing to do. Take a screenshot in the game as usual and WFMT converts it when the game's journal reports it.

**On the panel** (Field Ops mode, **OPS**):

- A status line. It reads `Waiting for a screenshot…` until one is taken, then the converted file's name (cut to 40 characters). **Click the status line to open the folder** the last screenshot was saved in.
- The **clock icon** to its right turns the auto-capture timer on and off (see below). It is hidden when the timer cannot work on your system or when you turn the icon off in Settings.
- **Click to expand** / **Click to collapse** shows or hides the thumbnails. They always start collapsed when EDMC starts.
- Expanded, you see the newest screenshot as a thumbnail (and, when a crop was made, the cropped copy beside it), then **Recent - click to preview**: the eight screenshots before it, in rows of four. Click any thumbnail to open a larger preview.
- The preview window is view-only. It scales the image to fit the window (never larger than the image itself), remembers its size and has an **Open Folder** button for the folder the file was saved in, a **Close** button and a help button.

**What happens to each screenshot.**

1. The game saves its own image file in its screenshots folder and writes a `Screenshot` entry to the journal.
2. WFMT finds the file, converts it to PNG in the **Converted Directory**, and names it from the **Filename Mask** (the system, the body or station, your commander name, a five-digit number or the date and time).
3. If **Delete original file after conversion** is ticked, the game's original is deleted after a 60 second grace period so that other tools can see it first.
4. If the panel that was open when you pressed the key has a crop rectangle, a cropped copy is made as well: the target panel, the comms panel, the role panel or the left-hand (systems) panel. A high-resolution screenshot is never cropped. The rectangles are fixed measurements for a 1920 by 1080 screen, scaled to the screenshot's size and centered on wider screens.
5. The status line, the thumbnails and (if you turned it on) the on-screen **Screenshot saved** message update.

The status line also reports problems: `Screenshot not found - check Screenshot Directory in Settings` (when the file is in none of the known folders), and `Conversion failed: <reason>`. If the file is not in the folder you set but WFMT finds it in a known fallback folder, it corrects the Screenshot Directory by itself (and moves the Converted Directory with it when that was still the default).

**The auto-capture timer.** The clock icon presses the game's screenshot key (F10) for you, on a timer, so you can leave it running while you work.

- Click the icon to start it (`Auto-capture enabled`) and again to stop it (`Auto-capture disabled`). It starts off every time EDMC starts and stops by itself when the game shuts down or you die (`Auto-capture stopped`).
- It only presses the key while Elite is the window in front; otherwise the status line says `Auto-capture paused (Elite not focused)`.
- It presses once every **poll interval** (1 second by default, 0.2 second at the least).
- It can only press the key on systems that support it (Windows, and Linux under X11 or XWayland with `xdotool`).
- **Thargoid scans.** When you collect a Thargoid signal's data, WFMT presses the key once for you (if *Automatically capture a screenshot when scanning a Thargoid signal* is on) and crops the copy to the bottom-left quarter of the screen, where the scan result appears. The same crop is used for the next screenshot you take while the game's Thargoid encounter music is playing.

**Settings → WFMT → Field Ops → Screenshots:**

- **Screenshot Directory**: where the game saves its screenshots. **Browse…** picks a folder.
- **Converted Directory**: where the PNG copies go. **Browse…** picks a folder.
- **Delete original file after conversion** (off by default).
- *Include WFMT's built-in overlay in the converted screenshot (the game's own capture never shows an overlay)* (off by default; Windows, needs the built-in overlay chosen under Settings → WFMT → Overlays).
  - The game's own screenshot never shows an overlay, so WFMT draws the cards that were on screen when you pressed the key onto the converted copy.
  - A failure here never loses the screenshot.
- **Group converted files into a per-system subfolder** (off by default).
- **Show the auto-capture timer icon on the main window** (on by default).
- **Filename Mask**: a drop-down of presets, from `SYSTEM(BODY)_NNNNN.png` (the default) through `SYSTEM(CMDR)_DATE.png`, `BODY(CMDR)_NNNNN.png`, `SYSTEM BODY (CMDR) NNNNN.png` to `DATE_SYSTEM_BODY_CMDR.png`. `NNNNN` is a running five-digit number, `DATE` the date and time.
- **Auto-capture poll interval (seconds)** (1; the minimum is 0.2).
- **Use high-resolution capture on the auto-timer (Solo play only)** (off by default). The timer then holds Left Alt with F10, which the game honors in Solo only.
- **Automatically capture a screenshot when scanning a Thargoid signal** (on by default).
- The optional **Show a notification on the in-game overlay when a screenshot is saved** is set on **Settings → WFMT → Overlays → Screenshots** (off by default; needs an overlay; has a **Test Overlay** button).

**Worked example: a photo set of one system.** You want every screenshot from a system in its own folder, with the file named by system and body.

1. Open **Settings → WFMT → Field Ops → Screenshots**.
2. Tick **Group converted files into a per-system subfolder**.
3. Leave **Filename Mask** on `SYSTEM(BODY)_NNNNN.png`.
4. Take a screenshot at a planet. WFMT converts it and the status line shows the new file name (cut to 40 characters). Click the status line to open the folder it was saved in.

**Worked example: auto-capture while you scan.** You are mapping a system and want a screenshot every few seconds.

1. With Elite in front, click the clock icon on the Field Ops panel. The status line says `Auto-capture enabled`.
2. WFMT presses F10 once per poll interval (1 second unless you changed **Auto-capture poll interval (seconds)**).
3. If you alt-tab away, the status line says `Auto-capture paused (Elite not focused)` and no key is pressed.
4. Click the icon again for `Auto-capture disabled`. The timer also stops by itself if the game shuts down or you die.

*On Linux, the auto-timer needs `xdotool`, and a Flatpak EDMC needs the screenshots permission. See
[WFMT on Linux](linux.md). On Windows, OneDrive-redirected folders are handled automatically.*

## Inventory

Tracks your Odyssey **microresources** and your cargo hold as capacity bars. For microresources it follows the
game's three categories: **Assets**, **Goods** and **Data** (the journal calls these Component, Item and Data).

**On the panel:** a status line (`Awaiting Odyssey loot…` until something happens), then up to four bars. Each shows
`count/capacity`, or just the count where WFMT doesn't know the capacity.

| Bar | Capacity | When it appears |
|---|---|---|
| **Backpack** | From your suit, if known (see below) | Always |
| **Ship Locker** | 1,000 each of Assets, Goods and Data (3,000 in all) | Always |
| **Carrier Locker** | Not shown | Only once WFMT has real fleet carrier locker data for this commander |
| **Cargo** | Your ship's cargo capacity; Scarab 4 t, Scorpion 2 t; Rhino capacity unknown | While you are in a ship or SRV. Hidden while on foot. The label reads Ship Cargo, Scarab Cargo and so on |

Under the bars a small line names the last change (a pick-up or a transfer), and a reminder reads `Click Inventory Bar to Open Inventory Panel`. **Click any bar** to open the Inventory window.

### The Inventory window

Tabs: **Backpack**, **Ship Locker**, **Carrier Locker** (only once a carrier is confirmed) and **Cargo**. Each of the
first three lists **Resource**, **Category** and **Held**; the Cargo tab lists **Commodity** and **Tons** for the
hold you are using (ship or SRV).

- The **Filter** box at the top filters every tab at once. **Clear** empties it.
- **Refresh** redraws the window.
- The subtitle shows your current suit (`Suit: ...`).
- The Cargo tab opens with a bar and `tons / capacity` (or `capacity unknown`), then the commodities, most tons first. On foot it says `Cargo - not applicable on foot`.
- The window remembers its size and position and follows the commander if you switch.
- A note on the Backpack tab says `Not yet synced this session` if the game hasn't yet reported your backpack
  (for example if you logged in already on foot). Loot, resupply or disembark to refresh it.
- Capacity colors change as a category fills: amber near the limit, red when full. The ship locker warning level
  is **90%** of 1,000 for a category. When a category crosses it, WFMT logs `Ship Locker <Assets|Goods|Data>: n/1000 - nearing capacity` and shows it on the overlay if pickup notifications are on (and the category is ticked under *Announce pickups for*). The same warning appears when you transfer remotely through an Apex shuttle's Manage Items screen.

### Things worth knowing

- **Carrier Locker comes from Frontier's servers, not the journal.** EDMC must be signed in to Frontier, and the
  data can **lag the game by 15 to 30 minutes**.
- **Backpack capacity is a built-in table, not something the game reports.** WFMT looks up your suit and whether it
  has the *Extra Backpack Capacity* mod. The table cannot see engineering grade, and has no figure for the Flight
  Suit (so its bar shows a count with no limit). The Settings tab lets you type in the real number for each of your
  suit loadouts.

| Suit | Assets | Goods | Data |
|---|---|---|---|
| Maverick (unmodded / extra capacity) | 60 / 120 | 40 / 80 | 20 / 40 |
| Artemis | 40 / 80 | 20 / 40 | 10 / 20 |
| Dominator | 20 / 40 | 10 / 20 | 10 / 20 |

### Worked examples

**Finding a single item.** You remember picking up a data item but not where it is.

1. Click any bar on the Field Ops panel to open the Inventory window.
2. Type part of its name in **Filter**. Every tab is filtered at once, so you see it on the **Backpack** or **Ship Locker** tab, with its **Category** and how many you hold.
3. Press **Clear** to see everything again.

**Checking your hold before a haul.** You are in your ship and want to know how many tons are free.

1. Click the **Cargo** bar, or open the Inventory window and pick the **Cargo** tab.
2. The tab opens with a bar and `tons / capacity`, then the commodities with the most tons first. On foot it says `Cargo - not applicable on foot`.

**Correcting a backpack limit.** The Backpack bar shows a limit that differs from the number you see in the game, because the built-in table cannot see engineering grade.

1. Open **Settings → WFMT → Field Ops → Inventory**.
2. Find your suit loadout under *Suit Backpack Capacity* and type the number the game shows. If the tab says `No suits recorded yet for this commander`, wear a suit in the game, then reopen Settings.

### Settings (Settings → WFMT → Field Ops → Inventory)

| Setting | Default |
|---|---|
| Show pillage notifications on the in-game overlay | Off |
| Pillage message (placeholders `{item}`, `{total}`) | `[{item}] pillaged! New Inventory Total: {total}` |
| Play a sound on pickup | Off |
| Show these inventory bars on the overlay (one tick per bar) | All off |
| Where it sits on screen | Top right area (set on Settings → WFMT → Overlays → Overlay Placement) |
| Announce pickups for (Assets, Goods, Data) | All three |
| Suit Backpack Capacity (per suit loadout) | The built-in table. One row per suit loadout WFMT has seen for the commander, pre-filled with the unengineered default; change the number to what you see in the game. Until a suit has been seen the tab says `No suits recorded yet for this commander` - wear a suit in the game, then reopen Settings |
| Test pickup (button, on the Overlays tab) | Sends a sample pickup to the overlay and says whether the overlay could be reached, even while notifications are off |

Unticking a category in *Announce pickups for* only mutes its notifications. It is still counted.
The overlay settings are on **Settings → WFMT → Overlays → Inventory** and need an overlay running; see
[Setting up the overlay](../OVERLAY_SETUP.md).

On Linux, the pickup sound needs `canberra-gtk-play` or `paplay`; see [Windows and Linux](platforms.md).

## Materials

What you hold of each engineering material: **Raw** (mined and scanned), **Manufactured** and **Encoded**, with each one's grade (1 very common to 5 very rare) and the most the game lets you hold of it.

A collapsible **Materials** row shows (click its title to fold it; the folded title carries a total such as `- 1,234 held`):

- the pieces held of each type (`Raw 400 · Manufactured 350 · Encoded 300`, plus `Other` for a material the table does not know),
- the last pick-up or discard ("Last: +3 Carbon (now 123)"),
- which materials are **at the limit** (`At the limit: ...`), so you know that collecting more is wasted,
- `As of your last session.` until the game has sent a fresh list,
- a wishlist line when you have one.

Before the game has told WFMT anything the row says `Log in to see your materials.`, and with an empty book `No materials yet. The counts fill in when you are in the game.`

**MATERIALS** opens the window, and **BLUEPRINTS** (under it) opens the Engineering window.

**To use it:**
1. Switch to Field Ops mode (**OPS**) and open the **Materials** row if it is folded. Log in to the game once, so WFMT has the full list.
2. Read the row: pieces held of each type, the last change, and anything at the limit.
3. Press **MATERIALS** to search, filter and sort. To find where to swap materials, press **Find a trader** inside that window (see below).
4. To plan crafts, press **BLUEPRINTS** (see [Engineering](#engineering-blueprints-and-a-wishlist)).

**The window** lists every material you hold in the columns **Material**, **Type**, **Grade**, **Held**, **Limit** and **Room**. A help button repeats these notes. Type in **Search** (every word must be in
the name), pick a **Type** or **Grade**, tick **Only what is at the limit**, and click a heading to sort.

**Where the counts come from.**

- The game writes your whole list when you log in, and then one entry for every change: pick-ups, discards, material trades, synthesis, engineering crafts, the Technology Broker, materials handed to an engineer and mission rewards. WFMT follows those.
- If you start EDMC in the middle of a session, WFMT takes EDMC's own running totals once, so the counts are right straight away.
- The counts are kept on your computer for the commander they belong to, and nothing is sent anywhere.

**The limits** are 300, 250, 200, 150 and 100 for grades 1 to 5. The names, types and grades are a built-in table of the game's 146 materials;
a new material the table does not know is still counted, with no grade or limit shown, until WFMT is updated.

**Find a trader.** A material trader swaps materials within one category (a Raw trader trades Raw materials, and so on). **Find a trader** in the Materials window opens a window to look for the closest one.

1. Pick the **Type** (it starts as the type with the most materials at the limit), how far to look (**Within**: 50, 100, 250 or 500 ly, or any distance; 100 ly by default) and the smallest landing **Pad** you need (**Any size**, **Medium or larger** or **Large only**).
2. Check the system to **Search from**. It starts as the one you are in; type another to plan ahead, or press **Here**.
3. Press **Find**.

The results:

- The window is called **Material trader**. Its columns are **Station**, **System**, **Where** (in space or on a surface, with its distance from the arrival star), **Distance (ly)** and **Largest pad**, closest first.
- Double-click a row to copy its system name for the galaxy map.
- Above the results is what you hold of that type by grade, with how many materials are at the game's limit, so you can see what is worth swapping.

Pressing **Find** is the only thing that goes online: it sends Spansh the system name and the type. The same search within two minutes is answered from memory.

**Worked example: swapping away surplus Raw materials.** Your Materials row says `At the limit: ...` and lists several Raw materials.

1. Press **MATERIALS**, then **Find a trader**. **Type** starts as the type with the most materials at the limit, here Raw.
2. Leave **Within** at 100 ly. If your ship needs it, set **Pad** to **Large only**.
3. Check **Search from** (it starts as your current system) and press **Find**.
4. In the **Material trader** window, read the closest station first: its **Where** column says whether it is in space or on a surface, with the distance from the arrival star. Above the list, the grades you hold of that type show what is worth swapping.
5. Double-click the row to copy the system name, then paste it into the galaxy map.
6. Check the rate at the trader itself: WFMT does not show rates.

## Engineering: blueprints and a wishlist

**BLUEPRINTS** on the Materials row opens the Engineering window. It has five tabs: Blueprints, Wishlist, Ship planner, Upgrade planner and Engineers. **Refresh counts** (top right) re-reads what you hold, which the Have and Short figures use.

**To use it:**
1. Press **BLUEPRINTS** on the Materials row. On the **Blueprints** tab, search for a module or an effect and pick a blueprint.
2. Read its ingredients: how many one craft takes, how many you hold and where each is found. Set **Crafts** to the number you expect to need.
3. Press **Add to wishlist**. Repeat for everything you plan to build.
4. Open the **Wishlist** tab: it says which entries can be made now, what you are short of, and the shopping list for all of it.
5. Open the **Engineers** tab to see who you have unlocked and what unlocking the others takes. **Put their unlock on the wishlist** adds it.

**Worked example: planning two crafts.** You want to know whether you can build a blueprint twice.

1. Press **BLUEPRINTS** and stay on the **Blueprints** tab. Type the module name in **Search**; every word you type must match.
2. Pick the blueprint. Under it you see who offers it, its effects and what **one craft** takes: each ingredient with how many you need, how many you hold and where it is found.
3. Set **Crafts** to 2 and press **Add to wishlist**.
4. Open the **Wishlist** tab. The entry says whether it **can be made now** and how many pieces it is **short**. The shopping list below lists each ingredient's need, have and short, with what is short at the top, and where it is found.
5. On the Materials row the wishlist line reads like `Wishlist: 3 blueprints, 2 can be made, 14 pieces short`.

Remember that two crafts is your estimate: the game rolls each result, so the real number can differ. Change it with **Set crafts**.

**Worked example: a whole build from EDSY.** You designed an engineered ship on EDSY.

1. In EDSY, export the build as SLEF and copy it.
2. In the Engineering window open **Ship planner** and press **Paste from clipboard**. If the text holds several ships, pick one in the **Ship** box.
3. Read the table: one row per engineered module. A pre-engineered module takes nothing, and anything the table does not cover says **not counted**.
4. Tick **Subtract what my current ship already has** if the build is for the ship you are flying. Modules already done say **already done**.
5. Set **Rolls per grade** (for example 3) and read the summary line for the totals.
6. Press **Add plan to wishlist**, then use the **Wishlist** tab for what you can make now and the shopping list.

**Blueprints.** Every engineering blueprint in the table (about 1,180: ship modules, Guardian items, Technology Broker unlocks, engineer unlocks, synthesis recipes, and Odyssey suit and weapon upgrades).

- The table has the columns **Module**, **Blueprint**, **Grade** and **Offered by**. **Search** matches the module, blueprint name, engineer, effect or an ingredient (every word you type must match), and **Module** narrows to one type; a count beside them says how many match.
- Pick a blueprint to see who offers it, its effects, and what **one craft** takes: each ingredient with how many you need, how many you hold, and where it is found.
- Set **Crafts** and press **Add to wishlist** (or double-click a row to add one craft).

**Wishlist.** Your list of blueprints, with a number of crafts each, kept on your computer for the commander who made it.

- For each entry it says whether it **can be made now** and how many pieces it is **short**.
- Below is one **shopping list** for the whole wishlist: need, have, short and where each ingredient is found, with what is short at the top.
- Each entry also says **who can do it**: an engineer you have unlocked, or a vendor or the synthesis panel (which need no unlocking), or "No engineer unlocked yet".
- The table has the columns **Blueprint**, **Crafts**, **Can be made now**, **Short** and **Who can do it**. The shopping list has **Ingredient**, **Kind**, **Need**, **Have**, **Short** and **Where it is found**.
- Select an entry, type the new number in **Crafts** and press **Set crafts**; **Remove** takes it off and **Clear list** empties the list. Each of the last two asks you to press the button a second time to confirm.
- The Materials row shows a line such as `Wishlist: 3 blueprints, 2 can be made, 14 pieces short`.

**Ship planner.** Work out what a whole ship's engineering takes, and put it on the wishlist in one step.

1. In **EDSY** or **Coriolis**, design the ship with its engineering and export it as **SLEF** (the Ship Loadout Exchange Format). Other ways in:
   - Paste one `Loadout` line from your journal to plan your current ship.
   - Paste an **import link** (`https://coriolis.io/import?data=...` or `https://edsy.org/#/I=...`), such as one copied with the **Coriolis link** or **EDSY link** buttons below, or made by EDMC's own shipyard links.
   - The address a site shows for a build you designed there (EDSY's `#/L=...`, Coriolis's `/outfit/...`) holds that site's own code, which WFMT cannot read, and short links would need a request to another website. For those, use **Export**, SLEF, instead.
2. In the Engineering window open the **Ship planner** tab and press **Paste from clipboard**, or paste into the box and press **Read loadout**. If the text holds several ships, pick one in the **Ship** box.
3. The table has the columns **Slot**, **Module**, **Engineering**, **Level**, **Experimental** and **Counted?** (and **In storage**, below), one row per engineered module. Select a row for the detail. **Clear** empties the box and the table.
   - A module with no engineering is left out.
   - A **pre-engineered** module (it comes that way from Frontier) says so and takes nothing.
   - Anything WFMT's table does not cover says **not counted** and why.
4. Optionally tick **Subtract what my current ship already has**. WFMT reads your newest journal for the ship you are flying and leaves out what it already holds.
   - For a module in the same slot with the same blueprint, the grades up to its level are done (only higher ones are planned), and an experimental effect it already carries is done.
   - A module that is completely done says **already done**.
   - It only subtracts when the build is the same kind of ship as yours (otherwise the line under the table says so).
   - It assumes the build is meant for the ship you are flying: two ships of one kind cannot be told apart.
   - A different blueprint in that slot is not subtracted from.
   - If it finds no ship, the status line says so and nothing is subtracted.
5. The **In storage** column says whether you already have the module in Module Storage.
   - **Yes**: a stored module of the same kind (the same module, size and class) with the engineering the build wants, at that level or higher.
   - **Partly**: a stored module of the same kind with other engineering, or none. Select the row to see what it has and where it is.
   - Only storage counts. A module fitted to a ship is not listed, and the plan is not reduced by what you hold in storage.
   - The list is as fresh as your last visit to Module Storage (see the Stored modules tab), and it does not say which experimental effect a stored module carries.
6. Set **Rolls per grade**. To reach level 5 the game applies grades 1 to 5 in order, and how many rolls each grade takes depends on the game's dice, which the journal cannot tell, so you say how many to plan for (1 to 10). An experimental effect is one craft. The summary line shows the totals.
7. Press **Add plan to wishlist**. The same blueprint on several modules is added together.
   - The wishlist holds 100 blueprints and 99 crafts of each. If the plan would pass either, **nothing is added** and the message says why.
   - Then use the **Wishlist** tab for what you can make now and the shopping list.

**This build on a site.** With a ship read and chosen:

- **Coriolis link** and **EDSY link** copy a link that opens that build on the site.
- **Open in Coriolis** and **Open in EDSY** open it in your browser.
- The link carries the whole loadout (ship, name, modules and engineering) in the address, so the site needs nothing else. When you open or share it, that site and anyone you send it to can see the build.
- Coriolis refuses a link of 2,083 characters or more, so for a very large engineered build WFMT says so instead of opening it, and the EDSY link is the one to use.
- WFMT sends nothing itself: the browser you press **Open** in makes the request.
- Links use the sites' main addresses (not their beta pages), and whether a site accepts a link is up to the site.

Nothing is sent anywhere: the text comes from you and everything is worked out on your computer.

What it cannot do:

- It does not know how many rolls you need.
- It cannot tell which of two ships of one kind a build is meant for.
- It only covers module types in the blueprint table.

The journal's names for blueprints and effects are matched to the table's from public lists (see [Technical](../TECHNICAL.md#ship-engineering-planner-ship_planpy-ship_plan_tabpy-journal_blueprintspy)); a name it does not know is shown as **not counted**.

**Upgrade planner.** What it takes to upgrade an Odyssey suit or weapon, and to fit its modifications, onto the wishlist.

1. Open the **Upgrade planner** tab and pick the **Item**: the Artemis, Dominator or Maverick suit, or one of the Karma, Manticore and TK weapons.
   - Or press **Read my gear**: WFMT reads the suits and weapons you own from your journal (the loadouts the game lists when you log in on foot, plus any upgrade since) and offers them in the box beside it.
   - Picking one fills in the item, the class it is now and the modifications it already carries.
2. Set the **Class now** and the class you **Wanted** (1 to 5). The table lists each step, from the class you have to the class you want, with the materials it takes and the credits. A line under the table gives the total.
3. Optionally pick up to four **Modifications**. An item you read from the journal that already carries some has fewer slots left, and the ones it has are not offered again.
   - The boxes offer those the table has for the item.
   - A weapon modification marked with a family in brackets, such as "(Kinematic kinetic)", is only offered for that family (Karma is kinetic, Manticore is plasma, TK is laser).
   - The table does not say whether the game offers every unmarked modification for every weapon.
4. Press **Add to wishlist**. Each class step and each modification goes on the list once, all or nothing (the limits are the wishlist's: 100 blueprints, 99 crafts). The Wishlist tab then shows the shopping list: what you hold in your ship locker and what you are short of.

**What the costs are, and are not:**

- **The materials** are the game's current ones.
  - The schematic, the item's family item and Manufacturing Instructions (a Health Monitor for a suit) take 1, 2, 4 and 5 for classes 2 to 5.
  - The item's other two materials take 2, 5, 9 and 12.
  - They were read from real upgrade events in the journals of play, for the Karma AR-50, C-44 and L-6, the Manticore Tormentor and Executioner, and the Maverick, Artemis and Dominator suits.
  - The counts were the same for every item, so they are used for the rest (the Karma P-15, Manticore Intimidator and Oppressor, and the three TK lasers), but those have not been confirmed by an upgrade of their own.
- **The credits** are a unit for the item times 1, 3, 6 and 10 for classes 2 to 5 (the Karma AR-50 costs 625,000 for class 2, so 12,500,000 for classes 2 to 5 together).
  - They are shown only for the eight items listed above.
  - For the others the tab says the credits are **not recorded**, and still plans the materials.
- **A modification's engineer fee** is not in the table, so it is not counted.
- **Read my gear** is what the game last listed, not a live inventory.
  - A suit or weapon you bought, sold or changed since the last time you logged in on foot may not show.
  - A session that never went on foot has no loadouts, so WFMT looks back through your newest journals.
  - It reads only the commander of your newest journal.
  - A modification the planner has no name for is mentioned in the status line and left out.
- The planner does not preview an item's stats.

**Engineers.** All 38 engineers (ship and on-foot, the Colonia ones included).

- **Show** box: above the table, it picks **Both**, **Bubble** (the 30 engineers in the human bubble) or **Colonia** (the 8 in the Colonia region, about 22,000 ly away: Baltanos, Eleanor Bresa, Etienne Dorn, Marsha Hicks, Mel Brandon, Petra Olmanova, Rosa Dayette and Yi Shen). The count beside it reads like `8 of 38 engineers`, and WFMT remembers your choice. An engineer the location table lacks (a name only your journal knows) shows under **Both** only.
- **Each row** has where you stand (Known, Invited, or Unlocked with their rank), how many blueprints they offer, **where they are** (base, system and planet, with "on foot" or "permit needed") and what unlocking them asks for.
- **Last column:** until an engineer is unlocked, it gives what gets you invited and what unlocks them, in words. For an engineer whose unlock is items (such as Yi Shen's three sets) it shows how much of it you hold; those items can go on the wishlist. Unlocked engineers come first.
- **Select an engineer** for the full details under the table:
  - how to find them, who introduces them, what to do to be invited and to unlock them, and how to gain standing with them,
  - whether they work on foot (no ranks: every upgrade is offered once you have met them),
  - any known quirk (for example, Terra Velasquez's meeting requirement is reported bugged: Covert Theft missions may not count, Covert Heist missions do).
- **Net profit line:** a line below the table gives the net profit that opens each grade for a ship engineer: grade 2 at 500,000 cr, grade 3 at 2,000,000 cr, grade 4 at 8,000,000 cr and grade 5 at 16,000,000 cr (sold at their workshop).
- **Buttons:** **Show their blueprints** lists what they offer, and **Put their unlock on the wishlist** adds what unlocking them takes.
- **Where standings come from:** the game's engineer list, sent at login and whenever one changes (including a rank-up), and kept on your computer for each commander.

**How "can be made now" works.** Entries are weighed in list order, as you would craft them: an entry that can be made takes what it needs, and the
ones below it only see what is left. An entry that cannot be made takes nothing, so it does not use up materials a later entry could use.

**Crafts are up to you.** A blueprint's ingredients are what one craft takes. How many crafts it takes to reach the result you want depends on the
game's rolls, which no tool can know; set the number you expect.

**What is counted:**
- **Ship materials** (Raw, Manufactured, Encoded): from the Materials counts above.
- **On-foot items** (Odyssey components, goods and data): from your **ship locker**, as the Inventory tracks it. The backpack and a fleet carrier's
  locker are not counted: move what you want to use into the ship locker. WFMT counts the ship locker as available and shows a carrier's
  stock apart; Frontier does not say whether that is right, so it is on the list to confirm in the game.
- **Trade goods** (a Technology Broker unlock takes commodities): shown as needed but **not counted**, and an entry that needs them says "Yes, not
  counting ..." rather than guessing.

## Ship Builds

A place to keep ship builds you've designed on sites like Coriolis, EDSY or Spansh, one list per commander. WFMT
doesn't design ships itself. This just helps you find a build again later.

**To save a build:**

1. Design your build on whichever site you like.
2. Click **SHIPS** (manage ship builds) in the **Ship Builds** row of the WFMT panel. The row is collapsible, and its text shows how many builds you have.
3. Click **Add** (the highlighted button).
4. Fill in the **Add Ship Build** form. **Name**, **Ship**, **Site** and **Link** are required. **Ship** starts as the ship you are flying; **Role** is what the build is for, such as "PvE Exploration"; **Notes** is free text.
5. Pick the **Site** (**Coriolis**, **EDSY (E:D Shipyard)**, **Spansh** or **Other**) and paste the build's web address, which must start with `http://` or `https://`, into **Link**.
6. Click **Save** (or **Cancel**).

**Example:** name `Krait Phantom explorer`, role `Exploration`, site `Coriolis`, and paste the link from your
browser's address bar.

**Worked example: finding a build again.** Months later you want your exploration build.

1. Press **SHIPS** in the **Ship Builds** row. The **Builds** tab lists your builds with their **Name**, **Ship**, **Role**, **Site** and **Updated**.
2. Select `Krait Phantom explorer`, then press **Open Link** to open it in your browser, or **Copy Link** to copy the address.
3. If the site's address changed, press **Edit**, paste the new link and save.

**To use it later:** the **Builds** tab lists your builds with the columns **Name**, **Ship**, **Role**, **Site** and **Updated**. Select one and use **Open Link** to open it in your browser, or **Copy Link** to copy
the address. **Edit** and **Delete** work on the selected build in the same way.

### Stored modules

The **Stored modules** tab of the Ship Builds window lists the modules you have in Module Storage and where they are. For each it shows:

- **Module** and **Class**,
- **Engineering** (blueprint and grade, or `-`),
- **Where** (the station and system),
- **Transfer** (the cost and time),
- **Marks** (hot modules and modules still in transit).

Type in the **Filter** box to narrow the list (a count beside it reads `Showing N of M; filter to narrow` for a long list); every word you type has to match something in the row (a name, a blueprint, a system, `hot`, `in transit`). The list is kept per commander, and the line above it says when it was last written.

How it stays current:

- The game writes the full list each time you open **Module Storage** at a station.
- Between visits WFMT follows the modules you store and take out.
- When EDMC starts it reads your newest journals to catch up on what happened while it was closed.
- Until you have opened Module Storage once, the tab says so and shows nothing.

A module that is fitted to a ship is part of that ship's loadout and is not listed here.

## What the game does and doesn't tell us, and how to work around it

WFMT, like every third-party tool, only knows what Elite Dangerous writes to its journal files. It adds what Frontier's servers give a signed-in EDMC (for the Carrier Locker) and works around the rest. Where it can't be sure, WFMT says so rather than guess quietly. See [How WFMT knows what it knows](README.md#how-wfmt-knows-what-it-knows).

| What you might expect | What the game gives | What to do |
|---|---|---|
| Screenshots cropped perfectly | The crop rectangles are **fixed measurements** and may need adjusting if Frontier changes the HUD. | Turn the crop off, or report it, if a crop is wrong after a game update. |
| The screenshot timer to press any button | It can only press **keyboard** keys. macOS isn't supported for key simulation, and Linux on Wayland without XWayland isn't either (conversion and cropping still work). | Bind a keyboard key to the screenshot control. |
| Screenshots to always save | Windows Controlled Folder Access or antivirus can block file access. The error message says so. | Allow EDMC through, or choose another save folder. |
| Your backpack capacity to be reported | The game doesn't report it. WFMT uses a **built-in table** by suit and the Extra Backpack Capacity mod. It can't see engineering grade and has no figure for the Flight Suit. | Type the real number for each suit loadout in the Inventory settings. |
| The inventory to show after restarting EDMC mid-game | EDMC does not replay the session to plugins, but it rebuilds its own state from the journal. WFMT syncs the backpack and ship locker from that state when EDMC starts. | If a bar still shows nothing, loot, resupply or disembark to refresh it. This relies on EDMC's state and has not been checked against every EDMC version. |
| The Backpack to be known at login | If you log in already on foot, the game hasn't yet reported it (the tab says `Not yet synced this session`). | Loot, resupply or disembark to refresh it. |
| The Carrier Locker to be live | It comes from **Frontier's servers**, not the journal. EDMC must be signed in to Frontier, and the data can **lag the game by 15 to 30 minutes**. | Sign EDMC in, and allow time after changes. The locker is hidden until real data arrives. |
| The Rhino's cargo capacity | Not confirmed against a real journal entry, so the bar shows the count with no limit. | Read the tons, not a percentage. |
| Your materials to be right as soon as EDMC starts | The game writes the full list only when you **log in**. Between logins WFMT follows each change, and after a restart it shows the counts from your last session until the next login list arrives (the window says so). | Log in to the game, or start EDMC before the game. |
| Materials you were not able to carry to be counted | When you are at the limit, the game discards what you cannot carry. WFMT never counts above the limit. | Nothing; the login list corrects any difference. |
| Which engineer or blueprint needs a material | Not shown yet. This page counts what you hold; it does not know what you need it for. | Use a site such as Inara or EDSY for what a blueprint takes. |
| The blueprint table to be current | The recipes are a table bundled with WFMT, supplemented with the suit and weapon upgrade costs seen in real upgrade events and with synthesis recipes and Thargoid-war and chip materials. The table is not Frontier's own list. A blueprint or material added to the game since may be missing, and a recipe Frontier changed may be out of date.<br><br>Checked against 4,391 real blueprint crafts from the journals of one commander, every one used exactly the materials the table lists for that grade. Experimental effects are in the table as one-craft entries, but they were **not** part of that check (the journals held 143 further crafts that used them), so their recipes are less certain. | Check the in-game recipe before you spend rare materials, and report a difference. |
| Which upgrades each Colonia engineer offers to be certain | The blueprint table lacks the four **Colonia on-foot engineers** (Baltanos, Eleanor Bresa, Rosa Dayette and Yi Shen). Their places, unlock steps and the suit and weapon upgrades each offers are bundled with WFMT separately; other sources may differ, and none is Frontier's own list. Yi Shen's unlock is the three sets of items handed to the other three. | Check what an engineer offers in the game's Engineers panel before you spend items on it, and report a difference. |
| Engineer places and steps to be current | They come from a table bundled with WFMT and can drift when the game changes. Yarden Bond's meeting requirement says 5 Smear campaign plans, while the blueprint table's "Unlock" row for him asks for 8 to be handed over: the sources disagree on that step. | Check the engineer's requirements in the game's Engineers panel. |
| What unlocking an engineer takes to be complete | The table lists the **materials or goods** an engineer asks for. An invitation can ask for more (a rank, a visit, a referral), which it does not list. | Check the engineer's requirements in the game's Engineers panel. |
| Your materials to match the game after every pick-up | The journal reports almost every gain, but not all of them: replaying real journals, WFMT's counts matched the game's next login list 97% of the time when the game was restarted within ten minutes (737 of 761), and 93% over all gaps (the rest are mostly play on another computer). The misses that remain are exactly 5 more of several materials in the game with no event in between. | The next login list corrects the counts. |
| The Engineering window to know how many crafts you need | The game rolls the result of each craft; nothing in the journal says how many it will take. | Set the number of crafts you expect. |
| On-foot upgrades to count your backpack | The wishlist counts the **ship locker** only. Whether the game also draws on the backpack is not confirmed. | Stow what you carry into the ship locker (or just check the count in the game). |
| The trader finder to say what a trade would give you | It finds the stations. The rates a trader offers are not in the journal or in Spansh's data, so WFMT does not show or work out a rate. | Check the rate at the trader before you swap. |
| The trader finder to be current | The list is Spansh's, from what players have reported: a station can have lost its trader or be closed to you (a permit, a faction state). | Check the station when you arrive; the `Pad` column is the largest pad Spansh knows. |
| The stored modules list to be live | The game writes the whole list only when you open **Module Storage** at a station. In between, WFMT applies the store and retrieve events the game reports, so a change the game does not report with those events (in checks against real journals a few modules appeared or left storage that way, and finished transfers move modules between stations) shows only at the next visit. The tab says when the last visit was. | Open Module Storage at a station to refresh the list. |
| Modules on ships kept in storage to be listed | The game reports a stored ship by its type, not by what is fitted to it, so those modules are not in the list. A module fitted to the ship you fly is in its loadout, not in storage. | Check the ship's loadout in the game. |
| Transfer cost and time to be current | They are the game's figures at the last visit to Module Storage and are not updated until the next one. A module that is not at a station shows `In transit` and may have no station or cost. | Open Module Storage again for current figures. |
| Every station to have a name | The list gives a system and a market number for each module, and a station's name only when WFMT has seen it in your own journals (the station you opened Module Storage at, or one you have docked at). Other stations show as `System (market 123456)`. | Look the market up on a site such as Inara or EDSM. |
| A module swapped out of a ship to show its engineering | When a swap puts a module into storage, the game does not say how that module was engineered, so the Engineering column shows `?` until the next visit to Module Storage. | Open Module Storage to read it. |
| Ship Builds to be checked | WFMT only stores the link and name you give it. It doesn't read or check the build. | Keep your link current if the site changes. |

