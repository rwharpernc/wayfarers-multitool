"""The Combat Record: kills and deaths counted per ship and per session (combat_record.py).

The events here are synthetic, with the field shapes the game writes. Run with: python -m unittest discover -s tests
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugin import combat_record as C  # noqa: E402

CMDR = "Test Pilot"
PYTHON = {"event": "LoadGame", "Commander": CMDR, "Ship": "python", "ShipID": 4, "ShipName": "Viper Bait", "ShipIdent": "VB-01"}


def at(seconds, entry):
    entry = dict(entry)
    entry["timestamp"] = "2026-10-20T10:00:%02dZ" % seconds
    return entry


def bounty(seconds, reward=1000, target="anaconda", **extra):
    return at(seconds, dict({"event": "Bounty", "Target": target, "TotalReward": reward, "VictimFaction": "Pirates"}, **extra))


def bond(seconds, reward=5000):
    return at(seconds, {"event": "FactionKillBond", "Reward": reward, "AwardingFaction": "A", "VictimFaction": "B"})


def died(seconds):
    return at(seconds, {"event": "Died", "KillerName": "Someone"})


def fresh(session="Journal.1.log"):
    book = C.CombatBook()
    book.logfile = lambda: session
    book.set_commander(CMDR, folder=tempfile.mkdtemp(), wait=True)
    return book


def feed(book, *events):
    for entry in events:
        book.handle(entry, CMDR)


class PureTests(unittest.TestCase):
    def test_delta_for(self):
        self.assertEqual(C.delta_for(bounty(1, 2500)), {"kills": 1, "reward": 2500})
        self.assertEqual(C.delta_for(at(1, {"event": "Bounty", "Reward": 700})), {"kills": 1, "reward": 700})
        self.assertEqual(C.delta_for(at(1, {"event": "Bounty", "Rewards": [{"Reward": 100}, {"Reward": 50}]})), {"kills": 1, "reward": 150})
        self.assertEqual(C.delta_for(bond(1, 9)), {"kills": 1, "reward": 9})
        self.assertEqual(C.delta_for(at(1, {"event": "PVPKill"})), {"pvp": 1})
        self.assertEqual(C.delta_for(died(1)), {"deaths": 1})
        self.assertIsNone(C.delta_for(at(1, {"event": "FSDJump"})))

    def test_bad_numbers_never_count(self):
        self.assertEqual(C.delta_for(at(1, {"event": "Bounty", "TotalReward": -5})), {"kills": 1, "reward": 0})
        self.assertEqual(C.delta_for(at(1, {"event": "Bounty", "TotalReward": True})), {"kills": 1, "reward": 0})
        self.assertEqual(C.clean_tally({"kills": "x", "deaths": -1, "pvp": 2.5, "reward": 7}), {"kills": 0, "pvp": 0, "deaths": 0, "reward": 7})

    def test_ratio_and_summary(self):
        self.assertEqual(C.ratio_text({"kills": 6, "pvp": 2, "deaths": 4}), "2.0")
        self.assertEqual(C.ratio_text({"kills": 6, "deaths": 0}), "-")
        self.assertEqual(C.summary_text({"kills": 1, "deaths": 1}), "1 kill, 1 death, K/D 1.0")
        self.assertEqual(C.summary_text({"kills": 12, "pvp": 3, "deaths": 0}), "12 kills, 3 PvP, 0 deaths, K/D -")

    def test_craft_follows_the_vessel(self):
        craft = C.Craft()
        craft.see(PYTHON)
        self.assertEqual(craft.key_for(bounty(1)), "python#4")
        craft.see(at(2, {"event": "Disembark", "SRV": False, "OnPlanet": True}))
        self.assertEqual(craft.key_for(died(3)), "foot")
        craft.see(at(4, {"event": "Embark", "SRV": True}))
        self.assertEqual(craft.key_for(bounty(5)), "srv")
        craft.see(at(6, {"event": "DockSRV"}))
        self.assertEqual(craft.key_for(bounty(7)), "python#4")
        craft.see(at(8, {"event": "ShipyardSwap", "ShipType": "federation_corvette", "ShipID": 9}))
        self.assertEqual(craft.key_for(bounty(9)), "federation_corvette#9")
        self.assertEqual(craft.key_for(bounty(9, target="suitai_scientist")), "foot")     # a ground target is an on-foot kill whatever the tracker believes

    def test_renaming_keeps_one_row(self):
        craft = C.Craft()
        craft.see(PYTHON)
        craft.see({"event": "SetUserShipName", "Ship": "python", "ShipID": 4, "UserShipName": "Renamed", "UserShipId": "RN-99"})
        self.assertEqual((craft.key_for(bounty(1)), craft.name, craft.ident), ("python#4", "Renamed", "RN-99"))
        craft.see({"event": "SetUserShipName", "Ship": "python", "ShipID": 5, "UserShipName": "Other", "UserShipId": "OT-01"})
        self.assertEqual(craft.name, "Renamed")

    def test_the_games_own_ship_name_is_kept(self):
        craft = C.Craft()
        craft.see({"event": "Loadout", "Ship": "newship_nx", "Ship_Localised": "Shiny Thing", "ShipID": 2, "ShipName": "", "ShipIdent": ""})
        self.assertEqual(C.ship_label(craft.meta(craft.key_for(bounty(1)))), "Shiny Thing")
        craft.see({"event": "ShipyardSwap", "ShipType": "other_nx", "ShipType_Localised": "Other Thing", "ShipID": 3})
        self.assertEqual(C.ship_label(craft.meta(craft.key_for(bounty(1)))), "Other Thing")

    def test_adopt_takes_edmcs_ship_only_when_none_is_known(self):
        craft = C.Craft()
        craft.adopt({"ShipType": "Anaconda", "ShipID": 2, "ShipName": "Big", "ShipIdent": "BG-01"})
        self.assertEqual((craft.type, craft.id), ("anaconda", 2))
        craft.adopt({"ShipType": "python", "ShipID": 9})
        self.assertEqual(craft.type, "anaconda")

    def test_labels(self):
        self.assertEqual(C.ship_label({"type": "foot"}), "On foot")
        self.assertEqual(C.ship_label({"type": "federation_corvette"}), "Federal Corvette")
        self.assertEqual(C.ship_label({"type": "anacondamkii"}), "Anaconda Mk II")           # no Ship_Localised in the journal: the table names it
        self.assertEqual(C.ship_label({"type": "smallcombat01_nx"}), "Kestrel Mk II")         # a codename
        self.assertEqual(C.ship_label({"type": "brand_new_ship"}), "Brand New Ship")          # unknown: words, never the raw string
        self.assertEqual(C.ship_label({"type": "brand_new_ship", "kind": "Shiny Thing"}), "Shiny Thing")   # the game's own name wins
        self.assertEqual(C.ship_title({"name": "Star", "ident": "S-1"}), "Star [S-1]")
        self.assertEqual(C.ship_title({"name": "", "ident": ""}), "")


class BookTests(unittest.TestCase):
    def test_kills_and_deaths_are_counted_per_ship_and_per_session(self):
        book = fresh()
        feed(book, at(0, PYTHON), bounty(1, 1000), bond(2, 500), died(3),
              at(4, {"event": "ShipyardSwap", "ShipType": "asp", "ShipID": 7}), bounty(5, 300), at(6, {"event": "PVPKill", "Victim": "Rival"}))
        self.assertEqual(book.total(CMDR), {"kills": 3, "pvp": 1, "deaths": 1, "reward": 1800})
        rows = {r["key"]: r for r in book.ship_rows(CMDR)}
        self.assertEqual(rows["python#4"]["tally"], {"kills": 2, "pvp": 0, "deaths": 1, "reward": 1500})
        self.assertEqual((rows["python#4"]["name"], rows["python#4"]["ident"]), ("Viper Bait", "VB-01"))
        self.assertEqual(rows["asp#7"]["tally"], {"kills": 1, "pvp": 1, "deaths": 0, "reward": 300})
        self.assertEqual(book.session_id, "Journal.1.log")
        self.assertEqual(book.session_total(CMDR, "Journal.1.log"), book.total(CMDR))
        self.assertEqual(len(book.ship_rows(CMDR, "Journal.1.log")), 2)

    def test_a_second_session_leaves_the_first_alone_and_the_totals_add_up(self):
        book = fresh("Journal.1.log")
        feed(book, at(0, PYTHON), bounty(1), died(2))
        book.logfile = lambda: "Journal.2.log"
        feed(book, at(10, PYTHON), bounty(11), bounty(12))
        self.assertEqual(book.session_id, "Journal.2.log")
        self.assertEqual(book.session_total(CMDR, "Journal.1.log")["kills"], 1)
        self.assertEqual(book.session_total(CMDR, "Journal.2.log")["kills"], 2)
        self.assertEqual(book.total(CMDR)["kills"], 3)
        self.assertEqual([s["id"] for s in book.sessions(CMDR)], ["Journal.2.log", "Journal.1.log"])

    def test_the_same_event_twice_counts_once_but_two_alike_in_one_second_count_twice(self):
        book = fresh()
        feed(book, at(0, PYTHON), bounty(1, 100), bounty(1, 100, VictimFaction="Other"))
        self.assertEqual(book.total(CMDR)["kills"], 2)
        feed(book, bounty(1, 100))                      # the first again
        self.assertEqual(book.total(CMDR)["kills"], 2)
        feed(book, bounty(0, 100))                      # older than the newest counted
        self.assertEqual(book.total(CMDR)["kills"], 2)

    def test_nothing_is_counted_before_a_commander_is_known(self):
        book = C.CombatBook()
        self.assertFalse(book.handle(bounty(1), CMDR))
        self.assertEqual(book.total(CMDR), C.new_tally())

    def test_ship_unknown_to_the_journal_uses_edmcs_state(self):
        book = fresh()
        book.handle(bounty(1), CMDR, {"ShipType": "cobramkiii", "ShipID": 3, "ShipName": "Cobby", "ShipIdent": "CB-01"})
        self.assertEqual([r["key"] for r in book.ship_rows(CMDR)], ["cobramkiii#3"])

    def test_a_kill_with_no_known_ship_goes_to_unknown(self):
        book = fresh()
        feed(book, bounty(1))
        self.assertEqual([r["key"] for r in book.ship_rows(CMDR)], [C.UNKNOWN])

    def test_commanders_are_kept_apart(self):
        book = fresh()
        feed(book, at(0, PYTHON), bounty(1))
        self.assertEqual(book.total("Someone Else"), C.new_tally())
        self.assertEqual(book.ship_rows("Someone Else"), [])
        self.assertEqual(book.sessions("Someone Else"), [])

    def test_saved_and_loaded_again(self):
        folder = tempfile.mkdtemp()
        book = C.CombatBook()
        book.logfile = lambda: "Journal.1.log"
        book.load(folder)
        book.set_commander(CMDR, folder=tempfile.mkdtemp(), wait=True)
        feed(book, at(0, PYTHON), bounty(1, 40), died(2))
        again = C.CombatBook()
        again.load(folder)
        self.assertEqual(again.total(CMDR), {"kills": 1, "pvp": 0, "deaths": 1, "reward": 40})
        self.assertEqual(again.ship_rows(CMDR)[0]["name"], "Viper Bait")
        with open(os.path.join(folder, C.STATE_FILENAME), encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["version"], 2)

    def test_a_damaged_file_gives_an_empty_book(self):
        folder = tempfile.mkdtemp()
        with open(os.path.join(folder, C.STATE_FILENAME), "w", encoding="utf-8") as handle:
            handle.write('{"version": 2, "commanders": {"test pilot": {"name": "Test Pilot", "data": {"total": 5, "ships": [], "sessions": {}}}}}')
        book = C.CombatBook()
        book.load(folder)
        self.assertEqual(book.total(CMDR), C.new_tally())
        self.assertEqual(book.ship_rows(CMDR), [])

    def test_sessions_are_limited_but_the_totals_are_not(self):
        book = fresh()
        for number in range(C.MAX_SESSIONS + 5):
            book.logfile = lambda number=number: f"Journal.{number}.log"
            book._session_id = ""
            feed(book, at(0, dict(PYTHON)))
            feed(book, dict(bounty(1), timestamp="2026-10-20T10:%02d:%02dZ" % divmod(number, 60)))
        self.assertEqual(len(book.sessions(CMDR)), C.MAX_SESSIONS)
        self.assertEqual(book.total(CMDR)["kills"], C.MAX_SESSIONS + 5)


def dated(day, events):
    """The events moved to 2026-10-<day>, as the game's journals run forward in time."""
    return [dict(entry, timestamp="2026-10-%02d" % day + entry["timestamp"][10:]) for entry in events]


class JournalTests(unittest.TestCase):
    def write(self, folder, name, events, mtime):
        path = os.path.join(folder, name)
        with open(path, "w", encoding="utf-8") as handle:
            for entry in events:
                handle.write(json.dumps(entry) + "\n")
        os.utime(path, (mtime, mtime))
        return path

    def journals(self):
        folder = tempfile.mkdtemp()
        other = {"event": "LoadGame", "Commander": "Other Pilot", "Ship": "asp", "ShipID": 1, "ShipName": "", "ShipIdent": ""}
        self.write(folder, "Journal.2026-10-01T100000.01.log",
                   dated(1, [at(0, {"event": "Commander", "Name": CMDR}), at(1, PYTHON), bounty(2, 100), died(3), at(4, {"event": "FSDJump"})]), 1000)
        self.write(folder, "Journal.2026-10-02T100000.01.log",
                   dated(2, [at(0, {"event": "Commander", "Name": "Other Pilot"}), at(1, other), bounty(2, 999), bounty(3, 999)]), 2000)
        self.write(folder, "Journal.2026-10-03T100000.01.log",
                   [dict(at(0, {"event": "Commander", "Name": CMDR}), timestamp="2026-10-03T10:00:00Z"), dict(PYTHON, timestamp="2026-10-03T10:00:01Z"),
                    dict(bounty(2, 50), timestamp="2026-10-03T10:00:02Z"), dict(at(3, {"event": "Disembark", "SRV": False}), timestamp="2026-10-03T10:00:03Z"),
                    dict(died(4), timestamp="2026-10-03T10:00:04Z")], 3000)
        return folder

    def test_every_journal_is_read_once_for_this_commander_only(self):
        folder = self.journals()
        book = C.CombatBook()
        book.set_commander(CMDR, folder=folder, wait=True)
        self.assertEqual(book.total(CMDR), {"kills": 2, "pvp": 0, "deaths": 2, "reward": 150})
        self.assertEqual({r["key"] for r in book.ship_rows(CMDR)}, {"python#4", "foot"})
        self.assertEqual([s["id"] for s in book.sessions(CMDR)], ["Journal.2026-10-03T100000.01.log", "Journal.2026-10-01T100000.01.log"])
        self.assertEqual(book.total("Other Pilot"), C.new_tally())     # nothing was read for another commander

    def test_reading_again_counts_nothing_twice(self):
        folder, plugin_dir = self.journals(), tempfile.mkdtemp()
        book = C.CombatBook()
        book.load(plugin_dir)
        book.set_commander(CMDR, folder=folder, wait=True)
        before = book.total(CMDR)
        book.set_commander(CMDR, folder=folder, wait=True, force=True)
        self.assertEqual(book.total(CMDR), before)
        later = C.CombatBook()
        later.load(plugin_dir)
        later.set_commander(CMDR, folder=folder, wait=True)
        self.assertEqual(later.total(CMDR), before)

    def test_rebuild_gives_the_same_record(self):
        folder = self.journals()
        book = C.CombatBook()
        book.set_commander(CMDR, folder=folder, wait=True)
        before = book.total(CMDR)
        book.rebuild(CMDR, folder=folder, wait=True)
        self.assertEqual(book.total(CMDR), before)

    def test_live_events_that_arrive_during_the_read_are_counted_once(self):
        folder = self.journals()
        current = self.write(folder, "Journal.2026-10-04T100000.01.log",
                             [dict(at(0, {"event": "Commander", "Name": CMDR}), timestamp="2026-10-04T10:00:00Z"), dict(PYTHON, timestamp="2026-10-04T10:00:01Z"),
                              dict(bounty(2), timestamp="2026-10-04T10:00:02Z")], 4000)
        book = C.CombatBook()
        book.logfile = lambda: os.path.basename(current)
        book.set_commander(CMDR, folder=folder)           # the read runs in the background
        book.handle(dict(bounty(2), timestamp="2026-10-04T10:00:02Z"), CMDR)     # the game's event for a kill the journal read also holds
        book.handle(dict(bounty(5), timestamp="2026-10-04T10:00:05Z"), CMDR)
        book._thread.join()
        self.assertEqual(book.total(CMDR)["kills"], 4)        # one in each of two older journals, one in the current journal (also sent live) and the live one at :05
        self.assertEqual(book.session_total(CMDR, os.path.basename(current))["kills"], 2)

    def test_the_vessel_at_the_end_of_the_current_journal_carries_on_live(self):
        folder = tempfile.mkdtemp()
        current = self.write(folder, "Journal.2026-10-04T100000.01.log",
                             [dict(at(0, {"event": "Commander", "Name": CMDR}), timestamp="2026-10-04T10:00:00Z"), dict(PYTHON, timestamp="2026-10-04T10:00:01Z"),
                              dict(at(2, {"event": "Disembark", "SRV": False}), timestamp="2026-10-04T10:00:02Z")], 4000)
        book = C.CombatBook()
        book.logfile = lambda: os.path.basename(current)
        book.set_commander(CMDR, folder=folder, wait=True)
        book.handle(dict(died(9), timestamp="2026-10-04T10:00:09Z"), CMDR)
        self.assertEqual([r["key"] for r in book.ship_rows(CMDR)], ["foot"])

    def test_a_missing_journal_folder_is_not_an_error(self):
        book = C.CombatBook()
        book.set_commander(CMDR, folder=os.path.join(tempfile.mkdtemp(), "nowhere"), wait=True)
        self.assertEqual(book.total(CMDR), C.new_tally())
        self.assertFalse(book.reading)


if __name__ == "__main__":
    unittest.main()
