# Sharing reports to Discord: research

**Status:** research and plan, written 2026-10-29. **Decisions (2026-10-29):** Discord webhooks are in scope, because posting by webhook is
now an expected feature for Discord users, and **plain copy and paste stays in scope for everyone else**, so commanders who use other chat
programs, forums or notes are not left out. **Stage 1 is built** (the shared formatter, webhook client, per-commander store and Settings tab, and the BGS report and Powerplay progress); stages 2 and 3 are not. The sections below were written before the build, so where they differ the code and [the guide](guide/discord.md) are right. One change was made after stage 1 first shipped: a webhook belongs to one channel, so each commander now saves a named **list of destinations** (not one webhook), **Post to Discord** asks which one when there are several, the same report keeps a separate earlier post for each destination, and Settings can copy another commander's list. This page records what other tools do, what Discord allows,
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
3. **Exploration and exobiology sales, expedition announcements, and colonization and team building.** From the Expedition Log and the
   Expedition window: a run's totals, and announcements the commander chooses to send (started, stop reached, finished). From the
   Colonization Sites window: shopping-list, progress, call-for-helpers and completion posts (section 10, whose scope is still to be chosen).
4. **Carrier movement.** Departure requests, cancellations and arrivals, with the departure time as a Discord timestamp.
5. **Customizing posts.** A dialog with presets, section toggles, a preview and saved templates (section 11), after the posts above exist to customize.

## 9. Open questions (stage 1 and the earlier stages)

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

## 10. Colonization and team building (added to stage 2, 2026-10-29)

**Status: scope chosen (2026-10-29).** The request was "some support for colonization and team building", without a settled idea of what that is. The first cut of
stage 2 is **A (shopping list), B (progress update), C (call for helpers) and D (completion post)**, and **E (who is hauling what)** as the team-building post.
**E depends on co-op building, which WFMT does not have yet**, so the co-op work comes first (see "Order of work" below).

**What exists to build on**
- The Colonization Sites window (`plugin/colonization_window.py`) already has **Copy To Acquire** (`_on_copy_acquire`: each commodity with the tons still to
  get, after the ship's cargo and the carrier's tally, biggest first) and the full shopping list copy. Both are plain text for the clipboard.
- A site (`colonization.Site`) holds its name, system, progress, remaining tons, whether it is complete or failed, when it was first seen and when it
  finished (so a build time), and the commodity rows (`colonization_view.py`, `view.acquire_lines`, `colonization.shopping_list`).
- Raven Colonial links already exist: `rcc_client.build_page_url(build_id)` and `system_page_url(system)` open the project or the system in a browser. Someone
  who gets the link can see the project and join it on Raven.
- **Co-op building in WFMT is not built.** [TODO.md](TODO.md) ("Multi-commander projects: plan") lists claim, release, join and ready as future phases. Two commanders
  who each run WFMT with their own Raven key are already credited on the same Raven project; what is missing is seeing and sharing who is doing what.

**Candidate posts, each built from the selected site** (all with **Copy**, **Copy for Discord** and **Post to Discord**, all manual):

| Candidate | What it says | Builds on | Needs |
|---|---|---|---|
| **A. Shopping list** | The site and system, then what is left to get, in tons, biggest first, and the trips for the commander's ship | **Copy To Acquire** and `view.acquire_lines` | Nothing new. The smallest piece |
| **B. Progress update** | The site, percent done, tons still needed, the biggest gaps, trips left, and a Raven link. Posted again later it edits the same message, so the channel keeps one live status post for the site | `Site.progress`, `remaining_total`, `view.commodity_rows`, the edit-earlier-post behavior already built | Nothing new |
| **C. Call for helpers (the team-building post)** | "Building *Station* in *System*: help wanted." The top commodities with tons, where to deliver (the system and the construction site), the Raven project link so a helper can join, and an optional line of the commander's own to say who to ask | A and B, and `rcc_client.build_page_url` | A **preview dialog** (as for expedition announcements) so the commander edits the wording and chooses whether their commander name and carrier name are included |
| **D. Completion post** | "*Station* in *System* is complete", with how long it took and the tons delivered (from the history) | `Site.completed_at`, `first_seen`, the delivery record in `colonization_ledger` | Nothing new |
| **E. Who is hauling what** | Which teammate has claimed which commodity | Raven's `commanders` data | **Not possible yet.** It needs the co-op phases in TODO.md. Listed so the Discord layer is ready to carry it when they exist |

**Where the buttons go:** beside **Copy To Acquire** in the Colonization Sites window, in a **Share** menu (the header bar there is also full at narrow
widths, as the Powerplay window showed), with **Call for helpers** opening its preview dialog.

**Privacy.** These posts say where a colony is being built and may name the carrier. All are manual. The call for helpers is the one most likely to be
read by strangers, so its preview shows exactly what will be sent, and the commander name and carrier name are off unless ticked.

**Order of work (stage 2)**
1. **Co-op reading first.** Phase 0 (check Raven's `commanders`, `ready` and delivery-history shapes against a live project with two or more linked commanders; this needs the
   commander's own Raven key and such a project, so it is the commander's test) and Phase 1 (read and display: a **Claimed** column in the Colonization Sites window, a
   split of each commodity into mine, taken by others and unclaimed, and who delivered what) from [TODO.md](TODO.md), "Multi-commander projects: plan". Read-only, one worker
   thread, nothing about other commanders saved to disk.
2. **Posts A to D** with the **Share** menu and the preview dialog (shared with expedition announcements).
3. **Post E** (who is hauling what) once Phase 1 gives the data: each teammate and the commodities they have taken, with the unclaimed ones listed so helpers can see what is open. It
   names other commanders, so its preview shows the names and they can be removed before it is sent.
4. Raven writes (claim, release, join, leave: Phases 2 and 3 of that plan) stay separate and later; Discord only reads and shares.

**Questions settled:** the first cut is A to D plus E (above), and the first question below is answered.

**Questions that remain**
1. ~~Which of A to D belong in the first cut of stage 2?~~ All four. (A and B are almost free; C needs the preview dialog that expedition announcements need anyway, so
   building C with the expedition announcements shares that dialog.)
2. Should the call for helpers include the Raven project link? It only exists when the commander has made a Raven project for the site. Without one, the post
   can still list the needs and the system.
3. Should the progress post (B) be one message that is edited as the build advances, or a new post each time? Edit-in-place keeps the channel quiet.
4. What does "team building" mean to you beyond a call for helpers: recruiting, coordinating who hauls what (needs the co-op phases), or something else?

## 11. Customizing posts: a dialog, presets and saved templates (brainstormed 2026-10-29)

**Status: brainstormed and scoped, not built.** Today each report has one fixed layout (`bgs_discord.py`, `powerplay_discord.py`). The only customization anywhere is Powerplay's
plain-text **Copy Progress** template under Settings. The idea is a separate dialog for customizing how a Discord (or other) post is formatted, with templates the commander can
save and choose between.

**Decisions**
- **The first build is toggles, not typed templates.** Presets plus section toggles for each report, a live preview, saved named templates, and a choice of which template each report
  uses. Typed header, row and footer templates with placeholders come later.
- **Embeds come later.** They can only be posted, never pasted by hand, and Discord's embed size limits have not been verified, so the first build keeps markdown messages and Copy for
  Discord keeps matching Post to Discord.
- **A per-destination "Post as" name was declined** (the webhook's own name is set in Discord; see [the guide](guide/discord.md#common-questions)).

**What the dialog does (first build)**
1. **Presets:** **Compact** (one line per system), **Standard** (today's layout), **Detailed** and **Plain** (no Discord marks). They are read-only starting points.
2. **Section toggles for each report.**
   - *BGS report:* heading and tick time, the star on pinned systems, the controlling faction in bold, state changes, influence and its change, pending, recovering and active states,
     your "You:" activity lines, and only the systems you worked or every system.
   - *Powerplay progress:* Inara links, estimated CP, the system's state, the cycle's total line, and a merits-only mode.
3. **Preview:** the post rendered approximately as Discord shows it, from the commander's real current data, with a counter such as "1,420 of 2,000 characters, 1 message". Because the escaping
   and the 2,000-character splitting stay automatic, no toggle can produce a post that pings someone or is too long to send.
4. **Saved named templates:** Save, Save as, Duplicate, Rename and Delete (the presets cannot be deleted), and a default template for each report.
5. **Where it lives:** a **Customize...** button in the BGS Report and Powerplay Sessions windows, and **Templates...** on the Discord Settings tab: one dialog with a tab for each report.

```
Customize Discord post          [BGS Report v] [Powerplay]
Template [Standard v] [Save as...] [Delete]
Sections  [x] Heading  [x] Pinned star  [x] States  [ ] Pending/Recovering  [x] You: lines
Time      (x) UTC text  ( ) Discord time tag
-------------------------------- Preview (1,420 / 2,000 characters, 1 message) ----
 **WFMT BGS report** ...
                                                                       [Done]
```

**Later**
- **A template for each destination** (for example `Squadron BGS` uses Detailed and `Friends` uses Compact), and **Send test** to a destination chosen in the dialog.
- **Typed templates:** header, row and footer templates with placeholders such as `{system}`, `{faction}`, `{influence}`, `{delta}`, `{merits}`, `{cp}` and `{state}`. Values are escaped
  automatically, so a name can never add formatting or a ping whatever the template says.
- **Import and Export** of a template as a block of text (as the Mining share line does) so squadron-mates can swap looks.
- **Embeds** (a colored side bar, a title, fields, a footer and a timestamp) as an option for Post to Discord only, once Discord's size limits are checked.
- **Other service formats** (Slack and Matrix webhooks use different markup) as new destination types with their own renderer, and a plain style for anywhere else.
- **A Discord time tag** (`<t:...>`, which shows each reader's own time) in place of UTC text, and a **Short** mode that keeps the top N systems so a report fits in one message.
- **A deliberate role ping** only as a high-risk, opt-in setting for each destination with a confirmation, because every post is sent with mentions switched off today.

**How it would be built**
- **A template is data, not code:** a name, the report it is for, the layout (a preset name or the section toggles) and the options. The pure renderers (`bgs_discord.py`,
  `powerplay_discord.py`) take a template and produce the messages; Standard reproduces today's output exactly, with a test.
- **Plain and Discord share the choices:** Copy for Discord and Post to Discord always render the same template. The plain **Copy Summary** and **Copy Progress** stay as they are.
- **Storage:** templates are not secrets, so they could be shared by every commander on the installation and included in **Back up my data**. Only which template a commander uses for each
  report would be saved for each commander. This is still to confirm.
- **Tests:** a renderer test for every preset and toggle (including that the output is identical to today's for Standard), the 2,000-character split with every toggle on, escaping with hostile
  names, saving, renaming, deleting and choosing templates, and a smoke test of the dialog.

**Questions that remain**
1. Should saved templates be shared by all commanders, or kept for each commander like the destinations? (Suggested: shared, with the choice for each commander.)
2. Do Import and Export of a template belong in the first build or the second? (Suggested: the second.)
3. Should the dialog open on real data or sample data when the commander has no current tick or session? (Suggested: sample data, labeled as an example.)

## Sources

- BGS-Tally: <https://github.com/aussig/BGS-Tally> and its wiki page <https://github.com/aussig/BGS-Tally/wiki/Discord-Server-Setup>
- BGS-Tally changelog: <https://github.imc.re/aussig/BGS-Tally/blob/develop/CHANGELOG.md>
- Discord webhook reference: <https://docs.discord.com/developers/resources/webhook>
- EDBGS: <https://codeberg.org/nola/EDBGS>
- Elite BGS bot: <https://github.com/Elite-Kode/bgsbot>
- EDMC PowerPlay Progress: <https://forums.frontier.co.uk/threads/edmc-plugin-power-play-progress.636217>
