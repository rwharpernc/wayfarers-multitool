# Engineer data to gather

This page says what information is needed to finish the Engineers tab, and how to gather and record it. It is for whoever is checking the data in the game. The aim is a short written guide for each engineer, for what the journal cannot tell WFMT: how to get the items an engineer asks for when they cannot simply be bought, and what the game says an invitation needs when WFMT cannot check it.

## Why this is needed

- Engineers' locations, invitation requirements and unlock items come from a community table, not from the game. Where the journal records a number (a rank, a lifetime figure) WFMT checks the requirement against it; for the other engineers (the **Verification needed** note) it cannot.
- Some unlock items are not sold anywhere: Sensor Fragments (a Thargoid material), items from planetary settlements (on foot), data from scanning ships, and rewards for missions or rescues. WFMT sorts every item by how it is got and offers the finder that fits (market lookup, Material trader, nearest Thargoid site), but for the rest it can only say, in a few words, where the item comes from.
- A written guide fixes that. The Engineers tab shows a guide in its own section (**How to get it**) once one exists, marked as community-reported until it has been confirmed in the game.

## What to gather

Work through an engineer at a time. Write plain notes as you go; wording can be tidied afterwards.

**A. What the game says about the invitation and the unlock.**
1. Open the in-game **Engineers** panel (Commander screen, Engineers) and select the engineer.
2. Copy, word for word, what it says an invitation needs, and what it says unlocking needs. Note your standing with them (Unknown, Known, Invited, Unlocked and the rank).
3. Note whether the wording matches the Engineers tab's **Path to unlock** and **Raising your rank with them**. Anything that differs or is missing is what to report.
4. If the requirement is one WFMT checks (a rank or a lifetime figure), compare the **you have ...** note with the figure the game shows (Commander screen, Statistics).

**B. How to get an item that cannot be bought.** For each such item:
1. What the item is called in the game's inventory (and in the journal, if you can see the event: `MaterialCollected` for a ship material, `CollectItems` or `BackpackChange` for an on-foot item, `MissionCompleted` for a reward).
2. The method that worked, step by step, in the order done: where to go (system and body, and coordinates or a description of the place), what to bring (ship modules, an SRV, on-foot equipment), what to do there.
3. How many you got per pickup, and how many you needed in total, so the guide can say how many pickups are left.
4. Whether the place can be farmed again (does it respawn, and what makes it respawn), and how long a round took.
5. What to watch out for: damage (for example corrosion from carrying something), hostile ships or defenders, a limit on how many you can carry, anything that wastes the item.
6. Any other way to get it (a different location, a mission, a trade) and whether it was better or worse.
7. Whether you did it yourself in the game. The guide stays marked "community-reported" until you can say yes.

**C. How to get an item that can be bought.** Name a market where it is in stock and what it cost per ton, or say it was mined and where. WFMT's Where to buy lookup finds markets itself; this is a check that it finds the right ones.

**D. Where the engineer is.** Confirm the base, the system and the body, and whether a permit is needed or the engineer is on foot. For the Colonia engineers, note the distance from Sol as the galaxy map shows it.

## How to record it

Send what you gather one of two ways:
- **A player or tester:** select the engineer on the Engineers tab and press **Report engineer data**. It opens a GitHub form with the engineer and the standing WFMT has filled in; write what the game shows under **What the game shows** and anything WFMT got wrong under **What WFMT showed that is wrong or missing**. Nothing is sent until you submit it there. **Settings, General, Help, Report game data** opens the same form blank, for anything else.
- **The maintainer writing a guide:** add an entry to `plugin/engineer_guides_data.py`:

```python
GUIDES["chloe sedesi"] = Guide(
    summary="One line saying what to do.",
    steps=("First step.", "Second step."),
    where="Where it happens, in a few words.",
    system="A system name (the pane links it to Inara).",
    cautions=("Something to watch out for.",),
    items=(("Item name", "How to get just that item."),),
    verified=False,       # True only once it has been done and confirmed in the game
    updated="",           # the date of that check, as YYYY-MM-DD
)
```

The key is the engineer's name in lower case, without a nickname. Leave `verified` False until the steps have been followed in the game; the pane then says "Community-reported and not yet confirmed in the game" and asks for corrections. Use WFMT's own words and no outside links.

## Per engineer

The table lists every engineer with what to gather (the letters are the sections above). It is a snapshot made from the data; it is not updated by itself.

| Engineer | Area | Base | Invitation | Unlock items (how they are got) | To gather |
|---|---|---|---|---|---|
| Baltanos | Colonia, on foot | The Divine Apparatus, Deriso 3 A | Verification needed | none | A: exact invitation wording and how you met it; D: location and permit |
| Bill Turner | Bubble, permit | Turner Metallics Inc, Alioth 4 A | Verification needed | Bromellite x50 (mine it) | A: exact invitation wording and how you met it; B: where you mined them; D: location and permit |
| Broo Tarquin | Bubble | Broo's Legacy, Muang 5 A | Checked against your journal | Fujin Tea x50 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Chloe Sedesi | Bubble | Cinder Dock, Shenve A 6 | Checked against your journal | Sensor Fragment x25 (collect at a Thargoid or Guardian site) | B: how to get the items; D: location and permit |
| Colonel Bris Dekker | Bubble, permit | Dekker's Yard, Sol Iapetus | Verification needed | none | A: exact invitation wording and how you met it; D: location and permit |
| Didi Vatermann | Bubble | Vatermann LLC, Leesti 1 A | Checked against your journal | Lavian Brandy x50 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Domino Green | Bubble, on foot | The Jackrabbit, Orishis 4 | Verification needed | none | A: exact invitation wording and how you met it; D: location and permit |
| Eleanor Bresa | Colonia, on foot | Bresa Modifications, Desy 7 A | Verification needed | none | A: exact invitation wording and how you met it; D: location and permit |
| Elvira Martuuk | Bubble | Long Sight Base, Khun 5 | Checked against your journal | Soontill Relics x3 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Etienne Dorn | Colonia | Kraken's Retreat, Los A 2 B | Checked against your journal | Occupied Escape Pod x25 (a mission reward or a rescue) | B: how to get the items; D: location and permit |
| Felicity Farseer | Bubble | Farseer Inc, Deciat 6 A | Checked against your journal | Meta-alloys x1 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Hera Tani | Bubble | The Jet's Hole, Kuwemaki A 3 A | Checked against your journal | Kamitra Cigars x50 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Hero Ferrari | Bubble, on foot | Nevermore Terrace, Siris 5 C | Verification needed | none | A: exact invitation wording and how you met it; D: location and permit |
| Jude Navarro | Bubble, on foot | Marshall's Drift, Aurai 1 A | Verification needed | none | A: exact invitation wording and how you met it; D: location and permit |
| Juri Ishmaak | Bubble | Pater's Memorial, Giryak 2 A | Checked against your journal | none | D: location and permit |
| Kit Fowler | Bubble, on foot | The Last Call, Capoya 2 | Verification needed | Push x5 (collect at a planetary settlement (on foot)); Opinion Polls x40 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how you met it; B: how to get the items; D: location and permit |
| Lei Cheung | Bubble | Trader's Rest, Laksak A 1 | Checked against your journal | Gold x200 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Liz Ryder | Bubble | Demolition Unlimited, Eurybia Makalu | Verification needed | Landmines x200 (buy at a market) | A: exact invitation wording and how you met it; C: confirm a market that stocks them; D: location and permit |
| Lori Jameson | Bubble, permit | Jameson Base, Shinrarta Dezhra A 1 | Checked against your journal | Kongga Ale x25 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Marco Qwent | Bubble, permit | Qwent Research Base, Sirius Lucifer | Verification needed | Modular Terminals x25 (a mission reward or a rescue) | A: exact invitation wording and how you met it; B: how to get the items; D: location and permit |
| Marsha Hicks | Colonia | The Watchtower, Tir A 2 | Checked against your journal | Osmium x10 (mine it) | B: where you mined them; D: location and permit |
| Mel Brandon | Colonia | The Brig, Luchtaine A 1 C | Verification needed | none | A: exact invitation wording and how you met it; D: location and permit |
| Oden Geiger | Bubble, on foot | Ankh's Promise, Candiaei 9 C | Verification needed | Financial Projections x15 (collect at a planetary settlement (on foot)); Biological Sample x20 (collect at a planetary settlement (on foot)); Employee Genetic Data x20 (collect at a planetary settlement (on foot)); Genetic Research x20 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how you met it; B: how to get the items; D: location and permit |
| Petra Olmanova | Colonia | Sanctuary, Asura 1 A | Checked against your journal | Progenitor Cells x200 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Professor Palin | Bubble | Abel Laboratory, Arque 4 E | Checked against your journal | Sensor Fragment x25 (collect at a Thargoid or Guardian site) | B: how to get the items; D: location and permit |
| Ram Tah | Bubble | Phoenix Base, Meene AB 5 D | Checked against your journal | Classified Scan Databanks x50 (scan ships or data points) | B: how to get the items; D: location and permit |
| Rosa Dayette | Colonia, on foot | Rosa's Shop, Kojeara 4 B | Verification needed | none | A: exact invitation wording and how you met it; D: location and permit |
| Selene Jean | Bubble | Prospector's Rest, Kuk B 3 | Checked against your journal | Painite x10 (mine it) | B: where you mined them; D: location and permit |
| Terra Velasquez | Bubble, on foot | Rascal's Choice, Shou Xing 1 | Verification needed | Genetic Repair Meds x5 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how you met it; B: how to get the items; D: location and permit |
| The Dweller | Bubble | Black Hide, Wyrd A 2 | Checked against your journal | none | D: location and permit |
| The Sarge | Bubble | The Beach, Beta-3 Tucani 2 B A | Checked against your journal | Aberrant Shield Pattern Analysis x50 (scan ships or data points) | B: how to get the items; D: location and permit |
| Tiana Fortune | Bubble, permit | Fortune's Loss, Achenar 4 A | Verification needed | Decoded Emission Data x50 (scan ships or data points) | A: exact invitation wording and how you met it; B: how to get the items; D: location and permit |
| Tod 'The Blaster' McQuinn | Bubble | Trophy Camp, Wolf 397 Trus Madi | Checked against your journal | none | D: location and permit |
| Uma Laszlo | Bubble, on foot | Laszlo's Resolve, Xuane A 3 | Verification needed | Insight Entertainment Suite x5 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how you met it; B: how to get the items; D: location and permit |
| Wellington Beck | Bubble, on foot | Beck Facility, Jolapa 6 A | Verification needed | Settlement Defence Plans x15 (collect at a planetary settlement (on foot)); Classic Entertainment x25 (collect at a planetary settlement (on foot)); Multimedia Entertainment x25 (collect at a planetary settlement (on foot)); Cat Media x25 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how you met it; B: how to get the items; D: location and permit |
| Yarden Bond | Bubble, on foot | Salamander Bank, Bayan 7 B | Verification needed | Surveillance Equipment x5 (collect at a planetary settlement (on foot)); Smear Campaign Plans x8 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how you met it; B: how to get the items; D: location and permit |
| Yi Shen | Colonia, on foot | Eidolon Hold, Einheriar 1 A | Verification needed | Faction Associates x10 (collect at a planetary settlement (on foot)); Digital Designs x10 (a mission reward or a rescue); Manufacturing Instructions x10 (a mission reward or a rescue) | A: exact invitation wording and how you met it; B: how to get the items; D: location and permit |
| Zacariah Nemo | Bubble | Nemo Cyber Party Base, Yoru 4 | Verification needed | Xihe Companions x25 (buy at a market) | A: exact invitation wording and how you met it; C: confirm a market that stocks them; D: location and permit |

## Order to work in

1. The two Sensor Fragment engineers (Chloe Sedesi and Professor Palin) share one guide, already written from a community report and not yet confirmed. To confirm it, follow it in the game and note how many fragments one sensor drops, whether they go to materials or cargo, and whether the sensors return after a relog; then set `verified` and `updated` in `plugin/engineer_guides_data.py`.
2. The engineers whose items come from planetary settlements (on foot): Kit Fowler, Oden Geiger, Terra Velasquez, Uma Laszlo, Wellington Beck and Yarden Bond.
3. The engineers whose items are scanned data: Ram Tah, The Sarge and Tiana Fortune.
4. The engineers whose items are a mission reward or a rescue: Etienne Dorn and Marco Qwent.
5. The engineers WFMT cannot check (**Verification needed**): section A for each.
6. The engineers whose items are bought or mined: section C, to confirm the lookup.

Each guide, once written and confirmed, also needs the matching line in `docs/TEST_PLAN.md` section 10 and a mention in the changelog.
