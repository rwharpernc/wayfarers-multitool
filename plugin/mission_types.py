"""
Classifies missions into the categories the Missions mode panel scrolls
through.

Elite Dangerous embeds mission type information in the internal `Name`
field as underscore-separated tags (e.g. "Mission_Massacre_Onslaught",
"Mission_Delivery_Illegal_MB"). This is undocumented by Frontier, but the
tag vocabulary is well established in the community.
"""

MASSACRE_SPACE = "massacre_space"
MASSACRE_GROUND = "massacre_ground"
COMBAT = "combat"
TRADE = "trade"
PASSENGER = "passenger"
COVERT = "covert"
OTHER = "other"

CATEGORY_LABELS: dict[str, str] = {
    MASSACRE_SPACE: "Massacre (Space)",
    MASSACRE_GROUND: "Settlement Raids (Ground)",
    COMBAT: "Combat",
    TRADE: "Trade & Mining",
    PASSENGER: "Passenger",
    COVERT: "Covert / On-Foot Ops",
    OTHER: "Other",
}

CATEGORY_ORDER: list[str] = [
    MASSACRE_SPACE, MASSACRE_GROUND, COMBAT, TRADE, PASSENGER, COVERT, OTHER,
]

_MASSACRE_HINTS = ("massacre", "onslaught", "raid")
_COMBAT_HINTS = ("assassinate", "assassination", "disable", "skimmer", "conflict",
                 "blops", "piracy", "scout", "thargoid", "terminalprosecution",
                 "tacticaltakedown", "reclamationpoint", "biohazardtakedown",
                 "rapidresponse")
_TRADE_HINTS = ("delivery", "courier", "collect", "mining", "salvage",
                "communitygoal", "smuggle")
_PASSENGER_HINTS = ("passenger", "sightseeing", "vip", "bulk", "evacuation",
                    "polprisoner")
_COVERT_HINTS = ("hack", "covert", "heist", "sabotage", "reboot", "download",
                 "upload", "poi", "productionheist", "theft", "power",
                 "production", "ncd")
_ILLEGAL_HINTS = ("illegal", "smuggle")


def is_ground_mission(event: dict) -> bool:
    """
    On-foot missions have "OnFoot" in the internal name; settlement-targeted
    missions also carry a DestinationSettlement field.
    """
    return "onfoot" in event.get("Name", "").lower() \
        or bool(event.get("DestinationSettlement"))


def is_massacre_shaped(event: dict) -> bool:
    """
    Matches any mission whose objective is killing members of a faction:
    ship massacre missions (Mission_Massacre, Mission_MassacreWing, ...),
    on-foot massacre missions, and settlement raids (Mission_OnFoot_Onslaught*).

    Primary signal is the mission shape - a kill count against a target
    faction - so mission types with unexpected internal names still match.
    Name hints catch known variants that might omit one of the fields.
    """
    if event.get("KillCount") and event.get("TargetFaction"):
        return True
    name = event.get("Name", "").lower()
    return any(hint in name for hint in _MASSACRE_HINTS)


def is_illegal(event: dict) -> bool:
    name = event.get("Name", "").lower()
    return any(hint in name for hint in _ILLEGAL_HINTS)


def is_colonization_mission(event: dict) -> bool:
    """True for missions accepted in support of a colonization effort
    (Mission_ColonisationDelivery, Mission_ColonisationBeacon, ...) -
    excluded from every mission page entirely rather than bucketed into a
    category."""
    name = event.get("Name", "").lower()
    return "colonisation" in name or "colonization" in name      # game spelling (colonisation) and ours; both are matched


def is_mining_mission(event: dict) -> bool:
    """
    True only for missions that require *mining* a commodity yourself
    (Mission_Mining, Mission_Mining_Expansion, ...) - deliberately narrower
    than "has a Commodity field", which Collect/Delivery missions also
    carry (confirmed from a live journal: Mission_Collect_Industrial
    commonly targets genuinely mineable commodities like Pyrophyllite or
    Cryolite, but those are bought/collected, not mined). Showing a mining
    hint on one of those would be actively wrong, not just unhelpful.
    """
    return "mining" in event.get("Name", "").lower()


ACCEPTED_AT = "WFMT_AcceptedAt"
"""A key WFMT adds to a MissionAccepted event it keeps: the name of the station the commander was docked at when they took the mission
(empty when not docked). The game's own event does not say, and a Delivery mission's cargo is picked up at that station."""

ACCEPTED_PAD = "WFMT_AcceptedPad"
"""Added the same way as ACCEPTED_AT: the largest landing pad of that station ("Large", "Medium" or "Small"), from the `LandingPads` counts on the journal's
`Docked` event; empty when the event gave none."""


def largest_pad_of(landing_pads) -> str:
    """"Large", "Medium" or "Small" from a `Docked` event's `LandingPads` ({"Small": 2, "Medium": 1, "Large": 0}), or "" when it has none."""
    if not isinstance(landing_pads, dict):
        return ""
    for size in ("Large", "Medium", "Small"):
        count = landing_pads.get(size)
        if isinstance(count, (int, float)) and not isinstance(count, bool) and count > 0:
            return size
    return ""


_NO_PICKUP_HINTS = ("onfoot", "colonisation", "colonization", "wing", "rank", "cooperative")      # game spelling: the mission names say colonisation
"""Delivery variants left out of the pickup rule: on-foot goods and colonization are handled elsewhere, and in one commander's journals
no wing, rank or cooperative delivery ever showed its cargo being collected, so nothing is known about how they are supplied."""


def needs_commodity_supply(event: dict) -> bool:
    """True for missions where the commander must source the commodity themselves from a market - mining it, or buying/collecting
    it (Collect and Mining missions). Delivery missions are not here: see `is_pickup_delivery`."""
    name = event.get("Name", "").lower()
    return "mining" in name or "collect" in name


def is_pickup_delivery(event: dict) -> bool:
    """True for a Delivery mission whose cargo is picked up at the station that gave the mission, not bought.

    The faction hands the goods over, but when varies: war-supplies deliveries and most others get a `CargoDepot` "Collect" event within
    seconds of acceptance, and others only when the commander collects the cargo at that station later (two "Deliver ... Personal
    Weapons" missions were collected 26 minutes after acceptance, with no purchase). In 23 collected `Mission_Delivery` and related
    missions across one commander's journals the pickup station was the station where the mission was accepted every time. Buying the
    goods on a market is the wrong answer for these, so Source commodities points at the station instead."""
    name = event.get("Name", "").lower()
    return ("delivery" in name and not any(hint in name for hint in _NO_PICKUP_HINTS)
            and bool(event.get("Commodity")) and (event.get("Count") or 0) > 0)


def classify(event: dict) -> str:
    """Bucket a MissionAccepted event into one of the panel's category pages."""
    if is_massacre_shaped(event):
        return MASSACRE_GROUND if is_ground_mission(event) else MASSACRE_SPACE

    name = event.get("Name", "").lower()
    if any(hint in name for hint in _COMBAT_HINTS):
        return COMBAT
    if any(hint in name for hint in _TRADE_HINTS):
        return TRADE
    if any(hint in name for hint in _PASSENGER_HINTS):
        return PASSENGER
    if any(hint in name for hint in _COVERT_HINTS) or is_ground_mission(event):
        return COVERT
    return OTHER
