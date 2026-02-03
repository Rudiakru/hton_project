### Judge Q&A (short answers)

Q: Does the demo call external services or LLMs at runtime?
A: No. It is fully offline. All analytics are precomputed into a frozen demo pack shipped with the repo.

Q: How do you prove integrity?
A: We ship `verify_integrity.py` inside the pack (run it locally) and an API endpoint `/api/demo/integrity`. Both should show `broken_refs = 0` for the shipped pack.

Q: How do you prove determinism?
A: We include `scripts/verify_determinism_twice.py`, which rebuilds the pack twice and byte-compares the stores. It prints success only if both builds are identical.

Q: What’s in the dataset and how reliable are results?
A: Six demo matches. Baselines and confidence are computed within this set. Confidence is labeled low (n=6). The goal is coach-plausible insights with verifiable evidence, not a benchmark.

Q: How do I run it quickly?
A: `make demo` (or `scripts/run_demo.ps1` on Windows, `scripts/run_demo.sh` on mac/Linux). It builds/verifies the pack and starts backend/frontend, then prints the URL.
