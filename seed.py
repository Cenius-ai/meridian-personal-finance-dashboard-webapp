"""Seed entrypoint for the four-phase runner.

Regenerates the deterministic demo CSV (idempotent) and then EXITS. This must
never start the HTTP server — the seed phase holds no ports.
"""

from data.generator import main

if __name__ == "__main__":
    main()
