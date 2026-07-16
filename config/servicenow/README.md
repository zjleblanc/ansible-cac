# servicenow

ServiceNow ITSM and related Selenium demo job templates.

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

The `servicenow` tag loads this folder. `common` still loads unless you pass `--skip-tags common`.

```bash
ansible-playbook pb_aap_config.yml --tags servicenow
```

## What lives here

- ServiceNow and Selenium job templates
- Shared dependencies (ServiceNow credential, inventories, Cloud Mgmt project) live in common/

## Scope to a single resource file

File-scoped one-liners use `--skip-tags common` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. Domain + resource tags filter which var files load (`vars/cac_file_resource_tags.yml`) and which `infra.aap_configuration.dispatch` roles run.

| File | Resource tag | Example |
|------|--------------|--------|
| `job_templates.yml` | `job_templates` | `ansible-playbook pb_aap_config.yml --tags servicenow,job_templates --skip-tags common` |

See also [config/README.md](../README.md).
