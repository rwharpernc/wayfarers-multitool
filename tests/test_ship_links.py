"""Links that carry a ship loadout (plugin/ship_links.py): making a Coriolis or EDSY link, reading a pasted one, the refusals, and that the Ship planner's parser accepts a link."""
from __future__ import annotations

import base64
import gzip
import io
import json
import os
import sys
import types
import unittest
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key: "", default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import ship_links as L  # noqa: E402
from plugin import ship_plan as S  # noqa: E402

LOADOUT = {"event": "Loadout", "Ship": "federation_corvette", "ShipName": "Big Réd", "ShipIdent": "FC-01",
           "Modules": [{"Slot": "FrameShiftDrive", "Item": "int_hyperdrive_size5_class5", "On": True,
                        "Engineering": {"BlueprintName": "FSD_LongRange", "Level": 5, "ExperimentalEffect": "special_fsd_heavy", "Quality": 1.0}},
                       {"Slot": "CargoHatch", "Item": "modularcargobaydoor", "On": True}]}


def emc_payload(loadout):
    """The payload exactly as EDMC's own plugin code builds it (its shared shipyard-link function), so a link made here matches what players already use."""
    string = json.dumps(loadout, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="w") as handle:
        handle.write(string)
    return base64.urlsafe_b64encode(out.getvalue()).decode().replace("=", "%3D")


def coriolis_zlib_payload(loadout):
    """A payload packed as a zlib stream with standard base64, which Coriolis's own importer also reads."""
    return base64.b64encode(zlib.compress(json.dumps(loadout).encode("utf-8"))).decode()


class MakeLinkTests(unittest.TestCase):
    def test_the_payload_decodes_with_the_same_recipe_edmc_uses(self):
        payload = L.loadout_payload(LOADOUT)
        self.assertEqual(json.loads(gzip.decompress(base64.urlsafe_b64decode(payload.replace("%3D", "=")))), LOADOUT)
        self.assertNotIn("=", payload)

    def test_the_payload_has_the_same_content_as_an_edmc_link(self):
        ours = json.loads(gzip.decompress(base64.urlsafe_b64decode(L.loadout_payload(LOADOUT).replace("%3D", "="))))
        theirs = json.loads(gzip.decompress(base64.urlsafe_b64decode(emc_payload(LOADOUT).replace("%3D", "="))))
        self.assertEqual(ours, theirs)

    def test_the_link_forms(self):
        self.assertTrue(L.coriolis_url(LOADOUT).startswith("https://coriolis.io/import?data="))
        self.assertTrue(L.coriolis_url(LOADOUT, beta=True).startswith("https://beta.coriolis.io/import?data="))
        self.assertTrue(L.edsy_url(LOADOUT).startswith("https://edsy.org/#/I="))
        self.assertTrue(L.edsy_url(LOADOUT, beta=True).startswith("https://edsy.org/beta/#/I="))

    def test_the_payload_is_the_same_every_time(self):
        self.assertEqual(L.loadout_payload(LOADOUT), L.loadout_payload(dict(reversed(list(LOADOUT.items())))))

    def test_a_long_link_is_flagged_for_coriolis(self):
        self.assertFalse(L.too_long(L.coriolis_url(LOADOUT)))
        self.assertTrue(L.too_long("https://coriolis.io/import?data=" + "A" * L.CORIOLIS_MAX_URL))
        self.assertTrue(L.too_long("x" * L.CORIOLIS_MAX_URL))
        self.assertFalse(L.too_long("x" * (L.CORIOLIS_MAX_URL - 1)))

    def test_a_build_becomes_a_journal_shaped_loadout(self):
        out = L.loadout_from_build("federation_corvette", "Big Red", LOADOUT["Modules"], "FC-01")
        self.assertEqual((out["event"], out["Ship"], out["ShipName"], out["ShipIdent"]), ("Loadout", "federation_corvette", "Big Red", "FC-01"))
        self.assertEqual(out["Modules"], LOADOUT["Modules"])
        self.assertNotIn("ShipIdent", L.loadout_from_build("x", "", []))


class ReadLinkTests(unittest.TestCase):
    def test_every_link_form_we_make_is_read_back(self):
        for url in (L.coriolis_url(LOADOUT), L.coriolis_url(LOADOUT, beta=True), L.edsy_url(LOADOUT), L.edsy_url(LOADOUT, beta=True)):
            self.assertEqual(L.decode_link(url), LOADOUT, url)

    def test_a_link_built_by_edmc_is_read(self):
        for prefix in ("https://coriolis.io/import?data=", "https://beta.coriolis.io/import?data=", "https://edsy.org/#/I=", "https://edsy.org/beta/#/I="):
            self.assertEqual(L.decode_link(prefix + emc_payload(LOADOUT)), LOADOUT)

    def test_the_path_form_and_a_zlib_stream_are_read(self):
        self.assertEqual(L.decode_link("https://coriolis.io/import/" + L.loadout_payload(LOADOUT)), LOADOUT)
        self.assertEqual(L.decode_link("https://coriolis.io/import?data=" + coriolis_zlib_payload(LOADOUT)), LOADOUT)

    def test_a_list_of_entries_is_read(self):
        entries = [{"data": LOADOUT}, {"data": LOADOUT}]
        self.assertEqual(L.decode_link(L.coriolis_url(entries)), entries)

    def test_padding_may_be_missing_or_quoted(self):
        payload = L.loadout_payload(LOADOUT)
        self.assertEqual(L.decode_payload(payload.replace("%3D", "")), LOADOUT)
        self.assertEqual(L.decode_payload(payload.replace("%3D", "=")), LOADOUT)

    def test_surrounding_spaces_and_case_in_the_host_are_tolerated(self):
        self.assertEqual(L.decode_link("  HTTPS://Coriolis.IO/import?data=" + L.loadout_payload(LOADOUT) + "  "), LOADOUT)

    def test_a_link_this_reader_cannot_use_says_why(self):
        cases = (("https://edsy.org/#/L=AbCdEf", "EDSY's own code"),
                 ("https://coriolis.io/outfit/asp?code=A0p", "Coriolis's own code"),
                 ("https://zip1.io/abc123", "short link"), ("https://sh.orbis.zone/xyz", "short link"),
                 ("https://example.com/import?data=abc", "coriolis.io and edsy.org only"),
                 ("https://coriolis.io/import", "no ship in it"), ("https://edsy.org/", "no ship in it"))
        for link, fragment in cases:
            with self.assertRaises(L.LinkError) as caught:
                L.decode_link(link)
            self.assertIn(fragment, str(caught.exception), link)

    def test_damaged_data_is_refused(self):
        for link in ("https://coriolis.io/import?data=!!!!", "https://coriolis.io/import?data=AAAA",
                     "https://coriolis.io/import?data=" + base64.urlsafe_b64encode(gzip.compress(b"not json")).decode()):
            with self.assertRaises(L.LinkError):
                L.decode_link(link)

    def test_a_payload_that_inflates_to_far_too_much_is_refused(self):
        bomb = base64.urlsafe_b64encode(gzip.compress(b"[" + b"0," * (L.MAX_LOADOUT_BYTES // 2 + 10) + b"0]")).decode()
        with self.assertRaises(L.LinkError):
            L.decode_link("https://coriolis.io/import?data=" + bomb)

    def test_a_huge_link_is_refused(self):
        with self.assertRaises(L.LinkError):
            L.decode_link("https://coriolis.io/import?data=" + "A" * (L.MAX_LINK_CHARS + 1))
        with self.assertRaises(L.LinkError):
            L.decode_link(None)

    def test_looks_like_link(self):
        self.assertTrue(L.looks_like_link(" https://coriolis.io/import?data=x"))
        self.assertTrue(L.looks_like_link("HTTP://edsy.org"))
        self.assertFalse(L.looks_like_link('{"Modules": []}'))
        self.assertFalse(L.looks_like_link(None))


class ShipPlanReadsLinksTests(unittest.TestCase):
    def test_the_ship_planner_accepts_a_pasted_link(self):
        for link in (L.coriolis_url(LOADOUT), L.edsy_url(LOADOUT)):
            builds = S.parse(link)
            self.assertEqual(len(builds), 1)
            self.assertEqual(builds[0].ship_id, "federation_corvette")
            self.assertEqual(len(builds[0].modules), 2)

    def test_the_ship_planner_reads_a_link_with_several_builds(self):
        builds = S.parse(L.coriolis_url([{"data": LOADOUT}, {"data": LOADOUT}]))
        self.assertEqual(len(builds), 2)

    def test_an_unusable_link_is_a_plan_error_with_the_reason(self):
        with self.assertRaises(S.PlanError) as caught:
            S.parse("https://edsy.org/#/L=AbCdEf")
        self.assertIn("EDSY's own code", str(caught.exception))

    def test_plain_json_still_works(self):
        self.assertEqual(len(S.parse(json.dumps(LOADOUT))), 1)


if __name__ == "__main__":
    unittest.main()
