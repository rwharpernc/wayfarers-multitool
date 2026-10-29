"""Trade panel: every button label has hover text, read from the source so no Tk or EDMC stand-ins are needed."""
import ast
import pathlib
import unittest

_SOURCE = pathlib.Path(__file__).resolve().parent.parent / "plugin" / "trade_panel.py"
_LABELS = ("Sell", "Buy", "Reset", "Save session", "History", "Rebuild", "Find routes", "Cancel", "Copy next system",
           "Hops", "Round trip", "Near me", "Galaxy", "Best picks", "Price finder")


def _button_tips() -> dict:
    for node in ast.parse(_SOURCE.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "BUTTON_TIPS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("BUTTON_TIPS not found")


class ButtonTipTests(unittest.TestCase):
    def test_every_button_has_text(self) -> None:
        tips = _button_tips()
        for label in _LABELS:
            self.assertTrue(tips.get(label, "").strip(), label)

    def test_every_tip_names_its_button_and_is_one_sentence(self) -> None:
        for key, text in _button_tips().items():
            self.assertTrue(text.startswith(f"{key} - "), key)
            self.assertNotIn(". ", text, key)


if __name__ == "__main__":
    unittest.main()
