# Changelog format reference

This repo's `CHANGELOG.md` uses dated headers with an automation summary and optional Domains / Resources / Secrets sections. Author **new** entries with this template. Do not rewrite older bullet-only entries unless the user asks.

## Header

```markdown
## YYYY-MM-DD — Brief summary of this change batch
```

- **Date:** commit date (`YYYY-MM-DD`).
- **Summary:** short, outcome-focused headline (roughly 5–12 words). Not a file list.
- **Details:** everything else goes **below** the header.

### Multiple entries on the same day

Unrelated batches on the same date get **separate** sections — same date, **different** summaries:

```markdown
## 2026-06-05 — Add configuration item detail page

…

## 2026-06-05 — Fix sidebar scroll layout

…
```

Do not merge unrelated batches into one section just because they share a date.

## Entry template

```markdown
## YYYY-MM-DD — Brief summary

One to three sentences: the general automation this batch adds — what it does
and why it exists. Operator/demo outcome, not a file list.

### Domains

_Only when a new domain folder is created_
Brief description of each **new** domain and a link to its README.

### Resources

| Type | Name | Description | Domain | |
|------|------|-------------|--------|------------|
| Job template | Example // Create Thing | Short description at most one hundred characters. | cloud | [🕵️](config/cloud/job_templates.yml#L12-L40) |
| | Example // Delete Thing | Another short description. | cloud | [🕵️](config/cloud/job_templates.yml#L41-L60) |
| Workflow job template | Example // Thing Lifecycle | Orchestrates create then delete for the demo. | cloud | [🕵️](config/cloud/workflow_job_templates.yml#L4-L80) |

### Secrets

| Component | Variable | Credential |
|-----------|----------|------------|
| Controller | controller_secrets_example | [Example Credential](config/cloud/credentials.yml#L12-L40) |
| | controller_secrets_example_two | [Example Credential Two](config/cloud/credentials.yml#L12-L40) |
| EDA | eda_secrets_example | [Example EDA Credential](config/aiops/eda_credentials.yml#L12-L40) |
| | eda_secrets_example_two | [Example EDA Credential Two](config/aiops/eda_credentials.yml#L12-L40) |

### Changed
- ...

### Fixed
- ...
```

Omit `### Domains`, `### Resources`, or `### Secrets` when empty. Omit empty `### Changed` / `### Fixed`. Do not add extra bullets that duplicate table rows.

### Domains section

Include **only** when this batch introduces a **new** domain under `config/` (new folder + typically `pb_aap_config.yml` include, domain label, and `config/<domain>/README.md`). Do **not** list domains that already existed and were only updated with new/changed resources.

For each newly created domain:

- One short sentence (or the README title line) describing the domain.
- Link to `config/<domain>/README.md`.

Example (new domain only):

```markdown
### Domains

- [observability](config/observability/README.md) — Observability demos and related Controller/EDA resources.
```

### Secrets section

Include only **new** placeholders added under `vars/*_secrets.redacted.yml` (or equivalent) in this batch.

| Column | Source |
|--------|--------|
| Component | `Controller`, `EDA`, `Hub`, etc. from the secrets file / var prefix. |
| Variable | Vault variable name (e.g. `controller_credential_servicenow_openflake`). |
| Credential | Link to the CaC credential entry that references the var; link text is the credential `name`. |

Sort by Component A–Z, then Variable A–Z. Leave the Component cell empty for the 2nd+ row of the same component (same pattern as Type in Resources).

## Resource type display names

Use these strings in the Type column (and for sort). Map from the CaC variable / file via `.cursor/skills/cac-parser/resource-map.md`.

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

## Resources table rules

- **Created only:** new list entries in `config/<domain>/*.yml`. Not edits to existing entries.
- **Sort:** type display name A–Z (case-insensitive), then `name` A–Z (case-insensitive), so each type is one contiguous block.
- **Type cell:** write the display name on the **first** row of a type group; leave the Type cell **empty** on the 2nd+ consecutive row of the same type. Do not use HTML `rowspan` / `colspan` (GitHub ignores them).
- **Description:** prefer YAML `description`. Else infer one line from name/playbook/conversation. If longer than 100 characters, keep 99 characters and append `…`.
- **Domain:** the `config/<domain>/` folder that owns the definition (e.g. `cloud`, `common`, `servicenow`). Do **not** use Controller `labels` — not all resources are labeled.
- **Definition link:** relative from repo root; fragment is the list item's line range. Link text is exactly `🕵️` (e.g. `[🕵️](config/cloud/job_templates.yml#L42-L71)`).
- **Markdown tables only** — GitHub Flavored Markdown pipe tables.

Insert new changelog sections **newest first** (right after `# Changelog`).
