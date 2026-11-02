# Shortcuts

Shortcuts start an action while Elite has the focus, without the mouse. Two methods exist: a **keyboard shortcut** (Windows) and a **chat command** (Windows and Linux). Both are configured under **Settings → WFMT → General → Shortcuts** and start the same six actions.

| Action | Keys (Windows) | Chat command | Function |
|---|---|---|---|
| Mark the center | Ctrl+Alt+Shift+**C** | `!wf center` | Marks the center of the current mining location, as **Mark center** does in the Surface Mining Live window ([marking a location](mining.md#marking-a-mining-location)). |
| Mark the border | Ctrl+Alt+Shift+**B** | `!wf border` | Marks the border of the nearest marked location, as **Mark border** does. |
| Radar range | Ctrl+Alt+Shift+**Z** | `!wf zoom` | Steps the Live radar's reach through 50 m, 250 m, 500 m, 1 km and 2 km, then back to 50 m. |
| Open the Live window | Ctrl+Alt+Shift+**L** | `!wf live` | Opens the Surface Mining Live window (the window opened by the **Surface Mining** button, with **Book** and **Dashboard** in its header), or raises it when open. |
| Hide or show overlays | Ctrl+Alt+Shift+**O** | `!wf overlays` | Hides every WFMT overlay, or shows them again ([hiding the overlays](../OVERLAY_SETUP.md#hiding-the-overlays-for-a-while)). |
| Rig placed | Ctrl+Alt+Shift+**R** | `!wf rig` | Records the Rhino's position as a placed mining rig, so that the radar can show the spacing bands ([rig bands](mining.md#the-live-window)). |

The last key of each combination can be set to any letter, digit or function key F1 to F12, or to **Off**.

## Configuration

1. Open **Settings → WFMT → General → Shortcuts**.
2. For each action, select the last key of the combination from the list beside **Ctrl+Alt+Shift+**: a letter, a digit, a function key F1 to F12, or **Off** to disable the shortcut. The defaults are in the table above.
3. Read the line under the action. It is empty when the key is acceptable. Otherwise it reads `Also used by: <another WFMT action>.` or `Elite already uses Ctrl+Alt+Shift+X for <control>. Pick another key.`
4. To use chat commands, select **Chat commands (type  !wf <word>  in Elite's chat)**. The option is off by default.
5. To play a sound as confirmation, select **Play a sound when a shortcut worked**. The option is on by default.
6. Select **OK** in the Settings window. The keys are registered at this point. If another program holds a combination, WFMT reports which one.

**Result messages.** The result is written to the status line of the Surface Mining Live window while the window is open, and to EDMC's log:

- **Hide or show overlays** reports `Overlays hidden.` or `Overlays shown.` Hidden overlays are cleared from the screen and are not drawn until shown again. The state is not saved: overlays are shown whenever EDMC starts.
- **Radar range** reports `Radar reaches <distance>.` and saves the new reach.
- **Open the Live window** reports `Opened the Surface Mining Live window.`
- The marking actions report the marked position, or the reason the mark could not be made (for example, no position yet).

## Keyboard shortcuts (Windows)

Every combination is **Ctrl+Alt+Shift** plus one key. Elite's own controls rarely use this combination. The shortcuts are registered with Windows for the whole desktop and work while Elite has the focus.

- **Conflict check against Elite.** The page reads the active Elite controls file and reports when one of Elite's controls uses exactly the selected combination. It also reports when two WFMT actions share a key. When the controls file cannot be found, the page states this and the combinations are not checked.
- **Combination held by another program.** WFMT reports this after **OK** is selected. A combination can be held by one program at a time. Select another key.
- **Sound.** When **Play a sound when a shortcut worked** is selected, a sound plays on success. Nothing plays on failure, for example when there is no position to mark.

**Linux.** A Linux desktop provides no portable way for a program to receive keys while another window has the focus, and Wayland provides none. Key combinations are therefore available on Windows only. On Linux the page shows the same table with the key choices grayed out.

## Chat commands (Windows and Linux)

Type `!wf center` (or `!wf border`, `!wf rig`, `!wf zoom`, `!wf live`, `!wf overlays`) in Elite's chat and press Enter.

The game writes the sent message to its journal as a `SendText` event, and WFMT reads the command from there. The method uses only the journal and works identically on both systems.

- Chat commands are off until **Chat commands** is selected on the Shortcuts page.
- Every participant in the channel receives the message. Use a channel without other members, such as a private channel with no members.
- WFMT acts only on a message that consists of exactly `!wf` and one of the words above. WFMT sends no messages itself.
- A command older than 30 seconds in the journal is ignored, so commands from before EDMC started are not run.
- Capitalization is ignored (`!WF Center` works). A message with additional text, such as a second word, is an ordinary chat line and is ignored.
- Chat commands are typed text and cannot be bound to a key in Elite. To use a key, use the key combinations above (Windows only).

## Actions that are not shortcuts

Saving a deposit (**Add hotspot**) and **Save map** open a window or a file dialog. They remain buttons in the Surface Mining Live window.
