"""The built-in overlay's scene (overlay_scene.py) and how it is drawn (overlay_raster.py)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugin import overlay_scene as S  # noqa: E402

try:
    from PIL import Image  # noqa: F401
    from plugin import overlay_raster as R  # noqa: E402
except ImportError:                                                    # pragma: no cover - Pillow ships with EDMC; a bare test machine may lack it
    R = None


class Clock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


def text(ident="t", body="hi", ttl=4, **extra):
    return {"id": ident, "text": body, "color": "#ffffff", "x": 10, "y": 20, "ttl": ttl, "size": "normal", **extra}


def rect(ident="r", ttl=4, w=100, h=50, **extra):
    return {"id": ident, "shape": "rect", "color": "#ff0000", "fill": "#80000000", "x": 5, "y": 6, "w": w, "h": h, "ttl": ttl, **extra}


class SceneTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.scene = S.Scene(self.clock)

    def test_each_kind_of_payload_becomes_an_item(self):
        self.scene.apply(text())
        self.scene.apply(rect())
        self.scene.apply({"id": "c", "shape": "circle", "color": "#fff", "fill": "", "x": 1, "y": 2, "radius": 7, "ttl": 4})
        self.scene.apply({"id": "v", "shape": "vect", "color": "#fff", "ttl": 4, "vector": [{"x": 1, "y": 2}, {"x": 3, "y": 4, "marker": "cross"}]})
        kinds = {item.id: item.kind for item in self.scene.items()}
        self.assertEqual(kinds, {"t": S.TEXT, "r": S.RECT, "c": S.CIRCLE, "v": S.VECT})

    def test_text_is_always_drawn_above_panels_whatever_order_they_were_sent_in(self):
        self.scene.apply(text("t1"))
        self.scene.apply(rect("panel"))                       # the panel arrives after the text
        self.scene.apply({"id": "c", "shape": "circle", "color": "#fff", "x": 1, "y": 2, "radius": 7, "ttl": 4})
        self.assertEqual([item.id for item in self.scene.items()], ["panel", "c", "t1"])
        self.clock.now += 3
        self.scene.apply(rect("panel"))                       # the panel is sent again: still below
        self.assertEqual([item.id for item in self.scene.items()][0], "panel")

    def test_an_id_sent_again_replaces_what_it_drew(self):
        self.scene.apply(text("t", "first"))
        self.scene.apply(text("t", "second"))
        self.assertEqual([item.text for item in self.scene.items()], ["second"])

    def test_something_that_draws_nothing_removes_the_id(self):
        self.scene.apply(text("t"))
        self.scene.apply(rect("r"))
        self.scene.apply({"id": "c", "shape": "circle", "color": "#fff", "x": 1, "y": 2, "radius": 7, "ttl": 4})
        self.scene.apply({"id": "v", "shape": "vect", "color": "#fff", "ttl": 4, "vector": [{"x": 1, "y": 2}]})
        self.scene.apply(text("t", "", ttl=1))
        self.scene.apply(rect("r", w=0, h=0, color="", fill="", ttl=1))
        self.scene.apply({"id": "c", "shape": "circle", "color": "", "fill": "", "x": 1, "y": 2, "radius": 7, "ttl": 1})
        self.scene.apply({"id": "v", "shape": "vect", "color": "#fff", "ttl": 1, "vector": []})
        self.assertEqual(self.scene.items(), [])

    def test_an_item_runs_out_after_its_ttl(self):
        self.scene.apply(text("t", ttl=4))
        self.clock.now += 3.9
        self.assertEqual(len(self.scene.items()), 1)
        self.clock.now += 0.2
        self.assertEqual(self.scene.items(), [])

    def test_the_version_changes_only_when_the_picture_would(self):
        self.scene.apply(text("t"))
        before = self.scene.version
        self.clock.now += 2
        self.scene.apply(text("t"))                           # the same thing, sent again to keep it up
        self.assertEqual(self.scene.version, before)
        self.scene.apply(text("t", "changed"))
        self.assertGreater(self.scene.version, before)
        before = self.scene.version
        self.clock.now += 10
        self.scene.items()                                    # it ran out
        self.assertGreater(self.scene.version, before)

    def test_resending_keeps_it_up_past_the_first_ttl(self):
        self.scene.apply(text("t", ttl=4))
        self.clock.now += 3
        self.scene.apply(text("t", ttl=4))
        self.clock.now += 3
        self.assertEqual(len(self.scene.items()), 1)

    def test_next_change_is_the_soonest_expiry(self):
        self.assertIsNone(self.scene.next_change())
        self.scene.apply(text("a", ttl=10))
        self.scene.apply(text("b", ttl=4))
        self.assertAlmostEqual(self.scene.next_change(), 4.0)

    def test_unusable_payloads_are_ignored(self):
        for payload in ({}, {"id": ""}, {"id": "x", "shape": "star"}, {"id": "y", "ttl": "soon"}):
            self.scene.apply(payload)
        self.assertEqual(len(self.scene), 0)

    def test_clear_empties_the_scene(self):
        self.scene.apply(text())
        self.scene.clear()
        self.assertEqual(self.scene.items(), [])


@unittest.skipIf(R is None, "Pillow is not installed")
class RasterTests(unittest.TestCase):
    def draw(self, payloads, width=1280, height=960, ratio=1.0):
        scene = S.Scene(Clock())
        for payload in payloads:
            scene.apply(payload)
        return R.render(scene.items(), width, height, ratio, R.Fonts(R.default_font_path()))

    def test_colors_parse_with_alpha_first(self):
        self.assertEqual(R.parse_color("#ff8040"), (255, 128, 64, 255))
        self.assertEqual(R.parse_color("#80ff8040"), (255, 128, 64, 128))
        self.assertEqual(R.parse_color("white"), (255, 255, 255, 255))
        self.assertIsNone(R.parse_color(""))
        self.assertIsNone(R.parse_color("not a color"))

    def test_a_rectangle_lands_where_its_canvas_position_and_pixel_size_say(self):
        image = self.draw([rect(x=640, y=480, w=100, h=50, color="", fill="#ffff0000")], width=2560, height=1920, ratio=2.0)
        self.assertEqual(image.getpixel((1285, 965))[:3], (255, 0, 0))              # just inside the top left: x 640 of 1280 is 1280 of 2560
        self.assertEqual(image.getpixel((1270, 965))[3], 0)                          # left of it: nothing
        self.assertEqual(image.getpixel((1280 + 199, 960 + 99))[:3], (255, 0, 0))    # 100 x 50 logical pixels at ratio 2 is 200 x 100 device pixels
        self.assertEqual(image.getpixel((1280 + 205, 960 + 50))[3], 0)

    def test_the_canvas_is_stretched_over_the_whole_window(self):
        image = self.draw([rect(x=1260, y=940, w=10, h=10, color="", fill="#ffff0000")], width=1920, height=1080)
        self.assertEqual(image.getpixel((1890 + 5, 1057 + 5))[:3], (255, 0, 0))      # x 1260 of 1280 across 1920 pixels; y 940 of 960 down 1080

    def test_text_draws_pixels_in_its_color_and_nothing_elsewhere(self):
        image = self.draw([text("t", "WFMT", x=100, y=100, color="#00ff00")], width=1280, height=960)
        box = image.getbbox()
        self.assertIsNotNone(box)
        self.assertGreaterEqual(box[0], 99)
        self.assertGreaterEqual(box[1], 99)
        self.assertLess(box[2], 200)
        greens = [p for p in image.crop(box).getdata() if p[3] > 200]
        self.assertTrue(greens and all(p[:3] == (0, 255, 0) for p in greens))

    def test_text_scales_with_display_scaling(self):
        small = self.draw([text("t", "WFMT", x=10, y=10)], ratio=1.0).getbbox()
        large = self.draw([text("t", "WFMT", x=10, y=10)], ratio=2.0).getbbox()
        self.assertGreater(large[2] - large[0], (small[2] - small[0]) * 1.6)

    def test_circles_and_lines_draw(self):
        image = self.draw([{"id": "c", "shape": "circle", "color": "#ff00ff", "fill": "", "x": 640, "y": 480, "radius": 20, "ttl": 4},
                           {"id": "v", "shape": "vect", "color": "#00ffff", "ttl": 4, "vector": [{"x": 100, "y": 100}, {"x": 300, "y": 100, "marker": "cross"}]}])
        self.assertEqual(image.getpixel((640, 480 - 20))[:3], (255, 0, 255))        # the top of the ring
        self.assertEqual(image.getpixel((640, 480))[3], 0)                           # hollow
        self.assertEqual(image.getpixel((200, 100))[:3], (0, 255, 255))             # the line between the points

    def test_a_group_is_placed_at_its_top_left_and_the_distances_inside_it_are_pixels(self):
        panel = {"id": "g_card", "shape": "rect", "color": "", "fill": "#ff0000ff", "x": 100, "y": 100, "w": 10, "h": 10, "ttl": 4}
        marker = {"id": "g_x1", "shape": "rect", "color": "", "fill": "#ffffff00", "x": 116, "y": 130, "w": 4, "h": 4, "ttl": 4}
        scene = S.Scene(Clock())
        scene.apply(panel)
        scene.apply(marker)
        scene.apply({"id": "other", "shape": "rect", "color": "", "fill": "#ffff0000", "x": 500, "y": 500, "w": 4, "h": 4, "ttl": 4})
        image = R.render(scene.items(), 1280, 960, 1.25, R.Fonts(R.default_font_path()), ["g_"])
        self.assertEqual(image.getpixel((101, 101))[:3], (0, 0, 255))                # the group sits at its panel's canvas position
        self.assertEqual(image.getpixel((121, 138))[:3], (255, 255, 0))              # 16 and 30 pixels along, times the 1.25 display scaling: 100 + 20, 100 + 37.5
        self.assertEqual(image.getpixel((117, 131))[3], 0)                           # not where a canvas-unit reading would put it
        self.assertEqual(image.getpixel((501, 501))[:3], (255, 0, 0))                # an item in no group is placed in canvas units
        self.assertEqual(R.group_of("g_x1", ["g_", "g_x"]), "g_x")                   # the longest prefix wins

    def test_a_panel_with_a_radius_has_rounded_corners_and_one_without_is_square(self):
        rounded = self.draw([rect("r", w=100, h=60, color="", fill="#ffff0000", radius=20)])
        square = self.draw([rect("r", w=100, h=60, color="", fill="#ffff0000")])
        self.assertEqual(rounded.getpixel((6, 6))[3], 0)                     # the corner is cut away
        self.assertEqual(rounded.getpixel((50, 30))[:3], (255, 0, 0))        # the middle is filled
        self.assertEqual(rounded.getpixel((50, 6))[:3], (255, 0, 0))         # and the straight edge is there
        self.assertEqual(square.getpixel((6, 6))[:3], (255, 0, 0))
        large = self.draw([rect("r", w=100, h=60, color="", fill="#ffff0000", radius=500)])
        self.assertEqual(large.getpixel((50, 30))[:3], (255, 0, 0))          # a radius larger than the panel is held to half of it

    def test_an_empty_scene_is_a_transparent_picture(self):
        self.assertIsNone(self.draw([]).getbbox())


def picture(color=(200, 30, 30, 255), size=(40, 30)):
    from PIL import Image
    return Image.new("RGBA", size, color)


def image(ident="i", key="k1", ttl=4, w=40, h=30, **extra):
    return {"id": ident, "shape": "image", "image": picture(size=(w, h)), "key": key, "x": 10, "y": 20, "w": w, "h": h, "ttl": ttl, **extra}


@unittest.skipIf(R is None, "Pillow is not installed")
class ImageTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.scene = S.Scene(self.clock)

    def test_an_image_payload_becomes_an_image_item_drawn_with_the_panels(self):
        self.scene.apply(text("t1"))
        self.scene.apply(image("pic"))
        self.scene.apply(rect("panel"))
        items = self.scene.items()
        self.assertEqual([item.id for item in items], ["pic", "panel", "t1"], "pictures sit in the panel layer, under text")
        self.assertEqual(items[0].kind, S.IMAGE)
        self.assertEqual((items[0].w, items[0].h, items[0].key), (40, 30, "k1"))

    def test_a_picture_without_a_size_or_without_an_image_draws_nothing(self):
        self.scene.apply(image("a", w=0))
        self.scene.apply({"id": "b", "shape": "image", "key": "k", "x": 1, "y": 1, "w": 10, "h": 10, "ttl": 4})
        self.assertEqual(len(self.scene), 0)

    def test_a_resend_with_the_same_key_does_not_repaint_and_a_new_key_does(self):
        self.scene.apply(image())
        version = self.scene.version
        self.clock.now += 1
        self.scene.apply(image())                       # a new object, the same key: the same picture
        self.assertEqual(self.scene.version, version)
        self.scene.apply(image(key="k2"))
        self.assertGreater(self.scene.version, version)

    def test_a_picture_runs_out_and_can_be_removed_like_anything_else(self):
        self.scene.apply(image(ttl=2))
        self.clock.now += 3
        self.assertEqual(self.scene.items(), [])
        self.scene.apply(image())
        self.scene.apply({"id": "i", "ttl": 1})
        self.assertEqual(len(self.scene), 0)

    def test_the_picture_is_drawn_where_it_was_put_at_the_size_asked_for(self):
        out = R.render([S.parse(image(w=64, h=48), 0.0)], 1280, 960)
        self.assertEqual(out.getpixel((10, 20))[:3], (200, 30, 30))
        self.assertEqual(out.getpixel((10 + 63, 20 + 47))[3], 255)
        self.assertEqual(out.getpixel((10 + 64, 20))[3], 0)
        self.assertEqual(out.getpixel((9, 20))[3], 0)

    def test_display_scaling_makes_it_larger_and_the_canvas_moves_it(self):
        item = S.parse(image(w=40, h=30, x=640, y=480), 0.0)
        out = R.render([item], 2560, 1920, ratio=2.0)
        self.assertEqual(out.getpixel((1280, 960))[3], 255)               # canvas (640, 480) is the middle of the window
        self.assertEqual(out.getpixel((1280 + 79, 960 + 59))[3], 255)     # 40 x 30 logical pixels at 200% is 80 x 60 device pixels
        self.assertEqual(out.getpixel((1280 + 80, 960))[3], 0)

    def test_the_picture_keeps_its_own_transparency(self):
        from PIL import Image
        half = Image.new("RGBA", (10, 10), (0, 255, 0, 100))
        out = R.render([S.parse({"id": "p", "shape": "image", "image": half, "key": "h", "x": 0, "y": 0, "w": 10, "h": 10, "ttl": 4}, 0.0)], 1280, 960)
        self.assertEqual(out.getpixel((5, 5)), (0, 255, 0, 100))

    def test_a_picture_partly_off_the_canvas_is_cut_off_and_one_wholly_off_draws_nothing(self):
        part = R.render([S.parse(image(w=40, h=30, x=-20, y=-10), 0.0)], 1280, 960)
        self.assertEqual(part.getpixel((0, 0))[3], 255)
        self.assertEqual(part.getpixel((19, 19))[3], 255)
        self.assertEqual(part.getpixel((20, 0))[3], 0)
        gone = R.render([S.parse(image(x=5000, y=5000), 0.0), S.parse(image("b", x=-500, y=-500), 0.0)], 1280, 960)
        self.assertEqual(gone.getbbox(), None)

    def test_a_picture_that_is_not_an_image_is_skipped_not_raised(self):
        out = R.render([S.parse({"id": "p", "shape": "image", "image": "not a picture", "key": "x", "x": 0, "y": 0, "w": 10, "h": 10, "ttl": 4}, 0.0)], 1280, 960)
        self.assertEqual(out.getbbox(), None)


class ImageClientTests(unittest.TestCase):
    """OverlayClient.send_image and the placement wrappers: no tkinter and no EDMC."""

    def setUp(self):
        import types
        from unittest import mock
        stub = sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))
        if not hasattr(stub, "config"):
            stub.config = types.SimpleNamespace(get_str=lambda key, default="": default, set=lambda *a, **k: None)
        sys.modules.setdefault("myNotebook", types.ModuleType("myNotebook"))
        from plugin import overlay, overlay_layout, overlay_native
        self.overlay, self.layout, self.native = overlay, overlay_layout, overlay_native
        self.sent = []
        self.accepting = mock.patch.object(overlay_native, "accepting", return_value=True)
        self.accepting.start()
        self.addCleanup(self.accepting.stop)
        raw = mock.patch.object(overlay.OverlayClient, "_send_raw", lambda _self, payload: self.sent.append(payload))
        raw.start()
        self.addCleanup(raw.stop)
        self.addCleanup(lambda: (setattr(overlay, "_hidden", False), overlay._last.clear()))
        self.client = overlay.OverlayClient()

    def test_a_picture_is_sent_to_the_built_in_overlay(self):
        self.assertTrue(self.client.send_image("pic", "IMG", 5, 6, 40, 30, "k", ttl=3))
        payload = self.sent[-1]
        self.assertEqual((payload["shape"], payload["image"], payload["key"], payload["x"], payload["y"], payload["w"], payload["h"], payload["ttl"]),
                         ("image", "IMG", "k", 5, 6, 40, 30, 3))

    def test_with_another_overlay_nothing_is_sent_and_the_answer_is_false(self):
        self.accepting.stop()
        self.addCleanup(self.accepting.start)
        self.assertFalse(self.client.send_image("pic", "IMG", 5, 6, 40, 30, "k"))
        self.assertEqual(self.sent, [])

    def test_a_picture_is_moved_by_a_shifted_client(self):
        self.layout.ShiftedClient(self.client, 100, 50).send_image("pic", "IMG", 5, 6, 40, 30, "k")
        self.assertEqual((self.sent[-1]["x"], self.sent[-1]["y"]), (105, 56))

    def test_a_hidden_displays_picture_is_cleared_not_drawn(self):
        self.client.send_image("pic", "IMG", 5, 6, 40, 30, "k", ttl=3)
        count = len(self.sent)
        self.assertFalse(self.layout.HiddenClient(self.client).send_image("pic", "IMG", 5, 6, 40, 30, "k"))
        self.assertGreater(len(self.sent), count)
        self.assertNotIn("image", self.sent[-1])

    def test_a_picture_comes_back_when_the_overlays_are_shown_again(self):
        self.client.send_image("pic", "IMG", 5, 6, 40, 30, "k", ttl=30)
        self.overlay.set_all_hidden(True)
        self.sent.clear()
        self.overlay.set_all_hidden(False)
        self.assertTrue(any(p.get("shape") == "image" for p in self.sent))


class ImageGuardTests(unittest.TestCase):
    def test_a_picture_never_reaches_the_socket_if_the_overlay_was_switched_after_it_was_drawn(self):
        import types
        from unittest import mock
        stub = sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))
        if not hasattr(stub, "config"):
            stub.config = types.SimpleNamespace(get_str=lambda key, default="": default, set=lambda *a, **k: None)
        sys.modules.setdefault("myNotebook", types.ModuleType("myNotebook"))
        from plugin import overlay, overlay_native
        client = overlay.OverlayClient()
        picture = {"id": "pic", "shape": "image", "image": object(), "key": "k", "x": 1, "y": 1, "w": 2, "h": 2, "ttl": 3}
        with mock.patch.object(overlay_native, "accepting", return_value=False), \
                mock.patch.object(overlay.OverlayClient, "_connect_locked", side_effect=AssertionError("opened the socket")):
            client._send_raw(picture)                          # returns quietly: nothing is serialized and no connection is tried


if __name__ == "__main__":
    unittest.main()
