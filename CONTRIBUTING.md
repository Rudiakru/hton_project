# Contributing

Thanks for your interest! For this hackathon release we are in feature-freeze. Only packaging, docs, assets, and small sanity fixes are accepted.

- No new features.
- Keep demo mode fully offline and deterministic.
- Do not change evidence ID formats or demo pack structure.

Local setup
- Python: `python -m venv .venv && .venv/Scripts/pip install -r requirements.txt`
- Frontend: `cd frontend && npm ci`

Quality checks
- Lint: `make lint`
- Tests: `pytest -q`

Please open an issue before proposing changes that might affect the public interface or demo pack format.