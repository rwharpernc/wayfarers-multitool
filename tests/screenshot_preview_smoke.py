"""Opens the screenshot preview window (plugin/screenshots.py, PreviewWindow) with EDMC stubbed, and checks that the image is scaled into a
bounded box for very wide and very tall sources (never past the screen), that the window re-fits the image when it is resized, that the
Open Folder and Close actions work, and that Esc closes it. Run by test_screenshot_preview_smoke.py in a subprocess so the stand-ins
never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
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


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui",
          "win32process", "win32clipboard", "pywintypes", "psutil", "ttkHyperlinkLabel"):
    sys.modules[n] = Any(n)
nbmod = Any("myNotebook")
nbmod.Frame, nbmod.Label, nbmod.Button, nbmod.Checkbutton = tk.Frame, tk.Label, tk.Button, tk.Checkbutton
sys.modules["myNotebook"] = nbmod
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
        return saved.get(key, default)

    def get_int(self, key, default=0):
        return default

    def get(self, key, default=None):
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

from PIL import Image  # noqa: E402
import io  # noqa: E402
from plugin import screenshots  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()
    root.after(150)
    root.update()


def png(width, height):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), (40, 90, 160)).save(buffer, format="PNG")
    return buffer.getvalue()


screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
max_w, max_h = screenshots.preview_bounds(screen_w, screen_h)
check(max_w <= screen_w and max_h <= screen_h, f"the box fits the screen: {(max_w, max_h)} on {(screen_w, screen_h)}")
check(max_w <= screenshots._PREVIEW_MAX_WIDTH and max_h <= screenshots._PREVIEW_MAX_HEIGHT, "the box never passes the fixed ceilings")

# fit_image: a genuine two-dimensional fit, aspect kept, never enlarged
for size in ((7680, 1440), (1440, 7680), (4000, 3000), (100, 60)):
    fitted = screenshots.fit_image(Image.new("RGB", size), 900, 500)
    check(fitted.width <= 900 and fitted.height <= 500, f"{size} fits the box: {fitted.size}")
    check(abs(fitted.width / fitted.height - size[0] / size[1]) < 0.05 * size[0] / size[1] + 0.05, f"{size} keeps its aspect: {fitted.size}")
check(screenshots.fit_image(Image.new("RGB", (100, 60)), 900, 500).size == (100, 60), "a small image is not enlarged")

for label, size in (("triple-screen", (7680, 1440)), ("tall", (1440, 7680)), ("ordinary", (1920, 1080))):
    saved.clear()
    opened = []
    screenshots.open_folder = lambda path: opened.append(path)
    win = screenshots.PreviewWindow(root, png(*size), "Recent capture", folder="C:/shots")
    pump()
    shown_w, shown_h = win.image_size
    check(win.alive, f"{label}: the window opens")
    check(shown_w <= max_w and shown_h <= max_h, f"{label}: image {win.image_size} inside the box {(max_w, max_h)}")
    check(win.window.winfo_width() <= screen_w and win.window.winfo_height() <= screen_h,
          f"{label}: window {win.window.winfo_width()}x{win.window.winfo_height()} inside the screen {screen_w}x{screen_h}")
    check(win._label.image is win._photo, f"{label}: the image reference is kept")
    check(win._photo.width() >= 1 and win._photo.height() >= 1, f"{label}: the image is not empty")
    check("px" in win._shell._status.cget("text"), f"{label}: the status shows the size")

    # shrinking the window re-fits the image inside it
    win.window.geometry("500x420")
    pump()
    body_w, body_h = win._shell.body.winfo_width(), win._shell.body.winfo_height()
    shown_w, shown_h = win.image_size
    check(shown_w <= body_w and shown_h <= body_h, f"{label}: after a resize {win.image_size} inside the body {(body_w, body_h)}")

    # The test windows cannot take focus, so a generated key press would go nowhere: run the window's own Esc binding instead.
    script = win.window.bind("<Escape>")
    check(bool(script), f"{label}: Esc is bound")
    win.window.tk.eval(script.replace("%#", "0").replace("%W", str(win.window)).replace("%%", "%"))
    pump()
    check(not win.alive, f"{label}: Esc closes")

# the actions and the remembered geometry
saved.clear()
win = screenshots.PreviewWindow(root, png(800, 600), "Capture", folder="C:/shots")
pump()
from plugin.uikit.widgets import FlatButton  # noqa: E402


def buttons(widget):
    found = []
    for child in widget.winfo_children():
        if isinstance(child, FlatButton):
            found.append(child)
        found += buttons(child)
    return found


names = {b.cget("text"): b for b in buttons(win.window)}
check({"Help", "Open Folder", "Close"} <= set(names), f"the header buttons: {sorted(names)}")
opened.clear()
names["Open Folder"]._command()
check(opened == ["C:/shots"], f"Open Folder opens the folder: {opened}")
names["Close"]._command()
pump()
check(not win.alive, "Close closes")
check(screenshots._PREVIEW_CONFIG_GEOMETRY in saved, "closing saves the geometry")

# a saved size from a larger screen is not reused; a good one is
saved[screenshots._PREVIEW_CONFIG_GEOMETRY] = f"{screen_w + 500}x{screen_h + 500}+0+0"
win = screenshots.PreviewWindow(root, png(800, 600), "Capture", folder="")
pump()
check(win.window.winfo_width() <= screen_w and win.window.winfo_height() <= screen_h, "an oversized saved geometry is ignored")
check("Open Folder" not in {b.cget("text") for b in buttons(win.window)}, "no folder, no Open Folder button")
win.close()

if problems:
    print("PROBLEMS:", len(problems))
    for line in problems:
        print(" -", line)
    sys.exit(1)
print("PREVIEW OK")
