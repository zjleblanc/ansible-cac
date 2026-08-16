# Changelog format reference

Read the project's existing changelog first. Use these patterns only when no file exists or entries are inconsistent.

This repo's `CHANGELOG.md` uses dated Keep a Changelog headers (`## YYYY-MM-DD — Brief summary`) with `### Added` / `### Changed` / `### Fixed`. New ansible-cac entries that create CaC resources also include a high-level automation paragraph and an HTML resources table under `### Added`.

## Detecting format

| Signal | Format |
|--------|--------|
| `**Short description:**`, `**Author:**`, `**Description:**` | Labeled fields (see below) |
| `### Added`, `### Changed`, `### Fixed` under `## YYYY-MM-DD — …` | Dated Keep a Changelog (preferred default) |
| `### Added`, `### Changed`, `### Fixed` under `## YYYY-MM-DD` (no summary) | Legacy dated Keep a Changelog — keep old entries; use summary headers for new ones |
| `### Added`, `### Changed`, `### Fixed` under `## [version]` | Versioned Keep a Changelog |
| `- **YYYY-MM-DD** — summary` or bullet under date headers | Simple dated list |
| `[Unreleased]` section at top | Keep a Changelog unreleased workflow — use only if the project already does |

Always mirror whatever the file already uses for **body** structure (categories, labels, bullets). For **headers**, use `## YYYY-MM-DD — Brief summary` on new entries.

## Header convention

Every new entry uses a two-part header:

```markdown
## YYYY-MM-DD — Brief summary of this change batch
```

- **Date:** commit date (`YYYY-MM-DD`).
- **Summary:** short, outcome-focused headline (roughly 5–12 words). Not a file list.
- **Details:** everything else goes **below** the header — high-level description, then categories, table, bullets, or labeled fields.

### Multiple entries on the same day

When two or more unrelated change batches land on the same date, add **separate** sections — same date, **different** summaries:

```markdown
## 2026-06-05 — Add configuration item detail page

### Added
- ...

## 2026-06-05 — Fix sidebar scroll layout

### Changed
- ...
```

Do not merge unrelated batches into one section just because they share a date.

## ansible-cac entry template (preferred in this repo)

```markdown
## YYYY-MM-DD — Brief summary

One to three sentences: the general automation this batch adds — what it does
and why it exists. Operator/demo outcome, not a file list.

### Added

<table>
<thead>
<tr>
<th>Resource type</th>
<th>Name</th>
<th>Description</th>
<th>Labels</th>
<th>Definition</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="2">Job template</td>
<td>Example // Create Thing</td>
<td>Short description at most one hundred characters.</td>
<td>Cloud</td>
<td><a href="config/cloud/job_templates.yml#L12-L40">📄 config</a></td>
</tr>
<tr>
<td>Example // Delete Thing</td>
<td>Another short description.</td>
<td>Cloud</td>
<td><a href="config/cloud/job_templates.yml#L41-L60">📄 config</a></td>
</tr>
<tr>
<td>Workflow job template</td>
<td>Example // Thing Lifecycle</td>
<td>Orchestrates create then delete for the demo.</td>
<td>Cloud</td>
<td><a href="config/cloud/workflow_job_templates.yml#L4-L80">📄 config</a></td>
</tr>
</tbody>
</table>

- Non-resource additions only (README, skills, scripts). Omit this list if none.

### Changed
- ...

### Fixed
- ...
```

Omit the table when nothing new was created under `config/`. Omit empty `### Changed` / `### Fixed` / extra `### Added` bullets.

### Resource type display names

Use these strings in the type column (and for sort). Map from the CaC variable / file via `.cursor/skills/cac-parser/resource-map.md`.

| Variable prefix | Display name |
|-----------------|--------------|
| `aap_organizations` | Organization |
| `aap_teams` | Team |
| `aap_user_accounts` | User |
| `ah_groups` | Hub group |
| `ah_roles` | Hub role |
| `ah_users` | Hub user |
| `controller_credential_input_sources` | Credential input source |
| `controller_credential_types` | Credential type |
| `controller_credentials` | Credential |
| `controller_execution_environments` | Execution environment |
| `controller_groups` | Group |
| `controller_inventories` | Inventory |
| `controller_inventory_sources` | Inventory source |
| `controller_labels` | Label |
| `controller_notifications` | Notification template |
| `controller_projects` | Project |
| `controller_schedules` | Schedule |
| `controller_templates` | Job template |
| `controller_workflows` | Workflow job template |
| `eda_credentials` | EDA credential |
| `eda_event_streams` | EDA event stream |
| `eda_projects` | EDA project |
| `eda_rulebook_activations` | EDA rulebook activation |
| `gateway_authenticator_maps` | Authenticator map |
| `gateway_authenticators` | Authenticator |
| `hub_collection_remotes` | Hub collection remote |
| `hub_ee_registries` | Hub EE registry |
| `hub_ee_repositories` | Hub EE repository |

If a new variable family appears, use the singular title from `docs/key_ordering.md`.

### Table rules

- **Created only:** new list entries in `config/<domain>/*.yml`. Not edits to existing entries.
- **Sort:** type display name A–Z (case-insensitive), then `name` A–Z (case-insensitive). Then apply `rowspan` on each type block.
- **Type cell:** first row of the group gets `<td rowspan="N">…</td>`; following rows of that type omit the type `<td>`. `rowspan="1"` is a normal `<td>` (no rowspan attribute).
- **Description:** prefer YAML `description`. Else infer one line from name/playbook/conversation. If longer than 100 characters, keep 99 characters and append `…`.
- **Labels:** comma-separated YAML label names; `—` when absent (typical for `config/common/`).
- **Definition link:** relative from repo root; fragment is the list item's line range. Link text is exactly `📄 config`.
- **HTML:** no blank lines inside `<table>…</table>`. One blank line before and after.

## Labeled-fields template

```markdown
---

## YYYY-MM-DD — One-line summary

**Author:** [git config user.name]

**Description:**

One or more paragraphs: what changed, why, and user-visible impact. Prose over file lists.

---
```

(`**Short description:**` may appear in older entries; new entries put the summary in the `##` header instead.)

## Dated Keep a Changelog template (default for new changelogs)

```markdown
## YYYY-MM-DD — Brief summary

### Added
- ...

### Changed
- ...

### Fixed
- ...
```

Use the commit date for `YYYY-MM-DD`. Add a new section for each distinct change batch; newest first.

## Keep a Changelog with [Unreleased] (only if project already uses it)

```markdown
## [Unreleased]

### Added
- ...

### Changed
- ...

### Fixed
- ...
```

Move items from `[Unreleased]` to a dated/summary section when the user cuts a release:

```markdown
## YYYY-MM-DD — Release summary

### Added
- ...
```

## Minimal fallback

```markdown
## YYYY-MM-DD — Brief summary

Details of what changed, in complete sentences.
```

After the first entry, follow the pattern that entry establishes.
