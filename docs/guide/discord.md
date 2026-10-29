# Sharing reports to Discord (and anywhere else)

WFMT can share its reports three ways, so you can use whichever fits the place you are sharing to:

| Button | What it does | Needs a webhook | Sends anything |
|---|---|---|---|
| **Copy** (**Copy Summary** on the BGS report, **Copy Progress** on Powerplay) | Puts the report on the clipboard as plain text, with no marks that another program would show as clutter. For forums, notes, email and any other chat program | No | No |
| **Copy for Discord** | Puts the report on the clipboard with Discord's formatting (bold names, links, bullet lists). You paste it into Discord yourself | No | No |
| **Post to Discord** | Sends the report to a Discord channel through a webhook you set up. One press, one post | Yes | Only the report text, to your own webhook, when you press it |

Nothing is ever posted on its own. Every post follows a button press.

**On this page:** [What you can share](#what-you-can-share) · [Quick start](#quick-start) · [Set up Discord](#set-up-discord-make-a-webhook) · [Set up WFMT](#set-up-wfmt) · [Examples](#examples) · [Sharing somewhere that is not Discord](#sharing-somewhere-that-is-not-discord) · [What is sent, and who can see it](#what-is-sent-and-who-can-see-it) · [Changing or removing the webhook](#changing-or-removing-the-webhook) · [When something goes wrong](#when-something-goes-wrong)

## What you can share

| Report | Where | The buttons |
|---|---|---|
| **BGS report**: the tick shown in the window, a block for each system with the factions, their states and influence, and what you did | BGS mode, **REPORT** window | **Copy Summary**, and the **Discord** menu in the window's header: **Copy for Discord** and **Post to Discord** |
| **Powerplay progress**: this session's merits and estimated Control Points for each system, and the cycle's total | Powerplay mode, **SES** (the Powerplay Sessions window) | **Copy Progress**, and **Copy for Discord** and **Post to Discord** in a row above the tabs |

Coming later, as separate builds: expedition sales and announcements, colonization and team building (shopping lists, progress, a call for helpers), and carrier movement. They are planned in
[the Discord sharing research](../DISCORD_SHARING_RESEARCH.md) and are not in WFMT yet.

## Quick start

1. In Discord, make a webhook for the channel you want ([Set up Discord](#set-up-discord-make-a-webhook)) and copy its link.
2. In EDMC open **File → Settings → WFMT → Discord**, tick **Allow Post to Discord**, paste the link, and press **Test webhook** ([Set up WFMT](#set-up-wfmt)).
3. Close Settings to save.
4. Open a report (**REPORT** in BGS mode, or **SES** in Powerplay mode) and press **Post to Discord**.

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
3. You will paste that number into WFMT's **Thread ID** box in the next section. (A forum channel needs a thread.)

## Set up WFMT

1. In EDMC open **File → Settings → WFMT → Discord**.
2. Tick **Allow Post to Discord**. It is off until you tick it, and posting still needs a button press every time.
3. Paste the link into **Webhook link**. The box hides what you type, like a password.
4. Optional: type a **Nickname**, such as `Squadron BGS`. It is only a label for you, so WFMT's messages can say where a report went without showing the link.
5. Optional: paste a **Thread ID** to post into a thread.
6. Press **Test webhook**. WFMT asks Discord whether the link works and posts nothing. You should see `Works: WFMT.` (the webhook's name).
7. Close Settings to save.

The webhook is saved **for the commander you are playing**, on this computer only. If you play several commanders, log in as each and save
a link for each (they can all use the same link). It is left out of **Back up my data**, so a backup you keep in a cloud folder does not hold it.

## Examples

### Post the BGS report after the tick

You have flown a few missions for your faction and want your squadron to see the result.

1. Open BGS mode and press **REPORT**. The window opens on the current tick. (Use the tick drop-down at the top to choose an earlier tick.)
2. Open the **Discord** menu in the window's header and choose **Post to Discord**.
3. The line at the foot of the window says `Posting to Discord...`, then `Posted to Squadron BGS.` (your nickname, or `Discord` if you left it blank).

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

1. In Powerplay mode press **SES** to open the Powerplay Sessions window.
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

### Post into a thread

Save the thread's number in **Thread ID** (see [Set up Discord](#set-up-discord-make-a-webhook)) and post as usual. WFMT adds the thread to the
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
  and **Copy for Discord**, **Test webhook** (which reads, and posts nothing) and the plain copy buttons send no report.
- **What the post holds:** the report text only. It has no commander name, but it does show the systems, factions and numbers you chose to share, and anyone who
  can read the channel can read it.
- **Nobody is pinged.** WFMT sends every post with mentions switched off, and puts an invisible space after any `@` in a name, so a faction called
  `@everyone` cannot notify anyone. Names with `*` or `_` show as written instead of turning into formatting.
- **The link is a secret.** WFMT keeps it for each commander in `discord_webhooks.json` in the plugin folder, leaves it out of Back up my data, never writes
  it to the EDMC log, and strips it from **Copy diagnostics** if it ever appeared. Do not share it yourself.
- The request names WFMT and its version (`WFMT/1.x (discord; +...)`), like every other WFMT request. See [What goes on the internet](internet-and-privacy.md).

## Changing or removing the webhook

- **Change it:** paste the new link on the **Discord** tab and close Settings. Test webhook checks it first.
- **Stop posting for now:** untick **Allow Post to Discord**. The link stays saved.
- **Remove it from WFMT:** clear the **Webhook link** box and close Settings. WFMT forgets the link and the nickname and thread.
- **Remove it from Discord:** open the channel's **Integrations → Webhooks**, open the webhook and press **Delete Webhook**. Do this if the link ever leaks.

## When something goes wrong

The message appears on the line at the foot of the window.

| You see | Why | What to do |
|---|---|---|
| `Turn on Post to Discord and save a webhook link on the Settings, Discord tab first.` | The switch is off, no link is saved for this commander, or WFMT has not seen you log in yet | Do [Set up WFMT](#set-up-wfmt) for the commander you are playing. After starting EDMC with the game closed, log in first |
| `That is not a Discord webhook link. It looks like https://discord.com/api/webhooks/...` | The box holds something else, such as the channel's address or a half-copied link | Copy the link again with **Copy Webhook URL** |
| `Discord did not accept that webhook link. It may have been changed or removed.` | The webhook was deleted or its link changed | Make a new webhook and paste the new link |
| `Discord could not find that webhook or message. It may have been deleted.` | The webhook (or a message WFMT wanted to edit) is gone | Check the webhook still exists. If only the earlier message was deleted, post again: WFMT sends a new one |
| `Discord is asking for a pause. Wait a little and try again.` | Discord limits how fast a webhook can post, and a retry did not clear it | Wait a minute and press the button again |
| `Discord refused the message (400). It may be too long.` | Discord did not accept the text | Try again; if it keeps happening, use **Copy for Discord** and paste by hand, and [report it](reporting-problems.md) |
| `Could not reach Discord. Check your connection and try again.` | No connection, or Discord is down | Check your connection and try again |
| `A post is already on its way.` | You pressed again while the last post was still being sent | Wait for the first to finish |
| `Posting failed unexpectedly; see the EDMC log.` | Something unexpected. The log line has the kind of error, never the link | [Report it](reporting-problems.md) with **Copy diagnostics** |
| Nothing appears in the channel | The webhook may point at a different channel, or a thread | Open the webhook in Discord and check its channel; check the **Thread ID** |

**The Post to Discord button does nothing visible?** Look at the line at the foot of the window: it says what happened. If you are in a window that is not
the BGS Report or Powerplay Sessions, sharing is not available there yet.
