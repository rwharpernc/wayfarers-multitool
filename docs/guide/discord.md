# Sharing reports to Discord (and anywhere else)

This page describes how WFMT copies or posts its reports: the buttons, the Discord webhook setup, the destination settings, the post templates, what is sent, and the messages shown on failure.

WFMT shares a report in three ways:

| Button | Action | Needs a webhook | Sends data |
|---|---|---|---|
| **Copy** (**Copy Summary** in the BGS report, **Copy Progress** in Powerplay) | Places the report on the clipboard as plain text without Discord formatting marks. For forums, notes, email and other chat programs | No | No |
| **Copy for Discord** | Places the report on the clipboard with Discord formatting (bold names, links, bullet lists). The text is pasted into Discord manually | No | No |
| **Post to Discord** | Sends the report to a Discord channel through a webhook. One press creates one post | Yes | The report text, to the saved webhook, when the button is pressed |

Nothing is posted without a button press. The appearance of the Discord posts is configurable: see [Customize post appearance](#customize-post-appearance).

**On this page:** [Shareable content](#shareable-content) · [Quick start](#quick-start) · [Set up Discord](#set-up-discord-make-a-webhook) · [Set up WFMT](#set-up-wfmt) · [Webhooks, commanders and channels](#webhooks-commanders-and-channels) · [Common questions](#common-questions) · [Customize post appearance](#customize-post-appearance) · [Examples](#examples) · [Sharing somewhere that is not Discord](#sharing-somewhere-that-is-not-discord) · [What is sent, and who can see it](#what-is-sent-and-who-can-see-it) · [Changing or removing a destination](#changing-or-removing-a-destination) · [When something goes wrong](#when-something-goes-wrong)

## Shareable content

| Report | Location | Buttons |
|---|---|---|
| **BGS report**: the tick shown in the window, one block per system with the factions, their states and influence, and the commander's activity | BGS mode, **Report** window | **Copy Summary**; the **Discord** menu in the window header: **Copy for Discord**, **Post to Discord**, **Customize post…** |
| **Powerplay progress**: the session's merits and estimated Control Points per system, and the cycle total | Powerplay mode, **Report** (Powerplay Sessions window) | **Copy Progress**; **Copy for Discord**, **Post to Discord** and **Customize…** in a row above the tabs |

## Quick start

1. Create a webhook for the target channel in Discord and copy its link ([Set up Discord](#set-up-discord-make-a-webhook)).
2. Open **File → Settings → WFMT → Discord**, tick **Allow Post to Discord**, enter a destination name, paste the link and press **Test** ([Set up WFMT](#set-up-wfmt)).
3. Press **OK** to save.
4. Open a report (**Report** in BGS mode or Powerplay mode) and press **Post to Discord**. When more than one destination is saved, a menu asks which one to use.

**Copy for Discord** and the plain copy buttons need no setup.

## Set up Discord: make a webhook

A webhook is a link that allows a program to post to one Discord channel. It is created in Discord; WFMT requires only the link. Creating a webhook requires the **Manage Webhooks** permission for the channel or server. Without it, a server administrator must create the webhook and supply the link privately. Discord menu names may differ from those below; the relevant entries are **Integrations** and **Webhooks**.

1. Open the Discord server and locate the target channel, for example `#bgs-reports`.
   - To test first, create a private channel: right-click the server name, choose **Create Channel**, name it, and switch on **Private Channel**. Move the webhook to the final channel later.
2. Hover over the channel in the channel list and click the **gear icon** (Edit Channel).
3. In the left menu choose **Integrations**, then **Webhooks**.
4. Press **Create Webhook** (or **New Webhook** if the channel already has one).
5. Open the new webhook and set:
   - **Name**: the name shown on the posts (for example `WFMT`).
   - **Channel**: the target channel.
6. Press **Copy Webhook URL**. The link has the form `https://discord.com/api/webhooks/123456789012345678/AbCdEf...`.
7. Press **Save Changes** if Discord offers it.

The link must be kept private. Anyone holding it can post to the channel. Do not paste it into chat, screenshots or bug reports.

**Posting into a thread:**

1. Enable Developer Mode: **User Settings** → **Advanced** → **Developer Mode**.
2. Right-click the thread in the channel list and choose **Copy Thread ID**.
3. Paste the number into the destination's **Thread ID** box ([Set up WFMT](#set-up-wfmt)). A forum channel requires a thread.

## Set up WFMT

1. Open **File → Settings → WFMT → Discord**.
2. Tick **Allow Post to Discord**. The setting is off by default. Each post still requires a button press.
3. Under **Destinations**, fill in the first destination:
   - **Name**: the label of the destination, for example `Squadron BGS`. It appears in the menu and in messages; the link is never displayed. Maximum 40 characters.
   - **Webhook link**: the link from Discord. The box hides the typed text.
   - **Thread ID (optional)**: the number of a thread to post into.
4. Press **Test**. WFMT asks Discord whether the link works and posts nothing. A working link produces `Works: WFMT.` (the webhook's own name).
5. To post to more than one channel or server, press **Add destination** and fill in another. The maximum is 10 destinations. **Remove** deletes a destination.
6. Press **OK** to save.

Destinations are saved for the commander being played, on this computer only. The commander is identified from the game's journal, so a login is required first. Destinations entered before WFMT has seen a login are saved for the next commander who logs in. Destinations are excluded from **Back up my data**.

## Webhooks, commanders and channels

A webhook belongs to one channel on one server, not to a commander. Its link can post to that channel (or a thread inside it) only.

- **One destination per target.** To post to two channels, or to channels on two servers, create a webhook in each and add a destination for each.
- **Choosing the target.** With one destination, **Post to Discord** posts to it. With several, a menu lists their names (`Post to Squadron BGS`, `Post to Friends`, Cancel) and the report is posted only to the chosen one.
- **Commander.** The destination list belongs to the commander the journal last named (the commander logged in). After a login as another commander, **Post to Discord** uses that commander's destinations and that commander's data. A commander with no saved destination is told to set one up, and nothing is sent.
- **Two commanders, one channel.** Both commanders may save the same link. On the second commander's Discord tab, **Copy their destinations** (shown when another commander has destinations saved) copies the first commander's list. Press **OK** to save.
- **Editing instead of duplicating.** Posting the same report again to the same destination edits the earlier post. A different destination receives its own post. WFMT keeps these post records for each commander until EDMC restarts.
- **The switch is shared.** **Allow Post to Discord** applies to every commander.

## Common questions

**Is membership of the channel required to post to it?** No. WFMT sends the post directly to Discord over the internet using the webhook link. The Discord account, the Discord app and the currently viewed channel or server are not involved. The link identifies one channel on one server, and any holder of the link can post there without being a member. To post elsewhere, add a destination with a webhook created in that channel ([Webhooks, commanders and channels](#webhooks-commanders-and-channels)).

**What prevents a post from arriving?** Deletion of the webhook or its channel, or replacement of the webhook link. WFMT then reports `Discord did not accept that webhook link` or `Discord could not find that webhook` ([When something goes wrong](#when-something-goes-wrong)). If a link has leaked, delete the webhook in Discord.

**Which name do posts show?** Posts appear under the webhook's own name and picture. WFMT sends no name of its own and the post carries no commander name.

- To change the name or picture: open the channel settings, choose **Integrations**, then **Webhooks**, open the webhook, change **Name** and the picture, and press **Save Changes**. A new webhook is not required. New posts use the new name; older posts keep the name they were posted under.
- Everyone posting through one webhook appears under the same name. For separate names, create a second webhook in the channel and save it as the second commander's destination.
- Discord rejects some webhook names. It reports the rejection on save.

## Customize post appearance

Each report is posted in one layout by default. A dialog selects another layout, switches parts of a post on and off, and saves custom layouts as templates. It changes **Copy for Discord** and **Post to Discord** together; both use the same template. **Copy Summary** and **Copy Progress** are not affected.

**Opening the dialog:** the BGS Report **Discord** menu (**Customize post…**), the **Customize…** button in the Powerplay Sessions window, or **Customize posts…** on the **Settings → WFMT → Discord** tab. A **Report** box at the top switches between the BGS report and Powerplay progress.

**Templates.** Selecting a template in the **Template** box makes it the template used for that report's posts immediately.

- **Standard** is the default layout. **Compact**, **Detailed** and **Plain** are the other built-in presets. Presets cannot be changed or deleted.
- Changing a checkbox changes only the preview. **Save as…** stores the version under a new name (up to 40 characters, not a preset name). **Save** replaces a custom template. **Rename…** and **Delete** act on custom templates; **Delete** asks for confirmation. A maximum of 30 custom templates is kept per report.
- Posts use the template shown in the box. A note under the buttons states when changes are unsaved.
- Templates are kept for the whole installation (not per commander), are included in **Back up my data**, and persist across updates.

**The preview** shows the post built from the current tick or session (or example data when none exists), approximately as Discord displays it, with the character and message counts. Discord allows 2,000 characters per message; a longer report is split into several messages.

**Options for the BGS report**

| Checkbox | Effect |
|---|---|
| Heading with the tick time | Title and the tick's time span at the top |
| Star on pinned systems | A star before the name of a pinned system |
| Controlling faction in bold | Emphasizes the faction that controls the system |
| State changes | Shows a change such as `None → Boom` |
| Influence and its change | Shows `45.2% (+1.3)` |
| Pending, recovering and active states | The lines listing those states |
| What you did (the You: lines) | Missions, trade, exploration data and similar, per faction |
| Government and allegiance | Adds `Democracy / Federation` to each faction |
| One line for each system | Compact layout: the controlling faction and the commander's activity on one line |
| No formatting marks | Bullets without bold or italics |
| Systems: **Every system in the tick** or **Only systems where you acted** | The second omits systems that were only passed through |

**Options for Powerplay progress**

| Checkbox | Effect |
|---|---|
| Heading | Title and the note that CP is an estimate |
| Your Power in the heading | Adds the Power's name to the title |
| Link each system to Inara | Makes each system name a link, without a preview card |
| Estimated Control Points | The `(~48.0 CP)` part of each line |
| The system's Powerplay state | Adds `Exploited`, `Fortified` and similar, for the current system |
| Merits by activity | Adds `Acquisition 80, Reinforcement 40` to each line |
| The cycle's total line | The cycle's merits, estimated CP and systems worked |
| No formatting marks | Bullets without bold or italics |

**Built-in presets**

| Preset | BGS report | Powerplay progress |
|---|---|---|
| **Standard** | Default layout | Default layout |
| **Compact** | One line per system, without the pending, recovering and active lists | No Inara links, no state, no cycle line |
| **Detailed** | Standard plus government and allegiance | Standard plus merits per activity |
| **Plain** | No bold or italics | No bold or italics (links appear as the address in angle brackets) |

**Settings that cannot be changed.** Every name is escaped, so a faction or system named `@everyone` or `*Raiders*` appears as written. Every post is sent with mentions switched off. Long posts are split under Discord's limit.

**Example: one line per system.**

1. Open the BGS Report, then the **Discord** menu, then **Customize post…**.
2. Select the **Compact** template. The preview shows lines such as `Example System — Example Union (None → Boom, 45.2% (+1.3)) — You: Example Union 2 mission(s) done, INF +4/-0; 1,500,000 cr exploration data`.
3. Press **Done**. **Post to Discord** uses this layout.

**Example: only the systems worked, without the heading.**

1. In the dialog, choose **Only systems where you acted** under **Systems** and untick **Heading with the tick time**.
2. Press **Save as…** and enter a name. The saved template becomes the template for BGS posts.

**Example: Powerplay progress with activity breakdown and no cycle line.**

1. Open the Powerplay Sessions window and press **Customize…**.
2. Select **Detailed**, then untick **The cycle's total line**. The preview lines read like `Example System — 120 merits (~48.0 CP) — Acquisition 80, Reinforcement 40 — Exploited`.
3. Press **Save as…** and enter a name. The saved template is selected for the next **Post to Discord**.

## Examples

### Post the BGS report after the tick

1. Open BGS mode and press **Report**. The window opens on the current tick. The tick drop-down at the top selects an earlier tick.
2. Open the **Discord** menu in the window header and choose **Post to Discord**.
3. With one destination, the line at the foot of the window shows `Posting to Discord...`, then `Posted to Squadron BGS.` (the destination's name). With several destinations, a menu asks for the target first.

Example post (names are fictitious):

```
WFMT BGS report
Current tick — since 2026-10-29 09:00 UTC
Nervi
- Nervi Brotherhood (bold: it controls the system) — Boom, 45.2% (+1.3)
  - Pending: Famine
  - You: 2 mission(s) done, INF +4/-0; 1,500,000 cr exploration data
- Allied Forces — War, 30.0%
```

Discord displays the headings and the controlling faction in bold and the lists as bullets. The report contains only the tick shown, with one block per system.

Posting again within the same tick edits the earlier post. The foot of the window shows `Updated your earlier post in Squadron BGS.` A new tick creates a new post. Post records are kept until EDMC restarts; after a restart, posting the same tick adds a new message.

### Share Powerplay progress

1. In Powerplay mode press **Report** to open the Powerplay Sessions window.
2. Press **Post to Discord** (above the tabs, at the right).

The post contains the session's merits per system, estimated Control Points marked `~`, then the cycle total line:

```
WFMT Powerplay progress — Aisling Duval
This session. CP is an estimate (~).
- Nervi — 120 merits (~48.0 CP) — Exploited
- Sol — 1,234 merits (~493.6 CP)
Cycle
CYCLE 12 TOTAL — 3,400 merits · est. 1,360.0 CP · 5 systems worked   (Acquisition 2,000 · Reinforcement 1,400)
```

Each system name links to its Inara page without a preview card. Posting again in the same session edits the post; a new login starts a new session and a new post.

### Copy for Discord without a webhook

1. Open the report and choose **Copy for Discord** (the **Discord** menu in the BGS report; the button in the Powerplay window).
2. The foot of the window shows `Copied for Discord.` Paste into the Discord message box and send.
3. A long report is several messages. The window shows `Copied for Discord (3 messages: paste each one on its own).` and the copy has a blank line between messages. Paste and send one message at a time.

### Post to two channels

1. Create a webhook in each channel ([Set up Discord](#set-up-discord-make-a-webhook)) and copy each link.
2. In **Settings → WFMT → Discord** add two destinations, for example `Squadron BGS` and `Friends`, each with its link. Press **Test** on each, then **OK**.
3. Open the BGS Report and choose **Post to Discord**. A menu offers `Post to Squadron BGS` and `Post to Friends`. Select one.
4. Post the same tick to the other destination in the same way. Each destination keeps its own post; posting again to `Friends` edits only the `Friends` message.

### Use the same channel from two commanders

1. Log in as the first commander and save the destination (name, link, **OK**).
2. Log in as the second commander and open **Settings → WFMT → Discord**. Select the first commander in the list beside **Copy their destinations** and press the button.
3. Press **OK**. Each commander posts that commander's own report to the same channel.

### Post into a thread

Enter the thread number in the destination's **Thread ID** ([Set up Discord](#set-up-discord-make-a-webhook)) and post as usual. WFMT adds the thread to the request. Discord reopens an archived thread for the post.

## Sharing somewhere that is not Discord

**Copy Summary** (BGS report) and **Copy Progress** (Powerplay Sessions window) copy plain text without Discord marks.

- **Copy Summary** produces lines such as `Nervi:` followed by `  * Nervi Brotherhood — Boom, 45.2% (+1.3)`.
- **Copy Progress** produces one line per system. The default is `[Nervi](https://inara.cz/...) - 120 merits (~48.0 CP) - Exploited`. The layout is editable on the **Settings** tab of the Powerplay Sessions window.

## What is sent, and who can see it

- **Post to Discord** sends the report text to the saved webhook address on `discord.com`. **Copy for Discord**, **Test** (which reads and posts nothing) and the plain copy buttons send no report.
- **The Customize dialog sends nothing.** It reads local data to draw the preview and saves templates on this computer.
- **Post content:** the report text only. It contains no commander name, but it shows the systems, factions and numbers selected for sharing, which anyone who can read the channel can read.
- **Mentions.** Every post is sent with mentions switched off, and an invisible space is inserted after any `@` in a name. Names containing `*` or `_` are shown as written instead of being formatted.
- **Link secrecy.** Each commander's destinations are stored in `discord_webhooks.json` in the plugin folder. The file is excluded from Back up my data, is never written to the EDMC log, and is stripped from **Copy diagnostics** if it appears there.
- The request names WFMT and its version (`WFMT/<version> (discord; +...)`), like every other WFMT request. See [What goes on the internet](internet-and-privacy.md).

## Changing or removing a destination

- **Change:** enter the new link (or change the name or thread) on the **Discord** tab and press **OK**. **Test** checks the link first.
- **Stop posting temporarily:** untick **Allow Post to Discord**. Destinations remain saved.
- **Remove from WFMT:** press **Remove** beside the destination and close Settings. Removing all destinations removes the commander's saved destinations.
- **Remove from Discord:** open the channel's **Integrations → Webhooks**, open the webhook and press **Delete Webhook**. Do this if the link has leaked.

## When something goes wrong

Messages appear on the line at the foot of the window.

| Message | Cause | Action |
|---|---|---|
| `Turn on Post to Discord and save a webhook link on the Settings, Discord tab first.` | The switch is off, no link is saved for this commander, or WFMT has not seen a login | Complete [Set up WFMT](#set-up-wfmt) for the commander being played. After starting EDMC with the game closed, log in first |
| `There is no destination called ...` | The menu named a destination that has since been removed or renamed | Check the names in **Settings → WFMT → Discord**, then post again |
| `That is not a Discord webhook link. It looks like https://discord.com/api/webhooks/...` | The box holds something other than a webhook link | Copy the link again with **Copy Webhook URL** |
| `Discord did not accept that webhook link. It may have been changed or removed.` | The webhook was deleted or its link changed | Create a new webhook and paste the new link |
| `Discord could not find that webhook or message. It may have been deleted.` | The webhook, or a message WFMT intended to edit, no longer exists | Check that the webhook exists. If only the earlier message was deleted, post again; WFMT sends a new message |
| `Discord is asking for a pause. Wait a little and try again.` | Discord rate-limits the webhook and a retry did not clear it | Wait and press the button again |
| `Discord refused the message (400). It may be too long.` | Discord did not accept the text | Try again. If it recurs, use **Copy for Discord** and [report it](reporting-problems.md) |
| `Could not reach Discord. Check your connection and try again.` | No connection, or Discord is unavailable | Check the connection and try again |
| `A post is already on its way.` | The button was pressed while the previous post was being sent | Wait for the first post to finish |
| `Posting failed unexpectedly; see the EDMC log.` | Unexpected error. The log line contains the kind of error, never the link | [Report it](reporting-problems.md) with **Copy diagnostics** |
| Nothing appears in the channel | The destination may point at a different channel or thread | Open the webhook in Discord and check its channel; check the destination's **Thread ID** |

If **Post to Discord** produces no visible result, the line at the foot of the window states what happened. Sharing is available only in the BGS Report and Powerplay Sessions windows.
