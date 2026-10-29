# Sharing reports to Discord: research

**Status:** research and plan, written 2026-10-29. **Decisions (2026-10-29):** Discord webhooks are in scope, because posting by webhook is
now an expected feature for Discord users, and **plain copy and paste stays in scope for everyone else**, so commanders who use other chat
programs, forums or notes are not left out. Nothing described here is built yet. This page records what other tools do, what Discord allows,
what WFMT already has, the options considered and the plan.

**Decisions this changes.** [BGS_TECH_SPEC.md](BGS_TECH_SPEC.md) listed a Discord webhook as a non-goal; that note now points here. An earlier
review declined *automatic* carrier-jump posts to Discord for privacy reasons; that still stands (section 6: nothing is posted without a
press). When the first webhook feature is built, [What goes on the internet](guide/internet-and-privacy.md) must list the new request.

## 1. What was asked for

The ability to share these from WFMT, as a Discord post, as Discord-formatted text, or as plain text for any other place:

- the **BGS report**,
- **Powerplay progress**,
- **exploration and exobiology sales** (what an expedition earned),
- **carrier movement**,
- **expedition announcements**.

There are three ways out, and every report offers all three:

| Output | For | Network |
|---|---|---|
| **Copy** (plain text) | Any client: other chat programs, forums, notes, email. No formatting marks that another program would show as clutter | None |
| **Copy for Discord** | Pasting into Discord by hand, with Discord's formatting | None |
| **Post to Discord** | A webhook you save in Settings | One request per press, to your own webhook |

## 2. What WFMT has today

All of this is copy to the clipboard. Nothing is sent anywhere.

| Report | What exists | Where |
|---|---|---|
| BGS report | **REPORT**, then **Copy Summary**: every tick and system as plain text, starting `WFMT BGS Report`. Written so it can be posted "without any Discord-specific formatting" | `plugin/bgs_format.py` (`summary_text`) |
| Powerplay progress | **Copy Progress** in **SES**: one line per system visited this session, in a format you edit (placeholders `{system}`, `{system_url}`, `{merits}`, `{cp}`, `{state}`) | [Powerplay guide](guide/powerplay.md#share-your-progress) |
| Exploration and exobiology sales | The Expedition Log keeps each expedition's totals, including credits earned from exploration data sales and exobiology sales, and the Log window can copy what an expedition recorded | `plugin/expedition_log.py` (`facts_lines`), `plugin/expedition_log_window.py` |
| Carrier movement | Read from the journal for the **Carrier jump countdown** on the Flight Alerts card: the request (destination system, body and departure time), a cancellation, and the completed jump | `plugin/carrier_jump_timer.py` |
| Expedition announcements | The Expedition planner knows the name, the stops, the next stop and each stop reached. It can copy the stop list and the next stop's name, but has no announcement text | `plugin/expedition.py`, [Expedition guide](guide/exploration.md#expedition) |

The Mining Book also has a one-line **Share line** for a hotspot that is meant to be pasted into Discord. It is a separate feature and
shows how a share-by-paste format is already handled.

## 3. What other tools do

- **BGS-Tally** is the one tool confirmed to post to Discord. Per its own wiki:
  - It generates Discord-ready text to paste by hand, and can post directly to one or more servers through webhooks. The feature list says
    this can happen "including fully automatically".
  - Webhooks are set up in EDMC's settings: a table of webhook URLs, each with a nickname and checkboxes for which kinds of information
    go to that server. A **Post to Discord** button then appears in its windows.
  - Posting again within the same tick updates the earlier post instead of creating another.
  - Threads are reached by appending `?thread_id=<id>` to the webhook URL.
  - It lists Powerplay merits among what it tracks, but its documentation does not say whether Powerplay reports are among what it
    posts. That is unconfirmed.
- **EDBGS** (a BGS helper) builds BGS reports to paste into a Discord server. It is not an EDMC plugin and has no webhook.
- **Elite BGS bot** (Elite-Kode) is a Discord bot that answers BGS questions in a server. It is a bot, not a plugin.
- **EDMC PowerPlay Progress** shows merits and totals by system. Its thread does not mention Discord.

No second EDMC plugin that posts reports by webhook turned up.

## 4. What Discord allows (webhooks)

From Discord's public webhook documentation:

- **Execute Webhook** (`POST` to the webhook URL): `content` up to 2,000 characters; up to 10 embeds per message; at least one of `content`,
  `embeds`, files, components or a poll is required.
- **`wait=true`** returns the created message, which includes its id. Without it nothing is returned.
- **`thread_id`** posts into a thread of the webhook's channel. A forum or media channel needs a `thread_id` or a `thread_name`.
- **`allowed_mentions`** in the body controls which mentions fire. Discord recommends setting it when the content is user-generated, so a
  system name or note cannot ping a role.
- **`username`** overrides the webhook's display name for that message.
- **Edit Webhook Message:** `PATCH /webhooks/{id}/{token}/messages/{message id}`. This is how "update the earlier post" works. It needs the
  message id from a `wait=true` post, so WFMT would have to remember it.
- **Delete Webhook Message:** `DELETE` on the same path (`204` on success).
- **No sign-in:** the token endpoints need no other authentication. The documentation does not say the URL is secret, but anyone who has it
  can post to, edit and delete from that webhook, so it should be treated as a password. This is an inference.
- **Not confirmed here:** the per-embed size limits and the rate limits were not on the page that was read. Look them up before building,
  and handle `429` responses by waiting the time Discord asks for.

## 5. What each report would say, and what it would reveal

All of these would be sent only when the commander presses a button (the options below say why not automatically).

| Report | Possible content | Privacy and accuracy notes |
|---|---|---|
| BGS report | The existing report, formatted for Discord: a heading per tick, system names in bold, a line per faction with what you did | The report names the systems and factions you worked and the credits earned. Posting to a squadron channel is the usual purpose |
| Powerplay progress | Merits and estimated CP per system for the session, plus the cycle totals | CP is an estimate from editable ratios, so the post should say so. The default clipboard line already does this with `~` |
| Exploration and exobiology sales | The expedition's name, duration, systems, jumps, bodies scanned, first discoveries, species analyzed, credits earned from data sales and the unsold estimate | Earned figures are what the game reports on a sale. Unsold figures are WFMT's estimate and must be marked |
| Carrier movement | Destination system and body, the departure time as a Discord timestamp so it shows in each reader's own time, and a cancellation | Reveals where the carrier is going and when. Only known if the game wrote the request while WFMT could see it. A past review declined automatic carrier posts for privacy. Manual only, to a channel the commander chooses, fits that decision |
| Expedition announcements | "Colonia run has set off from Sol: 12 stops", the next stop, a stop reached, the expedition finished with its totals | Reveals position over time. Manual, with the commander choosing which events to announce |

## 6. Options

| Option | What it is | For | Against |
|---|---|---|---|
| **A. Copy for Discord** | A **Copy for Discord** next to each existing copy button, which stays as the plain-text **Copy**. Same data, formatted with Discord's markdown: bold system names, a code block for columns, links wrapped so they do not unfurl, long reports split into messages under 2,000 characters | No network. Keeps "nothing is sent unless you opt in". Fits the existing buttons. Nothing to reverse in the specs | The commander still pastes by hand. Several messages for a long report |
| **B. Post by webhook** | A **Post to Discord** button that sends the same text to a webhook URL the commander saves in Settings | One press instead of copy and paste. Can update the earlier post for the same tick and use threads, as BGS-Tally does | A new online feature: the internet page and the BGS spec change. The webhook URL is a secret to store and never log. More failure cases (revoked webhook, rate limit, no connection) |
| **C. Automatic posting** | WFMT posts on a tick, a sale, a carrier request or an expedition event | Nothing to remember | The riskiest for privacy and for spam. A mistake posts location data without a press. Not recommended |

**Decision:** A and B are both in scope, and the plain-text copy stays for non-Discord clients. C stays out: every post follows a button
press. Each report is written once as data, then rendered two ways: plain text (the existing **Copy**, which must read well anywhere) and
Discord markdown (used by **Copy for Discord** and **Post to Discord**).

## 7. How the webhook feature would be built

A sketch to settle before any code is written:

- **Settings:** a **Discord** tab with the webhook URL (hidden after saving), a nickname, an optional thread id, and a tick for each of the
  five reports. The webhook is saved for each commander, because nothing else is shared between commanders. Off until a URL is saved.
- **The request:** one `POST` per message to the saved URL, using `wait=true` when the post may be updated later, with `allowed_mentions`
  set to allow no mentions, a `username` of the commander's choosing, and WFMT's usual User-Agent (`plugin/http_identity.py`) naming the
  feature. Nothing is sent except the text the commander just saw.
- **Never logged:** the URL is not written to the log, to **Copy diagnostics** or to a bug report. Errors name the nickname, not the URL.
- **Backups:** decide whether **Back up my data** includes the URL. It is a secret, so the default should be that it does not.
- **Updating a post:** remember the message id for the current tick and edit it with `PATCH` when the same report is posted again,
  falling back to a new post if the edit fails because the message was deleted.
- **Limits:** split text at 2,000 characters on a line boundary, and wait out a `429`.
- **Documentation:** a row on the internet page and in Settings → Online lookups, a section in each guide where a **Post to Discord**
  button appears, and the BGS spec's non-goal rewritten.
- **Tests:** in Docker, against a small local server that stands in for Discord, covering the split, the update, a `429`, a revoked
  webhook and a missing URL.

## 8. Plan

Build the shared parts once, then add one report at a time. Each phase is tested in Docker and documented before the next starts.

1. **Shared sharing core.** A plain-text renderer (the current wording, kept as the reference for what other clients get), the Discord
   formatter (bold, code blocks, links that do not unfurl, a timestamp helper), the 2,000-character
   splitter, the webhook client (post, post with `wait=true`, edit, `429` handling, the User-Agent and `allowed_mentions` rules above), the
   Discord settings tab with the saved webhook (never logged, never in diagnostics), the internet page entry and the rewritten spec note.
2. **BGS report and Powerplay progress.** Both already have copy buttons and data, so they prove the core: **Copy for Discord** and **Post to
   Discord** beside the existing buttons, and updating the earlier post for the same tick.
3. **Exploration and exobiology sales, and expedition announcements.** From the Expedition Log and the Expedition window: a run's totals,
   and announcements the commander chooses to send (started, stop reached, finished).
4. **Carrier movement.** Departure requests, cancellations and arrivals, with the departure time as a Discord timestamp.

## 9. Open questions

1. Should the webhook be saved for each commander or once for the installation? Suggested: for each commander, matching the rest of WFMT,
   with a way to copy it to another commander.
2. Should **Back up my data** include the webhook URL? Suggested: no, since it is a secret.
3. Should one webhook serve every report, or should each report type have its own (BGS to one channel, carrier movement to another)?
   BGS-Tally allows several, each with checkboxes for what goes to it.
4. Should expedition announcements use fixed wording, or open for editing before they are posted?
5. For carrier movement, which events are posted: the request, the cancellation and the arrival, or the request only?
6. Should each report have two buttons (**Copy** and **Copy for Discord**, with **Post to Discord** beside them), or one **Copy** with a
   **Plain / Discord** choice that WFMT remembers? Suggested: two buttons, because the choice is visible and a wrong format is never pasted
   by accident.

## Sources

- BGS-Tally: <https://github.com/aussig/BGS-Tally> and its wiki page <https://github.com/aussig/BGS-Tally/wiki/Discord-Server-Setup>
- BGS-Tally changelog: <https://github.imc.re/aussig/BGS-Tally/blob/develop/CHANGELOG.md>
- Discord webhook reference: <https://docs.discord.com/developers/resources/webhook>
- EDBGS: <https://codeberg.org/nola/EDBGS>
- Elite BGS bot: <https://github.com/Elite-Kode/bgsbot>
- EDMC PowerPlay Progress: <https://forums.frontier.co.uk/threads/edmc-plugin-power-play-progress.636217>
