"""Enriquece data/<fonte>.csv com lat/lng geocodificados por bairro.

Uso:
    python scripts/populate_cardinali_csv.py cardinali
    python scripts/populate_cardinali_csv.py sape
    python scripts/populate_cardinali_csv.py center

O script substitui coordenadas ausentes/inválidas por geocodificação
a partir de (bairro, cidade, estado), com cache em data/bairros_geocode.csv.
"""

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CACHE_CSV = DATA_DIR / "bairros_geocode.csv"

SUBS = {
    r"\bjd\b": "jardim", r"\bj\b": "jardim", r"\bpq\b": "parque",
    r"\bvl\b": "vila", r"\bres\b": "residencial", r"\bcond\b": "condominio",
    r"\bch\b": "chacara", r"\blot\b": "loteamento", r"\bcid\b": "cidade",
}


def normalizar_bairro(s: str) -> str:
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", errors="ignore").decode("utf-8")
    for pat, repl in SUBS.items():
        s = re.sub(pat, repl, s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


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

    if "latitude" not in df.columns:
        df["latitude"] = None
    if "longitude" not in df.columns:
        df["longitude"] = None

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df.loc[df["latitude"] == 0, "latitude"] = None
    df.loc[df["longitude"] == 0, "longitude"] = None

    df["bairro_norm"] = df["bairro"].apply(normalizar_bairro)

    sem_coord = df["latitude"].isna()
    print(f"{sem_coord.sum()} linhas sem coordenada de {len(df)} total")

    cache = load_cache()
    cache["bairro_norm"] = cache["bairro"].apply(normalizar_bairro)

    bairros = df.loc[sem_coord, ["bairro_norm", "cidade", "estado"]].drop_duplicates()
    merged = bairros.merge(cache[["bairro_norm", "lat", "lng"]].drop_duplicates("bairro_norm"),
                           on="bairro_norm", how="left")
    falta = merged[merged["lat"].isna()][["bairro_norm", "cidade", "estado"]]

    print(f"{len(bairros)} bairros a preencher, {len(falta)} a geocodificar (cache: {len(cache)})")

    if not falta.empty:
        falta_geo = falta.rename(columns={"bairro_norm": "bairro"})
        novos = geocode_missing(falta_geo)
        cache = pd.concat([cache, novos], ignore_index=True)
        cache["bairro_norm"] = cache["bairro"].apply(normalizar_bairro)
        cache.drop(columns=["bairro_norm"]).to_csv(CACHE_CSV, index=False)
        print(f"Cache salvo em {CACHE_CSV} ({len(cache)} bairros)")

    cache_dedup = cache[["bairro_norm", "lat", "lng"]].drop_duplicates("bairro_norm")
    fill = df.loc[sem_coord, ["bairro_norm"]].merge(
        cache_dedup, on="bairro_norm", how="left",
    )
    df.loc[sem_coord, "latitude"] = fill["lat"].values
    df.loc[sem_coord, "longitude"] = fill["lng"].values

    df = df.drop(columns=["bairro_norm"])
    df.to_csv(output_csv, index=False)
    faltando = df["latitude"].isna().sum()
    print(f"Salvo {output_csv} ({len(df)} linhas, {faltando} sem coord.)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/populate_cardinali_csv.py <fonte>")
        print("Exemplo: python scripts/populate_cardinali_csv.py sape")
        sys.exit(1)
    main(sys.argv[1])
