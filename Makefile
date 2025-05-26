.PHONY: run, seed-db, reset-db, setup, run, ui

seed-db:
	uv run python3 -m scripts.seed_db

reset-db:
	uv run python3 -c "from tos.db import DB; DB().reset_collection()"

setup:
	uv venv && uv pip sync

run:
	streamlit run main.py
