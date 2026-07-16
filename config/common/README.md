# common

Platform fundamentals and resources shared across two or more domains.

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

`common` is tagged `always` in `pb_aap_config.yml`, so it loads on every run. Running with no domain tags applies only common vars (other domains use `never` and are opt-in).

```bash
ansible-playbook pb_aap_config.yml
```

To run other domains **without** common (rare):

```bash
ansible-playbook pb_aap_config.yml --tags cloud --skip-tags common
```

## What lives here

- Organizations, users, teams, authenticators, and authenticator maps
- Execution environments, labels, and notification templates
- Projects, credentials, inventories, and inventory sources used by multiple domains

## Scope to a single resource file

Each YAML file has a one-liner comment at the top. Domain + resource tags compose with `infra.aap_configuration.dispatch` tags so only the matching role(s) run after vars load.

| File | Resource tag | Example |
|------|--------------|--------|
| `authenticator_maps.yml` | `authenticator_maps` | `ansible-playbook pb_aap_config.yml --tags authenticator_maps` |
| `authenticators.yml` | `authenticators` | `ansible-playbook pb_aap_config.yml --tags authenticators` |
| `credential_types.yml` | `credential_types` | `ansible-playbook pb_aap_config.yml --tags credential_types` |
| `credentials.yml` | `credentials` | `ansible-playbook pb_aap_config.yml --tags credentials` |
| `execution_environments.yml` | `execution_environments` | `ansible-playbook pb_aap_config.yml --tags execution_environments` |
| `inventories.yml` | `inventories` | `ansible-playbook pb_aap_config.yml --tags inventories` |
| `inventory_sources.yml` | `inventory_sources` | `ansible-playbook pb_aap_config.yml --tags inventory_sources` |
| `labels.yml` | `labels` | `ansible-playbook pb_aap_config.yml --tags labels` |
| `notifications.yml` | `notification_templates` | `ansible-playbook pb_aap_config.yml --tags notification_templates` |
| `organizations.yml` | `organizations` | `ansible-playbook pb_aap_config.yml --tags organizations` |
| `projects.yml` | `projects` | `ansible-playbook pb_aap_config.yml --tags projects` |
| `teams.yml` | `teams` | `ansible-playbook pb_aap_config.yml --tags teams` |
| `users.yml` | `users` | `ansible-playbook pb_aap_config.yml --tags users` |

See also [config/README.md](../README.md).
