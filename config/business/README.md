# business

Business process automation (BPA) resources.

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

The `business` tag loads this folder. `common` still loads unless you pass `--skip-tags common`.

```bash
ansible-playbook pb_aap_config.yml --tags business
```

## What lives here

- Business Process project and Business-labeled job templates
- Google OAuth Client credential type + credential for Google Sheets/Gmail automation
- Account Task Summarizer credential using the shared `OpenAI Config` credential type (`config/common/credential_types.yml`)
- Nightly schedule for the account task update job template

## Scope to a single resource file

File-scoped one-liners use `--skip-tags common` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. Domain + resource tags filter which var files load (`vars/cac_file_resource_tags.yml`) and which `infra.aap_configuration.dispatch` roles run.

| File | Resource tag | Example |
|------|--------------|--------|
| `credential_types.yml` | `credential_types` | `ansible-playbook pb_aap_config.yml --tags business,credential_types --skip-tags common` |
| `credentials.yml` | `credentials` | `ansible-playbook pb_aap_config.yml --tags business,credentials --skip-tags common` |
| `job_templates.yml` | `job_templates` | `ansible-playbook pb_aap_config.yml --tags business,job_templates --skip-tags common` |
| `projects.yml` | `projects` | `ansible-playbook pb_aap_config.yml --tags business,projects --skip-tags common` |
| `schedules.yml` | `schedules` | `ansible-playbook pb_aap_config.yml --tags business,schedules --skip-tags common` |

See also [config/README.md](../README.md).
