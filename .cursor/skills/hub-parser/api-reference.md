# Hub API reference — export endpoints

Read-only reference for exporting Private Automation Hub objects before conversion. The conversion workflow is [SKILL.md](SKILL.md).

There is no Hub MCP server. Use the Galaxy and Pulp APIs behind the AAP Gateway.

## Base URL and authentication

Assume these environment variables are already set:

| Var | Meaning |
|---|---|
| `AAP_HOSTNAME` | Gateway hostname (no scheme) |
| `AAP_USERNAME` | Platform username (not required once `AAP_TOKEN` is set) |
| `AAP_TOKEN` | Bearer token |

```bash
curl -sk "https://${AAP_HOSTNAME}/api/galaxy/<path>" \
  -H "Authorization: Bearer ${AAP_TOKEN}"
```

Never echo `AAP_TOKEN`, commit it, or write it into `config/`.

### Galaxy prefix

On the AAP Gateway, `GET /api/` returns an `apis` map. Use `apis.galaxy` (normally `/api/galaxy/`) as the prefix.

| API | Prefix under the Gateway |
|---|---|
| Pulp | `/api/galaxy/pulp/api/v3/` |
| Galaxy UI | `/api/galaxy/_ui/v1/` |
| Galaxy content | `/api/galaxy/v3/` |

If `GET /api/` has no `apis.galaxy` key, the host is standalone Hub. Stop and ask which prefix to use (`/api/automation-hub` or `/api/galaxy`) instead of guessing.

## Pagination

Pulp and Galaxy UI list endpoints return:

```json
{"count": 10, "next": "https://…?limit=100&offset=100", "previous": null, "results": []}
```

Pass `limit=100`. Follow `next` until it is null. Prefer `?name=<exact>` plus one object over paging a whole collection when converting a single resource.

Galaxy content (`/v3/namespaces/`, `/v3/collections/`) uses the same `results` envelope. Some deployments also accept `page` / `page_size`. `limit` / `offset` is the safe default.

## List vs retrieve

| Family | List | Retrieve |
|---|---|---|
| Pulp (remotes, repositories, distributions) | `GET <collection>/?name=<name>` → `results[]` with `pulp_href` | `GET <pulp_href>` returns the same object. Repository `remote` is still an href — GET that href for the remote name. |
| Galaxy UI (EE registries, EE repositories) | `GET <collection>/?name=<name>&limit=100` | `GET <collection>/<pk-or-name>/` |

Name filters are the discovery step. Resolve hrefs before writing CaC. Do not leave a `pulp_href` in YAML.

## Recommended export order

1. **Collection remotes** — no Hub dependency.
2. **Collection repositories** — `remote` href resolves to a remote from step 1.
3. **EE registries** — independent of collection objects.

Do not export namespaces or RBAC users/groups/roles into CaC. See [SKILL.md](SKILL.md) step 2. EE repository reads are only for deciding whether a repo is a local push repo (skip) or a registry-backed mirror (convert only if the user asks).

## Endpoint catalog

Paths below are relative to `https://${AAP_HOSTNAME}`.

### Collection remotes

Module: `ansible.hub.collection_remote`. CaC: `hub_collection_remotes_hub`.

| Endpoint | Use |
|---|---|
| `GET /api/galaxy/pulp/api/v3/remotes/ansible/collection/?name=<name>&limit=100` | Find a remote |
| `GET /api/galaxy/pulp/api/v3/remotes/ansible/collection/<uuid>/` | Full remote, including `requirements_file` |

`requirements_file` is a YAML **string**, not a list. `token` and `password` are not returned. `auth_url` set, or a hidden credential flagged on the object, means the CaC entry needs a `{{ hub_var_* }}` token or password.

### Collection repositories

Module: `ansible.hub.collection_repository`. CaC: `hub_collection_repositories_hub`.

| Endpoint | Use |
|---|---|
| `GET /api/galaxy/pulp/api/v3/repositories/ansible/ansible/?name=<name>&limit=100` | Find a repository |
| `GET /api/galaxy/pulp/api/v3/repositories/ansible/ansible/<uuid>/` | Full repository (`remote` href, `pulp_labels`, `retain_repo_versions`, `private`) |
| `GET /api/galaxy/pulp/api/v3/distributions/ansible/ansible/?name=<name>` | Distribution `base_path` / `name`, only if you need to see whether it differs from the repository name |

`remote: null` means an internal repository (`published`, `staging`, `rejected`). Do not invent a remote.

### EE registries

Module: `ansible.hub.ah_ee_registry`. CaC: `hub_ee_registries_hub`.

| Endpoint | Use |
|---|---|
| `GET /api/galaxy/_ui/v1/execution-environments/registries/?name=<name>&limit=100` | Find a registry |
| `GET /api/galaxy/_ui/v1/execution-environments/registries/<pk>/` | Full registry |

`write_only_fields` is a list of `{name, is_set}`. `is_set: true` on `password` or `username` means "configured", not "here is the value".

### Collection namespaces (do not convert)

Module: `ansible.hub.ah_namespace`. Not a CaC file in this repo. Collection sync creates namespaces.

| Endpoint | Use |
|---|---|
| `GET /api/galaxy/v3/namespaces/?name=<name>` | Confirm a namespace exists. Stop there. |

### EE repositories (usually do not convert)

Module: `ansible.hub.ah_ee_repository`. A repository without `registry` + `upstream_name` is a local push repo; the module cannot create it.

| Endpoint | Use |
|---|---|
| `GET /api/galaxy/_ui/v1/execution-environments/repositories/?name=<name>&limit=100` | Inspect only |
| `GET /api/galaxy/_ui/v1/execution-environments/repositories/<name>/` | `registry`, `upstream_name` — both required before a CaC entry is even possible |

### Not CaC (dispatch does not apply them)

| Endpoint | Object |
|---|---|
| `GET /api/galaxy/_ui/v1/groups/` | Hub group — use `aap_teams` in `config/common/` |
| `GET /api/galaxy/_ui/v1/users/` | Hub user — use `aap_user_accounts` in `config/common/` |
| `GET /api/galaxy/pulp/api/v3/roles/` | Hub role |

## Response quirks

- Pulp list and retrieve share one schema. There is no separate `*Read` type. The useful difference is that list rows still leave `remote` as an href.
- `policy` on remotes defaults to `immediate`. The module's other documented choice is the sentence `When syncing, download all metadata and content now.` If the API returns `on_demand`, do not invent a CaC value — flag it as a follow-up.
- `retain_repo_versions: null` on a repository means unlimited (module default). A positive integer is meaningful.
- Empty `pulp_labels: {}` is noise. Non-empty labels (`pipeline`, `hide_from_search`) are CaC.
- Sync tasks (`last_sync_task`, repository `.../sync/`, registry `.../sync`) are runtime state. This repo does not turn them into `update_repo: true`.

## Example

```bash
# 1. Collection remote by name
curl -sk "https://${AAP_HOSTNAME}/api/galaxy/pulp/api/v3/remotes/ansible/collection/?name=rh-certified&limit=10" \
  -H "Authorization: Bearer ${AAP_TOKEN}" | python3 -m json.tool

# 2. Collection repository, then its remote href
curl -sk "https://${AAP_HOSTNAME}/api/galaxy/pulp/api/v3/repositories/ansible/ansible/?name=rh-certified&limit=10" \
  -H "Authorization: Bearer ${AAP_TOKEN}" | python3 -m json.tool

# 3. EE registry by name
curl -sk "https://${AAP_HOSTNAME}/api/galaxy/_ui/v1/execution-environments/registries/?name=registry.redhat.io&limit=10" \
  -H "Authorization: Bearer ${AAP_TOKEN}" | python3 -m json.tool
```
