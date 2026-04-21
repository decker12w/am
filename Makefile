nb2py:
	uv run jupyter nbconvert --to script pre_processing/notebook.ipynb --stdout

api-dev:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

api-prod:
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
