"""Generate MkDocs pages that render domain-scoped config var files.

Invoked by mkdocs-gen-files during `mkdocs build` / `mkdocs serve`.
For each config/<domain>/*.yml file, emits a virtual markdown page under
config/<domain>/vars/<stem>.md. Domain nav and README links are wired in
hooks.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import mkdocs_gen_files
import yaml

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parents[1]
CONFIG = ROOT / "config"
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from domains import discover_domains  # noqa: E402

SUMMARY_COLUMNS = (
    "name",
    "organization",
    "project",
    "inventory",
    "playbook",
    "url",
    "description",
)


class _IgnoreUnknownTagsLoader(yaml.SafeLoader):
    """Load Ansible-flavored YAML; treat unknown tags (e.g. !unsafe) as scalars."""


def _construct_undefined(loader: yaml.Loader, tag_suffix: str, node: yaml.Node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


_IgnoreUnknownTagsLoader.add_multi_constructor("!", _construct_undefined)


def _title_from_stem(stem: str) -> str:
    return stem.replace("_", " ").title()


def _extract_one_liner(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("# ").strip()
        if stripped:
            break
    return ""


def _md_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        text = ", ".join(str(v) for v in value)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _indent_block(text: str, spaces: int = 4) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line else pad for line in text.splitlines())


def _pick_columns(entries: list[dict]) -> list[str]:
    present = {"name"}
    for entry in entries:
        for key in SUMMARY_COLUMNS:
            if key != "name" and entry.get(key) not in (None, "", []):
                present.add(key)
    return [c for c in SUMMARY_COLUMNS if c in present]


def _render_summary_table(entries: list[dict]) -> str:
    if not entries:
        return "_No resources defined._\n"

    columns = _pick_columns(entries)
    header = "| " + " | ".join(c.replace("_", " ").title() for c in columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for entry in entries:
        cells = [_md_cell(entry.get(col, "")) for col in columns]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep, *rows]) + "\n"


def _load_entries(path: Path) -> tuple[str | None, list[dict]]:
    text = path.read_text(encoding="utf-8")
    try:
        data = yaml.load(text, Loader=_IgnoreUnknownTagsLoader)
    except yaml.YAMLError:
        return None, []

    if not isinstance(data, dict) or not data:
        return None, []

    for key, value in data.items():
        if isinstance(value, list):
            entries = [e for e in value if isinstance(e, dict)]
            return str(key), entries
    return str(next(iter(data))), []


def _render_page(
    *,
    title: str,
    source_rel: str,
    one_liner: str,
    var_name: str | None,
    entries: list[dict],
    raw_yaml: str,
) -> str:
    lines = [
        f"# {title}",
        "",
        f"Source: `{source_rel}`",
        "",
    ]
    if one_liner:
        lines.extend(
            [
                "## Apply",
                "",
                "```bash",
                one_liner,
                "```",
                "",
            ]
        )
    if var_name:
        lines.extend(
            [
                "## Variable",
                "",
                f"`{var_name}`",
                "",
            ]
        )
    lines.extend(
        [
            f"## Resources ({len(entries)})",
            "",
            _render_summary_table(entries),
            "",
            "## Full definition",
            "",
            '???+ autodotes "YAML"',
            "",
            _indent_block("```yaml"),
            _indent_block(raw_yaml.rstrip("\n")),
            _indent_block("```"),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    for domain in discover_domains(CONFIG):
        domain_dir = CONFIG / domain
        for yml_path in sorted(domain_dir.glob("*.yml")):
            stem = yml_path.stem
            title = _title_from_stem(stem)
            raw = yml_path.read_text(encoding="utf-8")
            one_liner = _extract_one_liner(raw)
            var_name, entries = _load_entries(yml_path)

            doc_path = Path("config") / domain / "vars" / f"{stem}.md"
            source_rel = f"config/{domain}/{yml_path.name}"

            page = _render_page(
                title=title,
                source_rel=source_rel,
                one_liner=one_liner,
                var_name=var_name,
                entries=entries,
                raw_yaml=raw,
            )

            with mkdocs_gen_files.open(doc_path.as_posix(), "w") as f:
                f.write(page)
            mkdocs_gen_files.set_edit_path(doc_path.as_posix(), source_rel)


main()
