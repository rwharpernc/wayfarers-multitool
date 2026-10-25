"""Manual benchmark for the local star index (not run by the test suite).

Makes a synthetic dump of N neutron stars (default 1,000,000, spread through a disc about 60,000 ly across so the density is like the real data's), builds the index from it, and reports
the build time, the file size and the time of nearest-star queries at several distances. Run it as `python tests/star_index_bench.py [N] [folder]`; the folder (default: a new temporary
one) is where the dump and the index are written, and they are left there. N = 5000000 matches the real dump (it takes a few minutes and about 1 GB of disk).
"""
from __future__ import annotations

import os
import random
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugin import star_index, star_index_build   # noqa: E402
import star_index_fixtures as fixtures            # noqa: E402


def main() -> None:
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    folder = sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp(prefix="wfmt-star-bench-")
    os.makedirs(folder, exist_ok=True)
    dump = os.path.join(folder, "dump.json.gz")
    began = time.time()
    stars = fixtures.make_stars(count, seed=7, spread=30000.0, flat=800.0, odd_every=5000)
    fixtures.write_dump(dump, stars, extras=count // 10)
    print(f"made a dump of {count:,} neutron stars: {os.path.getsize(dump) / 1e6:.1f} MB gzip, {time.time() - began:.0f} s")
    result = star_index_build.build(dump, os.path.join(folder, "index"), {"url": "synthetic"},
                                    progress=lambda fraction, text: print(f"\r{fraction * 100:5.1f}%  {text}", end="", flush=True))
    print()
    print(f"built {result.count:,} records in {result.seconds:.1f} s, {result.size_bytes / 1e6:.1f} MB ({result.size_bytes / max(1, result.count):.1f} bytes each)")
    index = star_index.StarIndex(star_index.index_path(os.path.join(folder, "index")))
    rng = random.Random(3)
    for radius_note, max_radius in (("nearest 2, any distance up to 5000 ly", 5000.0), ("nearest 25 within 1000 ly", 1000.0)):
        wanted = 2 if max_radius > 1000 else 25
        timings = []
        for _ in range(200):
            star = stars[rng.randrange(len(stars))]
            began = time.perf_counter()
            index.nearest(star.x + 3.3, star.y - 1.1, star.z + 7.7, wanted, max_radius)
            timings.append(time.perf_counter() - began)
        timings.sort()
        print(f"{radius_note}: median {timings[100] * 1000:.1f} ms, worst of 200 {timings[-1] * 1000:.1f} ms")
    print(f"files are in {folder}")


if __name__ == "__main__":
    main()
