# app/main.py

from app.db import init_db

from flask import Flask
from app.routes import jobs_bp

def create_app():
    app = Flask(__name__)
    init_db() # ensure table exists
    app.register_blueprint(jobs_bp)
    return app

if __name__ == "__main__":
    create_app().run(debug=True)
