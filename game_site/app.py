import os
import sqlite3
from typing import Optional

from flask import Flask, jsonify, request, g, render_template


DATABASE_FILENAME = "game.db"


def get_database_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DATABASE_FILENAME)


def get_db() -> sqlite3.Connection:
    if "db_conn" not in g:
        db_path = get_database_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        g.db_conn = conn
    return g.db_conn  # type: ignore[attr-defined]


def close_db(_: Optional[BaseException] = None) -> None:
    conn: Optional[sqlite3.Connection] = g.pop("db_conn", None)  # type: ignore[attr-defined]
    if conn is not None:
        conn.close()


def init_db() -> None:
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL,
            result TEXT NOT NULL CHECK(result IN ('win','lose','draw')),
            moves INTEGER NOT NULL,
            duration_ms INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    @app.before_request
    def _before_request() -> None:
        # Ensure database is initialized before handling requests
        init_db()

    @app.teardown_appcontext
    def _teardown(exception: Optional[BaseException]) -> None:  # noqa: ARG001
        close_db()

    @app.get("/")
    def index():  # type: ignore[no-redef]
        return render_template("index.html")

    @app.get("/healthz")
    def healthz():  # type: ignore[no-redef]
        return jsonify({"status": "ok"})

    @app.get("/api/scores")
    def list_scores():  # type: ignore[no-redef]
        conn = get_db()
        rows = conn.execute(
            "SELECT id, player, result, moves, duration_ms, created_at FROM scores ORDER BY created_at DESC, id DESC LIMIT 20"
        ).fetchall()
        data = [
            {
                "id": row["id"],
                "player": row["player"],
                "result": row["result"],
                "moves": row["moves"],
                "duration_ms": row["duration_ms"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
        return jsonify({"scores": data})

    @app.post("/api/scores")
    def create_score():  # type: ignore[no-redef]
        payload = request.get_json(silent=True) or {}
        player = str(payload.get("player", "Player")).strip() or "Player"
        result = str(payload.get("result", "draw")).strip().lower()
        moves = int(payload.get("moves", 0))
        duration_ms = int(payload.get("duration_ms", 0))

        if result not in {"win", "lose", "draw"}:
            return jsonify({"error": "invalid result"}), 400
        if moves < 0 or duration_ms < 0:
            return jsonify({"error": "invalid metrics"}), 400

        conn = get_db()
        cur = conn.execute(
            "INSERT INTO scores (player, result, moves, duration_ms) VALUES (?, ?, ?, ?)",
            (player, result, moves, duration_ms),
        )
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({"id": new_id}), 201

    return app


app = create_app()


if __name__ == "__main__":
    # Bind to all interfaces to work in containerized/dev environments
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)

