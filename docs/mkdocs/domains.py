"""Discover config domains for MkDocs generation and nav."""

from __future__ import annotations

import re
from pathlib import Path

# Nav labels that differ from a simple title-case of the folder name.
_LABEL_OVERRIDES = {
    "aap": "AAP",
    "aiops": "AIOps",
    "hashi": "HashiCorp",
    "servicenow": "ServiceNow",
}


def domain_label(folder: str) -> str:
    if folder in _LABEL_OVERRIDES:
        return _LABEL_OVERRIDES[folder]
    return folder.replace("_", " ").title()


def discover_domains(config_dir: Path) -> list[str]:
    """Return domain folder names under config/, preferring README table order."""
    ordered: list[str] = []
    readme = config_dir / "README.md"
    if readme.is_file():
        for match in re.finditer(
            r"\| \[([^\]]+)\]\(\./([^/]+)/README\.md\)",
            readme.read_text(encoding="utf-8"),
        ):
            folder = match.group(2)
            domain_path = config_dir / folder
            if domain_path.is_dir() and folder not in ordered:
                ordered.append(folder)

    known = set(ordered)
    for path in sorted(config_dir.iterdir()):
        if not path.is_dir() or path.name in known:
            continue
        if (path / "README.md").is_file() or any(path.glob("*.yml")):
            ordered.append(path.name)
    return ordered
