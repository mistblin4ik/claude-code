# Drain Gang Catalog

Серверный каталог песен Drain Gang: FastAPI + Jinja2 + SQLite (без ORM).

## Возможности
- Список песен с поиском по названию, исполнителю и жанру
- Просмотр, добавление, редактирование и удаление песен

## Запуск
```
pip install -r requirements.txt
python -m uvicorn main:app --reload
```
Сервер: http://127.0.0.1:8000

База `songs.db` создаётся автоматически при первом запуске с тремя тестовыми песнями.

## Структура
- `main.py` — маршруты
- `db.py` — работа с SQLite
- `templates/` — Jinja2-шаблоны
- `static/css/style.css` — стили
