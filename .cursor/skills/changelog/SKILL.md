---
name: changelog
description: Add CHANGELOG.md entries for ansible-cac Configuration as Code changes, including a short high-level description of the automation and a sorted HTML table of created AAP resources (type, name, description, labels, config permalink). Also suggest a succinct plain-text git commit message. Use when the user asks for a changelog entry, release note, commit message, or to document current config/ changes before committing.
---

# Changelog and Commit Message

Document pending work in this repo's changelog and give the user a ready-to-use commit message. Do not commit unless the user explicitly asks.

This skill follows the same workflow as the user-wide changelog skill, with ansible-cac extras: a short automation summary and a table of **created** CaC resources.

## Workflow

1. **Gather changes**
   - Run `git status` and `git diff` (staged and unstaged).
   - Skim `git log -8 --oneline` to match this repo's commit-message tone.
   - Use conversation context for intent the diff alone may not show.
   - From `config/` diffs, collect **new** list entries (created resources) for the resources table.

2. **Find the changelog**
   - Use `CHANGELOG.md` at the repo root.
   - If it is missing, ask whether to create it or use the fallback in [format.md](format.md).

3. **Match existing format**
   - Read the top 2–3 entries and replicate structure, field labels, category headings (`### Added`, etc.), date format, and ordering exactly.
   - **Headers:** use `## YYYY-MM-DD — Brief summary` for new entries (date, em dash, one-line summary). Older entries may use date-only headers; do not rewrite them unless the user asks.
   - See [format.md](format.md) when no pattern exists.

4. **Draft the entry**
   - One entry per logical change batch unless the user asks to split or combine.
   - **Header:** `## YYYY-MM-DD — Brief summary` — the summary is a short headline of what this batch changes (outcome-focused, not a file list).
   - **High-level description:** immediately under the header, 1–3 sentences on the general automation being added (what it does for the operator/demo and why it exists). Not a file list. For non-automation batches (docs, tooling), describe that change in the same slot.
   - **Body:** details below that — category subsections (`### Added`, `### Changed`, `### Fixed`) matching the file's convention.
   - **Resources table:** when the batch creates one or more CaC list entries under `config/`, put the table under `### Added` (see [Resource table](#resource-table)). Do not also list those same resources as bullets.
   - Prefer a single entry when changes ship together; split only when themes are clearly unrelated.
   - **Same day, different content:** if an entry for today already exists but describes unrelated work, add a **new** section with the same date and a **different** summary — do not merge unrelated batches into one section.
   - Insert **newest first** per the file's convention (usually immediately after the `# Changelog` heading).

5. **Write the commit message**
   - One line, plain text — **no markdown** (no backticks, bold, bullets, or quotes).
   - Match repo conventions from `git log` (conventional commits, imperative sentence, etc.).
   - Default when unclear: imperative mood, sentence case, outcome-focused, ~72 chars when possible.
   - Summarize the **why/outcome**, not a file list.
   - Align with the section's brief summary in the changelog header.

6. **Resolve metadata**
   - **Date:** the commit date — use today's date (`YYYY-MM-DD`) when drafting before commit; match the format already used in the changelog.
   - **Author:** `git config user.name` unless the user specifies otherwise (include when the file uses labeled `**Author:**` fields).

7. **Deliver**
   - Confirm the changelog was updated (or show the draft if the user only wanted text).
   - Give the commit message on its own line, copy-paste ready.

## Resource table

Include this table only for **created** resources (new `- name:` list items under `config/`). Skip it when the batch is docs/tooling only, or only changes/removes existing entries.

- **Changed** existing resources stay as `### Changed` bullets.
- **Removed** resources stay as `### Removed` bullets.
- Non-resource additions (README, skills, scripts) stay as `### Added` bullets **after** the table.

### Columns

| Column | Source |
|--------|--------|
| Resource type | Human-readable type; **rowspan** all consecutive rows of the same type. Display names: [format.md](format.md). |
| Name | YAML `name` (or `username` for users). |
| Description | YAML `description`. If missing, one-line purpose from name/playbook/conversation. Max 100 characters; if longer, truncate and append `…`. |
| Labels | YAML `labels` joined with `, `. No labels → `—`. |
| Definition | Permalink to the list entry in CaC YAML. Link text: `📄 config`. |

### Sort

1. Resource type, alphabetical (case-insensitive), using the display name.
2. Then resource name, alphabetical (case-insensitive).

Group rowspan **after** sorting so each type is one contiguous block.

### Markup

GitHub Markdown tables cannot span cells. Use an **HTML** `<table>` with `rowspan` on the type column. Blank line before and after the table; **no** blank lines inside it.

Link target: relative path from `CHANGELOG.md` (repo root) plus a GitHub line fragment covering that list item (`#Lstart` or `#Lstart-Lend` from the `- name:` line through the last line of the entry). Example: `[📄 config](config/cloud/job_templates.yml#L42-L71)` inside `<a href="…">📄 config</a>`.

Do not bake a commit SHA (the entry is drafted before commit). Relative `#L` links resolve on the branch.

Full template and a filled example: [format.md](format.md).

## Commit message rules

| Do | Avoid (unless repo consistently uses them) |
|----|---------------------------------------------|
| Plain text, one line | Markdown, backticks, bullet lists |
| Outcome-focused | Raw file paths or "update X, Y, Z" |
| Match recent `git log` style | Inventing a new style mid-project |
| Align with the section summary | A message that contradicts the header |

## Split vs single entry

**Single entry** when changes are one feature/fix or ship together (e.g. feature + README + tests for same work). One `## YYYY-MM-DD — Summary` section with all related details below.

**Multiple entries** when:
- The user asks to split, or
- Unrelated features have no shared release story — even on the **same day**, use separate `## YYYY-MM-DD — Summary` sections with distinct summaries.

**Same-day rule:** multiple sections sharing a date are fine when each has different content. Do not append unrelated work to an existing same-day section; add a new header with a new summary instead.

## Checklist

- [ ] `git diff` reviewed; entry reflects all meaningful changes
- [ ] High-level description sits under the header (automation outcome, not a file list)
- [ ] Created `config/` resources are in the sorted HTML table (type rowspan, 100-char descriptions, `📄 config` links); not duplicated as bullets
- [ ] New entry follows the file's existing body format and sort order
- [ ] Header is `## YYYY-MM-DD — Brief summary` with details below (not `[Unreleased]`) unless the repo already uses unreleased sections
- [ ] Unrelated same-day work gets its own section, not merged into an existing one
- [ ] Brief summary / headline and commit message align
- [ ] Commit message is plain text, no markup
- [ ] Did not run `git commit` unless explicitly requested

## Additional resources

- Changelog format patterns, resource-type display names, and table template: [format.md](format.md)
