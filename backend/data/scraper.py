#!/usr/bin/env python3
import json
import logging
import time
import urllib.robotparser
from pathlib import Path
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("scraper")

BOT_NAME = "DarWasaltBot/1.0"
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "knowledge_base.json"

SITES = {
    "Dar Global": {
        "domain": "https://darglobal.co.uk",
        "robots": "https://darglobal.co.uk/robots.txt",
        "endpoints": ["/", "/press", "/landing-page/aida", "/projects"],
    },
    "Wasalt": {
        "domain": "https://wasalt.sa",
        "robots": "https://wasalt.sa/robots.txt",
        "endpoints": ["/en", "/en/s/wasalt-business", "/en/s/terms-of-advertising"],
    },
}


def is_allowed_by_robots(robots_url: str, url: str) -> bool:
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(BOT_NAME, url)
    except Exception as err:
        logger.warning(f"Failed to fetch robots.txt from {robots_url}: {err}")
        return True


def run_checks():
    logger.info("Checking access permissions for target portals...")
    session = requests.Session()
    session.headers.update({"User-Agent": BOT_NAME})

    for name, site in SITES.items():
        logger.info(f"\nChecking {name} ({site['domain']})")
        for ep in site["endpoints"]:
            full_url = f"{site['domain']}{ep}"
            allowed = is_allowed_by_robots(site["robots"], full_url)
            status = "ALLOWED" if allowed else "DISALLOWED"
            logger.info(f" - [{status}] {full_url}")
            time.sleep(0.3)

    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"\nTotal documents currently indexed: {len(data)}")
    else:
        logger.warning("knowledge_base.json not found!")


if __name__ == "__main__":
    run_checks()
