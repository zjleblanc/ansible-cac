# business

Business process automation (BPA) resources.

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

Set `business` in the `domains` extra-var to load this folder. `common` still loads unless you set `skip_common=true`.

```bash
ansible-playbook pb_aap_config.yml -e "domains=business"
```

## What lives here

- Business Process project and Business-labeled job templates
- Google OAuth Client credential type + credential for Google Sheets/Gmail automation
- Account Task Summarizer credential using the shared `OpenAI Config` credential type (`config/common/credential_types.yml`)
- Nightly schedule for the account task update job template

## Scope to a single resource file

File-scoped one-liners set `skip_common=true` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. The `domains` extra-var (plus `skip_common`) controls which var files load; resource tags (`--tags`) control which `infra.aap_configuration.dispatch` roles run.

| File | Resource tag | Example |
|------|--------------|--------|
| `credential_types.yml` | `credential_types` | `ansible-playbook pb_aap_config.yml -e "domains=business" -e "skip_common=true" --tags credential_types` |
| `credentials.yml` | `credentials` | `ansible-playbook pb_aap_config.yml -e "domains=business" -e "skip_common=true" --tags credentials` |
| `job_templates.yml` | `job_templates` | `ansible-playbook pb_aap_config.yml -e "domains=business" -e "skip_common=true" --tags job_templates` |
| `projects.yml` | `projects` | `ansible-playbook pb_aap_config.yml -e "domains=business" -e "skip_common=true" --tags projects` |
| `schedules.yml` | `schedules` | `ansible-playbook pb_aap_config.yml -e "domains=business" -e "skip_common=true" --tags schedules` |

See also [config/README.md](../README.md).
