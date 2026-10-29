# Development guide

How to set up, build, test and try out changes to WFMT.

- If you just want to *use* the plugin, the [README](../README.md) is what you want.
- For how the code is organized and why, read [TECHNICAL.md](TECHNICAL.md) next.
- For the reasoning behind the main decisions (and what was considered and not done), read [DESIGN_NOTES.md](DESIGN_NOTES.md).

## What you need

- **Python 3** (a recent version; the code uses modern type hints). The plugin itself runs inside
  EDMC's own Python, so you only need your own copy to run the tests and checks.
- **Node.js** (a current version), for the small build scripts (`npm run build`, `deploy` and `package`).
  Node is only used to copy and zip files. There is nothing to install with `npm install`.
- **[EDMC](https://github.com/EDCD/EDMarketConnector)**, to try the plugin for real.
- **Git**, to get the code and share changes.

## Get the code

```bash
git clone https://github.com/rwharpernc/wayfarers-multitool.git
cd wayfarers-multitool
```

**Layout**

- The plugin source is the `plugin/` folder.
- Tests are in `tests/`, build scripts in `scripts/`, and documentation in `docs/`.
- [TECHNICAL.md](TECHNICAL.md) section 2 has the full layout, and [MODULES.md](MODULES.md) names every module. Adding a module means adding its row there (a test checks).

**The bug-report form**

- `.github/ISSUE_TEMPLATE/bug_report.yml` is the bug-report form that Settings → General → Help → **Report an issue** opens.
- Its `id: environment` field must stay in step with `plugin/issue_report.py` (a test checks).
- The form is not part of the build, so a change to it takes effect for everyone once pushed to `master`.

## Build

```bash
npm run build      # copies plugin/ to dist/Wayfarers-Multitool (plus LICENSE and THIRD-PARTY-NOTICES.md)
npm run package    # builds, then zips the dist/Wayfarers-Multitool folder itself (every entry starts with Wayfarers-Multitool/) into dist/Wayfarers-Multitool.zip
```

`dist/` is ignored by git. The version number comes from `plugin/__init__.py` (and is mirrored in
`package.json`).

## Try your changes in EDMC

1. Run `npm run deploy`. It builds, detects which OS you are on, and merges the result into EDMC's
   plugins folder as `Wayfarers-Multitool`:
   - Windows: `%LOCALAPPDATA%\EDMarketConnector\plugins`
   - Linux: `~/.local/share/EDMarketConnector/plugins`, or the Flatpak equivalent
     (`~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/plugins`), whichever exists
   - macOS: `~/Library/Application Support/EDMarketConnector/plugins`

   For a non-standard location, set `WFMT_PLUGINS_DIR` or pass `--plugins-dir <path>`
   (`node scripts/build.mjs --install --plugins-dir <path>`). `npm run build` alone just builds and
   prints where it would copy to.
2. Restart EDMC. It loads plugin code at start-up, so every change needs a restart.

**Merge the files; don't delete and re-copy the folder.**

- A live plugin folder also holds per-commander data and plugin-managed files that aren't part of the build (saved hotspots, sessions, logs, backups, downloaded updates).
- Overwrite the files the build produces and leave everything else alone.

**Generated file.** `plugin/journal_blueprints.py` is generated.

- Run `python scripts/gen_journal_blueprints.py` (it needs the network) to rebuild it from public data lists (source and license: see ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md).
- Review the diff, and run the tests (`tests/test_ship_plan.py` checks every link points at a row the blueprint table has).
- It is never run by the build.

Settings and window positions are stored in EDMC's own config, under keys starting `wfmt_`.

## Working on Windows and Linux

The same repo is developed on both. Each machine builds and installs for itself, because the build
detects the OS and EDMC's plugins folder (see "Try your changes in EDMC" above).

**Setting up a fresh machine**

1. Install Python 3, a current Node.js, and Git. On Linux the Python Tk bindings are separate
   (Arch/CachyOS: `sudo pacman -S --needed tk nodejs npm`). Without Tk the UI tests and the import
   smoke test fail with `libtk8.6.so` errors.
2. Clone the repo, then run `git config core.autocrlf false` inside it.
   - The `.gitattributes` keeps everything LF; leaving `autocrlf` on can fight it.
   - Line endings are LF on both Windows and Linux. `.editorconfig` tells editors to write LF, and `tests/test_line_endings.py` fails if any text file in the working tree has CRLF.
   - If it does, fix the files with `sed -i 's/\r$//' FILE` (Git Bash or Linux), then run `git add -u` to refresh the index.
3. Set your Git name and email for the repo (`git config user.name` / `user.email`), and turn on the commit checks with `git config core.hooksPath .githooks`.
   - The `pre-commit` hook runs `scripts/check_docs.py` (see "Keeping the docs current" below) and refuses the commit while the docs disagree with the code.
   - The `commit-msg` hook checks the message's form:
     - a subject of 72 characters or fewer, starting with a capital and with no trailing period
     - a blank line
     - body lines of 80 or fewer
     - no chatty asides
   - Aim for a subject of about 50 and a body wrapped at 72.
   - On Linux the hook must be executable, which the repo already records.
   - `tests/test_commit_msg_hook.py` runs it on sample messages.
4. Check it works: `python -m unittest discover -s tests`, `python tests/import_smoke.py`,
   `npm run build` (the first line should name the right OS) and `npm run package`.

**Rules that apply on both machines**

- Everything saved about a player's play is **per commander** (`plugin/commander_data.py`); nothing is shared between commanders.
  - A new data file is classified in `tests/test_data_files_per_commander.py`.
  - A commander's name is never used in a file name (Windows is case-insensitive and rejects some characters; Linux is case-sensitive).
  - The one exception is `exo_observations.json` (facts about bodies, pooled on purpose to check the species prediction; it stores no commander name).
- Read and write files as UTF-8, write through a temporary file and `os.replace`, and keep OS-specific calls behind
  `platform_support.py`. Say in `LINUX_TESTING.md` what has only been tried on one OS.

**Day to day**

- Before starting on a machine: `git pull`. Before switching machines: commit and `git push`.
- `npm run deploy` builds and copies into EDMC's plugins folder for that OS. Restart EDMC after.
- EDMC on Linux may be a Flatpak. Check its log first when something works on one OS and not the other.
  - Linux Flatpak: `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/logs/EDMarketConnector-debug.log`
  - Windows: `%LOCALAPPDATA%\EDMarketConnector\logs\EDMarketConnector-debug.log`
  - EDMC's **Help → Open Log Folder** opens it.
- Not synced by Git (ignored on purpose): `docs/roadmap.md`, `dist/` and other local, ignored files.
  - `docs/TODO.md` is tracked: it is the public list of open work.
  - Copy local notes between machines yourself.

**Keep code portable**

- Don't use Windows-only Tk values such as `SystemWindow` color names, and don't call `powershell.exe`
  or Win32 APIs outside the existing `IS_WINDOWS` branches. Use `platform_support` helpers.
- Keep the Windows and Linux code paths behind `platform_support` (`IS_WINDOWS`, `IS_LINUX`) and say so in
  the feature's Settings tab with a **Works on:** note (see `platform_support.input_support_note`).
  Full list of what each OS does: [TECHNICAL.md section 18](TECHNICAL.md#18-platform-support-windows-and-linux).
- File names: use the game's exact case (`Status.json`), match journals as `Journal.*.log`, always pass
  `encoding=` to `open`, and take the name from a journal `Filename` with `screenshot_naming.journal_basename`
  (Elite writes backslashes even under Proton).
- New modal dialogs: use `ui.style.grab_when_visible(dialog)`, not `dialog.grab_set()` (X11 refuses a grab
  before the window is mapped).
- Text symbols in the UI: stick to ones every font has (`×`, `★`, `→`, `▾`).
- Settings tabs: never `pack` anything into an `nb.Frame`.
  - EDMC's `myNotebook.Frame` puts a gridded spacer child inside every instance, so packing into it raises, EDMC logs `Failed for Plugin "WFMT"` and the whole WFMT Settings tab disappears.
  - Use `grid`, or pack into a plain `tk.Frame`.
  - `tests/test_settings_layout.py` checks the source and `tests/test_prefs_smoke.py` builds the whole tab with EDMC-faithful stand-ins.
- Settings pages scroll: `ui` hands each feature's `build_settings` a `settings_scroll.ScrollContent` instead of a notebook.
  - A page taller than the screen allows (`settings_scroll.height_cap`) gets a scrollbar and the OK button stays visible.
  - Nothing changes for a feature: keep calling `notebook.add(frame, text=...)`.
  - Plain `tk.Frame` rows on a Settings page are recolored to the page color (`ui._match_page_background`), so they don't show as gray bands.
- Where a new feature's Settings go: `ui._build_settings_tabs` lays the tabs out (General, Powerplay, Missions, Exploration, Mining, Trade, BGS, Colonization, Discord, Operations, Overlays; the tabs are shown in alphabetical order).
  - Add the feature to the right group there.
  - Anything it draws on the overlay goes in the Overlays group (a `build_overlay_settings`, or the whole tab if it is an overlay feature), with its place registered in `overlay_placement.SLOTS`.
  - A feature with a `build_settings` that isn't listed still gets a tab, under "Other".
  - To put two small pages on one tab, wrap them with `_stacked_page`. Each feature's `build_settings(notebook)` keeps working unchanged, because the stack accepts `add(frame, text=...)` like a notebook does.
- `monitor.logfile` (EDMC) is a `str` or a `pathlib.Path` depending on the version: wrap it in `str()` before
  comparing it or saving it to JSON.
- Background threads must never touch a Tk widget; hand results back with a queue and `after()`.
- A bug that makes a Settings tab vanish usually means an exception while building it. EDMC catches it
  and logs `Failed for Plugin "WFMT"`, so look for that line.

## Test

```bash
python -m unittest discover -s tests
```

The tests cover the pure-logic modules (parsing, state, estimates, data handling). They don't need EDMC
or a display, because EDMC's `config` module is stubbed inside the tests. There is also a smoke test that
imports every module:

```bash
python tests/import_smoke.py
```

**Two guards worth knowing**

- `tests/test_prefs_smoke.py` builds every Settings tab. It hard-codes the number of top-level tabs, so adding a tab means updating it.
- `tests/test_own_data_files.py` fails if a module defines a data file (`*FILENAME = "x.json"`) that `plugin/update.py` doesn't list in `_OWN_DATA_FILES`.

**Smoke scripts**

- Many features also have a smoke script in `tests/` (named `*_smoke.py`) that builds the real Tk window or panel with EDMC stubbed.
- `tests/test_*_smoke.py` runs each in a subprocess and skips it when Tk has no display.
- On Windows a window that opens takes the keyboard focus, which interrupts anyone typing. So each script that creates a root window imports `tests/quiet_tk.py` first.
  - It disables every Tk and Toplevel on Windows so none can be given the focus, and makes `focus_force` do nothing.
  - The windows may still flash on screen. (Making them transparent too more than doubled the run time, so that is not done.)
- A new smoke script that creates a window should start with `import quiet_tk`.

### Running the tests without windows on your screen

`npm run test:docker` runs the Python tests inside a Linux container (`docker/Dockerfile`) on a virtual display (Xvfb) with a small window manager (openbox), so no window ever appears on your desktop or takes the focus.

- It runs `docker build` each time (cached after the first run), mounts the repo read-only, and runs `python -m unittest discover -s tests` and then `tests/import_smoke.py`.
- Anything after the script name replaces that command, for example `node scripts/docker-test.mjs python tests/mining_history_smoke.py`.

**Setup**

- **Windows:** install Docker Desktop. If its engine is not running, the script starts it (waiting up to three minutes) and quits it again afterward only when it started it and no other containers are running.
- **Linux (Arch/CachyOS):** `sudo pacman -S --needed docker`, then `sudo systemctl enable --now docker.socket` and `sudo usermod -aG docker $USER`.
  - Log out and in again so the group applies (without it, run the script as root or use rootless Docker).
  - Nothing else is needed, because Python, Tk and the fonts live in the image.

**What a pass covers**

- The container is always Linux, whichever machine runs it, so a pass says nothing about Windows-only code (the Win32 overlay, the `quiet_tk` Windows branch, `platform_support.py`).
- The container's fonts are not your desktop's, so the `test_window_fit_*` checks, which measure text, can differ from a run on a real desktop.

**Tests that depend on the date**

Several modules only read events from the last few days before now, so a test that replays a journal with a fixed date must also fix the clock (a `NOW` constant passed in, or a patched `time.time`). Otherwise it passes until that date ages out of the window.

- To look for such tests, run the suite with the clock set ahead. In the container, `apt-get install -y faketime`, then `faketime -f '+60d' python -m unittest discover -s tests`.
- A failure there is real only if it compares an event's own date with the clock. Tests that write a file and compare its modified time with the clock fail in that run for no reason of their own, because `faketime` moves the clock but not the files' times. On 2026-10-23 the ten tests that failed were all of that second kind.

**The built-in overlay tests**

The built-in overlay is tested in layers:

- The scene and the picture (`tests/test_overlay_scene.py`, Pillow only).
- The switch, fonts, text measuring and placement (`tests/test_overlay_native.py`, `tests/test_overlay_fonts.py`, `tests/test_overlay_style.py`).
- Hiding (`tests/test_overlay_hide.py`).
- The Win32 window itself (`plugin/overlay_window.py`) needs a desktop: `scripts/native_overlay_test.py` draws four real cards over Elite (or the screen) to look at.

**Scripts** in `scripts/`:

- `build.mjs`, `package.mjs` and `env.mjs` build and install the plugin; `docker-test.mjs` runs the tests in the container (`npm run test:docker`); `check_docs.py` checks the docs against the code.
- `gen_journal_blueprints.py` and `gen_organic_variants.py` regenerate data tables (source and license: see ATTRIBUTIONS.md and THIRD-PARTY-NOTICES.md).
- `verify_organic_variants.py` checks the color predictions against your own journals.
- `analyze_exo_observations.py` checks the species prediction against the finds WFMT recorded (`exo_observations.json`).
- `native_overlay_test.py` draws real overlay cards over Elite to look at (Windows only).

**Fonts**

- `plugin/fonts/` ships Source Sans 3 (SIL Open Font License; the license file sits beside it and is in THIRD-PARTY-NOTICES.md) for the built-in overlay.
- Font files a player adds go in the same folder. The updater only replaces files that are in the release zip, so they stay.
- A different bundled font needs its license added the same way.

**What is not covered**

Screens and windows aren't covered by automated tests. For those, build, copy and click through the feature in EDMC. [TECHNICAL.md](TECHNICAL.md) section 14 explains what is and isn't tested and why.

## Making a change

1. Keep logic that doesn't need the screen in its own module with no EDMC or Tk imports, so it can be
   unit-tested. [TECHNICAL.md](TECHNICAL.md) section 6 explains the split.
2. Follow the feature-module contract when adding a feature (section 4, with a checklist in section 16).
3. Anything that can size the main window (images, long text) needs a fixed upper bound on every
   dimension. Section 5 explains why.
4. Prefix config keys and overlay ids with `wfmt_<feature>_`.
   Any new network call must follow the API-usage rules in
   [TECHNICAL.md](TECHNICAL.md#keeping-api-traffic-low): opt-in or user-triggered, cached, capped, with a
   timeout, and identified through `http_identity.user_agent()`.
5. **Journal first.** A third-party tool only knows what the game writes to its journal, and not everything is logged, so start a feature from the journal events the game does write.
   - When it falls short, add data from Frontier (signed-in EDMC) or from a community service, or work around it with a labeled estimate or a step the user takes.
   - Record the gap and its workaround in the matching guide's "What the game does and doesn't tell us" table.
   - See the design principle at the top of [TECHNICAL.md](TECHNICAL.md).
6. Update the README and the user guides in `docs/guide/`, the changelog and any affected docs in the same change, including a row in
   [MODULES.md](MODULES.md) for any new module.
7. Write American English in code, names, comments and docs (color, tons, Colonization). `tests/test_american_spelling.py` checks it.
   - The game's own names keep their spelling: journal events such as `ColonisationContribution`, mission and station names, commodity and module names.
   - A line that matches the game's text on purpose carries a `game spelling` comment, which the test lets through.
8. Colors in WFMT's own windows come from `plugin/uikit/palette.py` and must be read when a widget is built (`P.BG`, not a value captured at import time or as a default argument), or a theme chosen later would not reach it. Use `None` as a default and `x or P.TOKEN` inside, or store a token name. `tests/test_window_themes.py` checks every theme's contrast. Text that should not follow the text size setting (a small box in a row) uses `style.font(spec, scaled=False)`.
9. Renaming a saved file, a settings key or a saved field needs a move for what users already have: add it to `plugin/legacy_names.py` (with a test), which runs at start-up.

### Using other people's work

Write code fresh, in your own way. Before using any code, asset or data from another project, check its
license. WFMT is GPL-3.0, so anything added must be compatible with that. If a license asks for a
notice, add it to [../THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md). Credit for ideas goes in
[ATTRIBUTIONS.md](ATTRIBUTIONS.md). Please don't copy code from a project that has no license, since
that means you have no permission to.

## Keeping the docs current

Docs go stale when a screen, setting or file is renamed and the prose is not. `scripts/check_docs.py` catches that mechanically, so it does not depend on someone re-reading everything:

- **links**: every relative link and `#anchor` in the Markdown resolves.
- **labels**: a bold name used as a reference to the screen (after "click", "tick", "press", before "button" or "tab", or in a controls table) is a string in `plugin/`.
- **paths**: every "Settings -> WFMT -> tab" path starts with a real Settings tab, read from the code.
- **files**: every module (`.py`), data file (`.json`) and `wfmt_*` setting key the docs name exists.
- **comments**: a backticked name in a code comment or docstring is defined somewhere in the code.
- **headers**: every page opens with a `# Title` on its first line and a lead paragraph, and bold label lines are never stacked (the standard opening is below).
- **version**: the version is the same in `plugin/__init__.py`, `package.json` and the newest changelog heading, and the example versions in `INSTALL.md`, `LINUX_TESTING.md`, `TECHNICAL.md` and the getting-started and reporting-problems guides are the current one.

Every page opens the same way (the checker enforces the title, the lead and unstacked label lines; the rest is a convention):

1. One `# Title` on the first line (a specification is "<Feature> technical specification").
2. A lead paragraph straight after it: what the page is and who it is for.
3. Optional notes as bullets, after the lead (`- **Author:** ...`, `- **Status:** ...`). Bold label lines are never stacked, because Markdown runs them into one paragraph.
4. A "**On this page:**" list when the page is long.
5. Then the `##` sections.

Run it with `python scripts/check_docs.py` (add `--only labels` for one check). It reads text only and opens no windows. The pre-commit hook (`.githooks/pre-commit`) runs it before every commit, and `tests/test_docs_current.py` runs it in the suite.

When it reports something, fix the doc or comment. Add a name to `docs/doc_terms.txt` only when it legitimately belongs to something else (the game, Discord, GitHub, EDMC, another project) or is a placeholder, and say why in a comment line.

The checker cannot judge whether a sentence is still true, so when you change behavior:

1. Search the docs for the old name and the feature's name (`grep -rn` over `README.md` and `docs/`), not just the guide you think owns it.
2. Update the guide, [features.md](guide/features.md), [planned.md](guide/planned.md) (move a built item out), the matching tech spec, [TODO.md](TODO.md), the changelog and [MODULES.md](MODULES.md).
3. Run `python scripts/check_docs.py` and `npm run test:docker`.

## Releasing

A release is cut from a clean `master`:

1. Set the version in `plugin/__init__.py` and `package.json`.
2. In `CHANGELOG.md`, add a dated section for the version and move the "Unreleased" entries under it.
3. Run the tests, then `npm run package` to build `dist/Wayfarers-Multitool.zip`.
4. Commit, then tag `v<version>` and push the commit and the tag.
5. Publish the release with the zip as its asset:

   ```bash
   gh release create v<version> dist/Wayfarers-Multitool.zip --title "WFMT <version>" --notes-file <the changelog section for the version>
   ```

   The title is `WFMT <version>` with no `v`; the tag keeps the `v` (`v1.0.0`, for example), and the in-app updater reads the tag, not the title.
   Publish it as a normal release, not a draft or a pre-release: the in-app updater and the README's "latest release" link only
   follow official GitHub releases, and they can read them only while the repository is public.
6. Update `docs/guide/known-issues.md` (what is known to go wrong in the new release) and `docs/STATUS.md` (the current release,
   which branches exist, what is still unreleased), and the version examples in `docs/guide/getting-started.md`.

Users download the zip, not the repository. A fix to a released version is made on a short `bugfix/<version>` branch cut from
`master`, merged back with the release, and the branch is then deleted.
