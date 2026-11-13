from contextlib import asynccontextmanager, closing
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import get_conn, init_db

BASE = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Drain Gang", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


def get_song_or_404(song_id: int):
    with closing(get_conn()) as conn:
        song = conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()
    if song is None:
        raise HTTPException(status_code=404, detail="Песня не найдена")
    return song


@app.get("/", response_class=HTMLResponse)
def index(request: Request, q: str = ""):
    with closing(get_conn()) as conn:
        if q:
            like = f"%{q}%"
            songs = conn.execute(
                "SELECT * FROM songs WHERE title LIKE ? OR artist LIKE ? OR genre LIKE ? ORDER BY id DESC",
                (like, like, like),
            ).fetchall()
        else:
            songs = conn.execute("SELECT * FROM songs ORDER BY id DESC").fetchall()
    return templates.TemplateResponse(request, "index.html", {"songs": songs, "q": q})


templates.env.filters["spaced"] = lambda n: f"{int(n):,}".replace(",", " ")


@app.get("/popular", response_class=HTMLResponse)
def popular(request: Request):
    with closing(get_conn()) as conn:
        tracks = conn.execute("SELECT * FROM popular_tracks ORDER BY streams DESC").fetchall()
    return templates.TemplateResponse(request, "popular.html", {"tracks": tracks})


@app.get("/songs/new", response_class=HTMLResponse)
def new_song_form(request: Request):
    return templates.TemplateResponse(request, "form.html", {"song": None})


@app.post("/songs/new")
def create_song(
    title: str = Form(...),
    artist: str = Form(...),
    year: str = Form(""),
    genre: str = Form(""),
    rating: int = Form(0),
    cover_url: str = Form(""),
    description: str = Form(""),
):
    year_val = int(year) if year.strip().isdigit() else None
    with closing(get_conn()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO songs (title, artist, year, genre, rating, cover_url, description) VALUES (?,?,?,?,?,?,?)",
            (title, artist, year_val, genre, rating, cover_url, description),
        )
        song_id = cur.lastrowid
    return RedirectResponse(f"/songs/{song_id}", status_code=303)


@app.get("/songs/{song_id}", response_class=HTMLResponse)
def view_song(request: Request, song_id: int):
    return templates.TemplateResponse(request, "song.html", {"song": get_song_or_404(song_id)})


@app.get("/songs/{song_id}/edit", response_class=HTMLResponse)
def edit_song_form(request: Request, song_id: int):
    return templates.TemplateResponse(request, "form.html", {"song": get_song_or_404(song_id)})


@app.post("/songs/{song_id}/edit")
def update_song(
    song_id: int,
    title: str = Form(...),
    artist: str = Form(...),
    year: str = Form(""),
    genre: str = Form(""),
    rating: int = Form(0),
    cover_url: str = Form(""),
    description: str = Form(""),
):
    get_song_or_404(song_id)
    year_val = int(year) if year.strip().isdigit() else None
    with closing(get_conn()) as conn, conn:
        conn.execute(
            "UPDATE songs SET title=?, artist=?, year=?, genre=?, rating=?, cover_url=?, description=? WHERE id=?",
            (title, artist, year_val, genre, rating, cover_url, description, song_id),
        )
    return RedirectResponse(f"/songs/{song_id}", status_code=303)


@app.post("/songs/{song_id}/delete")
def delete_song(song_id: int):
    with closing(get_conn()) as conn, conn:
        conn.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    return RedirectResponse("/", status_code=303)
