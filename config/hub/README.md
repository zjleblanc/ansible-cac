# hub

Private Automation Hub configuration (registries, repositories, collections, RBAC).

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

The `hub` tag loads this folder. `common` still loads unless you pass `--skip-tags common`.

```bash
ansible-playbook pb_aap_config.yml --tags hub
```

## What lives here

- EE registries and repositories
- Collection remotes / requirements
- Hub groups, roles, and users

## Scope to a single resource file

File-scoped one-liners use `--skip-tags common` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. Domain + resource tags compose with `infra.aap_configuration.dispatch` tags so only the matching role(s) run after vars load.

| File | Resource tag | Example |
|------|--------------|--------|
| `collection_remotes.yml` | `collectionremote` | `ansible-playbook pb_aap_config.yml --tags hub,collectionremote --skip-tags common` |
| `ee_registries.yml` | `registries` | `ansible-playbook pb_aap_config.yml --tags hub,registries --skip-tags common` |
| `ee_repositories.yml` | `repos` | `ansible-playbook pb_aap_config.yml --tags hub,repos --skip-tags common` |
| `groups.yml` | `groups` | `ansible-playbook pb_aap_config.yml --tags hub,groups --skip-tags common` |
| `roles.yml` | `roles` | `ansible-playbook pb_aap_config.yml --tags hub,roles --skip-tags common` |
| `users.yml` | `users` | `ansible-playbook pb_aap_config.yml --tags hub,users --skip-tags common` |

See also [config/README.md](../README.md).
