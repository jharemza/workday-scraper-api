# run.py

import click
from app.main import create_app
from app.scraper import run_scrape
from app.scraper_pkg.config_loader import load_institutions_config
import app.config as config

@click.group()
def cli():
    """Workday Scraper API CLI."""
    pass

@cli.command()
@click.option(
    "--companies", "-c",
    multiple=True,
    help="One or more company names to scrape. If omitted, scrapes all from config."
)
def scrape(companies):
    """
    Trigger the scraper and persist new/deleted jobs.
    """
    if companies:
        targets = list(companies)
    else:
        targets = [inst["name"] for inst in load_institutions_config()]
    result = run_scrape(targets)
    click.echo(result)

@cli.command()
@click.option("--host", default=config.API_HOST, help="Host to bind the API server to.")
@click.option("--port", default=config.API_PORT, type=int, help="Port for the API server.")
def serve(host, port):
    """
    Launch the Flask API.
    """
    app = create_app()
    app.run(host=host, port=port, debug=True)

if __name__ == "__main__":
    cli()
