.PHONY: run, seed-db, reset-db, setup, run, ui

seed-db:
	uv run python3 -m scripts.seed_db

reset-db:
	uv run python3 -c "from tos.db import DB; DB().reset_collection()"

setup:
	uv venv && uv pip sync

run:
	uv run python3 main.py

ui:
	streamlit run main.py
