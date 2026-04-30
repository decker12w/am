nb2py:
	uv run jupyter nbconvert --to script pre_processing/notebook.ipynb --stdout

db:
	cd backend && uv run python -c "from app.database import create_db; create_db()"

seed:
	cd backend && uv run python scripts/seed.py

db-seed: db seed

api-dev:
	cd backend && uv run uvicorn app.main:application --reload --host 0.0.0.0 --port 8000

api-prod:
	cd backend && uv run uvicorn app.main:application --host 0.0.0.0 --port 8000
