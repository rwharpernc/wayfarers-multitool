# Where things stand

Read this first when picking the project up on a machine that has not seen the recent work (for example the Linux test machine).

- It is kept in Git because Git is the only thing shared between the two test machines, one Windows and one Linux.
- Last updated 2026-10-26.

## Release

- **1.0.0** is the version number in `plugin/__init__.py` and `package.json`.
  - The project was renamed Wayfarer's Multitool (WFMT) and its version history restarted at 1.0.0 on 2026-10-21.
  - Everything built so far is the first release, published as 1.0.0.
  - The checks to run first are in [TEST_PLAN.md](TEST_PLAN.md), and the open in-game checks are in [TODO.md](TODO.md).
- 1.0.0 has not been published yet, and the repository is private until it is.
  - The in-app updater and the README's "latest release" link read GitHub's public releases API, so they start working once the release exists.

## Branches

There is one long-lived branch, `master`.

- For a fix to a released version, cut a short branch from `master` (for example `bugfix/1.0.1`), and merge it back.

## Testing

### Windows

- Tested by the maintainer, using a build of the branch being worked on (`npm run deploy`, run by hand).
- Bugs found are fixed on `master` or a short bug fix branch.
- To check on Windows with the 2026-10-23 build (steps in [TEST_PLAN.md](TEST_PLAN.md) section 5):
  - every overlay is off after the first start, for every commander, with one log line
  - a stopped expedition carries on from where it stopped, and Rescan leaves out paused and stopped time
  - Overlay Placement names where the screen size came from, and reads the real hardware size when the game's files are not found
  - long names in the Missions, Source commodities, Ship Builds and My Codex tables
  - saved data from before the spelling change still loads (`Renamed saved names:` once)
- Native checks already made on Windows on 2026-10-23: the display probe read 3840 x 2160 at 125% scaling; the journals confirmed the Mk II jet cone boost of 6x at a neutron star and 3x at a white dwarf (V-0351).

### Linux, next pass

- The current build is to be tested on CachyOS (Arch-based) with KDE Plasma and a Flatpak EDMC.
- The steps and the ordered checks are at the top of `docs/LINUX_TESTING.md` ("Testing: start here").
- Report the session type (Wayland or X11) with the results.

### Linux, earlier passes

- A pass on 2026-10-18 (KDE Plasma, Wayland, a Flatpak EDMC) went well.
- A quick pass on 2026-10-20 found the unit and smoke tests passing, the plugin loading without errors and the Settings pages right.
- Both passes were of earlier builds of this code, before the 1.0.0 restart and rename. No manual pass has been done on Linux since; the window-fit fixes of 2026-10-21 were checked only in a Docker run (a Linux container).
- Keyboard shortcuts (all six actions) are available on Windows only, so their key choices are grayed out on Linux.
  - To hide the overlays on Linux, click the Overlays line on the panel, press **Hide / show now**, or type `!wf overlays` (turn on **Chat commands** under Settings → WFMT → General → Shortcuts).
  - Whether a Linux key binding is worth adding is an open question in `docs/TODO.md`, under Shortcuts.
- The steps and the ordered list of what to check are at the top of `docs/LINUX_TESTING.md` ("Testing: start here").
- When reporting, give:
  - the distro and desktop
  - X11 or Wayland
  - native or Flatpak EDMC
  - the relevant lines of EDMC's log (`~/.local/share/EDMarketConnector/EDMarketConnector.log`)

### Assumptions not yet confirmed in the game

- `SendText` carries the typed text in a `Message` field.
- The 2 km scanner reach behind the green ground-driven area and the drive rings. Frontier has published no figure. EDRhinoSpotter calls its 2 km "the community figure" and SrvSurvey has none (checked 2026-10-23). It cannot be measured in the game, so it stays a labeled community estimate and is no longer an open item.
- Elite's controls file is found on Linux inside the Proton or Wine folder.

### Where the in-game checks are

- The in-game checks for Materials, Engineering, the Ship planner and Expedition are in [`docs/TODO.md`](TODO.md), the public list of open work.
- The Linux versions are in `docs/LINUX_TESTING.md`.

## To pick up on the Linux machine

Written 2026-10-21 on the Windows machine. This is work done since the last Linux pass that has not been run on Linux at all.

- **Spelling fix and saved-data migration (new, not run on Linux).** British spellings in names were replaced with American ones, including the Colonization modules, tests, saved files and settings.
  - What to check after `git pull --rebase`:
    - Start EDMC once and look at the WFMT lines in the log for `Renamed saved names:`.
    - The Colonization page still shows the current project and its history, the Sites window still lists your sites, and the fleet carrier column still has its figures.
    - The Colonization overlay card is still where you put it, and is still on or off as you left it.
    - A mode you had hidden is still hidden, and the panel opens on the mode you last used.
    - Trade stock and the Exploration surveys still show what they showed before.
  - If the Colonization history looks empty, say so: it can be rebuilt from the journals.
  - The installed plugin folder may still hold modules under their old names (`colonisation_*.py`). They are not loaded and can be deleted.
  - The Docker run passes on Windows (Docker Desktop, 3,342 tests). The migration ran correctly on a copy of the Windows data, and is untested on Linux data.
- **Order to work in on Linux:**
  1. `git pull --rebase`.
  2. Run `fc-match sans`, then `python -m unittest discover -s tests -p "test_window_fit_*_smoke.py"`, and report both.
  3. `npm run test:docker` once Docker is set up.
  4. Build and deploy by hand (`npm run deploy`), then follow `docs/LINUX_TESTING.md` and the checklists in `docs/TODO.md`.
- **Docker test runner.** `npm run test:docker` (see "Running the tests without windows on your screen" in `docs/DEVELOPMENT.md`).
  - Set up Docker first: `sudo pacman -S --needed docker`, enable the service, join the `docker` group, log in again.
  - Confirm the script and image build and run there. So far it has only run on Windows with Docker Desktop.
- **Window-fit checks.** The five `test_window_fit_*` tests failed on Windows (Docker Desktop) and on Linux (desktop font Noto Sans, and Docker with DejaVu Sans), so the layouts had real problems at the smallest sizes.
  - They were fixed on Linux on 2026-10-21 (narrower entries, wrapping labels, larger minimum sizes for some windows) and pass in the Docker run (`npm run test:docker`).
  - On 2026-10-24 the native run on the Linux desktop (KDE Wayland, Noto Sans) failed all five. Expedition, the Plan dialogs, Notes and the Price finder were then fixed (taller minimums, fewer table rows, narrower boxes), with `cad6ea5` checked in Docker with DejaVu Sans and with Noto Sans (3,370 tests, 12 skipped). The windows looked right on the Linux desktop afterward by eye; the native suite has not been re-run on that commit.
  - Docker with Noto Sans reproduced only about 10 of the desktop's 101 findings, so a Docker pass does not promise a desktop pass.
  - Not yet checked natively on Windows. The Expedition and Plan dialog minimum heights went up, so check they still fit a small screen.
  - Still to check by eye:
    - Colonization Sites, Surface Mining Book, Notes and Powerplay Sessions, whose minimum sizes went up
    - that no minimum is too large for a small screen
  - Stretch columns in tables now clip their text to the width they get, so the checker's cut-text notes are gone. That is also new on both OSes, so look at a long name in a wide and a narrow window.
- **Screen size from the operating system (new, not run on Linux).** With no game files or overlay log to read, the screen size now comes from the primary monitor (`xrandr --current`, through the host from a Flatpak) instead of an assumed 1920 x 1080.
  - Check it: remove or rename the overlay's log so nothing else is found, open Settings → Overlays → Overlay Placement, and read the source line. It should say *using the primary display* with your real resolution.
  - Report the session type (Wayland or X11) and whether `xrandr` is installed. On Windows this reads 3840 x 2160 on the test machine (native check, 2026-10-23).
- **Every overlay off (new, not run on Linux).** One reset switches every overlay off for every commander, once (`wfmt_overlay_reset_v2`).
  - Start EDMC and look for `All WFMT overlays reset to disabled` in the log. No card should show for any commander, and one you turn on stays on after a restart.
- **Expedition clock and Rescan (new, not run on Linux).** A stopped expedition started again carries its clock on from where it stopped; Rescan leaves out paused and stopped time. Steps are in `docs/LINUX_TESTING.md`.
- **Ship planner In storage column (new, not run on Linux).** Steps are in `docs/LINUX_TESTING.md`.
- **Table text caps (new, both OSes).** The caps went to 60 on the non-stretch name columns of Missions, Source commodities, Ship Builds and My Codex. Look at a long name at a narrow and a wide size.
- **Colonization, added 2026-10-26 (not run on Linux).** Steps are in `docs/LINUX_TESTING.md` and section 6 of [TEST_PLAN.md](TEST_PLAN.md).
  - Raven Colonial: **Create Project on Raven**, the **My Projects** window (the PROJECTS button) and finding a site's project by market id as well as name. Create Project, Mark Plan Entry Demolished and the My Projects writes have not yet run against the live service.
  - The Sites window's **Remaining** column now shows what is still to get (the need less the ship's hold and the fleet carrier), and the overlay card matches it, with no To buy column and an option, on by default, to hide the commodities already covered.
  - The ship's hold is read from the game's `Cargo.json`, so the In Cargo figures follow a purchase.
  - **Best single systems** after Find all, and the accent color for a search in progress.
- **Tests.** The Docker run on Windows (Docker Desktop, a Linux container) passed all 3,370 tests on 2026-10-23. Run the suite natively on Linux too, from a desktop session, and report the count and any failure.
  - Tests that replay dated journals now use a fixed clock; `docs/DEVELOPMENT.md` explains how to look for the ones that do not.
- **Star index Update.** Update now fetches Spansh's small 1-day or 1-week file instead of the whole 173 MB dump.
  - Follow the "Local star index" steps in `docs/LINUX_TESTING.md`.
  - Report the time an update takes.
- **Expedition window.** The Expedition window, Route Planner and Expedition Log are now the Plan, Route and Log tabs of one window.
  - Follow "One Expedition window" in `docs/LINUX_TESTING.md`.
  - Say whether the window takes the focus when it opens.
- **Mining.** Three additions since the last pass, each with its steps in `docs/TODO.md` ("Verification in the game") and `docs/LINUX_TESTING.md`:
  - Mining History's *credits after limpets*.
  - The *Hold full in* line.
  - The station's price against the galactic average when docked.
  - All three read only the journal and `Market.json`, so what to check on Linux is that the journal folder is found and the lines appear.
- **Expedition section.** The panel's Expedition and Expedition Log rows are now one section.
  - Check it fits the panel and that nothing widens EDMC's window.
- **Start expedition cue.** On the Route tab, a started expedition turns the status line green and the button reads *Started ✓* for four seconds.
  - A press that starts nothing shows neither.
- **Reopening a stopped expedition** (decided 2026-10-23). Its clock picks up from the time it stopped at, and the time stopped is not counted. It applies to the Route tab's Start and the Log's Resume, and is covered by a unit test. Rescan leaves out what happened while a run was paused or between a stop and the restart, as the live count does.

## Working rules for now

- **Deploys.** Nothing deploys by itself.
  - Committing builds nothing. Builds are made by hand when one is wanted, such as when a release is cut.
  - `npm run deploy` then copies the checked-out branch's build over the EDMC plugins folder, replacing the build being tested.
  - A deploy merges: files from an older build that no longer exist stay in the folder, unused.
- **Git.**
  - Commits, pushes, version bumps, tags and releases are made by the maintainer.
  - `git pull --rebase` before starting work, and push when done.
  - Do not commit machine-specific paths or logs.
- **Conventions.**
  - American English everywhere.
  - Everything saved about play is per commander (`plugin/commander_data.py`).
  - Files use LF line endings.
- **Releasing** is described in `docs/DEVELOPMENT.md` ("Releasing").

## Decisions already made

- The tests keep using Mactavious as a second test commander (a fixture name for checking that commanders' data stays apart). It is a test name only; CMDR Mactavious is also the project's credited author (see the README and [ATTRIBUTIONS.md](ATTRIBUTIONS.md)).
- Every online lookup is either opt-in in Settings or runs only when a button is pressed, and is listed in `docs/guide/internet-and-privacy.md`.
- Out of scope: Guardian ruin surveying, landing-pad diagrams and an FSS spectrum guide.
  - The journal lacks what they would need.
  - The spectrum ranges are not in it, and no open table of them exists.
