# Sharing reports to Discord (and anywhere else)

WFMT can share its reports three ways, so you can use whichever fits the place you are sharing to:

| Button | What it does | Needs a webhook | Sends anything |
|---|---|---|---|
| **Copy** (**Copy Summary** on the BGS report, **Copy Progress** on Powerplay) | Puts the report on the clipboard as plain text, with no marks that another program would show as clutter. For forums, notes, email and any other chat program | No | No |
| **Copy for Discord** | Puts the report on the clipboard with Discord's formatting (bold names, links, bullet lists). You paste it into Discord yourself | No | No |
| **Post to Discord** | Sends the report to a Discord channel through a webhook you set up. One press, one post | Yes | Only the report text, to your own webhook, when you press it |

Nothing is ever posted on its own. Every post follows a button press.

**On this page:** [What you can share](#what-you-can-share) · [Quick start](#quick-start) · [Set up Discord](#set-up-discord-make-a-webhook) · [Set up WFMT](#set-up-wfmt) · [Webhooks, commanders and channels](#webhooks-commanders-and-channels) · [Common questions](#common-questions) · [Customize how your posts look](#customize-how-your-posts-look) · [Examples](#examples) · [Sharing somewhere that is not Discord](#sharing-somewhere-that-is-not-discord) · [What is sent, and who can see it](#what-is-sent-and-who-can-see-it) · [Changing or removing a destination](#changing-or-removing-a-destination) · [When something goes wrong](#when-something-goes-wrong)

## What you can share

| Report | Where | The buttons |
|---|---|---|
| **BGS report**: the tick shown in the window, a block for each system with the factions, their states and influence, and what you did | BGS mode, **REPORT** window | **Copy Summary**, and the **Discord** menu in the window's header: **Copy for Discord** and **Post to Discord** |
| **Powerplay progress**: this session's merits and estimated Control Points for each system, and the cycle's total | Powerplay mode, **REPORT** (the Powerplay Sessions window) | **Copy Progress**, and **Copy for Discord** and **Post to Discord** in a row above the tabs |

Coming later, as separate builds: expedition sales and announcements, colonization and team building (shopping lists, progress, a call for helpers), and carrier movement. They are planned in
[the Discord sharing research](../DISCORD_SHARING_RESEARCH.md) and are not in WFMT yet.

## Quick start

1. In Discord, make a webhook for the channel you want ([Set up Discord](#set-up-discord-make-a-webhook)) and copy its link.
2. In EDMC open **File → Settings → WFMT → Discord**, tick **Allow Post to Discord**, give the destination a name, paste the link, and press **Test** ([Set up WFMT](#set-up-wfmt)).
3. Close Settings with **OK** to save.
4. Open a report (**REPORT** in BGS mode or in Powerplay mode) and press **Post to Discord**. With more than one destination saved, a small menu asks which one.

**Copy for Discord** and the plain copy buttons need no setup at all.

## Set up Discord: make a webhook

A webhook is a link that lets a program post to one Discord channel. You make it in Discord, and WFMT only needs the link. You need the
**Manage Webhooks** permission for the channel or server. If you do not see **Integrations** in the steps below, ask a server admin to make
the webhook and send you the link in a private message. Discord changes its menus from time to time, so if a name differs a little, look for
**Integrations** and **Webhooks**.

**Example: a squadron server with a channel for BGS reports.**

1. Open your Discord server and find the channel the reports should go to, for example `#bgs-reports`.
   - To try it first, make a private channel only you can see: right-click the server name, choose **Create Channel**, name it `wfmt-test` and
     switch on **Private Channel**. Move the webhook to the real channel later.
2. Hover the channel in the channel list and click the **gear icon** (Edit Channel).
3. In the menu on the left choose **Integrations**, then **Webhooks**.
4. Press **Create Webhook** (or **New Webhook** if the channel already has one). Discord adds a webhook with a default name.
5. Click the new webhook to open it and set:
   - **Name:** for example `WFMT`. This is the name the posts show.
   - **Channel:** check it is the channel you want.
6. Press **Copy Webhook URL**. The link looks like `https://discord.com/api/webhooks/123456789012345678/AbCdEf...` (a long number, then a long
   string of letters, digits and dashes).
7. Press **Save Changes** if Discord offers it.

Keep the link to yourself. **Whoever has it can post to that channel**, so do not paste it into a chat, a screenshot or a bug report.

**To post into a thread instead of the channel:**

1. Turn on Developer Mode: **User Settings** (the gear by your name) → **Advanced** → **Developer Mode**.
2. Right-click the thread in the channel list and choose **Copy Thread ID** (a long number).
3. You will paste that number into the destination's **Thread ID** box in the next section. (A forum channel needs a thread.)

## Set up WFMT

1. In EDMC open **File → Settings → WFMT → Discord**.
2. Tick **Allow Post to Discord**. It is off until you tick it, and posting still needs a button press every time.
3. Under **Destinations**, fill in the first destination:
   - **Name:** what you call it, such as `Squadron BGS`. It appears in the menu and in the messages, so the link itself is never shown.
   - **Webhook link:** paste the link from Discord. The box hides what you type, like a password.
   - **Thread ID (optional):** paste a thread's number to post into that thread.
4. Press **Test**. WFMT asks Discord whether the link works and posts nothing. You should see `Works: WFMT.` (the webhook's own name).
5. To post to more than one channel or server, press **Add destination** and fill in another. **Remove** deletes one.
6. Close Settings with **OK** to save.

Destinations are saved **for the commander you are playing**, on this computer only. WFMT learns who that is from the game's journal, so log in first. If you type them
before WFMT has seen you log in, they are kept and saved for the commander who logs in next. They are left out of **Back up my data**, so a backup you keep in a cloud
folder does not hold them.

## Webhooks, commanders and channels

**A webhook belongs to one channel, not to a commander.** In Discord, whoever has the **Manage Webhooks** permission makes a webhook for a particular channel on a
particular server, and its link can post to that channel (or to a thread inside it) and nowhere else. It cannot be pointed at another channel or another server.

- **One destination for each place you post.** To post to two channels, or to channels on two servers, make a webhook in each and add a destination for each, with a name
  you will recognize (`Squadron BGS`, `Friends`, `Colonization crew`).
- **Choosing where a report goes.** With one destination, **Post to Discord** posts to it. With several, it opens a small menu of their names (`Post to Squadron BGS`,
  `Post to Friends`, and Cancel) and posts only to the one you pick. Nothing is sent to a destination you did not choose.
- **The commander.** The list belongs to the commander the journal last named, meaning whoever is logged in. When you log in as another commander, **Post to Discord** uses
  that commander's destinations, and the report it posts is that commander's data. A commander with none saved is told to set one up, and nothing is sent.
- **Two commanders, one channel.** Webhooks are not tied to a commander, so both can save the same link and post to the same channel. On the second commander's Discord tab,
  use **Copy their destinations** (it appears when another commander has some saved) to add the first commander's list instead of pasting the links again. Press **OK**
  to save.
- **Editing instead of duplicating.** Posting the same report again to the same destination edits the earlier post. A different destination gets its own post. WFMT
  remembers these posts for each commander until EDMC restarts.
- **The switch is shared.** **Allow Post to Discord** covers every commander.

## Common questions

**Do I have to be in the channel to post to it? What if I am on a different server?**
No. A post goes to the channel the webhook belongs to, wherever you are in Discord. WFMT sends it straight to Discord over the internet using the webhook link, so your Discord
account, the Discord app and whichever channel or server you are looking at have no part in it. You can be on another server, in a direct message, or have Discord closed, and the
post still lands in that channel. The link names one channel on one server, and anyone who holds it can post there without being a member. To post somewhere else, add another
destination with a webhook made in that channel (see [Webhooks, commanders and channels](#webhooks-commanders-and-channels)).

**What can stop a post from arriving?** The webhook or its channel being deleted, or the webhook link being replaced. WFMT then says `Discord did not accept that webhook link` or
`Discord could not find that webhook` (see [When something goes wrong](#when-something-goes-wrong)). Because the link is all it takes to post, keep it private. If it leaks, delete
the webhook in Discord.

**Whose name do the posts show? Why is it not my commander name or my server nickname?**
A webhook is not your account, so its posts appear under the **webhook's own name and picture**, never your server nickname. WFMT does not send a name of its own and the post
carries no commander name, so what you see is the name the webhook was given.

- **To change the name or picture:** open the channel's settings (the gear icon), choose **Integrations**, then **Webhooks**, open the webhook, change **Name** (for example to your
  commander name) and the picture if you like, and press **Save Changes**. You can do this at any time, with no need to make a new webhook. New posts use the new name straight away,
  and older posts keep the name they were posted under.
- **One name for each webhook.** Everyone who posts through the same webhook shows the same name. If two commanders should appear under their own names, make a second webhook in the
  channel, name it for the second commander, and save it as that commander's destination.
- **Names Discord refuses.** Discord does not allow some names for webhooks. If it rejects the one you choose, it says so when you save, and you can pick another.

## Customize how your posts look

By default each report is posted in one layout. A dialog lets you choose another, switch parts of a post on and off, and save your own looks as templates. It changes **Copy for
Discord** and **Post to Discord** together (they always use the same template). The plain **Copy Summary** and **Copy Progress** are not affected.

**Open it** from the BGS Report's **Discord** menu (**Customize post…**), the **Customize…** button in the Powerplay Sessions window, or **Customize posts…** on the **Settings → WFMT →
Discord** tab. A **Report** box at the top switches between the BGS report and Powerplay progress.

**Templates.** Pick one in the **Template** box and it becomes the one that report's posts use at once.
- **Standard** is the layout the posts have always had. **Compact**, **Detailed** and **Plain** are the other built-in presets. The presets cannot be changed or deleted.
- Change the checkboxes, then **Save as…** to keep your version under a name of your own. **Save** replaces one of your own templates, **Rename…** and **Delete** act on them. You can keep
  30 for each report.
- Changing a checkbox only changes the **preview** until you save. Posts keep using the template shown in the box, and the note under the buttons says when your changes are not saved yet.
- Templates are kept for the whole installation (not for each commander), are included in **Back up my data**, and are kept across updates. They are only looks, so there is nothing secret in them.

**The preview** shows the post made from your current tick or session (or made-up example data when there is none yet), roughly as Discord will draw it, with how many characters and
messages it comes to. Discord allows 2,000 characters in a message, so a long report is several messages.

**What you can switch, for the BGS report**

| Checkbox | What it does |
|---|---|
| Heading with the tick time | The title and the tick's time span at the top |
| Star on pinned systems | A star before the name of a system you pinned |
| Controlling faction in bold | Makes the faction that controls the system stand out |
| State changes | Shows a change such as `None → Boom` |
| Influence and its change | Shows `45.2% (+1.3)` |
| Pending, recovering and active states | The lines listing those states |
| What you did (the You: lines) | Your missions, trade, exploration data and so on, for each faction |
| Government and allegiance | Adds `Democracy / Federation` to each faction |
| One line for each system | The compact layout: the controlling faction and what you did, on one line |
| No formatting marks | Bullets without bold or italics, for a quieter post |
| Systems: every system, or only where you acted | Leaves out systems you only passed through |

**What you can switch, for Powerplay progress**

| Checkbox | What it does |
|---|---|
| Heading | The title and the note that CP is an estimate |
| Your Power in the heading | Adds your Power's name to the title |
| Link each system to Inara | Makes each system name a link, without a preview card |
| Estimated Control Points | The `(~48.0 CP)` part of each line |
| The system's Powerplay state | Adds `Exploited`, `Fortified` and so on, for the system you are in |
| Merits by activity | Adds `Acquisition 80, Reinforcement 40` to each line |
| The cycle's total line | The cycle's merits, estimated CP and systems worked |
| No formatting marks | Bullets without bold or italics |

**The built-in presets**

| Preset | BGS report | Powerplay progress |
|---|---|---|
| **Standard** | The layout the posts have always had | The layout the posts have always had |
| **Compact** | One line for each system, without the pending, recovering and active lists | No Inara links, no state and no cycle line |
| **Detailed** | Standard with the government and allegiance | Standard with the merits for each activity |
| **Plain** | No bold or italics | No bold or italics (links appear as the address in angle brackets) |

**What no setting can change.** Every name is still escaped, so a faction or system called `@everyone` or `*Raiders*` shows as written, and every post is still sent with mentions
switched off, so nothing can ping anyone. Long posts are still split under Discord's limit, and a template that would make a very long post just means more messages.

**Example: a short post for a busy channel.** Your squadron's `#bgs-reports` channel is busy, so you want one line for each system.
1. Open the BGS Report, then the **Discord** menu, then **Customize post…**.
2. Pick the **Compact** template. The preview shows lines like
   `Example System — Example Union (None → Boom, 45.2% (+1.3)) — You: Example Union 2 mission(s) done, INF +4/-0; 1,500,000 cr exploration data`.
3. Press **Done**, and **Post to Discord** now posts that layout.

**Example: only the systems you worked, without the heading.**
1. In the dialog, tick **Only systems where you acted** and untick **Heading with the tick time**. The preview loses the title and the systems you passed through.
2. Press **Save as…** and name it `My systems`. It is now the template for BGS posts, and you can pick **Standard** again from the box any time.

**Example: Powerplay progress with the activity breakdown but no cycle line.**
1. Open the Powerplay Sessions window and press **Customize…**.
2. Pick **Detailed**, then untick **The cycle's total line**. The preview lines read like `Example System — 120 merits (~48.0 CP) — Acquisition 80, Reinforcement 40 — Exploited`.
3. **Save as…** `Squadron update`. It is chosen, so the next **Post to Discord** uses it.

## Examples

### Post the BGS report after the tick

You have flown a few missions for your faction and want your squadron to see the result.

1. Open BGS mode and press **REPORT**. The window opens on the current tick. (Use the tick drop-down at the top to choose an earlier tick.)
2. Open the **Discord** menu in the window's header and choose **Post to Discord**.
3. With one destination, the line at the foot of the window says `Posting to Discord...`, then `Posted to Squadron BGS.` (the destination's name). With several, a small menu asks which one first.

In the channel the post reads like this (names here are made up):

```
WFMT BGS report
Current tick - since 2026-10-29 09:00 UTC
Nervi
- Nervi Brotherhood (bold: it controls the system) - Boom, 45.2% (+1.3)
  - Pending: Famine
  - You: 2 mission(s) done, INF +4/-0; 1,500,000 cr exploration data
- Allied Forces - War, 30.0%
```

(Discord shows the headings and the controlling faction in bold, and the lists as bullets.) The report holds only the tick you are looking at, with
a block for each system.

**Post again later in the same tick** and WFMT **edits the earlier post** instead of adding another, so the channel keeps one up-to-date report for
that tick. The foot of the window says `Updated your earlier post in Squadron BGS.` A new tick is a new post. WFMT remembers the posts until you
restart EDMC; after a restart, posting the same tick again adds a new message.

### Share your Powerplay progress

1. In Powerplay mode press **REPORT** to open the Powerplay Sessions window.
2. Press **Post to Discord** (above the tabs, at the right).
3. The post has this session's merits for each system, with the estimated Control Points marked `~` because they are estimates, then the cycle's total line:

```
WFMT Powerplay progress - Aisling Duval
This session. CP is an estimate (~).
- Nervi - 120 merits (~48.0 CP) - Exploited
- Sol - 1,234 merits (~493.6 CP)
Cycle
CYCLE 12 TOTAL - 3,400 merits - est. 1,360.0 CP - 5 systems worked
```

Each system name links to its Inara page without a preview card. Post again later in the same session and WFMT edits the post; a new login is a
new session and a new post.

### Copy for Discord when you have no webhook

You are not allowed to make webhooks on a server, or you would rather paste by hand.

1. Open the report and choose **Copy for Discord** (the **Discord** menu on the BGS report, the button on the Powerplay window).
2. The foot of the window says `Copied for Discord.` Paste into the Discord message box and press Enter.
3. A long report is several messages, because Discord allows 2,000 characters in one. The window says `Copied for Discord (3 messages: paste each one on
   its own).` and the copy has a blank line between the messages. Paste one message at a time, sending each before the next.

### Post to two channels

Your squadron has a `#bgs-reports` channel and you also keep a `#friends-chat` channel on another server.

1. In each channel make a webhook (see [Set up Discord](#set-up-discord-make-a-webhook)) and copy each link.
2. In **Settings → WFMT → Discord** add two destinations: `Squadron BGS` with the first link and `Friends` with the second. Press **Test** on each, then **OK**.
3. Open the BGS Report and choose **Post to Discord**. A menu offers `Post to Squadron BGS` and `Post to Friends`. Pick one.
4. Post the same tick to the other destination the same way. Each destination keeps its own post, so posting again to `Friends` edits the `Friends` message only.

### Use the same channel from two commanders

You fly two commanders and want both to post to `#bgs-reports`.

1. Log in as the first commander and save the destination (name, link, **OK**).
2. Log in as the second commander and open **Settings → WFMT → Discord**. Choose the first commander in the list beside **Copy their destinations** and press the button. The destination appears in the list.
3. Press **OK**. Each commander now posts that commander's own report to the same channel.

### Post into a thread

Save the thread's number in the destination's **Thread ID** (see [Set up Discord](#set-up-discord-make-a-webhook)) and post as usual. WFMT adds the thread to the
request. If the thread is archived, Discord reopens it for the post.

## Sharing somewhere that is not Discord

The plain copy buttons are for everywhere else, and they are unchanged: **Copy Summary** on the BGS report and **Copy Progress** on the Powerplay
Sessions window. They copy plain text with no Discord marks, so a forum post, an email, a note or another chat program shows it cleanly.

**Example: a forum post.** Open **REPORT**, press **Copy Summary**, and paste into the post. You get lines such as `Nervi:` then
`  * Nervi Brotherhood — Boom, 45.2% (+1.3)`. **Copy Progress** gives one line for each system (by default
`[Nervi](https://inara.cz/...) - 120 merits (~48.0 CP) - Exploited`, which several forums and chat programs turn into a link). Its layout is
editable under **Settings → WFMT → Powerplay → Clipboard**.

## What is sent, and who can see it

- **Only when you press Post to Discord**, WFMT sends the report text to the webhook address you saved, which is on `discord.com`. Nothing is sent on its own,
  and **Copy for Discord**, **Test** (which reads, and posts nothing) and the plain copy buttons send no report.
- **What the post holds:** the report text only. It has no commander name, but it does show the systems, factions and numbers you chose to share, and anyone who
  can read the channel can read it.
- **Nobody is pinged.** WFMT sends every post with mentions switched off, and puts an invisible space after any `@` in a name, so a faction called
  `@everyone` cannot notify anyone. Names with `*` or `_` show as written instead of turning into formatting.
- **The links are secrets.** WFMT keeps each commander's destinations in `discord_webhooks.json` in the plugin folder, leaves it out of Back up my data, never writes
  it to the EDMC log, and strips it from **Copy diagnostics** if it ever appeared. Do not share it yourself.
- The request names WFMT and its version (`WFMT/1.x (discord; +...)`), like every other WFMT request. See [What goes on the internet](internet-and-privacy.md).

## Changing or removing a destination

- **Change one:** paste the new link (or change the name or thread) on the **Discord** tab and close Settings with **OK**. **Test** checks it first.
- **Stop posting for now:** untick **Allow Post to Discord**. The destinations stay saved.
- **Remove one from WFMT:** press **Remove** beside it and close Settings. Remove them all and WFMT forgets that commander's destinations.
- **Remove it from Discord:** open the channel's **Integrations → Webhooks**, open the webhook and press **Delete Webhook**. Do this if the link ever leaks.

## When something goes wrong

The message appears on the line at the foot of the window.

| You see | Why | What to do |
|---|---|---|
| `Turn on Post to Discord and save a webhook link on the Settings, Discord tab first.` | The switch is off, no link is saved for this commander, or WFMT has not seen you log in yet | Do [Set up WFMT](#set-up-wfmt) for the commander you are playing. After starting EDMC with the game closed, log in first |
| `There is no destination called ...` | The menu named a destination that has since been removed or renamed | Open **Settings → WFMT → Discord** and check the names, then post again |
| `That is not a Discord webhook link. It looks like https://discord.com/api/webhooks/...` | The box holds something else, such as the channel's address or a half-copied link | Copy the link again with **Copy Webhook URL** |
| `Discord did not accept that webhook link. It may have been changed or removed.` | The webhook was deleted or its link changed | Make a new webhook and paste the new link |
| `Discord could not find that webhook or message. It may have been deleted.` | The webhook (or a message WFMT wanted to edit) is gone | Check the webhook still exists. If only the earlier message was deleted, post again: WFMT sends a new one |
| `Discord is asking for a pause. Wait a little and try again.` | Discord limits how fast a webhook can post, and a retry did not clear it | Wait a minute and press the button again |
| `Discord refused the message (400). It may be too long.` | Discord did not accept the text | Try again; if it keeps happening, use **Copy for Discord** and paste by hand, and [report it](reporting-problems.md) |
| `Could not reach Discord. Check your connection and try again.` | No connection, or Discord is down | Check your connection and try again |
| `A post is already on its way.` | You pressed again while the last post was still being sent | Wait for the first to finish |
| `Posting failed unexpectedly; see the EDMC log.` | Something unexpected. The log line has the kind of error, never the link | [Report it](reporting-problems.md) with **Copy diagnostics** |
| Nothing appears in the channel | The destination may point at a different channel, or a thread | Open the webhook in Discord and check its channel; check the destination's **Thread ID** |

**The Post to Discord button does nothing visible?** Look at the line at the foot of the window: it says what happened. If you are in a window that is not
the BGS Report or Powerplay Sessions, sharing is not available there yet.
