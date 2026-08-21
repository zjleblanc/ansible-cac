"""Generate MkDocs pages for Cursor agent rules (`.mdc` files).

Invoked by mkdocs-gen-files during `mkdocs build` / `mkdocs serve`.
MkDocs only serves `.md` files, so for each `.cursor/rules/*.mdc` file this
strips the Cursor rule frontmatter and emits a virtual markdown page under
`.cursor/rules/agent/<stem>.md`. Nav wiring (auto-discovering rule pages
into the "AI > Rules" nav section) lives in hooks.py.
"""

from __future__ import annotations

from pathlib import Path

import mkdocs_gen_files

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parents[1]
RULES_DIR = ROOT / ".cursor" / "rules"


def _title_from_stem(stem: str) -> str:
    return stem.replace("-", " ").replace("_", " ").title()


def _strip_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Split leading `---` YAML frontmatter from body; return (fields, body)."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    _, raw_front, body = parts
    fields: dict[str, str] = {}
    for line in raw_front.strip().splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return fields, body.lstrip("\n")


def _render_page(
    *, title: str, source_rel: str, fields: dict[str, str], body: str
) -> str:
    lines = [f"# {title}", "", f"Source: `{source_rel}`", ""]

    description = fields.get("description")
    if description:
        lines.extend([description, ""])

    globs = fields.get("globs")
    always_apply = fields.get("alwaysApply")
    if globs or always_apply is not None:
        lines.append("## Scope")
        lines.append("")
        if always_apply is not None:
            lines.append(f"- Always applied: `{always_apply}`")
        if globs:
            lines.append(f"- Globs: `{globs}`")
        lines.append("")

    lines.append(body.strip())
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    if not RULES_DIR.is_dir():
        return
    for mdc_path in sorted(RULES_DIR.glob("*.mdc")):
        stem = mdc_path.stem
        fields, body = _strip_frontmatter(mdc_path.read_text(encoding="utf-8"))
        source_rel = f".cursor/rules/{mdc_path.name}"

        page = _render_page(
            title=_title_from_stem(stem),
            source_rel=source_rel,
            fields=fields,
            body=body,
        )

        doc_path = Path(".cursor") / "rules" / "agent" / f"{stem}.md"
        with mkdocs_gen_files.open(doc_path.as_posix(), "w") as f:
            f.write(page)
        mkdocs_gen_files.set_edit_path(doc_path.as_posix(), source_rel)


main()
