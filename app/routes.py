# app/routes.py

from flask import Blueprint, jsonify, request
from app.db import (
    get_all_jobs,
    get_jobs_today,
    get_jobs_by_company,
    get_new_jobs_by_company
)
from app.scraper import run_scrape  # your scraper entry‐point

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")

def row_to_dict(row):
    return { key: row[key] for key in row.keys() }

@jobs_bp.route("/all", methods=["GET"])
def all_jobs():
    rows = get_all_jobs()
    return jsonify([row_to_dict(r) for r in rows])

@jobs_bp.route("/today", methods=["GET"])
def jobs_today():
    rows = get_jobs_today()
    return jsonify([row_to_dict(r) for r in rows])

@jobs_bp.route("/company/<company>", methods=["GET"])
def jobs_company(company):
    rows = get_jobs_by_company(company)
    return jsonify([row_to_dict(r) for r in rows])

@jobs_bp.route("/company/<company>/new", methods=["GET"])
def new_jobs_company(company):
    rows = get_new_jobs_by_company(company)
    return jsonify([row_to_dict(r) for r in rows])

@jobs_bp.route("/scrape", methods=["POST"])
def trigger_scrape():
    """
    Trigger a fresh scrape for one or more companies.
    Expects JSON body: {"companies": ["M&T Bank", "Acme Corp"]}
    """
    data = request.get_json(force=True)
    companies = data.get("companies", [])
    results = run_scrape(companies)
    return jsonify({"scraped": results}), 202
