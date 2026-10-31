# How WFMT uses Spansh

[Spansh](https://spansh.co.uk/) is a community-run service that WFMT, like many Elite Dangerous tools, uses for routes, system data and market prices.

This page records what WFMT asks it for, when, how often, what is sent, and what WFMT does to keep its use light. It is kept up to date with the code: a change to the requests WFMT makes is a change to this page.

If you run Spansh, or you are another developer, and something here concerns you, please open an issue at <https://github.com/rwharpernc/wayfarers-multitool/issues>.

Every request carries a User-Agent that points to this project.

## How WFMT identifies itself

Every request has the User-Agent `WFMT/<version> (<feature>; +https://github.com/rwharpernc/wayfarers-multitool)`, where `<feature>` names the part of WFMT that made it (for example
`route-planner`, `neutron-finder`, `canonn-poi`). The code is in `plugin/http_identity.py`. WFMT does not hide behind a browser's User-Agent.

## Principles

- **Only on request.** Nothing is requested in the background to prepare a feature.
  - A request follows a button press, a switch the user turned on, or (for typing suggestions) typing.
  - The one large download, the neutron-star data dump, follows only the user pressing **Download and build** or **Update**.
  - The switches are all off until the user turns them on, except where a feature cannot work without the request, such as the **Generate route** button.
  - The list is on the **Online lookups** page of Settings and in [the guide](guide/internet-and-privacy.md).
- **Nothing about the player is sent.**
  - The requests carry system names or addresses, coordinates, search filters and, for the Route Planner, the ship's numbers (mass, fuel tank, drive figures).
  - They carry no commander name, credits, position history or journal text.
- **No bulk collection.** WFMT does not crawl or mirror Spansh's data. A search asks for what one action needs.
  - The exception is the optional local star index: a user who presses its button downloads one of the files Spansh publishes for download, once per press (see the table and the section under it).
- **Local caching.** Answers that are likely to be asked for again are kept for the session (see the table).

## What WFMT asks for, and when

| Feature | Endpoint | What starts it | Requests for one action | Switch |
|---|---|---|---|---|
| Route Planner: **Generate route** | `GET /api/systems/field_values/system_names` | The button | 1 for the destination, 1 more for the start if it is not the current system | None; the button is the request |
| Route Planner: **Generate route** | `POST /api/generic/route`, then `GET /api/results/<job>` | The button | 1 to submit, then 1 about every 5 seconds until the job finishes (a long route can take a minute or two; WFMT stops waiting after 5 minutes) | None; the button is the request |
| Carrier Route: **Generate route** | `GET /api/systems/field_values/system_names` | The button | 1 for each destination (up to 10), 1 more for the start if it is not where the carrier is | None; the button is the request |
| Carrier Route: **Generate route** | `POST /api/fleetcarrier/route`, then `GET /api/results/<job>` | The button | 1 to submit, then 1 about every 5 seconds until the job finishes (WFMT stops after 5 minutes); through the courtesy layer | None; the button is the request |
| Route Planner: neutron stops that may have a secondary star | `GET /api/system/<address>` | After a route is plotted, and as it is followed | One per neutron stop for the next 12 stops (asked for once each; one that failed is asked again after 5 minutes), then about one per system reached | None; follows the route |
| Expedition window: **Road to Riches**, **Exomastery** | `POST /api/riches/route`, `POST /api/exobiology/route`, `GET /api/results/<job>` | The **Plot** button | 1 to submit, then 1 about every 5 seconds until done | None; the button is the request |
| **Neutron Star** and **White Dwarf** buttons | `POST /api/bodies/search` | The button | 1 per press; none for **Neutron Star** when the local star index is installed and switched on | None |
| Local star index: **Download and build**, **Update** | `GET https://downloads.spansh.co.uk/systems_neutron.json.gz`; for an update usually `systems_1day.json.gz` or `systems_1week.json.gz` instead (the dumps listed on <https://spansh.co.uk/dumps>) | The button, in Settings → WFMT → General → Online lookups | 1 GET of one file per press: about 173 MB for the first download, about 3 MB (1 day) or 19 MB (1 week) for an update (more only to continue after a dropped connection or a busy answer, from where it stopped); an update sends `If-Modified-Since` with the date of the file the index is current to and downloads nothing when the file is unchanged | None; the button is the request |
| System name suggestions while typing | `GET /api/systems/field_values/system_names` | Typing 3 or more characters, after a pause of about a third of a second | 1 per pause; up to 400 typed starts are remembered for the session | Off until turned on (General → Window) |
| Random: random undiscovered system | `GET /api/systems/search` | The button | 1 per press; the list is reused for 10 minutes while the position is within 5 ly | None |
| Region Sweep | `GET /api/systems?q=` | The **Discover Known Systems (Spansh)** button | 1 per press, for the selected cube (or the current one) | Only when you press the button; there is no switch |
| Nearest place to land | `POST /api/stations/search` | **Find** in the window that the **Find** button on the Exploration panel opens | 2 per press (stations, then fleet carriers; 1 with carriers off); the same search asked again within 2 minutes is answered from memory | Off until turned on (the box in that window, or Settings) |
| Mining: Get body info (a system's bodies and mining-location counts) | `GET /api/dump/<system id>` | The button | 1 per press, through the courtesy layer | Off until turned on (Mining) |
| Mining: hotspot finder, best price finder, Market research, What pays | `POST /api/bodies/search`, `POST /api/stations/search` | The buttons | 1 per press (What pays one for each commodity, at most 16, 0.3 seconds apart, stopping at the first failure) | Each off until turned on (Mining) |
| Materials: Find a trader | `POST /api/stations/search` | **Find** in the Material trader window (opened from the Materials window) | 1 per press; the same search asked again within 2 minutes is answered from memory | None; the button is the request |
| Trade: routes, prices, best picks, round trip; mission sources | `POST /api/trade/route`, `GET /api/results/<job>`, `POST /api/stations/search` | The buttons | Routes: 1 to submit, then 1 about every 5 seconds until done. **Near me** or **Galaxy**: 2 searches (stations, then fleet carriers; 1 with carriers off). **Best picks**: about 4, or 5 with carriers, one after another. **Round trip**: 1 to 3 station searches of 100 stations each. A route search stops waiting after 4 minutes | Off until turned on (Trade) |
| Trade: Watch list **Refresh** | `POST /api/stations/search` | The **Refresh** button | 2 per watched commodity (buy, then sell; up to 30 commodities), 0.4 seconds apart, stations only, markets updated in the last 7 days; a press while a refresh runs does nothing | Off until turned on (Trade) |
| Colonization: Where to buy (**Find nearest**, **Find all**) | `POST /api/stations/search` | The **Find nearest** and **Find all** buttons | **Find nearest**: 1 search for the commodity (2 with fleet carriers, which are included unless **Exclude fleet carriers** is ticked, asked for apart). **Find all**: the same searches for each commodity (0.4 seconds apart; fewer when a station that sells several of them covers one in full), plus 1 or 2 searches for stations that sell several of the commodities at once, plus 1 more search (orbital stations only) for each commodity whose every source found is a surface port. Nothing else is asked per system; markets updated in the last 7 days; the same search asked again within 2 minutes is answered from memory | Only when you press the button |
| Exploration Value: Earth-like world rarity | `POST /api/bodies/search` | Scanning an Earth-like world | 1 per system; the count is kept for the session | Off until turned on |
| System targets: life and points of interest others found | `GET /api/system/<address>` | The arrival and other survey events of a system, once per system (tried again at the next event only after a failure) | 1 per system | Off until turned on (WFMT → Overlays → System targets) |
| Rare Goods Finder: which Power controls an origin system | `GET /api/system/<address>` | Opening the Rare Goods Finder window; ticking **Only my Power** there | 1 per listed origin system that is not already answered, queued 5 at a time and sent at most 2 at a time by the layer; answers, failures included, are kept for the session. With **Only my Power** ticked it asks about 10 origin systems at a time, nearest first, until enough are found for your Power (at most all 141, once per session) | None; opening the window, or ticking the box, is the request |

### The data dump download

The local star index is optional and is never started by WFMT. Nothing is downloaded until the user presses **Download and build** (or **Update**) in Settings → WFMT → General → Online lookups, which says what is fetched, from where, how large it is and how much disk it takes.

**The full file**

- The file is `systems_neutron.json.gz` on `downloads.spansh.co.uk`, a gzip of a JSON array with one system per line (about 173 MB).
- It holds systems whose main star is a neutron star, with some black holes and other main stars that WFMT discards.

**Update**

- **Update** uses `systems_1day.json.gz` (changes since midnight UTC the day before) or `systems_1week.json.gz` (since midnight 7 days ago).
- These are in the same layout, every main star, merged into the index.
- It chooses the smaller file that reaches back to the index's date and falls back to the full file when none does, after 20 updates in a row, or when the index's full file is more than 60 days old.

**The request**

- It is a plain GET with the User-Agent described above (feature `star-index`) and nothing else about the user.
- It goes through `Courtesy.stream_to_file`, which uses the same gate, cap of 2 requests in flight, retries for a GET and stop after repeated failures as every other request.

How the download is limited:

- **One download at a time**, started only by the user.
- **Conditional.** **Update** sends the date the installed index is current to (an update file), or the ETag and date of the full file it was built from (when the full file is asked for again), so an unchanged file is answered 304 and nothing is transferred.
- **Resumable.** A cancelled or interrupted download is kept as a partial file and continued with a Range request (with `If-Range`, so a file that changed meanwhile is fetched again from the start).
- **Checked before it is written.** WFMT needs room for the file and for building the index (about 300 MB more) and refuses to start without it, and it refuses a file larger than 200 MiB, a little
  over the expected size, so a changed or wrong answer cannot fill the disk.
- **Used once.** The file is turned into an index of about 110 MB in the plugin folder and deleted, so nothing is read from it again and the next download is the user's choice. The index lists only the
  main star of each system, as the dump does.

## What WFMT does to be considerate

Every request in the table goes through `plugin/spansh_courtesy.py`, and a test (`tests/test_spansh_through_courtesy.py`) fails if a module reaches Spansh any other way. The layer's behavior is covered by
tests (`tests/test_spansh_courtesy.py`).

- **A cap on requests at once.** No more than 2 requests are in flight, across every part of WFMT.
- **Spacing.** At least a quarter of a second passes between the starts of two requests.
- **Backing off when Spansh is busy.** An answer of 429, 502, 503 or 504 is retried up to 3 times, waiting 2, 6 and then 15 seconds (with a little randomness), or as long as a `Retry-After` header asks, up
  to a minute.
- **Retrying only what is safe to repeat.** A timeout is retried for a GET. A POST that timed out may already have been accepted, so it is not sent again; a POST is retried only when Spansh answers
  that it is busy.
- **Stopping when Spansh is struggling.** After 5 failed requests in a row (each already retried), WFMT makes no further Spansh requests for 5 minutes and says so in the window, instead of
  continuing to ask a service that is in trouble.
- **Cancelling.** A route that is being waited for can be cancelled, and cancelling also ends any wait before a retry.
- **No waiting while typing.** System name suggestions are asked for once, with no retry: a suggestion that arrived after several seconds of waiting would be for text that has already changed. They still
  count toward the pause after repeated failures, and during a pause no suggestions are asked for.
- **Asking once.** The star lookups for neutron stops are made once per stop, for the next dozen stops only. System name suggestions, the Random list and Powerplay answers are cached for the session.
- **A count.** **Copy diagnostics** (Settings → WFMT → General → Help) includes a line with the number of Spansh requests the session has sent, how many were retried, and how many were not sent during a pause.
- **Respecting refusals.** An answer such as 400, 404 or 422 is treated as an answer, not retried, and the message is shown to the user.

## What WFMT does not do

- It does not make Spansh requests on a timer or while a window sits open; each request follows an action, an event or typing, as in the table.
  - Other services have their own entries on the **Online lookups** page; for example the BGS tick check runs every minute against a different service.
- It does not download Spansh's data dumps by itself or on a schedule.
  - The only downloads are the neutron-star dump and its small update files, and only when the user presses **Download and build** or **Update** (see "The data dump download" above).
  - The larger files, the full galaxy dump among them, are never requested.
- It does not use any key or login with Spansh.

## If a concern is raised

The levers available to the project, from quickest to most involved:

1. **Lower the limits.** The numbers above (`MAX_CONCURRENT`, `MIN_GAP_S`, the retry waits, the pause after failures) are constants at the top of `plugin/spansh_courtesy.py`; changing them is one small
   release.
2. **Change or remove a feature's request.** Each feature's calls are in one module (listed in [MODULES.md](MODULES.md)); the request can be reduced, cached longer, or the feature switched to off by
   default.
3. **Use local data instead of requests** where Spansh publishes a dump that covers the need (the local star index does this for the Neutron Star button, and nothing is fetched unless the user asks).
   The download's size cap, the conditional and resumed requests and the button that starts it are in `plugin/star_index_download.py`; removing the button removes the request.

A change reaches users with the next release, through the in-app updater for those who have automatic updates on.
