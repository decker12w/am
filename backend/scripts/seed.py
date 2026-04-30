import sys
import re
import unicodedata
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))

import pandas as pd
from sqlmodel import Session, select
from app.database import engine, create_db
from app.models.listing import Listing
from app.models.neighborhood import Neighborhood

PROJECT_ROOT = Path(__file__).parents[2]
LISTINGS_CSV = PROJECT_ROOT / "data" / "todos_imoveis.csv"
NEIGHBORHOODS_CSV = PROJECT_ROOT / "data" / "bairros_geocode.csv"

ABBREV = {
    r"\bjd\b": "jardim",
    r"\bpq\b": "parque",
    r"\bvl\b": "vila",
    r"\bres\b": "residencial",
    r"\bcond\b": "condominio",
    r"\bch\b": "chacara",
}


def normalize_name(s: str) -> str:
    s = str(s).lower().strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", errors="ignore").decode()
    for pat, rep in ABBREV.items():
        s = re.sub(pat, rep, s)
    return re.sub(r"\s+", " ", s).strip()


def seed_neighborhoods(session: Session):
    if session.exec(select(Neighborhood)).first():
        print("neighborhoods already seeded, skipping")
        return

    df = pd.read_csv(NEIGHBORHOODS_CSV)
    df = df[df["cidade"] == "São Carlos"]
    df = df.dropna(subset=["lat", "lng"])
    df["name"] = df["bairro"].apply(normalize_name)
    df = df.drop_duplicates(subset=["name"], keep="first")

    records = [
        Neighborhood(name=row["name"], latitude=row["lat"], longitude=row["lng"])
        for _, row in df.iterrows()
    ]
    session.bulk_save_objects(records)
    session.commit()
    print(f"seeded {len(records)} neighborhoods")


def seed_listings(session: Session):
    if session.exec(select(Listing)).first():
        print("listings already seeded, skipping")
        return

    df = pd.read_csv(LISTINGS_CSV)

    def safe_float(val):
        if pd.isna(val):
            return None
        if isinstance(val, str):
            val = val.replace(".", "").replace(",", ".")
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    def safe_int(val):
        f = safe_float(val)
        return int(f) if f is not None else None

    records = [
        Listing(
            source=str(row["fonte"]),
            source_code=str(row["codigo"]),
            type=str(row["tipo"]),
            purpose=str(row["finalidade"]),
            rent_price=safe_float(row["preco_locacao"]),
            neighborhood=normalize_name(row["bairro"]),
            latitude=safe_float(row["latitude"]),
            longitude=safe_float(row["longitude"]),
            bedrooms=safe_int(row["dormitorios"]),
            bathrooms=safe_int(row["banheiros"]),
            parking=safe_int(row["garagens"]),
            useful_area=safe_float(row["area_util"]),
            built_area=safe_float(row["area_construida"]),
            url=str(row["url"]) if pd.notna(row["url"]) else None,
        )
        for _, row in df.iterrows()
    ]

    session.bulk_save_objects(records)
    session.commit()
    print(f"seeded {len(records)} listings")


if __name__ == "__main__":
    create_db()
    with Session(engine) as session:
        seed_neighborhoods(session)
        seed_listings(session)
