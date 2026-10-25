"""The Mining radar card (plugin/mining_radar_overlay.py) and the radar recipe it shares with the Live window (plugin/mining_radar_view.py). No Tk window and no real overlay: the client is a
stand-in that records what is sent. The file name sorts late on purpose: it imports the overlay modules, which must not be loaded before the tests that set up their own `config`."""

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_config = sys.modules.setdefault("config", types.ModuleType("config"))
for _attr, _default in (("appname", "EDMarketConnector"), ("user_agent", "WFMT-test"), ("appversion", lambda: "5.13.0")):
    if not hasattr(_config, _attr):
        setattr(_config, _attr, _default)
if not hasattr(_config, "config"):
    _config.config = mock.MagicMock()


class _Any(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return mock.MagicMock()


for _name in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "theme", "myNotebook"):
    sys.modules.setdefault(_name, _Any(_name))

from plugin import mining_coverage_render as radar  # noqa: E402
from plugin import mining_radar_overlay as card  # noqa: E402
from plugin import mining_radar_view as view  # noqa: E402
from plugin import mining_simulation  # noqa: E402
from plugin import mining_sources  # noqa: E402
from plugin import overlay_native  # noqa: E402

from PIL import Image  # noqa: E402


class FakeConfig:
    def __init__(self, **values):
        self.values = dict(values)

    def get_int(self, key, default=0):
        return self.values.get(key, default)

    def get_bool(self, key, default=False):
        return self.values.get(key, default)

    def get_str(self, key, default=""):
        return self.values.get(key, default)

    def set(self, key, value):
        self.values[key] = value


class FakeClient:
    def __init__(self):
        self.images, self.cleared = [], []

    def send_image(self, shape_id, image, x, y, w, h, key, ttl=8):
        self.images.append(dict(id=shape_id, image=image, x=x, y=y, w=w, h=h, key=key, ttl=ttl))
        return True

    def send_clear(self, shape_id):
        self.cleared.append(shape_id)

    def __getattr__(self, name):
        return mock.MagicMock()


class CardTestCase(unittest.TestCase):
    def setUp(self):
        self.config = FakeConfig(**{card.CFG_ENABLED: True})
        self.client = FakeClient()
        for patcher in (mock.patch.object(card, "config", self.config), mock.patch.object(view, "config", self.config),
                        mock.patch.object(overlay_native, "accepting", return_value=True),
                        mock.patch.object(card, "_client", self.client),
                        mock.patch.object(card.overlay_placement, "client_for_measured", lambda slot, client, block, look=None: client)):
            patcher.start()
            self.addCleanup(patcher.stop)
        card._busy, card._last, card._shown = False, 0.0, False
        self.addCleanup(lambda: (setattr(card, "_busy", False), setattr(card, "_last", 0.0), setattr(card, "_shown", False)))
        self.now = 1000.0
        self.sim = mining_simulation.SurfaceSimulation(clock=lambda: self.now)       # a clock that stands still: the pretend Rhino does not move between two pictures
        self.src = self.sim.sources


class SettingsTests(CardTestCase):
    def test_the_size_and_opacity_stay_in_their_ranges(self):
        for stored, expected in ((10, card.SIZE_RANGE[0]), (5000, card.SIZE_RANGE[1]), (400, 400)):
            self.config.values[card.CFG_SIZE] = stored
            self.assertEqual(card.card_size(), expected)
        for stored, expected in ((0, card.OPACITY_RANGE[0]), (900, card.OPACITY_RANGE[1]), (55, 55)):
            self.config.values[card.CFG_OPACITY] = stored
            self.assertEqual(card.opacity_percent(), expected)

    def test_the_defaults(self):
        self.config.values.clear()
        self.assertEqual((card.card_size(), card.opacity_percent(), card.enabled()), (card.SIZE_DEFAULT, card.OPACITY_DEFAULT, False))


class TranslucentTests(CardTestCase):
    def test_the_background_takes_the_opacity_and_what_is_drawn_stays_solid(self):
        picture = Image.new("RGB", (20, 20), radar.RADAR_BACKGROUND)
        picture.putpixel((5, 5), (255, 196, 64))
        picture.putpixel((6, 6), radar.GROUND_DRIVEN_COLOR)
        out = card.translucent(picture, 50)
        self.assertEqual(out.mode, "RGBA")
        self.assertEqual(out.getpixel((0, 0))[3], round(255 * 0.5))
        self.assertEqual(out.getpixel((6, 6))[3], round(255 * 0.5), "the green of the ground driven is translucent too")
        self.assertEqual(out.getpixel((5, 5)), (255, 196, 64, 255))

    def test_full_and_minimum_opacity(self):
        picture = Image.new("RGB", (4, 4), radar.RADAR_BACKGROUND)
        self.assertEqual(card.translucent(picture, 100).getpixel((0, 0))[3], 255)
        self.assertEqual(card.translucent(picture, -20).getpixel((0, 0))[3], 0)


class PictureTests(CardTestCase):
    def test_the_picture_is_the_card_size_square_and_translucent(self):
        self.config.values[card.CFG_SIZE] = 300
        picture = card.card_picture(self.src, 2000.0)
        self.assertEqual((picture.size, picture.mode), ((300, 300), "RGBA"))
        self.assertLess(picture.getchannel("A").getextrema()[0], 255, "some of it is plain background")
        self.assertEqual(picture.getchannel("A").getextrema()[1], 255, "and what is drawn is solid")

    def test_without_a_position_there_is_nothing_to_draw(self):
        quiet = mining_sources.Sources(surface=self.src.surface, coverage=self.src.coverage, hotspots=self.src.hotspots, space=self.src.space, position=lambda: None)
        self.assertIsNone(card.card_picture(quiet, 2000.0))
        self.assertIsNone(view.context(quiet))

    def test_the_view_gives_the_rings_stops_and_target_the_live_window_shows(self):
        ctx = view.context(self.src)
        self.assertIsNotNone(ctx)
        with mock.patch.object(view.mining_alerts, "load_target", return_value=("Platinum", 20)):
            extras = view.extras(ctx)
        self.assertEqual(extras.target_material, "Platinum")
        self.assertTrue(extras.drive_radii_m)
        self.assertTrue(extras.stops)
        self.assertEqual(view.extras(ctx, with_target=False).target_material, "")


class UpdateTests(CardTestCase):
    def test_the_card_is_drawn_while_the_rhino_is_out(self):
        card._work(self.src)
        self.assertEqual(len(self.client.images), 1)
        sent = self.client.images[0]
        self.assertEqual((sent["id"], sent["w"], sent["h"], sent["ttl"]), (card.SHAPE_ID, card.card_size(), card.card_size(), card.TTL_S))
        self.assertEqual((sent["x"], sent["y"]), (card.ORIGIN_X, card.ORIGIN_Y))
        self.assertTrue(sent["key"])
        self.assertTrue(card._shown)

    def test_the_same_picture_has_the_same_key_and_a_moved_rhino_a_different_one(self):
        card._work(self.src)
        card._work(self.src)
        self.assertEqual(self.client.images[0]["key"], self.client.images[1]["key"])
        self.now += 60.0
        card._work(self.src)
        self.assertNotEqual(self.client.images[0]["key"], self.client.images[2]["key"])

    def test_it_is_taken_down_once_when_the_rhino_is_stowed(self):
        card._work(self.src)
        self.src.surface.force_end_run()
        card._work(self.src)
        card._work(self.src)
        self.assertEqual(self.client.cleared, [card.SHAPE_ID])
        self.assertFalse(card._shown)

    def test_nothing_is_drawn_or_cleared_when_it_was_never_shown(self):
        self.src.surface.force_end_run()
        card._work(self.src)
        self.assertEqual((self.client.images, self.client.cleared), ([], []))

    def test_it_is_not_drawn_when_switched_off_or_with_another_overlay(self):
        self.config.values[card.CFG_ENABLED] = False
        card._work(self.src)
        self.config.values[card.CFG_ENABLED] = True
        with mock.patch.object(overlay_native, "accepting", return_value=False):
            card._work(self.src)
        self.assertEqual(self.client.images, [])

    def test_a_failure_while_drawing_is_swallowed_and_frees_the_next_update(self):
        with mock.patch.object(card, "card_picture", side_effect=RuntimeError("boom")):
            card._busy = True
            card._work(self.src)
        self.assertFalse(card._busy)

    def test_update_draws_at_most_once_a_second_and_never_on_the_callers_thread(self):
        started = []

        class Inline:
            def __init__(self, target, args=(), **kw):
                self.target, self.args = target, args

            def start(self):
                started.append(self)
                self.target(*self.args)

        with mock.patch.object(card.threading, "Thread", Inline):
            card.update(self.src)
            card.update(self.src)                       # inside the interval: skipped
            self.assertEqual(len(started), 1)
            card._last -= card.MIN_INTERVAL_S + 0.1
            card.update(self.src)
        self.assertEqual(len(started), 2)

    def test_switching_it_off_takes_a_shown_card_down(self):
        card._work(self.src)
        self.config.values[card.CFG_ENABLED] = False
        card.update(self.src)
        self.assertEqual(self.client.cleared, [card.SHAPE_ID])


class TestCardTests(CardTestCase):
    def test_the_test_draws_the_pretend_rhino_for_a_few_seconds(self):
        self.assertTrue(card.send_test(self.client))
        self.assertEqual(self.client.images[0]["ttl"], 8)

    def test_the_test_says_no_with_another_overlay(self):
        with mock.patch.object(overlay_native, "accepting", return_value=False):
            self.assertFalse(card.send_test(self.client))
        self.assertEqual(self.client.images, [])


if __name__ == "__main__":
    unittest.main()
