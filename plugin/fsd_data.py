"""Frame shift drive base values, for the Route Planner. Game facts: what each drive module is, before any engineering.

Spansh's exact plotter needs, for the drive a ship carries, its optimal mass, the most fuel one jump can use, and the two constants of the fuel formula (`fuel used =
fuel multiplier * (distance * mass / optimal mass) ^ fuel power`). The journal's `Loadout` names the drive and, for an engineered one, carries the final optimal mass and
maximum fuel in its modifiers, but the multiplier and power only come from here. These are game facts as Spansh's own exact-plotter page carries them (source and license: see docs/ATTRIBUTIONS.md), read on 2026-10-18 and listed in
docs/data_verification (V-0352). A drive that is not here is reported to the commander rather than guessed.

AUTO-GENERATED from that data; the one hand edit is the note above. Keys are the journal's `Item` in lower case.
"""
from __future__ import annotations

from typing import Dict, Tuple

# item -> (optimal mass t, most fuel per jump t, fuel multiplier, fuel power)
FSD: Dict[str, Tuple[float, float, float, float]] = {
    'int_hyperdrive_size2_class1': (48, 0.6, 0.011, 2),
    'int_hyperdrive_size2_class2': (54, 0.6, 0.01, 2),
    'int_hyperdrive_size2_class3': (60, 0.6, 0.008, 2),
    'int_hyperdrive_size2_class4': (75, 0.8, 0.01, 2),
    'int_hyperdrive_size2_class5': (90, 0.9, 0.012, 2),
    'int_hyperdrive_size3_class1': (80, 1.2, 0.011, 2.15),
    'int_hyperdrive_size3_class2': (90, 1.2, 0.01, 2.15),
    'int_hyperdrive_size3_class3': (100, 1.2, 0.008, 2.15),
    'int_hyperdrive_size3_class4': (125, 1.5, 0.01, 2.15),
    'int_hyperdrive_size3_class5': (150, 1.8, 0.012, 2.15),
    'int_hyperdrive_size4_class1': (280, 2, 0.011, 2.3),
    'int_hyperdrive_size4_class2': (315, 2, 0.01, 2.3),
    'int_hyperdrive_size4_class3': (350, 2, 0.008, 2.3),
    'int_hyperdrive_size4_class4': (437.5, 2.5, 0.01, 2.3),
    'int_hyperdrive_size4_class5': (525, 3, 0.012, 2.3),
    'int_hyperdrive_size5_class1': (560, 3.3, 0.011, 2.45),
    'int_hyperdrive_size5_class2': (630, 3.3, 0.01, 2.45),
    'int_hyperdrive_size5_class3': (700, 3.3, 0.008, 2.45),
    'int_hyperdrive_size5_class4': (875, 4.1, 0.01, 2.45),
    'int_hyperdrive_size5_class5': (1050, 5, 0.012, 2.45),
    'int_hyperdrive_size6_class1': (960, 5.3, 0.011, 2.6),
    'int_hyperdrive_size6_class2': (1080, 5.3, 0.01, 2.6),
    'int_hyperdrive_size6_class3': (1200, 5.3, 0.008, 2.6),
    'int_hyperdrive_size6_class4': (1500, 6.6, 0.01, 2.6),
    'int_hyperdrive_size6_class5': (1800, 8, 0.012, 2.6),
    'int_hyperdrive_size7_class1': (1440, 8.5, 0.011, 2.75),
    'int_hyperdrive_size7_class2': (1620, 8.5, 0.01, 2.75),
    'int_hyperdrive_size7_class3': (1800, 8.5, 0.008, 2.75),
    'int_hyperdrive_size7_class4': (2250, 10.6, 0.01, 2.75),
    'int_hyperdrive_size7_class5': (2700, 12.8, 0.012, 2.75),
    'int_hyperdrive_overcharge_size2_class1': (60, 0.6, 0.008, 2),
    'int_hyperdrive_overcharge_size2_class2': (90, 0.9, 0.012, 2),
    'int_hyperdrive_overcharge_size2_class3': (90, 0.9, 0.012, 2),
    'int_hyperdrive_overcharge_size2_class4': (90, 0.9, 0.012, 2),
    'int_hyperdrive_overcharge_size2_class5': (100, 1, 0.013, 2),
    'int_hyperdrive_overcharge_size3_class1': (100, 1.2, 0.008, 2.15),
    'int_hyperdrive_overcharge_size3_class2': (150, 1.8, 0.012, 2.15),
    'int_hyperdrive_overcharge_size3_class3': (150, 1.8, 0.012, 2.15),
    'int_hyperdrive_overcharge_size3_class4': (150, 1.8, 0.012, 2.15),
    'int_hyperdrive_overcharge_size3_class5': (167, 1.9, 0.013, 2.15),
    'int_hyperdrive_overcharge_size4_class1': (350, 2, 0.008, 2.3),
    'int_hyperdrive_overcharge_size4_class2': (525, 3, 0.012, 2.3),
    'int_hyperdrive_overcharge_size4_class3': (525, 3, 0.012, 2.3),
    'int_hyperdrive_overcharge_size4_class4': (525, 3, 0.012, 2.3),
    'int_hyperdrive_overcharge_size4_class5': (585, 3.2, 0.013, 2.3),
    'int_hyperdrive_overcharge_size5_class1': (700, 3.3, 0.008, 2.45),
    'int_hyperdrive_overcharge_size5_class2': (1050, 5, 0.012, 2.45),
    'int_hyperdrive_overcharge_size5_class3': (1050, 5, 0.012, 2.45),
    'int_hyperdrive_overcharge_size5_class4': (1050, 5, 0.012, 2.45),
    'int_hyperdrive_overcharge_size5_class5': (1175, 5.2, 0.013, 2.45),
    'int_hyperdrive_overcharge_size6_class1': (1200, 5.3, 0.008, 2.6),
    'int_hyperdrive_overcharge_size6_class2': (1800, 8, 0.012, 2.6),
    'int_hyperdrive_overcharge_size6_class3': (1800, 8, 0.012, 2.6),
    'int_hyperdrive_overcharge_size6_class4': (1800, 8, 0.012, 2.6),
    'int_hyperdrive_overcharge_size6_class5': (2000, 8.3, 0.013, 2.6),
    'int_hyperdrive_overcharge_size7_class1': (1800, 8.5, 0.008, 2.75),
    'int_hyperdrive_overcharge_size7_class2': (2700, 12.8, 0.012, 2.75),
    'int_hyperdrive_overcharge_size7_class3': (2700, 12.8, 0.012, 2.75),
    'int_hyperdrive_overcharge_size7_class4': (2700, 12.8, 0.012, 2.75),
    'int_hyperdrive_overcharge_size7_class5': (3000, 13.1, 0.013, 2.75),
    'int_hyperdrive_overcharge_size8_class1': (2800, 13.6, 0.008, 2.9),
    'int_hyperdrive_overcharge_size8_class2': (4200, 20.4, 0.012, 2.9),
    'int_hyperdrive_overcharge_size8_class3': (4200, 20.4, 0.012, 2.9),
    'int_hyperdrive_overcharge_size8_class4': (4200, 20.4, 0.012, 2.9),
    'int_hyperdrive_overcharge_size8_class5': (4670, 20.7, 0.013, 2.9),
    'int_hyperdrive_overcharge_size8_class5_overchargebooster_mkii': (4670, 6.8, 0.011, 2.5025),
}

# Guardian frame shift drive booster: size -> jump range added, ly
GUARDIAN_BOOST: Dict[int, float] = {1: 4, 2: 6, 3: 7.75, 4: 9.25, 5: 10.5}

# Drives whose supercharge at a neutron star is better than the usual 4 (the Mk II overcharge drive: 6). Others use 4.
SUPERCHARGE: Dict[str, int] = {'int_hyperdrive_overcharge_size8_class5_overchargebooster_mkii': 6}
SUPERCHARGE_DEFAULT = 4
INJECTION_MULTIPLIER = 2
