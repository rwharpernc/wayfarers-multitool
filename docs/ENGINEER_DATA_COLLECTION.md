# Engineer data collection

This page lists the information needed to complete the Engineers tab and describes how to gather and record it. The journal does not record how to obtain items that cannot be bought, or what the game states an invitation requires when WFMT cannot check it. Written guides for these cases are recorded per engineer.

## Background

- The locations, invitation requirements and unlock items of the engineers come from a community table, not from the game. Where the journal records a number (a rank or a lifetime figure), WFMT checks the requirement against it. For the other engineers it cannot, and the Engineers tab shows the note **Verification needed**.
- Some unlock items are not sold: Sensor Fragments (a Thargoid material), items from planetary settlements (on foot), data from scanning ships, and rewards for missions or rescues. WFMT classifies every item by how it is obtained and offers the matching finder (market lookup, Material trader, nearest Thargoid site). For the remaining items it shows only a short note on the source.
- The Engineers tab shows a written guide in its own section (**How to get it**) when one exists, marked as community-reported until confirmed in the game.

## Data to gather

Gather the data for one engineer at a time.

**A. Invitation and unlock requirements in the game**

1. Open the in-game Engineers panel (Commander screen, Engineers) and select the engineer.
2. Copy the invitation requirement and the unlock requirement word for word. Note the standing (Unknown, Known, Invited, Unlocked) and the rank.
3. Compare the wording with **Path to unlock** and **Raising your rank with them** on the Engineers tab. Record differences and omissions. The latter section remains a general text until an engineer's own text is confirmed.
4. For a requirement that WFMT checks (a rank or a lifetime figure), compare the **you have ...** note with the figure on the Commander screen, Statistics.

**B. Items that cannot be bought.** For each item, record:

1. The item name in the game inventory, and the journal event if visible: `MaterialCollected` (ship material), `CollectItems` or `BackpackChange` (on-foot item), `MissionCompleted` (reward).
2. The method used, in order: the location (system and body, with coordinates or a description of the place), the equipment needed (ship modules, SRV, on-foot equipment) and the actions taken.
3. The quantity per pickup and the total quantity required.
4. Whether the location can be farmed again, what causes respawn, and the duration of one round.
5. Hazards: damage (for example corrosion from carrying an item), hostile ships or defenders, carry limits, and anything that wastes the item.
6. Alternative sources (another location, a mission, a trade).
7. Whether the method was carried out in the game. A guide remains marked "community-reported" until it was.

**C. Items that can be bought.** Record a market that stocks the item and the price per ton, or the mining location. The Where to buy lookup finds markets itself; this record checks its results.

**D. Engineer location.** Confirm the base, system and body, and whether a permit is required or the engineer is on foot. For the Colonia engineers, record the distance from Sol shown on the galaxy map.

## Recording the data

- **Report engineer data.** Select the engineer on the Engineers tab and press **Report engineer data**. A GitHub form opens with the engineer and the standing WFMT knows prefilled. Enter the in-game text under **What the game shows** and WFMT errors under **What WFMT showed that is wrong or missing**. Nothing is sent until the form is submitted on GitHub. The **Report game data** button under Settings → WFMT → General → Help opens the same form blank.
- **Writing a guide.** Add an entry to `GUIDES` in `plugin/engineer_guides_data.py`:

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

The key is the engineer's name in lower case without a nickname (as written by `engineers.name_key`). `verified` stays False until the steps have been carried out in the game. While it is False, the pane states "Community-reported and not yet confirmed in the game" and requests corrections. Guides use WFMT's own wording and contain no outside links.

## Engineers

The table lists every engineer and the data to gather (the letters refer to the sections above). The unlock items come from the `Unlock` rows of `plugin/blueprints_data.py` and the other columns from `plugin/engineers_data.py`. The table is a snapshot and is not updated automatically.

| Engineer | Area | Base | Invitation | Unlock items (how they are got) | To gather |
|---|---|---|---|---|---|
| Baltanos | Colonia, on foot | The Divine Apparatus, Deriso 3 A | Verification needed | none | A: exact invitation wording and how it was met; D: location and permit |
| Bill Turner | Bubble, permit | Turner Metallics Inc, Alioth 4 A | Verification needed | Bromellite x50 (mine it) | A: exact invitation wording and how it was met; B: where they were mined; D: location and permit |
| Broo Tarquin | Bubble | Broo's Legacy, Muang 5 A | Checked against the journal | Fujin Tea x50 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Chloe Sedesi | Bubble | Cinder Dock, Shenve A 6 | Checked against the journal | Sensor Fragment x25 (collect at a Thargoid or Guardian site) | B: how to get the items; D: location and permit |
| Colonel Bris Dekker | Bubble, permit | Dekker's Yard, Sol Iapetus | Verification needed | none | A: exact invitation wording and how it was met; D: location and permit |
| Didi Vatermann | Bubble | Vatermann LLC, Leesti 1 A | Checked against the journal | Lavian Brandy x50 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Domino Green | Bubble, on foot | The Jackrabbit, Orishis 4 | Verification needed | none | A: exact invitation wording and how it was met; D: location and permit |
| Eleanor Bresa | Colonia, on foot | Bresa Modifications, Desy 7 A | Verification needed | none | A: exact invitation wording and how it was met; D: location and permit |
| Elvira Martuuk | Bubble | Long Sight Base, Khun 5 | Checked against the journal | Soontill Relics x3 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Etienne Dorn | Colonia | Kraken's Retreat, Los A 2 B | Checked against the journal | Occupied Escape Pod x25 (a mission reward or a rescue) | B: how to get the items; D: location and permit |
| Felicity Farseer | Bubble | Farseer Inc, Deciat 6 A | Checked against the journal | Meta-alloys x1 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Hera Tani | Bubble | The Jet's Hole, Kuwemaki A 3 A | Checked against the journal | Kamitra Cigars x50 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Hero Ferrari | Bubble, on foot | Nevermore Terrace, Siris 5 C | Verification needed | none | A: exact invitation wording and how it was met; D: location and permit |
| Jude Navarro | Bubble, on foot | Marshall's Drift, Aurai 1 A | Verification needed | none | A: exact invitation wording and how it was met; D: location and permit |
| Juri Ishmaak | Bubble | Pater's Memorial, Giryak 2 A | Checked against the journal | none | D: location and permit |
| Kit Fowler | Bubble, on foot | The Last Call, Capoya 2 | Verification needed | Push x5 (collect at a planetary settlement (on foot)); Opinion Polls x40 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how it was met; B: how to get the items; D: location and permit |
| Lei Cheung | Bubble | Trader's Rest, Laksak A 1 | Checked against the journal | Gold x200 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Liz Ryder | Bubble | Demolition Unlimited, Eurybia Makalu | Verification needed | Landmines x200 (buy at a market) | A: exact invitation wording and how it was met; C: confirm a market that stocks them; D: location and permit |
| Lori Jameson | Bubble, permit | Jameson Base, Shinrarta Dezhra A 1 | Checked against the journal | Kongga Ale x25 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Marco Qwent | Bubble, permit | Qwent Research Base, Sirius Lucifer | Verification needed | Modular Terminals x25 (a mission reward or a rescue) | A: exact invitation wording and how it was met; B: how to get the items; D: location and permit |
| Marsha Hicks | Colonia | The Watchtower, Tir A 2 | Checked against the journal | Osmium x10 (mine it) | B: where they were mined; D: location and permit |
| Mel Brandon | Colonia | The Brig, Luchtaine A 1 C | Verification needed | none | A: exact invitation wording and how it was met; D: location and permit |
| Oden Geiger | Bubble, on foot | Ankh's Promise, Candiaei 9 C | Verification needed | Financial Projections x15 (collect at a planetary settlement (on foot)); Biological Sample x20 (collect at a planetary settlement (on foot)); Employee Genetic Data x20 (collect at a planetary settlement (on foot)); Genetic Research x20 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how it was met; B: how to get the items; D: location and permit |
| Petra Olmanova | Colonia | Sanctuary, Asura 1 A | Checked against the journal | Progenitor Cells x200 (buy at a market) | C: confirm a market that stocks them; D: location and permit |
| Professor Palin | Bubble | Abel Laboratory, Arque 4 E | Checked against the journal | Sensor Fragment x25 (collect at a Thargoid or Guardian site) | B: how to get the items; D: location and permit |
| Ram Tah | Bubble | Phoenix Base, Meene AB 5 D | Checked against the journal | Classified Scan Databanks x50 (scan ships or data points) | B: how to get the items; D: location and permit |
| Rosa Dayette | Colonia, on foot | Rosa's Shop, Kojeara 4 B | Verification needed | none | A: exact invitation wording and how it was met; D: location and permit |
| Selene Jean | Bubble | Prospector's Rest, Kuk B 3 | Checked against the journal | Painite x10 (mine it) | B: where they were mined; D: location and permit |
| Terra Velasquez | Bubble, on foot | Rascal's Choice, Shou Xing 1 | Verification needed | Genetic Repair Meds x5 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how it was met; B: how to get the items; D: location and permit |
| The Dweller | Bubble | Black Hide, Wyrd A 2 | Checked against the journal | none | D: location and permit |
| The Sarge | Bubble | The Beach, Beta-3 Tucani 2 B A | Checked against the journal | Aberrant Shield Pattern Analysis x50 (scan ships or data points) | B: how to get the items; D: location and permit |
| Tiana Fortune | Bubble, permit | Fortune's Loss, Achenar 4 A | Verification needed | Decoded Emission Data x50 (scan ships or data points) | A: exact invitation wording and how it was met; B: how to get the items; D: location and permit |
| Tod 'The Blaster' McQuinn | Bubble | Trophy Camp, Wolf 397 Trus Madi | Checked against the journal | none | D: location and permit |
| Uma Laszlo | Bubble, on foot | Laszlo's Resolve, Xuane A 3 | Verification needed | Insight Entertainment Suite x5 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how it was met; B: how to get the items; D: location and permit |
| Wellington Beck | Bubble, on foot | Beck Facility, Jolapa 6 A | Verification needed | Settlement Defence Plans x15 (collect at a planetary settlement (on foot)); Classic Entertainment x25 (collect at a planetary settlement (on foot)); Multimedia Entertainment x25 (collect at a planetary settlement (on foot)); Cat Media x25 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how it was met; B: how to get the items; D: location and permit |
| Yarden Bond | Bubble, on foot | Salamander Bank, Bayan 7 B | Verification needed | Surveillance Equipment x5 (collect at a planetary settlement (on foot)); Smear Campaign Plans x8 (collect at a planetary settlement (on foot)) | A: exact invitation wording and how it was met; B: how to get the items; D: location and permit |
| Yi Shen | Colonia, on foot | Eidolon Hold, Einheriar 1 A | Verification needed | Faction Associates x10 (collect at a planetary settlement (on foot)); Digital Designs x10 (a mission reward or a rescue); Manufacturing Instructions x10 (a mission reward or a rescue) | A: exact invitation wording and how it was met; B: how to get the items; D: location and permit |
| Zacariah Nemo | Bubble | Nemo Cyber Party Base, Yoru 4 | Verification needed | Xihe Companions x25 (buy at a market) | A: exact invitation wording and how it was met; C: confirm a market that stocks them; D: location and permit |


## Order of work

1. Chloe Sedesi and Professor Palin share one guide, written from a community report and not yet confirmed. To confirm it, follow it in the game and record how many fragments one sensor drops, whether they go to materials or cargo, and whether the sensors return after a relog. Then set `verified` and `updated` in `plugin/engineer_guides_data.py`.
2. Engineers whose items come from planetary settlements (on foot): Kit Fowler, Oden Geiger, Terra Velasquez, Uma Laszlo, Wellington Beck and Yarden Bond.
3. Engineers whose items are scanned data: Ram Tah, The Sarge and Tiana Fortune.
4. Engineers whose items are a mission reward or a rescue: Etienne Dorn and Marco Qwent.
5. Engineers that WFMT cannot check (**Verification needed**): section A for each.
6. Engineers whose items are bought or mined: section C.

A confirmed guide also requires the matching line in `docs/TEST_PLAN.md` section 10 and an entry in the changelog.
