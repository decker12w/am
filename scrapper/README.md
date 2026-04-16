# Scraper de Imoveis - Sao Carlos

Scraper para coleta de dados de imoveis dos sites Cardinali e Roca, focado na cidade de Sao Carlos/SP.

## Como rodar

```bash
# Rodar tudo
uv run python scrapper.py

# Apenas uma imobiliaria
uv run python scrapper.py --apenas roca
uv run python scrapper.py -a cardinali

# Excluir uma imobiliaria
uv run python scrapper.py --excluir roca
uv run python scrapper.py -e cardinali
```

Os CSVs sao salvos na pasta `output/`.

---

## Dados disponiveis por fonte

### Cardinali (cardinali.com.br)

| Campo           | Onde esta no site                     | Exemplo                                              |
| --------------- | ------------------------------------- | ---------------------------------------------------- |
| Codigo          | `.cod-imovel strong`                  | `237790`                                             |
| Titulo          | `.card-titulo h2`                     | `Sala comercial Com estacionamento para 7 carros`    |
| Tipo            | URL (3o segmento)                     | `Comercial`                                          |
| Subtipo         | URL (4o segmento)                     | `Sala Salao com Condominio`                          |
| Finalidade      | URL (1o segmento: `alugar`/`comprar`) | `Locacao` ou `Venda`                                 |
| Preco Locacao   | `.card-valores` (sufixo `L`)          | `12.000,00`                                          |
| Preco Venda     | `.card-valores` (sufixo `V`)          | `265.000,00`                                         |
| Bairro          | `.card-bairro-cidade-texto`           | `Vila Marina`                                        |
| Cidade          | `.card-bairro-cidade-texto`           | `Sao Carlos`                                         |
| Estado          | `.card-bairro-cidade-texto`           | `SP`                                                 |
| Dormitorios     | `.imo-dad-compl .dorm-ico[title]`     | `3`                                                  |
| Suites          | `.imo-dad-compl .suites-ico[title]`   | `1`                                                  |
| Banheiros       | `.imo-dad-compl .banh-ico[title]`     | `2`                                                  |
| Garagens        | `.imo-dad-compl .gar-ico[title]`      | `4`                                                  |
| Area Total      | `.imo-dad-compl .a-total-ico[title]`  | `75.00`                                              |
| Area Construida | `.imo-dad-compl .a-const-ico[title]`  | `70.00`                                              |
| Area Util       | `.imo-dad-compl .a-util-ico[title]`   | `75.00`                                              |
| Area Terreno    | `.imo-dad-compl .a-terr-ico[title]`   | `100.00`                                             |
| Descricao       | `.card-texto p`                       | Texto livre (ate 500 chars)                          |
| URL             | `a.carousel-cell[href]`               | `https://www.cardinali.com.br/alugar/Sao-Carlos/...` |

**Paginacao:** `?pag=N` — ~27 imoveis por pagina, HTML server-rendered.

---

### Roca (roca.com.br)

**Metodo:** API REST via `POST /api/service/consult` (Solr). Retorna JSON paginado com todos os campos.

| Campo           | Campo na API (Solr)            | Exemplo                                              |
| --------------- | ------------------------------ | ---------------------------------------------------- |
| Codigo          | `idtProperty`                  | `35356`                                              |
| Titulo          | `desTitleSite`                 | `Apartamento Padrao para Alugar no Jardim Gibertoni` |
| Tipo            | `namCategory`                  | `Apartamentos`                                       |
| Subtipo         | `namSubCategory`               | `Padrao`                                             |
| Finalidade      | `indType` (`L`/`V`)            | `Locacao` ou `Venda`                                 |
| Preco Locacao   | `valLocation`                  | `2.000,00`                                           |
| Preco Venda     | `valSales`                     | `382.000,00`                                         |
| Bairro          | `namDistrict`                  | `Jardim Gibertoni`                                   |
| Cidade          | `namCity`                      | `Sao Carlos`                                         |
| Estado          | `namState`                     | `Sao Paulo`                                          |
| Dormitorios     | `totalRooms`                   | `4`                                                  |
| Suites          | `prop_char_1`                  | `1`                                                  |
| Banheiros       | `prop_char_176`                | `2`                                                  |
| Garagens        | `totalGarages`                 | `2`                                                  |
| Area Total      | `prop_char_5`                  | `78`                                                 |
| Area Construida | `prop_char_95`                 | `78`                                                 |
| Area Util       | `prop_char_2`                  | `78`                                                 |
| Area Terreno    | --                             | Nao disponivel                                       |
| Descricao       | --                             | Nao disponivel via API de listagem                   |
| URL             | Construida a partir dos campos | `https://www.roca.com.br/imovel/locacao/...`         |

**Paginacao:** `start` + `numRows` via POST JSON, 50 imoveis por batch. Filtro por cidade via `idtCityList: [1]` (Sao Carlos).

---

## Comparativo

| Campo           | Cardinali | Roca |
| --------------- | :-------: | :--: |
| Codigo          |    sim    | sim  |
| Titulo          |    sim    | sim  |
| Tipo            |    sim    | sim  |
| Subtipo         |    sim    | sim  |
| Finalidade      |    sim    | sim  |
| Preco Locacao   |    sim    | sim  |
| Preco Venda     |    sim    | sim  |
| Bairro          |    sim    | sim  |
| Cidade          |    sim    | sim  |
| Estado          |    sim    | sim  |
| Dormitorios     |    sim    | sim  |
| Suites          |    sim    | sim  |
| Banheiros       |    sim    | sim  |
| Garagens        |    sim    | sim  |
| Area Total      |    sim    | sim  |
| Area Construida |    sim    | sim  |
| Area Util       |    sim    | sim  |
| Area Terreno    |    sim    |  --  |
| Descricao       |    sim    |  --  |
| URL             |    sim    | sim  |
