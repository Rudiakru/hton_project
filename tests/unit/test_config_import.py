import importlib

import pytest


def test_import_core_config_does_not_require_api_key(monkeypatch):
    monkeypatch.delenv("GRID_API_KEY", raising=False)

    import dotenv

    # Prevent reading a local .env during this test run.
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    import core.config

    importlib.reload(core.config)

    assert core.config.Config.GRID_API_KEY in (None, "")


def test_config_validate_requires_api_key_when_requested():
    from core.config import Config

    old_key = Config.GRID_API_KEY
    try:
        Config.GRID_API_KEY = None
        with pytest.raises(ValueError):
            Config.validate(require_api_key=True)

        # Should not raise if API key is not required
        Config.validate(require_api_key=False)
    finally:
        Config.GRID_API_KEY = old_key
