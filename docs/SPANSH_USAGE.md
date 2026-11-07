# Spansh usage

This page lists every request WFMT sends to [Spansh](https://spansh.co.uk/): the endpoint, the action that starts it, the number of requests, the data sent, and the measures that limit the load. It is updated when the requests change.

Questions from Spansh operators or other developers can be raised as an issue at <https://github.com/rwharpernc/wayfarers-multitool/issues>.

## Identification

Every request carries the User-Agent `WFMT/<version> (<feature>; +https://github.com/rwharpernc/wayfarers-multitool)`. `<feature>` names the part of WFMT that made the request (for example `route-planner`, `neutron-finder`, `canonn-poi`, `star-index`). The code is in `plugin/http_identity.py`. WFMT does not use a browser User-Agent.

## Principles

- **Requests follow user actions.** No request is sent in the background to prepare a feature.
  - A request follows a button press, an enabled switch or, for name suggestions, typing.
  - The one large download, the neutron-star data dump, follows only **Download and build** or **Update**.
  - Switches are off by default, except where a feature cannot work without the request, such as the **Generate route** button.
  - Every switch is on the **Online** tab of Settings (Settings → WFMT → Online), and the list is in [the guide](guide/internet-and-privacy.md).
- **No personal data is sent.**
  - Requests carry system names or addresses, coordinates, search filters and, for the Route Planner, the ship's mass, fuel tank and drive figures.
  - Requests carry no commander name, credits, position history or journal text.
- **No bulk collection.** Each search requests the data one action needs. The exception is the optional local star index, which downloads one of the files Spansh publishes for download, once per button press.
- **Local caching.** Answers that are likely to be requested again are kept for the session (see the table).

## Requests by feature

| Feature | Endpoint | What starts it | Requests for one action | Switch |
|---|---|---|---|---|
| Route Planner: **Generate route** | `GET /api/systems/field_values/system_names` | The button | 1 for the destination, 1 more for the start if it is not the current system | None; the button is the request |
| Route Planner: **Generate route** | `POST /api/generic/route`, then `GET /api/results/<job>` | The button | 1 to submit, then 1 about every 5 seconds until the job finishes (WFMT stops waiting after 5 minutes) | None; the button is the request |
| Carrier Route: **Generate route** | `GET /api/systems/field_values/system_names` | The button | 1 for each destination (up to 10), 1 more for the start if it is not where the carrier is | None; the button is the request |
| Carrier Route: **Generate route** | `POST /api/fleetcarrier/route`, then `GET /api/results/<job>` | The button | 1 to submit, then 1 about every 5 seconds until the job finishes (WFMT stops after 5 minutes); through the courtesy layer | None; the button is the request |
| Route Planner: neutron stops that may have a secondary star | `GET /api/system/<address>` | After a route is plotted, and as it is followed | One per neutron stop for the next 12 stops (asked for once each; one that failed is asked again after 5 minutes), then about one per system reached | None; follows the route |
| Expedition window: **Road to Riches**, **Exomastery** | `POST /api/riches/route`, `POST /api/exobiology/route`, `GET /api/results/<job>` | The **Plot** button | 1 to submit, then 1 about every 5 seconds until done | None; the button is the request |
| **Neutron Star** and **White Dwarf** buttons | `POST /api/bodies/search` | The button | 1 per press; none for **Neutron Star** when the local star index is installed and switched on | None |
| Local star index: **Download and build**, **Update** | `GET https://downloads.spansh.co.uk/systems_neutron.json.gz`; for an update usually `systems_1day.json.gz` or `systems_1week.json.gz` instead (the dumps listed on <https://spansh.co.uk/dumps>) | The button, in Settings → WFMT → Online | 1 GET of one file per press: about 173 MB for the first download, about 3 MB (1 day) or 19 MB (1 week) for an update (more only to continue after a dropped connection or a busy answer, from where it stopped); an update sends `If-Modified-Since` with the date of the file the index is current to and downloads nothing when the file is unchanged | None; the button is the request |
| System name suggestions while typing | `GET /api/systems/field_values/system_names` | Typing 3 or more characters, after a pause of about a third of a second | 1 per pause; up to 400 typed starts are remembered for the session | Off until switched on (**System name suggestions while typing**, Settings → WFMT → Online) |
| Random: random undiscovered system | `GET /api/systems/search` | The button | 1 per press; the list is reused for 10 minutes while the position is within 5 ly | None |
| Region Sweep | `GET /api/systems?q=` | The **Discover Known Systems (Spansh)** button | 1 per press, for the selected cube (or the current one) | None; the button is the request |
| Nearest place to land | `POST /api/stations/search` | **Find** in the window that the **Find** button on the Exploration panel opens | 2 per press (stations, then fleet carriers; 1 with carriers off); the same search asked again within 2 minutes is answered from memory | Off until switched on (**Nearest place to land**, Settings → WFMT → Online; the box in that window changes the same switch) |
| Mining: Get body info (a system's bodies and mining-location counts) | `GET /api/dump/<system id>` | The button | 1 per press, through the courtesy layer | Off until switched on (**Mining: Get body info in the Surface Mining Book**, Settings → WFMT → Online) |
| Mining: hotspot finder, best price finder, Market research, What pays | `POST /api/bodies/search`, `POST /api/stations/search` | The buttons | 1 per press (What pays one for each commodity, at most 16, 0.3 seconds apart, stopping at the first failure) | Each off until turned on (**Mining: nearby hotspot finder**, **Mining: best price finder and Market research**, Settings → WFMT → Online) |
| Materials: Find a trader | `POST /api/stations/search` | **Find** in the Material trader window (opened from the Materials window) | 1 per press; the same search asked again within 2 minutes is answered from memory | None; the button is the request |
| Trade: routes, prices, best picks, round trip; mission sources | `POST /api/trade/route`, `GET /api/results/<job>`, `POST /api/stations/search` | The buttons | Routes: 1 to submit, then 1 about every 5 seconds until done. **Near me** or **Galaxy**: 2 searches (stations, then fleet carriers; 1 with carriers off). **Best picks**: about 4, or 5 with carriers, one after another. **Round trip**: 1 to 3 station searches of 100 stations each. A route search stops waiting after 4 minutes | Off until switched on (**Trade: routes, prices and best picks**, Settings → WFMT → Online) |
| Trade: Watch list **Refresh** | `POST /api/stations/search` | The **Refresh** button | 2 per watched commodity (buy, then sell; up to 30 commodities), 0.4 seconds apart, stations only, markets updated in the last 7 days; a press while a refresh runs does nothing | Off until switched on (**Trade: routes, prices and best picks**, Settings → WFMT → Online) |
| Colonization: Where to buy (**Find nearest**, **Find all**) | `POST /api/stations/search` | The **Find nearest** and **Find all** buttons | **Find nearest**: the commander's own system is searched first (1 search, `this_system_only`), and when a station there has the commodity that is the whole answer; otherwise 1 more search around the chosen system (carriers, which are left out unless **Exclude fleet carriers** is unticked, are asked for apart and double each of these). With **Large, then Medium** (the default) the pair is asked again for Medium pads when no Large-pad station has it, so a Find nearest is 1 to 4 searches (2 to 8 with carriers). **Find all**: the same searches for each commodity (a commodity a one-stop station in the commander's own system supplies in full needs none) (0.4 seconds apart; fewer when a station that sells several of them covers one in full), plus 1 or 2 searches for stations that sell several of the commodities at once, plus 1 more search (orbital stations only) for each commodity whose every source found is a surface port. Nothing else is asked per system; markets updated in the last 7 days; the same search asked again within 2 minutes is answered from memory | None; the button is the request |
| Exploration Value: Earth-like world rarity | `POST /api/bodies/search` | Scanning an Earth-like world | 1 per system; the count is kept for the session | Off until switched on (**Exploration Value: Earth-like world rarity**, Settings → WFMT → Online) |
| System targets: life and points of interest others found | `GET /api/system/<address>` | The arrival and other survey events of a system, once per system (tried again at the next event only after a failure) | 1 per system | Off until switched on (**System targets: life and points of interest others found**, Settings → WFMT → Online) |
| Powerplay overlay: the system being jumped to | `GET /api/system/<address>` | The journal saying a hyperspace jump has started | 1 per destination system (a system just arrived in is not asked about); the answer is kept for an hour (a failure for 2 minutes) | Off until switched on (Settings → WFMT → Online, **Powerplay card: the system you are jumping to**) |
| Rare Goods Finder: which Power controls an origin system | `GET /api/system/<address>` | Opening the Rare Goods Finder window; ticking **Only my Power** there | 1 per listed origin system that is not already answered, queued 5 at a time and sent at most 2 at a time by the layer; answers, failures included, are kept for the session. With **Only my Power** ticked it asks about 10 origin systems at a time, nearest first, until enough are found for the commander's Power (at most all 142, once per session) | None; opening the window, or ticking the box, is the request |

## Data dump download

The local star index is optional. WFMT starts no download itself. A download starts only when **Download and build** or **Update** is pressed in Settings → WFMT → Online, which states what is fetched, from where, the file size and the disk space used.

**Full file**

- The file is `systems_neutron.json.gz` on `downloads.spansh.co.uk`: a gzip of a JSON array with one system per line (about 173 MB).
- It contains systems whose main star is a neutron star, plus some black holes and other main stars, which WFMT discards.

**Update**

- **Update** uses `systems_1day.json.gz` (changes since midnight UTC the day before) or `systems_1week.json.gz` (changes since midnight 7 days earlier). These files have the same layout, contain every main star, and are merged into the index.
- The smaller file that reaches back to the index date is chosen. The full file is downloaded when neither does, after 20 updates in a row, or when the full file the index was built from is more than 60 days old.

**Request**

- The request is a GET with the User-Agent described above (feature `star-index`) and no other data about the user.
- The request goes through `Courtesy.stream_to_file`, which applies the same gate, the cap of 2 requests in flight, the GET retries and the stop after repeated failures as every other request.

**Limits on the download**

- One download at a time, started only by the user.
- Conditional: **Update** sends the date the installed index is current to (update file), or the ETag and date of the full file the index was built from (full file), so an unchanged file is answered 304 and nothing is transferred.
- Resumable: a cancelled or interrupted download is kept as a partial file and continued with a Range request with `If-Range`. A file that changed in the meantime is fetched again from the start.
- Checked before writing: WFMT requires room for the file and about 300 MB more for building the index, and refuses to start without it. It refuses a file larger than 200 MiB.
- Single use: the file is converted into an index of about 110 MB in the plugin folder and then deleted. The index lists only the main star of each system, as the dump does.

## Load limits

Every request in the table goes through `plugin/spansh_courtesy.py`. `tests/test_spansh_through_courtesy.py` fails if a module reaches Spansh by another route. The behavior of the layer is covered by `tests/test_spansh_courtesy.py`.

| Measure | Behavior | Constant |
|---|---|---|
| Concurrency | At most 2 requests in flight across all of WFMT. | `MAX_CONCURRENT` |
| Spacing | At least 0.25 seconds between the starts of two requests. | `MIN_GAP_S` |
| Backoff | An answer of 429, 502, 503 or 504 is retried up to 3 times, after 2, 6 and 15 seconds (plus random jitter), or after the `Retry-After` period, up to 60 seconds. | `MAX_RETRIES`, `BACKOFF_S`, `MAX_WAIT_S`, `RETRY_STATUS` |
| Safe retries | A timeout is retried for a GET. A POST that timed out is not resent, because it may have been accepted; a POST is retried only when Spansh answers that it is busy. | |
| Circuit breaker | After 5 failed requests in a row (each already retried), no Spansh request is made for 300 seconds. The window reports this. | `BREAKER_FAILURES`, `BREAKER_S` |
| Cancelling | A route that is being waited for can be cancelled. Cancelling also ends any wait before a retry. | |
| Name suggestions | Requested once with no retry (`retries=0`), because a late answer applies to text that has changed. They count toward the breaker, and none are requested while it is open. | |
| Caching | Star lookups for neutron stops are made once per stop for the next 12 stops (`WINDOW` in `plugin/route_secondary.py`). System name suggestions, the Random list and Powerplay answers are cached for the session. | |
| Refusals | An answer such as 400, 404 or 422 is not retried. The message is shown to the user. | |
| Count | **Copy diagnostics** (Settings → WFMT → General → Help) includes the number of Spansh requests sent in the session, the number retried and the number not sent during a pause. | |

## Not done by WFMT

- WFMT sends no Spansh request on a timer or while a window is open. Each request follows an action, an event or typing, as listed in the table.
  - Other services are listed on the **Online** tab. The BGS tick check, for example, runs every minute against a different service.
- WFMT does not download Spansh data dumps on its own or on a schedule. The only downloads are the neutron-star dump and its update files, started by **Download and build** or **Update**. Larger files, including the full galaxy dump, are never requested.
- WFMT uses no key or login with Spansh.

## Adjusting the load

- The limits above are constants at the top of `plugin/spansh_courtesy.py`.
- The calls of each feature are in one module (see [MODULES.md](MODULES.md)).
- The download size cap, the conditional and resumed requests and the button that starts the download are in `plugin/star_index_download.py`.

A change reaches users with the next release, through the in-app updater when automatic updates are on.
