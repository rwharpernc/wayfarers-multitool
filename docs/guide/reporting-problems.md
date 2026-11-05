# Reporting a problem

WFMT provides buttons that prepare a bug report. They are under **File → Settings → WFMT → General → Help**.

| Control | Function |
|---|---|
| **Report an issue** | Opens a bug report on GitHub in the browser, with the title started and the versions and operating system filled in |
| **Copy diagnostics** | Copies the same version lines and the newest WFMT lines from EDMC's log to the clipboard, for pasting into the report |
| **Report game data** | Opens the Game data form on GitHub, for reporting what the game shows ([procedure](#telling-us-what-the-game-shows-game-data)) |
| **Write a separate diagnostic log (off by default)** | A detailed WFMT log in a separate file ([procedure](#the-diagnostic-log)). **Open log folder** and **Copy log path** are below the option |

None of these controls sends data. A report exists on GitHub only after **Submit new issue** is selected there, which requires a GitHub account. A report can also be written by hand on the [Issues page](https://github.com/rwharpernc/wayfarers-multitool/issues).

## How to report a problem, step by step

1. **Check the settings.** Most "nothing happens" reports concern a feature that is switched off: see [Troubleshooting](troubleshooting.md#nothing-happens-settings-that-start-off). Check whether the gap is a known limit of what the game records (each mode guide ends with "What the game does and doesn't tell us"). A window's **Help** button, where present, explains its columns and colors. [Known issues](known-issues.md) lists known faults.
2. **Reproduce the problem with EDMC open**, so that the log contains the lines. An earlier problem can fall outside the part of the log that WFMT copies (see [what gets copied](#what-copy-diagnostics-copies)).
3. Open **File → Settings → WFMT → General → Help**.
4. Select **Copy diagnostics**. The line under the button reads *Copied. Paste it into the report's log box.* If it reads *Could not copy to the clipboard*, see [If something does not work](#if-something-does-not-work).
5. Select **Report an issue**. The browser opens GitHub's bug report form. GitHub requests a sign-in when none is active.
6. Complete the form:
   - **Title:** starts with the version, for example `[1.5.3] `. Append a short description of the problem.
   - **What happened?** The observed result and the expected result.
   - **Steps to reproduce:** the actions in order, and the panel, window or Settings page.
   - **Environment:** filled in with the WFMT, EDMC and Python versions and the operating system. Leave it unchanged.
   - **Log lines (optional):** paste the diagnostics (**Ctrl+V**).
7. Review the whole form, including the pasted log, and delete any content that should not be posted. Content submitted on the Issues page is visible to everyone who can see the repository (see [what is left out](#what-is-left-out-and-what-to-check)).
8. Select **Submit new issue**.

## Telling us what the game shows (Game data)

Some facts cannot be checked against the journal, and some WFMT tables (an engineer's requirements and locations, for example) come from community lists. The Game data form on GitHub reports what the game shows. It is separate from a bug report and applies to any part of WFMT. Engineers are the first use.

- **From the Engineers tab:** select an engineer and select **Report engineer data**. The form opens in the browser with the area (Engineers), the engineer's name, the standing WFMT has for the engineer and the Environment box filled in. Engineers whose invitation requirement WFMT cannot check show **Verification needed** in their details.
- **From Settings:** **File → Settings → WFMT → General → Help → Report game data** opens the same form with only the Environment box filled in.
- **Content:** under **What the game shows**, copy the text of the in-game panel (for an engineer, the invitation and unlock requirements from the Engineers panel). Under **What WFMT showed that is wrong or missing**, describe any mismatch. Correct the standing if the game shows a different one.
- WFMT sends nothing. The browser opens the form, which is submitted with the user's own GitHub account or closed. No commander name, system or file path is placed in the form, and none should be added.

## The diagnostic log

WFMT can write a separate, more detailed log, apart from EDMC's. It is off by default. No file is created until the option is enabled.

1. Open **File → Settings → WFMT → General → Help**.
2. Select **Write a separate diagnostic log (off by default)** and select **OK**. Clear the option and select **OK** to stop. The choice persists across restarts.
3. Reproduce the problem, then send the file named under the option (**Open log folder** shows it, **Copy log path** copies its path) together with EDMC's log.

**Location.** `logs/WFMT/wfmt-diagnostics.log` in EDMC's data folder, next to EDMC's own `logs` folder. The file rotates at 1 MB with three older files kept (about 4 MB at most). An update does not change it.

**Recorded:**
- everything WFMT normally logs, at every level, including the finer lines EDMC's log leaves out (EDMC's log is not changed: it reads the same with this on),
- the version, Python and operating system when it is switched on,
- the name of each journal event as it arrives, with the system and station,
- each button pressed in a WFMT window and each window opened or closed,
- each Spansh request: the endpoint (without its query), how it ended, how long it took, which try it was and the size of the answer,
- each Where to Buy search and Rescan Journals with its result and time, a Settings save, a mode button pressed, and Frontier carrier data arriving,
- the Route overlay: each read of the game's `NavRoute.json` (how many systems, the first and last, the current system, whether the ship is on the route, or that it could not be read) and each route card drawn or cleared,
- an interdiction that came with no warning beforehand: the NPC lines (message key and wording) from the 75 seconds before it.

**Not recorded.** The contents of journal events, request bodies, keys and webhook links. In every line the commander name is replaced by `<commander>`, the home folder by `~` and any Discord webhook link by `<webhook>`, as in Copy diagnostics. The file is plain text.

Example line: `2026-10-31 14:02:11.482 | DEBUG   | 1234 | spansh    POST spansh.co.uk/api/stations/search outcome=ok ms=412 attempt=1 bytes=18232`. The fields are the time, the level, the thread, the part of WFMT, the event and the details.

## What "Report an issue" fills in

The form opens with the title started and the **Environment** box filled in:

```
- WFMT: 1.5.3
- EDMC: 5.13.1
- Python: 3.11.9
- OS: Windows 11 (10.0.26200)
```

On Linux the OS line names the distribution, the session type and whether EDMC is a Flatpak, for example `Ubuntu 24.04.1 LTS, wayland, Flatpak`. See the Linux entries in [Troubleshooting](troubleshooting.md#linux).

The form is a template (`.github/ISSUE_TEMPLATE/bug_report.yml`) and the bug label is set automatically. The Game data form uses its own template, `game_data.yml`. When the browser opens the plain new-issue page, the template was not found. Enter the same information in the box.

## What "Copy diagnostics" copies

The clipboard text consists of:

- the four version lines above, plus one line with the number of overlay windows running and the number of requests the session has sent to Spansh (how many were retried and how many were not sent during a pause), then
- **WFMT log lines:** the newest lines written by WFMT from EDMC's log file (`EDMarketConnector-debug.log`), up to 80 lines and about 12,000 characters. A traceback (lines starting `Traceback (most recent call last)`) is included with the line that caused it. Lines written by other plugins and by EDMC are omitted.

When the examined part of the log has no WFMT lines, the text contains `(no WFMT lines found in the log)`. This is not an error: WFMT logged nothing recently. Describe the problem in the form.

WFMT reads only the last part of the log (about the last 400 KB), so a long session can push an earlier problem out of range. To obtain older lines, open the log folder from **EDMC → Help → Open Log Folder** and copy the lines manually.

## What is left out, and what to check

Before the log lines are copied, WFMT:

- replaces the **commander name** with `<commander>`, in any capitalization. WFMT knows the commander currently set in EDMC and the commander in the newest journal;
- replaces the **home folder** (for example `C:\Users\name` or `/home/name`) with `~`;
- replaces any **Discord webhook link** with `<webhook>` (WFMT does not log webhook links; this is a safeguard).

The version lines contain no commander name, system name or file path. The address that **Report an issue** opens carries only the title, the versions and the OS line.

WFMT cannot detect the following. Check them before submitting:

- **Other commander names.** When more than one commander is played, another name can appear in a log line. Replace it manually.
- **System, station and carrier names.** They appear in the log whenever WFMT logged something about them. They are game data and not personal data, and can reveal where the commander was.

The diagnostics can be pasted into a text editor and reviewed there before copying.

## If something does not work

| Symptom | Action |
|---|---|
| **Report an issue** opens nothing | No default browser is set. Open the [new-issue page](https://github.com/rwharpernc/wayfarers-multitool/issues/new?template=bug_report.yml) and use **Copy diagnostics** to fill the form |
| The form opens with an empty Environment box | The address was truncated. Select **Copy diagnostics** and paste the first lines into the box |
| *Could not copy to the clipboard* | Another program holds the clipboard, or (Linux) no clipboard service exists. Retry. If the message persists, open the log from **EDMC → Help → Open Log Folder** and copy the lines manually |
| The text contains `(no WFMT lines found in the log)` | WFMT logged nothing recently. Reproduce the problem, then select **Copy diagnostics** immediately |
| Linux Flatpak: the log is not found | A Flatpak EDMC keeps its log under `~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector/logs/`. Attach lines from the file manually |

The version lines and the OS line are copied even when the log cannot be found.

## Content of a useful report

- the actions taken, in order, and where (the mode, panel or window);
- the expected result and the actual result;
- whether the problem occurs every time or intermittently;
- for an incorrect number, the expected number and the reason.
  - For Colonization, Trade and Powerplay figures, the line of the relevant journal event is the most useful addition (for example the `CarrierStats` line for a fleet carrier).
  - The journal is in the folder that EDMC's settings show as the Journal directory, in a file named `Journal.<date>.log`.

Requests and suggestions are submitted on the same Issues page.

## Privacy

**Report an issue** and **Report game data** ask the browser to open a GitHub address. **Copy diagnostics** writes to the clipboard only. WFMT makes no connection to GitHub itself, and nothing is filed unless the form is submitted. These controls are listed in [What goes on the internet](internet-and-privacy.md).
