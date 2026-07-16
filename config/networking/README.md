# networking

Network automation for Cisco, Palo Alto, and Summit Connect demos.

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

The `networking` tag loads this folder. `common` still loads unless you pass `--skip-tags common`.

```bash
ansible-playbook pb_aap_config.yml --tags networking
```

## What lives here

- Network Mgmt project
- Cisco Lab and Palo Alto inventories, groups, and sources
- Networking / Palo Alto / Summit Connect job templates and workflows

## Scope to a single resource file

File-scoped one-liners use `--skip-tags common` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. Domain + resource tags compose with `infra.aap_configuration.dispatch` tags so only the matching role(s) run after vars load.

| File | Resource tag | Example |
|------|--------------|--------|
| `credential_types.yml` | `credential_types` | `ansible-playbook pb_aap_config.yml --tags networking,credential_types --skip-tags common` |
| `credentials.yml` | `credentials` | `ansible-playbook pb_aap_config.yml --tags networking,credentials --skip-tags common` |
| `inventories.yml` | `inventories` | `ansible-playbook pb_aap_config.yml --tags networking,inventories --skip-tags common` |
| `inventory_groups.yml` | `host_groups` | `ansible-playbook pb_aap_config.yml --tags networking,host_groups --skip-tags common` |
| `inventory_sources.yml` | `inventory_sources` | `ansible-playbook pb_aap_config.yml --tags networking,inventory_sources --skip-tags common` |
| `job_templates.yml` | `job_templates` | `ansible-playbook pb_aap_config.yml --tags networking,job_templates --skip-tags common` |
| `projects.yml` | `projects` | `ansible-playbook pb_aap_config.yml --tags networking,projects --skip-tags common` |
| `workflow_job_templates.yml` | `workflow_job_templates` | `ansible-playbook pb_aap_config.yml --tags networking,workflow_job_templates --skip-tags common` |

See also [config/README.md](../README.md).
