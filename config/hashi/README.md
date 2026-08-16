# hashi

HashiCorp stack: Terraform / HCP IaC and Vault.

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

Set `hashi` in the `domains` extra-var to load this folder. `common` still loads unless you set `skip_common=true`.

```bash
ansible-playbook pb_aap_config.yml -e "domains=hashi"
```

## What lives here

- Terraform Mgmt project, HCP/Terraform inventories and sources
- Terraform Cloud / backend credentials and credential types
- Vault install/lookup/OIDC demo job templates and HashiCorp Vault credentials (including OIDC lookup + input sources)
- Terraform deploy/configure workflows

## Scope to a single resource file

File-scoped one-liners set `skip_common=true` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. The `domains` extra-var (plus `skip_common`) controls which var files load; resource tags (`--tags`) control which `infra.aap_configuration.dispatch` roles run.

| File | Resource tag | Example |
|------|--------------|--------|
| `credential_types.yml` | `credential_types` | `ansible-playbook pb_aap_config.yml -e "domains=hashi" -e "skip_common=true" --tags credential_types` |
| `credentials.yml` | `credentials` | `ansible-playbook pb_aap_config.yml -e "domains=hashi" -e "skip_common=true" --tags credentials` |
| `credential_input_sources.yml` | `credential_input_sources` | `ansible-playbook pb_aap_config.yml -e "domains=hashi" -e "skip_common=true" --tags credential_input_sources` |
| `inventories.yml` | `inventories` | `ansible-playbook pb_aap_config.yml -e "domains=hashi" -e "skip_common=true" --tags inventories` |
| `inventory_sources.yml` | `inventory_sources` | `ansible-playbook pb_aap_config.yml -e "domains=hashi" -e "skip_common=true" --tags inventory_sources` |
| `job_templates.yml` | `job_templates` | `ansible-playbook pb_aap_config.yml -e "domains=hashi" -e "skip_common=true" --tags job_templates` |
| `projects.yml` | `projects` | `ansible-playbook pb_aap_config.yml -e "domains=hashi" -e "skip_common=true" --tags projects` |
| `workflow_job_templates.yml` | `workflow_job_templates` | `ansible-playbook pb_aap_config.yml -e "domains=hashi" -e "skip_common=true" --tags workflow_job_templates` |

See also [config/README.md](../README.md).
