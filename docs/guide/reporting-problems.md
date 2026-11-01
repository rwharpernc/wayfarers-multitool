# Reporting a problem

Found a bug, or a number that looks wrong? WFMT has buttons that make a good report quick to write. They are all in
**File → Settings → WFMT → General → Help**.

| Control | What it does |
|---|---|
| **Report an issue** | Opens a bug report on GitHub in your browser, with the title started and your versions and operating system already filled in |
| **Copy diagnostics** | Copies the same version lines plus the newest WFMT lines from EDMC's log to your clipboard, so you can paste them into the report |
| **Report game data** | Opens the Game data form on GitHub, for telling us what the game shows ([how](#telling-us-what-the-game-shows-game-data)) |
| **Write a separate diagnostic log (off by default)** | A tick, off until ticked. A detailed log of WFMT's own, in a separate file, for a problem that is hard to pin down ([how](#the-diagnostic-log)); **Open log folder** and **Copy log path** sit under it |

None of these sends anything by itself. The report only exists on GitHub if you press **Submit new issue** there, and that needs your
own free GitHub account. You can always write the report by hand on the
[Issues page](https://github.com/rwharpernc/wayfarers-multitool/issues) instead.

## How to report a problem, step by step

1. **Check whether it is a setting first.** Most "nothing happens" reports are a feature that is switched off. See
   [Troubleshooting](troubleshooting.md#nothing-happens-settings-that-start-off), and check whether the gap is a known limit of what the
   game records (each mode guide ends with "What the game does and doesn't tell us"). A window's own **Help** button, if it has one, explains its columns and colors, and [Known issues](known-issues.md) lists what is already known.
2. **Make the problem happen again if you can**, with EDMC still open, so the log has the lines from it. A problem from an hour ago may
   have scrolled out of the part of the log WFMT copies (see [what gets copied](#what-copy-diagnostics-copies)).
3. Open **File → Settings → WFMT → General → Help**.
4. Press **Copy diagnostics**. The line under the button reads *Copied. Paste it into the report's log box.* If it reads *Could not copy
   to the clipboard*, see [If something does not work](#if-something-does-not-work).
5. Press **Report an issue**. Your browser opens GitHub's bug report form. If you are not signed in to GitHub, it asks you to sign in
   first.
6. Fill in the form:
   - **Title:** it starts with your version, like `[1.4.1] `. Finish it with a few words on what went wrong.
   - **What happened?** What you saw, and what you expected to see instead.
   - **Steps to reproduce:** what you did, in order, and which panel, window or Settings page it was in.
   - **Environment:** already filled in with your WFMT, EDMC and Python versions and your operating system. Leave it as it is.
   - **Log lines (optional):** click in the box and paste (**Ctrl+V**). This is where the diagnostics go.
7. **Read the whole form before you submit it**, the pasted log included, and delete anything you would rather not post. Anything you submit
   on the Issues page is visible to everyone who can see the repository (see [what is left out](#what-is-left-out-and-what-to-check)).
8. Press **Submit new issue**.

## Telling us what the game shows (Game data)

WFMT cannot check some things against the game's journal, and some of its tables (an engineer's requirements and locations, for example) come from community lists. If you can see what the game really shows, a short form on GitHub lets you tell us. It is separate from a bug report and works for any part of WFMT; **engineers are the first use**.

- **From the Engineers tab:** select an engineer and press **Report engineer data**. The form opens in your browser with the area (Engineers), the engineer's name, the standing WFMT has for them and the Environment box already filled in. Engineers whose invitation requirement WFMT cannot check show **Verification needed** in their details; those are the ones most useful to report.
- **From Settings:** **File → Settings → WFMT → General → Help → Report game data** opens the same form with nothing filled in but the Environment box, for anything else you want to tell us.
- **What to write:** under **What the game shows**, copy what the in-game panel says in its own words (for an engineer, the invitation and unlock requirements from the Engineers panel), and under **What WFMT showed that is wrong or missing** anything that did not match. Correct the standing if the game says otherwise.
- **Nothing is sent by WFMT.** The browser opens the form; you read it, change it and submit it with your own GitHub account, or close the tab. No commander name, system or file path is put in it, and please do not add any.

## The diagnostic log

For a problem that is hard to pin down, WFMT can write a **separate, more detailed log** of its own, apart from EDMC's. It is **off by default**; nothing is written and no file is made until you switch it on.

1. Open **File → Settings → WFMT → General → Help**.
2. Tick **Write a separate diagnostic log (off by default)** and press **OK**. Untick it and press **OK** to stop; the choice is kept across restarts.
3. Make the problem happen, then send the file named under the tick (**Open log folder** shows it, **Copy log path** copies its path) together with EDMC's own log.

**Where it is.** `logs/WFMT/wfmt-diagnostics.log` in EDMC's data folder, next to EDMC's own `logs` folder. It is rotated at 1 MB with three older files kept (about 4 MB at most), and an update never touches it.

**What it records:**
- everything WFMT normally logs, at every level, including the finer lines EDMC's log leaves out (EDMC's log is not changed: it reads the same with this on),
- the version, Python and operating system when it is switched on,
- the name of each journal event as it arrives, with the system and station,
- each button pressed in a WFMT window and each window opened or closed,
- each Spansh request: the endpoint (without its query), how it ended, how long it took, which try it was and the size of the answer,
- each Where to Buy search and Rescan Journals with its result and time, a Settings save, a mode button pressed, and Frontier carrier data arriving,
- the Route overlay: each read of the game's `NavRoute.json` (how many systems, the first and last, the system you are in, whether you are on the route, or that it could not be read) and each route card drawn or cleared,
- an interdiction that came with no warning beforehand: the NPC lines (message key and wording) from the 75 seconds before it.

**What it leaves out.** The contents of journal events, request bodies, keys and webhook links are not written. In every line your commander name is replaced by `<commander>`, your home folder by `~` and any Discord webhook link by `<webhook>`, the same as Copy diagnostics, so the file can be attached to a report. Read it first if you want to be sure; it is plain text.

A line looks like `2026-10-31 14:02:11.482 | DEBUG   | 1234 | spansh    POST spansh.co.uk/api/stations/search outcome=ok ms=412 attempt=1 bytes=18232`: the time, the level, the thread, the part of WFMT, what happened and the details.

## What "Report an issue" fills in

The form opens with the title started and the **Environment** box filled in, like this:

```
- WFMT: 1.4.1
- EDMC: 5.13.1
- Python: 3.11.9
- OS: Windows 11 (10.0.26200)
```

On Linux the OS line names your distribution, the session type and whether EDMC is a Flatpak, for example
`Ubuntu 24.04.1 LTS, wayland, Flatpak`. That is what the Linux problems in [Troubleshooting](troubleshooting.md#linux) usually turn on.

The form is a template (`.github/ISSUE_TEMPLATE/bug_report.yml`), and the bug label is set for you. (Game data uses its own template, `game_data.yml`.) If your browser opened the plain
new-issue page instead, the template was not found; write the same information in the box by hand.

## What "Copy diagnostics" copies

The text on your clipboard is:

- the same four version lines as above, plus one line with the number of overlay windows running and how many requests the session has sent to Spansh (how many were retried and how many were not sent during a pause), then
- **WFMT log lines:** the newest lines from EDMC's log file (`EDMarketConnector-debug.log`) that were written by WFMT, up to 80 lines and
  about 12,000 characters. A traceback (the lines that start `Traceback (most recent call last)`) comes with the line that caused it.
  Lines written by other plugins and by EDMC itself are left out.

If the log has no WFMT lines in the part WFMT looked at, the text says `(no WFMT lines found in the log)`. That is not an error; it means
WFMT logged nothing recently. Describe what happened in the form instead.

WFMT reads only the last part of the log (roughly the last 400 KB), so a long play session can push an earlier problem out of reach. If
what you need is older, open the log folder from **EDMC → Help → Open Log Folder** and copy the lines by hand.

## What is left out, and what to check

Before the log lines are copied, WFMT:

- replaces your **commander name** with `<commander>`, in any capitals. It knows the commander EDMC currently has and the one in your
  newest journal;
- replaces your **home folder** (for example `C:\Users\you` or `/home/you`) with `~`;
- replaces any **Discord webhook link** with `<webhook>` (WFMT never logs one; this is only a safeguard).

The version lines never hold a commander name, a system name or a file path. The address that **Report an issue** opens carries only the
title, the versions and the OS line, nothing from your play.

Two things WFMT cannot know, so please look for them yourself before you press **Submit**:

- **Other commander names.** If you play more than one commander, another name could appear in a log line. Replace it by hand.
- **System, station and carrier names.** They are in the log whenever WFMT logged something about them. They are game data, not
  personal, but you may prefer not to show where you were.

You can paste the diagnostics into a text editor first and read them there, then copy again from the editor.

## If something does not work

| What you see | What to do |
|---|---|
| **Report an issue** opens nothing | Your system has no default browser set. Open the [new-issue page](https://github.com/rwharpernc/wayfarers-multitool/issues/new?template=bug_report.yml) yourself and use **Copy diagnostics** to fill the form |
| The form opens but the Environment box is empty | The address was cut off. Press **Copy diagnostics** and paste the first lines into the box |
| *Could not copy to the clipboard* | Another program holds the clipboard, or (Linux) there is no clipboard service. Try again; if it persists, open the log from **EDMC → Help → Open Log Folder** and copy lines by hand |
| The text says `(no WFMT lines found in the log)` | Nothing from WFMT was logged lately. Make the problem happen again, then press **Copy diagnostics** straight away |
| Linux Flatpak: the log is not found | A Flatpak EDMC keeps its log under `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/logs/`. Attach lines from the file by hand |

The version lines and the OS line are copied even when the log cannot be found.

## Good reports

A report that gets fixed quickly says:

- **what you did**, step by step, and where (the mode, panel or window);
- **what you expected** and **what happened instead**, in your words;
- **whether it happens every time** or only sometimes;
- for a **number that looks wrong**, the number you expected and why.
  - For Colonization, Trade and Powerplay figures, the line of the relevant event in your journal helps most (for example the `CarrierStats` line for a fleet carrier).
  - The journal is in the folder EDMC's settings show as the Journal directory, and the file is `Journal.<date>.log`.

For ideas and requests rather than bugs, the Issues page is the same place.

## Privacy

**Report an issue** and **Report game data** only ask your browser to open a GitHub address, and **Copy diagnostics** only writes to your clipboard. WFMT makes
no connection to GitHub itself, and nothing is filed unless you submit it. It is listed with everything else in
[What goes on the internet](internet-and-privacy.md).
