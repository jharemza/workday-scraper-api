# app/main.py

from app.db import init_db
import logging
from logging.handlers import RotatingFileHandler
import os
import app.config as config

# --- Logging Setup ---

# Ensure log directory exists
os.makedirs("logs", exist_ok=True)

# Define log format
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
DATE_FMT  = "%Y-%m-%d %H:%M:%S"

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(config.LOG_LEVEL)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(config.LOG_LEVEL)
ch.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FMT))
root_logger.addHandler(ch)

# Rotating file handler (10 MB per file, keep 5 backups)
fh = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
fh.setLevel(config.LOG_LEVEL)
fh.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FMT))
root_logger.addHandler(fh)

from flask import Flask
from app.routes import jobs_bp

def create_app():
    app = Flask(__name__)

    init_db() # ensure table exists
    app.register_blueprint(jobs_bp)

    #–– HTTP exceptions (400, 404, etc) ––
    from werkzeug.exceptions import HTTPException
    from flask import jsonify, current_app

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        current_app.logger.warning(f"HTTP error {e.code}: {e.description}")
        return jsonify({
            "error": e.name,
            "message": e.description
        }), e.code

    #–– All other uncaught exceptions ––
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        current_app.logger.exception("Unhandled exception")
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred."
        }), 500

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
