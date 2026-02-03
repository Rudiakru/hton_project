SHELL := /bin/sh

# Cross-platform venv python path
ifeq ($(OS),Windows_NT)
VENV_PY := .venv\Scripts\python
else
VENV_PY := .venv/bin/python
endif

.PHONY: setup dev-backend dev-frontend test lint

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