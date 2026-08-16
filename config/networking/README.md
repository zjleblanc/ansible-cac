# networking

Network automation for Cisco, Palo Alto, and Summit Connect demos.

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

Set `networking` in the `domains` extra-var to load this folder. `common` still loads unless you set `skip_common=true`.

```bash
ansible-playbook pb_aap_config.yml -e "domains=networking"
```

## What lives here

- Network Mgmt project
- Cisco Lab and Palo Alto inventories, groups, and sources
- Networking / Palo Alto / Summit Connect job templates and workflows

## Scope to a single resource file

File-scoped one-liners set `skip_common=true` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. The `domains` extra-var (plus `skip_common`) controls which var files load; resource tags (`--tags`) control which `infra.aap_configuration.dispatch` roles run.

| File | Resource tag | Example |
|------|--------------|--------|
| `credential_types.yml` | `credential_types` | `ansible-playbook pb_aap_config.yml -e "domains=networking" -e "skip_common=true" --tags credential_types` |
| `credentials.yml` | `credentials` | `ansible-playbook pb_aap_config.yml -e "domains=networking" -e "skip_common=true" --tags credentials` |
| `inventories.yml` | `inventories` | `ansible-playbook pb_aap_config.yml -e "domains=networking" -e "skip_common=true" --tags inventories` |
| `inventory_groups.yml` | `host_groups` | `ansible-playbook pb_aap_config.yml -e "domains=networking" -e "skip_common=true" --tags host_groups` |
| `inventory_sources.yml` | `inventory_sources` | `ansible-playbook pb_aap_config.yml -e "domains=networking" -e "skip_common=true" --tags inventory_sources` |
| `job_templates.yml` | `job_templates` | `ansible-playbook pb_aap_config.yml -e "domains=networking" -e "skip_common=true" --tags job_templates` |
| `projects.yml` | `projects` | `ansible-playbook pb_aap_config.yml -e "domains=networking" -e "skip_common=true" --tags projects` |
| `workflow_job_templates.yml` | `workflow_job_templates` | `ansible-playbook pb_aap_config.yml -e "domains=networking" -e "skip_common=true" --tags workflow_job_templates` |

See also [config/README.md](../README.md).
