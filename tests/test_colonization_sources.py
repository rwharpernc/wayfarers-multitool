"""Where-to-buy search for colonization commodities (colonization_sources.py), with Spansh replaced by a stand-in."""
from __future__ import annotations

import dataclasses
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key: "", default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import colonization_sources as src  # noqa: E402
from plugin.mining_spansh_client import StationPrice  # noqa: E402


def item(name, ly, price=400, kind="Coriolis Starport", pads=(4, 4, 4), ls=500.0, qty=1000, planetary=False):
    small, medium, large = pads
    return StationPrice(station=name, system="Sys " + name, station_type=kind, distance_ly=ly,
                        distance_to_arrival_ls=ls, is_planetary=planetary, price=price, quantity=qty,
                        small_pads=small, medium_pads=medium, large_pads=large)


class FakeSpansh:
    """Records each call and answers from a table keyed by whether it asked for carriers."""

    def __init__(self, stations, carriers=()):
        self.stations, self.carriers, self.calls = list(stations), list(carriers), []

    def __call__(self, system, commodity, transaction, radius, **kwargs):
        self.calls.append((system, commodity, transaction, radius, kwargs))
        return list(self.carriers if kwargs.get("station_types") == ["Drake-Class Carrier"] else self.stations)


class LocalSpansh:
    """Answers a this-system-only search from `local`, and any other from `outside`."""

    def __init__(self, local, outside):
        self.local, self.outside, self.calls = list(local), list(outside), []

    def __call__(self, system, commodity, transaction, radius, **kwargs):
        self.calls.append((system, kwargs))
        return list(self.local if kwargs.get("this_system_only") else self.outside)


def local_item(name, system, price=900):
    return dataclasses.replace(item(name, 0.0, price=price), system=system)


class CurrentSystemFirstTests(unittest.TestCase):
    def setUp(self):
        src.clear_cache()

    def test_stock_in_the_current_system_is_the_answer_and_nothing_outside_is_searched(self):
        fake = LocalSpansh([local_item("Home Port", "Home")], [item("Far", 30, price=100)])
        result = src.find("Elsewhere", "Steel", sort=src.SORT_PRICE, search=fake, here="Home")
        self.assertEqual([s.station for s in result.stations], ["Home Port"])
        self.assertEqual(len(fake.calls), 1)
        self.assertTrue(fake.calls[0][1]["this_system_only"])

    def test_with_none_in_the_current_system_the_search_goes_out_closest_first(self):
        fake = LocalSpansh([], [item("Far", 30), item("Near", 5)])
        result = src.find("Home", "Steel", search=fake, here="Home")
        self.assertEqual([s.station for s in result.stations], ["Near", "Far"])

    def test_a_station_from_another_system_is_not_taken_for_the_current_one(self):
        fake = LocalSpansh([local_item("Other Port", "Other")], [item("Near", 5)])
        result = src.find("Home", "Steel", search=fake, here="Home")
        self.assertEqual([s.station for s in result.stations], ["Near"])


class WholeListCurrentSystemTests(unittest.TestCase):
    def setUp(self):
        src.clear_cache()

    def run_list(self, fake, one_stop=None, **kwargs):
        return src.find_whole_list("Sol", ["Steel", "Water"], search=fake, sleep=lambda _s: None, here="Home", one_stop=one_stop, **kwargs)

    def test_a_commodity_in_stock_at_home_is_answered_from_home_alone(self):
        fake = LocalSpansh([local_item("Home Port", "Home")], [item("Far", 30)])
        result = self.run_list(fake)
        for _label, found in result.found:
            self.assertEqual([s.station for s in found.stations], ["Home Port"])
            self.assertTrue(found.local)

    def test_a_one_stop_station_elsewhere_is_not_added_to_a_home_answer(self):
        fake = LocalSpansh([local_item("Home Port", "Home")], [])
        elsewhere = item("Hub", 10)
        one_stop = lambda *_a, **_k: [(elsewhere, {"Steel": (500, 900), "Water": (400, 900)})]   # noqa: E731
        result = self.run_list(fake, one_stop=one_stop)
        for _label, found in result.found:
            self.assertEqual([s.station for s in found.stations], ["Home Port"])

    def test_a_home_answer_from_the_one_stop_search_lists_only_home_stations(self):
        fake = LocalSpansh([], [])
        home_hub = local_item("Home Hub", "Home")
        elsewhere = item("Hub", 10)
        one_stop = lambda *_a, **_k: [(home_hub, {"Steel": (500, 900), "Water": (400, 900)}), (elsewhere, {"Steel": (500, 900), "Water": (400, 900)})]   # noqa: E731
        result = self.run_list(fake, one_stop=one_stop, needs={"Steel": 100, "Water": 100})
        for _label, found in result.found:
            self.assertTrue(found.local)
            self.assertEqual([s.station for s in found.stations], ["Home Hub"])

    def test_a_one_stop_home_station_the_filters_would_hide_does_not_stand_in(self):
        fake = LocalSpansh([], [item("Far", 30)])
        home_hub = local_item("Home Hub", "Home")   # no shipyard
        one_stop = lambda *_a, **_k: [(home_hub, {"Steel": (500, 900), "Water": (400, 900)})]   # noqa: E731
        result = self.run_list(fake, one_stop=one_stop, needs={"Steel": 100, "Water": 100}, filters=src.LocalFilter(shipyard_only=True))
        for _label, found in result.found:
            self.assertFalse(found.local)

    def test_without_stock_at_home_it_goes_out_as_before(self):
        fake = LocalSpansh([], [item("Far", 30), item("Near", 5)])
        result = self.run_list(fake)
        for _label, found in result.found:
            self.assertEqual([s.station for s in found.stations], ["Near", "Far"])
            self.assertFalse(found.local)


class SmallFixTests(unittest.TestCase):
    def setUp(self):
        src.clear_cache()

    def test_a_saved_preset_that_is_not_text_gives_way_to_the_default(self):
        for junk in ('[1]', '{"a": 1}', '5', 'null', 'true'):
            self.assertEqual(src.load_prefs('{"preset": %s, "radius": 50}' % junk).preset, src.DEFAULT_PRESET)

    def test_an_empty_answer_has_no_fall_back_note(self):
        result = src.find("Sol", "Steel", pad=src.PAD_LARGE_FIRST, search=FakeSpansh([]))
        self.assertEqual((result.stations, result.carriers, result.note), ([], [], ""))

    def test_the_filtered_answers_keep_the_local_flag_and_the_note(self):
        kept = src.filter_found([("Steel", src.SearchResult([], [], local=True, note="n"))])[0][1]
        self.assertEqual((kept.local, kept.note), (True, "n"))

    def test_the_orbital_check_keeps_the_fall_back_note(self):
        surface = item("Surface", 3, planetary=True, kind="Planetary Port", pads=(0, 0, 4))
        orbital = item("Orbit", 9, pads=(0, 4, 0))

        def search(system, commodity, transaction, radius, **kwargs):
            if kwargs.get("required_pad") == "large":
                return []
            return [orbital] if kwargs["station_types"] == src.trade_prices.station_types(False) else [surface]
        result = src.find_whole_list("Sol", ["Steel"], pad=src.PAD_LARGE_FIRST, search=search, sleep=lambda _s: None)
        found = result.found[0][1]
        self.assertIn("Orbit", [s.station for s in found.stations])
        self.assertEqual(found.note, src.MEDIUM_NOTE)


class LocalFilterTests(unittest.TestCase):
    def setUp(self):
        src.clear_cache()

    def test_a_local_station_the_filters_would_hide_does_not_stop_the_search(self):
        fake = LocalSpansh([local_item("Home Port", "Home")], [item("Hub", 12)])   # Home Port has no shipyard in this stand-in
        result = src.find("Home", "Steel", search=fake, here="Home", filters=src.LocalFilter(shipyard_only=True))
        self.assertFalse(result.local)
        self.assertIn("Hub", [s.station for s in result.stations])

    def test_a_local_station_that_passes_the_filters_is_the_answer(self):
        fake = LocalSpansh([dataclasses.replace(local_item("Home Port", "Home"), has_shipyard=True)], [item("Hub", 12)])
        result = src.find("Home", "Steel", search=fake, here="Home", filters=src.LocalFilter(shipyard_only=True))
        self.assertTrue(result.local)

    def test_a_local_station_with_too_little_stock_does_not_count_when_enough_is_asked_for(self):
        small = dataclasses.replace(local_item("Home Port", "Home"), quantity=50)
        fake = LocalSpansh([small], [item("Hub", 12, qty=900)])
        wanted = src.LocalFilter(enough_stock=True)
        self.assertFalse(src.find("Home", "Steel", search=fake, here="Home", filters=wanted, needed_t=200).local)
        src.clear_cache()
        self.assertTrue(src.find("Home", "Steel", search=fake, here="Home", filters=wanted, needed_t=40).local)

    def test_a_surface_port_at_home_does_not_count_when_surface_ports_are_excluded(self):
        surface = dataclasses.replace(local_item("Home Base", "Home"), is_planetary=True)
        fake = LocalSpansh([surface], [item("Hub", 12)])
        self.assertFalse(src.find("Home", "Steel", search=fake, here="Home", filters=src.LocalFilter(no_surface=True)).local)

    def test_the_filters_are_part_of_what_is_remembered(self):
        fake = LocalSpansh([local_item("Home Port", "Home")], [item("Hub", 12)])
        src.find("Home", "Steel", search=fake, here="Home")
        src.find("Home", "Steel", search=fake, here="Home", filters=src.LocalFilter(shipyard_only=True))
        self.assertEqual(len(fake.calls), 3)   # the second ask was not answered from the first


class PresetTests(unittest.TestCase):
    def setUp(self):
        src.clear_cache()

    def test_the_default_is_large_then_medium_with_carriers_left_out_and_closest_first(self):
        default = src.SearchPrefs()
        self.assertEqual((default.pad, default.no_carriers, default.sort, default.preset),
                         (src.PAD_LARGE_FIRST, True, src.SORT_DISTANCE, src.DEFAULT_PRESET))
        self.assertEqual(src.PRESETS[0].key, src.DEFAULT_PRESET)

    def test_every_preset_sorts_closest_first_and_is_recognized_by_its_options(self):
        for preset in src.PRESETS:
            key = src.preset_for(pad=preset.pad, sort=src.SORT_DISTANCE, no_carriers=preset.no_carriers, no_surface=preset.no_surface,
                                 max_arrival_ls=preset.max_arrival_ls, enough_stock=preset.enough_stock, shipyard_only=preset.shipyard_only,
                                 radius_ly=preset.radius_ly or 50.0)
            self.assertEqual(key, preset.key)

    def test_a_changed_option_is_custom(self):
        self.assertEqual(src.preset_for(pad=src.PAD_ANY, sort=src.SORT_DISTANCE, no_carriers=True, no_surface=False, max_arrival_ls=None,
                                        enough_stock=False, shipyard_only=False, radius_ly=50.0), src.PRESET_CUSTOM)
        self.assertEqual(src.preset_for(pad=src.PAD_LARGE_FIRST, sort=src.SORT_PRICE, no_carriers=True, no_surface=False, max_arrival_ls=None,
                                        enough_stock=False, shipyard_only=False, radius_ly=50.0), src.PRESET_CUSTOM)

    def test_choices_saved_before_presets_existed_give_way_to_the_new_defaults_but_keep_the_radius(self):
        loaded = src.load_prefs('{"radius": 100, "pad": "any", "no_carriers": false, "sort": "price"}')
        self.assertEqual(loaded, src.SearchPrefs(radius_ly=100.0))

    def test_large_then_medium_tries_large_first_and_says_when_it_fell_back(self):
        def search(system, commodity, transaction, radius, **kwargs):
            return [item("Mid", 5, pads=(4, 4, 0))] if kwargs.get("required_pad") == "medium" else []
        result = src.find("Sol", "Steel", pad=src.PAD_LARGE_FIRST, search=search)
        self.assertEqual([s.station for s in result.stations], ["Mid"])
        self.assertEqual(result.note, src.MEDIUM_NOTE)

    def test_a_large_pad_answer_has_no_fall_back_note(self):
        def search(system, commodity, transaction, radius, **kwargs):
            return [item("Big", 9)] if kwargs.get("required_pad") == "large" else [item("Mid", 5)]
        result = src.find("Sol", "Steel", pad=src.PAD_LARGE_FIRST, search=search)
        self.assertEqual(([s.station for s in result.stations], result.note), (["Big"], ""))

    def test_large_elsewhere_beats_medium_at_home(self):
        def search(system, commodity, transaction, radius, **kwargs):
            if kwargs.get("this_system_only"):
                return [local_item("Home Mid", "Home")] if kwargs.get("required_pad") == "medium" else []
            return [item("Far Big", 30)] if kwargs.get("required_pad") == "large" else []
        result = src.find("Home", "Steel", pad=src.PAD_LARGE_FIRST, search=search, here="Home")
        self.assertEqual([s.station for s in result.stations], ["Far Big"])


class CacheTests(unittest.TestCase):
    def setUp(self):
        src.clear_cache()

    def test_the_same_search_is_answered_from_memory_for_a_short_while(self):
        fake, clock = FakeSpansh([item("Port", 4)]), [0.0]
        first = src.find("Sol", "Steel", search=fake, now=lambda: clock[0])
        clock[0] = src.CACHE_SECONDS - 1
        again = src.find(" sol ", "STEEL", search=fake, now=lambda: clock[0])
        self.assertEqual(len(fake.calls), 1)
        self.assertIs(first, again)
        clock[0] = src.CACHE_SECONDS + 1
        src.find("Sol", "Steel", search=fake, now=lambda: clock[0])
        self.assertEqual(len(fake.calls), 2)

    def test_changed_options_search_again(self):
        fake = FakeSpansh([item("Port", 4)])
        src.find("Sol", "Steel", search=fake)
        src.find("Sol", "Steel", pad=src.PAD_LARGE, search=fake)
        src.find("Sol", "Steel", include_carriers=True, search=fake)
        self.assertEqual(len(fake.calls), 4)   # the carrier search is two requests

    def test_a_failure_is_not_remembered(self):
        def failing(*args, **kwargs):
            raise OSError("down")
        with self.assertRaises(OSError):
            src.find("Sol", "Steel", search=failing)
        fake = FakeSpansh([item("Port", 4)])
        self.assertEqual(len(src.find("Sol", "Steel", search=fake).stations), 1)


class PadTests(unittest.TestCase):
    def setUp(self):
        src.clear_cache()

    def test_largest_pad(self):
        self.assertEqual(src.largest_pad(item("a", 1, pads=(4, 2, 1))), "Large")
        self.assertEqual(src.largest_pad(item("a", 1, pads=(4, 2, 0))), "Medium")
        self.assertEqual(src.largest_pad(item("a", 1, pads=(4, 0, 0))), "Small")
        self.assertEqual(src.largest_pad(item("a", 1, pads=(0, 0, 0))), "?")

    def test_any_size_is_the_default_and_asks_spansh_for_no_pad_filter(self):
        fake = FakeSpansh([item("Outpost", 5, pads=(4, 1, 0), kind="Outpost")])
        result = src.find("Sol", "Steel", search=fake)
        self.assertEqual([s.station for s in result.stations], ["Outpost"])
        self.assertIsNone(fake.calls[0][4]["required_pad"])

    def test_medium_and_large_are_passed_to_spansh_and_checked_again(self):
        stations = [item("Big", 9, pads=(4, 4, 4)), item("Mid", 3, pads=(4, 2, 0)), item("Tiny", 1, pads=(4, 0, 0))]
        fake = FakeSpansh(stations)
        medium = src.find("Sol", "Steel", pad=src.PAD_MEDIUM, search=fake)
        self.assertEqual(fake.calls[0][4]["required_pad"], "medium")
        self.assertEqual([s.station for s in medium.stations], ["Mid", "Big"])
        large = src.find("Sol", "Steel", pad=src.PAD_LARGE, search=fake)
        self.assertEqual(fake.calls[1][4]["required_pad"], "large")
        self.assertEqual([s.station for s in large.stations], ["Big"])

    def test_a_station_with_no_pad_figures_is_kept(self):
        unknown = StationPrice("Mystery", "X", "Outpost", 2.0, 100.0, False, 300, 10)
        result = src.find("Sol", "Steel", pad=src.PAD_LARGE, search=FakeSpansh([unknown]))
        self.assertEqual([s.station for s in result.stations], ["Mystery"])
        self.assertEqual(result.stations[0].pad, "?")


class CarrierTests(unittest.TestCase):
    def setUp(self):
        src.clear_cache()

    def test_carriers_are_not_searched_unless_asked(self):
        fake = FakeSpansh([item("Port", 4)], [item("FC", 1, kind="Drake-Class Carrier")])
        result = src.find("Sol", "Steel", search=fake)
        self.assertEqual(len(fake.calls), 1)
        self.assertEqual(result.carriers, [])

    def test_carriers_come_back_in_their_own_list(self):
        fake = FakeSpansh([item("Port", 4)], [item("FC", 1, kind="Drake-Class Carrier")])
        result = src.find("Sol", "Steel", include_carriers=True, search=fake)
        self.assertEqual(len(fake.calls), 2)
        self.assertEqual([s.station for s in result.stations], ["Port"])
        self.assertEqual([s.station for s in result.carriers], ["FC"])
        self.assertTrue(result.carriers[0].is_carrier)
        self.assertFalse(result.stations[0].is_carrier)


class OrderingTests(unittest.TestCase):
    def setUp(self):
        src.clear_cache()

    def test_closest_first_by_default_then_price(self):
        stations = [item("Far", 40, price=300), item("Near", 5, price=500), item("Near2", 5, price=450)]
        result = src.find("Sol", "Steel", search=FakeSpansh(stations))
        self.assertEqual([s.station for s in result.stations], ["Near2", "Near", "Far"])

    def test_cheapest_first_when_asked(self):
        stations = [item("Far", 40, price=300), item("Near", 5, price=500)]
        fake = FakeSpansh(stations)
        result = src.find("Sol", "Steel", sort=src.SORT_PRICE, search=fake)
        self.assertEqual([s.station for s in result.stations], ["Far", "Near"])
        self.assertEqual(fake.calls[0][4]["sort_by"], "price")


class RequestTests(unittest.TestCase):
    def setUp(self):
        src.clear_cache()

    def test_buy_search_around_the_given_system_and_radius(self):
        fake = FakeSpansh([])
        src.find("  Sol ", "Steel", radius_ly=100, search=fake)
        system, commodity, transaction, radius, kwargs = fake.calls[0]
        self.assertEqual((system, commodity, transaction, radius), ("Sol", "Steel", "Buy", 100))
        self.assertEqual(kwargs["market_days_old"], src.MAX_AGE_DAYS)

    def test_no_limit_radius_is_passed_as_none(self):
        fake = FakeSpansh([])
        src.find("Sol", "Steel", radius_ly=None, search=fake)
        self.assertIsNone(fake.calls[0][3])

    def test_a_blank_system_is_refused_before_any_request(self):
        fake = FakeSpansh([])
        with self.assertRaises(ValueError):
            src.find("   ", "Steel", search=fake)
        self.assertEqual(fake.calls, [])


class SpanshRequestTests(unittest.TestCase):
    """The request body the shared Spansh search builds for the new sort and pad options."""

    def body_for(self, **kwargs):
        import json
        from unittest import mock
        from plugin import mining_spansh_client as client
        captured = {}

        def fake_call(request, timeout, cancel=None, retries=None):
            captured["body"] = json.loads(request.data.decode("utf8"))
            return b'{"results": []}'

        with mock.patch.object(client.spansh_courtesy, "call", fake_call):
            client.search_best_price_stations("Sol", "Steel", "Buy", 50, **kwargs)
        return captured["body"]

    def test_default_request_is_unchanged(self):
        body = self.body_for()
        self.assertNotIn("medium_pads", body["filters"])
        self.assertNotIn("large_pads", body["filters"])
        self.assertIn("market_buy_price", body["sort"][0])

    def test_distance_sort_and_pad_filter(self):
        body = self.body_for(sort_by="distance", required_pad="large")
        self.assertEqual(body["sort"], [{"distance": {"direction": "asc"}}])
        self.assertEqual(body["filters"]["large_pads"], {"comparison": "<=>", "value": [1, 999]})

    def test_bad_options_are_refused(self):
        with self.assertRaises(ValueError):
            self.body_for(sort_by="newest")
        with self.assertRaises(ValueError):
            self.body_for(required_pad="small")


class WholeListTests(unittest.TestCase):
    def setUp(self):
        src.clear_cache()
        self.slept = []

    def run_list(self, commodities, fake, **kwargs):
        return src.find_whole_list("Sol", commodities, search=fake, sleep=self.slept.append, **kwargs)

    def test_each_commodity_is_searched_once_in_the_order_given(self):
        fake = FakeSpansh([item("Near", 5)])
        result = self.run_list(["Steel", "Water", "Copper"], fake)
        self.assertEqual([label for label, _ in result.found], ["Steel", "Water", "Copper"])
        self.assertEqual([call[1] for call in fake.calls], ["Steel", "Water", "Copper"])
        self.assertEqual(result.failed, [])
        self.assertFalse(result.stopped)

    def test_it_pauses_between_requests_but_not_before_the_first(self):
        self.run_list(["Steel", "Water", "Copper"], FakeSpansh([item("Near", 5)]), pause=0.4)
        self.assertEqual(self.slept, [0.4, 0.4])

    def test_answers_from_memory_send_nothing_and_cost_no_pause(self):
        fake = FakeSpansh([item("Near", 5)])
        self.run_list(["Steel", "Water"], fake)
        self.slept.clear()
        self.run_list(["Steel", "Water"], fake)
        self.assertEqual(len(fake.calls), 2)   # the second run was all cache hits
        self.assertEqual(self.slept, [])

    def test_one_failure_does_not_lose_the_others(self):
        def flaky(system, commodity, transaction, radius, **kwargs):
            if commodity == "Water":
                raise RuntimeError("Spansh timed out")
            return [item("Near", 5)]
        result = self.run_list(["Steel", "Water", "Copper"], flaky)
        self.assertEqual([label for label, _ in result.found], ["Steel", "Copper"])
        self.assertEqual(result.failed, [("Water", "Spansh timed out")])

    def test_stopping_keeps_what_was_found_so_far(self):
        calls = []
        result = self.run_list(["Steel", "Water", "Copper"], FakeSpansh([item("Near", 5)]),
                               cancelled=lambda: len(calls) >= 1, progress=lambda i, n, label: calls.append(label))
        self.assertEqual([label for label, _ in result.found], ["Steel"])
        self.assertTrue(result.stopped)

    def test_progress_reports_position_total_and_name(self):
        seen = []
        self.run_list(["Steel", "Water"], FakeSpansh([item("Near", 5)]), progress=lambda i, n, label: seen.append((i, n, label)))
        self.assertEqual(seen, [(0, 2, "Steel"), (1, 2, "Water")])

    def test_commodities_with_no_source_are_listed(self):
        fake = FakeSpansh([])
        result = self.run_list(["Steel", "Water"], fake)
        self.assertEqual(result.without_sources(), ["Steel", "Water"])

    def test_a_blank_system_is_refused_before_any_request(self):
        fake = FakeSpansh([item("Near", 5)])
        with self.assertRaises(ValueError):
            src.find_whole_list("  ", ["Steel"], search=fake)
        self.assertEqual(fake.calls, [])

    def test_options_reach_every_request(self):
        fake = FakeSpansh([item("Near", 5)])
        self.run_list(["Steel", "Water"], fake, radius_ly=100, pad=src.PAD_LARGE)
        self.assertEqual({call[3] for call in fake.calls}, {100})
        self.assertEqual({call[4]["required_pad"] for call in fake.calls}, {"large"})


class PrefsTests(unittest.TestCase):
    def test_defaults_when_nothing_is_saved(self):
        self.assertEqual(src.load_prefs(""), src.SearchPrefs())
        self.assertEqual(src.load_prefs(None), src.SearchPrefs())

    def test_a_round_trip_keeps_every_choice(self):
        prefs = src.SearchPrefs(radius_ly=100.0, pad=src.PAD_LARGE, no_carriers=True, sort=src.SORT_PRICE)
        self.assertEqual(src.load_prefs(src.dump_prefs(prefs)), prefs)

    def test_no_limit_survives_a_round_trip(self):
        prefs = src.SearchPrefs(radius_ly=None)
        self.assertIsNone(src.load_prefs(src.dump_prefs(prefs)).radius_ly)

    def test_junk_falls_back_to_the_defaults_field_by_field(self):
        self.assertEqual(src.load_prefs("not json"), src.SearchPrefs())
        self.assertEqual(src.load_prefs("[1, 2]"), src.SearchPrefs())
        loaded = src.load_prefs('{"radius": 7, "pad": "huge", "no_carriers": "yes", "sort": "newest"}')
        self.assertEqual(loaded, src.SearchPrefs())
        self.assertEqual(src.load_prefs('{"radius": 25, "pad": "medium", "preset": "custom"}'),
                         src.SearchPrefs(radius_ly=25.0, pad=src.PAD_MEDIUM, preset=src.PRESET_CUSTOM))
        self.assertEqual(src.load_prefs('{"radius": true}').radius_ly, src.DEFAULT_RADIUS_LY)


class OneStopTests(unittest.TestCase):
    """The extra "stations that sell every commodity" request merged into a whole-list search."""

    def setUp(self):
        src.clear_cache()
        self.calls = []

    def one_stop(self, hits):
        def fake(system, labels, radius, **kwargs):
            self.calls.append((system, list(labels), radius, kwargs))
            return hits
        return fake

    def run_list(self, one_stop, labels=("Steel", "Water"), **kwargs):
        return src.find_whole_list("Sol", list(labels), search=FakeSpansh([item("Near", 5)]), sleep=lambda s: None,
                                   one_stop=one_stop, **kwargs)

    def test_a_station_selling_everything_is_added_to_each_commodity_with_its_own_price(self):
        far = item("Hub", 80)
        result = self.run_list(self.one_stop([(far, {"Steel": (120, 900), "Water": (30, 400)})]))
        steel, water = (r for _, r in result.found)
        self.assertEqual([(s.station, s.price, s.supply) for s in steel.stations], [("Near", 400, 1000), ("Hub", 120, 900)])
        self.assertEqual([(s.station, s.price, s.supply) for s in water.stations], [("Near", 400, 1000), ("Hub", 30, 400)])
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0][1], ["Steel", "Water"])

    def test_a_station_already_listed_is_not_added_twice(self):
        result = self.run_list(self.one_stop([(item("Near", 5), {"Steel": (1, 1), "Water": (1, 1)})]))
        self.assertTrue(all(len(r.stations) == 1 for _, r in result.found))

    def test_the_route_can_use_the_added_station(self):
        result = self.run_list(self.one_stop([(item("Hub", 80), {"Steel": (120, 900), "Water": (30, 400)})]))
        plan = src.plan_route(result.found, {"Steel": 1800, "Water": 1200})   # more than "Near" alone has in stock
        self.assertEqual(sorted(stop.station for stop in plan.stops), ["Hub", "Near"])
        self.assertEqual(plan.uncovered, ())

    def test_pad_size_is_respected(self):
        small_only = item("Hub", 80, pads=(2, 0, 0))
        result = self.run_list(self.one_stop([(small_only, {"Steel": (1, 9), "Water": (1, 9)})]), pad=src.PAD_LARGE)
        self.assertTrue(all(len(r.stations) == 1 for _, r in result.found))

    def test_a_failing_extra_request_loses_nothing(self):
        def broken(*args, **kwargs):
            raise RuntimeError("busy")
        result = self.run_list(broken)
        self.assertEqual([label for label, _ in result.found], ["Steel", "Water"])

    def test_a_single_commodity_or_a_failed_one_skips_the_extra_request(self):
        self.run_list(self.one_stop([]), labels=["Steel"])
        self.assertEqual(self.calls, [])

    def test_it_is_off_unless_given(self):
        result = src.find_whole_list("Sol", ["Steel", "Water"], search=FakeSpansh([item("Near", 5)]), sleep=lambda s: None)
        self.assertTrue(all(len(r.stations) == 1 for _, r in result.found))


class NeedsAwareTests(unittest.TestCase):
    """With `needs`: the one-stop request goes first, satisfied commodities skip their own search, leftovers get one more."""

    def setUp(self):
        src.clear_cache()
        self.calls = []

    def one_stop(self, *answers):
        queue = list(answers)

        def fake(system, labels, radius, **kwargs):
            self.calls.append((list(labels), kwargs.get("also")))
            return queue.pop(0) if queue else []
        return fake

    def run_list(self, fake_stop, search, needs, labels=("Steel", "Water")):
        return src.find_whole_list("Sol", list(labels), search=search, sleep=lambda s: None, one_stop=fake_stop, needs=needs)

    def test_a_commodity_one_stop_can_supply_in_full_is_not_searched(self):
        search = FakeSpansh([item("Near", 5)])
        hub = (item("Hub", 80), {"Steel": (120, 900), "Water": (30, 400)})
        result = self.run_list(self.one_stop([hub]), search, {"Steel": 500, "Water": 1200})
        self.assertEqual([call[1] for call in search.calls], ["Water"])   # Steel came from the hub alone
        steel = dict(result.found)["Steel"]
        self.assertEqual([s.station for s in steel.stations], ["Hub"])

    def test_nothing_is_skipped_when_the_stock_falls_short(self):
        search = FakeSpansh([item("Near", 5)])
        hub = (item("Hub", 80), {"Steel": (120, 100), "Water": (30, 100)})
        self.run_list(self.one_stop([hub]), search, {"Steel": 500, "Water": 500})
        self.assertEqual(sorted(call[1] for call in search.calls), ["Steel", "Water"])

    def test_leftover_commodities_get_one_more_whole_market_request(self):
        search = FakeSpansh([item("Near", 5, qty=10)])   # too little of anything
        market = (item("Depot", 40), {"Water": (30, 900), "Ore": (50, 900), "Steel": (110, 900)})
        fake = self.one_stop([], [market])
        result = self.run_list(fake, search, {"Water": 500, "Ore": 500, "Steel": 500}, labels=("Water", "Ore", "Steel"))
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(sorted(self.calls[1][0]), ["Ore", "Steel", "Water"])   # all three still uncovered
        plan = src.plan_route(result.found, {"Water": 500, "Ore": 500, "Steel": 500})
        self.assertEqual([stop.station for stop in plan.stops][-1], "Depot")
        self.assertEqual(plan.uncovered, ())

    def test_no_leftover_request_when_the_route_covers_everything(self):
        search = FakeSpansh([item("Near", 5)])
        self.run_list(self.one_stop([]), search, {"Steel": 100, "Water": 100})
        self.assertEqual(len(self.calls), 1)

    def test_a_failing_first_request_still_searches_every_commodity(self):
        def broken(*args, **kwargs):
            raise RuntimeError("busy")
        search = FakeSpansh([item("Near", 5)])
        result = self.run_list(broken, search, {"Steel": 100, "Water": 100})
        self.assertEqual(sorted(call[1] for call in search.calls), ["Steel", "Water"])
        self.assertEqual(len(result.found), 2)


class TripOrderTests(unittest.TestCase):
    """The stops are flown in the order that makes the shortest trip, each jump measured from the stop before."""

    @staticmethod
    def source(name, system, distance, position, supply=1000):
        return src.Source(name, system, "Coriolis Starport", False, False, "Large", distance, 100.0, 400, supply, position=position)

    def found(self):
        # Away from the search system, in a line along x: A is 10 ly out, B 12 ly (but past C on the far side), C 30 ly.
        a = self.source("A Port", "A", 10.0, (10.0, 0.0, 0.0))
        b = self.source("B Port", "B", 12.0, (0.0, 12.0, 0.0))
        c = self.source("C Port", "C", 30.0, (30.0, 0.0, 0.0))
        return [("Steel", src.SearchResult([a], [])), ("Water", src.SearchResult([b], [])), ("Ore", src.SearchResult([c], []))]

    def test_the_shortest_trip_is_flown_not_the_nearest_to_the_start_first(self):
        plan = src.plan_route(self.found(), {"Steel": 100, "Water": 100, "Ore": 100})
        # B, A, C: 12 + 15.6 + 20 = 47.6 ly, against A, B, C: 10 + 15.6 + 36.1 = 61.7 ly.
        self.assertEqual([s.system for s in plan.stops], ["B", "A", "C"])
        self.assertAlmostEqual(plan.total_ly, 12.0 + (10.0 ** 2 + 12.0 ** 2) ** 0.5 + 20.0, places=4)
        self.assertEqual(plan.stops[0].leg_ly, 12.0)
        self.assertAlmostEqual(plan.stops[1].leg_ly, (10.0 ** 2 + 12.0 ** 2) ** 0.5, places=4)
        self.assertAlmostEqual(plan.stops[2].leg_ly, 20.0, places=4)

    def test_a_stop_with_no_known_position_falls_back_to_nearest_first_with_no_legs(self):
        found = self.found()
        far = self.source("C Port", "C", 30.0, None)
        found[2] = ("Ore", src.SearchResult([far], []))
        plan = src.plan_route(found, {"Steel": 100, "Water": 100, "Ore": 100})
        self.assertEqual([s.system for s in plan.stops], ["A", "B", "C"])
        self.assertIsNone(plan.total_ly)
        self.assertTrue(all(s.leg_ly is None for s in plan.stops))

    def test_the_copied_route_gives_the_legs_and_the_total(self):
        plan = src.plan_route(self.found(), {"Steel": 100, "Water": 100, "Ore": 100})
        lines = plan.lines()
        self.assertIn("47.6 ly in all", lines[0])
        self.assertIn("1. B Port (B)", lines[1])
        self.assertIn("12.0 ly", lines[1])

    def test_the_stop_keeps_its_pad_and_position(self):
        plan = src.plan_route(self.found(), {"Steel": 100})
        self.assertEqual((plan.stops[0].pad, plan.stops[0].position), ("Large", (10.0, 0.0, 0.0)))

    def test_spansh_positions_are_read_or_left_out(self):
        from plugin.mining_spansh_client import _position
        self.assertEqual(_position({"system_x": 1, "system_y": 2.5, "system_z": -3}), (1.0, 2.5, -3.0))
        self.assertIsNone(_position({"system_x": 1, "system_y": 2}))
        self.assertIsNone(_position({"system_x": "1", "system_y": 2, "system_z": 3}))

    def test_one_stop_is_a_trip_of_its_own_distance(self):
        plan = src.plan_route(self.found(), {"Steel": 100})
        self.assertEqual(plan.total_ly, 10.0)


class SurfacePortTests(unittest.TestCase):
    @staticmethod
    def source(name, planetary, supply=1000):
        return src.Source(name, "Sol", "Coriolis Starport", False, planetary, "Large", 5.0, 100.0, 400, supply)

    def found(self):
        ship = self.source("Orbital", False)
        ground = self.source("Ground", True)
        return [("Steel", src.SearchResult([ship, ground], [])), ("Titanium", src.SearchResult([ground], []))]

    def test_a_commodity_found_only_at_surface_ports_is_named(self):
        self.assertEqual(src.surface_only_labels(self.found()), frozenset({"Titanium"}))
        self.assertEqual(src.surface_only_labels([("Gold", src.SearchResult([], []))]), frozenset())

    def test_a_surface_port_is_a_leg_of_the_route(self):
        plan = src.plan_route(self.found(), {"Steel": 100, "Titanium": 50})
        ground = next(stop for stop in plan.stops if stop.station == "Ground")
        self.assertTrue(ground.is_planetary)
        self.assertEqual([b.commodity for b in ground.buys if b.commodity == "Titanium"], ["Titanium"])
        self.assertTrue(any("(surface port)" in line and "Titanium 50 t" in line for line in plan.lines()))

    def test_without_them_the_commodity_is_not_covered(self):
        plan = src.plan_route(src.filter_found(self.found(), no_surface=True), {"Steel": 100, "Titanium": 50})
        self.assertEqual(plan.uncovered, (("Titanium", 50),))

    def test_an_orbital_port_found_by_a_second_search_clears_the_surface_only_note(self):
        calls = []

        def search(reference, commodity, transaction, radius, **kwargs):
            calls.append((commodity, tuple(kwargs["station_types"])))
            if "Planetary Port" in kwargs["station_types"]:
                return [item("Ground", 5.0, planetary=True)]
            return [item("Orbital", 30.0)]

        src.clear_cache()
        out = src.find_whole_list("Sol", ["Steel"], search=search, pause=0, now=lambda: 0.0)
        self.assertEqual([s.station for s in out.found[0][1].stations], ["Ground", "Orbital"])
        self.assertEqual(src.surface_only_labels(out.found), frozenset())
        self.assertEqual(len(calls), 2)
        self.assertNotIn("Planetary Port", calls[1][1])

    def test_a_commodity_with_an_orbital_seller_needs_no_second_search(self):
        calls = []

        def search(reference, commodity, transaction, radius, **kwargs):
            calls.append(commodity)
            return [item("Ground", 5.0, planetary=True), item("Orbital", 9.0)]

        src.clear_cache()
        src.find_whole_list("Sol", ["Steel"], search=search, pause=0, now=lambda: 0.0)
        self.assertEqual(calls, ["Steel"])

    def test_surface_ports_are_taken_out(self):
        left = src.filter_found(self.found(), no_surface=True)
        self.assertEqual([(label, [s.station for s in r.stations]) for label, r in left], [("Steel", ["Orbital"]), ("Titanium", [])])

    def test_arrival_and_stock_filters(self):
        near = src.Source("Near", "Sol", "Coriolis Starport", False, False, "Large", 3.0, 200.0, 400, 500)
        far = src.Source("Far", "Sol", "Coriolis Starport", False, False, "Large", 4.0, 40000.0, 400, 500)
        small = src.Source("Small", "Sol", "Coriolis Starport", False, False, "Large", 5.0, 300.0, 400, 20)
        unknown = src.Source("Unknown", "Sol", "Coriolis Starport", False, False, "Large", 6.0, 0.0, 400, 500)
        found = [("Steel", src.SearchResult([near, far, small, unknown], []))]
        names = lambda out: [s.station for s in out[0][1].stations]
        self.assertEqual(names(src.filter_found(found, max_arrival_ls=5000)), ["Near", "Small", "Unknown"])
        self.assertEqual(names(src.filter_found(found, needs={"Steel": 100})), ["Near", "Far", "Unknown"])
        self.assertEqual(names(src.filter_found(found, max_arrival_ls=5000, needs={"Steel": 100})), ["Near", "Unknown"])
        self.assertEqual(names(src.filter_found(found, needs={"Other": 100})), ["Near", "Far", "Small", "Unknown"])
        self.assertEqual(names(src.filter_found(found)), ["Near", "Far", "Small", "Unknown"])
        yard = src.Source("Yard", "Sol", "Orbis Starport", False, False, "Large", 8.0, 100.0, 400, 500, True)
        both = [("Steel", src.SearchResult([near, yard], []))]
        self.assertEqual(names(src.filter_found(both, shipyard_only=True)), ["Yard"])
        self.assertEqual(names(src.filter_found(both)), ["Near", "Yard"])

    def test_the_new_filter_choices_are_remembered(self):
        prefs = src.SearchPrefs(max_arrival_ls=5000, enough_stock=True, shipyard_only=True)
        self.assertEqual(src.load_prefs(src.dump_prefs(prefs)), prefs)
        self.assertIsNone(src.load_prefs('{"arrival": 123}').max_arrival_ls)
        self.assertIsNone(src.SearchPrefs().max_arrival_ls)
        self.assertFalse(src.SearchPrefs().enough_stock)
        self.assertFalse(src.SearchPrefs().shipyard_only)

    def test_the_choice_is_remembered(self):
        self.assertEqual((src.SearchPrefs().no_surface, src.SearchPrefs().no_carriers), (False, True))
        self.assertTrue(src.load_prefs(src.dump_prefs(src.SearchPrefs(no_surface=True))).no_surface)
        self.assertFalse(src.load_prefs("{}").no_surface)


if __name__ == "__main__":
    unittest.main()
