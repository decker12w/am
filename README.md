# RentIQ

Aplicação web para predição de preços de aluguel de imóveis em São Carlos (SP), com modelo de machine learning treinado sobre dados reais coletados via scraper.

## Visão Geral

O usuário informa as características do imóvel — tipo (apartamento ou casa), bairro, área, quartos, banheiros e vagas — e recebe uma estimativa de aluguel com faixa de preço (mínimo/máximo) e os fatores que mais influenciaram o resultado.

O modelo preditivo é um **LightGBM** treinado com 1.152 amostras, com R² de 0,70 e MAE de R$ 514.

## Stack

| Camada            | Tecnologia                      |
| ----------------- | ------------------------------- |
| Frontend          | React 18 + TypeScript + Vite    |
| Backend           | FastAPI + Uvicorn (Python 3.12) |
| ML                | LightGBM, scikit-learn, pandas  |
| Banco de dados    | PostgreSQL 16                   |
| Pacotes Python    | uv                              |
| Pacotes Node      | Bun                             |
| Servidor estático | Nginx                           |
| Contêineres       | Docker + Docker Compose         |

## Arquitetura

```
┌─────────────┐     HTTP      ┌──────────────────┐     SQL      ┌──────────────┐
│  frontend   │ ────────────► │     backend      │ ───────────► │      db      │
│  nginx:80   │               │  fastapi:8000    │              │ postgres:5432│
└─────────────┘               └──────────────────┘              └──────────────┘
```

Três contêineres orquestrados via `docker-compose.yml`:

- **`db`** — PostgreSQL 16, persiste bairros e histórico de predições em volume nomeado
- **`backend`** — API REST (FastAPI), carrega o modelo LightGBM serializado em disco
- **`frontend`** — SPA React compilada servida pelo Nginx

## Execução com Docker Compose

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) >= 24
- [Docker Compose](https://docs.docker.com/compose/) >= 2

Nenhuma outra dependência precisa ser instalada no host.

### Passo a Passo

**1. Clone o repositório**

```bash
git clone https://github.com/<usuario>/rentiq.git
cd rentiq
```

**2. Crie o arquivo de variáveis de ambiente do backend**

Crie `backend/.env.docker` com o conteúdo abaixo:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/am
ALLOWED_ORIGINS=["http://localhost"]
MODEL_PATH=models/modelo_aluguel.pkl
STAGE=production
DEBUG=false
```

**3. Suba os contêineres**

```bash
docker compose up --build
```

**4. Acesse**

| Serviço                           | URL                         |
| --------------------------------- | --------------------------- |
| Interface web                     | http://localhost            |
| API REST                          | http://localhost:8000       |
| Documentação interativa (Swagger) | http://localhost:8000/docs  |
| ReDoc                             | http://localhost:8000/redoc |

### Parar

```bash
docker compose down          # para os contêineres
docker compose down -v       # para e remove o volume do banco
```

---

## Execução Local (sem Docker)

### Pré-requisitos

Instale as seguintes dependências antes de prosseguir:

| Dependência | Versão mínima | Download                                                |
| ----------- | ------------- | ------------------------------------------------------- |
| Python      | 3.12          | https://www.python.org/downloads/                       |
| uv          | qualquer      | https://docs.astral.sh/uv/getting-started/installation/ |
| Bun         | 1.x           | https://bun.sh/                                         |
| PostgreSQL  | 16            | https://www.postgresql.org/download/                    |

> **Atenção:** o PostgreSQL precisa estar instalado e em execução na máquina antes de seguir os passos abaixo.

### 1. Clone o repositório

```bash
git clone https://github.com/<usuario>/rentiq.git
cd rentiq
```

### 2. Configure o banco de dados

Ligue o processo do PostgreSQL local

```bash
brew services start postgresql@14 (MacOS)
sudo service postgresql start (Linux)
```

Crie um usuário e senha para o PostgreSQL:

```bash
psql postgres -c "CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';"
```

Crie um banco chamado `am` no PostgreSQL local:

```bash
psql postgres -c "CREATE DATABASE am;"
```

### 3. Configure e inicie o backend

Crie `backend/.env` com as credenciais do seu PostgreSQL local:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/am
ALLOWED_ORIGINS=["http://localhost:5173"]
MODEL_PATH=models/modelo_aluguel.pkl
STAGE=development
DEBUG=true
```

Instale as dependências e crie as tabelas:

```bash
uv sync
make db       # cria as tabelas no banco
make seed     # popula os bairros
```

Inicie a API em modo de desenvolvimento (com hot-reload):

```bash
make api-dev
```

A API estará disponível em http://localhost:8000.

### 4. Configure e inicie o frontend

```bash
cd frontend
bun install
bun run dev
```

O frontend estará disponível em http://localhost:5173.

## Estrutura do Repositório

```
rentiq/
├── backend/
│   ├── app/
│   │   ├── models/        # Entidades SQLModel
│   │   ├── routes/        # Endpoints FastAPI
│   │   └── services/      # Lógica de predição
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/               # Componentes React/TypeScript
│   ├── Dockerfile
│   └── nginx.conf
├── models/                # Modelo LightGBM serializado + métricas
├── pre_processing/        # Scripts de pré-processamento
├── scrapper/              # Scripts de coleta de dados
├── data/                  # Dados brutos e processados
└── docker-compose.yml
```

## API — Endpoints Principais

| Método | Rota                 | Descrição                    |
| ------ | -------------------- | ---------------------------- |
| `GET`  | `/api/neighborhoods` | Lista bairros disponíveis    |
| `POST` | `/api/predictions`   | Retorna predição de preço    |
| `GET`  | `/api/model/metrics` | Métricas do modelo (R², MAE) |

### Exemplo de requisição

```bash
curl -X POST http://localhost:8000/api/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "type": "apartment",
    "neighborhood_id": "<id>",
    "area": 65.0,
    "bedrooms": 2,
    "bathrooms": 1,
    "parking": 1
  }'
```

```json
{
  "price": 1450.0,
  "min": 1200.0,
  "max": 1700.0,
  "margin_pct": 0.17,
  "factors": [
    { "label": "Área útil", "value": 65.0, "weight": 0.41 },
    { "label": "Bairro", "value": 0.0, "weight": 0.28 }
  ]
}
```
