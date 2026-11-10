# hub

Private Automation Hub configuration (collection remotes/repositories, EE registries).

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `config/hub/vault.yml` or `vars/` are required for the resources you are applying.

Set `hub` in the `domains` extra-var to load this folder. `common` still loads unless you set `skip_common=true`.

```bash
ansible-playbook pb_aap_config.yml -e "domains=hub"
```

## What lives here

- Collection remotes and repositories (sync left to `PAH // Sync Repositories`)
- EE registries

Collection namespaces are created by those syncs, so they are not defined here. Hub groups/roles/users (`ah_*`) are **not** applied by `infra.aap_configuration.dispatch`. Platform teams and users belong under `config/common/`. Live EE push repositories without a remote registry are not managed here (`ansible.hub.ah_ee_repository` cannot create them).

Domain secrets are documented in `vault.redacted.yml` and loaded from gitignored `vault.yml` when this domain is selected.

## Scope to a single resource file

File-scoped one-liners set `skip_common=true` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. The `domains` extra-var (plus `skip_common`) controls which var files load; resource tags (`--tags`) control which `infra.aap_configuration.dispatch` roles run.

| File | Resource tag | Example |
|------|--------------|--------|
| `collection_remotes.yml` | `collectionremote` | `ansible-playbook pb_aap_config.yml -e "domains=hub" -e "skip_common=true" --tags collectionremote` |
| `collection_repositories.yml` | `collectionsrep` | `ansible-playbook pb_aap_config.yml -e "domains=hub" -e "skip_common=true" --tags collectionsrep` |
| `ee_registries.yml` | `registries` | `ansible-playbook pb_aap_config.yml -e "domains=hub" -e "skip_common=true" --tags registries` |

See also [config/README.md](../README.md).
