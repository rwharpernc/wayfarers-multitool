"""Engineering blueprints added from EDSY's data (imported 2026-11-03): the blueprints the table from EDEngineer's data (last changed 2024-03-07) lacks.

Hand-maintained from here on (nothing regenerates it). Source: the blueprint and material sections of EDSY's `eddb.js` (https://github.com/taleden/EDSY), read as
data, with the module-to-blueprint lists of its module groups. Only facts are taken (names, the materials of each grade, which modules a blueprint applies to); see
docs/ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md. What the rows are, and are not:

- Each row is (module type, blueprint name, grade, engineers, ingredients, effects), as in `blueprints_data.py`. **Engineers and effects are empty**: the source lists neither, so
  the Engineering window shows a dash for who offers them and nothing under effects.
- **Materials only.** The source notes that several of these also cost mercenary coins per grade (its own `merccoin` notes, which it has not filled in either); the coins are not a
  material WFMT tracks and are not in the rows, like an engineer's fee. A grade whose materials the source leaves empty (it does so for grade 1 of most of these) is left out, not
  written as free: the source does not know it. The Ship planner reports such a blueprint as partly counted, "the table has N of the L grades".
- **Anti-Guardian Zone Resistance** (journal name `GuardianModule_Sturdy`, seen on a Guardian Gauss cannon at level 1) is one grade. The source writes its three materials as three
  separate entries and marks the blueprint's journal name `TODO`; the name is confirmed by the journal, and the three are taken as the one craft's materials. A figure may be wrong.
- **Long Range for the mining laser and the abrasion blaster** has two journal names, and both are kept: the ordinary Long Range Weapon (`Weapon_LongRange`, which a journal's mining
  laser has been seen to name, and whose recipe equals this table's for every other weapon) and the source's own Long Range Mining Laser (`Weapon_LongRangeMiningLaser`). The rows for the
  two carry the same materials, so whichever name an event gives, the same craft is counted.
- **Left out**: Force Impact (the source has no materials for it), Expanded Cargo Rack (pre-engineered, no materials), High-Yield (flak and flechette launchers have no module type here)
  and the four decorative blueprints (no materials). They stay "not counted".

`EDSY_JOURNAL_NAMES` is how the journal names each blueprint (`BlueprintName`) and what it is called in the rows above, by module type; `scripts/gen_journal_blueprints.py` adds it to
`journal_blueprints.py`.
"""

from __future__ import annotations

from typing import Dict, Tuple

EDSY_ROWS: Tuple[tuple, ...] = (
    ('Power Distributor', 'Balanced', 2, (), (('Sulphur', 1), ('Specialised Legacy Firmware', 1), ('Chemical Processors', 1),), ()),
    ('Power Distributor', 'Balanced', 3, (), (('Specialised Legacy Firmware', 1), ('Chemical Processors', 1), ('High Density Composites', 1),), ()),
    ('Power Distributor', 'Balanced', 4, (), (('Chemical Processors', 1), ('High Density Composites', 1), ('Selenium', 1), ('Chemical Manipulators', 1),), ()),
    ('Power Distributor', 'Balanced', 5, (), (('Proprietary Composites', 1), ('Chemical Manipulators', 1), ('Military Supercapacitors', 1), ('Exquisite Focus Crystals', 1),), ()),
    ('Power Distributor', 'Support Focused', 2, (), (('Sulphur', 1), ('Specialised Legacy Firmware', 1), ('Conductive Components', 1),), ()),
    ('Power Distributor', 'Support Focused', 3, (), (('Anomalous Bulk Scan Data', 1), ('Chromium', 1), ('Electrochemical Arrays', 1),), ()),
    ('Power Distributor', 'Support Focused', 4, (), (('Unidentified Scan Archives', 1), ('Modified Consumer Firmware', 1), ('Selenium', 1), ('Polymer Capacitors', 1),), ()),
    ('Power Distributor', 'Support Focused', 5, (), (('Classified Scan Databanks', 1), ('Cadmium', 1), ('Proprietary Composites', 1), ('Military Supercapacitors', 1),), ()),
    ('Fuel Scoop', 'Scoop Rate Enhanced', 1, (), (('Phosphorus', 1), ('Grid Resistors', 1),), ()),
    ('Fuel Scoop', 'Scoop Rate Enhanced', 2, (), (('Chromium', 1), ('Grid Resistors', 1), ('Chemical Processors', 1),), ()),
    ('Fuel Scoop', 'Scoop Rate Enhanced', 3, (), (('Chromium', 1), ('Chemical Processors', 1), ('Conductive Ceramics', 1),), ()),
    ('Fuel Scoop', 'Scoop Rate Enhanced', 4, (), (('Chemical Processors', 2), ('Chemical Distillery', 1), ('Proto Light Alloys', 1),), ()),
    ('Fuel Scoop', 'Scoop Rate Enhanced', 5, (), (('Tellurium', 1), ('Chemical Manipulators', 1), ('Proto Heat Radiators', 1), ('Proto Radiolic Alloys', 1),), ()),
    ('Fragment Cannon', 'Double Screaming', 2, (), (('Carbon', 1), ('Mechanical Scrap', 1), ('Mechanical Equipment', 1),), ()),
    ('Fragment Cannon', 'Double Screaming', 3, (), (('Carbon', 1), ('Mechanical Equipment', 1), ('Tin', 1),), ()),
    ('Fragment Cannon', 'Double Screaming', 4, (), (('Vanadium', 1), ('Cracked Industrial Firmware', 1), ('Mechanical Components', 1), ('Security Firmware Patch', 1),), ()),
    ('Fragment Cannon', 'Double Screaming', 5, (), (('High Density Composites', 1), ('Mechanical Components', 1), ('Configurable Components', 1), ('Modified Embedded Firmware', 1),), ()),
    ('Missile Rack', 'Drag Seeker', 2, (), (('Mechanical Scrap', 1), ('Vanadium', 1), ('Heat Dispersion Plate', 1),), ()),
    ('Missile Rack', 'Drag Seeker', 3, (), (('Mechanical Scrap', 1), ('Mechanical Equipment', 1), ('Precipitated Alloys', 1),), ()),
    ('Missile Rack', 'Drag Seeker', 4, (), (('Modified Consumer Firmware', 1), ('Mechanical Components', 1), ('High Density Composites', 1), ('Thermic Alloys', 1),), ()),
    ('Missile Rack', 'Drag Seeker', 5, (), (('Mechanical Components', 1), ('Proprietary Composites', 1), ('Technetium', 1), ('Military Supercapacitors', 1),), ()),
    ('Missile Rack', 'Lightweight Thermal Seeker', 2, (), (('Mechanical Scrap', 1), ('Vanadium', 1), ('Manganese', 1),), ()),
    ('Missile Rack', 'Lightweight Thermal Seeker', 3, (), (('Mechanical Scrap', 1), ('Mechanical Equipment', 1), ('Conductive Ceramics', 1),), ()),
    ('Missile Rack', 'Lightweight Thermal Seeker', 4, (), (('Modified Consumer Firmware', 1), ('Phase Alloys', 1), ('Proto Light Alloys', 1), ('Thermic Alloys', 1),), ()),
    ('Missile Rack', 'Lightweight Thermal Seeker', 5, (), (('Mechanical Components', 1), ('Proto Light Alloys', 1), ('Proto Radiolic Alloys', 1), ('Military Supercapacitors', 1),), ()),
    ('Missile Rack', 'Lockdown', 2, (), (('Mechanical Scrap', 1), ('Nickel', 1), ('Vanadium', 1),), ()),
    ('Missile Rack', 'Lockdown', 3, (), (('Mechanical Scrap', 1), ('Mechanical Equipment', 1), ('Tungsten', 1),), ()),
    ('Missile Rack', 'Lockdown', 4, (), (('Modified Consumer Firmware', 1), ('Tungsten', 1), ('Molybdenum', 1), ('Thermic Alloys', 1),), ()),
    ('Missile Rack', 'Lockdown', 5, (), (('Mechanical Components', 1), ('Molybdenum', 1), ('Technetium', 1), ('Military Supercapacitors', 1),), ()),
    ('Beam Laser', 'Overloaded', 2, (), (('Chromium', 1), ('Conductive Components', 1), ('Nickel', 1),), ()),
    ('Beam Laser', 'Overloaded', 3, (), (('Chromium', 1), ('Conductive Components', 1), ('Electrochemical Arrays', 1),), ()),
    ('Beam Laser', 'Overloaded', 4, (), (('Electrochemical Arrays', 1), ('High Density Composites', 1), ('Polymer Capacitors', 1), ('Focus Crystals', 1),), ()),
    ('Beam Laser', 'Overloaded', 5, (), (('Zirconium', 1), ('Military Supercapacitors', 1), ('Modified Embedded Firmware', 1), ('Focus Crystals', 1),), ()),
    ('Beam Laser', 'Plasma Conversion', 1, (), (('Phosphorus', 1), ('Heat Conduction Wiring', 1),), ()),
    ('Beam Laser', 'Plasma Conversion', 2, (), (('Heat Conduction Wiring', 1), ('Heat Dispersion Plate', 1),), ()),
    ('Beam Laser', 'Plasma Conversion', 3, (), (('Heat Dispersion Plate', 1), ('Phase Alloys', 1),), ()),
    ('Beam Laser', 'Plasma Conversion', 4, (), (('Heat Dispersion Plate', 1), ('Phase Alloys', 1), ('Refined Focus Crystals', 1), ('Configurable Components', 1),), ()),
    ('Beam Laser', 'Plasma Conversion', 5, (), (('Technetium', 1), ('Thermic Alloys', 1), ('Military Supercapacitors', 1), ('Modified Embedded Firmware', 1),), ()),
    ('Burst Laser', 'Plasma Conversion', 1, (), (('Phosphorus', 1), ('Heat Conduction Wiring', 1),), ()),
    ('Burst Laser', 'Plasma Conversion', 2, (), (('Heat Conduction Wiring', 1), ('Heat Dispersion Plate', 1),), ()),
    ('Burst Laser', 'Plasma Conversion', 3, (), (('Heat Dispersion Plate', 1), ('Phase Alloys', 1),), ()),
    ('Burst Laser', 'Plasma Conversion', 4, (), (('Heat Dispersion Plate', 1), ('Phase Alloys', 1), ('Refined Focus Crystals', 1), ('Configurable Components', 1),), ()),
    ('Burst Laser', 'Plasma Conversion', 5, (), (('Technetium', 1), ('Thermic Alloys', 1), ('Military Supercapacitors', 1), ('Modified Embedded Firmware', 1),), ()),
    ('Pulse Laser', 'Plasma Conversion', 1, (), (('Phosphorus', 1), ('Heat Conduction Wiring', 1),), ()),
    ('Pulse Laser', 'Plasma Conversion', 2, (), (('Heat Conduction Wiring', 1), ('Heat Dispersion Plate', 1),), ()),
    ('Pulse Laser', 'Plasma Conversion', 3, (), (('Heat Dispersion Plate', 1), ('Phase Alloys', 1),), ()),
    ('Pulse Laser', 'Plasma Conversion', 4, (), (('Heat Dispersion Plate', 1), ('Phase Alloys', 1), ('Refined Focus Crystals', 1), ('Configurable Components', 1),), ()),
    ('Pulse Laser', 'Plasma Conversion', 5, (), (('Technetium', 1), ('Thermic Alloys', 1), ('Military Supercapacitors', 1), ('Modified Embedded Firmware', 1),), ()),
    ('Multi-cannon', 'Rapid Phase', 2, (), (('Mechanical Scrap', 1), ('Heat Dispersion Plate', 1), ('Conductive Components', 1),), ()),
    ('Multi-cannon', 'Rapid Phase', 3, (), (('Specialised Legacy Firmware', 1), ('Mechanical Equipment', 1), ('Precipitated Alloys', 1),), ()),
    ('Multi-cannon', 'Rapid Phase', 4, (), (('Modified Consumer Firmware', 1), ('Mechanical Components', 1), ('Conductive Ceramics', 1), ('Thermic Alloys', 1),), ()),
    ('Multi-cannon', 'Rapid Phase', 5, (), (('Precipitated Alloys', 1), ('Configurable Components', 1), ('Conductive Ceramics', 1), ('Technetium', 1),), ()),
    ('Burst Laser', 'Regenerative', 2, (), (('Nickel', 1), ('Modified Consumer Firmware', 1), ('Conductive Components', 1),), ()),
    ('Burst Laser', 'Regenerative', 3, (), (('Nickel', 1), ('Conductive Components', 1), ('Electrochemical Arrays', 1),), ()),
    ('Burst Laser', 'Regenerative', 4, (), (('Electrochemical Arrays', 1), ('Conductive Ceramics', 1), ('Polymer Capacitors', 1), ('Refined Focus Crystals', 1),), ()),
    ('Burst Laser', 'Regenerative', 5, (), (('Polymer Capacitors', 1), ('Conductive Polymers', 1), ('Modified Embedded Firmware', 1), ('Shielding Sensors', 1),), ()),
    ('Rail Gun', 'Enduring Feedback', 2, (), (('Mechanical Scrap', 1), ('Sulphur', 1), ('Modified Consumer Firmware', 1),), ()),
    ('Rail Gun', 'Enduring Feedback', 3, (), (('Sulphur', 1), ('Modified Consumer Firmware', 1), ('Niobium', 1),), ()),
    ('Rail Gun', 'Enduring Feedback', 4, (), (('Modified Consumer Firmware', 1), ('Niobium', 1), ('Conductive Polymers', 1), ('Tin', 1),), ()),
    ('Rail Gun', 'Enduring Feedback', 5, (), (('Mechanical Components', 1), ('Thermic Alloys', 1), ('Military Supercapacitors', 1), ('Biotech Conductors', 1),), ()),
    ('Surface Scanner', 'Long Range', 2, (), (('Mechanical Scrap', 1), ('Germanium', 1), ('Modified Consumer Firmware', 1),), ()),
    ('Surface Scanner', 'Long Range', 3, (), (('Mechanical Scrap', 1), ('Germanium', 1), ('Phase Alloys', 1),), ()),
    ('Surface Scanner', 'Long Range', 4, (), (('Mechanical Equipment', 1), ('Niobium', 1), ('Phase Alloys', 1), ('Proto Light Alloys', 1),), ()),
    ('Surface Scanner', 'Long Range', 5, (), (('Mechanical Equipment', 1), ('Mechanical Components', 1), ('Tin', 1), ('Proto Radiolic Alloys', 1),), ()),
    ('Module Reinforcement Package', 'Heavy Duty', 2, (), (('Carbon', 1), ('Iron', 1), ('Shield Emitters', 1),), ()),
    ('Module Reinforcement Package', 'Heavy Duty', 3, (), (('Iron', 1), ('Shield Emitters', 1), ('High Density Composites', 1),), ()),
    ('Module Reinforcement Package', 'Heavy Duty', 4, (), (('Shield Emitters', 1), ('High Density Composites', 1), ('Proprietary Composites', 1), ('Tungsten', 1),), ()),
    ('Module Reinforcement Package', 'Heavy Duty', 5, (), (('Compound Shielding', 1), ('Ruthenium', 1), ('Proto Heat Radiators', 1), ('Core Dynamics Composites', 1),), ()),
    ('Cargo Rack', 'Extended Cargo Rack', 2, (), (('Mechanical Scrap', 1), ('Vanadium', 1), ('Manganese', 1),), ()),
    ('Cargo Rack', 'Extended Cargo Rack', 3, (), (('Mechanical Scrap', 1), ('Vanadium', 1), ('Niobium', 1),), ()),
    ('Cargo Rack', 'Extended Cargo Rack', 4, (), (('Mechanical Equipment', 1), ('High Density Composites', 1), ('Tin', 1), ('Niobium', 1),), ()),
    ('Cargo Rack', 'Extended Cargo Rack', 5, (), (('Mechanical Equipment', 1), ('Mechanical Components', 1), ('Proprietary Composites', 1), ('Military Supercapacitors', 1),), ()),
    ('Mining Laser', 'Far-Reaching', 2, (), (('Sulphur', 1), ('Heat Dispersion Plate', 1), ('Modified Consumer Firmware', 1),), ()),
    ('Mining Laser', 'Far-Reaching', 3, (), (('Chromium', 1), ('Modified Consumer Firmware', 1), ('Heat Exchangers', 1),), ()),
    ('Mining Laser', 'Far-Reaching', 4, (), (('Modified Consumer Firmware', 1), ('Conductive Polymers', 1), ('Selenium', 1), ('Heat Vanes', 1),), ()),
    ('Mining Laser', 'Far-Reaching', 5, (), (('Cracked Industrial Firmware', 1), ('Thermic Alloys', 1), ('Biotech Conductors', 1), ('Proto Heat Radiators', 1),), ()),
    ('Abrasion Blaster', 'Far-Reaching', 2, (), (('Sulphur', 1), ('Heat Dispersion Plate', 1), ('Modified Consumer Firmware', 1),), ()),
    ('Abrasion Blaster', 'Far-Reaching', 3, (), (('Chromium', 1), ('Modified Consumer Firmware', 1), ('Heat Exchangers', 1),), ()),
    ('Abrasion Blaster', 'Far-Reaching', 4, (), (('Modified Consumer Firmware', 1), ('Conductive Polymers', 1), ('Selenium', 1), ('Heat Vanes', 1),), ()),
    ('Abrasion Blaster', 'Far-Reaching', 5, (), (('Cracked Industrial Firmware', 1), ('Thermic Alloys', 1), ('Biotech Conductors', 1), ('Proto Heat Radiators', 1),), ()),
    ('Mining Laser', 'Long Range Mining Laser', 2, (), (('Sulphur', 1), ('Heat Dispersion Plate', 1), ('Modified Consumer Firmware', 1),), ()),
    ('Mining Laser', 'Long Range Mining Laser', 3, (), (('Chromium', 1), ('Modified Consumer Firmware', 1), ('Heat Exchangers', 1),), ()),
    ('Mining Laser', 'Long Range Mining Laser', 4, (), (('Modified Consumer Firmware', 1), ('Conductive Polymers', 1), ('Selenium', 1), ('Heat Vanes', 1),), ()),
    ('Mining Laser', 'Long Range Mining Laser', 5, (), (('Cracked Industrial Firmware', 1), ('Thermic Alloys', 1), ('Biotech Conductors', 1), ('Proto Heat Radiators', 1),), ()),
    ('Abrasion Blaster', 'Long Range Mining Laser', 2, (), (('Sulphur', 1), ('Heat Dispersion Plate', 1), ('Modified Consumer Firmware', 1),), ()),
    ('Abrasion Blaster', 'Long Range Mining Laser', 3, (), (('Chromium', 1), ('Modified Consumer Firmware', 1), ('Heat Exchangers', 1),), ()),
    ('Abrasion Blaster', 'Long Range Mining Laser', 4, (), (('Modified Consumer Firmware', 1), ('Conductive Polymers', 1), ('Selenium', 1), ('Heat Vanes', 1),), ()),
    ('Abrasion Blaster', 'Long Range Mining Laser', 5, (), (('Cracked Industrial Firmware', 1), ('Thermic Alloys', 1), ('Biotech Conductors', 1), ('Proto Heat Radiators', 1),), ()),
    ('Power Plant', 'Anti-Guardian Zone Resistance', 1, (), (('Hardened Surface Fragments', 2), ('Caustic Crystal', 1), ('Tactical Core Chip', 1),), ()),
    ('Power Distributor', 'Anti-Guardian Zone Resistance', 1, (), (('Hardened Surface Fragments', 2), ('Caustic Crystal', 1), ('Tactical Core Chip', 1),), ()),
    ('Hull Reinforcement Package', 'Anti-Guardian Zone Resistance', 1, (), (('Hardened Surface Fragments', 2), ('Caustic Crystal', 1), ('Tactical Core Chip', 1),), ()),
    ('Module Reinforcement Package', 'Anti-Guardian Zone Resistance', 1, (), (('Hardened Surface Fragments', 2), ('Caustic Crystal', 1), ('Tactical Core Chip', 1),), ()),
    ('Guardian Gauss Cannon', 'Anti-Guardian Zone Resistance', 1, (), (('Hardened Surface Fragments', 2), ('Caustic Crystal', 1), ('Tactical Core Chip', 1),), ()),
    ('Guardian Plasma Charger', 'Anti-Guardian Zone Resistance', 1, (), (('Hardened Surface Fragments', 2), ('Caustic Crystal', 1), ('Tactical Core Chip', 1),), ()),
    ('Guardian Shard Cannon', 'Anti-Guardian Zone Resistance', 1, (), (('Hardened Surface Fragments', 2), ('Caustic Crystal', 1), ('Tactical Core Chip', 1),), ()),
    ('Mining Laser', 'Long Range Weapon', 1, (), (('Sulphur', 1),), ()),
    ('Mining Laser', 'Long Range Weapon', 2, (), (('Sulphur', 1), ('Modified Consumer Firmware', 1),), ()),
    ('Mining Laser', 'Long Range Weapon', 3, (), (('Sulphur', 1), ('Modified Consumer Firmware', 1), ('Focus Crystals', 1),), ()),
    ('Mining Laser', 'Long Range Weapon', 4, (), (('Modified Consumer Firmware', 1), ('Focus Crystals', 1), ('Conductive Polymers', 1),), ()),
    ('Mining Laser', 'Long Range Weapon', 5, (), (('Cracked Industrial Firmware', 1), ('Thermic Alloys', 1), ('Biotech Conductors', 1),), ()),
    ('Abrasion Blaster', 'Long Range Weapon', 1, (), (('Sulphur', 1),), ()),
    ('Abrasion Blaster', 'Long Range Weapon', 2, (), (('Sulphur', 1), ('Modified Consumer Firmware', 1),), ()),
    ('Abrasion Blaster', 'Long Range Weapon', 3, (), (('Sulphur', 1), ('Modified Consumer Firmware', 1), ('Focus Crystals', 1),), ()),
    ('Abrasion Blaster', 'Long Range Weapon', 4, (), (('Modified Consumer Firmware', 1), ('Focus Crystals', 1), ('Conductive Polymers', 1),), ()),
    ('Abrasion Blaster', 'Long Range Weapon', 5, (), (('Cracked Industrial Firmware', 1), ('Thermic Alloys', 1), ('Biotech Conductors', 1),), ()),
)

EDSY_JOURNAL_NAMES: Dict[str, Dict[str, str]] = {
    'PowerDistributor_Balanced': {'Power Distributor': 'Balanced'},
    'PowerDistributor_SupportFocused': {'Power Distributor': 'Support Focused'},
    'FuelScoop_ScoopRateEnhanced': {'Fuel Scoop': 'Scoop Rate Enhanced'},
    'Weapon_DoubleScreaming': {'Fragment Cannon': 'Double Screaming'},
    'Weapon_DragSeeker': {'Missile Rack': 'Drag Seeker'},
    'Weapon_LightweightThermalSeeker': {'Missile Rack': 'Lightweight Thermal Seeker'},
    'Weapon_LockdownSeeker': {'Missile Rack': 'Lockdown'},
    'BeamLaser_Overloaded': {'Beam Laser': 'Overloaded'},
    'Weapon_PlasmaConversion': {'Beam Laser': 'Plasma Conversion', 'Burst Laser': 'Plasma Conversion', 'Pulse Laser': 'Plasma Conversion'},
    'Weapon_RapidPhase': {'Multi-cannon': 'Rapid Phase'},
    'BurstLaser_Regenerative': {'Burst Laser': 'Regenerative'},
    'Weapon_EnduringFeedback': {'Rail Gun': 'Enduring Feedback'},
    'Sensor_LongRangeDSS': {'Surface Scanner': 'Long Range'},
    'MRP_HeavyDuty': {'Module Reinforcement Package': 'Heavy Duty'},
    'CargoRack_Extended': {'Cargo Rack': 'Extended Cargo Rack'},
    'Weapon_FarReaching': {'Mining Laser': 'Far-Reaching', 'Abrasion Blaster': 'Far-Reaching'},
    'Weapon_LongRangeMiningLaser': {'Mining Laser': 'Long Range Mining Laser', 'Abrasion Blaster': 'Long Range Mining Laser'},
    'GuardianModule_Sturdy': {'Power Plant': 'Anti-Guardian Zone Resistance', 'Power Distributor': 'Anti-Guardian Zone Resistance', 'Hull Reinforcement Package': 'Anti-Guardian Zone Resistance', 'Module Reinforcement Package': 'Anti-Guardian Zone Resistance', 'Guardian Gauss Cannon': 'Anti-Guardian Zone Resistance', 'Guardian Plasma Charger': 'Anti-Guardian Zone Resistance', 'Guardian Shard Cannon': 'Anti-Guardian Zone Resistance'},
    'Weapon_LongRange': {'Mining Laser': 'Long Range Weapon', 'Abrasion Blaster': 'Long Range Weapon'},
}
