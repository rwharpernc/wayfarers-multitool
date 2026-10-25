"""The Mining, Rare Goods, System targets and ELW rarity lookups go through the courtesy layer: they send their own User-Agent, and a refusal from the layer
(Spansh busy) ends in each module's normal failure result. The layer is replaced, so nothing here touches the network."""
from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugin import elw_rarity_spansh as elw  # noqa: E402
from plugin import mining_spansh_client as mining  # noqa: E402
from plugin import powerplay_control_lookup as control  # noqa: E402
from plugin import spansh_courtesy  # noqa: E402
from plugin import system_known  # noqa: E402

BUSY = spansh_courtesy.SpanshBusy("Spansh has not been answering, so WFMT is not asking it for another 5 minute(s).")


def _agent(call: mock.Mock) -> str:
    return call.call_args.args[0].get_header("User-agent")


class MiningClientTests(unittest.TestCase):
    def test_hotspot_search_sends_its_user_agent(self) -> None:
        with mock.patch.object(mining.spansh_courtesy, "call", return_value=b'{"results": []}') as call:
            mining.search_ring_hotspots("Sol", "Painite", 50)
        self.assertEqual(_agent(call), mining._USER_AGENT)

    def test_station_search_sends_its_user_agent(self) -> None:
        with mock.patch.object(mining.spansh_courtesy, "call", return_value=b'{"results": []}') as call:
            mining.search_best_price_stations("Sol", "Gold", "Sell", 50)
            self.assertEqual(_agent(call), mining._USER_AGENT)
            mining.search_material_traders("Sol", "Raw", 50)
            self.assertEqual(_agent(call), mining._TRADER_AGENT)

    def test_a_busy_layer_raises_for_the_caller_to_show(self) -> None:
        with mock.patch.object(mining.spansh_courtesy, "call", side_effect=BUSY):
            with self.assertRaises(OSError) as caught:
                mining.search_ring_hotspots("Sol", "Painite", 50)
            self.assertIn("not been answering", str(caught.exception))
            with self.assertRaises(spansh_courtesy.SpanshBusy):
                mining.search_system_stations("Sol")


class ControlLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        control._cache.clear()

    def test_sends_its_user_agent(self) -> None:
        with mock.patch.object(control.spansh_courtesy, "call", return_value=b'{"record": {}}') as call:
            control._fetch_one(5)
        self.assertEqual(_agent(call), control._USER_AGENT)

    def test_a_busy_layer_gives_an_unresolved_power(self) -> None:
        with mock.patch.object(control.spansh_courtesy, "call", side_effect=BUSY):
            self.assertIsNone(control._fetch_one(6))
        self.assertEqual(control.cached(6), (True, None))


class SystemKnownTests(unittest.TestCase):
    def test_sends_its_user_agent(self) -> None:
        with mock.patch.object(system_known.spansh_courtesy, "call", return_value=b'{"record": {"bodies": []}}') as call:
            self.assertEqual(system_known.fetch(7), {"bodies": []})
        self.assertEqual(_agent(call), system_known.http_identity.user_agent("system-known"))

    def test_a_busy_layer_is_a_failed_request(self) -> None:
        with mock.patch.object(system_known.spansh_courtesy, "call", side_effect=BUSY):
            self.assertIsNone(system_known.fetch(8))

    def test_an_oversized_answer_is_a_failed_request(self) -> None:
        with mock.patch.object(system_known, "MAX_RESPONSE_BYTES", 4), \
                mock.patch.object(system_known.spansh_courtesy, "call", return_value=b'{"record": {}}'):
            self.assertIsNone(system_known.fetch(9))


class ElwRarityTests(unittest.TestCase):
    def test_sends_its_user_agent(self) -> None:
        with mock.patch.object(elw.spansh_courtesy, "call", return_value=b'{"count": 182}') as call:
            self.assertEqual(elw.count_nearby_earthlike_worlds("Sol"), 182)
        self.assertEqual(_agent(call), elw._USER_AGENT)

    def test_a_busy_layer_raises_as_documented(self) -> None:
        with mock.patch.object(elw.spansh_courtesy, "call", side_effect=BUSY):
            with self.assertRaises(OSError):
                elw.count_nearby_earthlike_worlds("Sol")


if __name__ == "__main__":
    unittest.main()
