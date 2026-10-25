"""Builds Settings -> General -> Online lookups (plugin/settings_online.py) with its Local star index group in a real Tk window, presses the buttons against a fake server and a temporary folder, and
checks the status text, which buttons are enabled and that the tick is saved. Run by test_star_index_settings_smoke in a subprocess. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import os
import sys
import tempfile
import threading
import time
import types
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
from tkinter import ttk


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes",
          "psutil", "ttkHyperlinkLabel", "theme"):
    sys.modules[n] = Any(n)
nbmod = Any("myNotebook")
nbmod.Frame, nbmod.Label, nbmod.Button, nbmod.Checkbutton = tk.Frame, tk.Label, tk.Button, tk.Checkbutton
nbmod.Notebook = ttk.Notebook
sys.modules["myNotebook"] = nbmod
saved = {}


class Cfg:
    def get_str(self, key, default=""):
        return saved.get(key, default) or ""

    def get_bool(self, key, default=False):
        return saved.get(key, default)

    def get_int(self, key, default=0):
        return saved.get(key, default)

    def set(self, key, value):
        saved[key] = value


cfgmod = types.ModuleType("config")
cfgmod.appname = "EDMarketConnector"
cfgmod.config = Cfg()
cfgmod.user_agent = "WFMT-test"
cfgmod.appversion = lambda: "5.13.0"
sys.modules["config"] = cfgmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def wait_until(condition, seconds=20):
    end = time.time() + seconds
    while time.time() < end:
        root.update()
        if condition():
            return True
        time.sleep(0.02)
    return False


try:
    from plugin import settings_online, spansh_courtesy, star_index, star_index_job, star_index_settings
    import fake_dump_server
    import star_index_fixtures

    with tempfile.TemporaryDirectory() as tmp:
        folder = os.path.join(tmp, "star_index")
        dump = os.path.join(tmp, "d.json.gz")
        star_index_fixtures.write_dump(dump, star_index_fixtures.make_stars(300), extras=20)
        with open(dump, "rb") as handle:
            body = handle.read()
        server = fake_dump_server.FakeServer(body)
        courtesy = spansh_courtesy.Courtesy(opener=server, clock=lambda: 0.0, sleep=lambda seconds: None)
        job = star_index_job.StarIndexJob(folder, courtesy=courtesy, free_space=lambda directory: 10 ** 12)

        # The whole Online lookups page builds, with the group at the bottom.
        notebook = ttk.Notebook(root)
        with mock.patch.object(star_index_settings, "build_group", wraps=lambda parent, row: (star_index_settings.StarIndexGroup(parent, row, job), row + 5)) as built:
            settings_online.build_settings(notebook)
            root.update()
        check(built.called, "the Online lookups page builds the Local star index group")
        page = root.nametowidget(notebook.tabs()[0])
        labels = [w.cget("text") for w in page.winfo_children() if isinstance(w, tk.Label)]
        check(any("Local star index" in t for t in labels), "the group has its heading")
        check(any("downloads.spansh.co.uk" in t for t in labels), "the page says where the file comes from")

        group = star_index_settings.StarIndexGroup(page, 100, job)
        root.update()
        check("Not installed" in group.status.get(), "the status says not installed at first")
        states = {key: str(button["state"]) for key, button in group.buttons.items()}
        check(states == {"download": "normal", "update": "disabled", "cancel": "disabled", "delete": "disabled"}, f"buttons before installing: {states}")
        check(not server.requests, "nothing is requested until a button is pressed")

        group.buttons["download"].invoke()
        check(wait_until(lambda: star_index.status(folder).state == "ok" and not job.snapshot().active), "the download and build finish")
        wait_until(lambda: group.status.get().startswith("Installed"))       # the page's own timer picks the new state up
        check("300 neutron stars" in group.status.get(), f"the status shows the count: {group.status.get()!r}")
        states = {key: str(button["state"]) for key, button in group.buttons.items()}
        check(states == {"download": "disabled", "update": "normal", "cancel": "disabled", "delete": "normal"}, f"buttons after installing: {states}")
        check(len(server.requests) == 1, "one request was made")

        group.buttons["update"].invoke()
        wait_until(lambda: "up to date" in group.status.get())
        check("up to date" in group.status.get(), f"an update of an unchanged file says so: {group.status.get()!r}")
        check(server.requests[-1].get("if-modified-since") == server.last_modified, "the update was a conditional request")

        group.use.set(False)
        group.save()
        check(saved.get(star_index.CONFIG_USE) is False, "the tick is saved when changed")
        group.use.set(True)
        group.save()
        check(saved.get(star_index.CONFIG_USE) is True, "and saved when changed back")

        group.buttons["delete"].invoke()
        root.update()
        check(star_index.status(folder).state == "missing", "Delete removes the index")
        check("deleted" in group.status.get(), f"and says so: {group.status.get()!r}")
except Exception as exc:  # noqa: BLE001
    import traceback
    problems.append("raised: " + "".join(traceback.format_exception(exc)))

root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("STAR INDEX SETTINGS OK")
