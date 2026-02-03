from __future__ import annotations

import hashlib
from pathlib import Path

from backend.demo_pack.io import pack_to_tar_gz


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def test_pack_to_tar_gz_is_deterministic(tmp_path: Path) -> None:
    pack_root = tmp_path / "demo_pack"
    (pack_root / "matches").mkdir(parents=True)
    (pack_root / "processed").mkdir(parents=True)

    # Minimal representative structure
    (pack_root / "metadata.json").write_text('{"version": 1}', encoding="utf-8")
    (pack_root / "matches" / "TL-C9-G2.json").write_text('{"match_id": "TL-C9-G2"}', encoding="utf-8")
    (pack_root / "processed" / "events_store.json").write_text('{"version": 1, "matches": {}}', encoding="utf-8")

    out1 = tmp_path / "out1.tar.gz"
    out2 = tmp_path / "out2.tar.gz"

    pack_to_tar_gz(pack_root, out1)
    pack_to_tar_gz(pack_root, out2)

    assert _sha256(out1) == _sha256(out2)
