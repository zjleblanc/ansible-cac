# aiops

AIOps and Event-Driven Ansible (controller templates plus EDA component resources).

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

Set `aiops` in the `domains` extra-var to load this folder. `common` still loads unless you set `skip_common=true`.

```bash
ansible-playbook pb_aap_config.yml -e "domains=aiops"
```

## What lives here

- Event-Driven Demos project and AIOps-labeled job templates / workflows
- EDA projects, credentials, event streams, and rulebook activations
- Ticket enrichment credential using the shared `OpenAI Config` credential type (`config/common/credential_types.yml`)

## Scope to a single resource file

File-scoped one-liners set `skip_common=true` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. The `domains` extra-var (plus `skip_common`) controls which var files load; resource tags (`--tags`) control which `infra.aap_configuration.dispatch` roles run.

| File | Resource tag | Example |
|------|--------------|--------|
| `credentials.yml` | `credentials` | `ansible-playbook pb_aap_config.yml -e "domains=aiops" -e "skip_common=true" --tags credentials` |
| `eda_credentials.yml` | `credential` | `ansible-playbook pb_aap_config.yml -e "domains=aiops" -e "skip_common=true" --tags credential` |
| `eda_event_streams.yml` | `event_stream` | `ansible-playbook pb_aap_config.yml -e "domains=aiops" -e "skip_common=true" --tags event_stream` |
| `eda_projects.yml` | `project` | `ansible-playbook pb_aap_config.yml -e "domains=aiops" -e "skip_common=true" --tags project` |
| `eda_rulebook_activations.yml` | `rulebook_activation` | `ansible-playbook pb_aap_config.yml -e "domains=aiops" -e "skip_common=true" --tags rulebook_activation` |
| `job_templates.yml` | `job_templates` | `ansible-playbook pb_aap_config.yml -e "domains=aiops" -e "skip_common=true" --tags job_templates` |
| `projects.yml` | `projects` | `ansible-playbook pb_aap_config.yml -e "domains=aiops" -e "skip_common=true" --tags projects` |
| `workflow_job_templates.yml` | `workflow_job_templates` | `ansible-playbook pb_aap_config.yml -e "domains=aiops" -e "skip_common=true" --tags workflow_job_templates` |

See also [config/README.md](../README.md).
