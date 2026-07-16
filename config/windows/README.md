# windows

Windows, Active Directory, Proxmox Windows guests, and SQL Server demos.

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

The `windows` tag loads this folder. `common` still loads unless you pass `--skip-tags common`.

```bash
ansible-playbook pb_aap_config.yml --tags windows
```

## What lives here

- Windows / AD / Proxmox credentials and credential types
- Windows inventory, groups, and sources; Proxmox inventory groups
- Windows and Proxmox job templates and workflows

## Scope to a single resource file

File-scoped one-liners use `--skip-tags common` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. Domain + resource tags filter which var files load (`vars/cac_file_resource_tags.yml`) and which `infra.aap_configuration.dispatch` roles run.

| File | Resource tag | Example |
|------|--------------|--------|
| `credential_types.yml` | `credential_types` | `ansible-playbook pb_aap_config.yml --tags windows,credential_types --skip-tags common` |
| `credentials.yml` | `credentials` | `ansible-playbook pb_aap_config.yml --tags windows,credentials --skip-tags common` |
| `inventories.yml` | `inventories` | `ansible-playbook pb_aap_config.yml --tags windows,inventories --skip-tags common` |
| `inventory_groups.yml` | `host_groups` | `ansible-playbook pb_aap_config.yml --tags windows,host_groups --skip-tags common` |
| `inventory_sources.yml` | `inventory_sources` | `ansible-playbook pb_aap_config.yml --tags windows,inventory_sources --skip-tags common` |
| `job_templates.yml` | `job_templates` | `ansible-playbook pb_aap_config.yml --tags windows,job_templates --skip-tags common` |
| `workflow_job_templates.yml` | `workflow_job_templates` | `ansible-playbook pb_aap_config.yml --tags windows,workflow_job_templates --skip-tags common` |

See also [config/README.md](../README.md).
