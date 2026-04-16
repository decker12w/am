import re
import time

import requests
from bs4 import BeautifulSoup

from scrapers.base import HEADERS, BaseScraper

BASE_URL = "https://www.cardinali.com.br"

LISTING_URLS = [
    "/alugar/Sao-Carlos",
    "/comprar/Sao-Carlos",
]


def _parse_price(text: str) -> tuple[str, str]:
    """Return (preco_locacao, preco_venda) from price div text."""
    locacao = ""
    venda = ""
    for part in text.split("\n"):
        part = part.strip()
        if not part:
            continue
        match = re.search(r"R\$\s*([\d.,]+)\s*([LV])", part)
        if match:
            valor = match.group(1)
            tipo = match.group(2)
            if tipo == "L":
                locacao = valor
            elif tipo == "V":
                venda = valor
    return locacao, venda


def _parse_specs(card: BeautifulSoup) -> dict:
    """Extract specs (dormitorios, banheiros, garagens, areas) from card."""
    specs = {
        "dormitorios": "",
        "suites": "",
        "banheiros": "",
        "garagens": "",
        "area_total": "",
        "area_construida": "",
        "area_util": "",
        "area_terreno": "",
    }
    spec_divs = card.select(".imo-dad-compl div[title]")
    for div in spec_divs:
        title = div.get("title", "")
        match = re.match(r"([\d.,]+)", title)
        if not match:
            continue
        valor = match.group(1)
        cls = " ".join(div.get("class", []))
        if "dorm-ico" in cls:
            specs["dormitorios"] = valor
        elif "suites-ico" in cls:
            specs["suites"] = valor
        elif "banh-ico" in cls:
            specs["banheiros"] = valor
        elif "gar-ico" in cls:
            specs["garagens"] = valor
        elif "a-total-ico" in cls:
            specs["area_total"] = valor
        elif "a-const-ico" in cls:
            specs["area_construida"] = valor
        elif "a-util-ico" in cls:
            specs["area_util"] = valor
        elif "a-terr-ico" in cls:
            specs["area_terreno"] = valor
    return specs


def _parse_card(card: BeautifulSoup, session: requests.Session = None) -> dict | None:
    """Parse a single property card from Cardinali."""
    cod_el = card.select_one(".cod-imovel strong")
    if not cod_el:
        return None
    codigo = cod_el.get_text(strip=True)

    titulo_el = card.select_one(".card-titulo h2")
    titulo = titulo_el.get_text(strip=True) if titulo_el else ""

    loc_el = card.select_one(".card-bairro-cidade-texto")
    bairro, cidade, estado = "", "", ""
    if loc_el:
        loc_text = loc_el.get_text(strip=True)
        parts = [p.strip() for p in loc_text.split("-")]
        if len(parts) >= 2:
            bairro = parts[0]
            city_state = parts[1]
            if "/" in city_state:
                cidade, estado = city_state.split("/", 1)
                cidade = cidade.strip()
                estado = estado.strip()
            else:
                cidade = city_state

    price_el = card.select_one(".card-valores")
    preco_locacao, preco_venda = "", ""
    if price_el:
        preco_locacao, preco_venda = _parse_price(price_el.get_text())

    link_el = card.select_one("a.carousel-cell")
    url = ""
    tipo, subtipo = "", ""
    if link_el:
        href = link_el.get("href", "")
        url = f"{BASE_URL}/{href.lstrip('/')}"
        url_parts = href.strip("/").split("/")
        if len(url_parts) >= 4:
            tipo = url_parts[2].replace("-", " ")
            subtipo = url_parts[3].replace("-", " ")

    finalidade = ""
    if link_el:
        href = link_el.get("href", "")
        if href.startswith("alugar"):
            finalidade = "Locacao"
        elif href.startswith("comprar"):
            finalidade = "Venda"

    desc_el = card.select_one(".card-texto p")
    descricao = desc_el.get_text(strip=True) if desc_el else ""

    specs = _parse_specs(card)

    valor_condominio = ""
    valor_iptu = ""
    latitude = ""
    longitude = ""
    endereco = ""

    if url and session:
        try:
            d_resp = session.get(url, headers=HEADERS, timeout=12)
            if d_resp.status_code == 200:
                d_soup = BeautifulSoup(d_resp.text, "lxml")
                full_text = d_soup.get_text(" ", strip=True)
                
                # Extrai condomínio e IPTU por heurística
                c_match = re.search(r"Condom[íi]nio[^\d]*?([\d.,]+)", full_text, re.IGNORECASE)
                if c_match:
                    valor_condominio = c_match.group(1).strip()
                
                i_match = re.search(r"IPTU[^\d]*?([\d.,]+)", full_text, re.IGNORECASE)
                if i_match:
                    valor_iptu = i_match.group(1).strip()

                # Latitude e Longitude
                html_text = d_resp.text
                m_lat = re.search(r"lat\s*:\s*'?(-?\d+\.\d+)'?", html_text)
                m_lon = re.search(r"lng\s*:\s*'?(-?\d+\.\d+)'?", html_text)
                if m_lat and m_lon:
                    latitude = m_lat.group(1)
                    longitude = m_lon.group(1)

                # Melhorar descricao com campo completo da página interna
                d_texto = d_soup.select_one(".imovel-texto, .texto-descricao, .descricao")
                if d_texto:
                    descricao = d_texto.get_text(separator="\n", strip=True)

                # Endereço
                end_el = d_soup.select_one(".end-titulo, .endereco")
                if end_el:
                    endereco = end_el.get_text(strip=True)

        except Exception:
            pass

    return {
        "fonte": "Cardinali",
        "codigo": codigo,
        "titulo": titulo,
        "tipo": tipo,
        "subtipo": subtipo,
        "finalidade": finalidade,
        "preco_locacao": preco_locacao,
        "preco_venda": preco_venda,
        "valor_condominio": valor_condominio,
        "valor_iptu": valor_iptu,
        "bairro": bairro,
        "cidade": cidade,
        "estado": estado,
        "endereco": endereco,
        "latitude": latitude,
        "longitude": longitude,
        "descricao": descricao,
        "url": url,
        **specs,
    }


def _scrape_page(session: requests.Session, url: str) -> tuple[list[dict], bool]:
    """Scrape a single listing page. Returns (properties, has_next_page)."""
    resp = session.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    cards = soup.select(".muda_card1")
    properties = []
    for card in cards:
        prop = _parse_card(card, session)
        if prop:
            properties.append(prop)

    has_next = bool(soup.select_one('a[href*="pag="]'))
    return properties, has_next


class CardinaliScraper(BaseScraper):
    name = "Cardinali"
    csv_file = "cardinali.csv"

    def scrape(self, max_pages_per_listing: int = 100) -> list[dict]:
        all_props = []
        seen_codes = set()
        session = requests.Session()

        for listing_path in LISTING_URLS:
            page = 1
            while page <= max_pages_per_listing:
                url = f"{BASE_URL}{listing_path}"
                if page > 1:
                    url += f"?pag={page}"

                print(f"  [Cardinali] {url}")
                try:
                    props, has_next = _scrape_page(session, url)
                except Exception as e:
                    print(f"  [Cardinali] Erro na pagina {page}: {e}")
                    break

                new_count = 0
                for p in props:
                    if p["codigo"] not in seen_codes:
                        seen_codes.add(p["codigo"])
                        all_props.append(p)
                        new_count += 1

                print(f"  [Cardinali] Pagina {page}: {len(props)} imoveis ({new_count} novos)")

                if not has_next or not props or new_count == 0:
                    break
                page += 1
                time.sleep(1)

        return all_props
