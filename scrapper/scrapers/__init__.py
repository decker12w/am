from scrapers.base import BaseScraper, FIELDNAMES, HEADERS, OUTPUT_DIR
from scrapers.abias import AbiasScraper
from scrapers.cardinali import CardinaliScraper
from scrapers.roca import RocaScraper
from scrapers.sape import SapeScraper
from scrapers.center import CenterScraper

SCRAPERS: dict[str, BaseScraper] = {
    "cardinali": CardinaliScraper(),
    "roca": RocaScraper(),
    "abias": AbiasScraper(),
    "sape": SapeScraper(),
    "center": CenterScraper(),
}

__all__ = ["SCRAPERS", "FIELDNAMES", "HEADERS", "OUTPUT_DIR", "BaseScraper"]
