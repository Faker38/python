# Flask Tic-Tac-Toe Game

A minimal Flask-based game website featuring a browser-played Tic-Tac-Toe with recent scores stored in SQLite.

## Run locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000

## Endpoints

- GET `/` – Game page
- GET `/api/scores` – List recent scores
- POST `/api/scores` – Create a score `{player, result: win|lose|draw, moves, duration_ms}`

## Notes

- Database file: `game.db` will be created next to `app.py`.
- For production, run behind a WSGI server (e.g., gunicorn) and set `FLASK_ENV` / `PORT` appropriately.
