---
name: changelog
description: Add CHANGELOG.md entries for ansible-cac Configuration as Code changes, including a short high-level description of the automation and a sorted Markdown table of created AAP resources (type, name, description, domain, config permalink). Also suggest a succinct plain-text git commit message. Use when the user asks for a changelog entry, release note, commit message, or to document current config/ changes before committing.
---

# Changelog and Commit Message

Document pending work in this repo's `CHANGELOG.md` and give the user a ready-to-use commit message. Do not commit unless the user explicitly asks.

New entries follow the ansible-cac format in [format.md](format.md): dated summary header, automation blurb, optional Domains / Resources / Secrets sections, then `### Changed` / `### Fixed` as needed.

## Workflow

1. **Gather changes**
   - Run `git status` and `git diff` (staged and unstaged).
   - Skim `git log -8 --oneline` to match this repo's commit-message tone.
   - Use conversation context for intent the diff alone may not show.
   - From `config/` diffs, collect **new** list entries (created resources) for the resources table.
   - From secrets diffs (`vars/*_secrets.redacted.yml`), collect new vault variable placeholders for the secrets table.

2. **Find the changelog**
   - Use `CHANGELOG.md` at the repo root.
   - If it is missing, ask whether to create it using [format.md](format.md).

3. **Match format**
   - Read the newest entry or two for tone, but **author new entries** per [format.md](format.md) (not older bullet-only `### Added` layouts).
   - Insert **newest first** (immediately after the `# Changelog` heading).

4. **Draft the entry**
   - One entry per logical change batch unless the user asks to split or combine.
   - **Header:** `## YYYY-MM-DD — Brief summary` — outcome-focused headline (not a file list).
   - **High-level description:** 1–3 sentences under the header on the automation (operator/demo outcome). For docs/tooling-only batches, describe that change in the same slot.
   - **### Domains** (optional): only when the batch **creates a new** `config/<domain>/` folder (plus playbook tag / label / README wiring). Do **not** list existing domains merely because resources were added under them.
   - **### Resources:** Markdown table of **created** CaC list entries (see [Resource table](#resource-table)). Omit the whole section when nothing new was created under `config/`.
   - **### Secrets:** Markdown table of new vault placeholders wired to credentials (see [format.md](format.md)). Omit when none.
   - Do **not** re-list table rows as bullets. Omit empty `### Changed` / `### Fixed`.
   - **Same day, different content:** unrelated work gets a **new** section with the same date and a **different** summary — do not merge into an existing same-day section.

5. **Write the commit message**
   - One line, plain text — **no markdown** (no backticks, bold, bullets, or quotes).
   - Match repo conventions from `git log`.
   - Default when unclear: imperative mood, sentence case, outcome-focused, ~72 chars when possible.
   - Summarize the **why/outcome**, not a file list.
   - Align with the section's brief summary in the changelog header.

6. **Resolve metadata**
   - **Date:** commit date (`YYYY-MM-DD`); use today when drafting before commit.

7. **Deliver**
   - Confirm the changelog was updated (or show the draft if the user only wanted text).
   - Give the commit message on its own line, copy-paste ready.

## Resource table

Include under `### Resources` only for **created** resources (new `- name:` list items under `config/`). Skip when the batch is docs/tooling only, or only changes/removes existing entries.

- **Changed** existing resources → `### Changed` bullets.
- **Removed** resources → `### Removed` bullets.

### Columns

| Column | Source |
|--------|--------|
| Type | Human-readable type on the first row of a group; leave empty for the 2nd+ row of the same type. Display names: [format.md](format.md). |
| Name | YAML `name` (or `username` for users). |
| Description | YAML `description`. If missing, one-line purpose from name/playbook/conversation. Max 100 characters; if longer, truncate and append `…`. |
| Domain | Config domain folder for the YAML file (`cloud`, `common`, `servicenow`, …) — not the Controller `labels` list. |
| Definition | Permalink to the list entry. Link text: `🕵️`. |

### Sort

1. Type display name, alphabetical (case-insensitive).
2. Then resource name, alphabetical (case-insensitive).

After sorting, leave Type empty on consecutive same-type rows (no HTML `rowspan` / `colspan`).

### Markup

GitHub Flavored Markdown pipe tables only.

Link target: relative path from repo root plus `#Lstart-Lend` covering the list item. Example: `[🕵️](config/cloud/job_templates.yml#L42-L71)`.

Do not bake a commit SHA. Relative `#L` links resolve on the branch.

Full template: [format.md](format.md).

## Commit message rules

| Do | Avoid |
|----|--------|
| Plain text, one line | Markdown, backticks, bullet lists |
| Outcome-focused | Raw file paths or "update X, Y, Z" |
| Match recent `git log` style | Inventing a new style mid-project |
| Align with the section summary | A message that contradicts the header |

## Split vs single entry

**Single entry** when changes are one feature/fix or ship together. One `## YYYY-MM-DD — Summary` section with all related details below.

**Multiple entries** when the user asks to split, or unrelated features have no shared release story — even on the **same day**, use separate sections with distinct summaries.

## Checklist

- [ ] `git diff` reviewed; entry reflects all meaningful changes
- [ ] High-level description sits under the header (automation outcome, not a file list)
- [ ] Created `config/` resources are in the sorted Markdown Resources table (empty Type for 2nd+ same type, 100-char descriptions, `🕵️` links); not duplicated as bullets
- [ ] New secrets placeholders are in the Secrets table when applicable
- [ ] Entry follows [format.md](format.md); newest first
- [ ] Header is `## YYYY-MM-DD — Brief summary`
- [ ] Unrelated same-day work gets its own section
- [ ] Brief summary and commit message align
- [ ] Commit message is plain text, no markup
- [ ] Did not run `git commit` unless explicitly requested

## Additional resources

- Entry template, resource-type display names, secrets table: [format.md](format.md)
