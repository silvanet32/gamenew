import os
import sqlite3
from datetime import datetime

import requests
from functools import wraps

from flask import (
    Flask,
    Response,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
    send_from_directory,
)
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-me")

    init_db()

    def get_db() -> sqlite3.Connection:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def login_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get("user_id"):
                flash("Faça login para continuar.", "warning")
                return redirect(url_for("auth"))
            return fn(*args, **kwargs)

        return wrapper

    def admin_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get("is_admin"):
                abort(403)
            return fn(*args, **kwargs)

        return wrapper


    def detect_video_kind(url: str) -> str:
        value = (url or "").strip().lower()
        if not value:
            return "none"
        if "youtube.com/watch" in value or "youtu.be/" in value:
            return "youtube"
        if "drive.google.com/file/d/" in value:
            return "drive"
        if value.endswith('.mp4'):
            return "mp4"
        return "external"

    def to_embed_url(url: str) -> str:
        value = (url or "").strip()
        if "youtube.com/watch" in value and "v=" in value:
            video_id = value.split('v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        if "youtu.be/" in value:
            video_id = value.split('youtu.be/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        if "drive.google.com/file/d/" in value:
            file_id = value.split('/file/d/')[1].split('/')[0]
            return f"https://drive.google.com/file/d/{file_id}/preview"
        return value

    @app.context_processor
    def inject_user():
        return {
            "current_user": {
                "id": session.get("user_id"),
                "username": session.get("username"),
                "is_admin": session.get("is_admin", False),
            }
        }

    @app.get("/")
    def index():
        if session.get("user_id"):
            return redirect(url_for("home"))
        return redirect(url_for("auth"))

    @app.route("/auth", methods=["GET", "POST"])
    def auth():
        conn = get_db()
        c = conn.cursor()

        if request.method == "POST":
            action = request.form.get("action")

            if action == "login":
                email = request.form.get("email", "").strip().lower()
                password = request.form.get("password", "")

                user = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
                if user and check_password_hash(user["password_hash"], password):
                    session["user_id"] = user["id"]
                    session["username"] = user["username"]
                    session["is_admin"] = int(user["is_admin"]) == 1
                    flash("Você logou na conta.", "success")
                    conn.close()
                    return redirect(url_for("home"))

                flash("Email ou senha inválidos.", "danger")

            elif action == "register":
                username = request.form.get("username", "").strip()
                email = request.form.get("email", "").strip().lower()
                password = request.form.get("password", "")

                if len(username) < 3:
                    flash("Seu nome precisa ter pelo menos 3 caracteres.", "warning")
                elif len(password) < 6:
                    flash("Sua senha precisa ter pelo menos 6 caracteres.", "warning")
                elif not email:
                    flash("Email é obrigatório.", "warning")
                else:
                    exists = c.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone()
                    if exists:
                        flash("Esse email já está cadastrado.", "warning")
                    else:
                        c.execute(
                            "INSERT INTO users (username, email, password_hash, is_admin) VALUES (?,?,?,?)",
                            (username, email, generate_password_hash(password), 0),
                        )
                        conn.commit()
                        flash("Conta criada! Agora faça login.", "success")
            else:
                flash("Ação inválida.", "warning")

        conn.close()
        return render_template("auth.html")

    @app.get("/logout")
    def logout():
        session.clear()
        flash("Você saiu da conta.", "info")
        return redirect(url_for("auth"))

    @app.get("/home")
    @login_required
    def home():
        q = request.args.get("q", "").strip()
        conn = get_db()

        if q:
            like = f"%{q}%"
            rows = conn.execute(
                """
                SELECT id, title, description, cover_url, views, created_at
                FROM series
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY created_at DESC
                """,
                (like, like),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, title, description, cover_url, views, created_at
                FROM series
                ORDER BY created_at DESC
                """
            ).fetchall()

        methods = conn.execute(
            "SELECT id, name, payment_key FROM donation_methods WHERE is_active=1 ORDER BY id DESC"
        ).fetchall()
        conn.close()
        return render_template("home.html", series=rows, q=q, donation_methods=methods)

    @app.get("/serie/<int:series_id>")
    @login_required
    def serie_detail(series_id: int):
        user_id = int(session["user_id"])
        conn = get_db()
        c = conn.cursor()

        s = c.execute("SELECT * FROM series WHERE id=?", (series_id,)).fetchone()
        if not s:
            conn.close()
            abort(404)

        already = c.execute(
            "SELECT 1 FROM series_views WHERE user_id=? AND series_id=?",
            (user_id, series_id),
        ).fetchone()

        if not already:
            c.execute(
                "INSERT INTO series_views (user_id, series_id, created_at) VALUES (?,?,?)",
                (user_id, series_id, datetime.utcnow().isoformat()),
            )
            c.execute("UPDATE series SET views = views + 1 WHERE id=?", (series_id,))
            conn.commit()

        s = c.execute("SELECT * FROM series WHERE id=?", (series_id,)).fetchone()
        like_count = c.execute("SELECT COUNT(*) FROM series_likes WHERE series_id=?", (series_id,)).fetchone()[0]
        comments = c.execute(
            """
            SELECT c.comment, c.created_at, u.username
            FROM series_comments c
            JOIN users u ON u.id = c.user_id
            WHERE c.series_id=?
            ORDER BY c.id DESC
            """,
            (series_id,),
        ).fetchall()
        conn.close()

        return render_template("serie_detail.html", s=s, like_count=like_count, comments=comments)



    @app.get("/assistir/<int:series_id>")
    @login_required
    def watch_internal(series_id: int):
        conn = get_db()
        s = conn.execute("SELECT id, title, video_url FROM series WHERE id=?", (series_id,)).fetchone()
        conn.close()
        if not s:
            abort(404)

        kind = detect_video_kind(s["video_url"] or "")
        embed_url = None
        stream_url = None

        if kind in ("youtube", "drive"):
            embed_url = to_embed_url(s["video_url"])
        elif kind in ("mp4", "external"):
            stream_url = url_for("stream_internal", series_id=series_id)

        if not embed_url and not stream_url:
            flash("Essa série não possui vídeo configurado.", "warning")
            return redirect(url_for("serie_detail", series_id=series_id))

        return render_template(
            "watch_internal.html",
            title=s["title"],
            kind=kind,
            embed_url=embed_url,
            stream_url=stream_url,
            series_id=series_id,
        )


    @app.get("/stream/<int:series_id>")
    @login_required
    def stream_internal(series_id: int):
        conn = get_db()
        s = conn.execute("SELECT video_url FROM series WHERE id=?", (series_id,)).fetchone()
        conn.close()
        if not s or not s["video_url"]:
            return "Vídeo não encontrado.", 404

        upstream = (s["video_url"] or "").strip()
        headers = {}
        if request.headers.get("Range"):
            headers["Range"] = request.headers["Range"]

        try:
            resp = requests.get(upstream, stream=True, headers=headers, timeout=20)
        except Exception:
            return "Não foi possível carregar o vídeo.", 502

        allowed_headers = {}
        for key in ["Content-Type", "Content-Range", "Accept-Ranges", "Content-Length"]:
            if key in resp.headers:
                allowed_headers[key] = resp.headers[key]

        allowed_headers["Cache-Control"] = "no-store"
        allowed_headers["Pragma"] = "no-cache"
        allowed_headers["Content-Disposition"] = "inline"
        allowed_headers["X-Content-Type-Options"] = "nosniff"

        def generate():
            for chunk in resp.iter_content(chunk_size=1024 * 256):
                if chunk:
                    yield chunk

        status = 206 if request.headers.get("Range") and resp.status_code in (200, 206) else resp.status_code
        return Response(generate(), status=status, headers=allowed_headers)

    @app.post("/serie/<int:series_id>/like")
    @login_required
    def toggle_like(series_id: int):
        user_id = int(session["user_id"])
        conn = get_db()
        c = conn.cursor()
        exists = c.execute(
            "SELECT 1 FROM series_likes WHERE user_id=? AND series_id=?", (user_id, series_id)
        ).fetchone()
        if exists:
            c.execute("DELETE FROM series_likes WHERE user_id=? AND series_id=?", (user_id, series_id))
            flash("Like removido.", "info")
        else:
            c.execute(
                "INSERT INTO series_likes (user_id, series_id, created_at) VALUES (?,?,?)",
                (user_id, series_id, datetime.utcnow().isoformat()),
            )
            flash("Você curtiu esta série.", "success")
        conn.commit()
        conn.close()
        return redirect(url_for("serie_detail", series_id=series_id))

    @app.post("/serie/<int:series_id>/comment")
    @login_required
    def add_comment(series_id: int):
        comment = request.form.get("comment", "").strip()
        if not comment:
            flash("Comentário vazio.", "warning")
            return redirect(url_for("serie_detail", series_id=series_id))
        if len(comment) > 500:
            flash("Comentário muito grande (máx 500 caracteres).", "warning")
            return redirect(url_for("serie_detail", series_id=series_id))

        conn = get_db()
        conn.execute(
            "INSERT INTO series_comments (user_id, series_id, comment, created_at) VALUES (?,?,?,?)",
            (int(session["user_id"]), series_id, comment, datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()
        flash("Comentário publicado.", "success")
        return redirect(url_for("serie_detail", series_id=series_id))

    @app.get("/admin")
    @login_required
    @admin_required
    def admin_dashboard():
        return redirect(url_for("admin_manage"))

    @app.route("/admin/series/add", methods=["GET", "POST"])
    @login_required
    @admin_required
    def admin_add_series():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            cover_url = request.form.get("cover_url", "").strip()
            external_link = request.form.get("external_link", "").strip()
            video_url = request.form.get("video_url", "").strip()

            if not title:
                flash("Título é obrigatório.", "warning")
                return redirect(url_for("admin_add_series"))

            conn = get_db()
            conn.execute(
                """
                INSERT INTO series (title, description, cover_url, external_link, video_url, views, created_at)
                VALUES (?,?,?,?,?,?,?)
                """,
                (title, description, cover_url, external_link, video_url, 0, datetime.utcnow().isoformat()),
            )
            conn.commit()
            conn.close()
            flash("Série adicionada com sucesso.", "success")
            return redirect(url_for("admin_manage"))

        return render_template("admin_add_series.html")

    @app.get("/admin/manage")
    @login_required
    @admin_required
    def admin_manage():
        conn = get_db()
        rows = conn.execute(
            "SELECT id, title, description, cover_url, external_link, video_url, views, created_at FROM series ORDER BY id DESC"
        ).fetchall()
        conn.close()
        return render_template("admin_manage.html", rows=rows)

    @app.route("/admin/series/<int:series_id>/edit", methods=["GET", "POST"])
    @login_required
    @admin_required
    def admin_edit_series(series_id: int):
        conn = get_db()
        c = conn.cursor()
        s = c.execute("SELECT * FROM series WHERE id=?", (series_id,)).fetchone()
        if not s:
            conn.close()
            abort(404)

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            cover_url = request.form.get("cover_url", "").strip()
            external_link = request.form.get("external_link", "").strip()
            video_url = request.form.get("video_url", "").strip()
            if not title:
                flash("Título é obrigatório.", "warning")
                conn.close()
                return redirect(url_for("admin_edit_series", series_id=series_id))

            c.execute(
                """
                UPDATE series
                SET title=?, description=?, cover_url=?, external_link=?, video_url=?
                WHERE id=?
                """,
                (title, description, cover_url, external_link, video_url, series_id),
            )
            conn.commit()
            conn.close()
            flash("Série atualizada.", "success")
            return redirect(url_for("admin_manage"))

        conn.close()
        return render_template("admin_edit_series.html", s=s)

    @app.post("/admin/series/<int:series_id>/delete")
    @login_required
    @admin_required
    def admin_delete_series(series_id: int):
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM series_views WHERE series_id=?", (series_id,))
        c.execute("DELETE FROM series_likes WHERE series_id=?", (series_id,))
        c.execute("DELETE FROM series_comments WHERE series_id=?", (series_id,))
        c.execute("DELETE FROM series WHERE id=?", (series_id,))
        conn.commit()
        conn.close()
        flash("Série removida.", "info")
        return redirect(url_for("admin_manage"))

    @app.route("/admin/donation", methods=["GET", "POST"])
    @login_required
    @admin_required
    def admin_donation_panel():
        conn = get_db()
        c = conn.cursor()

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            key = request.form.get("key", "").strip()
            if name and key:
                c.execute(
                    "INSERT INTO donation_methods (name, payment_key, is_active, created_at) VALUES (?,?,?,?)",
                    (name, key, 1, datetime.utcnow().isoformat()),
                )
                conn.commit()
                flash("Método de doação adicionado.", "success")
            else:
                flash("Preencha nome e chave de pagamento.", "warning")

        methods = c.execute("SELECT * FROM donation_methods ORDER BY id DESC").fetchall()
        conn.close()
        return render_template("admin_donation.html", methods=methods)

    @app.get("/admin/donation/toggle/<int:method_id>")
    @login_required
    @admin_required
    def toggle_donation(method_id: int):
        conn = get_db()
        c = conn.cursor()
        m = c.execute("SELECT is_active FROM donation_methods WHERE id=?", (method_id,)).fetchone()
        if m:
            new_status = 0 if m["is_active"] else 1
            c.execute("UPDATE donation_methods SET is_active=? WHERE id=?", (new_status, method_id))
            conn.commit()
            flash("Status da doação atualizado.", "info")
        conn.close()
        return redirect(url_for("admin_donation_panel"))

    @app.get("/admin/stats")
    @login_required
    @admin_required
    def admin_stats():
        conn = get_db()
        c = conn.cursor()
        stats = {
            "users": c.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "series": c.execute("SELECT COUNT(*) FROM series").fetchone()[0],
            "views": c.execute("SELECT COALESCE(SUM(views),0) FROM series").fetchone()[0],
            "likes": c.execute("SELECT COUNT(*) FROM series_likes").fetchone()[0],
            "comments": c.execute("SELECT COUNT(*) FROM series_comments").fetchone()[0],
        }
        conn.close()
        return render_template("admin_stats.html", stats=stats)

    @app.get("/api/admin/series/<int:series_id>")
    @login_required
    @admin_required
    def api_admin_get_series(series_id: int):
        conn = get_db()
        s = conn.execute("SELECT * FROM series WHERE id=?", (series_id,)).fetchone()
        conn.close()
        if not s:
            return jsonify({"error": "Série não encontrada."}), 404
        return jsonify(dict(s))



    @app.get("/app")
    @app.get("/app/<path:asset_path>")
    def frontend_app(asset_path: str = ""):
        if not os.path.isdir(FRONTEND_DIST_DIR):
            flash("Frontend ainda não foi compilado. Execute: npm run build (na pasta frontend).", "warning")
            return redirect(url_for("home") if session.get("user_id") else url_for("auth"))

        if asset_path:
            candidate = os.path.join(FRONTEND_DIST_DIR, asset_path)
            if os.path.isfile(candidate):
                return send_from_directory(FRONTEND_DIST_DIR, asset_path)

        return send_from_directory(FRONTEND_DIST_DIR, "index.html")

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("error.html", code=403, message="Acesso negado."), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", code=404, message="Página não encontrada."), 404

    return app


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            cover_url TEXT,
            external_link TEXT,
            video_url TEXT,
            views INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS series_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            series_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, series_id)
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS series_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            series_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, series_id)
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS series_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            series_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS donation_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            payment_key TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
        """
    )

    admin_email = "admin@gmail.com"
    admin_exists = c.execute("SELECT 1 FROM users WHERE email=?", (admin_email,)).fetchone()
    if not admin_exists:
        c.execute(
            "INSERT INTO users (username, email, password_hash, is_admin) VALUES (?,?,?,?)",
            ("Admin", admin_email, generate_password_hash("admin123"), 1),
        )

    donation_exists = c.execute("SELECT 1 FROM donation_methods LIMIT 1").fetchone()
    if not donation_exists:
        c.execute(
            "INSERT INTO donation_methods (name, payment_key, is_active, created_at) VALUES (?,?,?,?)",
            ("PIX", "sua-chave-pix", 1, datetime.utcnow().isoformat()),
        )

    conn.commit()
    conn.close()


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
