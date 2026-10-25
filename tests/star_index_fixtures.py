"""A small stand-in for a Spansh systems dump, in the real record shape, for the star index tests and benchmark (not a test itself).

`make_dump` writes a gzip file holding a JSON array with one system on each line: neutron stars (most), black holes and other main stars (which the builder must skip), names with the
procedural shape ("Eol Prou RS-T d3-94", "Pyroomoa AA-A h0") and a few that do not have it. Positions are multiples of 1/32 ly, as in the real data. `Star` is what was written, so a test can
compare a query with a brute-force search.
"""
from __future__ import annotations

import gzip
import json
import random
from typing import List, NamedTuple, Tuple

SECTORS = ["Pyroomoa", "Eol Prou", "Dryaea Brau", "Slaulue", "Kyloae Ploe", "Col 285", "Blaa Hypai", "Praea Euq", "Schee Ploea", "HIP 8887"]
UPDATED = "2026-07-29T00:01:14Z"
OTHER_STARS = ["Black Hole", "B (Blue-White) Star", "O (Blue-White) Star", "White Dwarf (DA) Star"]


class Star(NamedTuple):
    id64: int
    name: str
    x: float
    y: float
    z: float


def _units(rng: random.Random, spread: float) -> float:
    return rng.randint(int(-spread * 32), int(spread * 32)) / 32.0


def make_stars(count: int, seed: int = 1, spread: float = 3000.0, flat: float = 400.0, odd_every: int = 97) -> List[Star]:
    rng = random.Random(seed)
    stars: List[Star] = []
    used = set()
    while len(stars) < count:
        id64 = rng.randint(1, 1 << 55)
        if id64 in used:
            continue
        used.add(id64)
        index = len(stars)
        if odd_every and index % odd_every == 0:
            name = f"Odd Name {index}"
        else:
            letters = "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(3))
            mass = rng.choice("abcdefgh")
            n2 = rng.randint(0, 3000)
            n1 = rng.choice((-1, -1, 0, 1, 2, 5, 12))
            tail = f"{letters[:2]}-{letters[2]} {mass}" + (f"{n1}-{n2}" if n1 >= 0 else f"{n2}")
            name = f"{rng.choice(SECTORS)} {tail}"
        stars.append(Star(id64, name, _units(rng, spread), _units(rng, flat), _units(rng, spread)))
    return stars


def write_dump(path: str, stars: List[Star], extras: int = 0, seed: int = 2, updated: str = UPDATED) -> None:
    """Writes `stars` (neutron stars) and `extras` systems with other main stars, mixed in id64 order, as a gzip file in the dump's layout."""
    rng = random.Random(seed)
    rows: List[Tuple[int, str]] = []
    for star in stars:
        rows.append((star.id64, _line(star.id64, star.name, "Neutron Star", star.x, star.y, star.z, updated)))
    for index in range(extras):
        id64 = rng.randint(1, 1 << 55)
        rows.append((id64, _line(id64, f"Other {index}", rng.choice(OTHER_STARS), _units(rng, 3000), _units(rng, 400), _units(rng, 3000), updated)))
    rows.sort()
    _write_rows(path, rows)


def write_update(path: str, neutron: List[Star], no_longer_neutron: List[Star] = (), others: int = 0, oldest: str = "2026-10-20T00:00:03Z", newest: str = "2026-10-20T22:00:00Z",
                 seed: int = 5) -> None:
    """Writes an update file in the layout of Spansh's `systems_1day.json.gz`: the systems changed since a past midnight, whatever their main star. `neutron` are neutron stars (new, moved
    or renamed ones); `no_longer_neutron` are systems whose main star is now something else; `others` more systems that are not neutron stars. The oldest change is `oldest`."""
    rng = random.Random(seed)
    newest = max(newest, oldest)
    rows: List[Tuple[int, str]] = []
    for star in neutron:
        rows.append((star.id64, _line(star.id64, star.name, "Neutron Star", star.x, star.y, star.z, newest)))
    for star in no_longer_neutron:
        rows.append((star.id64, _line(star.id64, star.name, "Black Hole", star.x, star.y, star.z, newest)))
    for index in range(others):
        id64 = rng.randint(1, 1 << 55)
        rows.append((id64, _line(id64, f"Changed {index}", rng.choice(OTHER_STARS), _units(rng, 3000), _units(rng, 400), _units(rng, 3000), newest)))
    rows.append((1, _line(1, "Oldest Change", "M (Red dwarf) Star", 0.0, 0.0, 0.0, oldest)))        # the file's oldest change, on a system that is not a neutron star
    rows.sort()
    _write_rows(path, rows)


def _write_rows(path: str, rows: List[Tuple[int, str]]) -> None:
    with gzip.open(path, "wb", compresslevel=1) as out:
        out.write(b"[\n")
        for number, (_id, line) in enumerate(rows):
            out.write(b"\t" + line.encode("utf-8") + (b",\n" if number + 1 < len(rows) else b"\n"))
        out.write(b"]\n")


def _line(id64: int, name: str, main: str, x: float, y: float, z: float, updated: str = UPDATED) -> str:
    return ('{"id64":%d,"name":%s,"mainStar":"%s","coords":{"x":%s,"y":%s,"z":%s},"updateTime":"%s"}'
            % (id64, json.dumps(name), main, repr(x), repr(y), repr(z), updated))


def brute_nearest(stars: List[Star], x: float, y: float, z: float, count: int) -> List[Tuple[float, int]]:
    """(distance, id64) of the `count` nearest, nearest first, found by looking at every star."""
    found = sorted(((x - s.x) ** 2 + (y - s.y) ** 2 + (z - s.z) ** 2, s.id64) for s in stars)[:count]
    return [(d2 ** 0.5, id64) for d2, id64 in found]
