# app/main.py

from app.db import init_db
import logging
from logging.handlers import RotatingFileHandler
import os
import app.config as config
from flask import Flask
from app.routes import jobs_bp

# --- Logging Setup ---

log_dir = os.path.dirname(config.LOG_FILE_PATH) or "."
os.makedirs(log_dir, exist_ok=True)

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

root_logger = logging.getLogger()
root_logger.setLevel(config.LOG_LEVEL)

ch = logging.StreamHandler()
ch.setLevel(config.LOG_LEVEL)
ch.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FMT))
root_logger.addHandler(ch)

fh = RotatingFileHandler(
    config.LOG_FILE_PATH,
    maxBytes=config.LOG_MAX_BYTES,
    backupCount=config.LOG_BACKUP_COUNT,
    encoding="utf-8",
)
fh.setLevel(config.LOG_LEVEL)
fh.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FMT))
root_logger.addHandler(fh)


def create_app():
    app = Flask(__name__)

    init_db()  # ensure table exists
    app.register_blueprint(jobs_bp)

    from werkzeug.exceptions import HTTPException
    from flask import jsonify, current_app

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        current_app.logger.warning(f"HTTP error {e.code}: {e.description}")
        return jsonify({"error": e.name, "message": e.description}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        current_app.logger.exception("Unhandled exception")
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                }
            ),
            500,
        )

    return app


if __name__ == "__main__":
    create_app().run(debug=config.APP_DEBUG)
