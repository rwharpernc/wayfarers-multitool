"""Sale-merit log: what each sale earned in Powerplay merits, kept so the trade-merit rule can be worked out from data.

Frontier does not publish how sales earn merits, and the players' reports conflict (docs/POWERPLAY_MERIT_RESEARCH.md). The journal does not link a
sale to its merits either: `PowerplayMerits` names only the Power, the gain and the new total. This module therefore pairs them by time, as the
megaship scans and the hand-ins do. In the owner's journals the merit event follows a `MarketSell` by 0 to 4 seconds in 97% of the sales that
have exactly one nearby merit event, so:

- a sale claims the first `PowerplayMerits` within `FIRST_MERIT_S` seconds after it,
- further merit events within `FOLLOW_ON_S` seconds of the last one claimed belong to the same sale,
- the next `MarketSell` closes the sale before it, and a merit event that a hand-in has already claimed is never taken.

A sale is recorded only when the commander is pledged and the system has a Powerplay state, and it is recorded with 0 merits when none follow:
the zero-pay sales are part of the question. Nothing here estimates merits; it only records what happened.

Pure logic (no Tk, no network, no EDMC): see tests/test_sale_merits.py. `SaleLog` is the CSV file; `replay_sales` rebuilds records from journal entries."""
from __future__ import annotations

import csv
import io
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

from .powerplay_ledger import cycle_number, cycle_start_for, parse_ts

FIRST_MERIT_S = 6
FOLLOW_ON_S = 3
LOG_FILENAME = "sale_merits.csv"

UNKNOWN_RANK = "?"
"""What the rank column holds when the journal gave no rank. A blank cell means the rank was not looked up yet (a row written before the column existed)."""

COLUMNS = (
    "time", "commander", "power", "rank", "cycle", "system", "station", "state", "holder", "activity", "commodity", "tons",
    "sell_price", "avg_paid", "total_sale", "profit", "margin_pct", "merits", "merit_events", "bought_in", "mined", "black_market",
)


@dataclass(frozen=True)
class Context:
    """Where the commander stands when a sale is made (supplied by the Powerplay tracker)."""

    power: str
    system: str
    state: str
    holder: str
    activity: str
    rank: Optional[int] = None


@dataclass
class Sale:
    time: str
    commander: str
    power: str
    system: str
    station: str
    state: str
    holder: str
    activity: str
    commodity: str
    tons: int
    sell_price: int
    avg_paid: int
    total_sale: int
    bought_in: str
    mined: bool
    black_market: bool
    merits: int = 0
    merit_events: int = 0
    rank: Optional[int] = None

    @property
    def rank_text(self) -> str:
        return str(self.rank) if self.rank is not None else UNKNOWN_RANK

    @property
    def cycle(self) -> Optional[int]:
        """The Powerplay cycle number the sale was made in (from its time; 101 began on 2026-10-01 07:00 UTC)."""
        return cycle_of(self.time)

    @property
    def profit(self) -> int:
        return self.total_sale - self.avg_paid * self.tons

    @property
    def margin_pct(self) -> Optional[float]:
        """Profit over what the goods cost, in percent, or None when the cost is unknown (a mission reward or other free cargo)."""
        return round((self.sell_price - self.avg_paid) * 100.0 / self.avg_paid, 1) if self.avg_paid > 0 else None

    @property
    def key(self) -> Tuple[str, str, str, int, int]:
        """The same sale seen twice (live, then by a rescan) has the same key."""
        return (self.commander.casefold(), self.time, self.commodity.casefold(), self.tons, self.total_sale)

    def row(self) -> List[Any]:
        margin = self.margin_pct
        return [self.time, self.commander, self.power, self.rank_text, "" if self.cycle is None else self.cycle, self.system, self.station, self.state, self.holder, self.activity, self.commodity,
                self.tons, self.sell_price, self.avg_paid, self.total_sale, self.profit, "" if margin is None else margin, self.merits,
                self.merit_events, self.bought_in, "yes" if self.mined else "no", "yes" if self.black_market else "no"]


def cycle_of(time_text: Any) -> Optional[int]:
    """The Powerplay cycle number for a journal timestamp, or None when it cannot be read."""
    when = parse_ts(time_text)
    return cycle_number(cycle_start_for(when)) if when is not None else None


def _stamp(value: Any) -> Optional[datetime]:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _norm(name: Any) -> str:
    """A commodity name as the journal writes it ("$platinum_name;" or "Platinum"), lower case without the markup."""
    text = str(name or "").strip().casefold()
    if text.startswith("$") and text.endswith("_name;"):
        text = text[1:-6]
    return text


class SaleTracker:
    """Feed it every journal event of one commander in order. `feed` returns the sales that are finished by that event."""

    def __init__(self, commander: str = "") -> None:
        self.commander = commander
        self._open: Optional[Sale] = None
        self._open_at: Optional[datetime] = None
        self._last_merit_at: Optional[datetime] = None
        self._bought_in: Dict[str, str] = {}
        self._mined: Set[str] = set()
        self._station = ""

    def feed(self, entry: Dict[str, Any], context: Callable[[], Optional[Context]]) -> List[Sale]:
        """A journal event other than `PowerplayMerits`. `context()` is called only for a sale or a purchase."""
        event = entry.get("event")
        when = _stamp(entry.get("timestamp"))
        done: List[Sale] = []
        if event == "Fileheader":
            done = self.flush()
            self._bought_in.clear()
            self._mined.clear()
            self._station = ""
            return done
        if self._open is not None and when is not None and self._expired(when):
            done = self.flush()
        if event == "Docked":
            self._station = str(entry.get("StationName") or "")
        elif event == "Location":
            self._station = str(entry.get("StationName") or "") if entry.get("Docked") else ""
        elif event == "CarrierJump":
            # Jumping aboard a fleet carrier leaves the commander docked at it, and no `Docked` event follows.
            self._station = str(entry.get("StationName") or "") if entry.get("Docked") else ""
        elif event in ("Undocked", "FSDJump", "SupercruiseEntry"):
            self._station = ""
        elif event == "MiningRefined":
            self._mined.add(_norm(entry.get("Type")))
        elif event == "MarketBuy":
            ctx = context()
            if ctx is not None:
                self._bought_in[_norm(entry.get("Type"))] = ctx.system
        elif event == "MarketSell":
            done += self.flush()
            sale = self._start(entry, when, context)
            if sale is not None:
                self._open, self._open_at, self._last_merit_at = sale, when, None
        return done

    def merit(self, entry: Dict[str, Any], gained: Optional[int], delivery: bool = False) -> List[Sale]:
        """A `PowerplayMerits` event that earned `gained` merits (the Powerplay tracker's reading of it). `delivery` is True when a hand-in has
        already claimed it, so a sale must not."""
        when = _stamp(entry.get("timestamp"))
        if self._open is None or when is None or self._open_at is None:
            return []
        if self._expired(when):
            done = self.flush()
            return done
        if delivery:
            return []
        if gained is None or gained <= 0:
            return []
        self._open.merits += gained
        self._open.merit_events += 1
        self._last_merit_at = when
        return []

    def flush(self) -> List[Sale]:
        """The sale still waiting for merits, if any (call it when the commander changes or EDMC closes)."""
        done = [self._open] if self._open is not None else []
        self._open = self._open_at = self._last_merit_at = None
        return done

    def _expired(self, when: datetime) -> bool:
        if self._open_at is None:
            return False
        if self._last_merit_at is not None:
            return (when - self._last_merit_at).total_seconds() > FOLLOW_ON_S
        return (when - self._open_at).total_seconds() > FIRST_MERIT_S

    def _start(self, entry: Dict[str, Any], when: Optional[datetime], context: Callable[[], Optional[Context]]) -> Optional[Sale]:
        ctx = context()
        count = _int(entry.get("Count"))
        if ctx is None or when is None or count <= 0 or not ctx.power or not ctx.state:
            return None
        name = str(entry.get("Type_Localised") or entry.get("Type") or "").strip()
        key = _norm(entry.get("Type"))
        return Sale(
            time=str(entry.get("timestamp")), commander=self.commander, power=ctx.power, system=ctx.system, station=self._station,
            state=ctx.state, holder=ctx.holder, activity=ctx.activity, rank=ctx.rank, commodity=name, tons=count,
            sell_price=_int(entry.get("SellPrice")), avg_paid=_int(entry.get("AvgPricePaid")), total_sale=_int(entry.get("TotalSale")),
            bought_in=self._bought_in.get(key, ""), mined=key in self._mined,
            black_market=bool(entry.get("BlackMarket") or entry.get("IllegalGoods") or entry.get("StolenGoods")),
        )


class SaleLog:
    """The CSV file. Thread safe, and a sale already in it is never written twice. New sales are appended. A file written before the rank and cycle
    columns existed is rewritten once with them (the cycle comes from the sale's time; the rank is left blank until a journal rescan fills it in),
    and a later rescan fills a blank rank in place."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._lock = threading.Lock()
        self._rows: Optional[Dict[Tuple[str, str, str, int, int], Dict[str, str]]] = None
        self._latest: Dict[str, str] = {}
        self._old_header = False

    @staticmethod
    def _key_of(row: Dict[str, str]) -> Tuple[str, str, str, int, int]:
        return ((row.get("commander") or "").casefold(), row.get("time") or "", (row.get("commodity") or "").casefold(),
                _int(row.get("tons")), _int(row.get("total_sale")))

    def latest(self, commander: str) -> str:
        """The timestamp of the newest sale logged for `commander` (case ignored), or "" when there is none."""
        with self._lock:
            self._load()
            return self._latest.get(commander.strip().casefold(), "")

    def missing_rank(self, commander: str) -> bool:
        """Whether a row of `commander` has a blank rank (written before the column existed), so a full journal read would fill it in."""
        with self._lock:
            who = commander.strip().casefold()
            return any(not row.get("rank") for key, row in self._load().items() if key[0] == who)

    def settle_rank(self, commander: str) -> None:
        """After a full read: a rank that is still blank is not in the journals; mark it unknown so it is not looked for again."""
        with self._lock:
            who = commander.strip().casefold()
            blank = [row for key, row in self._load().items() if key[0] == who and not row.get("rank")]
            if blank:
                for row in blank:
                    row["rank"] = UNKNOWN_RANK
                self._rewrite()

    def _load(self) -> Dict[Tuple[str, str, str, int, int], Dict[str, str]]:
        if self._rows is None:
            rows: Dict[Tuple[str, str, str, int, int], Dict[str, str]] = {}
            try:
                with open(self.path, newline="", encoding="utf-8") as handle:
                    reader = csv.DictReader(handle)
                    self._old_header = bool(reader.fieldnames) and tuple(reader.fieldnames) != COLUMNS
                    for row in reader:
                        row = {name: row.get(name) or "" for name in COLUMNS}
                        if not row["cycle"]:
                            cycle = cycle_of(row["time"])
                            row["cycle"] = "" if cycle is None else str(cycle)
                        rows[self._key_of(row)] = row
                        who = row["commander"].casefold()
                        if row["time"] > self._latest.get(who, ""):
                            self._latest[who] = row["time"]
            except OSError:
                pass
            self._rows = rows
        return self._rows

    def _rewrite(self) -> bool:
        """The whole file from memory, through a temporary file, so a failure leaves the old file as it was."""
        rows = self._load()
        temporary = self.path + ".tmp"
        try:
            with open(temporary, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle, lineterminator="\n")
                writer.writerow(COLUMNS)
                for row in rows.values():
                    writer.writerow([row.get(name, "") for name in COLUMNS])
            os.replace(temporary, self.path)
        except OSError:
            return False
        self._old_header = False
        return True

    def add(self, sales: Iterable[Sale]) -> int:
        """Append the sales not yet in the file (and fill a blank rank of one that is); returns how many were new. A file that cannot be written leaves the log as it was."""
        with self._lock:
            rows = self._load()
            new: List[Sale] = []
            filled = False
            seen: Set[Tuple[str, str, str, int, int]] = set()
            for sale in sales:
                if sale.key in seen:
                    continue
                seen.add(sale.key)
                existing = rows.get(sale.key)
                if existing is None:
                    new.append(sale)
                elif not existing.get("rank") and sale.rank is not None:
                    existing["rank"] = sale.rank_text
                    filled = True
            if not new and not filled and not self._old_header:
                return 0
            added = {sale.key: dict(zip(COLUMNS, [str(cell) for cell in sale.row()])) for sale in new}
            if filled or self._old_header or not os.path.exists(self.path) or os.path.getsize(self.path) == 0:
                snapshot = dict(rows)
                rows.update(added)
                if not self._rewrite():
                    rows.clear()
                    rows.update(snapshot)
                    return 0
            else:
                buffer = io.StringIO()
                writer = csv.writer(buffer, lineterminator="\n")
                for sale in new:
                    writer.writerow(sale.row())
                try:
                    with open(self.path, "a", newline="", encoding="utf-8") as handle:
                        handle.write(buffer.getvalue())
                except OSError:
                    return 0
                rows.update(added)
            for sale in new:
                if sale.time > self._latest.get(sale.commander.casefold(), ""):
                    self._latest[sale.commander.casefold()] = sale.time
            return len(new)


# --- replaying journals ---------------------------------------------------------------------------------

_PLEDGE_EVENTS = ("Powerplay", "PowerplayJoin", "PowerplayLeave", "PowerplayDefect")
_CONTEXT_EVENTS = ("Location", "FSDJump", "CarrierJump", "Docked")
_DELIVERY_EVENTS = ("PowerplayDeliver", "SearchAndRescue", "DeliverPowerMicroResources")
SALE_EVENTS = (
    "Fileheader", "Commander", "LoadGame", "Location", "FSDJump", "CarrierJump", "Docked", "Undocked", "SupercruiseEntry", "MarketBuy",
    "MarketSell", "MiningRefined", "PowerplayMerits", "PowerplayRank", *_PLEDGE_EVENTS, *_DELIVERY_EVENTS,
)
DELIVERY = "delivery"   # formulas.DELIVERY
NEEDLES = tuple(f'"{name}"' for name in SALE_EVENTS)


def context_of(tracker: Any, system: Optional[str]) -> Optional[Context]:
    """The Powerplay tracker's view of `system`, or None when it has none (not pledged, or no Powerplay state there)."""
    if not tracker.my_power or not system or tracker.system_name != system or not tracker.system_state:
        return None
    rank = tracker.rank if isinstance(tracker.rank, int) and not isinstance(tracker.rank, bool) else None
    return Context(power=tracker.my_power, system=system, state=str(tracker.system_state),
                   holder=str(tracker.system_controller or ""), activity=str(tracker.system_activity(system)), rank=rank)


def replay_sales(entries: Iterable[Dict[str, Any]], cmdr: str, tracker_factory: Callable[[], Any]) -> List[Sale]:
    """The sales of `cmdr` in the entries of ONE journal file, in order. Uses the same Powerplay tracker as the live feed, so a merit event
    that a hand-in claims is not taken by a sale, and the system state is the one the commander was in."""
    wanted = cmdr.strip().casefold()
    tracker = tracker_factory()
    sales = SaleTracker(cmdr.strip())
    current = ""
    system: Optional[str] = None
    found: List[Sale] = []
    for entry in entries:
        event = entry.get("event")
        if event == "Fileheader":
            found += sales.flush()
            tracker, current, system = tracker_factory(), "", None
            sales = SaleTracker(cmdr.strip())
            continue
        if event in ("Commander", "LoadGame"):
            name = str(entry.get("Name" if event == "Commander" else "Commander", "")).strip().casefold()
            if name and name != current:
                found += sales.flush()
                tracker, current, system = tracker_factory(), name, None
                sales = SaleTracker(cmdr.strip())
            continue
        if current != wanted:
            continue
        star_system = entry.get("StarSystem")
        if star_system:
            system = str(star_system)
        if tracker.apply_pledge_event(event, entry):
            pass
        elif event == "PowerplayRank":
            tracker.apply_rank(entry)
        elif event in _DELIVERY_EVENTS:
            tracker.apply_delivery_signal(event, entry)
        elif event == "PowerplayMerits":
            gained = tracker.apply_merits(entry)
            activity = tracker.classify_current_activity(system)
            found += sales.merit(entry, gained, delivery=activity == DELIVERY)
            continue
        if event in _CONTEXT_EVENTS:
            tracker.apply_system_context(system, entry)
        found += sales.feed(entry, lambda: context_of(tracker, system))
    found += sales.flush()
    return found


YIELD_EVERY = 1500
"""Lines read between short sleeps, so the scan on its worker thread never starves EDMC's window of the interpreter."""


def _file_entries(path: str) -> Iterable[Dict[str, Any]]:
    import json
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        return
    if '"MarketSell"' not in text:      # a file with no sale has nothing to give, and most files have none
        return
    for count, line in enumerate(text.splitlines()):
        if count % YIELD_EVERY == YIELD_EVERY - 1:
            time.sleep(0.002)
        if not any(needle in line for needle in NEEDLES):
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict):
            yield entry


def scan_journals(folder: str, cmdr: str, tracker_factory: Callable[[], Any],
                  progress: Optional[Callable[[int, int], None]] = None, since: Optional[datetime] = None) -> List[Sale]:
    """Every sale of `cmdr` in the Journal*.log files of `folder`, oldest file first. An unreadable folder gives an empty list.
    With `since`, files last written before it are skipped. `progress(done, total)` is called after each file. Safe on a worker thread."""
    root = os.path.expanduser(folder)
    try:
        names = sorted(name for name in os.listdir(root) if name.startswith("Journal") and name.endswith(".log"))
    except OSError:
        return []
    if since is not None:
        cutoff = since.timestamp()

        def written_since(name: str) -> bool:
            try:
                return os.path.getmtime(os.path.join(root, name)) >= cutoff
            except OSError:      # a file that vanished or cannot be read must not stop the scan: keep it, and the read skips it
                return True
        names = [name for name in names if written_since(name)]
    found: List[Sale] = []
    for index, name in enumerate(names, 1):
        before = len(found)
        try:
            found += replay_sales(_file_entries(os.path.join(root, name)), cmdr, tracker_factory)
        except Exception:        # one odd file must not stop the rest
            pass
        if len(found) > before or index % 25 == 0:
            time.sleep(0.003)   # let EDMC's window have the interpreter after real work, and now and then while skipping files
        if progress is not None:
            progress(index, len(names))
    return found
