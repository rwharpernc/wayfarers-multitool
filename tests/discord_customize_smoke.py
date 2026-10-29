"""Opens the real Customize Discord posts dialog (plugin/discord_customize.py) with EDMC stubbed, and checks that its preview follows the checkboxes, that Save, Save as, Rename and
Delete keep your own templates (and refuse to touch a preset), that choosing a template makes it the one posts use, and that the report choice switches between the BGS report and
Powerplay progress. Run by test_discord_customize_smoke.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
import tempfile
import types
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
import tkinter as tk


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes", "psutil"):
    sys.modules[n] = Any(n)
theme = Any("theme")
theme.theme = mock.MagicMock()
theme.theme.active = None
theme.theme.THEME_DEFAULT = 0
sys.modules["theme"] = theme
saved = {}


class Cfg:
    default_journal_dir = ""

    def get_str(self, key, default=""):
        return saved.get(key, default) or ""

    def get_bool(self, key, default=False):
        return default

    def get_int(self, key, default=0):
        return default

    def get(self, key, default=None):
        return saved.get(key, default)

    def set(self, key, value):
        saved[key] = value


cfgmod = types.ModuleType("config")
cfgmod.appname = "EDMarketConnector"
cfgmod.config = Cfg()
sys.modules["config"] = cfgmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()

from plugin import bgs_discord, discord_customize as C, discord_templates as T, powerplay_discord  # noqa: E402
from plugin.uikit import dialogs  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump(times=4):
    for _ in range(times):
        root.update()


tmp = tempfile.mkdtemp()
T.templates = T.DiscordTemplates(tmp)
answer = {"name": "", "confirm": True}
dialogs.set_test_responder(dialogs.answers(prompt=lambda title, message: answer["name"], confirm=lambda title, message: answer["confirm"]))


def preview():
    return win._text.get("1.0", "end")


win = C.show(root)
pump()
check(win.alive, "the dialog did not open")
check("WFMT BGS report" in preview(), f"the preview shows the post: {preview()[:80]!r}")
check("made-up example data" in win._count.cget("text"), f"with no tick the preview says it is example data: {win._count.cget('text')!r}")
check("characters in 1 message" in win._count.cget("text"), f"the preview counts the post: {win._count.cget('text')!r}")
check("bold" in win._text.tag_names() and win._text.tag_ranges("bold"), "the bold parts of the post are drawn bold")

# A checkbox changes the preview and says the template is changed; the built-in preset cannot be saved over.
win._vars["heading"].set(False)
win._on_changed()
pump()
check("WFMT BGS report" not in preview(), "turning the heading off takes it out of the preview")
check("Changed from Standard" in win._note.cget("text"), f"the note says the template is changed: {win._note.cget('text')!r}")
check(T.templates.chosen(T.BGS).name == T.STANDARD, "a changed checkbox does not change the template posts use")
win._on_save()
check("cannot be changed" in win._note.cget("text") and T.templates.names(T.BGS) == list(T.PRESET_NAMES), "Save does not touch a preset")

# Save as keeps it under a name and chooses it.
answer["name"] = "No heading"
win._on_save_as()
pump()
check(T.templates.names(T.BGS)[-1] == "No heading", f"Save as keeps the template: {T.templates.names(T.BGS)}")
check(T.templates.chosen(T.BGS).name == "No heading" and win._template_var.get() == "No heading", "the saved template is the one chosen")
check(T.templates.chosen(T.BGS).options["heading"] is False, "it kept the checkbox")
check("Changed from" not in win._note.cget("text"), f"saved means not changed: {win._note.cget('text')!r}")
answer["name"] = "Standard"
win._on_save_as()
check("built-in preset" in win._note.cget("text") and T.templates.names(T.BGS).count("Standard") == 1, f"a preset's name is refused: {win._note.cget('text')!r}")

# Picking another template switches to it and makes it the one posts use.
win._template_var.set("Compact")
win._on_template_picked()
pump()
check(T.templates.chosen(T.BGS).name == "Compact", "picking a template chooses it")
check(win._vars["compact"].get() is True and "No heading" not in win._note.cget("text"), "the checkboxes follow the picked template")
check("Compact is now the template" in win._note.cget("text"), f"the note says so: {win._note.cget('text')!r}")

# Rename and delete act on your own templates only.
win._template_var.set("No heading")
win._on_template_picked()
answer["name"] = "Quiet"
win._on_rename()
check(T.templates.names(T.BGS)[-1] == "Quiet" and win._template_var.get() == "Quiet", f"Rename renames it: {T.templates.names(T.BGS)}")
win._on_delete()
check("Quiet" not in T.templates.names(T.BGS) and T.templates.chosen(T.BGS).name == T.STANDARD and win._template_var.get() == T.STANDARD,
      f"Delete removes it and goes back to Standard: {T.templates.names(T.BGS)}")
win._on_delete()
check("cannot be deleted" in win._note.cget("text"), "a preset cannot be deleted")
answer["confirm"] = False
answer["name"] = "Keep me"
win._on_save_as()
win._on_delete()
check("Keep me" in T.templates.names(T.BGS), "answering no to Delete keeps the template")
answer["confirm"] = True

# The preview uses the report window's data when there is some.
view = bgs_discord.sample_view()
provider = lambda: (view, "Example System", [])  # noqa: E731
C.register_data(T.BGS, provider)
win._refresh()
pump()
check("your current tick" in win._count.cget("text"), f"with a tick the preview says it is yours: {win._count.cget('text')!r}")
C.unregister_data(T.BGS, provider)

# The report choice switches to Powerplay progress.
win.select_report(T.POWERPLAY)
pump()
check("WFMT Powerplay progress" in preview() and "power" in win._vars, f"the Powerplay preview and checkboxes: {preview()[:60]!r}")
check("scope" not in win._vars, "the systems choice is only for the BGS report")
check("CP is an estimate" in preview(), "the estimate note is shown")
win._vars["cp"].set(False)
win._on_changed()
pump()
check("CP is an estimate" not in preview() and "CP)" not in preview(), "turning the estimated CP off takes it out of the preview")
win._vars["activities"].set(True)
win._on_changed()
check("Acquisition 80" in preview(), "merits by activity can be added")
rows_provider = lambda: ([], "", "")  # noqa: E731
C.register_data(T.POWERPLAY, rows_provider)
win._refresh()
check("made-up example data" in win._count.cget("text"), "a session with nothing in it falls back to example data")
C.unregister_data(T.POWERPLAY, rows_provider)

# A second show raises the same window; closing and reopening works.
check(C.show(root, T.BGS) is win and win._report == T.BGS, "showing it again raises the same dialog on that report")
win.close()
pump()
check(not win.alive, "Done closes the dialog")
again = C.show(root, T.POWERPLAY)
check(again.alive and again is not win and again._report == T.POWERPLAY, "it opens again")
again.close()

dialogs.set_test_responder(None)
root.destroy()
if problems:
    print("PROBLEMS:\n  " + "\n  ".join(problems))
    sys.exit(1)
print("DISCORD CUSTOMIZE OK")
