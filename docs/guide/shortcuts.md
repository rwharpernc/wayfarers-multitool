# Shortcuts

Start an action without the mouse, while you are in the game: a **keyboard shortcut** (Windows) or a **chat command** (Windows and Linux). Both are set up under **Settings → WFMT → General → Shortcuts**, and both start the same six actions.

| Action | Keys (Windows) | Chat command | What it does |
|---|---|---|---|
| Mark the center (CTR) | Ctrl+Alt+Shift+**C** | `!wf center` | Marks the center of the mining location you are at, as **CTR** does in the Surface Live window ([marking a location](mining.md#marking-a-mining-location)). |
| Mark the border (BRD) | Ctrl+Alt+Shift+**B** | `!wf border` | Marks the border of the nearest marked location, as **BRD** does. |
| Radar range | Ctrl+Alt+Shift+**Z** | `!wf zoom` | Steps the Live radar's reach through 50 m, 250 m, 500 m, 1 km and 2 km and back. |
| Open the Live window | Ctrl+Alt+Shift+**L** | `!wf live` | Opens the Surface Mining Live window, or raises it if it is open. |
| Hide or show overlays | Ctrl+Alt+Shift+**O** | `!wf overlays` | Hides every WFMT overlay, or shows them again ([hiding the overlays](../OVERLAY_SETUP.md#hiding-the-overlays-for-a-while)). |
| Rig placed | Ctrl+Alt+Shift+**R** | `!wf rig` | Notes the Rhino's position as a mining rig you have just placed, so the radar can show the spacing bands ([rig bands](mining.md#the-live-window)). |

The last key of each combination can be changed to any letter, digit or function key F1 to F12, or to **Off**.

## How to set them up

1. Open **Settings → WFMT → General → Shortcuts**.
2. For each action, pick the last key of its combination from the list beside **Ctrl+Alt+Shift+**: a letter, a digit, a function key F1 to F12, or **Off** to switch that shortcut off. The defaults are in the table above.
3. Read the line under the action. It stays empty when the key is fine; otherwise it says `Also used by: <another WFMT action>.` or `Elite already uses Ctrl+Alt+Shift+X for <control>. Pick another key.`
4. Tick **Chat commands (type  !wf <word>  in Elite's chat)** if you want the chat commands (they are off at first, see below).
5. Leave **Play a sound when a shortcut worked** ticked (it is by default) if you want a sound as confirmation.
6. Press **OK** on the Settings window. The keys are registered when you press it; if another program already holds one, WFMT tells you which.

**What each action says it did.** The result is written to the Surface Live window's status line while it is open, and to EDMC's log:

- **Hide or show overlays** reports `Overlays hidden.` or `Overlays shown.` A hidden overlay clears what is on screen and stops drawing until shown again; nothing is saved, so overlays are shown whenever EDMC starts.
- **Radar range** reports `Radar reaches <distance>.` and saves the new reach.
- **Open the Live window** reports `Opened the Surface Mining Live window.`
- The marking actions report where they marked, or why they could not (for example that there is no position yet).

## Keyboard shortcuts (Windows)

Every combination is **Ctrl+Alt+Shift** plus one key. That is a combination Elite's own controls almost never use, and it is the same on every shortcut so it is easy to remember.

The shortcuts work while Elite has the focus, because they are registered with Windows for the whole desktop.

- **Checked against Elite.** The page reads your active Elite controls file and tells you if one of Elite's controls uses exactly the combination you picked. It also warns if two WFMT actions share a key. If the controls file cannot be found, it says so and the combinations are not checked.
- **Held by another program.** If another program already holds a combination, WFMT says so after you press **OK**; pick another key. (A combination is held by one program at a time.)
- **A sound** plays when a shortcut worked, if **Play a sound when a shortcut worked** is ticked (it is, by default), so you know it did something without looking away from the game. Nothing plays when it did not work, for example when there is no position to mark.
- Where the result shows: in the Surface Live window's status line while it is open, and in the Surface Mining page's text for the marks.

**On Linux:** a Linux desktop gives a program no portable way to hear keys while another window has the focus, and Wayland gives none, so the key combinations are for Windows only. The page shows the same table on Linux with the key choices grayed out.

## Chat commands (Windows and Linux)

Type `!wf center` (or `!wf border`, `!wf rig`, `!wf zoom`, `!wf live`, `!wf overlays`) in Elite's chat and press Enter.

The game writes what you send to its journal, WFMT reads it there, and the action runs. It works the same on both systems because it uses nothing but the journal.

- **Off until you switch it on** (**Chat commands** on the Shortcuts page).
- **Everyone in the channel you type into reads the command.**
  - Type it in a channel with nobody else in it, such as a private one with no members.
  - WFMT acts only on a message that is exactly `!wf` and one of the words above; it never sends anything itself.
- A command older than 30 seconds in the journal is ignored, so commands from before EDMC started are never run.
- Capitals do not matter (`!WF Center` works). Anything else in the message, such as a second word, makes it an ordinary chat line that WFMT ignores. The command is read from the game's `SendText` journal event, which the game writes for what you send.
- The chat commands are typed text, so they cannot be bound to a key in Elite. To use a key, use the key combinations above (Windows only).

## What is not a shortcut

Saving a deposit (**+H.S.**) and **Save map** open a window you fill in or a file dialog, which does not suit a key pressed in the game, so they stay buttons in the Surface Live window.
