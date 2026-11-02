"""The orange used for text on the main panel (panelkit.accent_color) must be readable on EDMC's light Default theme as well as the dark ones.

The bright Elite orange (#ff8c0d) is only about 1.7 to 2.3:1 against the light Default theme's backgrounds, so the light theme gets a darker orange.
"""
from __future__ import annotations

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

panelkit = None
theme_stub = None


def setUpModule():
    """Import panelkit against stand-ins for EDMC's modules, and take them out again afterwards so nothing leaks into other tests."""
    global panelkit, theme_stub
    config = types.ModuleType("config")
    config.appname = "EDMarketConnector"
    config.config = types.SimpleNamespace(get_str=lambda key, default="": default, get_bool=lambda key, default=False: default)
    theme_stub = types.SimpleNamespace(active=None, THEME_DEFAULT=0, THEME_DARK=1, THEME_TRANSPARENT=2)
    theme = types.ModuleType("theme")
    theme.theme = theme_stub
    patcher = mock.patch.dict(sys.modules, {"config": config, "theme": theme, "myNotebook": types.ModuleType("myNotebook")})
    patcher.start()
    sys.modules.pop("plugin.panelkit", None)
    from plugin import panelkit as loaded
    panelkit = loaded
    # Another test may have imported panelkit already (the package keeps it as an attribute), bound to its own theme: use ours.
    panelkit_patch = mock.patch.object(loaded, "theme", theme_stub)
    panelkit_patch.start()
    globals()["_patcher"] = patcher
    globals()["_panelkit_patch"] = panelkit_patch


def tearDownModule():
    globals()["_panelkit_patch"].stop()
    globals()["_patcher"].stop()
    sys.modules.pop("plugin.panelkit", None)


def _luminance(color: str) -> float:
    channels = []
    for i in (1, 3, 5):
        c = int(color[i:i + 2], 16) / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


class AccentColorTests(unittest.TestCase):
    def test_light_theme_gets_the_dark_orange(self) -> None:
        theme_stub.active = theme_stub.THEME_DEFAULT
        self.assertEqual(panelkit.accent_color(), panelkit.ACCENT_ON_LIGHT)

    def test_dark_themes_keep_the_bright_orange(self) -> None:
        for active in (theme_stub.THEME_DARK, theme_stub.THEME_TRANSPARENT):
            theme_stub.active = active
            self.assertEqual(panelkit.accent_color(), panelkit.ACCENT_ON_DARK)

    def test_readable_on_each_theme(self) -> None:
        # White and the common light system grays for the Default theme; near-black for Dark.
        for background in ("#ffffff", "#f0f0f0", "#d9d9d9"):
            self.assertGreaterEqual(_contrast(panelkit.ACCENT_ON_LIGHT, background), 4.5, background)
        self.assertGreaterEqual(_contrast(panelkit.ACCENT_ON_DARK, "#0d0d0d"), 4.5)


if __name__ == "__main__":
    unittest.main()
