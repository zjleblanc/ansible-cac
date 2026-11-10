# Resource map: Hub API → config file / variable / omit defaults

Hub resources in this repo live under `config/hub/`. Variable suffix is `_hub`.

## Type → file → variable prefix → dispatch tag

| API resource | `ansible.hub` module | File | Variable prefix | Dispatch tag | In this repo |
|---|---|---|---|---|---|
| Collection remote (`/pulp/api/v3/remotes/ansible/collection/`) | `collection_remote` | `collection_remotes.yml` | `hub_collection_remotes` | `collectionremote` | Yes |
| Collection repository (`/pulp/api/v3/repositories/ansible/ansible/`) | `collection_repository` | `collection_repositories.yml` | `hub_collection_repositories` | `collectionsrep` | Yes. Always `sync: false`. |
| EE registry (`/_ui/v1/execution-environments/registries/`) | `ah_ee_registry` | `ee_registries.yml` | `hub_ee_registries` | `registries` | Yes |
| EE repository (`/_ui/v1/execution-environments/repositories/`) | `ah_ee_repository` | `ee_repositories.yml` | `hub_ee_repositories` | `repos` | No, unless the user asks and the repo has `registry` + `upstream_name` |
| Collection namespace (`/v3/namespaces/`) | `ah_namespace` | — | — | `namespaces` | No. Sync creates namespaces. |
| Hub group / role / user | `ah_group` / `ah_role` / `ah_user` | — | `ah_groups` / `ah_roles` / `ah_users` | — | No. Not dispatched. Use `config/common/` teams and users. |

Dispatch tags are the ones on `infra.aap_configuration.dispatch` `hub_configuration_dispatcher_roles`. Imperative roles (`hub_collection_repository_sync`, `hub_ee_registry_sync`, `hub_ee_registry_index`, `hub_collection`, `hub_publish`) are not desired-state objects — do not invent CaC vars for them.

If a managed file is missing: create it with the one-liner `# ansible-playbook pb_aap_config.yml -e "domains=hub" -e "skip_common=true" --tags <tag>`, add the suffixed list, and add a row to [config/hub/README.md](../../../config/hub/README.md).

## Unwrap cheat sheet

| API shape | CaC field | Notes |
|---|---|---|
| `remote: "/api/galaxy/pulp/api/v3/remotes/ansible/collection/<uuid>/"` | `remote: rh-certified` | GET the href; use `.name` |
| `remote: null` | omit `remote` | Internal repository |
| `requirements_file: "---\ncollections:\n- name: …\n  version: …"` | `requirements: [{name, version}]` | Parse YAML. Drop the string. |
| `pulp_labels: {pipeline: staging, hide_from_search: ""}` | `pulp_labels:` same mapping | Keep a present empty-string `hide_from_search` |
| `pulp_labels: {}` | omit | |
| `distribution` whose `name` / `base_path` equals the repository `name` | omit | Module would recreate the default distribution |
| Distribution name differs | `distribution: {name, state: present}` | Only when the user is managing that split |
| `write_only_fields: [{name: password, is_set: true}]` | `password: "{{ hub_var_… }}"` | Never a copied secret |
| `token` absent but `auth_url` set | `token: "{{ hub_var_… }}"` | Authenticated remote; secret is hidden |

## `ansible.hub` module defaults (omit when the payload matches)

### `hub_collection_remotes_*` (`collection_remote`)

| Key | Omit when |
|---|---|
| `state` | `present` |
| `policy` | `immediate` |
| `tls_validation` | `true` |
| `sync_dependencies` | `true` |
| `signed_only` | `false` |
| `download_concurrency` | `10` |
| `rate_limit` | `8` |
| `max_retries` | `0` or null |
| `username`, `password`, `token`, `auth_url`, `proxy_*`, cert fields | absent |

Keep `name`, `url`, and `requirements` when the file lists any collection. Keep `auth_url` and a vault `token` (or `username` / `password`) when the remote authenticates.

### `hub_collection_repositories_*` (`collection_repository`)

| Key | Omit when |
|---|---|
| `state` | `present` |
| `description` | `""` or null |
| `retain_repo_versions` | null or `0` (unlimited) |
| `private` | `false` |
| `pulp_labels` | `{}` or absent |
| `remote` | null |
| `distribution` | absent, or name equals the repository name |
| `update_repo` | always omit — this repo uses `sync: false` instead |
| `wait` | `true` |
| `interval` | `1` |

**Always write `sync: false`.** That records "do not sync on apply". The Controller job `PAH // Sync Repositories` performs sync.

Keep `name`. Keep `retain_repo_versions` when it is a positive integer.

### `hub_ee_registries_*` (`ah_ee_registry`)

| Key | Omit when |
|---|---|
| `state` | `present` |
| `tls_validation` | `true` |
| `download_concurrency`, `rate_limit` | null or absent |
| `proxy_*`, cert fields | absent |

Keep `name` and `url`. Username and password are `{{ hub_var_* }}` when the registry has them set.

### `hub_ee_repositories_*` (`ah_ee_repository`) — only if the user overrides the skip

| Key | Omit when |
|---|---|
| `state` | `present` |
| `description` | `""` or null |
| `include_tags`, `exclude_tags` | `[]` |
| `readme` | `""` or absent |

Keep `name`. Keep `registry` and `upstream_name` together — without both, do not emit the entry.

## API-only noise (always drop)

`pulp_href`, `pulp_created`, `pulp_last_updated`, `versions_href`, `latest_version_href`, `last_sync_task`, `last_synced_metadata_time`, `gpgkey`, `pk`, `id`, `created`, `updated`, `created_at`, `updated_at`, `write_only_fields`, `hidden_fields`, `is_indexable`, `client_url`, `content_guard`, `repository_version`, task state, collection counts.

## Relationship graph

```text
Collection repository
  → Collection remote     (hub_collection_remotes_hub) when remote is set
  → sync is not a CaC trigger (PAH // Sync Repositories)

Collection remote
  → requirements          (inline list, not separate objects)
  → namespaces            (created by sync — no CaC object)

EE registry
  → no EE repository in this repo
```

Confirm every `remote` name exists in `config/hub/collection_remotes.yml` or is being added in the same change. Flag gaps as follow-ups.
