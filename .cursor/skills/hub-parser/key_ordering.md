# Canonical Key Ordering — Private Automation Hub

Every list entry under a `hub_*` config variable must follow the canonical key order below.

This is the Hub-specific copy of the order agents apply when converting Hub API payloads. The same Hub blocks live in [cac-parser/key_ordering.md](../cac-parser/key_ordering.md) under "Private Automation Hub". If you change an order here, change it there too.

## Guiding principles

1. **Identity first** — `name`, then `description`.
2. **Connection** — `url`, `auth_url`, credentials.
3. **Behavioral config** — booleans, retention, labels.
4. **Relationships** — `remote`, `registry`, `upstream_name`.
5. **Complex structures last** — `requirements`, `pulp_labels`, `distribution`, `readme`.

Keys absent from an entry are omitted. Remaining keys keep this relative order.

Collection namespaces are not a CaC type here. Collection sync creates them. Do not add a `hub_namespaces_*` block.

---

### EE Registries (`hub_ee_registries_*`)

```yaml
- name:
  url:
  username:
  password:
```

### EE Repositories (`hub_ee_repositories_*`)

Not managed in this repo unless the user explicitly asks and the repository has a remote `registry` plus `upstream_name`. `ansible.hub.ah_ee_repository` cannot create a local push repository.

```yaml
- name:
  description:
  registry:
  upstream_name:
  readme:
```

### Collection Remotes (`hub_collection_remotes_*`)

```yaml
- name:
  url:
  auth_url:
  token:
  sync_dependencies:
  requirements:
```

### Collection Repositories (`hub_collection_repositories_*`)

Always include `sync: false`.

```yaml
- name:
  description:
  retain_repo_versions:
  pulp_labels:
  distribution:
  private:
  remote:
  sync:
```

### Groups (`ah_groups_*`)

Not applied by `infra.aap_configuration.dispatch` (prefer `aap_teams` in common).

```yaml
- name:
  state:
```

### Roles (`ah_roles_*`)

Not applied by `infra.aap_configuration.dispatch`.

```yaml
- name:
  description:
  perms:
```

### Users (`ah_users_*`)

Not applied by `infra.aap_configuration.dispatch` (prefer `aap_user_accounts` in common).

```yaml
- username:
  password:
  email:
  first_name:
  last_name:
  groups:
  append:
  is_superuser:
```
