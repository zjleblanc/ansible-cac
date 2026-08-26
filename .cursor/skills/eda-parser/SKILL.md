---
name: eda-parser
description: Export and convert an Event-Driven Ansible (EDA) API resource into ansible-cac `config/aiops/` YAML. Hits the EDA API directly (auth via AAP_HOSTNAME/AAP_USERNAME/AAP_TOKEN) or accepts a pasted payload, resolves EDA API ref objects / `_id` fields to name strings, normalizes rulebook-activation event stream mappings, omits `ansible.eda` module defaults, and applies key_ordering.md. Use when the user asks to export/pull/discover an EDA resource, pastes an EDA API JSON/YAML object (project, credential, credential type, credential input source, decision environment, event stream, rulebook activation), or asks to add an EDA resource into config/.
disable-model-invocation: true
---

# eda-parser — EDA API payload → ansible-cac

Export and convert a single Event-Driven Ansible API resource object into a list entry ready for this repo's `config/aiops/` layout. There is no EDA MCP server in this workspace — exporting happens via direct API calls (see below), and conversion works from that JSON/YAML.

## Required reading (before converting)

1. [AGENTS.md](../../../AGENTS.md) — domains, wildcard suffixes, placement rules.
2. [key_ordering.md](key_ordering.md) — canonical key order for EDA resource types.
3. [resource-map.md](resource-map.md) — API type → file / var name, ref-object unwrap, defaults to omit.
4. [api-reference.md](api-reference.md) — export endpoints, auth, pagination, list vs retrieve, recommended export order.

Do not invent secrets. Credential `inputs` that contain secrets should use `{{ eda_credential_* }}` vault placeholders and call out any new vars for [`vars/eda_secrets.redacted.yml`](../../../vars/eda_secrets.redacted.yml).

**The EDA API never exposes real secret values** — credential `inputs` fields marked `secret: true` in the credential type schema always come back as the literal string `$encrypted$`, whether from a create/update payload or a read response. This is true for discovery/reconciliation flows just as much as one-off conversions: there is no way to recover a live secret value from the API. See "Secrets standards" under step 3 for the full handling rule.

## Exporting from the EDA API

When the user asks to export/pull/discover an EDA resource (rather than pasting one directly), hit the
API yourself instead of asking them to paste JSON.

**Prerequisites** — assume these environment variables are already set in the shell:

| Var | Meaning |
|---|---|
| `AAP_HOSTNAME` | Gateway hostname (no scheme), e.g. `aap.example.com` |
| `AAP_USERNAME` | Platform username (reference only) |
| `AAP_TOKEN` | Bearer token for the Gateway/EDA API |

If any are unset, ask the user to set them rather than requesting credentials directly.

**Quick export patterns:**

```bash
# List (discovery / find an ID) — add filters like ?name=... to narrow results
curl -sk "https://${AAP_HOSTNAME}/api/eda/v1/activations/?page_size=100" \
  -H "Authorization: Bearer ${AAP_TOKEN}" | python3 -m json.tool

# Retrieve by ID (prefer this for conversion — embeds ref objects as names)
curl -sk "https://${AAP_HOSTNAME}/api/eda/v1/activations/42/" \
  -H "Authorization: Bearer ${AAP_TOKEN}" | python3 -m json.tool
```

Swap `activations` for `projects`, `eda-credentials`, `credential-types`, `credential-input-sources`,
`decision-environments`, `event-streams`, or `rulebooks` as needed — see
[api-reference.md](api-reference.md) for the full endpoint catalog per resource type.

**List vs retrieve:** list endpoints return `_id` integers; retrieve-by-ID endpoints embed full ref
objects with names. Always retrieve by ID for the object(s) you're actually converting — only use list
for discovery or bulk reconciliation across a whole file.

**Export order (dependency-first)**, so every referenced name is already known: credential types → EDA
credentials (+ input sources) → projects → decision environments → event streams → rulebooks (for
source names) → rulebook activations. Full detail in [api-reference.md](api-reference.md).

Never print, log, or write `AAP_TOKEN` into any file — treat it as a live secret for whatever platform
is being exported from.

## Workflow

Copy this checklist and track it:

```
- [ ] 1. Identify resource type
- [ ] 2. Confirm domain (aiops by default)
- [ ] 3. Normalize API shape → CaC fields
- [ ] 4. Resolve relationships (project/rulebook/DE/credentials/event streams)
- [ ] 5. Drop omit-able defaults
- [ ] 6. Apply canonical key order
- [ ] 7. Emit placement + YAML (write only if asked)
```

### 1. Identify resource type

Accept JSON or YAML for one object (or a one-item `results` list — unwrap to the object).

Detect type from, in order:

1. User statement ("this is a rulebook activation").
2. API URL path (`/projects/`, `/eda-credentials/`, `/credential-types/`, `/credential-input-sources/`, `/decision-environments/`, `/event-streams/`, `/activations/`).
3. Discriminating fields:
   - `rulebook_id` / `rulebook` / `decision_environment_id` / `is_enabled` → rulebook activation
   - `image_url` → decision environment
   - `credential_type_id` / `credential_type` + `inputs` (and no `image_url`) → EDA credential
   - `inputs` + `injectors` (no `credential_type` ref) → credential type
   - `source_credential` + `target_credential` → credential input source
   - `eda_credential_id` / `eda_credential` + `test_mode` / `additional_data_headers` → event stream
   - `url` (git) + `scm_type` → project

If ambiguous, ask — do not guess between closely related types (e.g. EDA credential vs. Controller credential; both use `credential_type` + `inputs`, but EDA payloads come from `/eda-credentials/` paths or are explicitly scoped to EDA).

Map to the CaC variable family via [resource-map.md](resource-map.md).

### 2. Confirm domain

All EDA component resources in this repo currently live under `config/aiops/` (see [config/aiops/README.md](../../../config/aiops/README.md)). Unless the user says otherwise, place new EDA resources there with the `_aiops` suffix.

If the user is modeling a genuinely different domain's EDA usage (e.g. a new domain that also needs its own EDA project), follow the same placement rules as [cac-parser](../cac-parser/SKILL.md) — shared across domains → `common`-style consideration doesn't apply here since EDA has no `common` precedent yet; ask before introducing a new domain suffix for `eda_*` vars.

Target path pattern: `config/aiops/<file>.yml`
Variable: `eda_<type>_aiops` (never the unsuffixed base list).

### 3. Normalize API shape → CaC fields

The EDA API has two payload shapes that both need to resolve to **name strings** for CaC — never keep raw IDs or embedded ref objects:

- **Create/update payloads** use `_id` integer suffixes: `organization_id`, `decision_environment_id`, `rulebook_id`, `eda_credential_id`, `credential_type_id`, `source_credential`, `target_credential`.
- **Read responses** embed ref objects: `organization: {id, name}`, `project: {id, name, url, ...}`, `decision_environment: {id, name, image_url, ...}`, `credential_type: {id, name, namespace, kind}`, `rulebook: {id, name}`, `eda_credential: {id, name, ...}`.

Resolve both to the string the payload (or the user) provides for `.name`, using the **`ansible.eda` module parameter name**, which is not always the API field name:

| API field (either shape) | CaC field (module param) |
|---|---|
| `organization` / `organization_id` | `organization` |
| `project` (ref) | `project` |
| `rulebook` (ref) / `rulebook_id` | `rulebook` (module wants the rulebook **filename**, e.g. `datadog_event_stream.yml`, not the DB name) |
| `decision_environment` (ref) / `decision_environment_id` | `decision_environment` |
| `credential_type` (ref) / `credential_type_id` | `credential_type` |
| `eda_credential` (ref) / `eda_credential_id` | `credential_name` (event streams) or list entry in `eda_credentials` (activations) |
| `credential` (DE/project registry or SCM auth) | `credential` |
| `source_credential` / `target_credential` | same names, resolved to credential name strings |
| `is_enabled` (activation) | `enabled` |
| `extra_var` (activation, YAML string) | `extra_vars` (parse into a dict) |

See the full unwrap cheat sheet in [resource-map.md](resource-map.md).

**Rulebook activation event streams:** the API stores the source↔stream pairing as a `source_mappings` JSON string on the activation, and returns full `event_streams: [EventStreamOut, ...]` objects on read. Convert to the CaC list-of-dicts shape used by `ansible.eda.rulebook_activation`:

```yaml
event_streams:
  - event_stream: DataDog Event Stream
    source_name: DataDog Event Source
```

Each entry has `event_stream` (name) and either `source_name` (string, matches the rulebook's source name) or `source_index` (int) — never both. If only `source_mappings` JSON is given, decode it and resolve the event stream ID to its name; if a rulebook payload/listing is also available, prefer the source's declared name from `rulebooks/{id}/sources/`.

**Rulebook activation credentials:** API `eda_credentials` is a list of integers (create/update) or full `EdaCredential` objects (read). CaC is a flat list of name strings:

```yaml
eda_credentials:
  - Autodotes Controller
```

**Secrets standards:** never copy live secret values (`inputs` on credentials, `test_headers`/`test_content` on event streams) into config — the API returns `$encrypted$` for these fields anyway, so there is nothing to copy.

- For every credential `inputs` field marked `secret: true` in the credential type's schema, emit a `{{ eda_credential_<descriptive_name> }}` vault placeholder (e.g. `{{ eda_credential_dynatrace_token }}`), never a literal value.
- Add every new vault var to [`vars/eda_secrets.redacted.yml`](../../../vars/eda_secrets.redacted.yml) with the placeholder value `"secret"` — this file is committed and documents the expected shape of `vars/eda_secrets.yml`.
- Never write to or infer real values for `vars/eda_secrets.yml` — that file is vaulted, gitignored, and the user populates it themselves with real values before applying.
- Non-secret input fields (URLs, usernames, `auth_type`, `http_header_key`, `verify_ssl`, `audience`, `jwks_url`, and similar) are written as literal values, not vault refs — only fields the credential type schema marks `secret: true` need a placeholder.

### 4. Resolve relationships

Before finalizing, verify referenced objects exist (or will be added) in `config/aiops/`:

```
Rulebook Activation
  → Project (eda_projects_aiops)
  → Rulebook (filename inside the Project's repo — not a separate CaC object)
  → Decision Environment (eda_decision_environments_aiops, or "Default Decision Environment" if using the built-in one — no CaC entry needed for that)
  → EDA Credentials (eda_credentials_aiops, list of names)
  → Event Streams (eda_event_streams_aiops, list of {event_stream, source_name})

Event Stream → EDA Credential (credential_name)
Decision Environment → EDA Credential (optional; registry auth for image_url)
Project → EDA Credential (optional; SCM auth for private repos)
EDA Credential → Credential Type (credential_type name)
Credential Input Source → source_credential + target_credential (both EDA credential names)
```

If a referenced project/credential/credential type/decision environment/event stream is missing from `config/aiops/`, call it out as a follow-up (step 7) rather than inventing it. `"Default Decision Environment"` is a built-in AAP object — do not create a CaC entry for it.

### 5. Drop omit-able defaults

Use the `ansible.eda` module argument defaults in [resource-map.md](resource-map.md) (sourced from `plugins/modules/*.py` `DOCUMENTATION`) to decide what to omit. Common drops across EDA resources:

- Empty `description`, `""` string fields that restate "unset"
- `state: present` (module default)
- Rulebook activation: `restart_policy: on-failure`, `log_level: error`, `enabled: true`, `restart_on_project_update: false`, `enable_persistence: false`, `skip_audit_events: false` when `false`/default
- Event stream: `forward_events: false`, `headers: ""`
- Decision environment: `pull_policy: always`
- Project: `update_revision_on_launch: false`, `scm_update_cache_timeout: 0`
- Credential type: empty `inputs: {}` / `injectors: {}`

**Note:** this repo's existing `eda_rulebook_activations_aiops` entries **keep** `enabled: false` explicitly (all current demo activations are disabled by default) — match that convention when converting new activations rather than omitting `enabled` just because a value is "default-like"; only omit when the value truly matches the module default (`true`) or the peer entries in the target file omit it.

Always drop pure API noise regardless of resource type: `id`, `url` (unless it's the actual `project.url` git repo, which is required), `created_at`, `modified_at`, `created_by`, `modified_by`, `edited_at`, `edited_by`, `managed`, `git_hash`, `import_state`, `import_error`, `status`, `status_message`, `restart_count`, `current_job_id`, `rules_count`, `rules_fired_count`, `ruleset_stats`, `restarted_at`, `owner`, `test_content*`, `test_error_message`, `test_headers`, `events_received`, `last_event_received_at`, `log_tracking_id`, `awx_token_id`, `scm_type` (read-only, always `git`), `references`, `namespace`/`kind` (managed credential-type metadata), `proxy` (unless explicitly set).

### Rulebook activation CaC conventions

This repo's `eda_rulebook_activations_aiops` entries follow two deliberate conventions that **always override the live platform value**, regardless of what a discovery/reconciliation pass finds running:

- **`enabled: false`** — every activation ships disabled by default; a human enables it on the platform after verifying the configuration. Set this explicitly even though the running platform activation is `is_enabled: true` and even though the module default is `true`.
- **`restart_policy: never`** — CaC activations use `never` so an initial apply never triggers an automatic restart loop. Set this explicitly even if the platform shows `restart_policy: on-failure` (the module default).

When reconciling CaC against a live platform (discovery mode), do **not** update `enabled` or `restart_policy` to match the running platform's current values — keep the repo convention. All other behavioral/relationship fields (`log_level`, `extra_vars`, `event_streams`, `eda_credentials`, `rulebook`, `decision_environment`) should be updated to match what's actually configured on the platform.

### 6. Apply canonical key order

Reorder remaining keys to match [key_ordering.md](key_ordering.md) for the target variable family. Omit absent keys; do not add keys just to fill the template.

### 7. Emit result

Default: **do not write files** unless the user asks to add/append.

Output:

1. **Placement** — file path, variable name, one-line apply command matching the file's header style (see [config/aiops/README.md](../../../config/aiops/README.md)).
2. **Rationale** — one or two sentences.
3. **YAML entry** — a single list item (`- name: …`) ready to paste under the target variable (not a full file rewrite).
4. **Follow-ups** — missing deps (project/credential/credential type/decision environment/event stream), vault vars needed in `vars/eda_secrets.redacted.yml`, and any ambiguous type/domain decisions.

If the user asks to apply: append the entry to the correct list in the vars file; preserve the file one-liner and `---`; do not reorder unrelated entries unless asked; update [config/aiops/README.md](../../../config/aiops/README.md)'s file table only when adding a **new** YAML file.

**Orphaned entries policy:** when performing API-driven discovery/reconciliation across an entire `config/aiops/` file (rather than converting a single pasted object) and a CaC entry is found that no longer exists on the platform, **never remove it automatically**. Always list orphaned entries as a follow-up with context (what it was, what may have replaced it, e.g. a similarly-purposed new resource) and explicitly ask the user whether to remove or keep each one before touching the file.

## Output template

```markdown
## Placement
- File: `config/aiops/<file>.yml`
- Variable: `eda_<type>_aiops`
- Apply: `ansible-playbook pb_aap_config.yml -e "domains=aiops" -e "skip_common=true" --tags <resource_tag>`

## Rationale
<why this resource type / any relationship notes>

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

**Input (API rulebook activation read excerpt):** `decision_environment: {name: "Default Decision Environment"}`, `project: {name: "EDA Demos"}`, `rulebook: {name: "datadog_event_stream.yml"}`, `is_enabled: false`, `event_streams: [{name: "DataDog Event Stream", ...}]`, `source_mappings: "[{\"rulebook_source\": \"DataDog Event Source\", ...}]"`, `eda_credentials: [{name: "Autodotes Controller", ...}]`, `restart_policy: "never"`, `log_level: "debug"`.

**Output:** `name` / `description` / `organization` / `project: EDA Demos` / `rulebook: datadog_event_stream.yml` / `decision_environment: Default Decision Environment` / `event_streams: [{event_stream: DataDog Event Stream, source_name: DataDog Event Source}]` / `eda_credentials: [Autodotes Controller]` / `enabled: false` (kept — matches repo convention) / `log_level: debug` / `restart_policy: never` — no `is_enabled`, no ref-object dumps, no `source_mappings` raw string.

## Additional resources

- [api-reference.md](api-reference.md) — export endpoints, auth, pagination, list vs retrieve, recommended export order
- [resource-map.md](resource-map.md) — type map, ref-object unwrap rules, `ansible.eda` module defaults
- [key_ordering.md](key_ordering.md) — per-type key order for EDA resources
- [AGENTS.md](../../../AGENTS.md) — placement and naming
- [config/aiops/README.md](../../../config/aiops/README.md) — file table and apply one-liners
- `ansible.eda` module docs (`plugins/modules/*.py` under the installed collection) for omit-able defaults
