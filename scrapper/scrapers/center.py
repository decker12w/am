import time
import requests

from scrapers.base import HEADERS, BaseScraper

BASE_URL = "https://www.centerimoveis.com"
API_URL = "https://www.centerimoveis.com/api/service/consult"

IND_TYPE_MAP = {"L": "Locacao", "V": "Venda"}

def _parse_doc(doc: dict) -> dict:
    """Convert a Solr document from the Center API to our normalized schema."""
    ind_type = doc.get("indType", "")
    if not ind_type and doc.get("valLocation"): ind_type = "L"
    elif not ind_type and doc.get("valSales"): ind_type = "V"
        
    finalidade = IND_TYPE_MAP.get(ind_type, ind_type)

    preco_locacao = ""
    preco_venda = ""
    if ind_type == "L" and doc.get("valLocation"):
        preco_locacao = f"{doc['valLocation']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if doc.get("valSales"):
        preco_venda = f"{doc['valSales']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    categoria = doc.get("namCategory", "")
    subcategoria = doc.get("namSubCategory", "")

    area_total = str(doc.get("prop_char_5", ""))
    area_util = str(doc.get("prop_char_2", ""))
    area_construida = str(doc.get("prop_char_95", ""))

    url_category = categoria.lower() if categoria else "imovel"
    url_city = doc.get("namCity", "").lower().replace(" ", "-") if doc.get("namCity") else "cidade"
    url_district = doc.get("namDistrict", "").lower().replace(" ", "-") if doc.get("namDistrict") else "bairro"
    idt = doc.get("idtProperty", "")
    
    return {
        "fonte": "Center",
        "codigo": str(idt),
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
        "dormitorios": str(doc.get("totalRooms", "") or ""),
        "suites": str(doc.get("prop_char_1", "") or ""),
        "banheiros": str(doc.get("prop_char_176", "") or ""),
        "garagens": str(doc.get("totalGarages", "") or ""),
        "area_total": area_total,
        "area_construida": area_construida,
        "area_util": area_util,
        "area_terreno": "",
        "descricao": doc.get("desTitleSite", ""),
        "url": f"{BASE_URL}/imovel/{'locacao' if ind_type == 'L' else 'venda'}/{url_category}/{url_city}/{url_district}/{idt}",
    }

class CenterScraper(BaseScraper):
    name = "Center"
    csv_file = "center.csv"

    def scrape(self, batch_size: int = 50) -> list[dict]:
        all_props = []
        seen_codes = set()
        session = requests.Session()
        session.headers.update({
            **HEADERS,
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
        })

        for ind_type, label in [("L", "Locacao"), ("V", "Venda")]:
            start = 0
            print(f"  [Center] Buscando {label}...")

            while True:
                payload = {
                    "start": start,
                    "numRows": batch_size,
                    "type": ind_type,
                    "post": True,
                    "sortList": [f"moreRecents{'Location' if ind_type == 'L' else 'Sale'}"]
                }

                try:
                    resp = session.post(API_URL, json=payload, timeout=15)
                    resp.raise_for_status()
                except Exception as e:
                    print(f"  [Center] Erro: {e}")
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
                print(f"  [Center] {label}: {len(all_props)} / {num_found} imoveis extraídos.")

                # If we've reached the end of the total results
                if start + batch_size >= (num_found if isinstance(num_found, int) else 999999):
                    break

                start += batch_size
                time.sleep(0.5)

        return all_props
