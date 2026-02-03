from __future__ import annotations

import gzip
import json
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.demo_pack.schemas import DemoEvent, DemoMoment, DemoPattern, EvidencePanel


@dataclass(frozen=True)
class DemoPackPaths:
    root: Path

    @property
    def matches_dir(self) -> Path:
        return self.root / "matches"

    @property
    def processed_dir(self) -> Path:
        return self.root / "processed"

    @property
    def events_store(self) -> Path:
        return self.processed_dir / "events_store.json"

    @property
    def moments_store(self) -> Path:
        return self.processed_dir / "moments_store.json"

    @property
    def patterns_store(self) -> Path:
        return self.processed_dir / "patterns_store.json"

    @property
    def evidence_refs(self) -> Path:
        return self.processed_dir / "evidence_refs.json"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


def write_stores(
    pack_root: Path,
    events_by_match: dict[str, list[DemoEvent]],
    moments_by_match: dict[str, list[DemoMoment]],
    patterns: list[DemoPattern],
    evidence_panels: dict[str, EvidencePanel],
) -> None:
    paths = DemoPackPaths(pack_root)

    events_out = {
        "version": 1,
        "matches": {
            match_id: [e.model_dump() for e in events]
            for match_id, events in sorted(events_by_match.items())
        },
    }
    moments_out = {
        "version": 1,
        "matches": {
            match_id: [m.model_dump() for m in moments]
            for match_id, moments in sorted(moments_by_match.items())
        },
    }
    patterns_out = {
        "version": 1,
        "patterns": [p.model_dump() for p in patterns],
    }
    evidence_out = {
        "version": 1,
        "panels": {
            evidence_id: panel.model_dump()
            for evidence_id, panel in sorted(evidence_panels.items())
        },
    }

    write_json(paths.events_store, events_out)
    write_json(paths.moments_store, moments_out)
    write_json(paths.patterns_store, patterns_out)
    write_json(paths.evidence_refs, evidence_out)


def pack_to_tar_gz(pack_root: Path, out_tar_gz: Path) -> None:
    """Create a deterministic tar.gz for the demo pack.

    Determinism matters for judge-proof CI: even if file contents are identical,
    the archive hash can vary if mtimes/owners/order vary.
    """

    out_tar_gz.parent.mkdir(parents=True, exist_ok=True)
    if out_tar_gz.exists():
        out_tar_gz.unlink()

    fixed_mtime = 0

    def _add_dir(tar: tarfile.TarFile, arcname: str) -> None:
        ti = tarfile.TarInfo(name=arcname)
        ti.type = tarfile.DIRTYPE
        ti.mode = 0o755
        ti.uid = 0
        ti.gid = 0
        ti.uname = ""
        ti.gname = ""
        ti.mtime = fixed_mtime
        tar.addfile(ti)

    def _add_file(tar: tarfile.TarFile, src: Path, arcname: str) -> None:
        st = src.stat()
        ti = tarfile.TarInfo(name=arcname)
        ti.size = st.st_size
        ti.mode = 0o644
        ti.uid = 0
        ti.gid = 0
        ti.uname = ""
        ti.gname = ""
        ti.mtime = fixed_mtime
        with src.open("rb") as f:
            tar.addfile(ti, fileobj=f)

    # Use a deterministic gzip header (mtime=0, no embedded original filename)
    with out_tar_gz.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=fixed_mtime) as gzf:
            with tarfile.open(fileobj=gzf, mode="w", format=tarfile.PAX_FORMAT) as tar:
                root_arc = "demo_pack"
                _add_dir(tar, root_arc)

                # Add directories/files in stable sorted order
                rel_paths = sorted(
                    [p.relative_to(pack_root) for p in pack_root.rglob("*")],
                    key=lambda p: p.as_posix(),
                )
                added_dirs: set[str] = set([root_arc])
                for rel in rel_paths:
                    src = pack_root / rel
                    arc = f"{root_arc}/{rel.as_posix()}"

                    # Ensure parent dirs exist in archive in stable order
                    parents = []
                    cur = rel.parent
                    while cur != Path("."):
                        parents.append(cur)
                        cur = cur.parent
                    for d in reversed(parents):
                        d_arc = f"{root_arc}/{d.as_posix()}"
                        if d_arc not in added_dirs:
                            _add_dir(tar, d_arc)
                            added_dirs.add(d_arc)

                    if src.is_dir():
                        if arc not in added_dirs:
                            _add_dir(tar, arc)
                            added_dirs.add(arc)
                        continue
                    _add_file(tar, src, arc)


def load_stores(pack_root: Path) -> tuple[
    dict[str, list[DemoEvent]],
    dict[str, list[DemoMoment]],
    list[DemoPattern],
    dict[str, EvidencePanel],
]:
    paths = DemoPackPaths(pack_root)
    with paths.events_store.open("r", encoding="utf-8") as f:
        events_raw = json.load(f)
    with paths.moments_store.open("r", encoding="utf-8") as f:
        moments_raw = json.load(f)
    with paths.patterns_store.open("r", encoding="utf-8") as f:
        patterns_raw = json.load(f)
    with paths.evidence_refs.open("r", encoding="utf-8") as f:
        evidence_raw = json.load(f)

    events_by_match = {
        mid: [DemoEvent.model_validate(e) for e in evs]
        for mid, evs in events_raw.get("matches", {}).items()
    }
    moments_by_match = {
        mid: [DemoMoment.model_validate(m) for m in moms]
        for mid, moms in moments_raw.get("matches", {}).items()
    }
    patterns = [DemoPattern.model_validate(p) for p in patterns_raw.get("patterns", [])]
    evidence_panels = {
        eid: EvidencePanel.model_validate(p)
        for eid, p in evidence_raw.get("panels", {}).items()
    }

    return events_by_match, moments_by_match, patterns, evidence_panels
