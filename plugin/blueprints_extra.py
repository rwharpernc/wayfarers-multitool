"""Hand-added entries the blueprint table lacks (March 2024): the Yi Shen unlock, which asks the commander to hand each of the other
three Colonia on-foot engineers (Baltanos, Eleanor Bresa, Rosa Dayette) a set of items.

**Sources**: community-maintained, none of them from Frontier. Source and license: see docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md.
- The referral items are 10 Faction Associates to Baltanos, 10 Manufacturing Instructions to Rosa Dayette and 10 Digital Designs to Eleanor Bresa.
- Where each of the four is and how to unlock them is in `engineers_data.py`. Which suit and weapon upgrades each offers is in
  `blueprints_data.py`, from a community engineer list.

What goes in the table: one "Unlock" row for Yi Shen, so the wishlist and shopping list can count the three sets of items. The other three unlocks
are actions, not items, so they are text only (in `engineers_data.py`). The ingredients are micro-resources the Inventory already counts."""
from __future__ import annotations

from typing import Tuple

# Same shape as blueprints_data.BLUEPRINT_ROWS: (type, name, grade, engineers, ((ingredient, count), ...), ((property, effect, is good), ...)).
# For this row the "engineers" are the three who are handed the items.
EXTRA_ROWS: Tuple[tuple, ...] = (
    ("Unlock", "Yi Shen", 0, ("Baltanos", "Eleanor Bresa", "Rosa Dayette"),
     (("Faction Associates", 10), ("Digital Designs", 10), ("Manufacturing Instructions", 10)), ()),
)

# Same shape as blueprints_data.INGREDIENT_ROWS: (name, kind, canonical name, group, where it is found). The canonical names are the Inventory's keys.
EXTRA_INGREDIENTS: Tuple[tuple, ...] = (
    ("Faction Associates", "OdysseyIngredient", "factionassociates", "Data", ("Downloaded from the CMD data ports in settlement command rooms",)),
    ("Digital Designs", "OdysseyIngredient", "digitaldesigns", "Data", ()),
    ("Manufacturing Instructions", "OdysseyIngredient", "manufacturinginstructions", "Data", ()),
)

