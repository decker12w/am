import re
import time

import requests
from bs4 import BeautifulSoup

from scrapers.base import HEADERS, BaseScraper

BASE_URL = "https://abiasimoveis.com.br"

LISTING_URLS = [
    "/aluguel/residencial_comercial/",
    "/venda/residencial_comercial/",
]

FINALIDADE_MAP = {
    "Aluguel": "Locacao",
    "Venda": "Venda",
}

# Icon class -> field name mapping
AMENITY_MAP = {
    "fa-bed": "dormitorios",
    "fa-car": "garagens",
    "fa-compress-arrows-alt": "area_util",
    "fa-arrows-alt": "area_total",
    "fa-shower": "banheiros",
    "fa-bath": "suites",
}


def _extract_amenity_icon(div) -> str | None:
    """Return the fa-* icon class from an amenity div."""
    icon = div.select_one("i")
    if not icon:
        return None
    for cls in icon.get("class", []):
        if cls.startswith("fa-") and cls != "fas" and cls != "far":
            return cls
    return None


def _extract_amenity_value(div) -> str:
    """Extract the numeric value from an amenity div."""
    span = div.select_one("span")
    if not span:
        return ""
    text = span.get_text(strip=True)
    # Remove "m²" suffix
    text = re.sub(r"\s*m²\s*$", "", text)
    return text


def _parse_location(card: BeautifulSoup) -> tuple[str, str, str]:
    """Extract (bairro, cidade, estado) from the address element."""
    addr = card.select_one("h3[itemprop=streetAddress]")
    if not addr:
        return "", "", ""
    text = addr.get_text(strip=True)
    # Format: "Bairro - Cidade/UF"
    parts = text.split(" - ", 1)
    bairro = parts[0].strip() if parts else ""
    cidade, estado = "", ""
    if len(parts) >= 2:
        city_state = parts[1].strip()
        if "/" in city_state:
            cidade, estado = city_state.rsplit("/", 1)
            cidade = cidade.strip()
            estado = estado.strip().upper()
        else:
            cidade = city_state
    return bairro, cidade, estado


def _parse_card(card: BeautifulSoup, session: requests.Session = None) -> dict | None:
    """Parse a single property card."""
    codigo = card.get("data-codigo", "")
    if not codigo:
        return None

    titulo_el = card.select_one(".titulo-grid")
    titulo = titulo_el.get_text(strip=True) if titulo_el else ""

    bairro, cidade, estado = _parse_location(card)

    # Price and finalidade
    thumb_status = card.select_one(".thumb-status")
    status_text = thumb_status.get_text(strip=True) if thumb_status else ""
    finalidade = FINALIDADE_MAP.get(status_text, "")

    thumb_price = card.select_one(".thumb-price")
    preco_text = thumb_price.get_text(strip=True) if thumb_price else ""
    # Clean price: "R$ 1.020,00" -> "1.020,00"
    preco_valor = re.sub(r"^R\$\s*", "", preco_text)

    preco_locacao = preco_valor if finalidade == "Locacao" else ""
    preco_venda = preco_valor if finalidade == "Venda" else ""

    # URL
    link_el = card.select_one("a.button-info-panel") or card.select_one("a.swiper-wrapper")
    url = link_el.get("href", "") if link_el else ""

    # Tipo from title (first word: Apartamento, Casa, Kitnet, etc.)
    tipo = ""
    if titulo:
        tipo = titulo.split()[0] if titulo.split() else ""

    # Amenities
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
    for amenity_div in card.select(".amenities-main > div, .clb-amenities-extended > div"):
        icon_cls = _extract_amenity_icon(amenity_div)
        if icon_cls and icon_cls in AMENITY_MAP:
            field = AMENITY_MAP[icon_cls]
            specs[field] = _extract_amenity_value(amenity_div)

    # NOVOS ATRIBUTOS VIA REQUISIÇÃO DA PÁGINA
    valor_condominio = ""
    valor_iptu = ""
    descricao = ""
    latitude = ""
    longitude = ""
    endereco = ""

    if url and session:
        try:
            # Baixa a página do imóvel específico
            d_resp = session.get(url, headers=HEADERS, timeout=12)
            if d_resp.status_code == 200:
                d_soup = BeautifulSoup(d_resp.text, "lxml")
                
                # Descrição: tentamos pegar a div com texto principal (comum em themes)
                desc_el = d_soup.select_one("#property-description, .conteudo-descricao, .description, .texto-descricao")
                if desc_el:
                    descricao = desc_el.get_text(separator="\n", strip=True)
                else:
                    # Fallback para parágrafos longos soltos
                    ps = d_soup.find_all("p")
                    long_ps = [p.get_text(strip=True) for p in ps if len(p.get_text(strip=True)) > 150]
                    if long_ps:
                        descricao = "\n".join(long_ps)

                # Busca genérica no texto por Condomínio e IPTU
                full_text = d_soup.get_text(" ", strip=True)
                c_match = re.search(r"Condom[íi]nio[^\d]*?([\d.,]+)", full_text, re.IGNORECASE)
                if c_match:
                    valor_condominio = c_match.group(1).strip()
                
                i_match = re.search(r"IPTU[^\d]*?([\d.,]+)", full_text, re.IGNORECASE)
                if i_match:
                    valor_iptu = i_match.group(1).strip()

                # Latitude e Longitude de iFrames do Maps
                iframe = d_soup.select_one("iframe[src*='maps']")
                if iframe:
                    src = iframe.get("src", "")
                    m_latlon = re.search(r"q=(-?\d+\.\d+),(-?\d+\.\d+)", src)
                    if m_latlon:
                        latitude = m_latlon.group(1)
                        longitude = m_latlon.group(2)
        except Exception as e:
            pass

    return {
        "fonte": "Abias",
        "codigo": codigo,
        "titulo": titulo,
        "tipo": tipo,
        "subtipo": "",
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


class AbiasScraper(BaseScraper):
    name = "Abias"
    csv_file = "abias.csv"

    def scrape(self, max_pages: int = 100) -> list[dict]:
        all_props = []
        seen_codes = set()
        session = requests.Session()

        for listing_path in LISTING_URLS:
            listing_url = f"{BASE_URL}{listing_path}"
            print(f"  [Abias] Iniciando sessao: {listing_url}")

            try:
                session.get(listing_url, headers=HEADERS, timeout=30)
            except Exception as e:
                print(f"  [Abias] Erro ao iniciar sessao: {e}")
                continue

            page = 1
            while page <= max_pages:
                reload = 1 if page == 1 else 0
                api_url = f"{BASE_URL}/u-sr.php?queryData=&reload={reload}"

                try:
                    resp = session.get(api_url, headers=HEADERS, timeout=30)
                    resp.raise_for_status()
                except Exception as e:
                    print(f"  [Abias] Erro na pagina {page}: {e}")
                    break

                if resp.text.strip() == "0" or not resp.text.strip():
                    break

                soup = BeautifulSoup(resp.text, "lxml")
                cards = soup.select(".imovel-box-single")

                if not cards:
                    break

                new_count = 0
                for card in cards:
                    prop = _parse_card(card, session)
                    if prop and prop["codigo"] not in seen_codes:
                        seen_codes.add(prop["codigo"])
                        all_props.append(prop)
                        new_count += 1

                print(f"  [Abias] Pagina {page}: {len(cards)} imoveis ({new_count} novos)")

                if new_count == 0:
                    break
                page += 1
                time.sleep(0.5)

        return all_props
