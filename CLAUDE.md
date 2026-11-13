# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```
pip install -r requirements.txt
python -m uvicorn main:app --reload      # dev server on http://127.0.0.1:8000
```

There is no test suite, linter, or build step. `starlette.testclient` needs `httpx2`, which is not in `requirements.txt` and was blocked from being installed; to smoke-test, run the server and hit routes with `curl`.

## Architecture

Server-rendered catalog of Drain Gang songs: FastAPI + Jinja2 templates + raw `sqlite3` (no ORM). No JS framework; the only client script is an inline `confirm()` on the delete form.

- `main.py` — all routes. Pages: `/` (list, `?q=` searches title/artist/genre via `LIKE`), `/songs/{id}` (view), `/songs/new` and `/songs/{id}/edit` (the same `templates/form.html`; the template switches on whether `song` is `None`). `POST .../delete` removes a song. Every write ends in a `303` redirect (POST/redirect/GET).
- `db.py` — `get_conn()` (sets `row_factory = sqlite3.Row`, so templates use `song.title` attribute access) and `init_db()`, which creates the `songs` table and seeds three sample songs only when the table is empty. It runs from the FastAPI `lifespan` handler.
- `songs.db` — SQLite file created next to `main.py` on first run (path is relative to `db.py`, not the CWD). Delete it to reset to the seed data.
- `templates/` — `base.html` (header with search box, footer) is extended by `index.html`, `song.html`, `form.html`.
- `static/css/style.css` — the whole design (dark theme driven by CSS variables in `:root`), mounted at `/static`.

## Gotchas

- Connections are short-lived: open with `with closing(get_conn()) as conn, conn:` (`closing` closes it; `with conn` commits). `with sqlite3.connect(...)` alone does not close the connection, which locks `songs.db` on Windows.
- The `year` form field is taken as `str` and converted manually: an empty value would fail `int` validation (422) in FastAPI.
- UI text is in Russian.
