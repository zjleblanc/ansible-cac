---
name: hub-parser
description: Export and convert a Private Automation Hub (Galaxy/Pulp) API resource into ansible-cac config/hub YAML. Hits the Hub API through the AAP Gateway (AAP_HOSTNAME/AAP_USERNAME/AAP_TOKEN) or accepts a pasted payload, resolves Pulp hrefs to names, parses collection-remote requirements files, omits ansible.hub module defaults, and applies key_ordering.md. Use when the user asks to export, pull, or discover a Hub resource, pastes Galaxy or Pulp JSON/YAML (collection remote, collection repository, EE registry), or asks to add a Hub resource into config/. Collection namespaces are not converted; collection sync creates them.
disable-model-invocation: true
---

# hub-parser — Hub API payload → ansible-cac

Export and convert a single Private Automation Hub API object into a list entry for `config/hub/`. There is no Hub MCP server — exporting is a direct read of the Galaxy/Pulp API (see below). Conversion also works from pasted JSON/YAML.

Controller, Gateway, and EDA objects stay with [cac-parser](../cac-parser/SKILL.md) and [eda-parser](../eda-parser/SKILL.md).

## Required reading (before converting)

1. [AGENTS.md](../../../AGENTS.md) — domains, wildcard suffixes, placement.
2. [key_ordering.md](key_ordering.md) — canonical key order for Hub resource types.
3. [resource-map.md](resource-map.md) — API type → file / var / tag, href unwrap, defaults to omit.
4. [api-reference.md](api-reference.md) — export endpoints, auth, pagination, list vs retrieve.

Do not invent secrets. Token, password, and client-key fields use `{{ hub_var_* }}` placeholders. Document new vars in [`config/hub/vault.redacted.yml`](../../../config/hub/vault.redacted.yml) with mock values only. Never write `config/hub/vault.yml`.

**The Hub API does not return secret values.** Registry `write_only_fields[].is_set` and Pulp hidden fields (`token`, `password`, `client_key`, `proxy_password`) come back unset or redacted. There is nothing to copy. See step 3.

## Exporting from the Hub API

When the user asks to export, pull, or discover a Hub resource, call the API. Do not ask them to paste JSON first.

**Prerequisites** — assume these are already set:

| Var | Meaning |
|---|---|
| `AAP_HOSTNAME` | Gateway hostname (no scheme), e.g. `aap.example.com` |
| `AAP_USERNAME` | Platform username (reference only) |
| `AAP_TOKEN` | Bearer token for the Gateway |

If any are unset, ask the user to set them. Do not request the token value.

```bash
# List collection remotes (discovery)
curl -sk "https://${AAP_HOSTNAME}/api/galaxy/pulp/api/v3/remotes/ansible/collection/?name=community&limit=100" \
  -H "Authorization: Bearer ${AAP_TOKEN}" | python3 -m json.tool

# Retrieve one repository by Pulp href (after list)
curl -sk "https://${AAP_HOSTNAME}<pulp_href>" \
  -H "Authorization: Bearer ${AAP_TOKEN}" | python3 -m json.tool
```

Gateway installs expose Galaxy under `/api/galaxy/`. Confirm with `GET /api/` → `apis.galaxy` when the prefix is uncertain. Full catalog: [api-reference.md](api-reference.md).

**List vs retrieve:** Pulp list rows carry `pulp_href` and, on repositories, `remote` as an href. Filter with `?name=` to find the object, then GET the href when the list row is thin. Resolve every href to a name before emitting YAML.

**Export order:** collection remotes → collection repositories (remote name must already be known) → EE registries. Namespaces and EE repositories are read for context only — do not turn them into CaC unless the user explicitly overrides the rules in step 2.

Never print, log, or write `AAP_TOKEN`.

## Workflow

```
- [ ] 1. Identify resource type
- [ ] 2. Confirm domain (hub) and whether this repo manages it
- [ ] 3. Normalize API shape → CaC fields
- [ ] 4. Resolve relationships (remote href, requirements file)
- [ ] 5. Drop omit-able defaults
- [ ] 6. Apply canonical key order
- [ ] 7. Emit placement + YAML (write only if asked)
```

### 1. Identify resource type

Accept JSON or YAML for one object, or a one-item `results` list — unwrap to the object.

Detect type from, in order:

1. User statement ("this is a collection remote").
2. URL path (`remotes/ansible/collection`, `repositories/ansible/ansible`, `execution-environments/registries`, `v3/namespaces`, `execution-environments/repositories`).
3. Discriminating fields:
   - `requirements_file` or `auth_url` plus a remote `url` → collection remote
   - `retain_repo_versions` or `pulp_labels` plus a repository `name` → collection repository
   - `write_only_fields` or registry `url` under `execution-environments/registries` → EE registry
   - galaxy namespace (`company`, `avatar_url`, `/v3/namespaces/`) → namespace (do not convert)
   - `upstream_name` / container repository readme → EE repository (usually do not convert)

Map managed types via [resource-map.md](resource-map.md). If ambiguous, ask.

### 2. Confirm domain

Hub content in this repo lives under `config/hub/` with the `_hub` suffix. Do not put Hub objects in `common`.

Target: `config/hub/<file>.yml`  
Variable: `<prefix>_hub` (never the unsuffixed base list).

**Do not emit these, even when the API returns them:**

| API object | Why |
|---|---|
| Collection namespace | Created when a collection syncs. No `hub_namespaces_*` file. |
| Hub group, role, or user (`ah_*`) | `infra.aap_configuration.dispatch` does not apply them. Teams and users belong in `config/common/`. |
| EE repository with no remote registry | `ansible.hub.ah_ee_repository` cannot create a local push repository. This repo does not manage those. |

If the user explicitly asks to convert one of those anyway, say why this repo skips it and wait for confirmation before writing a file.

An EE repository that has both `registry` and `upstream_name` can be represented (see [key_ordering.md](key_ordering.md)), but only when the user asks. Flag it as a follow-up otherwise.

### 3. Normalize API shape → CaC fields

Pulp and Galaxy UI payloads become the flat dicts in `config/hub/`. Never keep hrefs, pulp metadata, or embedded objects.

| API field | CaC field |
|---|---|
| `name` | `name` |
| `remote` (repository, Pulp href or null) | `remote: <name>` — GET the href and take `.name`. Omit when null. |
| `requirements_file` (YAML string on a collection remote) | `requirements:` list of `{name, version}` mappings. Drop the raw string. |
| Registry `username` / `password` when `write_only_fields` says `is_set: true` | `{{ hub_var_* }}` placeholders. Do not copy a value. |
| Remote `token` / `password` (hidden) | `{{ hub_var_* }}` when the remote is authenticated (non-empty `auth_url`, or a hidden token/password flagged set). |

**Requirements file:** Pulp stores it as text:

```yaml
---
collections:
  - name: ansible.platform
    version: ">=2.5.3"
```

Emit the `collections` items as `requirements`, keeping `name` and `version` (and `source` when set). Match the mappings already in [`config/hub/collection_remotes.yml`](../../../config/hub/collection_remotes.yml).

**Collection repository sync:** every entry in this repo sets `sync: false`. Sync runs from the Controller job `PAH // Sync Repositories`, not from CaC apply. Always emit `sync: false`. Do not set `update_repo`.

**Secrets:**

- Placeholder pattern: `{{ hub_var_<short_name> }}` (for example `{{ hub_var_redhat_automation_hub_token }}`).
- Add each new name to `config/hub/vault.redacted.yml` with a mock (`"secret"` or `"user"`).
- Reuse an existing `hub_var_*` when the same credential already covers the object.
- Non-secret fields (`url`, `auth_url`, `username` only when it is not a secret, `tls_validation`) stay literal. Registry username in this repo is vaulted (`hub_var_redhat_registry_username`) — follow that when the live username is an account name you must not hardcode. If the user wants the username literal and it is not secret, keep the literal and vault only the password.

### 4. Resolve relationships

```
Collection repository
  → Collection remote (remote name) when the API remote href is set
  → no namespace object

Collection remote
  → requirements list (no separate CaC object per collection)

EE registry
  → no Hub repository object in this repo
```

If a repository points at a remote that is not already in `config/hub/collection_remotes.yml`, name it in follow-ups. Do not invent the remote.

### 5. Drop omit-able defaults

Use the omit tables in [resource-map.md](resource-map.md) (`ansible.hub` module defaults). Common drops:

- `state: present`
- Collection remote: `policy: immediate`, `tls_validation: true`, `sync_dependencies: true`, `signed_only: false`, `download_concurrency: 10`, `rate_limit: 8`, `max_retries: 0`
- Collection repository: `private: false`, `retain_repo_versions` when null or `0`, empty `description`, empty `pulp_labels`, `distribution` whose name equals the repository name
- EE registry: `tls_validation: true`, null concurrency / rate limit

**Keep** `sync: false` on collection repositories (repo convention, not a module default). **Keep** `sync_dependencies: false`, non-empty `pulp_labels`, and `retain_repo_versions` when it is a positive integer (this repo uses `1`).

Always drop API noise: `pulp_href`, `pulp_created`, `pulp_last_updated`, `pulp_labels` only when empty, `versions_href`, `latest_version_href`, `last_sync_task`, `last_synced_metadata_time`, `gpgkey`, `pk`, `id`, `created_at`, `updated_at`, `created`, `updated`, `write_only_fields`, `is_indexable`, `hidden_fields`, task and content counts.

### 6. Apply canonical key order

Reorder remaining keys to [key_ordering.md](key_ordering.md). Omit absent keys. Do not add keys just to fill the template, except `sync: false` on collection repositories.

### 7. Emit result

Default: **do not write files** unless the user asks to add or append.

1. **Placement** — file, variable, apply one-liner (see [config/hub/README.md](../../../config/hub/README.md)).
2. **Rationale** — one or two sentences.
3. **YAML entry** — one list item (`- name: …`) to paste under the target variable.
4. **Follow-ups** — missing remotes, new `hub_var_*` placeholders, objects skipped because this repo does not manage them.

If the user asks to apply: append to the correct list; keep the file one-liner and `---`; do not reorder unrelated entries. Update the hub README file table only when adding a **new** YAML file.

**Orphaned entries:** when reconciling a whole `config/hub/` file, never delete a CaC entry that is missing on the platform. List it and ask.

## Output template

```markdown
## Placement
- File: `config/hub/<file>.yml`
- Variable: `<prefix>_hub`
- Apply: `ansible-playbook pb_aap_config.yml -e "domains=hub" -e "skip_common=true" --tags <resource_tag>`

## Rationale
<why this type / relationship notes>

## Entry
```yaml
- name: ...
```

## Follow-ups
- ...
```

## Examples

**Input (Pulp collection remote):** `name: community`, `url: https://galaxy.ansible.com/api/`, `requirements_file` a YAML string listing `community.general` `>=6.5.0`, `sync_dependencies: true`, `policy: immediate`, no token.

**Output:** `name` / `url` / `requirements: [{name: community.general, version: ">=6.5.0"}]`. No `requirements_file`, no `policy`, no `sync_dependencies`.

**Input (Pulp collection repository):** `name: rh-certified`, `description: Red Hat certified content repository`, `retain_repo_versions: 1`, `private: false`, `remote: /api/galaxy/pulp/api/v3/remotes/ansible/collection/<uuid>/` which GETs as `name: rh-certified`.

**Output:** `name` / `description` / `retain_repo_versions: 1` / `remote: rh-certified` / `sync: false`. No `private`, no pulp href.

**Input (namespace `community`):** do not emit an entry. Tell the user collection sync creates namespaces.

## Additional resources

- [api-reference.md](api-reference.md) — endpoints, auth, pagination
- [resource-map.md](resource-map.md) — type map, unwrap, omit defaults
- [key_ordering.md](key_ordering.md) — per-type key order
- [config/hub/README.md](../../../config/hub/README.md) — what this domain manages
- `ansible.hub` modules under `~/.ansible/collections/ansible_collections/ansible/hub/plugins/modules/`
- `infra.aap_configuration` roles `hub_collection_remote`, `hub_collection_repository`, `hub_ee_registry`
