"""Enriquece data/<fonte>.csv com lat/lng geocodificados por bairro.

Uso:
    python scripts/populate_cardinali_csv.py cardinali
    python scripts/populate_cardinali_csv.py sape
    python scripts/populate_cardinali_csv.py center

O script substitui coordenadas ausentes/inválidas por geocodificação
a partir de (bairro, cidade, estado), com cache em data/bairros_geocode.csv.
"""

import sys
from pathlib import Path

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CACHE_CSV = DATA_DIR / "bairros_geocode.csv"


def load_cache() -> pd.DataFrame:
    if CACHE_CSV.exists():
        return pd.read_csv(CACHE_CSV)
    return pd.DataFrame(columns=["bairro", "cidade", "estado", "lat", "lng"])


def geocode_missing(falta: pd.DataFrame) -> pd.DataFrame:
    geolocator = Nominatim(user_agent="am-scraper/1.0 (josemaia.comp@gmail.com)")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)

    rows = []
    total = len(falta)
    for i, (_, r) in enumerate(falta.iterrows(), 1):
        q = f"{r['bairro']}, {r['cidade']}, {r['estado']}, Brasil"
        try:
            loc = geocode(q)
        except Exception as e:
            print(f"  [{i}/{total}] erro em {q!r}: {e}")
            loc = None
        lat = loc.latitude if loc else None
        lng = loc.longitude if loc else None
        status = "ok" if loc else "MISS"
        print(f"  [{i}/{total}] {status} {q} -> {lat}, {lng}")
        rows.append({**r, "lat": lat, "lng": lng})
    return pd.DataFrame(rows)


def main(fonte: str) -> None:
    input_csv = DATA_DIR / f"{fonte}.csv"
    output_csv = DATA_DIR / f"{fonte}.csv"

    print(f"Lendo {input_csv}")
    df = pd.read_csv(input_csv)

    df[["latitude", "longitude"]] = None

    cache = load_cache()
    bairros = df[["bairro", "cidade", "estado"]].drop_duplicates()
    merged = bairros.merge(cache, on=["bairro", "cidade", "estado"], how="left")
    falta = merged[merged["lat"].isna()][["bairro", "cidade", "estado"]]

    print(f"{len(bairros)} bairros únicos, {len(falta)} a geocodificar (cache: {len(cache)})")

    if not falta.empty:
        novos = geocode_missing(falta)
        cache = pd.concat([cache, novos], ignore_index=True)
        cache.to_csv(CACHE_CSV, index=False)
        print(f"Cache salvo em {CACHE_CSV} ({len(cache)} bairros)")

    df = df.drop(columns=["latitude", "longitude"]).merge(
        cache.rename(columns={"lat": "latitude", "lng": "longitude"}),
        on=["bairro", "cidade", "estado"],
        how="left",
    )

    df.to_csv(output_csv, index=False)
    faltando = df["latitude"].isna().sum()
    print(f"Salvo {output_csv} ({len(df)} linhas, {faltando} sem coord.)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/populate_cardinali_csv.py <fonte>")
        print("Exemplo: python scripts/populate_cardinali_csv.py sape")
        sys.exit(1)
    main(sys.argv[1])
