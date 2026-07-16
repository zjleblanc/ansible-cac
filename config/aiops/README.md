# aiops

AIOps and Event-Driven Ansible (controller templates plus EDA component resources).

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

The `aiops` tag loads this folder. `common` still loads unless you pass `--skip-tags common`.

```bash
ansible-playbook pb_aap_config.yml --tags aiops
```

## What lives here

- Event-Driven Demos project and AIOps-labeled job templates / workflows
- EDA projects, credentials, event streams, and rulebook activations
- Ticket enrichment / OpenAI credential types used by AIOps demos

## Scope to a single resource file

File-scoped one-liners use `--skip-tags common` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. Domain + resource tags compose with `infra.aap_configuration.dispatch` tags so only the matching role(s) run after vars load.

| File | Resource tag | Example |
|------|--------------|--------|
| `credential_types.yml` | `credential_types` | `ansible-playbook pb_aap_config.yml --tags aiops,credential_types --skip-tags common` |
| `credentials.yml` | `credentials` | `ansible-playbook pb_aap_config.yml --tags aiops,credentials --skip-tags common` |
| `eda_credentials.yml` | `credential` | `ansible-playbook pb_aap_config.yml --tags aiops,credential --skip-tags common` |
| `eda_event_streams.yml` | `event_stream` | `ansible-playbook pb_aap_config.yml --tags aiops,event_stream --skip-tags common` |
| `eda_projects.yml` | `project` | `ansible-playbook pb_aap_config.yml --tags aiops,project --skip-tags common` |
| `eda_rulebook_activations.yml` | `rulebook_activation` | `ansible-playbook pb_aap_config.yml --tags aiops,rulebook_activation --skip-tags common` |
| `job_templates.yml` | `job_templates` | `ansible-playbook pb_aap_config.yml --tags aiops,job_templates --skip-tags common` |
| `projects.yml` | `projects` | `ansible-playbook pb_aap_config.yml --tags aiops,projects --skip-tags common` |
| `workflow_job_templates.yml` | `workflow_job_templates` | `ansible-playbook pb_aap_config.yml --tags aiops,workflow_job_templates --skip-tags common` |

See also [config/README.md](../README.md).
