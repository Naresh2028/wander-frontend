"""Content-addressed disk cache: the same request is never paid for twice."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class DiskCache:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def key(*parts: Any) -> str:
        blob = json.dumps(parts, sort_keys=True, default=str, ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]

    def _path(self, namespace: str, key: str, ext: str) -> Path:
        d = self.root / namespace
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{key}.{ext}"

    # --- text / json -------------------------------------------------------------
    def get_text(self, namespace: str, key: str) -> str | None:
        p = self._path(namespace, key, "json")
        return p.read_text(encoding="utf-8") if p.is_file() else None

    def put_text(self, namespace: str, key: str, text: str) -> None:
        self._path(namespace, key, "json").write_text(text, encoding="utf-8")

    # --- bytes (images) ----------------------------------------------------------
    def get_bytes(self, namespace: str, key: str, ext: str) -> bytes | None:
        p = self._path(namespace, key, ext)
        return p.read_bytes() if p.is_file() else None

    def put_bytes(self, namespace: str, key: str, ext: str, data: bytes) -> Path:
        p = self._path(namespace, key, ext)
        p.write_bytes(data)
        return p
