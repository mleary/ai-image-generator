"""YAML-backed style presets."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise ImportError("PyYAML is required. Install with: pip install pyyaml") from exc


def _presets_path() -> Path:
    return Path(os.environ.get("PRESETS_PATH", Path(__file__).parent.parent / "presets.yaml"))


def _seed_presets_if_needed(path: Path) -> None:
    """Copy bundled presets.yaml to path on first run (e.g. Railway volume mount)."""
    if path.exists():
        return
    bundled = Path(__file__).parent.parent / "presets.yaml"
    if bundled.exists() and bundled.resolve() != path.resolve():
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bundled, path)


def get_presets() -> list[dict]:
    path = _presets_path()
    _seed_presets_if_needed(path)
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text()) or {}
    return data.get("presets", [])


def save_preset(name: str, style_prompt: str, description: str = "") -> None:
    path = _presets_path()
    data = yaml.safe_load(path.read_text()) if path.exists() else {}
    presets = data.get("presets", [])
    if any(p["name"] == name for p in presets):
        raise ValueError(f"A preset named '{name}' already exists.")
    presets.append({"name": name, "description": description or "", "style_prompt": style_prompt})
    path.write_text(yaml.dump({"presets": presets}, default_flow_style=False, allow_unicode=True))


def delete_preset(name: str) -> None:
    path = _presets_path()
    if not path.exists():
        return
    data = yaml.safe_load(path.read_text()) or {}
    presets = [p for p in data.get("presets", []) if p["name"] != name]
    path.write_text(yaml.dump({"presets": presets}, default_flow_style=False, allow_unicode=True))
