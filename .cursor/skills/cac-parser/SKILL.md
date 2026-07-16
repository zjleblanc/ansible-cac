---
name: cac-parser
description: Convert an AAP/Controller/EDA/Hub/Gateway API resource payload into ansible-cac domain YAML. Chooses domain and vars file, normalizes nested API objects to names, omits role/module defaults from infra.aap_configuration and ansible.* collections listed in collections/requirements.yml, and applies docs/key_ordering.md. Use when the user pastes an AAP API JSON/YAML object, export payload, or asks to add a Controller/EDA/Hub resource into config/.
disable-model-invocation: true
---

# cac-parser — AAP API payload → ansible-cac

Convert a single AAP API (or export) resource object into a list entry ready for this repo’s domain CaC layout.

## Required reading (before converting)

1. [AGENTS.md](../../../AGENTS.md) — domains, wildcard suffixes, placement rules (common vs domain).
2. [docs/key_ordering.md](../../../docs/key_ordering.md) — canonical key order for the target variable type.
3. [resource-map.md](resource-map.md) — API type → file / var name, nested-field unwrap, defaults to omit.

Do not invent secrets. Credential `inputs` that contain secrets should use `{{ vault_var }}` placeholders and call out any new vars for `vars/*_secrets.redacted.yml`.

## Workflow

Copy this checklist and track it:

```
- [ ] 1. Identify resource type
- [ ] 2. Choose domain + vars file
- [ ] 3. Normalize API shape → CaC fields
- [ ] 4. Drop omit-able defaults
- [ ] 5. Apply canonical key order
- [ ] 6. Emit placement + YAML (write only if asked)
```

### 1. Identify resource type

Accept JSON or YAML for one object (or a one-item `results` list — unwrap to the object).

Detect type from, in order:

1. User statement (“this is a job template”).
2. API URL / `type` / `related` hints (`job_template`, `workflow_job_template`, `project`, `credential`, …).
3. Discriminating fields (`playbook` → job template; `workflow_nodes` → workflow; `scm_type`+`scm_url` → project; `credential_type`+`inputs` → credential; `rulebook` → EDA activation; etc.).

Map to the CaC variable family via [resource-map.md](resource-map.md). If ambiguous, ask — do not guess between closely related types.

### 2. Choose domain and vars file

Domains: `common`, `cloud`, `networking`, `linux`, `windows`, `hashi`, `aiops`, `servicenow`, `apps`, `aap`, `hub`.

Placement rules (from AGENTS.md):

| Question | Place in |
|----------|----------|
| Referenced by JTs/workflows/inventory sources in **2+ domains**? | `config/common/` (`_<domain>` suffix `_common`) |
| Used by **one** domain only? | That domain folder with `_<domain>` suffix |
| Schedule? | Same domain as the `unified_job_template` it targets |
| Inventory source / group? | With the inventory’s domain (or `common` if inventory is shared); prefer use-case domain for groups on shared inventories |
| AIOps JT/workflow? | `aiops`; include `AIOps` in `labels` |

Hints for domain when not stated:

- Name / labels / project name (`AWS //`, `Vault //`, `EDA //`, `PAH //`, `Cisco`, `Windows`, `ServiceNow`, …).
- Existing similar resources already in `config/<domain>/`.
- User-stated product area.

If still unclear, ask **one** clarifying question (domain only). Prefer suggesting the best guess with rationale.

Target path pattern: `config/<domain>/<file>.yml`  
Variable: `<prefix>_<domain>` (never the unsuffixed base list).

### 3. Normalize API shape → CaC fields

Transform Controller/Gateway/EDA/Hub API objects into the flat dict shape used in this repo:

- **Named refs:** unwrap `{name: X, …}` / summary objects to the string `X` for `organization`, `project`, `inventory`, `execution_environment`, `credential`, `credential_type`, `unified_job_template`, `source_project`, etc.
- **Lists of named refs:** `credentials`, `labels`, `galaxy_credentials`, notification lists → list of name strings.
- **Drop API-only noise:** `id`, `url`, `related`, `summary_fields` (after extracting names), `created`, `modified`, `uuid`, `natural_key`, capability flags, counts, `type` (API type string), `redirect_*`, encrypted `$encrypted$` placeholders when the CaC entry should use vault vars instead.
- **Surveys:** keep `survey_enabled` + `survey_spec` when present and meaningful; drop empty survey shells if survey is disabled and spec is empty.
- **Workflows:** keep `workflow_nodes` structure expected by `infra.aap_configuration` (identifier / related / unified_job_template with name+type+organization), not raw API graph dumps with numeric IDs only — resolve names when the payload provides them.
- **Secrets:** never copy live secret values into config; use existing `{{ controller_credential_* }}` / vault patterns or `REPLACE_ME` + note.

Match field names already used in sibling entries in the target file (e.g. `controller_templates_*` not `job_templates`).

### 4. Drop omit-able defaults

API exports are verbose. Omit keys whose value matches a **documented default** (or an effective no-op empty) from the collections this repo depends on — see [collections/requirements.yml](../../../collections/requirements.yml).

Consult defaults in this order:

1. **`infra.aap_configuration`** dispatched role — `roles/<role>/tasks/main.yml` (`default(omit)` / `*_enforce_defaults` paths). This repo usually leaves enforce-defaults off, so unset keys are omitted.
2. **`ansible.*` collections listed in `collections/requirements.yml`** (currently `ansible.controller`, `ansible.platform`, `ansible.hub`, `ansible.eda`) — module `DOCUMENTATION` / argument specs under `plugins/modules/` for the resource being converted. These are the modules the configuration roles call.

Ignore other requirement entries (`infra.ee_utilities`, `infra.aap_utilities`, `containers.podman`) for omit decisions unless the payload is clearly for those collections.

See omit tables in [resource-map.md](resource-map.md). Common job-template drops:

- `job_type: run`
- `job_slice_count: 1`
- `verbosity: 0`, `forks: 0`, `timeout: 0`
- any `ask_*: false`
- `allow_simultaneous: false`, `use_fact_cache: false`, `survey_enabled: false`
- empty strings / empty lists / empty dicts that only restate defaults (`limit: ""`, `extra_vars: {}`, `labels: []`, …)

**Keep** non-default values even if noisy (`ask_variables_on_launch: true`, custom verbosity, real `extra_vars`, labels, surveys).

When unsure, open the matching role task and the matching `ansible.*` module docs under the installed collections (typical path: `~/.ansible/collections/ansible_collections/`).

### 5. Apply canonical key order

Reorder remaining keys to match [docs/key_ordering.md](../../../docs/key_ordering.md) for that variable family. Omit absent keys; do not add keys just to fill the template.

### 6. Emit result

Default: **do not write files** unless the user asks to add/append.

Output:

1. **Placement** — domain, file path, variable name, one-line apply command matching the file’s header style.
2. **Rationale** — one or two sentences (shared → common, label/name cues, etc.).
3. **YAML entry** — a single list item (`- name: …`) ready to paste under the target variable (not a full file rewrite).
4. **Follow-ups** — missing deps (project/credential/inventory/EE/label that must exist in domain or common), vault vars, or AIOps label reminder.

If the user asks to apply: append the entry to the correct list in the vars file; preserve the file one-liner and `---`; do not reorder unrelated entries unless asked; update the domain README file table only when adding a **new** YAML file.

## Output template

```markdown
## Placement
- Domain: `<domain>`
- File: `config/<domain>/<file>.yml`
- Variable: `<prefix>_<domain>`
- Apply: `ansible-playbook pb_aap_config.yml --tags ...`

## Rationale
<why this domain / file>

## Entry
```yaml
- name: ...
  organization: ...
  ...
```

## Follow-ups
- ...
```

## Examples

**Input (API job template excerpt):** playbook + project summary_fields, `job_type: run`, `job_slice_count: 1`, many `ask_*: false`, `labels` as related list.

**Output:** `name` / `organization` / `description` / `labels` (name list) / `project` / `playbook` / `inventory` / `execution_environment` / `credentials` — no default `job_type` / `job_slice_count` / false `ask_*`. Domain from name prefix or labels (e.g. `AWS //` → `cloud`).

## Additional resources

- [resource-map.md](resource-map.md) — type map, unwrap rules, omit defaults
- [docs/key_ordering.md](../../../docs/key_ordering.md) — per-type key order
- [AGENTS.md](../../../AGENTS.md) — placement and naming
- [collections/requirements.yml](../../../collections/requirements.yml) — collection set for this repo
- `infra.aap_configuration` role tasks + `ansible.controller` / `ansible.platform` / `ansible.hub` / `ansible.eda` module docs for omit-able defaults
