# hub

Private Automation Hub configuration (registries, repositories, collections, RBAC).

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

Set `hub` in the `domains` extra-var to load this folder. `common` still loads unless you set `skip_common=true`.

```bash
ansible-playbook pb_aap_config.yml -e "domains=hub"
```

## What lives here

- EE registries and repositories
- Collection remotes / requirements
- Hub groups, roles, and users

## Scope to a single resource file

File-scoped one-liners set `skip_common=true` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. The `domains` extra-var (plus `skip_common`) controls which var files load; resource tags (`--tags`) control which `infra.aap_configuration.dispatch` roles run.

| File | Resource tag | Example |
|------|--------------|--------|
| `collection_remotes.yml` | `collectionremote` | `ansible-playbook pb_aap_config.yml -e "domains=hub" -e "skip_common=true" --tags collectionremote` |
| `ee_registries.yml` | `registries` | `ansible-playbook pb_aap_config.yml -e "domains=hub" -e "skip_common=true" --tags registries` |
| `ee_repositories.yml` | `repos` | `ansible-playbook pb_aap_config.yml -e "domains=hub" -e "skip_common=true" --tags repos` |
| `groups.yml` | `groups` | `ansible-playbook pb_aap_config.yml -e "domains=hub" -e "skip_common=true" --tags groups` |
| `roles.yml` | `roles` | `ansible-playbook pb_aap_config.yml -e "domains=hub" -e "skip_common=true" --tags roles` |
| `users.yml` | `users` | `ansible-playbook pb_aap_config.yml -e "domains=hub" -e "skip_common=true" --tags users` |

See also [config/README.md](../README.md).
