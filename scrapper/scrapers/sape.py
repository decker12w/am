import re
import time

import requests
from bs4 import BeautifulSoup

from scrapers.base import HEADERS, BaseScraper

BASE_URL = "https://www.sapeimoveis.com.br"

LISTING_URLS = [
    "/Alugar",
    "/Comprar",
]

def _parse_card(card: BeautifulSoup, session: requests.Session, finalidade: str) -> dict | None:
    """Extrai informações do cartão da Sapê Imóveis (layout 2025+)."""

    link_el = card.find("a", href=re.compile(r"Detalhes\?id="))
    if not link_el:
        return None

    href = link_el.get("href", "")
    if not href.startswith("http"):
        href = href.lstrip("/")
        url = f"{BASE_URL}/{href}"
    else:
        url = href

    id_match = re.search(r"id=(\d+)", href)
    codigo = id_match.group(1) if id_match else ""

    ref_el = card.find("span", string=re.compile(r"Ref:\s*\d+"))
    if ref_el:
        m = re.search(r"Ref:\s*(\d+)", ref_el.get_text())
        if m:
            codigo = m.group(1)

    titulo_el = card.find("h2", class_=re.compile(r"card-title"))
    bairro = titulo_el.get_text(strip=True) if titulo_el else ""

    tipo = ""
    badges = card.select(".property-card-tags .badge")
    for badge in badges:
        txt = badge.get_text(strip=True)
        if not txt.startswith("Ref"):
            tipo = txt
            break

    preco_venda = ""
    preco_locacao = ""
    valor_condominio = ""
    valor_iptu = ""

    price_box = card.select_one(".property-price-box")
    if price_box:
        price_divs = price_box.find_all("div")
        for div in price_divs:
            txt = div.get_text(strip=True)
            m_price = re.search(r"R\$\s*([\d.,]+)", txt)
            if not m_price:
                continue
            val = m_price.group(1)
            if "cond" in txt.lower():
                valor_condominio = val
            elif "iptu" in txt.lower():
                valor_iptu = val
            elif "mês" in txt.lower() or "m\u00eas" in txt.lower():
                if finalidade == "Venda":
                    preco_venda = val
                else:
                    preco_locacao = val
            else:
                if finalidade == "Venda":
                    preco_venda = val
                else:
                    preco_locacao = val

    dormitorios = ""
    suites = ""
    banheiros = ""
    garagens = ""

    stats = card.select(".property-stats .col-6")
    for stat in stats:
        txt = stat.get_text(strip=True)
        m = re.match(r"(\d+)", txt)
        if not m:
            continue
        val = m.group(1)
        lower = txt.lower()
        if "dorm" in lower:
            dormitorios = val
        elif "suíte" in lower or "suite" in lower:
            suites = val
        elif "banho" in lower:
            banheiros = val
        elif "vaga" in lower:
            garagens = val

    latitude = ""
    longitude = ""
    endereco = ""
    descricao = ""
    area_total = ""
    area_util = ""

    try:
        time.sleep(0.3)
        print(f"    -> Detalhes: Ref {codigo}...", end=" ", flush=True)
        d_resp = session.get(url, headers=HEADERS, timeout=12)
        if d_resp.status_code == 200:
            d_soup = BeautifulSoup(d_resp.text, "lxml")
            full_text = d_soup.get_text(" ", strip=True)

            desc_el = d_soup.select_one(".descricao-imovel, #descricao, .texto, .property-description")
            if desc_el:
                descricao = desc_el.get_text(separator="\n", strip=True)
            else:
                ps = d_soup.find_all("p")
                long_ps = [p.get_text(strip=True) for p in ps if len(p.get_text(strip=True)) > 80]
                if long_ps:
                    descricao = "\n".join(long_ps)

            m_lat = re.search(r"lat\s*[:=]\s*'?(-?\d+\.\d+)'?", d_resp.text)
            m_lon = re.search(r"lng\s*[:=]\s*'?(-?\d+\.\d+)'?", d_resp.text)
            if m_lat and m_lon:
                latitude = m_lat.group(1)
                longitude = m_lon.group(1)

            a_match = re.search(r"([\d.,]+)\s*m²\s*[A-Za-z\s]*(?:[Úu]til|Constru)", full_text, re.IGNORECASE)
            if a_match:
                area_util = a_match.group(1)

            t_match = re.search(r"([\d.,]+)\s*m²\s*[A-Za-z\s]*(?:Total)", full_text, re.IGNORECASE)
            if t_match:
                area_total = t_match.group(1)

            e_match = re.search(r"Endereço[:\s]*([^,.\n\t]{5,50})", full_text, re.IGNORECASE)
            if e_match:
                endereco = e_match.group(1).strip()

        print("OK", flush=True)
    except Exception as e:
        print(f"ERRO: {e}", flush=True)

    if not tipo:
        tipo = "Indefinido"

    return {
        "fonte": "Sape",
        "codigo": codigo,
        "titulo": bairro,
        "tipo": tipo,
        "subtipo": "",
        "finalidade": finalidade,
        "preco_locacao": preco_locacao,
        "preco_venda": preco_venda,
        "valor_condominio": valor_condominio,
        "valor_iptu": valor_iptu,
        "bairro": bairro,
        "cidade": "São Carlos",
        "estado": "SP",
        "endereco": endereco,
        "latitude": latitude,
        "longitude": longitude,
        "dormitorios": dormitorios,
        "suites": suites,
        "banheiros": banheiros,
        "garagens": garagens,
        "area_total": area_total,
        "area_construida": "",
        "area_util": area_util,
        "area_terreno": "",
        "descricao": descricao,
        "url": url,
    }

class SapeScraper(BaseScraper):
    name = "Sape"
    csv_file = "sape.csv"

    def scrape(self, max_pages: int = 30) -> list[dict]:
        all_props = []
        seen_codes = set()
        session = requests.Session()

        for listing_path in LISTING_URLS:
            finalidade = "Locacao" if "Alugar" in listing_path else "Venda"
            page = 1

            while page <= max_pages:
                query_string = f"?page={page}" if page > 1 else ""
                url = f"{BASE_URL}{listing_path}{query_string}"

                print(f"  [Sape] Visitando: {url}")
                try:
                    resp = session.get(url, headers=HEADERS, timeout=15)
                    resp.raise_for_status()
                except Exception as e:
                    print(f"  [Sape] Erro em {url}: {e}")
                    break

                soup = BeautifulSoup(resp.text, "lxml")

                cards = soup.select("article.property-card")
                if not cards:
                    cards = soup.select(".card-imovel")
                if not cards:
                    cards = soup.select(".property-item")

                if not cards:
                    print("  [Sape] Nenhum cartão encontrado. Fim da paginação provavelmente.")
                    break

                new_count = 0
                for card in cards:
                    prop = _parse_card(card, session, finalidade)
                    if prop and prop["url"] not in seen_codes:
                        seen_codes.add(prop["url"])
                        all_props.append(prop)
                        new_count += 1

                print(f"  [Sape] Pagina {page}: Recebeu {len(cards)} imoveis ({new_count} Processados limpos)")

                if new_count == 0:
                    break

                page += 1
                time.sleep(1)

        return all_props
