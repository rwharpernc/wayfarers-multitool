# Sharing Reports to Discord: Research Record

Scope: the research behind WFMT's Discord sharing, the decisions taken on 2026-10-29, and the behavior of the implemented code. The user-facing description is in [the Discord guide](guide/discord.md); where this page and the code differ, the code is correct.

**Contents:**

- [Decisions](#decisions)
- [Outputs](#outputs)
- [Reports that have a Discord output](#reports-that-have-a-discord-output)
- [Reports without a Discord output](#reports-without-a-discord-output)
- [Webhook requests](#webhook-requests)
- [Destinations and storage](#destinations-and-storage)
- [Customizing posts](#customizing-posts)
- [Privacy rules](#privacy-rules)
- [Sources](#sources)

## Decisions

Recorded 2026-10-29.

- Discord webhooks are in scope. Plain copy to the clipboard remains available for other chat programs, forums and notes.
- Every post follows a button press. No automatic posting exists.
- [BGS_TECH_SPEC.md](BGS_TECH_SPEC.md) listed a Discord webhook as a non-goal; that entry now refers to this page.
- An earlier review declined automatic carrier-jump posts to Discord for privacy reasons; the decision stands.
- A webhook belongs to one channel. Each commander therefore saves a named list of destinations. **Post to Discord** asks which destination to use when more than one is saved. The same report keeps a separate earlier post for each destination. Settings can copy another commander's list.
- A per-destination "Post as" name is not implemented; the webhook's own name is set in Discord (see [the guide](guide/discord.md#common-questions)).

## Outputs

| Output | Network | Description |
| --- | --- | --- |
| Copy (plain text) | None | Text without formatting marks, for any client. |
| **Copy for Discord** | None | Text with Discord markdown, for pasting by hand. A report longer than 2,000 characters is copied as several messages. |
| **Post to Discord** | One request per message, to the chosen webhook | Sends the same messages as **Copy for Discord**. Requires the switch on the Discord Settings tab and at least one saved destination. |

## Reports that have a Discord output

| Report | Plain copy | Discord output | Source files |
| --- | --- | --- | --- |
| BGS report | **Copy Summary**: every period and system as plain text, starting `WFMT BGS Report` | The **Discord** menu of the BGS Report window: **Copy for Discord**, **Post to Discord**, **Customize post…** (the tick shown in the window) | `bgs_format.py` (`summary_text`), `bgs_discord.py`, `bgs_window.py` |
| Powerplay progress | **Copy Progress**: one line per system visited this session, from a template with the placeholders `{system}`, `{system_url}`, `{merits}`, `{cp}` and `{state}` (default `[{system}]({system_url}) - {merits} merits (~{cp} CP) - {state}`) | Buttons **Customize…**, **Copy for Discord** and **Post to Discord** in the Powerplay Sessions window | `powerplay_clipboard.py`, `powerplay_discord.py`, `powerplay_window.py` |
| Expedition summary | **Copy summary**: the selected expedition's recorded figures as plain lines (`expedition_log.py` `facts_lines`) | Buttons **Copy for Discord**, **Post to Discord** and **Customize…** in a row above the buttons at the foot of the Expedition Log window (the selected expedition); the key is the expedition's id, so posting it again edits the earlier post | `expedition_log.py`, `expedition_discord.py`, `expedition_log_window.py` |

Shared code: `discord_format.py` (escaping, bold, italic, links, code blocks, Discord timestamps, splitting at 2,000 characters), `discord_client.py` (webhook requests), `discord_share.py` (copy and post for the report windows), `discord_webhooks.py` (destinations), `discord_settings.py` (Settings tab), `discord_customize.py`, `discord_templates.py` and `discord_preview.py` (customizing).

## Reports without a Discord output

The following reports have no Discord output in the code. The data each holds is listed.

| Report | Existing data and copy function |
| --- | --- |
| Carrier movement | `carrier_jump_timer.py` reads the jump request (destination system, body and departure time), a cancellation and the completed jump from the journal for the Carrier jump countdown on the Flight Alerts card. |
| Expedition announcements | The Expedition planner holds the name, the stops, the next stop and each stop reached, and can copy the stop list and the next stop's name (`expedition.py`). It has no announcement text. |
| Colonization sites | The Colonization Sites window has **Copy Shopping List** (plain text, biggest first). `rcc_client.build_page_url(build_id)` and `system_page_url(system)` build Raven Colonial links. |

The Mining Book has a separate one-line **Share line** for a hotspot, intended for pasting into Discord or another Mining Book (`mining_ledger.py`).

## Webhook requests

Implemented in `discord_client.py`. Behavior verified in the code:

| Item | Behavior |
| --- | --- |
| Request | One request per message to the saved webhook, with `wait=true`; Discord answers with the created message, whose id is stored for later edits. |
| Message limit | `MESSAGE_LIMIT = 2000` characters. A longer message is rejected with an error; `discord_format.split_message` splits reports at that limit. An empty message is rejected. |
| Mentions | Every body carries `allowed_mentions` with `parse` empty, so no mention fires. |
| Threads | `thread_id` is sent when the destination has a thread id (digits only, at most 25) or the webhook link carries `thread_id`. |
| Hosts | `discord.com`, `ptb.discord.com`, `canary.discord.com`, `discordapp.com`. The path must match `/api[/vN]/webhooks/<id>/<token>`. |
| Editing | `edit` replaces a message by id; `delete` removes one. A repeated post of the same report under the same key to the same destination edits the earlier messages, posts a new message where the earlier one was deleted in Discord, and deletes surplus earlier messages when the report now needs fewer. The ids are kept for the session only. |
| Retry | A response with status 429, 502 or 503 is retried once after the wait Discord requests (`retry_after` in the body, else the `Retry-After` header, else 2.0 seconds), at most 10.0 seconds. |
| Timeout and size | Timeout 15 seconds. A response larger than 100,000 bytes is not read beyond that. |
| Test | **Test** on the Discord Settings tab checks the typed link through `discord_client.check`, a read that posts nothing. |
| User-Agent | WFMT's usual User-Agent from `http_identity.py`. |
| Errors | Worded as plain sentences that never contain the webhook link. |

WFMT sends `content` and `allowed_mentions` only; it sends no embeds, `username` or `thread_name`.

## Destinations and storage

- Destinations are stored for each commander in `discord_webhooks.json` (`discord_webhooks.py`), through `commander_data.py`.
- Each destination has a name (at most 40 characters, defaulting when empty, made unique with a numeric suffix), a link (at most 300 characters) and an optional thread id (at most 25 characters). A commander can save at most 10 destinations.
- A file written by the first version, which held one link with a nickname for each commander, is read as a list of one.
- The master switch is the setting `wfmt_discord_enabled`; it is off until turned on.
- `discord_webhooks.json` is left out of **Back up my data** (`data_backup.LEFT_OUT`, together with `rcc_keys.json`).
- The Discord Settings tab provides the switch, the destination rows (name, thread id, hidden link, **Test**, remove), a copy-from-another-commander control and **Customize posts…**.

## Customizing posts

Implemented in `discord_customize.py`, `discord_templates.py` and `discord_preview.py`, with options read by `bgs_discord.py`, `powerplay_discord.py` and `expedition_discord.py`.

- **Templates.** A template is data: a name, the report it is for and its options. The built-in presets Standard, Compact, Detailed and Plain cannot be changed or deleted. Standard reproduces the layout the posts had before templates existed. A commander's own templates are saved by name in `discord_templates.json`. Templates are shared by every commander, and the chosen template for each report applies to the installation. A report falls back to Standard when its chosen template is deleted.
- **Template actions.** Save, Save as, Rename and Delete; there is no Duplicate, since Save as serves that purpose. The template shown in the box is the one **Copy for Discord** and **Post to Discord** use for that report.
- **Preview.** Rendered from the current tick or session; example data, labeled as such, is used when none exists. A counter shows characters and message count.
- **Safety.** Escaping and the 2,000-character splitting are applied regardless of options, and no option enables a mention.
- **Entry points.** **Customize post…** in the BGS Report's **Discord** menu, **Customize…** in the Powerplay Sessions window, **Customize…** in the Expedition Log window, and **Customize posts…** on the Discord Settings tab. The dialog has a **Report** box that switches between the three reports.
- **Window size.** Default 860 x 780, minimum 720 x 640.

Options by report (default is the Standard value):

| Report | Option | Dialog label | Standard | Compact | Detailed | Plain |
| --- | --- | --- | --- | --- | --- | --- |
| BGS | `heading` | Heading with the tick time | on | on | on | on |
| BGS | `pinned_star` | Star on pinned systems | on | on | on | on |
| BGS | `bold_controller` | Controlling faction in bold | on | on | on | on |
| BGS | `states` | State changes (None to Boom) | on | on | on | on |
| BGS | `influence` | Influence and its change | on | on | on | on |
| BGS | `state_lists` | Pending, recovering and active states | on | off | on | on |
| BGS | `activity` | What you did (the You: lines) | on | on | on | on |
| BGS | `details` | Government and allegiance | off | off | on | off |
| BGS | `compact` | One line for each system | off | on | off | off |
| BGS | `plain` | No formatting marks (plain text) | off | off | off | on |
| BGS | `scope` | Systems: Every system in the tick / Only systems where you acted | every system | every system | every system | every system |
| Powerplay | `heading` | Heading | on | on | on | on |
| Powerplay | `power` | Your Power in the heading | on | on | on | on |
| Powerplay | `links` | Link each system to Inara | on | off | on | on |
| Powerplay | `cp` | Estimated Control Points | on | on | on | on |
| Powerplay | `state` | The system's Powerplay state | on | off | on | on |
| Powerplay | `activities` | Merits by activity | off | off | on | off |
| Powerplay | `cycle` | The cycle's total line | on | off | on | on |
| Powerplay | `plain` | No formatting marks (plain text) | off | off | off | on |
| Expedition | `heading` | Heading with the name, status and time | on | on | on | on |
| Expedition | `route` | Where it started and ended | on | off | on | on |
| Expedition | `exploration` | Exploration figures | on | off | on | on |
| Expedition | `exobiology` | Exobiology figures | on | off | on | on |
| Expedition | `sales` | What you earned from sales | on | on | on | on |
| Expedition | `unsold` | Unsold data (estimates) | on | off | on | on |
| Expedition | `ships` | Ships used | off | off | on | off |
| Expedition | `notes` | Your notes | off | off | on | off |
| Expedition | `plain` | No formatting marks (plain text) | off | off | off | on |

Not implemented: typed header, row and footer templates; embeds; a template for each destination; Import and Export of templates; a Discord time tag option in the dialog.

## Privacy rules

- Nothing is posted without a button press, and only while the switch on the Discord Settings tab is on.
- The webhook link is a secret: whoever has it can post to the channel. It is never logged, never shown in a message, left out of **Back up my data**, and kept out of the diagnostics text.
- BGS reports name the systems and factions worked. Powerplay estimates of Control Points come from editable ratios and are marked with `~` in the default clipboard line.
- The request is listed in [What goes on the internet](guide/internet-and-privacy.md).

## Sources

- Discord webhook reference: <https://docs.discord.com/developers/resources/webhook>
