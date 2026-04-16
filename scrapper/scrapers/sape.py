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
    """Extrai informações base do cartão da Sapê Imóveis e acessa links internos."""
    
    # URL do Imóvel
    link_el = card.find("a", href=re.compile(r"^/?Imovel/"))
    url = ""
    if link_el:
        href = link_el.get("href", "")
        if not href.startswith("http"):
            href = href.lstrip("/")
            url = f"{BASE_URL}/{href}"
        else:
            url = href
            
    if not url:
        return None

    # Título (Normalmente tem algo como Cód/Ref)
    codigo = ""
    # A referência no Sapê costuma ficar em textos de Ref: 1234
    ref_el = card.find(string=re.compile(r"Ref\s*:\s*\w+"))
    if ref_el:
        m_codigo = re.search(r"Ref\s*:\s*(\w+)", str(ref_el))
        if m_codigo:
            codigo = m_codigo.group(1).strip()

    titulo_el = card.find(class_=re.compile("card-title"))
    titulo = titulo_el.get_text(strip=True) if titulo_el else ""

    # Subtítulo (Normalmente o Bairro)
    bairro_el = card.find(class_=re.compile("card-subtitle"))
    bairro = bairro_el.get_text(strip=True) if bairro_el else ""

    # Preço principal do Card
    preco_venda = ""
    preco_locacao = ""
    price_text = ""
    if titulo_el:
        price_text = titulo_el.get_text(strip=True)
    elif card.find("strong", string=re.compile("R\$")):
        price_text = card.find("strong", string=re.compile("R\$")).get_text(strip=True)

    m_price = re.search(r"R\$\s*([\d.,]+)", price_text)
    if m_price:
        if finalidade == "Venda":
            preco_venda = m_price.group(1).strip()
        else:
            preco_locacao = m_price.group(1).strip()

    # Puxar dados da página do imóvel (descrição/valores extras/coordenadas)
    valor_condominio = ""
    valor_iptu = ""
    latitude = ""
    longitude = ""
    endereco = ""
    descricao = ""
    tipo = ""
    
    # Specs
    dormitorios = ""
    suites = ""
    banheiros = ""
    garagens = ""
    area_total = ""
    area_util = ""

    # Subrequisição para pegar os detalhes
    try:
        time.sleep(0.5)
        d_resp = session.get(url, headers=HEADERS, timeout=12)
        if d_resp.status_code == 200:
            d_soup = BeautifulSoup(d_resp.text, "lxml")
            full_text = d_soup.get_text(" ", strip=True)
            
            # Descrição Geral do Imóvel
            desc_el = d_soup.select_one(".descricao-imovel, #descricao, .texto, .property-description")
            if desc_el:
                descricao = desc_el.get_text(separator="\n", strip=True)
            else:
                # Fallback em WebForms C# geralmente tem paragrafos
                ps = d_soup.find_all("p")
                long_ps = [p.get_text(strip=True) for p in ps if len(p.get_text(strip=True)) > 80]
                if long_ps:
                    descricao = "\n".join(long_ps)

            # Heurística para Valores
            c_match = re.search(r"Condom[íi]nio[^\dR\$]*?(?:R\$)?\s*([\d.,]+)", full_text, re.IGNORECASE)
            if c_match:
                valor_condominio = c_match.group(1).strip()
            
            i_match = re.search(r"IPTU[^\dR\$]*?(?:R\$)?\s*([\d.,]+)", full_text, re.IGNORECASE)
            if i_match:
                valor_iptu = i_match.group(1).strip()

            # Extração de Coordenadas em Mapas/Scripts
            m_lat = re.search(r"lat\s*[:=]\s*'?(-?\d+\.\d+)'?", d_resp.text)
            m_lon = re.search(r"lng\s*[:=]\s*'?(-?\d+\.\d+)'?", d_resp.text)
            if m_lat and m_lon:
                latitude = m_lat.group(1)
                longitude = m_lon.group(1)

            # Extração de atributos e tipos (quarto, vagas) em blocos de texto
            # Muitas vezes WebForms C# lista os resumos em li, td, span
            q_match = re.search(r"(\d+)\s*(?:Quarto|Dormit[óo]rio)", full_text, re.IGNORECASE)
            if q_match: dormitorios = q_match.group(1)
            
            s_match = re.search(r"(\d+)\s*Su[íi]te", full_text, re.IGNORECASE)
            if s_match: suites = s_match.group(1)

            b_match = re.search(r"(\d+)\s*Banheiro", full_text, re.IGNORECASE)
            if b_match: banheiros = b_match.group(1)

            v_match = re.search(r"(\d+)\s*Vaga", full_text, re.IGNORECASE)
            if v_match: garagens = v_match.group(1)

            a_match = re.search(r"([\d.,]+)\s*m²\s*[A-Za-z\s]*(?:[Úu]til|Constru)", full_text, re.IGNORECASE)
            if a_match: area_util = a_match.group(1)

            t_match = re.search(r"([\d.,]+)\s*m²\s*[A-Za-z\s]*(?:Total)", full_text, re.IGNORECASE)
            if t_match: area_total = t_match.group(1)

            # Identificar o Tipo pelo título e texto (ex: Apartamento, Casa)
            tipos = ["Casa", "Apartamento", "Terreno", "Comercial", "Kitnet", "Fazenda", "Sítio", "Salão"]
            for t in tipos:
                if t.lower() in getattr(d_soup.title, "text", "").lower() or t.lower() in full_text[:400].lower():
                    tipo = t
                    break

            # Às vezes endereço ou rua vêm direto
            e_match = re.search(r"Endereço[:\s]*([^,.\n\t]{5,50})", full_text, re.IGNORECASE)
            if e_match: endereco = e_match.group(1).strip()
            
    except Exception as e:
        print(f"    - Aviso ao navegar pro interior de Sape: {e}")

    # Fallback se não pegou nada que indique Casa ou Apartamento
    if not tipo:
        tipo = "Indefinido"
    
    return {
        "fonte": "Sape",
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

    def scrape(self, max_pages: int = 15) -> list[dict]:
        all_props = []
        seen_codes = set()
        session = requests.Session()

        for listing_path in LISTING_URLS:
            finalidade = "Locacao" if "Alugar" in listing_path else "Venda"
            page = 1
            
            while page <= max_pages:
                # O Sape usa URLs amigáveis /Alugar?page=X
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
                
                # Os container dos cartoes
                cards = soup.select(".card-imovel")
                if not cards:
                    # Alternativas de layout (em caso de updates do SAPE)
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
