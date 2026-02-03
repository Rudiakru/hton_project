SHELL := /bin/sh

# Cross-platform venv python path
ifeq ($(OS),Windows_NT)
VENV_PY := .venv\Scripts\python
DEMO_CMD := powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\run_demo.ps1
else
VENV_PY := .venv/bin/python
DEMO_CMD := bash scripts/run_demo.sh
endif

.PHONY: setup dev-backend dev-frontend test lint demo

setup:
	@test -d .venv || python -m venv .venv
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install -r requirements.txt
	cd frontend && npm ci

dev-backend:
	$(VENV_PY) -m uvicorn backend.main:app --reload

dev-frontend:
	cd frontend && npm run dev

test:
	$(VENV_PY) -m pytest

lint:
	$(VENV_PY) -m ruff check .

demo:
	$(DEMO_CMD)