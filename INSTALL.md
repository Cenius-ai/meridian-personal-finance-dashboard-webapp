# Install

The single package manager for this project is **pip** (against the system
Python 3.11). There are no sub-projects — everything lives at the repo root.

## 1. Install dependencies and seed

```bash
bash install.sh
```

`install.sh` performs these steps and then **exits** (it never starts the
server):

1. Upgrades `pip`, `setuptools`, and `wheel`.
2. Installs the pinned dependencies from `requirements.txt`.
3. Regenerates the deterministic demo CSV via `python3 seed.py`.
4. Runs an import self-check.

It is safe to re-run; the seed is idempotent.

## 2. Seed (standalone)

The seed step is also available on its own, and it also exits after writing
the CSV:

```bash
python3 seed.py
```

## 3. Run the app

```bash
python3 app.py
```

The server binds `0.0.0.0` and honours the `PORT` environment variable,
falling back to Dash's conventional port `8050`. Open
<http://localhost:8050> and the root URL redirects to `/overview`.
