# apps

Application lifecycle demos: SSL/ACME, home automation (Kasa), CyberArk, and policy enforcement.

## Apply this domain

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

The `apps` tag loads this folder. `common` still loads unless you pass `--skip-tags common`.

```bash
ansible-playbook pb_aap_config.yml --tags apps
```

## What lives here

- App Mgmt and CyberArk-Conjur Demo projects
- SSL, Lab DNS, Kasa, CyberArk, and policy job templates
- Related schedules and workflows

## Scope to a single resource file

File-scoped one-liners use `--skip-tags common` so only this domain's vars are loaded for that resource type (common still loads on full-domain applies).

Each YAML file has a one-liner comment at the top. Domain + resource tags compose with `infra.aap_configuration.dispatch` tags so only the matching role(s) run after vars load.

| File | Resource tag | Example |
|------|--------------|--------|
| `credential_types.yml` | `credential_types` | `ansible-playbook pb_aap_config.yml --tags apps,credential_types --skip-tags common` |
| `credentials.yml` | `credentials` | `ansible-playbook pb_aap_config.yml --tags apps,credentials --skip-tags common` |
| `job_templates.yml` | `job_templates` | `ansible-playbook pb_aap_config.yml --tags apps,job_templates --skip-tags common` |
| `projects.yml` | `projects` | `ansible-playbook pb_aap_config.yml --tags apps,projects --skip-tags common` |
| `schedules.yml` | `schedules` | `ansible-playbook pb_aap_config.yml --tags apps,schedules --skip-tags common` |
| `workflow_job_templates.yml` | `workflow_job_templates` | `ansible-playbook pb_aap_config.yml --tags apps,workflow_job_templates --skip-tags common` |

See also [config/README.md](../README.md).
