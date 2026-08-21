"""MkDocs hooks for the Autodotes CaC docs site."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from domains import discover_domains, domain_label

ROOT = _HOOKS_DIR.parents[1]
CONFIG = ROOT / "config"
RULES = ROOT / ".cursor" / "rules"

_DOMAIN_README = re.compile(r"^config/([^/]+)/README\.md$")
_FILE_CELL = re.compile(r"^\| `([^`]+\.yml)` \|", re.M)


def _title_from_stem(stem: str) -> str:
    return stem.replace("_", " ").title()


def _rule_title(stem: str) -> str:
    return stem.replace("-", " ").replace("_", " ").title()


def _discover_rules(rules_dir: Path) -> list[dict[str, str]]:
    """Return nav entries for generated agent-rule pages, one per .mdc file."""
    entries = []
    if not rules_dir.is_dir():
        return entries
    for mdc_path in sorted(rules_dir.glob("*.mdc")):
        stem = mdc_path.stem
        entries.append({_rule_title(stem): f".cursor/rules/agent/{stem}.md"})
    return entries


def on_config(config):
    """Expand Configuration nav from config/ domains, and AI > Rules from .cursor/rules/."""
    domain_entries = [{"Overview": "config/README.md"}]
    for folder in discover_domains(CONFIG):
        domain_dir = CONFIG / folder
        children: list[dict[str, str]] = [
            {"Overview": f"config/{folder}/README.md"},
        ]
        for yml_path in sorted(domain_dir.glob("*.yml")):
            stem = yml_path.stem
            children.append(
                {_title_from_stem(stem): f"config/{folder}/vars/{stem}.md"}
            )
        domain_entries.append({domain_label(folder): children})

    nav = config["nav"]
    for i, item in enumerate(nav):
        if isinstance(item, dict) and "Configuration" in item:
            nav[i] = {"Configuration": domain_entries}
        elif isinstance(item, dict) and "AI" in item:
            ai_entries = item["AI"]
            for j, sub in enumerate(ai_entries):
                if isinstance(sub, dict) and "Rules" in sub:
                    ai_entries[j] = {"Rules": _discover_rules(RULES)}
            nav[i] = {"AI": ai_entries}
    return config


def on_files(files, config):
    """Record directories that have an index page for navbar breadcrumbs."""
    dirs = set()
    for f in files:
        src = f.src_uri.replace("\\", "/")
        if src in ("README.md", "index.md"):
            dirs.add("")
        elif src.endswith(("/README.md", "/index.md")):
            dirs.add(src.rsplit("/", 1)[0])
    config["extra"]["breadcrumb_dirs"] = dirs
    return files


def on_page_markdown(markdown: str, page, config, files):
    """Link domain README file-table cells to generated var pages at build time."""
    match = _DOMAIN_README.match(page.file.src_uri)
    if not match:
        return markdown

    domain = match.group(1)
    domain_dir = CONFIG / domain

    def repl(cell: re.Match[str]) -> str:
        fname = cell.group(1)
        stem = Path(fname).stem
        if (domain_dir / fname).is_file():
            return f"| [`{fname}`](vars/{stem}.md) |"
        return cell.group(0)

    return _FILE_CELL.sub(repl, markdown)
