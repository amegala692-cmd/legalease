install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

backend:
	. .venv/bin/activate && uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	. .venv/bin/activate && streamlit run frontend/app.py

test:
	. .venv/bin/activate && pytest -q
