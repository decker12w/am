import json
import re
import unicodedata
import numpy as np
import pandas as pd
import joblib
from functools import lru_cache
from pathlib import Path

from app.config import settings

METRICS_PATH = Path(__file__).parents[2] / "models" / "metrics.json"

_ABBREV = {r"\bjd\b": "jardim", r"\bpq\b": "parque", r"\bvl\b": "vila",
           r"\bres\b": "residencial", r"\bcond\b": "condominio", r"\bch\b": "chacara"}

def _normalize(s: str) -> str:
    s = str(s).lower().strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", errors="ignore").decode()
    for pat, rep in _ABBREV.items():
        s = re.sub(pat, rep, s)
    return re.sub(r"\s+", " ", s).strip()

@lru_cache(maxsize=1)
def _load_metrics() -> dict:
    return json.loads(METRICS_PATH.read_text())

KM_DEGREE = 111.0
CENTRO_LAT,     CENTRO_LON     = -22.0174, -47.8908
UFSCAR_LAT,     UFSCAR_LON     = -21.9839, -47.8822
USP_LAT,        USP_LON        = -22.0063, -47.8946
RODOVIARIA_LAT, RODOVIARIA_LON = -22.0304, -47.8823

FEATURES = [
    "tipo", "area_util", "bairro", "area_por_quarto",
    "dist_centro", "dist_ufscar", "dist_usp", "dist_rodoviaria",
    "garagens", "total_comodos", "dormitorios", "banheiros",
    "suites", "reformado_novo", "foco_estudante",
    "latitude", "longitude",
]

FACTOR_LABELS = {
    "area_util":      "Área útil",
    "bairro":         "Bairro",
    "area_por_quarto": "Área por quarto",
    "dist_centro":    "Distância ao centro",
    "dist_ufscar":    "Distância à UFSCar",
    "dist_usp":       "Distância à USP",
    "tipo":           "Tipo do imóvel",
    "dist_rodoviaria": "Distância à rodoviária",
    "garagens":       "Vagas de garagem",
    "total_comodos":  "Total de cômodos",
    "banheiros":      "Banheiros",
    "dormitorios":    "Quartos",
}

TYPE_MAP = {"apartment": "apartamento", "house": "casa", "studio": "apartamento"}



@lru_cache(maxsize=1)
def _load_model():
    path = Path(settings.MODEL_PATH)
    if not path.is_absolute():
        path = Path(__file__).parents[2] / path
    return joblib.load(path)


def _dist(lat: float, lon: float, ref_lat: float, ref_lon: float) -> float:
    return float(np.sqrt((lat - ref_lat) ** 2 + (lon - ref_lon) ** 2) * KM_DEGREE)


def predict(
    type: str,
    neighborhood_name: str,
    area: float,
    bedrooms: int,
    bathrooms: int,
    parking: int,
    latitude: float,
    longitude: float,
) -> dict:
    model = _load_model()

    row = {
        "tipo":           TYPE_MAP.get(type, "apartamento"),
        "bairro":         _normalize(neighborhood_name),
        "area_util":      area,
        "dormitorios":    bedrooms,
        "banheiros":      bathrooms,
        "garagens":       parking,
        "suites":         0,
        "reformado_novo": 0,
        "foco_estudante": 0,
        "area_por_quarto":  area / max(bedrooms, 1),
        "total_comodos":    bedrooms + bathrooms,
        "latitude":       latitude,
        "longitude":      longitude,
        "dist_centro":    _dist(latitude, longitude, CENTRO_LAT, CENTRO_LON),
        "dist_ufscar":    _dist(latitude, longitude, UFSCAR_LAT, UFSCAR_LON),
        "dist_usp":       _dist(latitude, longitude, USP_LAT, USP_LON),
        "dist_rodoviaria": _dist(latitude, longitude, RODOVIARIA_LAT, RODOVIARIA_LON),
    }

    X = pd.DataFrame([row])[FEATURES]
    price = float(model.predict(X)[0])

    # importances globais do LightGBM para aproximar contribuição por feature
    lgbm = model.named_steps["regressor"].regressor_
    feat_names = ["bairro", "tipo"] + [f for f in FEATURES if f not in ("bairro", "tipo")]
    importances = lgbm.feature_importances_ / lgbm.feature_importances_.sum()

    factors = []
    for feat, imp in sorted(zip(feat_names, importances), key=lambda x: -x[1]):
        label = FACTOR_LABELS.get(feat)
        if label is None or imp < 0.01:
            continue
        contribution = round(price * imp, 2)
        factors.append({"label": label, "value": contribution, "weight": round(imp * 100, 1)})

    mae = _load_metrics()["mae"]
    margin_pct = round(mae / price * 100, 1)

    price_rounded = round(price / 10) * 10
    return {
        "price":      price_rounded,
        "min":        round((price - mae) / 10) * 10,
        "max":        round((price + mae) / 10) * 10,
        "margin_pct": margin_pct,
        "factors":    factors[:6],
    }
