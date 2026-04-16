import csv
import time
from abc import ABC, abstractmethod
from pathlib import Path

import requests

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

FIELDNAMES = [
    "fonte",
    "codigo",
    "titulo",
    "tipo",
    "subtipo",
    "finalidade",
    "preco_locacao",
    "preco_venda",
    "valor_condominio",
    "valor_iptu",
    "bairro",
    "cidade",
    "estado",
    "endereco",
    "latitude",
    "longitude",
    "dormitorios",
    "suites",
    "banheiros",
    "garagens",
    "area_total",
    "area_construida",
    "area_util",
    "area_terreno",
    "descricao",
    "url",
]


class BaseScraper(ABC):
    """Base class for all real estate scrapers."""

    name: str
    csv_file: str

    @abstractmethod
    def scrape(self) -> list[dict]:
        """Scrape all listings and return a list of property dicts."""
        ...

    def save_csv(self, properties: list[dict]) -> Path:
        path = OUTPUT_DIR / self.csv_file
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(properties)
        return path
