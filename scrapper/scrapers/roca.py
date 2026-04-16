import time

import requests

from scrapers.base import HEADERS, BaseScraper

BASE_URL = "https://www.roca.com.br"
API_URL = "https://roca.com.br/api/service/consult"
CITY_ID = 1  # São Carlos

IND_TYPE_MAP = {"L": "Locacao", "V": "Venda"}


def _parse_doc(doc: dict) -> dict:
    """Convert a Solr document from the API to our normalized schema."""
    ind_type = doc.get("indType", "")
    finalidade = IND_TYPE_MAP.get(ind_type, "")

    preco_locacao = ""
    preco_venda = ""
    if ind_type == "L" and doc.get("valLocation"):
        preco_locacao = f"{doc['valLocation']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if doc.get("valSales"):
        preco_venda = f"{doc['valSales']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    categoria = doc.get("namCategory", "")
    subcategoria = doc.get("namSubCategory", "")

    area_construida = str(doc["prop_char_1"]) if doc.get("prop_char_1") else ""
    area_total = str(doc["prop_char_2"]) if doc.get("prop_char_2") else ""
    area_construida_alt = str(doc["prop_char_95"]) if doc.get("prop_char_95") else ""

    return {
        "fonte": "Roca",
        "codigo": str(doc.get("idtProperty", "")),
        "titulo": doc.get("desTitleSite", ""),
        "tipo": categoria,
        "subtipo": subcategoria,
        "finalidade": finalidade,
        "preco_locacao": preco_locacao,
        "preco_venda": preco_venda,
        "valor_condominio": str(doc.get("valCondominium", "") or ""),
        "valor_iptu": str(doc.get("valMonthIptu", "") or ""),
        "bairro": doc.get("namDistrict", ""),
        "cidade": doc.get("namCity", ""),
        "estado": doc.get("namState", ""),
        "endereco": "",
        "latitude": str(doc.get("latitude", "") or ""),
        "longitude": str(doc.get("longitude", "") or ""),
        "dormitorios": str(doc.get("prop_char_5", "") or ""),
        "suites": "",
        "banheiros": str(doc.get("prop_char_176", "") or ""),
        "garagens": str(doc.get("totalGarages", "") or ""),
        "area_total": area_total,
        "area_construida": area_construida or area_construida_alt,
        "area_util": area_construida or area_construida_alt,
        "area_terreno": "",
        "descricao": doc.get("desTitleSite", ""),
        "url": f"{BASE_URL}/imovel/{'locacao' if ind_type == 'L' else 'venda'}"
               f"/{categoria.lower()}/{doc.get('namCity', '').lower().replace(' ', '-')}"
               f"/{doc.get('namDistrict', '').lower().replace(' ', '-')}/{doc.get('idtProperty', '')}",
    }


class RocaScraper(BaseScraper):
    name = "Roca"
    csv_file = "roca.csv"

    def scrape(self, batch_size: int = 50) -> list[dict]:
        all_props = []
        seen_codes = set()
        session = requests.Session()
        session.headers.update({
            **HEADERS,
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://roca.com.br",
            "Referer": "https://roca.com.br/",
        })

        for ind_type, label in [("L", "Locacao"), ("V", "Venda")]:
            start = 0
            print(f"  [Roca] Buscando {label}...")

            while True:
                payload = {
                    "start": start,
                    "numRows": batch_size,
                    "type": ind_type,
                    "idtCityList": [CITY_ID],
                    "post": True,
                    "sortList": [f"moreRecents{'Location' if ind_type == 'L' else 'Sale'}"],
                }

                try:
                    resp = session.post(API_URL, json=payload, timeout=15)
                    resp.raise_for_status()
                except Exception as e:
                    print(f"  [Roca] Erro: {e}")
                    break

                data = resp.json()
                docs = data.get("response", {}).get("docs", [])

                if not docs:
                    break

                for doc in docs:
                    prop = _parse_doc(doc)
                    if prop["codigo"] not in seen_codes:
                        seen_codes.add(prop["codigo"])
                        all_props.append(prop)

                num_found = data.get("response", {}).get("numFound", "?")
                print(f"  [Roca] {label}: {len(all_props)} / {num_found} imoveis")

                start += batch_size
                time.sleep(0.5)

        return all_props
