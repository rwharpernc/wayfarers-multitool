# Development guide

Setup, build, test and release procedures for WFMT contributors.

- For using the plugin, see the [README](../README.md).
- For code organization, see [TECHNICAL.md](TECHNICAL.md).
- For the reasoning behind design decisions and the approaches that were rejected, see [DESIGN_NOTES.md](DESIGN_NOTES.md).

## Requirements

| Requirement | Use |
|---|---|
| Python 3 (a version that supports modern type hints) | Tests and checks. The plugin itself runs in EDMC's Python. |
| Node.js | The build scripts (`npm run build`, `deploy`, `package`). Node only copies and zips files; there is nothing to install with `npm install`. |
| [EDMC](https://github.com/EDCD/EDMarketConnector) | Running the plugin. |
| Git | Source control. |

## Getting the code

```bash
git clone https://github.com/rwharpernc/wayfarers-multitool.git
cd wayfarers-multitool
```

Layout:

- `plugin/`: the plugin source.
- `tests/`: tests.
- `scripts/`: build and maintenance scripts.
- `docs/`: documentation.
- [TECHNICAL.md](TECHNICAL.md) section 2 gives the full layout. [MODULES.md](MODULES.md) lists every module; a new module requires a row there (`tests/test_docs_modules.py` checks).

### Issue forms

- `.github/ISSUE_TEMPLATE/bug_report.yml` is the form opened by Settings → General → Help → **Report an issue**.
- `.github/ISSUE_TEMPLATE/game_data.yml` is the form opened by **Report game data** (Help) and by the Engineers tab's **Report engineer data**. `issue_report.build_feedback_url` prefills area, subject, context and environment. Any feature opens it with `issue_report.open_feedback(area, subject, context)`.
- The field ids in the templates match the `*_FIELD` constants in `plugin/issue_report.py`; the `id: environment` field must stay in step with that module.
- The forms are not part of the build. A change takes effect for all users once it is pushed to `master`.

## Build

```bash
npm run build      # copies plugin/ to dist/Wayfarers-Multitool (plus LICENSE and THIRD-PARTY-NOTICES.md)
npm run package    # builds, then zips the dist/Wayfarers-Multitool folder (every entry starts with Wayfarers-Multitool/) into dist/Wayfarers-Multitool.zip
```

- `dist/` is ignored by Git.
- The version number is defined in `plugin/__init__.py` and mirrored in `package.json`.

## Trying changes in EDMC

1. Run `npm run deploy`. The script builds, detects the operating system and merges the result into EDMC's plugins folder as `Wayfarers-Multitool`:
   - Windows: `%LOCALAPPDATA%\EDMarketConnector\plugins`
   - Linux: `~/.local/share/EDMarketConnector/plugins`, or the Flatpak location `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/plugins`, whichever exists
   - macOS: `~/Library/Application Support/EDMarketConnector/plugins`
2. For a non-standard location, set `WFMT_PLUGINS_DIR` or pass `--plugins-dir <path>` (`node scripts/build.mjs --install --plugins-dir <path>`). `npm run build` alone builds and prints the folder it would copy to.
3. Restart EDMC. EDMC loads plugin code at start-up, so every change requires a restart.

The deploy step merges files. A live plugin folder also holds per-commander data and plugin-managed files that are not part of the build (saved hotspots, sessions, logs, backups, downloaded updates). Overwrite the files the build produces and leave all other files in place.

Settings and window positions are stored in EDMC's configuration under keys that start with `wfmt_`.

### Generated file

`plugin/journal_blueprints.py` is generated and is never produced by the build.

1. Run `python scripts/gen_journal_blueprints.py` (requires network access). It rebuilds the file from public data lists (source and license: see [ATTRIBUTIONS.md](ATTRIBUTIONS.md) and [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md)).
2. Review the diff.
3. Run the tests. `tests/test_ship_plan.py` checks that every link points at a row of the blueprint table.

## Working on Windows and Linux

The repository is developed on both operating systems. Each machine builds and installs for itself, because the build detects the operating system and EDMC's plugins folder.

### Setting up a machine

1. Install Python 3, Node.js and Git. On Linux the Python Tk bindings are a separate package (Arch/CachyOS: `sudo pacman -S --needed tk nodejs npm`). Without Tk, the UI tests and the import smoke test fail with `libtk8.6.so` errors.
2. Clone the repository and run `git config core.autocrlf false` inside it.
   - `.gitattributes` keeps all files LF; `autocrlf` can conflict with it.
   - `.editorconfig` sets LF for editors. `tests/test_line_endings.py` fails when a text file in the working tree contains CRLF.
   - To repair a file: `sed -i 's/\r$//' FILE` (Git Bash or Linux), then `git add -u`.
3. Set the Git name and email for the repository (`git config user.name`, `git config user.email`) and enable the commit hooks with `git config core.hooksPath .githooks`.
   - The `pre-commit` hook runs `scripts/check_docs.py` and refuses the commit while the documentation disagrees with the code.
   - The `commit-msg` hook enforces:
     - a subject of 72 characters or fewer, starting with a capital letter, with no trailing period
     - a blank line after the subject
     - body lines of 80 characters or fewer (indented lines and URLs excepted)
     - no co-author or "generated with" lines, no exclamation marks, and none of the listed conversational phrases
   - The hook comments state a target of about 50 characters for the subject and about 72 for body lines.
   - On Linux the hook file must be executable; the repository records the mode.
   - `tests/test_commit_msg_hook.py` runs the hook on sample messages.
4. Verify the setup: `npm run test:docker`, `npm run build` (the first output line names the detected operating system) and `npm run package`.

### Rules that apply on both operating systems

- All data about a player's play is stored per commander (`plugin/commander_data.py`). Nothing is shared between commanders.
  - Each new data file is classified in `tests/test_data_files_per_commander.py`.
  - A commander name is never used in a file name (Windows file names are case-insensitive and reject some characters; Linux file names are case-sensitive).
  - The exception is `exo_observations.json`: facts about bodies, pooled to check the species prediction. It stores no commander name.
- Read and write files as UTF-8, write through a temporary file followed by `os.replace`, and keep operating-system-specific calls behind `platform_support.py`.
- Record in `LINUX_TESTING.md` what has been tried on one operating system only.

### Day-to-day workflow

- Run `git pull` before starting on a machine and commit and `git push` before switching machines.
- `npm run deploy` builds and copies into EDMC's plugins folder for that operating system. Restart EDMC afterward.
- EDMC on Linux may be a Flatpak. When behavior differs between operating systems, check the EDMC log first:
  - Linux Flatpak: `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/logs/EDMarketConnector-debug.log`
  - Windows: `%LOCALAPPDATA%\EDMarketConnector\logs\EDMarketConnector-debug.log`
  - EDMC's **Help → Open Log Folder** opens the folder.
- WFMT's own diagnostic log is enabled by Settings → WFMT → General → Help → **Write a separate diagnostic log** (off by default). The file is `logs/WFMT/wfmt-diagnostics.log` in EDMC's data folder; **Open log folder** in the same place opens it.
- Files not synchronized by Git: `docs/roadmap.md`, `dist/` and other ignored local files. `docs/TODO.md` is tracked and is the public list of open work.

### Portability rules

- Do not use Windows-only Tk values such as `SystemWindow` color names. Do not call `powershell.exe` or Win32 APIs outside the existing `IS_WINDOWS` branches. Use `platform_support` helpers (`IS_WINDOWS`, `IS_LINUX`).
- A feature with platform-dependent behavior states it in its Settings tab with a **Works on:** note (see `platform_support.input_support_note`). The per-operating-system list is in [TECHNICAL.md section 18](TECHNICAL.md#18-platform-support-windows-and-linux).
- File names: use the game's exact case (`Status.json`), match journals as `Journal.*.log`, pass `encoding=` to every `open`, and take the file name from a journal `Filename` field with `screenshot_naming.journal_basename`.
- Modal dialogs call `ui.style.grab_when_visible(dialog)`, not `dialog.grab_set()`.
- Text symbols in the UI are limited to symbols present in every font (`×`, `★`, `→`, `▾`).
- Settings tabs: never `pack` into an `nb.Frame`.
  - EDMC's `myNotebook.Frame` places a gridded spacer child in every instance. Packing into it raises an exception, EDMC logs `Failed for Plugin "WFMT"` and the WFMT Settings tab does not appear.
  - Use `grid`, or pack into a plain `tk.Frame`.
  - `tests/test_settings_layout.py` checks the source. `tests/test_prefs_smoke.py` builds the whole tab with EDMC-faithful stand-ins.
- Settings pages scroll. `ui` passes each feature's `build_settings` a `settings_scroll.ScrollContent` instead of a notebook.
  - A page taller than `settings_scroll.height_cap` receives a scrollbar. The cap is the screen height less 530 pixels, limited to 260 to 640 pixels.
  - Features keep calling `notebook.add(frame, text=...)`.
  - Plain `tk.Frame` rows on a Settings page are recolored to the page color by `ui._match_page_background`.
- Placement of a new feature's Settings: `ui._build_settings_tabs` defines the tabs: General, Online, Powerplay, Missions, Exploration, Mining, Trade, BGS, Colonization, Discord, Operations and Overlays. The tabs are sorted (`ui._sort_tabs`).
  - Add the feature to the correct group in that function.
  - Overlay drawing belongs in the Overlays group (a `build_overlay_settings`, or the whole tab for an overlay feature), with its place registered in `overlay_placement.SLOTS`.
  - A feature with a `build_settings` that is not listed receives a tab under "Other".
  - `_stacked_page` places two small pages on one tab. The stack accepts `add(frame, text=...)` like a notebook, so each `build_settings(notebook)` is unchanged.
- Since 1.5.0, a setting that belongs to a window is set in that window.
  - The window builds a card, tab or strip from a field list and saves each change at once. The config key is shared with the feature's Settings tab, which keeps only the Raven key and a line stating where the other settings moved (every switch for a lookup that contacts another service is on the Online tab, with a pointer where it used to be).
  - Keys, readers and savers are placed in a small `*_settings.py` module that imports nothing from the panel and provides `add_listener`, so the panel, the Settings tab and every open window redraw together. Examples: `mining_window_settings.py`, `bgs_settings.py`, `exploration_settings.py`.
  - A window never grants a permission. It displays the permission state and disables the controls that depend on it. Every permission to contact another service is switched only on the Online tab.
  - A page of a mode is a window opened from a button, not an arrow that pages the panel. A test for the window is placed in `tests/*_smoke.py` with a `test_*.py` wrapper that runs it headless.
- Name boxes use type-ahead: `system_autocomplete` for systems (the session's, the journals' through `system_history.py`, and Spansh when ticked), `commodity_autocomplete` for one commodity, `name_suggestions` for bodies, rings, ships, comma-separated commodities and any list of names (`attach_names`). A new box that takes a name WFMT can list gets one; `tests/test_field_suggestions_wired.py` lists the ones that have it.
- `monitor.logfile` (EDMC) is a `str` or a `pathlib.Path` depending on the EDMC version. Wrap it in `str()` before comparing or saving it to JSON.
- Background threads never touch a Tk widget. Results are passed back with a queue and `after()`.
- A Settings tab that does not appear indicates an exception while building it. EDMC logs `Failed for Plugin "WFMT"`.

## Tests

```bash
npm run test:docker
```

The command runs `python -m unittest discover -s tests` and `tests/import_smoke.py` in a container. Tests are run in the container so that no test window takes focus on the desktop.

- The tests cover pure-logic modules (parsing, state, estimates, data handling). They need neither EDMC nor a display, because EDMC's `config` module is replaced by a stub inside the tests.
- `tests/import_smoke.py` imports every module.

Two guard tests:

- `tests/test_prefs_smoke.py` builds every Settings tab and hard-codes the number of top-level tabs. Adding a tab requires updating it.
- `tests/test_own_data_files.py` fails when a module defines a data file (`*FILENAME = "x.json"`) that `plugin/update.py` does not list in `_OWN_DATA_FILES`.

### Smoke scripts

- Many features have a smoke script in `tests/` (`*_smoke.py`) that builds the real Tk window or panel with EDMC stubbed.
- `tests/test_*_smoke.py` runs each script in a subprocess and skips it when Tk has no display.
- On Windows, a window that opens takes keyboard focus. Each script that creates a root window imports `tests/quiet_tk.py` first, and a new script that creates a window starts with `import quiet_tk`.

### Container test run

`npm run test:docker` runs the tests in a Linux container (`docker/Dockerfile`) on a virtual display (Xvfb) with a window manager (openbox).

- Each run executes `docker build` (cached after the first run), mounts the repository read-only and runs `python -m unittest discover -s tests` followed by `tests/import_smoke.py`.
- Arguments after the script name replace that command. Example: `node scripts/docker-test.mjs python tests/mining_history_smoke.py`.

Setup:

- Windows: install Docker Desktop. If the engine is not running, the script starts it (waiting up to three minutes) and quits it afterward only when the script started it and no other containers are running.
- Linux (Arch/CachyOS): `sudo pacman -S --needed docker`, then `sudo systemctl enable --now docker.socket` and `sudo usermod -aG docker $USER`. A new login session is required for the group to apply; otherwise run the script as root or use rootless Docker. Python, Tk and fonts are provided by the image.

Coverage limits:

- The container is Linux regardless of the host. A pass does not cover Windows-only code (the Win32 overlay, the `quiet_tk` Windows branch, `platform_support.py`).
- The container's fonts differ from a desktop's, so the text-measuring `test_window_fit_*` checks can differ from a run on a real desktop.

### Date-dependent tests

Several modules read only events from the last few days before the current time. A test that replays a journal with a fixed date must also fix the clock (a `NOW` constant passed in, or a patched `time.time`). Otherwise the test fails once the date leaves the window.

To find such tests, run the suite with the clock advanced. In the container: `apt-get install -y faketime`, then `faketime -f '+60d' python -m unittest discover -s tests`. A failure indicates a defect only when the test compares an event's own date with the clock. Tests that write a file and compare its modification time with the clock fail in that run regardless, because `faketime` moves the clock and not the file times.

### Built-in overlay tests

| Layer | Test |
|---|---|
| Scene and picture | `tests/test_overlay_scene.py` (Pillow only) |
| Switch, fonts, text measuring, placement | `tests/test_overlay_native.py`, `tests/test_overlay_fonts.py`, `tests/test_overlay_style.py` |
| Hiding | `tests/test_overlay_hide.py` |
| Win32 window (`plugin/overlay_window.py`) | `scripts/native_overlay_test.py` draws four real cards over Elite (or the screen) for visual inspection; requires a desktop |

### Scripts

| Script | Purpose |
|---|---|
| `build.mjs`, `package.mjs`, `env.mjs` | Build and install the plugin. |
| `docker-test.mjs` | Runs the tests in the container (`npm run test:docker`). |
| `check_docs.py` | Checks the documentation against the code. |
| `gen_journal_blueprints.py`, `gen_organic_variants.py` | Regenerate data tables (source and license: see [ATTRIBUTIONS.md](ATTRIBUTIONS.md) and [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md)). |
| `verify_organic_variants.py` | Checks the color predictions against the local journals. |
| `analyze_exo_observations.py` | Checks the species prediction against the finds recorded in `exo_observations.json`. |
| `native_overlay_test.py` | Draws real overlay cards over Elite (Windows only). |

### Fonts

- `plugin/fonts/` ships Source Sans 3 (SIL Open Font License; the license file is in the same folder and in THIRD-PARTY-NOTICES.md) for the built-in overlay.
- Font files added by a player are placed in the same folder. The updater replaces only files that are in the release zip.
- A different bundled font requires its license to be added the same way.

### Coverage limits

Screens and windows are not covered by automated tests beyond the smoke scripts. Verify them by building, deploying and operating the feature in EDMC. [TECHNICAL.md](TECHNICAL.md) section 14 describes what is and is not tested.

## Making a change

1. Keep logic that does not need the screen in a module without EDMC or Tk imports so that it can be unit-tested ([TECHNICAL.md](TECHNICAL.md) section 6).
2. Follow the feature-module contract when adding a feature (section 4; checklist in section 16).
3. Content that can size the main window (images, long text) requires a fixed upper bound on every dimension (section 5).
4. Prefix config keys and overlay ids with `wfmt_<feature>_`. A new network call follows the API-usage rules in [TECHNICAL.md](TECHNICAL.md#keeping-api-traffic-low): opt-in or user-triggered, cached, capped, with a timeout, and identified through `http_identity.user_agent()`.
5. Journal first. A feature starts from the journal events the game writes, because not everything is logged.
   - Where the journal is insufficient, add data from Frontier (signed-in EDMC) or a community service, or use a labeled estimate or a user step.
   - Record the gap and its workaround in the matching guide's "What the game does and doesn't tell us" table.
   - See the design principle at the top of [TECHNICAL.md](TECHNICAL.md).
6. In the same change, update the README, the user guides in `docs/guide/`, the changelog and every affected document, including a row in [MODULES.md](MODULES.md) for each new module.
7. Write American English in code, names, comments and documentation (color, tons, Colonization). `tests/test_american_spelling.py` checks it.
   - The game's own names keep their spelling: journal events such as `ColonisationContribution`, mission and station names, commodity and module names.
   - A line that matches the game's text on purpose carries a `game spelling` comment, which the test accepts.
8. Colors in WFMT windows come from `plugin/uikit/palette.py` and are read when a widget is built (`P.BG`), not captured at import time or as a default argument. Use `None` as the default and `x or P.TOKEN` inside the function, or store a token name. `tests/test_window_themes.py` checks the contrast of every theme. Text that must not follow the text-size setting uses `style.font(spec, scaled=False)`.
9. Renaming a saved file, settings key or saved field requires a migration: add it to `plugin/legacy_names.py` (with a test). The migration runs at start-up.
10. A new online lookup (anything that makes WFMT contact another service) is added to `LOOKUPS` in `plugin/online_lookups.py`, with its default and the group it belongs under.
    - It is switched only on the Online tab (`plugin/settings_online.py`). A feature never writes the setting and never shows its own checkbox for it; where its old checkbox would have been it shows only a one-line pointer to Settings → WFMT → Online.
    - A feature that cannot work without the lookup shows `online_lookups.needs(<key>)` where it is used. The line is empty while the lookup is on, so the warning appears only when something is wrong. An extra that only improves a feature shows nothing.
    - `tests/test_settings_online.py` enforces the table and that the Online tab is the single writer.

### Third-party material

- Write code independently. Before using code, assets or data from another project, check its license. WFMT is GPL-3.0; added material must be compatible.
- When a license requires a notice, add it to [../THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md). Credit for ideas goes in [ATTRIBUTIONS.md](ATTRIBUTIONS.md).
- Code from a project without a license is not copied, because no permission exists.

## Keeping the documentation current

`scripts/check_docs.py` checks the documentation mechanically:

| Check | Verifies |
|---|---|
| links | Every relative link and `#anchor` in the Markdown resolves. |
| labels | A bold name used as a reference to the screen (after "click", "tick", "press", before "button" or "tab", or in a controls table) is a string in `plugin/`. |
| paths | Every "Settings -> WFMT -> tab" path starts with a real Settings tab, read from the code. |
| files | Every module (`.py`), data file (`.json`) and `wfmt_*` setting key named in the documentation exists. |
| comments | A backticked name in a code comment or docstring is defined in the code. |
| headers | Every page opens with a `# Title` on its first line and a lead paragraph, and bold label lines are not stacked. |
| version | The version is identical in `plugin/__init__.py`, `package.json` and the newest changelog heading, and the example versions in `INSTALL.md`, `LINUX_TESTING.md`, `TECHNICAL.md` and the getting-started and reporting-problems guides are the current one. |

Run `python scripts/check_docs.py` (`--only labels` runs one check). The script reads text only and opens no windows. `.githooks/pre-commit` runs it before every commit and `tests/test_docs_current.py` runs it in the test suite.

Page structure (the checker enforces the title, the lead paragraph and unstacked label lines; the rest is convention):

1. One `# Title` on the first line (a specification is titled "<Feature> technical specification").
2. A lead paragraph directly after it: what the page is and who it is for.
3. Optional notes as bullets after the lead (`- **Author:** ...`, `- **Status:** ...`). Bold label lines are not stacked, because Markdown merges them into one paragraph.
4. A "**On this page:**" list when the page is long.
5. The `##` sections.

On a report, correct the document or comment. Add a name to `docs/doc_terms.txt` only when it belongs to something else (the game, Discord, GitHub, EDMC, another project) or is a placeholder, with a comment line giving the reason.

The checker cannot determine whether a sentence is still true. When behavior changes:

1. Search the documentation for the old name and the feature name (`grep -rn` over `README.md` and `docs/`).
2. Update the guide, [features.md](guide/features.md), [planned.md](guide/planned.md) (move a built item out), the matching technical specification, [TODO.md](TODO.md), the changelog and [MODULES.md](MODULES.md).
3. Run `python scripts/check_docs.py` and `npm run test:docker`.

## Releasing

A release is cut from a clean `master`. **The docs are brought up to date before anything is tagged or published, and nothing is released until the owner says they are ready.**

1. Set the version in `plugin/__init__.py` and `package.json`.
2. In `CHANGELOG.md`, add a dated section for the version and move the "Unreleased" entries under it.
3. Run the tests (`npm run test:docker`) and perform the in-game passes (`docs/TEST_PLAN.md`, `docs/LINUX_TESTING.md`).
4. Update the documentation to the state it will have once the release is published: `docs/STATUS.md` (the current release, existing branches, what is unreleased), `docs/TEST_PLAN.md` and `docs/LINUX_TESTING.md` (test counts and passes done), `docs/TODO.md`, `README.md` (the latest release), `docs/guide/known-issues.md` (known problems in the new release) and the version examples in `docs/guide/getting-started.md`.
5. Run `npm run package` to build `dist/Wayfarers-Multitool.zip`. Commit, tag `v<version>`, and push the commit and the tag.
6. Publish the release with the zip as its asset:

   ```bash
   gh release create v<version> dist/Wayfarers-Multitool.zip --title "WFMT <version>" --notes-file <the changelog section for the version>
   ```

   - The title is `WFMT <version>` without `v`. The tag keeps the `v` (`v1.0.0`, for example). The in-app updater reads the tag, not the title.
   - Publish as a normal release, not a draft or pre-release. The in-app updater and the README's "latest release" link follow official GitHub releases only, and can read them only while the repository is public.

Users download the zip, not the repository. A fix to a released version is made on a short `bugfix/<version>` branch cut from `master`, merged back with the release, and then deleted.
